"""Безопасный перенос эффектов техов Millennium Dawn (промышленность, пехота, электроника).
Берутся только числовые модификаторы, которые есть в ванили; всё MD-специфичное отбрасывается.
Техи скрытые (без папки), выдаются эпохам 2041/2096 через set_technology."""
import os, re
SRC = os.path.join(os.path.dirname(__file__), "md_src")
OK = {
 "industrial_capacity_factory","industrial_capacity_dockyard","production_factory_max_efficiency_factor",
 "production_factory_start_efficiency_factor","production_factory_efficiency_gain_factor",
 "line_change_production_efficiency_factor","industry_repair_factor","production_speed_buildings_factor",
 "production_speed_industrial_complex_factor","production_speed_infrastructure_factor",
 "research_speed_factor","conversion_cost_civ_to_mil_factor","consumer_goods_factor",
 "army_attack_factor","army_defence_factor","army_org_factor","max_dig_in","recon_factor",
 "supply_consumption_factor","experience_gain_army_factor","army_speed_factor",
 "air_attack_factor","naval_attack_factor","decryption","encryption","industry_free_repair_factor",
 "local_resources_oil_factor","local_resources_aluminium_factor","local_resources_rubber_factor",
 "local_resources_tungsten_factor","local_resources_steel_factor","local_resources_chromium_factor",
}

def _blocks(s):
    depth = 0; out = []; name = None; start = 0
    for i, ch in enumerate(s):
        if ch == "{":
            if depth == 1:
                name = re.search(r"(\w+)\s*=\s*$", s[:i]).group(1); start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 1:
                out.append((name, s[start:i + 1]))
    return out

def load():
    techs = []
    for f in ("industry", "infantry", "engineering"):
        s = open(os.path.join(SRC, f + ".txt"), encoding="utf-8-sig").read()
        for name, b in _blocks(s):
            eff = []
            for line in b.split("\n"):
                m = re.match(r"^\t\t(\w+)\s*=\s*(-?[\d.]+)\s*(#.*)?$", line)
                if m and m.group(1) in OK:
                    eff.append((m.group(1), m.group(2)))
            ys = re.search(r"start_year\s*=\s*(\d+)", b)
            if eff:
                techs.append(dict(file=f, id="pax_md_" + name, src=name, year=int(ys.group(1)) if ys else 2000, eff=eff))
    return techs

CATS = {"industry": ("PAX_md_industry", "Технологии MD: промышленность", "Industry"),
        "infantry": ("PAX_md_infantry", "Технологии MD: пехота", "Infantry"),
        "engineering": ("PAX_md_electronics", "Технологии MD: электроника", "Electronics")}


def tech_block(t, x=0, y=0):
    body = "\n".join(f"\t{k} = {v}" for k, v in t["eff"])
    return (f"{t['id']} = {{\n{body}\n\tresearch_cost = 1\n\tstart_year = {t['year']}\n"
            f"\tallow = {{ always = no }}\n\tai_will_do = {{ factor = 0 }}\n}}")


LAYOUT = {  # папка WA: (файлы MD, y первой строки, число колонок)
    "industry_folder": (("industry", "infantry"), 1250, 13),
    "electronics_folder": (("engineering",), 1450, 6),
}
GRID_X, GRID_Y = 100, 100


def tree_positions():
    """id -> (папка, x, y) в пикселях внутри окна папки."""
    out = {}
    ts = load()
    for folder, (files, y0, cols) in LAYOUT.items():
        sel = sorted([t for t in ts if t["file"] in files], key=lambda t: (t["year"], t["id"]))
        for i, t in enumerate(sel):
            out[t["id"]] = (folder, 100 + (i % cols) * 90, y0 + (i // cols) * GRID_Y)
    return out


def visible_block(t, folder):
    body = "\n".join(f"\t{k} = {v}" for k, v in t["eff"])
    return (f"{t['id']} = {{\n{body}\n\tresearch_cost = 2\n\tstart_year = {t['year']}\n"
            f"\tfolder = {{\n\t\tname = {folder}\n\t\tposition = {{ x = 0 y = 0 }}\n\t}}\n"
            f"\tai_will_do = {{ factor = 0 }}\n}}")


def pretty(t):
    return "MD: " + t["src"].replace("_", " ")


def decisions(w, LOC, indent):
    """Скрытые техи MD покупаются как решения (родное дерево исследований требует своего интерфейса)."""
    cats = "\n".join(f"{c} = {{\n\ticon = generic_research\n\tvisible = {{ is_ai = no }}\n}}" for c, _, _ in CATS.values())
    w("common/decisions/categories/pax_md_categories.txt", cats + "\n")
    out = {c: [] for c, _, _ in CATS.values()}
    for c, ru, en in CATS.values():
        LOC[c] = ru
        LOC[c + "_desc"] = "Технологии из Millennium Dawn. Покупаются за политическую власть, эффекты постоянные."
    for t in load():
        c = CATS[t["file"]][0]
        did = "PAX_buy_" + t["id"]
        cost = 25 + max(0, t["year"] - 1985) // 2
        out[c].append(f"{did} = {{\n\ticon = generic_research\n"
                   f"\tvisible = {{ is_ai = no NOT = {{ has_tech = {t['id']} }} }}\n"
                   f"\tcost = {cost}\n\tfire_only_once = yes\n"
                   f"\tcomplete_effect = {{ set_technology = {{ {t['id']} = 1 }} }}\n\tai_will_do = {{ factor = 0 }}\n}}")
        LOC[did] = pretty(t)
        LOC[did + "_desc"] = "Технология Millennium Dawn: " + pretty(t)[4:] + "."
    w("common/decisions/pax_md_decisions.txt", "\n".join(f"{c} = {{\n" + "\n\n".join(indent(d, 1) for d in ds) + "\n}" for c, ds in out.items()) + "\n")
