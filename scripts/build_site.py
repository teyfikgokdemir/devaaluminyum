#!/usr/bin/env python3
from pathlib import Path
import html, json, shutil

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
DIST=ROOT/"dist"
DOMAIN="https://devaaluminyum.com.tr"
PHONE="+905333820705"
DISPLAY_PHONE="0 533 382 07 05"
EMAIL="murat.kozza@gmail.com"
ADDRESS="Eski Sanayi Mahallesi 6025. Sokak No: 5/B Kocasinan / Kayseri"

services=[
("aluminyum-kompozit-kaplama","Alüminyum Kompozit Kaplama","Kayseri’de bina cepheleri ve giriş alanları için alüminyum kompozit kaplama uygulamaları.",153),
("bina-giris-kompozit-kaplama","Bina Giriş Kompozit Kaplama","Bina girişlerinde dayanıklı ve düzenli cephe görünümü için kompozit kaplama çözümleri.",167),
("fabrika-yonetim-binasi-kompozit-kaplama","Fabrika Yönetim Binası Kompozit Kaplama","Fabrika yönetim binaları ve ticari yapılarda kompozit cephe uygulamaları.",168),
("aluminyum-dograma","Alüminyum Doğrama","Kayseri’de alüminyum doğrama uygulamaları ve projeye uygun ölçülendirme.",156),
("silikon-cephe-kaplama","Silikon Cephe Kaplama","Ticari ve kurumsal yapılarda silikon cephe sistemleri ve uygulamaları.",157),
("fransiz-balkon-korkuluklari","Fransız Balkon Korkulukları","Fransız balkonlar için alüminyum korkuluk uygulamaları.",171),
("balkon-korkuluklari","Balkon Korkulukları","Balkonlarda alüminyum korkuluk sistemleri ve ölçüye uygun uygulamalar.",170),
("merdiven-korkuluklari","Merdiven Korkulukları","İç ve dış merdivenlerde alüminyum korkuluk uygulamaları.",169),
("bina-giris-kapilari","Bina Giriş Kapıları","Bina girişleri için alüminyum kapı imalatı ve uygulamaları.",162),
("aluminyum-ofis-bolme","Alüminyum Ofis Bölmeleri","Ofis ve iş yerlerinde alüminyum bölme sistemleri.",163),
("fotoselli-otomatik-kapi","Fotoselli Otomatik Kapı Sistemleri","İşletme ve bina girişlerinde fotoselli otomatik kapı sistemleri.",164),
("cam-balkon-sistemleri","Cam Balkon İmalatı ve Montaj","Kayseri’de cam balkon imalatı ve montaj uygulamaları.",158),
]

refs=[
"0-620694757554-37693cfc748049e45d87b8c7d8b9aacd.jpg",
"0-620694757554-3c59dc048e8850243be8079a5c74d079.jpg",
"0-620694757554-b6d767d2f8ed5d21a44b0e5886680cb9.jpg",
"0-648675657737-1679091c5a880faf6fb5e6087eb1b2dc.jpg",
"0-648675657737-45c48cce2e2d7fbdea1afc51c7c6ad26.jpg",
"0-648675657737-8f14e45fceea167a5a36dedd4bea2543.jpg",
"0-648675657737-a87ff679a2f3e71d9181a67b7542122c.jpg",
"0-648675657737-c4ca4238a0b923820dcc509a6f75849b.jpg",
"0-648675657737-c81e728d9d4c2f636f067f89cc14862c.jpg",
"0-648675657737-c9f0f895fb98ab9159f51fd0297e236d.jpg",
"0-648675657737-d3d9446802a44259755d38e6d163e820.jpg",
"0-648675657737-e4da3b7fbbce2345d7772b0674a318d5.jpg",
"0-648675657737-eccbc87e4b5ce2fe28308fd9f2a7baf3.jpg",
"0-761997625541-1f0e3dad99908345f7439f8ffabdffc4.jpg",
"0-761997625541-6512bd43d9caa6e02c990b0a82652dca.jpg",
"0-761997625541-6f4922f45568161a8cdf4ad2299f6d23.jpg",
"0-761997625541-70efdf2ec9b086079795c442636b55fb.jpg",
"0-761997625541-98f13708210194c475687be6106a3b84.jpg",
"0-761997625541-9bf31c7ff062936a96d3c8bd1f8f2ff3.jpg",
"0-761997625541-aab3238922bcc25a6f606eb525ffdc56.jpg",
"0-761997625541-c20ad4d76fe97759aa27a0c99bff6710.jpg",
"0-761997625541-c51ce410c124a10e0db5e4b97fc2af39.jpg",
"0-761997625541-c74d97b01eae257e44aa9d5bade97baf.jpg",
]

