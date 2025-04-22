#!/usr/bin/env python3
"""Main function."""
from rich.highlighter import NullHighlighter
from rich.logging import RichHandler
import logging

from tempor.cli import main

logging.basicConfig(
    level='INFO',
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(
            rich_tracebacks=True,
            markup=True,
            show_level=False,
            show_path=False,
            show_time=False,
            highlighter=NullHighlighter()
        )
    ],
)

if __name__ == "__main__":
    main()
