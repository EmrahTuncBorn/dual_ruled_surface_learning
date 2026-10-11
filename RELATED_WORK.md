# Related work

References collected in v2 Section 13, PROGRESS.md S7 and v3 Section 9.

Verification status:
- **verified (search)** — title, authors and venue confirmed by a web search on 2026-10-11.
- **verified (known)** — a standard reference whose details were not searched again in this pass.
- **partly verified** — the work exists, but a detail (title, authors) could not be confirmed.
- **unverified** — no matching work was found; do not cite until confirmed.

## Line geometry and ruled surfaces

| Reference | Status | Role here |
|---|---|---|
| H. Pottmann, J. Wallner. *Computational Line Geometry.* Springer, 2001. | verified (known) | Plücker coordinates, pencils of lines, reciprocal product |
| H. Chen, H. Pottmann. Approximation by ruled surfaces. *J. Comput. Appl. Math.* 102(1):143–156, 1999. | verified (search) | fitting a line sequence, then a smooth ruled surface; optimisation baseline |
| H. Pottmann, M. Hofer, B. Odehnal, J. Wallner. Line geometry for 3D shape understanding and reconstruction. *ECCV 2004*, LNCS 3021, 297–309. | verified (search) | line-space approximation for recognising developable and other surfaces |
| İ. Arslan Güven, S. Kaya Nurkan, M. K. Karacan. Ruled Weingarten surfaces related to dual spherical curves. *General Mathematics Notes* 24(2):10–17, 2014; arXiv:1307.2716. | verified (search) | mathematical background (Study map, curvature); no learning |
| Rational point-line motion design with dual quaternions, unifying ruled-surface design and five-axis tool paths. *Science China Technological Sciences*, 2011, doi:10.1007/s11431-011-4609-4. | partly verified | v2 cites it as "Kinematic generation of ruled surface based on rational motion of point-line"; the DOI and content match, the exact title and authors were not confirmed |

## Developable surfaces

| Reference | Status | Role here |
|---|---|---|
| Y. Liu, H. Pottmann, J. Wallner, Y.-L. Yang, W. Wang. Geometric modeling with conical meshes and developable surfaces. *ACM TOG* 25(3):681–689, 2006 (SIGGRAPH). | verified (search) | planar-quad strips as discrete developables; closest to the hard layer |
| C. Tang, P. Bo, J. Wallner, H. Pottmann. Interactive design of developable surfaces. *ACM TOG* 35(2), article 12, 2016. | verified (search) | developability as quadratic constraints in a solver |
| O. Stein, E. Grinspun, K. Crane. Developability of triangle meshes. *ACM TOG* 37(4), article 77, 2018. | verified (search) | discrete developability energy; metric context for the angle defect |
| P. Selvaraju. Developability approximation for neural implicits through rank minimization. arXiv:2308.03900, 2023. | verified (search) | soft developability for neural implicits; baseline after a positive Phase 1 |
| Y. Pan, Z. Xu, B. Wang, B. Deng. Piecewise ruled approximation for freeform mesh surfaces. *ACM TOG*, 2025; arXiv:2501.15258. | verified (search) | optimisation baseline for ruled approximation |
| "Piecewise developable modeling via implicit neural deformation and feature-guided cutting" (v2 Section 13). | unverified | no work with this title was found; a related work is *Symmetric piecewise developable approximations*, Computer Graphics Forum 43, 2024, doi:10.1111/cgf.15242 |

## Learning on lines and representations

| Reference | Status | Role here |
|---|---|---|
| L. Liu, H. Li, H. Yao, R. Zha. PlückerNet: learn to register 3D line reconstructions. *CVPR 2021*, 1842–1852. | verified (search) | lines in Plücker form as network input |
| V. Sitzmann, S. Rezchikov, W. T. Freeman, J. B. Tenenbaum, F. Durand. Light field networks. *NeurIPS 2021*. | verified (known) | learning on ray space parameterised by Plücker coordinates |
| G. Sharma, D. Liu, S. Maji, E. Kalogerakis, S. Chaudhuri, R. Měch. ParSeNet. *ECCV 2020*. | verified (known) | parametric patch decomposition; no ruled class |
| M. A. Uy et al. Point2Cyl. *CVPR 2022*. | verified (known) | extrusion cylinders from point clouds |
| Y. Zhou, C. Barnes, J. Lu, J. Yang, H. Li. On the continuity of rotation representations in neural networks. *CVPR 2019*. | verified (known) | context for the Phase 0 negative result on output coordinates |
| C. Deng et al. Vector Neurons. *ICCV 2021*. | verified (known) | built-in rotation equivariance (deliberately not used, v2 Section 5) |
| D. Kozlov, M. Bakulin, S. Pavlov, A. Zuev, M. Krylova, I. Kharchikov. Learning properties of holomorphic neural networks of dual variables. *ICASSP 2023*. | verified (search) | dual-number networks; no line geometry |

## Open question for the paper

Is there earlier work that enforces the intersection of consecutive lines as a closed-form projection
in Plücker coordinates (kinematics, architectural geometry, or learning)? Not yet searched.
