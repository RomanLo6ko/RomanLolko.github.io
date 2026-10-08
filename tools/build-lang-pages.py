#!/usr/bin/env python3
"""Языковые страницы главной: /es/, /fr/, /de/, /ru/, /uk/ (Mac, 08.10.2026).

Зачем: язык на главной переключается скриптом на одном адресе, а роботы поиска и ИИ (GPTBot, ClaudeBot, PerplexityBot…)
скрипты обычно не выполняют — они видели только английский. Каждая страница здесь — готовый HTML на своём языке:
тексты из словаря I18N в index.html вписаны прямо в разметку, свои <title>, description, Open Graph, JSON-LD,
canonical и hreflang на все языки. Скрипт на странице продолжает работать (меню языков ведёт на нужный адрес).

Источник правды — index.html (английский и словари). После правки текстов: python3 tools/build-lang-pages.py.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://mydynasty.app"
LANGS = ["en", "es", "fr", "de", "ru", "uk"]
HREFLANG = {"en": "en", "es": "es", "fr": "fr", "de": "de", "ru": "ru", "uk": "uk"}
OG_LOCALE = {"en": "en_US", "es": "es_419", "fr": "fr_FR", "de": "de_DE", "ru": "ru_RU", "uk": "uk_UA"}

DESC = {
    "en": "myDynasty is a private family tree app for iPhone and Android: build a visual family tree, keep photos and "
          "documents, map places and burial sites, import and export GEDCOM. Optional Premium adds AI: restore old "
          "photos, tell a relative's story by voice, read headstone inscriptions.",
    "es": "myDynasty es una app privada de árbol genealógico para iPhone y Android: cree su árbol, guarde fotos y "
          "documentos, marque lugares y sepulturas en el mapa, importe y exporte GEDCOM. Premium opcional con IA: "
          "restaura fotos antiguas, llena fichas con su voz y lee lápidas.",
    "fr": "myDynasty est une application privée d’arbre généalogique pour iPhone et Android : créez votre arbre, "
          "conservez photos et documents, indiquez lieux et sépultures sur la carte, import et export GEDCOM. Premium "
          "facultatif avec IA : restauration de vieilles photos, fiches remplies à la voix, lecture des tombes.",
    "de": "myDynasty ist eine private Stammbaum-App für iPhone und Android: Stammbaum erstellen, Fotos und Dokumente "
          "aufbewahren, Orte und Grabstätten auf der Karte, GEDCOM-Import und -Export. Optional Premium mit KI: alte "
          "Fotos restaurieren, per Sprache erzählen, Grabinschriften lesen.",
    "ru": "myDynasty — приватное приложение семейного древа для iPhone и Android: стройте родословную, храните фото и "
          "документы, отмечайте места и захоронения на карте, импорт и экспорт GEDCOM. Premium по желанию — ИИ: "
          "реставрация старых фото, рассказ голосом, чтение надписей на памятниках.",
    "uk": "myDynasty — приватний застосунок родовідного дерева для iPhone та Android: будуйте родовід, зберігайте фото "
          "й документи, позначайте місця й поховання на мапі, імпорт і експорт GEDCOM. Premium за бажанням — ШІ: "
          "реставрація старих фото, розповідь голосом, читання написів на пам’ятниках.",
}


def page_url(lang):
    return f"{SITE}/" if lang == "en" else f"{SITE}/{lang}/"


def load_dicts(html):
    block = html[html.index("var I18N={"):]
    dicts = {}
    for lang in LANGS:
        m = re.search(r"\n\s*" + lang + r":\{\n(.*?)\n\s*\},?\n", block, re.S)
        dicts[lang] = json.loads("{" + m.group(1) + "}")
    return dicts


def json_ld(lang):
    data = {
        "@context": "https://schema.org",
        "@type": "MobileApplication",
        "name": "myDynasty",
        "url": page_url(lang),
        "inLanguage": lang,
        "description": DESC[lang],
        "applicationCategory": "LifestyleApplication",
        "operatingSystem": "iOS 15+, Android 7.0+",
        "availableLanguage": ["en", "es", "fr", "de", "ru", "uk"],
        "installUrl": ["https://apps.apple.com/app/id6793122627",
                       "https://play.google.com/store/apps/details?id=com.mydynasty.app"],
        "sameAs": ["https://apps.apple.com/app/id6793122627",
                   "https://play.google.com/store/apps/details?id=com.mydynasty.app"],
        "offers": [
            {"@type": "Offer", "name": "Free", "price": "0", "priceCurrency": "USD"},
            {"@type": "Offer", "name": "myDynasty Premium (monthly subscription, optional AI features)",
             "price": "4.99", "priceCurrency": "USD"},
        ],
        "featureList": ["Visual family tree", "Photos, documents and family archive", "Places and burial sites on a map",
                        "GEDCOM and LRV import and export", "No account, data stays on the device",
                        "Premium: AI photo restoration", "Premium: add a relative by telling a story by voice",
                        "Premium: read headstone inscriptions from a photo", "Premium: AI-assisted biographies"],
        "privacyPolicy": f"{SITE}/privacy",
        "publisher": {"@type": "Person", "name": "Roman Lobko", "url": f"{SITE}/"},
    }
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"


def alternates():
    links = [f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{page_url(l)}">' for l in LANGS]
    links.append(f'<link rel="alternate" hreflang="x-default" href="{page_url("en")}">')
    return "".join(links)


def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def build(html, dicts, lang):
    d = dicts[lang]
    out = html
    # Тексты: data-i18n — как textContent, data-i18n-html — как innerHTML (то же, что делает скрипт страницы).
    for attr, raw in (("data-i18n", False), ("data-i18n-html", True)):
        def repl(m):
            key = m.group(3)
            if key not in d:
                return m.group(0)
            val = d[key] if raw else esc(d[key]).replace("&quot;", '"')
            return m.group(1) + val + m.group(5)
        out, n = re.subn(r'(<(\w+)\b[^>]*\b' + attr + r'="([^"]+)"[^>]*>)(.*?)(</\2>)', repl, out, flags=re.S)
    # Шапка: язык, описание, OG, canonical, hreflang, JSON-LD.
    out = re.sub(r'<html lang="[^"]*">', f'<html lang="{lang}">', out, count=1)
    out = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(DESC[lang])}">', out, count=1)
    out = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{page_url(lang)}">' + alternates(), out, count=1)
    out = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{page_url(lang)}"><meta property="og:locale" content="{OG_LOCALE[lang]}">', out, count=1)
    out = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc(d["meta.title"])}">', out, count=1)
    out = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(DESC[lang])}">', out, count=1)
    out = re.sub(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{esc(d["meta.title"])}">', out, count=1)
    out = re.sub(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{esc(DESC[lang])}">', out, count=1)
    out = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: json_ld(lang), out, count=1, flags=re.S)
    # Снимки — сразу своего языка; относительные пути — от корня (страница лежит в /xx/).
    out = re.sub(r'(data-shot="([^"]+)" src=")screens/en/', lambda m: m.group(1) + f"screens/{lang}/", out)
    out = re.sub(r'((?:src|href)=")(?!https?:|#|/|mailto:|data:)', r"\1/", out)
    # Язык страницы — скрипту (меню ведёт на адрес языка, а не переводит на месте).
    out = re.sub(r"<script>window\.MD_PAGE_LANG='\w+';</script>\n", "", out)
    out = out.replace("</head>", f"<script>window.MD_PAGE_LANG='{lang}';</script>\n</head>", 1)
    return out


def main():
    path = os.path.join(ROOT, "index.html")
    html = open(path, encoding="utf-8").read()
    dicts = load_dicts(html)
    # Корень — английская страница: тот же разбор, чтобы шапка и JSON-LD были одинаковы на всех.
    for lang in LANGS:
        page = build(html, dicts, lang)
        if lang == "en":
            # Корень — сам источник: в нём меняется только шапка (описание, canonical+hreflang, JSON-LD).
            src = html
            for pat in (r'<meta name="description" content="[^"]*">', r'<link rel="canonical" href="[^"]*">(?:<link rel="alternate"[^>]*>)*',
                        r'<script type="application/ld\+json">.*?</script>'):
                new = re.search(pat, page, re.S).group(0)
                src = re.sub(pat, lambda m: new, src, count=1, flags=re.S)
            if "window.MD_PAGE_LANG" not in src:
                src = src.replace("</head>", "<script>window.MD_PAGE_LANG='en';</script>\n</head>", 1)
            open(path, "w", encoding="utf-8").write(src)
            print("ok /")
            continue
        os.makedirs(os.path.join(ROOT, lang), exist_ok=True)
        open(os.path.join(ROOT, lang, "index.html"), "w", encoding="utf-8").write(page)
        print(f"ok /{lang}/")


if __name__ == "__main__":
    main()
