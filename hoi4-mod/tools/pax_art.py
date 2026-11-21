# -*- coding: utf-8 -*-
"""Свои картинки PaxVanila: экраны загрузки, картинки событий, иконки фокусов и духов, портреты.

Всё рисуется кодом в пиксельном стиле, как обложки сервера (обложки/*.png):
сцена рисуется на холсте 480x270 и увеличивается в 4 раза без сглаживания.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Ванильные и DLC-имена экранов загрузки. Файлы с теми же именами перекрывают ванильные,
# поэтому в игре показываются только картинки PaxVanila. Список взят из Family
# (gfx/loadingscreens) и дополнен именами новых DLC.
LOADING_NAMES = [f"load_{i}" for i in range(1, 19)] + [
    "load_bba", "load_lar", "load_mtg", "load_mtg_2", "load_nsb", "load_tfv", "load_tiger",
    "load_aat", "load_toa", "load_goe", "load_gtd", "load_dod", "load_wtt", "load_rt56",
]

W, H = 480, 270


def _grad(d, top, bottom, h=H, w=W, y0=0):
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y0 + y), (w, y0 + y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)))


def _stars(d, rnd, n, ymax, color=(230, 230, 255)):
    for _ in range(n):
        x, y = rnd.randrange(W), rnd.randrange(ymax)
        d.point((x, y), fill=color)


def _ground(d, y, top, side, rnd):
    d.rectangle([0, y, W, H], fill=side)
    d.rectangle([0, y, W, y + 3], fill=top)
    for _ in range(300):
        x, yy = rnd.randrange(W), rnd.randrange(y + 4, H)
        d.point((x, yy), fill=tuple(max(0, v - 18) for v in side))


def _monolith(d, x, base, h, w=22, cracks=1):
    d.rectangle([x - w // 2, base - h, x + w // 2, base], fill=(28, 18, 40))
    d.rectangle([x - w // 2, base - h, x - w // 2 + 3, base], fill=(60, 40, 90))
    for i in range(0, h, 12):
        d.point((x - 3, base - i - 5), fill=(170, 90, 230))
        d.point((x + 4, base - i - 9), fill=(120, 60, 200))
    d.rectangle([x - w // 2 - 3, base - h - 4, x + w // 2 + 3, base - h], fill=(45, 30, 65))
    for c in range(cracks):
        cy = base - h // 2 - c * 18
        d.line([(x - w // 2, cy), (x - 2, cy + 5), (x + 3, cy - 2), (x + w // 2, cy + 3)], fill=(255, 200, 120))


def _guardian(d, x, base, color=(150, 150, 160), eye=(255, 140, 40)):
    d.rectangle([x - 5, base - 22, x + 5, base - 8], fill=color)
    d.rectangle([x - 4, base - 30, x + 4, base - 22], fill=color)
    d.rectangle([x - 8, base - 21, x - 6, base - 10], fill=color)
    d.rectangle([x + 6, base - 21, x + 8, base - 10], fill=color)
    d.rectangle([x - 4, base - 8, x - 1, base], fill=color)
    d.rectangle([x + 1, base - 8, x + 4, base], fill=color)
    d.point((x - 2, base - 27), fill=eye)
    d.point((x + 2, base - 27), fill=eye)


def scene_monolith(rnd):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    _grad(d, (10, 8, 30), (60, 30, 80)); _stars(d, rnd, 160, 170)
    d.ellipse([380, 30, 420, 70], fill=(240, 230, 200))
    _ground(d, 210, (70, 140, 60), (90, 65, 40), rnd)
    _monolith(d, 240, 210, 170, 26, cracks=1)
    for x in (200, 280):
        _guardian(d, x, 210)
    for x in (180, 300, 160, 320):
        d.rectangle([x - 4, 204, x + 4, 210], fill=(110, 110, 115))  # пустые постаменты
    return im


def scene_storm(rnd):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    _grad(d, (20, 22, 35), (70, 70, 90))
    for _ in range(40):
        x, y = rnd.randrange(W), rnd.randrange(80)
        d.ellipse([x - 30, y - 8, x + 30, y + 10], fill=(45, 45, 60))
    _ground(d, 215, (60, 110, 50), (70, 55, 40), rnd)
    _monolith(d, 240, 215, 175, 26, cracks=3)
    pts = [(250, 0), (238, 40), (252, 45), (236, 90), (248, 95), (240, 130)]
    d.line(pts, fill=(255, 255, 210), width=3)
    d.line(pts, fill=(170, 200, 255), width=1)
    for _ in range(400):
        x, y = rnd.randrange(W), rnd.randrange(H)
        d.line([(x, y), (x - 2, y + 6)], fill=(110, 120, 150))
    return im


def scene_steppe(rnd):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    _grad(d, (250, 160, 70), (120, 60, 70), h=190)
    d.ellipse([200, 120, 280, 200], fill=(255, 220, 120))
    _ground(d, 190, (170, 160, 70), (120, 100, 50), rnd)
    for i, x in enumerate((70, 140, 330, 400)):
        d.polygon([(x - 26, 190), (x - 26, 168), (x, 150), (x + 26, 168), (x + 26, 190)], fill=(230, 220, 200))
        d.rectangle([x - 5, 176, x + 5, 190], fill=(90, 50, 30))
        d.line([(x, 150), (x, 132)], fill=(60, 40, 30))
        d.polygon([(x, 132), (x + 14, 136), (x, 140)], fill=[(180, 30, 30), (40, 60, 150), (200, 160, 40), (40, 120, 60)][i])
    for x in range(180, 300, 14):
        d.rectangle([x, 214, x + 3, 226], fill=(40, 30, 30))
        d.rectangle([x - 3, 206, x + 6, 214], fill=(50, 35, 35))
    d.polygon([(232, 232), (240, 212), (248, 232)], fill=(255, 120, 30))
    d.polygon([(236, 232), (240, 220), (244, 232)], fill=(255, 220, 80))
    return im


def scene_forum(rnd):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    _grad(d, (90, 150, 220), (230, 210, 170), h=200)
    d.ellipse([360, 25, 420, 85], fill=(255, 215, 90))
    _monolith(d, 390, 200, 120, 14, cracks=1)
    d.rectangle([0, 200, W, H], fill=(200, 190, 160))
    d.rectangle([60, 80, 330, 96], fill=(235, 225, 200))
    d.polygon([(50, 80), (195, 40), (340, 80)], fill=(225, 215, 190))
    for x in range(75, 330, 32):
        d.rectangle([x, 96, x + 12, 196], fill=(240, 235, 215))
        d.rectangle([x - 3, 192, x + 15, 200], fill=(210, 200, 180))
    d.text((150, 58), "SPQR", fill=(160, 120, 40))
    return im


def scene_north(rnd):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    _grad(d, (30, 40, 70), (150, 170, 200))
    for i in range(5):
        y = 40 + i * 12
        pts = [(x, y + math.sin(x / 40 + i) * 8) for x in range(0, W + 1, 6)]
        d.line(pts, fill=(80, 220, 160) if i % 2 else (120, 160, 255), width=2)
    _ground(d, 200, (240, 245, 255), (200, 210, 230), rnd)
    d.rectangle([300, 120, 420, 200], fill=(90, 90, 110))
    for x in range(300, 421, 12):
        d.rectangle([x, 112, x + 6, 120], fill=(90, 90, 110))
    d.rectangle([350, 160, 370, 200], fill=(40, 30, 30))
    for x in (30, 70, 110, 150, 200, 250):
        d.polygon([(x - 16, 200), (x, 140), (x + 16, 200)], fill=(30, 70, 50))
        d.polygon([(x - 10, 170), (x, 140), (x + 10, 170)], fill=(240, 245, 255))
    for _ in range(500):
        d.point((rnd.randrange(W), rnd.randrange(H)), fill=(250, 250, 255))
    return im


def scene_sea(rnd):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    _grad(d, (250, 120, 80), (110, 60, 120), h=170)
    d.ellipse([210, 120, 270, 180], fill=(255, 200, 120))
    _grad(d, (40, 60, 120), (15, 25, 60), h=100, y0=170)
    for y in range(175, H, 6):
        for x in range(rnd.randrange(10), W, 20):
            d.line([(x, y), (x + 8, y)], fill=(90, 120, 190))
    for x, s in ((90, 1.0), (330, 0.8)):
        d.polygon([(x - 50 * s, 178), (x + 50 * s, 178), (x + 38 * s, 192), (x - 40 * s, 192)], fill=(70, 40, 30))
        d.line([(x, 178), (x, 178 - 70 * s)], fill=(50, 30, 20), width=2)
        d.polygon([(x + 2, 110 * s + 68 * (1 - s) + 0), (x + 40 * s, 170), (x + 2, 170)], fill=(240, 235, 220))
        d.polygon([(x - 2, 120), (x - 34 * s, 170), (x - 2, 170)], fill=(230, 225, 210))
    return im


def scene_seven(rnd):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    _grad(d, (10, 10, 15), (30, 25, 30))
    for y in range(0, H, 16):
        for x in range((y // 16) % 2 * 16, W, 32):
            d.rectangle([x, y, x + 15, y + 15], fill=(35, 33, 40))
    d.rectangle([150, 40, 330, 250], fill=(60, 50, 45))
    d.rectangle([160, 50, 320, 250], fill=(20, 15, 20))
    x, b = 240, 240
    c = (190, 110, 60)
    d.rectangle([x - 26, b - 120, x + 26, b - 50], fill=c)
    d.rectangle([x - 18, b - 160, x + 18, b - 120], fill=c)
    d.rectangle([x - 44, b - 118, x - 30, b - 60], fill=c)
    d.rectangle([x + 30, b - 118, x + 44, b - 60], fill=c)
    d.rectangle([x - 22, b - 50, x - 6, b], fill=c)
    d.rectangle([x + 6, b - 50, x + 22, b], fill=c)
    for ex in (x - 8, x + 8):
        d.ellipse([ex - 4, b - 146, ex + 4, b - 138], fill=(255, 210, 120))
    d.ellipse([x - 9, b - 100, x + 9, b - 82], fill=(255, 120, 60))
    d.text((x - 3, b - 96), "7", fill=(60, 20, 10))
    for _ in range(60):
        r = rnd.randrange(30, 120); a = rnd.random() * math.tau
        d.point((x + math.cos(a) * r, b - 120 + math.sin(a) * r * 0.6), fill=(255, 190, 110))
    return im


def scene_neon(rnd):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    _grad(d, (15, 0, 35), (60, 10, 70)); _stars(d, rnd, 60, 90, (255, 120, 255))
    x = 0
    while x < W:
        bw, bh = rnd.randrange(24, 60), rnd.randrange(60, 220)
        d.rectangle([x, H - bh, x + bw, H], fill=(20, 15, 40))
        for wy in range(H - bh + 6, H - 6, 8):
            for wx in range(x + 4, x + bw - 4, 7):
                if rnd.random() < 0.45:
                    d.point((wx, wy), fill=rnd.choice([(0, 255, 230), (255, 60, 200), (255, 230, 90)]))
        x += bw + rnd.randrange(2, 10)
    _monolith(d, 240, H, 250, 30, cracks=4)
    d.rectangle([215, 60, 265, 72], fill=(0, 255, 230))
    d.text((222, 61), "PAX", fill=(15, 0, 35))
    return im


def scene_cold(rnd):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    _grad(d, (40, 45, 60), (110, 110, 120))
    _ground(d, 205, (90, 100, 80), (70, 65, 55), rnd)
    _monolith(d, 240, 205, 160, 24, cracks=2)
    for x in range(0, W, 18):
        if abs(x - 240) > 30:
            d.rectangle([x, 175, x + 16, 205], fill=(150, 150, 150))
            d.line([(x, 175), (x + 16, 175)], fill=(110, 110, 110))
    d.line([(0, 168), (W, 168)], fill=(60, 60, 60))
    for x in range(0, W, 10):
        d.line([(x, 164), (x + 5, 172)], fill=(80, 80, 80))
    for x, col in ((90, (40, 60, 150)), (390, (160, 40, 40))):
        d.line([(x, 175), (x, 110)], fill=(30, 30, 30), width=2)
        d.rectangle([x + 1, 110, x + 40, 132], fill=col)
    return im


def scene_precursors(rnd):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    _grad(d, (60, 90, 160), (240, 190, 120), h=200)
    _ground(d, 200, (220, 190, 120), (190, 160, 100), rnd)
    for x, s in ((120, 1.0), (300, 0.7), (400, 0.5)):
        for i in range(8):
            ww = int((80 - i * 10) * s)
            yy = 200 - int(i * 12 * s)
            d.rectangle([x - ww, yy - int(12 * s), x + ww, yy], fill=(200 - i * 5, 170 - i * 5, 110))
    for i, x in enumerate(range(200, 260, 14)):
        d.rectangle([x, 214, x + 10, 230], fill=(150, 130, 100))
        d.line([(x + 2, 218), (x + 8, 218)], fill=(80, 60, 40))
        d.line([(x + 2, 223), (x + 6, 223)], fill=(80, 60, 40))
    _monolith(d, 450, 200, 90, 10, cracks=0)
    return im


SCENES = [
    ("monolith", scene_monolith, "Монолит в 1936 году: двое последних Стражей"),
    ("storm", scene_storm, "Молния бьёт в Монолит"),
    ("steppe", scene_steppe, "Курултай в степи"),
    ("forum", scene_forum, "Форум Ромеи"),
    ("north", scene_north, "Метель над Северным Царством"),
    ("sea", scene_sea, "Флоты Островного Союза и Карфагена"),
    ("seven", scene_seven, "Страж-7 под башней"),
    ("neon", scene_neon, "Мегакорпорации 2096 года"),
    ("cold", scene_cold, "Холодная война у башни"),
    ("precursors", scene_precursors, "Пирамиды Предтеч"),
]

# Какая сцена у какого события
EVENT_SCENES = {
    "pax.1": "monolith", "pax.2": "forum", "pax.3": "steppe", "pax.10": "storm", "pax.11": "cold",
    "pax.12": "seven", "pax.20": "precursors", "pax.21": "monolith", "pax.22": "forum",
    "pax.23": "neon", "pax.24": "cold", "pax.25": "seven", "pax.30": "north", "pax.40": "storm",
}


def render(name, scale=4):
    fn = dict((n, f) for n, f, _ in SCENES)[name]
    im = fn(random.Random(name))
    return im.resize((W * scale, H * scale), Image.NEAREST)


def _logo(im):
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 54)
    d.rectangle([48, im.height - 120, 470, im.height - 48], fill=(15, 10, 25))
    d.text((70, im.height - 114), "PaxVanila", font=f, fill=(255, 215, 90))
    return im


def _crop(im, size):
    tw, th = size
    r = max(tw / im.width, th / im.height)
    im = im.resize((math.ceil(im.width * r), math.ceil(im.height * r)), Image.NEAREST)
    x, y = (im.width - tw) // 2, (im.height - th) // 2
    return im.crop((x, y, x + tw, y + th))


# --- иконки ------------------------------------------------------------------
def _icon_canvas(size, s=4):
    return Image.new("RGBA", (size[0] * s, size[1] * s), (0, 0, 0, 0))


def _shield(d, w, h, fill, edge=(230, 190, 90)):
    pts = [(w * 0.18, h * 0.12), (w * 0.82, h * 0.12), (w * 0.82, h * 0.55), (w * 0.5, h * 0.92), (w * 0.18, h * 0.55)]
    d.polygon(pts, fill=edge)
    k = 0.06
    inner = [(w * (0.18 + k), h * (0.12 + k)), (w * (0.82 - k), h * (0.12 + k)), (w * (0.82 - k), h * 0.53),
             (w * 0.5, h * (0.92 - k * 1.4)), (w * (0.18 + k), h * 0.53)]
    d.polygon(inner, fill=fill)
    return inner


SYMBOLS = {}


def symbol(name):
    def deco(fn):
        SYMBOLS[name] = fn
        return fn
    return deco


@symbol("gear")
def _gear(d, cx, cy, r, c):
    for a in range(0, 360, 45):
        x, y = cx + math.cos(math.radians(a)) * r, cy + math.sin(math.radians(a)) * r
        d.rectangle([x - r * 0.22, y - r * 0.22, x + r * 0.22, y + r * 0.22], fill=c)
    d.ellipse([cx - r * 0.85, cy - r * 0.85, cx + r * 0.85, cy + r * 0.85], fill=c)
    d.ellipse([cx - r * 0.35, cy - r * 0.35, cx + r * 0.35, cy + r * 0.35], fill=(40, 35, 45))


@symbol("sword")
def _sword(d, cx, cy, r, c):
    for s in (-1, 1):
        d.line([(cx - s * r, cy + r), (cx + s * r * 0.8, cy - r * 0.9)], fill=c, width=int(r * 0.22))
        d.line([(cx - s * r * 0.95 + r * 0.25, cy + r * 0.45), (cx - s * r * 0.45 - r * 0.25, cy + r * 0.95)], fill=c, width=int(r * 0.18))


@symbol("coin")
def _coin(d, cx, cy, r, c):
    for i, dy in enumerate((0.45, 0.15, -0.15)):
        d.ellipse([cx - r * 0.9, cy + r * dy - r * 0.35, cx + r * 0.9, cy + r * dy + r * 0.35], fill=c, outline=(120, 90, 30), width=3)
    d.ellipse([cx - r * 0.8, cy - r * 0.95, cx + r * 0.8, cy + r * 0.05], fill=c, outline=(120, 90, 30), width=3)


@symbol("column")
def _column(d, cx, cy, r, c):
    d.rectangle([cx - r, cy - r, cx + r, cy - r * 0.75], fill=c)
    d.rectangle([cx - r, cy + r * 0.75, cx + r, cy + r], fill=c)
    for dx in (-0.6, 0, 0.6):
        d.rectangle([cx + dx * r - r * 0.16, cy - r * 0.75, cx + dx * r + r * 0.16, cy + r * 0.75], fill=c)


@symbol("sun")
def _sun(d, cx, cy, r, c):
    for a in range(0, 360, 30):
        d.line([(cx, cy), (cx + math.cos(math.radians(a)) * r, cy + math.sin(math.radians(a)) * r)], fill=c, width=int(r * 0.16))
    d.ellipse([cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5], fill=c)


@symbol("tower")
def _tower(d, cx, cy, r, c):
    d.rectangle([cx - r * 0.3, cy - r, cx + r * 0.3, cy + r], fill=(30, 20, 45))
    d.line([(cx - r * 0.3, cy), (cx, cy + r * 0.12), (cx + r * 0.3, cy - r * 0.1)], fill=c, width=int(r * 0.1))
    d.rectangle([cx - r * 0.45, cy - r * 1.05, cx + r * 0.45, cy - r * 0.85], fill=c)


ICON_COLORS = {"gear": (200, 200, 210), "sword": (225, 225, 235), "coin": (240, 200, 80),
               "column": (240, 235, 220), "sun": (255, 210, 90), "tower": (200, 130, 255)}


def focus_icon(sym, bg):
    s = 4
    im = _icon_canvas((94, 84), s)
    d = ImageDraw.Draw(im)
    w, h = im.size
    _shield(d, w, h, bg)
    SYMBOLS[sym](d, w * 0.5, h * 0.45, w * 0.2, ICON_COLORS[sym])
    return im.resize((94, 84), Image.LANCZOS)


def idea_icon(sym, bg):
    s = 4
    im = _icon_canvas((64, 64), s)
    d = ImageDraw.Draw(im)
    w, h = im.size
    d.rectangle([w * 0.08, h * 0.08, w * 0.92, h * 0.92], fill=(230, 190, 90))
    d.rectangle([w * 0.13, h * 0.13, w * 0.87, h * 0.87], fill=bg)
    SYMBOLS[sym](d, w * 0.5, h * 0.5, w * 0.24, ICON_COLORS[sym])
    return im.resize((64, 64), Image.LANCZOS)


def flag_icon(flag_im, size, framed_shield=True):
    s = 4
    im = _icon_canvas(size, s)
    d = ImageDraw.Draw(im)
    w, h = im.size
    if framed_shield:
        inner = _shield(d, w, h, (0, 0, 0))
        mask = Image.new("L", im.size, 0)
        ImageDraw.Draw(mask).polygon(inner, fill=255)
    else:
        d.rectangle([w * 0.08, h * 0.08, w * 0.92, h * 0.92], fill=(230, 190, 90))
        mask = Image.new("L", im.size, 0)
        ImageDraw.Draw(mask).rectangle([w * 0.13, h * 0.13, w * 0.87, h * 0.87], fill=255)
    fl = _crop(flag_im.convert("RGBA"), im.size)
    im.paste(fl, (0, 0), mask)
    return im.resize(size, Image.LANCZOS)


def portrait(flag_im, color, accent, kind, seed):
    """Пиксельный портрет 156x210: правитель в короне/шлеме на фоне флага."""
    rnd = random.Random(seed)
    pw, ph = 39, 52
    im = Image.new("RGB", (pw, ph))
    d = ImageDraw.Draw(im)
    bg = _crop(flag_im.convert("RGB"), (pw, ph))
    im.paste(Image.blend(bg, Image.new("RGB", (pw, ph), (15, 12, 20)), 0.55))
    skin = rnd.choice([(232, 190, 150), (210, 160, 120), (180, 130, 95), (240, 205, 170)])
    hair = rnd.choice([(40, 30, 25), (90, 60, 30), (200, 170, 110), (120, 120, 120)])
    robe = tuple(int(v * 0.8) for v in color)
    d.rectangle([6, 38, 33, 52], fill=robe)
    d.rectangle([16, 36, 23, 40], fill=skin)
    d.rectangle([12, 18, 27, 36], fill=skin)
    d.rectangle([12, 16, 27, 21], fill=hair)
    d.rectangle([11, 18, 12, 28], fill=hair)
    d.rectangle([27, 18, 28, 28], fill=hair)
    d.point((16, 26), fill=(30, 30, 40)); d.point((23, 26), fill=(30, 30, 40))
    d.line([(17, 32), (22, 32)], fill=(150, 80, 70))
    if rnd.random() < 0.5:
        d.rectangle([13, 31, 26, 36], fill=hair)
        d.line([(17, 32), (22, 32)], fill=(150, 80, 70))
    if kind in ("hammer_cross", "snow_star"):  # шлем
        d.rectangle([11, 12, 28, 18], fill=(140, 140, 150))
        d.rectangle([19, 8, 20, 12], fill=accent)
    elif kind in ("sun_horse", "kurgan"):  # меховая шапка
        d.rectangle([10, 11, 29, 18], fill=(120, 80, 50))
        d.rectangle([18, 8, 21, 11], fill=accent)
    else:  # корона или венок
        d.rectangle([12, 13, 27, 16], fill=accent)
        for x in (12, 16, 20, 24, 27):
            d.rectangle([x, 10, x, 13], fill=accent)
    d.rectangle([17, 42, 22, 46], fill=accent)
    return im.resize((156, 210), Image.NEAREST)


def save_dds(im, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.convert("RGBA").save(path, pixel_format="DXT1")


def bookmark_frame(im, title, date_text, accent=(255, 215, 90)):
    """Фирменное оформление сценария PaxVanila: тёмная виньетка, двойная золотая рамка, плашка с названием и датой."""
    im = im.convert("RGBA").copy()
    w, h = im.size
    # виньетка
    vig = Image.new("RGBA", im.size, (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for i in range(60):
        a = int(150 * (1 - i / 60) ** 2)
        vd.rectangle([i, i, w - i, h - i], outline=(5, 3, 12, a))
    im = Image.alpha_composite(im, vig)
    d = ImageDraw.Draw(im)
    # двойная рамка
    d.rectangle([14, 14, w - 15, h - 15], outline=accent, width=4)
    d.rectangle([28, 28, w - 29, h - 29], outline=(120, 90, 30), width=2)
    for cx, cy in ((14, 14), (w - 15, 14), (14, h - 15), (w - 15, h - 15)):
        d.rectangle([cx - 10, cy - 10, cx + 10, cy + 10], fill=(15, 10, 25), outline=accent, width=3)
    # плашка внизу
    fb = ImageFont.truetype(FONT, max(36, w // 28))
    fs = ImageFont.truetype(FONT, max(26, w // 44))
    bar_h = int(h * 0.2)
    d.rectangle([28, h - 28 - bar_h, w - 29, h - 29], fill=(15, 10, 25, 225))
    d.line([28, h - 28 - bar_h, w - 29, h - 28 - bar_h], fill=accent, width=3)
    d.text((60, h - 28 - bar_h + bar_h * 0.12), title, font=fb, fill=accent)
    d.text((60, h - 28 - bar_h + bar_h * 0.58), date_text, font=fs, fill=(230, 225, 205))
    # печать Монолита справа
    cx, cy = w - 110, h - 28 - bar_h // 2
    d.rectangle([cx - 18, cy - 38, cx + 18, cy + 38], fill=(20, 18, 28), outline=accent, width=3)
    d.line([cx, cy - 30, cx, cy - 6], fill=(255, 140, 40), width=3)
    return im
