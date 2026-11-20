# -*- coding: utf-8 -*-
"""Данные мода PaxVanila для Hearts of Iron IV.

Всё содержимое мода (державы, лидеры, фокусы, идеи, тексты) лежит здесь.
Файлы игры собирает build_mod.py: правьте этот файл и запускайте сборку заново.

Державы лора занимают реальные страны ванильной карты (теги HOI4):
  Союз PAX:      ITA Ромея, SPR Карфаген, GRE Эллада, FRA Галлия, ENG Островной Союз
  Степной Пакт:  GER Германия, SOV Северное Царство, ROM Дакия, TUR Орда, PER Скифия
"""

# ---------------------------------------------------------------------------
# Державы
# ---------------------------------------------------------------------------
# ruling: правящая идеология HOI4 (democratic / fascism / communism / neutrality)
# leader: персонаж; ideology = подтип HOI4 (conservatism, liberalism, socialism,
#   fascism_ideology, nazism, marxism, stalinism, despotism, oligarchism)
# flag: рисунок флага для build_mod.py

POWERS = {
    "ITA": dict(
        lore_id="romea", bloc="pax",
        name="Священная Ромейская Республика", short="Ромея", adj="ромейский",
        color=(176, 54, 43), accent=(232, 190, 72),
        flag=dict(kind="disc_obelisk"),
        ruling="democratic",
        popularities=dict(democratic=60, fascism=15, communism=10, neutrality=15),
        leader=dict(id="ITA_pax_romul", name="Ромул Двести Пятый", ideology="conservatism",
                    desc="Каждый правитель Ромеи при вступлении на престол берёт имя Ромул. Этот хранит печать с 1931 года и помнит, как в 1914 на башне появилась первая трещина."),
        spirit=dict(id="PAX_spirit_ITA", name="Хранители Печати",
                    desc="Ромея стоит у самого Монолита. Её сенаторы клянутся словом PAX, а летописцы Форума записывают всё, что происходит у башни.",
                    modifier=dict(stability_factor=0.05, political_power_gain=0.1)),
    ),
    "SPR": dict(
        lore_id="carthage", bloc="pax",
        name="Карфагенская Торговая Держава", short="Карфаген", adj="карфагенский",
        color=(208, 138, 30), accent=(110, 40, 90),
        flag=dict(kind="crescent_band"),
        ruling="neutrality",
        popularities=dict(democratic=30, fascism=10, communism=10, neutrality=50),
        leader=dict(id="SPR_pax_hannon", name="Суффет Ганнон Барка", ideology="oligarchism",
                    desc="Глава Совета суффетов и хозяин Золотого Каравана. Говорит, что лучшая война та, на которой зарабатывают обе стороны."),
        spirit=dict(id="PAX_spirit_SPR", name="Золотой Караван",
                    desc="Карфаген вырос из купцов Ур-Кадима. Его караваны и корабли ходят ко всем берегам мира.",
                    modifier=dict(consumer_goods_factor=-0.03, trade_opinion_factor=0.2)),
    ),
    "GRE": dict(
        lore_id="hellas", bloc="pax",
        name="Эллинская Республика", short="Эллада", adj="эллинский",
        color=(47, 127, 181), accent=(245, 245, 245),
        flag=dict(kind="waves"),
        ruling="democratic",
        popularities=dict(democratic=55, fascism=15, communism=15, neutrality=15),
        leader=dict(id="GRE_pax_pericles", name="Архонт Перикл Талассидис", ideology="liberalism",
                    desc="Потомок моряков Талассии. Верит, что море помнит всё, даже то, что утонуло."),
        spirit=dict(id="PAX_spirit_GRE", name="Морская Лига островов",
                    desc="Эллада это сотня островов и одна общая гавань. Каждый эллин с детства умеет держать весло.",
                    modifier=dict(experience_gain_navy=0.1, research_speed_factor=0.03)),
    ),
    "FRA": dict(
        lore_id="gaul", bloc="pax",
        name="Галльская Конфедерация", short="Галлия", adj="галльский",
        color=(63, 138, 58), accent=(240, 220, 130),
        flag=dict(kind="tree_tricolor"),
        ruling="democratic",
        popularities=dict(democratic=55, fascism=10, communism=20, neutrality=15),
        leader=dict(id="FRA_pax_ambiorix", name="Верховный друид Амбиорикс", ideology="conservatism",
                    desc="Глава Совета друидов. Каждую осень он сам собирает омелу в священной роще у столицы."),
        spirit=dict(id="PAX_spirit_FRA", name="Священные рощи",
                    desc="Галлия до сих пор молится в лесах. Рощи дают ей урожай и спокойствие.",
                    modifier=dict(stability_factor=0.05, army_core_defence_factor=0.05)),
    ),
    "ENG": dict(
        lore_id="islands", bloc="pax",
        name="Островной Союз", short="Островной Союз", adj="островной",
        color=(58, 166, 160), accent=(250, 250, 250),
        flag=dict(kind="island_stars"),
        ruling="democratic",
        popularities=dict(democratic=65, fascism=10, communism=10, neutrality=15),
        leader=dict(id="ENG_pax_elinor", name="Адмирал-президент Элинор Вейн", ideology="liberalism",
                    desc="Республика мореходов выбирает президента из капитанов. Вейн командовала флотом, который вернулся из Тумана Безымянных."),
        spirit=dict(id="PAX_spirit_ENG", name="Острова, которые сказали «нет»",
                    desc="В 1781 году колонии отбились от метрополий. С тех пор Островной Союз никому не платит дань.",
                    modifier=dict(stability_factor=0.05, experience_gain_navy=0.05)),
    ),
    "GER": dict(
        lore_id="germany", bloc="steppe",
        name="Германский Рейх", short="Германия", adj="германский",
        color=(92, 95, 102), accent=(200, 40, 40),
        flag=dict(kind="hammer_cross"),
        ruling="fascism",
        popularities=dict(democratic=20, fascism=55, communism=15, neutrality=10),
        leader=dict(id="GER_pax_arminius", name="Рейхсканцлер Арминий Вальдгер", ideology="fascism_ideology",
                    desc="Ветеран окопов 1914 года. Обещает Рейху железо и уголь Севера и не верит в метели."),
        spirit=dict(id="PAX_spirit_GER", name="Позор 1914 года",
                    desc="Рейх проиграл Первую Великую войну. Ему мало земли, и он помнит каждую обиду.",
                    modifier=dict(war_support_factor=0.1, stability_factor=-0.05)),
    ),
    "SOV": dict(
        lore_id="north", bloc="steppe",
        name="Северное Царство", short="Северное Царство", adj="северный",
        color=(143, 179, 217), accent=(255, 255, 255),
        flag=dict(kind="snow_star"),
        ruling="neutrality",
        popularities=dict(democratic=15, fascism=10, communism=25, neutrality=50),
        leader=dict(id="SOV_pax_vseslav", name="Царь Всеслав Ледяной", ideology="despotism",
                    desc="Северное Царство основали беглецы всех народов. Царь Всеслав говорит, что зима всегда на стороне того, кто дома."),
        spirit=dict(id="PAX_spirit_SOV", name="Зима на стороне дома",
                    desc="Метель 1241 года остановила Орду у стен Ромеи. Северяне выросли в такой метели.",
                    modifier=dict(attrition=-0.05, army_core_defence_factor=0.05)),
    ),
    "ROM": dict(
        lore_id="dacia", bloc="steppe",
        name="Дакийское Царство", short="Дакия", adj="дакийский",
        color=(181, 101, 47), accent=(60, 140, 120),
        flag=dict(kind="mountain"),
        ruling="neutrality",
        popularities=dict(democratic=25, fascism=20, communism=10, neutrality=45),
        leader=dict(id="ROM_pax_decebal", name="Царь Децебал Девятый", ideology="despotism",
                    desc="Царь медных гор. Ромея брала с Дакии дань с 117 года, и Децебал этого не простил."),
        spirit=dict(id="PAX_spirit_ROM", name="Медные рудники Каэр-Брун",
                    desc="В горах Дакии лежат древние рудники Медного Союза. В них нашли чертежи паровых машин.",
                    modifier=dict(local_resources_factor=0.1, war_support_factor=0.05)),
    ),
    "TUR": dict(
        lore_id="horde", bloc="steppe",
        name="Великая Степная Орда", short="Орда", adj="ордынский",
        color=(201, 162, 39), accent=(120, 30, 30),
        flag=dict(kind="sun_horse"),
        ruling="neutrality",
        popularities=dict(democratic=15, fascism=25, communism=10, neutrality=50),
        leader=dict(id="TUR_pax_tengiz", name="Каган Тенгиз", ideology="despotism",
                    desc="Избран курултаем кланов. Его предки вышли из песчаной бури в 375 году и дошли до самой башни."),
        spirit=dict(id="PAX_spirit_TUR", name="Дети песчаной бури",
                    desc="Орда приходит быстро и уходит быстро. Её конница помнит дорогу к стенам Ромеи.",
                    modifier=dict(army_speed_factor=0.05, army_attack_factor=0.03)),
    ),
    "PER": dict(
        lore_id="scythia", bloc="steppe",
        name="Скифское Царство", short="Скифия", adj="скифский",
        color=(122, 74, 140), accent=(230, 190, 60),
        flag=dict(kind="kurgan"),
        ruling="neutrality",
        popularities=dict(democratic=15, fascism=15, communism=15, neutrality=55),
        leader=dict(id="PER_pax_idanthyrsus", name="Царь Иданфирс Второй", ideology="despotism",
                    desc="Курганный царь дальнего востока. Его казна это золото предков, а армия это конные лучники."),
        spirit=dict(id="PAX_spirit_PER", name="Курганная знать",
                    desc="Цари Скифии правят вместе с родами. Роды дают золото и всадников, но любят спорить.",
                    modifier=dict(political_power_gain=0.15, stability_factor=-0.03)),
    ),
}

