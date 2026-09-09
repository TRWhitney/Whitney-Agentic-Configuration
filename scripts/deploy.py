#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.sync_navigators import NavigatorSyncError, sync_navigators

STATE_FILENAME = ".whitney-workflow-deployment.json"
STATE_VERSION = 1
EXTERNAL_SKILLS_FILENAME = "external-skills.json"
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_NAME_PATTERN = re.compile(
    r"^name:\s*[\"']?([^\"'\s]+)[\"']?\s*$", re.MULTILINE
)
FRONTMATTER_PATTERN = re.compile(
    r"\A---\r?\n(?P<frontmatter>.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL
)


class DeploymentError(RuntimeError):
    """Raised when deployment cannot proceed without risking unmanaged data."""


@dataclass(frozen=True)
class ExternalSkillSpec:
    name: str
    submodule: Path
    path: Path


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


def _validate_skill(name: str, skill_dir: Path, *, require_metadata: bool) -> None:
    skill_file = skill_dir / "SKILL.md"
    metadata_file = skill_dir / "agents" / "openai.yaml"
    if not skill_file.is_file() or (require_metadata and not metadata_file.is_file()):
        required = "SKILL.md and agents/openai.yaml" if require_metadata else "SKILL.md"
        _fail(f"Skill {name} must contain {required}")
    skill_text = skill_file.read_text(encoding="utf-8")
    frontmatter_match = FRONTMATTER_PATTERN.match(skill_text)
    name_match = (
        FRONTMATTER_NAME_PATTERN.search(frontmatter_match.group("frontmatter"))
        if frontmatter_match is not None
        else None
    )
    if name_match is None or name_match.group(1) != name:
        _fail(f"Skill frontmatter name must match directory name: {name}")


def _validate_sources(
    source_root: Path,
    external_skills: Mapping[str, Path] | None = None,
) -> tuple[Path, dict[str, Path]]:
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
        _validate_skill(name, skill_dir, require_metadata=True)
        skills[name] = skill_dir
    for name, skill_dir in sorted((external_skills or {}).items()):
        if name in skills:
            _fail(f"External skill conflicts with repository skill: {name}")
        _reject_symlinks(skill_dir)
        _validate_skill(name, skill_dir, require_metadata=False)
        skills[name] = skill_dir
    if not skills:
        _fail("No deployable skills found")
    try:
        sync_navigators(source_root, check=True)
    except NavigatorSyncError as error:
        _fail(str(error))
    return instructions, skills


