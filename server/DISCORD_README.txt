DISCORD (DiscordSRV 1.30.5, Modrinth, заявлены 26.2/26.3, SHA512 сверен) — 2026-11-16
==================================================================================
Файлы:
  plugins/DiscordSRV-Build-1.30.5.jar
  plugins/DiscordSRV/config.yml        — русский шаблон, канал консоли ВЫКЛЮЧЕН (безопасность)
  plugins/Skript/scripts/paxdiscord.sk — пересылает объявления сервера в Discord

Что нужно вписать в plugins/DiscordSRV/config.yml (сейчас там заглушки):
  BotToken: "<токен бота>"
  Channels: {"global": "<ID канала для чата>", "broadcasts": "<ID канала анонсов>"}

Как получить:
  1. https://discord.com/developers/applications -> New Application -> Bot -> Reset Token (скопировать).
     На вкладке Bot включить: MESSAGE CONTENT INTENT и SERVER MEMBERS INTENT.
  2. OAuth2 -> URL Generator: scopes "bot" + "applications.commands", права: Send Messages,
     Read Message History, Embed Links, Manage Webhooks. Открыть ссылку, добавить бота на свой сервер.
  3. В Discord: Настройки -> Расширенные -> Режим разработчика. ПКМ по каналу -> Копировать ID.
  4. Перезапуск сервера (токен) или /discord reload (каналы).

Что уходит в Discord:
  * канал "global": чат игроков, входы/выходы, смерти, старт/стоп сервера (стандарт DiscordSRV);
  * канал "broadcasts": все объявления с префиксами [PaxVanila], [Дипломатия], [Война #..], [Караван],
    [Событие], [Фокус], [Сезон] — начало недель, фазы Великой войны, объявления войн, пакты, вассалы,
    события сезонов. Строки-продолжения сразу после объявления тоже пересылаются.
  * Символ @ заменяется, чтобы из игры нельзя было пинговать @everyone.

Проверка: /paxdiscord test (OP). Если в Discord ничего не пришло, а токен верный —
значит Skript на этом сервере не вызывает событие "on broadcast" для своих объявлений; напишите, переделаю.
