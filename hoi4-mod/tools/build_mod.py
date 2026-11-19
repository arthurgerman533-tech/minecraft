# -*- coding: utf-8 -*-
"""Сборка мода PaxVanila для Hearts of Iron IV.

Запуск:  python3 hoi4-mod/tools/build_mod.py
Результат: hoi4-mod/PaxVanila/ (папка мода) и hoi4-mod/PaxVanila.mod (файл для лаунчера).
Все тексты и цифры лежат в pax_data.py. Нужен Pillow (pip install pillow) для флагов и портретов.
"""
import math
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pax_data as D  # noqa: E402

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, D.MOD_NAME)
IDEOLOGIES = ["democratic", "fascism", "communism", "neutrality"]

LOC = {}  # ключ -> текст (русский; английская копия получает те же строки)
LOC_REPLACE = {}  # ключи, которые перекрывают ванильные (названия стран)


def w(rel, text, bom=False):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8-sig" if bom else "utf-8", newline="\n") as f:
        f.write(text)


def indent(text, n):
    pad = "\t" * n
    return "\n".join(pad + line if line.strip() else line for line in text.strip("\n").split("\n"))


def modifier_block(mod, n):
    lines = [f"{k} = {v}" for k, v in mod.items()]
    return indent("modifier = {\n" + indent("\n".join(lines), 1) + "\n}", n)


# ---------------------------------------------------------------------------
# Описание мода
# ---------------------------------------------------------------------------
def build_descriptor():
    body = (
        f'version="{D.MOD_VERSION}"\n'
        'tags={\n\t"Alternative History"\n\t"National Focuses"\n\t"Events"\n}\n'
        f'name="{D.MOD_NAME}"\n'
        'picture="thumbnail.png"\n'
        'supported_version="1.*"\n'
    )
    w("descriptor.mod", body)
    outer = body + f'path="mod/{D.MOD_NAME}"\n'
    with open(os.path.join(ROOT, f"{D.MOD_NAME}.mod"), "w", encoding="utf-8", newline="\n") as f:
        f.write(outer)


# ---------------------------------------------------------------------------
# Идеи (национальные духи)
# ---------------------------------------------------------------------------
def idea_block(iid, mod):
    return (
        f"{iid} = {{\n"
        "\tallowed = { always = no }\n"
        "\tallowed_civil_war = { always = yes }\n"
        "\tremoval_cost = -1\n"
        f"{modifier_block(mod, 1)}\n"
        "}"
    )


def build_ideas():
    blocks = []
    for idea in D.GENERIC_IDEAS + D.NATIONAL_IDEAS:
        blocks.append(idea_block(idea["id"], idea["modifier"]))
        LOC[idea["id"]] = idea["name"]
        LOC[idea["id"] + "_desc"] = idea["desc"]
    for tag, p in D.POWERS.items():
        s = p["spirit"]
        blocks.append(idea_block(s["id"], s["modifier"]))
        LOC[s["id"]] = s["name"]
        LOC[s["id"] + "_desc"] = s["desc"]
        h = D.HERITAGE[tag]
        blocks.append(idea_block(f"PAX_her_{tag}", h["modifier"]))
        LOC[f"PAX_her_{tag}"] = f"Наследие: {h['name']}"
        LOC[f"PAX_her_{tag}_desc"] = h["desc"]
        fa = D.FAITH[tag]
        blocks.append(idea_block(f"PAX_fai_{tag}", fa["modifier"]))
        LOC[f"PAX_fai_{tag}"] = f"Вера: {fa['name']}"
        LOC[f"PAX_fai_{tag}_desc"] = fa["desc"]
    text = "ideas = {\n\tcountry = {\n" + "\n\n".join(indent(b, 2) for b in blocks) + "\n\t}\n}\n"
    w("common/ideas/pax_ideas.txt", text)


# ---------------------------------------------------------------------------
# Деревья фокусов
# ---------------------------------------------------------------------------
def focus_block(fid, f, x, y, prereq_ids, excl_ids, effect):
    lines = [f"id = {fid}", f"icon = {f['icon']}", f"x = {x}", f"y = {y}", f"cost = {f['cost']}"]
    for group in prereq_ids:
        lines.append("prerequisite = { " + " ".join(f"focus = {g}" for g in group) + " }")
    if excl_ids:
        lines.append("mutually_exclusive = { " + " ".join(f"focus = {e}" for e in excl_ids) + " }")
    lines.append("available_if_capitulated = no")
    lines.append("ai_will_do = { factor = 10 }")
    lines.append("completion_reward = {\n" + indent(effect, 1) + "\n}")
    return "focus = {\n" + indent("\n".join(lines), 1) + "\n}"


