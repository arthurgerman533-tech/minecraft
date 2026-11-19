import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:paxvanila/screens/map.dart';
import 'package:paxvanila/screens/meteo.dart';
import 'package:paxvanila/screens/chronicle.dart';
import 'dart:convert';
import 'dart:io';
import 'package:paxvanila/calendar.dart';
import 'package:paxvanila/content.dart';
import 'package:paxvanila/md.dart';

Config cfg(String launch) => Config({
      'launchDate': launch,
      'primeFrom': 17,
      'primeTo': 22,
      'border': {'start': 100, 'w1': 500, 'w2': 750, 'w3': 1000, 'w4': 1000, 'w5': 1500, 'w6': 2000},
    });

void main() {
  test('граница как в paxborder.sk', () {
    final b = cfg('').border;
    expect(radiusForDay(b, 0), 100);
    expect(radiusForDay(b, 6), 500);
    expect(radiusForDay(b, 13), 750);
    expect(radiusForDay(b, 27), 1000);
    expect(radiusForDay(b, 41), 2000);
    expect(radiusForDay(b, 100), 2000);
  });

  test('недели, война и сезоны', () {
    final c = cfg('2026-11-01T18:00:00+03:00');
    var s = serverState(c, DateTime.utc(2026, 11, 1, 16));
    expect(s.started, true);
    expect(s.day, 1);
    expect(s.week, 1);
    s = serverState(c, DateTime.utc(2026, 11, 25, 16)); // 24-й день от старта
    expect(s.week, 4);
    expect(s.warPhase, 'Великая война');
    s = serverState(c, DateTime.utc(2026, 12, 6, 16)); // день 35
    expect(s.season, seasons[1].$1);
    s = serverState(c, DateTime.utc(2026, 10, 30));
    expect(s.started, false);
    expect(s.untilDays, 3);
  });

  test('прайм-тайм по МСК', () {
    final c = cfg('');
    expect(serverState(c, DateTime.utc(2026, 11, 18, 15)).prime, true); // 18:00 МСК
    expect(serverState(c, DateTime.utc(2026, 11, 18, 19)).prime, false); // 22:00 МСК
    expect(serverState(c, DateTime.utc(2026, 11, 18, 13)).primeIn, 60);
  });

  test('markdown лора', () {
    final b = parseMarkdown('# Заголовок\n\nТекст **жирный**\n\n> цитата\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n- один\n- два\n\n---');
    expect(b.map((x) => x.type).toList(),
        [BlockType.h1, BlockType.p, BlockType.quote, BlockType.table, BlockType.ul, BlockType.hr]);
    expect(b[3].rows, [['a', 'b'], ['1', '2']]);
    expect(b[4].items, ['один', 'два']);
  });

  testWidgets('карта мира рисуется и выбирает точку', (tester) async {
    final c = Content(jsonDecode(File('assets/content.json').readAsStringSync()));
    expect(c.map.powers.length, 10);
    tester.view.physicalSize = const Size(400, 1400);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: MapScreen(content: c))));
    await tester.pumpAndSettle();
    expect(find.text('Монолит'), findsOneWidget);
    expect(find.byType(CustomPaint), findsWidgets);
    // тап по Карфагену (x -150, z 950) выбирает его
    final box = tester.getRect(find.byType(InteractiveViewer));
    final k = box.width / (2 * 2000 * 1.12);
    await tester.tapAt(box.topLeft + Offset((-150 + 2240) * k, (950 + 2240) * k));
    await tester.pumpAndSettle();
    expect(find.text('Карфаген'), findsOneWidget);
  });

  testWidgets('карта: рельеф, погода и Незер', (tester) async {
    final c = Content(jsonDecode(File('assets/content.json').readAsStringSync()));
    expect(c.map.terrain, isNotNull);
    expect(c.map.nether, isNotNull);
    tester.view.physicalSize = const Size(400, 2400);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: MapScreen(content: c))));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Погода'));
    await tester.pumpAndSettle();
    expect(find.text('Погода на сервере'), findsOneWidget);
    await tester.tap(find.text('Незер'));
    await tester.pumpAndSettle();
    expect(find.text('Великие врата'), findsOneWidget);
    await tester.tap(find.text('Мир 2: Земля'));
    await tester.pumpAndSettle();
    expect(find.text('В реальной истории: Рим.'), findsOneWidget);
  });

  testWidgets('погода и Вестник показывают демо', (tester) async {
    final c = Content(jsonDecode(File('assets/content.json').readAsStringSync()));
    tester.view.physicalSize = const Size(400, 1400);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: WeatherView(content: c))));
    expect(find.textContaining('Штормовое предупреждение'), findsOneWidget);
    expect(find.text('ДЕМО'), findsOneWidget);
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: NewsView(content: c))));
    expect(find.textContaining('Kadim_Ur'), findsOneWidget);
    await tester.tap(find.text('Наука'));
    await tester.pump();
    expect(find.textContaining('Kadim_Ur'), findsNothing);
  });

  test('летопись: записи подготовки, а после старта граница и эпохи', () {
    final j = jsonDecode(File('assets/content.json').readAsStringSync()) as Map<String, dynamic>;
    final c = Content(j);
    expect(c.chronicle.isNotEmpty, true);
    final before = chronicleItems(c, null, DateTime.utc(2026, 11, 20));
    expect(before.every((i) => i.cat == 'prep'), true);
    expect(before.first.key, '2026-11-19');
    final after = chronicleItems(c, {'items': [{'k': 'town', 'a': 'Roma', 'p': 'Romul', 't': 1796000000}]}, DateTime.utc(2026, 12, 30, 12));
    expect(after.any((i) => i.title.contains('Высадка')), true);
    expect(after.any((i) => i.cat == 'border'), true);
    expect(after.any((i) => i.title == 'Основан город Roma'), true);
  });

  testWidgets('экран «Новости сервера» рисуется', (tester) async {
    final c = Content(jsonDecode(File('assets/content.json').readAsStringSync()));
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: ChronicleView(content: c))));
    await tester.pump();
    expect(find.text('Названа дата высадки'), findsOneWidget);
    expect(find.text('19 ноября 2026'), findsOneWidget);
  });
}
