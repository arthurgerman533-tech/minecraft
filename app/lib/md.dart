import 'package:flutter/material.dart';

/// Небольшой рендер Markdown для лора (заголовки, абзацы, **жирный**, *курсив*, `код`,
/// цитаты, списки, таблицы, ---). Без сторонних пакетов, чтобы не зависеть от их поддержки.
enum BlockType { h1, h2, h3, h4, p, quote, ul, ol, table, hr }

class MdBlock {
  final BlockType type;
  final String text;
  final List<String> items;
  final List<List<String>> rows;
  final GlobalKey key = GlobalKey();
  MdBlock(this.type, {this.text = '', this.items = const [], this.rows = const []});
  bool get isHeading => type.index <= BlockType.h4.index;
}

List<MdBlock> parseMarkdown(String src) {
  src = src.replaceAll(RegExp(r'<!--.*?-->', dotAll: true), '');
  final lines = src.replaceAll('\r', '').split('\n');
  final out = <MdBlock>[];
  var i = 0;
  bool isList(String l) => RegExp(r'^\s*([-*•]|\d+\.)\s+').hasMatch(l);
  while (i < lines.length) {
    final l = lines[i];
    final t = l.trim();
    if (t.isEmpty) {
      i++;
      continue;
    }
    final h = RegExp(r'^(#{1,6})\s+(.*)$').firstMatch(t);
    if (h != null) {
      final lvl = h.group(1)!.length.clamp(1, 4);
      out.add(MdBlock(BlockType.values[lvl - 1], text: h.group(2)!));
      i++;
      continue;
    }
    if (RegExp(r'^(-{3,}|\*{3,}|_{3,})$').hasMatch(t)) {
      out.add(MdBlock(BlockType.hr));
      i++;
      continue;
    }
    if (t.startsWith('>')) {
      final buf = <String>[];
      while (i < lines.length && lines[i].trim().startsWith('>')) {
        buf.add(lines[i].trim().replaceFirst(RegExp(r'^>\s?'), ''));
        i++;
      }
      out.add(MdBlock(BlockType.quote, text: buf.join('\n').trim()));
      continue;
    }
    if (t.startsWith('|')) {
      final rows = <List<String>>[];
      while (i < lines.length && lines[i].trim().startsWith('|')) {
        final r = lines[i].trim();
        if (!RegExp(r'^\|[\s:\-|]+\|?$').hasMatch(r)) {
          var cells = r.split('|');
          cells = cells.sublist(1, r.endsWith('|') ? cells.length - 1 : cells.length);
          rows.add(cells.map((c) => c.trim()).toList());
        }
        i++;
      }
      out.add(MdBlock(BlockType.table, rows: rows));
      continue;
    }
    if (isList(l)) {
      final ordered = RegExp(r'^\s*\d+\.').hasMatch(l);
      final items = <String>[];
      while (i < lines.length && lines[i].trim().isNotEmpty) {
        if (isList(lines[i])) {
          items.add(lines[i].replaceFirst(RegExp(r'^\s*([-*•]|\d+\.)\s+'), ''));
        } else if (items.isNotEmpty) {
          items[items.length - 1] += ' ${lines[i].trim()}';
        }
        i++;
      }
      out.add(MdBlock(ordered ? BlockType.ol : BlockType.ul, items: items));
      continue;
    }
    final buf = <String>[];
    while (i < lines.length) {
      final x = lines[i].trim();
      if (x.isEmpty || x.startsWith('#') || x.startsWith('>') || x.startsWith('|') || isList(lines[i]) ||
          RegExp(r'^-{3,}$').hasMatch(x)) {
        break;
      }
      buf.add(x);
      i++;
    }
    out.add(MdBlock(BlockType.p, text: buf.join(' ')));
  }
  return out;
}

/// **жирный**, *курсив*, `код`, [текст](ссылка) → TextSpan.
TextSpan inlineSpans(String s, TextStyle base, {Color? codeBg, void Function(String href)? onLink}) {
  final spans = <InlineSpan>[];
  final re = RegExp(r'\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`|\[(.+?)\]\((.+?)\)');
  var pos = 0;
  for (final m in re.allMatches(s)) {
    if (m.start > pos) spans.add(TextSpan(text: s.substring(pos, m.start)));
    if (m.group(1) != null) {
      spans.add(inlineSpans(m.group(1)!, base.copyWith(fontWeight: FontWeight.w700), codeBg: codeBg, onLink: onLink));
    } else if (m.group(2) != null) {
      spans.add(inlineSpans(m.group(2)!, base.copyWith(fontStyle: FontStyle.italic), codeBg: codeBg, onLink: onLink));
    } else if (m.group(3) != null) {
      spans.add(TextSpan(text: m.group(3), style: base.copyWith(fontFamily: 'monospace', backgroundColor: codeBg)));
    } else {
      spans.add(TextSpan(
          text: m.group(4),
          style: base.copyWith(decoration: TextDecoration.underline, fontWeight: FontWeight.w600)));
    }
    pos = m.end;
  }
  if (pos < s.length) spans.add(TextSpan(text: s.substring(pos)));
  return TextSpan(style: base, children: spans);
}

