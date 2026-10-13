Commit: `ca3da264ab25c3a0855b8ef186ad818c213a3c5a`
tau = 0.00756

Selected settings (validation):

| Arm | lr | lambda_s | lambda_d | reached tau |
|---|---|---|---|---|
| A0 | 0.3 | 0.01 | 0 | None |
| PA | 0.03 | 0.1 | 1000 | True |
| PC | 0.03 | 1 | 1000 | False |
| H | 0.1 | 0.01 | 0 | None |

## Init: smooth (primary, decision)

Prerequisite: median G of H = 1.134 <= tau: False

| Metric | H vs | geo-mean ratio H/X | Wilcoxon p | Verdict |
|---|---|---|---|---|
| chamfer | PA | 0.726 | 1.33e-13 | H better |
| G | PA | 4313.194 | 1.97e-21 | H worse |
| chamfer | PC | 0.368 | 1.85e-20 | H better |
| G | PC | 1517.683 | 3.60e-21 | H worse |
| chamfer | A0 | 2.083 | 1.97e-21 | H worse |
| G | A0 | 4.078 | 5.64e-21 | H worse |

| Arm | chamfer | G mean | G median | flip | inside | seed_std |
|---|---|---|---|---|---|---|
| A0 | 1.323e-03 | 3.186e-01 | 2.609e-01 | 0.009 | 0.101 | 4.50e-04 |
| PA | 4.806e-03 | 1.411e-02 | 1.186e-04 | 0.001 | 0.007 | 4.47e-04 |
| PC | 9.190e-03 | 9.166e-02 | 2.154e-04 | 0.000 | 0.022 | 1.13e-03 |
| H | 2.763e-03 | 1.231e+00 | 1.134e+00 | 0.019 | 0.151 | 8.35e-04 |
| Hrev | 2.626e-03 | 1.245e+00 | 1.103e+00 | 0.019 | 0.154 | 8.02e-04 |

Per family (mean Chamfer x1e-4 / median G):

| Family | A0 | PA | PC | H |
|---|---|---|---|---|
| cylinder | 18.63 / 2.75e-01 | 55.55 / 8.27e-05 | 97.52 / 4.96e-05 | 33.81 / 1.35e+00 |
| cone | 13.87 / 2.26e-01 | 63.19 / 8.38e-05 | 117.13 / 1.51e-04 | 33.48 / 1.14e+00 |
| tangent | 7.19 / 2.61e-01 | 25.43 / 2.38e-04 | 61.05 / 9.17e-02 | 15.61 / 9.04e-01 |

**Decision rule on this init: weak (prerequisite failed)**

## Init: phase0 (secondary, reported only)

Prerequisite: median G of H = 0.1531 <= tau: False

| Metric | H vs | geo-mean ratio H/X | Wilcoxon p | Verdict |
|---|---|---|---|---|
| chamfer | PA | 0.374 | 2.02e-21 | H better |
| G | PA | 120.008 | 2.29e-21 | H worse |
| chamfer | PC | 0.143 | 1.97e-21 | H better |
| G | PC | 162.213 | 5.54e-20 | H worse |
| chamfer | A0 | 1.243 | 8.51e-15 | H worse |
| G | A0 | 0.590 | 6.08e-02 | no difference |

| Arm | chamfer | G mean | G median | flip | inside | seed_std |
|---|---|---|---|---|---|---|
| A0 | 1.874e-03 | 1.940e-01 | 1.457e-01 | 0.010 | 0.079 | 6.06e-04 |
| PA | 6.268e-03 | 3.645e-03 | 5.406e-04 | 0.001 | 0.003 | 6.40e-04 |
| PC | 1.576e-02 | 1.236e-02 | 2.541e-04 | 0.000 | 0.005 | 1.53e-03 |
| H | 2.764e-03 | 2.600e-01 | 1.531e-01 | 0.011 | 0.079 | 4.36e-04 |

Per family (mean Chamfer x1e-4 / median G):

| Family | A0 | PA | PC | H |
|---|---|---|---|---|
| cylinder | 23.37 / 1.69e-01 | 72.74 / 4.05e-04 | 141.98 / 9.96e-05 | 34.56 / 1.88e-01 |
| cone | 23.54 / 1.47e-01 | 81.42 / 5.52e-04 | 199.14 / 2.13e-04 | 36.01 / 1.53e-01 |
| tangent | 9.32 / 1.14e-01 | 33.89 / 6.84e-04 | 131.69 / 6.46e-03 | 12.36 / 1.16e-01 |

**Decision rule on this init: weak (prerequisite failed)**

Reversed layer (Hrev vs H, Chamfer): ratio 0.982, p 5.13e-01, no difference

**Decision (primary init): weak (prerequisite failed)**