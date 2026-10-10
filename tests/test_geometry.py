"""v2 Bölüm 14.7 sağlama testleri (+ S1). Numaralar v2'deki sırayı izler."""
import numpy as np
import pytest
import torch

from ruled import data
from ruled.geometry import dual_normalize, foot, moment, align_signs, pair_metrics, dot
from ruled.losses import chamfer, surface_points
from ruled.reps import REPS

torch.set_default_dtype(torch.float64)
T = lambda x: torch.as_tensor(np.ascontiguousarray(x), dtype=torch.float64)


def random_lines(rng, K):
    a = data.random_unit(rng, K)
    p = rng.uniform(-1, 1, (K, 3))
    return a, p


def surface_derivs(family, seed, n=200):
    surf = data.build(family, np.random.default_rng(seed))
    c, a = surf[0], surf[1]
    t = np.linspace(0.05, 0.95, n)
    ms = lambda t: np.cross(c(t), a(t))
    return dict(c=c(t), a=a(t), dc=data.deriv(c, t), da=data.deriv(a, t),
                dm=data.deriv(ms, t), m=ms(t), t=t, c_fn=c, a_fn=a)


# 1
def test_foot_point():
    a, p = random_lines(np.random.default_rng(0), 50)
    a, p = T(a), T(p)
    m = moment(p, a)
    f = foot(a, m)
    assert torch.allclose(torch.cross(f - p, a, dim=-1), torch.zeros_like(f), atol=1e-12)
    assert torch.allclose(dot(f, a), torch.zeros(50), atol=1e-12)
    assert torch.allclose(f.norm(dim=-1), m.norm(dim=-1), atol=1e-12)


# 2
def test_drall_dual_equals_classical():
    g = surface_derivs("general", 1)
    na2 = (g["da"] ** 2).sum(-1)
    dual = (g["da"] * g["dm"]).sum(-1) / na2
    classical = np.linalg.det(np.stack([g["dc"], g["a"], g["da"]], -2)) / na2
    assert np.allclose(dual, classical, atol=1e-6)


# 3
def test_striction_independent_of_base_curve():
    g = surface_derivs("general", 2)
    na2 = (g["da"] ** 2).sum(-1)
    s_c = g["c"] - ((g["dc"] * g["da"]).sum(-1) / na2)[:, None] * g["a"]
    f_fn = lambda t: np.cross(g["a_fn"](t), np.cross(g["c_fn"](t), g["a_fn"](t)))
    f, df = f_fn(g["t"]), data.deriv(f_fn, g["t"])
    s_f = f - ((df * g["da"]).sum(-1) / na2)[:, None] * g["a"]
    assert np.allclose(s_c, s_f, atol=1e-6)


def family_lines(family, seed, K):
    surf = data.build(family, np.random.default_rng(seed))
    t = np.linspace(0, 1, K)
    a = T(surf[1](t))
    return a, moment(T(surf[0](t)), a)


# 4
@pytest.mark.parametrize("family", ["cone", "cylinder"])
def test_developable_residual_zero(family):
    for seed in range(5):
        _, _, recip, _ = pair_metrics(*family_lines(family, seed, 32))
        assert recip.max() < 1e-12


# 5
def test_tangent_developable_residual_shrinks():
    for seed in range(5):
        r32 = pair_metrics(*family_lines("tangent", seed, 32))[2].mean()
        r64 = pair_metrics(*family_lines("tangent", seed, 64))[2].mean()
        assert r32 > 1e-10 and r64 < r32 / 4


# 6, 7
def test_discrete_identity_and_dsin():
    rng = np.random.default_rng(3)
    a, p = random_lines(rng, 40)
    a, p = T(a), T(p)
    m = moment(p, a)
    da, dm = a[1:] - a[:-1], m[1:] - m[:-1]
    recip = dot(a[:-1], m[1:]) + dot(a[1:], m[:-1])
    assert torch.allclose(dot(da, dm), -recip, atol=1e-12)
    # bağımsız d sinθ: d = |⟨p2−p1, a1×a2⟩| / ‖a1×a2‖
    cr = torch.cross(a[:-1], a[1:], dim=-1)
    d = dot(p[1:] - p[:-1], cr).abs() / cr.norm(dim=-1)
    assert torch.allclose(recip.abs(), d * cr.norm(dim=-1), atol=1e-12)
    theta, d2, _, _ = pair_metrics(a, m)
    assert torch.allclose(d2, d, atol=1e-9)


# 9
def test_constraint_layer_conditions():
    g = torch.Generator().manual_seed(0)
    a, m = dual_normalize(torch.randn(1000, 3, generator=g), torch.randn(1000, 3, generator=g))
    assert (dot(a, a) - 1).abs().max() < 1e-14
    assert dot(a, m).abs().max() < 1e-14


