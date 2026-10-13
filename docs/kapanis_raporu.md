# Plücker koordinatlarında regle ve açılabilir yüzey uydurma: kapanış raporu

Emrah Tunç · 2026-10-13 · Depo: EmrahTuncBorn/dual_ruled_surface_learning (commit `5bef525`)

## 1. Özet

Bu projede nokta bulutlarına regle yüzey (ruled surface) uydurulurken doğruların hangi koordinatlarla
temsil edileceğinin ve açılabilirliğin (developability) nasıl sağlanacağının öğrenmeyi etkileyip etkilemediği
incelendi. Ağ eğitilmeden önce, her yama için doğruların doğrudan optimize edildiği iki deney yapıldı. İki
deneyin de tasarımı, karar kuralı dahil, sonuçlar görülmeden yazıldı ve commit'lendi (ön kayıt; pre-registration).

- **Aşama 0 (temsil deneyi):** Plücker koordinatlarına dayanan dual temsil (A), iki uç noktayla temsile (C)
  göre uydurma hatasında ve yakınsama hızında anlamlı biçimde kötü, yalnız seed kararlılığında iyi çıktı.
  Ön kayıtlı karar: **temsil ekseni zayıf.**
- **Aşama 1b (açılabilirlik deneyi):** Ardışık doğruları kapalı biçimde kesiştiren sert açılabilirlik katmanı
  (H), açılabilirlik önkoşulunu sağlayamadı: test yamalarında açı açığı ölçütünün medyanı 1.134, eşik
  τ = 0.00756. Ön kayıtlı karar: **zayıf.** Aynı yamalarda ceza terimiyle çalışan kol (PA) eşiğin altına indi.
- **Mekanizma:** Katman her doğru çiftini kesiştirir ve şeritleri düzlemsel tutar, ama kesişme noktası yama
  içine düşünce şerit kendini keser. Kesişme yama dışında kaldığında H yüzeylerinin %95–98'i eşiğin altındadır,
  içine düştüğünde %1–4'ü.
- **Literatür:** Katmanın kapalı biçimiyle aynı olan önceki bir çalışma bulunmadı, ama parçaları standarttır.

Bu sonuçlar üzerine proje, ağ aşamasına geçilmeden kapatıldı. Rapor, yöntemi, deney tasarımını, sonuçları
ve süreçte öğrenilenleri bir arada sunar.

## 2. Problem ve motivasyon

### 2.1 Regle ve açılabilir yüzeyler

Regle yüzey, bir doğru ailesinin süpürdüğü yüzeydir: `x(u, v) = c(u) + v·a(u)`. Doğrulara üreteç
(ruling) denir. Açılabilir yüzey, gerilmeden ve yırtılmadan düzleme açılabilen yüzeydir; Gauss eğriliği her
yerde sıfırdır. Her açılabilir yüzey regledir; tersi doğru değildir (örneğin hiperbolik paraboloit regledir
ama açılabilir değildir). Açılabilir yüzeylerin üç temel türü silindir, koni ve teğet açılabilirdir
(tangent developable).

Açılabilirlik, sac metal, mimari cephe ve kumaş gibi düz bir malzemeden üretilen parçalar için doğrudan
bir üretim koşuludur. Bu yüzden bir nokta bulutuna açılabilir bir yüzey uydurmak pratik bir sorudur.

### 2.2 Ayrık açılabilirlik

Yüzey sonlu sayıda doğruyla (K doğru) temsil edildiğinde açılabilirlik koşulu basit bir biçim alır: **ardışık
her iki doğru aynı düzlemde olmalı**, yani kesişmeli ya da paralel olmalıdır. O zaman ardışık doğrular
arasındaki her şerit düzlemseldir ve şeritler düzleme açılabilir. Bu tanım klasiktir (Sauer 1970; Pottmann ve
Wallner 2001).

### 2.3 Plücker koordinatları ve dual doğrular

Birim yönü `a` ve üzerindeki bir noktası `p` olan doğru, Plücker koordinatlarında `(a, m)` çiftiyle temsil
edilir. Burada `m = p × a` moment vektörüdür ve iki koşul sağlanır: `‖a‖ = 1` ve `⟨a, m⟩ = 0`. Aynı
doğru dual sayılarla tek bir dual birim vektör olarak da yazılabilir: `A = a + ε m`, burada `ε² = 0`.

