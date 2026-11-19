PaxVanila — «Летопись дня» (страница «Новости сервера» на сайте)
=================================================================
Сайт: страница news.html. Записи о подготовке и важные новости лежат в content/chronicle.json
(раздел entries, новая запись в начало, текст ru и en). После правки: python tools/build_site.py.

Сайт сам, по дате старта (config.launchDate), ставит записи о росте границы, новых неделях,
эпохе государств, войне и сезонах. Ничего делать не нужно.

Живые новости из игры (по желанию): скрипт plugins/Skript/scripts/paxchronicle.sk.
Нужны Skript 2.8+ и skript-reflect. Он пишет plugins/PaxMeteo/chronicle.json:
войны, дипломатия, начало эпох, караваны, новые города и нации Towny, итоги дня.
Файл виден на сайте, только если папка выложена в интернет и в content/paxvanila.json задан
config.liveUrl (как для погоды, см. ПОГОДА_README.txt). На Aternos этого сделать нельзя,
но записи всё равно копятся, и их видно командой /chronicle.

Команды:
  /chronicle                — сколько записей
  /chronicle add <текст>    — весть от администрации (в чат и в летопись), право paxchronicle.admin
  /chronicle write          — записать файл сейчас
  /chronicle reset          — очистить летопись

RSS: https://arthurgerman533-tech.github.io/minecraft/news.xml (и /en/news.xml). Её можно
подключить к Discord-боту вроде MonitoRSS, чтобы новости сами приходили в канал.
