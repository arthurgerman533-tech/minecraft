# -*- coding: utf-8 -*-
"""Масштабные фокусы: «Великие свершения» (ряды 4-6 в каждой из трёх веток) и расширенные ветки эпох.

extend(D) дописывает фокусы и духи в pax_data до сборки. Эффекты только из проверенных:
заводы через CIV/MIL/DOCK, add_research_slot, add_manpower, опыт, add_ideas, технологические бонусы.
"""

BIG_FOCUSES = [
    # Промышленность
    dict(key="ind4", name="Великая стройка", x=0, y=3, cost=14, prereq=[["ind3"]],
         icon="GFX_goal_generic_construct_civ_factory",
         desc="Республика строит по плану на десятилетия. Каждый город получает завод, каждый завод свою железнодорожную ветку.",
         effect="CIV3"),
    dict(key="ind5", name="Города-заводы", x=0, y=4, cost=14, prereq=[["ind4"]],
         icon="GFX_goal_generic_construct_mil_factory",
         desc="Целые города переходят на выпуск оружия. Рабочие кварталы растут вокруг цехов.",
         effect="MIL3\nadd_ideas = PAX_idea_factory_cities"),
    dict(key="ind6", name="Эпоха стали", x=0, y=5, cost=14, prereq=[["ind5"]],
         icon="GFX_goal_generic_construction",
         desc="Сталь, уголь и пар дают державе больше, чем любая война. Лаборатории Форума открывают ещё одну кафедру.",
         effect="add_research_slot = 1\nadd_ideas = PAX_idea_age_of_steel\nTECHI"),
    # Армия
    dict(key="mil4", name="Новая армия", x=2, y=3, cost=14, prereq=[["mil3"]],
         icon="GFX_goal_generic_allies_build_infantry",
         desc="Старые легионы переучиваются на винтовки, пулемёты и бронетехнику. Главное: слушать штаб, а не память.",
         effect="army_experience = 50\nadd_manpower = 40000\nTECHA"),
    dict(key="mil5", name="Школа штаба", x=2, y=4, cost=14, prereq=[["mil4"]],
         icon="GFX_goal_generic_defence",
         desc="Штаб изучает ошибки прошлых войн. Генералы идут на курсы вместе с лейтенантами.",
         effect="army_experience = 50\nadd_ideas = PAX_idea_staff_school\nadd_political_power = 100"),
    dict(key="mil6", name="Сто легионов", x=2, y=5, cost=14, prereq=[["mil5"]],
         icon="GFX_goal_generic_major_war",
         desc="Республика призывает всех, кто может держать оружие. Страна становится одним большим лагерем.",
         effect="add_manpower = 80000\nadd_ideas = PAX_idea_hundred_legions\nadd_war_support = 0.05"),
    # Экономика
    dict(key="eco4", name="Золотой век торговли", x=4, y=3, cost=14, prereq=[["eco3"]],
         icon="GFX_goal_generic_consumer_goods",
         desc="Торговые дома открывают конторы по всему миру. Казна полна, а порты не успевают принимать грузы.",
         effect="DOCK\nCIV\nadd_political_power = 150"),
    dict(key="eco5", name="Союз договоров", x=4, y=4, cost=14, prereq=[["eco4"]],
         icon="GFX_goal_generic_improve_relations",
         desc="Сотня договоров связывает державу с соседями. Нарушить хоть один значит потерять все.",
         effect="add_ideas = PAX_idea_treaty_web\nadd_stability = 0.05"),
    dict(key="eco6", name="Мировая держава", x=4, y=5, cost=14, prereq=[["eco5"]],
         icon="GFX_goal_generic_political_pressure",
         desc="Слово державы слышно от Монолита до дальних земель. Её валюта в каждом кармане.",
         effect="add_stability = 0.05\nadd_political_power = 200\nadd_ideas = PAX_idea_world_power"),
]