# ---------------------------------------------------------------------------
# Общая часть дерева фокусов (как на сервере: Промышленность, Армия, Экономика)
# ---------------------------------------------------------------------------
# effect: готовый скрипт HOI4; {T} заменяется на тег страны.

CIV = """random_owned_controlled_state = {
	limit = { free_building_slots = { building = industrial_complex size > 0 include_locked = yes } }
	add_extra_state_shared_building_slots = 1
	add_building_construction = { type = industrial_complex level = 1 instant_build = yes }
}"""
MIL = """random_owned_controlled_state = {
	limit = { free_building_slots = { building = arms_factory size > 0 include_locked = yes } }
	add_extra_state_shared_building_slots = 1
	add_building_construction = { type = arms_factory level = 1 instant_build = yes }
}"""
DOCK = """random_owned_controlled_state = {
	limit = { is_coastal = yes free_building_slots = { building = dockyard size > 0 include_locked = yes } }
	add_extra_state_shared_building_slots = 1
	add_building_construction = { type = dockyard level = 1 instant_build = yes }
}"""


def tech(cat, focus, bonus="0.5", uses=2):
    return f"add_tech_bonus = {{ name = {focus} bonus = {bonus} uses = {uses} category = {cat} }}"


GENERIC_FOCUSES = [
    # Промышленность
    dict(key="ind1", name="Индустриализация", x=0, y=0, cost=10,
         icon="GFX_goal_generic_construct_civ_factory",
         desc="Первый шаг любой державы Века стали: заводы, железные дороги, уголь.",
         effect=CIV + "\n" + CIV),
    dict(key="ind2", name="Шахтёрские артели", x=0, y=1, cost=10, prereq=[["ind1"]],
         icon="GFX_goal_generic_construction",
         desc="Артели шахтёров копают глубже, как когда-то мастера Каэр-Тала.",
         effect="add_ideas = PAX_idea_mining_guilds"),
    dict(key="ind3", name="Военная экономика", x=0, y=2, cost=10, prereq=[["ind2"]],
         icon="GFX_goal_generic_construct_mil_factory",
         desc="Заводы переходят на снаряды и винтовки. Казна наполняется военными заказами.",
         effect=MIL + "\n" + MIL + "\nadd_ideas = PAX_idea_war_economy"),
    # Армия
    dict(key="mil1", name="Мобилизация", x=2, y=0, cost=10,
         icon="GFX_goal_generic_allies_build_infantry",
         desc="Каждый житель получает винтовку и паёк. Резервисты возвращаются в казармы.",
         effect="add_manpower = 25000\nadd_ideas = PAX_idea_mobilization"),
    dict(key="mil2", name="Укрепления", x=2, y=1, cost=10, prereq=[["mil1"]],
         icon="GFX_goal_generic_defence",
         desc="Стены вокруг стен. Ромея научила весь мир, что крепость переживёт любой набег.",
         effect="add_ideas = PAX_idea_fortifications"),
    dict(key="mil3", name="Тотальная война", x=2, y=2, cost=10, prereq=[["mil2"]], exclusive=["eco3"],
         icon="GFX_goal_generic_major_war",
         desc="Вся нация становится армией. Нельзя одновременно воевать мечом и держать соседей в вассалах.",
         effect="add_war_support = 0.1\nadd_ideas = PAX_idea_total_war\ncountry_event = { id = pax.40 }"),
    # Экономика
    dict(key="eco1", name="Торговые пути", x=4, y=0, cost=10,
         icon="GFX_goal_generic_consumer_goods",
         desc="Караваны и корабли снова ходят по старым дорогам. Торговля кормит казну.",
         effect="add_political_power = 75\nadd_ideas = PAX_idea_trade_routes"),
    dict(key="eco2", name="Дипкорпус", x=4, y=1, cost=10, prereq=[["eco1"]],
         icon="GFX_goal_generic_improve_relations",
         desc="Со времён Договора у Монолита в 251 году пакт о ненападении стоит дешевле войны.",
         effect="add_ideas = PAX_idea_diplomatic_corps"),
    dict(key="eco3", name="Гегемония", x=4, y=2, cost=10, prereq=[["eco2"]], exclusive=["mil3"],
         icon="GFX_goal_generic_political_pressure",
         desc="Держава правит не мечом, а данью. Соседи платят, а казна растёт.",
         effect="add_stability = 0.05\nadd_ideas = PAX_idea_hegemony"),
]

