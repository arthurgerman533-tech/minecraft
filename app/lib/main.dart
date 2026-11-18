import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'content.dart';
import 'screens/lore.dart';
import 'screens/mechanics.dart';
import 'screens/more.dart';
import 'screens/now.dart';
import 'screens/weeks.dart';

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

  @override
  void initState() {
    super.initState();
    SharedPreferences.getInstance().then((p) {
      final m = p.getString('theme');
      if (m != null && mounted) setState(() => mode = ThemeMode.values.byName(m));
    }).catchError((_) {});
  }

  void toggleTheme(BuildContext ctx) {
    final dark = mode == ThemeMode.dark || (mode == ThemeMode.system && MediaQuery.platformBrightnessOf(ctx) == Brightness.dark);
    setState(() => mode = dark ? ThemeMode.light : ThemeMode.dark);
    SharedPreferences.getInstance().then((p) => p.setString('theme', mode.name)).catchError((_) => false);
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
        future: Content.load(),
        builder: (ctx, snap) {
          if (snap.hasError) return Scaffold(body: Center(child: Text('Ошибка данных: ${snap.error}')));
          if (!snap.hasData) return const Scaffold(body: Center(child: CircularProgressIndicator()));
          return Home(content: snap.data!, onTheme: () => toggleTheme(ctx));
        },
      ),
    );
  }
}

class Home extends StatefulWidget {
  final Content content;
  final VoidCallback onTheme;
  const Home({super.key, required this.content, required this.onTheme});
  @override
  State<Home> createState() => _HomeState();
}

class _HomeState extends State<Home> {
  int tab = 0;
  static const titles = ['PaxVanila', 'Недели', 'Механики', 'Лор', 'Ещё'];

  @override
  Widget build(BuildContext context) {
    final c = widget.content;
    final pages = [NowScreen(content: c), WeeksScreen(content: c), MechanicsScreen(content: c), LoreList(content: c), MoreScreen(content: c)];
    return Scaffold(
      appBar: AppBar(
        title: Text(titles[tab], style: const TextStyle(fontWeight: FontWeight.w700, letterSpacing: .5)),
        actions: [IconButton(tooltip: 'Тема', icon: const Icon(Icons.brightness_6_outlined), onPressed: widget.onTheme)],
      ),
      body: IndexedStack(index: tab, children: pages),
      bottomNavigationBar: NavigationBar(
        selectedIndex: tab,
        onDestinationSelected: (i) => setState(() => tab = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.public_outlined), selectedIcon: Icon(Icons.public), label: 'Сейчас'),
          NavigationDestination(icon: Icon(Icons.calendar_month_outlined), selectedIcon: Icon(Icons.calendar_month), label: 'Недели'),
          NavigationDestination(icon: Icon(Icons.shield_outlined), selectedIcon: Icon(Icons.shield), label: 'Механики'),
          NavigationDestination(icon: Icon(Icons.auto_stories_outlined), selectedIcon: Icon(Icons.auto_stories), label: 'Лор'),
          NavigationDestination(icon: Icon(Icons.menu), label: 'Ещё'),
        ],
      ),
    );
  }
}
