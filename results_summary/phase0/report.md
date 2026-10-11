Commit: `e96bef16b65d3ddf9771cc26b39c17e2dc86c406`

| Metric | vs | geo-mean ratio A/X | Wilcoxon p | Verdict |
|---|---|---|---|---|
| chamfer | B | 1.104 | 2.55e-21 | no difference |
| conv | B | 0.982 | 7.51e-01 | no difference |
| seed_std | B | 1.274 | 5.84e-05 | A worse |
| chamfer | C | 1.342 | 2.05e-13 | A worse |
| conv | C | 2.213 | 1.61e-32 | A worse |
| seed_std | C | 0.757 | 1.01e-05 | A better |

Final Chamfer per family (mean, x1e-4):

| Family | A | B | C |
|---|---|---|---|
| cone | 10.432 | 8.449 | 13.355 |
| cylinder | 13.314 | 11.361 | 14.550 |
| general | 6.957 | 6.502 | 4.840 |
| hypar | 5.199 | 4.652 | 3.774 |
| tangent | 5.501 | 4.988 | 4.863 |

Mean primary metrics:

| Rep | chamfer | conv (steps) | seed_std |
|---|---|---|---|
| A | 8.280e-04 | 254 | 1.034e-04 |
| B | 7.191e-04 | 256 | 6.974e-05 |
| C | 8.277e-04 | 127 | 2.128e-04 |

Secondary metrics on developable families (mean):

| Family | Rep | d sin(theta) | drall d/theta |
|---|---|---|---|
| cylinder | A | 4.69e-02 | 5.98e-01 |
| cylinder | B | 4.36e-02 | 5.14e-01 |
| cylinder | C | 5.11e-03 | 1.17e+00 |
| cone | A | 3.68e-02 | 5.16e-01 |
| cone | B | 3.13e-02 | 5.11e-01 |
| cone | C | 4.24e-03 | 7.60e-01 |
| tangent | A | 1.94e-02 | 4.08e-01 |
| tangent | B | 1.88e-02 | 3.57e-01 |
| tangent | C | 2.36e-03 | 4.63e-01 |

**Decision: representation axis WEAK**