hero="aaaaaa6c7857455dcedbfa96584abd609a9dde.68d2f5.jpg"

FAQ_ITEMS=[
("Deva Alüminyum hangi hizmetleri veriyor?","Kompozit cephe kaplama, alüminyum doğrama, silikon cephe, balkon ve merdiven korkulukları, bina giriş kapıları, alüminyum ofis bölmeleri, fotoselli otomatik kapı ve cam balkon uygulamaları."),
("Deva Alüminyum hangi bölgede hizmet veriyor?","Deva Alüminyum'un arşivlenmiş kurumsal kayıtları Kayseri ve Kocasinan merkezli hizmet verdiğini gösteriyor."),
("Teklif almak için nasıl iletişime geçebilirim?","Telefon veya WhatsApp üzerinden proje, ölçü ve uygulama bilgilerini paylaşarak iletişime geçebilirsiniz."),
("Eski Deva Alüminyum referansları yeni sitede yer alacak mı?","Evet. Eski siteden kurtarılan gerçek referans görselleri yeni sitede korunuyor; arşivde bulunmayan müşteri isimleri uydurulmuyor.")
]

BLOGS_PATH=ROOT/"content"/"blogs.json"
BLOGS=json.loads(BLOGS_PATH.read_text(encoding="utf-8")) if BLOGS_PATH.exists() else []

def esc(s): return html.escape(s,quote=True)

def schema(page_name, page_url, service=None, article=None):
    org={
      "@context":"https://schema.org",
      "@type":"LocalBusiness",
      "name":"Deva Alüminyum",
      "url":DOMAIN,
      "telephone":PHONE,
      "email":EMAIL,
      "address":{"@type":"PostalAddress","streetAddress":"Eski Sanayi Mahallesi 6025. Sokak No: 5/B","addressLocality":"Kocasinan","addressRegion":"Kayseri","addressCountry":"TR"},
      "areaServed":{"@type":"City","name":"Kayseri"},
      "sameAs":["https://www.facebook.com/murat.peskirsoy.9"]
    }
    data=[org]
    if page_url==DOMAIN+"/":
      data.append({
        "@context":"https://schema.org",
        "@type":"WebSite",
        "name":"Deva Alüminyum",
        "url":DOMAIN,
        "inLanguage":"tr-TR"
      })
      data.append({
        "@context":"https://schema.org",
        "@type":"FAQPage",
        "mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FAQ_ITEMS]
      })
    else:
      crumbs=[{"@type":"ListItem","position":1,"name":"Anasayfa","item":DOMAIN+"/"}]
      if service:
        crumbs.append({"@type":"ListItem","position":2,"name":"Hizmetler","item":DOMAIN+"/hizmetler/"})
        crumbs.append({"@type":"ListItem","position":3,"name":service,"item":page_url})
      else:
        crumbs.append({"@type":"ListItem","position":2,"name":page_name.split(" | ")[0],"item":page_url})
      data.append({
        "@context":"https://schema.org",
        "@type":"BreadcrumbList",
        "itemListElement":crumbs
      })
    if service:
      data.append({
        "@context":"https://schema.org",
        "@type":"Service",
        "name":service,
        "provider":{"@type":"Organization","name":"Deva Alüminyum","url":DOMAIN},
        "areaServed":{"@type":"City","name":"Kayseri"},
        "url":page_url
      })
    if article:
      data.append({
        "@context":"https://schema.org",
        "@type":"Article",
        "headline":article["title"],
        "description":article["description"],
        "datePublished":"2026-09-21",
        "dateModified":"2026-09-21",
        "inLanguage":"tr-TR",
        "author":{"@type":"Organization","name":"Deva Alüminyum"},
        "publisher":{"@type":"Organization","name":"Deva Alüminyum","url":DOMAIN},
        "mainEntityOfPage":page_url,
        "image":DOMAIN+"/assets/recovered/resimler/"+hero
      })
    return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False,separators=(",",":"))+'</script>'