BIG_IDEAS = [
    dict(id="PAX_idea_factory_cities", name="Города-заводы",
         desc="Рабочие кварталы растут вокруг цехов.", modifier=dict(industrial_capacity_factory=0.1, production_factory_efficiency_gain_factor=0.05),
         pic="generic_production_bonus"),
    dict(id="PAX_idea_age_of_steel", name="Эпоха стали",
         desc="Сталь и пар дают державе больше, чем война.", modifier=dict(research_speed_factor=0.1, production_speed_buildings_factor=0.1),
         pic="generic_production_bonus"),
    dict(id="PAX_idea_staff_school", name="Школа штаба",
         desc="Штаб учится на ошибках прошлых войн.", modifier=dict(army_org_factor=0.05, experience_gain_army=0.15),
         pic="generic_infantry_bonus"),
    dict(id="PAX_idea_hundred_legions", name="Сто легионов",
         desc="Страна стала одним большим лагерем.", modifier=dict(conscription=0.02, army_attack_factor=0.05, stability_factor=-0.05),
         pic="generic_infantry_bonus"),
    dict(id="PAX_idea_treaty_web", name="Сеть договоров",
         desc="Сотня договоров держит соседей на привязи.", modifier=dict(political_power_gain=0.15, stability_factor=0.05),
         pic="generic_constitutional_guarantees"),
    dict(id="PAX_idea_world_power", name="Мировая держава",
         desc="Слово державы слышно от Монолита до дальних земель.", modifier=dict(political_power_factor=0.15, consumer_goods_factor=-0.05),
         pic="italy_control"),
]

# Расширение эпох: (era, key, name, desc, x, y, effect, prereq, exclusive, cost)
ERA_EXTRA = [
    # Холодная война: три крыла после «Щита»
    ("cold", "cw_arms", "Гонка вооружений", "Обе стороны складывают снаряды в погреба. Заводы работают в три смены.", -1, 2,
     "MIL3", [["cw_intel"]], [], 14),
    ("cold", "cw_spies", "Тени у башни", "Агенты Союза и Пакта играют в игру, правила которой знают только они.", 1, 2,
     "add_political_power = 150\nTECHI", [["cw_intel"]], [], 14),
    ("cold", "cw_bunkers", "Подземные убежища", "Если башня упадёт, под землёй должны остаться люди и станки.", -1, 3,
     "add_ideas = PAX_idea_cw_bunkers\nCIV", [["cw_arms"]], [], 14),
    ("cold", "cw_diplo", "Переговоры у Монолита", "Каждые пять лет послы собираются у башни и обещают не стрелять.", 1, 3,
     "add_stability = 0.05\nadd_political_power = 150", [["cw_spies"]], [], 14),
    ("cold", "cw_balance", "Равновесие страха", "Мир держится, пока обе стороны боятся друг друга.", 0, 4,
     "add_stability = 0.05\nadd_war_support = 0.05\nadd_ideas = PAX_idea_cw_balance", [["cw_deter", "cw_bunkers", "cw_diplo"]], [], 18),
    # Эпоха роботов
    ("robots", "rb_factories", "Автоматические заводы", "Конвейеры больше не ждут людей. Люди смотрят, чтобы ничего не сломалось.", -2, 1,
     "CIV3\nadd_ideas = PAX_idea_auto_factories", [["rb_net"]], [], 14),
    ("robots", "rb_labs", "Лаборатории Седьмого", "Разум помогает ставить опыты и читать результаты быстрее любого учёного.", 2, 1,
     "add_research_slot = 1\nTECHI", [["rb_net"]], [], 14),
    ("robots", "rb_drones", "Дроны разведки", "Лёгкие машины облетают границы и видят дальше любого часового.", -2, 2,
     "army_experience = 50\nTECHA", [["rb_factories"]], [], 14),
    ("robots", "rb_cyber", "Нейроинтерфейсы", "Командиры подключают штаб прямо к разуму. Приказ идёт мгновенно.", 2, 2,
     "add_ideas = PAX_idea_neuro_link\nadd_political_power = 100", [["rb_labs"]], [], 14),
    ("robots", "rb_peace", "Договор двух разумов", "Машины сели за стол раньше людей. Остальным остаётся подписать.", 0, 4,
     "add_stability = 0.1\nadd_political_power = 200", [["rb_war"]], [], 18),
    # Мегакорпорации
    ("corp", "co_ads", "Реклама в каждом доме", "Реклама заменила лозунги. Подписка заменила налог.", -2, 1,
     "add_political_power = 150\nadd_ideas = PAX_idea_ad_empire", [["co_charter"]], [], 14),
    ("corp", "co_security", "Корпоративная охрана", "Частные армии защищают офисы и склады лучше государственных.", 2, 1,
     "MIL3\nadd_manpower = 30000", [["co_charter"]], [], 14),
    ("corp", "co_monopoly", "Монополия на связь", "Скалк-сеть принадлежит нам. Всё остальное можно арендовать.", -2, 2,
     "CIV3\nadd_ideas = PAX_idea_comm_monopoly", [["co_ads"]], [], 14),
    ("corp", "co_black", "Чёрные серверы", "Архивы, которых нет, хранят всё, что мы забыли.", 2, 2,
     "TECHI\nadd_political_power = 100", [["co_security"]], [], 14),
    ("corp", "co_summit", "Совет директоров мира", "Десять корпораций сидят за одним столом. Решает тот, кто платит больше.", 0, 5,
     "add_stability = 0.1\nadd_political_power = 250\nadd_ideas = PAX_idea_board_of_world", [["co_loyal", "co_shadow"]], [], 21),
]