GENERIC_IDEAS = [
    dict(id="PAX_idea_mining_guilds", name="Шахтёрские артели",
         desc="Шахтёры копают глубже и быстрее.", modifier=dict(local_resources_factor=0.15)),
    dict(id="PAX_idea_war_economy", name="Военные заказы",
         desc="Заводы работают на войну.", modifier=dict(industrial_capacity_factory=0.05)),
    dict(id="PAX_idea_mobilization", name="Мобилизация",
         desc="Резервисты готовы встать в строй.", modifier=dict(conscription=0.01)),
    dict(id="PAX_idea_fortifications", name="Стены вокруг стен",
         desc="Своя земля защищена лучше чужой.", modifier=dict(army_core_defence_factor=0.1)),
    dict(id="PAX_idea_total_war", name="Тотальная война",
         desc="Вся нация воюет.", modifier=dict(army_attack_factor=0.1, war_support_factor=0.05)),
    dict(id="PAX_idea_trade_routes", name="Торговые пути",
         desc="Торговля кормит казну.", modifier=dict(consumer_goods_factor=-0.03, trade_opinion_factor=0.15)),
    dict(id="PAX_idea_diplomatic_corps", name="Дипкорпус",
         desc="Послы держав знают все старые договоры.", modifier=dict(political_power_gain=0.15)),
    dict(id="PAX_idea_hegemony", name="Гегемония",
         desc="Соседи платят дань и не спорят.", modifier=dict(stability_factor=0.05, political_power_factor=0.1)),
    dict(id="PAX_far_lands", name="Дальние земли",
         desc="Лор PaxVanila молчит об этой стране. Мир вращается вокруг Монолита, а не вокруг неё.",
         modifier=dict(research_speed_factor=-0.1, political_power_gain=-0.1, war_support_factor=-0.1)),
    # Монолит
    dict(id="PAX_idea_guardian_seven", name="Страж-7",
         desc="Под башней проснулся седьмой голем с медным сердцем. Его первое слово было «PAX».",
         modifier=dict(research_speed_factor=0.1, army_core_defence_factor=0.1)),
    dict(id="PAX_idea_kurultai_mind", name="Разум «Курултай»",
         desc="Степной Пакт украл чертежи Седьмого и построил свой разум.",
         modifier=dict(research_speed_factor=0.07, army_org_factor=0.05)),
]