İki doğrunun karşılıklı çarpımı (reciprocal product)

$$
r = \langle a_1, m_2 \rangle + \langle a_2, m_1 \rangle = -d \sin\theta
$$

ile verilir. Burada `d` doğrular arasındaki en kısa uzaklık, `θ` aralarındaki açıdır. İki doğru ancak ve
ancak `r = 0` ise aynı düzlemdedir. Dolayısıyla ayrık açılabilirlik koşulu Plücker koordinatlarında her ardışık
çift için tek bir denklemdir: `r_k = 0`.

### 2.4 Araştırma soruları

Projenin başlangıç tasarımı (v2) bir kodlayıcı-çözücü ağın doğruları dual temsille üretmesini öngörüyordu.
Ağ eğitimi pahalı olduğu için önce ağsız iki soru soruldu:

1. **Temsil sorusu (Aşama 0):** Dual temsil, doğrudan optimizasyonda diğer temsillere göre daha doğru, daha
   hızlı ya da daha kararlı mı?
2. **Açılabilirlik sorusu (Aşama 1b):** Açılabilirliği Plücker koordinatlarında kapalı biçimli bir sert katmanla
   (hard layer) zorlamak, aynı açılabilirlik düzeyine ceza terimiyle ulaşmaya göre uydurma doğruluğunda kazanç
   sağlar mı?

İkisinin de olumsuz çıkması hâlinde ağ aşamasına geçilmemesi baştan planlandı.

## 3. Yöntem

### 3.1 Veri

Yamalar sentetik olarak üretildi. Aşama 0'da beş aile kullanıldı: silindir, koni, teğet açılabilir,
hiperbolik paraboloit ve genel regle yüzey. Aşama 1b'de yalnız ilk üçü (açılabilir aileler) kullanıldı. Her
yamada 1024 nokta, %1 gürültü, normalizasyon ve rastgele dönme vardır. Doğrulama (validation) ve test kümeleri
ayrı veri seed'leriyle üretildi.

| Aşama | Doğrulama | Test |
|---|---|---|
| 0 | aile başına 10 (50 yama) | aile başına 40 (200 yama) |
| 1b | aile başına 10 (30 yama) | aile başına 40 (120 yama) |

### 3.2 Yüzey ve temsiller

Her yüzey K = 32 doğrudan oluşur. Ardışık doğrular arasında 4 ara doğru üretilir ve her doğrudan 16 nokta
örneklenir. Aşama 0'da üç temsil karşılaştırıldı:

| Temsil | Optimize edilen değişkenler | Ara doğru üretimi |
|---|---|---|
| A (dual) | `â, b` (Plücker, normalize edilmemiş) ve aralık | Plücker koordinatlarında doğrusal + dual normalizasyon |
| B (dayanak + yön) | `c, a` ve aralık | `c` ve `a`'da doğrusal + `a` normalizasyonu |
| C (iki uç nokta) | `q0, q1` | uç noktalarda doğrusal (çift doğrusal yama) |

**Dual normalizasyon.** Optimize edilen serbest altı sayı her adımda geçerli bir doğruya çevrilir:

$$
a = \frac{\hat a}{\lVert \hat a \rVert}, \qquad m = \frac{b - \langle b, a \rangle a}{\lVert \hat a \rVert}
$$

Bu, dual vektörün dual normuna bölünmesidir. İlk tasarımda `1/‖â‖` çarpanı eksikti ve ara doğrular orijine
doğru çekiliyordu; hata Aşama 0'dan önce bulunup düzeltildi (sapma S1). Literatür taramasında aynı formülün
Odehnal'ın (2008) "altı-vektöre en yakın doğru" formülüyle aynı olduğu görüldü.

### 3.3 Sert açılabilirlik katmanı

Katman, doğruları sırayla dolaşır ve her doğrunun momentini, bir önceki (düzeltilmiş) doğruyla aynı düzlemde
olacak biçimde en az değişiklikle düzeltir. Yönler değişmez. Yön sabitken koşul `r_k = 0` momente göre
doğrusaldır, bu yüzden çözüm kapalı biçimdedir:

