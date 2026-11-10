"""Keep raw evaluation outputs out of Git and instruction source checkouts."""

from __future__ import annotations

from pathlib import Path


def external_output(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    for parent in (resolved, *resolved.parents):
        marker = parent / ".git"
        checkout = (
            marker.is_file()
            or (marker / "HEAD").is_file()
            or (marker / "config").is_file()
        )
        bare = (
            (parent / "HEAD").is_file()
            and (parent / "objects").is_dir()
            and (parent / "config").is_file()
        )
        if (
            checkout
            or bare
            or (
                (parent / "skills").is_dir()
                and (parent / "config/global-agents.md").is_file()
            )
        ):
            raise ValueError("Raw evaluation outputs must be outside source checkouts.")
    return resolved
