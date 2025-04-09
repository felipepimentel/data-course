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
        pipeline_parser.add_argument("--output-dir", help="Output directory for backup")
        
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
            
            # Check if year exists
            if year not in self.available_years:
                self.console.print(f"[red]Year {year} not found in the database[/red]")
                return
                
            # Generate comparative report
            with Progress(
                SpinnerColumn(),
                *Progress.get_default_columns(),
                transient=True
            ) as progress:
                task = progress.add_task(f"[green]Generating comparative report for {year}...", total=1)
                
                # Generate report
                df = self.analyzer.generate_comparative_report(year)
                progress.update(task, completed=1)
                
            if df is None or df.empty:
                self.console.print(f"[yellow]No data available for year {year}[/yellow]")
                return
                
            # Display results
            table = Table(title=f"Comparative Analysis - {year}")
            table.add_column("Person", style="cyan")
            table.add_column("Concept", style="green")
            table.add_column("Score", style="blue")
            table.add_column("Group Avg", style="blue")
            table.add_column("Diff", style="yellow")
            
            for _, row in df.iterrows():
                diff = row['Difference']
                diff_style = "green" if diff >= 0 else "red"
                
                table.add_row(
                    row['Person'],
                    row['Overall Concept'],
                    f"{row['Average Score']:.2f}",
                    f"{row['Group Average']:.2f}",
                    f"[{diff_style}]{diff:.2f}[/{diff_style}]"
                )
                
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
                
        except Exception as e:
            self.console.print(f"[red]Error generating comparative report: {str(e)}[/red]")
    
    def handle_historical(self, args):
        """Handle the historical command"""
        try:
            person = args.person
            years_filter = args.years
            
            # Check if person exists
            if person not in self.available_people:
                self.console.print(f"[red]Person '{person}' not found in the database[/red]")
                return
                
            # Generate historical report
            with Progress(
                SpinnerColumn(),
                *Progress.get_default_columns(),
                transient=True
            ) as progress:
                task = progress.add_task(f"[green]Generating historical report for {person}...", total=1)
                
                # Generate report
                data = self.analyzer.person_year_over_year(person)
                progress.update(task, completed=1)
                
            if not data or not data.get("years"):
                self.console.print(f"[yellow]No data available for {person}[/yellow]")
                return
                
            # Filter by years if specified
            if years_filter:
                data["years"] = [y for y in data["years"] if y in years_filter]
                if not data["years"]:
                    self.console.print(f"[yellow]No data available for {person} in the specified years[/yellow]")
                    return
                    
            # Display results
            table = Table(title=f"Historical Analysis - {person}")
            table.add_column("Year", style="cyan")
            table.add_column("Concept", style="green")
            table.add_column("Score", style="blue")
            table.add_column("Group Avg", style="blue")
            table.add_column("Diff", style="yellow")
            
            for year in data["years"]:
                concept = data["concepts"].get(year, "Unknown")
                score = data["year_scores"].get(year, 0)
                group_score = data["year_group_scores"].get(year, 0)
                diff = score - group_score
                diff_style = "green" if diff >= 0 else "red"
                
                table.add_row(
                    year,
                    concept,
                    f"{score:.2f}",
                    f"{group_score:.2f}",
                    f"[{diff_style}]{diff:.2f}[/{diff_style}]"
                )
                
            self.console.print(table)
            
            # Display improvement information
            if len(data["years"]) >= 2:
                first_year = data["years"][0]
                last_year = data["years"][-1]
                improvement = data["improvement"]
                
                color = "green" if improvement >= 0 else "red"
                self.console.print(f"\nImprovement from {first_year} to {last_year}: [{color}]{improvement:.2f}[/{color}]")
                
                relative = data["relative_improvement"] * 100
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
                
        except Exception as e:
            self.console.print(f"[red]Error generating historical report: {str(e)}[/red]")
    
    def handle_validate(self, args):
        """Handle the validate command"""
        # Placeholder for validation implementation
        self.console.print("[yellow]Validation feature not yet implemented[/yellow]")
    
    def handle_export(self, args):
        """Handle the export command"""
        # Placeholder for export implementation
        self.console.print("[yellow]Export feature not yet implemented[/yellow]")
    
    def handle_filter(self, args):
        """Handle the filter command"""
        # Placeholder for filter implementation
        self.console.print("[yellow]Filter feature not yet implemented[/yellow]")
    
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
                # Import data from files
                if args.file:
                    # Single file import
                    self.console.print(f"[bold]Importing file {args.file}...[/bold]")
                    success = pipeline.ingest_file(
                        args.file,
                        args.year if hasattr(args, "year") else None,
                        args.person if hasattr(args, "person") else None,
                        overwrite=args.overwrite
                    )
                    
                    if success and success.get('success', False):
                        self.console.print(f"[green]Successfully imported file: {args.file}[/green]")
                    else:
                        error = success.get('error', 'Unknown error')
                        self.console.print(f"[red]Failed to import file: {args.file} - {error}[/red]")
                        
                elif args.directory:
                    # Directory import
                    self.console.print(f"[bold]Importing files from {args.directory}...[/bold]")
                    results = pipeline.ingest_directory(
                        args.directory,
                        pattern=args.pattern or "*.json",
                        overwrite=args.overwrite,
                        parallel=not args.sequential
                    )
                    
                    self.console.print(f"[green]Import completed: {results['success']} succeeded, {results['failed']} failed[/green]")
                    
                else:
                    self.console.print("[red]Error: Either --file or --directory must be specified for import operation[/red]")
            
            elif args.operation == "backup":
                # Create backup
                self.console.print("[bold]Creating backup...[/bold]")
                backup_path = pipeline.create_backup(args.output_dir)
                self.console.print(f"[green]Backup created at: {backup_path}[/green]")
                
            elif args.operation == "export":
                # Export raw data
                if not args.output:
                    self.console.print("[red]Error: --output parameter is required for export operation[/red]")
                    return
                    
                self.console.print(f"[bold]Exporting data to {args.output}...[/bold]")
                result = pipeline.export_raw_data(args.output)
                
                if result.get('success', False):
                    self.console.print(f"[green]Data exported to: {args.output} ({result['file_count']} files)[/green]")
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