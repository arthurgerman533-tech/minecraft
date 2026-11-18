# Генератор датапака PaxVanila_Tower (башня новичков в 0,0).
# Запуск:  python tools/paxtower_gen.py
# Результат: server/world/datapacks/PaxVanila_Tower.zip
# Высоту башни выбирает Skript (server/plugins/Skript/scripts/paxtower.sk) прямо на сервере:
# он меряет рельеф вокруг 0,0 и вызывает функции этого датапака послойно.

import json, math, os, random, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "server", "world", "datapacks", "PaxVanila_Tower.zip")
NS = "paxtower"
rng = random.Random(20261116)

R_IN = 5.5       # внутренняя пустота (d <= R_IN)
R_OUT = 7.5      # внешний край стены
R_PILLAR = 1.5   # центральный столб 3x3
R_PLAZA = 12.5
R_FOUND = 9.5
STAIR_PERIOD = 24          # слоёв на один оборот лестницы
SECTOR = 360 / STAIR_PERIOD


def d(x, z):
    return math.hypot(x, z)


def ang(x, z):
    return math.degrees(math.atan2(z, x)) % 360


def cells(rmax, rmin=-1.0):
    n = int(math.ceil(rmax))
    for x in range(-n, n + 1):
        for z in range(-n, n + 1):
            dd = d(x, z)
            if rmin < dd <= rmax:
                yield x, z


def pick(weights):
    tot = sum(w for _, w in weights)
    r = rng.uniform(0, tot)
    for b, w in weights:
        r -= w
        if r <= 0:
            return b
    return weights[-1][0]


def sb(x, z, block, y=0, mode=""):
    return f"setblock ~{x} ~{y} ~{z} minecraft:{block}{(' ' + mode) if mode else ''}"


files = {}


def fn(path, lines):
    files[f"data/{NS}/function/{path}.mcfunction"] = "\n".join(lines) + "\n"


fn("starter_cache", [
    "setblock ~0 ~1 ~-10 minecraft:barrel[facing=north]",
    "item replace block ~0 ~1 ~-10 container.0 with minecraft:stone_spear",
    "item replace block ~0 ~1 ~-10 container.1 with minecraft:stone_axe",
    "item replace block ~0 ~1 ~-10 container.2 with minecraft:cooked_cod 4",
    "item replace block ~0 ~1 ~-10 container.3 with minecraft:string 8",
    "item replace block ~0 ~1 ~-10 container.4 with minecraft:lead[minecraft:custom_name='{\"text\":\"Морской канат\",\"italic\":false}'] 2",
    "item replace block ~0 ~1 ~-10 container.5 with minecraft:fishing_rod",
    "item replace block ~0 ~1 ~-10 container.6 with minecraft:kelp 8",
    "item replace block ~0 ~1 ~-10 container.7 with minecraft:nautilus_shell",
    "item replace block ~0 ~1 ~-10 container.8 with minecraft:torch 16",
])


WALL_CELLS = list(cells(R_OUT, R_IN))
INNER_CELLS = list(cells(R_IN))
BAND_CELLS = list(cells(R_IN, R_PILLAR))
PILLAR_CELLS = list(cells(R_PILLAR))

MAT_LOW = [("mossy_stone_bricks", 32), ("stone_bricks", 26), ("cracked_stone_bricks", 14),
           ("mossy_cobblestone", 14), ("cobblestone", 8), ("andesite", 4), ("moss_block", 2)]
MAT_MID = [("stone_bricks", 46), ("cracked_stone_bricks", 22), ("mossy_stone_bricks", 17),
           ("cobblestone", 6), ("mossy_cobblestone", 4), ("andesite", 3), ("tuff_bricks", 2)]
MAT_TOP = [("stone_bricks", 36), ("cracked_stone_bricks", 32), ("mossy_stone_bricks", 14),
           ("cobblestone", 12), ("mossy_cobblestone", 6)]


def wall_variant(mats, hole):
    out = []
    for x, z in WALL_CELLS:
        if rng.random() < hole:
            out.append(sb(x, z, "air"))
        else:
            out.append(sb(x, z, pick(mats)))
    return out


for i in range(4):
    fn(f"wall/l{i}", wall_variant(MAT_LOW, 0.0))
for i in range(6):
    fn(f"wall/m{i}", wall_variant(MAT_MID, 0.015))
for i in range(4):
    fn(f"wall/t{i}", wall_variant(MAT_TOP, 0.07))