def shell(title,desc,path,body,service=None,article=None):
    canonical=DOMAIN+path
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#0d0f10">
<meta property="og:locale" content="tr_TR">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:image" content="{DOMAIN}/assets/recovered/resimler/{hero}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="/assets/recovered/Tema/logo.png">
<link rel="stylesheet" href="/assets/styles.css">
{schema(title,canonical,service,article)}
</head>
<body>
<a class="skip-link" href="#main-content">İçeriğe geç</a>
<header class="header"><div class="wrap nav">
<a class="brand" href="/"><img src="/assets/recovered/Tema/logo.png" alt="Deva Alüminyum logo"><span>DEVA ALÜMİNYUM</span></a>
<nav class="menu"><a href="/hizmetler/">Hizmetler</a><a href="/referanslar/">Referanslar</a><a href="/blog/">Blog</a><a href="/hakkimizda/">Hakkımızda</a><a href="/iletisim/">İletişim</a></nav>
<details class="mobile-nav"><summary>Menü</summary><div class="mobile-nav-panel"><a href="/hizmetler/">Hizmetler</a><a href="/referanslar/">Referanslar</a><a href="/blog/">Blog</a><a href="/hakkimizda/">Hakkımızda</a><a href="/iletisim/">İletişim</a><a href="https://wa.me/905333820705">WhatsApp</a></div></details>
<a class="cta" href="https://wa.me/905333820705">WhatsApp</a>
</div></header>
{body}
<footer class="footer"><div class="wrap footer-inner"><div>Deva Alüminyum · Kayseri</div><div class="small">Alüminyum doğrama · cephe · korkuluk · cam balkon · otomatik kapı</div></div></footer>
</body></html>"""

def write_route(path,content):
    folder=DIST/path.strip("/")
    folder.mkdir(parents=True,exist_ok=True)
    (folder/"index.html").write_text(content,encoding="utf-8")

def service_cards():
    out=[]
    for i,(slug,name,desc,_id) in enumerate(services,1):
      out.append(f'<a class="card service-card" href="/{slug}/"><div class="card-body"><div class="service-top"><span class="service-kicker">Deva Alüminyum</span><span class="service-arrow" aria-hidden="true">↗</span></div><h3>{esc(name)}</h3><p>{esc(desc)}</p><span class="service-link">Detayları incele</span></div></a>')
    return "".join(out)

def blog_cards(items=None):
    items=items or BLOGS
    out=[]
    for b in items:
      out.append(f'<a class="card blog-card" href="/blog/{b["slug"]}/"><div class="card-body"><div class="eyebrow">Rehber · 2026</div><h3>{esc(b["title"])}</h3><p>{esc(b["description"])}</p><span class="read-more">Yazıyı oku →</span></div></a>')
    return "".join(out)

def build():
    if DIST.exists(): shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(SITE/"assets",DIST/"assets")
    recovered=ROOT/"archive"/"known-assets"
    recovered_out=DIST/"assets"/"recovered"
    (recovered_out/"Tema").mkdir(parents=True,exist_ok=True)
    (recovered_out/"resimler").mkdir(parents=True,exist_ok=True)
    logo_src=recovered/"Tema"/"logo.png"
    if logo_src.exists():
      shutil.copy2(logo_src,recovered_out/"Tema"/"logo.png")
    # Production'a yalnızca yüksek değerli medya alınır: 5 adet 1920x1080 hero + 23 tam boy referans.
    for name in [hero]+refs:
      src=recovered/"resimler"/name
      if src.exists():
        shutil.copy2(src,recovered_out/"resimler"/name)
    for src in sorted((recovered/"resimler").glob("aaaaaa*.jpg")) if (recovered/"resimler").exists() else []:
      shutil.copy2(src,recovered_out/"resimler"/src.name)

    body=f"""
