import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import '../content.dart';
import '../i18n.dart';

/// Живые данные paxmeteo.sk (config.liveUrl + имя файла). null — нет адреса или сети, тогда показываем демо.
Future<Map<String, dynamic>?> fetchLive(String base, String name) async {
  if (base.isEmpty) return null;
  try {
    final u = Uri.parse(base.endsWith('/') ? base : '$base/').resolve(name);
    final r = await http.get(u).timeout(const Duration(seconds: 8));
    if (r.statusCode != 200) return null;
    return jsonDecode(utf8.decode(r.bodyBytes)) as Map<String, dynamic>;
  } catch (_) {
    return null;
  }
}

Color _hex(String? h) => Color(int.parse('FF${(h ?? '#888888').substring(1)}', radix: 16));
String _mmss(num s) => '${s ~/ 60}:${(s.toInt() % 60).toString().padLeft(2, '0')}';
String _date(num t) {
  final d = DateTime.fromMillisecondsSinceEpoch(t.toInt() * 1000);
  String p(int v) => v.toString().padLeft(2, '0');
  return '${p(d.day)}.${p(d.month)} ${p(d.hour)}:${p(d.minute)}';
}

Widget demoBadge(BuildContext c) => Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(color: Theme.of(c).colorScheme.error, borderRadius: BorderRadius.circular(99)),
      child: Text(t('ДЕМО', 'DEMO'), style: TextStyle(color: Theme.of(c).colorScheme.onError, fontSize: 11, fontWeight: FontWeight.w700)),
    );

class WeatherView extends StatefulWidget {
  final Content content;
  const WeatherView({super.key, required this.content});
  @override
  State<WeatherView> createState() => _WeatherViewState();
}

class _WeatherViewState extends State<WeatherView> {
  Map<String, dynamic>? live;
  @override
  void initState() {
    super.initState();
    fetchLive(widget.content.config.liveUrl, 'meteo.json').then((v) {
      if (mounted && v != null) setState(() => live = v);
    });
  }

  @override
  Widget build(BuildContext context) {
    final M = widget.content.meteo, D = live ?? widget.content.meteoDemo;
    if (M.isEmpty) return Center(child: Text(t('Нет данных', 'No data')));
    final cs = Theme.of(context).colorScheme;
    final levels = List<Map<String, dynamic>>.from(M['levels']);
    final events = [...List<Map<String, dynamic>>.from(M['events']), ...List<Map<String, dynamic>>.from(M['space'])];
    Map<String, dynamic>? ev(num? n) => events.where((e) => e['n'] == n).firstOrNull;
    Map<String, dynamic> lv(num? n) => levels[(n ?? 0).toInt().clamp(0, levels.length - 1)];
    final cur = (D['event']?['n'] ?? 0) > 0 ? ev(D['event']['n']) : null;
    final pen = (D['pending']?['n'] ?? 0) > 0 ? ev(D['pending']['n']) : null;
    var level = levels[0];
    String head, body;
    if (cur != null) {
      level = lv(cur['level'] ?? 1);
      head = '${cur['icon']} ${t('Действует', 'In effect')}: ${cur['name']}';
      body = '${cur['text'] ?? ''} ${t('Осталось', 'Left')}: ${_mmss(D['event']['left'] ?? 0)}.\n${cur['advice'] ?? ''}';
    } else if (pen != null) {
      level = lv(pen['level'] ?? 1);
      head = '⚠️ ${t('Штормовое предупреждение', 'Storm warning')}: ${pen['icon']} ${pen['name']}';
      body = '${t('Начнётся через', 'Starts in')} ${_mmss(D['pending']['warn'] ?? 0)}. ${pen['advice'] ?? ''}';
    } else {
      head = '✅ ${t('Катаклизмов нет', 'No cataclysms')}';
      final it = M['interval'];
      body = (D['next'] ?? 0) > 0
          ? '${t('Следующий примерно через', 'Next in about')} ${((D['next']) / 60).round()} ${t('мин', 'min')}.'
          : '${t('Катаклизмы приходят раз в', 'Cataclysms come every')} ${it['min']}–${it['max']} ${t('мин', 'min')}.';
    }
    final seasons = List<Map<String, dynamic>>.from(M['seasons']);
    final season = (D['season'] ?? -1) as num;
    final mc = Map<String, dynamic>.from(M['mc']);
    final hist = List<Map<String, dynamic>>.from(D['history'] ?? [])..sort((a, b) => (b['t'] as num).compareTo(a['t'] as num));
    final col = _hex(level['color']);
    Widget section(String s) => Padding(padding: const EdgeInsets.fromLTRB(0, 20, 0, 8), child: Text(s, style: TextStyle(fontWeight: FontWeight.w700, fontSize: 17, color: cs.primary)));
    return ListView(padding: const EdgeInsets.all(16), children: [
      if (D['demo'] == true) Row(children: [demoBadge(context), const SizedBox(width: 8), Expanded(child: Text(t('Демо-данные, живая сводка появится после запуска сервера.', 'Demo data, the live report appears after launch.'), style: TextStyle(color: cs.onSurfaceVariant, fontSize: 13)))]),
      const SizedBox(height: 10),
      Card(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: BorderSide(color: col, width: 2)),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
              decoration: BoxDecoration(color: col, borderRadius: BorderRadius.circular(99)),
              child: Text('${t('Уровень', 'Level')}: ${level['name']} · ${level['text']}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700, fontSize: 12)),
            ),
            const SizedBox(height: 8),
            Text(head, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 17)),
            const SizedBox(height: 4),
            Text(body),
            if (D['demo'] != true && D['updated'] != null) Padding(padding: const EdgeInsets.only(top: 6), child: Text('${t('Обновлено', 'Updated')}: ${_date(D['updated'])}', style: TextStyle(fontSize: 12, color: cs.onSurfaceVariant))),
          ]),
        ),
      ),
      Wrap(spacing: 8, runSpacing: 8, children: [
        for (final x in [
          ('🌦️', t('Погода', 'Weather'), '${mc[D['weather']] ?? D['weather'] ?? '—'}'),
          ('🍂', t('Сезон', 'Season'), season >= 0 && season < seasons.length ? '${seasons[season.toInt()]['name']}' : t('с 28-го дня', 'from day 28')),
          ('📅', t('День', 'Day'), '${(D['day'] ?? 0) > 0 ? D['day'] : '—'}'),
          ('👥', t('Онлайн', 'Online'), '${D['online'] ?? 0}'),
        ])
          Chip(label: Text('${x.$1} ${x.$2}: ${x.$3}')),
      ]),
      section(t('Шкала опасности', 'Danger scale')),
      Wrap(spacing: 8, runSpacing: 8, children: [
        for (final l in levels) Chip(avatar: CircleAvatar(backgroundColor: _hex(l['color']), radius: 7), label: Text('${l['name']}: ${l['text']}')),
      ]),
      section(t('Справочник катаклизмов', 'Cataclysm reference')),
      for (final e in [...List<Map<String, dynamic>>.from(M['events'])]..sort((a, b) => (b['p'] as num).compareTo(a['p'] as num)))
        Card(
          child: ListTile(
            leading: Text('${e['icon']}', style: const TextStyle(fontSize: 24)),
            title: Text('${e['name']} · ${e['p']}%', style: const TextStyle(fontWeight: FontWeight.w600)),
            subtitle: Text('${e['text']}\n${t('Длится', 'Lasts')} ${((e['min'] as num) / 60).round()}–${((e['max'] as num) / 60).round()} ${t('мин', 'min')}. ${e['advice']}'),
            trailing: CircleAvatar(backgroundColor: _hex(lv(e['level'])['color']), radius: 6),
            isThreeLine: true,
          ),
        ),
      section(t('Журнал', 'Log')),
      if (hist.isEmpty) Text(t('Пока ни одного катаклизма.', 'No cataclysms yet.')),
      for (final h in hist) ListTile(dense: true, leading: Text('${ev(h['n'])?['icon'] ?? '•'}'), title: Text('${ev(h['n'])?['name'] ?? '#${h['n']}'}'), trailing: Text(_date(h['t']))),
      section(t('Сезоны', 'Seasons')),
      for (var i = 0; i < seasons.length; i++)
        Card(child: ListTile(title: Text('${seasons[i]['name']}${i == season ? ' · ${t('сейчас', 'now')}' : ''}', style: TextStyle(fontWeight: FontWeight.w600, color: i == season ? cs.primary : null)), subtitle: Text('${seasons[i]['text']}'))),
    ]);
  }
}

