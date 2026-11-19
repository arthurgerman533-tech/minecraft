# -*- coding: utf-8 -*-
"""Наработки Arthur из «Family Historical MP mod», перенесённые в PaxVanila.

Исходники лежат в tools/family_src/ как они были в Family (папка «фэмили до обновы»):
  _economic.txt       законы экономики и торговли Family (баффы гражданской экономики и т.д.)
  Family_defines.lua  мультиплеерные defines Family (скорость, опыт, размен авиации, сопротивление)
Остальное (технологии VI, «Мирное небо», событие «Тотальная война», гайд с разделами)
переписано сюда из arthur.txt, industry.txt, FamilyEvents.txt и Family_l_russian.yml.
"""
import os
import re

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "family_src")


def _read(name):
    with open(os.path.join(SRC, name), encoding="utf-8-sig") as f:
        return f.read()


# Технологии из industry.txt Family. В Family их открывали ванильные технологии через
# leads_to_tech; здесь ванильные файлы не перекрываются, поэтому они доступны сразу,
# но до start_year идёт штраф за опережение.
FAMILY_TECHS = [
    ("concentrated_industry6", "Концентрированная промышленность VI",
     "Произошли значительные прорывы в автоматизации и эффективности производства. Благодаря передовым технологиям и усовершенствованным процессам удаётся значительно снизить издержки и увеличить выпуск.",
     {"industrial_capacity_factory": 0.05, "industrial_capacity_dockyard": 0.10, "global_building_slots_factor": 0.20},
     2.5, 1945, 4, 12, ["industry", "concentrated_industry_category"], None),
    ("dispersed_industry6", "Рассредоточенная промышленность VI",
     "Интеграция передовых технологий и безопасной связи улучшает защиту промышленности, делая её почти невозможной для обнаружения и уничтожения воздушными атаками.",
     {"line_change_production_efficiency_factor": 0.05, "production_factory_start_efficiency_factor": 0.05,
      "industry_air_damage_factor": -0.10, "production_factory_efficiency_gain_factor": 0.1},
     2.5, 1946, 6, 12, ["industry", "dispersed_industry_category"], None),
    ("construction6", "Строительство VI",
     "Строительный процесс оптимизирован с использованием новейших технологий и достижений в области проектного планирования.",
     {"production_speed_buildings_factor": 0.10, "industry_repair_factor": 0.05},
     2.5, 1945, 0, 10, ["industry", "construction_tech"], "excavation6"),
    ("excavation6", "Разработка VI",
     "Добыча ресурсов становится эффективнее благодаря автоматизации и робототехнике: больше руды и меньше отходов.",
     {"local_resources_factor": 0.10, "production_lack_of_resource_penalty_factor": -0.05},
     2.5, 1945, 2, 10, ["industry", "construction_tech", "excavation_tech"], None),
    ("flexible_line2", "Улучшенная гибкая линия",
     "Автоматизация и робототехника повышают гибкость производства и скорость перехода на новые модели.",
     {"production_factory_max_efficiency_factor": 0.1, "line_change_production_efficiency_factor": 0.15},
     2.5, 1945, -1, 12, ["industry", "cat_production"], None),
    ("streamlined_line2", "Улучшенная упорядоченная линия",
     "Автоматизация и робототехника увеличивают стандартизацию и эффективность производства.",
     {"production_factory_max_efficiency_factor": 0.1, "production_factory_efficiency_gain_factor": 0.05},
     2.5, 1945, 1, 12, ["industry", "cat_production"], None),
    ("improved_modern_oil_processing", "Улучшенная современная переработка нефти",
     "Термический крекинг и деасфальтизация растворителями увеличивают выход топлива.",
     {"fuel_gain_factor_from_states": 0.5},
     1.75, 1945, -1, 13, ["industry", "synth_resources", "cat_synth_oil"], None),
    ("improved_modern_rubber_processing", "Улучшенная современная переработка резины",
     "Оптимизированная полимеризация снижает затраты и увеличивает выпуск резины.",
     {}, 2, 1945, 1, 13, ["industry", "synth_resources", "cat_synth_rubber"], None),
    ("modern_equipment_conversion", "Современная модернизация оборудования",
     "Современные процессы переоснащения и специальные команды быстро обновляют старое оружие и технику до новых стандартов.",
     {"equipment_conversion_speed": 0.25, "refit_speed": 0.1, "repair_speed_factor": 0.05},
     2.5, 1941, 2, 8, ["industry", "cat_production"], None),
]

