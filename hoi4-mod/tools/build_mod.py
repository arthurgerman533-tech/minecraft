# -*- coding: utf-8 -*-
"""Сборка мода PaxVanila для Hearts of Iron IV.

Запуск:  python3 hoi4-mod/tools/build_mod.py
Результат: hoi4-mod/PaxVanila/ (папка мода) и hoi4-mod/PaxVanila.mod (файл для лаунчера).
Все тексты и цифры лежат в pax_data.py. Нужен Pillow (pip install pillow) для флагов и портретов.
"""
import math
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pax_data as D  # noqa: E402
import pax_eras as E  # noqa: E402
import family_port as F  # noqa: E402
import pax_art as A  # noqa: E402
import pax_era_focuses as EF  # noqa: E402
import pax_big as BIG
import md_port as MD  # noqa: E402
import pax_economy as ECO  # noqa: E402

BIG.extend(D)

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
FAM_REPLACE = ("history/states", "history/countries", "history/units", "history/general", "map/strategicregions")


def wa_replace_paths():
    """Вариант WA самодостаточный: в него скопированы файлы World Ablaze, поэтому нужны и его replace_path."""
    if D.BASE == "fam":  # карта и история Family старые: ванильные состояния 1.20 конфликтуют с ними
        return "".join(f'replace_path="{k}"\n' for k in FAM_REPLACE)
    if D.BASE != "wa":
        return ""
    seen, out = {"common/bookmarks"}, []
    for line in open(os.path.join(os.path.dirname(__file__), "wa_replace_paths.txt"), encoding="utf-8"):
        m = re.match(r'replace_path\s*=\s*"([^"]+)"', line.strip())
        if m:
            k = m.group(1).rstrip("/")
            if k not in seen:
                seen.add(k)
                out.append(f'replace_path="{k}"\n')
    return "".join(out)


