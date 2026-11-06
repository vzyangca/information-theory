"""Short-video pipeline for the Signal Stories series."""

from pathlib import Path as _Path

try:
    __version__ = "signal-stories-v-" + (_Path(__file__).resolve().parent.parent / "VERSION").read_text().strip()
except OSError:
    __version__ = "signal-stories (unknown version)"