$$
n = a_{k-1} - \langle a_{k-1}, a_k \rangle a_k, \qquad r = \langle a_{k-1}, m^0_k \rangle + \langle a_k, m_{k-1} \rangle
$$

$$
m_k = m^0_k - \frac{r}{\max(\lVert n \rVert^2, \epsilon^2)} \, n, \qquad \epsilon = 10^{-3}
$$

`n`, `a_k`'ya diktir; bu yüzden düzeltme Plücker koşulunu (`⟨a_k, m_k⟩ = 0`) korur. Düzeltmenin büyüklüğü,
ham doğru ile bir önceki doğru arasındaki en kısa uzaklığa eşittir. Payda, paralele yakın doğrularda patlamayı
önlemek için kırpılır: `sinθ ≥ ε` olduğunda düzeltme tamdır, paralel doğrularda sürekli olarak sıfıra iner.
Kapalı biçim ve özellikleri 1000 rastgele çiftte sayısal olarak sınandı (hata < 3e-14).

Kesişen iki doğrunun Plücker koordinatlarındaki ara değerleri aynı demette (pencil) kalır. Bu yüzden katmandan
geçmiş yüzeyde ara doğrular da şeridin düzleminde kalır ve her şerit düzlemseldir.

**Garantinin sınırı.** Katman şeritlerin düzlemsel olmasını garanti eder, yüzeyin açılabilir olmasını değil.
Ardışık iki doğrunun kesişme noktası yamanın içine düşerse şerit bir papyon (bowtie) biçimi alır ve kendini
keser; yüzey o noktada tekildir. Kesişme noktasının konumu `konum hatası / θ` oranında kötü koşulludur: açı
küçükken küçük bir hata kesişmeyi çok uzağa ya da yamanın içine taşır. Bu durum Aşama 1a'da birim testleri
sırasında bulundu ve tasarım belgesine yazıldı (sapma T2).

### 3.4 Karşılaştırılan kollar (Aşama 1b)

| Kol | Temsil | Açılabilirlik |
|---|---|---|
| A0 | A | yok (karşılaştırma tabanı) |
| PA | A | ceza: `Σ r_k²` |
| PC | C | ceza: `Σ V_k²` (ardışık uç noktaların oluşturduğu dörtyüzlü hacmi) |
| H | A | sert katman |
| Hrev | A | sert katman, ters sırada (yalnız ikincil analiz) |

Kayıp `L_CD + λ_s L_s + λ_d L_d` biçimindedir: `L_CD` Chamfer uzaklığı, `L_s` doğrular arası düzgünlük terimi,
`L_d` açılabilirlik cezasıdır. Optimizasyon Adam ile 1000 adım, kosinüs azalmasıyla yapıldı.

### 3.5 Ölçütler

- **Chamfer hatası:** tahmin edilen yüzey ile gürültüsüz gerçek yüzey arasında, alan ağırlıklı 4096'şar nokta.
- **Açı açığı 𝒢 (angle defect):** yüzey ızgarasındaki iç köşelerde `|2π − Σ açı|` değerlerinin toplamı; ayrık
  toplam mutlak Gauss eğriliğidir. Açılabilir yüzeyde sıfıra iner. Ölçüt silindir ve konide 1e-10'un altında,
  teğet açılabilirde ızgara inceldikçe sıfıra yakınsar.
- **Eşik τ = 0.00756:** açılabilir olmayan 20 gerçek yamanın medyan 𝒢'sinin (0.756) %1'i.
- **İkincil:** normal dönüşü oranı (katlanma ölçüsü), yama içi kesişme oranı, seed'ler arası standart sapma.

## 4. Deney tasarımı

### 4.1 Ön kayıt

Her deneyden önce soru, veri, ayar ızgarası, ölçütler, "anlamlı fark" tanımı, karar kuralı ve karışan
etkenler (confounds) yazılıp commit'lendi. Sonuç görüldükten sonra yapılan her değişiklik sapma tablosuna
tarihiyle ve "sonuçlardan sonra" notuyla yazıldı (v2'den sapmalar S1–S9, v3'ten sapmalar T1–T5).

### 4.2 Seçim ve test ayrımı

Ayarlar (öğrenme oranı, λ_s, λ_d) yalnızca doğrulama kümesinde seçildi. Test kümesi her karar için bir kez
kullanıldı. Test koşuları beş seed'le yapıldı ve yama başına seed ortalaması alındı.

