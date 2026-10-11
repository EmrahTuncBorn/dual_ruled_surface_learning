"""The three representations under comparison (v2 Sections 9 and 14.1).

Every representation uses 8 numbers per line (equal parameter count):
  A - dual             : a_raw(3), b(3), v_min, w    v_max = v_min + softplus(w), v measured from f
  B - base + direction : c(3), a_raw(3), v_min, w    v measured from c
  C - two endpoints    : q0(3), q1(3), unused, unused
  H - A with the hard developability layer (v3); not part of REPS

Common interface:
  init(a, p, v0, v1)        parameters from geometric lines (a unit, p a point on the line,
                            [v0, v1] the interval measured from p)
  segments(P, S, offset)    endpoints of the interpolated line segments, (B, L, 3) x 2
  lines(P)                  (a, a*) of the K lines, for evaluation
  smooth_vars(P)            variables whose second difference forms the smoothness loss
"""
import torch
import torch.nn.functional as F

from .geometry import (dot, dual_normalize, foot, moment, align_signs, lerp_lines,
                       developable_lines)


def inv_softplus(y):
    return y + torch.log(-torch.expm1(-y))


def _interval(P):
    vmin = P[..., 6]
    return vmin, vmin + F.softplus(P[..., 7])


def _flip_interval(vmin, vmax, s):
    neg = s < 0
    return torch.where(neg, -vmax, vmin), torch.where(neg, -vmin, vmax)


class DualRep:
    name = "A"

    @staticmethod
    def init(a, p, v0, v1):
        s = dot(p, a)
        return torch.cat([a, moment(p, a), (v0 + s)[..., None],
                          inv_softplus(v1 - v0)[..., None]], dim=-1)

    @classmethod
    def _aligned(cls, P):
        a, m = cls.lines(P)
        vmin, vmax = _interval(P)
        s = align_signs(a)
        vmin, vmax = _flip_interval(vmin, vmax, s)
        return a * s[..., None], m * s[..., None], vmin, vmax

    @classmethod
    def segments(cls, P, S=4, offset=None):
        a, m, vmin, vmax = cls._aligned(P)
        x = lerp_lines(torch.cat([a, m, vmin[..., None], vmax[..., None]], -1), S, offset)
        a, m = dual_normalize(x[..., 0:3], x[..., 3:6])
        f = foot(a, m)
        return f + x[..., 6:7] * a, f + x[..., 7:8] * a

    @staticmethod
    def lines(P):
        return dual_normalize(P[..., 0:3], P[..., 3:6])

    @classmethod
    def smooth_vars(cls, P):
        a, m, _, _ = cls._aligned(P)
        return torch.cat([a, m], -1)


class DevelopableDualRep(DualRep):
    """A with the sequential hard developability layer applied to its lines (v3 Section 3).

    Parameters and interpolation are those of A; with A's interpolation the lines
    between two coplanar lines stay in their pencil, so every strip is planar.
    """
    name = "H"
    eps = 1e-3

    @classmethod
    def lines(cls, P):
        a, m0 = dual_normalize(P[..., 0:3], P[..., 3:6])
        return a, developable_lines(a, m0, cls.eps)


class BaseDirRep:
    name = "B"

    @staticmethod
    def init(a, p, v0, v1):
        return torch.cat([p, a, v0[..., None], inv_softplus(v1 - v0)[..., None]], dim=-1)

    @staticmethod
    def _aligned(P):
        c = P[..., 0:3]
        a = F.normalize(P[..., 3:6], dim=-1, eps=1e-12)
        vmin, vmax = _interval(P)
        s = align_signs(a)
        vmin, vmax = _flip_interval(vmin, vmax, s)
        return c, a * s[..., None], vmin, vmax

    @classmethod
    def segments(cls, P, S=4, offset=None):
        c, a, vmin, vmax = cls._aligned(P)
        x = lerp_lines(torch.cat([c, a, vmin[..., None], vmax[..., None]], -1), S, offset)
        c, a = x[..., 0:3], F.normalize(x[..., 3:6], dim=-1, eps=1e-12)
        return c + x[..., 6:7] * a, c + x[..., 7:8] * a

    @staticmethod
    def lines(P):
        a = F.normalize(P[..., 3:6], dim=-1, eps=1e-12)
        return a, moment(P[..., 0:3], a)

    @classmethod
    def smooth_vars(cls, P):
        c, a, _, _ = cls._aligned(P)
        return torch.cat([c, a], -1)


class EndpointRep:
    name = "C"

    @staticmethod
    def init(a, p, v0, v1):
        q0 = p + v0[..., None] * a
        q1 = p + v1[..., None] * a
        return torch.cat([q0, q1, torch.zeros_like(q0[..., :2])], dim=-1)

    @staticmethod
    def segments(P, S=4, offset=None):
        x = lerp_lines(P[..., 0:6], S, offset)
        return x[..., 0:3], x[..., 3:6]

    @staticmethod
    def lines(P):
        q0, q1 = P[..., 0:3], P[..., 3:6]
        a = F.normalize(q1 - q0, dim=-1, eps=1e-12)
        return a, moment(q0, a)

    @staticmethod
    def smooth_vars(P):
        return P[..., 0:6]


REPS = {"A": DualRep, "B": BaseDirRep, "C": EndpointRep}
