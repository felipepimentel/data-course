"""
People management commands for People Analytics CLI.

This module contains commands for managing people data such as attendance, payments,
profiles, and sample data creation.
"""

import argparse
import logging
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.progress import Progress

from ..data_processor import DataProcessor
from .base_command import BaseCommand


class AddAttendanceCommand(BaseCommand):
    """Command to add attendance records."""

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.processor = None

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument("--person", required=True, help="Person name")
        parser.add_argument("--date", required=True, help="Date (YYYY-MM-DD)")
        parser.add_argument(
            "--status",
            choices=["present", "absent", "late", "leave"],
            required=True,
            help="Attendance status",
        )
        parser.add_argument("--notes", help="Additional notes")

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the add-attendance command."""
        self.console.print(
            f"[bold]Adding attendance record for {args.person}...[/bold]"
        )

        # Setup data processor
        data_path = Path.cwd() / "data"
        self.processor = DataProcessor(data_path)

        try:
            # Parse date
            try:
                date = datetime.strptime(args.date, "%Y-%m-%d").date()
            except ValueError:
                self.console.print("[red]Invalid date format. Use YYYY-MM-DD[/red]")
                return 1

            # Create attendance record
            attendance_data = {
                "person": args.person,
                "date": args.date,
                "status": args.status,
                "notes": args.notes or "",
            }

            # Add attendance record
            success = self.processor.add_attendance_record(attendance_data)

            if success:
                self.console.print(
                    f"[green]Successfully added attendance record for {args.person} on {args.date}[/green]"
                )
                return 0
            else:
                self.console.print("[red]Failed to add attendance record[/red]")
                return 1

        except Exception as e:
            self.console.print(f"[red]Error adding attendance record:[/red] {str(e)}")
            logging.exception("Error in add-attendance command")
            return 1


class AddPaymentCommand(BaseCommand):
    """Command to add payment records."""

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.processor = None

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument("--person", required=True, help="Person name")
        parser.add_argument("--date", required=True, help="Date (YYYY-MM-DD)")
        parser.add_argument(
            "--amount", required=True, type=float, help="Payment amount"
        )
        parser.add_argument(
            "--type",
            choices=["salary", "bonus", "reimbursement", "other"],
            required=True,
            help="Payment type",
        )
        parser.add_argument("--notes", help="Additional notes")

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the add-payment command."""
        self.console.print(f"[bold]Adding payment record for {args.person}...[/bold]")

        # Setup data processor
        data_path = Path.cwd() / "data"
        self.processor = DataProcessor(data_path)

        try:
            # Parse date
            try:
                date = datetime.strptime(args.date, "%Y-%m-%d").date()
            except ValueError:
                self.console.print("[red]Invalid date format. Use YYYY-MM-DD[/red]")
                return 1

            # Create payment record
            payment_data = {
                "person": args.person,
                "date": args.date,
                "amount": args.amount,
                "type": args.type,
                "notes": args.notes or "",
            }

            # Add payment record
            success = self.processor.add_payment_record(payment_data)

            if success:
                self.console.print(
                    f"[green]Successfully added {args.type} payment of {args.amount} for {args.person}[/green]"
                )
                return 0
            else:
                self.console.print("[red]Failed to add payment record[/red]")
                return 1

        except Exception as e:
            self.console.print(f"[red]Error adding payment record:[/red] {str(e)}")
            logging.exception("Error in add-payment command")
            return 1