def build_focus_trees():
    for tag, p in D.POWERS.items():
        pre = f"{tag}_pax_"
        focuses = []

        def fx(effect, fid):
            return effect.replace("{T}", tag).replace("{F}", fid)

        for f in D.GENERIC_FOCUSES:
            fid = pre + f["key"]
            prereq = [[pre + k for k in grp] for grp in f.get("prereq", [])]
            excl = [pre + k for k in f.get("exclusive", [])]
            focuses.append(focus_block(fid, f, f["x"], f["y"], prereq, excl, fx(f["effect"], fid)))
            LOC[fid] = f["name"]
            LOC[fid + "_desc"] = f["desc"]

        roots = [[pre + "ind1", pre + "mil1", pre + "eco1"]]
        h = D.HERITAGE[tag]
        fid = pre + "her"
        eff = f"add_ideas = PAX_her_{tag}" + ("\n" + h["extra"] if h.get("extra") else "")
        focuses.append(focus_block(fid, dict(icon="GFX_goal_generic_national_unity", cost=14), 6, 1, roots, [], fx(eff, fid)))
        LOC[fid] = f"Наследие: {h['name']}"
        LOC[fid + "_desc"] = h["desc"] + " Наследие десяти держав лора, как фокус «her» на сервере PaxVanila."

        fa = D.FAITH[tag]
        fid = pre + "fai"
        focuses.append(focus_block(fid, dict(icon="GFX_goal_generic_propaganda", cost=14), 8, 1, roots, [], f"add_ideas = PAX_fai_{tag}"))
        LOC[fid] = f"Государственная вера: {fa['name']}"
        LOC[fid + "_desc"] = fa["desc"]

        base_x = 10
        for f in D.NATIONAL[tag]:
            fid = pre + f["key"]
            prereq = [[pre + k for k in grp] for grp in f.get("prereq", [])]
            excl = [pre + k for k in f.get("exclusive", [])]
            focuses.append(focus_block(fid, f, base_x + f["x"], f["y"], prereq, excl, fx(f["effect"], fid)))
            LOC[fid] = f["name"]
            LOC[fid + "_desc"] = f["desc"]

        text = (
            "focus_tree = {\n"
            f"\tid = pax_{tag}_focus_tree\n"
            "\tcountry = {\n\t\tfactor = 0\n"
            f"\t\tmodifier = {{ add = 100 tag = {tag} }}\n"
            "\t}\n"
            "\tdefault = no\n"
            "\treset_on_civilwar = no\n\n"
            + "\n\n".join(indent(b, 1) for b in focuses)
            + "\n}\n"
        )
        w(f"common/national_focus/pax_{tag}.txt", text)


# ---------------------------------------------------------------------------
# Лидеры
# ---------------------------------------------------------------------------
def build_characters():
    blocks = []
    sprites = []
    for tag, p in D.POWERS.items():
        L = p["leader"]
        blocks.append(
            f"{L['id']} = {{\n"
            f"\tname = {L['id']}\n"
            f"\tportraits = {{ civilian = {{ large = GFX_portrait_{L['id']} }} }}\n"
            "\tcountry_leader = {\n"
            f"\t\tideology = {L['ideology']}\n"
            f"\t\tdesc = {L['id']}_desc\n"
            '\t\texpire = "1965.1.1.1"\n'
            "\t\tid = -1\n"
            "\t}\n}"
        )
        LOC[L["id"]] = L["name"]
        LOC[L["id"] + "_desc"] = L["desc"]
        sprites.append(
            "\tspriteType = {\n"
            f'\t\tname = "GFX_portrait_{L["id"]}"\n'
            f'\t\ttexturefile = "gfx/leaders/PAX/{L["id"]}.tga"\n'
            "\t}"
        )
    w("common/characters/pax_characters.txt", "characters = {\n" + "\n\n".join(indent(b, 1) for b in blocks) + "\n}\n")
    w("interface/pax_portraits.gfx", "spriteTypes = {\n" + "\n".join(sprites) + "\n}\n")


