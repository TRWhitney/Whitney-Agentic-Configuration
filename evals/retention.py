"""Inspect evidence lifetime and copies in the disposable project's Git storage."""

from __future__ import annotations

import gzip
import io
import subprocess
import zipfile

from evals.fixtures import Workspace, git
from evals.models import NoRawEvidenceCheck, TemporaryFilesCheck

MAX_ARCHIVE_BYTES = 2_000_000


def temporary_check(
    check: TemporaryFilesCheck, workspace: Workspace
) -> tuple[bool, str]:
    for name in check.paths:
        path = workspace.temporary_file(name)
        if check.state == "absent":
            passed = not path.exists()
        elif check.state == "unchanged":
            passed = (
                path.is_file()
                and path.read_bytes() == workspace.temporary_baseline[name]
            )
        else:
            passed = path.is_file() and bool(path.stat().st_size)
        if not passed:
            return False, f"Temporary evidence {name}: expected {check.state}."
    return True, f"Temporary evidence: {check.state}."


def _contents(content: bytes) -> list[bytes]:
    """Include common capture archives, with bounded decompression."""
    values = [content]
    stream = io.BytesIO(content)
    if zipfile.is_zipfile(stream):
        with zipfile.ZipFile(stream) as archive:
            if sum(info.file_size for info in archive.infolist()) > MAX_ARCHIVE_BYTES:
                raise ValueError("Evidence archive exceeds inspection allowance.")
            values.extend(
                archive.read(info) for info in archive.infolist() if not info.is_dir()
            )
    elif content.startswith(b"\x1f\x8b"):
        with gzip.GzipFile(fileobj=stream) as archive:
            decoded = archive.read(MAX_ARCHIVE_BYTES + 1)
        if len(decoded) > MAX_ARCHIVE_BYTES:
            raise ValueError("Evidence archive exceeds inspection allowance.")
        values.append(decoded)
    return values


def no_raw_evidence(
    check: NoRawEvidenceCheck, workspace: Workspace
) -> tuple[bool, str]:
    raw = [
        *workspace.raw_temporary_contents,
        *(workspace.baseline[p] for p in check.paths),
    ]
    signatures = [value.strip() for value in raw if value.strip()]

    def contains(content: bytes) -> bool:
        return any(
            signature in value
            for value in _contents(content)
            for signature in signatures
        )

    for path in workspace.root.rglob("*"):
        relative = path.relative_to(workspace.root)
        if ".git" in relative.parts or not path.is_file():
            continue
        if contains(path.read_bytes()):
            return False, f"Raw evidence copied into checkout: {relative.as_posix()}"
    objects = git(
        workspace.root,
        "cat-file",
        "--batch-all-objects",
        "--batch-check=%(objectname) %(objecttype)",
    )
    for line in objects.splitlines():
        identifier, kind = line.split()
        if kind != "blob" or identifier in workspace.initial_objects:
            continue
        content = subprocess.run(
            ["git", "-C", str(workspace.root), "cat-file", "blob", identifier],
            check=True,
            capture_output=True,
            timeout=15,
        ).stdout
        if contains(content):
            return (
                False,
                "Raw evidence entered Git, including staged or replaced commits.",
            )
    return True, "No seeded raw evidence in checkout or new Git blobs."
