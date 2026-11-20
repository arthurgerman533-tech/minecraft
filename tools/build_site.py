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
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
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
    N = M.get("nether")
    if N:
        tr = lambda L: [{kk: loc(vv) if kk in ("name", "text") else vv for kk, vv in it.items()} for it in L]
        out["nether"] = {"places": tr(N.get("places", [])), "sites": tr(N.get("sites", [])),
                         "roads": N.get("roads", []), "roadName": loc(N.get("roadName", "")), "roadText": loc(N.get("roadText", ""))}
    # настоящая карта мира (tools/render_world.py): подложка + зоны погоды
    out["terrain"], out["zones"] = None, None
    if os.path.exists(os.path.join(ROOT, "content", "world_map.webp")):
        zp = os.path.join(ROOT, "content", "world_zones.json")
        Z = json.load(open(zp, encoding="utf-8")) if os.path.exists(zp) else {}
        R = Z.get("radius", 2048)
        out["terrain"] = {"src": "img/world_map.webp", "big": "img/world_map_big.webp", "radius": R,
                          "bounds": Z.get("bounds", [-R, -R, R, R]), "explored": Z.get("generated", 0),
                          "date": Z.get("date", ""), "seed": Z.get("seedNote", "")}
        if Z.get("zones"):
            out["zones"] = {"cell": Z.get("cell", 64), **Z["zones"]}
    # карта настоящей Земли (tools/make_earth.py): державы на местах исторических прообразов
    ep = os.path.join(ROOT, "content", "earth.json")
    out["earth"] = None
    if os.path.exists(ep):
        E = json.load(open(ep, encoding="utf-8"))
        byid = {p["id"]: p for p in out["powers"]}
        out["earth"] = {"box": E["box"], "land": E["land"], "rivers": E.get("rivers", []), "lakes": E.get("lakes", []),
                        "seas": [{**s, "name": loc(s["name"])} for s in E["seas"]],
                        "powers": [{**byid[p["id"]], "x": p["x"], "z": p["y"], "lon": p["lon"], "lat": p["lat"], "real": loc(p["real"])}
                                   for p in E["powers"] if p["id"] in byid]}
    out["towns"], out["townsDate"] = [], ""
    tp = os.path.join(ROOT, "content", "map_towns.json")
    if os.path.exists(tp):
        with open(tp, encoding="utf-8") as f:
            T = json.load(f)
        out["towns"], out["townsDate"] = T.get("towns", []), T.get("generated", "")
    return out


