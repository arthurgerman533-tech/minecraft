import 'package:flutter/material.dart';

import '../content.dart';
import '../i18n.dart';

/// «Державы и игроки»: те же данные, что таблица #nations на сайте (content.roster).
class NationsView extends StatefulWidget {
  final Content content;
  const NationsView({super.key, required this.content});
  @override
  State<NationsView> createState() => _NationsViewState();
}

Color _hex(String? h) {
  final v = int.tryParse((h ?? '').replaceFirst('#', ''), radix: 16);
  return v == null ? Colors.grey : Color(0xFF000000 | v);
}

class _NationsViewState extends State<NationsView> {
  String filter = '';
  bool byTowns = false;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final r = widget.content.roster;
    final rows = [for (final e in (r['rows'] ?? const []) as List) Map<String, dynamic>.from(e)];
    final text = Map<String, dynamic>.from(r['text'] ?? {});
    final blocs = {...widget.content.map.blocs, 'new': t('Новые державы', 'New powers')};
    int towns(Map<String, dynamic> x) => (x['towns'] as List).length;
    bool taken(Map<String, dynamic> x) => x['status'] == 'taken' || x['status'] == 'new';
    final players = {for (final x in rows) ...List<String>.from(x['players'] ?? const [])}.length;
    final totalTowns = rows.fold<int>(0, (a, x) => a + towns(x));
    final totalRes = rows.fold<int>(0, (a, x) => a + (x['residents'] as num).toInt());
    var list = rows.where((x) => filter.isEmpty || (filter.startsWith('b:') ? x['bloc'] == filter.substring(2) : filter == 'taken' ? taken(x) : x['status'] == filter)).toList();
    if (byTowns) list.sort((a, b) => towns(b) != towns(a) ? towns(b) - towns(a) : (b['residents'] as num).compareTo(a['residents'] as num));
    final filters = [('', t('Все', 'All')), ('open', t('Свободные', 'Free')), ('taken', t('Занятые', 'Taken')),
      for (final e in blocs.entries) if (rows.any((x) => x['bloc'] == e.key)) ('b:${e.key}', e.value)];

    Widget stat(String n, String l) => Expanded(
        child: Card(
            child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
                child: Column(children: [
                  Text(n, style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700, color: cs.primary)),
                  Text(l, style: TextStyle(fontSize: 12, color: cs.onSurfaceVariant), textAlign: TextAlign.center),
                ]))));
    Widget status(String s) {
      final (label, color) = switch (s) {
        'taken' => (t('Занята', 'Taken'), Colors.green),
        'new' => (t('Новая', 'New'), Colors.deepPurple),
        'closed' => (t('Закрыта', 'Closed'), Colors.grey),
        _ => (t('Свободна', 'Free'), cs.primary),
      };
      return Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
          decoration: BoxDecoration(border: Border.all(color: color), borderRadius: BorderRadius.circular(99)),
          child: Text(label, style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.w600)));
    }

    return ListView(padding: const EdgeInsets.fromLTRB(12, 12, 12, 32), children: [
      if ((text['sub'] ?? '').toString().isNotEmpty) Padding(padding: const EdgeInsets.fromLTRB(4, 0, 4, 10), child: Text(text['sub'])),
      Row(children: [
        stat('${rows.where(taken).length}/${rows.length}', t('занято', 'taken')),
        stat('$players', t('игроков', 'players')),
        stat('$totalTowns', t('городов', 'towns')),
        stat('$totalRes', t('жителей', 'residents')),
      ]),
      const SizedBox(height: 6),
      Wrap(spacing: 6, runSpacing: 6, children: [
        for (final (k, l) in filters) ChoiceChip(label: Text(l), selected: filter == k, onSelected: (_) => setState(() => filter = k)),
        FilterChip(label: Text(t('По городам ↓', 'By towns ↓')), selected: byTowns, onSelected: (v) => setState(() => byTowns = v)),
      ]),
      const SizedBox(height: 8),
      for (final x in list)
        Card(
          clipBehavior: Clip.antiAlias,
          child: Container(
            decoration: BoxDecoration(border: Border(left: BorderSide(color: _hex(x['color']), width: 4))),
            child: ExpansionTile(
              leading: CircleAvatar(radius: 7, backgroundColor: _hex(x['color'])),
              title: Text(x['name'], style: const TextStyle(fontWeight: FontWeight.w700)),
              subtitle: Text([
                if (x['full'] != x['name']) x['full'],
                '${t('Правитель', 'Ruler')}: ${(x['ruler'] ?? '').toString().isEmpty ? '—' : x['ruler']}',
                '${t('Города', 'Towns')}: ${towns(x)} · ${t('жители', 'residents')}: ${x['residents']}',
              ].join('\n')),
              trailing: status(x['status'] ?? 'open'),
              childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
              expandedCrossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(blocs[x['bloc']] ?? '', style: TextStyle(color: cs.onSurfaceVariant)),
                if ((x['note'] ?? '').toString().isNotEmpty) Padding(padding: const EdgeInsets.only(top: 6), child: Text(x['note'])),
                if ((x['players'] as List).isNotEmpty) Padding(padding: const EdgeInsets.only(top: 6), child: Text('${t('Игроки', 'Players')}: ${(x['players'] as List).join(', ')}')),
                if (towns(x) > 0) ...[
                  Padding(padding: const EdgeInsets.only(top: 6), child: Text('${t('Столица', 'Capital')}: ${x['capital']}', style: const TextStyle(fontWeight: FontWeight.w600))),
                  for (final tw in x['towns'] as List)
                    Text('•  ${tw['name']}${tw['name'] == x['capital'] ? ' ★' : ''} · ${t('мэр', 'mayor')} ${tw['mayor'] ?? '—'} · ${tw['residents']} ${t('жит.', 'res.')}'),
                ] else
                  Padding(
                      padding: const EdgeInsets.only(top: 6),
                      child: Text(x['status'] == 'open' ? t('Держава свободна. Её можно занять.', 'This power is free to claim.') : t('Городов пока нет. Они появятся после старта сервера.', 'No towns yet. They will appear after the server opens.'),
                          style: TextStyle(color: cs.onSurfaceVariant))),
              ],
            ),
          ),
        ),
      if ((text['join'] ?? '').toString().isNotEmpty) Padding(padding: const EdgeInsets.fromLTRB(4, 10, 4, 0), child: Text(text['join'], style: TextStyle(color: cs.onSurfaceVariant, fontSize: 13))),
    ]);
  }
}