class UpdateProfileCommand(BaseCommand):
    """Command to update person profiles."""

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.processor = None

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument("--person", required=True, help="Person name")
        parser.add_argument("--department", help="Department name")
        parser.add_argument("--position", help="Job position")
        parser.add_argument("--manager", help="Manager name")
        parser.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
        parser.add_argument("--email", help="Email address")
        parser.add_argument("--phone", help="Phone number")
        parser.add_argument("--notes", help="Additional notes")

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the update-profile command."""
        self.console.print(f"[bold]Updating profile for {args.person}...[/bold]")

        # Setup data processor
        data_path = Path.cwd() / "data"
        self.processor = DataProcessor(data_path)

        try:
            # Create profile update data
            profile_data = {"person": args.person}

            # Add optional fields if provided
            if args.department:
                profile_data["department"] = args.department
            if args.position:
                profile_data["position"] = args.position
            if args.manager:
                profile_data["manager"] = args.manager
            if args.start_date:
                # Validate date format
                try:
                    datetime.strptime(args.start_date, "%Y-%m-%d").date()
                    profile_data["start_date"] = args.start_date
                except ValueError:
                    self.console.print(
                        "[red]Invalid start date format. Use YYYY-MM-DD[/red]"
                    )
                    return 1
            if args.email:
                profile_data["email"] = args.email
            if args.phone:
                profile_data["phone"] = args.phone
            if args.notes:
                profile_data["notes"] = args.notes

            # Check if any updates were provided
            if len(profile_data) <= 1:
                self.console.print("[yellow]No profile updates provided[/yellow]")
                return 0

            # Update profile
            success = self.processor.update_profile(profile_data)

            if success:
                self.console.print(
                    f"[green]Successfully updated profile for {args.person}[/green]"
                )
                return 0
            else:
                self.console.print("[red]Failed to update profile[/red]")
                return 1

        except Exception as e:
            self.console.print(f"[red]Error updating profile:[/red] {str(e)}")
            logging.exception("Error in update-profile command")
            return 1


class CreateSampleCommand(BaseCommand):
    """Command to create sample people data."""

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.processor = None

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "--count", type=int, default=10, help="Number of sample records to create"
        )
        parser.add_argument(
            "--type",
            choices=["people", "attendance", "payments", "evaluations", "all"],
            default="all",
            help="Type of sample data to create",
        )
        parser.add_argument(
            "--year", help="Year for the sample data (default is current year)"
        )
        parser.add_argument("--output", help="Output directory for sample data")

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the create-sample command."""
        sample_type = args.type
        count = args.count

        self.console.print(
            f"[bold]Creating {count} sample {sample_type} records...[/bold]"
        )

        # Setup paths
        data_path = Path.cwd() / "data"
        output_path = Path(args.output) if args.output else data_path
        self.processor = DataProcessor(data_path, output_path)

        try:
            # Determine year
            year = args.year or datetime.now().strftime("%Y")

            # Create sample data based on type
            with Progress() as progress:
                task = progress.add_task("Creating sample data...", total=None)

                if sample_type == "people" or sample_type == "all":
                    self._create_sample_people(count)

                if sample_type == "attendance" or sample_type == "all":
                    self._create_sample_attendance(count, year)

                if sample_type == "payments" or sample_type == "all":
                    self._create_sample_payments(count, year)

                if sample_type == "evaluations" or sample_type == "all":
                    self._create_sample_evaluations(count, year)

                progress.update(task, completed=1)

            self.console.print(
                f"[green]Successfully created sample data at: {output_path}[/green]"
            )
            return 0

        except Exception as e:
            self.console.print(f"[red]Error creating sample data:[/red] {str(e)}")
            logging.exception("Error in create-sample command")
            return 1

    def _create_sample_people(self, count):
        """Create sample people records."""
        self.console.print("[bold]Creating sample people records...[/bold]")

        # Generate sample people
        created = self.processor.create_sample_people(count)

        self.console.print(f"[green]Created {created} sample people records[/green]")

    def _create_sample_attendance(self, count, year):
        """Create sample attendance records."""
        self.console.print("[bold]Creating sample attendance records...[/bold]")

        # Generate sample attendance records
        created = self.processor.create_sample_attendance(count, year)

        self.console.print(
            f"[green]Created {created} sample attendance records[/green]"
        )

    def _create_sample_payments(self, count, year):
        """Create sample payment records."""
        self.console.print("[bold]Creating sample payment records...[/bold]")

        # Generate sample payment records
        created = self.processor.create_sample_payments(count, year)

        self.console.print(f"[green]Created {created} sample payment records[/green]")

    def _create_sample_evaluations(self, count, year):
        """Create sample evaluation records."""
        self.console.print("[bold]Creating sample evaluation records...[/bold]")

        # Generate sample evaluation records
        created = self.processor.create_sample_evaluations(count, year)

        self.console.print(
            f"[green]Created {created} sample evaluation records[/green]"
        )
