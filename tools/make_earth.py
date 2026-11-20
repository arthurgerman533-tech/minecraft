#!/usr/bin/env python3
"""make_earth.py — карта настоящей Земли для сайта и приложения (content/earth.json).

    python3 tools/make_earth.py <land-10m.json из npm-пакета world-atlas>   (STEP=3 — шаг упрощения в км)

Берёт контуры суши Natural Earth 1:10m (общественное достояние), вырезает Европу,
Средиземноморье и Великую степь, переводит в километры (равнопромежуточная проекция,
параллель 48°) и упрощает до шага ~3 км. Державы PaxVanila ставит туда, где их
исторические прообразы: Рим, Карфаген, Афины, Алезия, Лондиний, Германия, Уппсала,
Сармизегетуза, Сарай, Неаполь Скифский.
"""
import json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LON0, LAT0 = 25.0, 48.0
BOX = (-14.0, 26.0, 62.0, 71.5)  # lon0, lat0, lon1, lat1
K = math.cos(math.radians(LAT0)) * 111.32

def proj(lon, lat):
    return round((lon - LON0) * K), round(-(lat - LAT0) * 111.32)

# державы → реальные места (lon, lat) и подпись прообраза
REAL = {
    "romea":    (12.48, 41.89, "Рим", "Rome"),
    "carthage": (10.32, 36.85, "Карфаген (Тунис)", "Carthage (Tunisia)"),
    "hellas":   (23.73, 37.98, "Афины и острова Эгейского моря", "Athens and the Aegean islands"),
    "gaul":     (4.50, 47.54, "Алезия, Галлия", "Alesia, Gaul"),
    "islands":  (-0.12, 51.51, "Лондиний, Британия", "Londinium, Britain"),
    "germany":  (9.0, 51.6, "Германия за Рейном", "Germania beyond the Rhine"),
    "north":    (17.64, 59.86, "Уппсала, Скандинавия", "Uppsala, Scandinavia"),
    "dacia":    (23.31, 45.62, "Сармизегетуза, Карпаты", "Sarmizegetusa, the Carpathians"),
    "horde":    (47.5, 47.6, "Сарай, Великая степь", "Sarai, the Great Steppe"),
    "scythia":  (34.1, 44.95, "Неаполь Скифский, Крым", "Scythian Neapolis, Crimea"),
}
SEAS = [
    (18.5, 34.0, "Средиземное море · Mare Nostrum", "Mediterranean · Mare Nostrum"),
    (35.5, 42.4, "Чёрное море · Понт Эвксинский", "Black Sea · Pontus Euxinus"),
    (19.5, 56.5, "Балтийское море", "Baltic Sea"),
    (3.5, 56.0, "Северное море", "North Sea"),
    (-10.0, 44.5, "Атлантический океан", "Atlantic Ocean"),
    (50.5, 42.0, "Каспийское море", "Caspian Sea"),
]

def clip(pts, x0, y0, x1, y1):
    def cut(pts, inside, inter):
        out = []
        for i, cur in enumerate(pts):
            prev = pts[i - 1]
            if inside(cur):
                if not inside(prev): out.append(inter(prev, cur))
                out.append(cur)
            elif inside(prev):
                out.append(inter(prev, cur))
        return out
    def ix(v):
        return lambda a, b: (v, a[1] + (b[1] - a[1]) * (v - a[0]) / (b[0] - a[0]))
    def iy(v):
        return lambda a, b: (a[0] + (b[0] - a[0]) * (v - a[1]) / (b[1] - a[1]), v)
    for inside, inter in ((lambda p: p[0] >= x0, ix(x0)), (lambda p: p[0] <= x1, ix(x1)),
                          (lambda p: p[1] >= y0, iy(y0)), (lambda p: p[1] <= y1, iy(y1))):
        if not pts: break
        pts = cut(pts, inside, inter)
    return pts

STEP = int(os.environ.get("STEP", "3"))  # шаг упрощения, км

