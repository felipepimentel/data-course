"""
Command Line Interface for People Analytics.

This module provides the main CLI for the People Analytics system.
"""

import argparse
import sys
import json
from pathlib import Path
import os
from datetime import datetime
from typing import List
import shutil

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress

from .data_processor import DataProcessor
from .data_model import PersonData, AttendanceRecord, PaymentRecord, ProfileData
from .reports_generator import generate_attendance_report, generate_payment_report


class CLI:
    """Command Line Interface for People Analytics."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.console = Console()
        self.args = None
        self.processor = None
        
    def setup(self, data_path, output_path=None):
        """Set up the data processor."""
        # Convert relative paths to absolute paths
        data_path = Path(data_path).resolve()
        output_path = Path(output_path).resolve() if output_path else None
        self.processor = DataProcessor(data_path, output_path)
        
    def run(self):
        """Run the CLI application."""
        parser = self._create_parser()
        self.args = parser.parse_args()
        
        # Setup data processor with paths from args
        self.setup(self.args.data_path, self.args.output_path)
        
        # Handle the command
        if self.args.command == "validate":
            self.handle_validate()
        elif self.args.command == "list":
            self.handle_list()
        elif self.args.command == "import":
            self.handle_import()
        elif self.args.command == "export":
            self.handle_export()
        elif self.args.command == "summary":
            self.handle_summary()
        elif self.args.command == "report":
            self.handle_report()
        elif self.args.command == "backup":
            self.handle_backup()
        elif self.args.command == "plot":
            self.handle_plot()
        elif self.args.command == "add-attendance":
            self.handle_add_attendance()
        elif self.args.command == "add-payment":
            self.handle_add_payment()
        elif self.args.command == "update-profile":
            self.handle_update_profile()
        elif self.args.command == "create-sample":
            self.handle_create_sample()
        elif self.args.command == "sync":
            self.handle_sync()
        else:
            self.console.print("[red]Unknown command[/red]")
            
    def _create_parser(self):
        """Create the command line parser."""
        parser = argparse.ArgumentParser(
            description="People Analytics Data Processor",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        
        # Create subparsers for commands
        subparsers = parser.add_subparsers(dest="command", help="Command to execute")
        
        # Common arguments for commands that use data and output paths
        common_path_args = {
            "--data-path": {
                "default": ".",
                "help": "Path to the data directory"
            },
            "--output-path": {
                "default": "./output",
                "help": "Path to the output directory"
            }
        }
        
        # validate command
        validate_parser = subparsers.add_parser("validate", help="Validate all data")
        validate_parser.add_argument("--data-path", **common_path_args["--data-path"])
        validate_parser.add_argument("--output-path", **common_path_args["--output-path"])
        
        # list command
        list_parser = subparsers.add_parser("list", help="List people or years")
        list_parser.add_argument("--data-path", **common_path_args["--data-path"])
        list_parser.add_argument("--output-path", **common_path_args["--output-path"])
        list_parser.add_argument(
            "what", 
            choices=["people", "years", "data"],
            help="What to list"
        )
        list_parser.add_argument(
            "--person", 
            help="Person name for filtering years"
        )
        list_parser.add_argument(
            "--year", 
            help="Year for filtering people"
        )
        
        # import command
        import_parser = subparsers.add_parser("import", help="Import data")
        import_parser.add_argument("--data-path", **common_path_args["--data-path"])
        import_parser.add_argument("--output-path", **common_path_args["--output-path"])
        import_parser.add_argument(
            "source",
            help="Source file or directory to import"
        )
        import_parser.add_argument(
            "--recursive", 
            action="store_true",
            help="Recursively import directories"
        )
        
        # export command
        export_parser = subparsers.add_parser("export", help="Export data")
        export_parser.add_argument("--data-path", **common_path_args["--data-path"])
        export_parser.add_argument("--output-path", **common_path_args["--output-path"])
        export_parser.add_argument(
            "--person", 
            help="Person name for export"
        )
        export_parser.add_argument(
            "--year", 
            help="Year for export"
        )
        export_parser.add_argument(
            "--all", 
            action="store_true",
            help="Export all data"
        )
        
        # summary command
        summary_parser = subparsers.add_parser("summary", help="Generate summary")
        summary_parser.add_argument("--data-path", **common_path_args["--data-path"])
        summary_parser.add_argument("--output-path", **common_path_args["--output-path"])
        summary_parser.add_argument(
            "--format", 
            choices=["json", "csv", "html"],
            default="json",
            help="Output format"
        )
        
        # report command
        report_parser = subparsers.add_parser("report", help="Generate reports")
        report_parser.add_argument("--data-path", **common_path_args["--data-path"])
        report_parser.add_argument("--output-path", **common_path_args["--output-path"])
        report_parser.add_argument(
            "type",
            choices=["attendance", "payment", "all"],
            help="Type of report to generate"
        )
        report_parser.add_argument(
            "--year", 
            help="Year for filtering reports"
        )
        
        # backup command
        backup_parser = subparsers.add_parser("backup", help="Create a backup")
        backup_parser.add_argument("--data-path", **common_path_args["--data-path"])
        backup_parser.add_argument("--output-path", **common_path_args["--output-path"])
        
        # plot command
        plot_parser = subparsers.add_parser("plot", help="Generate plots")
        plot_parser.add_argument("--data-path", **common_path_args["--data-path"])
        plot_parser.add_argument("--output-path", **common_path_args["--output-path"])
        plot_parser.add_argument(
            "type",
            choices=["attendance", "payment", "all"],
            help="Type of plot to generate"
        )
        plot_parser.add_argument(
            "--year", 
            help="Year for filtering plots"
        )
        
        # Add attendance record
        attendance_parser = subparsers.add_parser('add-attendance', help='Add attendance record')
        attendance_parser.add_argument("--data-path", **common_path_args["--data-path"])
        attendance_parser.add_argument("--output-path", **common_path_args["--output-path"])
        attendance_parser.add_argument('--person', required=True, help='Person name')
        attendance_parser.add_argument('--year', required=True, help='Year')
        attendance_parser.add_argument('--date', required=True, help='Date (YYYY-MM-DD)')
        attendance_parser.add_argument('--status', required=True, choices=['present', 'absent', 'late'], help='Status')
        attendance_parser.add_argument('--hours', type=float, default=8.0, help='Hours worked')
        attendance_parser.add_argument('--notes', default='', help='Notes')
        
        # Add payment record
        payment_parser = subparsers.add_parser('add-payment', help='Add payment record')
        payment_parser.add_argument("--data-path", **common_path_args["--data-path"])
        payment_parser.add_argument("--output-path", **common_path_args["--output-path"])
        payment_parser.add_argument('--person', required=True, help='Person name')
        payment_parser.add_argument('--year', required=True, help='Year')
        payment_parser.add_argument('--date', required=True, help='Date (YYYY-MM-DD)')
        payment_parser.add_argument('--amount', type=float, required=True, help='Amount')
        payment_parser.add_argument('--type', required=True, choices=['salary', 'bonus', 'commission'], help='Payment type')
        payment_parser.add_argument('--notes', default='', help='Notes')
        
        # Update profile
        profile_parser = subparsers.add_parser('update-profile', help='Update person profile')
        profile_parser.add_argument("--data-path", **common_path_args["--data-path"])
        profile_parser.add_argument("--output-path", **common_path_args["--output-path"])
        profile_parser.add_argument('--person', required=True, help='Person name')
        profile_parser.add_argument('--year', required=True, help='Year')
        profile_parser.add_argument('--full-name', help='Full name')
        profile_parser.add_argument('--position', help='Position')
        profile_parser.add_argument('--department', help='Department')
        profile_parser.add_argument('--manager', help='Manager')
        profile_parser.add_argument('--is-manager', action='store_true', help='Is a manager')
        
        # Create sample data
        sample_parser = subparsers.add_parser('create-sample', help='Create sample data')
        sample_parser.add_argument("--data-path", **common_path_args["--data-path"])
        sample_parser.add_argument("--output-path", **common_path_args["--output-path"])
        
        # Sync command
        sync_parser = subparsers.add_parser('sync', help='Sync and generate all reports')
        sync_parser.add_argument("--data-path", **common_path_args["--data-path"])
        sync_parser.add_argument("--output-path", **common_path_args["--output-path"])
        sync_parser.add_argument(
            "--recursive", 
            action="store_true",
            help="Process directories recursively"
        )
        
        return parser
        
    def handle_validate(self):
        """Handle the validate command."""
        self.console.print("[bold]Validating all data...[/bold]")
        
        with Progress() as progress:
            task = progress.add_task("[green]Validating...", total=None)
            results = self.processor.validate_all_data()
            progress.update(task, completed=1)
        
        # Display results
        table = Table(title="Validation Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Files", str(results["total"]))
        table.add_row("Valid", str(results["valid"]))
        table.add_row("Invalid", str(results["invalid"]))
        
        self.console.print(table)
        
        # Display issues if any
        if results["issues"]:
            issues_table = Table(title="Validation Issues")
            issues_table.add_column("Person", style="cyan")
            issues_table.add_column("Year", style="green")
            issues_table.add_column("Status", style="yellow")
            issues_table.add_column("Message", style="red")
            
            for issue in results["issues"]:
                issues_table.add_row(
                    issue["person"],
                    issue["year"],
                    issue["status"],
                    issue["message"]
                )
                
            self.console.print(issues_table)
            
    def handle_list(self):
        """Handle the list command."""
        what = self.args.what
        
        if what == "people":
            if self.args.year:
                # List people for a specific year
                people = self.processor.get_people_for_year(self.args.year)
                title = f"People for Year {self.args.year}"
            else:
                # List all people
                people = self.processor.get_all_people()
                title = "All People"
                
            table = Table(title=title)
            table.add_column("Name", style="cyan")
            
            for person in people:
                table.add_row(person)
                
            self.console.print(table)
            
        elif what == "years":
            if self.args.person:
                # List years for a specific person
                years = self.processor.get_all_years_for_person(self.args.person)
                title = f"Years for {self.args.person}"
            else:
                # List all years
                years = sorted(list(self.processor.get_all_years()))
                title = "All Years"
                
            table = Table(title=title)
            table.add_column("Year", style="green")
            
            for year in years:
                table.add_row(year)
                
            self.console.print(table)
            
        elif what == "data":
            # List data details
            if not self.args.person or not self.args.year:
                self.console.print("[red]Both --person and --year are required for listing data[/red]")
                return
                
            data = self.processor.load_person_data(self.args.person, self.args.year)
            
            if not data:
                self.console.print(f"[red]No data found for {self.args.person} ({self.args.year})[/red]")
                return
                
            # Display summary
            attendance_summary = data.get_attendance_summary()
            payment_summary = data.get_payment_summary()
            profile_summary = data.get_profile_summary()
            
            # Create tables
            info_table = Table(title=f"Data for {self.args.person} ({self.args.year})")
            info_table.add_column("Field", style="cyan")
            info_table.add_column("Value", style="green")
            
            info_table.add_row("Name", data.name)
            info_table.add_row("Year", str(data.year))
            info_table.add_row("Attendance Records", str(len(data.attendance_records)))
            info_table.add_row("Payment Records", str(len(data.payment_records)))
            info_table.add_row("Profile Information", "Available" if data.profile else "Not Available")
            
            self.console.print(info_table)
            
            # Profile summary if available
            if profile_summary["available"]:
                profile_table = Table(title="Profile Information")
                profile_table.add_column("Field", style="cyan")
                profile_table.add_column("Value", style="green")
                
                profile_table.add_row("Full Name", profile_summary["full_name"])
                profile_table.add_row("Position", profile_summary["position"])
                profile_table.add_row("Department", profile_summary["department"])
                profile_table.add_row("Manager", profile_summary["manager"])
                profile_table.add_row("Is Manager", "Yes" if profile_summary["is_manager"] else "No")
                
                self.console.print(profile_table)
            
            # Attendance summary
            attendance_table = Table(title="Attendance Summary")
            attendance_table.add_column("Metric", style="cyan")
            attendance_table.add_column("Value", style="green")
            
            attendance_table.add_row("Total Days", str(attendance_summary["total"]))
            attendance_table.add_row("Days Present", str(attendance_summary["present"]))
            attendance_table.add_row("Days Absent", str(attendance_summary["absent"]))
            attendance_table.add_row("Attendance Rate", f"{attendance_summary['attendance_rate']:.2f}%")
            
            self.console.print(attendance_table)
            
            # Payment summary
            payment_table = Table(title="Payment Summary")
            payment_table.add_column("Metric", style="cyan")
            payment_table.add_column("Value", style="green")
            
            payment_table.add_row("Total Payments", str(payment_summary["total_payments"]))
            payment_table.add_row("Total Amount", f"{payment_summary['total_amount']:.2f}")
            payment_table.add_row("Average Payment", f"{payment_summary['average_payment']:.2f}")
            
            self.console.print(payment_table)
            
    def handle_import(self):
        """Handle the import command."""
        source = self.args.source
        source_path = Path(source)
        
        if not source_path.exists():
            self.console.print(f"[red]Source not found: {source}[/red]")
            return
            
        with Progress() as progress:
            task = progress.add_task("[green]Importing...", total=None)
            
            if source_path.is_file():
                # Import a single file
                success, message = self.processor.import_json_file(source_path, overwrite=True)
                
                if success:
                    self.console.print(f"[green]{message}[/green]")
                else:
                    self.console.print(f"[red]{message}[/red]")
            else:
                # Import a directory
                results = self.processor.import_directory(
                    source_path, 
                    recursive=self.args.recursive
                )
                
                if results["success"]:
                    self.console.print(f"[green]Imported {results['imported']} files[/green]")
                    
                    if results["failed"] > 0:
                        self.console.print(f"[yellow]Failed to import {results['failed']} files[/yellow]")
                        
                        for error in results["errors"]:
                            self.console.print(f"[red]Error importing {error['file']}: {error['error']}[/red]")
                else:
                    self.console.print(f"[red]{results['error']}[/red]")
                    
            progress.update(task, completed=1)
            
    def handle_export(self):
        """Handle the export command."""
        if self.args.all:
            # Export all data
            self.console.print("[bold]Exporting all data...[/bold]")
            
            with Progress() as progress:
                task = progress.add_task("[green]Exporting...", total=None)
                results = self.processor.export_all_data()
                progress.update(task, completed=1)
                
            self.console.print(f"[green]Exported {results['exported']} files[/green]")
            
            if results["failed"] > 0:
                self.console.print(f"[yellow]Failed to export {results['failed']} files[/yellow]")
                
                for error in results["errors"]:
                    self.console.print(f"[red]Error exporting {error['person']} ({error['year']}): {error['error']}[/red]")
        
        elif self.args.person and self.args.year:
            # Export specific person/year
            self.console.print(f"[bold]Exporting data for {self.args.person} ({self.args.year})...[/bold]")
            
            success, message = self.processor.export_person_data(self.args.person, self.args.year)
            
            if success:
                self.console.print(f"[green]{message}[/green]")
            else:
                self.console.print(f"[red]{message}[/red]")
        
        else:
            self.console.print("[red]Either --all or both --person and --year must be specified[/red]")
            
    def handle_summary(self):
        """Handle the summary command."""
        output_format = self.args.format
        
        self.console.print(f"[bold]Generating {output_format} summary...[/bold]")
        
        with Progress() as progress:
            task = progress.add_task("[green]Generating...", total=None)
            output_file = self.processor.generate_summary(output_format)
            progress.update(task, completed=1)
            
        self.console.print(f"[green]Summary generated at: {output_file}[/green]")
        
    def handle_report(self):
        """Handle the report command."""
        report_type = self.args.type
        year = self.args.year
        
        if report_type == "attendance" or report_type == "all":
            self.console.print(f"[bold]Generating attendance report{' for ' + year if year else ''}...[/bold]")
            
            with Progress() as progress:
                task = progress.add_task("[green]Generating...", total=None)
                output_file = self.processor.generate_attendance_report(year)
                progress.update(task, completed=1)
                
            self.console.print(f"[green]Attendance report generated at: {output_file}[/green]")
            
        if report_type == "payment" or report_type == "all":
            self.console.print(f"[bold]Generating payment report{' for ' + year if year else ''}...[/bold]")
            
            with Progress() as progress:
                task = progress.add_task("[green]Generating...", total=None)
                output_file = self.processor.generate_payment_report(year)
                progress.update(task, completed=1)
                
            self.console.print(f"[green]Payment report generated at: {output_file}[/green]")
            
    def handle_backup(self):
        """Handle the backup command."""
        self.console.print("[bold]Creating backup...[/bold]")
        
        with Progress() as progress:
            task = progress.add_task("[green]Backing up...", total=None)
            backup_file = self.processor.create_backup()
            progress.update(task, completed=1)
            
        self.console.print(f"[green]Backup created at: {backup_file}[/green]")
        
    def handle_plot(self):
        """Handle the plot command."""
        plot_type = self.args.type
        year = self.args.year
        
        if plot_type == "attendance" or plot_type == "all":
            self.console.print(f"[bold]Generating attendance plot{' for ' + year if year else ''}...[/bold]")
            
            with Progress() as progress:
                task = progress.add_task("[green]Generating...", total=None)
                output_file = self.processor.plot_attendance_summary(year)
                progress.update(task, completed=1)
                
            self.console.print(f"[green]Attendance plot generated at: {output_file}[/green]")
            
        if plot_type == "payment" or plot_type == "all":
            self.console.print(f"[bold]Generating payment plot{' for ' + year if year else ''}...[/bold]")
            
            with Progress() as progress:
                task = progress.add_task("[green]Generating...", total=None)
                output_file = self.processor.plot_payment_summary(year)
                progress.update(task, completed=1)
                
            self.console.print(f"[green]Payment plot generated at: {output_file}[/green]")

    def handle_add_attendance(self):
        """Handle the add-attendance command."""
        person_data = self.processor.load_person_data(self.args.person, self.args.year)
        
        if not person_data:
            self.console.print(f"[red]No data found for {self.args.person} ({self.args.year}). Creating new record.[/red]")
            person_data = self.processor.create_person_data(self.args.person, int(self.args.year))
        
        # Convert date string to date object
        try:
            record_date = datetime.strptime(self.args.date, "%Y-%m-%d").date()
        except ValueError:
            self.console.print("[red]Invalid date format. Use YYYY-MM-DD.[/red]")
            return
            
        # Map status to present value
        present = self.args.status == "present"
        
        # Check if the record already exists
        for record in person_data.attendance_records:
            if record.date == record_date:
                self.console.print(f"[yellow]Attendance record for {self.args.date} already exists. Updating...[/yellow]")
                record.present = present
                record.notes = self.args.notes
                self.processor.save_person_data(person_data)
                self.console.print("[green]Attendance record updated successfully[/green]")
                return
        
        # Add new record
        person_data.add_attendance(self.args.date, present, self.args.notes)
        self.processor.save_person_data(person_data)
        self.console.print("[green]Attendance record added successfully[/green]")

    def handle_add_payment(self):
        """Handle the add-payment command."""
        person_data = self.processor.load_person_data(self.args.person, self.args.year)
        
        if not person_data:
            self.console.print(f"[red]No data found for {self.args.person} ({self.args.year}). Creating new record.[/red]")
            person_data = self.processor.create_person_data(self.args.person, int(self.args.year))
        
        # Convert date string to date object
        try:
            record_date = datetime.strptime(self.args.date, "%Y-%m-%d").date()
        except ValueError:
            self.console.print("[red]Invalid date format. Use YYYY-MM-DD.[/red]")
            return
        
        # Check if the record already exists
        for record in person_data.payment_records:
            if record.date == record_date:
                self.console.print(f"[yellow]Payment record for {self.args.date} already exists. Updating...[/yellow]")
                record.amount = self.args.amount
                record.reference = self.args.notes
                self.processor.save_person_data(person_data)
                self.console.print("[green]Payment record updated successfully[/green]")
                return
        
        # Add new record
        person_data.add_payment(self.args.date, self.args.amount, self.args.type, self.args.notes)
        self.processor.save_person_data(person_data)
        self.console.print("[green]Payment record added successfully[/green]")

    def handle_update_profile(self):
        """Handle the update-profile command."""
        person_data = self.processor.load_person_data(self.args.person, self.args.year)
        
        if not person_data:
            self.console.print(f"[red]No data found for {self.args.person} ({self.args.year}). Creating new record.[/red]")
            person_data = self.processor.create_person_data(self.args.person, int(self.args.year))
        
        # Create profile if it doesn't exist
        if not person_data.profile:
            person_data.profile = ProfileData(
                full_name=self.args.person if not self.args.full_name else self.args.full_name
            )
        
        # Update profile fields
        if self.args.full_name:
            person_data.profile.full_name = self.args.full_name
        if self.args.position:
            person_data.profile.position = self.args.position
        if self.args.department:
            person_data.profile.department = self.args.department
        if self.args.manager:
            person_data.profile.manager_name = self.args.manager
        if self.args.is_manager:
            person_data.profile.is_manager = self.args.is_manager
        
        self.processor.save_person_data(person_data)
        self.console.print("[green]Profile updated successfully[/green]")

    def handle_create_sample(self):
        """Handle the create-sample command."""
        # Create sample person data
        sample_people = ["Ana Costa", "Bruno Santos", "Carla Oliveira"]
        current_year = str(datetime.now().year)
        current_year_int = int(current_year)
        
        for person in sample_people:
            # Create person data first
            person_data = PersonData(name=person, year=current_year_int)
            
            # Add profile data
            if person == "Ana Costa":
                person_data.profile = ProfileData(
                    full_name="Ana Costa",
                    position="Software Engineer",
                    department="Engineering",
                    manager_name="Bruno Santos",
                    is_manager=False
                )
            elif person == "Bruno Santos":
                person_data.profile = ProfileData(
                    full_name="Bruno Santos",
                    position="Engineering Manager",
                    department="Engineering",
                    manager_name="Carla Oliveira",
                    is_manager=True
                )
            elif person == "Carla Oliveira":
                person_data.profile = ProfileData(
                    full_name="Carla Oliveira",
                    position="CTO",
                    department="Executive",
                    is_manager=True
                )
            
            # Add attendance records
            person_data.add_attendance(f"{current_year}-01-15", True, "Regular day")
            person_data.add_attendance(f"{current_year}-01-16", False, "Traffic")
            person_data.add_attendance(f"{current_year}-01-17", False, "Sick")
            
            # Add payment records
            salary = 5000.0 if person == "Carla Oliveira" else (3500.0 if person == "Bruno Santos" else 2500.0)
            bonus = 1000.0 if person == "Carla Oliveira" else (500.0 if person == "Bruno Santos" else 250.0)
            
            person_data.add_payment(f"{current_year}-01-15", salary, "salary", "Monthly salary")
            person_data.add_payment(f"{current_year}-01-16", bonus, "bonus", "Performance bonus")
            
            # Save the data
            self.processor.save_person_data(person_data)
        
        self.console.print("[green]Sample data created successfully[/green]")
        
    def handle_sync(self):
        """Handle the sync command."""
        self.console.print("[bold]Syncing and generating reports...[/bold]")
        
        with Progress() as progress:
            # Import data
            task = progress.add_task("[green]Importing data...", total=None)
            import_results = self.processor.import_directory(
                self.args.data_path,
                recursive=self.args.recursive
            )
            progress.update(task, completed=1)
            
            if not import_results["success"]:
                self.console.print(f"[red]Import failed: {import_results['error']}[/red]")
                return
                
            # Generate reports for each person/year
            task = progress.add_task("[green]Generating reports...", total=None)
            
            # Find all person/year directories
            base_path = Path(self.args.data_path)
            if self.args.recursive:
                person_dirs = list(base_path.glob("**/*"))
            else:
                person_dirs = list(base_path.glob("*"))
                
            for person_dir in person_dirs:
                if not person_dir.is_dir():
                    continue
                    
                person = person_dir.name
                year_dirs = list(person_dir.glob("*"))
                
                for year_dir in year_dirs:
                    if not year_dir.is_dir():
                        continue
                        
                    year = year_dir.name
                    
                    # Create analytics directory
                    analytics_dir = year_dir / "analytics"
                    analytics_dir.mkdir(exist_ok=True)
                    
                    # Generate reports
                    report_path = self.processor.generate_report()
                    if report_path:
                        shutil.copy2(report_path, analytics_dir / "report.xlsx")
                        
                    # Generate summary
                    summary_path = self.processor.generate_summary("html")
                    if summary_path:
                        shutil.copy2(summary_path, analytics_dir / "summary.html")
                        
                    # Generate markdown
                    markdown_path = self.processor.generate_summary("markdown")
                    if markdown_path:
                        shutil.copy2(markdown_path, analytics_dir / "summary.md")
                        
            # Generate MermaidJS charts
            task = progress.add_task("[green]Generating MermaidJS charts...", total=None)
            mermaid_files = self.processor.generate_mermaid_chart()
            
            if mermaid_files:
                for person, file_path in mermaid_files.items():
                    # Find person directories
                    for person_dir in base_path.glob(f"*{person}*"):
                        if person_dir.is_dir():
                            # Find year directories
                            year_dirs = list(person_dir.glob("*"))
                            for year_dir in year_dirs:
                                if year_dir.is_dir() and year_dir.name.isdigit():
                                    # Copy to analytics directory
                                    analytics_dir = year_dir / "analytics"
                                    analytics_dir.mkdir(exist_ok=True)
                                    shutil.copy2(file_path, analytics_dir / "visualization.md")
                            
            progress.update(task, completed=1)
            
            # Generate AI prompts
            task = progress.add_task("[green]Generating AI prompts...", total=None)
            prompt_files = self.processor.generate_ai_prompt()
            
            if prompt_files:
                for person, file_path in prompt_files.items():
                    # Find person directories
                    for person_dir in base_path.glob(f"*{person}*"):
                        if person_dir.is_dir():
                            # Find year directories
                            year_dirs = list(person_dir.glob("*"))
                            for year_dir in year_dirs:
                                if year_dir.is_dir() and year_dir.name.isdigit():
                                    # Copy to analytics directory
                                    analytics_dir = year_dir / "analytics"
                                    analytics_dir.mkdir(exist_ok=True)
                                    shutil.copy2(file_path, analytics_dir / "ai_prompt.md")
                            
            progress.update(task, completed=1)
            
            # Generate stakeholder comparison reports
            task = progress.add_task("[green]Generating stakeholder comparison reports...", total=None)
            comparison_files = self.processor.generate_stakeholder_comparison()
            
            if comparison_files:
                for person, file_path in comparison_files.items():
                    # Find person directories
                    for person_dir in base_path.glob(f"*{person}*"):
                        if person_dir.is_dir():
                            # Find year directories
                            year_dirs = list(person_dir.glob("*"))
                            for year_dir in year_dirs:
                                if year_dir.is_dir() and year_dir.name.isdigit():
                                    # Copy to analytics directory
                                    analytics_dir = year_dir / "analytics"
                                    analytics_dir.mkdir(exist_ok=True)
                                    shutil.copy2(file_path, analytics_dir / "stakeholder_comparison.md")
                            
            progress.update(task, completed=1)
            
        self.console.print("[green]Sync completed successfully[/green]")


def main():
    """Run the CLI application."""
    cli = CLI()
    try:
        cli.run()
    except KeyboardInterrupt:
        cli.console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        cli.console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main() 