# S1: dual normalizasyon homojendir ve konide ara doğrular tepeden geçer
def test_dual_normalize_homogeneous():
    a, p = random_lines(np.random.default_rng(4), 20)
    a, p = T(a), T(p)
    m = moment(p, a)
    lam = T(np.random.default_rng(5).uniform(0.1, 5, 20))[:, None]
    a2, m2 = dual_normalize(lam * a, lam * m)
    assert torch.allclose(a2, a, atol=1e-12) and torch.allclose(m2, m, atol=1e-12)


def test_cone_interpolated_lines_pass_through_apex():
    rng = np.random.default_rng(6)
    w = T(rng.uniform(-1, 1, 3))
    a = T(data.random_unit(rng, 8))           # büyük açılar: hata belirgin olsun
    P = REPS["A"].init(a, w.expand(8, 3), torch.full((8,), 0.2), torch.ones(8))
    p0, p1 = REPS["A"].segments(P, S=4)
    u = p1 - p0
    dist = torch.cross(w - p0, u, dim=-1).norm(dim=-1) / u.norm(dim=-1)
    assert dist.max() < 1e-12


# 10
def test_representations_round_trip():
    rng = np.random.default_rng(7)
    a, p = random_lines(rng, 32)
    a, p = T(a), T(p)
    v0, v1 = T(rng.uniform(-1, -0.2, 32)), T(rng.uniform(0.2, 1, 32))
    ref0, ref1 = p + v0[:, None] * a, p + v1[:, None] * a
    for rep in REPS.values():
        P = rep.init(a, p, v0, v1)
        q0, q1 = rep.segments(P[None], S=1)
        # A ve B işaret hizalaması uçları değiştirebilir; parça kümesi aynı olmalı
        same = torch.allclose(q0[0], ref0, atol=1e-10) and torch.allclose(q1[0], ref1, atol=1e-10)
        swapped = (torch.minimum((q0[0] - ref0).norm(dim=-1), (q0[0] - ref1).norm(dim=-1)).max() < 1e-10
                   and torch.minimum((q1[0] - ref1).norm(dim=-1), (q1[0] - ref0).norm(dim=-1)).max() < 1e-10)
        assert same or swapped, rep.name
        la, lm = rep.lines(P)
        s = torch.sign(dot(la, a))[:, None]
        assert torch.allclose(la * s, a, atol=1e-10) and torch.allclose(lm * s, moment(p, a), atol=1e-10)


# 11
@pytest.mark.parametrize("name", ["A", "B"])
def test_sign_alignment_preserves_surface(name):
    rng = np.random.default_rng(8)
    t = np.linspace(0, 1, 32)
    surf = data.build("general", rng)
    a, p = T(surf[1](t)), T(surf[0](t))
    v0, v1 = torch.full((32,), -0.5), torch.full((32,), 0.7)
    rep = REPS[name]
    P = rep.init(a, p, v0, v1)
    flip = T(np.where(rng.uniform(size=32) < 0.5, -1.0, 1.0))
    Pf = rep.init(a * flip[:, None], p, torch.where(flip < 0, -v1, v0), torch.where(flip < 0, -v0, v1))
    X, Xf = surface_points(rep, P[None]), surface_points(rep, Pf[None])
    assert chamfer(X, Xf).item() < 1e-14


# 12
def test_chamfer_self_zero():
    x = torch.randn(1, 500, 3)
    assert chamfer(x, x).item() < 1e-14   # cdist matris çarpımı yuvarlaması


# 13
@pytest.mark.parametrize("family", data.FAMILIES)
def test_area_weighted_sampler(family):
    rng = np.random.default_rng(9)
    surf = data.build(family, rng)
    dA = data.grid_area(surf)
    _, ts = data.sample(surf, 20000, rng, 1.05 * dA.max(), return_params=True)
    # yoğun ızgaradan t < 0.5 bölgesinin alan payı
    nt, ns = 401, 64
    tt, ss = np.meshgrid(np.linspace(0, 1, nt), np.linspace(0, 1, ns), indexing="ij")
    X = data.evaluate(surf, tt.ravel(), ss.ravel()).reshape(nt, ns, 3)
    q = 0.5 * (np.linalg.norm(np.cross(X[1:, :-1] - X[:-1, :-1], X[:-1, 1:] - X[:-1, :-1]), axis=-1)
               + np.linalg.norm(np.cross(X[1:, :-1] - X[1:, 1:], X[:-1, 1:] - X[1:, 1:]), axis=-1))
    frac_mesh = q[: (nt - 1) // 2].sum() / q.sum()
    frac_smp = (ts[:, 0] < 0.5).mean()
    assert abs(frac_mesh - frac_smp) < 4 * np.sqrt(0.25 / 20000) + 2e-3


def test_make_patch_normalized():
    p = data.make_patch("general", np.random.default_rng(10))
    assert p["points"].shape == (1024, 3) and p["clean_eval"].shape == (4096, 3)
    assert np.allclose(p["points"].mean(0), 0, atol=1e-12)
    assert np.isclose(np.linalg.norm(p["points"], axis=-1).max(), 1.0)
