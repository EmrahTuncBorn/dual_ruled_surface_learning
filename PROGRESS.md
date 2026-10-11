# Geliştirme günlüğü

Referans belge: `docs/tarif_v3.md` (11 Ekim 2026, Sürüm 3). Önceki sürüm `docs/Regle_Yuzey_Ogrenme_Pilot_Sistem_Tarifi_v2.docx`
(6 Ekim 2026, Sürüm 2) de depoda sürümlenir. Terimler ve yazım kuralları `GLOSSARY.md`'dedir.
v2'deki "sabit" maddelere dokunan her değişiklik, ilgili sonuç görülmeden **önce** buraya tarihli
olarak yazılır ve commit'lenir.

---

## v2'den sapmalar

| # | Tarih | Değişiklik | Tür | Durum |
|---|---|---|---|---|
| S1 | 2026-10-10 | Kısıt katmanı (constraint layer) ve ara değer, gerçek dual normalizasyonla yapılır: `a = â/‖â‖`, `a* = (b − ⟨b,a⟩a)/‖â‖`. v2'deki biçimde `1/‖â‖` çarpanı eksikti; ara doğrular orijine doğru çekiliyordu (konide ara doğrunun tepeye uzaklığı 30°'de 6.7e-3, 90°'de 1.1e-1). 14.7'ye "konide ara doğrular tepeden geçer" testi eklendi. | hata düzeltmesi | uygulandı |
| S2 | 2026-10-10 | Aşama 0 eklendi: ağsız temsil deneyi (aşağıda). v2'nin 1–4. aşamalarından önce gelir; makalede sonradan eklenen aşama olarak raporlanır. | yeni aşama | tamamlandı: temsil ekseni zayıf |
| S3 | 2026-10-10 | Açılabilirlik için ayrık drall `δ_k = d_k / θ_k` de raporlanır. `d·sinθ = O(1/K²)` olduğundan v2'nin (iii) birincil ölçütü dönme miktarına bağlıdır. (iii)'ün değişip değişmeyeceği **Aşama 3'ten önce** karara bağlanacak. | ölçüt | v3'te karara bağlandı: birincil ölçüt ayrık toplam mutlak Gauss eğriliği; `d·sinθ` ve drall ikincil |
| S4 | 2026-10-10 | Test yamaları üzerinde eşleştirilmiş karşılaştırma (Wilcoxon işaretli sıra testi) ek analiz olarak eklenir. v2'nin "anlamlı fark" tanımının yerini alıp almayacağı Aşama 3'ten önce karara bağlanacak. | istatistik | v3'te karara bağlandı: Aşama 0 kuralı (geometrik ortalama oranı + Wilcoxon) |
| S5 | 2026-10-10 | Koşu sayısı düzeltildi: λ seçimi dahil yaklaşık 78 koşu (1. deney 4×3 ayar + 15; 2. deney 12×3 ayar + 15), v2'deki 30 değil. | takvim | not |
| S6 | 2026-10-10 | `L_s`, işaret hizalamasından **sonra** hesaplanır. | belirsizlik giderme | uygulandı |
| S7 | 2026-10-10 | İlgili çalışmalara eklenecekler (künyeler doğrulanmadı): Pottmann & Wallner *Computational Line Geometry*; Chen & Pottmann, regle yüzeyle yaklaşım; Pottmann–Hofer–Odehnal–Wallner, çizgi geometrisiyle yeniden yapılandırma; Liu et al. 2006 conical meshes; Stein–Grinspun–Crane 2018; Tang et al. 2016; Zhou et al. 2019 rotation representations; Point2Cyl; Vector Neurons. | literatür | açık |
| S8 | 2026-10-10 | Sıfıra bölme koruması: paydaya `+1e-8` eklemek yerine `max(‖a‖, 1e-12)` kullanılır. Toplama biçimi bağıl 1e-8 hata bırakıyor ve 14.7'deki makine hassasiyeti testlerini bozuyordu. | uygulama | uygulandı |
| S9 | 2026-10-11 | v3 belgesi yazıldı (`docs/tarif_v3.md`). Ana soru, temsil karşılaştırmasından Plücker koordinatlarındaki sert açılabilirlik katmanına kaydırıldı; v2'nin 1. deneyi kaldırıldı. Bundan sonra referans belge v3'tür. | yeni sürüm | yazıldı; Aşama 1a 2026-10-11'de onaylandı, sürüyor |


