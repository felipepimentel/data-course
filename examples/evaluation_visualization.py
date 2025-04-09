#!/usr/bin/env python3
"""
Evaluation Visualization Example
This script demonstrates how to use the visualization module with
evaluation data from the EvaluationAnalyzer.

Features demonstrated:
- Loading and processing real evaluation data
- Generating radar charts to compare performance with group averages
- Creating heatmaps to visualize behavior scores across evaluators
- Building interactive HTML reports with summary statistics and tables
- Comparing performance across multiple team members

Usage:
python examples/evaluation_visualization.py [data_path]

Where [data_path] is the directory containing evaluation data (defaults to ".")
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from visualization import Visualization, ChartConfig
from evaluation_analyzer import EvaluationAnalyzer
from rich.console import Console

# Create rich console for formatted output
console = Console()

def generate_person_report(analyzer, person, year, output_dir):
    """Generate visualization report for a person
    
    This function creates three types of visualizations:
    1. Radar chart comparing person's scores with group averages
    2. Heatmap showing behavior scores from different evaluators
    3. Interactive HTML report with summary data and tables
    
    Args:
        analyzer: The EvaluationAnalyzer instance
        person: Name of the person to analyze
        year: Year to analyze
        output_dir: Directory to save output files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    viz = Visualization()
    
    console.print(f"[bold]Generating report for {person} ({year})[/bold]")
    
    # 1. Get evaluation data
    evaluations = analyzer.get_evaluations_for_person(person, year)
    if not evaluations:
        console.print(f"[red]No data found for {person} in {year}[/red]")
        return
    
    # 2. Generate radar chart of behavior scores
    console.print("Generating radar chart...")
    behavior_scores = analyzer.get_behavior_scores(person, year)
    
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
        radar_data = {
            "categories": categories,
            "series": {
                person: person_scores,
                "Grupo": group_scores
            }
        }
        
        radar_path = str(output_dir / f"{person}_{year}_radar.png")
        viz.generate_radar_chart(
            data=radar_data,
            title=f"Performance Comparison - {person} ({year})",
            output_path=radar_path
        )
        console.print(f"[green]Radar chart saved to {radar_path}[/green]")
    
    # 3. Generate heatmap of individual behaviors
    console.print("Generating behavior heatmap...")
    
    # Extract behavior scores
    heatmap_data = []
    
    for dir_name, behaviors in behavior_scores.items():
        for comp_name, details in behaviors.items():
            for avaliador, scores in details.get("scores", {}).items():
                if avaliador != "%todos":  # Use individual evaluations
                    heatmap_data.append({
                        "Direcionador": dir_name,
                        "Comportamento": comp_name,
                        "Avaliador": avaliador,
                        "Score": scores.get("score_colaborador", 0)
                    })
    
    if heatmap_data:
        df = pd.DataFrame(heatmap_data)
        
        heatmap_path = str(output_dir / f"{person}_{year}_heatmap.png")
        viz.generate_heatmap(
            data=df,
            x_col="Comportamento",
            y_col="Avaliador",
            value_col="Score",
            title=f"Behavior Scores - {person} ({year})",
            output_path=heatmap_path
        )
        console.print(f"[green]Heatmap saved to {heatmap_path}[/green]")
    
    # 4. Generate interactive HTML report
    console.print("Generating interactive report...")
    
    # Get historical data
    years = analyzer.get_years_for_person(person)
    historical_data = []
    
    for y in sorted(years):
        avg_score = analyzer.get_average_score(person, y)
        if avg_score is not None:
            historical_data.append({
                "Year": y,
                "Score": avg_score
            })
    
    historical_df = pd.DataFrame(historical_data) if historical_data else None
    
    # Current year scores by category
    category_scores = []
    for dir_name, behaviors in behavior_scores.items():
        scores = []
        for comp_name, details in behaviors.items():
            for avaliador, score_data in details.get("scores", {}).items():
                if avaliador == "%todos":
                    scores.append(score_data.get("score_colaborador", 0))
        
        if scores:
            category_scores.append({
                "Category": dir_name.split(".")[0],
                "Score": sum(scores) / len(scores)
            })
    
    category_df = pd.DataFrame(category_scores) if category_scores else None
    
    # Prepare interactive data
    interactive_data = {
        "title": f"Performance Report - {person} ({year})",
        "summary": {
            "Person": person,
            "Year": year,
            "Average Score": analyzer.get_average_score(person, year) or "N/A",
            "Years Evaluated": ", ".join(sorted(years))
        },
        "chartType": "bar",
        "labels": [item["Category"] for item in category_scores] if category_scores else [],
        "datasets": [{
            "label": "Category Scores",
            "data": [item["Score"] for item in category_scores] if category_scores else [],
            "backgroundColor": "#4a6fa5"
        }],
        "tableData": heatmap_data
    }
    
    html_path = str(output_dir / f"{person}_{year}_report.html")
    viz.generate_interactive_html(
        data=interactive_data,
        output_path=html_path
    )
    console.print(f"[green]Interactive report saved to {html_path}[/green]")

