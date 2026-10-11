"""Phase 1: network-free developability experiment (v3 Section 5).

Arms on developable patches (cylinder, cone, tangent developable):
  A0  representation A, no developability term
  PA  A with the reciprocal-product penalty
  PC  C with the coplanarity-determinant penalty
  H   A with the hard developability layer

The structure follows phase0.py: every unit of work is written atomically to its own file
and skipped when present, and a run directory is bound to one git commit.

  python experiments/phase1.py scale      # lambda_d scale check on 5 validation patches (lambda_s 0)
  python experiments/phase1.py scale2     # the same check at lambda_s 1e-1 (T5)
  python experiments/phase1.py smooth     # folding check: A0 and H over a wider lambda_s range
  python experiments/phase1.py all        # validation sweep -> selection -> test (both inits)
"""
import argparse
import itertools
import json
import pickle
import time
from pathlib import Path

import numpy as np
import torch

import phase0 as p0
from ruled import data
from ruled.geometry import angle_defect_total, dot, pair_metrics
from ruled.losses import (chamfer, developability_A, developability_C, smoothness,
                          surface_grid, surface_points)
from ruled.reps import DualRep, DevelopableDualRep, EndpointRep

ROOT = p0.ROOT
OUT = ROOT / "results" / "phase1"
K, S, U = 32, 4, 16
STEPS, EVAL_EVERY = 1000, 10
LRS = (3e-2, 1e-1, 3e-1)
LAMBDA_S = (1e-2, 1e-1, 1.0)               # T5: lambda_s 0 and 1e-3 fold
LAMBDA_D = (1e-1, 1.0, 1e1, 1e2, 1e3)     # fixed by the scale check at lambda_s 1e-1 (v3 5.3)
SEEDS = (0, 1, 2, 3, 4)
DATA_SEEDS = {"val": 3000, "test": 4000}
N_PER_FAMILY = {"val": 10, "test": 40}
NOISE = 0.01
CHUNK = 50
TAU = 0.00756                              # v3 Section 4.2, experiments/phase1_tau.py
INITS = ("smooth", "phase0")               # primary, secondary (v3 Section 5.2)
SCALE_PATCHES = (0, 10, 20, 5, 15)         # cylinder, cone, tangent, cylinder, cone
SCALE_LAMBDA_D = tuple(10.0 ** k for k in range(-2, 7))
SMOOTH_LAMBDA_S = (0.0, 1e-2, 1e-1, 1.0, 1e1)

ARMS = {"A0": (DualRep, None), "PA": (DualRep, "A"), "PC": (EndpointRep, "C"), "H": (DevelopableDualRep, None)}


# ---------------------------------------------------------------------------
# Data and initialisation
# ---------------------------------------------------------------------------

def load_set(split, out=None):
    path = (out or OUT) / f"data_{split}.pkl"
    if path.exists():
        return pickle.loads(path.read_bytes())
    rng = np.random.default_rng(DATA_SEEDS[split])
    patches = [data.make_patch(f, rng, NOISE) for f in data.DEVELOPABLE for _ in range(N_PER_FAMILY[split])]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pickle.dumps(patches))
    return patches


def initial_lines(points, seed, init):
    """Phase 0 initial lines, or the same lines with a perturbation that is smooth in k.

    The smooth perturbation uses the cosine basis cos(pi j t), j = 0..3, with coefficients
    scaled so that the per-line standard deviation matches Phase 0 (0.1 for the direction,
    0.05 for the position).
    """
    if init == "phase0":
        return p0.initial_lines(points, seed)
    X = points - points.mean(0)
    _, _, Vt = np.linalg.svd(X, full_matrices=False)
    e1, e2 = Vt[0], Vt[1]
    x1, x2 = X @ e1, X @ e2
    p = np.linspace(x1.min(), x1.max(), K)[:, None] * e1 + points.mean(0)
    a = np.broadcast_to(e2, (K, 3)).copy()
    v0, v1 = np.full(K, x2.min()), np.full(K, x2.max())
    rng = np.random.default_rng(20_000 + seed)
    basis = np.cos(np.pi * np.arange(4)[:, None] * np.linspace(0, 1, K))       # (4, K)
    field = lambda sigma: basis.T @ rng.normal(scale=sigma / np.sqrt(2.5), size=(4, 3))
    n = field(0.1)
    a = data.unit(a + n - (n @ e2)[:, None] * e2)
    p = p + field(0.05)
    return a, p, v0, v1


