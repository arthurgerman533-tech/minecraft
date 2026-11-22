#!/usr/bin/env python3
"""Лента иконок зданий на 34 кадра (46x46): кадры 1-16 из старой ленты Family (r56), остальные дорисованы."""
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
FW = 46
ORANGE = (255, 150, 30, 255)
BLUE = (70, 140, 230, 255)
TEAL = (90, 180, 170, 255)
GREY = (190, 190, 190, 255)
YELLOW = (255, 220, 60, 255)
GREEN = (110, 190, 70, 255)


def blank_from(frame):
    """Пустая плашка: затираем яркие пиксели значка цветом фона слева в той же строке."""
    im = frame.copy()
    px = im.load()
    for y in range(FW):
        bg = px[5, y]
        for x in range(6, FW - 6):
            r, g, b, a = px[x, y]
            if abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2]) > 10:
                px[x, y] = bg
    return im


def new_frame(base):
    f = blank_from(base)
    return f, ImageDraw.Draw(f)


def flask(d, col, x=23, top=9):
    d.polygon([(x - 3, top), (x + 3, top), (x + 3, top + 9), (x + 11, top + 26), (x - 11, top + 26), (x - 3, top + 9)], outline=col, width=2)
    d.line([(x - 5, top), (x + 5, top)], fill=col, width=2)


def frame_for(n, base, src):
    f, d = new_frame(base)
    if n == 17:  # воздушная лаборатория: колба и самолёт
        flask(d, BLUE); d.polygon([(23, 22), (30, 31), (23, 29), (16, 31)], fill=BLUE)
    elif n == 18:  # морская: колба и якорь
        flask(d, TEAL); d.arc([17, 24, 29, 34], 0, 180, fill=TEAL, width=2); d.line([(23, 20), (23, 33)], fill=TEAL, width=2)
    elif n == 19:  # наземная: колба и танк
        flask(d, GREEN); d.rectangle([16, 28, 30, 32], fill=GREEN); d.line([(23, 26), (31, 24)], fill=GREEN, width=2)
    elif n == 20:  # ядерная: колба и атом
        flask(d, ORANGE); d.ellipse([19, 25, 27, 33], outline=ORANGE, width=2); d.ellipse([22, 28, 24, 30], fill=ORANGE)
    elif n in (21, 22):
        pass
    elif n == 23:  # опорный пункт: крепость
        d.rectangle([10, 20, 36, 36], outline=ORANGE, width=3)
        for x in (10, 19, 28):
            d.rectangle([x, 12, x + 7, 20], fill=ORANGE)
    elif n == 24:  # мега-орудие
        d.line([(10, 33), (34, 12)], fill=ORANGE, width=6); d.ellipse([8, 29, 20, 41], fill=ORANGE)
        d.line([(10, 36), (36, 36)], fill=ORANGE, width=3)
    elif n == 25:  # канал
        for y in (16, 28):
            d.line([(8, y), (38, y)], fill=BLUE, width=3)
        d.line([(16, 16), (16, 28)], fill=BLUE, width=3); d.line([(30, 16), (30, 28)], fill=BLUE, width=3)
        d.line([(8, 36), (38, 36)], fill=BLUE, width=2)
    elif n == 26:  # плотина
        d.polygon([(10, 14), (36, 14), (40, 36), (6, 36)], outline=ORANGE, width=3)
        d.line([(14, 24), (32, 24)], fill=BLUE, width=3); d.line([(12, 30), (34, 30)], fill=BLUE, width=3)
    elif n == 27:  # коммерческий реактор: атом + монета
        f = src[12].copy(); d = ImageDraw.Draw(f); d.ellipse([30, 30, 41, 41], fill=YELLOW)
    elif n == 28:  # морской узел снабжения
        f = src[14].copy(); px = f.load()
        for y in range(FW):
            for x in range(6, FW - 6):
                r, g, b, a = px[x, y]
                if r > 120 and g > 60 and b < 90: px[x, y] = (TEAL[0], TEAL[1], TEAL[2], a)
    elif n == 29:  # морской штаб: флаг
        d.line([(15, 12), (15, 38)], fill=TEAL, width=3)
        d.polygon([(15, 12), (36, 17), (15, 24)], fill=TEAL)
    elif n == 30:  # энергетическая инфраструктура: молния
        d.polygon([(26, 8), (14, 26), (22, 26), (18, 39), (33, 20), (25, 20)], fill=YELLOW)
    elif n == 31:  # промышленная инфраструктура: шестерня
        d.ellipse([13, 13, 33, 33], outline=ORANGE, width=5); d.ellipse([20, 20, 26, 26], fill=ORANGE)
        for a in range(8):
            import math
            x = 23 + 14 * math.cos(a * math.pi / 4); y = 23 + 14 * math.sin(a * math.pi / 4)
            d.rectangle([x - 2, y - 2, x + 2, y + 2], fill=ORANGE)
    elif n == 32:  # командный пункт Sonnengrad: тарелка
        d.arc([10, 14, 36, 40], 200, 340, fill=ORANGE, width=4); d.line([(23, 26), (23, 38)], fill=ORANGE, width=3)
        d.ellipse([21, 10, 25, 14], fill=YELLOW)
    return f


def build(out_path):
    src_im = Image.open(os.path.join(HERE, "bld_src", "r56_strip.png")).convert("RGBA")
    src = [src_im.crop((i * FW, 0, (i + 1) * FW, FW)) for i in range(src_im.width // FW)]
    frames = list(src[:16])
    for n in range(17, 33):
        frames.append(frame_for(n, src[6], src))
    frames.append(src[16])  # 33: steel_mill
    frames.append(src[17])  # 34: aluminum_mill
    strip = Image.new("RGBA", (FW * len(frames), FW))
    for i, f in enumerate(frames):
        strip.paste(f, (i * FW, 0))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    strip.save(out_path, pixel_format="DXT5")
    return len(frames), strip


if __name__ == "__main__":
    n, s = build("/tmp/pax_building_icon_strip.dds")
    s.resize((s.width * 2, s.height * 2), Image.NEAREST).save("/mnt/project-files/hoi4-mod/screens/bld_strip_preview.png")
    print(n)
