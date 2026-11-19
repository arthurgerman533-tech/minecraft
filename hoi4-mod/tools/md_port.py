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
                techs.append(dict(id="pax_md_" + name, src=name, year=int(ys.group(1)) if ys else 2000, eff=eff))
    return techs

def tech_block(t):
    body = "\n".join(f"\t{k} = {v}" for k, v in t["eff"])
    return (f"{t['id']} = {{\n{body}\n\tresearch_cost = 1\n\tstart_year = {t['year']}\n"
            f"\tallow = {{ always = no }}\n\tai_will_do = {{ factor = 0 }}\n}}")

def pretty(t):
    return "MD: " + t["src"].replace("_", " ")
