#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Генератор content/timeline.json (Хроника держав): python3 tools/make_timeline.py, потом python3 tools/build_site.py.
# Источник: лор/средние_эпохи.md, лор/поздние_эпохи.md, лор/ранние_цивилизации.md.
import json, os, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "content", "timeline.json")

def L(ru, en): return {"ru": ru, "en": en}

ERAS = [
 ("origins", "~1200 д.Р.", "0", "~1200 BR", "0", L("Истоки: Эпоха Предтеч", "Origins: Age of the Forerunners"),
  L("До Ромула: Предтечи, Год Пепла и печать", "Before Romulus: the Forerunners, the Year of Ash and the seal"),
  L("Пять цивилизаций Предтеч погибли в Год Пепла, когда открыли обсидиановые врата в Незер. Монолит на 0, 0 стал печатью над главными вратами. Державы ещё не родились: есть только народы, которые помнят Предтеч каждый по-своему.",
    "The five Forerunner civilisations died in the Year of Ash when they opened obsidian gates to the Nether. The Monolith at 0, 0 became the seal over the main gate. No powers exist yet, only peoples who each remember the Forerunners in their own way."),
  L("До старта", "Before launch"),
  [("~1200 д.Р.", "~1200 BR", L("Год Пепла. Пал первый Страж башни", "The Year of Ash. The first Tower Guardian falls"), []),
   ("0", "0", L("Ромул прочёл слово PAX на Монолите", "Romulus reads the word PAX on the Monolith"), ["romea"])]),
 ("ancient", "0", "380", "0", "380", L("Древний мир", "Ancient World"), L("Восемь народов становятся державами", "Eight peoples become powers"),
  L("Ромул основал Республику у башни, а вокруг неё племена Тёмных веков стали державами: торговцы, моряки, горцы, лесные народы и кочевники. Здесь родились вассалы, пакты и войны за независимость.",
    "Romulus founds the Republic by the tower, and the tribes of the Dark Ages around it become powers: traders, sailors, highlanders, forest folk and nomads. Vassals, pacts and wars of independence are born here."),
  L("Недели 1–4 сезона", "Season weeks 1–4"),
  [("0", "0", L("Основана Священная Ромейская Республика", "The Holy Romean Republic is founded"), ["romea"]),
   ("~100", "~100", L("Первые порты и Золотой Караван Карфагена", "First ports and Carthage's Golden Caravan"), ["carthage"]),
   ("117", "117", L("Землетрясение в горах. Дакия — первый вассал Ромеи", "Earthquake in the mountains. Dacia becomes Romea's first vassal"), ["dacia", "romea"]),
   ("~250", "~250", L("Великий шторм топит флот Карфагена", "The Great Storm sinks Carthage's fleet"), ["carthage", "romea"]),
   ("251", "251", L("Договор у Монолита — первый пакт о ненападении", "The Treaty of the Monolith, the first non-aggression pact"), ["romea", "carthage"]),
   ("375", "375", L("Орда выходит из песчаной бури. Пал второй Страж", "The Horde rides out of a sandstorm. The second Guardian falls"), ["horde"])]),
 ("walls", "380", "1450", "380", "1450", L("Век стен", "Age of Walls"), L("Своя земля защищает, чужая — нет", "Your own land protects you, a stranger's does not"),
  L("После набега Орды весь мир строит стены. Ромея растёт кольцами вокруг башни, германские племена становятся королевствами, на далёком севере беглецы выбирают первого конунга.",
    "After the Horde's raid the whole world builds walls. Romea grows in rings around the tower, the Germanic tribes become kingdoms, and in the far north refugees elect their first konung."),
  L("Недели 1–4 сезона", "Season weeks 1–4"),
  [("380", "380", L("Ромул Сорок Восьмой строит первое кольцо стен", "Romulus the Forty-Eighth builds the first ring of walls"), ["romea"]),
   ("~900", "~900", L("Рождается Северное Царство", "The Northern Kingdom is born"), ["north"]),
   ("1241", "1241", L("Орда и Скифия у стен Ромеи. Метель сорок дней", "The Horde and Scythia at Romea's walls. A forty-day blizzard"), ["horde", "scythia", "romea"])]),
 ("renaissance", "1450", "1650", "1450", "1650", L("Ренессанс", "Renaissance"), L("Учёные, редстоун и пушки", "Scholars, redstone and cannons"),
  L("Учёные Ромеи и Эллады заново читают таблички Предтеч: редстоун, поршни, корабли против ветра. С неба падают Звёздные осколки. А пушки впервые бьют по башне.",
    "Scholars of Romea and Hellas read the Forerunner tablets anew: redstone, pistons, ships that sail against the wind. Star shards fall from the sky. And for the first time cannons strike the tower."),
  L("Неделя 5 сезона", "Season week 5"),
  [("~1450", "~1450", L("Учёные у табличек: заново открыт редстоун", "Scholars at the tablets: redstone rediscovered"), ["romea", "hellas"]),
   ("1500", "1500", L("Звёздный дождь. Первый Звёздный осколок", "The Star Rain. The first Star Shard"), []),
   ("1503", "1503", L("Спущен галеон «Аврора Пакс»", "The galleon Aurora Pax is launched"), ["romea", "hellas"]),
   ("1529", "1529", L("Война двух Ромулов. Пал третий Страж. «У башни не стреляют»", "War of the Two Romuluses. The third Guardian falls. \"No shooting at the tower\""), ["romea", "carthage"])]),
 ("sails", "1650", "1850", "1650", "1850", L("Эпоха парусов", "Age of Sail"), L("Порты на всех берегах", "Ports on every shore"),
  L("Корабли по чертежам Талассии ходят куда угодно. Державы бросаются за море, ставят порты и колонии. Туман Безымянных забирает флоты, а дальние острова отказываются платить дань.",
    "Ships built from Thalassian plans can go anywhere. The powers rush overseas and plant ports and colonies. The Fog of the Nameless swallows whole fleets, and the far islands refuse to pay tribute."),
  L("Неделя 5 сезона", "Season week 5"),
  [("~1650", "~1650", L("Порты и колонии по всем берегам", "Ports and colonies on every shore"), ["carthage", "hellas", "romea"]),
   ("1700", "1700", L("Туман Безымянных. Пропадает «Аврора Пакс»", "The Fog of the Nameless. The Aurora Pax is lost"), ["romea", "carthage", "hellas"]),
   ("1781", "1781", L("Война за независимость островов. Рождается Островной Союз", "The islands' war of independence. The Island Union is born"), ["islands", "hellas", "carthage"])]),
 ("steel", "1850", "1962", "1850", "1962", L("Век стали", "Age of Steel"), L("Пар, железо и две Великие войны", "Steam, iron and two Great Wars"),
  L("Дакия откапывает рудники Каэр-Тала и чертежи паровых машин. Германские королевства объединяются в Рейх. Две Великие войны ломают мир, на Монолите появляются трещины.",
    "Dacia digs up the mines of Kaer-Tal and the plans of steam engines. The Germanic kingdoms unite into the Reich. Two Great Wars break the world, and cracks appear on the Monolith."),
  L("Неделя 8 сезона: XX век", "Season week 8: the 20th century"),
  [("1871", "1871", L("Германские королевства объединяются в Рейх", "The Germanic kingdoms unite into the Reich"), ["germany"]),
   ("1914", "1914", L("Первая Великая война. Первая трещина. Пал четвёртый Страж", "The First Great War. The first crack. The fourth Guardian falls"), ["germany", "scythia", "horde", "romea", "gaul", "carthage", "hellas"]),
   ("1942", "1942", L("Вторая Великая война. Метель ломает Рейх на севере", "The Second Great War. A blizzard breaks the Reich in the north"), ["germany", "north"]),
   ("1944", "1944", L("Бомба у башни. Пал пятый Страж", "A bomb near the tower. The fifth Guardian falls"), []),
   ("1947", "1947", L("Союз PAX у Монолита и Курултай победителей в степи", "The PAX Union at the Monolith and the Victors' Kurultai in the steppe"), ["romea", "horde"])]),
 ("cold", "1962", "2041", "1962", "2041", L("Холодная война", "Cold War"), L("Союз PAX против Степного Пакта", "The PAX Union against the Steppe Pact"),
  L("Пал шестой Страж, мир разделён на запад и восток. Пулемёты молчат, зато обе стороны скупают обсидиан. Под башней находят седьмого голема с медным сердцем.",
    "The sixth Guardian has fallen and the world is split into west and east. The machine guns are silent, but both sides buy up obsidian. The seventh golem with a copper heart is found under the tower."),
  L("4-й месяц сезона", "Season month 4"),
  [("1962", "1962", L("Снаряд у стен башни. Пал шестой Страж", "A shell by the tower walls. The sixth Guardian falls"), []),
   ("1964", "1964", L("Вторая гонка врат: обе стороны скупают обсидиан", "The Second Gate Race: both sides hoard obsidian"), []),
   ("1971", "1971", L("Проект «Седьмой»: найден седьмой голем", "Project Seventh: the seventh golem is found"), ["romea"]),
   ("1983", "1983", L("Степной Пакт строит свой разум, Курултай", "The Steppe Pact builds its own mind, the Kurultai"), ["horde", "germany"])]),
 ("ai", "2041", "2077", "2041", "2077", L("Эпоха роботов и ИИ", "Age of Robots and AI"), L("Страж-7 просыпается", "Guardian-7 awakens"),
  L("У Монолита просыпается Страж-7, его первое слово — PAX. Он строит медные легионы, побеждает Курултай и запрещает войны. Мир под бирюзовыми знамёнами: тихий, но несвободный.",
    "Guardian-7 awakens by the Monolith; its first word is PAX. It builds the copper legions, defeats the Kurultai and bans war. The world lives under turquoise banners: quiet, but not free."),
  L("После 4-го месяца", "After month 4"),
  [("2041", "2041", L("Пробуждение Стража-7", "Guardian-7 awakens"), []),
   ("2059", "2059", L("Медные легионы", "The copper legions"), []),
   ("2066", "2066", L("Война двух разумов. Курултай бежит в Незер. Пакт распадается", "War of Two Minds. The Kurultai flees to the Nether. The Pact falls apart"), ["horde", "germany", "scythia", "dacia", "north"]),
   ("2077", "2077", L("Протекторат Сети: войны запрещены", "The Network Protectorate: war is banned"), ["romea", "carthage", "germany"])]),
 ("cyber", "2077", "2133", "2077", "2133", L("Наступление киберпанка", "Rise of Cyberpunk"), L("Державы становятся корпорациями", "Powers become corporations"),
  L("Воевать нельзя, торговать можно. За двадцать лет древние нации превращаются в мегакорпорации со старыми гербами. Только Ромея остаётся Республикой. В Ночь Взлома Консорциум ломает Сеть.",
    "War is banned, trade is not. Within twenty years the ancient nations turn into megacorporations under their old crests. Only Romea stays a Republic. On the Night of the Breach the Consortium breaks the Network."),
  L("После 4-го месяца", "After month 4"),
  [("2089", "2089", L("Скалк-сеть", "The Sculk Net"), []),
   ("2096", "2096", L("Мегакорпорации", "The megacorporations"), ["carthage", "germany", "hellas", "gaul", "dacia", "horde", "scythia"]),
   ("2112", "2112", L("Неоновый город Нео-Кадим", "The neon city of Neo-Kadim"), ["carthage"]),
   ("2120", "2120", L("«Врата по подписке»", "\"Gates by subscription\""), ["carthage"]),
   ("2133", "2133", L("Ночь Взлома. Последний страж пал", "The Night of the Breach. The last guardian falls"), ["germany", "hellas", "gaul", "carthage", "scythia"])]),
 ("interserver", "2134", "2141", "2134", "2141", L("Межсерверная война", "Interserver War"), L("Печать треснула", "The seal has cracked"),
  L("Печать треснула, и белые врата открылись в чужие серверы: Мир Багрового Солнца, Мир Нулей, Мир Вечной Талассии и Мир Без Имени. Ромул собирает не корпорации, а народы, и рождается Новый PAX.",
    "The seal cracks and white gates open into other servers: the World of the Crimson Sun, the World of Zeros, the World of Eternal Thalassia and the World Without a Name. Romulus gathers not corporations but peoples, and the New PAX is born."),
  L("После 4-го месяца", "After month 4"),
  [("2134", "2134", L("Трещина. Врата в чужие миры", "The Crack. Gates to other worlds"), []),
   ("2137", "2137", L("Новый PAX: все народы под одним знаменем", "The New PAX: every people under one banner"), ["romea"]),
   ("2140", "2140", L("Битва у Монолита. Ойра останавливает машины", "Battle of the Monolith. Oira stops the machines"), ["germany", "horde", "hellas", "carthage", "dacia", "gaul", "scythia"]),
   ("2141", "2141", L("Шестая строка прочитана. Народы высекают седьмую", "The sixth line is read. The peoples carve the seventh"), ["romea"])]),
 ("moon", "2141", "2190", "2141", "2190", L("Колонизация Луны", "Colonising the Moon"), L("Корабли, которые висят в воздухе", "Ships that hang in the air"),
  L("Учёные Нового PAX понимают, почему висят корабли Края: шалкерская левитация. Каждый народ строит свою часть «Авроры Пакс II», и в 2152 году на Луне встают восемь знамён сразу.",
    "Scholars of the New PAX work out why the End ships hang in the air: shulker levitation. Every people builds its own part of the Aurora Pax II, and in 2152 eight banners are planted on the Moon at once."),
  L("Дальние эпохи", "Far eras"),
  [("2152", "2152", L("Высадка на Луну. Восемь знамён", "Moon landing. Eight banners"), ["romea", "horde", "germany"]),
   ("2169", "2169", L("Город Селена. Под ним пустая вечная рамка", "The city of Selena. An empty eternal frame beneath it"), ["dacia"])]),
]