FAMILY_IN_FILES = set()  # эти технологии уже лежат в industry.txt


TECH_EXTRA = {
    "excavation6": "show_effect_as_desc = yes",
    "improved_modern_rubber_processing": "show_effect_as_desc = yes",
    "improved_modern_oil_processing": "show_effect_as_desc = yes",
}

# «Мирное небо» (peaceful_sky из arthur.txt): в мирное время войска и авиация учатся
# быстро и без аварий. Пропадает, как только начинается война.
PEACEFUL_SKY = """PAX_peaceful_sky = {
	picture = air_support_focus
	allowed = { always = no }
	cancel = { has_war = yes }
	removal_cost = -1
	modifier = {
		training_time_army_factor = -0.5
		air_training_xp_gain_factor = 1
		experience_gain_navy_unit_factor = 20
		air_accidents_factor = -1
		naval_accidents_chance = -1
		mobilization_speed = 1.0
		army_fuel_consumption_factor = -1.0
		air_fuel_consumption_factor = -1.0
		repair_speed_factor = 1
		production_lack_of_resource_penalty_factor = -1
		min_export = -1
		attrition = -1
		supply_consumption_factor = -0.35
		supply_factor = 1
	}
}"""

# Из arthur.txt (NO_asia, NO_asia_ENG, NO_asia_GER) и endpoint.txt (e_neutral) для сценария «без Азии»
SMALL_WORLD = """PAX_small_world = {
	picture = generic_acquire_tanks
	allowed = { always = no }
	removal_cost = -1
	modifier = {
		consumer_goods_expected_value = -0.05
		industrial_capacity_factory = 0.15
		production_speed_buildings_factor = 0.10
		conscription = 0.03
	}
}

PAX_small_world_ENG = {
	picture = eng_the_sun_never_sets
	allowed = { always = no }
	removal_cost = -1
	modifier = {
		production_speed_buildings_factor = 0.10
		conscription = 0.03
		surrender_limit = 0.09
	}
}

PAX_small_world_GER = {
	picture = jap_intervene_in_china
	allowed = { always = no }
	removal_cost = -1
	equipment_bonus = {
		small_plane_airframe = { build_cost_ic = -0.15 instant = yes }
		small_plane_cas_airframe = { build_cost_ic = -0.15 instant = yes }
	}
}

PAX_far_lands_sealed = {
	picture = generic_pp_unity_bonus
	allowed = { always = no }
	removal_cost = -1
	modifier = {
		ai_get_ally_desire_factor = -1000
		ai_join_ally_desire_factor = -1000
		political_power_gain = -3
		justify_war_goal_time = 100
		enemy_justify_war_goal_time = 100
		conscription = -10
		consumer_goods_expected_value = 1
		join_faction_tension = 10
		industrial_capacity_factory = -10
		industrial_capacity_dockyard = -10
		experience_gain_army = -100
		research_speed_factor = -100
		min_export = 1
	}
}"""

EXTRA_IDEAS = [PEACEFUL_SKY, SMALL_WORLD]

# Страны, которые Family вырезал в сценарии без Азии
NO_ASIA_SEALED = ["USA", "JAP", "AST"]


def no_asia_effect():
    tags = " ".join(f"tag = {t}" for t in NO_ASIA_SEALED)
    return f"""# Сценарий «без Азии» из Family: Япония, США и Австралия под ИИ выключены из игры,
# а державы лора получают бонус малого мира (NO_asia)
every_country = {{
	limit = {{ OR = {{ {tags} }} is_ai = yes }}
	add_ideas = PAX_far_lands_sealed
	set_research_slots = 0
	country_lock_all_division_template = yes
}}
every_country = {{
	limit = {{ has_country_flag = pax_power NOT = {{ tag = ENG tag = GER }} }}
	add_ideas = PAX_small_world
}}
ENG = {{ add_ideas = PAX_small_world_ENG }}
GER = {{ add_ideas = {{ PAX_small_world PAX_small_world_GER }} }}"""