class NewsView extends StatefulWidget {
  final Content content;
  const NewsView({super.key, required this.content});
  @override
  State<NewsView> createState() => _NewsViewState();
}

class _NewsViewState extends State<NewsView> {
  Map<String, dynamic>? live;
  String cat = '';
  @override
  void initState() {
    super.initState();
    fetchLive(widget.content.config.liveUrl, 'news.json').then((v) {
      if (mounted && v != null) setState(() => live = v);
    });
  }

  @override
  Widget build(BuildContext context) {
    final W = widget.content.news, N = live ?? widget.content.newsDemo;
    if (W.isEmpty) return Center(child: Text(t('Нет данных', 'No data')));
    final cs = Theme.of(context).colorScheme;
    final cats = Map<String, dynamic>.from(W['categories']);
    final tpl = Map<String, dynamic>.from(W['templates']);
    final demo = N['demo'] == true;
    final found = (List<Map<String, dynamic>>.from(N['items'] ?? [])..sort((a, b) => (b['t'] as num).compareTo(a['t'] as num)))
        .where((x) => tpl.containsKey(x['k']))
        .map((x) {
      final tp = tpl[x['k']];
      return {'cat': tp['cat'], 'icon': tp['icon'], 'title': tp['title'], 'text': '${tp['text']}'.replaceAll('{p}', '${x['p']}'), 'reward': tp['reward'], 'date': _date(x['t'])};
    });
    final lore = List<Map<String, dynamic>>.from(W['items']).map((x) => {...x, 'lore': true});
    final items = [...found, ...lore].where((i) => cat.isEmpty || i['cat'] == cat).toList();
    return ListView(padding: const EdgeInsets.all(16), children: [
      Wrap(spacing: 6, runSpacing: 6, children: [
        ChoiceChip(label: Text(t('Все', 'All')), selected: cat.isEmpty, onSelected: (_) => setState(() => cat = '')),
        for (final c in cats.entries) ChoiceChip(label: Text('${c.value}'), selected: cat == c.key, onSelected: (_) => setState(() => cat = c.key)),
      ]),
      const SizedBox(height: 10),
      for (final i in items)
        Card(
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Wrap(spacing: 8, runSpacing: 4, crossAxisAlignment: WrapCrossAlignment.center, children: [
                Text('${i['icon']} ${cats[i['cat']] ?? ''}', style: TextStyle(fontSize: 12, color: cs.onSurfaceVariant)),
                if (i['lore'] == true) Text(t('лор', 'lore'), style: TextStyle(fontSize: 12, color: cs.primary, fontWeight: FontWeight.w700)) else ...[
                  Text('${i['date']}', style: TextStyle(fontSize: 12, color: cs.onSurfaceVariant)),
                  if (demo) demoBadge(context),
                ],
              ]),
              const SizedBox(height: 6),
              Text('${i['title']}', style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 16)),
              const SizedBox(height: 4),
              Text('${i['text']}'),
              if ('${i['reward'] ?? ''}'.isNotEmpty) Padding(padding: const EdgeInsets.only(top: 8), child: Text('🎁 ${i['reward']}', style: TextStyle(color: cs.onSurfaceVariant))),
            ]),
          ),
        ),
    ]);
  }
}
