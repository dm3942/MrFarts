# Mr Farts

A Mario-style pixel-art side-scroller built on **Phaser 3** (arcade physics), running entirely in the browser.

## Zones
| Zone | Levels | Hazards | Treats |
|---|---|---|---|
| 1 The Park | 3 (ends down a pipe) | grandmas, crocs, snakes, shark pools, redbacks | pancakes, bananas |
| 2 The Sewer | 3 (level 1 ends by pressing the flood button; level 2 is flooded until you pull the plug; level 3 is drained, ends up a pipe) | bats, crocs, sharks | pizza, donuts |
| 3 The City | 3 (generated rooftop chains joined by crane beams; finish on the road or on the last rooftop) | cars (flashing sign + honk before they arrive), pits, grandmas | hot dogs, coffee |
| 4 The Beach | 2 | crabs, seagulls, sharks | ice cream, fish & chips |

Finish bonuses: level clear +500, no damage taken +300, no birds hurt +200. Birds only faint if you walk under their tree on the ground; jump over the tree and the bird stays put and sings. A first aid kit high up in each level gives an extra life, and every level hides one museum piece (diamond, painting, crown, dinosaur bone, treasure chest, mummy, gold, statue, vase, pharaoh mask, silver trophy) worth +250.

## Starting a game
Type your name on the title screen and press **Enter**, or press Enter with the box empty to get a random name. Pick a difficulty with ↑ / ↓ or by clicking it:

| Difficulty | Life-taking hazards kept |
|---|---|
| Beginner | a quarter |
| Easy | half |
| Medium | three quarters |
| Hard | all of them (the original game) |

Hazards are grandmas, crocs, snakes, crabs, bats, seagulls, sharks, redbacks and cars; the ones kept are spread evenly along each level. Pits stay the same on every difficulty.

**Running out of lives** ends the run. There is no continuing the level: Enter starts again from the first level of the zone with 5 lives and a score of 0, and Esc goes back to the title to change player or difficulty.

## High scores
Scores are kept in this browser (IndexedDB), with a separate top-ten table for each difficulty, so everyone who plays on the same computer and browser shares the tables. A score is saved when a run ends, either by losing all lives or by finishing the game. Only runs that start at the beginning of a zone count; starting mid-zone (from the LEVEL menu, `[` / `]` or `?level=`) is a practice run and is not recorded.

Jump to a level with `index.html?level=7`, press `[` / `]` on the title screen, or use the small LEVEL button in the top-right corner at the start of any level. A jump from the LEVEL menu starts a fresh run.

## Play
* Double-click `play.bat` (starts a tiny local web server and opens the game), **or**
* open `index.html` directly in Chrome / Edge.

## Controls
| Key | Action |
|-----|--------|
| ← → / A D | run |
| Space / ↑ / W | jump — press again in mid-air for a **fart boost** (needs beans); swim stroke underwater |
| ↓ / S | crouch |
| Enter | start (title screen) / next level / restart the zone after game over |
| Esc | after game over: back to the title screen |
| M | music on / off (or use the MUSIC button and volume slider in the bottom-left corner) |

## Music
The theme (`music/mr_farts_theme.wav`) loops in the background from the first key press or click (browsers don't allow sound before that). The MUSIC button, the volume slider and the on/off choice are remembered in this browser.

## Files
* `index.html` – the whole game: level layout, hand-drawn pixel art (croc, shark, snake, redback, items, torches, tiles), AI, audio.
* `sprites.js` – Mr Farts / Grandma / kids as low-res pixel sprites, base64-packed (generated).
* `lib/` – Phaser 3.80.1 and the Press Start 2P font, bundled locally so the game runs offline.
* `sprites/` – full-size transparent cut-outs from the original `.jpg` sheets; `pixel/` – their pixelated versions.
* `tools_slice_sprites.py` → `sprites/`, then `tools_pixelate.py` → `pixel/` + `sprites.js`.
