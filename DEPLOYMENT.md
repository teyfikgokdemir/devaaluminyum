# Deva Alüminyum — Cloudflare Pages Yayın Ayarları

## Production

- Hedef domain: `devaaluminyum.com.tr`
- GitHub repo: `teyfikgokdemir/devaaluminyum`
- Branch: `main`
- Framework preset: None / Static HTML
- Build command: `python scripts/build_site.py`
- Build output directory: `dist`
- Root directory: repository root

## Domain alındığında

1. Domain Cloudflare hesabına eklenir.
2. Pages projesi bu repo / `main` branch ile bağlanır.
3. Yukarıdaki build ayarları girilir.
4. Önce Cloudflare preview domaininde QA yapılır.
5. Sonra `devaaluminyum.com.tr` custom domain olarak bağlanır.
6. SSL aktif olduktan sonra canonical/sitemap doğrulanır.
7. Google Search Console ve Bing Webmaster'a yeni domain eklenir.
8. Sitemap: `https://devaaluminyum.com.tr/sitemap.xml`
9. Google Business Profile web adresi final teyitten sonra yeni domaine çevrilir.

## Yayın öncesi zorunlu teyit

Temmuz 2025 arşivinde görünen aşağıdaki bilgiler final yayından hemen önce işletmeden doğrulanmalıdır:

- Telefon: 0 533 382 07 05
- E-posta: murat.kozza@gmail.com
- Adres: Eski Sanayi Mahallesi 6025. Sokak No: 5/B Kocasinan / Kayseri
- Facebook hesabı
- Google Business Profile adresi

## SEO migration notu

Eski `devaaluminyum.com` kontrolümüzde olmadığı için eski domainden 301 verilemez. Yeni sitede eski path'ler `_redirects` ile modern karşılıklarına eşlenmiştir; bu eşleme yeni domain üzerindeki eski-path taleplerini korur, ancak eski domainin backlink/PageRank değerini tek başına transfer etmez.