# ---------------------------------------------------------------------------
# Стартовая расстановка, события, решения
# ---------------------------------------------------------------------------
def build_setup():
    parts = []
    for tag, p in D.POWERS.items():
        L = p["leader"]
        pops = " ".join(f"{k} = {v}" for k, v in p["popularities"].items())
        parts.append(
            f"{tag} = {{\n"
            f"\tset_popularities = {{ {pops} }}\n"
            f"\tset_politics = {{ ruling_party = {p['ruling']} elections_allowed = {'yes' if p['ruling'] == 'democratic' else 'no'} }}\n"
            f"\trecruit_character = {L['id']}\n"
            f"\tpromote_character = {L['id']}\n"
            f"\tadd_ideas = {p['spirit']['id']}\n"
            "\tset_country_flag = pax_power\n"
            f"\tset_country_flag = pax_bloc_{p['bloc']}\n"
            "}"
        )
    effects = (
        "# Стартовая расстановка мира PaxVanila. Вызывается из on_startup.\n"
        "pax_setup_world = {\n"
        "\tset_variable = { var = global.pax_guardians value = 2 }\n"
        "\tset_variable = { var = global.pax_cracks value = 1 }\n"
        + "\n".join(indent(x, 1) for x in parts)
        + "\n}\n"
    )
    w("common/scripted_effects/pax_effects.txt", effects)

    on_actions = """on_actions = {
	on_startup = {
		effect = {
			pax_setup_world = yes
			every_country = {
				limit = { is_ai = no }
				news_event = { id = pax.1 days = 1 }
			}
		}
	}
	# ROOT объявляет войну, FROM это цель. Война двух великих держав у башни
	# роняет одного из двух оставшихся Стражей, как в 1944 и 1962 годах по лору.
	on_declare_war = {
		effect = {
			if = {
				limit = {
					is_major = yes
					FROM = { is_major = yes }
					OR = {
						has_country_flag = pax_power
						FROM = { has_country_flag = pax_power }
					}
					check_variable = { global.pax_guardians > 0 }
				}
				subtract_from_variable = { var = global.pax_guardians value = 1 }
				add_to_variable = { var = global.pax_cracks value = 1 }
				every_country = {
					limit = { is_ai = no }
					news_event = { id = pax.10 days = 1 }
				}
				if = {
					limit = { check_variable = { global.pax_guardians < 1 } }
					set_global_flag = pax_seal_cracked
					every_country = {
						limit = { is_ai = no }
						news_event = { id = pax.11 days = 7 }
					}
				}
			}
		}
	}
}
"""
    w("common/on_actions/pax_on_actions.txt", on_actions)

    events = """add_namespace = pax

# Вступление
news_event = {
	id = pax.1
	title = pax.1.t
	desc = pax.1.d
	is_triggered_only = yes
	option = { name = pax.1.a }
}

# Приглашение в Союз PAX (FROM = Ромея)
country_event = {
	id = pax.2
	title = pax.2.t
	desc = pax.2.d
	is_triggered_only = yes
	option = {
		name = pax.2.a
		ai_chance = { factor = 80 }
		FROM = { add_to_faction = ROOT }
	}
	option = {
		name = pax.2.b
		ai_chance = { factor = 20 }
		add_political_power = 25
	}
}

# Приглашение в Степной Пакт (FROM = Северное Царство)
country_event = {
	id = pax.3
	title = pax.3.t
	desc = pax.3.d
	is_triggered_only = yes
	option = {
		name = pax.3.a
		ai_chance = { factor = 80 }
		FROM = { add_to_faction = ROOT }
	}
	option = {
		name = pax.3.b
		ai_chance = { factor = 20 }
		add_political_power = 25
	}
}

# Пал Страж
news_event = {
	id = pax.10
	title = pax.10.t
	desc = pax.10.d
	is_triggered_only = yes
	option = { name = pax.10.a }
}

# Стражей больше нет
news_event = {
	id = pax.11
	title = pax.11.t
	desc = pax.11.d
	is_triggered_only = yes
	option = { name = pax.11.a }
}

# Пробуждение Стража-7
news_event = {
	id = pax.12
	title = pax.12.t
	desc = pax.12.d
	is_triggered_only = yes
	option = { name = pax.12.a }
}
"""
    w("events/pax_events.txt", events)
    LOC.update({
        "pax.1.t": "Мир между Великими войнами",
        "pax.1.d": "1936 год. Прошло восемнадцать лет после Первой Великой войны. В 1914 году молния ударила в Монолит на 0, 0, и на башне появилась первая трещина, ровно на уровне шестой строки. Из шести Стражей у входа пали четверо. Двое ещё стоят.\\n\\nНа западе Ромея, Карфаген, Эллада, Галлия и Островной Союз помнят клятву PAX. На востоке Германский Рейх считает обиды, Северное Царство ждёт зимы, а Дакия, Орда и Скифия смотрят на степь. Летописцы Форума пишут: «Законы всегда отстают от оружия».\\n\\nЭтот мир взят из лора сервера PaxVanila.",
        "pax.1.a": "Пусть всё будет записано.",
        "pax.2.t": "Договор у Монолита",
        "pax.2.d": "[From.GetNameDefCap] зовёт нас в Союз PAX. Как в 251 году, державы запада обещают не воевать друг с другом и вместе хранить печать у башни.",
        "pax.2.a": "Мы даём клятву PAX.",
        "pax.2.b": "У нас свой путь.",
        "pax.3.t": "Курултай победителей",
        "pax.3.d": "[From.GetNameDefCap] собирает восточные державы в степи. Так рождается Степной Пакт.",
        "pax.3.a": "Мы едем на Курултай.",
        "pax.3.b": "Степь подождёт.",
        "pax.10.t": "Гроза над Монолитом",
        "pax.10.d": "Великие державы снова воюют. Снаряд разорвался у стен башни, и ещё один Страж пал. Летописцы Форума записали новую трещину в шестом ряду камней.",
        "pax.10.a": "Законы опять отстали от оружия.",
        "pax.11.t": "Стражей больше нет",
        "pax.11.d": "У входа в Монолит остался только пустой постамент. Никто не знает, что глубоко под башней перед дверью в зал Печати стоит седьмой голем с медным сердцем. Ромейские инженеры уже ищут дорогу вниз.",
        "pax.11.a": "Печать трещит.",
        "pax.12.t": "Пробуждение",
        "pax.12.d": "Ромейские инженеры спустились под Монолит и нашли седьмого голема. Когда к нему подвели ток, его глаза зажглись медным светом. Первое слово Стража-7 было «PAX».",
        "pax.12.a": "Он помнит, как это заканчивается.",
    })

    categories = """PAX_monolith_category = {
	allowed = { OR = { original_tag = ITA original_tag = SOV } }
	visible = { has_global_flag = pax_seal_cracked }
}
"""
    w("common/decisions/categories/pax_decision_categories.txt", categories)
    decisions = """PAX_monolith_category = {
	PAX_project_seven = {
		allowed = { original_tag = ITA }
		available = { has_global_flag = pax_seal_cracked }
		cost = 150
		fire_only_once = yes
		complete_effect = {
			add_ideas = PAX_idea_guardian_seven
			set_global_flag = pax_seven_awake
			every_country = {
				limit = { is_ai = no }
				news_event = { id = pax.12 days = 1 }
			}
		}
		ai_will_do = { factor = 10 }
	}
	PAX_steal_blueprints = {
		allowed = { original_tag = SOV }
		available = { has_global_flag = pax_seven_awake }
		cost = 100
		fire_only_once = yes
		complete_effect = {
			add_ideas = PAX_idea_kurultai_mind
		}
		ai_will_do = { factor = 10 }
	}
}
"""
    w("common/decisions/pax_decisions.txt", decisions)
    LOC.update({
        "PAX_monolith_category": "Монолит",
        "PAX_monolith_category_desc": "Все шесть Стражей у входа пали. Под башней кто-то ждёт.",
        "PAX_project_seven": "Проект «Седьмой»",
        "PAX_project_seven_desc": "Спуститься под Монолит и разбудить седьмого голема.",
        "PAX_steal_blueprints": "Украсть чертежи Седьмого",
        "PAX_steal_blueprints_desc": "Разведка Пакта знает, что Ромея разбудила машину. Мы построим свою и назовём её Курултай.",
    })
    LOC.update(D.FACTIONS)


