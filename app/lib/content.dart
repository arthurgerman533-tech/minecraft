import 'dart:convert';

import 'package:flutter/services.dart' show rootBundle;
import 'i18n.dart';

/// Контент берётся из assets/content.json — тот же файл, что у сайта
/// (собирается tools/build_site.py из content/paxvanila.json).
class BorderCfg {
  final int start, w1, w2, w3, w4, w5, w6;
  BorderCfg(Map<String, dynamic> j)
      : start = j['start'], w1 = j['w1'], w2 = j['w2'], w3 = j['w3'],
        w4 = j['w4'], w5 = j['w5'], w6 = j['w6'];
}

class Config {
  final String serverName, serverAddress, discordUrl, mapUrl, launchDate, version;
  final int primeFrom, primeTo;
  final BorderCfg border;
  Config(Map<String, dynamic> j)
      : serverName = j['serverName'] ?? 'PaxVanila',
        serverAddress = j['serverAddress'] ?? '',
        discordUrl = j['discordUrl'] ?? '',
        mapUrl = j['mapUrl'] ?? '',
        launchDate = j['launchDate'] ?? '',
        version = j['version'] ?? '',
        primeFrom = j['primeFrom'] ?? 17,
        primeTo = j['primeTo'] ?? 22,
        border = BorderCfg(j['border']);
}

class Week {
  final int n;
  final String title, days, border, image, text;
  final List<String> commands;
  Week(Map<String, dynamic> j)
      : n = j['n'], title = j['title'], days = j['days'], border = j['border'],
        image = j['image'], text = j['text'], commands = List<String>.from(j['commands']);
  String get imageAsset => 'assets/img/${image.replaceAll('.png', '.jpg')}';
}

class Mechanic {
  final String id, icon, title, summary;
  final List<String> points, commands;
  Mechanic(Map<String, dynamic> j)
      : id = j['id'], icon = j['icon'], title = j['title'], summary = j['summary'],
        points = List<String>.from(j['points']), commands = List<String>.from(j['commands']);
}

class Rule {
  final String title;
  final List<String> items;
  Rule(Map<String, dynamic> j) : title = j['title'], items = List<String>.from(j['items']);
}

class LoreDoc {
  final String id, title, subtitle, dir;
  LoreDoc(Map<String, dynamic> j, {this.dir = 'lore'}) : id = j['id'], title = j['title'], subtitle = j['subtitle'];
  String get asset => 'assets/$dir$assetSuffix/$id.md';
}

class Content {
  final Config config;
  final String tagline;
  final List<Week> weeks;
  final List<Mechanic> mechanics;
  final List<Rule> rules;
  final List<String> join;
  final List<LoreDoc> lore;
  final List<LoreDoc> guides;

  Content(Map<String, dynamic> j)
      : config = Config(j['config']),
        tagline = j['tagline'],
        weeks = (j['weeks'] as List).map((e) => Week(e)).toList(),
        mechanics = (j['mechanics'] as List).map((e) => Mechanic(e)).toList(),
        rules = (j['rules'] as List).map((e) => Rule(e)).toList(),
        join = List<String>.from(j['join']),
        lore = (j['lore'] as List).map((e) => LoreDoc(e)).toList(),
        guides = ((j['guides'] ?? []) as List).map((e) => LoreDoc(e, dir: 'guides')).toList();

  /// Все команды без повторов: (команда, раздел, иконка).
  List<(String, String, String)> get commands {
    final seen = <String>{};
    final out = <(String, String, String)>[];
    for (final m in mechanics) {
      for (final c in m.commands) {
        if (seen.add(c)) out.add((c, m.title, m.icon));
      }
    }
    return out;
  }

  static Future<Content> load() async =>
      Content(jsonDecode(await rootBundle.loadString(isEn ? 'assets/content.en.json' : 'assets/content.json')));
}
