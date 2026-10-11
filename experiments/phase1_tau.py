"""Developability threshold tau of v3 Section 4.2.

tau = 1% of the median angle-defect total of true non-developable patches (general and
hypar, 10 each, validation seed 3000), on the evaluation grid ((K-1)*S+1 lines x U points).
The metric is rigid- and scale-invariant, so the raw generated surfaces are used.

  python experiments/phase1_tau.py
"""
import numpy as np
import torch

from ruled import data
from ruled.geometry import angle_defect_total

K, S, U = 32, 8, 64
SEED, N_PER_FAMILY = 3000, 10


def main():
    nt = (K - 1) * S + 1
    t, s = np.repeat(np.linspace(0, 1, nt), U), np.tile(np.linspace(0, 1, U), nt)
    rng = np.random.default_rng(SEED)
    vals = []
    for family in ("general", "hypar"):
        for _ in range(N_PER_FAMILY):
            while True:
                surf = data.build(family, rng)
                if data.acceptable(family, surf, data.grid_area(surf)):
                    break
            G = torch.tensor(data.evaluate(surf, t, s).reshape(nt, U, 3), dtype=torch.float64)
            vals.append(angle_defect_total(G).item())
            print(f"{family}: {vals[-1]:.4f}")
    med = float(np.median(vals))
    print(f"median {med:.4f}, tau = {0.01 * med:.5f}")


if __name__ == "__main__":
    main()
