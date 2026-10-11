"""Sanity tests of v3 Section 7.2 (hard developability layer and the angle-defect metric)."""
import numpy as np
import pytest
import torch

from ruled import data
from ruled.geometry import (dot, dual_normalize, moment, project_coplanar, developable_lines,
                            angle_defect_total)
from ruled.losses import developability_A, developability_C, surface_grid
from ruled.reps import DualRep, DevelopableDualRep, EndpointRep, ReversedDevelopableDualRep

torch.set_default_dtype(torch.float64)
T = lambda x: torch.as_tensor(np.ascontiguousarray(x), dtype=torch.float64)
EPS = DevelopableDualRep.eps


def random_lines(seed, n):
    g = torch.Generator().manual_seed(seed)
    return dual_normalize(torch.randn(n, 3, generator=g), torch.randn(n, 3, generator=g))


def shortest_distance(a1, m1, a2, m2):
    r = dot(a1, m2) + dot(a2, m1)
    return r.abs() / torch.cross(a1, a2, dim=-1).norm(dim=-1)


def recip(a, m):
    return dot(a[..., :-1, :], m[..., 1:, :]) + dot(a[..., 1:, :], m[..., :-1, :])


def family_lines(family, seed, K):
    surf = data.build(family, np.random.default_rng(seed))
    t = np.linspace(0, 1, K)
    a = T(surf[1](t))
    return a, moment(T(surf[0](t)), a)


def true_grid(surf, nt, ns):
    t, s = np.repeat(np.linspace(0, 1, nt), ns), np.tile(np.linspace(0, 1, ns), nt)
    return T(data.evaluate(surf, t, s).reshape(nt, ns, 3))


def total_abs_curvature(surf, nt=4000, ns=400):
    """Midpoint quadrature of |K| dA = det(a', c', a)^2 / |(c' + v a') x a|^3 dt dv."""
    c, a, lo, hi = surf
    t = np.repeat((np.arange(nt) + 0.5) / nt, ns)
    s = np.tile((np.arange(ns) + 0.5) / ns, nt)
    L, H = lo(t), hi(t)
    v = L + s * (H - L)
    dc, da, at = data.deriv(c, t), data.deriv(a, t), a(t)
    num = np.linalg.det(np.stack([da, dc, at], -2)) ** 2
    W = np.linalg.norm(np.cross(dc + v[:, None] * da, at), axis=-1)
    return (num / W ** 3 * (H - L)).mean()


# 1, 2
def test_projection_conditions_and_distance():
    (ai, mi), (a, m0) = random_lines(0, 1000), random_lines(1, 1000)
    m = project_coplanar(ai, mi, a, m0, EPS)
    keep = torch.cross(ai, a, dim=-1).norm(dim=-1) > EPS
    assert keep.sum() > 990
    assert dot(a, m).abs().max() < 1e-14
    assert (dot(ai, m) + dot(a, mi))[keep].abs().max() < 1e-13
    d0 = shortest_distance(ai, mi, a, m0)
    assert ((m - m0).norm(dim=-1) - d0)[keep].abs().max() < 1e-12


def test_sequential_layer_conditions():
    a, m0 = random_lines(2, 32)
    m = developable_lines(a, m0, EPS)
    assert dot(a, m).abs().max() < 1e-14
    assert recip(a, m).abs().max() < 1e-13
    assert torch.equal(m[0], m0[0])


# 3
@pytest.mark.parametrize("family", ["cone", "cylinder"])
def test_developable_lines_unchanged(family):
    for seed in range(5):
        a, m0 = family_lines(family, seed, 32)
        assert (developable_lines(a, m0, EPS) - m0).norm(dim=-1).max() < 1e-12


def test_tangent_correction_shrinks():
    # one pair is off by O(h^3), but the sequential layer accumulates it: O(h^2) overall
    for seed in range(5):
        ch = [(developable_lines(*family_lines("tangent", seed, K), EPS)
               - family_lines("tangent", seed, K)[1]).norm(dim=-1).max() for K in (32, 64, 128)]
        assert ch[0] > 1e-10 and ch[1] < ch[0] / 3 and ch[2] < ch[1] / 3


# 4
def test_sign_invariance():
    a, m0 = random_lines(3, 32)
    flip = torch.where(torch.rand(32, generator=torch.Generator().manual_seed(4)) < 0.5, -1.0, 1.0)
    m = developable_lines(a, m0, EPS)
    mf = developable_lines(a * flip[:, None], m0 * flip[:, None], EPS)
    assert torch.allclose(mf, m * flip[:, None], atol=1e-12)


# 5
def test_hard_layer_strips_are_planar():
    """Pencil property: every quad of the interpolated H surface is planar, for any lines."""
    g = torch.Generator().manual_seed(5)
    a = torch.nn.functional.normalize(torch.randn(4, 32, 3, generator=g), dim=-1)
    P = DualRep.init(a, torch.randn(4, 32, 3, generator=g), torch.full((4, 32), -0.6), torch.full((4, 32), 0.6))
    for rep in (DevelopableDualRep, ReversedDevelopableDualRep):
        G = surface_grid(rep, P)
        A, B, C, D = G[..., :-1, :-1, :], G[..., 1:, :-1, :], G[..., :-1, 1:, :], G[..., 1:, 1:, :]
        vol = dot(torch.cross(B - A, C - A, dim=-1), D - A).abs()
        rel = vol / ((B - A).norm(dim=-1) * (C - A).norm(dim=-1) * (D - A).norm(dim=-1))
        assert rel.max() < 1e-12, rep.name