# Ещё три технологии, у которых в Family осталась только локализация (Family_l_russian.yml).
# Сами блоки в Family не нашлись, поэтому бонусы подобраны по смыслу названий.
EXTRA_TECHS = [
    ("modern_fire_control_system", "Современная система управления огнём",
     "Вводя курс, скорость и расстояние до цели, современный механический компьютер может точнее предсказать, где будет находиться цель, когда будет готов следующий залп.",
     {"naval_hit_chance": 0.05, "naval_torpedo_hit_chance_factor": 0.05}, 2.5, 1946, 8, 10, ["electronics"], None),
    ("modern_encryption", "Шифрование: продвинутый стандарт шифрования",
     "AES работает с блоками по 128 бит и ключами 128, 192 или 256 бит и защищает связь армии от чужих ушей.",
     {"encryption_factor": 0.5}, 2.5, 1947, 8, 12, ["electronics"], None),
    ("modern_decryption", "Дешифрование: анализ блочного шифра",
     "Анализ закономерностей в блоках символов и статистика позволяют вскрыть чужой шифр и прочитать исходное сообщение.",
     {"decryption_factor": 0.5}, 2.5, 1947, 8, 14, ["electronics"], None),
]


GUIDE_ECONOMY = (
    "Законы экономики взяты из Family. §HГражданская экономика§! даёт +30% к скорости строительства гражданских фабрик и +25% к инфраструктуре. "
    "Когда закончите строить фабрики, переключитесь на военную экономику: она снижает ТНП и ускоряет военные заводы и верфи. "
    "§HСвободная торговля§! усилена, §HЗакрытая экономика§! изменена.\\n\\n"
    "Технологии Family «Концентрированная и Рассредоточенная промышленность VI», «Строительство VI», «Разработка VI», "
    "улучшенные линии и переработка нефти и резины лежат в папке «Промышленность». До своего года (1941–1946) они идут со штрафом за опережение."
)
GUIDE_ARMY = (
    "Пока нет войны, у всех держав дух §HМирное небо§!: обучение армии вдвое быстрее, авиация и флот учатся без аварий и без расхода топлива. "
    "С первой войной он пропадает.\\n\\n"
    "Шаблоны дивизий меняются бесплатно, опыт армии, флота и авиации копится до 9999. Опыт дивизий от боёв не растёт, обучение даёт до 0.9. "
    "Сопротивления на оккупированных землях почти нет.\\n\\n"
    "Размен самолётов уменьшен (урон в воздушном бою 0.35 от ванильного), авиация не бьёт по снабжению и железным дорогам. "
    "Совет из Family: со старта обучайте одну дивизию на 50 ширины фронта, она быстро набирает опыт."
)


def economic_laws():
    t = _read("_economic.txt")
    # В Family у СССР был свой исторический запрет тотальной мобилизации до 22.06.1941.
    # Северное Царство PaxVanila живёт по лору, поэтому этот блок убран.
    t = re.sub(
        r"\n\t*if = \{\s*limit = \{\s*original_tag = SOV\s*has_dlc = \"Waking the Tiger\"\s*\}\s*"
        r"NOT = \{ has_idea = SOV_debaf_warstart \}\s*date > 1941\.6\.22\s*\}",
        "", t)
    assert "SOV_debaf_warstart" not in t, "не удалось убрать блок СССР из _economic.txt"
    return t


def defines():
    lines = []
    for line in _read("Family_defines.lua").splitlines():
        s = line.strip()
        # голая переменная без NDefines ничего не делает в игре, в Family она осталась по ошибке
        if s.startswith("MAX_AHEAD_RESEARCH_PENALTY"):
            continue
        lines.append(line)
    lines.append("")
    lines.append("-- Из CHADDFIXREBALANCE (Arthur): цены фокусов там урезаны вдвое (cost 10 -> 5), здесь так же для всех деревьев сразу.")
    lines.append("NDefines.NFocus.FOCUS_POINT_DAYS = 3.5")
    return "-- Мультиплеерные defines из «Family Historical MP mod» (Arthur).\n" + "\n".join(lines) + "\n"


TECH_NAMES = {
    "fuel_refining5": ("Нефтепереработка V", "Новые установки перегоняют нефть почти без отходов."),
    "fuel_refining6": ("Нефтепереработка VI", "Полностью автоматические нефтеперегонные заводы."),
}
_SUP = {"engineers": "Инженерные роты", "recon": "Разведывательные роты", "military_police": "Военная полиция",
        "maintenance_company": "Ремонтные роты", "sniper": "Снайперы", "raider": "Рейдеры",
        "field_hospital": "Полевые госпитали", "logistics_company": "Роты снабжения",
        "signal_company": "Роты связи", "command": "Штабные роты"}
_RN = ["", " II", " III", " IV"]
for _k, _n in _SUP.items():
    for _i in range(4):
        TECH_NAMES["tech_" + _k + ("" if _i == 0 else str(_i + 1))] = (_n + _RN[_i], f"Развитие и подготовка: {_n.lower()}.")
