import 'content.dart';

/// Та же логика, что в paxborder.sk / paxwar.sk / paxseasons.sk и на сайте (app.js).
int radiusForDay(BorderCfg b, int d) {
  int r(num x) => x.round();
  if (d <= 6) return r(b.start + (b.w1 - b.start) * d / 6);
  if (d <= 13) return r(b.w1 + (b.w2 - b.w1) * (d - 6) / 7);
  if (d <= 20) return r(b.w2 + (b.w3 - b.w2) * (d - 13) / 7);
  if (d <= 27) return r(b.w3 + (b.w4 - b.w3) * (d - 20) / 7);
  if (d <= 34) return r(b.w4 + (b.w5 - b.w4) * (d - 27) / 7);
  if (d <= 41) return r(b.w5 + (b.w6 - b.w5) * (d - 34) / 7);
  return b.w6;
}

const seasons = [
  'Весна «Посевная»',
  'Лето «Экспедиции»',
  'Осень «Сбор урожая»',
  'Зима «Зимняя кампания»',
];

class ServerState {
  bool started = false;
  bool prime = false;
  int primeIn = 0; // минут до открытия/закрытия окна боёв
  int? untilDays, day, week, radius, tomorrow;
  String? season, warPhase;
}

ServerState serverState(Config cfg, [DateTime? now]) {
  now ??= DateTime.now();
  final st = ServerState();
  final msk = now.toUtc().add(const Duration(hours: 3));
  final mins = msk.hour * 60 + msk.minute;
  final from = cfg.primeFrom * 60, to = cfg.primeTo * 60;
  st.prime = msk.hour >= cfg.primeFrom && msk.hour < cfg.primeTo;
  st.primeIn = st.prime ? to - mins : (from - mins + 1440) % 1440;
  if (cfg.launchDate.isEmpty) return st;
  final t0 = DateTime.tryParse(cfg.launchDate);
  if (t0 == null) return st;
  final diff = now.difference(t0);
  if (diff.isNegative) {
    st.untilDays = (-diff.inHours / 24).ceil();
    return st;
  }
  st.started = true;
  final day = diff.inDays;
  st.day = day + 1;
  st.week = day >= 35 ? 6 : day >= 28 ? 5 : day >= 21 ? 4 : day >= 14 ? 3 : day >= 7 ? 2 : 1;
  st.radius = radiusForDay(cfg.border, day);
  st.tomorrow = radiusForDay(cfg.border, day + 1);
  st.season = day >= 28 ? seasons[((day - 28) ~/ 7) % 4] : null;
  st.warPhase = day >= 28
      ? 'Мир, итоги войны'
      : day >= 24
          ? 'Великая война'
          : day >= 23
              ? 'Мобилизация'
              : day >= 21
                  ? 'Формирование наций'
                  : null;
  return st;
}

String fmtMinutes(int n) {
  final h = n ~/ 60, m = n % 60;
  return h > 0 ? '$h ч $m мин' : '$m мин';
}