# Внутренность: воздух (построчно fill)
def rows(rmax, rmin_excl=None):
    n = int(math.ceil(rmax))
    for x in range(-n, n + 1):
        zs = [z for z in range(-n, n + 1) if d(x, z) <= rmax]
        if zs:
            yield x, min(zs), max(zs)


fn("interior", [f"fill ~{x} ~ ~{z0} ~{x} ~ ~{z1} minecraft:air" for x, z0, z1 in rows(R_IN)])
fn("clear", [f"fill ~{x} ~ ~{z0} ~{x} ~ ~{z1} minecraft:air" for x, z0, z1 in rows(R_PLAZA)])

PILLAR_MAT = [("stone_bricks", 50), ("mossy_stone_bricks", 20), ("cracked_stone_bricks", 18),
              ("polished_andesite", 7), ("chiseled_stone_bricks", 5)]
for i in range(3):
    fn(f"pillar/p{i}", [sb(x, z, pick(PILLAR_MAT)) for x, z in PILLAR_CELLS])


def in_sector(a, k, lo=-4.0, hi=19.0):
    base = k * SECTOR
    rel = (a - base) % 360
    if rel > 300:
        rel -= 360
    return lo <= rel < hi


def stair_cells(k):
    res = []
    for x, z in BAND_CELLS:
        a = ang(x, z)
        if in_sector(a, k):
            rel = (a - k * SECTOR) % 360
            if rel > 300:
                rel -= 360
            res.append((x, z, "bottom" if rel < 7.5 else "top"))
    return res


SLAB = [("stone_brick_slab", 60), ("mossy_stone_brick_slab", 25), ("cobblestone_slab", 15)]
for k in range(STAIR_PERIOD):
    sc = stair_cells(k)
    fn(f"stair/s{k}", [sb(x, z, f"{pick(SLAB)}[type={t}]") for x, z, t in sc])
    fn(f"hole/h{k}", [sb(x, z, "air") for x, z, _ in sc])

# Одна "стопка" слоя: стена + пустота + столб + ступень (макрос)
fn("layer", [
    "$function paxtower:wall/$(wall)",
    "function paxtower:interior",
    "$function paxtower:pillar/$(pillar)",
    "$function paxtower:stair/s$(stair)",
])

# Факелы на столбе (ставятся с противоположной от лестницы стороны)
fn("torch/e", [sb(2, 0, "wall_torch[facing=east]")])
fn("torch/s", [sb(0, 2, "wall_torch[facing=south]")])
fn("torch/w", [sb(-2, 0, "wall_torch[facing=west]")])
fn("torch/n", [sb(0, -2, "wall_torch[facing=north]")])

# Бойницы (2 блока высотой вызываются на y и y+1)
def slit(angles):
    out = []
    for x, z in WALL_CELLS:
        a = ang(x, z)
        for t in angles:
            diff = abs((a - t + 180) % 360 - 180)
            if diff < 5.5:
                out.append(sb(x, z, "air"))
    return out


fn("slit/a", slit([0, 90, 180, 270]))
fn("slit/b", slit([45, 135, 225, 315]))

# Пол первого этажа и площадь вокруг
FLOOR = [("stone_bricks", 45), ("mossy_stone_bricks", 20), ("cracked_stone_bricks", 20), ("cobblestone", 15)]
fn("floor", [sb(x, z, pick(FLOOR)) for x, z in cells(R_OUT)])
PLAZA = [("cobblestone", 20), ("mossy_cobblestone", 15), ("gravel", 14), ("coarse_dirt", 10),
         ("dirt_path", 10), ("moss_block", 10), ("stone_bricks", 10), ("cracked_stone_bricks", 6),
         ("andesite", 5)]
fn("plaza", [sb(x, z, pick(PLAZA)) for x, z in cells(R_PLAZA, R_OUT)])

FOUND = [("cobblestone", 45), ("stone", 30), ("mossy_cobblestone", 15), ("andesite", 10)]
for i in range(2):
    fn(f"foundation/f{i}", [
        f"fill ~{x} ~ ~{z} ~{x} ~ ~{z} minecraft:{pick(FOUND)} replace #minecraft:replaceable"
        for x, z in cells(R_FOUND)])

