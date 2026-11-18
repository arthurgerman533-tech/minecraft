#!/usr/bin/env python3
"""Выгрузка реальных городов Towny для карты на сайте и в приложении.

Запуск (с компьютера, где лежит сервер):
    python3 tools/towny_map.py server/plugins/Towny/data
    python3 tools/build_site.py

Читает плоские файлы Towny (towns/*.txt, nations/*.txt, townblocks/<мир>/*.data)
и пишет content/map_towns.json: имя города, нация, точка спавна города,
цвет нации и список занятых чанков. Никаких игроков, казны и других личных
данных в файл не попадает. Если Towny хранит данные в MySQL/H2, этот
скрипт не подойдёт: нужен flatfile (database.yml → database_load: flatfile).
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "content", "map_towns.json")
WORLD = "world"


def read_kv(path):
    d = {}
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.rstrip("\n").split("=", 1)
                    d[k.strip()] = v.strip()
    except OSError:
        pass
    return d


def color_of(d):
    for k in ("mapColorHexCode", "mapColor", "color"):
        v = d.get(k, "").lstrip("#")
        if len(v) == 6:
            try:
                int(v, 16)
                return "#" + v.lower()
            except ValueError:
                pass
    return ""


def main(data_dir):
    towns_dir = os.path.join(data_dir, "towns")
    if not os.path.isdir(towns_dir):
        sys.exit(f"Нет папки {towns_dir}. Укажи путь к plugins/Towny/data.")
    nations = {}
    nd = os.path.join(data_dir, "nations")
    if os.path.isdir(nd):
        for fn in os.listdir(nd):
            if fn.endswith(".txt"):
                d = read_kv(os.path.join(nd, fn))
                nations[d.get("name", fn[:-4])] = color_of(d)

    towns = {}
    for fn in os.listdir(towns_dir):
        if not fn.endswith(".txt"):
            continue
        d = read_kv(os.path.join(towns_dir, fn))
        name = d.get("name", fn[:-4])
        nation = d.get("nation", "")
        x = z = None
        sp = d.get("spawn", "").split(",")
        if len(sp) >= 4 and sp[0] == WORLD:
            try:
                x, z = round(float(sp[1])), round(float(sp[3]))
            except ValueError:
                pass
        if x is None:
            hb = d.get("homeBlock", "").split(",")
            if len(hb) >= 3 and hb[0] == WORLD:
                try:
                    x, z = int(hb[1]) * 16 + 8, int(hb[2]) * 16 + 8
                except ValueError:
                    pass
        towns[name] = {"name": name, "nation": nation, "x": x, "z": z,
                       "color": color_of(d) or nations.get(nation, ""), "blocks": []}

    tb = os.path.join(data_dir, "townblocks", WORLD)
    if os.path.isdir(tb):
        for fn in os.listdir(tb):
            if not fn.endswith(".data"):
                continue
            parts = fn[:-5].split("_")
            if len(parts) < 2:
                continue
            try:
                cx, cz = int(parts[0]), int(parts[1])
            except ValueError:
                continue
            t = read_kv(os.path.join(tb, fn)).get("town", "")
            if t in towns:
                towns[t]["blocks"].append([cx, cz])

    out = [t for t in towns.values() if t["x"] is not None or t["blocks"]]
    for t in out:
        if t["x"] is None:
            t["x"] = t["blocks"][0][0] * 16 + 8
            t["z"] = t["blocks"][0][1] * 16 + 8
    out.sort(key=lambda t: t["name"].lower())
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"generated": time.strftime("%Y-%m-%d %H:%M"), "towns": out}, f, ensure_ascii=False, indent=1)
    print(f"Записано {len(out)} городов в content/map_towns.json. Теперь запусти tools/build_site.py.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "server", "plugins", "Towny", "data"))
