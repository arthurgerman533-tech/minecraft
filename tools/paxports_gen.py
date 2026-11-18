import gzip
import os
import struct
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATAPACKS = ROOT / "server" / "world" / "datapacks"
SOURCE = DATAPACKS / "datapacks" / "data" / "paxports"
PORTS = SOURCE / "structure" / "port"
ARCHIVE = DATAPACKS / "PaxVanila_Ports.zip"


class Tag:
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value


def parse_nbt(data):
    offset = 0

    def take(size):
        nonlocal offset
        result = data[offset:offset + size]
        if len(result) != size:
            raise ValueError("Truncated NBT")
        offset += size
        return result

    def u8():
        return take(1)[0]

    def u16():
        return struct.unpack(">H", take(2))[0]

    def i32():
        return struct.unpack(">i", take(4))[0]

    def i64():
        return struct.unpack(">q", take(8))[0]

    def string():
        return take(u16()).decode("utf-8")

    def payload(kind):
        if kind == 1:
            return struct.unpack(">b", take(1))[0]
        if kind == 2:
            return struct.unpack(">h", take(2))[0]
        if kind == 3:
            return i32()
        if kind == 4:
            return i64()
        if kind == 5:
            return struct.unpack(">f", take(4))[0]
        if kind == 6:
            return struct.unpack(">d", take(8))[0]
        if kind == 7:
            return take(i32())
        if kind == 8:
            return string()
        if kind == 9:
            element_kind, count = u8(), i32()
            return element_kind, [payload(element_kind) for _ in range(count)]
        if kind == 10:
            result = {}
            while True:
                child_kind = u8()
                if child_kind == 0:
                    return result
                child_name = string()
                result[child_name] = Tag(child_kind, payload(child_kind))
        if kind == 11:
            return [i32() for _ in range(i32())]
        if kind == 12:
            return [i64() for _ in range(i32())]
        raise ValueError("Unsupported NBT tag: %s" % kind)

    root_kind, root_name = u8(), string()
    if root_kind != 10:
        raise ValueError("NBT root must be a compound")
    return root_name, payload(root_kind)


def encode_nbt(root_name, root):
    output = bytearray()

    def put_string(value):
        encoded = value.encode("utf-8")
        output.extend(struct.pack(">H", len(encoded)))
        output.extend(encoded)

    def put(kind, value):
        if kind == 1:
            output.extend(struct.pack(">b", value))
        elif kind == 2:
            output.extend(struct.pack(">h", value))
        elif kind == 3:
            output.extend(struct.pack(">i", value))
        elif kind == 4:
            output.extend(struct.pack(">q", value))
        elif kind == 5:
            output.extend(struct.pack(">f", value))
        elif kind == 6:
            output.extend(struct.pack(">d", value))
        elif kind == 7:
            output.extend(struct.pack(">i", len(value)))
            output.extend(value)
        elif kind == 8:
            put_string(value)
        elif kind == 9:
            element_kind, values = value
            output.extend(struct.pack(">Bi", element_kind, len(values)))
            for item in values:
                put(element_kind, item)
        elif kind == 10:
            for key, child in value.items():
                output.append(child.kind)
                put_string(key)
                put(child.kind, child.value)
            output.append(0)
        elif kind == 11:
            output.extend(struct.pack(">i", len(value)))
            for item in value:
                output.extend(struct.pack(">i", item))
        elif kind == 12:
            output.extend(struct.pack(">i", len(value)))
            for item in value:
                output.extend(struct.pack(">q", item))
        else:
            raise ValueError("Unsupported NBT tag: %s" % kind)

    output.append(10)
    put_string(root_name)
    put(10, root)
    return gzip.compress(bytes(output), mtime=0)


def compound(fields):
    return {key: Tag(kind, value) for key, kind, value in fields}


def add_block(root, palette, name, x, y, z, properties=None):
    properties = properties or {}
    state_id = None
    for index, state in enumerate(palette):
        if state["Name"].value != name:
            continue
        state_properties = state.get("Properties")
        state_properties = (
            {key: value.value for key, value in state_properties.value.items()}
            if state_properties else {}
        )
        if state_properties == properties:
            state_id = index
            break
    if state_id is None:
        fields = [("Name", 8, name)]
        if properties:
            fields.append((
                "Properties", 10,
                compound([(key, 8, value) for key, value in properties.items()]),
            ))
        palette.append(compound(fields))
        state_id = len(palette) - 1
    root["blocks"].value[1].append(compound([
        ("state", 3, state_id),
        ("pos", 9, (3, [x, y, z])),
    ]))


