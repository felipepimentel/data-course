"""
Reporting commands for People Analytics CLI.

This module contains commands for generating reports, summaries, notebooks, and plots.
"""

import argparse
import importlib.util
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.progress import Progress

from ..data_processor import DataProcessor
from .base_command import BaseCommand


class SummaryCommand(BaseCommand):
    """Command to generate data summaries."""

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.processor = None

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "--format",
            choices=["html", "markdown", "text"],
            default="html",
            help="Output format",
        )
        parser.add_argument("--output", help="Output path")

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the summary command."""
        output_format = args.format

        self.console.print(f"[bold]Generating {output_format} summary...[/bold]")

        # Setup data processor
        data_path = Path.cwd() / "data"
        self.processor = DataProcessor(data_path)

        try:
            # Determine output path
            if args.output:
                output_path = Path(args.output)
            else:
                timestamp = datetime.now().strftime("%Y%m%d")
                output_path = (
                    Path.cwd() / "output" / f"summary_{timestamp}.{output_format}"
                )

            # Create parent directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Generate summary
            with Progress() as progress:
                task = progress.add_task("Generating summary...", total=1)

                self.processor.generate_summary(
                    output_format=output_format, output_path=output_path
                )

                progress.update(task, completed=1)

            self.console.print(f"[green]Summary generated at: {output_path}[/green]")
            return 0

        except Exception as e:
            self.console.print(f"[red]Error generating summary:[/red] {str(e)}")
            logging.exception("Error in summary command")
            return 1


class ReportCommand(BaseCommand):
    """Command to generate reports."""

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.processor = None

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "--type",
            choices=["attendance", "payment", "performance", "all"],
            default="all",
            help="Report type",
        )
        parser.add_argument(
            "--format",
            choices=["html", "pdf", "markdown"],
            default="html",
            help="Output format",
        )
        parser.add_argument("--output", help="Output path")
        parser.add_argument("--year", help="Year for the report")

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the report command."""
        report_type = args.type
        year = args.year

        self.console.print(
            f"[bold]Generating {report_type} report for {year if year else 'all years'}...[/bold]"
        )

        # Setup data processor
        data_path = Path.cwd() / "data"
        output_path = Path.cwd() / "output" if not args.output else Path(args.output)
        self.processor = DataProcessor(data_path, output_path)

        try:
            # Create output directory if it doesn't exist
            output_path.mkdir(parents=True, exist_ok=True)

            # Generate reports based on type
            if report_type == "attendance" or report_type == "all":
                self._generate_attendance_report(args)

            if report_type == "payment" or report_type == "all":
                self._generate_payment_report(args)

            if report_type == "performance" or report_type == "all":
                self._generate_performance_report(args)

            return 0

        except Exception as e:
            self.console.print(f"[red]Error generating report:[/red] {str(e)}")
            logging.exception("Error in report command")
            return 1

    def _generate_attendance_report(self, args):
        """Generate attendance report."""
        self.console.print("[bold]Generating attendance report...[/bold]")

        # Generate report
        output_file = self.processor.generate_attendance_report(
            year=args.year, format=args.format
        )

        self.console.print(
            f"[green]Attendance report generated at: {output_file}[/green]"
        )

    def _generate_payment_report(self, args):
        """Generate payment report."""
        self.console.print("[bold]Generating payment report...[/bold]")

        # Generate report
        output_file = self.processor.generate_payment_report(
            year=args.year, format=args.format
        )

        self.console.print(f"[green]Payment report generated at: {output_file}[/green]")

    def _generate_performance_report(self, args):
        """Generate performance report."""
        self.console.print("[bold]Generating performance report...[/bold]")

        # Generate report
        output_file = self.processor.generate_performance_report(
            year=args.year, format=args.format
        )

        self.console.print(
            f"[green]Performance report generated at: {output_file}[/green]"
        )


