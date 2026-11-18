#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_site.py — собирает сайт PaxVanila (docs/, для GitHub Pages) и ассеты приложения (app/assets/)
из одного источника: content/paxvanila.json (+ paxvanila.en.json) + лор/*.md (+ лор/en/) + гайды/ + обложки/*.png.

    pip install markdown pillow
    python tools/build_site.py

После правки адреса сервера, Discord или даты старта в content/paxvanila.json — запустить снова,
закоммитить docs/ и app/assets/.
"""
import html
import json
import os
import re
import shutil
import time

import markdown
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "tools", "site_src")
DOCS = os.path.join(ROOT, "docs")
APP_ASSETS = os.path.join(ROOT, "app", "assets")
LORE = os.path.join(ROOT, "лор")
COVERS = os.path.join(ROOT, "обложки")
GUIDES = os.path.join(ROOT, "гайды")

GOLD = (224, 179, 84)
DARK = (20, 17, 13)


def font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
              "C:/Windows/Fonts/georgiab.ttf", "/Library/Fonts/Georgia Bold.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def make_icon(size, maskable=False, bg=True):
    """Щит с надписью PAX: золото на тёмном камне."""
    im = Image.new("RGBA", (size, size), DARK + (255,) if bg else (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pad = size * (0.2 if maskable else 0.1)
    w = size - 2 * pad
    x0, y0 = pad, pad
    top = y0 + w * 0.02
    pts = [(x0 + w * 0.08, top), (x0 + w * 0.92, top), (x0 + w * 0.92, y0 + w * 0.5),
           (x0 + w * 0.5, y0 + w * 0.98), (x0 + w * 0.08, y0 + w * 0.5)]
    d.polygon(pts, fill=(44, 36, 28, 255), outline=GOLD + (255,), width=max(2, int(size * 0.035)))
    f = font(int(w * 0.3))
    t = "PAX"
    bb = d.textbbox((0, 0), t, font=f)
    d.text((x0 + (w - (bb[2] - bb[0])) / 2 - bb[0], y0 + w * 0.36 - (bb[3] - bb[1]) / 2 - bb[1]), t, font=f, fill=GOLD + (255,))
    # маленькая «шестая строка» под словом
    ly = y0 + w * 0.62
    d.line([(x0 + w * 0.32, ly), (x0 + w * 0.68, ly)], fill=GOLD + (200,), width=max(1, int(size * 0.02)))
    return im


def slug(text, used):
    s = re.sub(r"[^\w\- ]", "", text.lower()).strip().replace(" ", "-")[:60] or "h"
    base, i = s, 2
    while s in used:
        s = f"{base}-{i}"
        i += 1
    used.add(s)
    return s


def render_lore(md_text, links):
    # ссылки между файлами лора → на страницы сайта
    for fname, page in links.items():
        md_text = md_text.replace(f"]({fname})", f"]({page})")
    md_text = re.sub(r"<!--.*?-->", "", md_text, flags=re.S)
    body = markdown.markdown(md_text, extensions=["tables", "sane_lists"])
    used, toc = set(), []

    def add_id(m):
        lvl, inner = m.group(1), m.group(2)
        txt = re.sub("<[^>]+>", "", inner)
        i = slug(html.unescape(txt), used)
        if lvl in ("1", "2", "3"):
            toc.append((int(lvl), txt, i))
        return f'<h{lvl} id="{i}">{inner}</h{lvl}>'
    body = re.sub(r"<h([1-6])>(.*?)</h\1>", add_id, body)
    return body, toc


PAGE = """<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}"><meta name="theme-color" content="#14110d">
<link rel="manifest" href="../manifest.webmanifest"><link rel="icon" href="../icons/icon-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+SC:wght@600;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../style.css"></head><body>
<header class="top"><div class="wrap"><a class="brand" href="../"><img src="../icons/icon-192.png" alt="">PaxVanila</a>
<nav class="main">{nav}</nav><a class="iconbtn" id="lang" href="__LANGURL__" hreflang="__LANGCODE__" title="__LANGTITLE__">__LANGLABEL__</a><button class="iconbtn" id="theme" aria-label="Сменить тему">☾</button></div></header>
<div class="wrap doc"><aside><details open><summary>Оглавление</summary>{toc}</details></aside><article>{body}</article></div>
<footer><div class="wrap"><a href="../">← На главную</a> · <a href="../lore.html">Весь лор</a></div></footer>
<script src="../app.js"></script></body></html>"""

LANGS = ("ru", "en")


def load_content(lang):
    with open(os.path.join(ROOT, "content", "paxvanila.json"), encoding="utf-8") as f:
        C = json.load(f)
    if lang == "ru":
        return C
    with open(os.path.join(ROOT, "content", f"paxvanila.{lang}.json"), encoding="utf-8") as f:
        T = json.load(f)
    T.pop("_comment", None)
    T["config"] = C["config"]  # адрес, даты, граница — общие
    return T


def load_map(lang):
    """content/map.json (схема по лору, ru/en рядом) + content/map_towns.json (реальные города Towny, если есть)."""
    with open(os.path.join(ROOT, "content", "map.json"), encoding="utf-8") as f:
        M = json.load(f)
    loc = lambda v: v.get(lang) or v.get("ru", "") if isinstance(v, dict) else v
    out = {k: [{kk: loc(vv) if kk in ("name", "text") else vv for kk, vv in it.items()} for it in M[k]]
           for k in ("places", "powers", "ancient")}
    out["lore"] = [{kk: loc(vv) if kk in ("name", "text") else vv for kk, vv in it.items()} for it in M.get("lore", [])]
    out["far"] = [{kk: loc(vv) if kk in ("name", "text") else vv for kk, vv in it.items()} for it in M.get("far", [])]
    out["blocs"] = {k: loc(v) for k, v in M["blocs"].items()}
    out["towns"], out["townsDate"] = [], ""
    tp = os.path.join(ROOT, "content", "map_towns.json")
    if os.path.exists(tp):
        with open(tp, encoding="utf-8") as f:
            T = json.load(f)
        out["towns"], out["townsDate"] = T.get("towns", []), T.get("generated", "")
    return out


def src_file(base, lang, fname):
    """Перевод лежит в <папка>/<lang>/<тот же файл>; если его нет — русский оригинал."""
    if lang != "ru":
        p = os.path.join(base, lang, fname)
        if os.path.exists(p):
            return p
    return os.path.join(base, fname)


def translator(lang):
    if lang == "ru":
        return lambda s: s
    with open(os.path.join(SRC, f"i18n_{lang}.json"), encoding="utf-8") as f:
        pairs = json.load(f)

    def tr(s):
        for a, b in pairs:
            s = s.replace(a, b)
        return s
    return tr


def lang_switch(html_text, lang, depth, page):
    """Кнопка RU/EN ведёт на ту же страницу на другом языке. depth — глубина страницы внутри языка."""
    if lang == "ru":
        url, code, label, title = "../" * depth + "en/" + page, "en", "EN", "English"
    else:
        url, code, label, title = "../" * (depth + 1) + page, "ru", "RU", "Русский"
    return (html_text.replace("__LANGURL__", url or "./").replace("__LANGCODE__", code)
            .replace("__LANGLABEL__", label).replace("__LANGTITLE__", title))


def localize(v, lang):
    """{ru, en} → строка нужного языка, рекурсивно по словарям и спискам."""
    if isinstance(v, dict):
        if v and set(v) <= {"ru", "en"}:
            return v.get(lang) or v.get("ru", "")
        return {k: localize(x, lang) for k, x in v.items() if k != "_comment"}
    if isinstance(v, list):
        return [localize(x, lang) for x in v]
    return v


def load_json(name):
    with open(os.path.join(ROOT, "content", name), encoding="utf-8") as f:
        return json.load(f)


def build(lang, out):
    C = load_content(lang)
    C["map"] = load_map(lang)
    # ПаксГидромет и «Вестник Академии»: справочники + демо-данные (живые пишет paxmeteo.sk)
    C["meteo"] = localize(load_json("meteo.json"), lang)
    C["meteoDemo"] = load_json("meteo_demo.json")
    C["news"] = localize(load_json("news.json"), lang)
    C["newsDemo"] = load_json("news_demo.json")
    tr = translator(lang)
    for d in ("", "img", "icons", "lore", "guides", "files"):
        os.makedirs(os.path.join(out, d), exist_ok=True)

    def write(rel, text, depth=0):
        with open(os.path.join(out, rel), "w", encoding="utf-8") as f:
            f.write(lang_switch(tr(text), lang, depth, rel.replace(os.sep, "/").replace("index.html", "")))

    # статика
    idx = open(os.path.join(SRC, "index.html"), encoding="utf-8").read()
    write("index.html", idx)
    for fn in ("style.css", "app.js"):
        shutil.copy(os.path.join(SRC, fn), os.path.join(out, fn))
    with open(os.path.join(out, "content.json"), "w", encoding="utf-8") as f:
        json.dump(C, f, ensure_ascii=False)

    # картинки: обложки 1920 → 1280 jpg (для en — копия)
    if lang == "ru":
        for fn in sorted(os.listdir(COVERS)):
            if fn.endswith(".png"):
                im = Image.open(os.path.join(COVERS, fn)).convert("RGB")
                im.thumbnail((1280, 720))
                im.save(os.path.join(out, "img", fn.replace(".png", ".jpg")), quality=82, optimize=True)
        for s in (192, 512):
            make_icon(s).save(os.path.join(out, "icons", f"icon-{s}.png"))
            make_icon(s, maskable=True).save(os.path.join(out, "icons", f"maskable-{s}.png"))
    else:
        for d in ("img", "icons"):
            for fn in os.listdir(os.path.join(DOCS, d)):
                shutil.copy(os.path.join(DOCS, d, fn), os.path.join(out, d, fn))

    # клиентская сборка
    mr = os.path.join(ROOT, "PaxVanila_Client_26.2", "PaxVanila_Client_26.2.mrpack")
    if os.path.exists(mr):
        shutil.copy(mr, os.path.join(out, "files"))
    elif os.path.exists(os.path.join(DOCS, "files", "PaxVanila_Client_26.2.mrpack")) and lang != "ru":
        shutil.copy(os.path.join(DOCS, "files", "PaxVanila_Client_26.2.mrpack"), os.path.join(out, "files"))

    # лор
    links = {l["file"]: f"{l['id']}.html" for l in C["lore"]}
    nav = "".join(f'<a href="{l["id"]}.html">{html.escape(l["title"])}</a>' for l in C["lore"])
    cards = []
    for l in C["lore"]:
        with open(src_file(LORE, lang, l["file"]), encoding="utf-8") as f:
            body, toc = render_lore(f.read(), links)
        toc_html = "".join(f'<a class="h{lv}" href="#{i}">{t}</a>' for lv, t, i in toc if lv <= 2 or len(toc) < 40)
        write(os.path.join("lore", f"{l['id']}.html"),
              PAGE.format(title=f"{l['title']} — PaxVanila", desc=html.escape(l["subtitle"]), nav=nav, toc=toc_html, body=body), 1)
        cards.append(f'<a href="lore/{l["id"]}.html"><div class="card"><h3>📜 {html.escape(l["title"])}</h3><p>{html.escape(l["subtitle"])}</p></div></a>')
    # гайды (та же вёрстка, папка guides/)
    for g in C.get("guides", []):
        with open(src_file(GUIDES, lang, g["file"]), encoding="utf-8") as f:
            body, toc = render_lore(f.read(), links)
        toc_html = "".join(f'<a class="h{lv}" href="#{i}">{t}</a>' for lv, t, i in toc if lv <= 2)
        write(os.path.join("guides", f"{g['id']}.html"),
              PAGE.format(title=f"{g['title']} — PaxVanila", desc=html.escape(g["subtitle"]), nav=nav.replace('href="', 'href="../lore/'), toc=toc_html, body=body), 1)
        cards.append(f'<a href="guides/{g["id"]}.html"><div class="card"><h3>🧭 {html.escape(g["title"])}</h3><p>{html.escape(g["subtitle"])}</p></div></a>')
    # политика конфиденциальности (нужна по URL для Google Play и App Store)
    pv = "privacy.md" if lang == "ru" else f"privacy.{lang}.md"
    with open(os.path.join(SRC, pv), encoding="utf-8") as f:
        body, _ = render_lore(f.read(), {})
    privacy_title = "Конфиденциальность — PaxVanila" if lang == "ru" else "Privacy — PaxVanila"
    write("privacy.html", PAGE.replace("../", "").replace('href="lore.html">Весь лор', 'href="lore.html">Лор')
          .format(title=privacy_title, desc="PaxVanila privacy policy", nav=nav.replace('href="', 'href="lore/'), toc="", body=body))
    lore_index = re.sub(r"<div class=\"hero\">.*?</footer>",
                        '<section><div class="wrap"><div class="kicker">История мира</div><h1>Лор PaxVanila</h1>'
                        '<p class="sub">Читать по порядку: Предтечи → Средние эпохи → Поздние эпохи (будущее мира: от роботов 1962 года до Луны, Марса и звёзд). Катаклизмы — отдельная летопись.</p>'
                        f'<div class="lorelist">{"".join(cards)}</div></div></section><footer><div class="wrap"><a href="./">← На главную</a></div></footer>',
                        idx, flags=re.S)
    write("lore.html", lore_index.replace("<title>PaxVanila</title>", "<title>Лор — PaxVanila</title>"))

    # PWA
    manifest = {
        "name": "PaxVanila", "short_name": "PaxVanila", "lang": lang, "start_url": "./", "scope": "./",
        "display": "standalone", "background_color": "#14110d", "theme_color": "#14110d",
        "description": "Геополитический Minecraft-сервер: статус, календарь недель, механики, правила и лор." if lang == "ru"
        else "Geopolitical Minecraft server: status, weekly calendar, mechanics, rules and lore.",
        "icons": [{"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}
    with open(os.path.join(out, "manifest.webmanifest"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    core = ["./", "index.html", "lore.html", "style.css", "app.js", "content.json", "icons/icon-192.png"] + \
           [f"lore/{l['id']}.html" for l in C["lore"]] + [f"guides/{g['id']}.html" for g in C.get("guides", [])] + ["privacy.html"] + \
           [f"img/{w['image'].replace('.png', '.jpg')}" for w in C["weeks"]] + ["img/about.jpg"]
    sw = open(os.path.join(SRC, "sw.js"), encoding="utf-8").read()
    sw = sw.replace("__VERSION__", lang + time.strftime("%Y%m%d%H%M")).replace("__CORE__", json.dumps(core, ensure_ascii=False))
    with open(os.path.join(out, "sw.js"), "w", encoding="utf-8") as f:
        f.write(sw)
    return C


def main():
    if os.path.isdir(DOCS):
        shutil.rmtree(DOCS)
    os.makedirs(DOCS)
    open(os.path.join(DOCS, ".nojekyll"), "w").close()
    built = {}
    for lang in LANGS:
        built[lang] = build(lang, DOCS if lang == "ru" else os.path.join(DOCS, lang))

    # ассеты приложения: content.json + lore/ + guides/ (ru), content.<lang>.json + lore_<lang>/ + guides_<lang>/
    if os.path.isdir(os.path.join(ROOT, "app")):
        for lang, C in built.items():
            sfx = "" if lang == "ru" else f"_{lang}"
            for d in ("", "lore" + sfx, "guides" + sfx, "img"):
                os.makedirs(os.path.join(APP_ASSETS, d), exist_ok=True)
            name = "content.json" if lang == "ru" else f"content.{lang}.json"
            with open(os.path.join(APP_ASSETS, name), "w", encoding="utf-8") as f:
                json.dump(C, f, ensure_ascii=False)
            for l in C["lore"]:
                shutil.copy(src_file(LORE, lang, l["file"]), os.path.join(APP_ASSETS, "lore" + sfx, f"{l['id']}.md"))
            for g in C.get("guides", []):
                shutil.copy(src_file(GUIDES, lang, g["file"]), os.path.join(APP_ASSETS, "guides" + sfx, f"{g['id']}.md"))
        for fn in os.listdir(os.path.join(DOCS, "img")):
            shutil.copy(os.path.join(DOCS, "img", fn), os.path.join(APP_ASSETS, "img", fn))
        make_icon(1024).convert("RGB").save(os.path.join(APP_ASSETS, "icon.png"))
        make_icon(1024, maskable=True, bg=False).save(os.path.join(APP_ASSETS, "icon_fg.png"))
    print("Готово: docs/ (сайт, русский), docs/en/ (английский) и app/assets/ (приложение).")


if __name__ == "__main__":
    main()