def add_ship(root, palette, ship):
    x0 = ship["x"]
    center_z = ship["z"]
    length = ship["length"]
    max_width = ship["width"]
    widths = [
        min(max_width, 1 + 2 * min(index, length - 1 - index))
        for index in range(length)
    ]
    for index, width in enumerate(widths):
        x = x0 + index
        lower_width = max(1, width - 2)
        for z in range(center_z - lower_width // 2, center_z + lower_width // 2 + 1):
            add_block(root, palette, ship["hull"], x, 4, z)
        for z in range(center_z - width // 2, center_z + width // 2 + 1):
            add_block(root, palette, ship["hull"], x, 5, z)
            add_block(root, palette, ship["timber"], x, 6, z)
    for index in range(1, length - 1):
        width = widths[index]
        for z in (center_z - width // 2, center_z + width // 2):
            add_block(root, palette, ship["fence"], x0 + index, 7, z)

    add_block(
        root, palette, "minecraft:barrel", x0 + 2, 7, center_z,
        {"facing": "north", "open": "false"},
    )
    mast_x = x0 + length // 2
    for y in range(7, 7 + ship["height"]):
        add_block(root, palette, ship["mast"], mast_x, y, center_z)
    sail_half_width = max(1, min(3, (max_width - 1) // 2))
    for y in range(8, 7 + ship["height"]):
        for x in range(mast_x - sail_half_width, mast_x + sail_half_width + 1):
            add_block(root, palette, ship["sail"], x, y, center_z + 1)
    return x0 + length - 1


def build_variant(source, output, original_size, ships, gangways):
    root_name, root = parse_nbt(gzip.decompress(source))
    palette = root["palette"].value[1]
    for x_start, x_end, z in gangways:
        for x in range(x_start, x_end + 1):
            add_block(root, palette, "minecraft:spruce_planks", x, 6, z)
    max_x = original_size[0] - 1
    for ship in ships:
        max_x = max(max_x, add_ship(root, palette, ship))
    size = [max_x + 1, original_size[1], original_size[2]]
    root["size"] = Tag(9, (3, size))
    result = encode_nbt(root_name, root)
    check_name, check = parse_nbt(gzip.decompress(result))
    if check_name != root_name or check["size"].value[1] != size:
        raise ValueError("Generated structure failed its NBT validation")
    output.write_bytes(result)
    return size, len(root["blocks"].value[1])


def ship(materials, x, z, length, width, height):
    return {
        "timber": materials[0],
        "hull": materials[1],
        "mast": materials[2],
        "fence": materials[3],
        "sail": materials[4],
        "x": x,
        "z": z,
        "length": length,
        "width": width,
        "height": height,
    }


WOOD = (
    "minecraft:spruce_planks", "minecraft:oak_planks",
    "minecraft:spruce_log", "minecraft:spruce_fence", "minecraft:white_wool",
)
TRADER = (
    "minecraft:dark_oak_planks", "minecraft:spruce_planks",
    "minecraft:spruce_log", "minecraft:dark_oak_fence", "minecraft:light_gray_wool",
)
COPPER = (
    "minecraft:dark_oak_planks", "minecraft:cut_copper",
    "minecraft:spruce_log", "minecraft:dark_oak_fence", "minecraft:light_gray_wool",
)
IRON = (
    "minecraft:dark_oak_planks", "minecraft:iron_block",
    "minecraft:iron_bars", "minecraft:iron_bars", "minecraft:gray_wool",
)

VARIANTS = {
    "harbor_skiff": ([ship(WOOD, 48, 23, 10, 3, 3)], [(47, 47, 23)]),
    "harbor_trader": ([ship(TRADER, 48, 23, 15, 5, 4)], [(47, 47, 23)]),
    "harbor_trade_caravan": ([
        ship(WOOD, 48, 17, 11, 3, 3),
        ship(TRADER, 48, 23, 14, 5, 4),
        ship(WOOD, 48, 29, 11, 3, 3),
    ], [(32, 47, 17), (47, 47, 23), (32, 47, 29)]),
    "harbor_copper_ship": ([ship(COPPER, 48, 23, 18, 7, 5)], [(47, 47, 23)]),
    "harbor_iron_ship": ([ship(IRON, 48, 23, 21, 9, 5)], [(47, 47, 23)]),
    "river_skiff": ([ship(WOOD, 30, 14, 8, 3, 2)], [(29, 29, 14)]),
    "river_trader": ([ship(TRADER, 30, 14, 12, 5, 3)], [(29, 29, 14)]),
    "river_trade_caravan": ([
        ship(WOOD, 30, 12, 9, 3, 2),
        ship(TRADER, 30, 16, 9, 3, 2),
    ], [(29, 29, 12), (29, 29, 16)]),
}


def update_archive():
    replacements = {}
    for path in SOURCE.rglob("*"):
        if path.is_file():
            replacements[path.relative_to(DATAPACKS / "datapacks").as_posix()] = path.read_bytes()
    fd, temp_path = tempfile.mkstemp(suffix=".zip", dir=str(DATAPACKS))
    os.close(fd)
    try:
        with zipfile.ZipFile(ARCHIVE, "r") as source, zipfile.ZipFile(
            temp_path, "w", zipfile.ZIP_DEFLATED
        ) as target:
            for entry in source.infolist():
                if entry.filename not in replacements:
                    target.writestr(entry, source.read(entry.filename))
            for name, content in replacements.items():
                target.writestr(name, content)
        with zipfile.ZipFile(temp_path, "r") as check:
            bad_entry = check.testzip()
            if bad_entry:
                raise ValueError("Corrupt archive entry: " + bad_entry)
            for name in VARIANTS:
                structure = "data/paxports/structure/port/" + name + ".nbt"
                parse_nbt(gzip.decompress(check.read(structure)))
        os.replace(temp_path, ARCHIVE)
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def main():
    harbor = (PORTS / "harbor.nbt").read_bytes()
    river = (PORTS / "river_landing.nbt").read_bytes()
    original = {
        "harbor_": (harbor, [47, 32, 47]),
        "river_": (river, [29, 20, 29]),
    }
    for name, (ships, gangways) in VARIANTS.items():
        prefix = "harbor_" if name.startswith("harbor_") else "river_"
        source, size = original[prefix]
        dims, blocks = build_variant(source, PORTS / (name + ".nbt"), size, ships, gangways)
        print("%s: size=%s blocks=%s" % (name, dims, blocks))
    update_archive()
    print("Updated %s" % ARCHIVE)


if __name__ == "__main__":
    main()
