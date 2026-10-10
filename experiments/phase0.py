"""Aşama 0: ağsız temsil deneyi (ön kayıt: progress.md).

Her yama için K doğru doğrudan Adam ile optimize edilir; A, B, C aynı başlangıç yüzeyinden başlar.

  python experiments/phase0.py timing
  python experiments/phase0.py tune
  python experiments/phase0.py test
"""
import argparse
import itertools
import json
import pickle
import time
from pathlib import Path

import numpy as np
import torch

from ruled import data
from ruled.geometry import pair_metrics
from ruled.losses import chamfer, smoothness, surface_points, sample_area_weighted
from ruled.reps import REPS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "phase0"
K, S, U = 32, 4, 16
STEPS, EVAL_EVERY = 1000, 10
LRS = (1e-3, 3e-3, 1e-2, 3e-2)
LAMBDAS = (0.0, 1e-3, 1e-2, 1e-1)
SEEDS = (0, 1, 2, 3, 4)
DATA_SEEDS = {"tune": 1000, "test": 2000}
N_PER_FAMILY = {"tune": 10, "test": 40}
NOISE = 0.01
CHUNK = 50


def load_set(stage):
    path = OUT / f"data_{stage}.pkl"
    if path.exists():
        return pickle.loads(path.read_bytes())
    patches = data.make_set(N_PER_FAMILY[stage], DATA_SEEDS[stage], NOISE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pickle.dumps(patches))
    return patches


def initial_lines(points, seed):
    """PCA düzleminde 2. eksene paralel K doğru; tohumla geometrik bozulma."""
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
    return P.detach(), np.stack(curve, -1)          # curve: (B, steps/EVAL_EVERY)


@torch.no_grad()
def evaluate(rep, P, patches):
    gen = torch.Generator().manual_seed(0)
    pred = sample_area_weighted(rep, P, 4096, generator=gen)
    clean = torch.tensor(np.stack([p["clean_eval"] for p in patches]), dtype=torch.float32)
    cd = chamfer(pred.double(), clean.double()).numpy()
    d = torch.cdist(pred.double(), clean.double())
    nn = torch.cat([d.min(-1).values, d.min(-2).values], -1)
    haus, haus95 = nn.max(-1).values.numpy(), torch.quantile(nn, 0.95, dim=-1).numpy()
    a, m = rep.lines(P.double())
    _, _, recip, drall = pair_metrics(a, m)
    return dict(chamfer=cd, hausdorff=haus, hausdorff95=haus95,
                dsin=recip.mean(-1).numpy(), drall=drall.mean(-1).numpy())


def convergence_step(curve):
    final = curve[:, -1:]
    hit = curve <= 1.1 * final
    return (hit.argmax(-1) + 1) * EVAL_EVERY


def run(rep_name, patches, seed, lr, lam):
    rep = REPS[rep_name]
    rows = []
    for i in range(0, len(patches), CHUNK):
        chunk = patches[i:i + CHUNK]
        P, curve = optimize(rep, chunk, seed, lr, lam)
        ev = evaluate(rep, P, chunk)
        conv = convergence_step(curve)
        for j, pt in enumerate(chunk):
            rows.append(dict(patch=i + j, family=pt["family"], rep=rep_name, seed=seed,
                             lr=lr, lam=lam, conv=int(conv[j]), final_data=float(curve[j, -1]),
                             **{k: float(v[j]) for k, v in ev.items()}))
    return rows


def save(rows, name):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(rows, indent=0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["timing", "tune", "test"])
    ap.add_argument("--threads", type=int, default=8)
    args = ap.parse_args()
    torch.set_num_threads(args.threads)

    if args.stage == "timing":
        patches = load_set("tune")
        for name in REPS:
            t0 = time.time()
            optimize(REPS[name], patches[:CHUNK], 0, 1e-2, 0.0, steps=50)
            print(f"{name}: {(time.time() - t0) / 50:.3f} s/adım ({CHUNK} yama)")
        return

    if args.stage == "tune":
        patches = load_set("tune")
        rows = []
        for name, lr, lam in itertools.product(REPS, LRS, LAMBDAS):
            t0 = time.time()
            r = run(name, patches, 0, lr, lam)
            rows += r
            print(f"{name} lr={lr:g} λs={lam:g}  chamfer={np.mean([x['chamfer'] for x in r]):.3e}"
                  f"  ({time.time() - t0:.0f} s)", flush=True)
            save(rows, "tune.json")
        best = {}
        for name in REPS:
            cfg = {(lr, lam): np.mean([x["chamfer"] for x in rows
                                       if x["rep"] == name and x["lr"] == lr and x["lam"] == lam])
                   for lr, lam in itertools.product(LRS, LAMBDAS)}
            (lr, lam) = min(cfg, key=cfg.get)
            best[name] = dict(lr=lr, lam=lam, chamfer=cfg[(lr, lam)])
        (OUT / "best.json").write_text(json.dumps(best, indent=2))
        print(json.dumps(best, indent=2))
        return

    best = json.loads((OUT / "best.json").read_text())
    patches = load_set("test")
    rows = []
    for name in REPS:
        for seed in SEEDS:
            t0 = time.time()
            rows += run(name, patches, seed, best[name]["lr"], best[name]["lam"])
            print(f"{name} seed={seed} ({time.time() - t0:.0f} s)", flush=True)
            save(rows, "test.json")


if __name__ == "__main__":
    main()
