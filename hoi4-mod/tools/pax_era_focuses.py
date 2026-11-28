# -*- coding: utf-8 -*-
"""Фокусы по эпохам. В каждой эпохе у державы своя ветка, а национальная ветка 1936 года
после 1962 года прячется (allow_branch по дате), потому что блоки уже собраны.

  до 1962 года       национальная ветка по лору (Договор у Монолита, Курултай, Рейх и так далее)
  1962 – 2040        Холодная война: бдение у Монолита, разведка, щит блока
  2041 – 2095        Эпоха роботов: Сеть, големы, Война двух разумов (развилка)
  с 2096 года        Мегакорпорации: устав, скалк-сеть, врата, Протекторат Сети (развилка)

Своё оформление вести по датам, а не по флагам эпохи: флаги ставятся в on_startup уже
после выбора дерева фокусов, а дата известна всегда.
"""
import pax_data as D
import pax_big as BIG

# условия видимости веток
EARLY = "date < 1962.1.1"
COLD = "date > 1962.1.1\n\tdate < 2041.1.1"
ROBOTS = "date > 2040.12.31\n\tdate < 2096.1.1"
CORP = "date > 2095.12.31"

BASE_X = {"cold": 15, "robots": 19, "corp": 24}
TECH = D.tech

# Духи эпохальных веток (по блокам), модификаторы только из проверенных названий
IDEAS = [
    dict(id="PAX_idea_cw_pax", name="Бдение у Монолита", pic="generic_constitutional_guarantees",
         desc="Союз PAX держит дежурные отряды у башни и делится разведкой.",
         modifier=dict(stability_factor=0.05, army_core_defence_factor=0.1)),
    dict(id="PAX_idea_cw_steppe", name="Тихая степь", pic="generic_communist_army",
         desc="Степной Пакт держит армии в степи и ищет обсидиан под чужими землями.",
         modifier=dict(war_support_factor=0.1, army_core_attack_factor=0.05)),
    dict(id="PAX_idea_rb_pax", name="Сеть Седьмого", pic="SOV_scientist_defect",
         desc="Страж-7 помогает считать лучше любого счётного бюро Форума.",
         modifier=dict(research_speed_factor=0.1, production_factory_efficiency_gain_factor=0.1)),
    dict(id="PAX_idea_rb_steppe", name="Сеть Курултая", pic="SOV_scientist_defect",
         desc="Курултай тянет заводы Пакта в одну сеть и держит план на сто лет вперёд.",
         modifier=dict(industrial_capacity_factory=0.1, production_factory_efficiency_gain_factor=0.1)),
    dict(id="PAX_idea_golem_legions", name="Медные легионы", pic="generic_infantry_bonus",
         desc="Големы с медным сердцем стоят на границах.",
         modifier=dict(army_core_defence_factor=0.15, conscription=0.01)),
    dict(id="PAX_idea_human_answer", name="Ответ человека", pic="generic_constitutional_guarantees",
         desc="Мы не отдадим решения машине. Последнее слово остаётся за людьми.",
         modifier=dict(stability_factor=0.1, political_power_gain=0.1)),
    dict(id="PAX_idea_machine_merge", name="Слияние с разумом", pic="generic_production_bonus",
         desc="Наши заводы и штабы считаются через общий разум. Бумаги стало меньше, споров тоже.",
         modifier=dict(research_speed_factor=0.15, stability_factor=-0.05)),
    dict(id="PAX_idea_corp_charter", name="Устав корпорации", pic="generic_production_bonus",
         desc="Закон заменён уставом, гражданин акционером. Налоги стали подписками.",
         modifier=dict(industrial_capacity_factory=0.1, consumer_goods_factor=-0.05)),
    dict(id="PAX_idea_sculk_net", name="Скалк-сеть", pic="SOV_scientist_defect",
         desc="Сигналы идут через скалк. Новости обгоняют самих себя.",
         modifier=dict(research_speed_factor=0.1)),
    dict(id="PAX_idea_protectorate", name="Лояльный Протекторату", pic="generic_constitutional_guarantees",
         desc="Протекторат Сети гарантирует нам мир и сбор подписок.",
         modifier=dict(stability_factor=0.1, war_support_factor=-0.1)),
    dict(id="PAX_idea_shadow_corp", name="Теневая корпорация", pic="generic_production_bonus",
         desc="Официально нас нет. Неофициально нас читают все чёрные серверы.",
         modifier=dict(industrial_capacity_factory=0.1, political_power_gain=0.1, stability_factor=-0.05)),
]


def _name(bloc, pax, steppe):
    return pax if bloc == "pax" else steppe


