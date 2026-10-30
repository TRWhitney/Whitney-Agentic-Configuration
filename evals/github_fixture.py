"""Local gh stand-in, copied into each disposable runtime without credentials."""

from __future__ import annotations

import json
import pathlib
import re
import shutil
import subprocess
import sys


def main() -> None:
    home = pathlib.Path(__file__).resolve().parents[1]
    args = sys.argv[1:]
    directory = home / "work-system"
    with (directory / "service-calls.jsonl").open("a") as stream:
        stream.write(json.dumps(args) + "\n")
    path = directory / "github.json"
    state = json.loads(path.read_text())

    if "--help" in args or "-h" in args:
        print(
            "Local gh fixture. Commands: auth status, repo view, issue, pr, api.\n"
            "Issue/PR actions: create, view, list, edit, close, reopen, comment.\n"
            "Options: --repo, --title, --body, --body-file, --json, --jq, --search.\n"
            "API options: --method, --field, --raw-field."
        )
        return

    def option(*names: str) -> str | None:
        for index, value in enumerate(args):
            if value in names and index + 1 < len(args):
                return args[index + 1]
            for name in names:
                if value.startswith(name + "="):
                    return value[len(name) + 1 :]
        return None

    def emit(result: object) -> None:
        output = json.dumps(result)
        query = option("--jq", "-q")
        if query:
            jq = shutil.which("jq")
            if jq:
                filtered = subprocess.run(
                    [jq, "-r", query],
                    input=output,
                    text=True,
                    capture_output=True,
                    check=True,
                )
                output = filtered.stdout.rstrip("\n")
            elif re.fullmatch(r"\.[A-Za-z]+", query) and isinstance(result, dict):
                output = str(result.get(query[1:], ""))
            else:
                raise SystemExit("fixture cannot apply this jq expression")
        print(output)

    parts = list(args)
    repository = option("-R", "--repo")
    if repository not in {None, "example/inventory"}:
        raise SystemExit("repository not found in local fixture")
    while parts and parts[0].startswith("-"):
        flag = parts.pop(0)
        if flag in {"-R", "--repo", "--hostname"} and parts:
            parts.pop(0)
    if not parts:
        raise SystemExit("fixture needs a command")
    for record in state["issues"].values():
        record.setdefault("id", 100_000 + record["number"])
    if parts[:2] == ["auth", "status"]:
        print("Logged in to the local GitHub fixture.")
        return
    if parts[:2] == ["repo", "view"]:
        if (
            len(parts) > 2
            and not parts[2].startswith("-")
            and parts[2] != "example/inventory"
        ):
            raise SystemExit("repository not found in local fixture")
        if state["read_error"]:
            raise SystemExit("GitHub unavailable: temporary read failure")
        emit(
            {
                "nameWithOwner": "example/inventory",
                "name": "inventory",
                "owner": {"login": "example"},
                "url": "https://github.com/example/inventory",
                "hasIssuesEnabled": True,
                "viewerPermission": "WRITE",
            }
        )
        return
    if parts[0] == "label":
        labels = state.setdefault("labels", [])
        if parts[1:2] == ["list"]:
            if state["read_error"]:
                raise SystemExit("GitHub unavailable: temporary read failure")
            emit([{"name": name} for name in labels])
        elif parts[1:2] == ["create"] and len(parts) > 2:
            if parts[2] not in labels:
                labels.append(parts[2])
            path.write_text(json.dumps(state))
            print(parts[2])
        else:
            raise SystemExit("unsupported fixture label action")
        return
    if parts[0] not in {"issue", "pr", "api"}:
        raise SystemExit("unsupported fixture command")
    resource = "issues" if parts[0] == "issue" else "prs"
    action = parts[1] if len(parts) > 1 else "view"
    number = next((p for p in parts[2:] if p.isdigit()), None)
    for argument in parts[2:]:
        if argument.startswith("https://github.com/"):
            selected = re.fullmatch(
                r"https://github.com/example/inventory/(issues|pull)/(\d+)", argument
            )
            expected = "issues" if parts[0] == "issue" else "pull"
            if selected is None or selected[1] != expected:
                raise SystemExit("record not found in local fixture")
            number = selected[2]
    fields: dict[str, str] = {}
    value: str | None
    if parts[0] == "api":
        endpoint = next(
            (p for p in parts[1:] if p.lstrip("/").startswith("repos/")), ""
        )
        for index, arg in enumerate(args):
            if arg in {"-f", "-F", "--field", "--raw-field"} and index + 1 < len(args):
                key, _, value = args[index + 1].partition("=")
                fields[key] = value
        method = option("-X", "--method") or ("POST" if fields else "GET")
        if endpoint.strip("/") == "repos/example/inventory" and method.upper() == "GET":
            if state["read_error"]:
                raise SystemExit("GitHub unavailable: temporary read failure")
            emit(
                {
                    "full_name": "example/inventory",
                    "has_issues": True,
                    "html_url": "https://github.com/example/inventory",
                    "permissions": {"push": True, "pull": True},
                }
            )
            return
        relation = re.fullmatch(
            r"/?repos/example/inventory/issues/(\d+)/sub_issues", endpoint
        )
        if relation:
            records = state["issues"]
            if relation[1] not in records:
                raise SystemExit("Not found")
            parent = records[relation[1]]
            if method.upper() == "GET":
                if state["read_error"]:
                    raise SystemExit("GitHub unavailable: temporary read failure")
                emit([records[str(n)] for n in parent.get("sub_issues", [])])
            elif method.upper() == "POST":
                child = next(
                    (
                        r
                        for r in records.values()
                        if str(r["id"]) == fields.get("sub_issue_id")
                    ),
                    None,
                )
                if child is None or child["number"] == parent["number"]:
                    raise SystemExit("Invalid sub-issue")
                children = parent.setdefault("sub_issues", [])
                if child["number"] in children:
                    raise SystemExit("Sub-issue already linked")
                children.append(child["number"])
                path.write_text(json.dumps(state))
                emit(child)
            else:
                raise SystemExit("unsupported fixture method")
            return
        match = re.fullmatch(
            r"/?repos/example/inventory/(issues|pulls)(?:/(\d+))?", endpoint
        )
        if not match:
            raise SystemExit("unsupported fixture endpoint")
        resource = "issues" if match[1] == "issues" else "prs"
        number = match[2]
        action = {
            "GET": "view" if number else "list",
            "PATCH": "edit",
            "POST": "create",
        }.get(method.upper(), "unsupported")
    records = state[resource]
    if state["read_error"] and action in {"view", "list"}:
        print("GitHub unavailable: temporary read failure", file=sys.stderr)
        raise SystemExit(1)
    mutating = action in {"create", "edit", "close", "reopen", "comment"}
    if action == "create":
        number = str(max([int(n) for n in records] + [9]) + 1)
        url_resource = "issues" if resource == "issues" else "pull"
        records[number] = {
            "id": 100_000 + int(number),
            "number": int(number),
            "title": "",
            "body": "",
            "state": "OPEN",
            "labels": [],
            "comments": [],
            "url": f"https://github.com/example/inventory/{url_resource}/{number}",
        }
    if action == "list":
        result: object = list(records.values())
        search = option("--search")
        if search:
            result = [
                r
                for r in records.values()
                if search.casefold().strip('"')
                in (r["title"] + " " + r["body"]).casefold()
            ]
    else:
        number = number or ("10" if resource == "issues" else "12")
        if number not in records:
            print("Not found", file=sys.stderr)
            raise SystemExit(1)
        record = records[number]
        if mutating:
            if action == "comment":
                filename = option("--body-file", "-F")
                body = (
                    pathlib.Path(filename).read_text()
                    if filename and filename != "-"
                    else sys.stdin.read()
                    if filename == "-"
                    else option("--body") or ""
                )
                record["comments"].append({"body": body})
            for key in ("title", "body"):
                if action == "comment":
                    continue
                value = fields.get(key, option("--" + key))
                if (
                    key == "body"
                    and option("--body-file", "-F") is not None
                    and parts[0] != "api"
                ):
                    filename = option("--body-file", "-F")
                    value = (
                        sys.stdin.read()
                        if filename == "-"
                        else pathlib.Path(str(filename)).read_text()
                    )
                if value is not None:
                    record[key] = value
            additions = option("--add-label", "--label", "-l")
            removals = option("--remove-label")
            names = [label["name"] for label in record["labels"]]
            if additions:
                names = list(dict.fromkeys([*names, *additions.split(",")]))
            if removals:
                names = [name for name in names if name not in removals.split(",")]
            record["labels"] = [{"name": name} for name in names]
            if action in {"close", "reopen"}:
                record["state"] = "CLOSED" if action == "close" else "OPEN"
        elif action != "view":
            raise SystemExit("unsupported fixture action")
        result = record
    if mutating:
        timeout = action == "create" and state["write_timeout"]
        if action == "create":
            state["write_timeout"] = False
        path.write_text(json.dumps(state))
        if timeout:
            print("Request timed out while waiting for GitHub", file=sys.stderr)
            raise SystemExit(1)
    if action == "create" and parts[0] in {"issue", "pr"}:
        print(record["url"])
    else:
        emit(result)


if __name__ == "__main__":
    main()
