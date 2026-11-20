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
  bool relief = true, weather = false, loreTags = true;

  /// world, nether или earth (карта настоящей Земли)
  String mode = 'world';
  bool get nether => mode == 'nether';
  bool get earth => mode == 'earth';
  bool get world => mode == 'world';
  String? ring;
  late MapPoint selected = widget.content.map.places.isNotEmpty
      ? widget.content.map.places.first
      : _empty;
  String selectedKind = t('центр мира', 'world centre');
  static final _empty = MapPoint({'name': '', 'x': 0, 'z': 0});

  double get extent => earth
      ? 2950
      : nether
      ? widget.content.config.border.w6 / 8 * 1.2
      : widget.content.config.border.w6 * 1.12;
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

  /// порталы держав в Незере: столица ÷ 8
  static List<MapPoint> _portals(WorldMap m) => [
    for (final e in m.powers)
      MapPoint({
        'id': e.id,
        'name': e.name,
        'color': e.color,
        'text':
            t(
              'Портал державы: постройте рамку на этих координатах Незера, и выйдете у столицы. ',
              'The power\'s portal: build a frame at these Nether coordinates and you will come out at the capital. ',
            ) +
            e.text,
        'x': (e.x / 8).round(),
        'z': (e.z / 8).round(),
      }),
  ];

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

    if (earth && m.earth != null) {
      test(m.earth!.powers, '', true);
      if (best != null) {
        setState(() {
          selected = best!;
          selectedKind = m.blocs[best!.bloc] ?? '';
        });
      }
      return;
    }
    if (nether && m.nether != null) {
      final n = m.nether!;
      test(n.places, t('под Монолитом', 'beneath the Monolith'), true);
      test(n.sites, t('Незер', 'Nether'), true);
      test(_portals(m), t('портал державы', 'power\'s portal'), true);
      if (best != null) {
        setState(() {
          selected = best!;
          selectedKind = kind;
        });
      }
      return;
    }
    test(m.places, t('центр мира', 'world centre'), true);
    test(m.lore, t('метка лора', 'lore tag'), loreTags);
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
        if (m.nether != null || m.earth != null) ...[
          SegmentedButton<String>(
            segments: [
              ButtonSegment(
                value: 'world',
                icon: const Icon(Icons.map_outlined),
                label: Text(t('Мир 1', 'World 1')),
              ),
              if (m.nether != null)
                ButtonSegment(
                  value: 'nether',
                  icon: const Icon(Icons.local_fire_department),
                  label: Text(t('Незер', 'Nether')),
                ),
              if (m.earth != null)
                ButtonSegment(
                  value: 'earth',
                  icon: const Icon(Icons.public),
                  label: Text(t('Мир 2: Земля', 'World 2: Earth')),
                ),
            ],
            selected: {mode},
            onSelectionChanged: (v) => setState(() {
              mode = v.first;
              ctrl.value = Matrix4.identity();
              final n = m.nether, e = m.earth;
              if (nether && n != null && n.places.isNotEmpty) {
                selected = n.places.first;
                selectedKind = t('под Монолитом', 'beneath the Monolith');
              } else if (earth && e != null && e.powers.isNotEmpty) {
                selected = e.powers.first;
                selectedKind = m.blocs[selected.bloc] ?? '';
              } else if (world && m.places.isNotEmpty) {
                selected = m.places.first;
                selectedKind = t('центр мира', 'world centre');
              }
            }),
          ),
          const SizedBox(height: 8),
        ],
        if (world)
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: [
              if (m.terrain != null)
                FilterChip(
                  label: Text(t('Рельеф', 'Terrain')),
                  selected: relief,
                  onSelected: (v) => setState(() => relief = v),
                ),
              FilterChip(
                avatar: const Icon(Icons.thunderstorm_outlined, size: 18),
                label: Text(t('Погода', 'Weather')),
                selected: weather,
                onSelected: (v) => setState(() => weather = v),
              ),
              if (m.lore.isNotEmpty)
                FilterChip(
                  label: Text(t('Метки лора', 'Lore tags')),
                  selected: loreTags,
                  onSelected: (v) => setState(() => loreTags = v),
                ),
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
        if (!earth)
          Wrap(
            spacing: 6,
            runSpacing: 6,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              Text(
                nether
                    ? t('Граница ÷ 8', 'Border ÷ 8')
                    : t('Граница', 'Border'),
                style: TextStyle(color: cs.onSurfaceVariant),
              ),
              for (final r in rings)
                ChoiceChip(
                  label: Text(r.$2),
                  selected: ringSel == r.$1,
                  onSelected: (v) => setState(
                    () => ring = v ? r.$1 : (st.started ? null : '_'),
                  ),
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
                  color: earth
                      ? Color.alphaBlend(const Color(0x552F7FB5), cs.surface)
                      : nether
                      ? const Color(0xFF2A0F0C)
                      : Color.alphaBlend(const Color(0x292F7FB5), cs.surface),
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
                            child: Stack(
                              children: [
                                if (world && relief && m.terrain != null)
                                  Positioned(
                                    left: (m.terrain!.x0 + extent) * k,
                                    top: (m.terrain!.z0 + extent) * k,
                                    width: (m.terrain!.x1 - m.terrain!.x0) * k,
                                    height: (m.terrain!.z1 - m.terrain!.z0) * k,
                                    child: Image.asset(
                                      m.terrain!.asset,
                                      fit: BoxFit.fill,
                                      filterQuality: FilterQuality.low,
                                      errorBuilder: (_, _, _) =>
                                          const SizedBox.shrink(),
                                    ),
                                  ),
                                Positioned.fill(
                                  child: CustomPaint(
                                    painter: earth
                                        ? _EarthPainter(
                                            earth: m.earth!,
                                            blocs: m.blocs,
                                            extent: extent,
                                            scale: scale,
                                            selected: sel,
                                            cs: cs,
                                          )
                                        : nether
                                        ? _NetherPainter(
                                            map: m,
                                            rings: rings,
                                            ringSel: ringSel,
                                            nowRadius: st.started
                                                ? st.radius
                                                : null,
                                            extent: extent,
                                            scale: scale,
                                            selected: sel,
                                            cs: cs,
                                          )
                                        : _MapPainter(
                                            map: m,
                                            border: b,
                                            rings: rings,
                                            ringSel: ringSel,
                                            nowRadius: st.started
                                                ? st.radius
                                                : null,
                                            extent: extent,
                                            scale: scale,
                                            powers: powers,
                                            ancient: ancient,
                                            towns: towns,
                                            relief: relief && m.terrain != null,
                                            weather: weather,
                                            loreTags: loreTags,
                                            selected: sel,
                                            cs: cs,
                                          ),
                                  ),
                                ),
                              ],
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
                    CmdChip(
                      earth
                          ? '${(48 - sel.z / 111.32).toStringAsFixed(1)}° N · ${(25 + sel.x / (math.cos(48 * math.pi / 180) * 111.32)).toStringAsFixed(1)}° E'
                          : nether
                          ? '${t('Незер', 'Nether')} X ${sel.x.round()} · Z ${sel.z.round()} · ${t('наверху', 'above')} X ${(sel.x * 8).round()} · Z ${(sel.z * 8).round()}'
                          : 'X ${sel.x.round()} · Z ${sel.z.round()}',
                    ),
                  ],
                ),
                if (sel.text.isNotEmpty || sel.blocks.isNotEmpty)
                  const SizedBox(height: 6),
                if (earth && sel.real.isNotEmpty)
                  Text(
                    '${t('В реальной истории', 'In real history')}: ${sel.real}.',
                    style: const TextStyle(fontWeight: FontWeight.w600),
                  ),
                if (sel.text.isNotEmpty) Text(sel.text),
                if (sel.blocks.isNotEmpty)
                  Text(
                    '${t('Занято чанков', 'Claimed chunks')}: ${sel.blocks.length}',
                  ),
              ],
            ),
          ),
        ),
        if (weather && world) ...[
          const SizedBox(height: 10),
          _WeatherLegend(content: c),
        ],
        if (world && m.far.isNotEmpty) ...[
          const SizedBox(height: 10),
          Text(
            t('За границей мира', 'Beyond the world border'),
            style: Theme.of(context).textTheme.titleSmall
                ?.copyWith(fontWeight: FontWeight.w700),
          ),
          for (final f in m.far)
            Card(
              child: ListTile(
                leading: const Icon(Icons.explore_outlined),
                title: Text(f.name),
                subtitle: Text(
                  '${t('≈', '≈')} ${math.sqrt(f.x * f.x + f.z * f.z).round()} ${t('блоков от 0,0', 'blocks from 0,0')} · X ${f.x.round()} · Z ${f.z.round()}\n${f.text}',
                ),
                isThreeLine: true,
                onTap: () => setState(() {
                  selected = f;
                  selectedKind = t('за границей мира', 'beyond the border');
                }),
              ),
            ),
        ],
        const SizedBox(height: 10),
        if (m.terrain != null && world)
          Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Text(
              t(
                    'Рельеф, реки, озёра и леса нарисованы блок в блок с настоящего мира PaxVanila. Разведана область вокруг спавна, дальше схема.',
                    'Terrain, rivers, lakes and forests are rendered block by block from the real PaxVanila world. The area around spawn is explored, the rest is a schematic.',
                  ) +
                  (m.terrain!.date.isEmpty ? '' : ' ${m.terrain!.date}'),
              style: TextStyle(color: cs.onSurfaceVariant),
            ),
          ),
        if (earth)
          Text(
            t(
              'Мир 2 строится по настоящей Земле. Контуры суши: Natural Earth. Державы стоят на местах своих исторических прообразов. В ванильном Мире 1 они вокруг Монолита.',
              'World 2 is built on the real Earth. Coastlines: Natural Earth. The powers stand where their historical prototypes were. In vanilla World 1 they surround the Monolith.',
            ),
            style: TextStyle(color: cs.onSurfaceVariant),
          )
        else if (nether)
          Text(
            t(
              'Порталы держав посчитаны из карты мира: координаты столицы ÷ 8. Крепости, бастионы и легенды показаны схемой по лору. Кольца это граница мира ÷ 8.',
              'The powers\' portals are taken from the world map: capital coordinates ÷ 8. Fortresses, bastions and legends are a schematic of the lore. The rings are the world border ÷ 8.',
            ),
            style: TextStyle(color: cs.onSurfaceVariant),
          )
        else
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
  final bool powers, ancient, towns, relief, weather, loreTags;
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
    required this.relief,
    required this.weather,
    required this.loreTags,
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

    if (relief) {
      // схема суши там, где мир ещё не разведан, а поверх картинки ничего
      final tr = map.terrain!;
      canvas.drawPath(
        Path.combine(
          PathOperation.difference,
          Path()..addOval(Rect.fromCircle(center: center, radius: rw)),
          Path()..addRect(Rect.fromPoints(p(tr.x0, tr.z0), p(tr.x1, tr.z1))),
        ),
        Paint()..color = Color.alphaBlend(const Color(0x386F9A4A), bg),
      );
      // за самой широкой границей мир темнее
      canvas.drawPath(
        Path()
          ..fillType = PathFillType.evenOdd
          ..addRect(Offset.zero & size)
          ..addOval(Rect.fromCircle(center: center, radius: rw)),
        Paint()..color = const Color(0x6B000000),
      );
    } else {
      canvas.drawCircle(
        center,
        rw,
        Paint()..color = Color.alphaBlend(const Color(0x386F9A4A), bg),
      );
    }
    if (weather) {
      final c = map.zoneCell.toDouble();
      for (final z in _weatherZones) {
        final cells = map.zones[z.$1] ?? const [];
        if (cells.isEmpty) continue;
        final path = Path();
        for (final e in cells) {
          path.addRect(
            Rect.fromLTWH(
              p(e[0].toDouble(), e[1].toDouble()).dx,
              p(e[0].toDouble(), e[1].toDouble()).dy,
              c * k,
              c * k,
            ),
          );
        }
        canvas.drawPath(path, Paint()..color = z.$2.withValues(alpha: .4));
      }
      canvas.drawCircle(
        center,
        120 * k,
        Paint()..color = const Color(0x4D8B1E1E),
      );
      canvas.drawRect(
        Rect.fromCenter(center: center, width: 96 * k, height: 96 * k),
        Paint()..color = const Color(0x553FA34D),
      );
    }
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
    if (loreTags) {
      for (final e in map.lore) {
        final col = switch (e.cat) {
          'cataclysm' => const Color(0xFFD9534F),
          'battle' => const Color(0xFFB0362B),
          'front' => const Color(0xFF8B6B3E),
          'old' => const Color(0xFF6C7A89),
          _ => cs.tertiary,
        };
        canvas.drawCircle(
          p(e.x, e.z),
          math.max(3 * s, 8 * k),
          Paint()..color = col,
        );
        label(
          e.name,
          p(e.x, e.z) - Offset(0, 6 * s),
          size: 11,
          color: col,
          w: FontWeight.w600,
          above: true,
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
      o.relief != relief ||
      o.weather != weather ||
      o.loreTags != loreTags ||
      o.ringSel != ringSel ||
      o.selected != selected ||
      o.cs != cs;
}

/// Зоны погоды на карте: (ключ зоны, цвет, катаклизм)
const _weatherZones = <(String, Color, String)>[
  ('desert', Color(0xFFE8A33D), 'sandstorm'),
  ('peaks', Color(0xFFF5C542), 'storm'),
  ('snow', Color(0xFF5FD4E8), 'blizzard'),
  ('water', Color(0xFF3B6FD9), 'flood'),
];

/// Легенда слоя погоды (данные: content.json → meteo, зоны из настоящего мира).
class _WeatherLegend extends StatelessWidget {
  final Content content;
  const _WeatherLegend({required this.content});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final events = [
      for (final e in (content.meteo['events'] ?? const []) as List)
        Map<String, dynamic>.from(e as Map),
    ];
    Map<String, dynamic> ev(String id) => events.firstWhere(
      (e) => e['id'] == id,
      orElse: () => {'icon': '', 'name': id},
    );
    final iv = Map<String, dynamic>.from(
      (content.meteo['interval'] ?? const {}) as Map,
    );
    final zones = content.map.zones;
    final rows = <(Color, String, String)>[
      for (final z in _weatherZones)
        if ((zones[z.$1] ?? const []).isNotEmpty)
          (
            z.$2,
            '${ev(z.$3)['icon']} ${ev(z.$3)['name']}',
            switch (z.$1) {
              'desert' => t(
                'пустыни и бесплодные земли',
                'deserts and badlands',
              ),
              'peaks' => t(
                'вершины выше Y 110: молнии бьют чаще',
                'peaks above Y 110: lightning strikes more often',
              ),
              'snow' => t(
                'снежные земли: метель сильнее',
                'snowy lands: the blizzard is harsher',
              ),
              _ => t('океаны, реки, пляжи', 'oceans, rivers, beaches'),
            },
          ),
      (
        const Color(0xFF8B1E1E),
        '${ev('ash')['icon']} ${ev('ash')['name']}',
        t(
          'столб огня над Монолитом 0,0',
          'a pillar of fire over the Monolith at 0,0',
        ),
      ),
      (
        const Color(0xFF3FA34D),
        t('Безопасная зона', 'Safe zone'),
        t(
          'башня новичков ±48 блоков: урона нет',
          'newcomer tower ±48 blocks: no damage',
        ),
      ),
    ];
    final everywhere =
        ['blizzard', 'drought', 'quake', 'meteor', 'fog', 'aurora', 'storm']
            .map(ev)
            .where((e) => e['name'] != null && e['name'] != e['id'])
            .map((e) => '${e['icon']} ${e['name']}')
            .join(', ');
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              t('Погода на сервере', 'Weather on the server'),
              style: Theme.of(context).textTheme.titleMedium
                  ?.copyWith(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 8),
            for (final r in rows)
              Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 14,
                      height: 14,
                      margin: const EdgeInsets.only(top: 3, right: 8),
                      decoration: BoxDecoration(
                        color: r.$1.withValues(alpha: .8),
                        borderRadius: BorderRadius.circular(3),
                      ),
                    ),
                    Expanded(
                      child: Text.rich(
                        TextSpan(
                          children: [
                            TextSpan(
                              text: r.$2,
                              style: const TextStyle(
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            TextSpan(text: ' ${r.$3}'),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            if (everywhere.isNotEmpty)
              Text(
                '${t('Везде под открытым небом', 'Everywhere under open sky')}: $everywhere.',
              ),
            const SizedBox(height: 6),
            Text(
              t(
                'Катаклизм приходит сам раз в ${iv['min'] ?? 45}–${iv['max'] ?? 90} минут, предупреждение за ${iv['warn'] ?? 60} секунд. Блоки не ломаются, урон только при 5+ сердцах, новички первые 48 ч без урона. Это справочник, не живая погода.',
                'A cataclysm comes on its own every ${iv['min'] ?? 45}–${iv['max'] ?? 90} minutes, with a ${iv['warn'] ?? 60}-second warning. Blocks are never broken, damage only above 5 hearts, newcomers are safe for 48 h. This is a reference, not live weather.',
              ),
              style: TextStyle(color: cs.onSurfaceVariant),
            ),
            if (zones.isEmpty)
              Text(
                t(
                  'Зоны пустынь, гор и морей появятся после рендера мира.',
                  'Desert, mountain and sea zones appear once the world is rendered.',
                ),
                style: TextStyle(color: cs.onSurfaceVariant),
              ),
          ],
        ),
      ),
    );
  }
}

/// Карта Незера: порталы держав (столица ÷ 8), крепости, бастионы, легенды, тракты.
class _NetherPainter extends CustomPainter {
  final WorldMap map;
  final List<(String, String, int)> rings;
  final String? ringSel;
  final int? nowRadius;
  final double extent, scale;
  final MapPoint selected;
  final ColorScheme cs;
  _NetherPainter({
    required this.map,
    required this.rings,
    required this.ringSel,
    required this.nowRadius,
    required this.extent,
    required this.scale,
    required this.selected,
    required this.cs,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final n = map.nether;
    if (n == null) return;
    final k = size.width / (2 * extent);
    Offset p(double x, double z) => Offset((x + extent) * k, (z + extent) * k);
    final s = 1 / scale;
    const gold = Color(0xFFF0B84A),
        ink = Color(0xFFF4E6D0),
        bg = Color(0xFF2A0F0C);
    final center = p(0, 0);

    // лава и леса: постоянный узор, как на сайте
    var seed = 7;
    double rnd() => (seed = (seed * 16807) % 2147483647) / 2147483647;
    for (var i = 0; i < 46; i++) {
      final x = (rnd() * 2 - 1) * extent * 1.5,
          z = (rnd() * 2 - 1) * extent * 1.5,
          r = 6 + rnd() * 22,
          tt = rnd();
      rnd();
      if (math.sqrt(x * x + z * z) < 30) continue;
      final col = tt < .55
          ? const Color(0x55E2561B)
          : tt < .8
          ? const Color(0x55A3242C)
          : const Color(0x55168A7C);
      canvas.drawOval(
        Rect.fromCenter(center: p(x, z), width: r * 3 * k, height: r * 2 * k),
        Paint()..color = col,
      );
    }
    final grid = Paint()
      ..color = const Color(0x33F4E6D0)
      ..strokeWidth = s;
    for (var v = -250.0; v <= 250; v += 50) {
      canvas.drawLine(p(v, -extent), p(v, extent), grid);
      canvas.drawLine(p(-extent, v), p(extent, v), grid);
    }

    void label(
      String txt,
      Offset at, {
      double size = 12,
      Color color = ink,
      bool above = false,
    }) {
      final st = TextStyle(fontSize: size * s, fontWeight: FontWeight.w700);
      final o = TextPainter(
        text: TextSpan(
          text: txt,
          style: st.copyWith(
            foreground: Paint()
              ..style = PaintingStyle.stroke
              ..strokeWidth = 3 * s
              ..color = bg,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout();
      final f = TextPainter(
        text: TextSpan(
          text: txt,
          style: st.copyWith(color: color),
        ),
        textDirection: TextDirection.ltr,
      )..layout();
      final at2 = at - Offset(f.width / 2, above ? f.height : 0);
      o.paint(canvas, at2);
      f.paint(canvas, at2);
    }

    for (final r in rings) {
      final on = r.$1 == ringSel;
      canvas.drawCircle(
        center,
        r.$3 / 8 * k,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = (on ? 3 : 1.2) * s
          ..color = gold.withValues(alpha: on ? 1 : .45),
      );
      if (on) {
        label(
          '${r.$2} · ${(r.$3 / 8).round()}',
          p(r.$3 / 8 * .7071, -r.$3 / 8 * .7071),
          color: gold,
          above: true,
        );
      }
    }
    if (nowRadius != null) {
      canvas.drawCircle(
        center,
        nowRadius! / 8 * k,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 3 * s
          ..color = cs.error,
      );
    }
    for (final r in n.roads) {
      canvas.drawLine(
        center,
        p(r.x, r.z),
        Paint()
          ..strokeWidth = 4 * s
          ..color = const Color(0xFFC07A45),
      );
    }
    for (final e in n.sites) {
      final col = switch (e.kind) {
        'fortress' => const Color(0xFFB0362B),
        'bastion' => const Color(0xFF6B6B6B),
        _ => const Color(0xFFC77DFF),
      };
      final c = p(e.x, e.z), d = math.max(6 * s, 10 * k);
      canvas.drawRect(
        Rect.fromCenter(center: c, width: d, height: d),
        Paint()..color = col,
      );
      if (e == selected) {
        canvas.drawRect(
          Rect.fromCenter(center: c, width: d + 6 * s, height: d + 6 * s),
          Paint()
            ..style = PaintingStyle.stroke
            ..strokeWidth = 2 * s
            ..color = ink,
        );
      }
      label(e.name, c + Offset(0, d / 2 + 2 * s), size: 11);
    }
    for (final e in map.powers) {
      final c = p((e.x / 8).roundToDouble(), (e.z / 8).roundToDouble());
      final col = _hex(e.color, gold);
      canvas.drawCircle(
        c,
        math.max(5 * s, 7 * k),
        Paint()..color = const Color(0xFF7A3CC8),
      );
      canvas.drawCircle(
        c,
        math.max(5 * s, 7 * k),
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2 * s
          ..color = col,
      );
      label(e.name, c + Offset(0, 8 * s), size: 12, color: col);
    }
    for (final e in n.places) {
      final c = p(e.x, e.z), d = math.max(8 * s, 16 * k);
      canvas.drawCircle(c, d, Paint()..color = const Color(0xFF1B1326));
      canvas.drawCircle(
        c,
        d,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2 * s
          ..color = gold,
      );
      label(
        e.name,
        c - Offset(0, d + 3 * s),
        size: 14,
        color: gold,
        above: true,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _NetherPainter o) =>
      o.scale != scale ||
      o.ringSel != ringSel ||
      o.selected != selected ||
      o.cs != cs;
}

/// Карта настоящей Земли: контуры суши Natural Earth и державы на местах прообразов.
class _EarthPainter extends CustomPainter {
  final EarthMap earth;
  final Map<String, String> blocs;
  final double extent, scale;
  final MapPoint selected;
  final ColorScheme cs;
  _EarthPainter({
    required this.earth,
    required this.blocs,
    required this.extent,
    required this.scale,
    required this.selected,
    required this.cs,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final k = size.width / (2 * extent);
    Offset p(double x, double z) => Offset((x + extent) * k, (z + extent) * k);
    final s = 1 / scale;
    final b = earth.box;
    final frame = Rect.fromPoints(p(b[0], b[1]), p(b[2], b[3]));
    canvas.save();
    canvas.clipRect(frame);
    canvas.drawRect(
      frame,
      Paint()..color = Color.alphaBlend(const Color(0x662F7FB5), cs.surface),
    );
    final land = Path()..fillType = PathFillType.evenOdd;
    for (final r in earth.land) {
      land.moveTo(
        p(r[0].toDouble(), r[1].toDouble()).dx,
        p(r[0].toDouble(), r[1].toDouble()).dy,
      );
      for (var i = 2; i + 1 < r.length; i += 2) {
        final q = p(r[i].toDouble(), r[i + 1].toDouble());
        land.lineTo(q.dx, q.dy);
      }
      land.close();
    }
    canvas.drawPath(
      land,
      Paint()..color = Color.alphaBlend(const Color(0x8CB9A777), cs.surface),
    );
    canvas.drawPath(
      land,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = .8 * s
        ..color = cs.outline.withValues(alpha: .6),
    );
    Path lines(List<List<int>> l, bool close) {
      final path = Path();
      for (final r in l) {
        final a = p(r[0].toDouble(), r[1].toDouble());
        path.moveTo(a.dx, a.dy);
        for (var i = 2; i + 1 < r.length; i += 2) {
          final q = p(r[i].toDouble(), r[i + 1].toDouble());
          path.lineTo(q.dx, q.dy);
        }
        if (close) path.close();
      }
      return path;
    }

    final water = Color.alphaBlend(const Color(0x662F7FB5), cs.surface);
    canvas.drawPath(lines(earth.lakes, true), Paint()..color = water);
    canvas.drawPath(
      lines(earth.rivers, false),
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.1 * s
        ..strokeJoin = StrokeJoin.round
        ..color = const Color(0xFF5A9CC8),
    );
    final grid = Paint()
      ..color = cs.outlineVariant.withValues(alpha: .5)
      ..strokeWidth = s;
    final kx = math.cos(48 * math.pi / 180) * 111.32;
    for (var lat = 30; lat <= 70; lat += 10) {
      final y = -(lat - 48) * 111.32;
      canvas.drawLine(p(b[0], y), p(b[2], y), grid);
    }
    for (var lon = -10; lon <= 60; lon += 10) {
      final x = (lon - 25) * kx;
      canvas.drawLine(p(x, b[1]), p(x, b[3]), grid);
    }
    canvas.restore();

    void label(
      String txt,
      Offset at, {
      double size = 13,
      Color? color,
      bool italic = false,
    }) {
      final st = TextStyle(
        fontSize: size * s,
        fontWeight: italic ? FontWeight.w600 : FontWeight.w700,
        fontStyle: italic ? FontStyle.italic : FontStyle.normal,
      );
      final o = TextPainter(
        text: TextSpan(
          text: txt,
          style: st.copyWith(
            foreground: Paint()
              ..style = PaintingStyle.stroke
              ..strokeWidth = 3 * s
              ..color = cs.surface,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout();
      final f = TextPainter(
        text: TextSpan(
          text: txt,
          style: st.copyWith(color: color ?? cs.onSurface),
        ),
        textDirection: TextDirection.ltr,
      )..layout();
      final at2 = at - Offset(f.width / 2, 0);
      o.paint(canvas, at2);
      f.paint(canvas, at2);
    }

    for (final e in earth.seas) {
      label(
        e.name,
        p(e.x, e.z),
        size: 11,
        color: const Color(0xFF2F6F9F),
        italic: true,
      );
    }
    for (final e in earth.powers) {
      final col = _hex(e.color, cs.primary);
      canvas.drawCircle(
        p(e.x, e.z),
        260 * k,
        Paint()..color = col.withValues(alpha: e == selected ? .4 : .22),
      );
      canvas.drawCircle(
        p(e.x, e.z),
        math.max(5 * s, 30 * k),
        Paint()..color = col,
      );
      label(e.name, p(e.x, e.z) + Offset(0, 8 * s), size: 13);
    }
  }

  @override
  bool shouldRepaint(covariant _EarthPainter o) =>
      o.scale != scale || o.selected != selected || o.cs != cs;
}
