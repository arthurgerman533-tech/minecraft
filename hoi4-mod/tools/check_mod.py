# -*- coding: utf-8 -*-
"""Статическая проверка мода PaxVanila без запуска игры.

Запуск:  python3 hoi4-mod/tools/check_mod.py
Проверяет скобки, локализацию (BOM, заголовок, дубли, пропущенные ключи),
ссылки фокусов друг на друга, координаты, идеи, события, флаги и портреты.
Игровые ошибки (неизвестный модификатор и т.п.) видны только в error.log самой игры.
"""
import os
import re
import sys

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "PaxVanila")
errors = []


def err(msg):
    errors.append(msg)


def files(ext):
    for dp, _, fs in os.walk(ROOT):
        for f in fs:
            if f.endswith(ext):
                yield os.path.join(dp, f)


def strip(text):
    text = re.sub(r'"[^"\n]*"', '""', text)
    return re.sub(r"#[^\n]*", "", text)


def rel(p):
    return os.path.relpath(p, ROOT)


# 1. Скобки
scripts = {}
for ext in (".txt", ".gfx", ".mod"):
    for p in files(ext):
        raw = open(p, encoding="utf-8-sig").read()
        t = strip(raw)
        scripts[p] = t
        depth = 0
        for i, ch in enumerate(t):
            depth += ch == "{"
            depth -= ch == "}"
            if depth < 0:
                err(f"{rel(p)}: лишняя '}}' около строки {t[:i].count(chr(10)) + 1}")
                break
        if depth > 0:
            err(f"{rel(p)}: не закрыто {depth} скобок")

# 2. Локализация
loc = {}
for p in files(".yml"):
    data = open(p, "rb").read()
    if not data.startswith(b"\xef\xbb\xbf"):
        err(f"{rel(p)}: нет UTF-8 BOM")
    lines = data.decode("utf-8-sig").split("\n")
    lang = os.path.basename(p).rsplit("_l_", 1)[-1][:-4]
    if lines[0].strip() != f"l_{lang}:":
        err(f"{rel(p)}: первая строка должна быть l_{lang}:")
    seen = set()
    for n, line in enumerate(lines[1:], 2):
        if not line.strip():
            continue
        m = re.match(r'^ ([A-Za-z0-9_.\-]+):\d* "(.*)"$', line)
        if not m:
            err(f"{rel(p)}:{n}: неверная строка локализации")
            continue
        if m.group(1) in seen:
            err(f"{rel(p)}:{n}: дубль ключа {m.group(1)}")
        seen.add(m.group(1))
        if lang == "russian":
            loc[m.group(1)] = m.group(2)


def need_loc(key, where):
    if key not in loc:
        err(f"{where}: нет локализации для {key}")


# 3. Идеи
ideas_txt = scripts[os.path.join(ROOT, "common/ideas/pax_ideas.txt")]
ideas = set(re.findall(r"^\t\t(\w+) = \{", ideas_txt, re.M))
for i in ideas:
    need_loc(i, "идея")
    need_loc(i + "_desc", "идея")
for p, t in scripts.items():
    for i in re.findall(r"add_ideas = (\w+)", t):
        if i not in ideas:
            err(f"{rel(p)}: add_ideas ссылается на неизвестную идею {i}")

# 4. Фокусы
all_focus = set()
for p in files(".txt"):
    if "national_focus" not in p:
        continue
    t = scripts[p]
    blocks = re.findall(r"\tfocus = \{(.*?)\n\t\}", t, re.S)
    ids, pos, excl = {}, {}, {}
    for b in blocks:
        fid = re.search(r"id = (\w+)", b).group(1)
        if fid in all_focus:
            err(f"{rel(p)}: id фокуса {fid} повторяется")
        all_focus.add(fid)
        ids[fid] = b
        xy = (re.search(r"\bx = (-?\d+)", b).group(1), re.search(r"\by = (-?\d+)", b).group(1))
        if xy in pos:
            err(f"{rel(p)}: {fid} и {pos[xy]} стоят в одной клетке {xy}")
        pos[xy] = fid
        need_loc(fid, rel(p))
        need_loc(fid + "_desc", rel(p))
        ex = re.search(r"mutually_exclusive = \{([^}]*)\}", b)
        excl[fid] = set(re.findall(r"focus = (\w+)", ex.group(1))) if ex else set()
    for fid, b in ids.items():
        for grp in re.findall(r"prerequisite = \{([^}]*)\}", b):
            for ref in re.findall(r"focus = (\w+)", grp):
                if ref not in ids:
                    err(f"{rel(p)}: {fid} требует несуществующий фокус {ref}")
        for ref in excl[fid]:
            if ref not in ids:
                err(f"{rel(p)}: {fid} исключает несуществующий {ref}")
            elif fid not in excl[ref]:
                err(f"{rel(p)}: исключение {fid} <-> {ref} не взаимное")
        for name in re.findall(r"add_tech_bonus = \{ name = (\w+)", b):
            if name not in ids:
                err(f"{rel(p)}: tech bonus name {name} не фокус этого дерева")

# 5. События
events_txt = scripts[os.path.join(ROOT, "events/pax_events.txt")]
event_ids = set(re.findall(r"id = (pax\.\d+)", events_txt))
for e in event_ids:
    need_loc(e + ".t", "событие")
    need_loc(e + ".d", "событие")
for name in re.findall(r"name = (pax\.\d+\.\w)", events_txt):
    need_loc(name, "событие")
