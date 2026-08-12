#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn

STATE_FILENAME = ".whitney-workflow-deployment.json"
STATE_VERSION = 1
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_NAME_PATTERN = re.compile(
    r"^name:\s*[\"']?([^\"'\s]+)[\"']?\s*$", re.MULTILINE
)
FRONTMATTER_PATTERN = re.compile(
    r"\A---\r?\n(?P<frontmatter>.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL
)


class DeploymentError(RuntimeError):
    """Raised when deployment cannot proceed without risking unmanaged data."""


def _fail(message: str) -> NoReturn:
    raise DeploymentError(message)


def _reject_symlinks(path: Path) -> None:
    if path.is_symlink():
        _fail(f"Refusing symlinked deployment path: {path}")
    if not path.exists():
        return
    for child in path.rglob("*"):
        if child.is_symlink():
            _fail(f"Refusing symlinked source or target content: {child}")


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _hash_tree(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(path.rglob("*")):
        relative = child.relative_to(path).as_posix().encode()
        digest.update(relative)
        if child.is_dir():
            digest.update(b"\0directory\0")
        else:
            digest.update(b"\0file\0")
            with child.open("rb") as source:
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    digest.update(chunk)
    return digest.hexdigest()


def _validate_sources(source_root: Path) -> tuple[Path, dict[str, Path]]:
    instructions = source_root / "config" / "global-agents.md"
    skills_root = source_root / "skills"
    if not instructions.is_file():
        _fail(f"Missing global instruction source: {instructions}")
    if not skills_root.is_dir():
        _fail(f"Missing skills source directory: {skills_root}")
    _reject_symlinks(instructions)
    _reject_symlinks(skills_root)

    skills: dict[str, Path] = {}
    for skill_dir in sorted(skills_root.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("."):
            continue
        name = skill_dir.name
        if SKILL_NAME_PATTERN.fullmatch(name) is None:
            _fail(f"Invalid skill directory name: {name}")
        skill_file = skill_dir / "SKILL.md"
        metadata_file = skill_dir / "agents" / "openai.yaml"
        if not skill_file.is_file() or not metadata_file.is_file():
            _fail(f"Skill {name} must contain SKILL.md and agents/openai.yaml")
        skill_text = skill_file.read_text(encoding="utf-8")
        frontmatter_match = FRONTMATTER_PATTERN.match(skill_text)
        name_match = (
            FRONTMATTER_NAME_PATTERN.search(frontmatter_match.group("frontmatter"))
            if frontmatter_match is not None
            else None
        )
        if name_match is None or name_match.group(1) != name:
            _fail(f"Skill frontmatter name must match directory name: {name}")
        skills[name] = skill_dir
    if not skills:
        _fail("No deployable skills found")
    return instructions, skills


def _load_state(path: Path) -> tuple[str | None, dict[str, str]]:
    if not path.exists():
        return None, {}
    if path.is_symlink() or not path.is_file():
        _fail(f"Invalid deployment state path: {path}")
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        _fail(f"Cannot read deployment state {path}: {error}")
    if not isinstance(loaded, dict) or loaded.get("version") != STATE_VERSION:
        _fail(f"Unsupported deployment state in {path}")
    managed = loaded.get("managed_skills")
    if not isinstance(managed, dict) or not all(
        isinstance(name, str) and isinstance(tree_hash, str)
        for name, tree_hash in managed.items()
    ):
        _fail(f"Invalid managed skill state in {path}")
    for name in managed:
        if SKILL_NAME_PATTERN.fullmatch(name) is None:
            _fail(f"Invalid managed skill name in {path}: {name}")
    instructions_hash = loaded.get("instructions_hash")
    if instructions_hash is not None and not isinstance(instructions_hash, str):
        _fail(f"Invalid instruction state in {path}")
    return instructions_hash, dict(managed)


def _atomic_copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", dir=destination.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, "wb") as target, source.open("rb") as origin:
            shutil.copyfileobj(origin, target)
            target.flush()
            os.fsync(target.fileno())
        os.chmod(temporary, stat.S_IMODE(source.stat().st_mode))
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_write_json(destination: Path, value: object) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", dir=destination.parent, text=True
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as target:
            json.dump(value, target, indent=2, sort_keys=True)
            target.write("\n")
            target.flush()
            os.fsync(target.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_replace_tree(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.new.", dir=destination.parent)
    )
    backup = destination.parent / f".{destination.name}.previous"
    shutil.rmtree(temporary)
    shutil.copytree(source, temporary, copy_function=shutil.copy2)
    try:
        if destination.exists():
            if backup.exists():
                _fail(f"Stale deployment backup requires inspection: {backup}")
            os.replace(destination, backup)
        try:
            os.replace(temporary, destination)
        except OSError:
            if backup.exists() and not destination.exists():
                os.replace(backup, destination)
            raise
        if backup.exists():
            shutil.rmtree(backup)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def deploy(
    source_root: Path,
    codex_home: Path,
    *,
    dry_run: bool = False,
    force: bool = False,
) -> tuple[str, ...]:
    source_root = source_root.resolve()
    expanded_codex_home = codex_home.expanduser()
    if expanded_codex_home.is_symlink():
        _fail(f"Refusing symlinked Codex home: {expanded_codex_home}")
    codex_home = expanded_codex_home.resolve()
    unsafe_targets = {Path(codex_home.anchor), Path.home().resolve(), source_root}
    if codex_home in unsafe_targets or source_root in codex_home.parents:
        _fail(f"Unsafe Codex home target: {codex_home}")
    instructions, source_skills = _validate_sources(source_root)
    state_path = codex_home / STATE_FILENAME
    previous_instructions_hash, previous_hashes = _load_state(state_path)
    destination_skills = codex_home / "skills"
    if destination_skills.is_symlink():
        _fail(f"Refusing symlinked skills destination: {destination_skills}")
    source_hashes = {
        name: _hash_tree(skill_dir) for name, skill_dir in source_skills.items()
    }
    source_instructions_hash = _hash_file(instructions)
    actions: list[str] = []

    destination_instructions = codex_home / "AGENTS.md"
    if destination_instructions.is_symlink():
        _fail(f"Invalid global instruction destination: {destination_instructions}")
    if not destination_instructions.exists():
        actions.append("CREATE global AGENTS.md")
    elif not destination_instructions.is_file():
        _fail(f"Invalid global instruction destination: {destination_instructions}")
    elif previous_instructions_hash is None and source_instructions_hash == _hash_file(
        destination_instructions
    ):
        actions.append("ADOPT identical global AGENTS.md")
    elif source_instructions_hash != _hash_file(destination_instructions):
        destination_instructions_hash = _hash_file(destination_instructions)
        if previous_instructions_hash is None and not force:
            _fail("Refusing to overwrite unowned AGENTS.md; rerun with --force")
        if destination_instructions_hash != previous_instructions_hash and not force:
            _fail(
                "Refusing to overwrite locally modified AGENTS.md; rerun with --force"
            )
        actions.append("UPDATE global AGENTS.md")

    for name, source_hash in source_hashes.items():
        destination = destination_skills / name
        if destination.is_symlink():
            _fail(f"Invalid skill destination: {destination}")
        if not destination.exists():
            actions.append(f"INSTALL skill {name}")
            continue
        if not destination.is_dir():
            _fail(f"Invalid skill destination: {destination}")
        _reject_symlinks(destination)
        destination_hash = _hash_tree(destination)
        if destination_hash == source_hash:
            if name not in previous_hashes:
                actions.append(f"ADOPT identical skill {name}")
            continue
        previous_hash = previous_hashes.get(name)
        if previous_hash is None and not force:
            _fail(f"Refusing to overwrite unowned skill {name}; rerun with --force")
        if (
            previous_hash is not None
            and destination_hash != previous_hash
            and not force
        ):
            message = (
                f"Refusing to overwrite locally modified skill {name}; "
                "rerun with --force"
            )
            _fail(message)
        actions.append(f"UPDATE skill {name}")

    for name, previous_hash in sorted(previous_hashes.items()):
        if name in source_skills:
            continue
        destination = destination_skills / name
        if destination.is_symlink():
            _fail(f"Invalid obsolete skill destination: {destination}")
        if not destination.exists():
            continue
        if not destination.is_dir():
            _fail(f"Invalid obsolete skill destination: {destination}")
        destination_hash = _hash_tree(destination)
        if destination_hash != previous_hash and not force:
            message = (
                f"Refusing to remove locally modified managed skill {name}; "
                "rerun with --force"
            )
            _fail(message)
        actions.append(f"REMOVE managed skill {name}")

    if dry_run:
        return tuple(actions)

    codex_home.mkdir(parents=True, exist_ok=True)
    if any(
        action in {"CREATE global AGENTS.md", "UPDATE global AGENTS.md"}
        for action in actions
    ):
        _atomic_copy_file(instructions, destination_instructions)
    for name, skill_dir in source_skills.items():
        if any(
            action in {f"INSTALL skill {name}", f"UPDATE skill {name}"}
            for action in actions
        ):
            _atomic_replace_tree(skill_dir, destination_skills / name)
    for name in previous_hashes.keys() - source_skills.keys():
        if f"REMOVE managed skill {name}" in actions:
            shutil.rmtree(destination_skills / name)
    desired_state = {
        "instructions_hash": source_instructions_hash,
        "managed_skills": source_hashes,
        "version": STATE_VERSION,
    }
    current_state = (
        json.loads(state_path.read_text(encoding="utf-8"))
        if state_path.is_file()
        else None
    )
    if current_state != desired_state:
        _atomic_write_json(state_path, desired_state)
    return tuple(actions)


def _parse_args(arguments: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deploy repository-owned Codex instructions and skills."
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")),
        help="Codex configuration directory (default: CODEX_HOME or ~/.codex).",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show changes without writing them."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite conflicting instructions or managed skill directories.",
    )
    return parser.parse_args(arguments)


def main(arguments: Sequence[str] | None = None) -> int:
    options = _parse_args(sys.argv[1:] if arguments is None else arguments)
    repository_root = Path(__file__).resolve().parents[1]
    try:
        actions = deploy(
            repository_root,
            options.codex_home,
            dry_run=options.dry_run,
            force=options.force,
        )
    except DeploymentError as error:
        print(f"Deployment failed: {error}", file=sys.stderr)
        return 1
    if not actions:
        print("Codex workflow is already current.")
        return 0
    prefix = "Would " if options.dry_run else ""
    for action in actions:
        print(f"{prefix}{action}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
