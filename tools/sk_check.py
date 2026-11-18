#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sk_check.py — быстрая проверка скриптов Skript PaxVanila без запуска сервера.

Запуск (из папки "Minecraft Разработка"):
    python tools/sk_check.py
    python tools/sk_check.py server/plugins/Skript/scripts      # другая папка
    python tools/sk_check.py --vars                              # + отчёт по общим переменным

Что ловит (то, на чём Skript молча не грузит скрипт или ведёт себя не так):
  * смешанные табы и пробелы в отступах одного файла;
  * скачок отступа больше чем на один уровень;
  * строку, заканчивающуюся двоеточием, без вложенного блока;
  * нечётное число кавычек в строке (незакрытая строка);
  * нечётное число % внутри строки в кавычках (сломанная вставка %выражение%; %% — норм);
  * несбалансированные { } и ( ) в строке;
  * одинаковые имена функций и команд в разных файлах (Skript ругается при загрузке);
  * вызов функции, которой нет ни в одном скрипте (опечатка в имени);
  * {@опция}, которой нет в options: этого файла.
С флагом --vars: переменные, которые читаются в одном файле, а пишутся только в другом
(полезно, когда меняете формат хранения в одном скрипте).

Это не полноценный парсер Skript: он не знает синтаксис эффектов и событий. Окончательная
проверка — /sk reload <скрипт> на сервере. Но опечатки и сломанную структуру ловит до заливки.
"""
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DIR = os.path.join(HERE, "..", "server", "plugins", "Skript", "scripts")

FUNC_DEF = re.compile(r"^function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
CMD_DEF = re.compile(r"^command\s+/?([^\s\[<:]+)")
ALIASES = re.compile(r"^\s*aliases\s*:\s*(.+)$")
CALL = re.compile(r"(?<![A-Za-z0-9_.\"'])([a-z][A-Za-z0-9_]*)\(")
OPT_USE = re.compile(r"\{@([A-Za-z0-9_]+)\}")
VAR = re.compile(r"\{(?!_)(?!@)([^{}]+)\}")

# слова, после которых "(" — это не вызов функции Skript
NOT_FUNCS = {
    "location", "vector", "world", "floor", "ceil", "ceiling", "round", "abs", "sqrt", "mod",
    "sin", "cos", "tan", "asin", "acos", "atan", "atan2", "exp", "ln", "log", "min", "max",
    "sum", "product", "rgb", "date", "player", "offlineplayer", "isnan", "calcexperience",
    "clamp", "caseequals", "formatnumber", "uuid", "random", "if", "while", "and", "or", "of",
    "is", "to", "in", "at", "by", "with", "set", "add", "remove", "send", "broadcast",
}


def strip_comment(line):
    """Убрать # комментарий вне строк (## внутри строки — не комментарий)."""
    out, in_str, i = [], False, 0
    while i < len(line):
        c = line[i]
        if c == '"':
            # "" внутри строки — экранированная кавычка
            if in_str and i + 1 < len(line) and line[i + 1] == '"':
                out.append('""')
                i += 2
                continue
            in_str = not in_str
        elif c == "#" and not in_str:
            if i + 1 < len(line) and line[i + 1] == "#":
                out.append("##")
                i += 2
                continue
            break
        out.append(c)
        i += 1
    return "".join(out).rstrip()


def string_parts(line):
    """Содержимое всех "..." в строке (с учётом "")."""
    parts, cur, in_str, i = [], [], False, 0
    while i < len(line):
        c = line[i]
        if c == '"':
            if in_str and i + 1 < len(line) and line[i + 1] == '"':
                cur.append('"')
                i += 2
                continue
            if in_str:
                parts.append("".join(cur))
                cur = []
            in_str = not in_str
        elif in_str:
            cur.append(c)
        i += 1
    return parts, in_str


def outside_strings(line):
    res, in_str, i = [], False, 0
    while i < len(line):
        c = line[i]
        if c == '"':
            if in_str and i + 1 < len(line) and line[i + 1] == '"':
                i += 2
                continue
            in_str = not in_str
        elif not in_str:
            res.append(c)
        i += 1
    return "".join(res)


def indent_of(raw):
    m = re.match(r"^[ \t]*", raw)
    return m.group(0)


