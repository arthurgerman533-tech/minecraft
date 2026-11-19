"""Упрощённое меню экономики в духе Millennium Dawn.
Родные механики MD (бюджет, энергия, население) в ванили невозможны, поэтому каждая «ручка»
это набор из 3 режимов: выбранный режим вешает динамический модификатор и снимает остальные."""

GROUPS = [
 ("tax", "Налоги", "Налоговая политика казны.", [
   ("low", "Низкие налоги", "Казна беднее, народ доволен.", {"consumer_goods_factor": -0.05, "stability_factor": 0.05, "political_power_factor": -0.05}),
   ("mid", "Умеренные налоги", "Золотая середина, без бонусов и штрафов.", {"consumer_goods_factor": 0.0}),
   ("high", "Высокие налоги", "Казна полна, народ ворчит.", {"consumer_goods_factor": 0.05, "stability_factor": -0.05, "political_power_factor": 0.08}),
 ]),
 ("fund", "Финансирование", "Куда идут деньги бюджета.", [
   ("civ", "Упор на гражданское", "Фабрики и стройки дешевле, армия ждёт.", {"production_speed_buildings_factor": 0.1, "conversion_cost_civ_to_mil_factor": 0.15}),
   ("bal", "Баланс бюджета", "Ровное финансирование всего.", {"industrial_capacity_factory": 0.02}),
   ("mil", "Упор на военное", "Армия получает больше, стройки медленнее.", {"production_speed_buildings_factor": -0.1, "conversion_cost_civ_to_mil_factor": -0.15, "war_support_factor": 0.05}),
 ]),
 ("trade", "Торговля", "Внешняя торговля державы.", [
   ("open", "Открытые рынки", "Больше торговли, больше уважения за рубежом.", {"trade_opinion_factor": 0.25, "consumer_goods_factor": -0.03}),
   ("mix", "Выборочная торговля", "Торгуем с теми, с кем выгодно.", {"research_speed_factor": 0.01}),
   ("closed", "Протекционизм", "Свои фабрики растут, чужие товары дороже.", {"trade_opinion_factor": -0.15, "production_factory_max_efficiency_factor": 0.05}),
 ]),
 ("energy", "Энергетика и топливо", "Как страна добывает энергию и топливо.", [
   ("fossil", "Нефть и уголь", "Дёшево и быстро, но топлива уходит больше.", {"industrial_capacity_factory": 0.05, "fuel_gain_factor": 0.1}),
   ("atom", "Атомная энергия", "Дорогой старт, потом стабильная энергия.", {"production_speed_buildings_factor": -0.05, "research_speed_factor": 0.05, "industrial_capacity_factory": 0.08}),
   ("green", "Зелёная энергия", "Чистая сеть и меньше расходов на топливо.", {"fuel_gain_factor": 0.05, "stability_factor": 0.03, "production_factory_max_efficiency_factor": 0.03}),
 ]),
]


def build(w, LOC, indent):
    w("common/decisions/categories/pax_economy_categories.txt",
      "PAX_economy_category = {\n\ticon = generic_research\n\tvisible = { is_ai = no }\n}\n")
    LOC["PAX_economy_category"] = "Экономика"
    LOC["PAX_economy_category_desc"] = ("Упрощённое меню экономики в духе Millennium Dawn: налоги, финансирование, торговля, энергетика. "
                                        "В каждой группе действует один режим, его можно менять за политическую власть.")
    mods, decs = [], []
    for gk, gname, gdesc, modes in GROUPS:
        for k, name, desc, eff in modes:
            mid = f"PAX_eco_{gk}_{k}"
            body = "\n".join(f"\t{a} = {b}" for a, b in eff.items())
            LOC[mid] = f"{gname}: {name}"
            others = [o for o, *_ in modes if o != k]
            rem = "\n".join(f"\t\t\tif = {{ limit = {{ has_dynamic_modifier = {{ modifier = PAX_eco_{gk}_{o} }} }} remove_dynamic_modifier = {{ modifier = PAX_eco_{gk}_{o} }} }}" for o in others)
            decs.append(
                f"{mid} = {{\n\ticon = generic_research\n"
                f"\tvisible = {{ is_ai = no }}\n"
                f"\tavailable = {{ NOT = {{ has_dynamic_modifier = {{ modifier = {mid} }} }} }}\n"
                f"\tcost = 25\n\tcomplete_effect = {{\n{rem}\n"
                f"\t\tadd_dynamic_modifier = {{ modifier = {mid} }}\n\t}}\n\tai_will_do = {{ factor = 0 }}\n}}")
            LOC[mid + "_desc"] = f"{desc} Режим группы «{gname}»: {name}."
            LOC[mid.replace("PAX_eco", "PAX_eco")] = LOC[mid]
    w("common/dynamic_modifiers/pax_economy_modifiers.txt", "\n\n".join(mods) + "\n")
    w("common/decisions/pax_economy_decisions.txt", "PAX_economy_category = {\n" + "\n\n".join(indent(d, 1) for d in decs) + "\n}\n")
