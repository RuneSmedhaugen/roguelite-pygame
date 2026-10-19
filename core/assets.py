"""Resolve bundled assets both from source and PyInstaller builds."""

import sys
from pathlib import Path


def asset_path(*parts):
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return root.joinpath("assets", *parts)