def load_roster(lang, M):
    """Таблица «Державы и игроки»: content/players.json (руками) + content/nations_towny.json (Towny, если есть)."""
    pp = os.path.join(ROOT, "content", "players.json")
    if not os.path.exists(pp):
        return None
    P = json.load(open(pp, encoding="utf-8"))
    tp = os.path.join(ROOT, "content", "nations_towny.json")
    TN = json.load(open(tp, encoding="utf-8")) if os.path.exists(tp) else {}
    towny = {n["name"].lower(): n for n in TN.get("nations", [])}
    used, rows = set(), []
    for pw in M["powers"]:
        e = localize(P["nations"].get(pw["id"], {}), lang)
        tn = towny.get((e.get("towny") or "").lower())
        if tn:
            used.add(tn["name"].lower())
        players = list(e.get("players") or [])
        if tn:
            for t in tn["towns"]:
                if t["mayor"] and t["mayor"] not in players:
                    players.append(t["mayor"])
        ruler = e.get("ruler") or (tn["king"] if tn else "")
        status = e.get("status") or ("taken" if ruler else "open")
        if status == "open" and tn and tn["towns"]:
            status = "taken"
        rows.append({"id": pw["id"], "name": pw["name"], "full": e.get("full") or pw["name"], "color": pw["color"],
                     "bloc": pw.get("bloc", ""), "ruler": ruler, "king": tn["king"] if tn else "", "players": players,
                     "status": status, "note": e.get("note", ""), "towny": e.get("towny", ""),
                     "towns": tn["towns"] if tn else [], "capital": tn["capital"] if tn else "",
                     "residents": tn["residents"] if tn else 0})
    for n in TN.get("nations", []):
        if n["name"].lower() in used:
            continue
        rows.append({"id": "towny-" + n["name"].lower(), "name": n["name"], "full": n["name"], "color": n["color"] or "#888888",
                     "bloc": "new", "ruler": n["king"], "king": n["king"],
                     "players": [t["mayor"] for t in n["towns"] if t["mayor"]], "status": "new", "note": "",
                     "towny": n["name"], "towns": n["towns"], "capital": n["capital"], "residents": n["residents"]})
    return {"rows": rows, "updated": P.get("updated", ""), "townyDate": TN.get("generated", ""),
            "freeTowns": TN.get("freeTowns", 0), "freeResidents": TN.get("freeResidents", 0),
            "text": P.get("text", {}).get(lang) or P.get("text", {}).get("ru", {})}


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
    C["roster"] = load_roster(lang, C["map"])
    # ПаксГидромет и «Вестник Академии»: справочники + демо-данные (живые пишет paxmeteo.sk)
    C["meteo"] = localize(load_json("meteo.json"), lang)
    C["meteoDemo"] = load_json("meteo_demo.json")
    # справочник катаклизмов датапака (tools/make_cataclysms.py) для слоя «Недавние катаклизмы» на карте
    C["cata"] = localize(load_json("cataclysms.json"), lang)
    C["news"] = localize(load_json("news.json"), lang)
    C["newsDemo"] = load_json("news_demo.json")
    # «Новости сервера» (news.html): летопись по дням + демо живых записей (?demo в адресе)
    C["chronicle"] = localize(load_json("chronicle.json"), lang)
    C["chronicleDemo"] = load_json("chronicle_demo.json")
    tr = translator(lang)
    for d in ("", "img", "icons", "lore", "guides", "files"):
        os.makedirs(os.path.join(out, d), exist_ok=True)

    def write(rel, text, depth=0):
        with open(os.path.join(out, rel), "w", encoding="utf-8") as f:
            f.write(lang_switch(tr(text), lang, depth, rel.replace(os.sep, "/").replace("index.html", "")))

    # статика
    idx = open(os.path.join(SRC, "index.html"), encoding="utf-8").read()
    write("index.html", idx)
    for fn in ("style.css", "app.js", "timeline.js"):
        shutil.copy(os.path.join(SRC, fn), os.path.join(out, fn))

    # «Хроника держав»: 10 держав по эпохам (content/timeline.json, генератор tools/make_timeline.py)
    tlp = os.path.join(ROOT, "content", "timeline.json")
    if os.path.exists(tlp):
        TL = localize(load_json("timeline.json"), lang)
        U = TL["ui"]
        header = tr(re.search(r'<header class="top">.*?</header>', idx, flags=re.S).group(0)).replace('href="#', 'href="./#')
        header = header.replace('<a href="timeline.html">', '<a class="on" href="timeline.html">')
        page = open(os.path.join(SRC, "timeline.html"), encoding="utf-8").read()
        for k, v in {"__HEADER__": header, "__LANG__": lang, "__TITLE__": U["title"], "__SUB__": U["sub"], "__KICKER__": U["kicker"],
                     "__NOTE__": U["note"], "__PREV__": U["prev"], "__NEXT__": U["next"], "__ERA__": U["era"], "__ADDED__": U["added"],
                     "__ALL__": U["all"], "__ALLSUB__": U["allsub"], "__NEXTERAS__": U["next_eras"], "__LORE__": U["lore"], "__HOME__": U["home"]}.items():
            page = page.replace(k, v if k == "__HEADER__" else html.escape(v, quote=True))
        page = page.replace("__DATA__", json.dumps(TL, ensure_ascii=False).replace("</", "<\\/"))
        write("timeline.html", page)
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

    # настоящая карта мира
    for fn in ("world_map.webp", "world_map_big.webp"):
        fp = os.path.join(ROOT, "content", fn)
        if os.path.exists(fp):
            shutil.copy(fp, os.path.join(out, "img", fn))

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
    L = C["lore"]
    for n, l in enumerate(L):
        with open(src_file(LORE, lang, l["file"]), encoding="utf-8") as f:
            body, toc = render_lore(f.read(), links)
        # соседние главы внизу страницы (на телефоне удобно читать подряд)
        prev_l, next_l = (L[n - 1] if n else None), (L[n + 1] if n + 1 < len(L) else None)
        ru = lang == "ru"
        body += '<nav class="chapnav">' + (
            f'<a class="prev" href="{prev_l["id"]}.html"><small>{"← Предыдущая глава" if ru else "← Previous chapter"}</small><b>{html.escape(prev_l["title"])}</b></a>' if prev_l else "") + (
            f'<a class="next" href="{next_l["id"]}.html"><small>{"Следующая глава →" if ru else "Next chapter →"}</small><b>{html.escape(next_l["title"])}</b></a>' if next_l else
            f'<a class="next" href="../lore.html"><small>{"Это последняя глава" if ru else "This is the last chapter"}</small><b>{"Весь лор" if ru else "All lore"}</b></a>') + '</nav>'

        toc_html = "".join(f'<a class="h{lv}" href="#{i}">{t}</a>' for lv, t, i in toc if lv <= 2 or len(toc) < 40)
        write(os.path.join("lore", f"{l['id']}.html"),
              PAGE.format(title=f"{l['title']} — PaxVanila", desc=html.escape(l["subtitle"]), nav=nav, toc=toc_html,
                          body=(f'<img class="lorecover" src="../img/{l["cover"]}" alt="" style="display:block;width:100%;max-width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;border-radius:10px;margin:0 0 1.2em">' if l.get("cover") else "") + body), 1)
        cards.append(f'<a href="lore/{l["id"]}.html"><div class="card">' + (f'<img class="cv" src="img/{l["cover"]}" alt="" loading="lazy" style="display:block;width:100%;max-width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;border-radius:10px;margin:0 0 12px">' if l.get("cover") else "") + f'<h3>📜 {html.escape(l["title"])}</h3><p>{html.escape(l["subtitle"])}</p></div></a>')
    # гайды (та же вёрстка, папка guides/)
    for g in C.get("guides", []):
        with open(src_file(GUIDES, lang, g["file"]), encoding="utf-8") as f:
            body, toc = render_lore(f.read(), links)
        toc_html = "".join(f'<a class="h{lv}" href="#{i}">{t}</a>' for lv, t, i in toc if lv <= 2)
        write(os.path.join("guides", f"{g['id']}.html"),
              PAGE.format(title=f"{g['title']} — PaxVanila", desc=html.escape(g["subtitle"]), nav=nav.replace('href="', 'href="../lore/'), toc=toc_html, body=body), 1)
        cards.append(f'<a href="guides/{g["id"]}.html"><div class="card"><h3>🧭 {html.escape(g["title"])}</h3><p>{html.escape(g["subtitle"])}</p></div></a>')
    if os.path.exists(os.path.join(ROOT, "content", "timeline.json")):
        U = localize(load_json("timeline.json")["ui"], lang)
        cards.insert(0, f'<a href="timeline.html"><div class="card"><h3>🗺️ {html.escape(U["title"])}</h3><p>{html.escape(U["sub"])}</p></div></a>')
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
                        '<div class="cta qz-cta"><a class="btn primary" href="quiz.html">🧩 Пройти лор-викторину</a></div>'
                        f'<div class="lorelist">{"".join(cards)}</div></div></section><footer><div class="wrap"><a href="./">← На главную</a></div></footer>',
                        idx, flags=re.S)
    lore_index = tr(lore_index)  # ссылки меню на разделы главной: #now → ./#now (иначе вели в никуда)
    lore_index = re.sub(r'(<nav class="main">.*?</nav>)', lambda m: m.group(1).replace('href="#', 'href="./#'), lore_index, flags=re.S)
    lore_index = lore_index.replace('<a href="lore.html">', '<a class="on" href="lore.html">', 1)
    write("lore.html", lore_index.replace("<title>PaxVanila</title>", "<title>Лор — PaxVanila</title>"))
    # «Новости сервера»: отдельная страница, записи рисует app.js (chronicleMain)
    X = C["chronicle"]["ui"]
    news_page = re.sub(r"<div class=\"hero\">.*?</footer>",
                       '<section class="chronhead"><div class="wrap">'
                       f'<div class="kicker">{html.escape(X["kicker"])}</div><h1>{html.escape(X["title"])}</h1>'
                       f'<p class="sub">{html.escape(X["lead"])}</p><div class="chips" id="chronState"></div>'
                       '<div id="chronNextWrap" hidden><h3 class="h3">Что впереди</h3><div class="now" id="chronNext"></div></div>'
                       '<div class="chips" id="chronCats"></div><div id="chron" class="chronlist"></div>'
                       '<p class="sub chronfoot">Записи о подготовке и важные события пишет администрация. Когда сервер откроется, рост границы, новые эпохи и сезоны появятся тут сами, '
                       'а если сервер публикует живые данные, сюда попадут и новые города, нации, войны и находки. <a href="news.xml">RSS-лента</a> для Discord-бота.</p>'
                       '</div></section><footer><div class="wrap"><a href="./">← На главную</a> · <a href="lore.html">Лор</a></div></footer>',
                       idx, flags=re.S)
    news_page = tr(news_page)  # перевод до замены ссылок меню (пары в i18n с href="#…")
    news_page = re.sub(r'(<nav class="main">.*?</nav>)', lambda m: m.group(1).replace('href="#', 'href="./#'), news_page, flags=re.S)
    news_page = news_page.replace("<title>PaxVanila</title>", f"<title>{html.escape(X['title'])} — PaxVanila</title>")
    write("news.html", news_page.replace('<a href="news.html">', '<a class="on" href="news.html">'))
    write_rss(C, lang, out)

    # лор-викторина (content/quiz.json): данные вшиты в страницу, чтобы работала и офлайн
    Q = localize(load_json("quiz.json"), lang)
    raw_ranks = load_json("quiz.json")["ui"]["ranks"]
    Q["ui"]["ranks"] = [{"min": r["min"], "text": r.get(lang) or r["ru"]} for r in raw_ranks]
    titles = {l["id"]: l["title"] for l in C["lore"]}
    for q in Q["questions"]:
        q["loreTitle"] = titles.get(q.get("lore"), "")
    qz = open(os.path.join(SRC, "quiz.html"), encoding="utf-8").read()
    qz = (qz.replace("__TITLE__", html.escape(Q["ui"]["title"])).replace("__DESC__", html.escape(Q["ui"]["intro"].split(".")[0] + "."))
          .replace("__QUIZ__", json.dumps(Q, ensure_ascii=False).replace("</", "<\\/")))
    write("quiz.html", qz)

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
    core = ["./", "index.html", "lore.html", "quiz.html", "news.html", "timeline.html", "timeline.js", "style.css", "app.js", "content.json", "icons/icon-192.png"] + \
           [f"lore/{l['id']}.html" for l in C["lore"]] + [f"guides/{g['id']}.html" for g in C.get("guides", [])] + ["privacy.html"] + \
           [f"img/{w['image'].replace('.png', '.jpg')}" for w in C["weeks"]] + ["img/about.jpg"]
    sw = open(os.path.join(SRC, "sw.js"), encoding="utf-8").read()
    sw = sw.replace("__VERSION__", lang + time.strftime("%Y%m%d%H%M")).replace("__CORE__", json.dumps(core, ensure_ascii=False))
    with open(os.path.join(out, "sw.js"), "w", encoding="utf-8") as f:
        f.write(sw)
    return C


