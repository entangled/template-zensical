# My Entangled Project
[![Entangled badge](https://img.shields.io/badge/entangled-Use%20the%20source!-%2300aeff)](https://entangled.github.io/)

## First time running
You need [`uv`](https://docs.astral.sh/uv/) installed; it takes care of Python (>= 3.13).

```shell
uv sync
```

## Build

```shell
uv run build.py
```

This synchronizes code and Markdown, runs REPL sessions in a Jupyter kernel, and renders the Markdown in `docs` to a website in `site`. Zensical has no plugins, so `build.py` first weaves the Markdown into `.entangled/woven`, adding code block titles and REPL output. Edit the pages in `docs`, not the woven ones.

## Live preview

```shell
uv run entangled serve --watch docs --build "uv run build.py" site
```

Open [localhost:8000](http://localhost:8000). The site is rebuilt and the browser reloads when you change a page in `docs`. To edit code in `src` and have it show up in the documentation, also run `uv run entangled watch`.
