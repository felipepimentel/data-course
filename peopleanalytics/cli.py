#!/usr/bin/env python3
"""
Command Line Interface for the People Analytics package.
Provides tools for data analysis, visualization and reporting.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
import datetime

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn
from rich.table import Table

from peopleanalytics.analyzer import EvaluationAnalyzer
from peopleanalytics.data_pipeline import DataPipeline
from peopleanalytics.schema_manager import SchemaManager
from peopleanalytics.visualization import Visualization


console = Console()


class CLI:
    """Command Line Interface for the People Analytics tool"""
    def __init__(self, base_path=None):
        """Initialize the CLI object"""
        # Set up default database path in user's home directory if none provided
        if base_path is None:
            base_path = os.path.join(os.path.expanduser("~"), ".peopleanalytics")
            
        self.base_path = base_path
        self.analyzer = EvaluationAnalyzer(base_path)
        self.visualization = Visualization()
        self.schema_manager = SchemaManager()
        self.pipeline = DataPipeline(base_path, self.schema_manager)
        self.console = Console()
        
        # Cache for available years and people
        self._available_years = None
        self._available_people = None
        
        # Define color schemes
        self.color_schemes = {
            "default": {
                "concept_colors": {
                    "Excellent": "#27AE60",
                    "Good": "#2ECC71", 
                    "Average": "#F1C40F",
                    "Below Average": "#E67E22",
                    "Poor": "#E74C3C",
                    "default": "#7F8C8D"
                }
            },
            "corporate": {
                "concept_colors": {
                    "Excellent": "#1F618D",
                    "Good": "#2874A6", 
                    "Average": "#5499C7",
                    "Below Average": "#7FB3D5",
                    "Poor": "#A9CCE3",
                    "default": "#D6EAF8"
                }
            },
            "monochrome": {
                "concept_colors": {
                    "Excellent": "#000000",
                    "Good": "#333333", 
                    "Average": "#666666",
                    "Below Average": "#999999",
                    "Poor": "#BBBBBB",
                    "default": "#EEEEEE"
                }
            }
        }
    
    @property
    def available_years(self) -> Set[str]:
        """Get all available years (cached)"""
        if self._available_years is None:
            self._available_years = self.analyzer.get_available_years()
        return self._available_years
    
    @property
    def available_people(self) -> Set[str]:
        """Get all available people (cached)"""
        if self._available_people is None:
            self._available_people = self.analyzer.get_available_people()
        return self._available_people
    
    def enable_caching(self, enabled: bool = True):
        """Enable or disable data caching"""
        if not enabled:
            self._available_years = None
            self._available_people = None
    
    @property
    def output_directory(self) -> str:
        """Get the standard output directory, creating it if it doesn't exist."""
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def run(self, args=None):
        """Main CLI entry point"""
        parser = argparse.ArgumentParser(
            description="Evaluation Analyzer CLI",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        
        # Global arguments
        parser.add_argument(
            "--base-path", 
            default=".", 
            help="Base path for evaluation data"
        )
        parser.add_argument(
            "--color-scheme",
            choices=["default", "corporate", "monochrome"],
            default="default",
            help="Color scheme for visualizations"
        )
        parser.add_argument(
            "--no-cache",
            action="store_true",
            help="Disable data caching for better memory usage"
        )
        parser.add_argument(
            "--parallel",
            action="store_true",
            help="Enable parallel processing for improved performance"
        )
        parser.add_argument(
            "--workers",
            type=int,
            default=None,
            help="Number of worker threads for parallel processing (default: auto)"
        )
        
        # Create subparsers for different commands
        subparsers = parser.add_subparsers(dest="command", help="Command to run")
        
        # List command
        list_parser = subparsers.add_parser("list", help="List available data")
        list_subparsers = list_parser.add_subparsers(dest="list_type", help="Type of data to list")
        
        # List people
        list_people_parser = list_subparsers.add_parser("people", help="List all people in the database")
        list_people_parser.add_argument("--years", nargs="+", help="Filter by specific years")
        
        # List years
        list_years_parser = list_subparsers.add_parser("years", help="List all available years")
        
        # List criteria
        list_criteria_parser = list_subparsers.add_parser("criteria", help="List all evaluation criteria")
        list_criteria_parser.add_argument("--year", help="Filter by specific year")
        
        # List stats
        list_stats_parser = list_subparsers.add_parser("stats", help="Show database statistics")
        
        # Compare command
        compare_parser = subparsers.add_parser("compare", help="Compare evaluations for a year")
        compare_parser.add_argument("year", help="Year to compare")
        compare_parser.add_argument("--filter", nargs="+", help="Filter specific people")
        compare_parser.add_argument("--output", help="Output file path (without extension)")
        compare_parser.add_argument(
            "--format", 
            choices=["csv", "png", "all"], 
            default="all",
            help="Output format"
        )

        # Historical command
        historical_parser = subparsers.add_parser("historical", help="Generate historical report for a person")
        historical_parser.add_argument("person", help="Person name")
        historical_parser.add_argument("--years", nargs="+", help="Filter by specific years")
        historical_parser.add_argument("--output", help="Output file path (without extension)")
        historical_parser.add_argument(
            "--format", 
            choices=["csv", "png", "all"], 
            default="all",
            help="Output format"
        )
        
        # Validate command with enhanced options
        validate_parser = subparsers.add_parser("validate", help="Validate evaluation data")
        validate_parser.add_argument("--output", help="Output file path for validation report")
        validate_parser.add_argument(
            "--fix", 
            action="store_true", 
            help="Attempt to fix common data issues"
        )
        validate_parser.add_argument(
            "--verbose", 
            action="store_true", 
            help="Show detailed validation results"
        )
        validate_parser.add_argument(
            "--html", 
            action="store_true", 
            help="Generate HTML validation report"
        )
        
        # Export command
        export_parser = subparsers.add_parser("export", help="Export evaluation data")
        export_parser.add_argument(
            "format", 
            choices=["excel", "csv", "json"], 
            help="Export format"
        )
        export_parser.add_argument("--output", help="Output file path (without extension)")
        export_parser.add_argument("--years", nargs="+", help="Filter by specific years")
        export_parser.add_argument("--people", nargs="+", help="Filter specific people")
        
        # Advanced filter command
        filter_parser = subparsers.add_parser("filter", help="Advanced filtering options")
        filter_parser.add_argument("--name-regex", help="Regex pattern to filter people names")
        filter_parser.add_argument("--behavior-regex", help="Regex pattern to filter behaviors")
        filter_parser.add_argument("--min-score", type=float, help="Minimum score threshold")
        filter_parser.add_argument("--max-score", type=float, help="Maximum score threshold")
        filter_parser.add_argument("--concepts", nargs="+", help="Filter by specific concepts")
        filter_parser.add_argument("--years", nargs="+", help="Filter by specific years")
        filter_parser.add_argument("--output", help="Output file path (without extension)")
        filter_parser.add_argument(
            "--format", 
            choices=["csv", "excel", "json", "html"],
            default="csv",
            help="Output format"
        )
        
        # Team analysis command
        team_parser = subparsers.add_parser("teams", help="Team analysis features")
        team_subparsers = team_parser.add_subparsers(dest="team_command", help="Team command to run")
        
        # Team structure file (shared argument)
        team_parser.add_argument(
            "--team-file", 
            required=True,
            help="JSON file containing team structure (manager -> [team members])"
        )
        
        # List teams
        team_list_parser = team_subparsers.add_parser("list", help="List all teams and managers")
        
        # Manager report
        team_manager_parser = team_subparsers.add_parser("manager", help="Generate manager report")
        team_manager_parser.add_argument("manager", help="Manager name")
        team_manager_parser.add_argument("year", help="Year to analyze")
        team_manager_parser.add_argument("--output", help="Output file path prefix")
        
        # Team comparison
        team_compare_parser = team_subparsers.add_parser("compare", help="Compare team performance")
        team_compare_parser.add_argument("team", help="Team identifier or manager name")
        team_compare_parser.add_argument("year", help="Year to analyze")
        team_compare_parser.add_argument("--output", help="Output file path prefix")
        
        # Visualization command
        viz_parser = subparsers.add_parser("visualize", help="Generate visualizations")
        viz_parser.add_argument(
            "--type", 
            choices=["radar", "heatmap", "interactive"],
            required=True,
            help="Type of visualization to generate"
        )
        viz_parser.add_argument("--data-file", help="JSON file containing data to visualize")
        viz_parser.add_argument("--output", required=True, help="Output file path")
        viz_parser.add_argument("--title", default="Evaluation Visualization", help="Chart title")
        
        # Add easier arguments for person and year
        viz_parser.add_argument("--person", help="Person to visualize (for radar charts)")
        viz_parser.add_argument("--year", help="Year to visualize")
        viz_parser.add_argument("--people", nargs="+", help="People to include in visualization")
        
        # Pipeline command
        pipeline_parser = subparsers.add_parser("pipeline", help="Handle data pipeline operations")
        pipeline_parser.add_argument(
            "operation", 
            choices=["import", "backup", "export", "fix"], 
            help="Operation to perform"
        )
        pipeline_parser.add_argument("--file", help="File to import")
        pipeline_parser.add_argument("--directory", help="Directory to import from")
        pipeline_parser.add_argument("--pattern", help="Pattern to match files")
        pipeline_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing data")
        pipeline_parser.add_argument("--sequential", action="store_true", help="Run operations sequentially")
        pipeline_parser.add_argument("--output", help="Output file path for exports")
        pipeline_parser.add_argument("--output-directory", help="Output directory for backup")
        pipeline_parser.add_argument("--verbose", action="store_true", help="Show verbose output including all errors")
        pipeline_parser.add_argument("--error-report", help="Save detailed error report to specified file")
        pipeline_parser.add_argument("--debug", action="store_true", help="Run in debug mode with detailed processing information")
        
        # Parse arguments
        parsed_args = parser.parse_args(args)
        
        # Set the base path
        if parsed_args.base_path:
            self.base_path = parsed_args.base_path
            self.analyzer = EvaluationAnalyzer(self.base_path)
            self.pipeline = DataPipeline(self.base_path, self.schema_manager)
        
        # Apply color scheme
        if hasattr(parsed_args, "color_scheme") and parsed_args.color_scheme in self.color_schemes:
            self.visualization.custom_colors = self.color_schemes[parsed_args.color_scheme]
        
        # Enable/disable caching
        if hasattr(parsed_args, "no_cache") and parsed_args.no_cache:
            self.enable_caching(False)
        
        # Handle different commands
        if parsed_args.command == "list":
            self.handle_list(parsed_args)
        elif parsed_args.command == "compare":
            self.handle_compare(parsed_args)
        elif parsed_args.command == "historical":
            self.handle_historical(parsed_args)
        elif parsed_args.command == "validate":
            self.handle_validate(parsed_args)
        elif parsed_args.command == "export":
            self.handle_export(parsed_args)
        elif parsed_args.command == "filter":
            self.handle_filter(parsed_args)
        elif parsed_args.command == "teams":
            self.handle_teams(parsed_args)
        elif parsed_args.command == "visualize":
            self.handle_visualization(parsed_args)
        elif parsed_args.command == "pipeline":
            self.handle_pipeline(parsed_args)
        else:
            parser.print_help()
            
    def handle_list(self, args):
        """Handle the list command by dispatching to the appropriate handler"""
        if args.list_type == "people":
            self.handle_list_people(args)
        elif args.list_type == "years":
            self.handle_list_years(args)
        elif args.list_type == "criteria":
            self.handle_list_criteria(args)
        elif args.list_type == "stats":
            self.handle_list_stats(args)
        else:
            self.console.print("[yellow]Please specify what to list (people, years, criteria, stats)[/yellow]")
    
    def handle_list_people(self, args):
        """Handle the list people command"""
        years_filter = args.years if hasattr(args, "years") else None
        
        # Get all people
        people = sorted(self.available_people)
        
        if not people:
            self.console.print("[yellow]No people found in the database[/yellow]")
            return
            
        # Apply year filter if specified
        if years_filter:
            filtered_people = []
            for person in people:
                person_years = self.analyzer.get_years_for_person(person)
                if any(year in person_years for year in years_filter):
                    filtered_people.append(person)
            people = filtered_people
            
        # Display results
        table = Table(title="Available People")
        table.add_column("Person", style="cyan")
        table.add_column("Years", style="green")
        
        for person in people:
            # Get years for this person
            years = sorted(self.analyzer.get_years_for_person(person))
            table.add_row(person, ", ".join(years))
            
        self.console.print(table)
        
    def handle_list_years(self, args):
        """Handle the list years command"""
        # Get all years
        years = sorted(self.available_years)
        
        if not years:
            self.console.print("[yellow]No years found in the database[/yellow]")
            return
            
        # Display results
        table = Table(title="Available Years")
        table.add_column("Year", style="cyan")
        table.add_column("People Count", style="green")
        
        for year in years:
            # Count people for this year
            people_count = len(self.analyzer.get_people_for_year(year))
            table.add_row(year, str(people_count))
            
        self.console.print(table)
        
    def handle_list_criteria(self, args):
        """Handle the list criteria command"""
        year_filter = args.year if hasattr(args, "year") else None
        
        # Get evaluation criteria
        try:
            criteria = self.analyzer.get_criteria_for_year(year_filter) if year_filter else {}
            
            if not criteria and year_filter:
                self.console.print(f"[yellow]No criteria found for year {year_filter}[/yellow]")
                return
                
            if not criteria:
                # Get criteria for all years
                all_criteria = {}
                for year in sorted(self.available_years):
                    year_criteria = self.analyzer.get_criteria_for_year(year)
                    if year_criteria:
                        all_criteria[year] = year_criteria
                
                if not all_criteria:
                    self.console.print("[yellow]No evaluation criteria found in any year[/yellow]")
                    return
                    
                # Display criteria by year
                for year, year_criteria in all_criteria.items():
                    self.console.print(f"\n[bold]Criteria for {year}:[/bold]")
                    
                    table = Table(title=f"Evaluation Criteria - {year}")
                    table.add_column("Direcionador", style="cyan")
                    table.add_column("Comportamentos", style="green")
                    
                    for direcionador, comportamentos in year_criteria.items():
                        table.add_row(direcionador, "\n".join(sorted(comportamentos)))
                        
                    self.console.print(table)
            else:
                # Display criteria for specific year
                table = Table(title=f"Evaluation Criteria - {year_filter}")
                table.add_column("Direcionador", style="cyan")
                table.add_column("Comportamentos", style="green")
                
                for direcionador, comportamentos in criteria.items():
                    table.add_row(direcionador, "\n".join(sorted(comportamentos)))
                    
                self.console.print(table)
                
        except Exception as e:
            self.console.print(f"[red]Error retrieving criteria: {str(e)}[/red]")
    
    def handle_list_stats(self, args):
        """Handle the list stats command"""
        # Collect statistics
        total_evaluations = 0
        evaluations_by_year = {}
        evaluations_by_person = {}
        
        years = sorted(self.available_years)
        people = sorted(self.available_people)
        
        for year in years:
            for person in people:
                try:
                    evaluation = self.analyzer.get_evaluations_for_person(person, year)
                    if evaluation and evaluation.get("success", False):
                        total_evaluations += 1
                        evaluations_by_year[year] = evaluations_by_year.get(year, 0) + 1
                        evaluations_by_person[person] = evaluations_by_person.get(person, 0) + 1
                except Exception:
                    # Skip if data is not available
                    pass
        
        # Display statistics
        self.console.print(Panel(
            f"[bold]Database Statistics[/bold]\n\n"
            f"Total People: [cyan]{len(people)}[/cyan]\n"
            f"Total Years: [cyan]{len(years)}[/cyan]\n"
            f"Total Evaluations: [cyan]{total_evaluations}[/cyan]",
            title="Summary",
            expand=False
        ))
        
        # Show evaluations by year
        if evaluations_by_year:
            table = Table(title="Evaluations by Year")
            table.add_column("Year", style="cyan")
            table.add_column("Count", style="green")
            
            for year, count in sorted(evaluations_by_year.items()):
                table.add_row(year, str(count))
                
            self.console.print(table)
        
        # Show top people by evaluation count
        if evaluations_by_person:
            table = Table(title="Top 10 People by Evaluation Count")
            table.add_column("Person", style="cyan")
            table.add_column("Count", style="green")
            
            # Sort by count (descending) and take top 10
            top_people = sorted(evaluations_by_person.items(), key=lambda x: x[1], reverse=True)[:10]
            
            for person, count in top_people:
                table.add_row(person, str(count))
                
            self.console.print(table)
    
    def handle_compare(self, args):
        """Handle the compare command"""
        try:
            year = args.year
            people_filter = args.filter
            
            # Generate comparative report
            self.console.print(f"[bold]Generating comparative report for {year}...[/bold]")
            
            df = self.analyzer.compare_people_for_year(year)
            
            if df.empty:
                self.console.print("[yellow]No data to analyze for this year[/yellow]")
                return
                
            # Apply people filter if specified
            if people_filter:
                df = df[df['Person'].isin(people_filter)]
                
                if df.empty:
                    self.console.print("[yellow]No data after filtering[/yellow]")
                    return
            
            # Display results as table
            table = Table(title=f"Comparative Results - {year}")
            table.add_column("Person", style="cyan")
            table.add_column("Concept", style="green")
            table.add_column("Score", style="yellow")
            table.add_column("Group Avg", style="blue")
            table.add_column("Diff", style="magenta")
            
            for _, row in df.iterrows():
                person = row['Person']
                concept = row['Overall Concept']
                score = f"{row['Average Score']:.2f}"
                group_avg = f"{row['Group Average']:.2f}"
                
                diff = row['Difference']
                diff_str = f"{diff:.2f}"
                
                # Color code the difference
                if diff > 0:
                    diff_str = f"[green]+{diff:.2f}[/green]"
                elif diff < 0:
                    diff_str = f"[red]{diff:.2f}[/red]"
                
                table.add_row(person, concept, score, group_avg, diff_str)
                
            self.console.print(table)
            
            # Save results if output specified
            if args.output:
                output_base = args.output
                output_format = args.format
                
                if output_format in ["csv", "all"]:
                    csv_path = f"{output_base}.csv"
                    df.to_csv(csv_path, index=False)
                    self.console.print(f"[green]CSV report saved to {csv_path}[/green]")
                    
                if output_format in ["png", "all"]:
                    png_path = f"{output_base}.png"
                    self.analyzer.plot_comparative_report(df, year, png_path)
                    self.console.print(f"[green]Chart saved to {png_path}[/green]")
            else:
                # Use default output path if none specified
                output_format = args.format
                
                if output_format in ["csv", "all"]:
                    csv_path = os.path.join(self.output_directory, f"comparative_report_{year}.csv")
                    df.to_csv(csv_path, index=False)
                    self.console.print(f"[green]CSV report saved to {csv_path}[/green]")
                    
                if output_format in ["png", "all"]:
                    png_path = os.path.join(self.output_directory, f"comparative_report_{year}.png")
                    self.analyzer.plot_comparative_report(df, year, png_path)
                    self.console.print(f"[green]Chart saved to {png_path}[/green]")
                
        except Exception as e:
            self.console.print(f"[red]Error generating comparative report: {str(e)}[/red]")
    
    def handle_historical(self, args):
        """Handle the historical command"""
        try:
            person = args.person
            
            # Ensure person exists
            if person not in self.available_people:
                self.console.print(f"[red]Person '{person}' not found in the database[/red]")
                return
                
            # Filter by years if specified
            years_filter = args.years
            
            # Get historical data
            self.console.print(f"[bold]Generating historical report for {person}...[/bold]")
            
            data = self.analyzer.person_year_over_year(person)
            
            if not data or "years" not in data or not data["years"]:
                self.console.print("[yellow]No historical data available for this person[/yellow]")
                return
                
            # Apply year filter if specified
            if years_filter:
                # Filter data to include only specified years
                filtered_years = [year for year in data["years"] if year in years_filter]
                
                if not filtered_years:
                    self.console.print("[yellow]No data available for the specified years[/yellow]")
                    return
                    
                # Update data structure with filtered years
                data["years"] = filtered_years
                
                # Filter all other year-specific data
                for key in ["year_scores", "year_group_scores", "concepts"]:
                    if key in data:
                        data[key] = {year: value for year, value in data[key].items() if year in filtered_years}
                
            # Display results
            self.console.print(f"\n[bold]Historical Report - {person}[/bold]")
            
            table = Table(title=f"Year-over-Year Performance - {person}")
            table.add_column("Year", style="cyan")
            table.add_column("Concept", style="green")
            table.add_column("Score", style="yellow")
            table.add_column("Group Avg", style="blue")
            table.add_column("Diff", style="magenta")
            
            for year in data["years"]:
                concept = data["concepts"].get(year, "Unknown")
                score = data["year_scores"].get(year, 0)
                group_avg = data["year_group_scores"].get(year, 0)
                diff = score - group_avg
                
                diff_style = "green" if diff >= 0 else "red"
                
                table.add_row(
                    year,
                    concept,
                    f"{score:.2f}",
                    f"{group_avg:.2f}",
                    f"[{diff_style}]{diff:.2f}[/{diff_style}]"
                )
                
            self.console.print(table)
            
            # Calculate overall trend
            years = data["years"]
            if len(years) > 1:
                first_year = years[0]
                last_year = years[-1]
                
                first_score = data["year_scores"].get(first_year, 0)
                last_score = data["year_scores"].get(last_year, 0)
                
                absolute = last_score - first_score
                relative = (absolute / first_score) * 100 if first_score > 0 else 0
                
                color = "green" if absolute >= 0 else "red"
                
                self.console.print(f"\n[bold]Overall Trend ({first_year} to {last_year}):[/bold]")
                self.console.print(f"Absolute change: [{color}]{absolute:.2f}[/{color}]")
                self.console.print(f"Relative improvement: [{color}]{relative:.1f}%[/{color}]")
            
            # Save results if output specified
            if args.output:
                output_base = args.output
                output_format = args.format
                
                if output_format in ["csv", "all"]:
                    # Create DataFrame from results
                    rows = []
                    for year in data["years"]:
                        rows.append({
                            "Year": year,
                            "Concept": data["concepts"].get(year, "Unknown"),
                            "Score": data["year_scores"].get(year, 0),
                            "Group_Average": data["year_group_scores"].get(year, 0),
                            "Difference": data["year_scores"].get(year, 0) - data["year_group_scores"].get(year, 0)
                        })
                    
                    result_df = pd.DataFrame(rows)
                    csv_path = f"{output_base}.csv"
                    result_df.to_csv(csv_path, index=False)
                    self.console.print(f"[green]CSV report saved to {csv_path}[/green]")
                    
                if output_format in ["png", "all"]:
                    png_path = f"{output_base}.png"
                    self.analyzer.generate_historical_report(person, png_path)
                    self.console.print(f"[green]Chart saved to {png_path}[/green]")
            else:
                # Use default output path if none specified
                output_format = args.format
                
                if output_format in ["csv", "all"]:
                    # Create DataFrame from results
                    rows = []
                    for year in data["years"]:
                        rows.append({
                            "Year": year,
                            "Concept": data["concepts"].get(year, "Unknown"),
                            "Score": data["year_scores"].get(year, 0),
                            "Group_Average": data["year_group_scores"].get(year, 0),
                            "Difference": data["year_scores"].get(year, 0) - data["year_group_scores"].get(year, 0)
                        })
                    
                    result_df = pd.DataFrame(rows)
                    csv_path = os.path.join(self.output_directory, f"historical_report_{person}.csv")
                    result_df.to_csv(csv_path, index=False)
                    self.console.print(f"[green]CSV report saved to {csv_path}[/green]")
                    
                if output_format in ["png", "all"]:
                    png_path = os.path.join(self.output_directory, f"historical_report_{person}.png")
                    self.analyzer.generate_historical_report(person, png_path)
                    self.console.print(f"[green]Chart saved to {png_path}[/green]")
                
        except Exception as e:
            self.console.print(f"[red]Error generating historical report: {str(e)}[/red]")
    
    def handle_validate(self, args):
        """Handle the validate command"""
        # Placeholder for validation implementation
        self.console.print("[yellow]Validation feature not yet implemented[/yellow]")
    
    def handle_export(self, args):
        """Handle the export command"""
        try:
            export_format = args.format
            years_filter = args.years
            people_filter = args.people
            
            # Get all people and years
            all_people = self.available_people
            all_years = self.available_years
            
            if not all_people or not all_years:
                self.console.print("[yellow]No data found to export[/yellow]")
                return
                
            # Apply filters
            people = [p for p in all_people if not people_filter or p in people_filter]
            years = [y for y in all_years if not years_filter or y in years_filter]
            
            if not people:
                self.console.print("[yellow]No people match the specified filter[/yellow]")
                return
                
            if not years:
                self.console.print("[yellow]No years match the specified filter[/yellow]")
                return
                
            # Collect all data
            self.console.print("[bold]Collecting data to export...[/bold]")
            data = []
            
            for person in sorted(people):
                for year in sorted(years):
                    evaluation = self.analyzer.get_evaluations_for_person(person, year)
                    if evaluation and evaluation.get('success', False):
                        score = self.analyzer.get_average_score(person, year)
                        concept = evaluation.get('data', {}).get('conceito_ciclo_filho_descricao', 'Unknown')
                        
                        data.append({
                            'Person': person,
                            'Year': year,
                            'Score': score if score is not None else 0,
                            'Concept': concept
                        })
                        
            if not data:
                self.console.print("[yellow]No data to export[/yellow]")
                return
                
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Determine output path
            if args.output:
                output_base = args.output
            else:
                # Use default output path
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_base = os.path.join(self.output_directory, f"export_{timestamp}")
                
            # Export based on format
            if export_format == "excel":
                output_file = f"{output_base}.xlsx"
                df.to_excel(output_file, index=False)
                self.console.print(f"[green]Data exported to {output_file}[/green]")
                
            elif export_format == "csv":
                output_file = f"{output_base}.csv"
                df.to_csv(output_file, index=False)
                self.console.print(f"[green]Data exported to {output_file}[/green]")
                
            elif export_format == "json":
                output_file = f"{output_base}.json"
                df.to_json(output_file, orient='records', indent=2)
                self.console.print(f"[green]Data exported to {output_file}[/green]")
                
        except Exception as e:
            self.console.print(f"[red]Error exporting data: {str(e)}[/red]")
    
    def handle_filter(self, args):
        """Handle the filter command with advanced filtering options"""
        try:
            # Get filter criteria
            name_regex = args.name_regex
            behavior_regex = args.behavior_regex
            min_score = args.min_score
            max_score = args.max_score
            concepts = args.concepts
            years_filter = args.years
            
            # Get all people and years
            all_people = self.available_people
            all_years = self.available_years
            
            if not all_people or not all_years:
                self.console.print("[yellow]No data found to filter[/yellow]")
                return
                
            # Apply year filter
            years = [y for y in all_years if not years_filter or y in years_filter]
            
            if not years:
                self.console.print("[yellow]No years match the specified filter[/yellow]")
                return
                
            # Collect all data
            self.console.print("[bold]Collecting data based on filters...[/bold]")
            filtered_data = []
            
            import re
            name_pattern = re.compile(name_regex) if name_regex else None
            behavior_pattern = re.compile(behavior_regex) if behavior_regex else None
            
            people_with_data = set()
            
            for person in sorted(all_people):
                # Filter by name regex if specified
                if name_pattern and not name_pattern.search(person):
                    continue
                    
                for year in sorted(years):
                    # Get evaluation data
                    evaluation = self.analyzer.get_evaluations_for_person(person, year)
                    if not evaluation or not evaluation.get('success', False):
                        continue
                        
                    # Get concept if available
                    concept = evaluation.get('data', {}).get('conceito_ciclo_filho_descricao', 'Unknown')
                    
                    # Filter by concept if specified
                    if concepts and concept not in concepts:
                        continue
                    
                    # Get behavior scores
                    behavior_scores = self.analyzer.get_behavior_scores(person, year)
                    if not behavior_scores:
                        continue
                    
                    # Check each behavior
                    for direcionador, behaviors in behavior_scores.items():
                        for comp_name, details in behaviors.items():
                            # Filter by behavior regex if specified
                            if behavior_pattern and not behavior_pattern.search(comp_name):
                                continue
                            
                            # Get score for this behavior
                            score = None
                            for avaliador, scores in details.get('scores', {}).items():
                                if avaliador == '%todos':
                                    score = scores.get('score_colaborador')
                                    break
                            
                            if score is None:
                                continue
                                
                            # Filter by score range if specified
                            if (min_score is not None and score < min_score) or \
                               (max_score is not None and score > max_score):
                                continue
                                
                            # Add to filtered data
                            filtered_data.append({
                                'Person': person,
                                'Year': year,
                                'Direcionador': direcionador,
                                'Comportamento': comp_name,
                                'Score': score,
                                'Concept': concept
                            })
                            
                            people_with_data.add(person)
                            
            if not filtered_data:
                self.console.print("[yellow]No data matches the specified filters[/yellow]")
                return
                
            # Convert to DataFrame
            df = pd.DataFrame(filtered_data)
            
            # Display summary
            self.console.print(f"\n[bold]Filter Results Summary:[/bold]")
            self.console.print(f"Matching records: [cyan]{len(filtered_data)}[/cyan]")
            self.console.print(f"Unique people: [cyan]{len(people_with_data)}[/cyan]")
            self.console.print(f"Years included: [cyan]{', '.join(sorted(years))}[/cyan]")
            
            # Display sample of results
            sample_size = min(10, len(filtered_data))
            if sample_size > 0:
                self.console.print(f"\n[bold]Sample of Results (showing {sample_size} of {len(filtered_data)}):[/bold]")
                
                table = Table()
                table.add_column("Person", style="cyan")
                table.add_column("Year", style="green")
                table.add_column("Behavior", style="yellow")
                table.add_column("Score", style="blue")
                
                for _, row in df.head(sample_size).iterrows():
                    table.add_row(
                        row['Person'],
                        row['Year'],
                        row['Comportamento'],
                        f"{row['Score']:.2f}"
                    )
                    
                self.console.print(table)
            
            # Export results if output specified
            if args.output:
                output_base = args.output
                output_format = args.format
                
                self._export_filtered_results(df, output_base, output_format)
            else:
                # Use default output path
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_base = os.path.join(self.output_directory, f"filtered_results_{timestamp}")
                output_format = args.format
                
                self._export_filtered_results(df, output_base, output_format)
                
        except Exception as e:
            self.console.print(f"[red]Error filtering data: {str(e)}[/red]")
            
    def _export_filtered_results(self, df, output_base, output_format):
        """Helper method to export filtered results in different formats"""
        if output_format == "csv":
            output_file = f"{output_base}.csv"
            df.to_csv(output_file, index=False)
            self.console.print(f"[green]Results exported to {output_file}[/green]")
            
        elif output_format == "excel":
            output_file = f"{output_base}.xlsx"
            df.to_excel(output_file, index=False)
            self.console.print(f"[green]Results exported to {output_file}[/green]")
            
        elif output_format == "json":
            output_file = f"{output_base}.json"
            df.to_json(output_file, orient='records', indent=2)
            self.console.print(f"[green]Results exported to {output_file}[/green]")
            
        elif output_format == "html":
            output_file = f"{output_base}.html"
            
            # Create an interactive HTML report using visualization.generate_interactive_html
            report_title = "Filtered Results Report"
            report_data = {
                'title': report_title,
                'filtered_data': df.to_dict('records'),
                'summary': {
                    'total_records': len(df),
                    'unique_people': df['Person'].nunique(),
                    'years': sorted(df['Year'].unique()),
                    'filters_applied': True
                }
            }
            
            self.visualization.generate_interactive_html(report_data, output_file)
            self.console.print(f"[green]Interactive HTML report saved to {output_file}[/green]")
    
    def handle_teams(self, args):
        """Handle the teams command"""
        # Placeholder for teams implementation
        self.console.print("[yellow]Teams feature not yet implemented[/yellow]")
    
    def handle_visualization(self, args):
        """Handle the visualization command"""
        try:
            self.console.print(f"[bold]Generating {args.type} visualization...[/bold]")
            
            # Load data if data file provided
            data = None
            if args.data_file:
                with open(args.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.console.print(f"[green]Loaded data from {args.data_file}[/green]")
            else:
                # If no data file, try to use analyzer to get data for the person or year
                if args.person and args.year and args.type == "radar":
                    # Get behavior scores for radar chart
                    behavior_scores = self.analyzer.get_behavior_scores(args.person, args.year)
                    if behavior_scores:
                        # Prepare radar chart data
                        categories = []
                        person_scores = []
                        group_scores = []
                        
                        for dir_name, behaviors in behavior_scores.items():
                            dir_scores_person = []
                            dir_scores_group = []
                            
                            for comp_name, details in behaviors.items():
                                for avaliador, scores in details.get("scores", {}).items():
                                    if avaliador == "%todos":  # Use the overall evaluation
                                        dir_scores_person.append(scores.get("score_colaborador", 0))
                                        dir_scores_group.append(scores.get("score_grupo", 0))
                            
                            if dir_scores_person and dir_scores_group:
                                categories.append(dir_name.split(".")[0])
                                person_scores.append(sum(dir_scores_person) / len(dir_scores_person))
                                group_scores.append(sum(dir_scores_group) / len(dir_scores_group))
                        
                        # Create radar chart data
                        data = {
                            "categories": categories,
                            "series": {
                                args.person: person_scores,
                                "Grupo": group_scores
                            }
                        }
                elif args.type == "heatmap" and args.year:
                    # Get all people for year
                    people = list(self.analyzer.get_people_for_year(args.year))
                    if not people:
                        self.console.print("[red]No people found for this year[/red]")
                        return
                        
                    # Limit to specified people if provided
                    if args.people:
                        people = [p for p in people if p in args.people]
                    
                    # Get criteria for selected year
                    criteria = self.analyzer.get_criteria_for_year(args.year)
                    
                    if criteria:
                        all_criteria = []
                        for dir_behaviors in criteria.values():
                            all_criteria.extend(dir_behaviors)
                        all_criteria = list(set(all_criteria))
                        
                        # Collect scores for each person and criterion
                        heatmap_data = []
                        for person in people:
                            for criterion in all_criteria:
                                score = self.analyzer.get_score_for_criterion(person, args.year, criterion)
                                if score is not None:
                                    heatmap_data.append({
                                        "Person": person,
                                        "Criterion": criterion,
                                        "Score": score
                                    })
                        
                        if heatmap_data:
                            import pandas as pd
                            data = pd.DataFrame(heatmap_data)
                elif args.type == "interactive" and args.year:
                    # Get all people for year
                    people = list(self.analyzer.get_people_for_year(args.year))
                    if not people:
                        self.console.print("[red]No people found for this year[/red]")
                        return
                    
                    # Limit to specified people if provided
                    if args.people:
                        people = [p for p in people if p in args.people]
                        
                    # Collect data for all people
                    comparison_data = []
                    for person in people:
                        avg_score = self.analyzer.get_average_score(person, args.year)
                        if avg_score is not None:
                            comparison_data.append({
                                "Person": person,
                                "Score": avg_score
                            })
                    
                    if comparison_data:
                        import pandas as pd
                        comparison_df = pd.DataFrame(comparison_data)
                        comparison_df = comparison_df.sort_values(by="Score", ascending=False)
                        
                        data = {
                            "title": f"Team Performance Comparison ({args.year})",
                            "summary": {
                                "Year": args.year,
                                "People Count": len(comparison_data),
                                "Average Team Score": round(comparison_df["Score"].mean(), 2)
                            },
                            "chartType": "bar",
                            "labels": comparison_df["Person"].tolist(),
                            "datasets": [{
                                "label": "Performance Score",
                                "data": comparison_df["Score"].tolist(),
                                "backgroundColor": "#4a6fa5"
                            }],
                            "tableData": [
                                {
                                    "Name": row["Person"],
                                    "Score": round(row["Score"], 2),
                                    "Rank": i+1
                                }
                                for i, row in enumerate(comparison_df.to_dict("records"))
                            ]
                        }
                
            # Generate visualization based on type
            if not data:
                self.console.print("[red]Error: No data available for visualization[/red]")
                return
                
            if args.type == "radar":
                self.visualization.generate_radar_chart(
                    data=data,
                    title=args.title,
                    output_path=args.output
                )
                self.console.print(f"[green]Radar chart saved to {args.output}[/green]")
                
            elif args.type == "heatmap":
                # Check if data is DataFrame
                if not isinstance(data, pd.DataFrame):
                    self.console.print("[red]Error: Invalid data format for heatmap[/red]")
                    return
                    
                # Check if required columns are present
                columns = data.columns
                if len(columns) < 3:
                    self.console.print("[red]Error: Heatmap requires at least 3 columns (x, y, value)[/red]")
                    return
                    
                x_col, y_col, val_col = columns[:3]
                self.visualization.generate_heatmap(
                    data=data,
                    x_col=x_col, 
                    y_col=y_col, 
                    value_col=val_col,
                    title=args.title,
                    output_path=args.output
                )
                self.console.print(f"[green]Heatmap saved to {args.output}[/green]")
                
            elif args.type == "interactive":
                self.visualization.generate_interactive_html(
                    data=data,
                    output_path=args.output
                )
                self.console.print(f"[green]Interactive HTML report saved to {args.output}[/green]")
                
        except Exception as e:
            self.console.print(f"[red]Error generating visualization: {str(e)}[/red]")
    
    def handle_pipeline(self, args):
        """Handle the pipeline command"""
        try:
            # Initialize pipeline
            pipeline = self.pipeline
            
            if args.operation == "import":
                # Enable debug mode if requested
                if hasattr(args, "debug") and args.debug:
                    self.console.print("[yellow]Debug mode enabled - showing detailed processing information[/yellow]")
                    # Set debug flag for detailed logging
                    pipeline.debug_mode = True
                
                # Import data from files
                if args.file:
                    # Single file import
                    self.console.print(f"[bold]Importing file {args.file}...[/bold]")
                    
                    if hasattr(args, "debug") and args.debug:
                        self.console.print(f"[dim]DEBUG: Processing file {args.file}[/dim]")
                        self.console.print(f"[dim]DEBUG: Extracting metadata...[/dim]")
                    
                    success = pipeline.ingest_file(
                        args.file,
                        args.year if hasattr(args, "year") else None,
                        args.person if hasattr(args, "person") else None,
                        overwrite=args.overwrite
                    )
                    
                    if success and success.get('success', False):
                        self.console.print(f"[green]Successfully imported file: {args.file}[/green]")
                        
                        if hasattr(args, "debug") and args.debug:
                            # Show detailed import information in debug mode
                            self.console.print("[dim]DEBUG: Import details:[/dim]")
                            for key, value in success.items():
                                if key not in ['success', 'file']:
                                    self.console.print(f"[dim]DEBUG:   {key}: {value}[/dim]")
                    else:
                        error = success.get('error', 'Unknown error')
                        self.console.print(f"[red]Failed to import file: {args.file} - {error}[/red]")
                        
                        if hasattr(args, "debug") and args.debug and 'error_trace' in success:
                            self.console.print(f"[dim]DEBUG: Error trace: {success['error_trace']}[/dim]")
                        
                elif args.directory:
                    # Directory import
                    self.console.print(f"[bold]Importing files from {args.directory}...[/bold]")
                    
                    if hasattr(args, "debug") and args.debug:
                        self.console.print(f"[dim]DEBUG: Searching for files matching pattern: {args.pattern or '*.json'}[/dim]")
                        self.console.print(f"[dim]DEBUG: Parallel processing: {not args.sequential}[/dim]")
                    
                    results = pipeline.ingest_directory(
                        args.directory,
                        pattern=args.pattern or "*.json",
                        overwrite=args.overwrite,
                        parallel=not args.sequential,
                        debug=hasattr(args, "debug") and args.debug
                    )
                    
                    self.console.print(f"[green]Import completed: {results['success']} succeeded, {results['failed']} failed[/green]")
                    
                    # Display debug summary if in debug mode
                    if hasattr(args, "debug") and args.debug and 'debug_info' in results:
                        self.console.print("[dim]DEBUG: Processing summary:[/dim]")
                        for info in results['debug_info'][:10]:  # Show first 10 debug entries
                            self.console.print(f"[dim]DEBUG: {info}[/dim]")
                        
                        if len(results.get('debug_info', [])) > 10:
                            self.console.print(f"[dim]DEBUG: ... and {len(results['debug_info']) - 10} more processing entries[/dim]")
                    
                    # Display detailed error information if there were failures
                    if results['failed'] > 0 and 'error_details' in results:
                        # Group errors by type
                        error_types = {}
                        for error in results['error_details']:
                            error_type = error.get('error_type', 'unknown')
                            if error_type not in error_types:
                                error_types[error_type] = []
                            error_types[error_type].append(error)
                            
                        # Print summary of error types
                        self.console.print("[yellow]Error summary:[/yellow]")
                        summary_table = Table(title="Error Types Summary")
                        summary_table.add_column("Error Type", style="cyan")
                        summary_table.add_column("Count", style="magenta")
                        summary_table.add_column("Description", style="green")
                        
                        error_descriptions = {
                            'json_decode': "JSON syntax errors in file",
                            'encoding': "File encoding issues",
                            'not_found': "Files not found",
                            'permission': "Permission denied",
                            'missing_fields': "Missing person or year information",
                            'exists': "Files already exist (use --overwrite to replace)",
                            'unexpected': "Unexpected errors",
                            'unknown': "Unknown error types"
                        }
                        
                        for error_type, errors in sorted(error_types.items(), key=lambda x: len(x[1]), reverse=True):
                            description = error_descriptions.get(error_type, "Miscellaneous errors")
                            summary_table.add_row(error_type, str(len(errors)), description)
                            
                        self.console.print(summary_table)
                        
                        # Show examples of each error type
                        self.console.print("[yellow]Error examples by type:[/yellow]")
                        
                        for error_type, errors in error_types.items():
                            type_table = Table(title=f"{error_type} Errors (showing {min(3, len(errors))} of {len(errors)})")
                            type_table.add_column("File", style="cyan")
                            type_table.add_column("Error", style="red")
                            
                            # Show at most 3 examples of each error type
                            for error in errors[:min(3, len(errors))]:
                                type_table.add_row(os.path.basename(error['file']), error['error'])
                                
                            self.console.print(type_table)
                        
                        # Show detailed errors if verbose
                        if args.verbose:
                            self.console.print("[yellow]Detailed error listing:[/yellow]")
                            all_errors_table = Table(title="All Errors")
                            all_errors_table.add_column("File", style="cyan")
                            all_errors_table.add_column("Error", style="red")
                            
                            for error in results['error_details']:
                                all_errors_table.add_row(error['file'], error['error'])
                                
                            self.console.print(all_errors_table)
                        else:
                            self.console.print(f"[yellow]Use --verbose to see all {len(results['error_details'])} detailed errors.[/yellow]")
                        
                        # Create a report file with all errors
                        # Use custom error report file if specified
                        if args.error_report or len(results['error_details']) > 10:
                            error_file = args.error_report if hasattr(args, "error_report") and args.error_report else f"import_errors_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                            
                            with open(error_file, 'w') as f:
                                f.write(f"Import errors report - {datetime.datetime.now()}\n")
                                f.write(f"Directory: {args.directory}\n")
                                f.write(f"Pattern: {args.pattern or '*.json'}\n\n")
                                
                                # Write summary
                                f.write("ERROR SUMMARY\n")
                                f.write("============\n\n")
                                for error_type, errors in error_types.items():
                                    description = error_descriptions.get(error_type, "Miscellaneous errors")
                                    f.write(f"{error_type}: {len(errors)} errors - {description}\n")
                                f.write("\n\n")
                                
                                # Write details grouped by type
                                f.write("DETAILED ERRORS BY TYPE\n")
                                f.write("======================\n\n")
                                for error_type, errors in error_types.items():
                                    f.write(f"## {error_type} Errors ({len(errors)} total)\n\n")
                                    for i, error in enumerate(errors, 1):
                                        f.write(f"{i}. File: {error['file']}\n   Error: {error['error']}\n\n")
                                    f.write("\n")
                                    
                                self.console.print(f"[green]Full error report saved to {error_file}[/green]")
                
                else:
                    self.console.print("[red]Error: Either --file or --directory must be specified for import operation[/red]")
            
            elif args.operation == "backup":
                # Create backup
                self.console.print("[bold]Creating backup...[/bold]")
                output_dir = args.output_directory if args.output_directory else self.output_directory
                backup_path = pipeline.create_backup(output_dir)
                self.console.print(f"[green]Backup created at: {backup_path}[/green]")
                
            elif args.operation == "export":
                # Export raw data
                if args.output:
                    output_file = args.output
                else:
                    # Use default output file in output directory
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = os.path.join(self.output_directory, f"data_export_{timestamp}.json")
                    
                self.console.print(f"[bold]Exporting data to {output_file}...[/bold]")
                result = pipeline.export_raw_data(output_file)
                
                if result.get('success', False):
                    self.console.print(f"[green]Data exported to: {output_file} ({result['file_count']} files)[/green]")
                else:
                    error = result.get('error', 'Unknown error')
                    self.console.print(f"[red]Failed to export data: {error}[/red]")
                
            elif args.operation == "fix":
                # Fix all data
                self.console.print("[bold]Fixing all data files...[/bold]")
                results = pipeline.fix_all_data(parallel=not args.sequential)
                self.console.print(f"[green]Fixed {results['fixed']} files, {results['unfixed']} were already valid[/green]")
                
                if results["errors"] > 0:
                    self.console.print(f"[yellow]Warning: {results['errors']} files had errors during processing[/yellow]")
            
            else:
                self.console.print(f"[red]Unknown pipeline operation: {args.operation}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Error in pipeline operation: {str(e)}[/red]")


def main():
    """Main CLI entry point"""
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main() 