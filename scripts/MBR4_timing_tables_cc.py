# Origin: cc
# Purpose: Timing + GPU tables for generation (per job and per problem) and evaluation (per problem) from SLURM/Modal logs and output timestamps.
# Machine-specific locations are environment variables (see config.example.env); SLURM account/partition lines removed.
"""Sources
  generation jobs : logs/MBR4_N002_gen_621780_<i>.out (task line, nvidia-smi line, /usr/bin/time wall clock)
  per problem     : mtimes of the 100 output CIFs per problem (sequential within a job) -> s/design without compile
  evaluation      : logs/MBR4_N003_eval_*.out (cluster: 'case .. gpu ..' + 'exit 0 after N s')
                    logs/MBR4_supervisor_622537.out (Modal: DONE dicts with seconds + gpu; 3 problems shared one GPU)
Usage: python MBR4_timing_tables_cc.py --out <dir> [--sweep]   (writes MBR4_timing_*.csv, prints a summary)"""
import argparse
import ast
import csv
import glob
import os
import re
import statistics as st
from pathlib import Path

P = Path(os.environ["MBR4_ROOT"])
G = P / "runs/MBR4_N002_rfd4-production-generation-30-motifbench"
CASES = sorted(p.stem for p in (P / "in/specs/unindexed").glob("*.yaml"))


def hms(s):
    parts = [float(x) for x in s.split(":")]
    return sum(v * 60 ** i for i, v in enumerate(reversed(parts)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    out = Path(ap.parse_args().out)
    # ---- generation per job
    jobs = []
    for f in sorted(glob.glob(str(P / "logs/MBR4_N002_gen_621780_*.out")), key=lambda x: int(x.rsplit("_", 1)[1][:-4])):
        txt = open(f).read()
        m = re.search(r"specs/MBR4_(indexed|unindexed)_rep(\d)_c(\d)\.yaml", txt)
        gpu = re.search(r"^(NVIDIA [^,]+), ([\d.]+), (\d+) MiB", txt, re.M)
        wall = re.findall(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): ([\d:.]+)", txt)
        mode, rep, chunk = m.group(1), int(m.group(2)), int(m.group(3))
        jobs.append(dict(mode=mode, rep=rep, chunk=chunk, problems=",".join(CASES[(chunk - 1) * 10:chunk * 10]),
                         designs=1000, gpu=gpu.group(1), compute_capability=gpu.group(2), gpu_mem_mib=int(gpu.group(3)),
                         wall_s=round(hms(wall[-1])), s_per_design=round(hms(wall[-1]) / 1000, 2)))
    with open(out / "MBR4_timing_generation_per_job.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(jobs[0]))
        w.writeheader()
        w.writerows(jobs)
    # ---- generation per problem (from output mtimes; excludes model load / compile)
    gpu_of = {(j["mode"], j["rep"], c): j["gpu"] for j in jobs for c in j["problems"].split(",")}
    rows = []
    for mode in ("indexed", "unindexed"):
        for rep in (1, 2, 3):
            d = G / f"out_{mode}_rep{rep}/inference_samples"
            for c in CASES:
                pat = f"{c}__*_0/*_generated.cif" if mode == "indexed" else f"{c}_[0-9]*/*_generated.cif"
                ts = sorted(os.path.getmtime(x) for x in d.glob(pat))
                if len(ts) < 2:
                    continue
                gaps = [b - a for a, b in zip(ts, ts[1:])]
                rows.append(dict(mode=mode, rep=rep, problem=c, gpu=gpu_of[(mode, rep, c)], designs=len(ts),
                                 median_s_per_design=round(st.median(gaps), 2), mean_s_per_design=round(sum(gaps) / len(gaps), 2)))
    with open(out / "MBR4_timing_generation_per_problem.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    # ---- evaluation per problem
    ev = []
    for f in glob.glob(str(P / "logs/MBR4_N003_eval_*.out")):
        txt = open(f).read()
        m = re.search(r"^case (\S+) cfg \S+MBR4_config_(\S+)\.txt host \S+ gpu (.+?) cc ([\d.]+)$", txt, re.M)
        e = re.search(r"^exit 0 after (\d+) s", txt, re.M)
        if m and e:
            ev.append(dict(set=m.group(2), problem=m.group(1), where="cluster", gpu=m.group(3),
                           problems_sharing_gpu=1, wall_s=int(e.group(1))))
    for line in open(P / "logs/MBR4_supervisor_622537.out"):
        if line.startswith("DONE "):
            d = ast.literal_eval(line[5:].strip())
            ev.append(dict(set=d["set"], problem=d["case"], where="modal", gpu=d["gpu"], problems_sharing_gpu=3,
                           wall_s=d["seconds"]))
    ev.sort(key=lambda r: (r["set"], r["problem"]))
    with open(out / "MBR4_timing_evaluation_per_problem.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ev[0]))
        w.writeheader()
        w.writerows(ev)
    # ---- summary
    print("GENERATION per job (1000 designs each):")
    by = {}
    for j in jobs:
        by.setdefault((j["mode"], j["gpu"]), []).append(j)
    for (mode, gpu), js in sorted(by.items()):
        print(f"  {mode:9s} {gpu:22s} jobs {len(js):2d}  wall {sum(j['wall_s'] for j in js) / 3600:5.1f} h  "
              f"{st.mean(j['s_per_design'] for j in js):.2f} s/design (incl. load+compile)")
    print(f"  total {sum(j['wall_s'] for j in jobs) / 3600:.1f} GPU-h for {len(jobs) * 1000} designs")
    print("GENERATION per problem (median s/design, steady state):")
    for mode in ("indexed", "unindexed"):
        v = [r["median_s_per_design"] for r in rows if r["mode"] == mode]
        print(f"  {mode:9s} median {st.median(v):.2f}  range {min(v):.2f}-{max(v):.2f} s/design")
    print("EVALUATION per problem:")
    for where in ("cluster", "modal"):
        for gpu in sorted({r["gpu"] for r in ev if r["where"] == where}):
            v = [r["wall_s"] / 60 for r in ev if r["where"] == where and r["gpu"] == gpu]
            print(f"  {where:7s} {gpu:28s} n={len(v):3d}  median {st.median(v):5.1f} min  range {min(v):.0f}-{max(v):.0f} min")


if __name__ == "__main__":
    main()
