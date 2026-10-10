# Geliştirme günlüğü

Referans belge: `Regle_Yuzey_Ogrenme_Pilot_Sistem_Tarifi_v2.docx` (6 Ekim 2026, Sürüm 2), depoda sürümlenir.
v2'deki "sabit" maddelere dokunan her değişiklik, ilgili sonuç görülmeden **önce** buraya tarihli
olarak yazılır ve commit'lenir.

---

## v2'den sapmalar

| # | Tarih | Değişiklik | Tür | Durum |
|---|---|---|---|---|
| S1 | 2026-10-10 | Kısıt katmanı (constraint layer) ve ara değer, gerçek dual normalizasyonla yapılır: `a = â/‖â‖`, `a* = (b − ⟨b,a⟩a)/‖â‖`. v2'deki biçimde `1/‖â‖` çarpanı eksikti; ara doğrular orijine doğru çekiliyordu (konide ara doğrunun tepeye uzaklığı 30°'de 6.7e-3, 90°'de 1.1e-1). 14.7'ye "konide ara doğrular tepeden geçer" testi eklendi. | hata düzeltmesi | uygulandı |
| S2 | 2026-10-10 | Aşama 0 eklendi: ağsız temsil deneyi (aşağıda). v2'nin 1–4. aşamalarından önce gelir; makalede sonradan eklenen aşama olarak raporlanır. | yeni aşama | ön kayıt yapıldı |
| S3 | 2026-10-10 | Açılabilirlik için ayrık drall `δ_k = d_k / θ_k` de raporlanır. `d·sinθ = O(1/K²)` olduğundan v2'nin (iii) birincil ölçütü dönme miktarına bağlıdır. (iii)'ün değişip değişmeyeceği **Aşama 3'ten önce** karara bağlanacak. | ölçüt | açık |
| S4 | 2026-10-10 | Test yamaları üzerinde eşleştirilmiş karşılaştırma (Wilcoxon işaretli sıra testi) ek analiz olarak eklenir. v2'nin "anlamlı fark" tanımının yerini alıp almayacağı Aşama 3'ten önce karara bağlanacak. | istatistik | açık |
| S5 | 2026-10-10 | Koşu sayısı düzeltildi: λ seçimi dahil yaklaşık 78 koşu (1. deney 4×3 ayar + 15; 2. deney 12×3 ayar + 15), v2'deki 30 değil. | takvim | not |
| S6 | 2026-10-10 | `L_s`, işaret hizalamasından **sonra** hesaplanır. | belirsizlik giderme | uygulandı |
| S7 | 2026-10-10 | İlgili çalışmalara eklenecekler (künyeler doğrulanmadı): Pottmann & Wallner *Computational Line Geometry*; Chen & Pottmann, regle yüzeyle yaklaşım; Pottmann–Hofer–Odehnal–Wallner, çizgi geometrisiyle yeniden yapılandırma; Liu et al. 2006 conical meshes; Stein–Grinspun–Crane 2018; Tang et al. 2016; Zhou et al. 2019 rotation representations; Point2Cyl; Vector Neurons. | literatür | açık |
| S8 | 2026-10-10 | Sıfıra bölme koruması: paydaya `+1e-8` eklemek yerine `max(‖a‖, 1e-12)` kullanılır. Toplama biçimi bağıl 1e-8 hata bırakıyor ve 14.7'deki makine hassasiyeti testlerini bozuyordu. | uygulama | uygulandı |

---

## Aşama 0 — Ağsız temsil deneyi (ön kayıt, 2026-10-10)

**Soru.** Ağ olmadan, her yama için K doğru doğrudan optimize edildiğinde A (dual), B (dayanak+yön)
ve C (iki uç nokta) temsilleri arasında doğruluk, yakınsama hızı ya da kararlılık farkı var mı?
Bu deneyle temsilin koşullanma (conditioning) etkisi, kodlayıcı/çözücü mimarisinden ayrılır.