<main id="main-content">
<section class="hero"><div class="hero-media"><img src="/assets/recovered/resimler/{hero}" alt="Deva Alüminyum cephe uygulaması"></div>
<div class="wrap hero-copy"><div class="eyebrow">Kayseri · Alüminyum & Cephe Sistemleri</div>
<h1>Yapının çizgisini alüminyumla tamamlıyoruz.</h1>
<p class="lead">Deva Alüminyum; kompozit cephe, alüminyum doğrama, korkuluk, cam balkon, ofis bölme ve otomatik kapı uygulamalarında Kayseri’de hizmet verir.</p>
<div class="actions"><a class="btn primary" href="/hizmetler/">Hizmetleri İncele</a><a class="btn" href="/referanslar/">Uygulamaları Gör</a></div></div></section>
<section class="section"><div class="wrap"><div class="section-head"><div><div class="eyebrow">Hizmetler</div><h2>Tek yapı, farklı alüminyum çözümleri.</h2></div><p>Eski Deva Alüminyum sitesinde yer alan doğrulanmış hizmet başlıkları korunarak yeni yapıda yeniden düzenlendi.</p></div>
<div class="grid">{service_cards()}</div></div></section>
<section class="section"><div class="wrap"><div class="section-head"><div><div class="eyebrow">Arşivden kurtarılan çalışmalar</div><h2>Gerçek uygulama görselleri.</h2></div><p>Eski Referanslarımız sayfasından kurtarılan fotoğraflar yeni siteye taşındı. Arşivde müşteri isimleri bulunmadığı için isim uydurulmadı.</p></div>
<div class="gallery">{''.join(f'<a href="/referanslar/"><img loading="lazy" src="/assets/recovered/resimler/{x}" alt="Deva Alüminyum uygulama referansı"></a>' for x in refs[:8])}</div></div></section>
<section class="section"><div class="wrap"><div class="section-head"><div><div class="eyebrow">Blog</div><h2>Güncel rehberler.</h2></div><p>Cam balkon, kompozit cephe, doğrama ve yapı sistemleri hakkında karar vermeyi kolaylaştıran içerikler.</p></div>
<div class="grid">{blog_cards(BLOGS[:3])}</div><div class="actions"><a class="btn" href="/blog/">Tüm yazıları gör</a></div></div></section>
<section class="section"><div class="wrap"><div class="section-head"><div><div class="eyebrow">Sık sorulan sorular</div><h2>Deva Alüminyum hakkında.</h2></div><p>Hizmet, bölge ve iletişim hakkında kısa yanıtlar.</p></div>
<div class="grid">{''.join(f'<div class="card"><div class="card-body"><h3>{esc(q)}</h3><p>{esc(a)}</p></div></div>' for q,a in FAQ_ITEMS)}</div></div></section>
<section class="section"><div class="wrap meta-strip"><div class="meta-item"><strong>Konum</strong>Kayseri</div><div class="meta-item"><strong>Telefon</strong><a href="tel:{PHONE}">{DISPLAY_PHONE}</a></div><div class="meta-item"><strong>Hızlı iletişim</strong><a href="https://wa.me/905333820705">WhatsApp üzerinden yazın</a></div></div></section>
</main>"""
    (DIST/"index.html").write_text(shell("Deva Alüminyum | Kayseri Alüminyum ve Cephe Sistemleri","Kayseri’de kompozit cephe, alüminyum doğrama, korkuluk, cam balkon, ofis bölme ve fotoselli kapı uygulamaları.","/",body),encoding="utf-8")

    services_body=f"""<main id="main-content"><div class="wrap breadcrumbs"><a href="/">Anasayfa</a> / Hizmetler</div><section class="page-hero"><div class="wrap"><div class="eyebrow">Hizmetler</div><h1>Alüminyum ve cephe uygulamaları</h1><p class="lead">Eski Deva Alüminyum sitesindeki doğrulanmış hizmet alanlarının tamamı.</p></div></section><section class="section"><div class="wrap"><div class="grid">{service_cards()}</div></div></section></main>"""
    write_route("hizmetler",shell("Hizmetler | Deva Alüminyum","Deva Alüminyum’un Kayseri’de sunduğu alüminyum ve cephe uygulamaları.","/hizmetler/",services_body))

    about_body="""<main id="main-content"><div class="wrap breadcrumbs"><a href="/">Anasayfa</a> / Hakkımızda</div><section class="page-hero"><div class="wrap"><div class="eyebrow">Deva Alüminyum</div><h1>Kayseri’de alüminyum ve cephe sistemleri.</h1></div></section><section class="section"><div class="wrap prose"><p>Deva Alüminyum Kompozit Cephe Sistemleri; alüminyum kompozit kaplama, bina giriş kompozit kaplama, alüminyum doğrama, silikon cephe, korkuluk sistemleri, bina giriş kapıları, ofis bölmeleri, fotoselli otomatik kapılar ve cam balkon uygulamalarıyla hizmet verir.</p><p>Eski kurumsal sitede müşteri memnuniyeti, dürüstlük, kalite ve sürekli gelişim temel çalışma ilkeleri olarak tanımlanmıştır. Yeni web sitesi bu kurumsal geçmişi korurken teknik yapıyı, içerik kalitesini ve erişilebilirliği günceller.</p></div></section></main>"""
    write_route("hakkimizda",shell("Hakkımızda | Deva Alüminyum","Deva Alüminyum’un Kayseri’deki alüminyum ve cephe sistemleri faaliyetleri hakkında.","/hakkimizda/",about_body))

    gallery=''.join(f'<a href="/assets/recovered/resimler/{x}" target="_blank"><img loading="lazy" src="/assets/recovered/resimler/{x}" alt="Deva Alüminyum referans uygulaması {i:02d}"></a>' for i,x in enumerate(refs,1))
    refs_body=f"""<main id="main-content"><div class="wrap breadcrumbs"><a href="/">Anasayfa</a> / Referanslar</div><section class="page-hero"><div class="wrap"><div class="eyebrow">Arşivden kurtarıldı</div><h1>Referans uygulamalarımız</h1><p class="lead">Eski Deva Alüminyum Referanslarımız sayfasından kurtarılan 23 tam boy çalışma fotoğrafı.</p></div></section><section class="section"><div class="wrap"><div class="gallery">{gallery}</div></div></section></main>"""
    write_route("referanslar",shell("Referanslar | Deva Alüminyum","Deva Alüminyum’un eski sitesinden kurtarılan gerçek uygulama ve referans fotoğrafları.","/referanslar/",refs_body))

    contact_body=f"""<main id="main-content"><div class="wrap breadcrumbs"><a href="/">Anasayfa</a> / İletişim</div><section class="page-hero"><div class="wrap"><div class="eyebrow">İletişim</div><h1>Projenizi konuşalım.</h1></div></section><section class="section"><div class="wrap contact-box"><div class="contact-panel"><h2>Deva Alüminyum</h2><p class="lead">Kayseri</p><p><strong>Telefon</strong><br><a href="tel:{PHONE}">{DISPLAY_PHONE}</a></p><p><strong>WhatsApp</strong><br><a href="https://wa.me/905333820705">Mesaj gönder</a></p><p><strong>E-posta</strong><br><a href="mailto:{EMAIL}">{EMAIL}</a></p><p><strong>Adres</strong><br>{ADDRESS}</p><p class="small">Bu iletişim bilgileri 11 Temmuz 2025 arşivinde doğrulandı; final yayından önce güncelliği tekrar teyit edilecektir.</p></div><div class="contact-panel"><h3>Hizmet alanları</h3><p>Kompozit cephe, alüminyum doğrama, silikon cephe, korkuluk sistemleri, bina giriş kapıları, ofis bölmeleri, fotoselli kapılar ve cam balkon.</p><p class="small">Sokak adresi, yayın öncesi güncel işletme kaydıyla son kez doğrulanacaktır.</p></div></div></section></main>"""
    write_route("iletisim",shell("İletişim | Deva Alüminyum","Deva Alüminyum Kayseri telefon ve WhatsApp iletişim bilgileri.","/iletisim/",contact_body))

    for slug,name,desc,_id in services:
      body=f"""<main id="main-content"><div class="wrap breadcrumbs"><a href="/">Anasayfa</a> / <a href="/hizmetler/">Hizmetler</a> / {esc(name)}</div><section class="page-hero"><div class="wrap"><div class="eyebrow">Kayseri · Deva Alüminyum</div><h1>{esc(name)}</h1><p class="lead">{esc(desc)}</p><div class="actions"><a class="btn primary" href="https://wa.me/905333820705">Teklif ve bilgi alın</a><a class="btn" href="/referanslar/">Referansları görün</a></div></div></section><section class="section"><div class="wrap prose"><h2>Uygulama hakkında</h2><p>{esc(desc)} Uygulama öncesinde ölçü, kullanım amacı, mevcut yapı ve mimari detaylar değerlendirilir. Malzeme ve montaj yaklaşımı proje koşullarına göre belirlenir.</p><h2>Planlama süreci</h2><p>Keşif ve ölçülendirme sonrasında uygulama alanına uygun detaylar netleştirilir. Amaç; estetik görünüm, kullanım güvenliği, bakım kolaylığı ve yapıyla uyum arasında dengeli bir çözüm oluşturmaktır.</p><h2>Teklif için gerekenler</h2><p>Uygulama yapılacak alanın fotoğrafları, yaklaşık ölçüleri ve varsa proje çizimleri ilk değerlendirme için paylaşılabilir. Nihai ölçüler uygulama öncesinde teyit edilir.</p><p class="small">Bu hizmet, Deva Alüminyum’un eski kurumsal sitesinde ayrı bir hizmet sayfası olarak yer almaktaydı; yeni sürümde eski anahtar kelime tekrarları temizlenerek hizmet ilişkisi korunmuştur.</p></div></section></main>"""
      write_route(slug,shell(f"{name} | Deva Alüminyum Kayseri",desc,f"/{slug}/",body,name))

    blog_body=f"""<main id="main-content"><div class="wrap breadcrumbs"><a href="/">Anasayfa</a> / Blog</div><section class="page-hero"><div class="wrap"><div class="eyebrow">Deva Rehber</div><h1>Alüminyum ve cephe sistemleri rehberi.</h1><p class="lead">Kayseri'de yapı, yenileme ve uygulama kararı verirken en çok araştırılan konuları teknik ve anlaşılır biçimde ele alıyoruz.</p></div></section><section class="section"><div class="wrap"><div class="grid">{blog_cards()}</div></div></section></main>"""
    write_route("blog",shell("Blog | Deva Alüminyum","Cam balkon, kompozit cephe, alüminyum doğrama, korkuluk, ofis bölme ve otomatik kapı rehberleri.","/blog/",blog_body))

    service_names={s[0]:s[1] for s in services}
    for b in BLOGS:
      sections="".join(f'<section class="article-section"><h2>{esc(h)}</h2><p>{esc(p)}</p></section>' for h,p in b["sections"])
      svc=b.get("service")
      svc_name=service_names.get(svc,"İlgili hizmet")
      article_body=f"""<main id="main-content"><div class="wrap breadcrumbs"><a href="/">Anasayfa</a> / <a href="/blog/">Blog</a> / {esc(b["title"])}</div><article class="article"><header class="page-hero"><div class="wrap"><div class="eyebrow">Deva Rehber · 21 Eylül 2026</div><h1>{esc(b["title"])}</h1><p class="lead">{esc(b["description"])}</p></div></header><div class="section"><div class="wrap article-layout"><div class="prose article-prose">{sections}<div class="article-cta"><h2>Projeniz için uygulama değerlendirmesi</h2><p>Fotoğraf, yaklaşık ölçü ve kullanım beklentinizi paylaşarak ilk değerlendirme için iletişime geçebilirsiniz.</p><div class="actions"><a class="btn primary" href="https://wa.me/905333820705">WhatsApp'tan yazın</a><a class="btn" href="/{svc}/">{esc(svc_name)}</a></div></div></div></div></div></article></main>"""
      write_route("blog/"+b["slug"],shell(b["title"]+" | Deva Alüminyum",b["description"],"/blog/"+b["slug"]+"/",article_body,article=b))

    redirects=[
      ("/Hakkimizda.html","/hakkimizda/"),
      ("/Sayfa/56/hizmetlerimiz","/hizmetler/"),
      ("/Sayfa/56/hizmetlerimiz/","/hizmetler/"),
      ("/Sayfa/72/referanslarimiz","/referanslar/"),
      ("/Sayfa/72/referanslarimiz/","/referanslar/"),
      ("/iletisim.html","/iletisim/"),
    ]
    for slug,name,desc,id_ in services:
      old={
        153:"kayseri--aluminyum-kompozit-kaplama",167:"bina-giris-kompozit-kaplama",168:"fabrika-yonetim-binasi-kompozit-kaplama",
        156:"kayseri-aluminyum-dograma",157:"kayseri-slikon-cephe-kaplama",171:"fransiz-balkon-korkuluklari",
        170:"balkon-korkuluklari",169:"merdiven-korkuluklari",162:"kayseri--bina-giris-kapisi",
        163:"kayseri-aluminyum-ofis-bolmeleri",164:"kayseri--fotoselli-otomatik-kapi-sistemleri-",158:"kayseri-cam-balkon-imalati-ve-montaj"
      }[id_]
      redirects += [
        (f"/Sayfa/{id_}/{old}",f"/{slug}/"),
        (f"/Sayfa/{id_}/{old}/",f"/{slug}/"),
        (f"/Detay/56/{id_}/{old}/",f"/{slug}/"),
      ]
    (DIST/"_redirects").write_text("\n".join(f"{a} {b} 301" for a,b in redirects)+"\n",encoding="utf-8")

    urls=["/","/hizmetler/","/referanslar/","/blog/","/hakkimizda/","/iletisim/"]+[f"/{s[0]}/" for s in services]+[f"/blog/{b['slug']}/" for b in BLOGS]
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{DOMAIN}{u}</loc></url>\n' for u in urls)+'</urlset>\n'
    (DIST/"sitemap.xml").write_text(sitemap,encoding="utf-8")
    feed_items="".join(f'<item><title>{esc(b["title"])}</title><link>{DOMAIN}/blog/{b["slug"]}/</link><guid>{DOMAIN}/blog/{b["slug"]}/</guid><description>{esc(b["description"])}</description><pubDate>Mon, 21 Sep 2026 09:00:00 +0300</pubDate></item>' for b in BLOGS)
    (DIST/"feed.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Deva Alüminyum Blog</title><link>'+DOMAIN+'/blog/</link><description>Alüminyum ve cephe sistemleri rehberi</description>'+feed_items+'</channel></rss>',encoding="utf-8")
    llms=["# Deva Alüminyum","","> Kayseri merkezli alüminyum ve cephe sistemleri uygulama firması.","","## Hizmetler"]+[f"- [{name}]({DOMAIN}/{slug}/): {desc}" for slug,name,desc,_ in services]+["","## Rehberler"]+[f"- [{b['title']}]({DOMAIN}/blog/{b['slug']}/): {b['description']}" for b in BLOGS]+["","## İletişim",f"- Telefon: {DISPLAY_PHONE}",f"- E-posta: {EMAIL}",f"- Adres: {ADDRESS}"]
    (DIST/"llms.txt").write_text("\n".join(llms)+"\n",encoding="utf-8")
    (DIST/"robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n",encoding="utf-8")
    (DIST/"_headers").write_text("""/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Cross-Origin-Opener-Policy: same-origin

/assets/*
  Cache-Control: public, max-age=31536000, immutable

/sitemap.xml
  Cache-Control: public, max-age=3600
""",encoding="utf-8")
    (DIST/"404.html").write_text(shell("Sayfa bulunamadı | Deva Alüminyum","Aradığınız sayfa bulunamadı.","/404",'<main id="main-content"><section class="page-hero"><div class="wrap"><h1>Sayfa bulunamadı</h1><p class="lead"><a href="/">Anasayfaya dönün</a></p></div></section></main>'),encoding="utf-8")

if __name__=="__main__":
    build()
    print("Built",DIST)
