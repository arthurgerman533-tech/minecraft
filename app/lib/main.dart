import 'dart:ui' show PlatformDispatcher;

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'content.dart';
import 'screens/lore.dart';
import 'screens/map.dart';
import 'screens/mechanics.dart';
import 'screens/more.dart';
import 'screens/now.dart';
import 'screens/weeks.dart';
import 'i18n.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const PaxApp());
}

const gold = Color(0xFFE0B354);
const goldLight = Color(0xFF8A5E0C);

ThemeData buildTheme(Brightness b) {
  final dark = b == Brightness.dark;
  final cs = ColorScheme.fromSeed(
    seedColor: gold,
    brightness: b,
    primary: dark ? gold : goldLight,
    surface: dark ? const Color(0xFF14110D) : const Color(0xFFF4EFE4),
  );
  return ThemeData(
    colorScheme: cs,
    useMaterial3: true,
    scaffoldBackgroundColor: cs.surface,
    cardTheme: CardThemeData(
      elevation: 0,
      color: dark ? const Color(0xFF221D17) : const Color(0xFFFFFAF0),
      shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
          side: BorderSide(color: dark ? const Color(0xFF3A3227) : const Color(0xFFD9CDB5))),
      margin: EdgeInsets.zero,
    ),
    appBarTheme: AppBarTheme(backgroundColor: cs.surface, surfaceTintColor: Colors.transparent, centerTitle: false),
  );
}

class PaxApp extends StatefulWidget {
  const PaxApp({super.key});
  @override
  State<PaxApp> createState() => _PaxAppState();
}

class _PaxAppState extends State<PaxApp> {
  ThemeMode mode = ThemeMode.system;
  Future<Content> content = Content.load();

  @override
  void initState() {
    super.initState();
    SharedPreferences.getInstance().then((p) {
      final m = p.getString('theme');
      if (m != null && mounted) setState(() => mode = ThemeMode.values.byName(m));
      final l = p.getString('lang') ?? (PlatformDispatcher.instance.locale.languageCode == 'ru' ? 'ru' : 'en');
      if (l != lang && mounted) setLang(l, save: false);
    }).catchError((_) {});
  }

  void toggleTheme(BuildContext ctx) {
    final dark = mode == ThemeMode.dark || (mode == ThemeMode.system && MediaQuery.platformBrightnessOf(ctx) == Brightness.dark);
    setState(() => mode = dark ? ThemeMode.light : ThemeMode.dark);
    SharedPreferences.getInstance().then((p) => p.setString('theme', mode.name)).catchError((_) => false);
  }

  void setLang(String l, {bool save = true}) {
    setState(() {
      lang = l;
      content = Content.load();
    });
    if (save) SharedPreferences.getInstance().then((p) => p.setString('lang', l)).catchError((_) => false);
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PaxVanila',
      debugShowCheckedModeBanner: false,
      theme: buildTheme(Brightness.light),
      darkTheme: buildTheme(Brightness.dark),
      themeMode: mode,
      home: FutureBuilder<Content>(
        future: content,
        builder: (ctx, snap) {
          if (snap.hasError) return Scaffold(body: Center(child: Text('${t('Ошибка данных', 'Data error')}: ${snap.error}')));
          if (!snap.hasData) return const Scaffold(body: Center(child: CircularProgressIndicator()));
          return Home(key: ValueKey(lang), content: snap.data!, onTheme: () => toggleTheme(ctx), onLang: () => setLang(isEn ? 'ru' : 'en'));
        },
      ),
    );
  }
}

class Home extends StatefulWidget {
  final Content content;
  final VoidCallback onTheme, onLang;
  const Home({super.key, required this.content, required this.onTheme, required this.onLang});
  @override
  State<Home> createState() => _HomeState();
}

class _HomeState extends State<Home> {
  int tab = 0;
  List<String> get titles => ['PaxVanila', t('Недели', 'Weeks'), t('Карта мира', 'World map'), t('Механики', 'Mechanics'), t('Лор', 'Lore'), t('Ещё', 'More')];

  @override
  Widget build(BuildContext context) {
    final c = widget.content;
    final pages = [NowScreen(content: c), WeeksScreen(content: c), MapScreen(content: c), MechanicsScreen(content: c), LoreList(content: c), MoreScreen(content: c, onLang: widget.onLang)];
    return Scaffold(
      appBar: AppBar(
        title: Text(titles[tab], style: const TextStyle(fontWeight: FontWeight.w700, letterSpacing: .5)),
        actions: [
          TextButton(onPressed: widget.onLang, child: Text(isEn ? 'RU' : 'EN', style: const TextStyle(fontWeight: FontWeight.w700))),
          IconButton(tooltip: t('Тема', 'Theme'), icon: const Icon(Icons.brightness_6_outlined), onPressed: widget.onTheme),
        ],
      ),
      body: IndexedStack(index: tab, children: pages),
      bottomNavigationBar: NavigationBar(
        selectedIndex: tab,
        labelBehavior: NavigationDestinationLabelBehavior.onlyShowSelected,
        onDestinationSelected: (i) => setState(() => tab = i),
        destinations: [
          NavigationDestination(icon: const Icon(Icons.public_outlined), selectedIcon: const Icon(Icons.public), label: t('Сейчас', 'Now')),
          NavigationDestination(icon: const Icon(Icons.calendar_month_outlined), selectedIcon: const Icon(Icons.calendar_month), label: t('Недели', 'Weeks')),
          NavigationDestination(icon: const Icon(Icons.map_outlined), selectedIcon: const Icon(Icons.map), label: t('Карта', 'Map')),
          NavigationDestination(icon: const Icon(Icons.shield_outlined), selectedIcon: const Icon(Icons.shield), label: t('Механики', 'Mechanics')),
          NavigationDestination(icon: const Icon(Icons.auto_stories_outlined), selectedIcon: const Icon(Icons.auto_stories), label: t('Лор', 'Lore')),
          NavigationDestination(icon: const Icon(Icons.menu), label: t('Ещё', 'More')),
        ],
      ),
    );
  }
}
