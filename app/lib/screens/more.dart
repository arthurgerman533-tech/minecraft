import 'package:flutter/material.dart';

import '../content.dart';
import '../i18n.dart';
import 'lore.dart';
import 'meteo.dart';
import 'widgets.dart';

class MoreScreen extends StatelessWidget {
  final Content content;
  final VoidCallback onLang;
  const MoreScreen({super.key, required this.content, required this.onLang});

  void push(BuildContext ctx, String title, Widget body) =>
      Navigator.of(ctx).push(MaterialPageRoute(builder: (_) => Scaffold(appBar: AppBar(title: Text(title)), body: body)));

  @override
  Widget build(BuildContext context) {
    final cfg = content.config;
    Widget tile(IconData i, String title, String s, VoidCallback onTap) => Padding(
          padding: const EdgeInsets.only(bottom: 10),
          child: Card(child: ListTile(leading: Icon(i), title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600)), subtitle: Text(s), trailing: const Icon(Icons.chevron_right), onTap: onTap)),
        );
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 4, 16, 32),
      children: [
        tile(Icons.thunderstorm_outlined, t('Погода · ПаксГидромет', 'Weather · PaxHydromet'), t('Сводка, предупреждения, катаклизмы', 'Report, warnings, cataclysms'), () => push(context, t('ПаксГидромет', 'PaxHydromet'), WeatherView(content: content))),
        tile(Icons.science_outlined, t('Вестник Академии', 'Academy Herald'), t('Что узнали учёные: находки и данжи', 'What scholars learned: finds and dungeons'), () => push(context, t('Вестник Академии', 'Academy Herald'), NewsView(content: content))),
        for (final g in content.guides)
          tile(Icons.menu_book_outlined, g.title, g.subtitle,
              () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => LoreReader(doc: g)))),
        tile(Icons.translate, t('Язык: русский', 'Language: English'), t('Switch to English', 'Переключить на русский'), onLang),
        tile(Icons.gavel_outlined, t('Правила', 'Rules'), t('Честная игра, войны, ивенты', 'Fair play, wars, events'), () => push(context, t('Правила', 'Rules'), RulesView(content: content))),
        tile(Icons.terminal, t('Команды', 'Commands'), t('Поиск по всем командам сервера', 'Search all server commands'), () => push(context, t('Команды', 'Commands'), CommandsView(content: content))),
        tile(Icons.forum_outlined, 'Discord', t('Новости, объявления войн, катаклизмы', 'News, war declarations, cataclysms'), () => openUrl(context, cfg.discordUrl)),
        if (cfg.boostyUrl.isNotEmpty) tile(Icons.favorite_outline, t('Поддержать на Boosty', 'Support us on Boosty'), t('Помочь с хостингом и развитием сервера', 'Help with hosting and development'), () => openUrl(context, cfg.boostyUrl)),
        if (cfg.mapUrl.isNotEmpty) tile(Icons.map_outlined, t('Карта мира', 'World map'), t('Территории наций на BlueMap', 'Nation territories on BlueMap'), () => openUrl(context, cfg.mapUrl)),
        tile(Icons.privacy_tip_outlined, t('Конфиденциальность', 'Privacy'), t('Приложение не собирает данные', 'The app collects no data'), () => push(context, t('Конфиденциальность', 'Privacy'), const PrivacyView())),
        tile(Icons.info_outline, t('О приложении', 'About'), t('PaxVanila · фанатский сервер', 'PaxVanila · fan server'), () => showAboutDialog(
              context: context,
              applicationName: 'PaxVanila',
              applicationVersion: '1.0.0',
              children: [Text(t('Неофициальное приложение Minecraft-сервера PaxVanila. Не связано с Mojang и Microsoft.', 'Unofficial app of the PaxVanila Minecraft server. Not affiliated with Mojang or Microsoft.'))],
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
          decoration: InputDecoration(prefixIcon: const Icon(Icons.search), hintText: t('claim, война, деньги…', 'claim, war, money…'), border: const OutlineInputBorder()),
          onChanged: (v) => setState(() => q = v),
        ),
      ),
      Expanded(
        child: list.isEmpty
            ? Center(child: Text(t('Ничего не найдено', 'Nothing found')))
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
  Widget build(BuildContext context) => SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Text(isEn ? privacyTextEn : privacyText),
      );
}

const privacyText = '''Политика конфиденциальности приложения PaxVanila

Приложение не требует регистрации и не собирает, не хранит и не передаёт личные данные.

• Все тексты (лор, правила, механики) встроены в приложение.
• Для статуса сервера приложение отправляет адрес игрового сервера в публичный сервис api.mcsrvstat.us. Данные о вас не передаются.
• Выбор темы (светлая/тёмная) и языка хранится только на вашем устройстве.
• Ссылки на Discord и карту открываются во внешнем браузере или приложении; их правила действуют отдельно.
• Рекламы, аналитики и трекеров нет.

Вопросы — в Discord сервера PaxVanila.''';


const privacyTextEn = '''PaxVanila app privacy policy

The app needs no account and does not collect, store or share personal data.

• All texts (lore, rules, mechanics) are built into the app.
• To show the server status, the app sends the game server address to the public service api.mcsrvstat.us. No data about you is sent.
• Your theme (light/dark) and language choice are stored only on your device.
• Links to Discord and the map open in an external browser or app, where their own rules apply.
• There are no ads, analytics or trackers.

Questions: ask in the PaxVanila Discord server.''';
