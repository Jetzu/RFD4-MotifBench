# Origin: cc
# Purpose: Convert RFD4-Proteina design CIFs into a MotifBench scaffold directory (PDBs + scaffold_info.csv) with motif-RMSD QC.
"""
Indexed:   placements come from the spec's layout.tsv (gap lengths are fixed per design key <case>__<i>).
Unindexed: placements come from the model's insertion mapping written into the output CIF
           (is_unindexed_insertion + annotation_src-index-group_1_atom); index group k = motif segment k
           in contig order (groups are numbered from 2 upward in the order the segments were declared).
           A mapping that is not one contiguous, correctly-sized run per segment is repaired by a sliding
           window search (best backbone RMSD over all non-overlapping windows, segments in mapped order)
           and the repair is reported in qc.tsv.

Usage:
  python MBR4_convert_to_motifbench_cc.py --mode indexed|unindexed --samples <inference_samples dir>
         --seg-map in/specs/seg_map.json --motif-dir <MotifBench motif_pdbs> --out <scaffolds dir>
         [--layout layout.tsv] [--cases 01_1LDB ...]
"""
import argparse
import csv
import itertools
import json
from collections import defaultdict
from pathlib import Path

import biotite.structure as struc
import biotite.structure.io.pdb as pdb
import biotite.structure.io.pdbx as pdbx
import numpy as np

BB = ["N", "CA", "C", "O"]


def read_cif(path):
    f = pdbx.CIFFile.read(str(path))
    block = f.block
    aa = pdbx.get_structure(f, model=1, use_author_fields=False)
    site = block["atom_site"]
    cols = {}
    for name in ("is_unindexed_insertion", "annotation_src-index-group_1_atom"):
        if name in site:
            cols[name] = site[name].as_array()
    return aa, cols


def bb_coords(arr, res_ids):
    out = []
    for r in res_ids:
        m = arr[arr.res_id == r]
        for a in BB:
            x = m[m.atom_name == a]
            if len(x) != 1:
                return None
            out.append(x.coord[0])
    return np.array(out)


def rmsd(a, b):
    sup, _ = struc.superimpose(b, a)
    return float(np.sqrt(((sup - b) ** 2).sum(-1).mean()))


def motif_reference(motif_pdb, segs):
    ref = pdb.PDBFile.read(str(motif_pdb)).get_structure(model=1)
    per_seg = []
    for sg in segs:
        ch = ref[ref.chain_id == sg["orig_chain"]]
        ids = sorted(set(ch.res_id))[: sg["length"]]
        per_seg.append(bb_coords(ch, ids))
    return per_seg


def placement_string(starts, segs, L):
    """starts: dict seg_index -> 1-based start in design. Returns MotifBench string, segments in sequence order."""
    order = sorted(starts, key=lambda k: starts[k])
    parts, pos = [], 1
    for k in order:
        gap = starts[k] - pos
        if gap > 0:
            parts.append(str(gap))
        parts.append(segs[k]["orig_chain"])
        pos = starts[k] + segs[k]["length"]
    if L - pos + 1 > 0:
        parts.append(str(L - pos + 1))
    return "/".join(parts)


def window_search(design, segs, ref, order, L):
    """Repair placement when the insertion mapping is unusable. Keeps the segment ORDER the model chose
    (`order`, by mean mapped position) and places segments longest-first; each candidate window is scored
    by the joint backbone RMSD of all segments placed so far (so 1-residue segments are placed in the
    frame of the longer ones), within bounds that leave room for the segments still unplaced."""
    lens = {k: segs[k]["length"] for k in order}
    pos_in_order = {k: i for i, k in enumerate(order)}
    starts = {}
    for k in sorted(order, key=lambda k: (-lens[k], pos_in_order[k])):
        i = pos_in_order[k]
        lo, between = 1, 0
        for j in reversed(order[:i]):
            if j in starts:
                lo = starts[j] + lens[j]
                break
            between += lens[j]
        lo += between
        hi, between = L + 1, 0
        for j in order[i + 1:]:
            if j in starts:
                hi = starts[j]
                break
            between += lens[j]
        hi -= between + lens[k]
        best = (np.inf, lo)
        for st in range(lo, hi + 1):
            trial = {**starts, k: st}
            d = np.concatenate([bb_coords(design, range(trial[x], trial[x] + lens[x])) for x in trial])
            r = np.concatenate([ref[x] for x in trial])
            v = rmsd(d, r)
            if v < best[0]:
                best = (v, st)
        starts[k] = best[1]
    d = np.concatenate([bb_coords(design, range(starts[k], starts[k] + lens[k])) for k in order])
    return rmsd(d, np.concatenate([ref[k] for k in order])), starts


