# Geliştirme günlüğü

Referans belge: `Regle_Yuzey_Ogrenme_Pilot_Sistem_Tarifi_v2.docx` (6 Ekim 2026, Sürüm 2), depoda sürümlenir.
v2'deki "sabit" maddelere dokunan her değişiklik, ilgili sonuç görülmeden **önce** buraya tarihli
olarak yazılır ve commit'lenir.

---

## v2'den sapmalar

| # | Tarih | Değişiklik | Tür | Durum |
|---|---|---|---|---|
| S1 | 2026-10-10 | Kısıt katmanı (constraint layer) ve ara değer, gerçek dual normalizasyonla yapılır: `a = â/‖â‖`, `a* = (b − ⟨b,a⟩a)/‖â‖`. v2'deki biçimde `1/‖â‖` çarpanı eksikti; ara doğrular orijine doğru çekiliyordu (konide ara doğrunun tepeye uzaklığı 30°'de 6.7e-3, 90°'de 1.1e-1). 14.7'ye "konide ara doğrular tepeden geçer" testi eklendi. | hata düzeltmesi | uygulandı |
| S2 | 2026-10-10 | Aşama 0 eklendi: ağsız temsil deneyi (aşağıda). v2'nin 1–4. aşamalarından önce gelir; makalede sonradan eklenen aşama olarak raporlanır. | yeni aşama | tamamlandı: temsil ekseni zayıf |
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

### Aşama 0 sonuçları (2026-10-11)

Bütün koşular `e96bef1` commit'inden yapıldı (3000 test satırı, tek commit; analiz bunu denetler).
Ham çıktılar `results/phase0/` altındadır (sürümlenmez); `report.md` ve `report.json` analiz betiğiyle üretildi.

**Doğrulamada seçilen ayarlar** (seed 0, 50 yama):

| Temsil | lr | λ_s | Doğrulama Chamfer |
|---|---|---|---|
| A | 3e-2 | 0 | 8,22e-4 |
| B | 3e-2 | 0 | 7,50e-4 |
| C | 3e-2 | 1e-3 | 6,37e-4 |

**Birincil ölçütler** (test, 200 yama, beş seed'in ortalaması; oran = A/X oranlarının geometrik ortalaması):

| Ölçüt | Karşı | Oran A/X | Wilcoxon p | Hüküm |
|---|---|---|---|---|
| Chamfer | B | 1,104 | 2,6e-21 | fark yok (eşik 1,111'in altında) |
| yakınsama adımı | B | 0,982 | 0,75 | fark yok |
| seed std | B | 1,274 | 5,8e-5 | A kötü |
| Chamfer | C | 1,342 | 2,1e-13 | **A kötü** |
| yakınsama adımı | C | 2,213 | 1,6e-32 | **A kötü** |
| seed std | C | 0,757 | 1,0e-5 | **A iyi** |

| Temsil | ort. Chamfer | ort. yakınsama (adım) | ort. seed std |
|---|---|---|---|
| A | 8,28e-4 | 254 | 1,03e-4 |
| B | 7,19e-4 | 256 | 6,97e-5 |
| C | 8,28e-4 | 127 | 2,13e-4 |

**Karar (ön kayıtlı kurala göre): temsil ekseni zayıf.** A, C'ye karşı Chamfer ve yakınsama hızında
anlamlı biçimde kötü, yalnız seed kararlılığında anlamlı biçimde iyidir. Kural "hiçbirinde kötü değil"
koşulunu istediği için sonuç "zayıf"tır.

**Aile bazında son Chamfer** (ortalama, ×1e-4):

| Aile | A | B | C |
|---|---|---|---|
| koni | 10,43 | 8,45 | 13,36 |
| silindir | 13,31 | 11,36 | 14,55 |
| genel | 6,96 | 6,50 | 4,84 |
| hiperbolik paraboloit | 5,20 | 4,65 | 3,77 |
| teğet açılabilir | 5,50 | 4,99 | 4,86 |

**İkincil ölçütler** (açılabilir aileler, ortalama; `d·sinθ` ve d mutlak değerdir):

| Aile | Temsil | d·sinθ | drall d/θ |
|---|---|---|---|
| silindir | A / B / C | 4,7e-2 / 4,4e-2 / 5,1e-3 | 0,60 / 0,51 / 1,17 |
| koni | A / B / C | 3,7e-2 / 3,1e-2 / 4,2e-3 | 0,52 / 0,51 / 0,76 |
| teğet | A / B / C | 1,9e-2 / 1,9e-2 / 2,4e-3 | 0,41 / 0,36 / 0,46 |

**Gözlemler.**
1. Aritmetik ortalamada A ve C'nin Chamfer'ı eşittir (8,28e-4); fark ailelere göre yön değiştirir.
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
  Kesintiden önceki son birimin süresi (20.719 sn) bilgisayarın uykuya geçmesinden kaynaklanır.

**Sonraki adım (onay bekleniyor).** Ön kayda göre katkı, değişmez tabanlı kayıp/üretim ve
hesaplama katmanı eksenine kaydırılır ve v3 belgesi yazılır.

---

## Günlük

- **2026-10-10** — Depo açıldı. v2 incelendi; S1–S8 kaydedildi. Aşama 0 ön kaydı yapıldı.
- **2026-10-10** — Çekirdek kod yazıldı: `ruled/geometry.py`, `ruled/reps.py`, `ruled/data.py`, `ruled/losses.py`. v2 14.7 testleri (Blaschke q testi hariç; çatı yalnız analiz içindir) ve S1 testleri: 20/20 geçti. Aşama 0 betiği `experiments/phase0.py`, değerlendirmesi `experiments/phase0_analyze.py` olarak yazıldı.
- **2026-10-10** — Chamfer hızlandırıldı: en yakın komşular KD-ağacıyla gradyansız bulunur, kayıp eşleşen çiftlerden hesaplanır (değer ve gradyan, referansla 1e-16 düzeyinde aynı). 50 yama için adım süresi 2,2 sn'den yaklaşık 0,25 sn'ye indi; ön kayıtlı yama sayısı korundu. Doğrulama kümesinden 10 yamada smoke test (kısa sağlama koşusu) yapıldı: üç temsil de 1000 adımda Chamfer'ı 5e-2'den yaklaşık 1e-3'e indirdi. Bu yalnız çalışırlık kontrolüdür, karar için kullanılmaz.
- **2026-10-10** — İlk Aşama 0 koşusu 48 yapılandırmanın 12'sinde **durduruldu ve sonuçları silindi**. Nedenleri: koşu sürerken `phase0.py` değiştirilmişti (Hausdorff hesabı bellek nedeniyle KD-ağacına alındı; sayısal etkisi 1e-8), yani doğrulama ve test aşamaları farklı commit'lerle koşacaktı; ayrıca koşu kaldığı yerden devam edemiyordu. Düzeltmeler: kod, docstring'ler ve çıktılar İngilizceye çevrildi; koşu resumable yapıldı (her birim ayrı dosyaya atomik olarak yazılır, bitmiş birimler atlanır); koşu dizini `manifest.json` ile tek commit'e bağlandı (kirli çalışma ağacı ya da farklı commit reddedilir); her sonuç satırına commit hash'i yazılır ve analiz tek commit'ten gelmeyen satırları reddeder. Karışan etkenler notu ön kayda eklendi. Ön kaydın içeriği (veri, ölçütler, karar kuralı) değiştirilmedi.
- **2026-10-11** — Aşama 0 tamamlandı (`e96bef1`). Karar: temsil ekseni zayıf. Ayrıntılar yukarıdaki "Aşama 0 sonuçları" bölümündedir.
