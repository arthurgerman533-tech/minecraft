import 'package:flutter/material.dart';

import '../content.dart';
import 'widgets.dart';

class MechanicsScreen extends StatelessWidget {
  final Content content;
  const MechanicsScreen({super.key, required this.content});

  @override
  Widget build(BuildContext context) {
    final th = Theme.of(context);
    return ListView.separated(
      padding: const EdgeInsets.fromLTRB(16, 4, 16, 32),
      itemCount: content.mechanics.length + (content.donate.isEmpty ? 0 : 1),
      separatorBuilder: (_, _) => const SizedBox(height: 10),
      itemBuilder: (ctx, i) {
        if (i == content.mechanics.length) return DonateCard(donate: content.donate, url: content.config.donateUrl);
        final m = content.mechanics[i];
        return Card(
          clipBehavior: Clip.antiAlias,
          child: ExpansionTile(
            shape: const Border(),
            leading: Text(m.icon, style: const TextStyle(fontSize: 26)),
            title: Text(m.title, style: const TextStyle(fontWeight: FontWeight.w700)),
            subtitle: Text(m.summary),
            childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            expandedCrossAxisAlignment: CrossAxisAlignment.start,
            children: [
              for (final p in m.points)
                Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Text('•  ', style: TextStyle(color: th.colorScheme.primary, fontWeight: FontWeight.w700)),
                    Expanded(child: Text(p)),
                  ]),
                ),
              if (m.commands.isNotEmpty) ...[const SizedBox(height: 6), cmdWrap(m.commands)],
            ],
          ),
        );
      },
    );
  }
}

/// Блок «Поддержать сервер»: тарифы Житель / Меценат / Бог. Кнопка активна, только когда задан config.donateUrl.
class DonateCard extends StatelessWidget {
  final Map<String, dynamic> donate;
  final String url;
  const DonateCard({super.key, required this.donate, required this.url});

  @override
  Widget build(BuildContext context) {
    final th = Theme.of(context);
    final gold = th.colorScheme.primary;
    final tiers = (donate['tiers'] ?? []) as List;
    final soon = (donate['soon'] ?? '') as String;
    final note = (donate['note'] ?? '') as String;
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: BorderSide(color: gold)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            const Text('💛', style: TextStyle(fontSize: 26)),
            const SizedBox(width: 10),
            Expanded(child: Text('${donate['title'] ?? ''}', style: th.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700))),
          ]),
          const SizedBox(height: 8),
          Text('${donate['text'] ?? ''}'),
          for (final raw in tiers) ...[
            const SizedBox(height: 12),
            _tier(context, Map<String, dynamic>.from(raw as Map), gold, soon),
          ],
          if (note.isNotEmpty) ...[const SizedBox(height: 10), Text(note, style: th.textTheme.bodySmall)],
        ]),
      ),
    );
  }

  Widget _tier(BuildContext context, Map<String, dynamic> t, Color gold0, String soon) {
    final th = Theme.of(context);
    final id = '${t['id'] ?? ''}';
    final gold = id == 'satan' ? const Color(0xFFB3261E) : gold0;
    final big = id == 'angel' || id == 'satan';
    final button = '${t['button'] ?? ''}';
    final items = List<String>.from(t['items'] ?? const []);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: id == 'free' ? th.dividerColor : gold, width: big ? 2 : 1),
        color: big ? gold.withValues(alpha: 0.08) : null,
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('${t['name'] ?? ''}', style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 17)),
        Text('${t['price'] ?? ''}', style: TextStyle(color: gold, fontWeight: FontWeight.w600)),
        const SizedBox(height: 6),
        for (final p in items)
          Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('•  ', style: TextStyle(color: gold, fontWeight: FontWeight.w700)),
              Expanded(child: Text(p)),
            ]),
          ),
        if (button.isNotEmpty) ...[
          const SizedBox(height: 8),
          SizedBox(
            width: double.infinity,
            child: FilledButton(onPressed: url.isEmpty ? null : () => openUrl(context, url), child: Text(button)),
          ),
          if (url.isEmpty && soon.isNotEmpty) Padding(padding: const EdgeInsets.only(top: 6), child: Text(soon, style: th.textTheme.bodySmall)),
        ],
      ]),
    );
  }
}
