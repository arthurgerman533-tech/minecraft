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

TECH_EXTRA = {
    "excavation6": """on_research_complete = {
	modify_building_resources = { building = aluminum_mill resource = aluminium amount = 4 }
	modify_building_resources = { building = steel_mill resource = steel amount = 4 }
}""",
    "improved_modern_rubber_processing": """on_research_complete = {
	modify_building_resources = { building = synthetic_refinery resource = rubber amount = 1 }
}
show_effect_as_desc = yes""",
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
    return "-- Мультиплеерные defines из «Family Historical MP mod» (Arthur), без изменений.\n" + "\n".join(lines) + "\n"


def build(w, LOC, indent):
    w("common/ideas/_economic.txt", economic_laws())
    w("common/defines/pax_family_defines.lua", defines())

    blocks = []
    for tid, name, desc, mod, cost, year, x, y, cats, nxt in FAMILY_TECHS:
        b = [f"{k} = {v}" for k, v in mod.items()]
        if tid in TECH_EXTRA:
            b.append(TECH_EXTRA[tid])
        if nxt:
            b.append(f"path = {{ leads_to_tech = {nxt} research_cost_coeff = 1 }}")
        b += [f"research_cost = {cost}", f"start_year = {year}",
              f"folder = {{ name = industry_folder position = {{ x = {x} y = {y} }} }}",
              "categories = { " + " ".join(cats) + " }",
              "ai_will_do = { factor = 5 modifier = { factor = 10 date > \"1943.1.1\" } }"]
        blocks.append(f"{tid} = {{\n" + indent("\n".join(b), 1) + "\n}")
        LOC[tid] = name
        LOC[tid + "_desc"] = desc
    w("common/technologies/pax_family_techs.txt",
      "# Технологии из «Family Historical MP mod»\ntechnologies = {\n" + "\n\n".join(indent(b, 1) for b in blocks) + "\n}\n")

    LOC.update({
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