for p, t in scripts.items():
    for e in re.findall(r"_event = \{ id = (pax\.\d+)", t):
        if e not in event_ids:
            err(f"{rel(p)}: вызывается несуществующее событие {e}")

# 6. Решения, фракции, персонажи
dec = scripts[os.path.join(ROOT, "common/decisions/pax_decisions.txt")]
for d in re.findall(r"^\t(\w+) = \{", dec, re.M):
    need_loc(d, "решение")
    need_loc(d + "_desc", "решение")
cat = scripts[os.path.join(ROOT, "common/decisions/categories/pax_decision_categories.txt")]
for c in re.findall(r"^(\w+) = \{", cat, re.M):
    need_loc(c, "категория")
for p, t in scripts.items():
    for fct in re.findall(r"create_faction = (\w+)", t):
        need_loc(fct, rel(p))
chars = scripts[os.path.join(ROOT, "common/characters/pax_characters.txt")]
char_ids = set(re.findall(r"^\t(\w+) = \{", chars, re.M))
for c in char_ids:
    need_loc(c, "персонаж")
for p, t in scripts.items():
    for c in re.findall(r"(?:recruit|promote)_character = (\w+)", t):
        if c not in char_ids:
            err(f"{rel(p)}: неизвестный персонаж {c}")
gfx = open(os.path.join(ROOT, "interface/pax_portraits.gfx"), encoding="utf-8").read()
sprites = dict(re.findall(r'name = "(\w+)"\s*texturefile = "([^"]+)"', gfx))
for sp in re.findall(r"large = (\w+)", chars):
    if sp not in sprites:
        err(f"персонаж ссылается на спрайт {sp}, его нет в .gfx")
for sp, tex in sprites.items():
    path = os.path.join(ROOT, tex)
    if not os.path.isfile(path):
        err(f"{sp}: нет файла {tex}")
    elif Image.open(path).size != (156, 210):
        err(f"{tex}: портрет должен быть 156x210")

# 7. Скриптовые эффекты
eff = scripts[os.path.join(ROOT, "common/scripted_effects/pax_effects.txt")]
effects = set(re.findall(r"^(\w+) = \{", eff, re.M))
for p, t in scripts.items():
    for e in re.findall(r"(pax_\w+) = yes", t):
        if e not in effects:
            err(f"{rel(p)}: неизвестный scripted effect {e}")

# 8. Флаги
sizes = {"": (82, 52), "medium/": (41, 26), "small/": (10, 7)}
tags = sorted(set(re.findall(r"^\t([A-Z]{3}) = \{", eff, re.M)))
for tag in tags:
    for sub, size in sizes.items():
        for suf in ["", "_democratic", "_fascism", "_communism", "_neutrality"]:
            path = os.path.join(ROOT, "gfx/flags", sub + tag + suf + ".tga")
            if not os.path.isfile(path):
                err(f"нет флага {rel(path)}")
            elif Image.open(path).size != size:
                err(f"{rel(path)}: размер должен быть {size}")
    for key in [tag, tag + "_DEF", tag + "_ADJ"]:
        if key not in loc:
            err(f"нет названия страны {key}")

# 9. Описание мода
desc = open(os.path.join(ROOT, "descriptor.mod"), encoding="utf-8").read()
for k in ("name=", "version=", "supported_version="):
    if k not in desc:
        err(f"descriptor.mod: нет {k}")
if re.search(r"^path=", desc, re.M):
    err("descriptor.mod внутри папки мода не должен содержать path=")

tech = scripts[os.path.join(ROOT, "common/technologies/pax_lore_techs.txt")]
tech_ids = set(re.findall(r"^\t(\w+) = \{", tech, re.M))
for t in tech_ids:
    need_loc(t, "технология")
    need_loc(t + "_desc", "технология")
for ref in re.findall(r"leads_to_tech = (\w+)", tech):
    if ref not in tech_ids:
        err(f"технология ведёт к неизвестной {ref}")
bm = scripts[os.path.join(ROOT, "common/bookmarks/pax_bookmarks.txt")]
for k in re.findall(r"(?:name|desc|history) = (PAX_BM_\w+)", bm):
    need_loc(k, "закладка")
for era in re.findall(r"^(pax_setup_\d+) = \{", eff, re.M):
    if not re.search(era + r" = yes", scripts[os.path.join(ROOT, "common/on_actions/pax_on_actions.txt")]):
        err(f"{era} не вызывается из on_startup")
for c in sorted(set(re.findall(r"set_cosmetic_tag = (\w+)", eff))):
    need_loc(c, "косметический тег")
    for sub, size in sizes.items():
        path = os.path.join(ROOT, "gfx/flags", sub + c + ".tga")
        if not os.path.isfile(path) or Image.open(path).size != size:
            err(f"нет или неверный флаг {rel(path)}")
for t in re.findall(r"set_technology = \{([^}]*)\}", eff):
    for name in re.findall(r"(\w+) = 1", t):
        if name.startswith("pax_") and name not in tech_ids:
            err(f"set_technology: неизвестная технология {name}")

print(f"Технологий: {len(tech_ids)}, эпох: {len(re.findall(r'bookmark = ', bm))}")
print(f"Фокусов: {len(all_focus)}, идей: {len(ideas)}, событий: {len(event_ids)}, ключей локализации: {len(loc)}, держав: {len(tags)}")
if errors:
    print(f"ОШИБОК: {len(errors)}")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("Ошибок нет.")
