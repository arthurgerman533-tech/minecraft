import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../calendar.dart';
import '../content.dart';
import '../status.dart';
import 'widgets.dart';

class NowScreen extends StatefulWidget {
  final Content content;
  const NowScreen({super.key, required this.content});
  @override
  State<NowScreen> createState() => _NowScreenState();
}

class _NowScreenState extends State<NowScreen> {
  ServerStatus? status;
  bool loading = false;
  Timer? timer;

  @override
  void initState() {
    super.initState();
    refresh();
    timer = Timer.periodic(const Duration(seconds: 30), (_) => setState(() {}));
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }

  Future<void> refresh() async {
    setState(() => loading = true);
    final s = await fetchStatus(widget.content.config.serverAddress);
    if (mounted) {
      setState(() {
        status = s;
        loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final c = widget.content, cfg = c.config, st = serverState(cfg);
    final cs = Theme.of(context).colorScheme;
    final tiles = <Widget>[
      _Stat(
        label: 'Сервер',
        value: cfg.serverAddress.isEmpty
            ? 'Скоро'
            : loading
                ? '…'
                : status == null
                    ? 'Нет данных'
                    : status!.online
                        ? '${status!.players}/${status!.max} онлайн'
                        : 'Офлайн',
        sub: cfg.serverAddress.isEmpty ? 'адрес появится перед открытием' : cfg.serverAddress,
        dot: status?.online,
      ),
      _Stat(
        label: 'Окно боёв ${cfg.primeFrom}–${cfg.primeTo} МСК',
        value: st.prime ? '⚔️ Открыто' : '🕊️ Закрыто',
        sub: '${st.prime ? 'закроется' : 'откроется'} через ${fmtMinutes(st.primeIn)}',
      ),
      if (st.started) ...[
        _Stat(label: 'День сезона', value: '${st.day}', sub: 'Неделя ${st.week}: ${c.weeks.firstWhere((w) => w.n == st.week).title}'),
        _Stat(label: 'Граница мира', value: '${st.radius} блоков', sub: 'завтра ${st.tomorrow}'),
        if (st.warPhase != null) _Stat(label: 'Эпоха государств', value: st.warPhase!),
        if (st.season != null) _Stat(label: 'Сезон', value: st.season!),
      ] else
        _Stat(label: 'Открытие', value: st.untilDays != null ? 'через ${st.untilDays} дн.' : 'скоро', sub: 'следите в Discord'),
    ];

    return RefreshIndicator(
      onRefresh: refresh,
      child: ListView(
        padding: const EdgeInsets.fromLTRB(16, 0, 16, 32),
        children: [
          const SizedBox(height: 8),
          Text(c.tagline, style: Theme.of(context).textTheme.bodyLarge),
          const SizedBox(height: 16),
          Wrap(spacing: 10, runSpacing: 10, children: [
            FilledButton.icon(
              onPressed: cfg.serverAddress.isEmpty
                  ? null
                  : () {
                      Clipboard.setData(ClipboardData(text: cfg.serverAddress));
                      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Адрес скопирован')));
                    },
              icon: const Icon(Icons.copy),
              label: Text(cfg.serverAddress.isEmpty ? 'Адрес скоро' : cfg.serverAddress),
            ),
            OutlinedButton.icon(onPressed: () => openUrl(context, cfg.discordUrl), icon: const Icon(Icons.forum_outlined), label: const Text('Discord')),
            if (cfg.mapUrl.isNotEmpty)
              OutlinedButton.icon(onPressed: () => openUrl(context, cfg.mapUrl), icon: const Icon(Icons.map_outlined), label: const Text('Карта')),
          ]),
          const Kicker('Сервер сегодня'),
          LayoutBuilder(builder: (ctx, box) {
            final cols = box.maxWidth > 700 ? 3 : 2;
            final w = (box.maxWidth - 10 * (cols - 1)) / cols;
            return Wrap(spacing: 10, runSpacing: 10, children: [for (final t in tiles) SizedBox(width: w, child: t)]);
          }),
          const Kicker('Как зайти'),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                for (var i = 0; i < c.join.length; i++)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                      CircleAvatar(radius: 11, backgroundColor: cs.primary, child: Text('${i + 1}', style: TextStyle(fontSize: 12, color: cs.onPrimary))),
                      const SizedBox(width: 10),
                      Expanded(child: Text(c.join[i])),
                    ]),
                  ),
              ]),
            ),
          ),
        ],
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  final String label, value;
  final String? sub;
  final bool? dot;
  const _Stat({required this.label, required this.value, this.sub, this.dot});
  @override
  Widget build(BuildContext context) {
    final th = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(label.toUpperCase(), style: th.textTheme.labelSmall!.copyWith(letterSpacing: 1, color: th.colorScheme.onSurfaceVariant)),
          const SizedBox(height: 4),
          Row(children: [
            if (dot != null)
              Container(
                  width: 10,
                  height: 10,
                  margin: const EdgeInsets.only(right: 6),
                  decoration: BoxDecoration(shape: BoxShape.circle, color: dot! ? Colors.green : Colors.red)),
            Flexible(child: Text(value, style: th.textTheme.titleLarge!.copyWith(fontWeight: FontWeight.w700))),
          ]),
          if (sub != null) Text(sub!, style: th.textTheme.bodySmall!.copyWith(color: th.colorScheme.onSurfaceVariant)),
        ]),
      ),
    );
  }
}