# Расширение основания (контрфорс) — 4 слоя
FLARE = [("mossy_cobblestone", 40), ("cobblestone", 25), ("mossy_stone_bricks", 25), ("stone", 10)]
for i, r in enumerate([9.4, 8.9, 8.4, 8.0]):
    lines = []
    for x, z in cells(r, R_OUT):
        if i == 3:
            lines.append(sb(x, z, f"{pick([('mossy_stone_brick_slab', 50), ('cobblestone_slab', 50)])}[type=bottom]"))
        elif rng.random() < 0.9:
            lines.append(sb(x, z, pick(FLARE)))
    fn(f"flare/r{i}", lines)

# Вход с юга (+Z): проём 3x4 + арка
fn("door", [sb(x, z, "air") for x in (-1, 0, 1) for z in range(5, 11)])
fn("door_top", [sb(0, z, "air") for z in range(5, 11)])

# Верхняя площадка
TOPF = [("stone_bricks", 40), ("cracked_stone_bricks", 25), ("mossy_stone_bricks", 20),
        ("cobblestone", 15)]
fn("top_floor", [sb(x, z, pick(TOPF)) for x, z in INNER_CELLS] + [sb(0, 0, "lantern", y=1)])

# Корона: сплошное кольцо, зубцы, обломки зубцов
def crown(level):
    out = []
    broken_side = rng.uniform(0, 360)
    for x, z in WALL_CELLS:
        a = ang(x, z)
        near_break = abs((a - broken_side + 180) % 360 - 180) < 35
        if level == 1:
            p = 0.08 + (0.35 if near_break else 0)
        else:
            if d(x, z) <= 6.5 or int(a // 20) % 2 == 1:
                continue
            p = (0.15 if level == 2 else 0.5) + (0.5 if near_break else 0)
        if rng.random() >= p:
            out.append(sb(x, z, pick(MAT_TOP)))
    return out


for lvl in (1, 2, 3):
    for i in range(2):
        fn(f"crown/c{lvl}_{i}", crown(lvl))

# Лианы: 12 наборов "прядей"
EXT = []
for x, z in cells(8.6, R_OUT):
    for dx, dz, face in ((1, 0, "east"), (-1, 0, "west"), (0, 1, "south"), (0, -1, "north")):
        if R_IN < d(x + dx, z + dz) <= R_OUT:
            EXT.append((x, z, face))
            break
EXT.sort(key=lambda c: ang(c[0], c[1]))
for j in range(12):
    start = rng.randrange(len(EXT))
    strand = [EXT[(start + o) % len(EXT)] for o in range(rng.randint(2, 4))]
    fn(f"vines/v{j}", [sb(x, z, f"vine[{face}=true]", mode="keep") for x, z, face in strand])

# Обломки у подножия
RUB = [("mossy_cobblestone", 30), ("cobblestone", 20), ("cracked_stone_bricks", 15),
       ("mossy_stone_brick_slab[type=bottom]", 15), ("moss_carpet", 20)]
rub = []
for x, z in cells(R_PLAZA, 8.2):
    if abs(x) <= 1 and z > 0:
        continue  # дорожка от входа
    if rng.random() < 0.14:
        rub.append(sb(x, z, pick(RUB), mode="keep"))
fn("rubble", rub)

files["pack.mcmeta"] = json.dumps({
    "pack": {
        "description": [{"text": "PaxVanila Tower", "color": "#3c8dbc"},
                        {"text": "\nБашня новичков в 0,0", "color": "gray"}],
        "min_format": 107, "max_format": 1000}
}, ensure_ascii=False, indent=2)

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
    for p, c in sorted(files.items()):
        zf.writestr(p, c)

total = sum(c.count("\n") for p, c in files.items() if p.endswith(".mcfunction"))
print(f"{OUT}: {len(files)} files, {total} commands")
print("wall cells/layer:", len(WALL_CELLS), "inner:", len(INNER_CELLS), "band:", len(BAND_CELLS))
print("stair cells per layer:", [len(stair_cells(k)) for k in range(STAIR_PERIOD)])

# ASCII-превью одного слоя (W стена, P столб, b/t ступени слоя 0 и 6)
if __name__ == "__main__":
    s0 = {(x, z): t for x, z, t in stair_cells(0)}
    for z in range(-9, 10):
        row = ""
        for x in range(-9, 10):
            c = "."
            if (x, z) in s0: c = s0[(x, z)][0]
            elif d(x, z) <= R_PILLAR: c = "P"
            elif R_IN < d(x, z) <= R_OUT: c = "W"
            elif R_OUT < d(x, z) <= 8.6: c = ","
            row += c
        print(row)