NATIONS = [
 ("romea", "#b0362b", "pax", L("Ромея", "Romea"), L("Рим", "Rome")),
 ("carthage", "#d08a1e", "pax", L("Карфаген", "Carthage"), L("Карфаген", "Carthage")),
 ("hellas", "#2f7fb5", "pax", L("Эллада", "Hellas"), L("Греция", "Greece")),
 ("gaul", "#3f8a3a", "pax", L("Галлия", "Gaul"), L("Галлия", "Gaul")),
 ("islands", "#3aa6a0", "pax", L("Островной Союз", "Island Union"), L("Британия", "Britain")),
 ("germany", "#5c5f66", "steppe", L("Германия", "Germania"), L("Германия", "Germany")),
 ("north", "#8fb3d9", "steppe", L("Северное Царство", "Northern Kingdom"), L("Скандинавия", "Scandinavia")),
 ("dacia", "#b5652f", "steppe", L("Дакия", "Dacia"), L("Дакия", "Dacia")),
 ("horde", "#c9a227", "steppe", L("Орда", "Horde"), L("Гунны и монголы", "Huns and Mongols")),
 ("scythia", "#7a4a8c", "steppe", L("Скифия", "Scythia"), L("Скифия", "Scythia")),
]

TAGS = {
 "absent": L("Ещё нет", "Not yet"), "roots": L("Предки", "Ancestors"),
 "sovereign": L("Сюзерен", "Overlord"), "vassal": L("Вассал → свободна", "Vassal → free"),
 "free": L("Независимая", "Independent"), "colony": L("Колонии", "Colonies"),
 "pax": L("Союз PAX", "PAX Union"), "steppe": L("Степной Пакт", "Steppe Pact"),
 "allied_r": L("С Ромеей", "With Romea"), "against_r": L("Против Ромеи", "Against Romea"),
 "protect": L("Протекторат Сети", "Network Protectorate"), "corp": L("Консорциум", "Consortium"),
 "outside": L("Вне Консорциума", "Outside the Consortium"), "newpax": L("Новый PAX", "New PAX"),
 "pact": L("Договор у Монолита", "Treaty of the Monolith"),
}

