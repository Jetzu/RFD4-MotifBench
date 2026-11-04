# Run the official MotifBench evaluate_bbs.sh for one (set, case) on a Modal L40S (3 problems share one GPU), using the same environment as the cluster runs.
# Machine-specific locations are environment variables (see config.example.env); SLURM account/partition lines removed.
"""
Same environment as the local runs, at the same absolute paths:
  - MotifBench's motif_bench conda env (torch 2.8.0+cu128) extracted from the volume at image build
  - $MOTIFBENCH_DIR checkout (Scaffold-Lab, motif_pdbs, scripts) mounted from local disk
  - ESMFold torch-hub weights and the Foldseek PDB database read from the volume mbr4-motifbench
Scaffold and result directories also keep their local absolute paths, so the result files are
indistinguishable from local runs. Only change vs the official call (same as local): cwd is a
work dir with a setup.cfg root marker and hydra.run.dir points there.

Deploy once:   modal deploy modal_evaluate.py          (L40S, 3 problems per GPU)
Drive:         python modal_evaluate.py <tasks.tsv> [<tasks.tsv> ...]   (see client() below)
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

ENV = os.environ["MOTIFBENCH_ENV"]
MB = os.environ["MOTIFBENCH_DIR"]
FOLDSEEK_DB_DIR = os.environ["FOLDSEEK_DB_DIR"]
VOL_NAME = "mbr4-motifbench"
APP_NAME = "mbr4-motifbench-eval"

vol = modal.Volume.from_name(VOL_NAME, create_if_missing=True)
app = modal.App(APP_NAME)


def _extract_env():
    with tarfile.open("/vol/motif_bench_env.tar") as t:
        t.extractall("/")


image = (
    # same OS as the cluster nodes (Ubuntu 24.04, glibc 2.39): the env has wheels built against glibc 2.38+
    modal.Image.from_registry("ubuntu:24.04", add_python="3.11")
    .apt_install("build-essential", "libaio-dev", "procps")
    .run_function(_extract_env, volumes={"/vol": vol})
    .env({"MOTIFBENCH_ENV": ENV, "MOTIFBENCH_DIR": MB, "FOLDSEEK_DB_DIR": FOLDSEEK_DB_DIR})
    .add_local_dir(MB, MB, ignore=["tmp", "tmp/**", "outputs", "outputs/**", ".git", ".git/**"])
)


# L40S: ~91 TFLOPS fp32 (ESMFold runs fp32), ~3x an A10G for <2x the price -> cheaper per problem.
# Three problems share one GPU (ESMFold ~10 GB each of 48 GB) so the CPU-bound phases
# (ProteinMPNN subprocess per backbone, Foldseek novelty) overlap with GPU folding.
@app.function(image=image, gpu="L40S", cpu=24.0, memory=98304, volumes={"/vol": vol},
              timeout=10 * 3600, max_containers=55)  # user approved >10 GPUs (2026-11-03)
@modal.concurrent(max_inputs=3)
def eval_case(set_name: str, case: str, scaffold_dir: str, result_dir: str, config_text: str,
              scaffold_tar: bytes) -> dict:
    t0 = time.time()
    # assets at their local paths
    os.makedirs(os.path.dirname(FOLDSEEK_DB_DIR), exist_ok=True)
    try:
        os.symlink("/vol/foldseek_database", FOLDSEEK_DB_DIR)
    except FileExistsError:
        pass
    # scaffolds at their local path (fresh copy; drop leftovers of an earlier input)
    subprocess.call(["rm", "-rf", scaffold_dir, result_dir])
    Path(scaffold_dir).parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(scaffold_tar), mode="r:gz") as t:
        t.extractall(Path(scaffold_dir).parent)
    work = Path(f"/tmp/mbr4_work/{set_name}__{case}")
    subprocess.call(["rm", "-rf", str(work)])
    (work / case).mkdir(parents=True, exist_ok=True)
    (work / "setup.cfg").touch()  # Scaffold-Lab rootutils root marker (it chdirs here, writes tmp/)
    cfg = work / "config.txt"
    cfg.write_text(config_text)
    env = dict(os.environ, CUDA_HOME=ENV, PATH=f"{ENV}/bin:" + os.environ["PATH"],
               TRITON_CACHE_DIR=f"/tmp/triton_{set_name}_{case}", TORCH_HOME="/vol/torch")
    log = work / case / "eval.log"
    with open(log, "w") as fh:
        rc = subprocess.call(["bash", f"{MB}/scripts/evaluate_bbs.sh", case, str(cfg),
                              f"hydra.run.dir={work / case / 'hydra'}",
                              "evaluation.foldseek_cores_for_pdbTM=8"],
                             cwd=work / case, env=env, stdout=fh, stderr=subprocess.STDOUT)
    ok = rc == 0 and os.path.exists(f"{result_dir}/esm_summary.txt")
    out = f"/vol/results/{set_name}/{case}.tar.gz"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with tarfile.open(out, "w:gz") as t:
        if os.path.isdir(result_dir):
            t.add(result_dir, arcname=result_dir.lstrip("/"))
        mi = Path(scaffold_dir) / "motif_info.csv"
        if mi.exists():
            t.add(str(mi), arcname=str(mi).lstrip("/"))
        t.add(str(log), arcname=f"{result_dir.lstrip('/')}/MBR4_modal_eval.log")
    gpu = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                         capture_output=True, text=True).stdout.strip()
    res = dict(set=set_name, case=case, rc=rc, ok=ok, seconds=round(time.time() - t0), gpu=gpu, tar=out)
    with open(f"/vol/results/{set_name}/{case}.json", "w") as fh:
        json.dump(res, fh)
    vol.commit()
    return res


def _pull(remote_vol, res, rdir):
    data = b"".join(remote_vol.read_file(res["tar"].replace("/vol/", "", 1)))
    if os.path.isdir(rdir):
        subprocess.call(["rm", "-rf", rdir])
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as t:
        t.extractall("/")


def client(task_files, max_attempts=3):
    """Run on a SLURM CPU node. Idempotent: skips cases already evaluated locally, pulls results that are
    already on the volume (earlier client runs), spawns the rest, retries failures. Exit 0 iff all done."""
    fn = modal.Function.from_name(APP_NAME, "eval_case")
    remote_vol = modal.Volume.from_name(VOL_NAME)
    todo = []
    for tf in task_files:
        set_name = Path(tf).stem.replace("MBR4_tasks_", "")
        for line in open(tf):
            case, cfgpath, _wd = line.rstrip("\n").split("\t")
            cfg_text = open(cfgpath).read()
            conf = dict(l.split("=", 1) for l in cfg_text.splitlines() if "=" in l)
            sdir = f"{conf['scaffold_base_dir']}/{case}"
            rdir = f"{conf['base_output_dir']}/{case}"
            if os.path.exists(f"{rdir}/esm_summary.txt"):
                continue
            try:
                res = json.loads(b"".join(remote_vol.read_file(f"results/{set_name}/{case}.json")))
                if res.get("ok"):
                    _pull(remote_vol, res, rdir)
                    print("PULLED", res, flush=True)
                    continue
            except Exception:  # noqa: BLE001  (no earlier result on the volume)
                pass
            todo.append((set_name, case, sdir, rdir, cfg_text))
    print(f"to evaluate: {len(todo)}", flush=True)

    def spawn(t):
        set_name, case, sdir, rdir, cfg_text = t
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as tar:
            tar.add(sdir, arcname=case, filter=lambda ti: None if ti.name.endswith("motif_info.csv") else ti)
        return fn.spawn(set_name, case, sdir, rdir, cfg_text, buf.getvalue())

    pending = [(t, spawn(t), 1) for t in todo]
    print(f"spawned {len(pending)}", flush=True)
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
                res = dict(set=t[0], case=t[1], ok=False, error=repr(e))
            if res.get("ok"):
                _pull(remote_vol, res, t[3])
                print("DONE", res, flush=True)
            elif attempt < max_attempts:
                print("RETRY", attempt, res, flush=True)
                still.append((t, spawn(t), attempt + 1))
            else:
                print("FAILED", res, flush=True)
                failed.append(t[:2])
        pending = still
        if pending:
            time.sleep(60)
    print("client finished; failed:", failed, flush=True)
    return 0 if not failed else 3


if __name__ == "__main__":
    sys.exit(client(sys.argv[1:]))
