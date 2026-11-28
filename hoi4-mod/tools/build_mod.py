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


def build_building_strip():
    """Лента иконок зданий на 34 кадра: в Family кадры зданий больше, чем в старой ленте на 18 кадров."""
    import pax_building_strip as BS
    n, _ = BS.build(os.path.join(OUT, "gfx/interface/buildings/pax_building_icon_strip.dds"))
    w("interface/pax_buildings_strip.gfx",
      "spriteTypes = {\n\tspriteType = {\n\t\tname = \"GFX_buildings_strip\"\n"
      "\t\ttextureFile = \"gfx/interface/buildings/pax_building_icon_strip.dds\"\n"
      f"\t\tnoOfFrames = {n}\n\t}}\n}}\n")


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
    # ученые: по два на державу, лор-имена
    SCI = {
        "ITA": [("Марк Витрувий Младший", "nuclear", 3, "scientist_trait_nuclear_specialist scientist_trait_brilliant_theorist", "Главный физик Форума. Первым измерил излучение трещины в Монолите."),
                ("Корнелия Аврелиана", "land", 2, "scientist_trait_bright", "Инженер легионных мастерских, придумала новые осадные машины."),
                ("Сисикал Строитель", "land", 3, "scientist_trait_bright scientist_trait_brilliant_theorist", "Человек, который построил тысячу цивок. Вечный слабейший, но всегда на связи: «Да, сисикал, да!»")],
        "SPR": [("Ганнон Магонид", "naval", 3, "scientist_trait_bright", "Карфагенский корабел, строитель торговых галер нового типа."),
                ("Элисса Баркид", "land", 2, "scientist_trait_bright", "Литейщица Гаевых пушек, снизила цену осадных орудий.")],
        "GRE": [("Архимед Младший", "naval", 3, "scientist_trait_brilliant_theorist", "Потомок сиракузского геометра, считает волны и корабли."),
                ("Гипатия Эллинская", "nuclear", 2, "scientist_trait_nuclear_specialist", "Хранительница Александрийской библиотеки и её чертежей.")],
        "FRA": [("Дивициак Мудрый", "land", 3, "scientist_trait_bright", "Друид-инженер священных рощ, мастер полевых укреплений."),
                ("Бригита Эдуйская", "air", 2, "scientist_trait_bright", "Строит первые галльские воздушные шары для разведки.")],
        "ENG": [("Пифей Мореход", "naval", 3, "scientist_trait_brilliant_theorist", "Мореход-астроном Союза Числа, считает курс по звёздам."),
                ("Теано Пифагорейская", "air", 2, "scientist_trait_bright", "Математик школы Пифагора, считает аэродинамику крыла.")],
        "GER": [("Гельмут Донарсон", "land", 3, "scientist_trait_bright", "Кузнец и инженер, мастер германской брони."),
                ("Хильда Вотанстохтер", "nuclear", 2, "scientist_trait_nuclear_specialist", "Исследует руды Германских королевств.")],
        "SOV": [("Борислав Метельный", "air", 3, "scientist_trait_rocketry_specialist scientist_trait_bright", "Строит ракеты в студёных лабораториях Царства."),
                ("Ольга Печатникова", "nuclear", 2, "scientist_trait_nuclear_specialist", "Изучает Печать Монолита с севера.")],
        "ROM": [("Децебал Мудрец", "land", 3, "scientist_trait_bright", "Мастер рудников Медного Союза."),
                ("Залмоксиана Дакская", "air", 2, "scientist_trait_bright", "Конструктор лёгких штурмовых самолётов Дакии.")],
        "TUR": [("Билге Тюркут", "land", 3, "scientist_trait_bright", "Мастер степных осадных машин Орды."),
                ("Умай Бурян", "air", 2, "scientist_trait_bright", "Изучает ветры и бури, из которых выходит Орда.")],
        "PER": [("Дарий Скифский", "land", 3, "scientist_trait_bright", "Мастер золота и конных луков."),
                ("Табити Золотая", "nuclear", 2, "scientist_trait_nuclear_specialist", "Хранительница царских курганов и их тайн.")],
    }
    for tag, lst in SCI.items():
        base = D.POWERS[tag]["leader"]["id"]
        for k, (nm, spec, lvl, traits, desc) in enumerate(lst, 1):
            cid = f"{tag}_pax_scientist_{k}"
            blocks.append(
                f"{cid} = {{\n\tname = {cid}\n"
                f"\tportraits = {{ civilian = {{ large = GFX_portrait_{base} }} }}\n"
                f"\tscientist = {{\n\t\ttraits = {{ {traits} }}\n"
                f"\t\tskills = {{ specialization_{spec} = {lvl} }}\n\t}}\n}}"
            )
            LOC[cid] = nm
            LOC[cid + "_desc"] = desc
    # генералы и адмиралы по реальным игрокам (ники друзей Артура)
    PLAYERS = [
        ("kozebot1", "GER", "corps", "armor_officer", 4, 2, 4, 3, "Козебот родился в окопе под Берлином и с детства рыл землю быстрее, чем ходил. Верный соратник Хирохито, создателя мода Бох, и мастер обороны германских рудников. Его танки стоят так, что их не сдвинуть даже Монолитом."),
        ("siqye", "GER", "corps", "infantry_officer", 3, 3, 3, 2, "Тень Козебота и ещё один соратник Бох. Где один роет укрепления, там другой носит ему воду и приказы. Германские хроники называют их неразлучными."),
        ("Euroctor", "FRA", "corps", "career_officer", 3, 3, 3, 3, "Соратник Хирохито по мастерской Бох. Никто не знает, откуда он пришёл. Галльские друиды видели его у священных рощ, а штаб видел только его приказы. Он ничего не рассказывает и этим всех устраивает."),
        ("feels", "ITA", "field", "offensive_doctrine", 4, 4, 3, 3, "Первый и самый преданный ученик Сисикала Строителя. Он записывает каждое его слово на восковых табличках и цитирует в Сенате. «Да, сисикал, да!» его девиз, а Ромея его слушает."),
        ("comeback_", "ITA", "corps", "organizer", 3, 3, 4, 3, "Хранитель древних версий. Помнит, что было в Family до всех обновлений, и готов спорить об этом ночь напролёт. Ромейские сенаторы зовут его живой летописью."),
        ("__kefir__", "FRA", "field", "defensive_doctrine", 7, 7, 7, 7, "Галл до мозга костей: усы, плащ, любовь к вину и к священным рощам. Говорят, что кефир он пьёт только по праздникам, а в бою не отступает."),
        ("walli", "SPR", "corps", "career_officer", 3, 3, 3, 3, "Везде понемногу: в штабе, в порту, на складе, в лавке. Карфагенские купцы считают его своим, а армия своим. Универсальный человек, которого невозможно потерять."),
        ("vadya1337", "SOV", "field", "offensive_doctrine", 5, 4, 4, 4, "Вадя, Хозяин Михисты. Его слово в Царстве закон, а его имя знают на всех фронтах. Рассказывают, что Метель 1942 началась в тот день, когда он вышел из дома без шапки."),
        ("Adolfus", "SOV", "field", "defensive_doctrine", 4, 4, 4, 3, "Второй человек в Михисте и правая рука Вади. Он тот, кто молча решает дела, пока первый произносит речи. Его печать на документах весит больше, чем иные армии."),
        ("Orfey", "GRE", "corps", "media_personality", 2, 3, 2, 3, "Самый невезучий полководец в мире: любой план при нём идёт наперекосяк, любая дорога ведёт не туда. Эллины считают его проклятым Посейдоном, но почему-то он всегда возвращается живым."),
        ("arsen0541", "ROM", "field", "media_personality", 4, 3, 4, 3, "Любит Болгар и говорит о нём так, что слушают даже враги. Харизма дакийского вождя и крепкий голос. Идти за ним готовы полки Медного Союза."),
        ("Гвоздичка", "GER", "field", "armor_officer", 4, 4, 4, 4, "Германский генерал, ставший легендой танковых клиньев. Он режет вражеский фронт, как гвоздь доску. Враги шутят, что он оставляет после себя только пыль."),
        ("kotofei_1488", "TUR", "corps", "trait_cautious", 3, 3, 3, 4, "Спокойный как степь перед бурей. Орда называет его Котофеем, и это единственное имя, которое он признаёт. Говорят, он пришёл в Орду вместе с кошкой, и она ему важнее любого штаба."),
        ("g000dd", "ENG", "corps", "armor_officer", 3, 3, 3, 3, "Моряк по крови, американец по духу, большой любитель дота и танков. Союз Числа считает его своим странным родственником из-за океана. Вместе с Корой они держат фронт."),
        ("kor2062", "ENG", "corps", "infantry_officer", 3, 3, 3, 3, "Старый друг g000dd. Вдвоём они держат фронт и острят о прошлых боях. Говорят, что без него в Союзе мореходов было бы тише, но и скучнее. Кор у нас пивной: фронт держится на пене."),
        ("gokers", "ENG", "corps", "career_officer", 2, 2, 3, 3, "Младший в компании, учится быстро и всё ещё ищет свой путь. Мореходы дали ему полк на пробу. Он уже вырос, но шутить над ним по-прежнему приятно."),
        ("imperialmp", "ITA", "navy", "old_guard_navy", 2, 2, 3, 3, "Адмирал Ромеи, которому ещё предстоит научиться строить флот. Корабли Республики порой тонут раньше, чем выходят из порта. Но он упрям и обещает, что в следующий раз всё получится."),
        ("luxel_", "PER", "corps", "organizer", 3, 3, 3, 3, "Загадочный вопросительный знак на карте Скифии. Никто не видел его лица, но все знают его приказы. Курганы хранят молчание о том, кто он на самом деле. Сам он говорит, что его интеллект превосходит интеллект окружающих, а знание для него высшая ценность. Магией стихий он стремится к власти над степью, и очень высокого о себе мнения: почти никого не уважает и забывает о подчинённых за считаные минуты."),
        ("artemyruz", "PER", "corps", "logistics_wizard", 3, 3, 3, 4, "Сын великого юга и вечный борец с голодом. Каждый раз, когда он пытается накормить провинцию, зерно кончается раньше, чем наступает урожай. Скифский двор терпит его за терпение и добрый нрав."),
        ("Lemon4ik", "ITA", "field", "media_personality", 4, 4, 4, 5, "Самый милый маршал Ромеи и лучший друг создателя мира. Враги сдаются ему сами, потому что не могут на него сердиться. В штабе его зовут Лимончиком, и без него не начинается ни один поход."),
        ("Ромул Арутр", "ITA", "field", "offensive_doctrine", 5, 4, 5, 5, "Создатель мода Family и хранитель его древних чертежей. Каждый ромейский правитель берёт имя Ромул, но Арутр единственный, кто сам написал правила мира. Сенат слушает его так же внимательно, как Монолит. Втайне он ещё и верный подсос Бох-мода и Хирохито-хана, о чём в Ромее предпочитают не говорить вслух."),
        ("Extreme", "GRE", "field", "defensive_doctrine", 5, 4, 5, 4, "Создатель Vesti и один из отцов мода Family. Эллада зовёт его Экстримом и верит, что чертежи, которые он оставил, держат Лигу вместе. Он редко говорит, но если говорит, то все записывают."),
        ("Molod", "ENG", "navy", "old_guard_navy", 3, 2, 3, 3, "Британец по духу, адмирал Союза мореходов. Любит большие линкоры, а вот подводных охотников до сих пор побаивается: лодки у него обычно уходят безнаказанно. Мореходы зовут его Молодым, хотя он давно не молод. В штабе ходит шутка, что его тайная страсть это длинные мощные орудия главного калибра, и он в этом даже не стесняется признаться."),
        ("Sapr", "ROM", "field", "organizer", 5, 4, 5, 5, "Создатель Sapn Maps и живая легенда Сисикала. Дакийские картографы считают, что каждая гора на карте нарисована его рукой. Говорят, он единственный, кто дочитал Сисикала до конца."),
        ("mavrus", "ROM", "corps", "armor_officer", 4, 3, 4, 3, "Вторая рука Sapr и его вечный помощник. Огненный воин Медного Союза: там, где он проходит, остаётся только пепел. Любит Sapr и верен ему до последней карты."),
        ("Nizzi", "SPR", "field", "offensive_doctrine", 5, 4, 4, 5, "Самый недооценённый игрок во всём Сисикале и сообществе Hearts of Iron. Он бывал почти везде и побеждал всех, но об этом почти никто не помнит. Карфагенские хроники записали его имя мелким шрифтом, а зря."),
        ("trazynn_", "GRE", "corps", "career_officer", 3, 3, 4, 3, "Трахиночка, наша общая любимица Эллады. Её все помнят, но с тех пор, как она подружилась с Хэвингом, о ней ничего не слышно. Эллинские хроники хранят надежду, что она однажды вернётся."),
        ("Хирохито", "TUR", "field", "defensive_doctrine", 5, 5, 4, 4, "Создатель мода Бох и повелитель его соратников. Орда зовёт его Хирохито-хан. Козебот, Еврактор и Силанов служат ему и называют своим мастером."),
        ("Silanov A.N.", "GER", "corps", "infantry_officer", 3, 3, 3, 3, "Ещё один соратник мастерской Бох. Строг, пунктуален и любит порядок на карте. Германские короли считают его надёжным писарем и полководцем."),
        ("Havin'", "TUR", "corps", "infantry_officer", 3, 3, 3, 3, "Хэвин из мастерской Бох, соратник Хирохито-хана. Вместе с Трахиночкой они пара, которую знает вся Орда: она осталась в Элладе, а он в степи, и письма между ними не прекращаются. Говорят, ради неё он готов обойти пол-мира."),
        ("Nurik", "ITA", "corps", "organizer", 3, 3, 3, 3, "Нурик, воин Ромеи, который с гордостью называет себя Сисивином. Его лицо знает вся армия: стоит ему появиться перед строем, и легионеры начинают хохотать, а потом идут в бой ещё веселее. Говорят, сам Сисикал признал его своим."),
        ("KoLDeR", "ITA", "corps", "armor_officer", 4, 3, 3, 4, "Колдер, самый любимый сисикаллер Ромулов. Рыжий лис в венке из лепестков сакуры, которого враги принимают за шутку, пока не поздно. Он ещё и танковод: его бронеклинья рвут фронты быстрее, чем враг успевает понять, что произошло. Говорят, под его знаменем легионеры поют гимн Сисикала быстрее, чем маршируют."),
        ("Арсен (Монголия)", "MON", "corps", "armor_officer", 4, 4, 4, 4, "Арсен, генерал танковой Монголии и ханский любимец. Он водит бронеколонны по степи так, будто едет на праздник, и ни одна пехота перед ним не устоит. В штабе его знают по красному колпаку и тёмным очкам."),
        ("Арсен с калыванем", "MON", "corps", "armor_officer", 4, 3, 3, 4, "Тот же Арсен, но с калыванем. В дыму он становится философом, и приказы выходят красивые, но запутанные. Степные ветераны говорят, что с калыванем он быстрее, но иногда забывает, куда ехали танки."),
        ("Арсен Булгар", "BUL", "corps", "armor_officer", 4, 4, 3, 4, "Арсен из Булгара, степной брат монгольских Арсенов. Говорит, что в его жилах течёт волжская вода и крымский ветер, а броня для него вторая кожа. Булгары чтят его как хана танковых клиньев."),
        ("Commander-in-Chief Dabi", "ROM", "corps", "armor_officer", 4, 4, 4, 3, "Главнокомандующий Дэби, он же «Боевой вертолёт Апачи». Генерал Восточного фронта: служит и Германии, и Союзу, и Дакии, и везде танкист. В биографии у него написано: не фанат первой доки, не фанат SAPR MP, не фанат первого абуза, не фанат жёсткого режима 41 года, зато фанат низких мп и двенадцатый коммандер."),
    ]
    EXTRA_AWARDS = {
        "Арсен с калыванем": [
            ("Злоупотребление опиумом", "Степной недуг. Арсен слишком часто задерживается над калыванем, из-за чего приказы выходят вялыми и запутанными.", "attack_skill = -1\n\t\tplanning_skill = -1"),
        ],
        "Арсен (Монголия)": [
            ("Танковая степь", "Награда за любовь к броне и танковым клиньям.", "defense_skill = 1"),
            ("Красный колпак", "Узнаваемый знак генерала в тёмных очках. Враги видят колпак и отходят.", "attack_skill = 1"),
        ],
        "KoLDeR": [
            ("Танковый щит", "Награда за любовь к танкам на защиту. Колдер ставит бронетехнику в оборону и ни разу не пожалел.", "defense_skill = 1"),
            ("Бронебойный упор", "За танки, которые стоят так, что их не берёт ни одна пушка.", "defense_skill = 1"),
            ("Стальной клин", "За прорыв, о котором потом писали все хроники.", "planning_skill = 1"),
            ("Масло танкиста", "Награда за то, что танки у него не ломаются.", "logistics_skill = 1"),
            ("Танковый гвоздь", "Награда за клинья, которыми он режет фронты, как гвоздём доску.", "attack_skill = 1"),
            ("Золотая гусеница", "Высшая танковая награда Ромеи. Её вручают только тем, чьи танки доходят до моря.", "attack_skill = 1"),
            ("Танковод", "Награда за любовь к танкам и смелые прорывы. Колдер водит бронеколонны так, будто едет на праздник.", "attack_skill = 1"),
            ("Сисикаллер", "Титул тех, кто живёт и дышит Сисикалом. Колдер носит его с гордостью.", "planning_skill = 1"),
            ("Любимчик создателя", "Награда лично от Ромула Арутра. Самое тёплое признание в Ромее.", "logistics_skill = 1"),
        ],
        "Nurik": [
            ('Я Сисивин', 'Роль и гордость. Он сам так сказал.', 'attack_skill = 1'),
            ('Смех легиона', 'За смех, который заражает целую армию.', 'logistics_skill = 1'),
        ],
        "Havin'": [
            ('Совместная медаль «Любят друг друга»', 'Шуточная парная медаль для Хэвина и Трахиночки: они самая настоящая парочка и любят друг друга. На фронте стоят плечом к плечу, а вторую такую же носит она.', 'defense_skill = 1\n\t\tplanning_skill = 1'),
            ('Письма в Элладу', 'Награда за каждое письмо, которое дошло до адресата.', 'planning_skill = 1'),
            ('Сисикал навсегда', 'За слова «Сисикал живёт вечно», сказанные в 3:36 ночи.', 'attack_skill = 1'),
        ],
        "Silanov A.N.": [
            ('Перо порядка', 'За то, что у него в штабе всё на своих местах.', 'logistics_skill = 1'),
            ('Печать Бох', 'Награда мастерской Бох за верность Хирохито.', 'defense_skill = 1'),
        ],
        "Хирохито": [
            ('Орда в ладони', 'Награда за то, что вся Орда зовёт его ханом.', 'logistics_skill = 1'),
            ('Меч мастера Бох', 'Подарок соратников из мастерской Бох.', 'planning_skill = 1'),
        ],
        "trazynn_": [
            ('Совместная медаль «Любят друг друга»', 'Шуточная парная медаль для Трахиночки и Хэвина: он ждёт её в Орде, она пишет ему из Эллады, и они очень любят друг друга. Вторую такую же носит он.', 'defense_skill = 1\n\t\tplanning_skill = 1'),
            ('Цветок Эллады', 'Награда за красоту, с которой она вернётся.', 'attack_skill = 1'),
            ('Письмо из степи', 'Памятка о том, что её кто-то ждёт в Орде.', 'defense_skill = 1'),
        ],
        "Nizzi": [
            ('Золото забытых', 'Награда за то, чего никто не заметил, но все использовали.', 'logistics_skill = 1'),
            ('Печать сисикала', 'Недооценённый игрок получает сисикала по праву.', 'defense_skill = 1'),
        ],
        "Commander-in-Chief Dabi": [
            ('Подсос Сапра', 'Шуточная награда за то, как преданно он стоит рядом с создателем Sapn Maps и кивает на каждую карту.', 'logistics_skill = 1'),
            ('Сапр-мод', 'Награда за любовь к моду Sapr. Дэби ругает его, но играет только в него.', 'planning_skill = 1'),
        ],
        "mavrus": [
            ('Правая рука Sapr', 'Награда за службу второй рукой великого картографа.', 'defense_skill = 1'),
            ('Огненное клеймо', 'За боевой пыл и самоотверженность.', 'planning_skill = 1'),
        ],
        "Sapr": [
            ('Резец картографа', 'За каждую гору, нанесённую на Sapn Maps.', 'logistics_skill = 1'),
            ('Легенда сисикала', 'Награда за то, что его слава живёт дольше самого мода.', 'attack_skill = 1'),
        ],
        "Molod": [
            ('Линкор мечты', 'Награда за любовь к самым большим кораблям флота.', 'attack_skill = 1'),
            ('Британский чай', 'За британский дух, с которым он ходит в бой.', 'logistics_skill = 1'),
        ],
        "Extreme": [
            ('Свиток Vesti', 'За рождение Vesti, ставшей основой мода Family.', 'attack_skill = 1'),
            ('Печать архитектора', 'Награда за то, что один из родителей Family.', 'defense_skill = 1'),
        ],
        "Ромул Арутр": [
            ('Знак подсоса Бох-мода', 'Шуточный знак для создателя Family, который тайно болеет за Бох-мод и верен Хирохито-хану.', 'defense_skill = 1'),
            ('Перо Создателя', 'Награда за каждую строчку, написанную для мира PaxVanila.', 'planning_skill = 1'),
            ('Венец Сенатора', 'Высшее признание Сената Ромеи.', 'logistics_skill = 1'),
        ],
        "Lemon4ik": [
            ('Лимонный чай', 'Награда за то, что штаб без него не начинает ни одного похода.', 'logistics_skill = 1'),
            ('Улыбка маршала', 'Враг сдаётся, увидев её.', 'defense_skill = 1'),
        ],
        "artemyruz": [
            ('Колос Персии', 'Награда за каждый колос, который он спас от голода.', 'defense_skill = 1'),
            ('Печать амбара', 'За снабжение, не знающее перебоев, пока оно есть.', 'planning_skill = 1'),
        ],
        "luxel_": [
            ('Знание превыше всего', 'Награда за то, что его интеллект выше интеллекта окружающих. Он сам так считает и охотно напоминает об этом штабу.', 'planning_skill = 1'),
            ('Забывчивый маг', 'Шуточная награда: маг так занят стихиями, что забывает о подчинённых за считаные минуты.', 'logistics_skill = -1\n\t\tattack_skill = 1'),
            ('Тайна скифа', 'Награда за то, что даже штаб не знает, кто это.', 'attack_skill = 1'),
            ('Стрела степи', 'Скифская стрела, летящая туда, куда никто не целился.', 'defense_skill = 1'),
        ],
        "imperialmp": [
            ('Компас новичка', 'Награда за то, что адмирал без карты всё равно находит порт.', 'planning_skill = 1'),
            ('Первая верфь', 'За строительство первого корабля собственными руками.', 'logistics_skill = 1'),
        ],
        "kor2062": [
            ('Печать напарника', 'За то, что всегда прикрывает g000dd.', 'attack_skill = 1'),
            ('Старая броня', 'Награда за службу, которая тянется дольше многих войн.', 'logistics_skill = 1'),
            ('Пивной кор', 'Звание за то, что кор у нас пивной: чем гуще пена, тем крепче держится фронт.', 'defense_skill = 1\n\t\tlogistics_skill = 1'),
        ],
        "g000dd": [
            ('Золотой дот', 'За самый крепкий дот в истории Союза мореходов.', 'defense_skill = 1'),
            ('Древнекитайская мудрость', 'Награда за цитату про котёл, которую знает каждый новобранец.', 'planning_skill = 1'),
        ],
        "kotofei_1488": [
            ('Лапа степного кота', 'За то, что в бою двигается так же тихо, как кошка.', 'attack_skill = 1'),
            ('Ожерелье Орды', 'Орда вручает его тем, кого уважает.', 'planning_skill = 1'),
        ],
        "Гвоздичка": [
            ('Стальной клин', 'За прорыв, о котором потом писали все хроники.', 'planning_skill = 1'),
            ('Масло танкиста', 'Награда за то, что танки у неё не ломаются.', 'logistics_skill = 1'),
        ],
        "arsen0541": [
            ('Дакийский щит', 'За оборону Дакии, которую не взяли даже со второго раза.', 'defense_skill = 1'),
            ('Знак Arsen34', 'Награда по второму имени генерала.', 'planning_skill = 1'),
        ],
        "Orfey": [
            ('Скамейка лузеров', 'Почётное место на скамейке лузеров. Орфей сидит там дольше всех и знает каждую доску.', 'defense_skill = 1'),
            ('Медаль за второе место', 'Награда за то, что он дошёл до финала и ровно там проиграл.', 'planning_skill = 1'),
            ('Кубок утешения', 'Приз для тех, кто старался и не получил ничего. Орфей хранит его на видном месте.', 'logistics_skill = 1'),
            ('Лавровый венок поражений', 'Венок, сплетённый из всех его проигранных катек. Выглядит красиво.', 'attack_skill = 1'),
            ('Сын твари', 'Прозвище, которое Орфей носит с неловкой гордостью, и стоит оно ровно один евро.', 'attack_skill = 1'),
            ('Медаль последнего донатера', 'За самую щедрую подачку штабу и самое громкое хвастовство ею.', 'logistics_skill = 1'),
        ],
        "Adolfus": [
            ('Тень Вади', 'Награда за то, что правая рука не отстаёт ни на шаг.', 'defense_skill = 1'),
            ('Красная печать приказа', 'Вручается тем, кто передаёт слова вождя без искажений.', 'attack_skill = 1'),
        ],
        "walli": [
            ('Знак мастера на все руки', 'За то, что умеет всего понемногу и пригодится везде.', 'attack_skill = 1'),
            ('Золотой гаечный ключ', 'Награда за починку всего, что сломалось в штабе.', 'planning_skill = 1'),
        ],
        "comeback_": [
            ('Архив Family', 'За то, что помнит каждый патч и каждую ошибку мода.', 'logistics_skill = 1'),
            ('Печать ворчуна', 'Награда за вечные споры о версиях.', 'defense_skill = 1'),
        ],
        "feels": [
            ('Гимн Сисикала', 'Награда за то, что гимн знает наизусть и поёт во всех походах.', 'defense_skill = 1'),
            ('Знамя главного фаната', 'Носить его могут только самые преданные.', 'planning_skill = 1'),
        ],
        "Euroctor": [
            ('Печать молчаливого мастера', 'За то, что мастер Бох служит тихо и без жалоб.', 'planning_skill = 1'),
            ('Ключ от кладовой', 'Доверенное лицо, знающее, где лежит всё снабжение.', 'logistics_skill = 1'),
        ],
        "siqye": [
            ('Тень Козебота', 'Награда за то, что верная тень всегда рядом и никогда не спорит.', 'defense_skill = 1'),
            ('Перо писаря', 'За аккуратные доклады, которые читают даже в Берлине.', 'planning_skill = 1'),
        ],
        "gokers": [
            ('Диплом новичка', 'Выдан после сотой катки. Гокерс повесил его на стену и теперь показывает всем.', 'defense_skill = 1'),
            ("Вечный ученик", "Награда за слова «я ещё учусь», которые Гокерс повторяет после каждой катки. Он учится так упорно, что учителя уже устали.", "planning_skill = 1"),
        ],
        "kozebot1": [
            ('Козийболт', 'Прозвище из чата Бох-мастерской. Говорят, жизнь не бесконечна, так что Козебот ест где надо.', 'defense_skill = 1'),
            ('Слуга Хирохито-хана', 'Награда за то, что вместе с Еврактором и Силановым служит мастеру Бох без упрёка.', 'logistics_skill = 1'),
            ('Знак подсоса Бох-мода', 'Шуточный знак верности Бох-моду. Орда носит его с гордостью.', 'planning_skill = 1'),
            ('Бронебойный упор', 'За танки, которые он ставит на оборону так, что их не берёт ни одна пушка.', 'defense_skill = 1'),
            ('Сисикал вечен', 'Награда за преданность Сисикалу, пока Козебот ест где надо.', 'attack_skill = 1'),
            ('Медаль рудного окопа', 'За то, что ни разу не отдал шахту врагу.', 'logistics_skill = 1'),
            ("Танковый щит", "Награда за любовь к танкам на защиту. Козебот ставит бронетехнику в оборону и ни разу не пожалел.", "defense_skill = 1"),
        ],
        "vadya1337": [
            ("Рядовой КаллМиДрист", "Звание рядового мультиплеера Mi Hist. Даже Вадя когда-то начинал с самого низа.", "logistics_skill = 1"),
            ("Meh", "Роль того, кого ничем не удивить. Любой штурм вызывает у него одно слово: «мех».", "defense_skill = 1"),
            ("Бэст оф зэ Бэст оф зэ Бэст Сисикал", "Титул лучшего из лучших из лучших сисикала. Никто не помнит, кто его присудил.", "attack_skill = 1"),
            ("BoH Hist hoi4", "Знак игрока исторического мода Бох. Его носят те, кто помнит старые хисты.", "planning_skill = 1"),
            ("Саботирующий игры", "Роль того, кто умеет развалить любую катку изнутри, и все его за это любят.", "logistics_skill = 1"),
            ("Похотливый", "Фиолетовая роль, которую Вадя носит с гордостью. Штаб предпочитает не уточнять, почему она ему досталась.", "attack_skill = 1"),
            ("Цирковая обезьяна", "Синяя роль вечного шоумена. Вся Михиста ждёт его выступлений.", "attack_skill = 1"),
            ("Медаль обезьяны", "Награда за самое весёлое поведение на карте. Вешается на грудь рядом с Цирковой обезьяной.", "defense_skill = 1"),
            ("Медаль главного болтуна", "Награда за самые длинные и смелые истории про свои победы. Правда в них встречается редко.", "planning_skill = 1"),
            ("Рядовой СисиФофорд", "Розовое звание в армии Сисикала. Рядовой, который знает больше многих генералов.", "attack_skill = 1"),
        ],
        "__kefir__": [
            ("⚡ Модератор-корпуса", "Фиолетовая роль порядка. Кефир следит, чтобы в корпусе никто не нарушал правил, и банит не глядя.", "planning_skill = 2"),
            ("★ Капитан-очевидность", "Жёлтая роль человека, который всегда первым говорит то, что видят все.", "logistics_skill = 2"),
            ("Скамейка лузеров", "Коричневая роль скамейки запасных. Оттуда видно весь фронт, и никто не мешает.", "defense_skill = 2"),
            ("Клоун-корпуса", "Красная роль того, кто смешит штаб, пока идёт мобилизация. Говорят, лучшее оружие против уныния.", "attack_skill = 2"),
        ],
    }
    AWARDS = {
        "kozebot1": ("Железный окоп", "Награда Хирохито за оборону рудников. Окоп Козебота не взяла ни одна армия.", "defense_skill = 1"),
        "siqye": ("Печать верного друга", "Вручена за то, что всегда стоит рядом с Козеботом.", "logistics_skill = 1"),
        "Euroctor": ("Знак безымянного", "Награда за службу, о которой никто не знает. Приказы выполняются, а имён не называют.", "planning_skill = 1"),
        "feels": ("Орден Сисикала", "Высшая награда Ромеи за преданность Сисикалу. «Да, сисикал, да!»", "attack_skill = 1"),
        "comeback_": ("Свиток старых версий", "За память о каждой версии Family и бесконечные споры о них.", "planning_skill = 1"),
        "__kefir__": ("Галльский рог", "Награда друидов за стойкость на родной земле.", "defense_skill = 2\n\t\tattack_skill = 2"),
        "walli": ("Значок универсала", "За то, что везде понемногу, и всегда вовремя.", "logistics_skill = 1"),
        "vadya1337": ("Звезда Михисты", "Высшая награда Михисты. Её носят только те, чьё слово закон.", "attack_skill = 1\n\tdefense_skill = 1"),
        "Adolfus": ("Печать второго", "Награда за службу правой рукой Вади.", "planning_skill = 1\n\tlogistics_skill = 1"),
        "Orfey": ("Лента невезения", "Награда за то, что вернулся живым вопреки всему. Невезение хранит его.", "defense_skill = 1"),
        "arsen0541": ("Знак Болгара", "Награда дакийских полков за харизму и любовь к Болгару.", "attack_skill = 1"),
        "Гвоздичка": ("Танковый гвоздь", "Награда за клинья, которыми режут фронты, как гвоздём доску.", "attack_skill = 1\n\tplanning_skill = 1"),
        "kotofei_1488": ("Хвост степной кошки", "Награда Орды за спокойствие перед бурей.", "defense_skill = 1"),
        "g000dd": ("Знак дотера", "За страсть к доту и танкам. Союз мореходов принял его как своего.", "attack_skill = 1"),
        "kor2062": ("Бронза старого друга", "За то, что вместе с g000dd держит фронт.", "defense_skill = 1"),
        "gokers": ("Лента новичка", "Выдаётся тем, кто учится быстро. Гокерс носит её с гордостью.", "logistics_skill = 1"),
        "imperialmp": ("Якорь упорства", "Награда Ромеи за упорство, с которым адмирал учится строить флот.", "defense_skill = 1"),
        "luxel_": ("Вопросительный знак", "Скифская награда для тех, кого никто не знает. Её нельзя расшифровать.", "planning_skill = 1"),
        "artemyruz": ("Зерно юга", "Награда за борьбу с голодом в провинциях. Зерна всегда не хватает, но он не сдаётся.", "logistics_skill = 1"),
        "Lemon4ik": ("Лимонная звезда", "Самая милая награда Ромеи. Враги не хотят воевать против того, кто её носит.", "attack_skill = 1\n\tdefense_skill = 1"),
        "Ромул Арутр": ("Печать Создателя Family", "Высшая награда мира PaxVanila. Принадлежит тому, кто написал правила.", "attack_skill = 1\n\tdefense_skill = 1\n\tplanning_skill = 1"),
        "Extreme": ("Чертёж Vesti", "Награда за создание Vesti и вклад в Family. Эллада хранит его чертежи под замком.", "planning_skill = 1\n\tlogistics_skill = 1"),
        "Molod": ("Якорь без лодок", "Награда за верность линкорам. Подводные лодки по-прежнему уходят безнаказанными.", "attack_skill = 1"),
        "Sapr": ("Карта Сисикала", "Награда за Sapn Maps. Говорят, на ней отмечены все горы мира.", "planning_skill = 1\n\tlogistics_skill = 1"),
        "mavrus": ("Огненная маска", "Награда Медного Союза для огненного воина и второй руки Sapr.", "attack_skill = 1"),
        "Nizzi": ("Недооценённый", "Награда, которую вручают тем, кого помнят меньше, чем стоило бы. Она тяжелее золота.", "attack_skill = 1\n\tdefense_skill = 1"),
        "trazynn_": ("Лента возвращения", "Эллинская награда, которую хранят до возвращения Трахиночки.", "planning_skill = 1"),
        "Хирохито": ("Корона Бох", "Высшая награда Бох-мастерской. Носит только её создатель.", "attack_skill = 1\n\tdefense_skill = 1\n\tplanning_skill = 1"),
        "Silanov A.N.": ("Печать писаря", "За аккуратные приказы и порядок на карте.", "planning_skill = 1"),
        "Арсен (Монголия)": ("Орден монгольской брони", "Награда танковой Монголии за степные прорывы.", "attack_skill = 1"),
        "Commander-in-Chief Dabi": ("Двенадцатый командир", "Награда Дакии за двенадцатый заход в бой и танковый клин без лишних слов.", "attack_skill = 1"),
        "Арсен Булгар": ("Ханская печать Булгара", "Награда булгарской степи за танковый клин, прошедший сквозь три фронта.", "attack_skill = 1"),
        "Арсен с калыванем": ("Калыван степи", "Дымный трофей, который Арсен возит с собой в каждый поход.", "planning_skill = 1"),
        "KoLDeR": ("Сакуровый венок", "Награда Ромеи за красоту и боевой дух. Лепестки не вянут, пока жив Сисикал.", "attack_skill = 1"),
        "Nurik": ("Знак Сисивина", "Шуточная награда Ромеи. Тот, кто её носит, поднимает боевой дух одним своим видом.", "planning_skill = 1"),
        "Havin'": ("Лента двоих", "Награда Бох-мастерской за любовь к Трахиночке. Её вручают только вдвоём.", "logistics_skill = 1"),
    }
    trait_blocks = []
    AWICONS = []
    import re as _re
    _QUIPS = ["(Вручена без оркестра и с опозданием.)", "(Медаль слегка погнута, как и заслуги.)", "(Выдана строго за заслуги, которых никто не помнит.)", "(Эксперты спорят, настоящая ли она.)", "(Изготовлена из чайной ложки и энтузиазма.)", "(Носить на левой груди, ближе к совести.)", "(Вручена после третьей кружки.)", "(Комиссия проголосовала, потому что устала.)", "(Не пытайтесь съесть, это не шоколад.)", "(Гордость начисляется отдельно.)"]
    for k, (nm, tag, kind, trait, atk, dfn, pln, log, desc) in enumerate(PLAYERS, 1):
        base = D.POWERS.get(tag, D.POWERS["ITA"])["leader"]["id"]
        cid = f"{tag}_pax_player_{k}"
        role = {"corps": "corps_commander", "field": "field_marshal", "navy": "navy_leader"}[kind]
        for _j, _xa in enumerate(EXTRA_AWARDS.get(nm, []), 1):
            _xt = f"pax_award_{k}_{_j}"
            trait = trait + " " + _xt
            trait_blocks.append(
                f"\t{_xt} = {{\n\t\ttype = all\n\t\ttrait_type = personality_trait\n"
                "\t\tgain_xp = { always = no }\n"
                f"\t\t{_xa[2]}\n"
                "\t\tnew_commander_weight = { factor = 0 }\n\t}"
            )
            LOC[_xt] = _xa[0]; AWICONS.append((_xt, _xa[0]))
            LOC[_xt + "_desc"] = _xa[1] + " " + _QUIPS[int(__import__("hashlib").md5(_xt.encode()).hexdigest(),16) % len(_QUIPS)]
        _hv = int(__import__("hashlib").md5(nm.encode("utf-8")).hexdigest(), 16)
        _pool = {"corps": ["organizer", "trickster", "trait_engineer", "skilled_staffer", "infantry_leader", "commando", "ranger", "urban_assault_specialist", "infantry_expert", "fortress_buster", "scavenger", "ambusher"],
                 "field": ["logistics_wizard", "offensive_doctrine", "defensive_doctrine", "fast_planner", "thorough_planner", "unyielding_defender", "aggressive_assaulter", "organisational_leader", "inspirational_leader", "expert_delegator"],
                 "navy": ["big_guns_expert", "destroyer_leader", "cruiser_captain", "torpedo_expert", "safety_first", "blue_water_expert"]}[kind]
        _tk = {"corps": 4, "field": 4, "navy": 3}[kind]
        _extra = [_pool[(_hv >> (3 * j)) % len(_pool)] for j in range(_tk * 2)]
        _ex = []
        for _t in _extra:
            if _t not in _ex and _t not in trait.split(): _ex.append(_t)
        _ex = _ex[:_tk]
        if nm in ("kozebot1", "KoLDeR", "Гвоздичка", "g000dd", "kor2062", "Арсен (Монголия)", "Арсен с калыванем", "Арсен Булгар", "Commander-in-Chief Dabi") and kind == "corps":
            _ex = ["panzer_leader", "panzer_expert"] + [x for x in _ex if x not in ("panzer_leader", "panzer_expert")][:2]
        trait = trait + " " + " ".join(_ex)
        if kind == "field":
            trait = trait + " pax_fm_mountain pax_fm_winter pax_fm_desert pax_fm_jungle pax_fm_swamp pax_fm_hills"
        if kind == "corps":
            trait = trait + " " + " ".join(t_ for t_ in ("trait_mountaineer", "winter_specialist", "desert_fox", "jungle_rat", "swamp_fox", "hill_fighter") if t_ not in trait.split())
        aw = AWARDS.get(nm)
        if aw:
            tid = f"pax_award_{k}"
            trait = trait + " " + tid
            trait_blocks.append(
                f"\t{tid} = {{\n\t\ttype = all\n\t\ttrait_type = personality_trait\n"
                "\t\tgain_xp = { always = no }\n"
                f"\t\t{aw[2]}\n"
                "\t\tnew_commander_weight = { factor = 0 }\n\t}"
            )
            LOC[tid] = aw[0]; AWICONS.append((tid, aw[0]))
            LOC[tid + "_desc"] = aw[1] + " " + _QUIPS[int(__import__("hashlib").md5(tid.encode()).hexdigest(),16) % len(_QUIPS)]
        _LV = {"kozebot1": 9, "siqye": 9, "Euroctor": 9, "feels": 9, "comeback_": 6, "__kefir__": 9, "walli": 6, "vadya1337": 9, "Adolfus": 6, "Orfey": 6, "arsen0541": 6, "Гвоздичка": 6, "kotofei_1488": 6, "g000dd": 6, "kor2062": 6, "gokers": 4, "imperialmp": 6, "luxel_": 6, "artemyruz": 6}
        _sk = _LV.get(nm, 9)
        if kind == "navy":
            skills = f"skill = {_sk}\n\t\tattack_skill = {atk}\n\t\tdefense_skill = {dfn}\n\t\tmaneuvering_skill = {pln}\n\t\tcoordination_skill = {log}"
        else:
            skills = f"skill = {_sk}\n\t\tattack_skill = {atk}\n\t\tdefense_skill = {dfn}\n\t\tplanning_skill = {pln}\n\t\tlogistics_skill = {log}"
        AV = {"g000dd": "g000dd", "Арсен (Монголия)": "arsen34", "Арсен Булгар": "arsen34", "Commander-in-Chief Dabi": "dabi", "Арсен с калыванем": "arsen34", "arsen0541": "arsen34", "luxel_": "luxel", "KoLDeR": "kolder", "Havin'": "havin", "Nurik": "nurik", "Хирохито": "hirohito", "Ромул Арутр": "arthur", "trazynn_": "trazynn", "Nizzi": "Nizzi", "Sapr": "Sapr", "mavrus": "mavrus", "Molod": "Molod", "Extreme": "Extreme", "kozebot1": "kozebot1", "__kefir__": "__kefir__", "vadya1337": "vadya1337", "walli": "walli", "comeback_": "comeback_", "Euroctor": "Euroctor", "Lemon4ik": "Lemon4ik", "artemyruz": "artemyruz", "gokers": "gokers", "kor2062": "kor2062", "feels": "feels", "kotofei_1488": "kotofei_1488"}
        port = f"GFX_portrait_{base}"
        if nm in AV:
            from PIL import Image as _I
            im = _I.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "avatars", AV[nm] + ".png")).convert("RGB").resize((156, 156), _I.LANCZOS)
            pimg = _I.new("RGB", (156, 210), (20, 20, 20)); pimg.paste(im, (0, 27))
            os.makedirs(os.path.join(OUT, "gfx/leaders/PAX"), exist_ok=True)
            pimg.save(os.path.join(OUT, "gfx/leaders/PAX", cid + ".tga"))
            port = f"GFX_portrait_{cid}"
            sprites.append("\tspriteType = {\n" f'\t\tname = "{port}"\n' f'\t\ttexturefile = "gfx/leaders/PAX/{cid}.tga"\n' "\t}")
        blocks.append(
            f"{cid} = {{\n\tname = {cid}\n"
            f"\tportraits = {{ army = {{ large = {port} }} }}\n"
            f"\t{role} = {{\n\t\ttraits = {{ {trait} }}\n\t\t{skills}\n\t}}\n}}"
        )
        LOC[cid] = nm
        LOC[cid + "_desc"] = desc
    # уникальные иконки наград: ленточка + медаль + свой значок по смыслу названия
    import hashlib as _hl, math as _mt
    from PIL import Image as _AI, ImageDraw as _AD
    def _glyph(d, kind, cx, cy, col):
        if kind == "star":
            pts = []
            for k in range(10):
                a_ = -_mt.pi / 2 + k * _mt.pi / 5; rr = 30 if k % 2 == 0 else 13
                pts.append((cx + rr * _mt.cos(a_), cy + rr * _mt.sin(a_)))
            d.polygon(pts, fill=col)
        elif kind == "shield":
            d.polygon([(cx, cy - 28), (cx + 24, cy - 14), (cx + 18, cy + 20), (cx, cy + 30), (cx - 18, cy + 20), (cx - 24, cy - 14)], fill=col)
        elif kind == "crown":
            d.polygon([(cx - 26, cy + 18), (cx - 26, cy - 14), (cx - 12, cy), (cx, cy - 22), (cx + 12, cy), (cx + 26, cy - 14), (cx + 26, cy + 18)], fill=col)
        elif kind == "sword":
            d.polygon([(cx - 4, cy - 32), (cx + 4, cy - 32), (cx + 6, cy + 10), (cx - 6, cy + 10)], fill=col)
            d.rectangle([cx - 20, cy + 8, cx + 20, cy + 14], fill=col); d.rectangle([cx - 4, cy + 14, cx + 4, cy + 30], fill=col)
        elif kind == "tank":
            d.rectangle([cx - 28, cy + 4, cx + 28, cy + 22], fill=col); d.rectangle([cx - 16, cy - 10, cx + 12, cy + 6], fill=col)
            d.rectangle([cx + 10, cy - 6, cx + 34, cy - 1], fill=col)
        elif kind == "wheat":
            d.line([cx, cy + 30, cx, cy - 26], fill=col, width=5)
            for k in range(4):
                y = cy - 22 + k * 11
                d.ellipse([cx - 16, y, cx - 2, y + 9], fill=col); d.ellipse([cx + 2, y, cx + 16, y + 9], fill=col)
        elif kind == "anchor":
            d.line([cx, cy - 26, cx, cy + 26], fill=col, width=6); d.line([cx - 14, cy - 12, cx + 14, cy - 12], fill=col, width=5)
            d.arc([cx - 24, cy - 6, cx + 24, cy + 34], 0, 180, fill=col, width=6); d.ellipse([cx - 6, cy - 34, cx + 6, cy - 22], outline=col, width=4)
        elif kind == "scroll":
            d.rectangle([cx - 20, cy - 24, cx + 20, cy + 24], fill=col)
            for k in range(4):
                d.line([cx - 12, cy - 14 + k * 10, cx + 12, cy - 14 + k * 10], fill=(255, 255, 255, 160), width=3)
        elif kind == "key":
            d.ellipse([cx - 22, cy - 22, cx + 2, cy + 2], outline=col, width=7); d.line([cx - 6, cy - 2, cx + 26, cy + 28], fill=col, width=7)
            d.line([cx + 14, cy + 16, cx + 22, cy + 8], fill=col, width=6)
        elif kind == "smile":
            d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=col)
            d.ellipse([cx - 14, cy - 12, cx - 6, cy - 2], fill=(30, 30, 30, 255)); d.ellipse([cx + 6, cy - 12, cx + 14, cy - 2], fill=(30, 30, 30, 255))
            d.arc([cx - 16, cy - 8, cx + 16, cy + 20], 20, 160, fill=(30, 30, 30, 255), width=4)
        elif kind == "cup":
            d.polygon([(cx - 22, cy - 22), (cx + 22, cy - 22), (cx + 14, cy + 8), (cx - 14, cy + 8)], fill=col)
            d.rectangle([cx - 4, cy + 8, cx + 4, cy + 22], fill=col); d.rectangle([cx - 16, cy + 22, cx + 16, cy + 28], fill=col)
        elif kind == "flower":
            for k in range(5):
                a_ = k * 2 * _mt.pi / 5
                d.ellipse([cx + 14 * _mt.cos(a_) - 11, cy + 14 * _mt.sin(a_) - 11, cx + 14 * _mt.cos(a_) + 11, cy + 14 * _mt.sin(a_) + 11], fill=col)
            d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(255, 235, 140, 255))
        elif kind == "question":
            d.arc([cx - 18, cy - 28, cx + 18, cy + 4], 180, 360 + 70, fill=col, width=8); d.line([cx + 4, cy + 4, cx, cy + 14], fill=col, width=8)
            d.ellipse([cx - 5, cy + 20, cx + 5, cy + 30], fill=col)
        elif kind == "ribbonbow":
            d.polygon([(cx, cy), (cx - 28, cy - 18), (cx - 28, cy + 18)], fill=col); d.polygon([(cx, cy), (cx + 28, cy - 18), (cx + 28, cy + 18)], fill=col)
            d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=col)
        elif kind == "heart":
            d.ellipse([cx - 28, cy - 24, cx, cy + 4], fill=col); d.ellipse([cx, cy - 24, cx + 28, cy + 4], fill=col)
            d.polygon([(cx - 27, cy - 5), (cx + 27, cy - 5), (cx, cy + 30)], fill=col)
        elif kind == "beer":
            d.rectangle([cx - 20, cy - 12, cx + 12, cy + 28], fill=col)
            d.arc([cx + 4, cy - 4, cx + 30, cy + 20], 270, 90, fill=col, width=6)
            for k in range(3):
                d.ellipse([cx - 24 + k * 14, cy - 28, cx - 6 + k * 14, cy - 8], fill=(255, 255, 255, 235))
        elif kind == "banana":
            d.arc([cx - 30, cy - 34, cx + 30, cy + 26], 20, 150, fill=col, width=14)
            d.ellipse([cx - 26, cy + 2, cx - 18, cy + 10], fill=(60, 40, 10, 255))
        elif kind == "fish":
            d.ellipse([cx - 26, cy - 14, cx + 14, cy + 14], fill=col)
            d.polygon([(cx + 10, cy), (cx + 30, cy - 16), (cx + 30, cy + 16)], fill=col)
        elif kind == "boot":
            d.rectangle([cx - 10, cy - 28, cx + 10, cy + 8], fill=col)
            d.polygon([(cx - 10, cy + 8), (cx + 10, cy + 8), (cx + 32, cy + 20), (cx + 32, cy + 28), (cx - 10, cy + 28)], fill=col)
        elif kind == "ring":
            d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], outline=col, width=8); d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=col)
        else:
            d.polygon([(cx - 24, cy + 20), (cx, cy - 28), (cx + 24, cy + 20)], fill=col)
    _KW = [("танк", "tank"), ("гусениц", "tank"), ("клин", "sword"), ("гвоздь", "sword"), ("меч", "sword"), ("клинок", "sword"), ("звезд", "star"), ("знамя", "star"), ("орден", "star"), ("гимн", "star"), ("щит", "shield"), ("окоп", "shield"), ("упор", "shield"), ("броня", "shield"), ("дот", "shield"), ("корон", "crown"), ("венец", "crown"), ("венок", "flower"), ("сакур", "flower"), ("цветок", "flower"), ("зерно", "wheat"), ("колос", "wheat"), ("амбар", "wheat"), ("якорь", "anchor"), ("линкор", "anchor"), ("верфь", "anchor"), ("компас", "anchor"), ("свиток", "scroll"), ("архив", "scroll"), ("перо", "scroll"), ("письм", "scroll"), ("карта", "scroll"), ("чертёж", "scroll"), ("чертеж", "scroll"), ("диплом", "scroll"), ("печать", "scroll"), ("резец", "scroll"), ("ключ", "key"), ("улыбк", "smile"), ("лимон", "smile"), ("клоун", "smile"), ("обезьян", "smile"), ("смех", "smile"), ("кубок", "cup"), ("любят", "heart"), ("пивн", "beer"), ("пиво", "beer"), ("кружк", "beer"), ("рыб", "fish"), ("банан", "banana"), ("сапог", "boot"), ("лапот", "boot"), ("тапок", "boot"), ("чай", "cup"), ("скамейка", "cup"), ("медаль за", "cup"), ("?", "question"), ("вопрос", "question"), ("тайна", "question"), ("неизвест", "question"), ("лента", "ribbonbow"), ("письма", "scroll"), ("сисикал", "star"), ("сисивин", "star")]
    _PAL = [((235, 190, 50), (150, 105, 15)), ((200, 205, 215), (110, 115, 130)), ((205, 125, 60), (120, 65, 25)), ((120, 190, 255), (40, 90, 160)), ((230, 90, 90), (130, 30, 40)), ((150, 220, 130), (50, 110, 50)), ((200, 140, 235), (95, 50, 130)), ((255, 160, 200), (150, 60, 100))]
    _RIB = [(70, 140, 220), (200, 50, 50), (60, 160, 90), (150, 70, 190), (230, 170, 40), (40, 40, 50)]
    def _award_icon(name):
        h = int(_hl.md5(name.encode("utf-8")).hexdigest(), 16)
        S = 4; N = 34 * S
        im = _AI.new("RGBA", (N, N), (0, 0, 0, 0)); d = _AD.Draw(im)
        lo = name.lower()
        kind = None
        for w_, k_ in _KW:
            if w_ in lo: kind = k_; break
        if kind is None: kind = ["banana", "fish", "boot", "beer", "smile", "ribbonbow", "star", "cup"][h % 8]
        gray = any(w_ in lo for w_ in ("лузер", "поражен", "утешен", "второе", "meh"))
        c1, c2 = ((165, 165, 170), (80, 80, 88)) if gray else _PAL[(h >> 4) % len(_PAL)]
        rib = _RIB[(h >> 12) % len(_RIB)]
        cx = N // 2
        d.polygon([(cx - 36, 0), (cx - 4, 0), (cx + 22, 70), (cx - 10, 70)], fill=rib)
        d.polygon([(cx + 36, 0), (cx + 4, 0), (cx - 22, 70), (cx + 10, 70)], fill=tuple(int(x * 0.75) for x in rib))
        r = 50; cy = 88
        d.ellipse([cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4], fill=(25, 25, 30, 255))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c2)
        d.ellipse([cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8], fill=c1)
        sym = tuple(int(x * 0.5) for x in c2) + (255,)
        _glyph(d, kind, cx, cy, sym)
        # шуточные глазки на каждой медали
        for ex in (cx - 15, cx + 15):
            d.ellipse([ex - 12, cy - 30, ex + 12, cy - 6], fill=(255, 255, 255, 255), outline=(20, 20, 20, 255), width=3)
            off = ((h >> (ex % 7)) % 9) - 4
            d.ellipse([ex - 4 + off // 2, cy - 22 + (off % 3), ex + 5 + off // 2, cy - 13 + (off % 3)], fill=(10, 10, 10, 255))
        return im.resize((34, 34), _AI.LANCZOS), "award_" + _hl.md5(name.encode("utf-8")).hexdigest()[:8]
    os.makedirs(os.path.join(OUT, "gfx/interface/leader_traits"), exist_ok=True)
    _sp = []; _seen = set()
    for _tid, _nm in AWICONS:
        _img, _fn = _award_icon(_nm)
        if _fn not in _seen:
            _seen.add(_fn)
            _img.save(os.path.join(OUT, f"gfx/interface/leader_traits/{_fn}.dds"), pixel_format="DXT5")
        _sp.append("\tspriteType = {\n" f'\t\tname = "GFX_trait_{_tid}"\n' f'\t\ttexturefile = "gfx/interface/leader_traits/{_fn}.dds"\n' "\t}")
    for _tid, _ter, _icon, _nm in (("pax_fm_mountain", "mountain", "trait_mountaineer", "Горный маршал"), ("pax_fm_winter", "forest", "trait_winter_specialist", "Зимний маршал"),
                                   ("pax_fm_desert", "desert", "trait_desert_fox", "Пустынный маршал"), ("pax_fm_jungle", "jungle", "trait_jungle_rat", "Маршал джунглей"),
                                   ("pax_fm_swamp", "marsh", "trait_swamp_fox", "Болотный маршал"), ("pax_fm_hills", "hills", "trait_hill_fighter", "Маршал холмов")):
        _mod = "winter_attrition_factor = -0.5" if _ter == "forest" else f"{_ter} = {{\n\t\t\t\tattack = 0.1\n\t\t\t\tdefence = 0.1\n\t\t\t\tmovement = 0.05\n\t\t\t}}"
        trait_blocks.append(f"\t{_tid} = {{\n\t\ttype = field_marshal\n\t\ttrait_type = personality_trait\n\t\tgain_xp = {{ always = no }}\n\t\tmodifier = {{\n\t\t\t{_mod}\n\t\t}}\n\t\tnew_commander_weight = {{ factor = 0 }}\n\t}}")
        LOC[_tid] = _nm; LOC[_tid + "_desc"] = "Черта местности для маршала: бонус к атаке, защите и скорости в этой местности."
        _sp.append("\tspriteType = {\n" f'\t\tname = "GFX_trait_{_tid}"\n' f'\t\ttexturefile = "gfx/interface/traits/{_icon}.dds"\n' "\t}")
    w("interface/pax_award_icons.gfx", "spriteTypes = {\n" + "\n".join(_sp) + "\n}\n")
    w("common/unit_leader/pax_award_traits.txt", "leader_traits = {\n" + "\n\n".join(trait_blocks) + "\n}\n")
    # пасхалка: друзья-генералы доступны через решение
    by_tag = {}
    for k, (nm, tag, *_r) in enumerate(PLAYERS, 1):
        by_tag.setdefault(tag, []).append(f"{tag}_pax_player_{k}")
    # генералы Восточного фронта доступны также СССР и Германии
    for k, (nm, tag, *_r) in enumerate(PLAYERS, 1):
        if nm in ("Sapr", "mavrus", "Commander-in-Chief Dabi"):
            for _t in ("SOV", "GER"):
                by_tag.setdefault(_t, []).append(f"{tag}_pax_player_{k}")
    dec = []
    for tag, ids in by_tag.items():
        rec = "\n".join(f"\t\t\trecruit_character = {i}" for i in ids)
        dec.append(
            f"\tpax_friends_{tag} = {{\n"
            "\t\ticon = generic_form_nation\n"
            f"\t\tallowed = {{ original_tag = {tag} }}\n"
            "\t\tfire_only_once = yes\n"
            "\t\tcost = 50\n"
            "\t\tcomplete_effect = {\n" + rec + "\n\t\t}\n"
            "\t\tai_will_do = { factor = 0 }\n"
            "\t}"
        )
        LOC[f"pax_friends_{tag}"] = "Позвать друзей на службу"
        LOC[f"pax_friends_{tag}_desc"] = "Старые товарищи по партиям приходят в армию. Пасхалка для своих."
    allrec = "\n".join(f"\t\t\trecruit_character = {tag}_pax_player_{k}" for k, (nm, tag, *_r) in enumerate(PLAYERS, 1))
    dec.append(
        "\tpax_friends_all = {\n\t\ticon = generic_form_nation\n"
        "\t\tallowed = { always = yes }\n\t\tfire_only_once = yes\n\t\tcost = 300\n"
        "\t\tcomplete_effect = {\n" + allrec + "\n\t\t}\n\t\tai_will_do = { factor = 0 }\n\t}"
    )
    _alltr = " ".join(f"has_trait = pax_award_{k}" for k in range(1, len(PLAYERS) + 1))
    for _id, _ef, _nm, _ds in (("pax_train_attack", "add_attack = 1", "Тренировка друзей: атака", "За политическую власть друзья-генералы учатся бить сильнее (+1 к атаке)."),
                               ("pax_train_defense", "add_defense = 1", "Тренировка друзей: защита", "За политическую власть друзья-генералы учатся держать оборону (+1 к защите).")):
        dec.append(
            f"\t{_id} = {{\n\t\ticon = generic_military\n"
            "\t\tallowed = { always = yes }\n\t\tcost = 25\n\t\tdays_re_enable = 1\n"
            "\t\tavailable = { any_unit_leader = { OR = { " + _alltr + " } } }\n"
            "\t\tcomplete_effect = {\n\t\t\tevery_unit_leader = {\n\t\t\t\tlimit = { OR = { " + _alltr + " } }\n"
            f"\t\t\t\t{_ef}\n\t\t\t}}\n\t\t}}\n\t\tai_will_do = {{ factor = 0 }}\n\t}}"
        )
        LOC[_id] = _nm; LOC[_id + "_desc"] = _ds
    dec.append(
        "\tpax_mon_tank_nation = {\n\t\ticon = generic_tank\n"
        "\t\tallowed = { original_tag = MON }\n\t\tfire_only_once = yes\n\t\tcost = 0\n"
        "\t\tcomplete_effect = {\n\t\t\tadd_ideas = pax_mon_tank_nation\n\t\t\tadd_manpower = 40000\n"
        "\t\t\tadd_equipment_to_stockpile = { type = light_tank_chassis_1 amount = 150 producer = MON }\n"
        "\t\t\tadd_equipment_to_stockpile = { type = motorized_equipment_1 amount = 400 producer = MON }\n"
        "\t\t}\n\t\tai_will_do = { factor = 0 }\n\t}"
    )
    LOC["pax_mon_tank_nation"] = "Танковая Монголия"
    LOC["pax_mon_tank_nation_desc"] = "Степь становится бронёй. Монголия получает танки, моторизацию и дух танковой державы. Генералы Арсен доступны в решении «Позвать друзей»."
    LOC["pax_mon_tank_nation_idea"] = "Танковая Монголия"
    LOC["pax_mon_tank_nation_idea_desc"] = "Вся степь работает на броню."
    w("common/ideas/pax_mon_ideas.txt", "ideas = {\n\tcountry = {\n\t\tpax_mon_tank_nation = {\n\t\t\tmodifier = {\n\t\t\t\tarmy_armor_attack_factor = 0.15\n\t\t\t\tarmy_armor_defence_factor = 0.15\n\t\t\t}\n\t\t}\n\t}\n}\n")
    # дерево фокусов Монголии
    _mf = [
        ("steppe_levy", 3, 0, [], "GFX_goal_generic_construction", "Степной призыв", "Каждый всадник степи становится солдатом.", "add_manpower = 20000\n\t\t\tadd_war_support = 0.05"),
        ("horse_to_steel", 1, 1, ["steppe_levy"], "GFX_goal_generic_production", "От коня к стали", "Старые кавалерийские традиции пересаживаются в броню.", "add_ideas = pax_mon_tank_nation"),
        ("khan_workshops", 3, 1, ["steppe_levy"], "GFX_goal_generic_production", "Мастерские хана", "Ремонтные ямы под открытым небом дают первые моторы.", "add_equipment_to_stockpile = { type = motorized_equipment_1 amount = 200 producer = MON }"),
        ("iron_horde", 5, 1, ["steppe_levy"], "GFX_goal_generic_army_artillery", "Железная орда", "Орда получает оружие и порядок.", "add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 1500 producer = MON }\n\t\t\tadd_stability = 0.05"),
        ("tank_wedges", 1, 2, ["horse_to_steel"], "GFX_goal_generic_army_doctrines", "Танковые клинья", "Лёгкие танки идут по степи быстрее любого коня.", "add_equipment_to_stockpile = { type = light_tank_chassis_1 amount = 100 producer = MON }"),
        ("red_cap", 3, 2, ["khan_workshops"], "GFX_goal_generic_construction", "Красный колпак", "Знак генерала в тёмных очках виден на всю степь.", "add_political_power = 100\n\t\t\tadd_war_support = 0.05"),
        ("great_steppe", 3, 3, ["tank_wedges", "red_cap"], "GFX_goal_generic_production", "Великая степь", "От Байкала до пустыни Гоби идёт одна броня.", "add_manpower = 30000\n\t\t\tadd_equipment_to_stockpile = { type = light_tank_chassis_1 amount = 150 producer = MON }"),
    ]
    _fb = []
    for _fid, _x, _y, _pre, _ic, _nm, _ds, _ef in _mf:
        _pr = ("\t\tprerequisite = { " + " ".join(f"focus = pax_mon_{q}" for q in _pre) + " }\n") if _pre else ""
        _fb.append(f"\tfocus = {{\n\t\tid = pax_mon_{_fid}\n\t\ticon = {_ic}\n\t\tx = {_x}\n\t\ty = {_y}\n\t\tcost = 5\n{_pr}\t\tcompletion_reward = {{\n\t\t\t{_ef}\n\t\t}}\n\t\tai_will_do = {{ factor = 1 }}\n\t}}")
        LOC[f"pax_mon_{_fid}"] = _nm; LOC[f"pax_mon_{_fid}_desc"] = _ds
    w("common/national_focus/pax_MON.txt", "# Монголия: дерево фокусов из Chaddhaus (national_focus/mongolia.txt)\n")
    # автошаблоны дивизий (по скринам Arthur'а), добавляются решением
    def _tpl(name, rows, support):
        # rows: список по колонкам: [(unit, count)...] колонка x=0..4, y = 0.. по порядку
        regs = []
        for x, col in enumerate(rows):
            y = 0
            for unit, cnt in col:
                for _ in range(cnt):
                    regs.append(f"\t\t\t\t\t{unit} = {{ x = {x} y = {y} }}")
                    y += 1
        sup = []
        for y, u in enumerate(support):
            sup.append(f"\t\t\t\t\t{u} = {{ x = 0 y = {y} }}")
        return (
            "\t\t\tadd_division_template = {\n"
            f'\t\t\t\tname = "{name}"\n'
            "\t\t\t\tregiments = {\n" + "\n".join(regs) + "\n\t\t\t\t}\n"
            "\t\t\t\tsupport = {\n" + "\n".join(sup) + "\n\t\t\t\t}\n"
            "\t\t\t}"
        )
    _sup = ["engineer", "recon", "artillery", "anti_tank", "signal_company"]
    tpls = [
        _tpl("Горно-стрелковые войска", [[("mountaineers", 4)]] * 5, _sup),
        _tpl("Infantry Division", [[("infantry", 5)], [("infantry", 5)], [("infantry", 5)], [("infantry", 5)], [("infantry", 2)]], _sup),
        _tpl("Marines", [[("marine", 2), ("mountaineers", 2)]] * 5, _sup),
        _tpl("Marines — копия — копия", [[("mountaineers", 5)], [("mountaineers", 5)], [("mountaineers", 5)], [("mountaineers", 5)], [("medium_armor", 1)]], _sup),
    ]
    tdec = []
    for i, (t, ttl) in enumerate(zip(tpls, ["Горно-стрелковые войска", "Пехотная дивизия (22)", "Морпехи", "Морпехи с танком"]), 1):
        tdec.append(f"\tpax_tpl_{i} = {{\n\t\ticon = generic_construction\n\t\tallowed = {{ always = yes }}\n\t\tfire_only_once = yes\n\t\tcost = 0\n\t\tcomplete_effect = {{\n\t\t\tload_oob = pax_tpl_{i}\n\t\t}}\n\t\tai_will_do = {{ factor = 0 }}\n\t}}")
        w(f"history/units/pax_tpl_{i}.txt", "\n".join(l[3:] for l in t.replace("add_division_template", "division_template").split("\n")) + "\n")
        LOC[f"pax_tpl_{i}"] = "Шаблон: " + ttl
        LOC[f"pax_tpl_{i}_desc"] = "Добавляет готовый шаблон дивизии."
    LOC["pax_templates_category"] = "Основные шаблоны"
    LOC["pax_templates_category_desc"] = "Автошаблоны дивизий."
    w("common/decisions/categories/pax_templates_categories.txt", "pax_templates_category = {\n\ticon = generic_military\n\tpriority = 1000\n\tallowed = { always = yes }\n}\n")
    w("common/decisions/pax_templates_decisions.txt", "pax_templates_category = {\n" + "\n".join(tdec) + "\n}\n")
    LOC["pax_auto_templates"] = "Автошаблоны дивизий"
    LOC["pax_auto_templates_desc"] = "Добавляет готовые шаблоны: горно-стрелковые войска, пехотная дивизия, морпехи и морпехи с танком."
    LOC["pax_friends_all"] = "Позвать всех друзей (проверка)"
    LOC["pax_friends_all_desc"] = "Все 29 друзей сразу, для проверки. Доступно любой державе."
    LOC["pax_friends_category"] = "Друзья"
    LOC["pax_friends_category_desc"] = "Старая гвардия сервера."
    w("common/decisions/categories/pax_friends_categories.txt",
      "pax_friends_category = {\n\ticon = generic_political_actions\n\tallowed = { always = yes }\n}\n")
    w("common/decisions/pax_friends_decisions.txt", "pax_friends_category = {\n" + "\n".join(dec) + "\n}\n")
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
    # 300 слотов по кругу: ванильные цитаты (LOADING_TIP_N) полностью перекрыты своими
    for i in range(0 if os.environ.get("PAX_BASE") == "fam" else 300):  # Family: цитаты друзей лежат в loading_tips_l_russian.yml
        LOC_REPLACE[f"LOADING_TIP_{i}"] = D.LOADING_TIPS[i % len(D.LOADING_TIPS)]


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
    # мем-картинка Arthur'а на экране загрузки (две ячейки)
    from PIL import Image as _M
    _m = _M.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "avatars", "loading_meme.png")).convert("RGB")
    _h = 1080; _w = int(_m.width * _h / _m.height)
    _bg = _M.new("RGB", (1920, 1080), (12, 12, 16)); _bg.paste(_m.resize((_w, _h), _M.LANCZOS), ((1920 - _w) // 2, 0))
    for _n in ("load_1", "load_2"):
        A.save_dds(_bg, os.path.join(OUT, f"gfx/loadingscreens/{_n}.dds"))
    A.save_dds(_M.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "avatars", "loading_meme2.png")).convert("RGB"), os.path.join(OUT, "gfx/loadingscreens/load_3.dds"))
    # свои картинки сценариев (закладки старта): по сцене на эпоху
    bm_scene = {"1241": "north", "1914": "storm", "1936": "monolith", "1936e": "sea", "1939": "storm", "1962": "cold", "2041": "seven", "2096": "neon"}
    bm_sprites = []
    for eid, sc in bm_scene.items():
        era = next(e for e in E.ERAS if e["id"] == eid)
        y, mo, dd = era["date"].split(".")[:3]
        # окно выбора сценария показывает картинку в натуральном размере (~232x192), поэтому делаем маленькую
        big_im = A.render(sc)
        tw, th = 700, 579
        k = max(tw / big_im.width, th / big_im.height)
        big_im = big_im.resize((int(big_im.width * k) + 1, int(big_im.height * k) + 1))
        l, t = (big_im.width - tw) // 2, (big_im.height - th) // 2
        poster = A.bookmark_frame(big_im.crop((l, t, l + tw, t + th)), era["name"], f"{dd}.{mo}.{y}   PaxVanila")
        A.save_dds(poster.resize((232, 192), A.Image.LANCZOS), os.path.join(OUT, f"gfx/interface/bookmarks/pax_bm_{eid}.dds"))
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
        build_building_strip()
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
