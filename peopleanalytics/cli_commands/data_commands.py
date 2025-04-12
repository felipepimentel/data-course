"""
Data management commands for People Analytics CLI.

This module contains commands for data validation, listing, import, export, and backup.
"""

import argparse
import logging
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from ..data_processor import DataProcessor
from .base_command import BaseCommand


class ValidateCommand(BaseCommand):
    """Command to validate data files."""

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.processor = None

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument("path", nargs="?", help="Path to validate")
        parser.add_argument("--fix", action="store_true", help="Try to fix issues")

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the validate command."""
        self.console.print("[bold]Validating data files...[/bold]")

        # Setup data processor
        data_path = Path(args.path) if args.path else Path.cwd() / "data"
        self.processor = DataProcessor(data_path)

        try:
            # Validate data files
            issues = self.processor.validate_all()

            if not issues:
                self.console.print("[green]All data files are valid![/green]")
                return 0

            # Display issues
            issues_table = Table(title="Data Validation Issues")
            issues_table.add_column("File", style="cyan")
            issues_table.add_column("Issues", style="yellow")

            for issue in issues:
                issues_table.add_row(issue["file"], "\n".join(issue["issues"]))

            self.console.print(issues_table)

            # Fix issues if requested
            if args.fix:
                self.console.print("[bold]Fixing issues...[/bold]")
                fixed = self.processor.fix_issues(issues)
                self.console.print(f"[green]Fixed {fixed} issues![/green]")

            return 0 if not issues else 1

        except Exception as e:
            self.console.print(f"[red]Error validating data:[/red] {str(e)}")
            logging.exception("Error in validate command")
            return 1


class ListCommand(BaseCommand):
    """Command to list data files and contents."""

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.processor = None

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "--type",
            choices=["collaborators", "evaluations", "trainings", "all"],
            default="all",
            help="Type of data to list",
        )
        parser.add_argument("--year", help="Filter by year")
        parser.add_argument("--person", help="Filter by person")

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the list command."""
        # Setup data processor
        data_path = Path.cwd() / "data"
        self.processor = DataProcessor(data_path)

        try:
            data_type = args.type.lower()
            self.console.print(f"[bold]Listing {data_type} data...[/bold]")

            # List data based on type
            if data_type == "collaborators" or data_type == "all":
                self._list_collaborators(args)

            if data_type == "evaluations" or data_type == "all":
                self._list_evaluations(args)

            if data_type == "trainings" or data_type == "all":
                self._list_trainings(args)

            return 0

        except Exception as e:
            self.console.print(f"[red]Error listing data:[/red] {str(e)}")
            logging.exception("Error in list command")
            return 1

    def _list_collaborators(self, args):
        """List collaborator data."""
        collaborators = self.processor.get_all_collaborators()

        if not collaborators:
            self.console.print("[yellow]No collaborators found[/yellow]")
            return

        # Filter by year if specified
        if args.year:
            collaborators = [c for c in collaborators if args.year in c["years"]]

        # Filter by person if specified
        if args.person:
            collaborators = [
                c for c in collaborators if args.person.lower() in c["name"].lower()
            ]

        # Display collaborators
        table = Table(title="Collaborators")
        table.add_column("Name", style="cyan")
        table.add_column("Years", style="green")
        table.add_column("Department", style="yellow")

        for collab in collaborators:
            table.add_row(
                collab["name"],
                ", ".join(collab["years"]),
                collab.get("department", "N/A"),
            )

        self.console.print(table)

    def _list_evaluations(self, args):
        """List evaluation data."""
        evaluations = self.processor.get_all_evaluations()

        if not evaluations:
            self.console.print("[yellow]No evaluations found[/yellow]")
            return

        # Filter by year if specified
        if args.year:
            evaluations = [e for e in evaluations if args.year == e["year"]]

        # Filter by person if specified
        if args.person:
            evaluations = [
                e for e in evaluations if args.person.lower() in e["person"].lower()
            ]

        # Display evaluations
        table = Table(title="Evaluations")
        table.add_column("Person", style="cyan")
        table.add_column("Year", style="green")
        table.add_column("Score", style="yellow")
        table.add_column("Status", style="magenta")

        for eval in evaluations:
            table.add_row(
                eval["person"],
                eval["year"],
                str(eval.get("score", "N/A")),
                eval.get("status", "N/A"),
            )

        self.console.print(table)

    def _list_trainings(self, args):
        """List training data."""
        trainings = self.processor.get_all_trainings()

        if not trainings:
            self.console.print("[yellow]No trainings found[/yellow]")
            return

        # Filter by year if specified
        if args.year:
            trainings = [t for t in trainings if args.year == t["year"]]

        # Filter by person if specified
        if args.person:
            trainings = [
                t for t in trainings if args.person.lower() in t["person"].lower()
            ]

        # Display trainings
        table = Table(title="Trainings")
        table.add_column("Person", style="cyan")
        table.add_column("Year", style="green")
        table.add_column("Training", style="yellow")
        table.add_column("Status", style="magenta")

        for training in trainings:
            table.add_row(
                training["person"],
                training["year"],
                training["name"],
                training.get("status", "N/A"),
            )

        self.console.print(table)