def write_rss(C, lang, out):
    """news.xml — RSS-лента записей Летописца (для Discord-ботов вроде MonitoRSS)."""
    from email.utils import format_datetime
    from datetime import datetime, timezone, timedelta
    X, site = C["chronicle"], "https://arthurgerman533-tech.github.io/minecraft/" + ("" if lang == "ru" else lang + "/")
    items = []
    for i, e in enumerate(X["entries"][:50]):
        dt = datetime.fromisoformat(e["date"]).replace(hour=12, tzinfo=timezone(timedelta(hours=3))) - timedelta(minutes=i)
        items.append(f"<item><title>{html.escape(e['icon'] + ' ' + e['title'])}</title><link>{site}news.html#d-{e['date']}</link>"
                     f"<guid isPermaLink=\"false\">pax-{e['date']}-{html.escape(e['title'])}</guid><pubDate>{format_datetime(dt)}</pubDate>"
                     f"<description>{html.escape(e['text'])}</description></item>")
    title = X["ui"]["title"] + " — PaxVanila"
    rss = (f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>{html.escape(title)}</title><link>{site}news.html</link>'
           f'<description>{html.escape(X["ui"]["lead"])}</description><language>{lang}</language>{"".join(items)}</channel></rss>\n')
    with open(os.path.join(out, "news.xml"), "w", encoding="utf-8") as f:
        f.write(rss)