def _relative_path(value: object, *, field: str, name: str) -> Path:
    if not isinstance(value, str) or not value:
        _fail(f"External skill {name} has invalid {field}")
    path = Path(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        _fail(f"External skill {name} has unsafe {field}: {value}")
    return path


def _load_external_skill_specs(source_root: Path) -> tuple[ExternalSkillSpec, ...]:
    manifest = source_root / "config" / EXTERNAL_SKILLS_FILENAME
    if not manifest.exists():
        return ()
    if manifest.is_symlink() or not manifest.is_file():
        _fail(f"Invalid external skill manifest: {manifest}")
    try:
        loaded = json.loads(manifest.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        _fail(f"Cannot read external skill manifest {manifest}: {error}")
    if not isinstance(loaded, dict):
        _fail(f"External skill manifest must contain an object: {manifest}")

    specs: list[ExternalSkillSpec] = []
    for name, value in sorted(loaded.items()):
        if not isinstance(name, str) or SKILL_NAME_PATTERN.fullmatch(name) is None:
            _fail(f"Invalid external skill name in {manifest}: {name}")
        if not isinstance(value, dict) or set(value) != {"path", "submodule"}:
            _fail(f"External skill {name} must define path and submodule")
        specs.append(
            ExternalSkillSpec(
                name=name,
                submodule=_relative_path(
                    value["submodule"], field="submodule", name=name
                ),
                path=_relative_path(value["path"], field="path", name=name),
            )
        )
    return tuple(specs)


def _git(
    repository: Path,
    arguments: Sequence[str],
    *,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            ["git", "-c", "protocol.file.allow=always", *arguments],
            cwd=repository,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        _fail(f"Cannot run Git in {repository}: {error}")
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown Git error"
        _fail(f"Git command failed in {repository}: {detail}")
    return result


def _submodule_configuration(source_root: Path, path: Path) -> tuple[str, str | None]:
    modules_file = source_root / ".gitmodules"
    if modules_file.is_symlink() or not modules_file.is_file():
        _fail(f"External skill submodule is not configured: {path}")
    configured = _git(
        source_root,
        [
            "config",
            "--file",
            str(modules_file),
            "--get-regexp",
            r"^submodule\..*\.path$",
        ],
    ).stdout.splitlines()
    key = next(
        (
            line.split(maxsplit=1)[0]
            for line in configured
            if len(line.split(maxsplit=1)) == 2
            and line.split(maxsplit=1)[1] == path.as_posix()
        ),
        None,
    )
    if key is None:
        _fail(f"External skill submodule is not configured: {path}")
    prefix = key.removesuffix(".path")
    url = _git(
        source_root,
        ["config", "--file", str(modules_file), "--get", f"{prefix}.url"],
    ).stdout.strip()
    if not url:
        _fail(f"External skill submodule has no URL: {path}")
    branch_result = _git(
        source_root,
        ["config", "--file", str(modules_file), "--get", f"{prefix}.branch"],
        check=False,
    )
    branch = branch_result.stdout.strip() if branch_result.returncode == 0 else None
    return url, branch


def _submodule_is_initialized(path: Path) -> bool:
    if not path.is_dir():
        return False
    result = _git(path, ["rev-parse", "--show-toplevel"], check=False)
    return (
        result.returncode == 0
        and Path(result.stdout.strip()).resolve() == path.resolve()
    )


def _require_clean_submodule(path: Path) -> None:
    changes = _git(path, ["status", "--porcelain"]).stdout.strip()
    if changes:
        _fail(f"Refusing to use locally modified external skill submodule: {path}")


def _submodule_revision(path: Path) -> str:
    return _git(path, ["rev-parse", "HEAD"]).stdout.strip()


def _pinned_submodule_revision(source_root: Path, path: Path) -> str:
    result = _git(source_root, ["ls-files", "--stage", "--", path.as_posix()])
    fields = result.stdout.split()
    if (
        len(fields) < 3
        or fields[0] != "160000"
        or not re.fullmatch(r"[0-9a-fA-F]{40,64}", fields[1])
    ):
        _fail(f"External skill path is not a tracked Git submodule: {path}")
    return fields[1]


def _clone_submodule(
    source_root: Path,
    spec: ExternalSkillSpec,
    destination: Path,
    *,
    update: bool,
) -> Path:
    url, branch = _submodule_configuration(source_root, spec.submodule)
    clone_arguments = ["clone", "--quiet"]
    if update and branch:
        clone_arguments.extend(["--branch", branch, "--single-branch"])
    clone_arguments.extend(["--", url, str(destination)])
    _git(source_root, clone_arguments)
    if not update:
        revision = _pinned_submodule_revision(source_root, spec.submodule)
        _git(destination, ["checkout", "--quiet", "--detach", revision])
    return destination


def _external_skill_path(submodule: Path, spec: ExternalSkillSpec) -> Path:
    if submodule.is_symlink():
        _fail(f"Refusing symlinked external skill path: {submodule}")
    skill = submodule
    for part in spec.path.parts:
        skill /= part
        if skill.is_symlink():
            _fail(f"Refusing symlinked external skill path: {skill}")
    resolved_submodule = submodule.resolve()
    resolved_skill = skill.resolve()
    if (
        resolved_skill != resolved_submodule
        and resolved_submodule not in resolved_skill.parents
    ):
        _fail(f"External skill path escapes its submodule: {skill}")
    return skill


@contextmanager
def _external_skill_sources(
    source_root: Path,
    *,
    update: bool,
    dry_run: bool,
) -> Iterator[tuple[dict[str, Path], tuple[str, ...]]]:
    specs = _load_external_skill_specs(source_root)
    if not specs:
        yield {}, ()
        return

    submodules = sorted({spec.submodule for spec in specs})
    pinned_revisions: dict[Path, str] = {}
    current_revisions: dict[Path, str | None] = {}
    for submodule in submodules:
        _submodule_configuration(source_root, submodule)
        pinned_revisions[submodule] = _pinned_submodule_revision(source_root, submodule)
        checked_out = source_root / submodule
        if _submodule_is_initialized(checked_out):
            _require_clean_submodule(checked_out)
            current_revisions[submodule] = _submodule_revision(checked_out)
        else:
            current_revisions[submodule] = None

    with tempfile.TemporaryDirectory(prefix="external-skills-") as temporary_name:
        temporary_root = Path(temporary_name)
        prepared: dict[Path, Path] = {}
        actions: list[str] = []
        if dry_run:
            for spec in specs:
                if spec.submodule in prepared:
                    continue
                checked_out = source_root / spec.submodule
                current_revision = current_revisions[spec.submodule]
                pinned_revision = pinned_revisions[spec.submodule]
                if not update and current_revision == pinned_revision:
                    prepared[spec.submodule] = checked_out
                else:
                    clone_destination = temporary_root / f"submodule-{len(prepared)}"
                    prepared[spec.submodule] = _clone_submodule(
                        source_root,
                        spec,
                        clone_destination,
                        update=update,
                    )
                desired_revision = _submodule_revision(prepared[spec.submodule])
                if current_revision is None:
                    actions.append(f"INITIALIZE external source {spec.submodule}")
                elif current_revision != desired_revision:
                    verb = "UPDATE" if update else "RESET"
                    actions.append(f"{verb} external source {spec.submodule}")
        else:
            paths = [path.as_posix() for path in submodules]
            arguments = ["submodule", "update", "--init"]
            if update:
                arguments.append("--remote")
            arguments.extend(["--checkout", "--", *paths])
            _git(source_root, arguments)
            for submodule in submodules:
                checked_out = source_root / submodule
                if not _submodule_is_initialized(checked_out):
                    _fail(
                        f"Git did not initialize external skill submodule: {submodule}"
                    )
                _require_clean_submodule(checked_out)
                prepared[submodule] = checked_out
                new_revision = _submodule_revision(checked_out)
                old_revision = current_revisions[submodule]
                if old_revision is None:
                    actions.append(f"INITIALIZE external source {submodule}")
                elif old_revision != new_revision:
                    verb = "UPDATE" if update else "RESET"
                    actions.append(f"{verb} external source {submodule}")

        sources = {
            spec.name: _external_skill_path(prepared[spec.submodule], spec)
            for spec in specs
        }
        yield sources, tuple(actions)


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


def _resolve_codex_home(source_root: Path, codex_home: Path) -> Path:
    expanded_codex_home = codex_home.expanduser()
    if expanded_codex_home.is_symlink():
        _fail(f"Refusing symlinked Codex home: {expanded_codex_home}")
    resolved_codex_home = expanded_codex_home.resolve()
    unsafe_targets = {
        Path(resolved_codex_home.anchor),
        Path.home().resolve(),
        source_root.resolve(),
    }
    if (
        resolved_codex_home in unsafe_targets
        or source_root.resolve() in resolved_codex_home.parents
    ):
        _fail(f"Unsafe Codex home target: {resolved_codex_home}")
    return resolved_codex_home


def purge_skills(
    source_root: Path,
    codex_home: Path,
    *,
    dry_run: bool = False,
    force: bool = False,
) -> tuple[str, ...]:
    codex_home = _resolve_codex_home(source_root, codex_home)

    state_path = codex_home / STATE_FILENAME
    instructions_hash, managed_skills = _load_state(state_path)
    destination_skills = codex_home / "skills"
    if destination_skills.is_symlink():
        _fail(f"Refusing symlinked skills destination: {destination_skills}")

    removals: list[tuple[str, Path]] = []
    for name, deployed_hash in sorted(managed_skills.items()):
        destination = destination_skills / name
        if destination.is_symlink():
            _fail(f"Invalid skill destination: {destination}")
        if not destination.exists():
            continue
        if not destination.is_dir():
            _fail(f"Invalid skill destination: {destination}")
        _reject_symlinks(destination)
        if _hash_tree(destination) != deployed_hash and not force:
            message = (
                f"Refusing to remove locally modified managed skill {name}; "
                "rerun with --force"
            )
            _fail(message)
        removals.append((name, destination))

    actions = tuple(f"REMOVE managed skill {name}" for name, _ in removals)

    if dry_run:
        return actions

    for _, destination in removals:
        shutil.rmtree(destination)
    if managed_skills:
        _atomic_write_json(
            state_path,
            {
                "instructions_hash": instructions_hash,
                "managed_skills": {},
                "version": STATE_VERSION,
            },
        )
    return actions


def _deploy_validated(
    source_root: Path,
    codex_home: Path,
    instructions: Path,
    source_skills: Mapping[str, Path],
    *,
    dry_run: bool = False,
    force: bool = False,
) -> tuple[str, ...]:
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


def deploy(
    source_root: Path,
    codex_home: Path,
    *,
    dry_run: bool = False,
    force: bool = False,
    update_external_skills: bool = False,
) -> tuple[str, ...]:
    source_root = source_root.resolve()
    codex_home = _resolve_codex_home(source_root, codex_home)
    with _external_skill_sources(
        source_root,
        update=update_external_skills,
        dry_run=dry_run,
    ) as (external_skills, external_actions):
        instructions, source_skills = _validate_sources(source_root, external_skills)
        deployment_actions = _deploy_validated(
            source_root,
            codex_home,
            instructions,
            source_skills,
            dry_run=dry_run,
            force=force,
        )
        return external_actions + deployment_actions


def _parse_args(arguments: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Deploy repository-owned Codex instructions and skills, or purge only "
            "the skills."
        )
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
        help="Overwrite conflicting content or remove modified managed skills.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--purge-skills",
        action="store_true",
        help="Remove repository-managed skills without removing global AGENTS.md.",
    )
    mode.add_argument(
        "--update-external-skills",
        action="store_true",
        help=(
            "Advance external skill submodules to their tracked branches, deploy "
            "them, and leave the new revisions for commit."
        ),
    )
    return parser.parse_args(arguments)


def main(
    arguments: Sequence[str] | None = None,
    *,
    repository_root: Path | None = None,
) -> int:
    options = _parse_args(sys.argv[1:] if arguments is None else arguments)
    if repository_root is None:
        repository_root = Path(__file__).resolve().parents[1]
    try:
        if options.purge_skills:
            actions = purge_skills(
                repository_root,
                options.codex_home,
                dry_run=options.dry_run,
                force=options.force,
            )
        else:
            actions = deploy(
                repository_root,
                options.codex_home,
                dry_run=options.dry_run,
                force=options.force,
                update_external_skills=options.update_external_skills,
            )
    except DeploymentError as error:
        print(f"Deployment failed: {error}", file=sys.stderr)
        return 1
    if not actions:
        message = (
            "No repository-managed skills are installed."
            if options.purge_skills
            else "Codex workflow is already current."
        )
        print(message)
        return 0
    prefix = "Would " if options.dry_run else ""
    for action in actions:
        print(f"{prefix}{action}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
