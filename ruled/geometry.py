"""Doğru geometrisi çekirdeği (torch).

Bir yönlü doğru, dual birim vektör A = a + ε a* ile verilir:
‖a‖ = 1, ⟨a, a*⟩ = 0, a* = c × a  (c doğru üzerinde herhangi bir nokta).
Bütün fonksiyonlar baştaki boyutlarda (batch, K, ...) yayınlanır.
"""
import torch

EPS = 1e-12


def dot(x, y):
    return (x * y).sum(-1)


def dual_normalize(a_raw, b):
    """A/‖A‖ (dual norm). Gerçek kısım küreye, dual kısım teğet düzleme gider.

    A = a + εb için ‖A‖ = ‖a‖ + ε⟨a,b⟩/‖a‖, dolayısıyla
    A/‖A‖ = â + ε (b − ⟨b,â⟩â)/‖a‖.
    v2'deki katman 1/‖a‖ çarpanını atlıyordu (progress.md, S1).
    """
    n = a_raw.norm(dim=-1, keepdim=True).clamp_min(EPS)
    a = a_raw / n
    m = (b - dot(b, a)[..., None] * a) / n
    return a, m


def foot(a, m):
    """Doğrunun orijine en yakın noktası f = a × a*."""
    return torch.cross(a, m, dim=-1)


def moment(c, a):
    return torch.cross(c, a, dim=-1)


def align_signs(a):
    """Ardışık doğrular arasında ⟨a_k, a_{k+1}⟩ ≥ 0 olacak işaret dizisi s_k ∈ {±1}.

    a: (..., K, 3). Dönen: (..., K). s_0 = 1; işaretler sabit (gradyan taşımaz).
    """
    with torch.no_grad():
        d = dot(a[..., :-1, :], a[..., 1:, :])
        step = torch.where(d < 0, -torch.ones_like(d), torch.ones_like(d))
        ones = torch.ones_like(d[..., :1])
        return torch.cumprod(torch.cat([ones, step], dim=-1), dim=-1)


def lerp_lines(x, S, offset=None):
    """Ardışık satırlar arasında S ara adımla doğrusal ara değer.

    x: (..., K, D) -> (..., (K-1)*S + 1, D). offset ∈ [0,1) ara adımları kaydırır
    (eğitimdeki rastgele kaydırma); son doğru her zaman dahildir.
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
    """p0, p1: (..., L, 3) uç noktalar; u: (U,) -> (..., L, U, 3)."""
    u = u[:, None]
    return (1 - u) * p0[..., None, :] + u * p1[..., None, :]


# ---------------------------------------------------------------------------
# Doğru çifti ölçüleri
# ---------------------------------------------------------------------------

def pair_metrics(a, m):
    """Ardışık doğru çiftleri için (θ, d, |karşılıklı moment|, drall).

    a, m: (..., K, 3) birim yön ve moment. Yönsüz açı kullanılır.
    karşılıklı moment ⟨a1,m2⟩ + ⟨a2,m1⟩ = −d sinθ (işaret yönlendirmeye bağlı).
    """
    a1, a2, m1, m2 = a[..., :-1, :], a[..., 1:, :], m[..., :-1, :], m[..., 1:, :]
    recip = (dot(a1, m2) + dot(a2, m1)).abs()
    cr = torch.cross(a1, a2, dim=-1).norm(dim=-1)
    theta = torch.atan2(cr, dot(a1, a2).abs())
    # d: kesişmeyen doğrular için |recip| / sinθ; paralelde orijine dik uzaklık farkı
    f1, f2 = foot(a1, m1), foot(a2, m2)
    diff = f2 - f1
    d_par = (diff - dot(diff, a1)[..., None] * a1).norm(dim=-1)
    d = torch.where(cr > 1e-6, recip / cr.clamp_min(1e-12), d_par)
    drall = d / theta.clamp_min(1e-12)
    return theta, d, recip, drall
