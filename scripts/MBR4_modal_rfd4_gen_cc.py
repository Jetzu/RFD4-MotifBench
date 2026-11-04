# Origin: cc
# Purpose: Run rfd4-generate chunks on Modal GPUs with the same environment as the lab's cu128 Apptainer image (full pip freeze), resumable client that pulls outputs back to their local paths.
# Machine-specific locations are environment variables (see config.example.env); SLURM account/partition lines removed.
"""
Environment: python 3.12 + the exact package freeze of rfd4-proteina-cu128.sif
(containers/rfd4-proteina-cu128-build/container-environment.txt, torch 2.11.0+cu128), RFD4 source at
commit ed63183a installed editable at /opt/rfd4 (rootutils needs /opt/rfd4/.project-root), weights bundle
on the volume mbr4-rfd4 (/vol/bundle). Same rfd4-generate arguments as scripts/run/MBR4_rfd4_generate_cc.sh.
Spec files reference motif CIFs and outputs by absolute local paths; those paths are recreated in the
container, so outputs land in the same place locally after pulling.

Deploy:  modal deploy MBR4_modal_rfd4_gen_cc.py
Drive:   python MBR4_modal_rfd4_gen_cc.py <tasks.tsv>   (spec, out_dir, num_replicates, seed, extra-override)
"""
import io
import json
import os
import subprocess
import sys
import tarfile
import time
from pathlib import Path

import modal
import modal.exception

REPO = os.environ.get("RFD4_REPO", "")  # image build only
FREEZE = os.environ.get("RFD4_PIP_FREEZE", "")  # image build only: pip freeze of a working RFD4 cu128 environment
APP_NAME = "mbr4-rfd4-gen"
vol = modal.Volume.from_name("mbr4-rfd4", create_if_missing=True)
app = modal.App(APP_NAME)

image = (
    modal.Image.from_registry("python:3.12-slim-bookworm")
    .apt_install("build-essential", "libxrender1", "libx11-6", "libxext6", "git")
    .pip_install("uv")
    .add_local_file(FREEZE, "/opt/freeze_full.txt", copy=True)
    .run_commands(
        "grep -v '^rfd4-proteina' /opt/freeze_full.txt > /opt/freeze.txt",
        "uv pip install --system --no-cache --no-sources --torch-backend cu128 "
        "--only-binary tmol,tmol-ops-cu12 -r /opt/freeze.txt",
    )
    .add_local_dir(REPO, "/opt/rfd4", copy=True,
                   ignore=[".git", ".git/**", "data/benchmarks", "data/benchmarks/**", "docs", "docs/**", "website",
                           "website/**", "examples", "examples/**", "assets", "assets/**", ".agents", ".agents/**",
                           ".claude", ".claude/**", "tests", "tests/**"])
    .run_commands("uv pip install --system --no-cache --no-sources --no-deps -e /opt/rfd4",
                  "python -c 'import torch, rfproteina, atomworks; print(torch.__version__)'")
    .env({"DATA_PATH": "/data", "HF_HOME": "/root/.cache/huggingface", "HF_HUB_OFFLINE": "1",
          "TMOL_DISABLE_WHEEL_FETCH": "1", "TMOL_JIT_FALLBACK": "0", "TMOL_USE_JIT": "0",
          "PYTHONNOUSERSITE": "1", "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
          "CLUSTER": "local", "DEBUG": "false"})
)


@app.function(image=image, gpu="L40S", cpu=8.0, memory=65536, volumes={"/vol": vol},
              timeout=10 * 3600, max_containers=30)  # user approved >10 GPUs for MBR4 (2026-11-03)
def gen_task(task_id: str, spec_path: str, spec_text: str, motifs: dict, out_dir: str, nrep: int, seed: int,
             extra: str) -> dict:
    t0 = time.time()
    for path, data in motifs.items():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_bytes(data)
    Path(spec_path).parent.mkdir(parents=True, exist_ok=True)
    Path(spec_path).write_text(spec_text)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    work = Path(f"/tmp/work_{task_id}")
    work.mkdir(parents=True, exist_ok=True)
    cmd = ["rfd4-generate", f"inputs={spec_path}", f"out_dir={out_dir}", f"num_replicates={nrep}", f"seed={seed}",
           "hf_ckpt_path=/vol/bundle", "~metrics", "num_workers=2"] + ([extra] if extra else [])
    log = work / "gen.log"
    with open(log, "w") as fh:
        rc = subprocess.call(cmd, cwd=work, stdout=fh, stderr=subprocess.STDOUT)
    samples = sorted(Path(out_dir, "inference_samples").glob("*"))
    n = sum(1 for _ in Path(out_dir, "inference_samples").glob("*/*_generated.cif"))
    out = f"/vol/gen/{task_id}.tar.gz"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with tarfile.open(out, "w:gz") as t:
        for s in samples:
            t.add(str(s), arcname=str(s).lstrip("/"))
        t.add(str(log), arcname=f"{out_dir.lstrip('/')}/MBR4_modal_gen_{task_id}.log")
    gpu = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                         capture_output=True, text=True).stdout.strip()
    res = dict(task=task_id, rc=rc, n_cif=n, seconds=round(time.time() - t0), gpu=gpu, tar=out)
    with open(f"/vol/gen/{task_id}.json", "w") as fh:
        json.dump(res, fh)
    vol.commit()
    return res


def _pull(rv, res):
    data = b"".join(rv.read_file(res["tar"].replace("/vol/", "", 1)))
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as t:
        t.extractall("/")


def client(task_file, max_attempts=2):
    fn = modal.Function.from_name(APP_NAME, "gen_task")
    rv = modal.Volume.from_name("mbr4-rfd4")
    todo = []
    for k, line in enumerate(open(task_file)):
        spec, out_dir, nrep, seed, extra = (line.rstrip("\n").split("\t") + [""])[:5]
        task_id = f"{Path(out_dir).name}__{Path(spec).stem}"
        try:
            res = json.loads(b"".join(rv.read_file(f"gen/{task_id}.json")))
            if res.get("rc") == 0 and res.get("n_cif", 0) > 0:
                _pull(rv, res)
                print("PULLED", res, flush=True)
                continue
        except Exception:  # noqa: BLE001
            pass
        spec_text = open(spec).read()
        motifs = {}
        for l in spec_text.splitlines():
            if l.strip().startswith("input:"):
                p = l.split("input:", 1)[1].strip()
                if p not in motifs:
                    motifs[p] = open(p, "rb").read()
        todo.append((task_id, spec, spec_text, motifs, out_dir, int(nrep), int(seed), extra))
    print(f"to generate: {len(todo)}", flush=True)
    pending = [(t, fn.spawn(*t), 1) for t in todo]
    failed = []
    while pending:
        still = []
        for t, fc, attempt in pending:
            try:
                res = fc.get(timeout=0)
            except (TimeoutError, modal.exception.TimeoutError):
                still.append((t, fc, attempt))
                continue
            except Exception as e:  # noqa: BLE001
                res = dict(task=t[0], rc=-1, n_cif=0, error=repr(e))
            if res.get("rc") == 0 and res.get("n_cif", 0) > 0:
                _pull(rv, res)
                print("DONE", res, flush=True)
            elif attempt < max_attempts:
                print("RETRY", res, flush=True)
                still.append((t, fn.spawn(*t), attempt + 1))
            else:
                print("FAILED", res, flush=True)
                failed.append(t[0])
        pending = still
        if pending:
            time.sleep(60)
    print("gen client finished; failed:", failed, flush=True)
    return 0 if not failed else 3


if __name__ == "__main__":
    sys.exit(client(sys.argv[1]))
