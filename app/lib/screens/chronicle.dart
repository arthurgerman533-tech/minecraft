// «Новости сервера»: летопись по дням (как news.html на сайте). Данные: content.chronicle
// (content/chronicle.json), живые записи — config.liveUrl → chronicle.json из paxchronicle.sk.
import 'package:flutter/material.dart';

import '../calendar.dart';
import '../content.dart';
import '../i18n.dart';
import 'meteo.dart' show fetchLive;

class ChronItem {
  final String key, cat, icon, title, text;
  final num ord;
  final int? time;
  ChronItem(this.key, this.ord, this.cat, this.icon, this.title, this.text, [this.time]);
}

/// Дата дня по Москве (UTC+3), как на сайте.
String _dayKey(DateTime d) => d.toUtc().add(const Duration(hours: 3)).toIso8601String().substring(0, 10);

String _fill(String s, Map<String, Object?> v) => s.replaceAllMapped(RegExp(r'\{(\w)\}'), (m) => v.containsKey(m[1]) ? '${v[m[1]]}' : m[0]!);

String _plural(int n, String a, String b, String c) {
  n = n.abs() % 100;
  final m = n % 10;
  return n > 10 && n < 20 ? c : m == 1 ? a : m >= 2 && m <= 4 ? b : c;
}

const _monthsRu = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
const _monthsEn = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
String _dateText(String key) {
  final p = key.split('-').map(int.parse).toList();
  return isEn ? '${p[2]} ${_monthsEn[p[1] - 1]} ${p[0]}' : '${p[2]} ${_monthsRu[p[1] - 1]} ${p[0]}';
}

List<ChronItem> chronicleItems(Content c, Map<String, dynamic>? live, [DateTime? now]) {
  final X = c.chronicle, cfg = c.config, out = <ChronItem>[];
  if (X.isEmpty) return out;
  final entries = List<Map<String, dynamic>>.from(X['entries'] ?? []);
  for (var i = 0; i < entries.length; i++) {
    final e = entries[i];
    out.add(ChronItem(e['date'], 1e6 - i, e['cat'], e['icon'], e['title'], e['text']));
  }
  final t0 = DateTime.tryParse(cfg.launchDate);
  if (t0 != null) {
    now ??= DateTime.now();
    final days = now.difference(t0).inMinutes / 1440;
    at(int d) => _dayKey(t0.add(Duration(days: d)));
    final B = Map<String, dynamic>.from(X['border']);
    final lines = List<String>.from(B['lines']);
    for (var d = 1; d <= days.floor() && d <= 41; d++) {
      final r = radiusForDay(cfg.border, d), r0 = radiusForDay(cfg.border, d - 1);
      if (r > r0) out.add(ChronItem(at(d), d * 10 + 1, 'border', '🧭', B['title'], _fill(lines[d % lines.length], {'n': r, 'd': r - r0})));
    }
    for (final e in List<Map<String, dynamic>>.from(X['calendar'] ?? [])) {
      final d = (e['day'] as num).toInt();
      if (d - 1 <= days.floor() && days >= 0) out.add(ChronItem(at(d - 1), d * 10 + 5, e['cat'], e['icon'], e['title'], e['text']));
    }
    final S = Map<String, dynamic>.from(X['seasons']);
    for (var d = 35; d <= days.floor(); d += 7) {
      final s = seasons[((d - 28) ~/ 7) % 4];
      out.add(ChronItem(at(d), d * 10 + 4, 'epoch', '🍂', S['title'], _fill(S['text'], {'a': t(s.$1, s.$2)})));
    }
  }
  final tpl = Map<String, dynamic>.from(X['templates'] ?? {});
  for (final x in List<Map<String, dynamic>>.from(live?['items'] ?? [])) {
    final tp = tpl[x['k']];
    if (tp == null || x['t'] == null) continue;
    final ts = (x['t'] as num).toInt();
    final v = {'a': x['a'] ?? '', 'b': x['b'] ?? '', 'n': x['n'] ?? '', 'p': x['p'] ?? '', 'm': '${x['m'] ?? ''}'.replaceFirst(RegExp(r'^\[[^\]]*\]\s*'), '')};
    out.add(ChronItem(_dayKey(DateTime.fromMillisecondsSinceEpoch(ts * 1000)), ts, tp['cat'], tp['icon'], _fill(tp['title'], v), _fill(tp['text'], v), ts));
  }
  out.sort((a, b) => a.key != b.key ? b.key.compareTo(a.key) : b.ord.compareTo(a.ord));
  return out;
}

