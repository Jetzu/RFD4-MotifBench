# Origin: cc
# Purpose: Build RFD4-Proteina condition specs (YAML) for the 30 MotifBench problems, indexed and unindexed.
"""
Inputs (read-only):
  --json-dir   RFD3 ExpertGuess contig JSONs (contig, length, select_unfixed_sequence)
  --gly-dir    motif PDBs with redesignable residues as backbone-only GLY
  --mb-dir     MotifBench checkout (motif_pdbs/ with UNK = redesignable, used as ground truth)

Outputs (under --out):
  motifs/<case>.cif                 motif merged onto ONE chain A, segments in contig order,
                                    segment k numbered 100*k+1 ... (gap so segments are not bonded)
  seg_map.json                      per case: [{orig_chain, new_start, length}] in contig order
  indexed/rep<r>/<case>.yaml        100 design keys <case>__<i>, every gap length fixed, total == length
  indexed/rep<r>/layout.tsv         case, sample_num, motif_placements (MotifBench format)
  unindexed/<case>.yaml             one key; one expandable segment of exactly `length` residues,
                                    every motif segment unindexed in its own index group

Conditioning (both modes): fixed-identity motif residues get C_CRD on all atoms + C_SEQ;
redesignable residues (UNK in MotifBench) get C_CRD on backbone N/CA/C/O only and no C_SEQ.
"""
import argparse
import copy
import json
import random
from pathlib import Path

import biotite.structure as struc
import biotite.structure.io.pdb as pdb
import biotite.structure.io.pdbx as pdbx
import numpy as np
import yaml

BB = ("N", "CA", "C", "O")


def parse_contig(contig):
    toks = []
    for t in contig.split(","):
        t = t.strip()
        if t[0].isalpha():
            a, b = t[1:].split("-") if "-" in t[1:] else (t[1:], t[1:])
            toks.append(("motif", t[0], int(a), int(b)))
        else:
            a, b = t.split("-") if "-" in t else (t, t)
            toks.append(("gap", int(a), int(b)))
    return toks


def sample_gaps(gaps, budget, rng):
    """Uniformly sample each gap within its range, conditioned on the total == budget (rejection, then fallback)."""
    lo = [g[0] for g in gaps]
    hi = [g[1] for g in gaps]
    assert sum(lo) <= budget <= sum(hi), (gaps, budget)
    for _ in range(200000):
        x = [rng.randint(a, b) for a, b in zip(lo, hi)]
        if sum(x) == budget:
            return x
    # sequential feasible-bounds sampling in random order (only for very constrained cases)
    order = list(range(len(gaps)))
    rng.shuffle(order)
    x = [0] * len(gaps)
    rem = budget
    for n, i in enumerate(order):
        rest = order[n + 1:]
        a = max(lo[i], rem - sum(hi[j] for j in rest))
        b = min(hi[i], rem - sum(lo[j] for j in rest))
        x[i] = rng.randint(a, b)
        rem -= x[i]
    return x


