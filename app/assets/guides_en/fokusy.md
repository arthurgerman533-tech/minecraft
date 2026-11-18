# National focus guide

Focuses are a nation's long-term decisions, as in Hearts of Iron. The nation leader picks a focus, pays from the nation's treasury and waits. When the timer runs out, the whole nation gets the bonus for good. Only one focus runs at a time.

## How it works

| Command | Who | What it does |
|---|---|---|
| `/focus` | any resident | the focus tree and your nation's progress |
| `/focus start <id>` | nation leader | start a focus |
| `/focus heritage` | anyone | list of heritages and who took them |
| `/focus heritage <id>` | nation leader | pick a heritage (once) |
| `/focus kit` | every resident | collect the «Mobilisation» gear (once) |

Cost and time depend on the tier:

| Tier | Cost | Time |
|---|---|---|
| 1 | 500$ | 12 h |
| 2 | 1500$ | 24 h |
| 3 | 3000$ | 36 h |

Each focus in a branch needs the one before it. The timer keeps running when nobody is online, so start a focus before you go to sleep.

## Three branches

### Industry, for builders

| id | Focus | Bonus |
|---|---|---|
| `ind1` | Industrialisation | +16 chunks for every town in the nation, including towns that join later |
| `ind2` | Miners' Guilds | Haste I on your territory |
| `ind3` | War Economy | +150$ into the nation treasury every day |

### Army, for fighters

| id | Focus | Bonus |
|---|---|---|
| `mil1` | Mobilisation | iron armour, a sword and food for every resident (`/focus kit`) |
| `mil2` | Fortifications | Resistance I on your territory while the nation is in battle |
| `mil3` | Total War | Speed I and Strength I everywhere while the nation is in battle |

### Economy, for negotiators

| id | Focus | Bonus |
|---|---|---|
| `eco1` | Trade Routes | +100$ into the nation treasury every day |
| `eco2` | Diplomatic Corps | non-aggression pacts (`/dip pact`) are free for the nation |
| `eco3` | Hegemony | double tribute from vassals: 20% of their treasury, up to 1000$ a day |

**Total War and Hegemony exclude each other.** The nation chooses: win with the sword, or keep its neighbours as vassals.

«In battle» means the nation is currently «hot» in `/paxwar`: a war is declared, it is prime time (17:00–22:00 Moscow time), and defenders are online.

## Heritage: the tenth focus

The nation leader picks one of the ten powers from the lore. The heritage gives a permanent bonus straight away and unlocks the unique focus `her` (tier 2: 1500$ and 24 hours, needs any tier 1 focus).

A nation can take one heritage, and each heritage goes to one nation only. First come, first served. You cannot change your choice yourself, only the admins can reset it.

| id | Power | Bonus straight away | Heritage focus |
|---|---|---|---|
| `rome` | Romea | a pact costs 50$ instead of 100$ | **SPQR**: +1 war point for each enemy killed on your land |
| `carthage` | Carthage | +25$ into the treasury a day | **Guns of Gaius**: siege weapons (`/siege`) 25% cheaper |
| `hellas` | Hellas | Water Breathing in water | **Sea League**: Dolphin's Grace as well |
| `dacia` | Dacia | Haste I below Y=40 | **Copper of Caer-Tal**: Haste II on your territory |
| `germania` | Germania | Speed I on your territory | **Iron and Coal**: +100$ into the treasury a day |
| `gallia` | Gallia | autumn harvest pays 60$ instead of 40$ | **Sacred Groves**: Regeneration I at home during battle |
| `horde` | Horde | Speed I in the wilderness | **Out of the Sandstorm**: Strength I on foreign land during battle |
| `scythia` | Scythia | +20$ a day per town (up to 100$) | **Royal Kurgans**: vassal tribute 15% instead of 10% |
| `north` | Northern Kingdom | winter cold on foreign land does not affect you | **Blizzard of 1942**: in winter, enemies on your land get Slowness II |
| `isles` | Island Union | if you become a vassal, you pay half the tribute | **Republic of Seafarers**: Dolphin's Grace and Water Breathing |

The lore explains why: Romulus and the Treaty at the Monolith, the Golden Caravan of Carthage, the copper of Dacia, the Horde out of the sandstorm, the blizzards of 1241 and 1942. Read «Middle Ages».

## What to take and when

The server runs in weeks. The border grows, and in week 4 (day 21) the Great War begins: day 21 is Formation, day 23 Mobilisation, day 24 the war itself, day 28 peace. You will not get everything: a full branch takes 3 days, and all the focuses you can take (nine of them, because Total War and Hegemony exclude each other) take about 9 days and 13,500$.

**Week 1.** The treasury is empty. Take your heritage right away, it is free. The first focus is usually `eco1` (Trade Routes): it pays for itself in five days and funds everything else. If your nation has many builders, start with `ind1`.

**Weeks 2–3.** Decide who you are. If you are preparing for war, `mil1` and `mil2` should be done by day 23. If you want vassals, take the economy branch towards `eco3`. This is a good time for the heritage focus, once the treasury has its first 1500$.

**Week 4, the war.** Total War on day 24 is the strongest, but it costs 3000$ and 36 hours. Start it no later than day 22.

**After the war.** Seasons change every week. Gallia earns in autumn, the North is strongest in winter.

## Ready-made builds

**Empire.** Romea or Germania. Order: `eco1` → `mil1` → `her` → `mil2` → `mil3`. Sign cheap pacts with those you leave alone, and hit one neighbour in prime time.

**Merchant republic.** Carthage or Scythia. Order: `eco1` → `ind1` → `eco2` → `her` → `eco3`. Scythia with Hegemony and the Kurgans takes 30% of a vassal's treasury a day (up to 1000$).

**Fortress.** Dacia or Gallia. Order: `ind1` → `ind2` → `mil1` → `mil2` → `her`. You are expensive to storm: Resistance, Regeneration, and Haste to repair the walls.

**Nomads.** The Horde. Order: `mil1` → `her` → `mil2` → `mil3`. Fast raids through the wilderness, Strength on foreign land.

**The sea.** Hellas or the Isles. Order: `eco1` → `her` → `ind1`. Underwater temples, ports and the Caravan. The Isles are not afraid of becoming a vassal: the tribute is halved.

**The North.** Order: `ind1` → `mil1` → `her` → `mil2`. Hold on in summer, attack in winter: you do not feel the cold, and an enemy on your land has it twice as bad.

## FAQ

**Can I cancel a focus?** No. Choose when the treasury has enough for the next one.

**What happens if the nation is disbanded?** Its focuses go with it, and its heritage is freed within 30 minutes.

**I joined the nation later. Do I get the bonuses?** Yes. Effects and income are shared by the whole nation, and `ind1` gives chunks to new towns too. The `/focus kit` gear is given once per player, for good, even if you change nations.

**Do bonuses stack?** Money stacks: Germania with `eco1`, `ind3` and its own focus gets 350$ a day. Effects of the same kind do not stack, the strongest applies: Dacia with its heritage focus has Haste II at home even if it took `ind2`.