class ImportCommand(BaseCommand):
    """Command to import data."""

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.processor = None

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument("--source", required=True, help="Source of data")
        parser.add_argument(
            "--format",
            choices=["csv", "json", "excel"],
            default="csv",
            help="Format of data",
        )
        parser.add_argument(
            "--type",
            choices=["collaborators", "evaluations", "trainings"],
            required=True,
            help="Type of data",
        )
        parser.add_argument(
            "--recursive",
            action="store_true",
            help="Recursively import from directories",
        )

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the import command."""
        self.console.print(
            f"[bold]Importing {args.type} data from {args.source}...[/bold]"
        )

        # Setup data processor
        data_path = Path.cwd() / "data"
        self.processor = DataProcessor(data_path)

        try:
            source_path = Path(args.source)

            # Check if source exists
            if not source_path.exists():
                self.console.print(f"[red]Source {args.source} does not exist[/red]")
                return 1

            # Import based on whether source is file or directory
            if source_path.is_file():
                # Import single file
                with Progress() as progress:
                    task = progress.add_task(
                        f"Importing {source_path.name}...", total=1
                    )

                    result = self.processor.import_file(
                        source_path, data_type=args.type, format=args.format
                    )

                    if result["success"]:
                        self.console.print(
                            f"[green]Successfully imported {source_path.name}[/green]"
                        )
                    else:
                        self.console.print(
                            f"[red]Error importing {source_path.name}: {result['error']}[/red]"
                        )

                    progress.update(task, completed=1)

            else:
                # Import directory
                with Progress() as progress:
                    task = progress.add_task("Importing files...", total=None)

                    results = self.processor.import_directory(
                        source_path,
                        recursive=args.recursive,
                        data_type=args.type,
                        format=args.format,
                    )

                    progress.update(task, completed=1)

                    # Display results
                    success_count = sum(1 for r in results if r["success"])
                    self.console.print(
                        f"[green]Successfully imported {success_count} of {len(results)} files[/green]"
                    )

                    # Show errors if any
                    errors = [r for r in results if not r["success"]]
                    if errors:
                        error_table = Table(title="Import Errors")
                        error_table.add_column("File", style="cyan")
                        error_table.add_column("Error", style="red")

                        for error in errors:
                            error_table.add_row(error["file"], error["error"])

                        self.console.print(error_table)

            return 0

        except Exception as e:
            self.console.print(f"[red]Error importing data:[/red] {str(e)}")
            logging.exception("Error in import command")
            return 1


class ExportCommand(BaseCommand):
    """Command to export data."""

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.processor = None

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "--format",
            choices=["csv", "json", "excel"],
            default="csv",
            help="Format for export",
        )
        parser.add_argument("--output", required=True, help="Output path")
        parser.add_argument(
            "--type",
            choices=["collaborators", "evaluations", "trainings"],
            required=True,
            help="Type of data",
        )
        parser.add_argument("--person", help="Filter by person")
        parser.add_argument("--year", help="Filter by year")
        parser.add_argument("--all", action="store_true", help="Export all data")

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the export command."""
        # Setup data processor
        data_path = Path.cwd() / "data"
        output_path = Path(args.output)
        self.processor = DataProcessor(data_path, output_path)

        try:
            # Create output directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if args.all:
                # Export all data
                self.console.print(
                    f"[bold]Exporting all {args.type} data to {args.output}...[/bold]"
                )

                with Progress() as progress:
                    task = progress.add_task("Exporting data...", total=None)

                    results = self.processor.export_all(
                        args.type, format=args.format, output_path=output_path
                    )

                    progress.update(task, completed=1)

                    # Display results
                    success_count = sum(1 for r in results if r["success"])
                    self.console.print(
                        f"[green]Successfully exported {success_count} of {len(results)} files[/green]"
                    )

                    # Show errors if any
                    errors = [r for r in results if not r["success"]]
                    if errors:
                        error_table = Table(title="Export Errors")
                        error_table.add_column("Item", style="cyan")
                        error_table.add_column("Error", style="red")

                        for error in errors:
                            error_table.add_row(
                                f"{error.get('person', '')} ({error.get('year', '')})",
                                error["error"],
                            )

                        self.console.print(error_table)

            elif args.person and args.year:
                # Export specific person/year
                self.console.print(
                    f"[bold]Exporting data for {args.person} ({args.year}) to {args.output}...[/bold]"
                )

                success, message = self.processor.export_person_data(
                    args.person,
                    args.year,
                    data_type=args.type,
                    format=args.format,
                    output_path=output_path,
                )

                if success:
                    self.console.print(
                        f"[green]Successfully exported data to {args.output}[/green]"
                    )
                else:
                    self.console.print(f"[red]Error exporting data: {message}[/red]")
                    return 1
            else:
                self.console.print(
                    "[red]Either --all or both --person and --year must be specified[/red]"
                )
                return 1

            return 0

        except Exception as e:
            self.console.print(f"[red]Error exporting data:[/red] {str(e)}")
            logging.exception("Error in export command")
            return 1


class BackupCommand(BaseCommand):
    """Command to create data backups."""

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.processor = None

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument("--output", help="Output path for backup")

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the backup command."""
        self.console.print("[bold]Creating backup...[/bold]")

        # Setup paths
        data_path = Path.cwd() / "data"
        self.processor = DataProcessor(data_path)

        try:
            # Determine backup path
            if args.output:
                backup_path = Path(args.output)
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = Path.cwd() / "backups" / f"backup_{timestamp}.zip"

            # Create parent directory if it doesn't exist
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            # Create backup
            with Progress() as progress:
                task = progress.add_task("Creating backup...", total=1)

                self.processor.create_backup(backup_path)

                progress.update(task, completed=1)

            self.console.print(f"[green]Backup created at: {backup_path}[/green]")
            return 0

        except Exception as e:
            self.console.print(f"[red]Error creating backup:[/red] {str(e)}")
            logging.exception("Error in backup command")
            return 1
