"""Phase 0: network-free representation experiment (pre-registered in PROGRESS.md).

For every patch, K lines are optimised directly with Adam; A, B and C start from
the same initial surface. The run is resumable: every unit of work
(representation, configuration, seed, chunk) is written to its own file and
skipped when it already exists. A run directory is bound to one git commit.

  python experiments/phase0.py timing
  python experiments/phase0.py all        # validation sweep -> selection -> test
"""
import argparse
import itertools
import json
import pickle
import subprocess
import time
from pathlib import Path

import numpy as np
import torch

from ruled import data
from ruled.geometry import pair_metrics
from ruled.losses import chamfer, nearest, smoothness, surface_points, sample_area_weighted
from ruled.reps import REPS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "phase0"
K, S, U = 32, 4, 16
STEPS, EVAL_EVERY = 1000, 10
LRS = (1e-3, 3e-3, 1e-2, 3e-2)
LAMBDAS = (0.0, 1e-3, 1e-2, 1e-1)
SEEDS = (0, 1, 2, 3, 4)
DATA_SEEDS = {"val": 1000, "test": 2000}
N_PER_FAMILY = {"val": 10, "test": 40}
NOISE = 0.01
CHUNK = 50


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                          check=True).stdout.strip()


def bind_commit(allow_dirty=False):
    """Return HEAD; refuse a dirty tree or a run directory made by another commit."""
    commit = git("rev-parse", "HEAD")
    if git("status", "--porcelain") and not allow_dirty:
        raise SystemExit("working tree is not clean; commit before running")
    manifest = OUT / "manifest.json"
    if manifest.exists():
        bound = json.loads(manifest.read_text())["commit"]
        if bound != commit:
            raise SystemExit(f"{OUT} belongs to commit {bound[:7]}, HEAD is {commit[:7]}; "
                             "use a new run directory or check out that commit")
    else:
        OUT.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps({"commit": commit}, indent=2))
    return commit


# ---------------------------------------------------------------------------
# Data and initialisation
# ---------------------------------------------------------------------------

def load_set(split):
    path = OUT / f"data_{split}.pkl"
    if path.exists():
        return pickle.loads(path.read_bytes())
    patches = data.make_set(N_PER_FAMILY[split], DATA_SEEDS[split], NOISE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pickle.dumps(patches))
    return patches


def initial_lines(points, seed):
    """K lines parallel to the 2nd principal axis on the PCA plane, perturbed per seed."""
    X = points - points.mean(0)
    _, _, Vt = np.linalg.svd(X, full_matrices=False)
    e1, e2 = Vt[0], Vt[1]
    x1, x2 = X @ e1, X @ e2
    p = np.linspace(x1.min(), x1.max(), K)[:, None] * e1 + points.mean(0)
    a = np.broadcast_to(e2, (K, 3)).copy()
    v0, v1 = np.full(K, x2.min()), np.full(K, x2.max())
    rng = np.random.default_rng(10_000 + seed)
    n = rng.normal(scale=0.1, size=(K, 3))
    a = data.unit(a + n - (n @ e2)[:, None] * e2)
    p = p + rng.normal(scale=0.05, size=(K, 3))
    return a, p, v0, v1


def init_params(rep, patches, seed):
    lines = [initial_lines(pt["points"], seed) for pt in patches]
    a, p, v0, v1 = (torch.tensor(np.stack(x), dtype=torch.float32) for x in zip(*lines))
    return rep.init(a, p, v0, v1)


# ---------------------------------------------------------------------------
# Optimisation and evaluation
# ---------------------------------------------------------------------------

def optimize(rep, patches, seed, lr, lam, steps=STEPS):
    torch.manual_seed(seed)
    pts = torch.tensor(np.stack([p["points"] for p in patches]), dtype=torch.float32)
    P = init_params(rep, patches, seed).requires_grad_(True)
    opt = torch.optim.Adam([P], lr=lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps)
    curve = []
    for it in range(steps):
        X = surface_points(rep, P, S, U, jitter=True)
        loss = chamfer(pts, X) + lam * smoothness(rep, P)
        opt.zero_grad()
        loss.sum().backward()
        opt.step()
        sched.step()
        if (it + 1) % EVAL_EVERY == 0:
            with torch.no_grad():
                curve.append(chamfer(pts, surface_points(rep, P, S, U)).numpy())
    return P.detach(), np.stack(curve, -1)          # curve: (B, steps / EVAL_EVERY)