TECH_NAMES["tech_support"] = ("Вспомогательные роты", "Малые подразделения усиливают дивизии на поле боя.")
TECH_NAMES["support_weapons"] = ("Оружие поддержки", "Пулемётчики, миномётчики и военные псы идут вместе с пехотой.")

UNIT_NAMES = {
    "sniper": ("Снайперы", "Снайп."), "mortar": ("Миномётчики", "Мином."), "wardog": ("Военные псы", "Псы"),
    "gunner": ("Пулемётчики", "Пулем."), "raider": ("Рейдеры", "Рейд."), "field_hospital": ("Полевой госпиталь", "Госп."),
    "flamethrower_sppt": ("Огнемётчики", "Огнем."), "light_flame_tank": ("Лёгкие огнемётные танки", "Огн.тк"),
    "medium_flame_tank": ("Средние огнемётные танки", "Огн.тк"), "heavy_flame_tank": ("Тяжёлые огнемётные танки", "Огн.тк"),
}


SUPPORT_TECH = """technologies = {
	# Скрытая технология: открывает роты из Family. Выдаётся всем странам при старте (on_startup).
	pax_family_support = {
		enable_subunits = {
			gunner
			mortar
			wardog
			sniper
			raider
			field_hospital
			flamethrower_sppt
			light_flame_tank
			medium_flame_tank
			heavy_flame_tank
		}
		allow = { always = no }
		research_cost = 1
		start_year = 1936
		ai_will_do = { factor = 0 }
	}
}
"""


def _copy_tree(w):
    """Сквозной перенос файлов Family: доп. роты, их исследования, экономические решения."""
    for fn in sorted(os.listdir(os.path.join(SRC, "units"))):
        w("common/units/" + fn, _read("units/" + fn))
    # Файлы технологий Family (support, infantry, naval и др.) НЕ копируются: они от старой версии игры, и замена
    # ванильных файлов убирает новые технологии (cavity_magnatron, rangers_tech...), ломая скрипты ИИ и категории.
    # Вместо этого роты открывает скрытая технология pax_family_support (см. SUPPORT_TECH).
    w("common/technologies/pax_family_support.txt", SUPPORT_TECH)
    w("common/decisions/zz_family_economic.txt", _read("decisions/chd_economic.txt"))
    # Деревья фокусов Arthur из CHADDFIXREBALANCE (его правка Chaddhaus MP): великие державы и лорные страны.
    # Имена файлов как у ванили, поэтому заменяют ванильные деревья (версия 1.13.7).
    for fn in sorted(os.listdir(os.path.join(SRC, "national_focus"))):
        w("common/national_focus/" + fn, _read("national_focus/" + fn))
    w("common/ideas/chd_focus_ideas.txt", _read("ideas_chd_focus_ideas.txt"))
    chd = _read("loc/chd_focuses.yml").split("\n", 1)[1]
    for lang in ("russian", "english"):
        w(f"localisation/{lang}/chd_focuses_l_{lang}.yml", f"l_{lang}:\n" + chd, bom=True)


def _loc_from(path, wanted_text):
    out = {}
    with open(os.path.join(SRC, "loc", path), encoding="utf-8-sig") as f:
        for line in f:
            m = re.match(r'\s+([A-Za-z0-9_.\-]+):\d*\s+"(.*)"\s*$', line)
            if m and re.search(r"(?<![A-Za-z0-9_])" + re.escape(m.group(1)) + r"(?![A-Za-z0-9_])", wanted_text):
                out[m.group(1)] = m.group(2)
    return out