class NotebookCommand(BaseCommand):
    """Command to generate interactive notebooks."""

    def __init__(self):
        super().__init__()
        self.console = Console()

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument("--output", help="Output path for notebook")
        parser.add_argument(
            "--type",
            choices=["people", "teams", "org"],
            default="people",
            help="Type of analysis",
        )

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the notebook command."""
        self.console.print(
            "[bold]Generating notebook for interactive analysis...[/bold]"
        )

        try:
            # Determine output path
            if args.output:
                output_path = args.output
            else:
                # Create filename based on type
                filename = f"analyze_{args.type}_data.ipynb"
                output_path = os.path.join("notebooks", filename)

                # Create notebooks directory if it doesn't exist
                os.makedirs("notebooks", exist_ok=True)

            # Import the notebook generator from assets folder
            script_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "assets",
                "create_notebook.py",
            )

            if not os.path.exists(script_path):
                self.console.print(
                    f"[red]Error: Notebook generator script not found at {script_path}[/red]"
                )
                return 1

            # Import the module dynamically
            spec = importlib.util.spec_from_file_location(
                "notebook_generator", script_path
            )
            notebook_module = importlib.util.module_from_spec(spec)
            sys.modules["notebook_generator"] = notebook_module
            spec.loader.exec_module(notebook_module)

            # Generate the notebook
            notebook_path = notebook_module.create_people_analytics_notebook(
                output_path
            )

            self.console.print(f"[green]Notebook generated at: {notebook_path}[/green]")
            self.console.print("\n[bold]To open the notebook, run:[/bold]")
            self.console.print(f"jupyter notebook {notebook_path}")

            return 0

        except Exception as e:
            self.console.print(f"[red]Error generating notebook:[/red] {str(e)}")
            logging.exception("Error in notebook command")
            return 1


class PlotCommand(BaseCommand):
    """Command to generate plots and visualizations."""

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.processor = None

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "--type",
            choices=["attendance", "payment", "performance", "all"],
            default="all",
            help="Plot type",
        )
        parser.add_argument("--output", help="Output directory")
        parser.add_argument("--year", help="Year for the plot")
        parser.add_argument(
            "--format",
            choices=["png", "svg", "pdf"],
            default="png",
            help="Output format",
        )

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the plot command."""
        plot_type = args.type
        year = args.year

        self.console.print(
            f"[bold]Generating {plot_type} plots for {year if year else 'all years'}...[/bold]"
        )

        # Setup data processor
        data_path = Path.cwd() / "data"
        output_path = (
            Path.cwd() / "output" / "plots" if not args.output else Path(args.output)
        )
        self.processor = DataProcessor(data_path, output_path)

        try:
            # Create output directory if it doesn't exist
            output_path.mkdir(parents=True, exist_ok=True)

            # Generate plots based on type
            if plot_type == "attendance" or plot_type == "all":
                self._generate_attendance_plot(args)

            if plot_type == "payment" or plot_type == "all":
                self._generate_payment_plot(args)

            if plot_type == "performance" or plot_type == "all":
                self._generate_performance_plot(args)

            return 0

        except Exception as e:
            self.console.print(f"[red]Error generating plots:[/red] {str(e)}")
            logging.exception("Error in plot command")
            return 1

    def _generate_attendance_plot(self, args):
        """Generate attendance plot."""
        self.console.print("[bold]Generating attendance plot...[/bold]")

        # Generate plot
        output_file = self.processor.generate_attendance_plot(
            year=args.year, format=args.format
        )

        self.console.print(
            f"[green]Attendance plot generated at: {output_file}[/green]"
        )

    def _generate_payment_plot(self, args):
        """Generate payment plot."""
        self.console.print("[bold]Generating payment plot...[/bold]")

        # Generate plot
        output_file = self.processor.generate_payment_plot(
            year=args.year, format=args.format
        )

        self.console.print(f"[green]Payment plot generated at: {output_file}[/green]")

    def _generate_performance_plot(self, args):
        """Generate performance plot."""
        self.console.print("[bold]Generating performance plot...[/bold]")

        # Generate plot
        output_file = self.processor.generate_performance_plot(
            year=args.year, format=args.format
        )

        self.console.print(
            f"[green]Performance plot generated at: {output_file}[/green]"
        )
