# PaxVanila

Minecraft-сервер (Paper 26.2) про государства и войны: Towny + свои скрипты Skript и датапаки.

Discord: https://discord.gg/sN9TnBFec · Сайт: https://arthurgerman533-tech.github.io/minecraft/

- `content/map.json` — карта мира для сайта и приложения (схема по лору); реальные города Towny: `python3 tools/towny_map.py <plugins/Towny/data>`, потом `python3 tools/build_site.py`.
- `ЗАПУСК_СЕРВЕРА.txt` — чек-лист первого запуска и календарь недель.
- `server/plugins/Skript/scripts/` — скрипты (бордер, ивенты недель, Великая война, дипломатия, фокусы, сезоны, приваты, осада, помощники, башня, Discord).
- `server/*_README.txt` — описание каждой системы.
- `server/world/datapacks/PaxVanila_*.zip` — свои датапаки (катаклизмы, порты, башня-монолит).
- `server/plugins/*/` — наши конфиги плагинов (сами jar не хранятся, список — в README и `НЕ_НАЙДЕНО.txt`).
- `tools/sk_check.py` — проверка скриптов без сервера: `python tools/sk_check.py`.
- `PaxVanila_Client_26.2/` — клиентская сборка (`.mrpack` для Modrinth/Prism).
- `лор/`, `обложки/` — лор мира и тексты/обложки для Discord.

Не в репозитории: миры, jar плагинов и модов, сторонние датапаки, видео, конфиг DiscordSRV (там токен бота).
