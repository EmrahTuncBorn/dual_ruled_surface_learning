"""Phase 1 evaluation: applies the pre-registered decision rule of v3 Section 5.5.

The decision uses the primary init only. The secondary init and the reversed layer (Hrev)
are reported with the same comparisons and do not enter the decision.
"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from phase0_analyze import compare
from phase1 import ARMS, INITS, N_PER_FAMILY, OUT, SEEDS, TAU

METRICS = ("chamfer", "G", "hausdorff", "hausdorff95", "dsin", "drall", "inside", "flip", "conv")
N_PATCH = 3 * N_PER_FAMILY["test"]
GROUPS = [(INITS[0], arm) for arm in ARMS] + [(INITS[0], "Hrev")] + [(INITS[1], arm) for arm in ARMS]


def load_rows():
    rows = [r for f in sorted((OUT / "test").glob("*.json")) for r in json.loads(f.read_text())]
    expected = len(GROUPS) * len(SEEDS) * N_PATCH
    if len(rows) != expected:
        raise SystemExit(f"expected {expected} rows, found {len(rows)}; the test runs are incomplete")
    commits = {r["commit"] for r in rows}
    if len(commits) != 1:
        raise SystemExit(f"rows come from several commits: {sorted(commits)}")
    return rows, commits.pop()


def per_patch(rows):
    """{(init, arm): {metric: (n_patch,)}}: mean over the five seeds, plus seed std of the Chamfer."""
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        for k in METRICS:
            by[(r["init"], r["arm"], r["patch"])][k].append(r[k])
    patches = sorted({r["patch"] for r in rows})
    family = {r["patch"]: r["family"] for r in rows}
    out = {}
    for g in GROUPS:
        m = defaultdict(list)
        for p in patches:
            d = by[g + (p,)]
            for k, v in d.items():
                m[k].append(np.mean(v))
            m["seed_std"].append(np.std(d["chamfer"], ddof=1))
        out[g] = {k: np.array(v) for k, v in m.items()}
    return out, np.array([family[p] for p in patches])


def decide(data, init):
    """v3 5.5 on one init: prerequisite on H's median G, then H against PA and PC on Chamfer."""
    h = data[(init, "H")]
    prereq = bool(np.median(h["G"]) <= TAU)
    verdicts = {o: compare(h["chamfer"], data[(init, o)]["chamfer"]) for o in ("PA", "PC")}
    v = [x[2] for x in verdicts.values()]
    if not prereq:
        decision = "weak (prerequisite failed)"
    elif "A worse" in v:
        decision = "weak"
    elif "A better" in v:
        decision = "strong"
    else:
        decision = "equivalent"
    return prereq, verdicts, decision


def main():
    rows, commit = load_rows()
    data, fam = per_patch(rows)
    selected = json.loads((OUT / "selected.json").read_text())
    report, lines = {}, [f"Commit: `{commit}`", f"tau = {TAU}", ""]

    lines += ["Selected settings (validation):", "", "| Arm | lr | lambda_s | lambda_d | reached tau |",
              "|---|---|---|---|---|"]
    for arm in ARMS:
        s = selected[arm]
        lines.append(f"| {arm} | {s['lr']:g} | {s['lam_s']:g} | {s['lam_d']:g} | {s['reached_tau']} |")

    for init in INITS:
        prereq, verdicts, decision = decide(data, init)
        report[init] = dict(prereq=prereq, H_median_G=float(np.median(data[(init, "H")]["G"])), decision=decision,
                            **{f"chamfer_H_vs_{o}": dict(ratio=r, p=p, verdict=v) for o, (r, p, v) in verdicts.items()})
        role = "primary, decision" if init == INITS[0] else "secondary, reported only"
        lines += ["", f"## Init: {init} ({role})", "",
                  f"Prerequisite: median G of H = {report[init]['H_median_G']:.4g} <= tau: {prereq}", "",
                  "| Metric | H vs | geo-mean ratio H/X | Wilcoxon p | Verdict |", "|---|---|---|---|---|"]
        for o in ("PA", "PC", "A0"):
            for k in ("chamfer", "G"):
                r, p, v = compare(data[(init, "H")][k], data[(init, o)][k])
                lines.append(f"| {k} | {o} | {r:.3f} | {p:.2e} | {v.replace('A ', 'H ')} |")
        lines += ["", "| Arm | chamfer | G mean | G median | flip | inside | seed_std |", "|---|---|---|---|---|---|---|"]
        for arm in list(ARMS) + (["Hrev"] if init == INITS[0] else []):
            d = data[(init, arm)]
            lines.append(f"| {arm} | {d['chamfer'].mean():.3e} | {d['G'].mean():.3e} | {np.median(d['G']):.3e} "
                         f"| {d['flip'].mean():.3f} | {d['inside'].mean():.3f} | {d['seed_std'].mean():.2e} |")
        lines += ["", "Per family (mean Chamfer x1e-4 / median G):", "",
                  "| Family | " + " | ".join(ARMS) + " |", "|---" * (len(ARMS) + 1) + "|"]
        for f in ("cylinder", "cone", "tangent"):
            sel = fam == f
            lines.append(f"| {f} | " + " | ".join(
                f"{1e4 * data[(init, a)]['chamfer'][sel].mean():.2f} / {np.median(data[(init, a)]['G'][sel]):.2e}"
                for a in ARMS) + " |")
        lines += ["", f"**Decision rule on this init: {decision}**"]

    r, p, v = compare(data[(INITS[0], "Hrev")]["chamfer"], data[(INITS[0], "H")]["chamfer"])
    report["Hrev_vs_H_chamfer"] = dict(ratio=r, p=p, verdict=v)
    lines += ["", f"Reversed layer (Hrev vs H, Chamfer): ratio {r:.3f}, p {p:.2e}, {v.replace('A ', 'Hrev ')}",
              "", f"**Decision (primary init): {report[INITS[0]]['decision']}**"]
    text = "\n".join(lines)
    (OUT / "report.md").write_text(text, encoding="utf-8")
    (OUT / "report.json").write_text(json.dumps(dict(report, commit=commit), indent=2))
    print(text)


if __name__ == "__main__":
    main()
