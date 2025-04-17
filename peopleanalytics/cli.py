"""
Command Line Interface for People Analytics.

This module provides the main CLI for the People Analytics system.
"""

import argparse
import logging
import sys

from rich.console import Console

# Import essential modules for comprehensive analysis
# Import domain models for data processing
# Import talent development modules for advanced analysis
from peopleanalytics.cli_commands import (
    SyncCommand,
)

# Map commands to their corresponding classes
COMMANDS = {
    "sync": SyncCommand,
}


def main():
    """Command-line interface entry point."""
    cli = CLI()
    return cli.run()


def show_skills_analyzer_help():
    """Show help information about the skills analyzer functionality."""
    print("\nSkills Analyzer Usage Examples:")
    print("-------------------------------")
    print("Basic usage (all skills analysis features enabled by default):")
    print("  python -m peopleanalytics sync --data-dir=data --output-dir=output")
    print("\nWith organizational chart and year comparison:")
    print("  python -m peopleanalytics sync --data-dir=data --output-dir=output \\")
    print("    --include-org-chart --year-comparison")
    print("\nCustom report output directory:")
    print("  python -m peopleanalytics sync --data-dir=data --output-dir=output \\")
    print("    --report-output-dir=custom_reports")
    print("-------------------------------")


class CLI:
    """Command-line interface for People Analytics."""

    def __init__(self):
        """Initialize the CLI."""
        self.console = Console()
        self.commands = COMMANDS

    def run(self, args=None):
        """Run the command-line interface.

        Args:
            args: Command-line arguments to parse.
                If None, sys.argv[1:] is used.

        Returns:
            int: The exit code for the command.
        """

        # Initialize logging
        self._init_logging()

        # Create parser
        parser = self.create_parser()

        # Parse arguments
        try:
            parsed_args = parser.parse_args(args)
        except SystemExit as exit_exception:
            # Check if this was a help request with the sync command
            if len(sys.argv) > 1 and "--help" in sys.argv and "sync" in sys.argv:
                show_skills_analyzer_help()
            return exit_exception.code

        # If no command was provided, show help
        if not hasattr(parsed_args, "command") or not parsed_args.command:
            parser.print_help()
            show_skills_analyzer_help()
            return 0

        # Get the command object
        command_class = self.commands.get(parsed_args.command)
        if not command_class:
            self.console.print(
                f"[bold red]Error:[/] Unknown command '{parsed_args.command}'"
            )
            return 1

        # Create command instance
        command = command_class()

        # Execute the command
        try:
            return command.execute(parsed_args)
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}", exc_info=True)
            self.console.print(f"[bold red]Error:[/] {str(e)}")
            return 1

    def create_parser(self):
        """
        Create the argument parser for the CLI.

        Returns:
            ArgumentParser: The configured argument parser.
        """
        parser = argparse.ArgumentParser(
            description="People Analytics CLI",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        # Create subparsers for each command
        subparsers = parser.add_subparsers(
            title="commands",
            dest="command",
            help="Command to execute",
        )

        # Add parsers for each command
        for command_name, command_class in COMMANDS.items():
            command_parser = subparsers.add_parser(
                command_name,
                help=f"{command_name.capitalize()} command",
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            )
            command = command_class()
            command.add_arguments(command_parser)

        return parser

    def _init_logging(self):
        """Initialize logging for the CLI."""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)


if __name__ == "__main__":
    sys.exit(main())
