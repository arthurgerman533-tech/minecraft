"""Иконки сайта вместо эмодзи.

Эмодзи в шрифтах выглядят по-разному на каждом телефоне, поэтому сайт
заменяет их на линейные SVG-иконки Lucide (лицензия ISC). app.js при загрузке
страницы находит эмодзи в тексте и подставляет иконку (функция iconify).

Запуск (нужен распакованный пакет npm lucide-static):
    npm pack lucide-static@1.80.0 && tar xzf lucide-static-1.80.0.tgz
    python3 tools/make_icons.py package/icons
Скрипт переписывает блок между /* ICONS:BEGIN */ и /* ICONS:END */ в tools/site_src/app.js.
Новый эмодзи в контенте: добавьте его в EMOJI ниже и запустите скрипт снова.
"""
import json, os, re, sys

EMOJI = {
    "⌨": "keyboard", "⏳": "hourglass", "☀": "sun", "☄": "sparkle", "☠": "skull", "☢": "radiation",
    "☰": "menu", "☼": "sun", "☾": "moon", "♜": "castle", "⚓": "anchor", "⚔": "swords", "⚖": "scale",
    "⚙": "settings", "⚠": "triangle-alert", "⚡": "zap", "⛈": "cloud-lightning", "⛏": "pickaxe",
    "⛰": "mountain", "⛵": "sailboat", "⛶": "maximize", "✅": "circle-check", "✨": "sparkles",
    "❄": "snowflake", "❤": "heart", "⬆": "arrow-up", "⬇": "download", "🌄": "sunrise", "🌊": "waves",
    "🌋": "flame", "🌌": "orbit", "🌍": "earth", "🌑": "moon", "🌕": "moon-star", "🌘": "moon",
    "🌙": "moon", "🌞": "sun", "🌤": "cloud-sun", "🌦": "cloud-sun-rain", "🌧": "cloud-rain",
    "🌩": "cloud-lightning", "🌪": "tornado", "🌫": "cloud-fog", "🌱": "sprout", "🍂": "leaf",
    "🍏": "apple", "🎁": "gift", "🎞": "film", "🎨": "palette", "🎪": "tent", "🎯": "target",
    "🎲": "dices", "🏁": "flag", "🏆": "trophy", "🏘": "house", "🏚": "house", "🏛": "landmark",
    "🏜": "sun-dim", "🏠": "house", "🏰": "castle", "🏺": "amphora", "🐉": "flame", "🐪": "package",
    "🐷": "piggy-bank", "👁": "eye", "👑": "crown", "👥": "users", "💀": "skull", "💎": "gem",
    "💛": "heart", "💣": "bomb", "💫": "sparkles", "💬": "message-circle", "💰": "coins",
    "📅": "calendar", "📆": "calendar-days", "📋": "copy", "📏": "ruler", "📑": "bookmark",
    "📖": "book-open", "📚": "library-big", "📜": "scroll-text", "📯": "megaphone", "📰": "newspaper",
    "📱": "smartphone", "📲": "smartphone", "🔍": "search", "🔒": "lock", "🔔": "bell", "🔗": "link",
    "🔥": "flame", "🔬": "microscope", "🔭": "telescope", "🔱": "shield", "🔴": "circle-dot",
    "🕊": "bird", "🕒": "clock", "🕰": "clock", "🗝": "key-round", "🗺": "map", "🗼": "radio-tower",
    "🗿": "pyramid", "😇": "feather", "🚩": "flag", "🛡": "shield", "🛩": "plane", "🛸": "rocket",
    "🟠": "circle-dot", "🤖": "bot", "🤝": "handshake", "🥁": "drum", "🦇": "ghost", "🧩": "puzzle",
    "🧬": "dna", "🧭": "compass", "🧲": "magnet",
}


def inner(path):
    s = open(path, encoding="utf-8").read()
    body = re.search(r"<svg[^>]*>(.*)</svg>", s, flags=re.S).group(1)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    return re.sub(r"\s+", " ", body).replace("> <", "><").replace(" />", "/>").strip()


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "package/icons"
    names = sorted(set(EMOJI.values()) | {"chevron-down", "x", "map-pin"})
    icons = {n: inner(os.path.join(src, n + ".svg")) for n in names}
    block = ("/* ICONS:BEGIN — генерирует tools/make_icons.py, руками не править. Lucide, ISC License */\n"
             "const ICONS=" + json.dumps(icons, ensure_ascii=False, separators=(",", ":")) + ";\n"
             "const EMO=" + json.dumps(EMOJI, ensure_ascii=False, separators=(",", ":")) + ";\n"
             "/* ICONS:END */")
    app = os.path.join(os.path.dirname(__file__), "site_src", "app.js")
    s = open(app, encoding="utf-8").read()
    if "/* ICONS:BEGIN" in s:
        s = re.sub(r"/\* ICONS:BEGIN.*?/\* ICONS:END \*/", lambda m: block, s, flags=re.S)
    else:
        s = block + "\n" + s
    open(app, "w", encoding="utf-8").write(s)
    print(f"{len(icons)} иконок, {len(EMOJI)} эмодзи → {app}")


if __name__ == "__main__":
    main()