ERA_IDEAS = [
    dict(id="PAX_idea_cw_bunkers", name="Подземные убежища", desc="Под городами лежат склады и мастерские.",
         modifier=dict(stability_factor=0.05, industry_air_damage_factor=-0.1), pic="generic_constitutional_guarantees"),
    dict(id="PAX_idea_cw_balance", name="Равновесие страха", desc="Мир держится на взаимном страхе.",
         modifier=dict(war_support_factor=0.05, political_power_gain=0.1), pic="generic_constitutional_guarantees"),
    dict(id="PAX_idea_auto_factories", name="Автоматические заводы", desc="Конвейеры не ждут людей.",
         modifier=dict(industrial_capacity_factory=0.1, production_factory_efficiency_gain_factor=0.1), pic="generic_production_bonus"),
    dict(id="PAX_idea_neuro_link", name="Нейроинтерфейсы", desc="Приказ идёт напрямую от штаба к войскам.",
         modifier=dict(army_org_factor=0.1, research_speed_factor=0.05, stability_factor=-0.05), pic="SOV_scientist_defect"),
    dict(id="PAX_idea_ad_empire", name="Империя рекламы", desc="Подписка заменила налог.",
         modifier=dict(political_power_gain=0.1, consumer_goods_factor=-0.05), pic="free_trade"),
    dict(id="PAX_idea_comm_monopoly", name="Монополия на связь", desc="Вся связь принадлежит корпорации.",
         modifier=dict(research_speed_factor=0.1, industrial_capacity_factory=0.05), pic="SOV_scientist_defect"),
    dict(id="PAX_idea_board_of_world", name="Совет директоров мира", desc="Десять корпораций делят мир за одним столом.",
         modifier=dict(stability_factor=0.05, political_power_factor=0.1, industrial_capacity_factory=0.1), pic="generic_production_bonus"),
]

# подстановки сокращений в effect
def expand(effect, D):
    rep = {
        "CIV3": "\n".join([D.CIV] * 3),
        "MIL3": "\n".join([D.MIL] * 3),
        "TECHI": D.tech("industry", "{F}", "0.5", 2),
        "TECHA": D.tech("infantry_weapons", "{F}", "0.5", 2),
    }
    out = []
    for line in effect.split("\n"):
        out.append(rep.get(line.strip(), line))
    # CIV/MIL/DOCK — многострочные блоки; ключевое слово в отдельной строке
    res = "\n".join(out)
    for k, v in (("DOCK", D.DOCK), ("CIV", D.CIV), ("MIL", D.MIL)):
        res = "\n".join(v if l.strip() == k else l for l in res.split("\n"))
    return res


def extend(D):
    for f in BIG_FOCUSES:
        D.GENERIC_FOCUSES.append(dict(f, effect=expand(f["effect"], D)))
    for i in BIG_IDEAS + ERA_IDEAS:
        D.GENERIC_IDEAS.append(dict(id=i["id"], name=i["name"], desc=i["desc"], modifier=i["modifier"]))
        D.IDEA_PICTURES[i["id"]] = i["pic"]