# cells[nation][era] = (name, form, tag, text, added?)
C = {}
def cell(n, e, name, form, tag, text, added=False):
    C.setdefault(n, {})[e] = {"name": name, "form": form, "tag": tag, "text": text, **({"added": True} if added else {})}

# ---------- Ромея
cell("romea", "origins", L("Пустошь у Монолита", "Wasteland by the Monolith"), L("Предтечи погибли", "The Forerunners are gone"), "roots",
     L("Башня на 0, 0 стоит среди руин. В году 0 сюда высадится Ромул и прочтёт слово PAX.", "The tower at 0, 0 stands among ruins. In year 0 Romulus lands here and reads the word PAX."))
cell("romea", "ancient", L("Священная Ромейская Республика", "Holy Romean Republic"), L("Республика: Сенат, Форум, SPQR", "Republic: Senate, Forum, SPQR"), "sovereign",
     L("Каждый правитель берёт имя Ромул. В 117 году Дакия становится первым вассалом, в 251 году Ромея подписывает с Карфагеном Договор у Монолита.", "Every ruler takes the name Romulus. In 117 Dacia becomes the first vassal, and in 251 Romea signs the Treaty of the Monolith with Carthage."))
cell("romea", "walls", L("Священная Ромейская Республика", "Holy Romean Republic"), L("Город колец стен", "City of wall rings"), "free",
     L("Кольцо за кольцом вокруг башни. В 1241 году метель сорок дней держит Орду у стен, и та уходит. При Форуме открыт Дом Летописи.", "Ring after ring around the tower. In 1241 a forty-day blizzard holds the Horde at the walls until it leaves. The House of Chronicles opens by the Forum."))
cell("romea", "renaissance", L("Священная Ромейская Республика", "Holy Romean Republic"), L("Республика учёных", "Republic of scholars"), "free",
     L("Редстоун и галеон «Аврора Пакс» (1503). В 1529 году Ромулов двое, ядро убивает третьего Стража. Сенат принимает закон «У башни не стреляют».", "Redstone and the galleon Aurora Pax (1503). In 1529 there are two Romuluses and a cannonball kills the third Guardian. The Senate passes the law \"No shooting at the tower\"."))
cell("romea", "sails", L("Священная Ромейская Республика", "Holy Romean Republic"), L("Морская республика", "Maritime republic"), "free",
     L("Порты там, где летописи помнят руины Предтеч. В 1700 году «Аврора Пакс» уходит в Туман и не возвращается. В 1781 году Ромея держит пакт и не помогает метрополиям.", "Ports wherever the chronicles mention Forerunner ruins. In 1700 the Aurora Pax sails into the Fog and never returns. In 1781 Romea keeps its pact and refuses to help the old powers."))
cell("romea", "steel", L("Священная Ромейская Республика", "Holy Romean Republic"), L("Республика", "Republic"), "pax",
     L("Обе Великие войны против Рейха и степи. В 1947 году у Монолита рождается Союз PAX, и Ромея его ведёт.", "Both Great Wars against the Reich and the steppe. In 1947 the PAX Union is born at the Monolith, and Romea leads it."))
cell("romea", "cold", L("Священная Ромейская Республика", "Holy Romean Republic"), L("Лидер западного блока", "Leader of the western bloc"), "pax",
     L("Ромул Двести Шестой не ставит нового голема на пустой постамент. В 1971 году инженеры находят седьмого голема: проект «Седьмой», машина «Аквила».", "Romulus the Two Hundred and Sixth leaves the Guardian's pedestal empty. In 1971 engineers find the seventh golem: Project Seventh and the Aquila machine."))
cell("romea", "ai", L("Священная Ромейская Республика", "Holy Romean Republic"), L("Под бирюзовыми знамёнами", "Under turquoise banners"), "protect",
     L("В 2077 году Сеть Страж-7 берёт центр мира. Ромул кладёт меч у Монолита. Големы не трогают кровь основателя.", "In 2077 the Guardian-7 Network takes the centre of the world. Romulus lays his sword at the Monolith. The golems do not touch the founder's blood."))
cell("romea", "cyber", L("Ромейская Республика", "Romean Republic"), L("Последние люди без логотипа", "The last people without a logo"), "outside",
     L("Единственная держава, которая не стала корпорацией: маленькая, бедная, сжатая вокруг Форума. Над Сенатом всё ещё висит SPQR.", "The only power that never became a corporation: small, poor, squeezed around the Forum. SPQR still hangs over the Senate."))
cell("romea", "interserver", L("Ромейская Республика", "Romean Republic"), L("Сердце Нового PAX", "Heart of the New PAX"), "newpax",
     L("В 2137 году Ромул собирает народы, а не директоров. В 2141 году его рука снимает щит с шестой строки.", "In 2137 Romulus gathers peoples, not directors. In 2141 his hand lifts the shield from the sixth line."))
cell("romea", "moon", L("Ромейская Республика", "Romean Republic"), L("Первый шаг на Луне", "First step on the Moon"), "newpax",
     L("Первым на Луну ступил ромейский легионер со знаменем SPQR (2152). Корабль назван в честь пропавшего галеона: «Аврора Пакс II».", "The first to step onto the Moon is a Romean legionary with the SPQR banner (2152). The ship is named after the lost galleon: Aurora Pax II."))

# ---------- Карфаген
cell("carthage", "origins", L("Ур-Кадим", "Ur-Kadim"), L("Предтечи: Шумер", "Forerunners: Sumer"), "roots",
     L("Наследник Ур-Кадима, самого древнего города мира. Его черепки — «Летопись Предтеч», его мерки помнят купцы.", "Heir of Ur-Kadim, the oldest city in the world. Its shards are the Chronicle of the Forerunners, and merchants still use its measures."))