def init_params(rep, patches, seed, init):
    lines = [initial_lines(pt["points"], seed, init) for pt in patches]
    a, p, v0, v1 = (torch.tensor(np.stack(x), dtype=torch.float32) for x in zip(*lines))
    return rep.init(a, p, v0, v1)


# ---------------------------------------------------------------------------
# Optimisation and evaluation
# ---------------------------------------------------------------------------

def penalty(arm, rep, P):
    kind = ARMS[arm][1]
    if kind == "A":
        return developability_A(rep, P)
    if kind == "C":
        return developability_C(P)
    return torch.zeros(P.shape[0], dtype=P.dtype)


def optimize(arm, patches, seed, lr, lam_s, lam_d, init, steps=STEPS):
    rep = ARMS[arm][0]
    torch.manual_seed(seed)
    pts = torch.tensor(np.stack([p["points"] for p in patches]), dtype=torch.float32)
    P = init_params(rep, patches, seed, init).requires_grad_(True)
    opt = torch.optim.Adam([P], lr=lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps)
    curve = []
    for it in range(steps):
        X = surface_points(rep, P, S, U, jitter=True)
        loss = chamfer(pts, X) + lam_s * smoothness(rep, P) + lam_d * penalty(arm, rep, P)
        opt.zero_grad()
        loss.sum().backward()
        opt.step()
        sched.step()
        if (it + 1) % EVAL_EVERY == 0:
            with torch.no_grad():
                curve.append(chamfer(pts, surface_points(rep, P, S, U)).numpy())
    return P.detach(), np.stack(curve, -1)


@torch.no_grad()
def meeting_inside(rep, P):
    """Fraction of consecutive line pairs whose closest-approach point lies inside either segment.

    For coplanar lines this is the meeting point; inside the segment the strip crosses itself.
    """
    p0_, p1_ = rep.segments(P, S=1)
    d1, d2 = p1_[..., :-1, :] - p0_[..., :-1, :], p1_[..., 1:, :] - p0_[..., 1:, :]
    w = p0_[..., :-1, :] - p0_[..., 1:, :]
    a, b, c, d, e = dot(d1, d1), dot(d1, d2), dot(d2, d2), dot(d1, w), dot(d2, w)
    den = a * c - b * b
    ok = den > 1e-12 * a * c
    s = (b * e - c * d) / den.clamp_min(1e-30)
    u = (a * e - b * d) / den.clamp_min(1e-30)
    inside = ok & (((s > 0) & (s < 1)) | ((u > 0) & (u < 1)))
    return inside.double().mean(-1)


@torch.no_grad()
def fold_rates(rep, P, S_grid=8, U_grid=64):
    """Two folding measures of the predicted surface.

    reversal: fraction of interior lines where the path of segment midpoints turns back
              (the step to the next midpoint points against the step from the previous one)
    flip:     fraction of neighbouring quad pairs across a line whose normals are opposed
    """
    q0, q1 = rep.segments(P, S=1)
    d = 0.5 * (q0 + q1).diff(dim=-2)
    reversal = (dot(d[..., 1:, :], d[..., :-1, :]) < 0).double().mean(-1)
    G = surface_grid(rep, P, S_grid, U_grid)
    n = torch.cross(G[..., 1:, :-1, :] - G[..., :-1, :-1, :], G[..., :-1, 1:, :] - G[..., :-1, :-1, :], dim=-1)
    flip = (dot(n[..., 1:, :, :], n[..., :-1, :, :]) < 0).double().mean((-1, -2))
    return reversal, flip


