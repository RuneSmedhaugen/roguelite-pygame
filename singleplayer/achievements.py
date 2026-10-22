"""Local achievement catalog and persistence for Small Punch Puppies."""

import json

from core.characters import CHARACTERS
from core.user_settings import settings_path


ENDLESS_MILESTONES = (
    (10, "bronze", (186, 119, 71)),
    (25, "silver", (166, 184, 204)),
    (50, "gold", (235, 190, 76)),
)
CLASSIC_TIER = "champion"
CLASSIC_COLOR = (222, 174, 67)


def build_catalog():
    achievements = []
    for character in CHARACTERS:
        character_id = character.get("id", character["name"].lower().replace(" ", "_"))
        common = {
            "character_id": character_id,
            "character_name": character["name"],
            "sprite": character.get("sprite"),
        }
        achievements.append({
            **common,
            "id": f"classic_{character_id}",
            "mode": "classic",
            "tier": CLASSIC_TIER,
            "color": CLASSIC_COLOR,
            "name": f"Classic Champion: {character['name']}",
            "description": f"Complete Classic mode with {character['name']}.",
        })
        for level, tier, color in ENDLESS_MILESTONES:
            achievements.append({
                **common,
                "id": f"endless_{character_id}_{level}",
                "mode": "endless",
                "level": level,
                "tier": tier,
                "color": color,
                "name": f"Endless {level}: {character['name']}",
                "description": f"Beat level {level} in Endless mode with {character['name']}.",
            })
    return achievements


CATALOG = build_catalog()
CATALOG_BY_ID = {achievement["id"]: achievement for achievement in CATALOG}


def achievements_path():
    return settings_path().with_name("achievements.json")


class AchievementStore:
    def __init__(self):
        self.unlocked = set()
        self._load()

    def _load(self):
        try:
            payload = json.loads(achievements_path().read_text(encoding="utf-8"))
            stored = payload.get("unlocked", []) if isinstance(payload, dict) else []
            self.unlocked = {item for item in stored if item in CATALOG_BY_ID}
        except (OSError, json.JSONDecodeError, TypeError):
            self.unlocked = set()

    def _save(self):
        path = achievements_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        payload = {"unlocked": sorted(self.unlocked)}
        temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temporary.replace(path)

    def unlock(self, achievement_id):
        if achievement_id not in CATALOG_BY_ID or achievement_id in self.unlocked:
            return None
        self.unlocked.add(achievement_id)
        try:
            self._save()
        except OSError as error:
            print(f"Could not save achievements: {error}")
        return CATALOG_BY_ID[achievement_id]

    def reset(self):
        self.unlocked.clear()
        try:
            self._save()
        except OSError as error:
            print(f"Could not reset achievements: {error}")

    def get(self, achievement_id):
        return CATALOG_BY_ID.get(achievement_id)

    def for_ids(self, achievement_ids):
        return [CATALOG_BY_ID[item] for item in achievement_ids if item in CATALOG_BY_ID]

    def filtered(self, mode="all"):
        if mode == "all":
            return CATALOG
        return [achievement for achievement in CATALOG if achievement["mode"] == mode]
