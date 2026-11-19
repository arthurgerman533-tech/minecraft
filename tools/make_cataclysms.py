#!/usr/bin/env python3
"""Справочник катаклизмов для слоя «Недавние катаклизмы» на карте сайта.

Источник — weather_for_map.json, который выдаёт генератор датапака погоды
(weather/make_weather_v2.py, датапак PaxVanila_Cataclysms_v2). Копия лежит в content/src/.
Скрипт добавляет английский перевод и пишет content/cataclysms.json ({ru, en} в полях).

    python3 tools/make_cataclysms.py [content/src/weather_for_map.json]
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "content", "src", "weather_for_map.json")

EN = {  # key: (name, where)
    "storm": ("Thunderstorm", "Earth: everywhere, stronger on peaks above Y 110"),
    "blizzard": ("Blizzard", "Earth: everywhere under open sky"),
    "drought": ("Drought", "Earth: everywhere, damage in deserts"),
    "sandstorm": ("Sandstorm", "Earth: deserts and badlands (desert, badlands, Terralith deserts)"),
    "quake": ("Earthquake", "Earth: everywhere, cave-ins in mines below Y 50"),
    "meteor": ("Star shower", "Earth: near players under open sky"),
    "ash": ("Ash Night", "Earth: everywhere, a pillar of fire over the Monolith at 0,0"),
    "flood": ("Great Storm", "Earth: oceans, rivers, beaches"),
    "fog": ("Fog of the Nameless", "Earth: everywhere"),
    "aurora": ("Northern Lights", "Earth: everywhere under open sky"),
    "flare": ("Solar flare", "Moon and Mars, surface"),
    "meteorstorm": ("Meteor storm", "Moon and Mars"),
    "duststorm": ("Martian dust storm", "Mars"),
    "dustdevil": ("Dust devils", "Mars"),
    "moonquake": ("Moonquake", "Moon"),
    "lunarnight": ("Lunar night", "Moon"),
    "magstorm": ("Magnetic storm", "Moon, Mars and an aurora over Earth"),
    "comet": ("Comet", "Earth, Moon, Mars (fragments fall in space)"),
}
# где катаклизм бьёт на карте Мира 1: zone — клетки из world_zones.json, point — точка, all — весь мир
AREA = {"storm": "zone:peaks", "blizzard": "zone:snow", "sandstorm": "zone:desert", "flood": "zone:water",
        "drought": "zone:desert", "ash": "point:0,0"}
# в каких мирах бывает космическое событие
SPACE = {"flare": ["moon", "mars"], "meteorstorm": ["moon", "mars"], "duststorm": ["mars"], "dustdevil": ["mars"],
         "moonquake": ["moon"], "lunarnight": ["moon"], "magstorm": ["moon", "mars", "earth"], "comet": ["earth", "moon", "mars"]}

W = json.load(open(SRC, encoding="utf-8"))
out = {"_comment": "Создано tools/make_cataclysms.py из " + W.get("pack", "") + " (weather_for_map.json). Руками не править.",
       "pack": W.get("pack", ""), "safe_zone": W.get("safe_zone"),
       "rules": {"ru": "; ".join(W.get("rules", [])),
                 "en": "blocks are never broken; damage only above 5 hearts; newcomers are safe for the first 48 h"},
       "events": []}
for e in W["events"]:
    k = e["key"]; n_en, w_en = EN.get(k, (e["name"], e["where"]))
    out["events"].append({"n": e["id"], "id": k, "icon": e["icon"], "color": e["color"],
                          "world": e["world"], "worlds": SPACE.get(k, ["earth"]), "area": AREA.get(k, "all"),
                          "dur": e["duration_sec"], "weight": e["weight"],
                          "name": {"ru": e["name"], "en": n_en}, "where": {"ru": e["where"], "en": w_en}})
p = os.path.join(ROOT, "content", "cataclysms.json")
json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("записано", p, len(out["events"]), "событий")
