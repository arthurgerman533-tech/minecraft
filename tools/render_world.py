#!/usr/bin/env python3
"""render_world.py — настоящая карта мира PaxVanila сверху из файлов региона (.mca).

    python3 tools/render_world.py <папка world/region> [--radius 2048]

Читает каждый чанк (формат 1.18+: sections / block_states / biomes / Heightmaps),
берёт верхний блок по карте высот WORLD_SURFACE, красит по таблице цветов,
затеняет рельеф (свет с северо-запада), под водой показывает глубину.
Пишет:
  content/world_map.webp      — карта для сайта и приложения (1 px = 1 блок, до 2048 px, иначе 1 px = 2 блока)
  content/world_map_big.webp  — 1 пиксель = 1 блок (кнопка «подробная карта»)
  Картинка обрезана до прогруженной области, её края в world_zones.json → bounds [x0, z0, x1, z1].
  content/world_zones.json    — где на карте пустыни, океаны, горы, снег, джунгли
                                (для слоя погоды: куда приходят бури)
Без внешних библиотек NBT: только numpy и Pillow.
"""
import argparse, gzip, io, json, os, struct, sys, zlib
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_Y = -64

# ---------- NBT ----------
def _nbt(buf, pos, t):
    if t == 1: return struct.unpack_from(">b", buf, pos)[0], pos + 1
    if t == 2: return struct.unpack_from(">h", buf, pos)[0], pos + 2
    if t == 3: return struct.unpack_from(">i", buf, pos)[0], pos + 4
    if t == 4: return struct.unpack_from(">q", buf, pos)[0], pos + 8
    if t == 5: return struct.unpack_from(">f", buf, pos)[0], pos + 4
    if t == 6: return struct.unpack_from(">d", buf, pos)[0], pos + 8
    if t == 7:
        n = struct.unpack_from(">i", buf, pos)[0]; pos += 4
        return buf[pos:pos + n], pos + n
    if t == 8:
        n = struct.unpack_from(">H", buf, pos)[0]; pos += 2
        return buf[pos:pos + n].decode("utf-8", "replace"), pos + n
    if t == 9:
        et = buf[pos]; n = struct.unpack_from(">i", buf, pos + 1)[0]; pos += 5
        out = []
        for _ in range(n):
            v, pos = _nbt(buf, pos, et); out.append(v)
        return out, pos
    if t == 10:
        d = {}
        while True:
            tt = buf[pos]; pos += 1
            if tt == 0: return d, pos
            n = struct.unpack_from(">H", buf, pos)[0]; pos += 2
            name = buf[pos:pos + n].decode("utf-8", "replace"); pos += n
            d[name], pos = _nbt(buf, pos, tt)
    if t == 11:
        n = struct.unpack_from(">i", buf, pos)[0]; pos += 4
        return np.frombuffer(buf, ">i4", n, pos), pos + 4 * n
    if t == 12:
        n = struct.unpack_from(">i", buf, pos)[0]; pos += 4
        return np.frombuffer(buf, ">i8", n, pos), pos + 8 * n
    raise ValueError(f"NBT tag {t}")

def read_nbt(data):
    t = data[0]; n = struct.unpack_from(">H", data, 1)[0]
    v, _ = _nbt(data, 3 + n, t)
    return v

def region_chunks(path):
    with open(path, "rb") as f: raw = f.read()
    if len(raw) < 8192: return
    for i in range(1024):
        off = int.from_bytes(raw[i * 4:i * 4 + 3], "big"); cnt = raw[i * 4 + 3]
        if not off or not cnt: continue
        p = off * 4096
        ln = struct.unpack_from(">I", raw, p)[0]; comp = raw[p + 4]
        body = raw[p + 5:p + 4 + ln]
        if comp & 0x80: continue  # внешний .mcc — редко, пропускаем
        try:
            data = zlib.decompress(body) if comp == 2 else gzip.decompress(body) if comp == 1 else body
            yield i & 31, i >> 5, read_nbt(data)
        except Exception:
            continue

def unpack(longs, bits, count):
    """Упакованный массив Minecraft 1.16+: значения не переходят границу long."""
    longs = np.asarray(longs).astype(np.uint64)
    per = 64 // bits
    idx = np.arange(count)
    li = idx // per; sh = ((idx % per) * bits).astype(np.uint64)
    return ((longs[li] >> sh) & np.uint64((1 << bits) - 1)).astype(np.int32)

