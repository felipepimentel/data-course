"""
Command Line Interface for People Analytics.

This module provides the main CLI for the People Analytics system.
"""

import argparse
import sys
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress

from .data_processor import DataProcessor
from .data_model import PersonData


class CLI:
    """Command Line Interface for People Analytics."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.console = Console()
        self.args = None
        self.processor = None
        
    def setup(self, data_path, output_path=None):
        """Set up the data processor."""
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
        else:
            self.console.print("[red]Unknown command[/red]")
            
    def _create_parser(self):
        """Create the command line parser."""
        parser = argparse.ArgumentParser(
            description="People Analytics Data Processor",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        
        # Global options
        parser.add_argument(
            "--data-path", 
            default="data",
            help="Path to the data directory"
        )
        parser.add_argument(
            "--output-path", 
            default="output",
            help="Path to the output directory"
        )
        
        # Create subparsers for commands
        subparsers = parser.add_subparsers(dest="command", help="Command to execute")
        
        # validate command
        validate_parser = subparsers.add_parser("validate", help="Validate all data")
        
        # list command
        list_parser = subparsers.add_parser("list", help="List people or years")
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
        summary_parser.add_argument(
            "--format", 
            choices=["json", "csv", "html"],
            default="json",
            help="Output format"
        )
        
        # report command
        report_parser = subparsers.add_parser("report", help="Generate reports")
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
        
        # plot command
        plot_parser = subparsers.add_parser("plot", help="Generate plots")
        plot_parser.add_argument(
            "type",
            choices=["attendance", "payment", "all"],
            help="Type of plot to generate"
        )
        plot_parser.add_argument(
            "--year", 
            help="Year for filtering plots"
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
            
            # Create tables
            info_table = Table(title=f"Data for {self.args.person} ({self.args.year})")
            info_table.add_column("Field", style="cyan")
            info_table.add_column("Value", style="green")
            
            info_table.add_row("Name", data.name)
            info_table.add_row("Year", str(data.year))
            info_table.add_row("Attendance Records", str(len(data.attendance_records)))
            info_table.add_row("Payment Records", str(len(data.payment_records)))
            
            self.console.print(info_table)
            
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