# ---------------------------------------------------------------------------
# Наследие и вера: по одному фокусу на державу (уровень 2, как на сервере)
# ---------------------------------------------------------------------------
HERITAGE = {
    "ITA": dict(name="SPQR", desc="Сенат и народ Ромеи. Каждый враг, павший на ромейской земле, делает Республику сильнее.",
                modifier=dict(army_core_defence_factor=0.1, army_core_attack_factor=0.05)),
    "SPR": dict(name="Пушки Гая", desc="Карфагенские литейщики делают осадные орудия дешевле всех в мире.",
                modifier=dict(production_speed_arms_factory_factor=0.1), extra=tech("artillery", "{F}", "1.0", 2)),
    "GRE": dict(name="Морская Лига", desc="Флот Эллады ходит по морю, как дельфин.",
                modifier=dict(experience_gain_navy=0.15), extra=tech("naval_doctrine", "{F}")),
    "FRA": dict(name="Священные рощи", desc="Дома, в своих лесах, галлы встают после любого удара.",
                modifier=dict(army_org_factor=0.05, stability_factor=0.05)),
    "ENG": dict(name="Республика мореходов", desc="Каждый гражданин Союза моряк, и каждый порт его дом.",
                modifier=dict(experience_gain_navy=0.1, production_speed_dockyard_factor=0.1)),
    "GER": dict(name="Железо и уголь", desc="Германские королевства сидят на самых богатых рудах мира.",
                modifier=dict(industrial_capacity_factory=0.1)),
    "SOV": dict(name="Метель 1942", desc="Зимой враги на земле Царства вмерзают в снег.",
                modifier=dict(attrition=-0.1, army_core_defence_factor=0.1)),
    "ROM": dict(name="Медь Каэр-Тала", desc="Дакия раскопала рудники Медного Союза до самого дна.",
                modifier=dict(local_resources_factor=0.2)),
    "TUR": dict(name="Из песчаной бури", desc="Орда выходит из бури там, где её не ждут, и бьёт на чужой земле.",
                modifier=dict(army_speed_factor=0.05, army_attack_factor=0.05)),
    "PER": dict(name="Царские курганы", desc="Золото предков и дань вассалов идут в казну скифских царей.",
                modifier=dict(political_power_gain=0.2)),
}

FAITH = {
    "ITA": dict(name="Марс Градив", desc="Боги Капитолия. Марс стоит за Ромею, когда враг у её стен.",
                modifier=dict(army_core_attack_factor=0.05, war_support_factor=0.05)),
    "SPR": dict(name="Щедрость Танит", desc="Баал-Хаммон и Танит. Богиня любит щедрых купцов.",
                modifier=dict(consumer_goods_factor=-0.03)),
    "GRE": dict(name="Посейдон", desc="Боги Олимпа. Морской бог хранит корабли Эллады.",
                modifier=dict(navy_org_factor=0.05)),
    "FRA": dict(name="Омела", desc="Боги рощ. Друиды лечат раненых омелой и травами.",
                modifier=dict(stability_factor=0.05)),
    "ENG": dict(name="Союз Числа", desc="Школа Пифагора. Мореходы верят, что у всего есть число, даже у удачи.",
                modifier=dict(research_speed_factor=0.05)),
    "GER": dict(name="Молот Донара", desc="Вотан и Донар. В грозу германские полки идут вперёд.",
                modifier=dict(army_attack_factor=0.05)),
    "SOV": dict(name="Хранители Печати", desc="Северяне верят в Монолит больше, чем в богов. Печать держит мир.",
                modifier=dict(stability_factor=0.05, political_power_gain=0.1)),
    "ROM": dict(name="Без страха смерти", desc="Залмоксис. Даки идут в бой, потому что не боятся смерти.",
                modifier=dict(army_defence_factor=0.05)),
    "TUR": dict(name="Яса", desc="Тенгри и Умай. Под открытым небом конница Орды не знает поражений.",
                modifier=dict(army_attack_factor=0.05)),
    "PER": dict(name="Стрелы Папая", desc="Табити, Папай и Апи. Конные лучники Скифии бьют без промаха.",
                modifier=dict(army_org_factor=0.05)),
}

# ---------------------------------------------------------------------------
# Национальные ветки (по лору). Позиции x считаются от начала ветки.
# effect может ссылаться на {T} (тег) и {F} (id фокуса).
# ---------------------------------------------------------------------------
JOIN_PAX = """if = {
	limit = { ITA = { is_faction_leader = yes } is_in_faction = no }
	ITA = { add_to_faction = ROOT }
}
else = { add_political_power = 75 }"""
JOIN_STEPPE = """if = {
	limit = { SOV = { is_faction_leader = yes } is_in_faction = no }
	SOV = { add_to_faction = ROOT }
}
else = { add_political_power = 75 }"""

