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
* Online, on a computer, phone or tablet: https://dm3942.github.io/MrFarts/
* Double-click `play.bat` (starts a tiny local web server and opens the game), **or**
* open `index.html` directly in Chrome / Edge.

## Touch screens
On a phone or tablet the game shows on-screen buttons while you play: **◀ ▶** to run (bottom-left), **JUMP** and **▼** crouch (bottom-right). Tap JUMP again in mid-air for the fart boost. Each finger is tracked on its own, so you can hold a direction while tapping JUMP, and slide a thumb from ◀ to ▶ without lifting it.

* Every screen can be tapped: **START** / **RANDOM NAME** and the **< >** level arrows on the title, **RESTART ZONE** / **CHANGE PLAYER** after game over, and tap anywhere to carry on after a level.
* The game plays in landscape. Held upright, it pauses behind a "turn your device sideways" screen.
* **FULL SCREEN** (top of the screen) hides the browser bars where the browser allows it. On iPhone use Share → **Add to Home Screen**, which opens the game full screen from its own icon.
* Sound starts on the first tap. On iPhone and iPad the music volume runs through Web Audio, because Safari ignores the volume setting on audio elements.
* The buttons switch on with the first touch and hide again when you play with the arrow keys. Add `?touch=1` to the address to force them on (for testing on a computer) or `?touch=0` to force them off.

## Controls
| Key | Action |
|-----|--------|
| ← → / A D | run |
| Space / ↑ / W | jump — press again in mid-air for a **fart boost** (needs beans); swim stroke underwater |
| ↓ / S | crouch |
| Enter | start (title screen) / next level / restart the zone after game over |
| Esc | after game over: back to the title screen |
| M | music on / off (or use the MUSIC button and volume slider in the bottom-left corner; on touch screens they move to the top while you play) |

## Music
The theme (`music/mr_farts_theme.wav`) loops in the background from the first key press or click (browsers don't allow sound before that). The volume slider tops out at 15% of the recording so sound effects and voices stay clear; the slider level and the on/off choice are remembered in this browser.

## Files
* `index.html` – the whole game: level layout, hand-drawn pixel art (croc, shark, snake, redback, items, torches, tiles), AI, audio.
* `sprites.js` – Mr Farts / Grandma / kids as low-res pixel sprites, base64-packed (generated).
* `manifest.webmanifest`, `icons/` – lets phones add the game to the home screen as a full-screen app.
* `lib/` – Phaser 3.80.1 and the Press Start 2P font, bundled locally so the game runs offline.
* `sprites/` – full-size transparent cut-outs from the original `.jpg` sheets; `pixel/` – their pixelated versions.
* `tools_slice_sprites.py` → `sprites/`, then `tools_pixelate.py` → `pixel/` + `sprites.js`.