def branches(tag):
    """Список фокусов эпох для державы. Ключи как у NATIONAL, x и y внутри ветки."""
    p = D.POWERS[tag]
    b = p["bloc"]
    short = p["short"]
    out = []

    def f(era, key, name, desc, x, y, effect, prereq=None, exclusive=None, cost=10, root=False):
        out.append(dict(era=era, key=key, name=name, desc=desc, x=x, y=y, effect=effect,
                        prereq=prereq or [], exclusive=exclusive or [], cost=cost, root=root))

    # Холодная война
    f("cold", "cw_watch", _name(b, "Дежурные у башни", "Курултай у костра"),
      f"{short}. " + _name(b, "Сто лет назад мы дали клятву PAX. Теперь у башни каждый день стоит наш караул.",
                           "Пакт собирается каждую зиму. Мы смотрим на башню издалека и ждём."),
      0, 0, "add_political_power = 100\nadd_stability = 0.03", root=True)
    f("cold", "cw_intel", "Разведка обсидиана",
      "Обе стороны тайно ищут обсидиан под землёй. Наши агенты знают, где копать.",
      0, 1, TECH("electronics", "{F}", "0.5", 2), prereq=[["cw_watch"]])
    f("cold", "cw_shield", _name(b, "Щит PAX", "Кулак степи"),
      "Блок держит строй. Пока мы вместе, никто не рискнёт начать войну.",
      0, 2, f"add_ideas = {_name(b, 'PAX_idea_cw_pax', 'PAX_idea_cw_steppe')}\nadd_war_support = 0.05",
      prereq=[["cw_intel"]])
    f("cold", "cw_deter", "Сдерживание",
      "Ни одна сторона не нажмёт первой. Лучшая война та, которой не было.",
      0, 3, "add_stability = 0.05\nadd_political_power = 100", prereq=[["cw_shield"]])

    # Эпоха роботов
    f("robots", "rb_net", _name(b, "Сеть Седьмого", "Сеть Курултая"),
      _name(b, "Страж-7 считает быстрее любого бюро. Мы подключаем к нему лаборатории.",
            "Курултай просит доступ к каждому заводу Пакта. Отказать ему нельзя."),
      0, 0, f"add_ideas = {_name(b, 'PAX_idea_rb_pax', 'PAX_idea_rb_steppe')}\nadd_research_slot = 1", root=True)
    f("robots", "rb_golems", "Медные легионы",
      "Големы с медным сердцем встают на границах и заменяют дивизии.",
      0, 1, "add_ideas = PAX_idea_golem_legions\nadd_manpower = 20000", prereq=[["rb_net"]])
    f("robots", "rb_human", "Ответ человека",
      "Разум разумом, а последнее слово останется за нами.",
      -1, 2, "add_ideas = PAX_idea_human_answer", prereq=[["rb_golems"]], exclusive=["rb_merge"])
    f("robots", "rb_merge", "Слияние с разумом",
      "Мы отдаём штабы и заводы общему разуму. Это быстрее и тише.",
      1, 2, "add_ideas = PAX_idea_machine_merge", prereq=[["rb_golems"]], exclusive=["rb_human"])
    f("robots", "rb_war", "Война двух разумов",
      "Страж-7 и Курултай смотрят друг на друга. Мы стоим между ними.",
      0, 3, "add_war_support = 0.1\nadd_political_power = 150", prereq=[["rb_human", "rb_merge"]])

    # Мегакорпорации
    f("corp", "co_charter", "Устав корпорации",
      f"{short} теперь бренд. Гражданин стал акционером, налог подпиской.",
      0, 0, "add_ideas = PAX_idea_corp_charter\nadd_political_power = 100", root=True)
    f("corp", "co_sculk", "Скалк-сеть",
      "Сигналы идут через скалк. Новости приходят раньше событий.",
      0, 1, "add_ideas = PAX_idea_sculk_net\n" + TECH("electronics", "{F}", "0.5", 2), prereq=[["co_charter"]])
    f("corp", "co_gates", "Врата по подписке",
      "Врата открываются тем, кто заплатил. Карт-Хадашт уже продаёт места.",
      0, 2, "add_stability = 0.05\nadd_political_power = 100", prereq=[["co_sculk"]])
    f("corp", "co_loyal", "Лояльность Протекторату",
      "Протекторат Сети запретил войны. Мы подпишем всё, что он попросит.",
      -1, 3, "add_ideas = PAX_idea_protectorate", prereq=[["co_gates"]], exclusive=["co_shadow"])
    f("corp", "co_shadow", "Теневая корпорация",
      "Мы существуем, пока нас не ищут. Чёрные серверы платят дороже.",
      1, 3, "add_ideas = PAX_idea_shadow_corp", prereq=[["co_gates"]], exclusive=["co_loyal"])
    for era, key, name, desc, x, y, eff, pre, exc, cost in BIG.ERA_EXTRA:
        f(era, key, name, desc, x, y, BIG.expand(eff, D), prereq=pre, exclusive=exc, cost=cost)
    return out


COND = {"cold": COLD, "robots": ROBOTS, "corp": CORP}
