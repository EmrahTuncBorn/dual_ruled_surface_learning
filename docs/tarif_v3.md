# Dual Küresel Eğrilerle Regle Yüzey Öğrenme — Sürüm 3

**Sert açılabilirlik katmanı: pilot tasarımı ve uygulama tarifi**

11 Ekim 2026 · Sürüm 3 · Önceki sürüm: `Regle_Yuzey_Ogrenme_Pilot_Sistem_Tarifi_v2.docx` (6 Ekim 2026)

---

## 0. Bir bakışta

**v2'nin sorusu.** Çıktı doğruları dual birim vektör olarak yazıldığında öğrenme, alışılmış iki temsile
(dayanak+yön, iki uç nokta) göre ölçülebilir biçimde iyileşir mi?

**Aşama 0'ın yanıtı.** Ağsız deneyde hayır (Bölüm 2). Dual temsil (A), iki uç nokta temsiline (C) göre
Chamfer hatasında anlamlı biçimde kötü çıktı; genişletilmiş lr ızgarasında da sıralama değişmedi.
Ön kayıtlı kurala göre temsil ekseni zayıftır.

**v3'ün sorusu.** Dual dil çıktı koordinatı olarak bir üstünlük sağlamıyor; ancak bir yerde yapısal bir
fark yaratır: ardışık iki doğrunun kesişme koşulu, yani açılabilirlik (developability), Plücker
koordinatlarında bir sonraki doğrunun momentinde **doğrusaldır**. Bu yüzden açılabilirlik, ceza terimiyle
yaklaşık olarak değil, kapalı biçimli ve türevlenebilir bir izdüşümle **tam olarak** zorlanabilir.
v3'ün sınadığı soru şudur:

> Açılabilir veride, açılabilirliği dual koordinatlarda sert bir katmanla zorlamak, aynı açılabilirlik
> düzeyine ceza terimiyle ulaşan yöntemlere göre uydurma doğruluğundan ne kadar ödün verir?

Yanıt bilinmiyor. Sert katman ödün vermiyorsa katkı, ayar gerektirmeyen bir yapısal garantidir;
belirgin ödün veriyorsa katman bırakılır ve katkı, Aşama 0'ın yöntemsel bulgularıyla sınırlı kalır.

**Değişmeyenler.** v2'nin 1–4. bölümlerindeki matematik (Study dönüşümü, dual birim küre, değişmezler,
veri üreteci), 6. bölümdeki kısıt katmanı (S1 düzeltmesiyle), 7. bölümdeki yüzey kurulumu ve 14.7'deki
sağlama testleri geçerlidir; burada tekrar edilmez.

---

## 1. v2'den v3'e değişenler

