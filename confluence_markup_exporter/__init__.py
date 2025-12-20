"""Confluence Markup Exporter package."""

try:
    from importlib.metadata import version

    __version__ = version("confluence-markup-exporter")
except Exception:  # noqa: BLE001
    # fallback if package not installed or metadata not available
    __version__ = "unknown"