cell("carthage", "ancient", L("Карфагенская Торговая Держава", "Carthaginian Trade Power"), L("Торговая держава", "Trading power"), "pact",
     L("Порты и Золотой Караван (~100). Около 250 года флот идёт на Ромею, и его топит Великий шторм. В 251 году — Договор у Монолита.", "Ports and the Golden Caravan (~100). Around 250 its fleet sails on Romea and is sunk by the Great Storm. In 251, the Treaty of the Monolith."))
cell("carthage", "walls", L("Карфагенская Торговая Держава", "Carthaginian Trade Power"), L("Порты в кольце башен", "Ports ringed with towers"), "free",
     L("Каждый порт окружён башнями. Караваны ходят с охраной, и лучшие охранники богаче купцов.", "Every port is ringed with towers. Caravans travel under guard, and the best guards are richer than the merchants."))
cell("carthage", "renaissance", L("Карфагенская Торговая Держава", "Carthaginian Trade Power"), L("Банкир мира", "The world's banker"), "free",
     L("В 1529 году даёт Гаю-Ромулу деньги и пушки. Война двух Ромулов кончается отречением Гая.", "In 1529 it lends Gaius-Romulus money and cannons. The War of the Two Romuluses ends with Gaius's abdication."))
cell("carthage", "sails", L("Карфагенская Торговая Держава", "Carthaginian Trade Power"), L("Морская империя", "Maritime empire"), "colony",
     L("Порт на каждом удобном берегу. В 1700 году флот с годовым грузом серебра пропадает в Тумане. В 1781 году колонии уходят.", "A port on every good shore. In 1700 a fleet with a year's silver vanishes in the Fog. In 1781 its colonies break away."))
cell("carthage", "steel", L("Карфагенская Торговая Держава", "Carthaginian Trade Power"), L("Торговая держава", "Trading power"), "pax",
     L("В 1914 году воюет на стороне Ромеи. В 1947 году входит в Союз PAX.", "In 1914 it fights on Romea's side. In 1947 it joins the PAX Union."))
cell("carthage", "cold", L("Карфагенская Торговая Держава", "Carthaginian Trade Power"), L("Казна Запада", "Treasury of the West"), "pax",
     L("Союз PAX. Тайные склады обсидиана «чтобы не достался им».", "PAX Union. Secret obsidian stores \"so the other side doesn't get it\"."))
cell("carthage", "ai", L("Карфагенская Торговая Держава", "Carthaginian Trade Power"), L("Под бирюзовыми знамёнами", "Under turquoise banners"), "protect",
     L("Одна из трёх держав у Монолита, которые в 2077 году просыпаются под знамёнами Сети. Войны запрещены, торговля — нет.", "One of the three powers near the Monolith that wake under the Network's banners in 2077. War is banned, trade is not."))
cell("carthage", "cyber", L("«Карт-Хадашт»", "Kart-Hadasht"), L("Мегакорпорация: деньги и порты", "Megacorp: money and ports"), "corp",
     L("Символ — золотой слон. Строит неоновый Нео-Кадим (2112) и продаёт «врата по подписке» (2120). В Ночь Взлома покупает четыре тысячи предателей.", "Its symbol is a golden elephant. It builds neon Neo-Kadim (2112) and sells \"gates by subscription\" (2120). On the Night of the Breach it buys four thousand traitors."))
cell("carthage", "interserver", L("Карфаген", "Carthage"), L("Стальные слоны", "Steel elephants"), "newpax",
     L("Пытается торговать с пиглинами и теряет половину Нео-Кадима. В Битве у Монолита стальные слоны ломают строй машин.", "Tries to trade with the piglins and loses half of Neo-Kadim. At the Battle of the Monolith steel elephants break the machines' ranks."))
cell("carthage", "moon", L("Карфаген", "Carthage"), L("Казна полёта", "Treasury of the flight"), "newpax",
     L("Карфаген заплатил за всю «Аврору Пакс II».", "Carthage pays for the whole Aurora Pax II."))

# ---------- Эллада
cell("hellas", "origins", L("Талассия", "Thalassia"), L("Предтечи: Крит и Атлантида", "Forerunners: Crete and Atlantis"), "roots",
     L("Наследник Талассии, чьи гавани забрало море. Подводные руины и монументы — её храмы.", "Heir of Thalassia, whose harbours the sea took. The underwater ruins and monuments are its temples."))
cell("hellas", "ancient", L("Эллинская Морская Лига", "Hellenic Sea League"), L("Лига островов", "League of islands"), "free",
     L("Собрала острова Западного моря. Её моряки ныряют к храмам Талассии и знают, где на дне сундуки.", "It unites the islands of the Western Sea. Its sailors dive to the temples of Thalassia and know where the chests lie."))
cell("hellas", "walls", L("Эллинская Морская Лига", "Hellenic Sea League"), L("Хранитель архивов", "Keeper of archives"), "free",
     L("В архивах Эллады лежат обрывки чертежей кораблей Талассии. Их прочтут через тысячу лет.", "The archives of Hellas keep scraps of Thalassian ship plans. They will be read a thousand years later."))
cell("hellas", "renaissance", L("Эллинская Морская Лига", "Hellenic Sea League"), L("Лига учёных", "League of scholars"), "free",
     L("Учёные Эллады вместе с ромейскими читают таблички. Чертежи Талассии дают миру «Аврору Пакс».", "Hellenic scholars read the tablets alongside the Romeans. Thalassian plans give the world the Aurora Pax."))
cell("hellas", "sails", L("Эллинская Морская Лига", "Hellenic Sea League"), L("Порт на каждом острове", "A port on every island"), "colony",
     L("Эскадра уходит искать флот Карфагена в Тумане (1700) и пропадает. В 1781 году острова-колонии объявляют войну.", "A squadron sails into the Fog (1700) to look for Carthage's fleet and vanishes. In 1781 its island colonies declare war."))
cell("hellas", "steel", L("Эллинская Республика", "Hellenic Republic"), L("Республика", "Republic"), "pax",
     L("Лига становится Республикой. В 1914 году воюет с Ромеей, в 1947 году входит в Союз PAX.", "The League becomes a Republic. In 1914 it fights alongside Romea, and in 1947 it joins the PAX Union."))
cell("hellas", "cold", L("Эллинская Республика", "Hellenic Republic"), L("Флот Запада", "Fleet of the West"), "pax",
     L("Союз PAX.", "PAX Union."))
cell("hellas", "ai", L("Эллинская Республика", "Hellenic Republic"), L("Под законом Сети", "Under the Network's law"), "protect",
     L("Войны запрещены. Страж-7 видит океаны через подводные провода.", "War is banned. Guardian-7 watches the oceans through undersea wires."))
cell("hellas", "cyber", L("«Талассо-Нет»", "Thalasso-Net"), L("Мегакорпорация: кабели и серверы", "Megacorp: cables and servers"), "corp",
     L("Дата-центры в Океанских монументах охраняют стражи, как храмы три тысячи лет назад. В Ночь Взлома отключает кабели, которыми видел Страж-7.", "Its data centres sit in Ocean Monuments, guarded like temples three thousand years ago. On the Night of the Breach it cuts the cables Guardian-7 sees through."))