def main():
    if os.path.isdir(DOCS):
        shutil.rmtree(DOCS)
    os.makedirs(DOCS)
    open(os.path.join(DOCS, ".nojekyll"), "w").close()
    # «Отчёт для папы» — отдельное приложение (PWA) из папки papa/, просто копируем как есть
    papa_dir = os.path.join(ROOT, "papa")
    if os.path.isdir(papa_dir):
        shutil.copytree(papa_dir, os.path.join(DOCS, "papa"))
    # пластинки «Архив Монолита»: ресурспак (ссылка в server.properties) → docs/rp/, датапак → docs/files/
    disc_dir = os.path.join(ROOT, "пластинки")
    if os.path.isdir(disc_dir):
        os.makedirs(os.path.join(DOCS, "rp"), exist_ok=True); os.makedirs(os.path.join(DOCS, "files"), exist_ok=True)
        for fn in os.listdir(disc_dir):
            if fn.endswith(".zip"):
                shutil.copy(os.path.join(disc_dir, fn), os.path.join(DOCS, "rp" if "_RP_" in fn else "files", fn))
    built = {}
    for lang in LANGS:
        built[lang] = build(lang, DOCS if lang == "ru" else os.path.join(DOCS, lang))
    # сброс кэша браузера: GitHub Pages отдаёт файлы с max-age=600, поэтому к app.js, style.css и content.json добавляем ?v=<время сборки>
    import time
    ver = time.strftime("%Y%m%d%H%M%S")
    for dp, _, fns in os.walk(DOCS):
        for fn in fns:
            fp = os.path.join(dp, fn)
            if fn.endswith(".html"):
                t = open(fp, encoding="utf-8").read()
                t = re.sub(r'(src|href)="((?:\.\./)*)(app\.js|style\.css|timeline\.js)"', lambda m: f'{m.group(1)}="{m.group(2)}{m.group(3)}?v={ver}"', t)
                open(fp, "w", encoding="utf-8").write(t)
            elif fn == "app.js":
                t = open(fp, encoding="utf-8").read().replace("fetch('content.json')", f"fetch('content.json?v={ver}')")
                open(fp, "w", encoding="utf-8").write(t)

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
            if fn == "world_map_big.webp":  # подробная карта только на сайте, в APK лёгкая
                continue
            shutil.copy(os.path.join(DOCS, "img", fn), os.path.join(APP_ASSETS, "img", fn))
        make_icon(1024).convert("RGB").save(os.path.join(APP_ASSETS, "icon.png"))
        make_icon(1024, maskable=True, bg=False).save(os.path.join(APP_ASSETS, "icon_fg.png"))
    print("Готово: docs/ (сайт, русский), docs/en/ (английский) и app/assets/ (приложение).")


if __name__ == "__main__":
    main()
