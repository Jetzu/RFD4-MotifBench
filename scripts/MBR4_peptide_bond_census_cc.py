# Origin: cc
# Purpose: Peptide-bond census of submitted MotifBench scaffolds (same check as the RFD3-Unindexed-MotifBench write-up): count designs with any C(i)-N(i+1) bond > 2 A, and whether breaks sit at motif junctions.
# Machine-specific locations are environment variables (see config.example.env); SLURM account/partition lines removed.
"""Usage: python MBR4_peptide_bond_census_cc.py <scaffolds_dir> [<scaffolds_dir> ...] --out <tsv>
Writes one row per design: set, case, sample, n_breaks(>2A), max_CN, breaks_at_motif_boundary, placement."""
import argparse
import csv
import sys
from pathlib import Path

import numpy as np


def bb(pdb):
    C, N, rid = {}, {}, []
    for l in open(pdb):
        if l.startswith("ATOM"):
            a, r = l[12:16].strip(), int(l[22:26])
            xyz = np.array([float(l[30:38]), float(l[38:46]), float(l[46:54])])
            if a == "C":
                C[r] = xyz
            elif a == "N":
                N[r] = xyz
    rs = sorted(set(C) & set(N))
    d = np.array([np.linalg.norm(N[b] - C[a]) for a, b in zip(rs, rs[1:])])
    return rs, d


def motif_boundaries(placement):
    """Residue indices i such that bond i->i+1 enters or leaves a motif segment (1-indexed)."""
    pos, edges, segs = 1, set(), {}
    for tok in placement.split("/"):
        if tok.isdigit():
            pos += int(tok)
        else:
            segs[tok] = pos
    return segs


ap = argparse.ArgumentParser()
ap.add_argument("dirs", nargs="+")
ap.add_argument("--out", required=True)
ap.add_argument("--lens", required=True, help="seg_map.json for segment lengths")
a = ap.parse_args()
import json
seg_map = json.load(open(a.lens))
rows = []
for d in a.dirs:
    set_name = Path(d).name.replace("scaffolds_", "")
    for case_dir in sorted(Path(d).glob("[0-9][0-9]_*")):
        case = case_dir.name
        seglen = {s["orig_chain"]: s["length"] for s in seg_map[case]["segments"]}
        place = {int(r["sample_num"]): r["motif_placements"] for r in csv.DictReader(open(case_dir / "scaffold_info.csv"))}
        for i in range(100):
            rs, dist = bb(case_dir / f"{case}_{i}.pdb")
            starts = motif_boundaries(place[i])
            edge = set()
            for ch, s in starts.items():
                edge.add(s - 1)                    # bond (s-1)->s enters segment
                edge.add(s + seglen[ch] - 1)       # bond (end)->(end+1) leaves segment
            brk = [rs[k] for k in np.flatnonzero(dist > 2.0)]
            rows.append((set_name, case, i, len(brk), f"{dist.max():.2f}", sum(b in edge for b in brk), place[i]))
with open(a.out, "w") as f:
    f.write("set\tcase\tsample\tn_breaks_gt2A\tmax_CN\tbreaks_at_motif_boundary\tplacement\n")
    for r in rows:
        f.write("\t".join(map(str, r)) + "\n")
import collections
by = collections.defaultdict(lambda: [0, 0])
for r in rows:
    by[r[0]][0] += 1
    by[r[0]][1] += r[3] > 0
for s, (n, b) in sorted(by.items()):
    print(f"{s}: {b}/{n} designs with a C-N bond > 2 A ({100*b/n:.1f}%)")
