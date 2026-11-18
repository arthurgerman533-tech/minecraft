import 'package:flutter/material.dart';

import '../calendar.dart';
import '../content.dart';
import 'widgets.dart';
import '../i18n.dart';

class WeeksScreen extends StatelessWidget {
  final Content content;
  const WeeksScreen({super.key, required this.content});

  @override
  Widget build(BuildContext context) {
    final st = serverState(content.config);
    final th = Theme.of(context);
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 4, 16, 32),
      children: [
        Text(t('Граница мира растёт понемногу каждый день. Каждая неделя открывает новое.', 'The world border grows a little every day. Every week unlocks something new.'),
            style: th.textTheme.bodyMedium!.copyWith(color: th.colorScheme.onSurfaceVariant)),
        const SizedBox(height: 12),
        for (final w in content.weeks)
          Padding(
            padding: const EdgeInsets.only(bottom: 14),
            child: Card(
              clipBehavior: Clip.antiAlias,
              shape: st.started && st.week == w.n
                  ? RoundedRectangleBorder(borderRadius: BorderRadius.circular(14), side: BorderSide(color: th.colorScheme.primary, width: 2))
                  : null,
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                AspectRatio(aspectRatio: 16 / 9, child: Image.asset(w.imageAsset, fit: BoxFit.cover)),
                Padding(
                  padding: const EdgeInsets.all(14),
                  child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Text('${t('Неделя', 'Week')} ${w.n} · ${w.days} · ${t('граница', 'border')} ${w.border}${st.started && st.week == w.n ? t(' · сейчас', ' · now') : ''}',
                        style: th.textTheme.labelMedium!.copyWith(color: th.colorScheme.primary, fontWeight: FontWeight.w700)),
                    const SizedBox(height: 4),
                    Text(w.title, style: th.textTheme.titleLarge!.copyWith(fontWeight: FontWeight.w700)),
                    const SizedBox(height: 6),
                    Text(w.text),
                    const SizedBox(height: 10),
                    cmdWrap(w.commands),
                  ]),
                ),
              ]),
            ),
          ),
      ],
    );
  }
}
