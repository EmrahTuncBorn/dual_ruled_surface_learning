"""Phase 0 evaluation: applies the pre-registered decision rule of PROGRESS.md."""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

OUT = Path(__file__).resolve().parents[1] / "results" / "phase0"
PRIMARY = ("chamfer", "conv", "seed_std")
SECONDARY = ("hausdorff", "hausdorff95", "dsin", "drall")
RATIO, ALPHA = 0.9, 0.01
N_EXPECTED = 3 * 5 * 200


def load_rows():
    rows = [r for f in sorted((OUT / "test").glob("*.json")) for r in json.loads(f.read_text())]
    if len(rows) != N_EXPECTED:
        raise SystemExit(f"expected {N_EXPECTED} rows, found {len(rows)}; the test runs are incomplete")
    commits = {r["commit"] for r in rows}
    if len(commits) != 1:
        raise SystemExit(f"rows come from several commits: {sorted(commits)}")
    return rows, commits.pop()


def per_patch(rows):
    """{rep: {metric: (n_patch,)}}: mean over the five seeds, plus seed std of the final Chamfer."""
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        for k in ("chamfer", "conv") + SECONDARY:
            by[(r["rep"], r["patch"])][k].append(r[k])
    reps = sorted({r["rep"] for r in rows})
    patches = sorted({r["patch"] for r in rows})
    family = {r["patch"]: r["family"] for r in rows}
    out = {}
    for rep in reps:
        m = defaultdict(list)
        for p in patches:
            d = by[(rep, p)]
            for k, v in d.items():
                m[k].append(np.mean(v))
            m["seed_std"].append(np.std(d["chamfer"], ddof=1))
        out[rep] = {k: np.array(v) for k, v in m.items()}
    return out, np.array([family[p] for p in patches])


def compare(x, y):
    """Geometric-mean ratio x/y and paired Wilcoxon p; lower is better for every metric."""
    floor = 1e-12
    gm = float(np.exp(np.mean(np.log((x + floor) / (y + floor)))))
    p = float(wilcoxon(x, y).pvalue) if np.any(x != y) else 1.0
    if gm <= RATIO and p < ALPHA:
        verdict = "A better"
    elif gm >= 1 / RATIO and p < ALPHA:
        verdict = "A worse"
    else:
        verdict = "no difference"
    return gm, p, verdict


def main():
    rows, commit = load_rows()
    data, fam = per_patch(rows)
    report = {}
    lines = [f"Commit: `{commit}`", "",
             "| Metric | vs | geo-mean ratio A/X | Wilcoxon p | Verdict |", "|---|---|---|---|---|"]
    for other in ("B", "C"):
        for k in PRIMARY:
            gm, p, v = compare(data["A"][k], data[other][k])
            report[f"{k}_vs_{other}"] = dict(ratio=gm, p=p, verdict=v)
            lines.append(f"| {k} | {other} | {gm:.3f} | {p:.2e} | {v} |")

    vs_c = [report[f"{k}_vs_C"]["verdict"] for k in PRIMARY]
    alive = "A better" in vs_c and "A worse" not in vs_c
    decision = "representation axis ALIVE" if alive else "representation axis WEAK"

    lines += ["", "Final Chamfer per family (mean, x1e-4):", "",
              "| Family | A | B | C |", "|---|---|---|---|"]
    for f in sorted(set(fam)):
        sel = fam == f
        lines.append(f"| {f} | " + " | ".join(f"{1e4 * data[r]['chamfer'][sel].mean():.3f}"
                                              for r in ("A", "B", "C")) + " |")
    lines += ["", "Mean primary metrics:", "", "| Rep | chamfer | conv (steps) | seed_std |", "|---|---|---|---|"]
    for r in ("A", "B", "C"):
        lines.append(f"| {r} | {data[r]['chamfer'].mean():.3e} | {data[r]['conv'].mean():.0f} "
                     f"| {data[r]['seed_std'].mean():.3e} |")
    lines += ["", "Secondary metrics on developable families (mean):", "",
              "| Family | Rep | d sin(theta) | drall d/theta |", "|---|---|---|---|"]
    for f in ("cylinder", "cone", "tangent"):
        sel = fam == f
        for r in ("A", "B", "C"):
            lines.append(f"| {f} | {r} | {data[r]['dsin'][sel].mean():.2e} | {data[r]['drall'][sel].mean():.2e} |")
    lines += ["", f"**Decision: {decision}**"]
    text = "\n".join(lines)
    (OUT / "report.md").write_text(text, encoding="utf-8")
    (OUT / "report.json").write_text(json.dumps(dict(report, decision=decision, commit=commit), indent=2))
    print(text)


if __name__ == "__main__":
    main()
