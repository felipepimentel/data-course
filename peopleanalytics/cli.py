"""
Command Line Interface for People Analytics.

This module provides the main CLI for the People Analytics system.
"""

import argparse
import logging
import sys

from rich.console import Console

from .cli_commands import COMMANDS


class CLI:
    """
    Command Line Interface for People Analytics.

    This class provides the main entry point for the CLI application.
    It parses command-line arguments and dispatches to the appropriate
    command handler.
    """

    def __init__(self):
        """Initialize the CLI with a console for rich output."""
        self.console = Console()

    def run(self) -> int:
        """
        Run the CLI application.

        Returns:
            int: Return code (0 for success, non-zero for error)
        """
        # Parse command-line arguments
        parser = self.create_parser()
        args = parser.parse_args()

        # Configure logging based on verbose flag
        log_level = logging.DEBUG if args.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        # If no command was provided, show help
        if not args.command:
            parser.print_help()
            return 1

        # Get the command class and execute it
        command_class = COMMANDS.get(args.command)
        if not command_class:
            self.console.print(f"[bold red]Unknown command: {args.command}[/bold red]")
            return 1

        # Create command instance and execute it
        command = command_class()
        return command.execute(args)

    def create_parser(self) -> argparse.ArgumentParser:
        """
        Create the command-line argument parser.

        Returns:
            argparse.ArgumentParser: The configured parser
        """
        # Create main parser
        parser = argparse.ArgumentParser(
            description="People Analytics CLI", prog="people_analytics"
        )

        # Add global arguments
        parser.add_argument(
            "--verbose", "-v", action="store_true", help="Enable verbose output"
        )

        # Create subparsers for commands
        subparsers = parser.add_subparsers(
            dest="command",
            title="Commands",
            description="Available commands",
            help="Command to execute",
        )

        # Add all registered commands
        for command_name, command_class in COMMANDS.items():
            command_parser = subparsers.add_parser(
                command_name,
                help=command_class.__doc__.split("\n")[0]
                if command_class.__doc__
                else None,
            )

            # Let the command add its own arguments
            command = command_class()
            command.add_arguments(command_parser)

        return parser


def main():
    """Run the CLI application."""
    cli = CLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
