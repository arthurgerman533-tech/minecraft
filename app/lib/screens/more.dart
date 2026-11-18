import 'package:flutter/material.dart';

import '../content.dart';
import 'lore.dart';
import 'widgets.dart';

class MoreScreen extends StatelessWidget {
  final Content content;
  const MoreScreen({super.key, required this.content});

  void push(BuildContext ctx, String title, Widget body) =>
      Navigator.of(ctx).push(MaterialPageRoute(builder: (_) => Scaffold(appBar: AppBar(title: Text(title)), body: body)));

  @override
  Widget build(BuildContext context) {
    final cfg = content.config;
    Widget tile(IconData i, String t, String s, VoidCallback onTap) => Padding(
          padding: const EdgeInsets.only(bottom: 10),
          child: Card(child: ListTile(leading: Icon(i), title: Text(t, style: const TextStyle(fontWeight: FontWeight.w600)), subtitle: Text(s), trailing: const Icon(Icons.chevron_right), onTap: onTap)),
        );
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 4, 16, 32),
      children: [
        for (final g in content.guides)
          tile(Icons.menu_book_outlined, g.title, g.subtitle,
              () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => LoreReader(doc: g)))),
        tile(Icons.gavel_outlined, 'Правила', 'Честная игра, войны, ивенты', () => push(context, 'Правила', RulesView(content: content))),
        tile(Icons.terminal, 'Команды', 'Поиск по всем командам сервера', () => push(context, 'Команды', CommandsView(content: content))),
        tile(Icons.forum_outlined, 'Discord', 'Новости, объявления войн, катаклизмы', () => openUrl(context, cfg.discordUrl)),
        if (cfg.mapUrl.isNotEmpty) tile(Icons.map_outlined, 'Карта мира', 'Территории наций на BlueMap', () => openUrl(context, cfg.mapUrl)),
        tile(Icons.privacy_tip_outlined, 'Конфиденциальность', 'Приложение не собирает данные', () => push(context, 'Конфиденциальность', const PrivacyView())),
        tile(Icons.info_outline, 'О приложении', 'PaxVanila · фанатский сервер', () => showAboutDialog(
              context: context,
              applicationName: 'PaxVanila',
              applicationVersion: '1.0.0',
              children: const [Text('Неофициальное приложение Minecraft-сервера PaxVanila. Не связано с Mojang и Microsoft.')],
            )),
      ],
    );
  }
}

class RulesView extends StatelessWidget {
  final Content content;
  const RulesView({super.key, required this.content});
  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return ListView(padding: const EdgeInsets.all(16), children: [
      for (var i = 0; i < content.rules.length; i++)
        Padding(
          padding: const EdgeInsets.only(bottom: 10),
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text('${i + 1}. ${content.rules[i].title}', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 17, color: cs.primary)),
                const SizedBox(height: 6),
                for (final it in content.rules[i].items)
                  Padding(padding: const EdgeInsets.only(bottom: 4), child: Text('•  $it')),
              ]),
            ),
          ),
        ),
    ]);
  }
}

class CommandsView extends StatefulWidget {
  final Content content;
  const CommandsView({super.key, required this.content});
  @override
  State<CommandsView> createState() => _CommandsViewState();
}

class _CommandsViewState extends State<CommandsView> {
  String q = '';
  @override
  Widget build(BuildContext context) {
    final all = widget.content.commands;
    final list = all.where((c) => q.isEmpty || '${c.$1} ${c.$2}'.toLowerCase().contains(q.toLowerCase())).toList();
    return Column(children: [
      Padding(
        padding: const EdgeInsets.all(16),
        child: TextField(
          decoration: const InputDecoration(prefixIcon: Icon(Icons.search), hintText: 'claim, война, деньги…', border: OutlineInputBorder()),
          onChanged: (v) => setState(() => q = v),
        ),
      ),
      Expanded(
        child: list.isEmpty
            ? const Center(child: Text('Ничего не найдено'))
            : ListView.builder(
                itemCount: list.length,
                itemBuilder: (_, i) => ListTile(
                  title: Align(alignment: Alignment.centerLeft, child: CmdChip(list[i].$1)),
                  subtitle: Padding(padding: const EdgeInsets.only(top: 4), child: Text('${list[i].$3} ${list[i].$2}')),
                ),
              ),
      ),
    ]);
  }
}

class PrivacyView extends StatelessWidget {
  const PrivacyView({super.key});
  @override
  Widget build(BuildContext context) => const SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Text(privacyText),
      );
}

const privacyText = '''Политика конфиденциальности приложения PaxVanila

Приложение не требует регистрации и не собирает, не хранит и не передаёт личные данные.

• Все тексты (лор, правила, механики) встроены в приложение.
• Для статуса сервера приложение отправляет адрес игрового сервера в публичный сервис api.mcsrvstat.us. Данные о вас не передаются.
• Выбор темы (светлая/тёмная) хранится только на вашем устройстве.
• Ссылки на Discord и карту открываются во внешнем браузере или приложении; их правила действуют отдельно.
• Рекламы, аналитики и трекеров нет.

Вопросы — в Discord сервера PaxVanila.''';
