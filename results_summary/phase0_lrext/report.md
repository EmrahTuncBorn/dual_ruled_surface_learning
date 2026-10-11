Exploratory: wider lr grid. Does not change the Phase 0 decision.

| Rep | Phase 0 (lr, lam) | wide grid (lr, lam) | val chamfer | test rows from |
|---|---|---|---|---|
| A | 0.03, 0 | 0.1, 0 | 7.121e-04 | 88ea95e |
| B | 0.03, 0 | 0.3, 0 | 5.918e-04 | 88ea95e |
| C | 0.03, 0.001 | 0.3, 0.001 | 4.970e-04 | 88ea95e |

| Metric | vs | geo-mean ratio A/X | Wilcoxon p | Verdict |
|---|---|---|---|---|
| chamfer | B | 1.145 | 6.53e-26 | A worse |
| conv | B | 0.502 | 1.43e-34 | A better |
| seed_std | B | 1.398 | 8.76e-09 | A worse |
| chamfer | C | 1.326 | 3.78e-31 | A worse |
| conv | C | 3.064 | 1.71e-34 | A worse |
| seed_std | C | 0.737 | 2.05e-06 | A better |

| Rep | chamfer | conv (steps) | seed_std |
|---|---|---|---|
| A | 6.866e-04 | 334 | 7.684e-05 |
| B | 5.668e-04 | 650 | 3.456e-05 |
| C | 5.078e-04 | 117 | 8.858e-05 |