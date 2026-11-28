"""Патч interface/countrytechtreeview.gui из WA: ячейки (gridboxtype) под техи MD в папках Промышленность и Электроника.
Вход: исходный GUI WA, выход: патченый GUI. Запуск: python3 md_tree_gui.py SRC.gui OUT.gui"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import md_port as M

def patch(src):
    pos = M.tree_positions()
    lines = src.split("\n")
    for folder, (files, y0, cols) in M.LAYOUT.items():
        ids = [i for i, (f, x, y) in pos.items() if f == folder]
        start = next(i for i, l in enumerate(lines) if f'name = "{folder}"' in l)
        # size_filler: нарастить высоту
        sf = next(i for i in range(start, len(lines)) if "size_filler" in lines[i])
        wl = next(i for i in range(sf, sf + 8) if "width =" in lines[i] and "height =" in lines[i])
        m = re.search(r"width = (\d+) height = (\d+)", lines[wl])
        rows = (len(ids) + cols - 1) // cols
        lines[wl] = lines[wl].replace(m.group(0), f"width = {m.group(1)} height = {max(int(m.group(2)), y0 + rows * M.GRID_Y + 80)}")
        gb = next(i for i in range(sf, len(lines)) if "gridboxtype = {" in lines[i])
        boxes = ['\t\t\tinstantTextBoxType = {\n\t\t\t\tname = "pax_md_title"\n\t\t\t\tposition = { x = 100 y = %d }\n\t\t\t\ttextureFile = ""\n\t\t\t\tfont = "hoi_36header"\n\t\t\t\tborderSize = { x = 0 y = 4 }\n\t\t\t\ttext = "PAX_MD_TREE_TITLE"\n\t\t\t\tmaxWidth = 500\n\t\t\t\tmaxHeight = 40\n\t\t\t\tformat = left\n\t\t\t\tOrientation = "UPPER_LEFT"\n\t\t\t}\n' % (y0 - 60)]
        for i in sorted(ids):
            _, x, y = pos[i]
            boxes.append(f'\t\t\tgridboxtype = {{\n\t\t\t\tname = "{i}_tree"\n\t\t\t\tposition = {{ x = {x} y = {y} }}\n\t\t\t\tsize = {{ width = 72 height = 72 }}\n\t\t\t\tslotsize = {{ width = 70 height = 70 }}\n\t\t\t\tformat = "UP"\n\t\t\t}}\n')
        lines[gb:gb] = ["".join(boxes).rstrip("\n")]
    return "\n".join(lines)

if __name__ == "__main__":
    s = open(sys.argv[1], encoding="utf-8-sig", newline="").read()
    open(sys.argv[2], "w", encoding="utf-8-sig", newline="").write(patch(s))
