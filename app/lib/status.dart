import 'dart:convert';

import 'package:http/http.dart' as http;

class ServerStatus {
  final bool online;
  final int players, max;
  final String version;
  const ServerStatus(this.online, this.players, this.max, this.version);
}

/// Публичный API mcsrvstat.us (без ключей). null — нет сети или адрес не задан.
Future<ServerStatus?> fetchStatus(String address) async {
  if (address.isEmpty) return null;
  try {
    final r = await http
        .get(Uri.parse('https://api.mcsrvstat.us/3/${Uri.encodeComponent(address)}'),
            headers: {'User-Agent': 'PaxVanila-App'})
        .timeout(const Duration(seconds: 10));
    if (r.statusCode != 200) return null;
    final j = jsonDecode(r.body) as Map<String, dynamic>;
    final online = j['online'] == true;
    final p = (j['players'] ?? {}) as Map<String, dynamic>;
    return ServerStatus(online, p['online'] ?? 0, p['max'] ?? 0, '${j['version'] ?? ''}');
  } catch (_) {
    return null;
  }
}