NATIONAL = {
    "ITA": [
        dict(key="senate", name="Сенат у башни", x=0, y=0, cost=7, icon="GFX_goal_support_democracy",
             desc="Сенат собирается у Монолита, как в год основания. Ромул слушает сенаторов.",
             effect="add_political_power = 100\nadd_stability = 0.05"),
        dict(key="tower_law", name="«У башни не стреляют»", x=0, y=1, cost=10, prereq=[["senate"]],
             icon="GFX_goal_generic_defence",
             desc="Закон 1529 года. Новые пушки бьют на пятьдесят километров, и закон надо переписать.",
             effect="add_ideas = PAX_idea_ITA_tower_law"),
        dict(key="tablets", name="Таблички Предтеч", x=2, y=1, cost=10, prereq=[["senate"]],
             icon="GFX_goal_generic_scientific_exchange",
             desc="Учёные Форума снова читают таблички Ур-Кадима и Каэр-Тала.",
             effect=tech("industry", "{F}", "0.5", 2) + "\n" + tech("electronics", "{F}", "0.5", 1)),
        dict(key="monolith_pact", name="Договор у Монолита", x=1, y=2, cost=10, prereq=[["tower_law"], ["tablets"]],
             icon="GFX_goal_generic_major_alliance",
             desc="Первый пакт о ненападении был подписан у башни в 251 году. Пора собрать союз снова и назвать его словом над входом.",
             effect="""if = {
	limit = { is_in_faction = no }
	create_faction = PAX_faction_pax
}
every_country = {
	limit = { OR = { tag = SPR tag = GRE tag = FRA tag = ENG } exists = yes is_in_faction = no }
	country_event = { id = pax.2 days = 1 }
}"""),
        dict(key="romul_legacy", name="Имя, которое не умирает", x=1, y=3, cost=10, prereq=[["monolith_pact"]],
             icon="GFX_goal_generic_national_unity",
             desc="Ромулов было двести пять. Республика переживёт и эту войну.",
             effect="add_stability = 0.1\nadd_war_support = 0.05\narmy_experience = 25"),
    ],
    "SPR": [
        dict(key="suffets", name="Совет суффетов", x=0, y=0, cost=7, icon="GFX_goal_generic_political_pressure",
             desc="Карфагеном правят купцы. Совет суффетов решает, где торговать и с кем воевать.",
             effect="add_political_power = 100"),
        dict(key="caravan", name="Золотой Караван", x=0, y=1, cost=10, prereq=[["suffets"]],
             icon="GFX_goal_generic_consumer_goods",
             desc="Самая длинная торговая дорога мира снова открыта.",
             effect=CIV + "\nadd_political_power = 50"),
        dict(key="new_fleet", name="Новый флот Карфагена", x=2, y=1, cost=10, prereq=[["suffets"]],
             icon="GFX_goal_generic_build_navy",
             desc="В 264 году до н.э. буря утопила флот Карфагена. Новый флот строят из стали.",
             effect=DOCK + "\n" + DOCK + "\n" + tech("naval_doctrine", "{F}", "0.5", 1)),
        dict(key="kart_hadasht", name="Карт-Хадашт", x=1, y=2, cost=10, prereq=[["caravan"], ["new_fleet"]],
             icon="GFX_goal_generic_construct_civ_factory",
             desc="«Новый город». Карфаген строит фабрики так же быстро, как раньше строил корабли.",
             effect=CIV + "\n" + CIV),
        dict(key="join_pax", name="Место в Союзе PAX", x=1, y=3, cost=10, prereq=[["kart_hadasht"]],
             icon="GFX_goal_generic_improve_relations",
             desc="Старый спор с Ромеей забыт. Карфаген встаёт рядом с ней у Монолита.",
             effect=JOIN_PAX),
    ],
    "GRE": [
        dict(key="thalassia", name="Наследие Талассии", x=0, y=0, cost=7, icon="GFX_goal_generic_navy_doctrines_tactics",
             desc="Сто островов Западного моря ушли под воду, но их чертежи кораблей остались у эллинов.",
             effect=tech("naval_doctrine", "{F}", "0.5", 2)),
        dict(key="academy", name="Академия Эллады", x=2, y=0, cost=10, icon="GFX_goal_generic_scientific_exchange",
             desc="Платон и Аристотель составили перечень всего. Академия продолжает их работу.",
             effect="add_ideas = PAX_idea_GRE_academy"),
        dict(key="isles", name="Острова Лиги", x=0, y=1, cost=10, prereq=[["thalassia"]],
             icon="GFX_goal_generic_construct_naval_dockyard",
             desc="Каждый остров Лиги строит свою верфь.",
             effect=DOCK + "\n" + DOCK),
        dict(key="hoplites", name="Гоплиты Олимпа", x=2, y=1, cost=10, prereq=[["academy"]],
             icon="GFX_goal_generic_small_arms",
             desc="Строй гоплитов теперь держит винтовки.",
             effect="army_experience = 20\n" + tech("infantry_weapons", "{F}", "0.5", 1)),
        dict(key="join_pax", name="Место в Союзе PAX", x=1, y=2, cost=10, prereq=[["isles"], ["hoplites"]],
             icon="GFX_goal_generic_improve_relations",
             desc="Эллада всегда стояла рядом с Ромеей. Пора сказать это вслух.",
             effect=JOIN_PAX),
    ],
    "FRA": [
        dict(key="druids", name="Совет друидов", x=0, y=0, cost=7, icon="GFX_goal_generic_national_unity",
             desc="Конфедерацией правят друиды. Их совет собирается в самой старой роще.",
             effect="add_stability = 0.05\nadd_political_power = 75"),
        dict(key="harvest", name="Осенний урожай", x=0, y=1, cost=10, prereq=[["druids"]],
             icon="GFX_goal_generic_consumer_goods",
             desc="Урожай Галлии кормит полмира.",
             effect="add_ideas = PAX_idea_FRA_harvest"),
        dict(key="forest_forts", name="Лесные крепости", x=2, y=1, cost=10, prereq=[["druids"]],
             icon="GFX_goal_generic_defence",
             desc="Каждая роща может стать крепостью. Галлы прячут пушки под дубами.",
             effect="army_experience = 20\nadd_ideas = PAX_idea_FRA_forest_forts"),
        dict(key="druidicon", name="Друидикон", x=1, y=2, cost=10, prereq=[["harvest"], ["forest_forts"]],
             icon="GFX_goal_generic_radar",
             desc="Друиды изучают редстоун так же, как травы. Из их лабораторий выйдет целая корпорация.",
             effect=tech("electronics", "{F}", "0.5", 2)),
        dict(key="join_pax", name="Место в Союзе PAX", x=1, y=3, cost=10, prereq=[["druidicon"]],
             icon="GFX_goal_generic_improve_relations",
             desc="Галлия и Ромея вместе стояли в окопах 1914 года.",
             effect=JOIN_PAX),
    ],
    "ENG": [
        dict(key="said_no", name="Мы сказали «нет»", x=0, y=0, cost=7, icon="GFX_goal_generic_national_unity",
             desc="Память о войне за независимость 1781 года объединяет все острова.",
             effect="add_stability = 0.05\nadd_war_support = 0.05"),
        dict(key="ports", name="Порты на всех берегах", x=0, y=1, cost=10, prereq=[["said_no"]],
             icon="GFX_goal_generic_construct_naval_dockyard",
             desc="Эпоха парусов оставила Союзу порты по всему миру.",
             effect=DOCK + "\n" + DOCK),
        dict(key="fog", name="Туман Безымянных", x=2, y=1, cost=10, prereq=[["said_no"]],
             icon="GFX_goal_generic_intelligence_exchange",
             desc="В 1700 году флот пропал в тумане. Союз до сих пор посылает туда разведчиков.",
             effect="navy_experience = 25\n" + tech("naval_doctrine", "{F}", "0.5", 1)),
        dict(key="sailor_fleet", name="Флот мореходов", x=1, y=2, cost=10, prereq=[["ports"], ["fog"]],
             icon="GFX_goal_generic_navy_battleship",
             desc="Республика мореходов строит новый флот.",
             effect=DOCK + "\n" + tech("naval_doctrine", "{F}", "0.5", 1)),
        dict(key="join_pax", name="Место в Союзе PAX", x=1, y=3, cost=10, prereq=[["sailor_fleet"]],
             icon="GFX_goal_generic_improve_relations",
             desc="Острова никому не платят дань, но клятву PAX дают сами.",
             effect=JOIN_PAX),
    ],
    "GER": [
        dict(key="revanche", name="Реванш за 1914", x=1, y=0, cost=7, icon="GFX_goal_generic_propaganda",
             desc="Рейх проиграл Первую Великую войну. Канцлер обещает, что второй раз так не будет.",
             effect="add_war_support = 0.1\nadd_political_power = 50"),
        dict(key="teutoburg", name="Тевтобург Индастриз", x=0, y=1, cost=10, prereq=[["revanche"]],
             icon="GFX_goal_generic_construct_mil_factory",
             desc="Старый лес наконец построил свой каменный город, и тот вышел больше всех.",
             effect=MIL + "\n" + MIL),
        dict(key="army", name="Армия Рейха", x=2, y=1, cost=10, prereq=[["revanche"]],
             icon="GFX_goal_generic_army_doctrines",
             desc="Штаб изучает ошибки окопной войны.",
             effect="army_experience = 25\n" + tech("land_doctrine", "{F}", "0.5", 1)),
        dict(key="iron_north", name="За железом на север", x=1, y=2, cost=10, prereq=[["teutoburg"], ["army"]],
             icon="GFX_goal_generic_territory_or_war",
             desc="Железо и уголь Северного Царства. Так началась Вторая Великая война.",
             effect="create_wargoal = { type = annex_everything target = SOV }"),
        dict(key="before_winter", name="Наступать до зимы", x=0, y=3, cost=10, prereq=[["iron_north"]],
             exclusive=["winter_lesson"], icon="GFX_goal_generic_army_motorized",
             desc="Канцлер верит, что армия успеет до снега. Так думали и в 1942 году.",
             effect="add_ideas = PAX_idea_GER_blitz"),
        dict(key="winter_lesson", name="Урок метели", x=2, y=3, cost=10, prereq=[["iron_north"]],
             exclusive=["before_winter"], icon="GFX_goal_generic_position_armies",
             desc="Летописцы Форума писали: «Зима всегда на стороне того, кто дома». Рейх шьёт зимние шинели.",
             effect="add_ideas = PAX_idea_GER_winter_coats"),
    ],
    "SOV": [
        dict(key="tsar", name="Царь во льдах", x=1, y=0, cost=7, icon="GFX_goal_generic_neutrality_focus",
             desc="Царство собрали беглецы всех народов. Царь держит их вместе.",
             effect="add_stability = 0.1\nadd_political_power = 50"),
        dict(key="winter_campaign", name="Обычай зимней кампании", x=0, y=1, cost=10, prereq=[["tsar"]],
             icon="GFX_goal_generic_position_armies",
             desc="Обычай родился в 1241 году, когда метель остановила Орду. Северяне воюют зимой.",
             effect="add_ideas = PAX_idea_SOV_winter_campaign"),
        dict(key="forests", name="Отступить в леса и ждать", x=2, y=1, cost=10, prereq=[["tsar"]],
             icon="GFX_goal_generic_defence",
             desc="Северяне не держат границу. Они уходят в леса и ждут, пока враг замёрзнет.",
             effect="army_experience = 20\n" + tech("land_doctrine", "{F}", "0.5", 1)),
        dict(key="north_iron", name="Железо Севера", x=1, y=2, cost=10, prereq=[["winter_campaign"], ["forests"]],
             icon="GFX_goal_generic_construct_mil_factory",
             desc="За этим железом придёт Рейх. Пусть оно сначала станет пушками.",
             effect=MIL + "\n" + MIL),
        dict(key="kurultai", name="Курултай победителей", x=1, y=3, cost=10, prereq=[["north_iron"]],
             icon="GFX_goal_generic_major_alliance",
             desc="Восточные державы сходятся в степи. Рождается Степной Пакт.",
             effect="""if = {
	limit = { is_in_faction = no }
	create_faction = PAX_faction_steppe
}
every_country = {
	limit = { OR = { tag = ROM tag = TUR tag = PER } exists = yes is_in_faction = no }
	country_event = { id = pax.3 days = 1 }
}"""),
    ],
    "ROM": [
        dict(key="old_tribute", name="Старая дань не забыта", x=1, y=0, cost=7, icon="GFX_goal_generic_propaganda",
             desc="В 117 году горы рухнули, и голодная Дакия стала первым вассалом Ромеи. Даки помнят.",
             effect="add_war_support = 0.1\nadd_political_power = 50"),
        dict(key="sarmizegetusa", name="Сармизегетуза Майнинг", x=0, y=1, cost=10, prereq=[["old_tribute"]],
             icon="GFX_goal_generic_construction",
             desc="Царские рудники становятся компанией. Медь идёт на заводы.",
             effect=CIV + "\nadd_ideas = PAX_idea_ROM_copper"),
        dict(key="steam", name="Паровые машины Каэр-Тала", x=2, y=1, cost=10, prereq=[["old_tribute"]],
             icon="GFX_goal_generic_production",
             desc="В рудниках нашли чертежи паровых машин. С них начался Век стали.",
             effect=tech("industry", "{F}", "0.5", 2)),
        dict(key="mountain_forts", name="Горные крепости", x=1, y=2, cost=10, prereq=[["sarmizegetusa"], ["steam"]],
             icon="GFX_goal_generic_defence",
             desc="Горы Дакии сами по себе крепость.",
             effect="army_experience = 20\nadd_stability = 0.05"),
        dict(key="join_steppe", name="Голос на Курултае", x=1, y=3, cost=10, prereq=[["mountain_forts"]],
             icon="GFX_goal_generic_improve_relations",
             desc="Дакия не простила Ромее старую дань и идёт к восточным державам.",
             effect=JOIN_STEPPE),
    ],
    "TUR": [
        dict(key="clans", name="Курултай кланов", x=1, y=0, cost=7, icon="GFX_goal_generic_national_unity",
             desc="Кланы Орды выбирают кагана и клянутся ему на коне.",
             effect="add_political_power = 100"),
        dict(key="cavalry", name="Конница степи", x=0, y=1, cost=10, prereq=[["clans"]],
             icon="GFX_goal_generic_cavalry",
             desc="Конница Орды прошла от песчаной бури до стен Ромеи.",
             effect="army_experience = 25\n" + tech("land_doctrine", "{F}", "0.5", 1)),
        dict(key="sand_roads", name="Дороги через пески", x=2, y=1, cost=10, prereq=[["clans"]],
             icon="GFX_goal_generic_construct_infrastructure",
             desc="Старые караванные дороги становятся железными.",
             effect=CIV + "\n" + MIL),
        dict(key="raid", name="Снова к стенам", x=0, y=2, cost=10, prereq=[["cavalry"], ["sand_roads"]],
             exclusive=["steppe_peace"], icon="GFX_goal_generic_territory_or_war",
             desc="В 375 году Орда дошла до башни. Каган хочет повторить путь предков через земли Эллады.",
             effect="create_wargoal = { type = puppet_wargoal_focus target = GRE }"),
        dict(key="steppe_peace", name="Мир степи", x=2, y=2, cost=10, prereq=[["cavalry"], ["sand_roads"]],
             exclusive=["raid"], icon="GFX_goal_generic_improve_relations",
             desc="Каган выбирает союз с Севером, а не набег.",
             effect=JOIN_STEPPE),
    ],
    "PER": [
        dict(key="kurgan_gold", name="Золото курганов", x=1, y=0, cost=7, icon="GFX_goal_generic_consumer_goods",
             desc="Цари вскрывают казну предков. Золото курганов идёт на заводы.",
             effect="add_political_power = 75\n" + CIV),
        dict(key="archers", name="Конные лучники", x=0, y=1, cost=10, prereq=[["kurgan_gold"]],
             icon="GFX_goal_generic_small_arms",
             desc="Скифский всадник стреляет на скаку. Теперь из винтовки.",
             effect="army_experience = 20\n" + tech("infantry_weapons", "{F}", "0.5", 1)),
        dict(key="animal_style", name="Звериный стиль", x=2, y=1, cost=10, prereq=[["kurgan_gold"]],
             icon="GFX_goal_generic_propaganda",
             desc="Олени и барсы на золотых бляхах снова на знамёнах. Роды спорят меньше.",
             effect="add_stability = 0.1"),
        dict(key="tribute", name="Дань степи", x=1, y=2, cost=10, prereq=[["archers"], ["animal_style"]],
             icon="GFX_goal_generic_political_pressure",
             desc="Кочевья платят дань царю, а царь строит дороги.",
             effect=CIV + "\n" + MIL),
        dict(key="join_steppe", name="Скифы на Курултае", x=1, y=3, cost=10, prereq=[["tribute"]],
             icon="GFX_goal_generic_improve_relations",
             desc="Скифия встаёт в Степной Пакт рядом с Ордой и Севером.",
             effect=JOIN_STEPPE),
    ],
}

