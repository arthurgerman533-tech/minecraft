КАТАКЛИЗМЫ И КОСМОС (датапак PaxVanila_Cataclysms_v2.zip, пространство имён paxweather) — 2026-11-18
=====================================================================================================
Файл: server/world/datapacks/PaxVanila_Cataclysms_v2.zip (v1 лежит в server/_old_datapacks, не включать вместе).
Плагины не нужны: чистый датапак, работает на Paper сам. Формат пака 107+ (26.2).
Лор событий — лор/катаклизмы.md.

Главное для админа:
  /function paxweather:help          — все команды кликабельным списком
  /function paxweather:status        — что сейчас идёт и когда следующее
  /function paxweather:auto_on | auto_off   — авто-катаклизмы по расписанию (включены по умолчанию)
  /function paxweather:interval {min:45,max:90}   — интервал между событиями, минуты
  /function paxweather:newbie_hours {h:48}        — сколько часов новички не получают урон
  /function paxweather:start/random  — случайный земной катаклизм через 10 секунд
  /function paxweather:start/<имя>   — конкретный (см. ниже)
  /function paxweather:stop          — остановить всё

Земные (10): storm гроза, blizzard метель, drought засуха, sandstorm песчаная буря, quake землетрясение,
  meteor звёздный дождь, ash пепельная ночь, flood великий шторм/наводнение, fog туман Безымянных,
  aurora северное сияние.
Космические (8, на Луне и Марсе): flare вспышка, meteorstorm, duststorm, dustdevil, moonquake,
  lunarnight, magstorm, comet. Случайный: /function paxweather:start/random_space
Луна/Марс: /function paxweather:go_moon | go_mars | go_earth (свои измерения с пониженной гравитацией).

Безопасность (проверено по файлам датапака):
  * Блоки НЕ ломаются и не ставятся — только частицы, звук, погода, эффекты, мобы события.
    Значит, города Towny и личные приваты (paxclaims) катаклизмы не портят.
  * Урон только тем, у кого 5+ сердец; новички (по умолчанию 48 ч игрового времени) без урона.
  * Башня новичков (квадрат 96x96 вокруг 0,0) — без урона.
  * Метеориты/кометы роняют лут (loot_table meteor/comet) — повод выйти из дома.

Что стоит знать:
  * Объявления идут через tellraw, а не broadcast — в Discord (paxdiscord.sk) они НЕ уходят.
    Если нужно — можно дописать в датапак вызов «/discord bcast» или обёртку на Skript.
  * Погода во время события меняется командой weather — сезоны paxseasons.sk (random tick speed)
    этому не мешают.
  * Перелёт на Луну/Марс — через /function, т.е. только OP. Для игроков нужен командный блок
    или NPC-портал, если захотите сделать «космодром».