def generate_comparison_report(analyzer, people, year, output_dir):
    """Generate comparison report for multiple people
    
    This function creates two types of visualizations:
    1. Heatmap comparing performance across different criteria
    2. Interactive HTML report with rankings and summary statistics
    
    Args:
        analyzer: The EvaluationAnalyzer instance
        people: List of people to compare
        year: Year to analyze
        output_dir: Directory to save output files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    viz = Visualization()
    
    console.print(f"[bold]Generating comparison report for {year}[/bold]")
    
    # Collect data for all people
    comparison_data = []
    for person in people:
        avg_score = analyzer.get_average_score(person, year)
        if avg_score is not None:
            comparison_data.append({
                "Person": person,
                "Score": avg_score
            })
    
    if not comparison_data:
        console.print("[red]No data found for comparison[/red]")
        return
    
    # Create comparison heatmap
    console.print("Generating comparison heatmap...")
    
    # Get criteria for selected year
    criteria = analyzer.get_criteria_for_year(year)
    
    if criteria:
        all_criteria = []
        for year_criteria in criteria.values():
            all_criteria.extend(year_criteria)
        all_criteria = list(set(all_criteria))
        
        # Collect scores for each person and criterion
        heatmap_data = []
        for person in people:
            for criterion in all_criteria:
                score = analyzer.get_score_for_criterion(person, year, criterion)
                if score is not None:
                    heatmap_data.append({
                        "Person": person,
                        "Criterion": criterion,
                        "Score": score
                    })
        
        if heatmap_data:
            df = pd.DataFrame(heatmap_data)
            
            heatmap_path = str(output_dir / f"comparison_{year}_heatmap.png")
            viz.generate_heatmap(
                data=df,
                x_col="Criterion",
                y_col="Person", 
                value_col="Score",
                title=f"Performance Comparison ({year})",
                output_path=heatmap_path
            )
            console.print(f"[green]Comparison heatmap saved to {heatmap_path}[/green]")
    
    # Create interactive comparison report
    console.print("Generating interactive comparison report...")
    
    comparison_df = pd.DataFrame(comparison_data)
    comparison_df = comparison_df.sort_values(by="Score", ascending=False)
    
    interactive_data = {
        "title": f"Team Performance Comparison ({year})",
        "summary": {
            "Year": year,
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
    
    html_path = str(output_dir / f"comparison_{year}_report.html")
    viz.generate_interactive_html(
        data=interactive_data,
        output_path=html_path
    )
    console.print(f"[green]Interactive comparison report saved to {html_path}[/green]")

def main():
    """Main function to demonstrate visualizations with evaluation data"""
    # Get base path from command line or use default
    base_path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # Initialize analyzer
    analyzer = EvaluationAnalyzer(base_path)
    console.print(f"[bold]Loading evaluation data from {base_path}[/bold]")
    
    # Create output directory
    output_dir = Path("./output/evaluation_reports")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Get list of people and years
    all_people = analyzer.get_all_people()
    all_years = analyzer.get_all_years()
    
    if not all_people or not all_years:
        console.print("[red]No evaluation data found[/red]")
        return
    
    console.print(f"Found {len(all_people)} people and {len(all_years)} years of data")
    
    # Generate individual reports
    if all_people and all_years:
        # Use the latest person and year for the example
        person = all_people[0]
        year = max(all_years)
        
        generate_person_report(analyzer, person, year, output_dir / "individual")
    
    # Generate comparison report if multiple people
    if len(all_people) > 1 and all_years:
        # Use up to 5 people for the example
        people = all_people[:5]
        year = max(all_years)
        
        generate_comparison_report(analyzer, people, year, output_dir / "comparison")
    
    console.print("[bold green]All reports generated successfully![/bold green]")
    console.print("\nTo view the reports, navigate to the output directory:")
    console.print(f"- Individual report: {output_dir}/individual/")
    console.print(f"- Comparison report: {output_dir}/comparison/")

if __name__ == "__main__":
    main() 