class ChronicleView extends StatefulWidget {
  final Content content;
  const ChronicleView({super.key, required this.content});
  @override
  State<ChronicleView> createState() => _ChronicleViewState();
}

class _ChronicleViewState extends State<ChronicleView> {
  Map<String, dynamic>? live;
  String cat = '';
  @override
  void initState() {
    super.initState();
    fetchLive(widget.content.config.liveUrl, 'chronicle.json').then((v) {
      if (mounted && v != null) setState(() => live = v);
    });
  }

  String _sub(String key) {
    final t0 = DateTime.tryParse(widget.content.config.launchDate);
    if (t0 == null) return '';
    final n = DateTime.parse('${key}T00:00:00Z').difference(DateTime.parse('${_dayKey(t0)}T00:00:00Z')).inDays;
    return n >= 0 ? t('День ${n + 1} сервера', 'Server day ${n + 1}') : t('За ${-n} ${_plural(-n, 'день', 'дня', 'дней')} до высадки', '${-n} day${-n == 1 ? '' : 's'} before landfall');
  }

  @override
  Widget build(BuildContext context) {
    final c = widget.content, X = c.chronicle;
    if (X.isEmpty) return Center(child: Text(t('Нет данных', 'No data')));
    final cs = Theme.of(context).colorScheme;
    final cats = Map<String, dynamic>.from(X['categories']);
    final ui = Map<String, dynamic>.from(X['ui']);
    final all = chronicleItems(c, live);
    final items = all.where((i) => cat.isEmpty || i.cat == cat).toList();
    final st = serverState(c.config);
    final state = st.started
        ? t('Сегодня день ${st.day}, граница ${st.radius}', 'Today is day ${st.day}, border ${st.radius}')
        : st.untilDays != null
            ? t('До высадки ${st.untilDays} ${_plural(st.untilDays!, 'день', 'дня', 'дней')}', 'Landfall in ${st.untilDays} day${st.untilDays == 1 ? '' : 's'}')
            : t('Дата открытия скоро', 'Launch date coming soon');
    final rows = <Widget>[
      Text('${ui['lead']}', style: TextStyle(color: cs.onSurfaceVariant)),
      const SizedBox(height: 10),
      Chip(label: Text(state)),
      const SizedBox(height: 6),
      Wrap(spacing: 6, runSpacing: 6, children: [
        ChoiceChip(label: Text(t('Все', 'All')), selected: cat.isEmpty, onSelected: (_) => setState(() => cat = '')),
        for (final e in cats.entries)
          if (all.any((i) => i.cat == e.key)) ChoiceChip(label: Text('${e.value}'), selected: cat == e.key, onSelected: (_) => setState(() => cat = e.key)),
      ]),
    ];
    String? last;
    for (final i in items) {
      if (i.key != last) {
        last = i.key;
        final s = _sub(i.key);
        rows.add(Padding(
          padding: const EdgeInsets.only(top: 18, bottom: 6),
          child: Wrap(spacing: 10, crossAxisAlignment: WrapCrossAlignment.end, children: [
            Text(_dateText(i.key), style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18, color: cs.primary)),
            if (s.isNotEmpty) Text(s, style: TextStyle(fontSize: 13, color: cs.onSurfaceVariant)),
          ]),
        ));
      }
      rows.add(Card(
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text('${i.icon} ${cats[i.cat] ?? ''}${i.time != null ? ' · ${TimeOfDay.fromDateTime(DateTime.fromMillisecondsSinceEpoch(i.time! * 1000)).format(context)}' : ''}',
                style: TextStyle(fontSize: 12, color: cs.onSurfaceVariant)),
            const SizedBox(height: 6),
            Text(i.title, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 16)),
            const SizedBox(height: 4),
            Text(i.text),
          ]),
        ),
      ));
    }
    return ListView(padding: const EdgeInsets.all(16), children: rows);
  }
}
