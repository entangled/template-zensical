"""
Build the documentation:

1. synchronize code and Markdown with `entangled sync`,
2. run the REPL sessions in a Jupyter kernel,
3. weave the Markdown in `docs` into `.entangled/woven`, adding code block
   titles and the output of REPL sessions,
4. render the woven Markdown with Zensical into `site`.

Run with `uv run build.py`.
"""

from pathlib import Path
import shutil
import subprocess
import sys

from entangled.config import read_config
from entangled.interface import Context
from entangled.logging import configure, logger
from entangled.model import ReferenceId, ReferenceMap
from entangled.model.properties import Class, get_attribute_string
from entangled.weave import codeblock_filter, filters, transform_markdown
from repl_session import read_session, run_session, write_session


DOCS = Path("docs")
WOVEN = Path(".entangled/woven")

log = logger()


def find_sessions(context: Context, pages: list[Path]) -> set[Path]:
    """Find the session files of all REPL sessions in the given pages."""
    sessions: set[Path] = set()

    @codeblock_filter
    def collect(refs: ReferenceMap, r: ReferenceId):
        props = refs[r].properties
        if Class("repl") in props and (session := get_attribute_string(props, "session")):
            sessions.add(Path(session))
        return [r]

    for page in pages:
        for _ in transform_markdown(context, page.read_text(), collect, filename=page):
            pass
    return sessions


def run_sessions(sessions: set[Path], pages: list[Path]):
    """Run each session whose output is older than the session or any page:
    changes to the code it uses only show in the Markdown."""
    if not sessions:
        return
    newest = max(p.stat().st_mtime for p in [*sessions, *pages])
    for session in sorted(sessions):
        output = session.with_suffix(".out.json")
        if output.exists() and output.stat().st_mtime > newest:
            continue
        log.info(f"running REPL session `{session}`")
        with session.open() as f:
            result = run_session(read_session(f))
        with output.open("w") as f:
            write_session(result, f)


def weave(context: Context, pages: list[Path]):
    """Copy `docs` to `.entangled/woven` and weave each page."""
    shutil.rmtree(WOVEN, ignore_errors=True)
    shutil.copytree(DOCS, WOVEN)
    for page in pages:
        text = "".join(transform_markdown(
            context, page.read_text(), filters["title"], filters["repl"], filename=page))
        _ = (WOVEN / page.relative_to(DOCS)).write_text(text)


def main():
    configure()
    _ = subprocess.run([sys.executable, "-m", "entangled.main", "sync"], check=True)

    context = Context()
    context |= read_config(context.fs)
    pages = sorted(DOCS.glob("**/*.md"))

    run_sessions(find_sessions(context, pages), pages)
    weave(context, pages)
    _ = subprocess.run([sys.executable, "-m", "zensical", "build"], check=True)


if __name__ == "__main__":
    main()
