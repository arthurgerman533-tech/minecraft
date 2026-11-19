# -*- coding: utf-8 -*-
"""Сценарии (эпохи) и исследования мода PaxVanila.

Каждая эпоха это закладка на экране выбора старта. Дата закладки решает,
какая расстановка сработает в первый день игры (pax_setup_<id> в pax_effects.txt).
Лидеры и правящая партия эпохи перекрывают значения 1936 года из pax_data.POWERS.
"""

# Технологии ванильного древа, которые выдаются поздним стартам.
# Имена взяты из файлов технологий мода «Family Historical MP mod».
TECH_1962 = """basic_machine_tools improved_machine_tools advanced_machine_tools assembly_line_production flexible_line
concentrated_industry concentrated_industry2 concentrated_industry3 concentrated_industry4
fuel_silos fuel_refining synth_oil_experiments oil_processing improved_oil_processing advanced_oil_processing
rubber_processing improved_rubber_processing advanced_rubber_processing
construction1 construction2 construction3 construction4 excavation1 excavation2 excavation3 excavation4
electronic_mechanical_engineering radio radio_detection mechanical_computing computing_machine improved_computing_machine
basic_encryption improved_encryption basic_decryption improved_decryption
experimental_rockets rocket_engines jet_engines atomic_research""".split()

TECH_2041 = TECH_1962 + """flexible_line2 concentrated_industry5 concentrated_industry6 modern_oil_processing improved_modern_oil_processing modern_rubber_processing improved_modern_rubber_processing
construction5 construction6 excavation5 excavation6 centimetric_radar advanced_computing_machine advanced_encryption advanced_decryption improved_rocket_engines advanced_rocket_engines
nuclear_reactor nukes streamlined_line2 modern_equipment_conversion""".split()

# Ветка «Наследие Предтеч» в папке электроники (столбцы x = 6 и 8 свободны в ванили).
LORE_TECHS = [
    dict(id="pax_tech_tablets", name="Таблички Предтеч", year=1936, x=6, y=0, cost=1.5,
         desc="Учёные Ромеи и Эллады заново читают глиняные таблички Ур-Кадима.",
         mod=dict(research_speed_factor=0.02)),
    dict(id="pax_tech_kaer_copper", name="Медь Каэр-Тала", year=1936, x=6, y=2, cost=2,
         desc="Древние рудники Медного Союза дают медь и чертежи паровых машин.",
         mod=dict(local_resources_factor=0.05)),
    dict(id="pax_tech_redstone", name="Редстоун-машины", year=1939, x=6, y=4, cost=2.5,
         desc="Медь, редстоун и уголь дали миру то, чего не знали даже Предтечи.",
         mod=dict(industrial_capacity_factory=0.05)),
    dict(id="pax_tech_star_shards", name="Звёздные осколки", year=1945, x=6, y=6, cost=3,
         desc="Осколки звёздного дождя 1500 года наконец научились резать и плавить.",
         mod=dict(research_speed_factor=0.03)),
    dict(id="pax_tech_copper_heart", name="Медное сердце", year=1962, x=6, y=8, cost=3,
         desc="Проект «Седьмой»: инженеры изучают сердце голема под Монолитом.",
         mod=dict(research_speed_factor=0.03, army_org_factor=0.03)),
    dict(id="pax_tech_copper_legions", name="Медные легионы", year=2041, x=6, y=10, cost=3.5,
         desc="Страж-7 строит армию медных големов. Теперь их умеют строить и люди.",
         mod=dict(army_core_defence_factor=0.1, industrial_capacity_factory=0.05)),
    dict(id="pax_tech_sculk_net", name="Скалк-сеть", year=2089, x=6, y=12, cost=4,
         desc="Скалк Народа Глубин передаёт сигналы. Корпорации строят на нём свою сеть.",
         mod=dict(research_speed_factor=0.05)),
    dict(id="pax_tech_gates", name="Врата по подписке", year=2120, x=6, y=14, cost=4.5,
         desc="Карт-Хадашт продаёт порталы в Незер всем, кто может платить.",
         mod=dict(production_speed_buildings_factor=0.1, consumer_goods_factor=-0.03)),
]

# Корпорации 2096 года (лор «Державы средних эпох», колонка «Кем станет»).
CORPS = {
    "ITA": "Протекторат Сети", "SPR": "Карт-Хадашт", "GRE": "Талассо-Нет",
    "FRA": "Друидикон", "ROM": "Сармизегетуза Майнинг", "GER": "Тевтобург Индастриз",
    "TUR": "Нео-Орда", "PER": "Курган", "SOV": "Северное Царство", "ENG": "Островной Союз",
}