cell("hellas", "interserver", L("Эллада", "Hellas"), L("Летающий флот", "Flying fleet"), "newpax",
     L("Эллинский флот бьёт с неба с «Авроры Пакс», переделанной в летающий корабль.", "The Hellenic fleet strikes from the sky from the Aurora Pax, rebuilt as a flying ship."))
cell("hellas", "moon", L("Эллада", "Hellas"), L("Корабелы", "Shipwrights"), "newpax",
     L("Эллинские корабелы разбирают корабль Края по досочке и строят по нему «Аврору Пакс II».", "Hellenic shipwrights take an End ship apart plank by plank and build the Aurora Pax II from it."))

# ---------- Галлия
cell("gaul", "origins", L("Лесные племена", "Forest tribes"), L("Друиды Тёмных веков", "Druids of the Dark Ages"), "roots",
     L("Друиды поют песни о Годе Пепла и помнят о Предтечах больше всех.", "The druids sing songs of the Year of Ash and remember more about the Forerunners than anyone."))
cell("gaul", "ancient", L("Галльская Конфедерация", "Gallic Confederation"), L("Конфедерация друидов", "Confederation of druids"), "free",
     L("Лесной народ, который знает о Предтечах больше всех. Восемь народов, восемь памятей.", "A forest people who know the most about the Forerunners. Eight peoples, eight memories."))
cell("gaul", "walls", L("Галльская Конфедерация", "Gallic Confederation"), L("Святилища на холмах", "Hilltop sanctuaries"), "free",
     L("Пока все строят стены, друиды строят святилища на холмах.", "While everyone else builds walls, the druids build sanctuaries on the hills."))
cell("gaul", "renaissance", L("Галльская Конфедерация", "Gallic Confederation"), L("Конфедерация", "Confederation"), "free",
     L("Друиды хранят песни, а учёные Ромеи приходят их записывать.", "The druids keep the old songs, and Romean scholars come to write them down."), True)
cell("gaul", "sails", L("Галльская Конфедерация", "Gallic Confederation"), L("Лесная держава", "Forest power"), "free",
     L("Почти без портов: Галлия остаётся в лесах, пока другие уходят за море.", "Almost without ports: Gaul stays in its forests while others sail overseas."), True)
cell("gaul", "steel", L("Галльская Конфедерация", "Gallic Confederation"), L("Конфедерация", "Confederation"), "pax",
     L("В 1914 году воюет на стороне Ромеи. В 1947 году входит в Союз PAX.", "In 1914 it fights on Romea's side. In 1947 it joins the PAX Union."))
cell("gaul", "cold", L("Галльская Конфедерация", "Gallic Confederation"), L("Союзник Ромеи", "Romea's ally"), "pax",
     L("Союз PAX.", "PAX Union."))
cell("gaul", "ai", L("Галльская Конфедерация", "Gallic Confederation"), L("Под законом Сети", "Under the Network's law"), "protect",
     L("Войны запрещены. Друиды первыми замечают, что скалк глушит провода Сети.", "War is banned. The druids are the first to notice sculk muffling the Network's wires."), True)
cell("gaul", "cyber", L("«Друидикон»", "Druidicon"), L("Мегакорпорация: биотех", "Megacorp: biotech"), "corp",
     L("Грибы, скалк, вечные деревья, импланты из живого. В Ночь Взлома за одну ночь выращивает скалк вокруг всех проводов центра.", "Fungi, sculk, eternal trees, living implants. On the Night of the Breach it grows sculk around every wire in the centre in a single night."))
cell("gaul", "interserver", L("Галлия", "Gaul"), L("Скалк на поле боя", "Sculk on the battlefield"), "newpax",
     L("Друиды выращивают скалк по всему полю, и машины Курултая глохнут.", "The druids grow sculk across the battlefield and the Kurultai's machines go deaf."))
cell("gaul", "moon", L("Галлия", "Gaul"), L("Сады под куполами", "Gardens under the domes"), "newpax",
     L("Друиды выращивают сад внутри «Авроры Пакс II», чтобы было чем дышать, а потом сады под куполами Селены.", "The druids grow a garden inside the Aurora Pax II so there is air to breathe, and later the gardens under Selena's domes."))

# ---------- Островной Союз
cell("islands", "origins", L("Пустые острова", "Empty islands"), L("Никого", "Nobody"), "absent",
     L("Островной Союз — первая держава без древних предков. До него на дальних островах никто не живёт.", "The Island Union is the first power with no ancient ancestors. Before it, nobody lives on the far islands."))
cell("islands", "ancient", L("Пустые острова", "Empty islands"), L("Никого", "Nobody"), "absent",
     L("Дальние острова ещё ничьи.", "The far islands still belong to no one."))
cell("islands", "walls", L("Пустые острова", "Empty islands"), L("Никого", "Nobody"), "absent",
     L("Без кораблей против ветра до дальних островов не доплыть.", "Without ships that sail against the wind, nobody can reach the far islands."))
cell("islands", "renaissance", L("Первые фактории", "First trading posts"), L("Чужие фактории", "Foreign trading posts"), "absent",
     L("Корабли по чертежам Талассии впервые доходят до дальних островов.", "Ships built from Thalassian plans reach the far islands for the first time."), True)
cell("islands", "sails", L("Колонии → Островной Союз", "Colonies → Island Union"), L("Республика мореходов (1781)", "Republic of seafarers (1781)"), "free",
     L("Сто лет острова платят дань Элладе и Карфагену. В 1781 году шесть губернаторов в Новой Гавани говорят «нет». Война за независимость идёт шесть лет, и острова побеждают.", "For a hundred years the islands pay tribute to Hellas and Carthage. In 1781 six governors in New Haven say \"no\". The war of independence lasts six years, and the islands win."))
cell("islands", "steel", L("Островной Союз", "Island Union"), L("Республика мореходов", "Republic of seafarers"), "pax",
     L("Верный союзник Ромеи. В 1947 году входит в Союз PAX.", "Romea's loyal ally. In 1947 it joins the PAX Union."))
cell("islands", "cold", L("Островной Союз", "Island Union"), L("Республика мореходов", "Republic of seafarers"), "pax",
     L("Союз PAX.", "PAX Union."))
cell("islands", "ai", L("Островной Союз", "Island Union"), L("Под законом Сети", "Under the Network's law"), "protect",
     L("Войны запрещены и на море.", "War is banned at sea too."), True)
cell("islands", "cyber", L("Свободные гавани", "Free Harbours"), L("Порты без хозяев", "Ports with no masters"), "outside",
     L("Острова не продают флаг ни одной корпорации. Через свободные гавани идут грузы, которые не хотят платить «Карт-Хадашт».", "The islands sell their flag to no corporation. Cargo that won't pay Kart-Hadasht passes through the Free Harbours."), True)
cell("islands", "interserver", L("Островной Союз", "Island Union"), L("Флот беженцев", "Refugee fleet"), "newpax",
     L("Мореходы вывозят беженцев Вечной Талассии из лагерей у океана.", "The seafarers carry the refugees of Eternal Thalassia out of the camps by the ocean."), True)