@torch.no_grad()
def evaluate(arm, P, patches):
    rep = ARMS[arm][0]
    ev = p0.evaluate(rep, P, patches)
    Pd = P.double()
    ev["G"] = angle_defect_total(surface_grid(rep, Pd)).numpy()
    ev["inside"] = meeting_inside(rep, Pd).numpy()
    ev["reversal"], ev["flip"] = (x.numpy() for x in fold_rates(rep, Pd))
    return ev


def run_unit(path, arm, patches, offset, seed, lr, lam_s, lam_d, init, commit):
    """Optimise and evaluate one chunk; write rows to path. Skipped if path exists."""
    if path.exists():
        return json.loads(path.read_text()), False
    P, curve = optimize(arm, patches, seed, lr, lam_s, lam_d, init)
    ev = evaluate(arm, P, patches)
    conv = p0.convergence_step(curve)
    rows = [dict(patch=offset + j, family=pt["family"], arm=arm, seed=seed, lr=lr, lam_s=lam_s,
                 lam_d=lam_d, init=init, conv=int(conv[j]), final_data=float(curve[j, -1]),
                 commit=commit, **{k: float(v[j]) for k, v in ev.items()})
            for j, pt in enumerate(patches)]
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(rows))
    tmp.replace(path)
    return rows, True


def run(split, arm, seed, lr, lam_s, lam_d, init, commit, tag, patches=None, out=None):
    out = out or OUT
    patches = patches if patches is not None else load_set(split, out)
    rows = []
    for i in range(0, len(patches), CHUNK):
        path = out / split / f"{tag}_chunk{i // CHUNK}.json"
        t0 = time.time()
        r, fresh = run_unit(path, arm, patches[i:i + CHUNK], i, seed, lr, lam_s, lam_d, init, commit)
        rows += r
        if fresh:
            print(f"{split} {tag} chunk {i // CHUNK}: chamfer={np.mean([x['chamfer'] for x in r]):.3e} "
                  f"G={np.mean([x['G'] for x in r]):.3e} inside={np.mean([x['inside'] for x in r]):.3f}"
                  f" ({time.time() - t0:.0f} s)", flush=True)
    return rows


def bind(out):
    p0.OUT = out                      # phase0.bind_commit writes the manifest into p0.OUT
    return p0.bind_commit()


# ---------------------------------------------------------------------------
# Stages
# ---------------------------------------------------------------------------

def scale_check(lam_s=0.0, name="phase1_scale"):
    """PA and PC over a wide lambda_d range on 5 validation patches (lr 1e-1, smooth init)."""
    out = ROOT / "results" / name
    commit = bind(out)
    patches = [load_set("val", out)[i] for i in SCALE_PATCHES]
    keys = ("chamfer", "G", "inside", "flip")
    lines = ["| arm | lambda_d | " + " | ".join(keys) + " |", "|---" * (len(keys) + 2) + "|"]
    configs = [("A0", 0.0), ("H", 0.0)] + [(arm, ld) for arm in ("PA", "PC") for ld in SCALE_LAMBDA_D]
    for arm, ld in configs:
        r = run("val", arm, 0, 1e-1, lam_s, ld, "smooth", commit, f"{arm}_lamd{ld:g}", patches, out)
        m = {k: np.mean([x[k] for x in r]) for k in keys}
        lines.append(f"| {arm} | {ld:g} | " + " | ".join(f"{m[k]:.3e}" if k in ("chamfer", "G") else f"{m[k]:.3f}"
                                                         for k in keys) + " |")
    text = "\n".join(lines + ["", f"lambda_s = {lam_s}, tau = {TAU}"])
    (out / "report.md").write_text(text, encoding="utf-8")
    print(text, flush=True)


