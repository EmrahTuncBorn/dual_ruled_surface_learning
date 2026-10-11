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
# Hard developability layer (v3 Section 3)
# ---------------------------------------------------------------------------

def project_coplanar(a_prev, m_prev, a, m0, eps=1e-3):
    """Moment closest to m0 that makes the line (a, m) coplanar with (a_prev, m_prev).

    The coplanarity condition <a_prev, m> + <a, m_prev> = 0 is linear in m. With
    n = a_prev - <a_prev, a> a (|n| = sin theta) the solution is m0 - r n / |n|^2, and
    |m - m0| equals the shortest distance between the raw line and the previous one.
    The denominator is clamped at eps^2, so pairs with sin theta < eps are corrected
    only partly and the correction goes continuously to zero for parallel lines.
    """
    n = a_prev - dot(a_prev, a)[..., None] * a
    r = dot(a_prev, m0) + dot(a, m_prev)
    return m0 - (r / dot(n, n).clamp_min(eps ** 2))[..., None] * n


def developable_lines(a, m0, eps=1e-3):
    """Sequential hard layer: line k is projected against the projected line k-1.

    a, m0: (..., K, 3) unit directions and moments with <a, m0> = 0. Directions are kept.
    """
    ms = [m0[..., 0, :]]
    for k in range(1, a.shape[-2]):
        ms.append(project_coplanar(a[..., k - 1, :], ms[-1], a[..., k, :], m0[..., k, :], eps))
    return torch.stack(ms, dim=-2)


def angle_defect_total(G):
    """Discrete total absolute Gaussian curvature of a grid surface (v3 Section 4.2).

    G: (..., L, U, 3). Each quad is split along the (i,j)-(i+1,j+1) diagonal; the result
    is the sum over interior vertices of |2 pi - sum of incident triangle angles|.
    """
    def angle(p, q, r):
        u, v = q - p, r - p
        return torch.atan2(torch.cross(u, v, dim=-1).norm(dim=-1), dot(u, v))

    A, B, C, D = G[..., :-1, :-1, :], G[..., 1:, :-1, :], G[..., :-1, 1:, :], G[..., 1:, 1:, :]
    total = torch.zeros(G.shape[:-1], dtype=G.dtype, device=G.device)
    total[..., :-1, :-1] += angle(A, B, D) + angle(A, D, C)     # triangles ABD and ADC
    total[..., 1:, :-1] += angle(B, D, A)
    total[..., 1:, 1:] += angle(D, A, B) + angle(D, C, A)
    total[..., :-1, 1:] += angle(C, A, D)
    defect = 2 * torch.pi - total[..., 1:-1, 1:-1]
    return defect.abs().sum((-1, -2))


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
