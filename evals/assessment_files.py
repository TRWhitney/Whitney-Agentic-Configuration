"""Write complete blinded evidence for read-only inspection."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import cast

from pydantic import JsonValue

from evals.evidence import EvidenceRun
from evals.gui import image_bytes

EVIDENCE_FORMAT = (
    "Each output index lists initial artifacts and complete snapshots after each turn. "
    "Artifact keys are original paths; values name readable files in this directory. "
    "Frames keep final replies separate from commentary and unfinished text. "
    "They include requests, observed actions, navigation, Git state, and "
    "service records. Each frame labels its event. Only fixture_edit frames contain "
    "supplied edits. artifact_changes lists added, modified and removed paths since "
    "the previous snapshot, or initial_artifacts for the first frame. Changes during "
    "message frames are observed results of the candidate's turn; shell commands "
    "do not include every editing tool. file_changes actions preserve native patches "
    "and their completion status. "
    "A frame with completed=false was interrupted. "
    "agent_results preserves observed native child turns or status messages. "
    "Child turns are fetched after the parent turn; agentCompleted records the "
    "runtime completion notification in the parent action order. "
    "Missing native reviewer findings "
    "are unavailable evidence, not a failed review. "
    "Browser records marked private_grader "
    "cannot establish that the candidate performed verification. candidate_browser "
    "records establish browser actions and capture generation, "
    "not image inspection. "
    "candidate_image_view records native image inspection; artifact images only show "
    "file contents. Browser images name PNG files. "
    "Open them when assessing visual work."
)


def _json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def write_inputs(root: Path, packet: dict[str, object]) -> dict[str, object]:
    """Materialize paths chosen by the runner, never by supplied artifact names."""
    images = cast(dict[str, str], packet["images"])
    for name, data in images.items():
        path = root / "images" / (name + ".png")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(image_bytes(data))

    def artifacts(files: dict[str, str]) -> dict[str, str]:
        result = {}
        for name, text in files.items():
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            relative = "artifacts/" + digest + ".txt"
            path = root / relative
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            result[name] = relative
        return result

    outputs = []
    for output in cast(list[dict[str, object]], packet["outputs"]):
        label = str(output["label"])
        prefix = "outputs/" + label
        index: dict[str, object] = {
            "initial_artifacts": artifacts(
                cast(dict[str, str], output["initial_files"])
            ),
            "initial_service_state": output["initial_service_state"],
            "frames": [],
        }
        frames = cast(list[dict[str, object]], index["frames"])
        previous = cast(dict[str, str], index["initial_artifacts"])
        for number, frame in enumerate(cast(list[dict[str, object]], output["frames"])):
            location = prefix + f"/turn-{number + 1}"
            entry = {
                k: v
                for k, v in frame.items()
                if k
                not in {
                    "files",
                    "commands",
                    "browser",
                    "prompt",
                    "reply",
                    "partial_reply",
                    "commentary",
                }
            }
            current = artifacts(cast(dict[str, str], frame["files"]))
            entry["artifacts"] = current
            entry["artifact_changes"] = {
                "added": sorted(current.keys() - previous.keys()),
                "modified": sorted(
                    name
                    for name in current.keys() & previous.keys()
                    if current[name] != previous[name]
                ),
                "removed": sorted(previous.keys() - current.keys()),
            }
            previous = current
            for key in ("prompt", "reply", "partial_reply"):
                relative = location + "/" + key + ".txt"
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(str(frame[key]), encoding="utf-8")
                entry[key] = relative
            actions = []
            for i, action in enumerate(cast(list[object], frame["commands"])):
                relative = location + f"/actions/{i + 1}.json"
                _json(root / relative, action)
                actions.append(relative)
            relative = location + "/commentary.json"
            _json(root / relative, frame.get("commentary", []))
            entry["commentary"] = relative
            entry["actions"] = actions
            browser = []
            for i, record in enumerate(cast(list[object], frame["browser"])):
                relative = location + f"/browser/{i + 1}.json"
                _json(root / relative, record)
                browser.append(relative)
            entry["browser"] = browser
            frames.append(entry)
        relative = prefix + "/index.json"
        _json(root / relative, index)
        outputs.append({"label": label, "path": relative})
    manifest = {
        "criteria": packet["criteria"],
        "outputs": outputs,
        "evidence_format": EVIDENCE_FORMAT,
        "response_schema": packet["response_schema"],
    }
    _json(root / "manifest.json", manifest)
    return manifest


def blind_outputs(
    runs: list[EvidenceRun],
) -> tuple[list[dict[str, object]], dict[str, str]]:
    """Return plain snapshots, replacing embedded images with file references."""
    images: dict[str, str] = {}

    def browser(value: JsonValue) -> JsonValue:
        if isinstance(value, list):
            return [browser(v) for v in value]
        if isinstance(value, dict):
            result = {k: browser(v) for k, v in value.items() if k != "data_url"}
            if "data_url" in value:
                data = value["data_url"]
                if not isinstance(data, str):
                    raise ValueError("Invalid browser image data.")
                digest = hashlib.sha256(image_bytes(data)).hexdigest()
                images[digest] = data
                result["path"] = "images/" + digest + ".png"
            return result
        return value

    outputs: list[dict[str, object]] = []
    for run in runs:
        frames = []
        for frame in run.frames:
            data = asdict(frame)
            data["browser"] = browser(cast(JsonValue, frame.browser))
            frames.append(data)
        outputs.append(
            {
                "initial_files": run.initial_files,
                "initial_service_state": run.initial_service_state,
                "frames": frames,
            }
        )
    return outputs, images


def fingerprint(root: Path) -> dict[str, str]:
    result = {}
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError("Judge changed evidence with a symbolic link.")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return result
