"""
Helper for the Brei workflow in `entangled.toml`, which builds the site.

`python workflow.py tasks` prints a workflow, that is included back into
Brei. Entangled lists the Markdown it reads and the files it writes in
`.entangled/filedb.json`, REPL sessions among them. We add a task for each
session, running it in a Jupyter kernel, and for each page, weaving it into
`.entangled/woven` with code block titles and the output of REPL sessions.

`python workflow.py static` mirrors the folders in `docs` and copies all
other files, like images and scripts, to `.entangled/woven`.
"""

import json
import shlex
import shutil
import sys
from pathlib import Path


DOCS = Path("docs")
WOVEN = Path(".entangled/woven")


def is_session(path: Path) -> bool:
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return False
    return isinstance(data, dict) and {"config", "commands"} <= data.keys()


def tasks():
    filedb = json.loads(Path(".entangled/filedb.json").read_text())
    targets = [Path(t) for t in filedb["targets"]]
    pages = [Path(f) for f in filedb["files"]
             if Path(f) not in targets and Path(f).suffix == ".md" and Path(f).is_relative_to(DOCS)]
    sessions = [t for t in targets if t.suffix == ".json" and is_session(t)]
    code = [t.as_posix() for t in targets if t not in sessions]
    outputs = [s.with_suffix(".out.json").as_posix() for s in sessions]

    result: list[dict[str, object]] = [{
        "description": f"running REPL session `{session.as_posix()}`",
        "stdin": session.as_posix(),
        "stdout": output,
        "requires": [session.as_posix(), *code],
        "script": "repl-session",
    } for session, output in zip(sessions, outputs)]

    woven: list[str] = []
    for page in pages:
        out = (WOVEN / page.relative_to(DOCS)).as_posix()
        woven.append(out)
        result.append({
            "description": f"weaving `{page.as_posix()}`",
            "creates": [out],
            "requires": [page.as_posix(), "#static", *outputs],
            "script": shlex.join(["entangled", "weave", "-f", "title", "-f", "repl",
                                  "-o", out, page.as_posix()]),
        })

    result.append({"name": "woven", "requires": woven})
    print(json.dumps({"task": result}, indent=2))


def static():
    WOVEN.mkdir(parents=True, exist_ok=True)
    for path in DOCS.glob("**/*"):
        target = WOVEN / path.relative_to(DOCS)
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.suffix != ".md" and (
                not target.exists() or target.stat().st_mtime < path.stat().st_mtime):
            target.parent.mkdir(parents=True, exist_ok=True)
            _ = shutil.copy2(path, target)


if __name__ == "__main__":
    match sys.argv[1:]:
        case ["tasks"]:
            tasks()
        case ["static"]:
            static()
        case _:
            sys.exit("usage: python workflow.py tasks|static")
