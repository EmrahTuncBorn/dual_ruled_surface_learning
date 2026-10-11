# Terimler sözlüğü ve yazım kuralları

## Yazım kuralları

- **Ondalık ayırıcı nokta:** `8.22e-4`, `1.104`, `p < 0.01`, `σ = 0.1`. Bu kural `PROGRESS.md`, `docs/tarif_v3.md`
  ve rapor çıktılarında geçerlidir (2026-10-11'de karara bağlandı). v2 belgesi değiştirilmez.
- **Binlik ayırıcı boşluk:** `20 719 sn`, `16 000 yama`. Nokta binlik ayırıcı olarak kullanılmaz.
- **Yüzde işareti sayıdan önce:** `%1`, `%15–20`.
- **Formül gösterimi:** tasarım belgesinde (`docs/tarif_v3.md`) LaTeX (`$\sin\theta$`); günlükte ve ön kayıtlarda
  (`PROGRESS.md`) Unicode (`sinθ`, `‖a‖`, `λ_s`). Bu ayrım bilinçlidir: belge matematiksel metin, günlük düz metindir.
- **Terim kuralı:** yerleşik Türkçe terim kullanılır, ilk geçişte İngilizcesi parantez içinde verilir. epoch, batch,
  seed, checkpoint, baseline ve smoke test İngilizce kalır; ilk geçişte Türkçe anlamı verilir. Kod adları ve
  dosya yolları çevrilmez.
- **Dil:** kod, docstring, `README.md`, `RELATED_WORK.md` İngilizce; `PROGRESS.md`, `GLOSSARY.md`, tasarım
  belgeleri ve şekil açıklamaları Türkçe ve edilgen çatıyla yazılır.

## Geometri

| Türkçe | English | Not |
|---|---|---|
| regle yüzey | ruled surface | |
| anadoğru | ruling | |
| açılabilir yüzey | developable surface | Gauss eğriliği sıfır |
| açılabilirlik | developability | |
| dayanak eğrisi | base curve (directrix) | |
| boğaz noktası / boğaz çizgisi | striction point / striction curve | |
| dağılma parametresi | distribution parameter (drall) | δ = ⟨a′, a*′⟩ / ‖a′‖² |
| gerileme kenarı | edge of regression | teğet açılabilirde dayanak eğrisi; ayrık durumda ardışık doğruların kesişme noktaları |
| moment vektörü | moment vector | a* = c × a |
| Plücker koordinatları | Plücker coordinates | (a, a*) |
| dual birim küre | dual unit sphere | |
| dual normalizasyon | dual normalisation | A/‖A‖ (S1) |
| teğet demet | tangent bundle | |
| doğru demeti | pencil of lines | bir düzlemde, bir noktadan geçen doğrular |
| karşılıklı moment | reciprocal product | ⟨a₁, a₂*⟩ + ⟨a₂, a₁*⟩ = −d sinθ |
| vida adımı | pitch (of a screw) | |
| açı açığı | angle defect | 2π − köşedeki açılar toplamı |
| Gauss tasviri | Gauss image | |
| toplam mutlak eğrilik | total absolute curvature | ∫\|K\| dA; v3 ölçütü 𝒢 |
| küresel ay | spherical lune | |
| sayısal kareleme | numerical quadrature | |
| asli eğrilik | principal curvature | |
| geri çekme | retraction | |

## Yöntem ve deney

| Türkçe | English | Not |
|---|---|---|
| kısıt katmanı | constraint layer | ham sayıları dual birim küreye indirir |
| sert katman | hard (constraint) layer | açılabilirliği izdüşümle tam zorlar (v3) |
| ceza terimi | penalty term | |
| temsil | representation | A dual, B dayanak+yön, C iki uç nokta, H sert katmanlı A |
| işaret hizalama | sign alignment | |
| ara değer | interpolation | |
| kodlayıcı / çözücü | encoder / decoder | |
| kayıp fonksiyonu | loss function | |
| nokta bulutu | point cloud | |
| öğrenme oranı | learning rate (lr) | |
| kosinüs azalması | cosine decay | |
| yakınsama | convergence | |
| ızgara | grid | ayar ızgarası ya da değerlendirme ızgarası |
| doğrulama kümesi | validation set | ayar seçimi yalnız burada |
| test kümesi | test set | bir kez değerlendirilir |
| kol | arm (of an experiment) | Aşama 1'de A0, PA, PC, H |
| birim | unit (of work) | bir temsil, ayar, seed ve parçanın tek koşusu |
| parça | chunk | 50 yamalık grup |
| ön kayıt | pre-registration | sonuçlar görülmeden yazılıp commit'lenen tasarım |
| karışan etken | confound | |
| keşif amaçlı | exploratory | ön kayıt dışı, karara girmez |
| kaldığı yerden sürdürülebilir | resumable | bitmiş birimler atlanır |
| atomik yazım | atomic write | geçici dosya, sonra yeniden adlandırma |
| KD-ağacı | KD-tree | en yakın komşu araması |
| eşleştirilmiş Wilcoxon işaretli sıra testi | paired Wilcoxon signed-rank test | |
| geometrik ortalama oranı | geometric-mean ratio | yama başına oranların |
| birincil / ikincil ölçüt | primary / secondary metric | |
| karar kuralı | decision rule | |
| geç/kal ölçütü | go/no-go criterion | |
| aşırı uydurma | overfitting | |
| reddetme yöntemiyle örnekleme | rejection sampling | |
| alan ağırlıklı örnekleme | area-weighted sampling | |
| seed | seed | rastgelelik tohumu |
| smoke test | smoke test | kısa sağlama koşusu |
| baseline | baseline | karşılaştırma tabanı |
| epoch | epoch | dönem: eğitim verisinin bir tam geçişi |
| checkpoint | checkpoint | denetim noktası: kaydedilmiş model durumu |
| batch | batch | yığın |
