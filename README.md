# Eagle Strike

A fast-paced vertical scrolling shooter (shmup) built with Pygame.  
Pilot the Eagle fighter against waves of Terminids, Automatons, and Illuminate forces.  
Destroy enemies, build combos, collect power-ups, defeat bosses, and climb the leaderboard!

## Quick Overview

- Classic arcade-style vertical shooter with modern touches
- Score-based progression with escalating difficulty
- Varied enemy waves and scripted formations
- Power-ups, combo multiplier, bombs, and a screen-clearing Eagle Strike special
- Bosses with phases and unique attacks
- Mini-boss encounters via dropships
- Local high score leaderboard and simple achievements

## Features

- Multiple enemy factions with different visuals and behaviors
- Formations (lines, arrows, walls, diamonds, crosses) that force active dodging
- Power-ups:
  - Rapid Fire (faster shooting)
  - Triple Shot (spread fire)
  - Shield (one free hit)
  - Bomb charges (screen clear on demand)
  - Extra Life
- Boost meter for temporary speed bursts
- Eagle Strike meter (fills with kills) → full-screen nuke
- Combo system: higher combo = bigger score multiplier (up to 4×)
- Boss fights every ~20-35k points with breathing room afterward
- Short "lull" periods after big clears for recovery and tension build-up
- Persistent local leaderboard and achievements

## Controls

### Gamepad (tested with Xbox/PlayStation-style controllers)
- Left stick: Movement
- Right trigger (R2/RT): Shoot
- Left trigger (L2/LT): Special (Bomb / Eagle Strike)
- A / Cross button: Boost
- L1 / Options button: Pause

## How to Run

1. Requirements:
   - Python 3.8+
   - Pygame (`pip install pygame`)

2. Place all asset files (images/*.png, sounds/*.wav) in the same folder as `eagle_strike.py`.

3. Run the game:

4. *easy made for Windows option (download and run the EagleStrike.exe that's included, look for version 2.1.