# ---------- цвета ----------
C = {
 "grass_block": (110, 152, 64), "dirt": (134, 96, 67), "coarse_dirt": (119, 85, 59), "rooted_dirt": (144, 103, 76),
 "podzol": (106, 76, 40), "mycelium": (111, 99, 105), "dirt_path": (148, 122, 65), "farmland": (110, 75, 45), "mud": (60, 57, 61),
 "sand": (219, 207, 163), "red_sand": (190, 102, 33), "sandstone": (216, 203, 155), "red_sandstone": (186, 99, 29), "gravel": (131, 127, 126),
 "suspicious_sand": (219, 207, 163), "clay": (160, 166, 179),
 "stone": (125, 125, 125), "cobblestone": (122, 122, 122), "mossy_cobblestone": (110, 118, 94), "andesite": (136, 136, 137), "diorite": (188, 188, 188), "granite": (149, 103, 85),
 "tuff": (108, 109, 102), "calcite": (223, 224, 220), "deepslate": (80, 80, 82), "dripstone_block": (134, 107, 92), "smooth_basalt": (72, 72, 78),
 "snow": (249, 254, 254), "snow_block": (249, 254, 254), "powder_snow": (248, 253, 253), "ice": (145, 183, 253), "packed_ice": (141, 180, 250), "blue_ice": (116, 167, 253),
 "water": (52, 94, 200), "lava": (207, 92, 20), "bubble_column": (52, 94, 200), "kelp": (52, 94, 200), "kelp_plant": (52, 94, 200), "seagrass": (52, 94, 200), "tall_seagrass": (52, 94, 200),
 "terracotta": (152, 94, 67), "white_terracotta": (209, 178, 161), "orange_terracotta": (161, 83, 37), "yellow_terracotta": (186, 133, 35),
 "brown_terracotta": (77, 51, 35), "red_terracotta": (143, 61, 46), "light_gray_terracotta": (135, 106, 97),
 "moss_block": (89, 109, 45), "moss_carpet": (89, 109, 45), "pale_moss_block": (106, 112, 104), "pale_moss_carpet": (106, 112, 104),
 "obsidian": (20, 18, 30), "magma_block": (142, 63, 31), "netherrack": (97, 38, 38), "bedrock": (85, 85, 85),
 "pumpkin": (198, 118, 24), "melon": (111, 145, 30), "cactus": (85, 127, 43), "sugar_cane": (148, 192, 101), "bamboo": (94, 143, 40),
 "hay_block": (166, 136, 38), "bricks": (150, 97, 83), "stone_bricks": (122, 121, 122), "mud_bricks": (137, 103, 79),
 "prismarine": (99, 156, 151), "copper_block": (192, 107, 79), "oxidized_copper": (82, 162, 132), "amethyst_block": (133, 97, 191),
 "sculk": (13, 30, 36), "mangrove_roots": (74, 59, 38), "muddy_mangrove_roots": (68, 58, 50),
}
LEAF = {"oak_leaves": (60, 110, 32), "birch_leaves": (110, 140, 70), "spruce_leaves": (55, 84, 55), "jungle_leaves": (48, 120, 20),
        "acacia_leaves": (90, 120, 30), "dark_oak_leaves": (44, 88, 22), "mangrove_leaves": (68, 112, 30), "azalea_leaves": (90, 120, 45),
        "flowering_azalea_leaves": (110, 120, 70), "cherry_leaves": (229, 172, 194), "pale_oak_leaves": (160, 168, 158)}
C.update(LEAF)
WATERLIKE = {"water", "bubble_column", "kelp", "kelp_plant", "seagrass", "tall_seagrass"}
SKIP = ("air", "cave_air", "void_air", "light", "barrier", "structure_void")

_cache = {}
def color_of(name):
    n = name.split(":")[-1]
    if n in _cache: return _cache[n]
    c = C.get(n)
    if c is None:
        for k, v in (("leaves", (60, 105, 35)), ("log", (102, 81, 51)), ("wood", (102, 81, 51)), ("planks", (162, 130, 78)),
                     ("stairs", (140, 120, 95)), ("slab", (140, 120, 95)), ("wall", (120, 120, 120)), ("fence", (150, 120, 80)),
                     ("glass", (175, 210, 220)), ("wool", (220, 220, 220)), ("carpet", (200, 190, 170)), ("concrete", (180, 180, 180)),
                     ("terracotta", (152, 94, 67)), ("ore", (125, 125, 125)), ("copper", (160, 110, 80)), ("snow", (249, 254, 254)),
                     ("sand", (219, 207, 163)), ("stone", (125, 125, 125)), ("brick", (140, 100, 90)), ("coral", (190, 90, 120)),
                     ("grass", (100, 150, 55)), ("fern", (90, 140, 50)), ("flower", (110, 150, 60)), ("bush", (80, 130, 45)),
                     ("mushroom", (150, 110, 90)), ("vine", (60, 110, 30)), ("roots", (100, 80, 55)), ("ice", (145, 183, 253))):
            if k in n: c = v; break
    _cache[n] = c or (120, 140, 90)
    return _cache[n]

