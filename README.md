# Eagle-Strike-2.0
Complete new build of previous game code
Eagle Strike

A fast-paced, retro-style vertical shoot 'em up built with Pygame. 
Take control of a lone Eagle fighter and battle waves of enemies 
across three enemy factions: Terminids, Automatons, and Illuminates. 
Survive escalating waves, collect power-ups, defeat mini-bosses and 
full bosses, and climb the local leaderboard!

Inspired by classic arcade shooters and the chaotic fun of games 
like Helldivers 2.

Features

- Three Enemy Factions with unique behaviors and visuals 
  (Terminids, Automatons, Illuminates)
- Progressive Stages with increasing difficulty and background tint changes
- Power-Up System:
    Rapid Fire (faster shooting)
    Triple Shot (spread fire)
    Shield (one free hit)
    Extra Bomb (screen-clear ability)
    Extra Life
- Boost Mechanic – Hold to move faster (drains meter, recharges when not used) *PS5 controller>press Square button
- Eagle Strike – Ultimate ability that clears or heavily damages enemies 
  when meter is full *PS5 controller>press Triangle button
- Mini-Bosses dropped from transports with escalating health and attack patterns
- Full Boss Battles every ~10,000–15,000 points
- Random Events (Breach, Patrol, Supply) that change spawn behavior
- Local Leaderboard – Top 10 scores with 3-letter initials
- Controller Support (tested with DualSense; generic gamepads should work)
- Keyboard Controls (fully configurable via code if desired)
- High-Quality Audio – Multiple music tracks, SFX for shooting, explosions, 
  power-ups, etc.
- PyInstaller Compatible – Easy to build as a standalone executable

Controls

Keyboard
- Movement: WASD or Arrow Keys
- Shoot: Space
- Boost: Left/Right Shift
- Eagle Strike / Bomb: Q (uses Eagle meter if full, otherwise consumes a bomb charge)

Controller (Generic / DualSense)
- Movement: Left Stick
- Shoot: Right Trigger (R2)
- Boost: A Button (or X)
- Eagle Strike / Bomb: Triangle or specific button (configurable in code)

Menus support both keyboard (Up/Down/Enter) and controller navigation.

How to Run

Requirements
- Python 3.8+
- Pygame (pip install pygame)
- Run the EagleStrike.exe for seamless operation


Quick Start
1. Clone or download the repository, or download and run the executable (EagleStrike.exe).
2. Place all assets (images, sounds) in the appropriate folders relative to eagle_strike.py.
3. Run:
   python eagle_strike.py

Building an Executable (Optional)
The game includes PyInstaller support via resource_path().
pyinstaller --onefile --add-data "assets;assets" eagle_strike.py
(Adjust --add-data separator for your OS: ; on Windows, : on macOS/Linux)

Files
- eagle_strike.py – Main game file
- leaderboard.json – Saved automatically (top 10 entries)
- eagle_strike_debug.log – Debug log (overwritten each launch)

Credits
- Developed by [Milsim Rooster]
- Assets: Custom or sourced (generated via AI)
- Sound effects and music: (generated via AI)
- Built with Pygame

Known Issues / Todo
- No online leaderboard (local only)
- Balance tuning ongoing
- More enemy variety / power-ups possible in future updates

Enjoy diving into the action – for Super Earth!
