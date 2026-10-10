"""Line geometry core (torch).

An oriented line is the dual unit vector A = a + eps a*, with
|a| = 1, <a, a*> = 0, a* = c x a  (c any point on the line).
All functions broadcast over leading dimensions (batch, K, ...).
"""
import torch

EPS = 1e-12


def dot(x, y):
    return (x * y).sum(-1)


def dual_normalize(a_raw, b):
    """A/|A| under the dual norm: real part to the sphere, dual part to its tangent plane.

    For A = a + eps b, |A| = |a| + eps <a,b>/|a|, hence
    A/|A| = a_hat + eps (b - <b,a_hat> a_hat) / |a|.
    The v2 constraint layer omitted the 1/|a| factor (PROGRESS.md, S1).
    """
    n = a_raw.norm(dim=-1, keepdim=True).clamp_min(EPS)
    a = a_raw / n
    m = (b - dot(b, a)[..., None] * a) / n
    return a, m


def foot(a, m):
    """Point of the line closest to the origin, f = a x a*."""
    return torch.cross(a, m, dim=-1)


def moment(c, a):
    return torch.cross(c, a, dim=-1)


def align_signs(a):
    """Signs s_k in {+1, -1} such that <s_k a_k, s_{k+1} a_{k+1}> >= 0.

    a: (..., K, 3) -> (..., K), with s_0 = 1. Signs are constants (no gradient).
    """
    with torch.no_grad():
        d = dot(a[..., :-1, :], a[..., 1:, :])
        step = torch.where(d < 0, -torch.ones_like(d), torch.ones_like(d))
        ones = torch.ones_like(d[..., :1])
        return torch.cumprod(torch.cat([ones, step], dim=-1), dim=-1)


def lerp_lines(x, S, offset=None):
    """Linear interpolation with S sub-steps between consecutive rows.

    x: (..., K, D) -> (..., (K-1)*S + 1, D). offset in [0, 1) shifts the sub-steps
    (the random jitter used during training); the last line is always kept.
    """
    K = x.shape[-2]
    lam = torch.arange(S, dtype=x.dtype, device=x.device) / S
    if offset is not None:
        lam = lam + offset / S
    x0, x1 = x[..., :-1, None, :], x[..., 1:, None, :]
    lam = lam[:, None]
    mid = (1 - lam) * x0 + lam * x1                       # (..., K-1, S, D)
    mid = mid.reshape(*x.shape[:-2], (K - 1) * S, x.shape[-1])
    return torch.cat([mid, x[..., -1:, :]], dim=-2)


def u_grid(n, dtype, device, jitter=None):
    u = (torch.arange(n, dtype=dtype, device=device) + 0.5) / n
    if jitter is not None:
        u = (u + (jitter - 0.5) / n).clamp(0, 1)
    return u


def segment_points(p0, p1, u):
    """p0, p1: (..., L, 3) endpoints; u: (U,) -> (..., L, U, 3)."""
    u = u[:, None]
    return (1 - u) * p0[..., None, :] + u * p1[..., None, :]


# ---------------------------------------------------------------------------
# Measures on pairs of consecutive lines
# ---------------------------------------------------------------------------

def pair_metrics(a, m):
    """(theta, d, |reciprocal product|, drall) for consecutive line pairs.

    a, m: (..., K, 3) unit directions and moments. The angle is unoriented.
    Reciprocal product <a1,m2> + <a2,m1> = -d sin(theta) (sign depends on orientation).
    """
    a1, a2, m1, m2 = a[..., :-1, :], a[..., 1:, :], m[..., :-1, :], m[..., 1:, :]
    recip = (dot(a1, m2) + dot(a2, m1)).abs()
    cr = torch.cross(a1, a2, dim=-1).norm(dim=-1)
    theta = torch.atan2(cr, dot(a1, a2).abs())
    # d: |recip| / sin(theta) for non-parallel lines; foot-point offset for parallel ones
    f1, f2 = foot(a1, m1), foot(a2, m2)
    diff = f2 - f1
    d_par = (diff - dot(diff, a1)[..., None] * a1).norm(dim=-1)
    d = torch.where(cr > 1e-6, recip / cr.clamp_min(1e-12), d_par)
    drall = d / theta.clamp_min(1e-12)
    return theta, d, recip, drall
