#!/usr/bin/env python3
"""
Visualization Examples
This script demonstrates how to use the visualization module to create
different types of charts and reports.

Features demonstrated:
- Radar charts for multi-dimensional comparisons
- Heatmaps for visualizing data matrices
- Interactive HTML reports with charts and tables
- Customization options for all visualizations

Run this script to generate sample visualizations in the output/ directory.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from visualization import Visualization, ChartConfig

def main():
    """Main function to demonstrate visualizations"""
    # Create output directory
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)
    
    # Initialize visualization module
    viz = Visualization(output_dir=None)  # Don't set this, we'll handle paths manually
    
    # Example 1: Generate a radar chart
    # 
    # Radar charts are perfect for comparing multiple dimensions/categories
    # between different entities (e.g., person vs. team average)
    print("Generating radar chart...")
    radar_data = {
        "categories": ["Leadership", "Communication", "Innovation", "Teamwork", "Technical Skills", "Delivery"],
        "series": {
            "Person A": [4.2, 3.8, 4.5, 4.0, 4.7, 3.9],
            "Team Average": [3.9, 3.7, 3.5, 4.2, 4.0, 3.8]
        }
    }
    
    radar_path = str(output_dir / "radar_example.png")
    viz.generate_radar_chart(
        data=radar_data,
        title="Performance Comparison",
        output_path=radar_path
    )
    print(f"Radar chart saved to {radar_path}")
    
    # Example 2: Generate a heatmap
    #
    # Heatmaps are useful for visualizing data in matrix form with color intensity
    # indicating the value magnitude (e.g., scores across multiple criteria)
    print("\nGenerating heatmap...")
    
    # Create sample data
    people = ["Person A", "Person B", "Person C", "Person D", "Person E"]
    criteria = ["Criterion 1", "Criterion 2", "Criterion 3", "Criterion 4"]
    
    # Create random scores
    np.random.seed(42)  # For reproducibility
    data = []
    
    for person in people:
        for criterion in criteria:
            score = round(np.random.uniform(1, 5), 1)
            data.append({
                "Person": person,
                "Criterion": criterion,
                "Score": score
            })
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Generate heatmap
    heatmap_path = str(output_dir / "heatmap_example.png")
    viz.generate_heatmap(
        data=df,
        x_col="Criterion",
        y_col="Person",
        value_col="Score",
        title="Evaluation Heatmap",
        output_path=heatmap_path
    )
    print(f"Heatmap saved to {heatmap_path}")
    
    # Example 3: Generate an interactive HTML report
    #
    # Interactive HTML reports combine charts and tables in a single view
    # that can be viewed in any web browser without additional software
    print("\nGenerating interactive HTML report...")
    
    # Prepare data for interactive report
    interactive_data = {
        "title": "Team Performance Report",
        "summary": {
            "Team Size": len(people),
            "Evaluation Period": "Q2 2023",
            "Average Score": round(df["Score"].mean(), 2)
        },
        "chartType": "bar",
        "labels": people,
        "datasets": [{
            "label": "Average Score",
            "data": [df[df["Person"] == person]["Score"].mean() for person in people],
            "backgroundColor": [
                "#4a6fa5", "#6fb26f", "#d9834f", "#9b59b6", "#f1c40f"
            ]
        }],
        "tableData": [
            {
                "Name": person,
                "Average Score": round(df[df["Person"] == person]["Score"].mean(), 2),
                "Highest Score": round(df[df["Person"] == person]["Score"].max(), 2),
                "Lowest Score": round(df[df["Person"] == person]["Score"].min(), 2)
            }
            for person in people
        ]
    }
    
    # Generate interactive report
    html_path = str(output_dir / "interactive_example.html")
    viz.generate_interactive_html(
        data=interactive_data,
        output_path=html_path
    )
    print(f"Interactive HTML report saved to {html_path}")
    
    print("\nAll examples completed!")
    print("Open the output files to see the visualization results.")
    print("For more examples with real evaluation data, run 'python examples/evaluation_visualization.py data'")

if __name__ == "__main__":
    main() 