NATIONAL_IDEAS = [
    dict(id="PAX_idea_ITA_tower_law", name="«У башни не стреляют»",
         desc="Закон 1529 года переписан для пушек Века стали.", modifier=dict(army_core_defence_factor=0.1, stability_factor=0.03)),
    dict(id="PAX_idea_GRE_academy", name="Академия Эллады",
         desc="Перечень всего продолжается.", modifier=dict(research_speed_factor=0.05)),
    dict(id="PAX_idea_FRA_harvest", name="Осенний урожай",
         desc="Урожай кормит армию и заводы.", modifier=dict(consumer_goods_factor=-0.03, stability_factor=0.03)),
    dict(id="PAX_idea_FRA_forest_forts", name="Лесные крепости",
         desc="Каждая роща может стать крепостью.", modifier=dict(army_core_defence_factor=0.1)),
    dict(id="PAX_idea_GER_blitz", name="Наступать до зимы",
         desc="Быстро и без зимних шинелей.", modifier=dict(army_speed_factor=0.1, attrition=0.05)),
    dict(id="PAX_idea_GER_winter_coats", name="Зимние шинели",
         desc="Рейх запомнил урок метели.", modifier=dict(attrition=-0.1, army_org_factor=0.03)),
    dict(id="PAX_idea_SOV_winter_campaign", name="Зимняя кампания",
         desc="Северяне воюют зимой лучше всех.", modifier=dict(attrition=-0.1, army_defence_factor=0.05)),
    dict(id="PAX_idea_ROM_copper", name="Медь Сармизегетузы",
         desc="Медь идёт на заводы.", modifier=dict(local_resources_factor=0.1)),
]

