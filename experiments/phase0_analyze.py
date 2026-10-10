"""Aşama 0 değerlendirmesi: progress.md'deki ön kayıtlı karar kuralını uygular."""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

OUT = Path(__file__).resolve().parents[1] / "results" / "phase0"
PRIMARY = ("chamfer", "conv", "seed_std")
RATIO, ALPHA = 0.9, 0.01


def per_patch(rows):
    """{rep: {metric: (n_patch,)}} — beş tohumun ortalaması ve son Chamfer'ın tohum sapması."""
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by[(r["rep"], r["patch"])]["chamfer"].append(r["chamfer"])
        for k in ("conv", "hausdorff", "hausdorff95", "dsin", "drall"):
            by[(r["rep"], r["patch"])][k].append(r[k])
    reps = sorted({r["rep"] for r in rows})
    patches = sorted({r["patch"] for r in rows})
    fam = {r["patch"]: r["family"] for r in rows}
    out = {}
    for rep in reps:
        m = defaultdict(list)
        for p in patches:
            d = by[(rep, p)]
            for k, v in d.items():
                m[k].append(np.mean(v))
            m["seed_std"].append(np.std(d["chamfer"], ddof=1))
        out[rep] = {k: np.array(v) for k, v in m.items()}
    return out, np.array([fam[p] for p in patches])


def compare(x, y):
    """X'in Y'ye oranı (geometrik ortalama) ve eşleştirilmiş Wilcoxon p."""
    floor = 1e-12
    gm = float(np.exp(np.mean(np.log((x + floor) / (y + floor)))))
    p = float(wilcoxon(x, y).pvalue) if np.any(x != y) else 1.0
    verdict = "A iyi" if gm <= RATIO and p < ALPHA else "A kötü" if gm >= 1 / RATIO and p < ALPHA else "fark yok"
    return gm, p, verdict


def main():
    rows = json.loads((OUT / "test.json").read_text())
    data, fam = per_patch(rows)
    report = {}
    lines = ["| Ölçüt | Karşı | geo. ort. oran A/X | Wilcoxon p | Sonuç |", "|---|---|---|---|---|"]
    for other in ("B", "C"):
        for k in PRIMARY:
            gm, p, v = compare(data["A"][k], data[other][k])
            report[f"{k}_vs_{other}"] = dict(ratio=gm, p=p, verdict=v)
            lines.append(f"| {k} | {other} | {gm:.3f} | {p:.2e} | {v} |")

    vs_c = [report[f"{k}_vs_C"]["verdict"] for k in PRIMARY]
    alive = "A iyi" in vs_c and "A kötü" not in vs_c
    decision = "Temsil ekseni CANLI" if alive else "Temsil ekseni ZAYIF"

    lines += ["", "Aile bazında son Chamfer (ortalama, ×1e-4):", "",
              "| Aile | A | B | C |", "|---|---|---|---|"]
    for f in sorted(set(fam)):
        sel = fam == f
        lines.append(f"| {f} | " + " | ".join(f"{1e4 * data[r]['chamfer'][sel].mean():.3f}"
                                              for r in ("A", "B", "C")) + " |")
    lines += ["", "Açılabilir ailelerde ikincil ölçütler (ortalama):", "",
              "| Aile | Temsil | d·sinθ | drall d/θ |", "|---|---|---|---|"]
    for f in ("cylinder", "cone", "tangent"):
        sel = fam == f
        for r in ("A", "B", "C"):
            lines.append(f"| {f} | {r} | {data[r]['dsin'][sel].mean():.2e} | {data[r]['drall'][sel].mean():.2e} |")
    lines += ["", f"**Karar: {decision}**"]
    text = "\n".join(lines)
    (OUT / "report.md").write_text(text, encoding="utf-8")
    (OUT / "report.json").write_text(json.dumps(dict(report, decision=decision), indent=2))
    print(text)


if __name__ == "__main__":
    main()