**Veri.** v2 Bölüm 14.3'teki üreteç; beş aile. Doğrulama kümesi (validation set): aile başına 10 yama (50).
Test kümesi: aile başına 40 yama (200). Ayrı veri seed'leri (rastgelelik tohumu; 1000 ve 2000).
Bu test kümesi Aşama 0'a özgüdür, v2'nin test ayrımıyla ilgisi yoktur. Yama başına 1024 nokta,
%1 gürültü, v2 normalizasyonu, rastgele dönme. Kısmi örnekleme yok (v2'de yalnız eğitim içindir).

**Yüzey.** K = 32 doğru, ardışık doğrular arasında 4 ara adım, doğru başına 16 nokta (v2 14.4).
A'da ara değer S1'deki dual normalizasyonla yapılır.

**Başlangıç.** Üç temsil için **aynı başlangıç yüzeyi**: nokta bulutunun PCA düzlemi üzerinde,
2. ana eksene paralel 32 doğru, 1. ana eksen boyunca eşit aralıklı; aralık izdüşüm genişliğini
kapsar. Seed s ∈ {0,…,4} için her doğru geometrik olarak küçük bir rastgele dönme (σ = 0.1 rad)
ve öteleme (σ = 0.05) ile bozulur; bozulmuş doğrular sonra her temsile çevrilir.
Aynı seed üç temsilde aynı başlangıç yüzeyini verir.

**Optimizasyon.** Adam, 1000 adım, kosinüs azalması. Kayıp `L_CD + λ_s L_s`; `L_s` her temsilin kendi
değişkenlerinde (v2 14.4), işaret hizalamasından sonra. `L_d` yoktur.
Ayar: her temsil için `lr ∈ {1e-3, 3e-3, 1e-2, 3e-2}` × `λ_s ∈ {0, 1e-3, 1e-2, 1e-1}`;
yalnızca doğrulama kümesinde ve seed 0 ile, ortalama son Chamfer hatasına göre seçilir.

**Birincil ölçütler** (test kümesinde, yama başına, beş seed'in ortalaması):
1. Son Chamfer hatası: tahmin ile gürültüsüz gerçek yüzey arasında alan ağırlıklı 4096'şar nokta.
2. Yakınsama hızı: veri Chamfer kaybının son değerinin %110'una ilk indiği adım.
3. Kararlılık: son Chamfer hatasının beş seed üzerindeki standart sapması.

İkincil (yalnız rapor): açılabilir ailelerde ayrık drall ve `d·sinθ` kalıntısı; aile bazında tablolar.

**Anlamlı fark.** İki temsil X, Y için yama başına oran `r = m_X / m_Y`. Fark, oranların geometrik
ortalaması ≤ 0.9 ya da ≥ 1/0.9 **ve** 200 yama üzerinde eşleştirilmiş Wilcoxon p < 0.01 ise anlamlıdır.

**Karar kuralı (sonuçlardan önce sabit).**
- **Temsil ekseni canlı:** A, en az bir birincil ölçütte C'den anlamlı biçimde iyi ve hiçbirinde
  anlamlı biçimde kötü. → v2 pilotu (Aşama 1–4) temsil sorusuyla sürer.
- **Temsil ekseni zayıf:** diğer bütün durumlar. → Katkı, değişmez tabanlı kayıp/üretim ve
  hesaplama katmanı eksenine kaydırılır; v3 belgesi yazılır.
- A–B karşılaştırması bilgi amaçlı raporlanır, karara girmez.

**Karışan etkenler (confound).** Temsiller arasında tek bir şey değişmez; "temsil" şu üç bileşenin
paketidir ve Aşama 0 bunları birbirinden ayırmaz:
1. çıktı koordinatları (optimize edilen 8 sayının anlamı);
2. ardışık doğrular arasındaki ara değer şeması (A: Plücker koordinatlarında doğrusal + dual
   normalizasyon; B: c ve a'da doğrusal + a normalizasyonu; C: uç noktalarda doğrusal, yani
   çift doğrusal yama);
3. `L_s`'nin hesaplandığı değişkenler (A: a, a*; B: c, a; C: q0, q1).

Ayrıca lr ve λ_s her temsil için ayrı seçilir; bu, karşılaştırmanın adil olması için bilerek yapılır.
"Temsil ekseni canlı" çıkarsa, farkın hangi bileşenden geldiğini ayırmak için ek ablasyon gerekir.

**Sınır.** Olumsuz sonuç, ağ içinde fark olmadığını kanıtlamaz; yalnızca temsil sorusunun
öncelikli yatırım olmadığını gösterir.

Hesaplama bütçesi aşılırsa, **sonuçlar görülmeden** önce yama sayısı azaltılır ve buraya yazılır.

---

## Günlük

- **2026-10-10** — Depo açıldı. v2 incelendi; S1–S8 kaydedildi. Aşama 0 ön kaydı yapıldı.
- **2026-10-10** — Çekirdek kod yazıldı: `ruled/geometry.py`, `ruled/reps.py`, `ruled/data.py`, `ruled/losses.py`. v2 14.7 testleri (Blaschke q testi hariç; çatı yalnız analiz içindir) ve S1 testleri: 20/20 geçti. Aşama 0 betiği `experiments/phase0.py`, değerlendirmesi `experiments/phase0_analyze.py` olarak yazıldı.
- **2026-10-10** — Chamfer hızlandırıldı: en yakın komşular KD-ağacıyla gradyansız bulunur, kayıp eşleşen çiftlerden hesaplanır (değer ve gradyan, referansla 1e-16 düzeyinde aynı). 50 yama için adım süresi 2,2 sn'den yaklaşık 0,25 sn'ye indi; ön kayıtlı yama sayısı korundu. Doğrulama kümesinden 10 yamada smoke test (kısa sağlama koşusu) yapıldı: üç temsil de 1000 adımda Chamfer'ı 5e-2'den yaklaşık 1e-3'e indirdi. Bu yalnız çalışırlık kontrolüdür, karar için kullanılmaz.
- **2026-10-10** — İlk Aşama 0 koşusu 48 yapılandırmanın 12'sinde **durduruldu ve sonuçları silindi**. Nedenleri: koşu sürerken `phase0.py` değiştirilmişti (Hausdorff hesabı bellek nedeniyle KD-ağacına alındı; sayısal etkisi 1e-8), yani doğrulama ve test aşamaları farklı commit'lerle koşacaktı; ayrıca koşu kaldığı yerden devam edemiyordu. Düzeltmeler: kod, docstring'ler ve çıktılar İngilizceye çevrildi; koşu resumable yapıldı (her birim ayrı dosyaya atomik olarak yazılır, bitmiş birimler atlanır); koşu dizini `manifest.json` ile tek commit'e bağlandı (kirli çalışma ağacı ya da farklı commit reddedilir); her sonuç satırına commit hash'i yazılır ve analiz tek commit'ten gelmeyen satırları reddeder. Karışan etkenler notu ön kayda eklendi. Ön kaydın içeriği (veri, ölçütler, karar kuralı) değiştirilmedi.