FACTIONS = {
    "PAX_faction_pax": "Союз PAX",
    "PAX_faction_steppe": "Степной Пакт",
}

import os as _os
BASE = _os.environ.get("PAX_BASE", "vanilla")  # vanilla | wa (лор поверх World Ablaze)
MOD_NAME = "PaxVanilaWA" if BASE == "wa" else "PaxVanila"
MOD_VERSION = "0.8.10"

# Картинки духов. Имена взяты из рабочего мода Arthur «Family Historical MP mod»,
# там они точно есть в игре. Ключ с * подходит для всех тегов (PAX_her_*, PAX_fai_*).
IDEA_PICTURES = {
    "PAX_idea_mining_guilds": "generic_production_bonus",
    "PAX_idea_war_economy": "generic_production_bonus",
    "PAX_idea_mobilization": "generic_infantry_bonus",
    "PAX_idea_fortifications": "generic_infantry_bonus",
    "PAX_idea_total_war": "generic_acquire_tanks",
    "PAX_idea_trade_routes": "free_trade",
    "PAX_idea_diplomatic_corps": "generic_constitutional_guarantees",
    "PAX_idea_hegemony": "italy_control",
    "PAX_far_lands": "great_depression",
    "PAX_idea_guardian_seven": "SOV_scientist_defect",
    "PAX_idea_kurultai_mind": "SOV_scientist_defect",
    "PAX_idea_ITA_tower_law": "generic_infantry_bonus",
    "PAX_idea_GRE_academy": "SOV_scientist_defect",
    "PAX_idea_FRA_harvest": "free_trade",
    "PAX_idea_FRA_forest_forts": "generic_infantry_bonus",
    "PAX_idea_GER_blitz": "generic_acquire_tanks",
    "PAX_idea_GER_winter_coats": "generic_infantry_bonus",
    "PAX_idea_SOV_winter_campaign": "generic_communist_army",
    "PAX_idea_ROM_copper": "generic_production_bonus",
    "PAX_spirit_ITA": "italy_control",
    "PAX_spirit_SPR": "free_trade",
    "PAX_spirit_GRE": "generic_navy_bonus",
    "PAX_spirit_FRA": "generic_constitutional_guarantees",
    "PAX_spirit_ENG": "eng_the_sun_never_sets",
    "PAX_spirit_GER": "generic_fascism_drift_bonus",
    "PAX_spirit_SOV": "generic_communist_army",
    "PAX_spirit_ROM": "generic_production_bonus",
    "PAX_spirit_TUR": "generic_volunteer_expedition_bonus",
    "PAX_spirit_PER": "german_advisors",
    "PAX_her_*": "generic_intel_bonus",
    "PAX_fai_*": "generic_constitutional_guarantees",
}

