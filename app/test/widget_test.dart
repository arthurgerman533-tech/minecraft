import 'package:flutter_test/flutter_test.dart';
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
}
