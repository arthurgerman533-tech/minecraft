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
      itemCount: content.mechanics.length,
      separatorBuilder: (_, _) => const SizedBox(height: 10),
      itemBuilder: (ctx, i) {
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