GUIDE_TEXT = (
    "1936 год, между Первой и Второй Великими войнами. Десять держав лора сервера PaxVanila заняли страны Европы и Азии: "
    "Ромея, Карфаген, Эллада, Галлия и Островной Союз на западе, Германия, Северное Царство, Дакия, Орда и Скифия на востоке. Остальной мир это «Дальние земли».\\n\\n"
    "Разделы гайда: экономика и меню решений, технологии MD и армия, сценарии и эпохи, Монолит и Стражи.\\n\\n"
    "Фокусы у держав из вашей сборки (CHADDFIXREBALANCE). Лорные ветки, наследие и вера вашей державы лежат в решениях, категория «Лор PaxVanila»."
)

LOADING_TIPS = [
    "«Законы всегда отстают от оружия».\\n- Летописец Форума",
    "«Зима всегда на стороне того, кто дома».\\n- Летописцы Форума, 1942",
    "«PAX».\\n- Первое слово Стража-7",
    "«Пусть все видят, что стражей больше нет. Может быть, это остановит их».\\n- Ромул Двести Шестой",
    "«История повторяется не потому, что люди глупы».\\n- Летописец Форума",
    "«У башни не стреляют».\\n- Закон 1529 года",
    "«Я помню это, потому что уже видел, как это заканчивается».\\n- Страж-7",
    "«Каждый правитель Ромеи берёт имя Ромул. Так будет всегда».\\n- Сенат, год 12",
]
