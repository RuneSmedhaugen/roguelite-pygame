# Publishing a game update

Windows testers install one ZIP once. After that, the game checks GitHub Releases at startup. If it finds a newer version, the main menu replaces **Play** with **Update Game**. Selecting it closes the game, lets the bundled helper replace the installed game folder, and starts the new version.

For local playtesting, install the build dependencies once into the project's `.venv` with `python -m pip install -r requirements-build.txt`, then run `.\build_windows.ps1`. Launch `dist\SmallPunchPuppies\SmallPunchPuppies.exe`; the script also creates `SmallPunchPuppies-Windows-v<VERSION>.zip`. This local build does not need a GitHub release to launch.

## Publishing a release

1. Bump `VERSION` in `core/version.py` (for example, `0.1.0` to `0.1.1`).
2. Commit and push the change to the GitHub repository.
3. Create a GitHub Release with a matching tag such as `v0.1.1`. Alpha releases may be marked as prereleases; the updater checks prereleases too.
4. Publish the release. The Windows workflow builds `SmallPunchPuppies-Windows.zip` and attaches it to that release.
5. Confirm the workflow succeeded and the ZIP is attached before telling testers an update is available.

The repository and its releases must be public for the unauthenticated game client to check and download updates. If GitHub cannot be reached, the current build remains playable. A known newer version must be installed before **Play** becomes available.

The updater preserves settings because they are stored in the user's app-data folder, outside the game installation. It writes update failure details to `%LOCALAPPDATA%\SmallPunchPuppies\update-error.log`.

This first updater targets Windows ZIP builds. Source checkouts and other operating systems continue to run without automatic updating.