### 4.3 Anlamlı fark ve karar kuralları

İki kol X ve Y için yama başına oran `m_X / m_Y` hesaplanır. Fark, oranların geometrik ortalaması ≤ 0.9 ya da
≥ 1/0.9 **ve** eşleştirilmiş Wilcoxon işaretli sıra testinde p < 0.01 ise anlamlıdır.

- **Aşama 0:** A, en az bir birincil ölçütte C'den anlamlı biçimde iyi ve hiçbirinde anlamlı biçimde kötü
  değilse "temsil ekseni canlı", aksi hâlde "zayıf".
- **Aşama 1b:** Önkoşul, H'nin yama başına 𝒢 medyanının τ'nun altında olmasıdır. Önkoşul sağlanırsa H, PA ve
  PC ile Chamfer'da karşılaştırılır. Güçlü: H en az birinden iyi, hiçbirinden kötü değil. Eşdeğer: ikisiyle de
  fark yok. Zayıf: diğer bütün durumlar.

### 4.4 Yeniden üretilebilirlik

Her koşu tek bir commit'e bağlıdır; çalışma ağacı kirliyse koşu başlamaz. Sonuçlar birim birim, atomik olarak
yazılır; kesilen koşu kaldığı yerden sürer ve biten birimleri yeniden hesaplamaz. Tekrar koşulan bütün
kontrollerde (örneğin genişletilmiş lr ızgarasının 3e-2 satırları) değerler birebir aynı çıktı. Projede 42 birim
testi vardır.

## 5. Sonuçlar

### 5.1 Aşama 0: temsil deneyi

Seçilen ayarlar: üç temsilde de lr 3e-2; λ_s A ve B'de 0, C'de 1e-3. Test (200 yama, beş seed):

| Ölçüt | Karşı | Oran A/X | Wilcoxon p | Hüküm |
|---|---|---|---|---|
| Chamfer | B | 1.104 | 2.6e-21 | fark yok |
| yakınsama adımı | B | 0.982 | 0.75 | fark yok |
| seed std | B | 1.274 | 5.8e-5 | A kötü |
| Chamfer | C | 1.342 | 2.1e-13 | A kötü |
| yakınsama adımı | C | 2.213 | 1.6e-32 | A kötü |
| seed std | C | 0.757 | 1.0e-5 | A iyi |

