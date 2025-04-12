"""
Nine-Box Matrix CLI commands for talent development.
"""

import datetime
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from peopleanalytics.data_pipeline import DataPipeline
from peopleanalytics.talent_development.matrix_9box import DynamicMatrix9Box


class TalentDevelopmentCommands:
    """
    Class that implements CLI commands for the talent development module.
    """

    def __init__(self, console: Console, data_pipeline: DataPipeline):
        """
        Initialize talent development commands.

        Args:
            console: Rich console for display
            data_pipeline: Data pipeline
        """
        self.console = console
        self.data_pipeline = data_pipeline

    def add_parser(self, subparsers):
        """
        Add parsers for commands related to talent development.

        Args:
            subparsers: Subparsers object from the main parser
        """
        # Nine-box matrix command
        matrix_parser = subparsers.add_parser(
            "nine-box", help="Nine-Box Matrix for performance and potential analysis"
        )
        matrix_subparsers = matrix_parser.add_subparsers(dest="nine_box_command")

        # Visualize subcommand
        visualize_parser = matrix_subparsers.add_parser(
            "visualize", help="Visualize nine-box matrix for a person"
        )
        visualize_parser.add_argument("person_id", type=str, help="Person ID")
        visualize_parser.add_argument(
            "--quarters",
            type=int,
            default=8,
            help="Number of quarters for analysis (default: 8)",
        )
        visualize_parser.add_argument(
            "--output", type=str, help="Path to save visualization"
        )
        visualize_parser.add_argument(
            "--show-future", action="store_true", help="Show future projection"
        )

        # Report subcommand
        report_parser = matrix_subparsers.add_parser(
            "report", help="Generate nine-box matrix report for a person"
        )
        report_parser.add_argument("person_id", type=str, help="Person ID")
        report_parser.add_argument(
            "--quarters",
            type=int,
            default=8,
            help="Number of quarters for analysis (default: 8)",
        )
        report_parser.add_argument(
            "--output", type=str, help="Directory to save report"
        )

        # Add position subcommand
        add_parser = matrix_subparsers.add_parser(
            "add-position", help="Add new nine-box matrix position"
        )
        add_parser.add_argument("person_id", type=str, help="Person ID")
        add_parser.add_argument(
            "--performance", type=float, required=True, help="Performance value (0-10)"
        )
        add_parser.add_argument(
            "--potential", type=float, required=True, help="Potential value (0-10)"
        )
        add_parser.add_argument(
            "--date",
            type=str,
            help="Assessment date (format: YYYY-MM-DD, default: today)",
        )
        add_parser.add_argument(
            "--source", type=str, help='Assessment source (e.g., "Annual Review 2024")'
        )

        # Feedback cycle command
        feedback_parser = subparsers.add_parser(
            "feedback-cycle", help="Integrated feedback cycle for development"
        )
        feedback_subparsers = feedback_parser.add_subparsers(dest="feedback_command")

        # Influence network command
        network_parser = subparsers.add_parser(
            "influence-network", help="Influence and impact network analysis"
        )
        network_subparsers = network_parser.add_subparsers(dest="network_command")

        # Career simulation command
        simulation_parser = subparsers.add_parser(
            "career-sim", help="Career scenario simulation"
        )
        simulation_subparsers = simulation_parser.add_subparsers(
            dest="simulation_command"
        )

    def handle_command(self, args):
        """
        Handle talent development commands.

        Args:
            args: Parsed arguments

        Returns:
            True if command was found and executed, False otherwise
        """
        if hasattr(args, "command") and args.command == "nine-box":
            return self._handle_nine_box(args)
        elif hasattr(args, "command") and args.command == "feedback-cycle":
            return self._handle_feedback_cycle(args)
        elif hasattr(args, "command") and args.command == "influence-network":
            return self._handle_influence_network(args)
        elif hasattr(args, "command") and args.command == "career-sim":
            return self._handle_career_simulation(args)

        return False

    def _handle_nine_box(self, args):
        """
        Handle nine-box matrix commands.

        Args:
            args: Parsed arguments

        Returns:
            True if command was found and executed, False otherwise
        """
        matrix = DynamicMatrix9Box(self.data_pipeline)

        if hasattr(args, "nine_box_command"):
            if args.nine_box_command == "visualize":
                self._handle_nine_box_visualize(args, matrix)
                return True
            elif args.nine_box_command == "report":
                self._handle_nine_box_report(args, matrix)
                return True
            elif args.nine_box_command == "add-position":
                self._handle_nine_box_add_position(args, matrix)
                return True

        self.console.print(
            Panel(
                "[yellow]Incomplete Nine-Box Matrix command.[/yellow] "
                "Use one of these subcommands: visualize, report, add-position"
            )
        )
        return True

    def _handle_nine_box_visualize(self, args, matrix: DynamicMatrix9Box):
        """
        Handle nine-box matrix visualization command.

        Args:
            args: Parsed arguments
            matrix: Nine-box matrix instance
        """
        person_id = args.person_id
        quarters = args.quarters
        output_path = args.output
        show_future = args.show_future

        try:
            visualization = matrix.visualize(
                person_id=person_id, quarters=quarters, show_future=show_future
            )

            if output_path:
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w") as f:
                    f.write(visualization)
                self.console.print(
                    f"Nine-box visualization saved to [bold]{output_path}[/bold]"
                )
            else:
                # Display directly if no output path specified
                md = Markdown(visualization)
                self.console.print(md)

        except Exception as e:
            self.console.print(f"[bold red]Error:[/bold red] {str(e)}")

    def _handle_nine_box_report(self, args, matrix: DynamicMatrix9Box):
        """
        Handle nine-box matrix report command.

        Args:
            args: Parsed arguments
            matrix: Nine-box matrix instance
        """
        person_id = args.person_id
        quarters = args.quarters
        output_dir = args.output

        try:
            report_content = matrix.generate_report(
                person_id=person_id, quarters=quarters
            )

            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)

                filename = f"nine_box_report_{person_id}_{datetime.datetime.now().strftime('%Y%m%d')}.md"
                file_path = output_path / filename

                with open(file_path, "w") as f:
                    f.write(report_content)

                self.console.print(f"Nine-box report saved to [bold]{file_path}[/bold]")
            else:
                # Display directly if no output path specified
                md = Markdown(report_content)
                self.console.print(md)

        except Exception as e:
            self.console.print(f"[bold red]Error:[/bold red] {str(e)}")

    def _handle_nine_box_add_position(self, args, matrix: DynamicMatrix9Box):
        """
        Handle adding a position to the nine-box matrix.

        Args:
            args: Parsed arguments
            matrix: Nine-box matrix instance
        """
        person_id = args.person_id
        performance = args.performance
        potential = args.potential

        # Validate input ranges
        if not (0 <= performance <= 10):
            self.console.print(
                "[bold red]Error:[/bold red] Performance must be between 0 and 10"
            )
            return

        if not (0 <= potential <= 10):
            self.console.print(
                "[bold red]Error:[/bold red] Potential must be between 0 and 10"
            )
            return

        # Process date
        if args.date:
            try:
                date = datetime.datetime.strptime(args.date, "%Y-%m-%d").date()
            except ValueError:
                self.console.print(
                    "[bold red]Error:[/bold red] Date must be in YYYY-MM-DD format"
                )
                return
        else:
            date = datetime.date.today()

        # Process source
        source = (
            args.source
            or f"Manual Entry ({datetime.datetime.now().strftime('%Y-%m-%d')})"
        )

        try:
            matrix.add_position(
                person_id=person_id,
                performance=performance,
                potential=potential,
                date=date,
                source=source,
            )

            # Get quadrant name based on position
            quadrant = matrix.get_quadrant_name(performance, potential)

            # Display success message with formatted table showing the new position
            table = Table(title=f"New Nine-Box Position Added for {person_id}")
            table.add_column("Date", style="cyan")
            table.add_column("Performance", style="green")
            table.add_column("Potential", style="magenta")
            table.add_column("Quadrant", style="yellow")
            table.add_column("Source", style="blue")

            table.add_row(
                date.strftime("%Y-%m-%d"),
                f"{performance:.1f}",
                f"{potential:.1f}",
                quadrant,
                source,
            )

            self.console.print(table)

        except Exception as e:
            self.console.print(f"[bold red]Error:[/bold red] {str(e)}")

    def _handle_feedback_cycle(self, args):
        """
        Handle feedback cycle commands.

        Args:
            args: Parsed arguments

        Returns:
            True if command was handled, False otherwise
        """
        self.console.print(
            Panel(
                "[yellow]Feedback cycle commands coming soon![/yellow] "
                "This feature is under development."
            )
        )
        return True

    def _handle_influence_network(self, args):
        """
        Handle influence network commands.

        Args:
            args: Parsed arguments

        Returns:
            True if command was handled, False otherwise
        """
        self.console.print(
            Panel(
                "[yellow]Influence network commands coming soon![/yellow] "
                "This feature is under development."
            )
        )
        return True

    def _handle_career_simulation(self, args):
        """
        Handle career simulation commands.

        Args:
            args: Parsed arguments

        Returns:
            True if command was handled, False otherwise
        """
        self.console.print(
            Panel(
                "[yellow]Career simulation commands coming soon![/yellow] "
                "This feature is under development."
            )
        )
        return True