def test_reversed_layer_keeps_last_line():
    """The reversed layer keeps the last line and differs from H on generic lines."""
    g = torch.Generator().manual_seed(14)
    a = torch.nn.functional.normalize(torch.randn(2, 16, 3, generator=g), dim=-1)
    P = DualRep.init(a, torch.randn(2, 16, 3, generator=g), torch.full((2, 16), -0.5), torch.full((2, 16), 0.5))
    _, m0 = DualRep.lines(P)
    _, mf = DevelopableDualRep.lines(P)
    _, mr = ReversedDevelopableDualRep.lines(P)
    assert torch.allclose(mr[:, -1], m0[:, -1]) and torch.allclose(mf[:, 0], m0[:, 0])
    assert (mr - mf).abs().max() > 1e-3


def test_hard_layer_surface_is_developable():
    """Perturbed cone lines meet near the apex, outside the interval: the angle defect vanishes.

    If consecutive lines meet inside the interval, the strip crosses itself and the surface
    is singular; the angle defect then is large (v3 Section 3.4).
    """
    rng = np.random.default_rng(11)
    w = T(rng.uniform(-1, 1, 3))
    a = T(data.spherical_bezier(rng)(np.linspace(0, 1, 32)))
    p = w + 1e-3 * torch.randn(4, 32, 3, generator=torch.Generator().manual_seed(12))   # << theta * 0.2
    P = DualRep.init(a.expand(4, 32, 3), p, torch.full((4, 32), 0.2), torch.ones(4, 32))
    assert angle_defect_total(surface_grid(DualRep, P)).min() > 1e-3
    assert angle_defect_total(surface_grid(DevelopableDualRep, P)).max() < 1e-9


# 6
@pytest.mark.parametrize("family", ["cone", "cylinder"])
def test_angle_defect_zero_on_developables(family):
    for seed in range(3):
        assert angle_defect_total(true_grid(data.build(family, np.random.default_rng(seed)), 249, 64)) < 1e-10


def test_angle_defect_tangent_converges_to_zero():
    for seed in range(3):
        surf = data.build("tangent", np.random.default_rng(seed))
        g = [angle_defect_total(true_grid(surf, n, n)) for n in (32, 64, 128)]
        assert g[1] < g[0] / 8 and g[2] < g[1] / 8


# 7
@pytest.mark.parametrize("family", ["hypar", "general"])
def test_angle_defect_converges_to_total_curvature(family):
    for seed in range(3):
        surf = data.build(family, np.random.default_rng(seed))
        ref = total_abs_curvature(surf)
        err = [abs(angle_defect_total(true_grid(surf, n, n)).item() - ref) / ref for n in (64, 128, 256)]
        assert err[1] < 0.7 * err[0] and err[2] < 0.7 * err[1] and err[2] < 0.02


def test_angle_defect_rigid_and_scale_invariant():
    surf = data.build("hypar", np.random.default_rng(0))
    G = true_grid(surf, 64, 64)
    R = T(data.random_rotation(np.random.default_rng(1)))
    assert torch.isclose(angle_defect_total(G), angle_defect_total(3.7 * G @ R.T + 0.5), atol=1e-10)


# 8
def pair_at_angle(sin_theta, seed):
    """A line and a second one whose direction is turned by asin(sin_theta), at an offset."""
    g = torch.Generator().manual_seed(seed)
    (ai, mi), = [random_lines(seed, 1)]
    w = torch.nn.functional.normalize(torch.cross(ai, torch.randn(1, 3, generator=g), dim=-1), dim=-1)
    th = torch.asin(torch.tensor(sin_theta))
    a = torch.cos(th) * ai + torch.sin(th) * w
    p = torch.cross(ai, mi, dim=-1) + 0.3 * torch.randn(1, 3, generator=g)
    return ai, mi, a, moment(p, a)


@pytest.mark.parametrize("k", [10.0, 0.5, 0.1, 0.0])
def test_gradient_near_parallel(k):
    ai, mi, a, m0 = pair_at_angle(k * EPS, int(10 * k))
    inputs = [x.clone().requires_grad_(True) for x in (ai, mi, a, m0)]
    assert torch.autograd.gradcheck(lambda *x: project_coplanar(*x, EPS), inputs)
    out = project_coplanar(*inputs, EPS).sum()
    grads = torch.autograd.grad(out, inputs)
    assert all(torch.isfinite(g).all() for g in grads)


def test_gradient_sequential_layer():
    a, m0 = random_lines(6, 8)
    a, m0 = a.requires_grad_(True), m0.requires_grad_(True)
    assert torch.autograd.gradcheck(lambda x, y: developable_lines(x, y, EPS), (a, m0))


# penalties
def test_penalty_C_equals_reciprocal_times_lengths():
    g = torch.Generator().manual_seed(7)
    q0, q1 = torch.randn(16, 3, generator=g), torch.randn(16, 3, generator=g)
    P = torch.cat([q0, q1, torch.zeros(16, 2)], -1)
    a, m = EndpointRep.lines(P)
    L = (q1 - q0).norm(dim=-1)
    expect = (recip(a, m) * L[:-1] * L[1:]).square().sum()
    assert torch.isclose(developability_C(P), expect, rtol=1e-12)
    assert torch.isclose(developability_A(EndpointRep, P), recip(a, m).square().sum(), rtol=1e-12)
