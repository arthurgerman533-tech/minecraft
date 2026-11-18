import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../calendar.dart';
import '../content.dart';
import '../i18n.dart';
import 'widgets.dart';

/// Карта мира: те же данные, что у сайта (content.json → map).
/// Координаты в блоках: x на восток, z на юг, Монолит в 0,0.
class MapScreen extends StatefulWidget {
  final Content content;
  const MapScreen({super.key, required this.content});
  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  final ctrl = TransformationController();
  double side = 1;
  bool powers = true, ancient = true, towns = true;
  String? ring;
  late MapPoint selected = widget.content.map.places.isNotEmpty
      ? widget.content.map.places.first
      : _empty;
  String selectedKind = t('центр мира', 'world centre');
  static final _empty = MapPoint({'name': '', 'x': 0, 'z': 0});

  double get extent => widget.content.config.border.w6 * 1.12;
  double get k => side / (2 * extent); // пикселей карты на блок
  Offset toCanvas(double x, double z) =>
      Offset((x + extent) * k, (z + extent) * k);

  @override
  void initState() {
    super.initState();
    ctrl.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    ctrl.dispose();
    super.dispose();
  }

  void onTap(Offset p) {
    final m = widget.content.map;
    final scale = ctrl.value.getMaxScaleOnAxis();
    MapPoint? best;
    String kind = '';
    var bestD = 28 / scale; // радиус попадания в пикселях холста
    void test(List<MapPoint> l, String kd, bool on) {
      if (!on) return;
      for (final e in l) {
        final d = (toCanvas(e.x, e.z) - p).distance;
        if (d < bestD) {
          bestD = d;
          best = e;
          kind = kd;
        }
      }
    }

    test(m.places, t('центр мира', 'world centre'), true);
    test(m.towns, t('город', 'town'), towns);
    test(m.ancient, t('Предтечи', 'Forerunners'), ancient);
    test(m.powers, '', powers);
    if (best != null) {
      setState(() {
        selected = best!;
        selectedKind = kind.isEmpty ? (m.blocs[best!.bloc] ?? '') : kind;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final c = widget.content,
        m = c.map,
        b = c.config.border,
        st = serverState(c.config);
    final cs = Theme.of(context).colorScheme;
    final rings = <(String, String, int)>[
      ('start', t('Старт', 'Start'), b.start),
      ('w1', t('Н1', 'W1'), b.w1),
      ('w2', t('Н2', 'W2'), b.w2),
      ('w3', t('Н3', 'W3'), b.w3),
      ('w5', t('Н5', 'W5'), b.w5),
      ('w6', t('Н6', 'W6'), b.w6),
    ];
    final ringSel = ring ?? (st.started ? null : 'w6');
    final scale = ctrl.value.getMaxScaleOnAxis();
    final sel = selected;
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
      children: [
        Wrap(
          spacing: 6,
          runSpacing: 6,
          children: [
            FilterChip(
              label: Text(t('Державы', 'Powers')),
              selected: powers,
              onSelected: (v) => setState(() => powers = v),
            ),
            FilterChip(
              label: Text(t('Древние места', 'Ancient sites')),
              selected: ancient,
              onSelected: (v) => setState(() => ancient = v),
            ),
            FilterChip(
              label: Text(
                '${t('Города', 'Towns')}${m.towns.isEmpty ? '' : ' (${m.towns.length})'}',
              ),
              selected: towns,
              onSelected: (v) => setState(() => towns = v),
            ),
          ],
        ),
        const SizedBox(height: 6),
        Wrap(
          spacing: 6,
          runSpacing: 6,
          crossAxisAlignment: WrapCrossAlignment.center,
          children: [
            Text(
              t('Граница', 'Border'),
              style: TextStyle(color: cs.onSurfaceVariant),
            ),
            for (final r in rings)
              ChoiceChip(
                label: Text(r.$2),
                selected: ringSel == r.$1,
                onSelected: (v) =>
                    setState(() => ring = v ? r.$1 : (st.started ? null : '_')),
              ),
          ],
        ),
        const SizedBox(height: 10),
        ClipRRect(
          borderRadius: BorderRadius.circular(14),
          child: LayoutBuilder(
            builder: (ctx, box) {
              side = box.maxWidth;
              return SizedBox(
                width: side,
                height: side,
                child: Container(
                  color: Color.alphaBlend(const Color(0x292F7FB5), cs.surface),
                  child: Stack(
                    children: [
                      InteractiveViewer(
                        transformationController: ctrl,
                        minScale: 1,
                        maxScale: 24,
                        boundaryMargin: const EdgeInsets.all(200),
                        child: GestureDetector(
                          onTapUp: (d) => onTap(d.localPosition),
                          child: SizedBox(
                            width: side,
                            height: side,
                            child: CustomPaint(
                              painter: _MapPainter(
                                map: m,
                                border: b,
                                rings: rings,
                                ringSel: ringSel,
                                nowRadius: st.started ? st.radius : null,
                                extent: extent,
                                scale: scale,
                                powers: powers,
                                ancient: ancient,
                                towns: towns,
                                selected: sel,
                                cs: cs,
                              ),
                            ),
                          ),
                        ),
                      ),
                      Positioned(
                        right: 8,
                        top: 8,
                        child: IconButton.filledTonal(
                          tooltip: t('Сбросить', 'Reset'),
                          icon: const Icon(Icons.center_focus_strong),
                          onPressed: () => ctrl.value = Matrix4.identity(),
                        ),
                      ),
                      Positioned(
                        right: 10,
                        bottom: 8,
                        child: Text(
                          t('С ↑', 'N ↑'),
                          style: TextStyle(
                            fontWeight: FontWeight.w700,
                            color: cs.onSurfaceVariant,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
        const SizedBox(height: 10),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Wrap(
                  spacing: 8,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: [
                    Text(
                      sel.name,
                      style: Theme.of(context).textTheme.titleMedium
                          ?.copyWith(fontWeight: FontWeight.w700),
                    ),
                    if (selectedKind.isNotEmpty)
                      Text(
                        selectedKind,
                        style: TextStyle(color: cs.onSurfaceVariant),
                      ),
                    CmdChip('X ${sel.x.round()} · Z ${sel.z.round()}'),
                  ],
                ),
                if (sel.text.isNotEmpty || sel.blocks.isNotEmpty)
                  const SizedBox(height: 6),
                if (sel.text.isNotEmpty) Text(sel.text),
                if (sel.blocks.isNotEmpty)
                  Text(
                    '${t('Занято чанков', 'Claimed chunks')}: ${sel.blocks.length}',
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 10),
        Text(
          t(
                'Державы и древние места показаны схемой по лору: настоящие столицы строят игроки.',
                'Powers and ancient sites are a schematic based on the lore: the real capitals are built by players.',
              ) +
              (m.towns.isNotEmpty
                  ? t(' Города Towny выгружены ', ' Towny towns exported ') +
                        m.townsDate
                  : t(
                      ' Реальные города появятся после открытия сервера.',
                      ' Real towns will appear after the server opens.',
                    )),
          style: TextStyle(color: cs.onSurfaceVariant),
        ),
        if (c.config.mapUrl.isNotEmpty) ...[
          const SizedBox(height: 10),
          OutlinedButton.icon(
            onPressed: () => openUrl(context, c.config.mapUrl),
            icon: const Icon(Icons.map_outlined),
            label: Text(t('Живая карта BlueMap', 'Live BlueMap')),
          ),
        ],
      ],
    );
  }
}

Color _hex(String h, Color fallback) {
  final v = int.tryParse(h.replaceFirst('#', ''), radix: 16);
  return v == null ? fallback : Color(0xFF000000 | v);
}

class _MapPainter extends CustomPainter {
  final WorldMap map;
  final BorderCfg border;
  final List<(String, String, int)> rings;
  final String? ringSel;
  final int? nowRadius;
  final double extent, scale;
  final bool powers, ancient, towns;
  final MapPoint selected;
  final ColorScheme cs;
  _MapPainter({
    required this.map,
    required this.border,
    required this.rings,
    required this.ringSel,
    required this.nowRadius,
    required this.extent,
    required this.scale,
    required this.powers,
    required this.ancient,
    required this.towns,
    required this.selected,
    required this.cs,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final k = size.width / (2 * extent);
    Offset p(double x, double z) => Offset((x + extent) * k, (z + extent) * k);
    final s = 1 / scale; // толщина линий и шрифт не растут при приближении
    final gold = cs.primary, ink = cs.onSurface, bg = cs.surface;
    final center = p(0, 0), rw = border.w6 * k;

    canvas.drawCircle(
      center,
      rw,
      Paint()..color = Color.alphaBlend(const Color(0x386F9A4A), bg),
    );
    canvas.save();
    canvas.clipPath(
      Path()..addOval(Rect.fromCircle(center: center, radius: rw)),
    );
    final grid = Paint()
      ..color = cs.outlineVariant.withValues(alpha: .6)
      ..strokeWidth = s;
    for (var v = -2000.0; v <= 2000; v += 500) {
      canvas.drawLine(p(v, -extent), p(v, extent), grid);
      canvas.drawLine(p(-extent, v), p(extent, v), grid);
    }
    canvas.restore();

    void label(
      String txt,
      Offset at, {
      double size = 13,
      Color? color,
      FontWeight w = FontWeight.w700,
      bool italic = false,
      bool above = false,
    }) {
      final fs = size * s;
      final style = TextStyle(
        fontSize: fs,
        fontWeight: w,
        fontStyle: italic ? FontStyle.italic : FontStyle.normal,
      );
      final outline = TextPainter(
        text: TextSpan(
          text: txt,
          style: style.copyWith(
            foreground: Paint()
              ..style = PaintingStyle.stroke
              ..strokeWidth = 3 * s
              ..color = bg,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout();
      final fill = TextPainter(
        text: TextSpan(
          text: txt,
          style: style.copyWith(color: color ?? ink),
        ),
        textDirection: TextDirection.ltr,
      )..layout();
      final o = at - Offset(fill.width / 2, above ? fill.height : 0);
      outline.paint(canvas, o);
      fill.paint(canvas, o);
    }

    if (powers) {
      for (final e in map.powers) {
        final col = _hex(e.color, gold);
        canvas.drawCircle(
          p(e.x, e.z),
          230 * k,
          Paint()..color = col.withValues(alpha: e == selected ? .38 : .22),
        );
        canvas.drawCircle(
          p(e.x, e.z),
          math.max(5 * s, 22 * k),
          Paint()..color = col,
        );
        label(e.name, p(e.x, e.z) + Offset(0, 9 * s), size: 14);
      }
    }
    for (final r in rings) {
      final on = r.$1 == ringSel;
      canvas.drawCircle(
        center,
        r.$3 * k,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = (on ? 3 : 1.2) * s
          ..color = gold.withValues(alpha: on ? 1 : .5),
      );
      if (on || r.$1 != 'start') {
        final a = p(r.$3 * .7071, -r.$3 * .7071);
        label(
          '${r.$2} · ${r.$3}',
          a + Offset(0, -2 * s),
          size: on ? 13 : 11,
          color: gold,
          above: true,
        );
      }
    }
    if (nowRadius != null) {
      canvas.drawCircle(
        center,
        nowRadius! * k,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 3 * s
          ..color = cs.error,
      );
      label(
        '${t('Сейчас', 'Now')} $nowRadius',
        p(0, nowRadius!.toDouble()),
        size: 12,
        color: cs.error,
      );
    }
    canvas.drawCircle(
      center,
      80 * k,
      Paint()..color = gold.withValues(alpha: .15),
    );
    if (ancient) {
      for (final e in map.ancient) {
        final c = p(e.x, e.z);
        canvas.save();
        canvas.translate(c.dx, c.dy);
        canvas.rotate(math.pi / 4);
        final d = math.max(4 * s, 18 * k);
        canvas.drawRect(
          Rect.fromCenter(center: Offset.zero, width: d, height: d),
          Paint()..color = cs.tertiary,
        );
        canvas.restore();
        label(
          e.name,
          c + Offset(0, 9 * s),
          size: 12,
          color: cs.tertiary,
          w: FontWeight.w600,
          italic: true,
        );
      }
    }
    if (towns) {
      for (final e in map.towns) {
        final col = _hex(e.color, gold);
        final fill = Paint()..color = col.withValues(alpha: .55);
        for (final bl in e.blocks) {
          canvas.drawRect(
            Rect.fromLTWH(
              p(bl[0] * 16.0, bl[1] * 16.0).dx,
              p(bl[0] * 16.0, bl[1] * 16.0).dy,
              16 * k,
              16 * k,
            ),
            fill,
          );
        }
        canvas.drawCircle(p(e.x, e.z), 5 * s, Paint()..color = col);
        label(
          e.name,
          p(e.x, e.z) + Offset(0, 7 * s),
          size: 12,
          w: FontWeight.w600,
        );
      }
    }
    for (final e in map.places) {
      final c = p(e.x, e.z), d = math.max(8 * s, 34 * k);
      canvas.drawRect(
        Rect.fromCenter(center: c, width: d, height: d),
        Paint()..color = ink,
      );
      canvas.drawRect(
        Rect.fromCenter(center: c, width: d, height: d),
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2 * s
          ..color = gold,
      );
      label(
        e.name,
        c - Offset(0, d / 2 + 3 * s),
        size: 15,
        color: gold,
        above: true,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _MapPainter o) =>
      o.scale != scale ||
      o.powers != powers ||
      o.ancient != ancient ||
      o.towns != towns ||
      o.ringSel != ringSel ||
      o.selected != selected ||
      o.cs != cs;
}