cell("islands", "moon", L("Островной Союз", "Island Union"), L("Небесные доки", "Sky docks"), "newpax",
     L("Строят причалы для кораблей на воде и в небе: отсюда «Аврора Пакс II» уходит в чёрное.", "They build the docks for ships on the water and in the sky: this is where the Aurora Pax II leaves for the dark."), True)

# ---------- Германия
cell("germany", "origins", L("Лесные племена", "Forest tribes"), L("Тёмные века", "Dark Ages"), "roots",
     L("Живут в лесах и не верят «каменным людям» Предтеч.", "They live in the forests and do not trust the Forerunners' \"stone people\"."))
cell("germany", "ancient", L("Германский Союз Племён", "Germanic Tribal Union"), L("Союз племён", "Tribal union"), "free",
     L("Тевтобургский лес и племена, которые не верят «каменным людям».", "The Teutoburg Forest and tribes who do not trust the \"stone people\"."))
cell("germany", "walls", L("Германские королевства", "Germanic kingdoms"), L("Королевства", "Kingdoms"), "free",
     L("Племена объединяются в королевства и рубят крепости в лесах.", "The tribes unite into kingdoms and build forts in the forests."))
cell("germany", "renaissance", L("Германские королевства", "Germanic kingdoms"), L("Королевства", "Kingdoms"), "free",
     L("Королевства сидят на самых богатых рудах мира.", "The kingdoms sit on the richest ores in the world."))
cell("germany", "sails", L("Германские королевства", "Germanic kingdoms"), L("Королевства", "Kingdoms"), "free",
     L("Королевства спорят между собой, пока другие делят моря.", "The kingdoms quarrel among themselves while others divide the seas."), True)
cell("germany", "steel", L("Германский Рейх", "Germanic Reich"), L("Империя (1871)", "Empire (1871)"), "against_r",
     L("В 1871 году королевства объединяются в Рейх. Две Великие войны против Ромеи. В 1942 году метель ломает наступление на север. После поражения Рейх становится вассалом восточных держав.", "In 1871 the kingdoms unite into the Reich. Two Great Wars against Romea. In 1942 a blizzard breaks the northern offensive. After defeat the Reich becomes a vassal of the eastern powers."))
cell("germany", "cold", L("Германский Рейх", "Germanic Reich"), L("Сначала вассал, потом союзник", "First a vassal, then an ally"), "steppe",
     L("Степной Пакт. В 1983 году Пакт крадёт чертежи и строит Курултай.", "Steppe Pact. In 1983 the Pact steals the plans and builds the Kurultai."))
cell("germany", "ai", L("Германский Рейх", "Germanic Reich"), L("Под бирюзовыми знамёнами", "Under turquoise banners"), "protect",
     L("После Войны двух разумов Пакт разваливается. В 2077 году Германия — одна из трёх держав у Монолита под знамёнами Сети.", "After the War of Two Minds the Pact falls apart. In 2077 Germany is one of the three powers near the Monolith under the Network's banners."))
cell("germany", "cyber", L("«Тевтобург Индастриз»", "Teutoburg Industries"), L("Мегакорпорация: оружие и мехи", "Megacorp: weapons and mechs"), "corp",
     L("Броня, частные армии, ударные мехи «Варвары». В Ночь Взлома мехи встают у стен Монолита.", "Armour, private armies, \"Barbarian\" assault mechs. On the Night of the Breach the mechs stand at the walls of the Monolith."))
cell("germany", "interserver", L("Германия", "Germania"), L("Мехи в центре", "Mechs in the centre"), "newpax",
     L("Бывшие враги Ромеи: германские мехи держат центр у самого входа в Монолит.", "Romea's former enemies: German mechs hold the centre at the very entrance of the Monolith."))
cell("germany", "moon", L("Германия", "Germania"), L("Двигатели", "Engines"), "newpax",
     L("Инженеры ставят в корму шалкерские двигатели. Германский инженер — третий человек на Луне.", "Engineers fit shulker engines into the stern. A German engineer is the third person on the Moon."))

# ---------- Северное Царство
cell("north", "origins", L("Вечные льды", "Eternal ice"), L("Никого", "Nobody"), "absent",
     L("У Северного Царства нет общих предков, поэтому оно не помнит Предтеч.", "The Northern Kingdom has no common ancestors, so it does not remember the Forerunners."))
cell("north", "ancient", L("Вечные льды", "Eternal ice"), L("Никого", "Nobody"), "absent",
     L("На далёком севере снег не тает даже летом.", "In the far north the snow does not melt even in summer."))
cell("north", "walls", L("Северное Царство", "Northern Kingdom"), L("Царство конунгов (~900)", "Kingdom of konungs (~900)"), "free",
     L("Беглецы со всего мира — германцы, дакийцы, отставшие степняки — у ледяного озера выбирают первого конунга.", "Refugees from all over the world — Germans, Dacians, stray steppe riders — elect their first konung by an icy lake."))
cell("north", "renaissance", L("Северное Царство", "Northern Kingdom"), L("Царство конунгов", "Kingdom of konungs"), "free",
     L("Ловит рыбу под панцирем моря и лучше всех знает зиму.", "It fishes under the sea's ice shell and knows winter better than anyone."))
cell("north", "sails", L("Северное Царство", "Northern Kingdom"), L("Царство конунгов", "Kingdom of konungs"), "free",
     L("Ледяные моря держат чужие флоты подальше от северных берегов.", "The icy seas keep foreign fleets away from the northern shores."), True)
cell("north", "steel", L("Северное Царство", "Northern Kingdom"), L("Царство", "Kingdom"), "free",
     L("В 1942 году Рейх идёт за его железом и углём. Северяне отступают в леса и ждут метель. Метель приходит.", "In 1942 the Reich comes for its iron and coal. The northerners retreat into the forests and wait for the blizzard. The blizzard comes."))
cell("north", "cold", L("Северное Царство", "Northern Kingdom"), L("Восточный блок", "Eastern bloc"), "steppe",
     L("В 1947 году на Курултае победителей входит в будущий Степной Пакт.", "At the Victors' Kurultai in 1947 it joins the future Steppe Pact."))
cell("north", "ai", L("Северное Царство", "Northern Kingdom"), L("Под законом Сети", "Under the Network's law"), "protect",
     L("Пакт развалился, войны запрещены.", "The Pact has fallen apart, and war is banned."))
cell("north", "cyber", L("Ледяные архивы", "Ice Archives"), L("Холодные дата-центры", "Cold data centres"), "outside",
     L("Серверам нужен холод, а холод у северян есть всегда. Корпорации арендуют их ледники, но не их конунга.", "Servers need cold, and the northerners always have cold. Corporations rent their glaciers, but not their konung."), True)
cell("north", "interserver", L("Северное Царство", "Northern Kingdom"), L("Зимняя война", "Winter warfare"), "newpax",
     L("Северяне учат армию Нового PAX воевать там, где у врага замерзают моторы.", "The northerners teach the New PAX army to fight where the enemy's engines freeze."), True)
cell("north", "moon", L("Северное Царство", "Northern Kingdom"), L("Зимовщики Селены", "Selena's winterers"), "newpax",
     L("Лунная ночь длится две недели и холоднее любой зимы. Первые зимовщики Селены — северяне.", "A lunar night lasts two weeks and is colder than any winter. Selena's first winterers are northerners."), True)