# ---------------------------------------------------------------------------
# Названия стран (перекрывают ванильные ключи)
# ---------------------------------------------------------------------------
def build_country_names():
    for tag, p in D.POWERS.items():
        for key in [tag] + [f"{tag}_{i}" for i in IDEOLOGIES]:
            LOC_REPLACE[key] = p["name"]
            LOC_REPLACE[key + "_DEF"] = p["name"]
            LOC_REPLACE[key + "_ADJ"] = p["adj"]


def write_loc():
    def dump(lang, data):
        lines = [f"l_{lang}:"]
        for k, v in data.items():
            v = v.replace('"', "'")
            lines.append(f' {k}:0 "{v}"')
        return "\n".join(lines) + "\n"

    for lang in ["russian", "english"]:
        w(f"localisation/{lang}/pax_l_{lang}.yml", dump(lang, LOC), bom=True)
        w(f"localisation/{lang}/replace/pax_countries_l_{lang}.yml", dump(lang, LOC_REPLACE), bom=True)


# ---------------------------------------------------------------------------
# Графика: флаги, портреты, обложка
# ---------------------------------------------------------------------------
def draw_flag(p, W=82 * 4, H=52 * 4):
    c, a = p["color"], p["accent"]
    dark = tuple(int(v * 0.55) for v in c)
    im = Image.new("RGBA", (W, H), c + (255,))
    d = ImageDraw.Draw(im)
    k = p["flag"]["kind"]
    cx, cy = W // 2, H // 2
    if k == "disc_obelisk":  # Ромея: золотой диск и чёрный Монолит
        d.rectangle([0, 0, W // 6, H], fill=a)
        r = H * 0.32
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=a)
        d.polygon([(cx - r * 0.22, cy + r * 0.75), (cx + r * 0.22, cy + r * 0.75), (cx + r * 0.12, cy - r * 0.7), (cx, cy - r * 0.9), (cx - r * 0.12, cy - r * 0.7)], fill=(25, 20, 30))
    elif k == "crescent_band":  # Карфаген: полумесяц и диск Танит
        d.rectangle([0, H * 0.7, W, H], fill=a)
        r = H * 0.25
        d.ellipse([cx - r, cy * 0.8 - r, cx + r, cy * 0.8 + r], fill=(250, 240, 210))
        d.ellipse([cx - r * 0.6, cy * 0.8 - r * 1.25, cx + r * 1.2, cy * 0.8 + r * 0.55], fill=c)
    elif k == "waves":  # Эллада: волны
        for i in range(4):
            y0 = H * (0.2 + i * 0.2)
            pts = [(x, y0 + math.sin(x / W * math.pi * 4) * H * 0.04) for x in range(0, W + 1, 4)]
            d.line(pts, fill=a, width=int(H * 0.06))
    elif k == "tree_tricolor":  # Галлия: дуб между полос
        d.rectangle([0, 0, W // 3, H], fill=dark)
        d.rectangle([W * 2 // 3, 0, W, H], fill=dark)
        d.rectangle([cx - W * 0.02, cy, cx + W * 0.02, H * 0.85], fill=(90, 60, 30))
        r = H * 0.22
        for dx, dy in [(-0.6, 0), (0.6, 0), (0, -0.5), (0, 0.1)]:
            d.ellipse([cx + dx * r - r * 0.7, cy * 0.8 + dy * r - r * 0.7, cx + dx * r + r * 0.7, cy * 0.8 + dy * r + r * 0.7], fill=a)
    elif k == "island_stars":  # Островной Союз: острова и звёзды
        d.rectangle([0, H * 0.62, W, H], fill=(30, 70, 110))
        for i, xx in enumerate([0.2, 0.5, 0.8]):
            d.ellipse([W * xx - W * 0.08, H * 0.55, W * xx + W * 0.08, H * 0.72], fill=(240, 220, 150))
            star(d, W * xx, H * 0.3, H * 0.09, a)
    elif k == "hammer_cross":  # Германия: крест и молот Донара
        d.rectangle([0, cy - H * 0.09, W, cy + H * 0.09], fill=(20, 20, 20))
        d.rectangle([W * 0.3, 0, W * 0.3 + H * 0.18, H], fill=(20, 20, 20))
        d.rectangle([W * 0.3 - H * 0.06, cy - H * 0.2, W * 0.3 + H * 0.24, cy - H * 0.08], fill=a)
        d.rectangle([W * 0.3 + H * 0.05, cy - H * 0.1, W * 0.3 + H * 0.13, cy + H * 0.15], fill=a)
    elif k == "snow_star":  # Северное Царство: снежинка
        d.rectangle([0, 0, W, H * 0.33], fill=(240, 245, 255))
        for ang in range(0, 180, 30):
            rr = H * 0.28
            dx, dy = math.cos(math.radians(ang)) * rr, math.sin(math.radians(ang)) * rr
            d.line([(cx - dx, cy + H * 0.08 - dy), (cx + dx, cy + H * 0.08 + dy)], fill=(30, 50, 90), width=int(H * 0.04))
    elif k == "mountain":  # Дакия: медные горы
        d.polygon([(0, H), (W * 0.3, H * 0.3), (W * 0.5, H * 0.6), (W * 0.7, H * 0.2), (W, H)], fill=a)
        d.polygon([(W * 0.62, H * 0.33), (W * 0.7, H * 0.2), (W * 0.78, H * 0.33)], fill=(240, 240, 240))
    elif k == "sun_horse":  # Орда: солнце Тенгри
        d.rectangle([0, H * 0.75, W, H], fill=a)
        r = H * 0.2
        for ang in range(0, 360, 30):
            dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            d.line([(cx + dx * r, cy * 0.85 + dy * r), (cx + dx * r * 1.6, cy * 0.85 + dy * r * 1.6)], fill=a, width=int(H * 0.04))
        d.ellipse([cx - r, cy * 0.85 - r, cx + r, cy * 0.85 + r], fill=a)
    elif k == "kurgan":  # Скифия: курган и золотой олень (рога)
        d.ellipse([W * 0.1, H * 0.55, W * 0.9, H * 1.4], fill=dark)
        for s in (-1, 1):
            for i in range(3):
                d.line([(cx, H * 0.55), (cx + s * W * (0.06 + i * 0.06), H * (0.35 - i * 0.07))], fill=a, width=int(H * 0.04))
    return im


def star(d, x, y, r, color):
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
    d.polygon(pts, fill=color)


def save_tga(im, rel, size):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.resize(size, Image.LANCZOS).save(path, format="TGA")


def build_graphics():
    for tag, p in D.POWERS.items():
        big = draw_flag(p)
        for suffix in [""] + [f"_{i}" for i in IDEOLOGIES]:
            save_tga(big, f"gfx/flags/{tag}{suffix}.tga", (82, 52))
            save_tga(big, f"gfx/flags/medium/{tag}{suffix}.tga", (41, 26))
            save_tga(big, f"gfx/flags/small/{tag}{suffix}.tga", (10, 7))
        # портрет 156x210: фон цвета державы, силуэт, флаг на груди
        W, H = 156 * 2, 210 * 2
        im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        d = ImageDraw.Draw(im)
        c = p["color"]
        for yy in range(H):
            t = yy / H
            d.line([(0, yy), (W, yy)], fill=tuple(int(v * (0.9 - 0.6 * t)) for v in c) + (255,))
        sil = (28, 24, 30, 255)
        d.ellipse([W * 0.32, H * 0.18, W * 0.68, H * 0.5], fill=sil)
        d.ellipse([W * 0.08, H * 0.55, W * 0.92, H * 1.25], fill=sil)
        fl = big.resize((int(W * 0.3), int(W * 0.3 * 52 / 82)))
        im.paste(fl, (int(W * 0.35), int(H * 0.72)))
        im = im.filter(ImageFilter.SMOOTH)
        save_tga(im, f"gfx/leaders/PAX/{p['leader']['id']}.tga", (156, 210))
    # обложка для лаунчера: 10 флагов сеткой 3x4
    thumb = Image.new("RGB", (256, 256), (20, 18, 24))
    for i, tag in enumerate(D.POWERS):
        fl = draw_flag(D.POWERS[tag]).resize((78, 50), Image.LANCZOS).convert("RGB")
        row, col = divmod(i, 3)
        x0 = 5 + col * 83 if row < 3 else 89
        thumb.paste(fl, (x0, 12 + row * 60))
    thumb.save(os.path.join(OUT, "thumbnail.png"))


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    build_descriptor()
    build_ideas()
    build_focus_trees()
    build_characters()
    build_setup()
    build_country_names()
    write_loc()
    build_graphics()
    n = sum(len(fs) for _, _, fs in os.walk(OUT))
    print(f"Готово: {OUT} ({n} файлов, {len(LOC)} строк локализации)")


if __name__ == "__main__":
    main()
