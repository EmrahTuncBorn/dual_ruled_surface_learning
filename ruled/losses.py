"""Kayıplar ve ölçütler (v2 Bölüm 8 ve 14.5)."""
import os
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import torch
from scipy.spatial import cKDTree

from .geometry import segment_points, u_grid

_POOL = ThreadPoolExecutor(os.cpu_count() or 4)


@torch.no_grad()
def nearest(x, y):
    """Her iki yönde en yakın komşu indisleri (KD-ağacı, yama başına bir iş parçacığı)."""
    X, Y = x.detach().cpu().numpy(), y.detach().cpu().numpy()

    def one(b):
        return cKDTree(Y[b]).query(X[b])[1], cKDTree(X[b]).query(Y[b])[1]

    ix, iy = zip(*_POOL.map(one, range(len(X))))
    as_t = lambda i: torch.from_numpy(np.stack(i).astype(np.int64)).to(x.device)
    return as_t(ix), as_t(iy)


def surface_points(rep, P, S=4, U=16, jitter=False):
    """Yüzeyden noktalar: (K-1)*S+1 doğru × U nokta. jitter: ara adım ve u kaydırılır."""
    off = torch.rand((), dtype=P.dtype) if jitter else None
    uj = torch.rand((), dtype=P.dtype) if jitter else None
    p0, p1 = rep.segments(P, S, off)
    X = segment_points(p0, p1, u_grid(U, P.dtype, P.device, uj))
    return X.reshape(*X.shape[:-3], -1, 3)


def chamfer(x, y):
    """İki yönlü ortalama kare en yakın uzaklık; x: (B,N,3), y: (B,M,3) -> (B,).

    En yakın komşular gradyansız bulunur; kayıp yalnız eşleşen çiftlerden yeniden
    hesaplanır. min'in gradyanı zaten yalnız argmin çiftinden geçtiği için türev
    tam matris üzerinden alınanla aynıdır, ama geri yayılım O(N+M) olur.
    """
    ix, iy = nearest(x, y)                                 # (B,N), (B,M)
    gather = lambda z, i: torch.gather(z, 1, i[..., None].expand(-1, -1, 3))
    return ((x - gather(y, ix)).square().sum(-1).mean(-1)
            + (y - gather(x, iy)).square().sum(-1).mean(-1))


def smoothness(rep, P):
    v = rep.smooth_vars(P)
    d2 = v[..., 2:, :] - 2 * v[..., 1:-1, :] + v[..., :-2, :]
    return d2.square().sum((-1, -2))


@torch.no_grad()
def sample_area_weighted(rep, P, n=4096, S=8, U=64, generator=None):
    """Tahmin edilen yüzeyden alan ağırlıklı n nokta (ince ızgaranın dörtgenleri üzerinden)."""
    p0, p1 = rep.segments(P, S)
    G = segment_points(p0, p1, torch.linspace(0, 1, U, dtype=P.dtype))   # (B, L, U, 3)
    A, Bq, Cq, Dq = G[:, :-1, :-1], G[:, 1:, :-1], G[:, :-1, 1:], G[:, 1:, 1:]
    area = 0.5 * (torch.cross(Bq - A, Cq - A, dim=-1).norm(dim=-1)
                  + torch.cross(Bq - Dq, Cq - Dq, dim=-1).norm(dim=-1))
    area = area.reshape(area.shape[0], -1) + 1e-12
    idx = torch.multinomial(area, n, replacement=True, generator=generator)
    st = torch.rand(area.shape[0], n, 2, dtype=P.dtype, generator=generator)
    s, t = st[..., :1], st[..., 1:]
    take = lambda Q: torch.gather(Q.reshape(Q.shape[0], -1, 3), 1, idx[..., None].expand(-1, -1, 3))
    return ((1 - s) * (1 - t) * take(A) + s * (1 - t) * take(Bq)
            + (1 - s) * t * take(Cq) + s * t * take(Dq))
