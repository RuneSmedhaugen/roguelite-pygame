"""Load and save preferences outside the game installation directory."""

import json
import os
from pathlib import Path


DEFAULTS = {
    "display_mode": "fullscreen",
    "resolution": [0, 0],
    "display_index": 0,
    "audio_levels": {"master": 0.65, "music": 0.45, "effects": 0.8},
}


def settings_path():
    if os.name == "nt":
        root = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return root / "SmallPunchPuppies" / "settings.json"


def load_settings():
    values = dict(DEFAULTS)
    values["audio_levels"] = dict(DEFAULTS["audio_levels"])
    try:
        saved = json.loads(settings_path().read_text(encoding="utf-8"))
        if isinstance(saved, dict):
            if saved.get("display_mode") in {"fullscreen", "borderless", "windowed"}:
                values["display_mode"] = saved["display_mode"]
            resolution = saved.get("resolution")
            if (isinstance(resolution, (list, tuple)) and len(resolution) == 2
                    and all(isinstance(size, int) and size >= 0 for size in resolution)):
                values["resolution"] = list(resolution)
            display_index = saved.get("display_index")
            if isinstance(display_index, int) and display_index >= 0:
                values["display_index"] = display_index
            audio = saved.get("audio_levels")
            if isinstance(audio, dict):
                for key in values["audio_levels"]:
                    try:
                        values["audio_levels"][key] = max(0.0, min(1.0, float(audio[key])))
                    except (KeyError, TypeError, ValueError):
                        pass
    except (OSError, json.JSONDecodeError):
        pass
    return values


def save_settings(values):
    path = settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(values, indent=2), encoding="utf-8")
    temporary.replace(path)
