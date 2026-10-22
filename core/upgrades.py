"""Shared stat-upgrade application primitives."""


def apply_upgrade(unit, upgrade):
    """Apply a stat change to a combat unit.

    Upgrade selection and balance are owned by each game mode; this function
    only applies a selected stat change to a shared character model.
    """
    stat = upgrade.get("stat")
    value = upgrade.get("value")

    if stat == "hp":
        unit.max_hp += value
        unit.hp += value
    elif stat == "atk":
        min_inc, max_inc = value
        unit.atk_min += min_inc
        unit.atk_max += max_inc
    elif hasattr(unit, stat):
        setattr(unit, stat, getattr(unit, stat) + value)
