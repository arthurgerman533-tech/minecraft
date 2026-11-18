Косметические плагины PaxVanila (все с Modrinth, бесплатные, под Paper 26.2, SHA512 проверен)

SkinsRestorer 15.12.6   — скины (в т.ч. для пиратских аккаунтов). /skin set <ник|ссылка_на_png>, /skin clear
ImageFrame 2026.1.5     — свои картинки и GIF на картах в рамках. Ресурспак НЕ нужен.
GSit 3.8.0              — сесть/лечь/ползти: /sit, /lay, /crawl, ПКМ по ступеньке
ArmorStandEditor 52.1   — позирование стоек для брони (флинт в руку, ПКМ по стойке)
HeadDB 6.1.1            — каталог декоративных голов: /hdb

Ни один из них не использует ресурспак, конфликта с паком WeaponMechanics нет.

КАК ПОВЕСИТЬ СВОЮ КАРТИНКУ (ImageFrame)
1. Залей картинку (png/jpg/gif) куда-нибудь с прямой ссылкой (Discord-вложение, imgur -> "Copy image link").
2. Поставь стену из рамок, например 4x3 (рамки ставь на блоки, все в одну сторону).
3. В игре:  /imageframe create <название> <ссылка> 4 3
   Получишь карты — кликни ими по рамкам, либо используй /imageframe select и выдели рамки.
   Соотношение сторон: 1 карта = 128x128 пикселей. Для 4x3 лучше картинка 512x384.
4. Полезное: /imageframe list, /imageframe delete <название>, /imageframe info <название>.
   Лимиты на игрока — plugins/ImageFrame/config.yml (MaxImagesPerPlayer, размеры).
   Чтобы картинки мог делать только админ — не выдавай права imageframe.create обычным игрокам.

Права: на Minehut без LuckPerms всё по OP. Если поставите LuckPerms — выдать игрокам
gsit.sit, gsit.lay, skinsrestorer.command.set, headdb.open (по желанию).
