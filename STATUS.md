# Deva Alüminyum — Proje Durumu

Son güncelleme: 2026-09-21

## Kurtarma

- Temmuz 2025 ana snapshot: doğrulandı
- Ocak 2025 fallback snapshotları: doğrulandı
- Kritik sayfalar: 16/16 kurtarıldı
- Referans galerisi: 23/23 büyük görsel + 23/23 thumbnail kurtarıldı
- Production için seçilen medya:
  - 1 orijinal logo
  - 5 adet 1920x1080 hero görseli
  - 23 adet tam boy referans görseli
- Eski URL yapısı envantere alındı
- Eski gizli keyword stuffing yeni siteye taşınmadı
- Dış sitelerden hotlink edilmiş alakasız materyal production'a taşınmadı

## Yeni site

- Statik build: `python scripts/build_site.py`
- Çıktı: `dist/`
- Toplam HTML route: 17
- Mobil menü: hazır
- Referans galerisi: hazır
- Hakkımızda: hazır
- İletişim: hazır
- 12 hizmet sayfası: hazır
- 404: hazır
- robots.txt: hazır
- sitemap.xml: hazır
- Cloudflare Pages `_redirects`: hazır

## SEO / GEO / AEO

- Canonical: hazır
- Meta title/description: hazır
- Open Graph: hazır
- Twitter card: hazır
- LocalBusiness JSON-LD: hazır
- Service JSON-LD: hazır
- FAQPage JSON-LD: hazır
- Eski URL -> yeni URL eşlemeleri: hazır
- QA: 0 issue

## Görsel QA

Son production paketi:
- A kalite: 5
- C kalite: 18
- D kalite: 3
- E otomatik sınıf: 3
- E sınıfındakilerin biri 258x157 arşiv logosu, diğerleri dikey oran nedeniyle otomatik sınıflandırmada düşük görünür.
- 150x150 kullanılmayan eski thumbnaillar production paketinden çıkarıldı.

## Final yayından önce teyit edilecek bilgiler

Temmuz 2025 arşivinde doğrulanan fakat güncelliği işletmeden son kez teyit edilecek:

- Telefon: 0 533 382 07 05
- E-posta: murat.kozza@gmail.com
- Adres: Eski Sanayi Mahallesi 6025. Sokak No: 5/B Kocasinan / Kayseri
- Facebook hesabı
- Google Business Profile konumu / web adresi

## Domain geldiğinde

- `devaaluminyum.com.tr` Cloudflare'e eklenir
- Cloudflare Pages repo: `teyfikgokdemir/devaaluminyum`
- Branch: `main`
- Build command: `python scripts/build_site.py`
- Output: `dist`
- Preview QA sonrası custom domain bağlanır
- Search Console + Bing Webmaster + sitemap gönderimi yapılır
- Google Business Profile web adresi güncellenir