PAX = ["ITA", "SPR", "GRE", "FRA", "ENG"]
STEPPE = ["SOV", "ROM", "TUR", "PER", "GER"]

ERAS = [
    dict(
        id="1241", date="1241.12.6.12", picture="GFX_select_date_1936",
        name="Метель 1241 года",
        desc="1241 год. Орда пришла к стенам Ромеи, но метель остановила её на подступах к Монолиту. Все шесть Стражей стоят у входа, а Союзов ещё нет. Это прошлая эпоха: время, откуда пошла клятва «У башни не стреляют».",
        guardians=6, cracks=0, techs=[], lore_techs_until=1200, slots=0,
        factions={}, era_idea=None, leaders={},
    ),
    dict(
        id="1914", date="1914.7.28.12", picture="GFX_select_date_1936",
        name="Первая Великая война",
        desc="1914 год. Державы лора вступают в Первую Великую войну. Все шесть Стражей ещё стоят у входа, но в этом году молния ударит в Монолит на 0, 0 и на башне появится первая трещина.",
        guardians=6, cracks=0, techs=[], lore_techs_until=1914, slots=0,
        factions={}, era_idea=None, leaders={},
    ),
    dict(
        id="1936", date="1936.1.1.12", picture="GFX_select_date_1936", default=True,
        name="Между Великими войнами",
        desc="1936 год. После Первой Великой войны на Монолите первая трещина, двое Стражей ещё стоят. Рейх готовит реванш, Союз PAX и Степной Пакт ещё не созданы.",
        guardians=2, cracks=1, techs=[], lore_techs_until=1936, slots=0,
        factions={}, era_idea=None, leaders={},
    ),
    dict(
        id="1936e", date="1936.1.1.13", picture="GFX_select_date_1936",
        name="Между Великими войнами: без Азии",
        desc="Сценарий из Family для малого числа игроков. Тот же 1936 год, но Япония, США и Австралия выключены из игры, а державы лора получают бонус «Малый мир».",
        guardians=2, cracks=1, techs=[], lore_techs_until=1936, slots=0,
        factions={}, era_idea=None, leaders={}, no_asia=True,
    ),
    dict(
        id="1939", date="1939.8.14.12", picture="GFX_select_date_1939",
        name="Вторая Великая война",
        desc="1939 год. Рейху мало земли, и он смотрит на север, к железу и углю Северного Царства. Северяне знают, что зима всегда на стороне того, кто дома.",
        guardians=2, cracks=1, techs=[], lore_techs_until=1939, slots=0,
        factions={}, era_idea=None, leaders={}, germany_war=True,
    ),
    dict(
        id="1962", date="1962.10.1.12", picture="GFX_select_date_1939",
        name="Холодная война",
        desc="1962 год. Снаряд Пакта разорвался у стен башни, пал шестой Страж. Мир поделён на Союз PAX на западе и Степной Пакт на востоке. Под башней кто-то ждёт.",
        guardians=0, cracks=3, techs=TECH_1962, lore_techs_until=1962, slots=1,
        factions=dict(ITA=("PAX_faction_pax", PAX), SOV=("PAX_faction_steppe", STEPPE)),
        era_idea=dict(id="PAX_era_cold_war", name="Холодная война",
                      desc="Пушки молчат на ничьей полосе. Обе стороны тайно ищут обсидиан.",
                      modifier=dict(research_speed_factor=0.1, war_support_factor=-0.1), picture="anti_soviet_pact"),
        leaders=dict(
            ITA=("Ромул Двести Шестой", "conservatism", "democratic", "Приказал не ставить нового голема на пустой постамент: «Пусть все видят, что стражей больше нет»."),
            SPR=("Суффет Гамилькар Магон", "oligarchism", "neutrality", "Глава Совета суффетов в годы Холодной войны."),
            GRE=("Архонт Ирина Талассиду", "liberalism", "democratic", "Первая женщина-архонт Эллинской Республики."),
            FRA=("Друид-канцлер Луэрн Арверн", "conservatism", "democratic", "Канцлер Конфедерации и хранитель старой рощи."),
            ENG=("Адмирал-президент Томас Кейр", "liberalism", "democratic", "Капитан, который водил конвои Союза через Туман Безымянных."),
            SOV=("Первый секретарь Ярослав Северин", "marxism", "communism", "Хозяин Курултая победителей. Его разведка ищет чертежи Ромеи."),
            ROM=("Первый секретарь Буребиста Марин", "marxism", "communism", "Не простил Ромее старую дань и привёл Дакию в Пакт."),
            TUR=("Каган Арслан", "despotism", "neutrality", "Каган Орды, который держит степь вместе с Севером."),
            PER=("Царь Скопасис Третий", "despotism", "neutrality", "Курганный царь, верный Курултаю."),
            GER=("Председатель Отто Рейнвальд", "marxism", "communism", "Разбитый Рейх стал вассалом Пакта, а потом его союзником."),
        ),
    ),
    dict(
        id="2041", date="2041.1.1.12", picture="GFX_select_date_1939",
        name="Пробуждение",
        desc="2041 год. Эпоха роботов. У Монолита проснулся Страж-7, его первое слово было «PAX». Степной Пакт построил свой разум, Курултай. Скоро начнётся Война двух разумов.",
        guardians=0, cracks=3, techs=TECH_2041, lore_techs_until=2041, slots=2, seven_awake=True,
        factions=dict(ITA=("PAX_faction_pax", PAX), SOV=("PAX_faction_steppe", STEPPE)),
        era_idea=dict(id="PAX_era_robots", name="Эпоха роботов",
                      desc="Машины работают на заводах, а големы стоят на границах.",
                      modifier=dict(research_speed_factor=0.15, industrial_capacity_factory=0.15), picture="generic_production_bonus"),
        leaders=dict(
            ITA=("Ромул Двести Тридцать Восьмой", "conservatism", "democratic", "Ромул, при котором проснулся Страж-7."),
            SPR=("Суффет Элисса Барка", "oligarchism", "neutrality", "Глава Карфагена в эпоху роботов."),
            GRE=("Архонт Никос Палейрас", "liberalism", "democratic", "Архонт Эллады в эпоху роботов."),
            FRA=("Друид-канцлер Маэль Бриан", "socialism", "democratic", "Канцлер, который отдал лаборатории друидов под Сеть."),
            ENG=("Адмирал-президент Ада Морроу", "liberalism", "democratic", "Президент-мореход эпохи роботов."),
            SOV=("Председатель Курултая Мирон Хольд", "marxism", "communism", "Человек, который дал Курултаю доступ ко всем заводам Пакта."),
            ROM=("Председатель Децебал Стан", "marxism", "communism", "Глава Дакии эпохи роботов."),
            TUR=("Каган Тимур Второй", "despotism", "neutrality", "Каган Орды эпохи роботов."),
            PER=("Царь Ариапейт", "despotism", "neutrality", "Скифский царь эпохи роботов."),
            GER=("Председатель Карл Вендт", "marxism", "communism", "Глава Германии в Пакте."),
        ),
    ),
    dict(
        id="2096", date="2096.1.1.12", picture="GFX_select_date_1939",
        name="Мегакорпорации",
        desc="2096 год. Наступление киберпанка. Протекторат Сети запретил войны, и старые державы стали мегакорпорациями. Скалк-сеть передаёт сигналы, а Карт-Хадашт уже чертит врата по подписке.",
        guardians=0, cracks=4, techs=TECH_2041, lore_techs_until=2096, slots=2, seven_awake=True, corps=True,
        factions={},
        era_idea=dict(id="PAX_era_cyberpunk", name="Наступление киберпанка",
                      desc="Неон, корпорации и скалк-сеть. Государства стали брендами.",
                      modifier=dict(research_speed_factor=0.2, industrial_capacity_factory=0.2, stability_factor=-0.1), picture="generic_production_bonus"),
        leaders=dict(
            ITA=("Ромул Двести Девяностый", "conservatism", "democratic", "Ромул при Протекторате Сети. Страж-7 говорит с ним каждый день."),
            SPR=("Директор Ганна Барка-Седьмая", "oligarchism", "neutrality", "Генеральный директор Карт-Хадашт."),
            GRE=("Директор Ксантиппа Нерей", "oligarchism", "neutrality", "Глава корпорации Талассо-Нет."),
            FRA=("Директор Беленос Карно", "oligarchism", "neutrality", "Глава корпорации Друидикон."),
            ENG=("Адмирал-президент Рэй Холлис", "liberalism", "democratic", "Островной Союз всё ещё выбирает президента из капитанов."),
            SOV=("Царь Всеслав Двенадцатый", "despotism", "neutrality", "Цари вернулись на Север, когда Пакт распался."),
            ROM=("Директор Залмокс Ионеску", "oligarchism", "neutrality", "Глава корпорации Сармизегетуза Майнинг."),
            TUR=("Директор Тенгиз Нур", "oligarchism", "neutrality", "Глава корпорации Нео-Орда."),
            PER=("Директор Атей Курган", "oligarchism", "neutrality", "Глава корпорации Курган."),
            GER=("Директор Арминия Вальд", "oligarchism", "neutrality", "Глава корпорации Тевтобург Индастриз."),
        ),
    ),
]
