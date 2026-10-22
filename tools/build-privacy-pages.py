#!/usr/bin/env python3
"""Политика конфиденциальности отдельной страницей на язык: /es/privacy, /fr/privacy, /de/privacy, /ru/privacy, /uk/privacy
(Мак, 23.10.2026).

Зачем: на /privacy все шесть языков на одной странице, язык переключает скрипт, а у страницы lang="en" — поиск и ИИ
(GPTBot, ClaudeBot…) берут её как английскую и испанскую или французскую политику не видят. Каждая страница здесь —
только свой язык, свой <title>, description, canonical и hreflang на все языки.

🔑 /privacy остаётся как есть, со всеми языками и якорями: на неё ведут App Store («#choices-es»), Google Play
(«#delete») и само приложение. Ей добавляются только ссылки hreflang на языковые страницы.

Источник правды — privacy.html. После правки политики: python3 tools/build-privacy-pages.py.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://mydynasty.app"
LANGS = ["en", "uk", "ru", "de", "es", "fr"]
OG_LOCALE = {"en": "en_US", "es": "es_419", "fr": "fr_FR", "de": "de_DE", "ru": "ru_RU", "uk": "uk_UA"}

DESC = {
    "en": "Privacy policy of the myDynasty family-tree app for iPhone, iPad and Android: your tree stays on your device, "
          "and AI features ask for your consent before sending anything.",
    "uk": "Політика конфіденційності застосунку родовідного дерева myDynasty для iPhone, iPad та Android: ваше дерево "
          "залишається на пристрої, а функції ШІ питають згоди, перш ніж щось надіслати.",
    "ru": "Политика конфиденциальности приложения семейного древа myDynasty для iPhone, iPad и Android: ваше дерево "
          "остаётся на устройстве, а функции ИИ спрашивают согласия, прежде чем что-то отправить.",
    "de": "Datenschutzerklärung der Stammbaum-App myDynasty für iPhone, iPad und Android: Ihr Stammbaum bleibt auf Ihrem "
          "Gerät, und KI-Funktionen fragen nach Ihrer Einwilligung, bevor sie etwas senden.",
    "es": "Política de privacidad de la app de árbol genealógico myDynasty para iPhone, iPad y Android: su árbol se queda "
          "en su dispositivo y las funciones de IA piden su consentimiento antes de enviar nada.",
    "fr": "Politique de confidentialité de l’application d’arbre généalogique myDynasty pour iPhone, iPad et Android : "
          "votre arbre reste sur votre appareil, et les fonctions d’IA demandent votre consentement avant tout envoi.",
}


def page_url(lang):
    return f"{SITE}/privacy" if lang == "en" else f"{SITE}/{lang}/privacy"


def alternates():
    links = [f'<link rel="alternate" hreflang="{l}" href="{page_url(l)}">' for l in LANGS]
    links.append(f'<link rel="alternate" hreflang="x-default" href="{page_url("en")}">')
    return "\n".join(links)


def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def sections(html):
    """Секция каждого языка — от её <section> до начала следующей (или до конца последней)."""
    starts = [(m.start(), m.group(1)) for m in re.finditer(r'<section class="lang-content[^"]*" data-lang="(\w+)"', html)]
    out = {}
    for i, (start, lang) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else html.index("</section>", start) + len("</section>")
        body = html[start:end]
        body = body[:body.rindex("</section>") + len("</section>")]
        out[lang] = body
    return out, starts[0][0], end


# Переключатель языка на языковой странице ведёт на адрес языка; #choices и #delete — к своему разделу.
PAGE_SCRIPT = """<script>
  (function () {
    document.querySelectorAll('.lang-switch button').forEach(function (btn) {
      btn.addEventListener('click', function () {
        try { localStorage.setItem('mydynasty.privacy.lang', btn.dataset.lang); } catch (e) {}
        location.href = btn.dataset.lang === 'en' ? '/privacy' : '/' + btn.dataset.lang + '/privacy';
      });
    });
    var lang = document.documentElement.getAttribute('lang');
    function openChoices() {
      var m = /^#(choices|delete)(?:-\\w+)?$/.exec(location.hash);
      if (!m) return;
      var target = document.getElementById(lang === 'en' ? m[1] : m[1] + '-' + lang);
      if (target) target.scrollIntoView();
    }
    openChoices();
    window.addEventListener('hashchange', openChoices);
  })();
</script>"""


def build(html, lang, secs, first, last):
    out = html[:first] + secs[lang].replace('class="lang-content"', 'class="lang-content is-active"', 1) + html[last:]
    # Шапка.
    title = re.search(r"<h1>(.*?)</h1>", secs[lang], re.S).group(1).strip()
    out = re.sub(r'<html lang="[^"]*">', f'<html lang="{lang}">', out, count=1)
    out = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", out, count=1, flags=re.S)
    out = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(DESC[lang])}">', out, count=1)
    out = re.sub(r'<link rel="canonical" href="[^"]*">(?:\n<link rel="alternate"[^>]*>)*',
                 lambda m: f'<link rel="canonical" href="{page_url(lang)}">\n{alternates()}', out, count=1)
    out = re.sub(r'<meta property="og:url" content="[^"]*">',
                 f'<meta property="og:url" content="{page_url(lang)}"><meta property="og:locale" content="{OG_LOCALE[lang]}">', out, count=1)
    out = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc(title)}">', out, count=1)
    out = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(DESC[lang])}">', out, count=1)
    # Кнопка своего языка — нажата сразу, без скрипта.
    out = re.sub(r'(<button type="button" role="tab" data-lang="\w+") class="is-active" aria-selected="true">',
                 r'\1 aria-selected="false">', out)
    out = out.replace(f'data-lang="{lang}" aria-selected="false">', f'data-lang="{lang}" class="is-active" aria-selected="true">', 1)
    # Скрипт переключения — свой; относительные пути — от корня (страница лежит в /xx/).
    out = re.sub(r"<script>\s*\(function \(\) \{\s*var buttons = document\.querySelectorAll\('\.lang-switch button'\);.*?</script>",
                 lambda m: PAGE_SCRIPT, out, count=1, flags=re.S)
    out = re.sub(r'((?:src|href)=")(?!https?:|#|/|mailto:|data:)', r"\1/", out)
    return out


def main():
    path = os.path.join(ROOT, "privacy.html")
    html = open(path, encoding="utf-8").read()
    secs, first, last = sections(html)
    assert set(secs) == set(LANGS), secs.keys()

    for lang in LANGS:
        if lang == "en":
            continue
        os.makedirs(os.path.join(ROOT, lang), exist_ok=True)
        open(os.path.join(ROOT, lang, "privacy.html"), "w", encoding="utf-8").write(build(html, lang, secs, first, last))
        print(f"ok /{lang}/privacy")

    # /privacy — всё как было, плюс hreflang на языковые страницы.
    root = re.sub(r'<link rel="canonical" href="[^"]*">(?:\n<link rel="alternate"[^>]*>)*',
                  lambda m: f'<link rel="canonical" href="{page_url("en")}">\n{alternates()}', html, count=1)
    open(path, "w", encoding="utf-8").write(root)
    print("ok /privacy (hreflang)")


if __name__ == "__main__":
    main()
