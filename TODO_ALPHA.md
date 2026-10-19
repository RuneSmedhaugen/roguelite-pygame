# Alpha release TODO

## Before the next alpha release

1. [x] Explain each character passive in plain language on the selection screen and show its current state or trigger feedback during battle.
2. [x] Make the existing feedback and bug report form accessible from the in-game pause menu. Opening it should pause the run, and sending or cancelling should return to the paused game.
3. Play through both Classic and Endless from the main menu and check the run flow, including level 20 victory, losing and retrying the same Classic level, running out of lives, upgrades, and game over.
4. Build and launch a clean alpha package; confirm the feedback dashboard is excluded from the player download and settings persist.
5. Publish a test GitHub release and verify the updater can update an installed older build, preserve settings, and relaunch the game.

## After alpha

1. Add local highscores for each mode, recording the character, furthest level, and other useful run details. A completed Classic run should receive a distinct completion result rather than just “Level 20.”
2. Add a global leaderboard for Endless runs using the database. Keep Classic results local unless a compelling use for global Classic scores comes up.
