# Origin: cc
# Purpose: Print per-token condition annotations (C_IDX, C_SEQ, C_CRD + group columns) of an annotated RFD4 CIF.
import sys

import rfproteina.conditions  # noqa: F401  registers RFD4 condition columns before parse
from atomworks.io import parse
from atomworks.ml.conditions import C_CRD, C_IDX, C_SEQ
from atomworks.ml.utils.token import get_token_starts
from rfproteina.utils.parse_presets import ANNOTATED_CIF

for path in sys.argv[1:]:
    aa = parse(path, config=ANNOTATED_CIF)["assemblies"]["1"][0]
    starts = get_token_starts(aa)
    cats = sorted(aa.get_annotation_categories())
    print("==", path, "atoms", len(aa), "tokens", len(starts))
    print("annotations:", [c for c in cats if c.startswith("condition") or "standard" in c or c.isupper()])
    idx = C_IDX.mask(aa, default="generate")
    crd = C_CRD.mask(aa, default="generate")
    seq = C_SEQ.mask(aa, default="generate")
    grp = [c for c in cats if "index-group" in c or "CoordinateGroup" in c or "insertion" in c.lower()]
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else len(aa)
        extra = {g.split("_")[1]: aa.get_annotation(g)[s] for g in grp}
        print(f"{aa.chain_id[s]} {aa.res_id[s]:4d} {aa.res_name[s]:>4} idx={int(idx[s])} seq={int(seq[s])} "
              f"crd={int(crd[s:e].sum())}/{e - s} {extra}")