## v3'ten sapmalar

v3'teki "sabit" maddelere ve tanımlanmış testlere dokunan her değişiklik, ilgili sonuç görülmeden **önce**
buraya tarihli olarak yazılır ve commit'lenir. Sonuç görüldükten sonra yapılan değişiklik bu durumu açıkça belirtir.

| # | Tarih | Değişiklik | Tür | Durum |
|---|---|---|---|---|
| T1 | 2026-10-11 | Sert katmanın paydası `sin²θ + ε²` yerine `max(sin²θ, ε²)` (v3 3.3). İlk biçim büyük açılarda da `ε²/sin²θ` oranında kaçak bırakıyordu; yeni biçim `sinθ ≥ ε` için tamdır ve sıfıra sürekli iner. Gradyan testindeki açı kümesi kırpma köşesinden uzak tutuldu: `sinθ ∈ {10ε, 0.5ε, 0.1ε, 0}`. Kod yazılmadan, hiçbir koşu yapılmadan değiştirildi. | uygulama | uygulandı |
| T2 | 2026-10-11 | 7.2'deki iki testin iddiası, testler **başarısız olduktan sonra** değiştirildi. (3) Teğet açılabilirde düzeltmenin `K` ikiye katlanınca 4 kat küçülmesi beklenmişti; ölçülen oran 4.0'dır (sıralı katman tek çiftin `O(1/K³)` hatasını `O(1/K²)`'ye biriktirir), eşik 3 kata çekildi. (5) "Sert katmandan geçmiş yüzeyde 𝒢 makine hassasiyetinde sıfır" iddiası rastgele doğrularda yanlış çıktı (𝒢 = 9.5–19.1): şeritler düzlemseldir (düzlemsizlik < 2e-14) ama kesişme noktası yama aralığına düşebilir. İddia daraltıldı: düzlemsellik her durumda, 𝒢 ≈ 0 kesişmeler yama dışındayken. Bulgu v3 3.4'e yazıldı. | test / iddia | uygulandı |
| T3 | 2026-10-11 | v3'e eklenenler: 3.4 (gerileme kenarının yamaya düşmesi), 5.2'de başlangıç yüzeyi açık kararı, 5.4'te H için ikincil ölçüt (aralık içindeki kesişme oranı), 5.3'te τ = 0.00756. | tasarım | uygulandı; başlangıç kararı açık |
| T4 | 2026-10-11 | Ondalık ayırıcı noktaya çevrildi (PROGRESS, v3); v3'teki terim tablosu `GLOSSARY.md`'ye taşındı; v2 belgesi `docs/` altına taşındı. İçerik değişikliği yoktur. | yazım | uygulandı |
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
Ayar: her temsil için öğrenme oranı (learning rate) `lr ∈ {1e-3, 3e-3, 1e-2, 3e-2}` × `λ_s ∈ {0, 1e-3, 1e-2, 1e-1}`;
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

### Aşama 0 sonuçları (2026-10-11)

Bütün koşular `e96bef1` commit'inden yapıldı (3000 test satırı, tek commit; analiz bunu denetler).
Ham çıktılar `results/phase0/` altındadır (sürümlenmez); `report.md` ve `report.json` analiz betiğiyle üretildi.

**Doğrulamada seçilen ayarlar** (seed 0, 50 yama):

| Temsil | lr | λ_s | Doğrulama Chamfer |
|---|---|---|---|
| A | 3e-2 | 0 | 8.22e-4 |
| B | 3e-2 | 0 | 7.50e-4 |
| C | 3e-2 | 1e-3 | 6.37e-4 |

**Birincil ölçütler** (test, 200 yama, beş seed'in ortalaması; oran = A/X oranlarının geometrik ortalaması):

| Ölçüt | Karşı | Oran A/X | Wilcoxon p | Hüküm |
|---|---|---|---|---|
| Chamfer | B | 1.104 | 2.6e-21 | fark yok (eşik 1.111'in altında) |
| yakınsama adımı | B | 0.982 | 0.75 | fark yok |
| seed std | B | 1.274 | 5.8e-5 | A kötü |
| Chamfer | C | 1.342 | 2.1e-13 | **A kötü** |
| yakınsama adımı | C | 2.213 | 1.6e-32 | **A kötü** |
| seed std | C | 0.757 | 1.0e-5 | **A iyi** |

| Temsil | ort. Chamfer | ort. yakınsama (adım) | ort. seed std |
|---|---|---|---|
| A | 8.28e-4 | 254 | 1.03e-4 |
| B | 7.19e-4 | 256 | 6.97e-5 |
| C | 8.28e-4 | 127 | 2.13e-4 |

**Karar (ön kayıtlı kurala göre): temsil ekseni zayıf.** A, C'ye karşı Chamfer ve yakınsama hızında
anlamlı biçimde kötü, yalnız seed kararlılığında anlamlı biçimde iyidir. Kural "hiçbirinde kötü değil"
koşulunu istediği için sonuç "zayıf"tır.

**Aile bazında son Chamfer** (ortalama, ×1e-4):

| Aile | A | B | C |
|---|---|---|---|
| koni | 10.43 | 8.45 | 13.36 |
| silindir | 13.31 | 11.36 | 14.55 |
| genel | 6.96 | 6.50 | 4.84 |
| hiperbolik paraboloit | 5.20 | 4.65 | 3.77 |
| teğet açılabilir | 5.50 | 4.99 | 4.86 |

**İkincil ölçütler** (açılabilir aileler, ortalama; `d·sinθ` ve d mutlak değerdir):

| Aile | Temsil | d·sinθ | drall d/θ |
|---|---|---|---|
| silindir | A / B / C | 4.7e-2 / 4.4e-2 / 5.1e-3 | 0.60 / 0.51 / 1.17 |
| koni | A / B / C | 3.7e-2 / 3.1e-2 / 4.2e-3 | 0.52 / 0.51 / 0.76 |
| teğet | A / B / C | 1.9e-2 / 1.9e-2 / 2.4e-3 | 0.41 / 0.36 / 0.46 |

**Gözlemler.**
1. Aritmetik ortalamada A ve C'nin Chamfer'ı eşittir (8.28e-4); fark ailelere göre yön değiştirir.
   C, genel ve hiperbolik paraboloit ailelerinde; B ve A ise koni ve silindirde daha iyidir.
   Yama başına oranların geometrik ortalaması C lehinedir. Tek bir "en iyi temsil" yoktur;
   etki aileye bağlıdır.
2. B, Chamfer'da her ailede A'dan biraz iyidir; A'nın dual yapısı ağsız optimizasyonda bir üstünlük
   sağlamamıştır.
3. C iki kat hızlı yakınsar, ancak seed'ler arası yayılımı en büyüktür.
4. Hiçbir temsil açılabilirliği kendiliğinden öğrenmemiştir (`L_d` yoktur; drall sıfırdan uzaktır).
   C'de `d·sinθ` bir mertebe küçüktür, ama drall büyüktür. Bu, S3'teki çekinceyi doğrular:
   `d·sinθ` küçüklüğü açılabilirlik değil, ardışık doğrular arasındaki küçük dönme açısından gelir.
   S3, Aşama 3'ten önce drall lehine karara bağlanmalıdır.

**Sınırlılıklar.**
- Üç temsilde de seçilen lr ızgaranın üst sınırındadır (3e-2); daha büyük lr'lerde sıralama değişebilir.
  Izgara ön kayıtlı olduğu için genişletilmedi.
- Tek gürültü düzeyi (%1), beş seed, K = 32; kısmi örnekleme yoktur.
- Sonuç, ağ içinde fark olmadığını kanıtlamaz (ön kayıttaki sınır). "Temsil" üç bileşenin paketidir;
  bileşenler ayrılmamıştır.
- Test koşusu bellek yetersizliği nedeniyle 54/60 birimde kesildi ve aynı commit'ten kaldığı yerden
  sürdürüldü. Bitmiş birimler atlandığı ve dosyalar atomik yazıldığı için sonuçlar etkilenmez.
  Kesintiden önceki son birimin süresi (20 719 sn, yaklaşık 5.8 saat; değer `results/phase0_run.log`'dan doğrulandı) bilgisayarın uykuya geçmesinden kaynaklanır.

**Sonraki adım.** Ön kayda göre katkı, değişmez tabanlı kayıp/üretim ve hesaplama katmanı
eksenine kaydırılır ve v3 belgesi yazılır. Ondan önce aşağıdaki keşif kontrolü yapılır.

### Aşama 0 ek kontrolü: genişletilmiş lr ızgarası (keşif amaçlı, 2026-10-11)

**Neden.** Seçilen lr üç temsilde de ızgaranın üst sınırındaydı. "A, C'den kötü" bulgusu
ayar sınırından kaynaklanıyorsa v3'ün gerekçesi değişir.

**Statü.** Sonuçlar görüldükten sonra tasarlandığı için **ön kayıt dışıdır** ve Aşama 0 kararını
değiştirmez; yalnız sınırlılığın ne kadar etkili olduğunu gösterir.

**Tasarım (koşudan önce sabit).** Betik: `experiments/phase0_lrext.py`; çıktı: `results/phase0_lrext/`.
- Doğrulama taraması: `lr ∈ {3e-2, 1e-1, 3e-1}` × `λ_s ∈ {0, 1e-3}` (Aşama 0'da seçilen λ değerleri), seed 0.
  3e-2 tekrarı yeniden üretilebilirlik denetimidir; Aşama 0 değerleriyle aynı çıkması beklenir.
- Seçim yine yalnız doğrulamada, ortalama son Chamfer'a göre yapılır.
- Seçimi değişen temsiller için test kümesi beş seed'le yeniden koşulur; seçimi değişmeyenlerde
  Aşama 0 test satırları kullanılır. Karşılaştırma, aynı ölçüt ve aynı eşiklerle yapılır.
- Bu kontrolde test kümesi ikinci kez kullanılmış olur; bu nedenle sonuç yalnız bilgi amaçlıdır.

**Sonuçlar (`88ea95e`).** Yeniden üretilebilirlik denetimi geçti: lr 3e-2 birimleri Aşama 0 değerlerini
aynen verdi (A 8.220e-4; B 7.501e-4; C λ 1e-3 6.369e-4). Üç temsilin seçimi de değişti; test üçü için
yeniden koşuldu.

| Temsil | Aşama 0 (lr, λ_s) | geniş ızgara (lr, λ_s) | doğrulama Chamfer | test ort. Chamfer | yakınsama | seed std |
|---|---|---|---|---|---|---|
| A | 3e-2, 0 | 1e-1, 0 | 7.12e-4 | 6.87e-4 | 334 | 7.68e-5 |
| B | 3e-2, 0 | 3e-1, 0 | 5.92e-4 | 5.67e-4 | 650 | 3.46e-5 |
| C | 3e-2, 1e-3 | 3e-1, 1e-3 | 4.97e-4 | 5.08e-4 | 117 | 8.86e-5 |

| Ölçüt | Karşı | Oran A/X | Wilcoxon p | Hüküm |
|---|---|---|---|---|
| Chamfer | B | 1.145 | 6.5e-26 | A kötü |
| yakınsama | B | 0.502 | 1.4e-34 | A iyi |
| seed std | B | 1.398 | 8.8e-9 | A kötü |
| Chamfer | C | 1.326 | 3.8e-31 | A kötü |
| yakınsama | C | 3.064 | 1.7e-34 | A kötü |
| seed std | C | 0.737 | 2.1e-6 | A iyi |

**Yorum.**
1. Daha büyük lr üç temsili de iyileştirdi (Chamfer %15–20 düştü), ama sıralama değişmedi: C < B < A.
   A–C oranı neredeyse aynı kaldı (1.34 → 1.33). "A, C'den kötü" bulgusu ızgara sınırından kaynaklanmaz.
2. A'da 1e-1 ile 3e-1 neredeyse eşittir (7.12e-4 ve 7.13e-4), yani A'nın ayarı doymuştur. B ve C'de en iyi
   lr yine üst sınırdadır (3e-1); daha da büyük lr'ler bu iki temsili iyileştirirse aradaki fark büyür,
   kapanmaz.
3. Yakınsama adımı lr'ye güçlü biçimde bağlıdır (B'de 256 → 650): kosinüs azalmasıyla büyük lr'de kayıp
   sona kadar düşmeye devam eder. Bu ölçüt temsiller arasında farklı lr'lerle karşılaştırıldığında
   temsil etkisini lr etkisinden ayırmaz; ağırlığı düşük tutulmalıdır.
4. Aşama 0 kararı (temsil ekseni zayıf) bu kontrolle desteklenir.

---

## Günlük

- **2026-10-10** — Depo açıldı. v2 incelendi; S1–S8 kaydedildi. Aşama 0 ön kaydı yapıldı.
- **2026-10-10** — Çekirdek kod yazıldı: `ruled/geometry.py`, `ruled/reps.py`, `ruled/data.py`, `ruled/losses.py`. v2 14.7 testleri (Blaschke q testi hariç; çatı yalnız analiz içindir) ve S1 testleri: 20/20 geçti. Aşama 0 betiği `experiments/phase0.py`, değerlendirmesi `experiments/phase0_analyze.py` olarak yazıldı.
- **2026-10-10** — Chamfer hızlandırıldı: en yakın komşular KD-ağacıyla gradyansız bulunur, kayıp eşleşen çiftlerden hesaplanır (değer ve gradyan, referansla 1e-16 düzeyinde aynı). 50 yama için adım süresi 2.2 sn'den yaklaşık 0.25 sn'ye indi; ön kayıtlı yama sayısı korundu. Doğrulama kümesinden 10 yamada smoke test (kısa sağlama koşusu) yapıldı: üç temsil de 1000 adımda Chamfer'ı 5e-2'den yaklaşık 1e-3'e indirdi. Bu yalnız çalışırlık kontrolüdür, karar için kullanılmaz.
- **2026-10-10** — İlk Aşama 0 koşusu 48 yapılandırmanın 12'sinde **durduruldu ve sonuçları silindi**. Nedenleri: koşu sürerken `phase0.py` değiştirilmişti (Hausdorff hesabı bellek nedeniyle KD-ağacına alındı; sayısal etkisi 1e-8), yani doğrulama ve test aşamaları farklı commit'lerle koşacaktı; ayrıca koşu kaldığı yerden devam edemiyordu. Düzeltmeler: kod, docstring'ler ve çıktılar İngilizceye çevrildi; koşu kaldığı yerden sürdürülebilir (resumable) yapıldı (her birim, yani bir temsil-ayar-seed-parça koşusu, ayrı dosyaya atomik olarak yazılır, bitmiş birimler atlanır); koşu dizini `manifest.json` ile tek commit'e bağlandı (kirli çalışma ağacı ya da farklı commit reddedilir); her sonuç satırına commit hash'i yazılır ve analiz tek commit'ten gelmeyen satırları reddeder. Karışan etkenler notu ön kayda eklendi. Ön kaydın içeriği (veri, ölçütler, karar kuralı) değiştirilmedi.
- **2026-10-11** — Aşama 0 tamamlandı (`e96bef1`). Karar: temsil ekseni zayıf. Ayrıntılar yukarıdaki "Aşama 0 sonuçları" bölümündedir.
- **2026-10-11** — Genişletilmiş lr ızgarasıyla keşif kontrolü yapıldı (`88ea95e`). Sıralama değişmedi (C < B < A); A–C oranı 1.33. Karar desteklendi.
- **2026-10-11** — v3 belgesi `docs/tarif_v3.md` olarak yazıldı. Sert izdüşümün kapalı biçimi (düzeltme büyüklüğü = en kısa uzaklık) ve kesişen doğruların ara değerinin demette kalması, 1000 rastgele çiftte sayısal olarak sınandı (hata < 3e-14).
- **2026-10-11** — Depo GitHub'da özel olarak açıldı; gönderimler aşama sonlarında onayla yapılır.
- **2026-10-11** — Aşama 1a (kısmi): sert katman (`project_coplanar`, `developable_lines`, `DevelopableDualRep`), açı açığı ölçütü (`angle_defect_total`), cezalar (`developability_A`, `developability_C`) ve v3 7.2 testleri yazıldı; toplam 40 test geçti. `DualRep` yalnızca yeniden düzenlendi, Aşama 0 testleri değişmeden geçti.
  - Düzenlileştirme biçimi değiştirildi: payda `sin²θ + ε²` yerine `max(sin²θ, ε²)`. İlk biçim büyük açılarda da `ε²/sin²θ` oranında kaçak bırakıyordu; yeni biçim `sinθ ≥ ε` için tamdır.
  - Ölçüt sağlaması: silindir ve konide 𝒢 < 1e-10; teğet açılabilirde ızgara iki kat inceldikçe yaklaşık 16 kat küçülür; hiperbolik paraboloit ve genel ailede sayısal karelemeye birinci mertebeden yakınsar (256×256 ızgarada bağıl hata < %2).
  - Teğet açılabilirde katmanın düzeltmesi `O(1/K²)` küçülür (oran 4.0); tek çiftin hatası `O(1/K³)`'tür, sıralı katman bunu biriktirir. Testin başlangıçtaki 4 kat eşiği sınırdaydı, 3 kata çekildi.
  - **Olumsuz bulgu (v3 Bölüm 3.4):** katmanın garantisi yereldir. Her şerit düzlemseldir (dörtgen düzlemsizliği < 2e-14), ama ardışık doğruların kesişme noktası yama aralığına düşerse şerit kendini keser ve yüzey tekil olur. Kesişme noktası `konum hatası / θ` oranında kötü koşulludur: koni doğrularında 1e-2 konum gürültüsü kesişmelerin %21'ini aralığa sokar (𝒢 en çok 0.79), 1e-3 gürültüde hiçbiri girmez (𝒢 = 4e-12). Aşama 0'ın başlangıcı (doğru başına bağımsız σ = 0.1 rad) açılabilir yamalarda kesişmelerin %57–67'sini aralığa sokar.
  - τ = 0.00756 hesaplandı (`experiments/phase1_tau.py`; açılabilir olmayan 20 gerçek yamanın medyan 𝒢'si 0.756).
  - Açık karar: Aşama 1b'nin başlangıç yüzeyi (v3 Bölüm 5.2). `λ_d` ölçek koşusu ve `experiments/phase1.py` bu karara bağlıdır.
- **2026-10-11** — Depo düzeni gözden geçirildi (sapma T4). `pyproject.toml` eklendi; `pip install -e .` ile `ruled` paketi her dizinden içe aktarılır, betikler `PYTHONPATH` olmadan çalışır (`python experiments/phase0.py --help` repo dışından denendi). Sabitlenmiş `requirements.txt` (torch 2.14.1, numpy 2.5.3, scipy 1.18.1, matplotlib 3.11.2, pytest 9.1.1), `.gitattributes` (LF) ve `.gitignore` eklemeleri yapıldı. `README.md`, `RELATED_WORK.md` ve `GLOSSARY.md` yazıldı. Künyeler web aramasıyla denetlendi: 11'i doğrulandı, 1'i kısmen doğrulandı (2011 tarihli dual kuaterniyon makalesi: DOI ve içerik uyuşuyor, başlık ve yazarlar doğrulanamadı), 1'i bulunamadı ("Piecewise developable modeling via implicit neural deformation and feature-guided cutting"); 6'sı bilinen künye olarak işaretlendi. Biten koşuların özet dosyaları `results_summary/` altına alındı; tam sonuçlar `results/archives/phase0_e96bef1_lrext_88ea95e.zip` olarak arşivlendi (200 dosya, 57 MB) ve Drive'a yüklenmek üzere bekliyor. Bundan sonra Aşama 1'deki kollar (arms; karşılaştırılan yöntemler) A0, PA, PC ve H olarak anılır.
- **2026-10-11** — Aşama 1b'nin başlangıç yüzeyi karara bağlandı (v3 5.2): birincil koşu düşük frekanslı bozulmayla (doğru indisine göre `cos(πjt)`, `j = 0..3`; doğru başına standart sapma Aşama 0'la aynı: yönde 0.1, konumda 0.05), ikincil dayanıklılık analizi Aşama 0 başlangıcıyla yapılır; ikisi de dört kola uygulanır, ikincil analizde birincil koşuda seçilen ayarlar kullanılır. Ölçülen başlangıç durumu (12 doğrulama yaması, 3 seed): düşük frekanslı bozulmada yama içindeki kesişme oranı A0 0.083, H 0.090, 𝒢 0.09–0.12; Aşama 0 başlangıcında 0.74 ve 0.62, 𝒢 7.7–7.8.
- **2026-10-11** — `experiments/phase1.py` yazıldı (resumable, commit'e bağlı; `scale` ve `all` aşamaları). Smoke test sırasında bir hata bulundu: `DevelopableDualRep` eklenirken `DualRep.smooth_vars` yanlışlıkla alt sınıfa kaymıştı (`091d5b9`); A'da düzgünlük kaybı çağrılınca hata veriyordu. Düzeltildi ve bu hatayı yakalayan bir arayüz testi eklendi (hatalı sürümde başarısız, düzeltilmiş sürümde başarılı olduğu denetlendi); 41 test geçti. `091d5b9`'dan hiçbir koşu yapılmadığı için sonuçlar etkilenmedi. Adım süresi (50 yama): A0 0.25 sn, H 0.42 sn.
- **2026-10-11** — `λ_d` ölçek koşusu yapıldı (`c7a7d27`; doğrulama kümesinin 5 yaması, lr 1e-1, λ_s 0, düşük frekanslı başlangıç; özet `results_summary/phase1_scale/`). **Hiçbir kol τ = 0.00756'ya yaklaşmadı:** A0 𝒢 = 9.46 (Chamfer 7.5e-4); H 𝒢 = 26.9 (Chamfer 1.7e-3); PA'da `λ_d` 1e-2'den 1e6'ya çıkarken 𝒢 en az 1.35'e iner (λ_d = 1e3, Chamfer 6.2e-3); PC'de 𝒢 en az 14.6'dır (λ_d = 1e2, Chamfer 3.1e-3). Değerler eşiğin 180–4600 katıdır; açılabilir olmayan gerçek yamaların medyanı 0.76'dır.
  - **Tanı (karar verisi değildir, aynı 5 yamada A0 ve H yeniden optimize edildi):** yüzeyler katlanır. Ardışık doğru orta noktalarının yön değiştirme oranı A0'da %47–60, H'de %57–73 (doğrular ileri geri zikzak çizer); komşu doğrular arasında dörtgen normali ters dönen dörtgen oranı A0'da %6–7, H'de %10–13. Bu, v2 14.6'daki "doğru sırası ters döner, yüzey kendi üzerine katlanır" biçimidir. Chamfer bunu görmez; 𝒢 katlanmayı büyük değer olarak yakalar. Dolayısıyla 𝒢'nin büyüklüğü açılabilirlikten çok katlanmayı ölçmektedir ve v3 5.3'teki τ kuralı bu haliyle hiçbir kolda sağlanamaz.
  - **Aşama 0 için çekince:** Aşama 0'da da λ_s seçimi yalnız Chamfer'a göre yapıldı ve λ_s = 0 ya da 1e-3 seçildi; yüzeylerin orada da katlanmış olması olasıdır (ölçülmedi). Aşama 0'ın bulgusu bu nedenle "nokta uydurma doğruluğu" ile sınırlı okunmalıdır, yüzey kalitesi hakkında bir şey söylemez.
  - Aşama 1a kapanmadı: `λ_d` ızgarası bu durumda anlamlı biçimde sabitlenemez. Tasarım kararı bekleniyor.

- **2026-10-11** — Katlanma tanısının planı (sonuçlar görülmeden yazıldı; keşif amaçlıdır, karar verisi değildir). Soru: düzgünlük terimi katlanmayı gideriyor mu, giderirken Chamfer ne kadar bozuluyor? Yalnız A0 ve H; doğrulama kümesinin ölçek koşusundaki 5 yaması; lr 1e-1, seed 0, düşük frekanslı başlangıç; λ_s ∈ {0, 1e-2, 1e-1, 1, 10} (λ_s = 0 karşılaştırma için yeniden koşulur). Ölçülenler: Chamfer, 𝒢, yama içindeki kesişme oranı ve iki katlanma ölçüsü (`fold_rates`, `experiments/phase1.py`): (1) yön değiştirme oranı: ardışık doğru orta noktalarının izlediği yolun geri döndüğü iç doğruların oranı; (2) normal dönüşü oranı: değerlendirme ızgarasında (S = 8, U = 64) bir doğrunun iki yanındaki dörtgen normallerinin ters yönlü olduğu çiftlerin oranı. Ölçülerin sağlaması: gerçek koni, silindir ve teğet açılabilir doğrularında yön değiştirme 0–0.03, normal dönüşü 0–0.011 (tepe noktası ve gerileme kenarı yakınındaki yozlaşmış dörtgenler); doğru sırası ikişer ikişer yer değiştirilmiş zikzakta 0.97–1.0 ve yaklaşık 0.12. Sonuç ne olursa olsun, v3 5.3'te yapılacak değişiklik Aşama 1b ön kaydından önce T5 sapması olarak ayrıca yazılacaktır.
- **2026-10-11** — Katlanma tanısı yapıldı (`3084de4`; özet `results_summary/phase1_smooth/`; keşif amaçlıdır, karar verisi değildir). λ_s = 0 satırları ölçek koşusuyla birebir aynı çıktı.

  | Kol | λ_s | Chamfer | 𝒢 ortalama | 𝒢 medyan | Normal dönüşü | Yön değiştirme | Yama içi kesişme |
  |---|---|---|---|---|---|---|---|
  | A0 | 0 | 7.5e-4 | 9.46 | 8.32 | 0.069 | 0.55 | 0.40 |
  | A0 | 1e-2 | 1.19e-3 | 0.287 | 0.126 | 0.006 | 0.44 | 0.10 |
  | A0 | 1e-1 | 4.42e-3 | 0.144 | 0.094 | 0.003 | 0.46 | 0.10 |
  | A0 | 1 | 9.22e-3 | 0.107 | 0.029 | 0.000 | 0.61 | 0.11 |
  | A0 | 10 | 1.36e-2 | 0.030 | 0.019 | 0.000 | 0.77 | 0.10 |
  | H | 0 | 1.74e-3 | 26.9 | 25.3 | 0.113 | 0.66 | 0.52 |
  | H | 1e-2 | 4.10e-3 | 0.923 | 0.336 | 0.018 | 0.46 | 0.17 |
  | H | 1e-1 | 5.41e-3 | 0.125 | 0.006 | 0.010 | 0.48 | 0.04 |
  | H | 1 | 1.19e-2 | 0.169 | 0.085 | 0.009 | 0.52 | 0.07 |
  | H | 10 | 3.76e-2 | 0.124 | 0.044 | 0.009 | 0.66 | 0.08 |

  - Doğrular arası katlanma (normal dönüşü) λ_s ≥ 1e-2'de giderilir: A0'da 0.069'dan 0.006 ve altına, H'de 0.113'ten 0.018 ve altına iner; gerçek açılabilir yüzeylerdeki taban 0–0.011'dir. Bu en küçük λ_s'de Chamfer bedeli A0'da 1.6 kat, H'de 2.4 kattır. 𝒢 30–200 kat düşer.
  - **Önceki tanıda bir ölçüt hatası düzeltildi:** yön değiştirme oranı katlanmanın geçerli bir ölçüsü değildir. λ_s arttıkça katlanma kaybolurken bu oran düşmez, artar (A0'da 0.44'ten 0.77'ye). Orta nokta, doğru boyunca serbestçe kayabildiği için yüzeyin şeklini değil, aralıkların yerleşimini yansıtır. Bir önceki kayıttaki "doğrular ileri geri zikzak çizer" yorumu bu ölçüye dayanıyordu ve geri çekilir; katlanma bulgusu normal dönüşü ve 𝒢 ile geçerliliğini korur.
  - Hiçbir yapılandırmada ortalama 𝒢 τ = 0.00756'ya inmez (en düşük A0 λ_s = 10'da 0.030, Chamfer 18 kat kötü). Ortalama, yama başına uç değerlere duyarlıdır: H λ_s = 1e-1'de yama değerleri 0.000, 0.536, 0.000, 0.080, 0.006'dır, medyan 0.006 ≤ τ. Ortalama ile medyan arasındaki bu fark not edildi; seçim kuralının (v3 5.3, ortalama) ve H önkoşulunun (v3 5.5, medyan) farklı istatistik kullandığı bu vesileyle görüldü. 5 yamayla A0–H karşılaştırması yapılmaz.
  - Aşama 1a kapanmadı. v3 5.3'te yapılacak değişiklik karara bağlanınca T5 olarak yazılacaktır; bu tanının sonuçlarını gördükten sonra yapılacağı için o kayıtta açıkça belirtilecektir.
