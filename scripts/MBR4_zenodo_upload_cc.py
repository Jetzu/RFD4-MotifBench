# Origin: cc
# Purpose: Create a Zenodo DRAFT deposition for the RFD4 MotifBench submission (reserved DOI), upload the archives; publishing stays a manual step on zenodo.org.
# Machine-specific locations are environment variables (see config.example.env); SLURM account/partition lines removed.
"""Token: a Zenodo personal access token with scopes deposit:write + deposit:actions, read from $ZENODO_TOKEN or
~/.zenodo_token (chmod 600). Nothing is published: the deposition stays a draft; its reserved DOI is printed and
written next to the archives so it can go into the GitHub README before you press "Publish".

Usage: python MBR4_zenodo_upload_cc.py <file> [<file> ...] [--sandbox]"""
import json
import os
import sys
import urllib.request
from pathlib import Path

D = Path(os.environ["MBR4_ROOT"]) / "deliverables"
args = [a for a in sys.argv[1:] if not a.startswith("--")]
BASE = "https://sandbox.zenodo.org/api" if "--sandbox" in sys.argv else "https://zenodo.org/api"
tok = os.environ.get("ZENODO_TOKEN") or Path.home().joinpath(".zenodo_token").read_text().strip()


def api(method, url, data=None, headers=None):
    h = {"Authorization": f"Bearer {tok}", **(headers or {})}
    body = json.dumps(data).encode() if isinstance(data, dict) else data
    if isinstance(data, dict):
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=h, method=method)
    with urllib.request.urlopen(req, timeout=24 * 3600) as r:
        txt = r.read()
    return json.loads(txt) if txt else {}


meta = {"metadata": {
    "title": "RFD4-Proteina on MotifBench: indexed and unindexed motif scaffolding (3 replicates each)",
    "upload_type": "dataset",
    "description": (
        "Submission archives for the MotifBench motif-scaffolding benchmark (30 problems) with RFD4-Proteina. "
        "One archive per mode (indexed: MotifBench reference contigs; unindexed: RFD4 places the motif segments). "
        "Each contains 3 independently generated replicates of 100 designs per problem in MotifBench format "
        "(scaffold PDBs + scaffold_info.csv), the full output of MotifBench's evaluate_bbs.sh, the official "
        "summaries, the raw RFD4 outputs, inputs and scripts. MotifBench score (official, mean +- SD over 3 replicates): "
        "indexed 55.06 +- 1.35, unindexed 60.36 +- 0.87. Write-up: https://github.com/Jetzu/RFD4-MotifBench"),
    "creators": [{"name": "Gerstung, Lukas", "affiliation": "Technical University of Munich"}],
    "keywords": ["protein design", "motif scaffolding", "MotifBench", "RFD4-Proteina", "RFdiffusion"],
    "related_identifiers": [{"identifier": "https://github.com/Jetzu/RFD4-MotifBench", "relation": "isSupplementTo"},
                            {"identifier": "https://github.com/blt2114/MotifBench", "relation": "references"}],
    "license": "cc-by-4.0",
    "prereserve_doi": True,
}}
dep = api("POST", f"{BASE}/deposit/depositions", meta)
doi = dep["metadata"]["prereserve_doi"]["doi"]
print("draft deposition", dep["id"], "reserved DOI", doi, "edit:", dep["links"]["html"], flush=True)
bucket = dep["links"]["bucket"]
for f in args:
    p = Path(f)
    size = p.stat().st_size
    print(f"uploading {p.name} ({size / 1e9:.2f} GB) ...", flush=True)
    with open(p, "rb") as fh:
        res = api("PUT", f"{bucket}/{p.name}", data=fh, headers={"Content-Length": str(size),
                                                                     "Content-Type": "application/octet-stream"})
    print("  done, checksum", res.get("checksum"), flush=True)
(D / "zenodo" / "MBR4_zenodo_draft.json").write_text(json.dumps(
    {"deposition_id": dep["id"], "reserved_doi": doi, "edit_url": dep["links"]["html"],
     "files": [Path(f).name for f in args]}, indent=1))
print("DRAFT ONLY - review and publish at", dep["links"]["html"])
