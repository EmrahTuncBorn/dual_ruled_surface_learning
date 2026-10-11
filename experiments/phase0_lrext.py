"""Exploratory (not pre-registered in Phase 0): extends the learning-rate grid upward.

In Phase 0 the selected lr lay on the upper edge of the grid for all three
representations. This script repeats the validation sweep on a wider grid and
re-runs the test only for representations whose selection changes; the others
reuse the Phase 0 test rows. It never changes the Phase 0 decision.

  python experiments/phase0_lrext.py
"""
import json

import numpy as np
import torch

import phase0 as p0
import phase0_analyze as an

ORIG = p0.OUT
p0.OUT = p0.ROOT / "results" / "phase0_lrext"
p0.LRS = (3e-2, 1e-1, 3e-1)          # 3e-2 is repeated as a reproducibility check
p0.LAMBDAS = (0.0, 1e-3)             # the lambdas selected in Phase 0


def test_rows(out):
    return [r for f in sorted((out / "test").glob("*.json")) for r in json.loads(f.read_text())]


def main():
    torch.set_num_threads(8)
    commit = p0.bind_commit()
    best = p0.validation_sweep(commit)
    orig = json.loads((ORIG / "selected.json").read_text())
    changed = [n for n in p0.REPS
               if (best[n]["lr"], best[n]["lam"]) != (orig[n]["lr"], orig[n]["lam"])]
    print("changed selections:", changed, flush=True)
    for name in changed:
        for seed in p0.SEEDS:
            p0.run("test", name, seed, best[name]["lr"], best[name]["lam"], commit, f"{name}_seed{seed}")

    rows = ([r for r in test_rows(ORIG) if r["rep"] not in changed]
            + [r for r in test_rows(p0.OUT) if r["rep"] in changed])
    if len(rows) != an.N_EXPECTED:
        raise SystemExit(f"expected {an.N_EXPECTED} rows, found {len(rows)}")
    data, _ = an.per_patch(rows)
    commits = {rep: sorted({r["commit"][:7] for r in rows if r["rep"] == rep}) for rep in p0.REPS}

    lines = ["Exploratory: wider lr grid. Does not change the Phase 0 decision.", "",
             "| Rep | Phase 0 (lr, lam) | wide grid (lr, lam) | val chamfer | test rows from |",
             "|---|---|---|---|---|"]
    for n in p0.REPS:
        lines.append(f"| {n} | {orig[n]['lr']:g}, {orig[n]['lam']:g} | {best[n]['lr']:g}, {best[n]['lam']:g} "
                     f"| {best[n]['val_chamfer']:.3e} | {', '.join(commits[n])} |")
    lines += ["", "| Metric | vs | geo-mean ratio A/X | Wilcoxon p | Verdict |", "|---|---|---|---|---|"]
    report = {}
    for other in ("B", "C"):
        for k in an.PRIMARY:
            gm, p, v = an.compare(data["A"][k], data[other][k])
            report[f"{k}_vs_{other}"] = dict(ratio=gm, p=p, verdict=v)
            lines.append(f"| {k} | {other} | {gm:.3f} | {p:.2e} | {v} |")
    lines += ["", "| Rep | chamfer | conv (steps) | seed_std |", "|---|---|---|---|"]
    for r in p0.REPS:
        lines.append(f"| {r} | {data[r]['chamfer'].mean():.3e} | {np.mean(data[r]['conv']):.0f} "
                     f"| {data[r]['seed_std'].mean():.3e} |")
    text = "\n".join(lines)
    (p0.OUT / "report.md").write_text(text, encoding="utf-8")
    (p0.OUT / "report.json").write_text(json.dumps(dict(report, selected=best, changed=changed,
                                                        commits=commits), indent=2))
    print(text, flush=True)


if __name__ == "__main__":
    main()