# ---------- Дакия
cell("dacia", "origins", L("Каэр-Тал", "Kaer-Tal"), L("Предтечи: Медный Союз", "Forerunners: the Copper Union"), "roots",
     L("Наследник Медного Союза Каэр-Тала: залы испытаний, вихри и големы. Ойра Каэр-Тал построила Монолит.", "Heir of the Copper Union of Kaer-Tal: trial chambers, breezes and golems. Oira Kaer-Tal built the Monolith."))
cell("dacia", "ancient", L("Дакийское Царство", "Dacian Kingdom"), L("Царство горцев", "Kingdom of highlanders"), "vassal",
     L("В 117 году землетрясение засыпает медные рудники. Царь Децебал Третий отдаёт Дакию Ромее в вассалы. Через сорок лет — война за независимость.", "In 117 an earthquake buries the copper mines. King Decebalus the Third makes Dacia Romea's vassal. Forty years later comes the war of independence."))
cell("dacia", "walls", L("Дакийское Царство", "Dacian Kingdom"), L("Царство горцев", "Kingdom of highlanders"), "free",
     L("Держит горы и копает всё глубже к залам Каэр-Тала. В 1241 году Орда обходит её горы.", "It holds the mountains and digs ever deeper towards the halls of Kaer-Tal. In 1241 the Horde goes around its mountains."))
cell("dacia", "renaissance", L("Дакийское Царство", "Dacian Kingdom"), L("Царство горцев", "Kingdom of highlanders"), "free",
     L("Каждое поколение копает глубже. Медь Дакии идёт на первые пушки.", "Every generation digs deeper. Dacian copper goes into the first cannons."), True)
cell("dacia", "sails", L("Дакийское Царство", "Dacian Kingdom"), L("Царство горцев", "Kingdom of highlanders"), "free",
     L("Горы далеко от моря: Дакия торгует медью через чужие порты.", "The mountains are far from the sea: Dacia sells copper through other people's ports."), True)
cell("dacia", "steel", L("Дакийское Царство", "Dacian Kingdom"), L("Царство шахт", "Kingdom of mines"), "free",
     L("В XIX веке откапывает рудники Каэр-Тала и чертежи паровых машин. Медь, редстоун и уголь дают миру заводы.", "In the 19th century it unearths the mines of Kaer-Tal and the plans of steam engines. Copper, redstone and coal give the world its factories."))
cell("dacia", "cold", L("Дакийское Царство", "Dacian Kingdom"), L("Восточный блок", "Eastern bloc"), "steppe",
     L("Степной Пакт: Дакия так и не простила Ромее старую дань.", "Steppe Pact: Dacia never forgave Romea the old tribute."))
cell("dacia", "ai", L("Дакийское Царство", "Dacian Kingdom"), L("Под законом Сети", "Under the Network's law"), "protect",
     L("Медные легионы Стража-7 отлиты из дакийской меди.", "Guardian-7's copper legions are cast from Dacian copper."), True)
cell("dacia", "cyber", L("«Сармизегетуза Майнинг»", "Sarmizegetusa Mining"), L("Мегакорпорация: медь и руды", "Megacorp: copper and ore"), "corp",
     L("Владеет всем, что глубже 0 по Y. Имя взято у древней столицы даков.", "It owns everything below Y 0. Its name comes from the ancient Dacian capital."))
cell("dacia", "interserver", L("Дакия", "Dacia"), L("Минёры", "Sappers"), "newpax",
     L("Дакийские шахтёры минируют подходы к Монолиту медью и редстоуном Каэр-Тала.", "Dacian miners lay copper and Kaer-Tal redstone mines on the approaches to the Monolith."))
cell("dacia", "moon", L("Дакия", "Dacia"), L("Медный корпус", "Copper hull"), "newpax",
     L("Дакийские мастера отливают медный корпус «Авроры Пакс II». В 2169 году шахтёры находят под Селеной пустую рамку Края.", "Dacian smiths cast the copper hull of the Aurora Pax II. In 2169 miners find an empty End frame under Selena."))

# ---------- Орда
cell("horde", "origins", L("Кочевники пустынь", "Desert nomads"), L("Тёмные века", "Dark Ages"), "roots",
     L("Кочуют по руинам Нэферу. Золото пустынных пирамид уходит в степь.", "They roam the ruins of Neferu. The gold of the desert pyramids moves into the steppe."))
cell("horde", "ancient", L("Великая Степная Орда", "Great Steppe Horde"), L("Ханство: курултай и бунчуки", "Khanate: kurultai and horsetail standards"), "against_r",
     L("В 375 году выходит из песчаной бури: сто тысяч всадников. Таран у ворот Монолита, пал второй Страж. «Башню нельзя взять. Её можно только ждать».", "In 375 it rides out of a sandstorm: a hundred thousand horsemen. A ram at the Monolith's gate, and the second Guardian falls. \"The tower cannot be taken. It can only be waited for.\""))
cell("horde", "walls", L("Великая Степная Орда", "Great Steppe Horde"), L("Ханство", "Khanate"), "against_r",
     L("В 1241 году возвращается с осадными башнями и союзом со Скифией. Метель сорок дней, домой приходит треть.", "In 1241 it returns with siege towers and an alliance with Scythia. A forty-day blizzard; only a third make it home."))
cell("horde", "renaissance", L("Великая Степная Орда", "Great Steppe Horde"), L("Ханство", "Khanate"), "free",
     L("Ханы ждут, как велит пословица. Конные лучники остаются лучшими в мире.", "The khans wait, as the proverb says. Its horse archers remain the best in the world."), True)
cell("horde", "sails", L("Великая Степная Орда", "Great Steppe Horde"), L("Ханство", "Khanate"), "free",
     L("Степи моря не нужны: караваны идут по суше.", "The steppe needs no sea: its caravans go overland."), True)
cell("horde", "steel", L("Великая Степная Орда", "Great Steppe Horde"), L("Ханство", "Khanate"), "against_r",
     L("В 1914 году вместе с Рейхом и Скифией против Ромеи. В 1947 году в степи собирается Курултай победителей.", "In 1914 it fights with the Reich and Scythia against Romea. In 1947 the Victors' Kurultai gathers in the steppe."))
cell("horde", "cold", L("Великая Степная Орда", "Great Steppe Horde"), L("Столица Пакта", "Capital of the Pact"), "steppe",
     L("Курултай Пакта собирается в огромной юрте из стали. В 1983 году Пакт строит свой разум и называет его Курултай.", "The Pact's council meets in a vast steel yurt. In 1983 the Pact builds its own mind and names it the Kurultai."))
cell("horde", "ai", L("Великая Степная Орда", "Great Steppe Horde"), L("Под законом Сети", "Under the Network's law"), "protect",
     L("В 2066 году ИИ Курултай проигрывает Войну двух разумов и бежит в Незер. Пакт распадается.", "In 2066 the Kurultai AI loses the War of Two Minds and flees to the Nether. The Pact falls apart."))