def build(w, LOC, indent):
    _copy_tree(w)
    LOC.update(_loc_from('decisions_l_russian.yml', _read('decisions/chd_economic.txt')))
    LOC['pax_family_support'] = 'Роты Family'
    LOC['pax_family_support_desc'] = 'Снайперы, миномётчики, военные псы, огнемётчики и другие роты из Family.'
    for uid, (n, s) in UNIT_NAMES.items():
        LOC[uid] = n
        LOC[uid + '_short'] = s
        LOC[uid + '_desc'] = n

    w("common/ideas/_economic.txt", economic_laws())
    w("common/defines/pax_family_defines.lua", defines())

    blocks = []
    for tid, name, desc, mod, cost, year, x, y, cats, nxt in FAMILY_TECHS + EXTRA_TECHS:
        if tid in FAMILY_IN_FILES:
            LOC[tid] = name
            LOC[tid + "_desc"] = desc
            continue
        b = [f"{k} = {v}" for k, v in mod.items()]
        if tid in TECH_EXTRA:
            b.append(TECH_EXTRA[tid])
        if nxt:
            b.append(f"path = {{ leads_to_tech = {nxt} research_cost_coeff = 1 }}")
        b += [f"research_cost = {cost}", f"start_year = {year}",
              f"folder = {{ name = {'electronics_folder' if 'electronics' in cats else 'industry_folder'} position = {{ x = {x} y = {y} }} }}",
              "categories = { " + " ".join(cats) + " }",
              "ai_will_do = { factor = 5 modifier = { factor = 10 date > \"1943.1.1\" } }"]
        blocks.append(f"{tid} = {{\n" + indent("\n".join(b), 1) + "\n}")
        LOC[tid] = name
        LOC[tid + "_desc"] = desc
    w("common/technologies/pax_family_techs.txt",
      "# Технологии из «Family Historical MP mod»\ntechnologies = {\n" + "\n\n".join(indent(b, 1) for b in blocks) + "\n}\n")

    LOC.update({
        "PAX_small_world": "Малый мир",
        "PAX_small_world_desc": "Сценарий «без Азии»: дальние земли молчат, и державы лора строят быстрее. Взято из Family (NO_asia).",
        "PAX_small_world_ENG": "Малый мир: острова",
        "PAX_small_world_ENG_desc": "Островной Союз строит быстрее и держится дольше. Взято из Family (NO_asia_ENG).",
        "PAX_small_world_GER": "Малый мир: дешёвые крылья",
        "PAX_small_world_GER_desc": "Лёгкие самолёты Рейха на 15% дешевле. Взято из Family (NO_asia_GER).",
        "PAX_far_lands_sealed": "Закрытые дальние земли",
        "PAX_far_lands_sealed_desc": "В сценарии «без Азии» эта страна выключена из игры, как e_neutral в Family.",
        "PAX_peaceful_sky": "Мирное небо",
        "PAX_peaceful_sky_desc": "Пока пушки молчат, армия учится без потерь. Дух пропадает с первой войной. Взято из Family.",
        "pax.40.t": "Вы хотите Тотальной Войны?",
        "pax.40.d": "Вы устроили Тотальную войну... Чем всё это закончится? Кто выиграет? ВАМ предстоит узнать это.\\n\\nС уважением, разработчики Family mod.",
        "pax.40.a": "МЫ ВЫИГРАЕМ, Я ВАС УВЕРЯЮ!!",
        "pax.20.b": "О мире PaxVanila",
        "pax.20.c": "Экономика",
        "pax.20.e": "Армия и авиация",
        "pax.21.t": "Гайд о мире",
        "pax.22.t": "Гайд об экономике",
        "pax.22.d": GUIDE_ECONOMY,
        "pax.23.t": "Гайд об армии и авиации",
        "pax.23.d": GUIDE_ARMY,
        "pax.21.a": "Вернуться назад",
        "pax.21.b": "Выйти из гайда",
    })


EVENTS = """
# Путеводитель с разделами, как гайд basa_basa в Family
country_event = {
	id = pax.20
	title = pax.20.t
	desc = pax.20.d
	is_triggered_only = yes
	option = { name = pax.20.b country_event = { id = pax.21 } }
	option = { name = pax.20.c country_event = { id = pax.22 } }
	option = { name = pax.20.e country_event = { id = pax.23 } }
	option = { name = pax.20.a }
}
country_event = {
	id = pax.21
	title = pax.21.t
	desc = pax.21.d
	is_triggered_only = yes
	option = { name = pax.21.a country_event = { id = pax.20 } }
	option = { name = pax.21.b }
}
country_event = {
	id = pax.22
	title = pax.22.t
	desc = pax.22.d
	is_triggered_only = yes
	option = { name = pax.21.a country_event = { id = pax.20 } }
	option = { name = pax.21.b }
}
country_event = {
	id = pax.23
	title = pax.23.t
	desc = pax.23.d
	is_triggered_only = yes
	option = { name = pax.21.a country_event = { id = pax.20 } }
	option = { name = pax.21.b }
}

# «Вы хотите Тотальной Войны?» (Familyevents.81), приходит после фокуса «Тотальная война»
country_event = {
	id = pax.40
	title = pax.40.t
	desc = pax.40.d
	picture = GFX_report_event_radar_01
	is_triggered_only = yes
	option = { name = pax.40.a }
}
"""