**Karar: temsil ekseni zayıf.** Etki aileye bağlıdır: C genel ve hiperbolik paraboloit ailelerinde, A ve B
koni ve silindirde daha iyidir. Seçilen lr ızgaranın üst sınırında olduğu için keşif amaçlı bir kontrolle
ızgara genişletildi (lr 3e-1'e kadar). Üç temsil de %15–20 iyileşti ama sıralama (C < B < A) ve A/C oranı
(1.34 → 1.33) değişmedi. Bu kontrol test kümesini ikinci kez kullandığı için karar verisi sayılmadı.

### 5.2 Aşama 1a: hazırlık ve iki önemli bulgu

Aşama 1b'den önce katman, ölçüt ve ayar ölçekleri hazırlandı. Bu sırada iki bulgu tasarımı değiştirdi:

1. **Katlanma.** Düzgünlük terimi olmadan (λ_s = 0) optimize edilen yüzeyler doğrular arasında katlanıyordu:
   komşu dörtgenlerin normalleri ters dönüyordu (A0'da %7, H'de %11). Chamfer bunu görmez, 𝒢 büyük değer olarak
   yakalar. Düzgünlük terimi λ_s ≥ 1e-2 yapıldığında katlanma gerçek açılabilir yüzeylerdeki taban düzeyine
   indi; bedeli Chamfer'da A0 için 1.6, H için 2.4 kattır. λ_s ızgarası buna göre değiştirildi (T5). Bu değişiklik
   doğrulama kümesinin 5 yamasındaki tanıdan sonra yapıldı ve öyle kaydedildi.
2. **Geri çekilen bir ölçü.** İlk tanıda kullanılan "orta nokta yön değiştirme oranı" katlanmanın geçerli bir
   ölçüsü çıkmadı: katlanma kaybolurken bu oran artıyordu. Orta nokta doğru boyunca serbestçe kayabildiği için
   yüzeyin şeklini ölçmüyordu. Ölçü ve ona dayanan yorum geri çekildi; bulgu normal dönüşü oranıyla korundu.

### 5.3 Aşama 1b: açılabilirlik deneyi

Doğrulamada seçilen ayarlar:

| Kol | lr | λ_s | λ_d | Doğrulamada ortalama 𝒢 ≤ τ |
|---|---|---|---|---|
| A0 | 0.3 | 1e-2 | – | – |
| PA | 0.03 | 1e-1 | 1e3 | evet |
| PC | 0.03 | 1 | 1e3 | hayır (yedek kural) |
| H | 0.1 | 1e-2 | – | – |

Test, birincil başlangıç (120 yama, beş seed ortalaması):

| Kol | Chamfer | 𝒢 ortalama | 𝒢 medyan | Normal dönüşü | Yama içi kesişme |
|---|---|---|---|---|---|
| A0 | 1.32e-3 | 0.319 | 0.261 | 0.009 | 0.101 |
| PA | 4.81e-3 | 0.0141 | 1.2e-4 | 0.001 | 0.007 |
| PC | 9.19e-3 | 0.0917 | 2.2e-4 | 0.000 | 0.022 |
| H | 2.76e-3 | 1.231 | 1.134 | 0.019 | 0.151 |
| Hrev | 2.63e-3 | 1.245 | 1.103 | 0.019 | 0.154 |

**Karar: zayıf, önkoşul sağlanamadı.** H'nin medyan 𝒢'si τ'nun yaklaşık 150 katıdır. Karar kuralının dışında
kalan karşılaştırmalar raporlanır:

- H, Chamfer'da PA'dan (oran 0.726) ve PC'den (0.368) iyi, A0'dan (2.08) kötüdür; bütün p < 1e-12.
- H'nin 𝒢'si katmansız A0'dan da büyüktür (oran 4.1).
- İkincil başlangıçta (Aşama 0'ın daha gürültülü başlangıcı) karar aynıdır; H'nin medyan 𝒢'si 0.153.
- Ters sıralı katman H'den farklı değildir (Chamfer oranı 0.982, p = 0.51): katmanın yönü sonucu belirlemez.
- Ön kayıttaki "PA ortalamada τ'ya ulaşamaz" beklentisi tutmadı. Bu beklenti tek bir öğrenme oranındaki
  5 yamalık ölçek koşusuna dayanıyordu.

### 5.4 Keşif amaçlı analizler

Aşağıdaki iki analiz sonuçlar görüldükten sonra yapıldı; karar verisi değildir.

**Mekanizma.** H'nin test yamaları, kesişme noktasının yama içine düşüp düşmemesine göre ayrıldı:

| Başlangıç | Kesişme yama dışında | 𝒢 ≤ τ oranı | Kesişme yama içinde | 𝒢 ≤ τ oranı |
|---|---|---|---|---|
| birincil | 51 / 600 | 0.98 | 549 / 600 | 0.01 |
| ikincil | 154 / 600 | 0.95 | 446 / 600 | 0.04 |

Kesişme yamanın dışında kaldığında katman gerçekten açılabilir yüzey üretir (medyan 𝒢 ≈ 1e-11). Sorun,
kesişmenin yamaların büyük çoğunluğunda içeri düşmesidir. Bu, Aşama 1a'daki "garanti yalnız yereldir"
bulgusunun büyük ölçekte doğrulanmasıdır.

**Seçim kuralının etkisi.** H, ön kayda göre yalnız Chamfer'la seçildi ve bu en küçük λ_s'yi seçtirdi. H
doğrulamada hiçbir ayarda ortalama 𝒢 ≤ τ'ya ulaşamadı (en düşük 0.058). PA'daki gibi bir 𝒢 koşuluyla (medyan)
seçilseydi lr 0.03, λ_s 0.1 seçilirdi; doğrulama Chamfer'ı 4.00e-3, PA'nınki 4.38e-3'tür (oran 0.91). Bu, 0.9
eşiğinin hemen üstündedir: seçim kuralı farklı olsaydı da sonucun en iyi hâli "eşdeğer" olurdu.

## 6. Literatür ve yenilik değerlendirmesi

Aşama 1b koşarken, katmanın kapalı biçiminin daha önce yapılıp yapılmadığı tarandı (ayrıntılar `RELATED_WORK.md`).

- **Koşulun kendisi klasiktir:** ardışık doğruların eş düzlemliliği, ayrık açılabilir yüzeyin standart tanımıdır.
- **Geometri işlemede aynı koşul yinelemeli ve noktalar üzerinde zorlanır.** Liu ve diğerleri (2006) düzlemsel
  dörtgen şeritleri optimizasyonla korur. Tang ve diğerleri (2014, 2016) koşulu ikinci dereceden denklemlere
  çevirip kısıt uzayına yönlendirilmiş izdüşümle (guided projection) çözer. Tang ve diğerlerinin (2016) kübik
  determinant biçimi, PC cezasının karesini aldığı niceliktir; yazarlar bu biçimin bir mertebe kötü yakınsadığını
  bildirir. Bu, PC'nin bu projedeki zayıf performansıyla tutarlıdır.
- **Plücker uzayında:** Odehnal (2008) altı-vektörü geçerli bir doğruya çeviren formülü verir (bu projede S1
  düzeltmesinin formülü); onun yöntemi açılabilirliği korumaz.
- **Öğrenmede:** sert kısıt katmanları biliniyor (DC3, 2021; HardNet, 2024). Bu projedeki katman, yön sabitken
  momente göre iki afin kısıta (Plücker ve karşılıklı çarpım) en küçük normlu izdüşümdür, yani bu tür bir afin
  izdüşümün sıralı uygulanmış özel hâlidir. Açılabilirlik öğrenen çalışmalar (NeurCADRecon 2024 ve diğerleri)
  yumuşak eğrilik cezaları kullanır; doğru tahmin eden bir ağ bulunmadı.

Sonuç: katman basit bir yapı olarak tanımlanabilir, kendi başına bir yöntem katkısı değildir.

## 7. Süreçte öğrenilenler

1. **Ön kayıt işe yarar.** İki deneyin sonucu da beklenenden kötü çıktı. Karar kuralı önceden yazıldığı için
   sonuç yorumlanırken kural esnetilmedi. Kuralın kendisinde bir zayıflık görüldüğünde (H'nin yalnız Chamfer'la
   seçilmesi) kural değiştirilmedi; etkisi ayrı ve işaretli bir analizle ölçüldü.
2. **Doğru ölçüt, yanlış görünen sonucu açıklar.** Chamfer katlanmayı görmedi; açı açığı gördü. Bir ölçünün
   geçerliliği, sonucu bilinen durumlarda (gerçek koni, yapay zikzak) sınanmadan kullanılmamalıdır; sınanmayan
   bir ölçü bu projede geri çekilmek zorunda kalındı.
3. **Ortalama ve medyan farklı şeyler söyler.** 𝒢 dağılımı birkaç uç yamanın baskın olduğu çarpık bir dağılımdır.
   Seçim kuralında ortalama, önkoşulda medyan kullanılması sonuçları etkiledi; bu tür seçimler baştan
   gerekçelendirilmelidir.
4. **Garantinin kapsamı açık yazılmalıdır.** "Her şerit düzlemsel" ile "yüzey açılabilir" aynı şey değildir. Bu
   fark birim testi sırasında bulundu ve sonunda deneyin sonucunu belirledi.
5. **Hatalar erken yakalandığında ucuzdur.** Dual normalizasyondaki eksik çarpan, arayüzdeki bir kalıtım hatası
   ve geçersiz bir ölçü, karar koşularından önce bulundu.
6. **Uzun koşular kesintiye dayanıklı olmalıdır.** İki aşamada da koşu bellek yetersizliği ya da uyku nedeniyle
   kesildi; sonuçlar etkilenmedi, çünkü koşular commit'e bağlı ve kaldığı yerden sürdürülebilirdi.

## 8. Sınırlılıklar

- Deneyler ağsızdır. Olumsuz sonuçlar, bir ağın içinde fark olmayacağını kanıtlamaz; yalnız bu soruların öncelikli
  yatırım olmadığını gösterir.
- Veri sentetiktir; tek gürültü düzeyi (%1), K = 32 ve beş seed kullanıldı.
- Aşama 0'da "temsil", çıktı koordinatları, ara değer şeması ve düzgünlük teriminin değişkenlerinden oluşan bir
  pakettir; bileşenler ayrılmadı.
- λ_s ve λ_d ızgaraları, doğrulama kümesinin 5 yamasındaki tanıdan sonra sabitlendi (T5). Test kümesine dokunulmadı,
  ama ızgara tamamen sonuçlardan bağımsız değildir.
- Aşama 0'da λ_s yalnız Chamfer'a göre seçildi; o yüzeylerin de katlanmış olması olasıdır. Aşama 0 bulgusu
  "nokta uydurma doğruluğu" ile sınırlı okunmalıdır.

## 9. Olası devam yönleri

Proje burada kapatıldı. Soru yeniden açılırsa en doğrudan yön, katmanın başarısız olduğu durumu hedeflemektir:
**kesişme noktasını yamanın dışında tutan** bir kısıt ya da parametreleme. Örneğin kesişme noktası açıkça bir
değişken olarak tutulup yama aralığının dışına itilebilir ya da açılabilir yüzey doğrudan gerileme eğrisiyle
(teğet açılabilir için) parametrelenebilir. İkinci yön, katmanı yumuşak cezayla birleştirmektir: PA'nın
açılabilirliği ile H'nin uydurma doğruluğu arasındaki ödünleşimi bir arada aramak. İkisi de ayrı bir proje
ölçeğindedir.

## 10. Yeniden üretim

| Adım | Commit | Komut | Özet |
|---|---|---|---|
| Aşama 0 | `e96bef1` | `python experiments/phase0.py` | `results_summary/phase0/` |
| Aşama 0 lr kontrolü | `88ea95e` | `python experiments/phase0_lrext.py` | `results_summary/phase0_lrext/` |
| Aşama 1a tanıları | `3084de4`, `43f4485` | `python experiments/phase1.py smooth` / `scale2` | `results_summary/phase1_smooth/`, `phase1_scale_ls0.1/` |
| Aşama 1b | `ca3da26` | `python experiments/phase1.py all` ve `python experiments/phase1_analyze.py` | `results_summary/phase1/` |

Tam sonuçlar `results/archives/` altında zip olarak arşivlenmiştir. Ayrıntılı günlük `PROGRESS.md`'de, tasarım
`docs/tarif_v3.md`'de, terimler `GLOSSARY.md`'de, kaynaklar `RELATED_WORK.md`'dedir.

## Kaynaklar

- Pottmann, H., Wallner, J. *Computational Line Geometry.* Springer, 2001.
- Pottmann, H., Wallner, J. Approximation algorithms for developable surfaces. *Computer Aided Geometric Design*
  16:539–556, 1999.
- Odehnal, B. Subdivision algorithms for ruled surfaces. *Journal for Geometry and Graphics* 12(1):1–18, 2008.
- Liu, Y., Pottmann, H., Wallner, J., Yang, Y.-L., Wang, W. Geometric modeling with conical meshes and developable
  surfaces. *ACM Transactions on Graphics* 25(3):681–689, 2006.
- Tang, C., Sun, X., Gomes, A., Wallner, J., Pottmann, H. Form-finding with polyhedral meshes made simple. *ACM
  Transactions on Graphics* 33(4), 2014.
- Tang, C., Bo, P., Wallner, J., Pottmann, H. Interactive design of developable surfaces. *ACM Transactions on
  Graphics* 35(2), article 12, 2016.
- Stein, O., Grinspun, E., Crane, K. Developability of triangle meshes. *ACM Transactions on Graphics* 37(4), 2018.
- Dong, Q. ve diğerleri. NeurCADRecon: neural representation for reconstructing CAD surfaces by enforcing zero
  Gaussian curvature. *ACM Transactions on Graphics* 43(4), 2024.
- Donti, P. L., Rolnick, D., Kolter, J. Z. DC3: a learning method for optimization with hard constraints. *ICLR*, 2021.
- HardNet: hard-constrained neural networks with universal approximation guarantees. arXiv:2410.10807, 2024.
- Zhou, Y., Barnes, C., Lu, J., Yang, J., Li, H. On the continuity of rotation representations in neural networks.
  *CVPR*, 2019.