@torch.no_grad()
def evaluate(rep, P, patches):
    gen = torch.Generator().manual_seed(0)
    pred = sample_area_weighted(rep, P, 4096, generator=gen).double()
    clean = torch.tensor(np.stack([p["clean_eval"] for p in patches]), dtype=torch.float64)
    ix, iy = nearest(pred, clean)          # the dense 50x4096x4096 matrix does not fit in RAM
    take = lambda z, i: torch.gather(z, 1, i[..., None].expand(-1, -1, 3))
    nn = torch.cat([(pred - take(clean, ix)).norm(dim=-1),
                    (clean - take(pred, iy)).norm(dim=-1)], -1)
    n_pred = pred.shape[1]
    cd = nn[:, :n_pred].square().mean(-1) + nn[:, n_pred:].square().mean(-1)
    a, m = rep.lines(P.double())
    _, _, recip, drall = pair_metrics(a, m)
    return dict(chamfer=cd.numpy(), hausdorff=nn.max(-1).values.numpy(),
                hausdorff95=torch.quantile(nn, 0.95, dim=-1).numpy(),
                dsin=recip.mean(-1).numpy(), drall=drall.mean(-1).numpy())


def convergence_step(curve):
    hit = curve <= 1.1 * curve[:, -1:]
    return (hit.argmax(-1) + 1) * EVAL_EVERY


def run_unit(path, rep_name, patches, offset, seed, lr, lam, commit):
    """Optimise and evaluate one chunk; write rows to path. Skipped if path exists."""
    if path.exists():
        return json.loads(path.read_text()), False
    rep = REPS[rep_name]
    P, curve = optimize(rep, patches, seed, lr, lam)
    ev = evaluate(rep, P, patches)
    conv = convergence_step(curve)
    rows = [dict(patch=offset + j, family=pt["family"], rep=rep_name, seed=seed, lr=lr, lam=lam,
                 conv=int(conv[j]), final_data=float(curve[j, -1]), commit=commit,
                 **{k: float(v[j]) for k, v in ev.items()})
            for j, pt in enumerate(patches)]
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(rows))
    tmp.replace(path)                       # atomic: a killed run never leaves half a file
    return rows, True


def run(split, rep_name, seed, lr, lam, commit, tag):
    patches = load_set(split)
    rows = []
    for i in range(0, len(patches), CHUNK):
        path = OUT / split / f"{tag}_chunk{i // CHUNK}.json"
        t0 = time.time()
        r, fresh = run_unit(path, rep_name, patches[i:i + CHUNK], i, seed, lr, lam, commit)
        rows += r
        if fresh:
            print(f"{split} {tag} chunk {i // CHUNK}: chamfer={np.mean([x['chamfer'] for x in r]):.3e}"
                  f" ({time.time() - t0:.0f} s)", flush=True)
    return rows


# ---------------------------------------------------------------------------
# Stages
# ---------------------------------------------------------------------------

def validation_sweep(commit):
    rows = []
    for name, lr, lam in itertools.product(REPS, LRS, LAMBDAS):
        rows += run("val", name, 0, lr, lam, commit, f"{name}_lr{lr:g}_lam{lam:g}")
    best = {}
    for name in REPS:
        score = {(lr, lam): np.mean([x["chamfer"] for x in rows
                                     if x["rep"] == name and x["lr"] == lr and x["lam"] == lam])
                 for lr, lam in itertools.product(LRS, LAMBDAS)}
        lr, lam = min(score, key=score.get)
        best[name] = dict(lr=lr, lam=lam, val_chamfer=score[(lr, lam)])
    (OUT / "selected.json").write_text(json.dumps(dict(best, commit=commit), indent=2))
    print(json.dumps(best, indent=2), flush=True)
    return best


def test_runs(best, commit):
    for name in REPS:
        for seed in SEEDS:
            run("test", name, seed, best[name]["lr"], best[name]["lam"], commit,
                f"{name}_seed{seed}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["timing", "all"])
    ap.add_argument("--threads", type=int, default=8)
    args = ap.parse_args()
    torch.set_num_threads(args.threads)

    if args.stage == "timing":
        patches = data.make_set(N_PER_FAMILY["val"], DATA_SEEDS["val"], NOISE)
        for name in REPS:
            t0 = time.time()
            optimize(REPS[name], patches[:CHUNK], 0, 1e-2, 0.0, steps=50)
            print(f"{name}: {(time.time() - t0) / 50:.3f} s/step ({CHUNK} patches)")
        return

    commit = bind_commit()
    best = validation_sweep(commit)
    test_runs(best, commit)
    print("done", flush=True)


if __name__ == "__main__":
    main()