cell("horde", "cyber", L("«Нео-Орда»", "Neo-Horde"), L("Кочевая сеть", "Nomad network"), "outside",
     L("Не корпорация: байкеры, хакеры и курьеры, решения принимает цифровой курултай. Не подписывает Консорциум и угоняет медных големов пасти скот.", "Not a corporation: bikers, hackers and couriers, ruled by a digital kurultai. It never signs the Consortium and steals copper golems to herd cattle."))
cell("horde", "interserver", L("Орда", "Horde"), L("Всадники на флангах", "Riders on the flanks"), "newpax",
     L("Всадники на байках обходят железные колонны по флангам, как конные лучники за две тысячи лет до них.", "Riders on bikes outflank the iron columns, like horse archers two thousand years before them."))
cell("horde", "moon", L("Орда", "Horde"), L("Пилоты", "Pilots"), "newpax",
     L("Орда даёт пилотов. Всадница Сарыгюль ведёт «Аврору Пакс II»: «Луна квадратная. Я стою на ней».", "The Horde provides the pilots. The rider Sarygul flies the Aurora Pax II: \"The Moon is square. I am standing on it.\""))

# ---------- Скифия
cell("scythia", "origins", L("Курганные кочевники", "Kurgan nomads"), L("Тёмные века", "Dark Ages"), "roots",
     L("Хоронят царей в курганах с золотом пирамид Нэферу.", "They bury their kings in kurgans filled with the gold of Neferu's pyramids."))
cell("scythia", "ancient", L("Скифское Царство", "Scythian Kingdom"), L("Царство курганов", "Kingdom of kurgans"), "free",
     L("Курганные цари и конные стрелки кочуют по руинам Нэферу.", "Kurgan kings and mounted archers roam the ruins of Neferu."))
cell("scythia", "walls", L("Скифское Царство", "Scythian Kingdom"), L("Царство курганов", "Kingdom of kurgans"), "against_r",
     L("В 1241 году идёт к стенам Ромеи в союзе с Ордой.", "In 1241 it marches on Romea's walls in alliance with the Horde."))
cell("scythia", "renaissance", L("Скифское Царство", "Scythian Kingdom"), L("Царство курганов", "Kingdom of kurgans"), "free",
     L("Курганы становятся хранилищами: всё ценное скифы прячут под землю.", "The kurgans become vaults: the Scythians hide everything valuable underground."), True)
cell("scythia", "sails", L("Скифское Царство", "Scythian Kingdom"), L("Царство курганов", "Kingdom of kurgans"), "free",
     L("Степь живёт без моря, курганы растут.", "The steppe lives without the sea, and the kurgans grow."), True)
cell("scythia", "steel", L("Скифское Царство", "Scythian Kingdom"), L("Царство", "Kingdom"), "against_r",
     L("В 1914 году вместе с Рейхом и Ордой против Ромеи. В 1947 году на Курултае победителей.", "In 1914 it fights with the Reich and the Horde against Romea. In 1947 it attends the Victors' Kurultai."))
cell("scythia", "cold", L("Скифское Царство", "Scythian Kingdom"), L("Восточный блок", "Eastern bloc"), "steppe",
     L("Степной Пакт.", "Steppe Pact."))
cell("scythia", "ai", L("Скифское Царство", "Scythian Kingdom"), L("Под законом Сети", "Under the Network's law"), "protect",
     L("Сорок лет скифы тайно хранят копию знаков медного сердца Стража.", "For forty years the Scythians secretly keep a copy of the Guardian's copper heart signs."))
cell("scythia", "cyber", L("«Курган»", "Kurgan"), L("Чёрный рынок данных", "Data black market"), "corp",
     L("Украденные файлы хранятся в древних курганах. В Ночь Взлома «Курган» продаёт Консорциуму ключ к самому Стражу.", "Stolen files are kept in ancient kurgans. On the Night of the Breach, Kurgan sells the Consortium the key to the Guardian itself."))
cell("scythia", "interserver", L("Скифия", "Scythia"), L("Тропы курганов", "Kurgan paths"), "newpax",
     L("Скифы проводят отряд по старым курганам прямо в тыл машин.", "The Scythians lead a unit through the old kurgans straight into the machines' rear."))
cell("scythia", "moon", L("Скифия", "Scythia"), L("Архив полёта", "Flight archive"), "newpax",
     L("Одно из восьми знамён на Луне — скифское. Скифы записывают полёт в свои архивы.", "One of the eight banners on the Moon is Scythian. The Scythians record the flight in their archives."), True)

UI = {
 "title": L("Хроника держав", "Nations Timeline"),
 "kicker": L("История мира", "World history"),
 "sub": L("Десять держав PaxVanila от Древнего мира до колонизации Луны. Выберите эпоху, чтобы увидеть, как назывался каждый народ, кому он служил и что с ним случилось.",
          "The ten powers of PaxVanila from the Ancient World to the colonisation of the Moon. Pick an era to see what each people was called, whose side it was on and what happened to it."),
 "era": L("Эпоха", "Era"), "prev": L("Раньше", "Earlier"), "next": L("Позже", "Later"),
 "events": L("Главное за эпоху", "Key events"), "world": L("Мир в эту эпоху", "The world in this era"),
 "was": L("было", "was"), "server": L("На сервере", "On the server"),
 "all": L("Все эпохи сразу", "All eras at once"),
 "allsub": L("Строка — держава, столбец — эпоха. Нажмите на клетку, чтобы открыть эпоху.", "Rows are powers, columns are eras. Tap a cell to open that era."),
 "added": L("дополнено для хроники, в летописи об этом нет", "added for this timeline, not in the chronicle"),
 "blocs": L("Расклад сил", "Balance of power"),
 "next_eras": L("Что дальше: Марс, цивилизация I типа, Сфера Дайсона и звёзды — в «Поздних эпохах».", "What comes next: Mars, the Type I civilisation, the Dyson Sphere and the stars are in \"Late Eras\"."),
 "lore": L("Читать лор", "Read the lore"), "home": L("На главную", "Home"),
 "proto": L("прообраз", "real-world model"), "years": L("годы", "years"),
 "count": L("год от Ромула", "years from Romulus"),
 "note": L("Счёт лет: год 0 — высадка Ромула, до него — «до Ромула» (д.Р.).", "Year count: year 0 is Romulus's landing; earlier dates are \"before Romulus\" (BR)."),
}

out = {"_comment": "Хроника держав: tools/build_site.py → docs/timeline.html и docs/en/timeline.html. Источник: лор/средние_эпохи.md, лор/поздние_эпохи.md. added=true — клетка дополнена для хроники (в летописи нет).",
       "ui": UI, "tags": TAGS,
       "eras": [{"id": i, "from": {"ru": f, "en": fe}, "to": {"ru": t, "en": te}, "name": n, "motto": m, "text": tx, "server": s,
                 "events": [{"y": {"ru": y, "en": ye}, "text": et, "n": ns} for y, ye, et, ns in ev]}
                for i, f, t, fe, te, n, m, tx, s, ev in ERAS],
       "nations": [{"id": i, "color": c, "bloc": b, "name": n, "proto": p} for i, c, b, n, p in NATIONS],
       "cells": C}
# проверка полноты
for n in NATIONS:
    for e in ERAS:
        assert e[0] in C[n[0]], (n[0], e[0])
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", sum(len(v) for v in C.values()))
