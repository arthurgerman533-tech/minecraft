import json,re
r=json.load(open('/tmp/rest.json'))
D={
"12 months ago":None,
}
EX={
"Economic Race":"Экономическая гонка",
"The five largest economies, since [?global.won_hs_y0|0]":"Пять крупнейших экономик с [?global.won_hs_y0|0] года",
"The five largest factions, since [?global.won_hs_y0|0]":"Пять крупнейших фракций с [?global.won_hs_y0|0] года",
"Rankings":"Рейтинги","§gUpdated every month.§!":"§gОбновляется ежемесячно.§!",
"Back to the World Economic League.":"Вернуться в Мировую экономическую лигу.",
"See how the top five economies and factions have moved against each other.":"Посмотрите, как пять крупнейших экономик и фракций менялись местами.",
"§YCountries§!":"§YСтраны§!","Countries":"Страны","§YFactions§!":"§YФракции§!","Factions":"Фракции",
"§gGDP, billions a year§!":"§gВВП, млрд в год§!",
"§gOne point every [?global.won_hs_step|0] month(s). The chart always covers the whole game.§!":"§gОдна точка каждые [?global.won_hs_step|0] мес. График всегда охватывает всю игру.§!",
"Standings now":"Текущее положение","Change since this line began.":"Изменение с начала этой линии.",
"Economic Sphere":"Экономическая сфера",
"Not part of any economic sphere":"Не входит ни в одну экономическую сферу",
"The [?won_sp_hc.GetAdjective] Sphere":"Сфера: [?won_sp_hc.GetAdjective]",
"No economic sphere":"Нет экономической сферы",
"Your faction or empire as an economic bloc: influence, directive, Economic Minister and members.":"Ваша фракция или империя как экономический блок: влияние, директива, министр экономики и члены.",
"§YEconomic Sphere§!\\nInfluence: §Y[?won_sp_my_inf|0] / 100§!\\nClick to open.":"§YЭкономическая сфера§!\\nВлияние: §Y[?won_sp_my_inf|0] / 100§!\\nНажмите, чтобы открыть.",
"Sphere influence":"Влияние сферы",
"No. [?won_sp_my_rank|0] of [?global.won_sp_count|0] spheres":"№ [?won_sp_my_rank|0] из [?global.won_sp_count|0] сфер",
"Led by [?won_sp_hc.GetFlag] [?won_sp_hc.GetName]. The more influence, the stronger every member's bonuses.":"Возглавляет [?won_sp_hc.GetFlag] [?won_sp_hc.GetName]. Чем больше влияние, тем сильнее бонусы каждого члена.",
"Create or join a faction, or take a puppet, to belong to an economic sphere.":"Создайте фракцию, вступите в неё или заведите марионетку, чтобы войти в экономическую сферу.",
"Where influence comes from":"Откуда берётся влияние",
"Influence is recalculated every month, up to 100.":"Влияние пересчитывается каждый месяц, максимум 100.",
"Share of world economy: [?won_sp_share|1]%  §G+[?won_sp_pt_share|0]§!":"Доля в мировой экономике: [?won_sp_share|1]%  §G+[?won_sp_pt_share|0]§!",
"Economic ties between members: [?won_sp_ties|1]  §G+[?won_sp_pt_ties|0]§!":"Экономические связи между членами: [?won_sp_ties|1]  §G+[?won_sp_pt_ties|0]§!",
"Members: [?won_sp_n|0]  §G+[?won_sp_pt_mem|0]§!":"Члены: [?won_sp_n|0]  §G+[?won_sp_pt_mem|0]§!",
"Directive: [GetWonSpDir]  §G+[?won_sp_pt_dir|0]§!":"Директива: [GetWonSpDir]  §G+[?won_sp_pt_dir|0]§!",
"Economic Minister: [GetWonSpMin]  §G+[?won_sp_pt_min|0]§!":"Министр экономики: [GetWonSpMin]  §G+[?won_sp_pt_min|0]§!",
"Every member gets":"Каждый член получает",
"Applied to every member of the sphere through the National Economy spirit, the GDP and inflation.":"Применяется к каждому члену сферы через дух национальной экономики, ВВП и инфляцию.",
"Productivity [?won_sp_bp|+1]%, inflation target [?won_sp_bi|-1]":"Производительность [?won_sp_bp|+1]%, цель по инфляции [?won_sp_bi|-1]",
"Arms output [?won_sp_bo|+1]%, construction [?won_sp_bb|+1]%":"Выпуск вооружений [?won_sp_bo|+1]%, строительство [?won_sp_bb|+1]%",
"Investment climate [?won_sp_bc|+0], trade [?won_sp_bt|+0]%, resource exports [?won_sp_br|+0]%":"Инвестиционный климат [?won_sp_bc|+0], торговля [?won_sp_bt|+0]%, экспорт ресурсов [?won_sp_br|+0]%",
"Sphere GDP §Y[?won_sp_gdp|1] bn§!, [?won_sp_fact|0] factories.":"ВВП сферы §Y[?won_sp_gdp|1] млрд§!, заводов: [?won_sp_fact|0].",
"§gSign trade agreements, construction pacts and investments with members to raise influence.§!":"§gЗаключайте торговые соглашения, строительные пакты и инвестиции с членами, чтобы повысить влияние.§!",
"Sphere directive":"Директива сферы",
"Now: §Y[GetWonSpDir]§!\\n§g50 political power, then 90 days before the next change.§!":"Сейчас: §Y[GetWonSpDir]§!\\n§g50 очков политической власти, затем 90 дней до следующей смены.§!",
"Economic Minister":"Министр экономики",
"Now: §Y[GetWonSpMin]§!\\n§g100 political power, then 180 days before the next change.§!":"Сейчас: §Y[GetWonSpMin]§!\\n§g100 очков политической власти, затем 180 дней до следующей смены.§!",
"§GWe lead this sphere.§!":"§GМы возглавляем эту сферу.§!",
"§gOnly the sphere leader decides.§!":"§gРешает только лидер сферы.§!",
"Balanced":"Сбалансированная","Cooperation":"Сотрудничество","Rearmament":"Перевооружение","None":"Нет",
"Industrialist":"Индустриалист","Financier":"Финансист","Planner":"Плановик",
"§YEconomic Cooperation§!\\nUp to §G+8%§! productivity and §G-3§! inflation for every member, §G+10§! influence. Arms output §R-3%§!.":"§YЭкономическое сотрудничество§!\\nДо §G+8%§! производительности и §G-3§! инфляции для каждого члена, §G+10§! влияния. Выпуск вооружений §R-3%§!.",
"§YBalanced§!\\nUp to §G+4%§! productivity and §G-1.5§! inflation for every member, §G+5§! influence.":"§YСбалансированная§!\\nДо §G+4%§! производительности и §G-1,5§! инфляции для каждого члена, §G+5§! влияния.",
"§YJoint Rearmament§!\\nUp to §G+6%§! arms output for every member. Productivity §R-2%§!, inflation target §R+0.5§!.":"§YСовместное перевооружение§!\\nДо §G+6%§! выпуска вооружений для каждого члена. Производительность §R-2%§!, цель по инфляции §R+0,5§!.",
"§YIndustrialist§!\\nConstruction §G+4%§!, up to §G+10%§! with influence, for every member. §G+5§! influence.":"§YИндустриалист§!\\nСтроительство §G+4%§!, до §G+10%§! с влиянием, для каждого члена. §G+5§! влияния.",
"§YFinancier§!\\nInvestment climate §G+5§! and inflation target §G-1§! for every member. §G+5§! influence.":"§YФинансист§!\\nИнвестиционный климат §G+5§! и цель по инфляции §G-1§! для каждого члена. §G+5§! влияния.",
"§YPlanner§!\\nTrade agreements §G+10%§! and resource export earnings §G+25%§! for every member. §G+5§! influence.":"§YПлановик§!\\nТорговые соглашения §G+10%§! и доход от экспорта ресурсов §G+25%§! для каждого члена. §G+5§! влияния.",
"Members":"Члены",
"§g... and [?won_sp_more|0] more§!":"§g... и ещё [?won_sp_more|0]§!",
"Most influential spheres":"Самые влиятельные сферы",
"A Rising Economic Sphere":"Растущая экономическая сфера",
"Our partners now trade, build and invest with each other on a scale the world has noticed. Our economic sphere has reached an influence of 50, and smaller nations are starting to look to us before they sign with anyone else.":"Наши партнёры торгуют, строят и инвестируют друг в друга в масштабах, заметных всему миру. Влияние нашей экономической сферы достигло 50, и малые страны начинают смотреть на нас, прежде чем подписывать что-либо с другими.",
"Prosperity binds stronger than treaties.":"Процветание связывает крепче договоров.",
"Economic Hegemony":"Экономическая гегемония",
"Our sphere's influence has passed 80. Prices, credit and industry across our bloc now move to the rhythm of our ministries, and rival capitals speak of our sphere the way they once spoke of empires.":"Влияние нашей сферы превысило 80. Цены, кредит и промышленность всего нашего блока теперь движутся в ритме наших министерств, а столицы соперников говорят о нашей сфере так, как когда-то говорили об империях.",
"The world runs on our economy now.":"Мир теперь живёт за счёт нашей экономики.",
"§YCooperation§!":"§YСотрудничество§!",
"§YBalanced§!":"§YСбалансированная§!","§YRearmament§!":"§YПеревооружение§!",
"§YIndustrialist§!":"§YИндустриалист§!","§YFinancier§!":"§YФинансист§!","§YPlanner§!":"§YПлановик§!",
}
def tr(t):
    if t in EX: return EX[t]
    m=re.match(r'(\d+) months ago: (.*) of world GDP$',t)
    if m: return f"{m[1]} мес. назад: {m[2]} мирового ВВП"
    m=re.match(r'Last month: (.*) of world GDP$',t)
    if m: return f"В прошлом месяце: {m[1]} мирового ВВП"
    if t==" bn": return " млрд"
    t2=t.replace(" bn§!"," млрд§!")
    t2=re.sub(r'^(§.\d\.§! \S+) The (\S+) Sphere$',lambda m:m[0],t2)
    t2=re.sub(r'\] The \[(\?global\.won_sp_c\d\.GetAdjective)\] Sphere',r'] Сфера: [\1]',t2)
    return t2
