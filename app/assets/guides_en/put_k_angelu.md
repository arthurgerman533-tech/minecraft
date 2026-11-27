# Path of the Angel: a personal branch for every player

The "Path of the Angel" is a set of personal focuses, like a nation's focuses but for one player. Five stages lead from Initiate to Angel. At the last stage the Monolith at 0, 0 unlocks the **heavenly weapons**.

The branch is the same for everyone and is unlocked only by playing. Donations do not speed it up and do not give weapons: the "Angel" and "Satan" tiers only change how things look.

## Commands

| Command | What it does |
|---|---|
| `/apotheosis` or `/путь` | your stage and what is left to do |
| `/apotheosis info <1-5>` | requirements of a stage |
| `/apotheosis start <1-5>` | complete a stage (standing at the Monolith) |
| `/apotheosis weapons` | heavenly weapons and recipes |
| `/apotheosis craft <hammer, spear or crown>` | craft a weapon at a Star Altar |
| `/apotheosis aura` | turn the aura on or off ("Angel" tier only) |
| `/apotheosis skin` | refresh the look of the weapon in your hand for your tier |

**Where to complete stages.** At the Monolith: in the overworld, no further than 16 blocks from 0, 0. Stages go in order and cannot be skipped.

## The five stages

| # | Stage | What you need |
|---|---|---|
| 1 | **Initiate** | bring 5 Star Shards to the Monolith |
| 2 | **Chosen** | survive 3 cataclysms, keep your faith for 24 hours and bring its offering |
| 3 | **Guardian** | win in a war by the rules (one of three ways) |
| 4 | **Ascended** | visit the Moon and Mars and bring 4 Nameless Fragments |
| 5 | **Angel** | 8 Star Shards and a Nether Star, then 24 hours of waiting |

### 1. Initiate

Bring **5 Star Shards** to the Monolith and type `/apotheosis start 1`.

A Star Shard is an amethyst shard with a description. It drops in the "Star Shower", "Meteor Storm" and "Comet" cataclysms. Ordinary amethyst does not count.

### 2. Chosen

Two conditions:

- **Survive 3 cataclysms.** A cataclysm counts if you were online from its start to its end and did not die. The count is shown in `/apotheosis`.
- **Faith task.** Pick a faith or philosophy (`/faith list`, then `/faith <id>`), keep it for **24 hours** without changing it, and bring its offering to the Monolith.

| Faith or philosophy | id | Offering |
|---|---|---|
| Gods of the Capitol | `jupiter` | 8 gold ingots |
| Baal Hammon and Tanit | `baal` | 32 wheat |
| Gods of Olympus | `olymp` | 4 honey bottles |
| Wotan and Donar | `wotan` | 1 iron axe |
| Gods of the Groves | `druids` | 16 oak saplings |
| Zalmoxis | `zalmox` | 4 emeralds |
| Tengri and Umay | `tengri` | 16 leather |
| Tabiti, Papai and Api | `papai` | 16 bones |
| Keepers of the Seal | `monolith` | 32 stone bricks |
| The Porch (Stoics) | `stoa` | 4 books |
| The Academy | `academy` | 8 feathers |
| School of Cubes | `atom` | 16 redstone |
| The Barrel Folk | `cynic` | 1 bread |
| Union of Number | `pythag` | 4 note blocks |
| The Way | `dao` | 32 bamboo |
| The Order | `kong` | 4 lanterns |

### 3. Guardian

You must be in a Towny nation. **Any one** of these counts:

- your nation **won the Great War**;
- you **killed an attacker while defending your nation**;
- you won **5 fights against the enemy** in a war.

Only kills of players from the enemy nation count, while a war by the rules is going on between your nations (declared 24 hours ahead, fights in the 17:00–22:00 Moscow time window). Kills outside a war do not count.

### 4. Ascended

- **Visit the Moon and Mars.** Being in each world once is enough, the script remembers it. The Moon and Mars open in the server's space eras.
- Bring **4 Nameless Fragments** to the Monolith. A fragment is paper with a description, left behind by the "Fog of the Nameless". Ordinary paper does not count.

### 5. Angel

The last focus. Bring **8 Star Shards** and a **Nether Star** to the Monolith and type `/apotheosis start 5`. Then wait **24 hours**: the timer runs even when you are offline. When it ends, the whole server sees an announcement and the heavenly weapons unlock for you.

## Heavenly weapons

Crafted with `/apotheosis craft <id>` at a **Star Altar**: any lodestone within 4 blocks of you. Each weapon costs 8 Star Shards, 4 Nameless Fragments and one more resource. The weapons never break.

| id | Weapon | Recipe | What it does |
|---|---|---|---|
| `hammer` | **Hammer of the PAX Seal** (mace) | 8 shards, 4 fragments, 2 netherite ingots, 4 gold blocks | Right click — **Seal Strike**: a 6-block wave, 8 damage, knocks enemies up. 40 s cooldown |
| `spear` | **Spear of the Sixth Line** (trident) | 8 shards, 4 fragments, 1 trident, 4 echo shards | Right click — **The Line**: a 30-block beam pierces everyone on its path, 7 damage each. 15 s cooldown |
| `crown` | **Crown of the Monolith** (golden helmet) | 8 shards, 4 fragments, 8 gold blocks, 1 Nether Star | Worn — Resistance I. Shift + left click with an empty hand — **Light of the Monolith**: heals you and your nation within 8 blocks by 3 hearts. 90 s cooldown |

The weapons never break blocks. Damage is dealt in your name, so newcomer protection, claims and peaceful towns work as with a normal hit.

## "Angel" and "Satan" tiers: looks only

| What | No tier | "Angel" tier |
|---|---|---|
| Branch speed | normal | the same |
| Weapon power | normal | the same |
| Weapon look | normal | golden, enchanted glint |
| Aura | none | golden particles (`/apotheosis aura`) |
| Title above the name | none | "Angel" |

The "Satan" tier is also cosmetic only. More about the tiers is in "Support the server" on the home page.

## Where this comes from in the lore

The Monolith at 0, 0 is the seal over the Great Gate that destroyed the Precursors in the Year of Ash. Star Shards warm the shield on the sixth line, and Nameless Fragments are traces of Those Who Are Not. With the Hammer of the Seal the Guardians carved the word PAX into the Monolith, and the Spear of the Sixth Line was made from the line nobody can read. More in [The Age of the Precursors](../lore/predtechi.html).
