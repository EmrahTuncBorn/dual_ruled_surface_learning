"""Synthetic ruled-surface patches (v2 Sections 4 and 14.3), numpy.

A patch is X(t, s) = c(t) + v a(t),  v = v_min(t) + s (v_max(t) - v_min(t)),  t, s in [0, 1].
Area element in (t, s): (v_max - v_min) |(c' + v a') x a|.
"""
import numpy as np

FAMILIES = ("general", "cylinder", "cone", "tangent", "hypar")
DEVELOPABLE = ("cylinder", "cone", "tangent")
FD_H = 1e-4


def bezier(ctrl, t):
    """Cubic Bezier; ctrl: (4, 3), t: (N,) -> (N, 3)."""
    t = t[:, None]
    b = [(1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t ** 2 * (1 - t), t ** 3]
    return sum(bi * ci for bi, ci in zip(b, ctrl))


def unit(x):
    return x / np.linalg.norm(x, axis=-1, keepdims=True)


def random_unit(rng, n=None):
    return unit(rng.normal(size=(3,) if n is None else (n, 3)))


def cap_vectors(rng, axis, half_angle, n):
    """n unit vectors uniform on the spherical cap of the given half-angle around axis."""
    z = rng.uniform(np.cos(half_angle), 1.0, n)
    phi = rng.uniform(0, 2 * np.pi, n)
    r = np.sqrt(1 - z ** 2)
    local = np.stack([r * np.cos(phi), r * np.sin(phi), z], -1)
    e1 = unit(np.cross(axis, random_unit(rng)))
    e2 = np.cross(axis, e1)
    return local @ np.stack([e1, e2, axis])


def random_rotation(rng):
    q, r = np.linalg.qr(rng.normal(size=(3, 3)))
    q = q * np.sign(np.diag(r))
    return q if np.linalg.det(q) > 0 else -q


def linear_interval(rng):
    lo = rng.uniform(-1, -0.3, 2)
    hi = rng.uniform(0.3, 1, 2)
    return (lambda t: lo[0] + (lo[1] - lo[0]) * t), (lambda t: hi[0] + (hi[1] - hi[0]) * t)


def spherical_bezier(rng):
    ctrl = cap_vectors(rng, random_unit(rng), np.radians(60), 4)
    return lambda t: unit(bezier(ctrl, t))


def build(family, rng):
    """(c, a, v_min, v_max) functions for the given family."""
    if family == "general":
        cc = rng.uniform(-1, 1, (4, 3))
        c = lambda t: bezier(cc, t)
        a = spherical_bezier(rng)
        vmin, vmax = linear_interval(rng)
    elif family == "cylinder":
        a0 = random_unit(rng)
        cc = rng.uniform(-1, 1, (4, 3))
        cc = cc - (cc @ a0)[:, None] * a0
        c = lambda t: bezier(cc, t)
        a = lambda t: np.broadcast_to(a0, (len(t), 3)).copy()
        vmin, vmax = linear_interval(rng)
    elif family == "cone":
        w = rng.uniform(-1, 1, 3)
        c = lambda t: np.broadcast_to(w, (len(t), 3)).copy()
        a = spherical_bezier(rng)
        vmin, vmax = (lambda t: 0.2 + 0 * t), (lambda t: 1.0 + 0 * t)
    elif family == "tangent":
        cc = rng.uniform(-1, 1, (4, 3))
        c = lambda t: bezier(cc, t)
        a = lambda t: unit(bezier(cc, t + FD_H) - bezier(cc, t - FD_H))
        vmin, vmax = (lambda t: 0.2 + 0 * t), (lambda t: 1.0 + 0 * t)
    elif family == "hypar":
        P0, P1, Q0, Q1 = rng.uniform(-1, 1, (4, 3))
        c = lambda t: P0 + (P1 - P0) * t[:, None]
        d = lambda t: (Q0 - P0) + ((Q1 - Q0) - (P1 - P0)) * t[:, None]
        a = lambda t: unit(d(t))
        vmin, vmax = (lambda t: 0 * t), (lambda t: np.linalg.norm(d(t), axis=-1))
    else:
        raise ValueError(family)
    return c, a, vmin, vmax


def deriv(fn, t):
    return (fn(t + FD_H) - fn(t - FD_H)) / (2 * FD_H)


def area_element(surf, t, s):
    c, a, vmin, vmax = surf
    lo, hi = vmin(t), vmax(t)
    v = lo + s * (hi - lo)
    Xt = deriv(c, t) + v[:, None] * deriv(a, t)
    return (hi - lo) * np.linalg.norm(np.cross(Xt, a(t)), axis=-1)


def evaluate(surf, t, s):
    c, a, vmin, vmax = surf
    lo, hi = vmin(t), vmax(t)
    return c(t) + (lo + s * (hi - lo))[:, None] * a(t)


def sample(surf, n, rng, dmax, return_params=False):
    """n area-weighted samples by rejection (v2 14.3)."""
    ts = []
    while sum(len(x) for x in ts) < n:
        t, s = rng.uniform(0, 1, 4 * n), rng.uniform(0, 1, 4 * n)
        keep = rng.uniform(0, 1, 4 * n) < area_element(surf, t, s) / dmax
        ts.append(np.stack([t[keep], s[keep]], -1))
    ts = np.concatenate(ts)[:n]
    X = evaluate(surf, ts[:, 0], ts[:, 1])
    return (X, ts) if return_params else X


def grid_area(surf, nt=256, ns=32):
    t = np.repeat(np.linspace(0, 1, nt), ns)
    s = np.tile(np.linspace(0, 1, ns), nt)
    return area_element(surf, t, s)


def acceptable(family, surf, dA):
    if dA.min() < 0.02 * dA.mean():
        return False
    t = np.linspace(0, 1, 256)
    P = evaluate(surf, np.repeat(t, 16), np.tile(np.linspace(0, 1, 16), 256))
    sv = np.linalg.svd(P - P.mean(0), compute_uv=False)
    if sv[0] / max(sv[1], 1e-12) > 10:
        return False
    if family == "tangent":
        c = surf[0]
        d1, d2 = deriv(c, t), (c(t + FD_H) - 2 * c(t) + c(t - FD_H)) / FD_H ** 2
        kappa = np.linalg.norm(np.cross(d1, d2), axis=-1) / np.linalg.norm(d1, axis=-1) ** 3
        if kappa.min() < 0.05:
            return False
    return True


def make_patch(family, rng, noise=0.01, n=1024, n_eval=4096, K=32):
    """Normalised noisy cloud, clean evaluation samples and ground-truth lines."""
    while True:
        surf = build(family, rng)
        dA = grid_area(surf)
        if acceptable(family, surf, dA):
            break
    dmax = 1.05 * dA.max()
    clean = sample(surf, n, rng, dmax)
    ev = sample(surf, n_eval, rng, dmax)
    tk = np.linspace(0, 1, K)
    true_a, true_p = surf[1](tk), surf[0](tk)

    R = random_rotation(rng)
    clean, ev, true_a, true_p = clean @ R.T, ev @ R.T, true_a @ R.T, true_p @ R.T
    diag = np.linalg.norm(clean.max(0) - clean.min(0))
    noisy = clean + rng.normal(scale=noise * diag, size=clean.shape)

    center = noisy.mean(0)
    scale = np.linalg.norm(noisy - center, axis=-1).max()
    T = lambda x: (x - center) / scale
    return dict(family=family, points=T(noisy), clean_eval=T(ev),
                true_a=true_a, true_p=T(true_p))


def make_set(n_per_family, seed, noise=0.01):
    rng = np.random.default_rng(seed)
    return [make_patch(f, rng, noise) for f in FAMILIES for _ in range(n_per_family)]