def load_pdb(path):
    return pdb.PDBFile.read(str(path)).get_structure(model=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-dir", required=True)
    ap.add_argument("--gly-dir", required=True)
    ap.add_argument("--mb-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--seed", type=int, default=20261103)
    a = ap.parse_args()
    out = Path(a.out)
    (out / "motifs").mkdir(parents=True, exist_ok=True)
    seg_map = {}
    cases = sorted(p.stem for p in Path(a.json_dir).glob("*.json"))
    assert len(cases) == 30, cases
    layouts = {r: [] for r in range(1, a.reps + 1)}
    for case in cases:
        spec = json.load(open(Path(a.json_dir) / f"{case}.json"))["motif"]
        length = int(spec["length"])
        toks = parse_contig(spec["contig"])
        gly = load_pdb(Path(a.gly_dir) / f"{case}.pdb")
        unk = load_pdb(Path(a.mb_dir) / "motif_pdbs" / f"{case}.pdb")
        # ---- merge motif segments onto chain A in contig order
        pieces, segs = [], []
        redesign = set()
        motif_toks = [t for t in toks if t[0] == "motif"]
        for k, (_, ch, s, e) in enumerate(motif_toks, start=1):
            m = gly[(gly.chain_id == ch) & (gly.res_id >= s) & (gly.res_id <= e)].copy()
            u = unk[(unk.chain_id == ch) & (unk.res_id >= s) & (unk.res_id <= e)]
            assert len(np.unique(m.res_id)) == e - s + 1, (case, ch, s, e)
            # gly and MotifBench coordinates must agree on the backbone
            for r in range(s, e + 1):
                gm = m[(m.res_id == r) & np.isin(m.atom_name, BB)]
                um = u[(u.res_id == r) & np.isin(u.atom_name, BB)]
                assert np.abs(gm.coord - um.coord).max() < 1e-3, (case, ch, r)
                if u.res_name[u.res_id == r][0] == "UNK":
                    redesign.add(100 * k + (r - s) + 1)
            new_start = 100 * k + 1
            m.res_id = m.res_id - s + new_start
            m.chain_id[:] = "A"
            m.hetero[:] = False
            pieces.append(m)
            segs.append(dict(orig_chain=ch, orig_start=s, new_start=new_start, length=e - s + 1))
        motif = struc.concatenate(pieces)
        # cross-check the redesign set against the JSON (when given)
        unf = spec.get("select_unfixed_sequence")
        seg_map[case] = dict(length=length, segments=segs, redesign=sorted(redesign),
                             json_unfixed=unf, contig=spec["contig"])
        # gly file must hold GLY (backbone only) at exactly the redesign positions
        for rid in sorted(redesign):
            names = set(motif.atom_name[motif.res_id == rid])
            assert names <= set(BB) | {"CB"}, (case, rid, names)
        cif = pdbx.CIFFile()
        pdbx.set_structure(cif, motif)
        cif_path = out / "motifs" / f"{case}.cif"
        cif.write(str(cif_path))

        fixed_ids = sorted(set(int(x) for x in motif.res_id) - redesign)
        rd_ids = sorted(redesign)

        def rng_list(ids):
            return "[" + ", ".join(str(i) for i in ids) + "]"

        cond_crd, cond_seq = [], []
        if fixed_ids:
            cond_crd.append({"select": f"sel('A/*/{rng_list(fixed_ids)}')"})
            cond_seq.append({"select": f"sel('A/*/{rng_list(fixed_ids)}')"})
        if rd_ids:
            cond_crd.append({"select": f"sel('A/*/{rng_list(rd_ids)}') and is_protein_backbone"})
        base_conditions = {"C_CRD": {True: cond_crd}}
        if cond_seq:
            base_conditions["C_SEQ"] = {True: cond_seq}

        motif_tokens = [f"A{sg['new_start']}-{sg['new_start'] + sg['length'] - 1}" for sg in segs]
        motif_len = sum(sg["length"] for sg in segs)

        # ---- unindexed: one key, generated chain of exactly `length`
        uidx = copy.deepcopy(base_conditions)
        uidx["C_IDX"] = {False: [{"select": f"sel('A/*/[{sg['new_start']}-{sg['new_start'] + sg['length'] - 1}]')",
                                  "group": f"seg{k}"} for k, sg in enumerate(segs, start=1)]}
        # expandable segment first, then the unindexed motif tokens (same layout as the repo's
        # data/benchmarks/motif_scaffolding/motif_unindexed/*.cif.zst)
        udoc = {case: {"input": f"../motifs/{case}.cif",
                       "contig": ", ".join([f"SCAF:{length}"] + motif_tokens),
                       "conditions": uidx}}
        (out / "unindexed").mkdir(exist_ok=True)
        yaml.safe_dump(udoc, open(out / "unindexed" / f"{case}.yaml", "w"), sort_keys=False)

        # ---- indexed: per-design fixed gap lengths, total == length
        gaps = [(t[1], t[2]) for t in toks if t[0] == "gap"]
        for r in range(1, a.reps + 1):
            rng = random.Random(f"{a.seed}-{case}-{r}")
            doc = {}
            for i in range(a.n):
                g = sample_gaps(gaps, length - motif_len, rng)
                parts, place, gi, mi = [], [], 0, 0
                for t in toks:
                    if t[0] == "gap":
                        n = g[gi]
                        gi += 1
                        if n > 0:
                            parts.append(f"G{gi}:{n}")
                            place.append(str(n))
                    else:
                        parts.append(motif_tokens[mi])
                        place.append(segs[mi]["orig_chain"])
                        mi += 1
                assert sum(int(p) for p in place if p.isdigit()) + motif_len == length
                doc[f"{case}__{i}"] = {"input": f"../../motifs/{case}.cif", "contig": ", ".join(parts),
                                       "conditions": copy.deepcopy(base_conditions)}
                layouts[r].append((case, i, "/".join(place)))
            d = out / "indexed" / f"rep{r}"
            d.mkdir(parents=True, exist_ok=True)
            yaml.safe_dump(doc, open(d / f"{case}.yaml", "w"), sort_keys=False)
        print(case, length, spec["contig"], "segs", [(s["orig_chain"], s["length"]) for s in segs],
              "redesign", len(redesign), "json_unfixed", unf)
    for r, rows in layouts.items():
        with open(out / "indexed" / f"rep{r}" / "layout.tsv", "w") as f:
            f.write("case\tsample_num\tmotif_placements\n")
            for row in rows:
                f.write("\t".join(map(str, row)) + "\n")
    json.dump(seg_map, open(out / "seg_map.json", "w"), indent=1)


if __name__ == "__main__":
    main()
