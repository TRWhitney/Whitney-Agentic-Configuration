"""Send local browser operations across the evaluation sandbox boundary."""

from __future__ import annotations

import base64
import json
import os
import sys
import time
import uuid
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: browser-run SCENARIO_JSON OUTPUT_DIR", file=sys.stderr)
        return 2
    scenario = json.loads(Path(sys.argv[1]).read_text())
    queue = Path(os.environ["CODEX_HOME"]) / "work-system/browser-queue"
    identifier = uuid.uuid4().hex
    request = queue / (identifier + ".request.json")
    pending = queue / (identifier + ".pending")
    pending.write_text(json.dumps(scenario))
    pending.rename(request)
    response = queue / (identifier + ".response.json")
    deadline = time.monotonic() + 90
    while not response.is_file():
        if time.monotonic() >= deadline:
            print("Browser worker did not respond.", file=sys.stderr)
            return 1
        time.sleep(0.05)
    result = json.loads(response.read_text())
    if result["returncode"]:
        print(result["stderr"], file=sys.stderr)
        return int(result["returncode"])
    output = Path(sys.argv[2])
    output.mkdir(parents=True, exist_ok=True)
    for capture in result["images"]:
        (output / (capture["name"] + ".png")).write_bytes(
            base64.b64decode(capture["data_url"].split(",", 1)[1])
        )
    for capture in result["structures"]:
        (output / capture["name"]).write_text(capture["content"])
    for observation in result["result"]["observations"]:
        if isinstance(observation, dict) and "capture" in observation:
            name = observation["capture"]
            observation["screenshot"] = str(output / (name + ".png"))
            observation["structure"] = str(output / (name + ".json"))
    result["result"]["output"] = str(output)
    print(json.dumps(result["result"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
