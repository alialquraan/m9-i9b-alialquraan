"""Command-line entry point.

Usage:
    python cli.py "find me a quick Italian recipe with eggplant"

Prints the top-5 results from ``pipeline(query)`` one per line.
"""

import argparse
import sys

from pipeline import pipeline


def main() -> int:
    """Parse argv, run the pipeline, pretty-print results.

    Exit code is 0 on success (including empty results — empty is a valid
    pipeline outcome on UNKNOWN intent or all-NIL linker output).
    """
    # TODO: build an argparse.ArgumentParser with a single positional
    # `query` argument (help: "natural-language query string").
    # TODO: call pipeline(args.query).
    # TODO: pretty-print each result row, one per line, including at
    # least the recipe name and URI. Format suggestion:
    #     "  {name}  <{recipe}>"
    raise NotImplementedError(
        "Implement main() — see the integration guide for the task description."
    )


if __name__ == "__main__":
    sys.exit(main() or 0)