def check_file(path, problems, defs):
    name = os.path.basename(path)
    with open(path, encoding="utf-8-sig") as f:
        lines = f.read().split("\n")

    styles = set()
    options = set()
    in_options = False
    unit = None
    prev_level = 0
    prev_colon = False
    prev_lineno = 0
    for n, raw in enumerate(lines, 1):
        code = strip_comment(raw)
        if not code.strip():
            continue
        ind = indent_of(code)
        if ind:
            if " " in ind and "\t" in ind:
                problems.append((name, n, "в отступе смешаны табы и пробелы"))
            styles.add("tab" if "\t" in ind else "space")
            if unit is None:
                unit = ind if "\t" in ind else ind
        # уровень отступа
        if "\t" in ind:
            level = ind.count("\t")
        else:
            w = len(unit) if unit and "\t" not in unit else 4
            level = len(ind) // max(w, 1)
        body = code.strip()

        if level == 0:
            in_options = body.startswith("options:")
            m = FUNC_DEF.match(body)
            if m:
                defs["func"][m.group(1)].append((name, n))
            m = CMD_DEF.match(body)
            if m:
                defs["cmd"][m.group(1).lower()].append((name, n))
        elif in_options and level == 1:
            m = re.match(r"^([A-Za-z0-9_]+)\s*:", body)
            if m:
                options.add(m.group(1))
        if level >= 1:
            m = ALIASES.match(body)
            if m:
                for a in m.group(1).split(","):
                    a = a.strip().lstrip("/").lower()
                    if a:
                        defs["cmd"][a].append((name, n))

        if prev_colon and level <= prev_level:
            problems.append((name, prev_lineno, "строка кончается ':' но вложенного блока нет"))
        if level > prev_level + 1 and not in_options:
            problems.append((name, n, "отступ прыгнул больше чем на один уровень"))

        parts, open_str = string_parts(body)
        if open_str:
            problems.append((name, n, "незакрытая кавычка"))
        for s in parts:
            if (s.count("%") - 2 * s.count("%%")) % 2:
                problems.append((name, n, "нечётное число % в строке — сломанная вставка %…%"))
        out = outside_strings(body)
        for a, b in ("{}", "()"):
            if body.count(a) != body.count(b):
                problems.append((name, n, "не сходятся скобки %s%s" % (a, b)))
        for m in CALL.finditer(out):
            fn = m.group(1)
            if fn.lower() not in NOT_FUNCS:
                defs["call"][fn].append((name, n))
        if not in_options:
            for m in OPT_USE.finditer(body):
                defs["opt_use"][(name, m.group(1))].append(n)
        # переменные: локальные {_x} внутри имён сводим к *, затем ищем глобальные
        flat = body
        for _ in range(5):
            flat2 = re.sub(r"\{_[^{}]*\}", "L", flat)
            flat2 = re.sub(r"%[^%{}]*%", "*", flat2)
            if flat2 == flat:
                break
            flat = flat2
        first = flat.split()[0] if flat.split() else ""
        target = ""
        if first == "set" and " to " in flat:
            target = flat[:flat.index(" to ")]
        elif first == "add" and " to " in flat:
            target = flat[flat.rindex(" to "):]
        elif first == "remove" and " from " in flat:
            target = flat[flat.rindex(" from "):]
        elif first in ("delete", "clear", "reset"):
            target = flat
        for m in VAR.finditer(flat):
            v = re.sub(r"\*+", "*", m.group(1))
            kind = "var_w" if m.start() < len(target) and (first != "add" and first != "remove" or m.start() >= len(flat) - len(target)) else "var_r"
            if first in ("add", "remove"):
                kind = "var_w" if m.start() >= len(flat) - len(target) else "var_r"
            defs[kind][v].add(name)

        prev_level = level
        prev_colon = body.endswith(":") and not in_options
        prev_lineno = n

    if prev_colon:
        problems.append((name, prev_lineno, "строка кончается ':' но вложенного блока нет"))
    if len(styles) > 1:
        problems.append((name, 0, "в файле есть и табы, и пробелы — Skript требует одно"))
    defs["options"][name] = options


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    want_vars = "--vars" in sys.argv
    folder = os.path.abspath(args[0] if args else DEFAULT_DIR)
    files = sorted(
        os.path.join(folder, f) for f in os.listdir(folder)
        if f.endswith(".sk") and not f.startswith("-")
    )
    if not files:
        print("Нет .sk файлов в", folder)
        return 1
    problems = []
    defs = {
        "func": defaultdict(list), "cmd": defaultdict(list), "call": defaultdict(list),
        "opt_use": defaultdict(list), "options": {},
        "var_r": defaultdict(set), "var_w": defaultdict(set),
    }
    for p in files:
        check_file(p, problems, defs)

    for fn, where in defs["func"].items():
        if len(where) > 1:
            problems.append((where[1][0], where[1][1], "функция %s уже объявлена в %s:%d" % (fn, where[0][0], where[0][1])))
    for c, where in defs["cmd"].items():
        files_with = {w[0] for w in where}
        if len(where) > 1:
            problems.append((where[1][0], where[1][1], "команда/алиас /%s уже есть в %s:%d" % (c, where[0][0], where[0][1])))
    for fn, where in defs["call"].items():
        if fn not in defs["func"]:
            for f, n in where[:3]:
                problems.append((f, n, "вызов %s(), но такой функции нет ни в одном скрипте" % fn))
    for (f, opt), lines in defs["opt_use"].items():
        if opt not in defs["options"].get(f, set()):
            problems.append((f, lines[0], "{@%s} не объявлена в options: этого файла" % opt))

    problems.sort(key=lambda x: (x[0], x[1]))
    print("Проверено скриптов: %d (%s)" % (len(files), folder))
    if problems:
        for f, n, msg in problems:
            print("  %s:%s  %s" % (f, n if n else "-", msg))
        print("Найдено замечаний: %d" % len(problems))
    else:
        print("Замечаний нет.")

    if want_vars:
        print("\nОбщие переменные (читаются в одном файле, пишутся в другом):")
        import fnmatch
        def writers_of(v):
            w = set()
            for pat, fs in defs["var_w"].items():
                if pat == v or fnmatch.fnmatchcase(v, pat) or fnmatch.fnmatchcase(pat, v):
                    w |= fs
            return w
        for v in sorted(defs["var_r"]):
            if "," in v or " " in v:
                continue  # это не переменная, а NBT/JSON в команде
            readers = defs["var_r"][v]
            writers = writers_of(v)
            foreign = readers - writers
            if writers and foreign:
                print("  {%s}  пишет: %s  читает: %s" % (v, ", ".join(sorted(writers)), ", ".join(sorted(foreign))))
            elif not writers:
                print("  {%s}  читается в %s, но НИГДЕ не записывается" % (v, ", ".join(sorted(readers))))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