| # | Değişiklik | Gerekçe |
|---|---|---|
| D1 | Ana soru, temsil karşılaştırmasından sert açılabilirlik katmanına kaydırıldı. | Aşama 0: temsil ekseni zayıf (Bölüm 2). |
| D2 | v2'nin 1. deneyi (beş ailede ağlı temsil karşılaştırması) kaldırıldı. Aşama 0 sonucu, olumsuz bulgu olarak raporlanır. | Ağsız deneyde fark C lehine; ağlı sürümün maliyeti, beklenen bilgi değerine göre yüksek. |
| D3 | Birincil açılabilirlik ölçütü, ayrık toplam mutlak Gauss eğriliğidir (Bölüm 4). `d·sinθ` ve drall yalnızca ikincil olarak raporlanır. | `d·sinθ` dönme açısına bağlıdır (S3, Aşama 0'da gözlendi); drall silindirde tanımsızdır. |
| D4 | "Anlamlı fark" tanımı Aşama 0'daki kuraldır: yama başına oranların geometrik ortalaması ≤ 0,9 ya da ≥ 1/0,9 **ve** eşleştirilmiş Wilcoxon p < 0,01. | v2'deki birleşik standart sapma kuralı, eşleştirilmiş tasarımı kullanmaz (S4). |
| D5 | Yakınsama hızı birincil ölçüt değildir. | Aşama 0 ek kontrolünde lr'ye güçlü biçimde bağlı çıktı; farklı lr'lerle ayarlanan yöntemlerde temsil etkisini ayırmaz. |
| D6 | Önce ağsız deney yapılır; ağ yalnızca ağsız deney olumlu çıkarsa kurulur. | Aşama 0'ın ucuz ve ayırt edici olduğu görüldü. |
| D7 | Kısıt katmanında sıfıra bölme koruması `max(‖a‖, 1e-12)` biçimindedir. | S8. |

---

## 2. Aşama 0'ın özeti

Ayrıntılar `PROGRESS.md`'dedir; burada yalnızca v3'ün dayandığı bulgular verilir.

- **Kurulum.** Ağ yoktur; her yama için 32 doğru, aynı başlangıç yüzeyinden doğrudan optimize edildi.
  Beş aile, %1 gürültü, 200 test yaması, beş seed (rastgelelik tohumu). Ayarlar yalnızca doğrulama
  kümesinde seçildi.
- **Birincil sonuç.** A/C oranlarının geometrik ortalaması: Chamfer 1,34; yakınsama adımı 2,21
  (ikisi de A aleyhine, p < 1e-12); seed std 0,76 (A lehine). Karar: temsil ekseni zayıf.
- **Ek kontrol (keşif amaçlı).** Seçilen lr ızgaranın sınırındaydı. Izgara genişletildi; üç temsil de
  %15–20 iyileşti, sıralama değişmedi (C < B < A), A/C Chamfer oranı 1,33.
- **Aileye bağlılık.** C genel ve hiperbolik paraboloit ailelerinde; A ve B koni ve silindirde daha iyi.
- **Açılabilirlik.** Hiçbir temsil açılabilirliği kendiliğinden öğrenmedi. C'de `d·sinθ` bir mertebe
  küçük, drall ise büyük çıktı: `d·sinθ`'nın küçüklüğü açılabilirlikten değil, küçük dönme açısından gelir.

---

## 3. Sert açılabilirlik katmanı

### 3.1 Sezgi

Regle yüzey açılabilirse komşu doğrular kesişir (ya da paraleldir). Ayrık durumda bu, ardışık her doğru
çiftinin aynı düzlemde olmasıdır; yüzey düzlemsel şeritlerden oluşur. Ağ ya da optimizasyon serbest
doğrular önerir; katman her doğruyu, bir öncekiyle kesişecek biçimde en az miktarda kaydırır.
Kaydırma yalnızca momentte yapılır, yön değişmez.

### 3.2 Matematik

Doğru $i$ için $(a_i, m_i)$, $\|a_i\| = 1$, $\langle a_i, m_i\rangle = 0$. Bir sonraki doğrunun yönü $a$
ve kısıt katmanından çıkmış momenti $m_0$ olsun ($\langle a, m_0\rangle = 0$). İki doğrunun aynı düzlemde
olması karşılıklı momentin (reciprocal product) sıfırlanmasıdır:

$$
\langle a_i, m\rangle + \langle a, m_i\rangle = 0 .
$$

Bu koşul, $a$ sabitken $m$'de **doğrusaldır**. Plücker koşuluyla birlikte $m$ için iki doğrusal koşul
vardır. $n = a_i - \langle a_i, a\rangle a$ ($\|n\| = \sin\theta$) ve $r = \langle a_i, m_0\rangle + \langle a, m_i\rangle$
ile, iki koşulu sağlayan ve $m_0$'a en yakın moment kapalı biçimde bulunur:

$$
m = m_0 - \frac{r}{\|n\|^2}\, n .
$$

Özellikler (sayısal olarak sınandı, 1000 rastgele çiftte hata < 5e-15):

1. $\langle a, m\rangle = 0$ ve karşılıklı moment sıfırdır.
2. Düzeltmenin büyüklüğü $\|m - m_0\|$, ham doğrunun önceki doğruya **en kısa uzaklığına** eşittir:
   $|r| / \sin\theta = d_0$. Katman, her doğruyu tam olarak gereken kadar kaydırır.
3. İşaret değişimine duyarsızdır: $(a_i, m_i) \to -(a_i, m_i)$ ya da $(a, m_0) \to -(a, m_0)$ aynı doğruyu verir.

Katman sıralıdır: doğru 0 serbesttir; $k = 1, \dots, K-1$ için doğru $k$, **düzeltilmiş** doğru $k-1$'e
göre izdüşürülür. Yön değişkenleri ve yama aralığı katmandan etkilenmez.

**Kesişen doğruların ara değeri.** Kesişen iki doğrunun Plücker koordinatlarının doğrusal birleşimi,
Plücker koşulunu kendiliğinden sağlar:

$$
\langle (1-w)a_1 + w a_2,\ (1-w)m_1 + w m_2\rangle = w(1-w)\big(\langle a_1, m_2\rangle + \langle a_2, m_1\rangle\big) = 0 .
$$

Ortaya çıkan doğru, iki doğrunun belirlediği demete (pencil) aittir: aynı düzlemde ve aynı noktadan geçer
(sayısal sınama: hata < 3e-14). Dolayısıyla A'nın ara değer şeması (v2 Bölüm 7, S1), sert katmandan
geçmiş doğrular arasında **tam düzlemsel şeritler** üretir: yüzey, ara adımlar dahil, ayrık anlamda tam
açılabilirdir. Bu özellik B ve C'nin ara değer şemalarında kendiliğinden yoktur.

### 3.3 Paralel doğrular ve düzenlileştirme

$\sin\theta \to 0$ iken düzeltme sınırlıdır ($d_0$), ama yönü süreksizdir: tam paralel doğrular zaten aynı
düzlemdedir ve düzeltme gerekmez, oysa küçük bir açıyla kaymış doğrular $d_0$ kadar kaydırılır. Silindir
verisinde bu, doğru aralığı mertebesinde sıçramalara yol açabilir. Bu nedenle payda alttan kırpılır:

$$
m = m_0 - \frac{r}{\max(\sin^2\theta,\ \varepsilon^2)}\, n ,\qquad \varepsilon = 10^{-3}\ \text{(öneri)} .
$$

$\sin\theta \ge \varepsilon$ için katman tamdır; düzeltme $\sin\theta$'nın sürekli bir fonksiyonudur ve
$\sin\theta \to 0$ iken sıfıra iner. (İlk taslaktaki $\sin^2\theta + \varepsilon^2$ biçimi büyük açılarda da
$\varepsilon^2/\sin^2\theta$ oranında kaçak bıraktığı için Aşama 1a'da bu biçimle değiştirildi.)
$\sin\theta < \varepsilon$ olan çiftler yalnızca kısmen düzeltilir;
bir şeridin Gauss tasviri (Gauss image) alanı, anadoğru tam boyunda alınsa bile açısı $\theta$ olan bir
küresel ay (lune) ile, yani $2\theta$ ile sınırlı olduğu için, bunun açılabilirlik ölçütüne katkısı şerit
başına en çok $2\varepsilon$ mertebesindedir. $\varepsilon$ değeri ve gradyanın
$\theta \approx \varepsilon$ çevresindeki davranışı, Aşama 1a'daki testlerle denetlenir.

### 3.4 Gerileme kenarı yamanın içine düşebilir (Aşama 1a bulgusu)

Katmanın garantisi **yereldir**: her şerit düzlemseldir (rastgele doğrularda dörtgen düzlemsizliği
< 2e-14). Ama ardışık iki doğrunun kesişme noktası, yani ayrık gerileme kenarı (edge of regression),
yama aralığının içine düşerse şerit kendini keser (papyon biçimi); yüzey o noktada tekildir ve
$\mathcal{G}$ bunu büyük bir değer olarak yakalar. Bu, açılabilir yüzeylerin doğasında olan bir
tekilliktir; katmanın bir hatası değildir, ama "tam açılabilirlik garantisi" ancak kesişme noktaları
yamanın dışında kaldığında geçerlidir.

Kesişme noktasının konumu kötü koşulludur: ardışık açısı $\theta$ olan doğrularda $\delta$ büyüklüğündeki
bir konum hatası, kesişme noktasını yaklaşık $\delta/\theta$ kadar kaydırır. Sayısal örnekler:

- Koni doğruları ($\theta \approx 0{,}047$), konumda $10^{-3}$ gürültü: kesişmelerin %0'ı aralık içinde,
  $\mathcal{G} = 4\cdot 10^{-12}$. Gürültü $10^{-2}$: kesişmelerin %21'i aralık içinde, $\mathcal{G}$ en çok 0,79.
- Aşama 0'ın başlangıcı (doğru başına bağımsız σ = 0,1 rad bozulma), açılabilir yamalarda: sert katmandan
  sonra kesişmelerin %57–67'si aralık içinde; başlangıç $\mathcal{G}$'si 6,3–9,5 (A'nın başlangıcında da
  6,3–9,5).

Sonuçları: (i) Aşama 1b'de "aralık içindeki kesişme oranı" H için ikincil ölçüt olarak raporlanır;
(ii) başlangıç yüzeyinin seçimi H için belirleyicidir (Bölüm 5.2).

### 3.5 Geometrik yorum

Sert katman, v2'deki kısıt katmanının açılabilir yüzeyler için uzantısıdır. Kısıt katmanı ham sayıları
dual birim küreye indirir; sert katman, dual küresel eğriyi $\mathrm{Du}\langle A', A'\rangle = 0$ koşulunun
ayrık karşılığını sağlayan eğrilere indirir. Koşul A koordinatlarında doğrusal, B'de kübik, C'de dört
noktanın eşdüzlemliliği olarak kübiktir (v2 Bölüm 9); kapalı biçimli izdüşüm yalnızca A'da vardır.
Aşama 0'da A'nın yenildiği uydurma doğruluğu bakımından değil, bu yapısal özellik bakımından
dual dil ayırt edicidir.

**Yenilik için dürüst not.** "Ardışık anadoğrular kesişir" koşulu, ayrık açılabilir yüzeylerin klasik
tanımıdır (düzlemsel dörtgen şeritler; Liu ve ark. 2006, Tang ve ark. 2016, Stein–Grinspun–Crane 2018).
Olası yenilik, bu koşulun Plücker koordinatlarında kapalı biçimli, türevlenebilir bir öğrenme katmanı
olarak kullanılmasıdır. Literatürdeki durumu doğrulanmamıştır (Bölüm 9).

---

## 4. Açılabilirlik ölçütü

### 4.1 Neden yeni bir ölçüt

- `d·sinθ` (v2'nin ölçütü) aynı yüzeyde doğru sayısı arttıkça $O(1/K^2)$ küçülür; daha küçük dönme açılı
  bir çözüm, açılabilir olmadan küçük değer alır (Aşama 0'da C'de gözlendi).
- Drall $d/\theta$ ölçekten bağımsızdır, ama silindirde $0/0$'dır ve silindire yakın tahminlerde kötü
  koşulludur.

### 4.2 Tanım

Tahmin edilen yüzey, değerlendirme ızgarasında (ardışık doğrular arasında $S = 8$ ara adım, doğru başına
$U = 64$ nokta) üçgen ağa çevrilir. Birincil açılabilirlik ölçütü, ayrık toplam mutlak Gauss eğriliğidir:

$$
\mathcal{G} = \sum_{v\ \in\ \text{iç köşeler}} \Big|\, 2\pi - \sum_{\text{v'deki üçgenler}} \alpha \,\Big| .
$$

Burada $\alpha$, köşedeki üçgen açılarıdır (açı açığı, angle defect). Ölçüt boyutsuzdur, ölçek ve dönmeden
bağımsızdır, silindirde tanımlıdır ve ızgara inceldikçe $\int |K|\, dA$'ya, yani Gauss tasvirinin alanına
yakınsar. Regle yüzeylerde $K \le 0$ olduğundan sürekli durumda işaret iptali yoktur.

**Eşik.** "Pratikte açılabilir" eşiği $\tau$, doğrulama kümesindeki açılabilir olmayan gerçek yamaların
(genel ve hiperbolik paraboloit aileleri, aynı ızgara) $\mathcal{G}$ değerlerinin medyanının %1'idir.
$\tau$, deney koşulmadan önce hesaplanır ve `PROGRESS.md`'ye yazılır.

**İkincil ölçütler.** Ortalama $|d\sin\theta|$ ve drall (yalnızca $\theta > 10^{-3}$ olan çiftlerde),
aile bazında.

---

## 5. Aşama 1: ağsız açılabilirlik deneyi

### 5.1 Veri

v2 Bölüm 14.3'teki üreteç; yalnızca açılabilir aileler (silindir, koni, teğet açılabilir). Aşama 0'ın
veri kümeleri kullanılmaz: Aşama 0'ın test kümesi iki kez kullanıldı. Yeni veri seed'leri: doğrulama
3000 (aile başına 10, toplam 30 yama), test 4000 (aile başına 40, toplam 120 yama). Yama başına 1024
nokta, %1 gürültü, rastgele dönme, v2 normalizasyonu. $\tau$ için ayrıca genel ve hiperbolik paraboloit
ailelerinden doğrulama seed'i 3000 ile aile başına 10 gerçek yama üretilir.

### 5.2 Kollar (arms)

Bütün kollar aynı başlangıç doğrularından, Adam ve kosinüs azalmasıyla 1000 adım optimize edilir.
Kayıp `L_CD + λ_s L_s (+ λ_d L_d)`. H'nin başlangıç yüzeyi, aynı başlangıç doğrularının katmandan geçmiş
hâlidir.

**Başlangıç (açık karar, Aşama 1b ön kaydından önce verilir).** Aşama 0'daki doğru başına bağımsız bozulma
(σ = 0,1 rad), H'de kesişmelerin %57–67'sini yamanın içine düşürür (Bölüm 3.4). Seçenekler:
(i) Aşama 0 başlangıcı, Aşama 0 ile tutarlıdır ama H'yi tekil bir yüzeyden başlatır;
(ii) düşük frekanslı bozulma (doğru indisine göre düzgün, örneğin birkaç sinüs bileşeni), bir ağın düzgün
çıktısına daha yakındır. Hangisi seçilirse seçilsin bütün kollara aynı biçimde uygulanır ve seçim, kolların
karşılaştırması görülmeden yapılır.

| Kol | Temsil | Açılabilirlik | Rolü |
|---|---|---|---|
| A0 | A | yok | başvuru (Aşama 0 koşulu) |
| PA | A | ceza: $L_d^A = \sum_k r_k^2$, $r_k$ ardışık doğruların karşılıklı momenti | sert katmanın tek değişkenli karşılığı |
| PC | C | ceza: $L_d^C = \sum_k V_k^2$, $V_k = \det(p_1 - p_0,\ q_0 - p_0,\ q_1 - p_0)$ | Aşama 0'ın en iyi uydurma temsili |
| H | A | sert katman (Bölüm 3) | sınanan yöntem |

**Karşılaştırmaların anlamı.**
- **H–PA** tek değişkenlidir: koordinatlar, ara değer şeması ve `L_s` aynı; yalnızca açılabilirliğin
  zorlanma biçimi değişir.
- **H–PC** pratik karşılaştırmadır. Koordinatlar, ara değer şeması, `L_s` değişkenleri ve ceza biçimi
  birlikte değişir; bu karışan etkenler (confound) açıkça not edilir.

### 5.3 Ayar (yalnızca doğrulama kümesinde, seed 0)

- `lr ∈ {3e-2, 1e-1, 3e-1}` × `λ_s ∈ {0, 1e-3}`; PA ve PC'de ayrıca `λ_d ∈ {1, 10, 1e2, 1e3, 1e4}` (öneri).
- PA ve PC için: her (lr, λ_s) çiftinde, ortalama doğrulama $\mathcal{G}$'si $\tau$'nun altına inen
  **en küçük** `λ_d` alınır; bu yapılandırmalar arasından ortalama doğrulama Chamfer'ı en düşük olan seçilir.
  Hiçbir `λ_d` eşiğe inmiyorsa ortalama $\mathcal{G}$'si en düşük yapılandırma seçilir ve bu durum raporlanır.
- A0 ve H için: ortalama doğrulama Chamfer'ı en düşük (lr, λ_s).
- Seçilen değer bir ızgara sınırındaysa raporlanır; ızgara, sonuç görüldükten sonra genişletilmez.
- `λ_d` ızgarası, koşudan önce doğrulama kümesinin 5 yamasında kısa bir ölçek koşusuyla denetlenir;
  değişirse koşudan önce `PROGRESS.md`'ye yazılır.
- $\tau = 0{,}00756$ (Aşama 1a'da hesaplandı: 20 açılabilir olmayan gerçek yamanın medyan
  $\mathcal{G}$'si 0,756; betik `experiments/phase1_tau.py`).

Doğrulama birimi: 3 lr × 2 λ_s × (1 + 1 + 5 + 5) = 72. Test birimi: 4 kol × 5 seed × 3 parça = 60.

### 5.4 Birincil ölçütler (test, yama başına beş seed ortalaması)

1. Son Chamfer hatası (Aşama 0'daki tanım).
2. $\mathcal{G}$ (Bölüm 4.2).

İkincil: seed std, Hausdorff ve 95. yüzdeliği, `d·sinθ`, drall, aile bazında tablolar; H için ardışık
doğruların kesişme noktalarının yama aralığı içinde kalma oranı (Bölüm 3.4).

### 5.5 Karar kuralı (sonuçlardan önce sabit)

"Anlamlı" sözcüğü D4'teki tanımdır. Önkoşul: H'nin medyan $\mathcal{G}$'si $\le \tau$; sağlanmazsa
sonuç "zayıf"tır ve katmanın uygulaması incelenir.

- **Güçlü.** Önkoşul sağlanır; H, Chamfer'da PA ya da PC'den en az birine göre anlamlı biçimde iyi,
  hiçbirine göre anlamlı biçimde kötü değil.
  → Aşama 2 (ağ) yapılır; katkı "ödünsüz ve ayarsız yapısal açılabilirlik" olarak sunulur.
- **Eşdeğer.** Önkoşul sağlanır; H, Chamfer'da ikisine göre de anlamlı fark göstermez.
  → Aşama 2 yapılır; katkı "aynı doğrulukta, `λ_d` ayarı gerektirmeyen tam garanti"dir.
- **Zayıf.** Diğer bütün durumlar.
  → Sert katman bırakılır. Katkı, Aşama 0'ın olumsuz bulgusu ve açılabilirlik ölçütüyle ilgili yöntemsel
  bulgularla sınırlıdır; kısa bir olumsuz sonuç yazısı olarak değerlendirilir.

Ek bilgi (karara girmez): PA ya da PC eşiğe hiçbir `λ_d`'de inemiyorsa bu, H lehine ayrıca raporlanır.
Aile bazında, özellikle silindirde (Bölüm 3.3), H'nin davranışı ayrıca incelenir.

### 5.6 Sınırlar

- Ağsız sonuç, ağ içindeki davranışı kanıtlamaz.
- Sert katman yalnızca açılabilir yüzeyler içindir; karışık veride hangi yamanın açılabilir olduğunu
  bilmek ayrı bir sorundur ve v3'ün kapsamı dışındadır.
- Katman sıralıdır; doğru 0'ın seçimi ve sıranın yönü sonucu etkileyebilir. Ters sıra, ikincil analiz
  olarak raporlanır.

---

## 6. Aşama 2: ağlı pilot (yalnızca "güçlü" ya da "eşdeğer" sonuçtan sonra)

- v2 Bölüm 5, 6 ve 14.4'teki kodlayıcı ve çözücü; yalnızca açılabilir veri (v2'nin 2. deneyi).
- Kollar: H, PA, PC (Aşama 1'de seçilen kollar). Dört gürültü düzeyi ve kısmi örnekleme, v2'deki gibi.
- Koşular Colab L4 üzerinde yapılır. Ayrıntılı tasarım, karar kuralı ve koşu sayısı, Aşama 1
  sonuçlarından sonra ve koşulardan önce `PROGRESS.md`'de ön kayda alınır.

---

## 7. Uygulama tarifi (Aşama 1a)

### 7.1 Kod

- `ruled/reps.py`: `DevelopableDualRep`. `DualRep`'in parametreleri; `lines` çıktısına sıralı sert
  katman uygulanır. Ara değer ve `smooth_vars`, `DualRep` ile aynıdır.
- `ruled/geometry.py`: `project_coplanar(a_prev, m_prev, a, m0, eps)` (Bölüm 3.3) ve
  `angle_defect_total(G)` (Bölüm 4.2).
- `ruled/losses.py`: `developability_A`, `developability_C`.
- `experiments/phase1.py`: Aşama 0 betiğinin yapısı (resumable, commit'e bağlı koşu dizini).

### 7.2 Sağlama testleri (koşudan önce geçmeli)

1. Katmanın çıktısı Plücker koşulunu ve $\theta \gg \varepsilon$ için karşılıklı moment koşulunu makine
   hassasiyetinde sağlar.
2. Düzeltmenin büyüklüğü, ham doğrunun önceki doğruya en kısa uzaklığına eşittir.
3. Koni ve silindir doğruları katmandan değişmeden geçer; teğet açılabilirde değişim $K$ arttıkça
   $O(1/K^2)$ küçülür (tek çiftin hatası $O(1/K^3)$'tür, sıralı katman bunu biriktirir).
4. İşaret değişimi katmanın ürettiği doğruları (doğru olarak) değiştirmez.
5. Sert katmandan geçmiş doğruların A ara değeriyle kurulan yüzeyinde her dörtgen, rastgele doğrularda da
   makine hassasiyetinde düzlemseldir; kesişme noktaları yama dışında kaldığında (bozulmuş koni doğruları)
   $\mathcal{G}$ makine hassasiyetinde sıfırdır.
6. $\mathcal{G}$: silindir ve koni ızgaralarında makine hassasiyetinde sıfır; teğet açılabilirde
   ızgara inceldikçe sıfıra yakınsar.
7. $\mathcal{G}$: hiperbolik paraboloitte, $\int|K|\,dA$'nın sayısal kareleme (quadrature) değerine
   ızgara inceldikçe yakınsar.
8. Gradyan sonludur ve sayısal türevle uyuşur; $\sin\theta \in \{10\varepsilon, 0{,}5\varepsilon, 0{,}1\varepsilon, 0\}$
   için de denetlenir (kırpmanın köşesi $\sin\theta = \varepsilon$'da türev tek yönlüdür).

### 7.3 Bilinen başarısızlık biçimleri

| Belirti | Olası neden | Ne yapılır |
|---|---|---|
| Silindirde H'nin Chamfer'ı yüksek | $\theta \approx \varepsilon$ çevresinde düzeltme sıçraması | $\varepsilon$ testi (7.2/8); aile bazında tablo |
| Hata sıra boyunca birikir | sıralı izdüşüm | ters sıra analizi; doğru 0'ın konumu incelenir |
| PA/PC eşiğe inmez | `λ_d` ızgarası dar | ölçek koşusu (5.3); sonuç görüldükten sonra değiştirilmez |
| H'de gradyan patlaması | $1/\max(\sin^2\theta, \varepsilon^2)$ çarpanı | gradyan kırpma yalnızca bütün kollara birlikte uygulanır |

---

## 8. Aşamalar

Her aşamanın sonunda durulur; sonuç sayılarıyla `PROGRESS.md`'ye yazılır, commit'lenir ve onaya sunulur.

| Aşama | İş | Kabul ölçütü |
|---|---|---|
| 0 | Ağsız temsil deneyi | tamamlandı: temsil ekseni zayıf |
| 1a | Sert katman, $\mathcal{G}$ ölçütü, cezalar, testler | 7.2'deki testler geçer; $\tau$ ve `λ_d` ızgarası `PROGRESS.md`'ye yazılır |
| 1b | Ağsız açılabilirlik deneyi | ön kayıt koşudan önce commit'lenir; 5.5'teki kural uygulanır |
| 2 | Ağlı pilot (koşullu) | ön kayıt Aşama 1b'den sonra yazılır |
| 3 | Yazım | — |

---

## 9. Katkı ve ilgili çalışmalar

**Katkı düzeyleri** (en sağlamdan en iddialıya):

1. **Yöntemsel ve olumsuz bulgu.** Ağsız ortamda dual çıktı koordinatlarının uydurmayı kolaylaştırmadığı;
   `d·sinθ`'nın açılabilirlik ölçütü olarak yanıltıcı olduğu. Aşama 0'dan gelir, kesindir, iddiası mütevazıdır.
2. **Sert açılabilirlik katmanı.** Açılabilirliğin Plücker koordinatlarında doğrusal olmasından doğan,
   kapalı biçimli ve türevlenebilir izdüşüm; A ara değeriyle birlikte tam ayrık açılabilirlik.
   Katmanın doğruluğu kanıtlıdır; maliyeti Aşama 1b'nin sorusudur.
3. **Ağlı öğrenme.** Taranmış veriden doğrudan açılabilir yüzey çıkarma. Aşama 2'ye bağlıdır.

**Katkı olmayan şey.** Yeni bir geometri teoremi çıkmaz; kullanılan bütün özdeşlikler klasiktir.

**Doğrulanacak kaynaklar** (künyeler henüz doğrulanmadı, S7):

- Pottmann & Wallner, *Computational Line Geometry* — Plücker koordinatları, doğru demetleri, karşılıklı moment.
- Liu, Pottmann, Wallner, Yang, Wang 2006, conical meshes — düzlemsel dörtgen ağlar ve ayrık açılabilirlik.
- Tang, Bo, Wallner, Pottmann 2016, interactive design of developable surfaces — açılabilirliğin optimizasyonla zorlanması.
- Stein, Grinspun, Crane 2018, developability of triangle meshes — ayrık açılabilirlik ölçütleri.
- Chen & Pottmann, regle yüzeyle yaklaşım; Pottmann–Hofer–Odehnal–Wallner, çizgi geometrisiyle yeniden yapılandırma.
- Zhou ve ark. 2019, dönme temsillerinin sürekliliği — Aşama 0'ın olumsuz bulgusunun bağlamı.
- v2 Bölüm 13'teki çalışmalar (sinirsel örtük yüzeylerde açılabilirlik; Plücker tabanlı ağlar).

Makale öncesinde özellikle şu sorulur: Plücker koordinatlarında ardışık doğruların kesişme koşulunu
kapalı biçimli bir izdüşümle zorlayan bir yöntem, kinematik ya da mimari geometri literatüründe var mı?

---

## Ek: Yeni terimler

| Türkçe | English |
|---|---|
| sert katman | hard (constraint) layer |
| ceza terimi | penalty term |
| doğru demeti | pencil of lines |
| karşılıklı moment | reciprocal product |
| açı açığı | angle defect |
| Gauss tasviri | Gauss image |
| toplam mutlak eğrilik | total absolute curvature |
| kol | arm (of an experiment) |
| karışan etken | confound |
| sayısal kareleme | numerical quadrature |