# грубые группы биомов для слоя погоды
def biome_group(b):
    b = b.split(":")[-1]
    if "ocean" in b or b in ("deep_ocean",): return "ocean"
    if any(k in b for k in ("desert", "badlands", "dune", "mesa", "sand", "arid", "canyon")): return "desert"
    if "savanna" in b or "steppe" in b or "shrub" in b: return "dry"
    if any(k in b for k in ("peak", "summit", "alpine", "glacier", "jagged", "frozen", "snow", "ice", "tundra", "cold")): return "snow"
    if any(k in b for k in ("jungle", "swamp", "mangrove", "bayou", "rainforest", "tropic")): return "wet"
    if any(k in b for k in ("mountain", "highland", "cliff", "crag", "rocky", "stony", "scarp", "plateau", "hills")): return "high"
    if "river" in b or "beach" in b or "shore" in b or "lake" in b: return "coast"
    return "land"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("region"); ap.add_argument("--radius", type=int, default=2048)
    ap.add_argument("--out", default=os.path.join(ROOT, "content"))
    a = ap.parse_args()
    R = a.radius; N = 2 * R
    rgb = np.zeros((N, N, 3), np.float32); rgb[:] = (24, 26, 30)
    height = np.full((N, N), np.nan, np.float32)
    wdepth = np.zeros((N, N), np.float32)
    have = np.zeros((N, N), bool)
    bgrid = {}  # (x//64, z//64) -> {group: count}
    rmin, rmax = (-R) >> 9, (R - 1) >> 9
    files = 0
    for rx in range(rmin, rmax + 1):
        for rz in range(rmin, rmax + 1):
            p = os.path.join(a.region, f"r.{rx}.{rz}.mca")
            if not os.path.exists(p): continue
            files += 1
            for cx, cz, ch in region_chunks(p):
                gx = (rx * 32 + cx) * 16 + R; gz = (rz * 32 + cz) * 16 + R
                if gx < 0 or gz < 0 or gx >= N or gz >= N: continue
                if ch.get("Status", "").split(":")[-1] not in ("full", "spawn", "heightmaps", "light", "initialize_light", "features"): continue
                hm = ch.get("Heightmaps", {})
                if "WORLD_SURFACE" not in hm: continue
                ws = unpack(hm["WORLD_SURFACE"], 9, 256).reshape(16, 16) + MIN_Y - 1  # [z][x] y верхнего блока
                of = unpack(hm["OCEAN_FLOOR"], 9, 256).reshape(16, 16) + MIN_Y - 1 if "OCEAN_FLOOR" in hm else ws
                secs = {}
                for s in ch.get("sections", []):
                    bs = s.get("block_states")
                    if not bs: continue
                    pal = [e.get("Name", "minecraft:air") for e in bs.get("palette", [])]
                    if "data" in bs and len(pal) > 1:
                        bits = max(4, (len(pal) - 1).bit_length())
                        arr = unpack(bs["data"], bits, 4096)
                    else:
                        arr = np.zeros(4096, np.int32)
                    bio = s.get("biomes", {})
                    secs[s["Y"]] = (pal, arr, bio)
                tile = np.zeros((16, 16, 3), np.float32)
                th = np.zeros((16, 16), np.float32); twd = np.zeros((16, 16), np.float32)
                for z in range(16):
                    for x in range(16):
                        y = int(ws[z, x]); name = "minecraft:air"
                        for _ in range(40):  # прозрачное (трава, цветы, стекло) пропускаем вниз
                            sec = secs.get(y >> 4)
                            if sec is None: y -= 1; continue
                            pal, arr, _b = sec
                            name = pal[arr[((y & 15) << 8) | (z << 4) | x]]
                            n = name.split(":")[-1]
                            if n.endswith(SKIP): y -= 1; continue
                            break
                        n = name.split(":")[-1]
                        tile[z, x] = color_of(name)
                        th[z, x] = y
                        if n in WATERLIKE: twd[z, x] = max(1, y - int(of[z, x]))
                        elif n.endswith(("_grass", "fern", "flower", "tulip", "poppy", "dandelion", "orchid", "allium", "bluet", "daisy")) or n in ("short_grass", "tall_grass"):
                            # трава поверх блока: цвет почвы, высота блока ниже
                            th[z, x] = y - 1
                # биом в центре чанка на поверхности + доля воды и вершин выше Y 110
                yc = int(ws[8, 8]); sec = secs.get(yc >> 4); grp = "land"
                if sec and sec[2].get("palette"):
                    bp = sec[2]["palette"]
                    if len(bp) > 1 and "data" in sec[2]:
                        bb = unpack(sec[2]["data"], max(1, (len(bp) - 1).bit_length()), 64)
                        bname = bp[bb[(((yc & 15) >> 2) << 4) | (2 << 2) | 2]]
                    else: bname = bp[0]
                    grp = biome_group(bname)
                k = ((gx - R) // 64, (gz - R) // 64)
                d = bgrid.setdefault(k, {"n": 0, "water": 0.0, "peak": 0.0})
                d["n"] += 1; d[grp] = d.get(grp, 0) + 1
                d["water"] += float((twd > 0).mean()); d["peak"] += float((th > 110).mean())
                rgb[gz:gz + 16, gx:gx + 16] = tile; height[gz:gz + 16, gx:gx + 16] = th
                wdepth[gz:gz + 16, gx:gx + 16] = twd; have[gz:gz + 16, gx:gx + 16] = True
            print(f"r.{rx}.{rz}.mca", file=sys.stderr)
    if not files: sys.exit(f"В {a.region} нет файлов r.X.Z.mca для радиуса {R}")
    # затенение рельефа: свет с северо-запада
    h = np.where(np.isnan(height), 62, height)
    dz = np.zeros_like(h); dz[1:, 1:] = h[1:, 1:] - (h[:-1, 1:] + h[1:, :-1]) / 2
    shade = np.clip(1 + dz * 0.09, 0.62, 1.32)
    water = wdepth > 0
    shade[water] = 1.0
    deep = np.clip(wdepth / 28, 0, 1)[..., None]
    out = rgb * shade[..., None]
    out = np.where(water[..., None], rgb * (1.05 - 0.55 * deep) + np.array([0, 6, 20]) * deep, out)
    # лёгкий тон по высоте: низины темнее, вершины светлее
    tone = np.clip(1 + (h - 64) / 900, 0.9, 1.15)
    out = np.where(water[..., None], out, out * tone[..., None])
    out[~have] = (24, 26, 30)
    # обрезаем до прогруженной области (кратно 16 блокам)
    zs, xs = np.where(have)
    x0, x1 = xs.min() // 16 * 16, (xs.max() // 16 + 1) * 16
    z0, z1 = zs.min() // 16 * 16, (zs.max() // 16 + 1) * 16
    out = out[z0:z1, x0:x1]
    bounds = [int(x0 - R), int(z0 - R), int(x1 - R), int(z1 - R)]
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")
    os.makedirs(a.out, exist_ok=True)
    img.save(os.path.join(a.out, "world_map_big.webp"), quality=85, method=6)
    w, hh = img.size
    small = img if max(w, hh) <= 2048 else img.resize((w // 2, hh // 2), Image.LANCZOS)
    small.save(os.path.join(a.out, "world_map.webp"), quality=85, method=6)
    # зоны 64×64 для погоды: пустыни (песчаная буря, засуха), вода (наводнение), вершины выше Y 110 (гроза), снег (метель)
    zones = {"desert": [], "water": [], "peaks": [], "snow": []}
    for (bx, bz), d in sorted(bgrid.items()):
        n = d["n"]; c = [bx * 64, bz * 64]
        if (d.get("desert", 0) + d.get("dry", 0) * 0.3) / n >= 0.5: zones["desert"].append(c)
        if d["water"] / n >= 0.55: zones["water"].append(c)
        if d["peak"] / n >= 0.35: zones["peaks"].append(c)
        if d.get("snow", 0) / n >= 0.5: zones["snow"].append(c)
    known = have.mean()
    import datetime
    json.dump({"radius": R, "bounds": bounds, "cell": 64, "generated": round(float(known), 3),
               "date": datetime.date.today().strftime("%d.%m.%Y"), "zones": zones}, open(os.path.join(a.out, "world_zones.json"), "w"), separators=(",", ":"))
    print(f"Готово: {files} регионов, прогружено {known:.0%} квадрата ±{R}", file=sys.stderr)

if __name__ == "__main__":
    main()