class MdView extends StatelessWidget {
  final List<MdBlock> blocks;
  final ScrollController? controller;
  const MdView({super.key, required this.blocks, this.controller});

  @override
  Widget build(BuildContext context) {
    final th = Theme.of(context);
    final cs = th.colorScheme;
    final body = th.textTheme.bodyLarge!.copyWith(height: 1.55);
    final codeBg = cs.surfaceContainerHighest;
    Widget rich(String t, TextStyle st) => Text.rich(inlineSpans(t, st, codeBg: codeBg));

    Widget block(MdBlock b) {
      switch (b.type) {
        case BlockType.h1:
          return Padding(
              padding: const EdgeInsets.only(top: 24, bottom: 8),
              child: rich(b.text, th.textTheme.headlineMedium!.copyWith(color: cs.primary, fontWeight: FontWeight.w700)));
        case BlockType.h2:
          return Padding(
              padding: const EdgeInsets.only(top: 20, bottom: 6),
              child: rich(b.text, th.textTheme.titleLarge!.copyWith(fontWeight: FontWeight.w700)));
        case BlockType.h3:
        case BlockType.h4:
          return Padding(
              padding: const EdgeInsets.only(top: 16, bottom: 4),
              child: rich(b.text, th.textTheme.titleMedium!.copyWith(fontWeight: FontWeight.w700, color: cs.primary)));
        case BlockType.p:
          return Padding(padding: const EdgeInsets.only(bottom: 10), child: rich(b.text, body));
        case BlockType.quote:
          return Container(
            margin: const EdgeInsets.only(bottom: 12),
            padding: const EdgeInsets.fromLTRB(14, 10, 12, 10),
            decoration: BoxDecoration(
                color: cs.surfaceContainerHigh,
                border: Border(left: BorderSide(color: cs.primary, width: 3)),
                borderRadius: const BorderRadius.horizontal(right: Radius.circular(10))),
            child: rich(b.text, body.copyWith(fontStyle: FontStyle.italic)),
          );
        case BlockType.ul:
        case BlockType.ol:
          return Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                for (var k = 0; k < b.items.length; k++)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                      SizedBox(
                          width: 26,
                          child: Text(b.type == BlockType.ol ? '${k + 1}.' : '•',
                              style: body.copyWith(color: cs.primary, fontWeight: FontWeight.w700))),
                      Expanded(child: rich(b.items[k], body)),
                    ]),
                  ),
              ],
            ),
          );
        case BlockType.table:
          if (b.rows.isEmpty) return const SizedBox.shrink();
          final cols = b.rows.map((r) => r.length).reduce((a, c) => a > c ? a : c);
          final small = th.textTheme.bodyMedium!.copyWith(height: 1.4);
          return Padding(
            padding: const EdgeInsets.only(bottom: 14),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: ConstrainedBox(
                constraints: BoxConstraints(minWidth: MediaQuery.sizeOf(context).width - 32),
                child: Table(
                  defaultColumnWidth: const IntrinsicColumnWidth(flex: 1),
                  border: TableBorder.all(color: cs.outlineVariant),
                  children: [
                    for (var r = 0; r < b.rows.length; r++)
                      TableRow(
                        decoration: BoxDecoration(color: r == 0 ? cs.surfaceContainerHigh : null),
                        children: [
                          for (var c = 0; c < cols; c++)
                            Padding(
                              padding: const EdgeInsets.all(8),
                              child: ConstrainedBox(
                                constraints: const BoxConstraints(maxWidth: 260),
                                child: rich(c < b.rows[r].length ? b.rows[r][c] : '',
                                    r == 0 ? small.copyWith(fontWeight: FontWeight.w700) : small),
                              ),
                            ),
                        ],
                      ),
                  ],
                ),
              ),
            ),
          );
        case BlockType.hr:
          return const Padding(padding: EdgeInsets.symmetric(vertical: 12), child: Divider());
      }
    }

    return SingleChildScrollView(
      controller: controller,
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 48),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [for (final b in blocks) KeyedSubtree(key: b.key, child: block(b))],
      ),
    );
  }
}
