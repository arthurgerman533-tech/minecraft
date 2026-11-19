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
  final String serverName, serverAddress, discordUrl, boostyUrl, mapUrl, launchDate, version, liveUrl;
  final int primeFrom, primeTo;
  final BorderCfg border;
  Config(Map<String, dynamic> j)
      : serverName = j['serverName'] ?? 'PaxVanila',
        serverAddress = j['serverAddress'] ?? '',
        discordUrl = j['discordUrl'] ?? '',
        boostyUrl = j['boostyUrl'] ?? '',
        mapUrl = j['mapUrl'] ?? '',
        launchDate = j['launchDate'] ?? '',
        version = j['version'] ?? '',
        liveUrl = j['liveUrl'] ?? '',
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

/// Карта мира: content/map.json (+ map_towns.json), см. tools/build_site.py.
class MapPoint {
  final String id, name, text, color, bloc, cat, kind, lore, real;
  final double x, z;
  final List<List<int>> blocks;
  MapPoint(Map<String, dynamic> j)
      : id = j['id'] ?? j['name'] ?? '',
        name = j['name'] ?? '',
        text = j['text'] ?? '',
        color = j['color'] ?? '',
        bloc = j['bloc'] ?? '',
        cat = j['cat'] ?? '',
        kind = j['kind'] ?? '',
        lore = j['lore'] ?? '',
        real = j['real'] ?? '',
        x = (j['x'] as num).toDouble(),
        z = (j['z'] as num).toDouble(),
        blocks = [for (final b in (j['blocks'] ?? []) as List) List<int>.from(b)];
}

/// Настоящая карта мира (tools/render_world.py): картинка сверху и зоны погоды.
class Terrain {
  final String asset, date;
  /// края картинки в блоках: x0, z0, x1, z1
  final double x0, z0, x1, z1;
  Terrain(Map<String, dynamic> j)
      : asset = 'assets/${j['src']}',
        date = j['date'] ?? '',
        x0 = ((j['bounds'] as List)[0] as num).toDouble(),
        z0 = ((j['bounds'] as List)[1] as num).toDouble(),
        x1 = ((j['bounds'] as List)[2] as num).toDouble(),
        z1 = ((j['bounds'] as List)[3] as num).toDouble();
}

/// Карта настоящей Земли (tools/make_earth.py): км от 25°E 48°N, x на восток, z на юг.
class EarthMap {
  final List<double> box;
  final List<List<int>> land;
  final List<MapPoint> powers, seas;
  EarthMap(Map<String, dynamic> j)
      : box = [for (final v in j['box'] as List) (v as num).toDouble()],
        land = [for (final r in j['land'] as List) List<int>.from(r)],
        powers = WorldMap._pts(j['powers']),
        seas = [
          for (final s in (j['seas'] ?? []) as List)
            MapPoint({'name': s['name'], 'x': s['x'], 'z': s['z'] ?? s['y']}),
        ];
}

/// Карта Незера: координаты Незера (1 блок = 8 наверху).
class NetherMap {
  final List<MapPoint> places, sites, roads;
  final String roadName, roadText;
  NetherMap(Map<String, dynamic> j)
      : places = WorldMap._pts(j['places']),
        sites = WorldMap._pts(j['sites']),
        roads = WorldMap._pts(j['roads']),
        roadName = j['roadName'] ?? '',
        roadText = j['roadText'] ?? '';
}

class WorldMap {
  final List<MapPoint> places, powers, ancient, towns, lore, far;
  final Map<String, String> blocs;
  final String townsDate;
  final Terrain? terrain;
  /// зоны 64×64 блока: desert, water, peaks, snow → список [x, z] левого верхнего угла
  final Map<String, List<List<int>>> zones;
  final int zoneCell;
  final NetherMap? nether;
  final EarthMap? earth;
  WorldMap(Map<String, dynamic> j)
      : places = _pts(j['places']),
        powers = _pts(j['powers']),
        ancient = _pts(j['ancient']),
        towns = _pts(j['towns']),
        lore = _pts(j['lore']),
        far = _pts(j['far']),
        blocs = Map<String, String>.from(j['blocs'] ?? {}),
        townsDate = j['townsDate'] ?? '',
        terrain = j['terrain'] == null ? null : Terrain(j['terrain']),
        zoneCell = ((j['zones'] ?? {})['cell'] ?? 64) as int,
        zones = {
          for (final e in ((j['zones'] ?? {}) as Map<String, dynamic>).entries)
            if (e.value is List) e.key: [for (final c in e.value as List) List<int>.from(c)],
        },
        nether = j['nether'] == null ? null : NetherMap(j['nether']),
        earth = j['earth'] == null ? null : EarthMap(j['earth']);
  static List<MapPoint> _pts(dynamic l) => [for (final e in (l ?? []) as List) MapPoint(e)];
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
  final WorldMap map;
  /// ПаксГидромет и «Вестник Академии»: справочники и демо-данные (разбирает screens/meteo.dart).
  final Map<String, dynamic> meteo, meteoDemo, news, newsDemo;

  Content(Map<String, dynamic> j)
      : config = Config(j['config']),
        tagline = j['tagline'],
        weeks = (j['weeks'] as List).map((e) => Week(e)).toList(),
        mechanics = (j['mechanics'] as List).map((e) => Mechanic(e)).toList(),
        rules = (j['rules'] as List).map((e) => Rule(e)).toList(),
        join = List<String>.from(j['join']),
        lore = (j['lore'] as List).map((e) => LoreDoc(e)).toList(),
        guides = ((j['guides'] ?? []) as List).map((e) => LoreDoc(e, dir: 'guides')).toList(),
        map = WorldMap(j['map'] ?? {}),
        meteo = Map<String, dynamic>.from(j['meteo'] ?? {}),
        meteoDemo = Map<String, dynamic>.from(j['meteoDemo'] ?? {}),
        news = Map<String, dynamic>.from(j['news'] ?? {}),
        newsDemo = Map<String, dynamic>.from(j['newsDemo'] ?? {});

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