def main():
    topo = json.load(open(sys.argv[1]))
    sx, sy = topo["transform"]["scale"]; tx, ty = topo["transform"]["translate"]
    arcs = []
    for a in topo["arcs"]:
        x = y = 0; pts = []
        for dx, dy in a:
            x += dx; y += dy; pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)
    def ring(ids):
        out = []
        for i in ids:
            p = arcs[i] if i >= 0 else arcs[~i][::-1]
            out.extend(p if not out else p[1:])
        return out
    geoms = topo["objects"]["land"]["geometries"]
    polys = []
    for g in geoms:
        for poly in (g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]):
            for r in poly:
                pts = ring(r)
                if any(x > 150 for x, _ in pts):  # Чукотка за линией перемены дат
                    pts = [(x + 360 if x < -150 else x, y) for x, y in pts]
                lo = [p[0] for p in pts]; la = [p[1] for p in pts]
                if max(lo) < BOX[0] - 3 or min(lo) > BOX[2] + 3 or max(la) < BOX[1] - 3 or min(la) > BOX[3] + 3:
                    continue
                # обрезка по рамке с запасом (Сазерленд — Ходжман), чтобы Азия и Африка не тянулись на весь мир
                pts = clip(pts, BOX[0] - 2, BOX[1] - 2, BOX[2] + 2, BOX[3] + 2)
                if len(pts) < 3: continue
                q = []
                for lon, lat in pts:
                    x, y = proj(lon, lat)
                    if not q or abs(x - q[-1][0]) + abs(y - q[-1][1]) >= STEP:
                        q.append((x, y))
                if len(q) >= 4:
                    polys.append([c for p in q for c in p])
    rivers, lakes = [], []
    if len(sys.argv) > 2:  # реки и озёра: world_50m.json из npm-пакета sane-topojson
        T = json.load(open(sys.argv[2]))
        tsx, tsy = T["transform"]["scale"]; ttx, tty = T["transform"]["translate"]
        tarcs = []
        for a in T["arcs"]:
            x = y = 0; pts = []
            for dx, dy in a:
                x += dx; y += dy; pts.append((x * tsx + ttx, y * tsy + tty))
            tarcs.append(pts)
        tarc = lambda i: tarcs[i] if i >= 0 else tarcs[~i][::-1]
        inb = lambda lo, la: BOX[0] - 1 <= lo <= BOX[2] + 1 and BOX[1] - 1 <= la <= BOX[3] + 1
        def simp(pts, step):
            q = []
            for lon, lat in pts:
                x, y = proj(lon, lat)
                if not q or abs(x - q[-1][0]) + abs(y - q[-1][1]) >= step: q.append((x, y))
            return q
        for g in T["objects"]["rivers"]["geometries"]:
            lines = g["arcs"] if g["type"] == "MultiLineString" else [g["arcs"]]
            for ln in lines:
                pts = [p for i in ln for p in tarc(i)]
                seg = []
                for lo, la in pts + [(999, 999)]:
                    if inb(lo, la): seg.append((lo, la)); continue
                    q = simp(seg, STEP)
                    if len(q) >= 2: rivers.append([c for p in q for c in p])
                    seg = []
        for g in T["objects"]["lakes"]["geometries"]:
            for poly in (g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]):
                pts = [p for i in poly[0] for p in tarc(i)]
                if not all(inb(lo, la) for lo, la in pts): continue
                q = simp(pts, STEP)
                if len(q) >= 4: lakes.append([c for p in q for c in p])
    x0, y1 = proj(BOX[0], BOX[1]); x1, y0 = proj(BOX[2], BOX[3])
    M = json.load(open(os.path.join(ROOT, "content", "map.json"), encoding="utf-8"))
    powers = []
    for p in M["powers"]:
        if p["id"] not in REAL: continue
        lon, lat, ru, en = REAL[p["id"]]; x, y = proj(lon, lat)
        powers.append({"id": p["id"], "x": x, "y": y, "lon": lon, "lat": lat, "real": {"ru": ru, "en": en}})
    seas = [{"x": proj(a, b)[0], "y": proj(a, b)[1], "name": {"ru": ru, "en": en}} for a, b, ru, en in SEAS]
    out = {"_comment": "Сгенерировано tools/make_earth.py из Natural Earth 1:10m (world-atlas). Единица = 1 км, центр 25°E 48°N.",
           "box": [x0, y0, x1, y1], "lon0": LON0, "lat0": LAT0, "land": polys, "fill": "evenodd", "rivers": rivers, "lakes": lakes, "powers": powers, "seas": seas}
    json.dump(out, open(os.path.join(ROOT, "content", "earth.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"{len(rivers)} рек, {len(lakes)} озёр, {len(polys)} контуров, {sum(len(p) for p in polys)//2} точек, box {out['box']}")

if __name__ == "__main__":
    main()
