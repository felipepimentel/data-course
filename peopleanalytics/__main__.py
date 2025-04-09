#!/usr/bin/env python
"""
Main entry point for the peopleanalytics package.
This allows running the package directly with python -m peopleanalytics
"""

from peopleanalytics.cli import CLI


def main():
    """Entry point for the peopleanalytics CLI."""
    cli = CLI()
    return cli.run()


if __name__ == "__main__":
    main() 