def assign_groups(design, group_res, gids, segs, ref):
    """Map output index-group id -> segment index, minimising joint motif backbone RMSD."""
    glen = {g: len(group_res[g]) for g in gids}
    if sorted(glen.values()) != sorted(sg["length"] for sg in segs):
        return None
    by_len = defaultdict(list)
    for k, sg in enumerate(segs):
        by_len[sg["length"]].append(k)
    g_by_len = defaultdict(list)
    for g in gids:
        g_by_len[glen[g]].append(g)
    lens = sorted(by_len)
    best = (np.inf, None)
    for perms in itertools.product(*[itertools.permutations(by_len[n]) for n in lens]):
        assign = {}
        for n, perm in zip(lens, perms):
            assign.update(dict(zip(g_by_len[n], perm)))
        d = np.concatenate([bb_coords(design, sorted(group_res[g])) for g in gids])
        r = np.concatenate([ref[assign[g]] for g in gids])
        v = rmsd(d, r)
        if v < best[0]:
            best = (v, assign)
    return best[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["indexed", "unindexed"], required=True)
    ap.add_argument("--samples", required=True)
    ap.add_argument("--seg-map", required=True)
    ap.add_argument("--motif-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--layout")
    ap.add_argument("--cases", nargs="*")
    ap.add_argument("--n", type=int, default=100)
    a = ap.parse_args()
    seg_map = json.load(open(a.seg_map))
    layout = {}
    if a.layout:
        for row in csv.DictReader(open(a.layout), delimiter="\t"):
            layout[(row["case"], int(row["sample_num"]))] = row["motif_placements"]
    samples = Path(a.samples)
    out = Path(a.out)
    cases = a.cases or sorted(seg_map)
    qc_rows = []
    for case in cases:
        info = seg_map[case]
        segs, L = info["segments"], info["length"]
        ref = motif_reference(Path(a.motif_dir) / f"{case}.pdb", segs)
        cdir = out / case
        cdir.mkdir(parents=True, exist_ok=True)
        rows = []
        for i in range(a.n):
            if a.mode == "indexed":
                cif = samples / f"{case}__{i}_0" / f"{case}__{i}_0_generated.cif"
            else:
                cif = samples / f"{case}_{i}" / f"{case}_{i}_generated.cif"
            if not cif.exists():
                qc_rows.append((case, i, "MISSING", "", "", ""))
                continue
            aa, cols = read_cif(cif)
            aa = aa[(aa.element != "H") & struc.filter_amino_acids(aa)]
            chains = list(dict.fromkeys(aa.chain_id))
            assert len(chains) == 1, (cif, chains)
            # renumber 1..L
            old = list(dict.fromkeys(aa.res_id))
            assert len(old) == L, (cif, len(old), L)
            remap = {r: k + 1 for k, r in enumerate(old)}
            aa.res_id = np.array([remap[r] for r in aa.res_id])
            aa.chain_id[:] = "A"
            aa.hetero[:] = False
            repaired = ""
            if a.mode == "indexed":
                place = layout[(case, i)]
                starts, pos = {}, 1
                k = 0
                for tok in place.split("/"):
                    if tok.isdigit():
                        pos += int(tok)
                    else:
                        starts[k] = pos
                        pos += segs[k]["length"]
                        k += 1
            else:
                full, _ = read_cif(cif)
                keep = (full.element != "H") & struc.filter_amino_acids(full)
                ins = cols["is_unindexed_insertion"][keep]
                grp = cols["annotation_src-index-group_1_atom"][keep]
                rid = aa.res_id
                group_res = defaultdict(set)
                for r, flag, g in zip(rid, ins, grp):
                    if str(flag).lower() in ("true", "1") and g not in (".", "?", "0", "-1"):
                        group_res[int(g)].add(int(r))
                gids = sorted(group_res)
                starts, ok = {}, len(gids) == len(segs)
                if ok:
                    # output group ids are not in segment order: assign groups to segments by joint
                    # backbone RMSD over all permutations among equal-length segments
                    assign = assign_groups(aa, group_res, gids, segs, ref)
                    ok = assign is not None
                if ok:
                    for g, k in assign.items():
                        rs = sorted(group_res[g])
                        if rs[-1] - rs[0] + 1 != len(rs):
                            ok = False
                        starts[k] = rs[0]
                    s_sorted = sorted(starts, key=starts.get)
                    for x, y in zip(s_sorted, s_sorted[1:]):
                        if starts[x] + segs[x]["length"] > starts[y]:
                            ok = False
                if not ok:
                    repaired_reason = (f"groups={len(gids)}/{len(segs)};sizes="
                                       + ",".join(str(len(group_res[g])) for g in gids))
                    mean_pos = {k: (np.mean(sorted(group_res[g])) if k < len(gids) else 1e9)
                                for k, g in enumerate(gids)} if gids else {}
                    order = sorted(range(len(segs)), key=lambda k: mean_pos.get(k, 1e9))
                    _, starts = window_search(aa, segs, ref, order, L)
                    repaired = "window_search:" + repaired_reason
                place = placement_string(starts, segs, L)
            d = np.concatenate([bb_coords(aa, range(starts[k], starts[k] + segs[k]["length"]))
                                for k in range(len(segs))])
            r = np.concatenate(ref)
            motif_rmsd = rmsd(d, r)
            f = pdb.PDBFile()
            f.set_structure(aa)
            f.write(str(cdir / f"{case}_{i}.pdb"))
            rows.append((i, place))
            qc_rows.append((case, i, place, f"{motif_rmsd:.3f}", repaired, str(cif)))
        with open(cdir / "scaffold_info.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["sample_num", "motif_placements"])
            w.writerows(rows)
        print(case, "converted", len(rows), flush=True)
    with open(out / "MBR4_qc.tsv", "a") as fh:
        for row in qc_rows:
            fh.write("\t".join(map(str, row)) + "\n")


if __name__ == "__main__":
    main()