def build_won():
    """Мод «Economic System Rework» (Wealth of Nations, workshop 3841374063) целиком: рынок, лига, гонка, сферы."""
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "won_src")
    for root, _, files in os.walk(src):
        for fn in files:
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, src).replace(os.sep, "/")
            dst = os.path.join(OUT, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(p, dst)


def build_extra_mods():
    """Только для варианта Family: Artillery Designer (3783427912) и Globe Mod (3816496697)."""
    here = os.path.dirname(os.path.abspath(__file__))
    for name in ("artdes_src", "globe_src"):
        src = os.path.join(here, name)
        for root, _, files in os.walk(src):
            for fn in files:
                p = os.path.join(root, fn)
                dst = os.path.join(OUT, os.path.relpath(p, src))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(p, dst)


def build_descriptor():
    body = (
        f'version="{D.MOD_VERSION}"\n'
        'tags={\n\t"Alternative History"\n\t"National Focuses"\n\t"Events"\n}\n'
        f'name="{D.MOD_NAME}"\n'
        'picture="thumbnail.png"\n'
        'replace_path="common/bookmarks"\n'
        + wa_replace_paths() +
        'supported_version="1.20.*"\n'
    )
    w("descriptor.mod", body)
    outer = body + f'path="mod/{D.MOD_NAME}"\n'
    with open(os.path.join(ROOT, f"{D.MOD_NAME}.mod"), "w", encoding="utf-8", newline="\n") as f:
        f.write(outer)


# ---------------------------------------------------------------------------
# Идеи (национальные духи)
# ---------------------------------------------------------------------------
def idea_block(iid, mod):
    pic = D.IDEA_PICTURES.get(iid) or D.IDEA_PICTURES.get(iid.rsplit("_", 1)[0] + "_*", "")
    return (
        f"{iid} = {{\n"
        + (f"\tpicture = {pic}\n" if pic else "")
        +
        "\tallowed = { always = no }\n"
        "\tallowed_civil_war = { always = yes }\n"
        "\tremoval_cost = -1\n"
        f"{modifier_block(mod, 1)}\n"
        "}"
    )


def build_ideas():
    for tag, p in D.POWERS.items():  # свои иконки духов (pax_art)
        D.IDEA_PICTURES[p["spirit"]["id"]] = f"pax_spirit_{tag}"
        D.IDEA_PICTURES[f"PAX_her_{tag}"] = f"pax_her_{tag}"
        D.IDEA_PICTURES[f"PAX_fai_{tag}"] = f"pax_fai_{tag}"
    blocks = []
    for idea in D.GENERIC_IDEAS + D.NATIONAL_IDEAS:
        blocks.append(idea_block(idea["id"], idea["modifier"]))
        LOC[idea["id"]] = idea["name"]
        LOC[idea["id"] + "_desc"] = idea["desc"]
    for era in E.ERAS:
        ei = era["era_idea"]
        if ei:
            D.IDEA_PICTURES[ei["id"]] = ei["picture"]
            blocks.append(idea_block(ei["id"], ei["modifier"]))
            LOC[ei["id"]] = ei["name"]
            LOC[ei["id"] + "_desc"] = ei["desc"]
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
    blocks += F.EXTRA_IDEAS  # из Family (arthur.txt, endpoint.txt)
    for ei in EF.IDEAS:
        D.IDEA_PICTURES[ei["id"]] = ei["pic"]
        blocks.append(idea_block(ei["id"], ei["modifier"]))
        LOC[ei["id"]] = ei["name"]
        LOC[ei["id"] + "_desc"] = ei["desc"]
    text = "ideas = {\n\tcountry = {\n" + "\n\n".join(indent(b, 2) for b in blocks) + "\n\t}\n}\n"
    w("common/ideas/pax_ideas.txt", text)


# ---------------------------------------------------------------------------
# Деревья фокусов
# ---------------------------------------------------------------------------
def focus_block(fid, f, x, y, prereq_ids, excl_ids, effect, allow=None):
    lines = [f"id = {fid}", f"icon = {f['icon']}", f"x = {x}", f"y = {y}", f"cost = {f['cost']}"]
    if allow:
        lines.append("allow_branch = { " + allow.replace("\n\t", " ") + " }")
    for group in prereq_ids:
        lines.append("prerequisite = { " + " ".join(f"focus = {g}" for g in group) + " }")
    if excl_ids:
        lines.append("mutually_exclusive = { " + " ".join(f"focus = {e}" for e in excl_ids) + " }")
    lines.append("available_if_capitulated = no")
    lines.append("ai_will_do = { factor = 10 }")
    lines.append("completion_reward = {\n" + indent(effect, 1) + "\n}")
    return "focus = {\n" + indent("\n".join(lines), 1) + "\n}"


def build_lore_decisions():
    """Вместо своих деревьев фокусов (у держав остаются ванильные) лорные ветки, Наследие и Вера стали решениями."""
    cats = ("PAX_lore_category = {\n\tallowed = { OR = { " +
            " ".join(f"original_tag = {tg}" for tg in D.POWERS) + " } }\n}\n")
    w("common/decisions/categories/pax_lore_categories.txt", cats)
    LOC["PAX_lore_category"] = "Лор PaxVanila"
    LOC["PAX_lore_category_desc"] = "Национальные решения вашей державы: наследие, вера, союзы и пути эпох."
    out = ["PAX_lore_category = {"]
    for tg in D.POWERS:  # пустые заглушки: у держав остаются ванильные деревья (и старые файлы версии 0.5 не мешают)
        w(f"common/national_focus/pax_{tg}.txt", "# Своих деревьев фокусов нет: у державы ванильное дерево. Лорные ветки лежат в решениях (pax_lore_decisions.txt).\n")

    def dec(tag, key, name, desc, cost, effect, prereq=None, excl=None, cond=None, once=True):
        did = f"PAX_{tag}_{key}"
        vis = [f"original_tag = {tag}"]
        if cond:
            vis.append(cond)
        for grp in (prereq or []):
            vis.append("OR = { " + " ".join(f"has_country_flag = {did_flag(tag, g)}" for g in grp) + " }")
        for e in (excl or []):
            vis.append(f"NOT = {{ has_country_flag = {did_flag(tag, e)} }}")
        vis.append(f"NOT = {{ has_country_flag = {did_flag(tag, key)} }}")
        body = (
            f"\t{did} = {{\n"
            "\t\ticon = generic_research\n"
            "\t\tallowed = { original_tag = " + tag + " }\n"
            "\t\tvisible = {\n" + "\n".join("\t\t\t" + v.replace("\n\t", " ") for v in vis) + "\n\t\t}\n"
            f"\t\tcost = {cost}\n"
            "\t\tfire_only_once = yes\n"
            "\t\tcomplete_effect = {\n"
            f"\t\t\tset_country_flag = {did_flag(tag, key)}\n"
            + indent(effect.replace("{T}", tag).replace("{F}", did), 3) + "\n"
            "\t\t}\n"
            "\t\tai_will_do = { factor = 5 }\n"
            "\t}"
        )
        out.append(body)
        LOC[did] = name
        LOC[did + "_desc"] = desc

    def did_flag(tag, key):
        return f"pax_{tag}_{key}"

    for tag, p in D.POWERS.items():
        h, fa = D.HERITAGE[tag], D.FAITH[tag]
        eff = f"add_ideas = PAX_her_{tag}" + ("\n" + h["extra"] if h.get("extra") else "")
        dec(tag, "her", f"Наследие: {h['name']}", h["desc"], 100, eff)
        dec(tag, "fai", f"Государственная вера: {fa['name']}", fa["desc"], 100, f"add_ideas = PAX_fai_{tag}")
        for f in D.NATIONAL[tag]:
            cond = None
            dec(tag, f["key"], f["name"], f["desc"], f["cost"] * 10, f["effect"],
                prereq=f.get("prereq"), excl=f.get("exclusive"), cond=EF.EARLY)
        for ef in EF.branches(tag):
            dec(tag, ef["key"], ef["name"], ef["desc"], ef["cost"] * 10, ef["effect"],
                prereq=ef["prereq"], excl=ef["exclusive"], cond=EF.COND[ef["era"]])
    w("common/decisions/pax_lore_decisions.txt", "\n\n".join(out) + "\n}\n" if False else "\n".join(out) + "\n}\n")


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
            f = dict(f, icon=f"GFX_goal_pax_{f['key']}")
            focuses.append(focus_block(fid, f, f["x"], f["y"], prereq, excl, fx(f["effect"], fid)))
            LOC[fid] = f["name"]
            LOC[fid + "_desc"] = f["desc"]

        roots = [[pre + "ind1", pre + "mil1", pre + "eco1"]]
        h = D.HERITAGE[tag]
        fid = pre + "her"
        eff = f"add_ideas = PAX_her_{tag}" + ("\n" + h["extra"] if h.get("extra") else "")
        focuses.append(focus_block(fid, dict(icon=f"GFX_goal_pax_her_{tag}", cost=14), 6, 1, roots, [], fx(eff, fid)))
        LOC[fid] = f"Наследие: {h['name']}"
        LOC[fid + "_desc"] = h["desc"] + " Наследие десяти держав лора, как фокус «her» на сервере PaxVanila."

        fa = D.FAITH[tag]
        fid = pre + "fai"
        focuses.append(focus_block(fid, dict(icon=f"GFX_goal_pax_fai_{tag}", cost=14), 8, 1, roots, [], f"add_ideas = PAX_fai_{tag}"))
        LOC[fid] = f"Государственная вера: {fa['name']}"
        LOC[fid + "_desc"] = fa["desc"]

        base_x = 10
        for f in D.NATIONAL[tag]:
            fid = pre + f["key"]
            prereq = [[pre + k for k in grp] for grp in f.get("prereq", [])]
            excl = [pre + k for k in f.get("exclusive", [])]
            f = dict(f, icon=f"GFX_goal_pax_nat_{tag}")
            allow = EF.EARLY if not prereq else None
            focuses.append(focus_block(fid, f, base_x + f["x"], f["y"], prereq, excl, fx(f["effect"], fid), allow))
            LOC[fid] = f["name"]
            LOC[fid + "_desc"] = f["desc"]

        for ef in EF.branches(tag):
            fid = f"{pre}{ef['key']}"
            prereq = [[pre + k for k in grp] for grp in ef["prereq"]]
            excl = [pre + k for k in ef["exclusive"]]
            fdict = dict(icon=f"GFX_goal_pax_nat_{tag}", cost=ef["cost"])
            focuses.append(focus_block(fid, fdict, EF.BASE_X[ef["era"]] + ef["x"], ef["y"], prereq, excl,
                                       fx(ef["effect"], fid), EF.COND[ef["era"]] if ef["root"] else None))
            LOC[fid] = ef["name"]
            LOC[fid + "_desc"] = ef["desc"]

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
    for era in E.ERAS:
        for tag, (name, ideology, _ruling, desc) in era["leaders"].items():
            cid = f"{tag}_pax_{era['id']}"
            base = D.POWERS[tag]["leader"]["id"]
            blocks.append(
                f"{cid} = {{\n\tname = {cid}\n"
                f"\tportraits = {{ civilian = {{ large = GFX_portrait_{base} }} }}\n"
                f"\tcountry_leader = {{\n\t\tideology = {ideology}\n\t\tdesc = {cid}_desc\n"
                '\t\texpire = "4000.1.1.1"\n\t\tid = -1\n\t}\n}'
            )
            LOC[cid] = name
            LOC[cid + "_desc"] = desc
    w("common/characters/pax_characters.txt", "characters = {\n" + "\n\n".join(indent(b, 1) for b in blocks) + "\n}\n")
    w("interface/pax_portraits.gfx", "spriteTypes = {\n" + "\n".join(sprites) + "\n}\n")


# ---------------------------------------------------------------------------
# Стартовая расстановка, события, решения
# ---------------------------------------------------------------------------
def build_setup():
    effects = "# Стартовая расстановка мира PaxVanila по эпохам. Вызывается из on_startup.\n\n" + era_effects()
    w("common/scripted_effects/pax_effects.txt", effects)

    on_actions = """on_actions = {
	on_startup = {
		effect = {
			# эпоха выбирается по дате закладки
			if = { limit = { date > 2095.12.31 } ITA = { pax_setup_2096 = yes } }
			else_if = { limit = { date > 2040.12.31 } ITA = { pax_setup_2041 = yes } }
			else_if = { limit = { date > 1962.1.1 } ITA = { pax_setup_1962 = yes } }
			else_if = { limit = { date > 1939.1.1 } ITA = { pax_setup_1939 = yes } }
			# «Без Азии» из Family: та же дата, но на час позже (1936.1.1.13)
			else_if = { limit = { has_start_date > 1936.1.1.12 } ITA = { pax_setup_1936e = yes } }
			else_if = { limit = { date < 1900.1.1 } ITA = { pax_setup_1241 = yes } }
			else_if = { limit = { date < 1930.1.1 } ITA = { pax_setup_1914 = yes } }
			else = { ITA = { pax_setup_1936 = yes } }
			# Как в «Family Historical MP mod»: страны вне лора под управлением ИИ
			# получают дух «Дальние земли» и не мешают игрокам. Удалите блок, если не нужно.
			every_country = {
				limit = { is_ai = yes NOT = { has_country_flag = pax_power } }
				add_ideas = PAX_far_lands
			}
			# роты Family (снайперы, миномёты, псы...) открываются скрытой технологией
			""" + ("" if D.BASE != "vanilla" else "every_country = { set_technology = { pax_family_support = 1 } }") + """
			# «Мирное небо» из Family: быстрое обучение в мирное время, пропадает с войной
			every_country = { add_ideas = PAX_peaceful_sky }
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

# Вторая Великая война: Рейх решает, идти ли на север (старт 1939)
country_event = {
	id = pax.30
	title = pax.30.t
	desc = pax.30.d
	is_triggered_only = yes
	option = {
		name = pax.30.a
		ai_chance = { factor = 70 }
		add_war_support = 0.1
		create_wargoal = { type = annex_everything target = SOV }
	}
	option = {
		name = pax.30.b
		ai_chance = { factor = 30 }
		add_political_power = 50
	}
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
    events += F.EVENTS
    events = add_event_pictures(events)
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
        "pax.30.t": "За железом на север",
        "pax.30.d": "Рейху мало земли. Железо и уголь Северного Царства лежат за границей. Генералы говорят, что армия успеет до снега. Летописцы Форума говорят, что зима всегда на стороне того, кто дома.",
        "pax.30.a": "Готовить войну с Севером.",
        "pax.30.b": "Подождать.",
        "pax.20.t": "Путеводитель PaxVanila",
        "pax.20.d": "Выберите раздел путеводителя.",
        "pax.20.a": "Выйти",
        "pax.21.d": D.GUIDE_TEXT,
    })

    categories = """PAX_monolith_category = {
	allowed = { OR = { original_tag = ITA original_tag = SOV } }
	visible = { has_global_flag = pax_seal_cracked }
}
"""
    categories += """
PAX_guide_category = {
	allowed = { always = yes }
}
"""
    w("common/decisions/categories/pax_decision_categories.txt", categories)
    decisions = """PAX_monolith_category = {
	PAX_project_seven = {
		allowed = { original_tag = ITA }
		icon = generic_research
		visible = { NOT = { has_global_flag = pax_seven_awake } }
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
		icon = generic_operation
		visible = { NOT = { has_idea = PAX_idea_kurultai_mind } }
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
    decisions += """
PAX_guide_category = {
	PAX_open_guide = {
		icon = generic_research
		fire_only_once = no
		days_re_enable = 1
		complete_effect = {
			country_event = { id = pax.20 }
		}
		ai_will_do = { factor = 0 }
	}
}
"""
    w("common/decisions/pax_decisions.txt", decisions)
    LOC.update({
        "PAX_guide_category": "Путеводитель PaxVanila",
        "PAX_guide_category_desc": "Как устроен этот мир и что даёт каждая ветка фокусов.",
        "PAX_open_guide": "Открыть путеводитель",
        "PAX_open_guide_desc": "Короткая справка по моду.",
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
START_ERAS = ("1936", "1936e")  # закладки на старте; остальные эпохи остаются в коде


def era_effects():
    out = []
    for era in E.ERAS:
        L = []
        L.append(f"set_global_flag = pax_era_{era['id']}")
        L.append(f"set_variable = {{ var = global.pax_guardians value = {era['guardians']} }}")
        L.append(f"set_variable = {{ var = global.pax_cracks value = {era['cracks']} }}")
        if era["guardians"] == 0:
            L.append("set_global_flag = pax_seal_cracked")
        if era.get("seven_awake"):
            L.append("set_global_flag = pax_seven_awake")
        techs = list(era["techs"]) + [t["id"] for t in E.LORE_TECHS if t["year"] <= era["lore_techs_until"]]
        md_year = {"2041": 2040, "2096": 2100}.get(era["id"])
        if md_year:
            techs += [t["id"] for t in MD.load() if t["year"] <= md_year]
        for tag, p in D.POWERS.items():
            lead = era["leaders"].get(tag)
            if lead:
                cid, ruling = f"{tag}_pax_{era['id']}", lead[2]
                lsub, lpic = lead[1], p["leader"]["id"]
                others = [i for i in ("democratic", "fascism", "communism", "neutrality") if i != ruling]
                pops = f"{ruling} = 55 " + " ".join(f"{o} = 15" for o in others)
            else:
                cid, ruling = p["leader"]["id"], p["ruling"]
                lsub, lpic = p["leader"]["ideology"], cid
                pops = " ".join(f"{k} = {v}" for k, v in p["popularities"].items())
            b = [f"set_popularities = {{ {pops} }}",
                 f"set_politics = {{ ruling_party = {ruling} elections_allowed = {'yes' if ruling == 'democratic' else 'no'} }}",
                 # create_country_leader работает в любой момент игры (recruit_character только в history)
                 f"create_country_leader = {{\n\tname = \"{cid}\"\n\tdesc = \"{cid}_desc\"\n"
                 f"\tpicture = \"gfx/leaders/PAX/{lpic}.tga\"\n\texpire = \"4000.1.1.1\"\n"
                 f"\tideology = {lsub}\n\ttraits = {{ }}\n}}",
                 f"add_ideas = {p['spirit']['id']}",
                 "set_country_flag = pax_power", f"set_country_flag = pax_bloc_{p['bloc']}"]
            if era["era_idea"]:
                b.append(f"add_ideas = {era['era_idea']['id']}")
            if techs:
                b.append("set_technology = {\n" + "\n".join(f"\t{t} = 1" for t in techs) + "\n}")
            if era["slots"]:
                b.append(f"add_research_slot = {era['slots']}")
            if era.get("corps"):
                b.append(f"set_cosmetic_tag = PAX_CORP_{tag}")
            if era.get("seven_awake") and tag == "ITA":
                b.append("add_ideas = PAX_idea_guardian_seven")
            if era.get("seven_awake") and tag == "SOV":
                b.append("add_ideas = PAX_idea_kurultai_mind")
            L.append(f"{tag} = {{\n" + indent("\n".join(b), 1) + "\n}")
        if era["factions"]:
            members = [t for _, (_, ms) in era["factions"].items() for t in ms]
            for t in members:
                L.append(f"{t} = {{\n\tif = {{ limit = {{ is_faction_leader = yes }} dismantle_faction = yes }}\n"
                         f"\telse_if = {{ limit = {{ is_in_faction = yes }} leave_faction = yes }}\n}}")
            for leader, (fname, ms) in era["factions"].items():
                adds = "\n".join(f"\tadd_to_faction = {m}" for m in ms if m != leader)
                L.append(f"{leader} = {{\n\tcreate_faction = {fname}\n{adds}\n}}")
        if era.get("no_asia"):
            L.append(F.no_asia_effect())
        if era.get("germany_war"):
            L.append("GER = { country_event = { id = pax.30 days = 3 } }")
        out.append(f"pax_setup_{era['id']} = {{\n" + indent("\n".join(L), 1) + "\n}\n")
    return "\n".join(out)


def build_eras_extra():
    # Технологии ветки «Наследие Предтеч»
    blocks = []
    for i, t in enumerate(E.LORE_TECHS):
        b = [f"{k} = {v}" for k, v in t["mod"].items()]
        if i + 1 < len(E.LORE_TECHS):
            b.append(f"path = {{ leads_to_tech = {E.LORE_TECHS[i + 1]['id']} research_cost_coeff = 1 }}")
        b += [f"research_cost = {t['cost']}", f"start_year = {t['year']}",
              "allow = { always = no }",  # скрытая: без клетки в дереве (нет grid box), выдаётся эпохой через set_technology
              "ai_will_do = { factor = 0 }"]
        blocks.append(f"{t['id']} = {{\n" + indent("\n".join(b), 1) + "\n}")
        LOC[t["id"]] = t["name"]
        LOC[t["id"] + "_desc"] = t["desc"]
    w("common/technologies/pax_lore_techs.txt", "technologies = {\n" + "\n\n".join(indent(b, 1) for b in blocks) + "\n}\n")

    mdt = MD.load()
    if D.BASE == "wa":  # в WA сетка дерева правится отдельно (tools/md_tree_gui.py), техи видимые
        pos = MD.tree_positions()
        w("common/technologies/pax_md_techs.txt", "technologies = {\n" + "\n\n".join(indent(MD.visible_block(t, pos[t["id"]][0]), 1) for t in mdt) + "\n}\n")
        LOC["PAX_MD_TREE_TITLE"] = "Millennium Dawn"
        tex = {"industry": "basic_machine_tools", "infantry": "fra_advanced_infantry_weapons", "engineering": "advanced_computing_machine"}
        w("interface/pax_md_techs.gfx", "spriteTypes = {\n" + "\n".join(
            f'\tspriteType = {{\n\t\tname = "GFX_{t["id"]}_medium"\n\t\ttexturefile = "gfx/interface/technologies/{tex[t["file"]]}.dds"\n\t}}' for t in mdt) + "\n}\n")
    else:
        w("common/technologies/pax_md_techs.txt", "technologies = {\n" + "\n\n".join(indent(MD.tech_block(t, 0, 0), 1) for i, t in enumerate(mdt)) + "\n}\n")
    for t in mdt:
        LOC[t["id"]] = MD.pretty(t)
        LOC[t["id"] + "_desc"] = "Технология Millennium Dawn."

    # Закладки выбора старта
    marks = []
    for era in [e for e in E.ERAS if e['id'] in START_ERAS]:
        c = []
        for tag, p in D.POWERS.items():
            lead = era["leaders"].get(tag)
            ideology = lead[2] if lead else p["ruling"]
            key = f"PAX_BM_{era['id']}_{tag}"
            minor = "" if tag in ("ITA", "GER", "SOV", "FRA", "ENG") else "\tminor = yes\n"
            c.append(f"{tag} = {{\n{minor}\thistory = {key}\n\tideology = {ideology}\n\tideas = {{ {p['spirit']['id']} }}\n\tfocuses = {{ }}\n}}")
            who = lead[0] if lead else p["leader"]["name"]
            LOC[key] = f"{p['short']}. Правитель: {who}. {E.CORPS[tag] + '.' if era.get('corps') else ''}".strip()
        c.append('"---" = { history = PAX_BM_OTHER }')
        marks.append(
            "bookmark = {\n"
            f"\tname = PAX_BM_{era['id']}\n\tdesc = PAX_BM_{era['id']}_DESC\n"
            f"\tdate = {era['date']}\n\tpicture = GFX_pax_bm_{era['id']}\n\tdefault_country = ITA\n"
            + ("\tdefault = yes\n" if era.get("default") else "")
            + indent("\n".join(c), 1) + "\n"
            "\teffect = { randomize_weather = 22345 }\n}"
        )
        LOC[f"PAX_BM_{era['id']}"] = f"{era['date'][:4]}: {era['name']}"
        LOC[f"PAX_BM_{era['id']}_DESC"] = era["desc"]
    LOC["PAX_BM_OTHER"] = "Дальние земли, о которых лор PaxVanila молчит."
    w("common/bookmarks/pax_bookmarks.txt", "bookmarks = {\n" + "\n".join(indent(m, 1) for m in marks) + "\n}\n")

    # Игра не должна заканчиваться в 1949 году
    w("common/defines/pax_defines.lua", 'NDefines.NGame.END_DATE = "4000.1.1.1"\n')


def build_country_names():
    for tag, p in D.POWERS.items():
        for key in [tag] + [f"{tag}_{i}" for i in IDEOLOGIES]:
            LOC_REPLACE[key] = p["name"]
            LOC_REPLACE[key + "_DEF"] = p["name"]
            LOC_REPLACE[key + "_ADJ"] = p["adj"]
    for tag, corp in E.CORPS.items():
        k = f"PAX_CORP_{tag}"
        LOC_REPLACE[k] = corp
        LOC_REPLACE[k + "_DEF"] = corp
        LOC_REPLACE[k + "_ADJ"] = D.POWERS[tag]["adj"]
    # советы на экране загрузки (как LOADING_TIP в «Family Historical MP mod»)
    for i, tip in enumerate(D.LOADING_TIPS):
        LOC_REPLACE[f"LOADING_TIP_{i}"] = tip


def write_loc():
    def dump(lang, data):
        lines = [f"l_{lang}:"]
        for k, v in data.items():
            v = v.replace('"', "'")
            lines.append(f' {k}:0 "{v}"')
        return "\n".join(lines) + "\n"

    import json
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "en_translations.json"), encoding="utf-8") as fh:
        EN = json.load(fh)
    missing = set()

    def to_en(data):
        out = {}
        for k, v in data.items():
            if re.search("[а-яёА-ЯЁ]", v):
                if v not in EN:
                    missing.add(v)
                v = EN.get(v, v)
            out[k] = v
        return out

    for lang in ["russian", "english"]:
        a, b = (LOC, LOC_REPLACE) if lang == "russian" else (to_en(LOC), to_en(LOC_REPLACE))
        w(f"localisation/{lang}/pax_l_{lang}.yml", dump(lang, a), bom=True)
        w(f"localisation/{lang}/replace/pax_countries_l_{lang}.yml", dump(lang, b), bom=True)
    if missing:
        print("НЕТ английского перевода:", len(missing))
        for m in sorted(missing)[:10]:
            print("  ", m[:80])


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
        corp = big.copy()
        ov = Image.new("RGBA", corp.size, (20, 0, 40, 110))
        corp = Image.alpha_composite(corp, ov)
        dc = ImageDraw.Draw(corp)
        dc.rectangle([0, 0, corp.size[0] - 1, corp.size[1] - 1], outline=(0, 255, 230, 255), width=10)
        for sub, size in (("", (82, 52)), ("medium/", (41, 26)), ("small/", (10, 7))):
            save_tga(corp, f"gfx/flags/{sub}PAX_CORP_{tag}.tga", size)
        # портрет 156x210: пиксельный правитель на фоне флага (pax_art)
        im = A.portrait(big, p["color"], p["accent"], p["flag"]["kind"], tag)
        save_tga(im, f"gfx/leaders/PAX/{p['leader']['id']}.tga", (156, 210))
        continue
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


def add_event_pictures(events):
    import re
    def sub(m):
        kind, eid = m.group(1), m.group(2)
        scene = A.EVENT_SCENES.get(eid, "monolith")
        pic = f"GFX_news_event_pax_{scene}" if kind == "news_event" else f"GFX_report_event_pax_{scene}"
        return m.group(0) + f"\tpicture = {pic}\n"
    events = re.sub(r"\tpicture = [^\n]*\n", "", events)
    return re.sub(r"(news_event|country_event) = \{\n\tid = (pax\.\d+)\n(?:\t\w+ = [^\n]*\n)*?\tdesc = [^\n]*\n", sub, events)


def build_art():
    sprites = []

    def sprite(name, rel):
        sprites.append(f'\tspriteType = {{\n\t\tname = "{name}"\n\t\ttexturefile = "{rel}"\n\t}}')
        if name.startswith("GFX_goal_pax_"):  # без _shine игра пишет «Missing icon shine»
            sprites.append(f'\tspriteType = {{\n\t\tname = "{name}_shine"\n\t\ttexturefile = "{rel}"\n\t}}')

    # экраны загрузки: 10 своих сцен под всеми ванильными именами
    scenes = [n for n, _, _ in A.SCENES]
    big = {n: A._logo(A.render(n)) for n in scenes}
    for i, name in enumerate(A.LOADING_NAMES):
        A.save_dds(big[scenes[i % len(scenes)]], os.path.join(OUT, f"gfx/loadingscreens/{name}.dds"))
    # свои картинки сценариев (закладки старта): по сцене на эпоху
    bm_scene = {"1241": "north", "1914": "storm", "1936": "monolith", "1936e": "sea", "1939": "storm", "1962": "cold", "2041": "seven", "2096": "neon"}
    bm_sprites = []
    for eid, sc in bm_scene.items():
        era = next(e for e in E.ERAS if e["id"] == eid)
        y, mo, dd = era["date"].split(".")[:3]
        A.save_dds(A.bookmark_frame(A.render(sc), era["name"], f"{dd}.{mo}.{y}   PaxVanila"),
                   os.path.join(OUT, f"gfx/interface/bookmarks/pax_bm_{eid}.dds"))
        bm_sprites.append(f'\tspriteType = {{\n\t\tname = "GFX_pax_bm_{eid}"\n\t\ttexturefile = "gfx/interface/bookmarks/pax_bm_{eid}.dds"\n\t}}')
    w("interface/pax_bookmarks.gfx", "spriteTypes = {\n" + "\n".join(bm_sprites) + "\n}\n")
    # картинки событий
    for n in scenes:
        im = A.render(n, scale=1)
        save_tga(A._crop(im, (210, 176)).convert("RGBA"), f"gfx/event_pictures/pax_{n}.tga", (210, 176))
        save_tga(A._crop(im, (397, 153)).convert("RGBA"), f"gfx/event_pictures/pax_news_{n}.tga", (397, 153))
        sprite(f"GFX_report_event_pax_{n}", f"gfx/event_pictures/pax_{n}.tga")
        sprite(f"GFX_news_event_pax_{n}", f"gfx/event_pictures/pax_news_{n}.tga")
    # иконки фокусов
    branch = {"ind": ("gear", (70, 70, 85)), "mil": ("sword", (120, 35, 35)), "eco": ("coin", (40, 90, 50))}
    for f in D.GENERIC_FOCUSES:
        sym, bg = branch[f["key"][:3]]
        if f["key"] == "mil2":
            sym = "tower"
        os.makedirs(os.path.join(OUT, "gfx/interface/goals"), exist_ok=True)
        A.focus_icon(sym, bg).save(os.path.join(OUT, f"gfx/interface/goals/pax_{f['key']}.tga"))
        sprite(f"GFX_goal_pax_{f['key']}", f"gfx/interface/goals/pax_{f['key']}.tga")
    os.makedirs(os.path.join(OUT, "gfx/interface/ideas"), exist_ok=True)
    for tag, p in D.POWERS.items():
        fl = draw_flag(p)
        c = tuple(int(v * 0.7) for v in p["color"])
        fai_bg = tuple(int(v * 0.35) for v in p["accent"])
        icons = {
            f"goals/pax_her_{tag}": A.focus_icon("column", c),
            f"goals/pax_fai_{tag}": A.focus_icon("sun", fai_bg),
            f"goals/pax_nat_{tag}": A.flag_icon(fl, (94, 84)),
            f"ideas/pax_spirit_{tag}": A.flag_icon(fl, (64, 64), framed_shield=False),
            f"ideas/pax_her_{tag}": A.idea_icon("column", c),
            f"ideas/pax_fai_{tag}": A.idea_icon("sun", fai_bg),
        }
        for rel, im in icons.items():
            im.save(os.path.join(OUT, f"gfx/interface/{rel}.tga"))
            kind, nm = rel.split("/")
            sprite(("GFX_goal_" if kind == "goals" else "GFX_idea_") + nm, f"gfx/interface/{rel}.tga")
    w("interface/pax_art.gfx", "spriteTypes = {\n" + "\n".join(sprites) + "\n}\n")


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    build_descriptor()
    build_ideas()
    build_lore_decisions()
    ECO.build(w, LOC, indent)
    if D.BASE != "wa":
        MD.decisions(w, LOC, indent)
    for bm in ('blitzkrieg', 'the_gathering_storm') + (('No_Asia',) if D.BASE == "fam" else ()):  # noqa  # лаунчер стирает replace_path из внешнего .mod, поэтому глушим ванильные закладки
        w(f'common/bookmarks/{bm}.txt', 'bookmarks = {\n}\n')
    build_won()
    if D.BASE == "fam":
        build_extra_mods()
    build_characters()
    build_setup()
    build_eras_extra()
    F.build(w, LOC, indent)
    build_country_names()
    write_loc()
    build_graphics()
    build_art()
    n = sum(len(fs) for _, _, fs in os.walk(OUT))
    print(f"Готово: {OUT} ({n} файлов, {len(LOC)} строк локализации)")


if __name__ == "__main__":
    main()
