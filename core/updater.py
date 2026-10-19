"""GitHub release checks and launch handoff for packaged Windows builds."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import threading
import urllib.request
from pathlib import Path
from queue import Empty, Queue

from core.version import GITHUB_REPOSITORY, VERSION, WINDOWS_ASSET_NAME


API_URL = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/releases?per_page=30"


def _version_key(value):
    """Return a sortable key for simple vMAJOR.MINOR.PATCH alpha tags."""
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)(?:[-.]?([0-9A-Za-z.-]+))?", value.strip())
    if not match:
        return None
    major, minor, patch, prerelease = match.groups()
    # A prerelease sorts below the matching final version.
    return (int(major), int(minor), int(patch), 0 if prerelease else 1, prerelease or "")


def find_latest_update(timeout=5):
    """Return release metadata newer than this build, or None if up to date."""
    request = urllib.request.Request(
        API_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Small-Punch-Puppies-Updater",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        releases = json.loads(response.read().decode("utf-8"))

    current_key = _version_key(VERSION)
    candidates = []
    for release in releases:
        if release.get("draft"):
            continue
        tag = release.get("tag_name", "")
        key = _version_key(tag)
        if key is None or key <= current_key:
            continue
        asset = next(
            (item for item in release.get("assets", []) if item.get("name") == WINDOWS_ASSET_NAME),
            None,
        )
        if asset and asset.get("browser_download_url"):
            candidates.append((key, {
                "version": tag,
                "url": asset["browser_download_url"],
                "digest": asset.get("digest"),
            }))
    return max(candidates, key=lambda candidate: candidate[0])[1] if candidates else None


class UpdateService:
    """Runs the release check off the game thread and exposes its result."""

    def __init__(self):
        self._results = Queue()
        self._thread = None

    def check_async(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._check, daemon=True)
        self._thread.start()

    def _check(self):
        try:
            self._results.put(("ready", find_latest_update()))
        except Exception as error:
            self._results.put(("unavailable", str(error)))

    def take_result(self):
        try:
            return self._results.get_nowait()
        except Empty:
            return None


def launch_update_helper(update):
    """Copy the helper outside the install folder and hand off the update."""
    if sys.platform != "win32" or not getattr(sys, "frozen", False):
        raise RuntimeError("Automatic updates are available in the Windows game build.")

    install_dir = Path(sys.executable).resolve().parent
    bundled_helper = install_dir / "SmallPunchPuppiesUpdater.exe"
    if not bundled_helper.is_file():
        raise FileNotFoundError("The update helper is missing from this game installation.")

    local_data = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    helper_dir = local_data / "SmallPunchPuppies" / "Updater"
    helper_dir.mkdir(parents=True, exist_ok=True)
    helper_copy = helper_dir / "SmallPunchPuppiesUpdater.exe"
    shutil.copy2(bundled_helper, helper_copy)

    arguments = [
        str(helper_copy),
        "--pid", str(os.getpid()),
        "--install-dir", str(install_dir),
        "--download-url", update["url"],
        "--launch", Path(sys.executable).name,
    ]
    if update.get("digest", "").startswith("sha256:"):
        arguments.extend(("--sha256", update["digest"].split(":", 1)[1]))

    flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    subprocess.Popen(arguments, cwd=helper_dir, creationflags=flags, close_fds=True)
