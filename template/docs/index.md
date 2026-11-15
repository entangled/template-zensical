# Welcome to Zensical/Entangled

For full documentation visit [zensical.org](https://zensical.org) and [entangled.github.io](https://entangled.github.io).

## Literate programming

Code blocks with a `file` attribute are tangled to source files. This one computes the Fibonacci numbers, \(F_n = F_{n-1} + F_{n-2}\), by keeping track of the last two numbers.

``` {.python file=src/fibonacci.py}
def fibonacci(n: int) -> list[int]:
    """The first `n` Fibonacci numbers."""
    a, b = 0, 1
    result = []
    for _ in range(n):
        <<fibonacci-step>>
    return result
```

Each step appends the current number and moves one ahead.

``` {.python #fibonacci-step}
result.append(a)
a, b = b, a + b
```

## REPL sessions

Code blocks with the `repl` class run in a Jupyter kernel. The first block of a session gives an identifier and a `session` file; following blocks with the same identifier continue that session. Their output is inserted below each block.

``` {.python .repl #demo session=.entangled/repl/index.json}
from fibonacci import fibonacci
fibonacci(10)
```

Printed output is shown separately from the result.

``` {.python .repl #demo}
for n, f in enumerate(fibonacci(5)):
    print(f"F_{n} = {f}")
```

## Commands

* `uv run entangled brei site` - Tangle, run REPL sessions and build the site.
* `uv run entangled serve --watch docs --build "entangled brei site" site` - Live preview.
* `uv run entangled tangle` - Extract source files.
* `uv run entangled stitch` - Merge changes into markdown.
* `uv run entangled -h` - Print help message and exit.

## Help

* [Entangled](https://entangled.github.io)
* [Zensical](https://zensical.org)
* [REPL sessions](https://entangled.github.io/repl-session)
* [Brei workflows](https://entangled.github.io/brei)

## Project layout

    zensical.toml   # The Zensical configuration file.
    entangled.toml  # The Entangled configuration file.
    workflow.py     # Generates the workflow that builds the site.
    docs/
        index.md    # The documentation homepage.
        ...         # Other markdown pages, images and other files.
    src/            # Tangled source code.