def smooth_check():
    """A0 and H over a wider lambda_s range on the scale patches (lr 1e-1, smooth init).

    Validation only and not decision data: tests whether the smoothness term removes folding.
    """
    out = ROOT / "results" / "phase1_smooth"
    commit = bind(out)
    patches = [load_set("val", out)[i] for i in SCALE_PATCHES]
    keys = ("chamfer", "G", "inside", "reversal", "flip")
    lines = ["| arm | lambda_s | " + " | ".join(keys) + " |", "|---" * (len(keys) + 2) + "|"]
    for arm, ls in itertools.product(("A0", "H"), SMOOTH_LAMBDA_S):
        r = run("val", arm, 0, 1e-1, ls, 0.0, "smooth", commit, f"{arm}_lams{ls:g}", patches, out)
        m = {k: np.mean([x[k] for x in r]) for k in keys}
        lines.append(f"| {arm} | {ls:g} | " + " | ".join(f"{m[k]:.3e}" if k in ("chamfer", "G") else f"{m[k]:.3f}"
                                                         for k in keys) + " |")
    text = "\n".join(lines + ["", f"tau = {TAU}"])
    (out / "report.md").write_text(text, encoding="utf-8")
    print(text, flush=True)


def select(rows):
    """v3 Section 5.3 selection rule; rows of one init (validation, seed 0)."""
    def mean(arm, lr, ls, ld, key):
        return np.mean([x[key] for x in rows if x["arm"] == arm and x["lr"] == lr
                        and x["lam_s"] == ls and x["lam_d"] == ld])
    best = {}
    for arm in ARMS:
        if ARMS[arm][1] is None:
            score = {(lr, ls, 0.0): mean(arm, lr, ls, 0.0, "chamfer") for lr, ls in itertools.product(LRS, LAMBDA_S)}
            cfg = min(score, key=score.get)
            best[arm] = dict(lr=cfg[0], lam_s=cfg[1], lam_d=0.0, val_chamfer=score[cfg], reached_tau=None)
            continue
        cand = {}
        for lr, ls in itertools.product(LRS, LAMBDA_S):
            hit = [ld for ld in LAMBDA_D if mean(arm, lr, ls, ld, "G") <= TAU]
            if hit:
                cand[(lr, ls, min(hit))] = mean(arm, lr, ls, min(hit), "chamfer")
        if cand:
            cfg = min(cand, key=cand.get)
            reached = True
        else:
            g = {(lr, ls, ld): mean(arm, lr, ls, ld, "G")
                 for lr, ls, ld in itertools.product(LRS, LAMBDA_S, LAMBDA_D)}
            cfg = min(g, key=g.get)
            reached = False
        best[arm] = dict(lr=cfg[0], lam_s=cfg[1], lam_d=cfg[2],
                         val_chamfer=mean(arm, *cfg, "chamfer"), val_G=mean(arm, *cfg, "G"), reached_tau=reached)
    return best


def validation_sweep(commit):
    rows = []
    for arm in ARMS:
        lds = LAMBDA_D if ARMS[arm][1] else (0.0,)
        for lr, ls, ld in itertools.product(LRS, LAMBDA_S, lds):
            rows += run("val", arm, 0, lr, ls, ld, "smooth", commit, f"{arm}_lr{lr:g}_lams{ls:g}_lamd{ld:g}")
    best = select(rows)
    (OUT / "selected.json").write_text(json.dumps(dict(best, commit=commit), indent=2))
    print(json.dumps(best, indent=2), flush=True)
    return best


def test_runs(best, commit):
    """Primary init first, then the secondary robustness check with the same selections."""
    for init in INITS:
        for arm in ARMS:
            b = best[arm]
            for seed in SEEDS:
                run("test", arm, seed, b["lr"], b["lam_s"], b["lam_d"], init, commit, f"{init}_{arm}_seed{seed}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["scale", "scale2", "smooth", "all"])
    ap.add_argument("--threads", type=int, default=8)
    args = ap.parse_args()
    torch.set_num_threads(args.threads)
    if args.stage == "scale":
        scale_check()
        return
    if args.stage == "scale2":
        scale_check(1e-1, "phase1_scale_ls0.1")
        return
    if args.stage == "smooth":
        smooth_check()
        return
    commit = bind(OUT)
    best = validation_sweep(commit)
    test_runs(best, commit)
    print("done", flush=True)


if __name__ == "__main__":
    main()
