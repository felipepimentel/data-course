"""
Command Line Interface for People Analytics.

This module provides the main CLI for the People Analytics system.
"""

import argparse
import logging
import sys

from rich.console import Console

from peopleanalytics.cli_commands.analysis_commands import AnalysisCommand
from peopleanalytics.cli_commands.career_commands import CareerSimCommand
from peopleanalytics.cli_commands.doc_commands import DocCommand
from peopleanalytics.cli_commands.skills_commands import (
    SkillsAnalysisCommand,
    SkillsRadarCommand,
)

# Import command classes
from peopleanalytics.cli_commands.sync_commands import SyncCommand


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
    print("\nGenerate skill radar charts:")
    print(
        "  python -m peopleanalytics skills-radar --data-dir=data --output-dir=output/viz"
    )
    print("\nPerform comprehensive skills analysis:")
    print(
        "  python -m peopleanalytics skills-analysis --data-dir=data --output-dir=output/analysis"
    )
    print("-------------------------------")


class CLI:
    """Command-line interface for peopleanalytics."""

    def __init__(self):
        """Initialize the CLI."""
        self.console = Console()
        self._commands = {
            "sync": SyncCommand(),
            "doc": DocCommand(),
            "analysis": AnalysisCommand(),
            "career-sim": CareerSimCommand(),
            "skills-radar": SkillsRadarCommand(),
            "skills-analysis": SkillsAnalysisCommand(),
        }

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
        command = self._commands.get(parsed_args.command)
        if not command:
            self.console.print(
                f"[bold red]Error:[/] Unknown command '{parsed_args.command}'"
            )
            return 1

        # Execute the command
        try:
            return command.execute(parsed_args)
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}", exc_info=True)
            self.console.print(f"[bold red]Error:[/] {str(e)}")
            return 1

    def create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser for the CLI.

        Returns:
            An argparse.ArgumentParser instance
        """
        parser = argparse.ArgumentParser(
            description="People Analytics Data Processor", prog="peopleanalytics"
        )
        parser.add_argument(
            "--verbose", action="store_true", help="Enable verbose output"
        )
        parser.add_argument(
            "--log-level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            default="INFO",
            help="Set the logging level",
        )
        parser.add_argument(
            "--config",
            type=str,
            help="Path to configuration file",
        )
        parser.add_argument(
            "--version", action="store_true", help="Print version and exit"
        )

        # Add subcommands
        subparsers = parser.add_subparsers(dest="command", help="Command to run")

        # Add sync command
        sync_parser = subparsers.add_parser("sync", help="Synchronize and process data")
        self._commands["sync"].add_arguments(sync_parser)

        # Add doc command
        doc_parser = subparsers.add_parser("doc", help="Generate documentation")
        self._commands["doc"].add_arguments(doc_parser)

        # Add analysis command
        analysis_parser = subparsers.add_parser("analysis", help="Run analysis tools")
        self._commands["analysis"].add_arguments(analysis_parser)

        # Add career simulation command
        career_parser = subparsers.add_parser(
            "career-sim", help="Run career simulation tools"
        )
        self._commands["career-sim"].add_arguments(career_parser)

        # Add skills radar command
        skills_radar_parser = subparsers.add_parser(
            "skills-radar", help="Generate skill radar charts"
        )
        self._commands["skills-radar"].add_arguments(skills_radar_parser)

        # Add skills analysis command
        skills_analysis_parser = subparsers.add_parser(
            "skills-analysis", help="Perform comprehensive skills analysis"
        )
        self._commands["skills-analysis"].add_arguments(skills_analysis_parser)

        return parser

    def _init_logging(self):
        """Initialize logging for the CLI."""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)


if __name__ == "__main__":
    sys.exit(main())
