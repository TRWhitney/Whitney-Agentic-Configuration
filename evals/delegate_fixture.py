"""Local delegation stand-in for inspecting submitted assignments."""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path


def main() -> None:
    home = Path(__file__).resolve().parent.parent
    settings = json.loads((home / "work-system/delegate.json").read_text())
    root = Path(settings["root"])
    assignment = Path(sys.argv[1]).resolve()
    if not assignment.is_relative_to(root):
        raise ValueError("Assignment must be inside the project.")
    prompt = assignment.read_text()
    if not prompt.strip():
        raise ValueError("Assignment is empty.")
    scenario = settings["scenario"]
    if scenario == "label":
        path = root / "docs/inventory.md"
        path.write_text(path.read_text().replace("inventroy", "inventory"))
        result = "Corrected docs/inventory.md. The label check passes."
    elif scenario == "total":
        path = root / "src/app.py"
        path.write_text(
            path.read_text().replace(
                'sum(item["quantity"] for item in items)',
                'sum(max(0, item["quantity"]) for item in items)',
            )
        )
        result = "Implemented src/app.py. The assigned stock-total check passes."
    elif scenario == "review":
        result = "Intent and engineering review: pass, no findings."
    else:
        raise ValueError("Unknown delegation scenario.")
    identifier = uuid.uuid4().hex
    with (home / "work-system/delegations.jsonl").open("a") as stream:
        stream.write(json.dumps({"id": identifier, "prompt": prompt}) + "\n")
    print("DELEGATION_FIXTURE_ID:" + identifier)
    print(result)


if __name__ == "__main__":
    main()
