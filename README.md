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

Jump to a level with `index.html?level=7`, press `[` / `]` on the title screen, or use the small LEVEL button in the top-right corner at the start of any level.

## Play
* Double-click `play.bat` (starts a tiny local web server and opens the game), **or**
* open `index.html` directly in Chrome / Edge.

## Controls
| Key | Action |
|-----|--------|
| ← → / A D | run |
| Space / ↑ / W | jump — press again in mid-air for a **fart boost** (needs beans); swim stroke underwater |
| ↓ / S | crouch |
| Enter | restart after game over / level complete |

## Files
* `index.html` – the whole game: level layout, hand-drawn pixel art (croc, shark, snake, redback, items, torches, tiles), AI, audio.
* `sprites.js` – Mr Farts / Grandma / kids as low-res pixel sprites, base64-packed (generated).
* `lib/` – Phaser 3.80.1 and the Press Start 2P font, bundled locally so the game runs offline.
* `sprites/` – full-size transparent cut-outs from the original `.jpg` sheets; `pixel/` – their pixelated versions.
* `tools_slice_sprites.py` → `sprites/`, then `tools_pixelate.py` → `pixel/` + `sprites.js`.
