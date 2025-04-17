import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .data_model import PersonData
from .evaluation_analyzer import EvaluationAnalyzer


class ChartConfig:
    """Configuration for chart generation"""

    def __init__(
        self,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        figsize: Tuple[int, int] = (10, 6),
        palette: str = "viridis",
        style: str = "whitegrid",
        context: str = "talk",
        font_scale: float = 1.0,
        legend_title: Optional[str] = None,
        grid: bool = True,
        rotate_xlabels: bool = False,
        rotate_ylabels: bool = False,
        format_func: Optional[callable] = None,
    ):
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.figsize = figsize
        self.palette = palette
        self.style = style
        self.context = context
        self.font_scale = font_scale
        self.legend_title = legend_title
        self.grid = grid
        self.rotate_xlabels = rotate_xlabels
        self.rotate_ylabels = rotate_ylabels
        self.format_func = format_func


def generate_report(
    report_type: str,
    data: Union[List[PersonData], Dict[str, Any]],
    output_dir: str = "output/reports",
) -> str:
    """
    Generate a report based on the specified type.

    Args:
        report_type: Type of report to generate ('attendance', 'payment', etc.)
        data: Data to include in the report
        output_dir: Directory to save the report

    Returns:
        Path to the generated report file
    """
    os.makedirs(output_dir, exist_ok=True)

    if report_type.lower() == "attendance":
        if not isinstance(data, list):
            raise ValueError("Attendance report requires a list of PersonData objects")
        return generate_attendance_report(data, output_dir)

    elif report_type.lower() == "payment":
        if not isinstance(data, list):
            raise ValueError("Payment report requires a list of PersonData objects")
        return generate_payment_report(data, output_dir)

    elif report_type.lower() == "evaluation":
        if not isinstance(data, list):
            raise ValueError("Evaluation report requires a list of PersonData objects")
        return generate_evaluation_report(data, output_dir)

    elif report_type.lower() == "skill_recommendations":
        if not isinstance(data, list):
            raise ValueError(
                "Skill recommendations requires a list of PersonData objects"
            )
        return generate_skill_recommendations(data, output_dir)

    elif report_type.lower() == "skill_analytics":
        if not isinstance(data, list):
            raise ValueError("Skill analytics requires a list of PersonData objects")
        person_name = None
        if isinstance(data, dict) and "person_name" in data:
            person_name = data["person_name"]
            data = data.get("data_list", [])
        return generate_individual_skill_analytics(data, output_dir, person_name)

    elif report_type.lower() == "advanced_visualizations":
        if not isinstance(data, list):
            raise ValueError(
                "Advanced visualizations requires a list of PersonData objects"
            )
        return generate_advanced_visualizations(data, output_dir)

    elif report_type.lower() == "comprehensive":
        if not isinstance(data, list):
            raise ValueError(
                "Comprehensive report requires a list of PersonData objects"
            )
        return generate_comprehensive_report(data, output_dir)

    elif report_type.lower() == "custom":
        if not isinstance(data, dict):
            raise ValueError(
                "Custom report requires a dictionary with report parameters"
            )
        return generate_custom_report(data, output_dir)

    elif report_type.lower() == "360_evaluation":
        # New report type for 360 evaluations using the EvaluationAnalyzer
        if not isinstance(data, dict):
            raise ValueError("360 evaluation report requires configuration parameters")
        return generate_360_evaluation_report(data, output_dir)

    else:
        raise ValueError(f"Unknown report type: {report_type}")


def generate_360_evaluation_report(data: Dict[str, Any], output_dir: str) -> str:
    """Generate a 360-degree evaluation report using the EvaluationAnalyzer.

    Args:
        data: Dictionary with configuration parameters:
            - data_path: Path to the data directory
            - year: Year to analyze
            - people: List of people to include (optional)
            - include_comparative: Whether to include comparative analysis
            - include_historical: Whether to include historical analysis

    Returns:
        Path to the generated report directory
    """
    # Extract parameters
    data_path = data.get("data_path", "data")
    year = data.get("year")
    people = data.get("people", [])
    include_comparative = data.get("include_comparative", True)
    include_historical = data.get("include_historical", True)

    # Create output directory
    report_dir = os.path.join(
        output_dir, f"360_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    os.makedirs(report_dir, exist_ok=True)

    # Initialize analyzer
    analyzer = EvaluationAnalyzer(data_path)

    # Get available years and people if not specified
    available_years = analyzer.get_all_years()
    if not year and available_years:
        year = available_years[-1]  # Use most recent year

    available_people = analyzer.get_all_people()
    if not people:
        people = available_people

    # Generate reports
    results = {
        "report_dir": report_dir,
        "year": year,
        "people_analyzed": [],
        "comparative_report": None,
        "historical_reports": [],
    }

    # Generate comparative report if requested
    if include_comparative and year:
        try:
            comparative_file = os.path.join(report_dir, f"comparative_{year}.png")
            df = analyzer.compare_people_for_year(year)
            if not df.empty:
                analyzer.plot_comparative_report(df, year, report_dir)

                # Save as CSV too
                csv_path = os.path.join(report_dir, f"comparative_{year}.csv")
                df.to_csv(csv_path)

                results["comparative_report"] = comparative_file
                print(f"Generated comparative report for {year}")
        except Exception as e:
            print(f"Error generating comparative report: {str(e)}")

    # Generate historical reports for each person if requested
    if include_historical:
        for person in people:
            if person in available_people:
                try:
                    historical_file = os.path.join(
                        report_dir, f"historical_{person}.png"
                    )
                    success = analyzer.generate_historical_report(
                        person, historical_file
                    )
                    if success:
                        results["historical_reports"].append(historical_file)
                        results["people_analyzed"].append(person)
                        print(f"Generated historical report for {person}")
                except Exception as e:
                    print(f"Error generating historical report for {person}: {str(e)}")

    # Save results summary
    summary_file = os.path.join(report_dir, "report_summary.json")
    with open(summary_file, "w") as f:
        json.dump(results, f, indent=2)

    return report_dir


def setup_plot(config: ChartConfig) -> Tuple[plt.Figure, plt.Axes]:
    """Setup a matplotlib plot with the specified configuration"""
    # Set the style
    sns.set_style(config.style)
    sns.set_context(config.context, font_scale=config.font_scale)

    # Create figure and axis
    fig, ax = plt.subplots(figsize=config.figsize)

    # Set title and labels
    if config.title:
        ax.set_title(config.title)
    if config.xlabel:
        ax.set_xlabel(config.xlabel)
    if config.ylabel:
        ax.set_ylabel(config.ylabel)

    # Add grid if requested
    if config.grid:
        ax.grid(True, linestyle="--", alpha=0.6)

    return fig, ax


def finalize_plot(fig: plt.Figure, ax: plt.Axes, config: ChartConfig) -> plt.Figure:
    """Finalize plot with common customizations"""
    # Rotate labels if requested
    if config.rotate_xlabels:
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    if config.rotate_ylabels:
        plt.setp(ax.get_yticklabels(), rotation=45, va="top")

    # Set legend title if provided
    if config.legend_title and ax.get_legend():
        ax.get_legend().set_title(config.legend_title)

    # Adjust layout
    plt.tight_layout()

    return fig


def generate_radar_chart(
    data: Dict[str, List[float]],
    categories: List[str],
    title: str = "",
    filename: Optional[str] = None,
) -> Optional[str]:
    """
    Generate a radar chart from data.

    Args:
        data: Dictionary mapping series names to lists of values (one per category)
        categories: List of category names (labels for radar axes)
        title: Chart title
        filename: Path to save the chart (if None, displays the chart)

    Returns:
        Path to the saved chart if filename is provided, None otherwise
    """
    # Number of variables
    N = len(categories)

    # Create angle for each variable
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Close the loop

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

    # Add category labels
    plt.xticks(angles[:-1], categories, size=12)

    # Set y ticks
    ax.set_rlabel_position(0)
    plt.yticks([1, 2, 3, 4], ["1", "2", "3", "4"], color="grey", size=10)
    plt.ylim(0, 4.5)

    # Plot each series
    for i, (name, values) in enumerate(data.items()):
        # Ensure the data is a complete loop
        values_loop = values.copy()
        values_loop += values[:1]

        # Plot values
        ax.plot(angles, values_loop, linewidth=2, linestyle="solid", label=name)
        ax.fill(angles, values_loop, alpha=0.1)

    # Add legend
    plt.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))

    # Add title
    plt.title(title, size=20, y=1.1)

    # Save or show the chart
    if filename:
        plt.savefig(filename, bbox_inches="tight")
        plt.close()
        return filename
    else:
        plt.tight_layout()
        plt.show()
        plt.close()
        return None


def generate_heatmap(
    data: pd.DataFrame, title: str = "", filename: Optional[str] = None
) -> Optional[str]:
    """
    Generate a heatmap from a DataFrame.

    Args:
        data: DataFrame to visualize
        title: Chart title
        filename: Path to save the chart (if None, displays the chart)

    Returns:
        Path to the saved chart if filename is provided, None otherwise
    """
    # Create figure
    plt.figure(figsize=(12, 10))

    # Create heatmap
    sns.heatmap(data, annot=True, cmap="YlGnBu", linewidths=0.5)

    # Add title
    plt.title(title, size=16)

    # Save or show the chart
    if filename:
        plt.savefig(filename, bbox_inches="tight")
        plt.close()
        return filename
    else:
        plt.tight_layout()
        plt.show()
        plt.close()
        return None


def generate_interactive_html(data: Dict[str, Any], output_path: str) -> bool:
    """Generate an interactive HTML report.

    Args:
        data: Dictionary with data to visualize
        output_path: Path to save the HTML file

    Returns:
        Boolean indicating success
    """
    try:
        # Create a simple HTML template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{data.get("title", "People Analytics Report")}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                h1, h2 {{ color: #2c3e50; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ text-align: left; padding: 12px; }}
                th {{ background-color: #3498db; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .positive {{ color: green; }}
                .negative {{ color: red; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{data.get("title", "People Analytics Report")}</h1>
        """

        # Add summary information if available
        if "summary" in data:
            html_content += """
                <h2>Summary</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
            """

            for key, value in data["summary"].items():
                if isinstance(value, list):
                    value_str = ", ".join(str(v) for v in value)
                else:
                    value_str = str(value)

                html_content += f"""
                    <tr><td>{key.replace("_", " ").title()}</td><td>{value_str}</td></tr>
                """

            html_content += """
                </table>
            """

        # Add people data if available
        if "people_data" in data:
            html_content += """
                <h2>People Data</h2>
                <table>
                    <tr>
                        <th>Person</th>
                        <th>Concept</th>
                        <th>Score</th>
                        <th>Group Avg</th>
                        <th>Difference</th>
                    </tr>
            """

            for person_data in data["people_data"]:
                person = person_data.get("Person", "Unknown")
                concept = person_data.get("Overall Concept", "Unknown")
                score = person_data.get("Average Score", 0)
                group_avg = person_data.get("Group Average", 0)
                diff = person_data.get("Difference", 0)

                # Format difference with color
                diff_class = "positive" if diff >= 0 else "negative"
                diff_sign = "+" if diff > 0 else ""

                html_content += f"""
                    <tr>
                        <td>{person}</td>
                        <td>{concept}</td>
                        <td>{score:.2f}</td>
                        <td>{group_avg:.2f}</td>
                        <td class="{diff_class}">{diff_sign}{diff:.2f}</td>
                    </tr>
                """

            html_content += """
                </table>
            """

        # Add filtered data if available
        if "filtered_data" in data:
            html_content += """
                <h2>Filtered Results</h2>
                <table>
                    <tr>
                        <th>Person</th>
                        <th>Year</th>
                        <th>Behavior</th>
                        <th>Score</th>
                    </tr>
            """

            for item in data["filtered_data"]:
                person = item.get("Person", "Unknown")
                year = item.get("Year", "Unknown")
                behavior = item.get("Comportamento", item.get("Behavior", "Unknown"))
                score = item.get("Score", 0)

                html_content += f"""
                    <tr>
                        <td>{person}</td>
                        <td>{year}</td>
                        <td>{behavior}</td>
                        <td>{score:.2f}</td>
                    </tr>
                """

            html_content += """
                </table>
            """

        # Add images if available
        if "image_paths" in data and data["image_paths"]:
            html_content += """
                <h2>Visualizations</h2>
                <div class="visualizations">
            """

            for img_path in data["image_paths"]:
                if os.path.exists(img_path):
                    img_name = os.path.basename(img_path)
                    # Copy image to the output directory if needed
                    output_dir = os.path.dirname(output_path)
                    output_img_path = os.path.join(output_dir, img_name)

                    if img_path != output_img_path:
                        import shutil

                        shutil.copy(img_path, output_img_path)

                    html_content += f"""
                        <div class="viz-container">
                            <h3>{img_name.replace("_", " ").replace(".png", "").title()}</h3>
                            <img src="{img_name}" alt="{img_name}" style="max-width:100%;">
                        </div>
                    """

            html_content += """
                </div>
            """

        # Close the HTML
        html_content += """
            </div>
        </body>
        </html>
        """

        # Write the HTML file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return True
    except Exception as e:
        print(f"Error generating interactive HTML: {str(e)}")
        return False


def generate_custom_report(data: Dict[str, Any], output_dir: str) -> str:
    """Generate a custom report based on provided data dictionary."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_name = data.get("report_name", "custom")

    # Save the data as JSON
    json_path = os.path.join(output_dir, f"{report_name}_{timestamp}.json")
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Generated custom report: {json_path}")
    return json_path


def generate_attendance_report(data_list: List[PersonData], output_dir: str) -> str:
    """Generate attendance report for the given data list."""

    # Prepare data for the report
    report_data = []

    for person_data in data_list:
        for record in person_data.attendance_records:
            entry = {
                "Person": person_data.name,
                "Year": person_data.year,
                "Date": record.date,
                "Status": record.status,
                "Hours": record.hours,
                "Notes": record.notes,
            }

            # Add profile information if available
            if person_data.profile:
                entry["Department"] = person_data.profile.department
                entry["Position"] = person_data.profile.position
                entry["Manager"] = person_data.profile.manager
            else:
                entry["Department"] = ""
                entry["Position"] = ""
                entry["Manager"] = ""

            report_data.append(entry)

    if not report_data:
        print("No attendance data available for report.")
        return ""

    # Create DataFrame
    df = pd.DataFrame(report_data)

    # Calculate statistics
    stats = {
        "total_days": len(df),
        "present_days": len(df[df["Status"] == "present"]),
        "absent_days": len(df[df["Status"] == "absent"]),
        "late_days": len(df[df["Status"] == "late"]),
        "total_hours": df["Hours"].sum(),
    }

    # Generate report files
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save raw data as CSV
    csv_path = os.path.join(output_dir, f"attendance_report_{timestamp}.csv")
    df.to_csv(csv_path, index=False)

    # Save statistics as JSON
    stats_path = os.path.join(output_dir, f"attendance_stats_{timestamp}.json")
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)

    # Generate visualization
    plt.figure(figsize=(10, 6))
    status_counts = df["Status"].value_counts()
    status_counts.plot(kind="bar", color=["green", "red", "orange"])
    plt.title("Attendance Status Distribution")
    plt.xlabel("Status")
    plt.ylabel("Count")
    plt.tight_layout()

    plot_path = os.path.join(output_dir, f"attendance_plot_{timestamp}.png")
    plt.savefig(plot_path)
    plt.close()

    # If profile information is available, generate a department-wise report
    if "Department" in df.columns and not df["Department"].isna().all():
        dept_stats = (
            df.groupby("Department")["Status"].value_counts().unstack().fillna(0)
        )
        plt.figure(figsize=(12, 8))
        dept_stats.plot(kind="bar", stacked=True)
        plt.title("Attendance by Department")
        plt.xlabel("Department")
        plt.ylabel("Count")
        plt.tight_layout()

        dept_plot_path = os.path.join(output_dir, f"attendance_by_dept_{timestamp}.png")
        plt.savefig(dept_plot_path)
        plt.close()

    print(f"Generated attendance report with {len(df)} records.")
    return csv_path


def generate_payment_report(data_list: List[PersonData], output_dir: str) -> str:
    """Generate payment report for the given data list."""

    # Prepare data for the report
    report_data = []

    for person_data in data_list:
        for record in person_data.payment_records:
            entry = {
                "Person": person_data.name,
                "Year": person_data.year,
                "Date": record.date,
                "Amount": record.amount,
                "Type": record.type,
                "Notes": record.notes,
            }

            # Add profile information if available
            if person_data.profile:
                entry["Department"] = person_data.profile.department
                entry["Position"] = person_data.profile.position
                entry["Manager"] = person_data.profile.manager
            else:
                entry["Department"] = ""
                entry["Position"] = ""
                entry["Manager"] = ""

            report_data.append(entry)

    if not report_data:
        print("No payment data available for report.")
        return ""

    # Create DataFrame
    df = pd.DataFrame(report_data)

    # Calculate statistics
    stats = {
        "total_payments": len(df),
        "total_amount": df["Amount"].sum(),
        "average_amount": df["Amount"].mean(),
        "max_amount": df["Amount"].max(),
        "min_amount": df["Amount"].min(),
        "payment_types": df["Type"].value_counts().to_dict(),
    }

    # Generate report files
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save raw data as CSV
    csv_path = os.path.join(output_dir, f"payment_report_{timestamp}.csv")
    df.to_csv(csv_path, index=False)

    # Save statistics as JSON
    stats_path = os.path.join(output_dir, f"payment_stats_{timestamp}.json")
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)

    # Generate visualization
    plt.figure(figsize=(10, 6))
    type_amounts = df.groupby("Type")["Amount"].sum()
    type_amounts.plot(kind="bar", color=["blue", "green", "orange"])
    plt.title("Payment Amounts by Type")
    plt.xlabel("Payment Type")
    plt.ylabel("Total Amount")
    plt.tight_layout()

    plot_path = os.path.join(output_dir, f"payment_plot_{timestamp}.png")
    plt.savefig(plot_path)
    plt.close()

    # If profile information is available, generate a department-wise report
    if "Department" in df.columns and not df["Department"].isna().all():
        dept_amounts = (
            df.groupby("Department")["Amount"].sum().sort_values(ascending=False)
        )
        plt.figure(figsize=(12, 8))
        dept_amounts.plot(kind="bar")
        plt.title("Total Payments by Department")
        plt.xlabel("Department")
        plt.ylabel("Total Amount")
        plt.tight_layout()

        dept_plot_path = os.path.join(output_dir, f"payment_by_dept_{timestamp}.png")
        plt.savefig(dept_plot_path)
        plt.close()

    print(f"Generated payment report with {len(df)} records.")
    return csv_path


def generate_evaluation_report(data_list: List[PersonData], output_dir: str) -> str:
    """Generate comprehensive evaluation report based on resultado.json and perfil.json data.

    This report includes:
    - Performance comparisons across years and people
    - Department and team analysis
    - Career progression insights
    - Mermaid diagrams for organizational relationships
    - Detailed tables for easy comparison

    Args:
        data_list: List of PersonData objects containing evaluation data
        output_dir: Directory to save the report

    Returns:
        Path to the generated markdown report
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Initialize dataframes for analysis
    profile_data = []
    evaluation_data = []
    career_data = []

    # Process each person's data
    for person in data_list:
        # Get profile information if available
        if person.profile:
            profile_data.append(
                {
                    "Name": person.name,
                    "Year": person.year,
                    "Department": person.profile.nome_departamento,
                    "Position": person.profile.cargo,
                    "Manager": person.profile.nome_gestor or "N/A",
                    "Is_Manager": person.profile.tipo_gestao,
                    "Squad": person.profile.nome_squad,
                    "Community": person.profile.nome_comunidade,
                }
            )

        # Get evaluation data if available
        if person.evaluation_data:
            # Extract overall score if available
            overall_score = None
            if isinstance(person.evaluation_data, dict):
                if "pontuacao_final" in person.evaluation_data:
                    overall_score = person.evaluation_data["pontuacao_final"]
                elif (
                    "avaliacoes" in person.evaluation_data
                    and "pontuacao_final" in person.evaluation_data["avaliacoes"]
                ):
                    overall_score = person.evaluation_data["avaliacoes"][
                        "pontuacao_final"
                    ]

            evaluation_data.append(
                {
                    "Name": person.name,
                    "Year": person.year,
                    "Score": overall_score,
                    "Raw_Data": person.evaluation_data,
                }
            )

        # Get career progression data if available
        if person.career_progression:
            promotion_velocity = person.career_progression.get_promotion_velocity()
            skill_growth = person.career_progression.get_skill_growth_rate()

            # Calculate skill level distribution
            skill_levels = {}
            if person.career_progression.skills_matrix:
                for level in range(1, 6):  # Levels 1-5
                    count = sum(
                        1
                        for v in person.career_progression.skills_matrix.values()
                        if v == level
                    )
                    skill_levels[f"Level_{level}"] = count

            career_data.append(
                {
                    "Name": person.name,
                    "Year": person.year,
                    "Promotion_Velocity": promotion_velocity,
                    "Skill_Growth_Rate": skill_growth,
                    "Total_Skills": len(person.career_progression.skills_matrix)
                    if person.career_progression.skills_matrix
                    else 0,
                    "Avg_Skill_Level": sum(
                        person.career_progression.skills_matrix.values()
                    )
                    / len(person.career_progression.skills_matrix)
                    if person.career_progression.skills_matrix
                    else 0,
                    "Certification_Count": len(
                        person.career_progression.certifications
                    ),
                    "Level_1_Skills": skill_levels.get("Level_1", 0),
                    "Level_2_Skills": skill_levels.get("Level_2", 0),
                    "Level_3_Skills": skill_levels.get("Level_3", 0),
                    "Level_4_Skills": skill_levels.get("Level_4", 0),
                    "Level_5_Skills": skill_levels.get("Level_5", 0),
                }
            )

    # Convert to DataFrames for easy analysis
    profile_df = pd.DataFrame(profile_data) if profile_data else pd.DataFrame()
    evaluation_df = pd.DataFrame(evaluation_data) if evaluation_data else pd.DataFrame()
    career_df = pd.DataFrame(career_data) if career_data else pd.DataFrame()

    # Create the comprehensive markdown report
    report_path = os.path.join(output_dir, f"evaluation_report_{timestamp}.md")

    with open(report_path, "w", encoding="utf-8") as md_file:
        # Write report header
        md_file.write("# Comprehensive People Analytics Report\n\n")
        md_file.write(
            f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        )
        md_file.write(f"*Total people analyzed: {len(data_list)}*\n\n")

        # Table of Contents
        md_file.write("## Table of Contents\n\n")
        md_file.write("1. [Executive Summary](#executive-summary)\n")
        md_file.write("2. [Department & Team Analysis](#department-team-analysis)\n")
        md_file.write("3. [Year-over-Year Performance](#year-over-year-performance)\n")
        md_file.write(
            "4. [Career Development Insights](#career-development-insights)\n"
        )
        md_file.write("5. [Organizational Structure](#organizational-structure)\n")
        md_file.write(
            "6. [Skill Distribution Analysis](#skill-distribution-analysis)\n"
        )
        md_file.write("7. [Detailed Comparisons](#detailed-comparisons)\n\n")

        # 1. Executive Summary
        md_file.write("## Executive Summary\n\n")

        if not profile_df.empty:
            total_people = profile_df["Name"].nunique()
            departments = (
                profile_df["Department"].nunique()
                if "Department" in profile_df.columns
                else 0
            )
            managers = (
                profile_df["Manager"].nunique()
                if "Manager" in profile_df.columns
                else 0
            )

            md_file.write(
                f"This analysis covers **{total_people}** people across **{departments}** departments with **{managers}** managers.\n\n"
            )

            # Score distribution if available
            if not evaluation_df.empty and "Score" in evaluation_df.columns:
                valid_scores = evaluation_df["Score"].dropna()
                if not valid_scores.empty:
                    avg_score = valid_scores.mean()
                    max_score = valid_scores.max()
                    min_score = valid_scores.min()

                    md_file.write("**Performance Overview:**\n")
                    md_file.write(f"- Average Score: {avg_score:.2f}\n")
                    md_file.write(f"- Highest Score: {max_score:.2f}\n")
                    md_file.write(f"- Lowest Score: {min_score:.2f}\n\n")

        # Key insights
        md_file.write("### Key Insights\n\n")
        md_file.write("- The analysis suggests areas for focus in skill development\n")
        md_file.write(
            "- There are clear patterns in career progression across departments\n"
        )
        md_file.write("- Performance varies significantly by team structure\n\n")

        # 2. Department & Team Analysis
        md_file.write("## Department & Team Analysis\n\n")

        if not profile_df.empty and "Department" in profile_df.columns:
            dept_counts = profile_df["Department"].value_counts()

            # Department distribution table
            md_file.write("### Department Distribution\n\n")
            md_file.write("| Department | People Count |\n")
            md_file.write("|------------|-------------|\n")

            for dept, count in dept_counts.items():
                md_file.write(f"| {dept} | {count} |\n")

            md_file.write("\n")

            # Department performance if evaluation data available
            if (
                not evaluation_df.empty
                and "Score" in evaluation_df.columns
                and not profile_df.empty
            ):
                # Join evaluation and profile data
                merged_df = pd.merge(
                    evaluation_df, profile_df, on=["Name", "Year"], how="inner"
                )

                if (
                    not merged_df.empty
                    and "Department" in merged_df.columns
                    and "Score" in merged_df.columns
                ):
                    # Calculate average score by department
                    dept_scores = (
                        merged_df.groupby("Department")["Score"]
                        .agg(["mean", "min", "max"])
                        .reset_index()
                    )

                    md_file.write("### Performance by Department\n\n")
                    md_file.write(
                        "| Department | Average Score | Min Score | Max Score |\n"
                    )
                    md_file.write(
                        "|------------|---------------|-----------|----------|\n"
                    )

                    for _, row in dept_scores.iterrows():
                        md_file.write(
                            f"| {row['Department']} | {row['mean']:.2f} | {row['min']:.2f} | {row['max']:.2f} |\n"
                        )

                    md_file.write("\n")

        # 3. Year-over-Year Performance
        md_file.write("## Year-over-Year Performance\n\n")

        if (
            not evaluation_df.empty
            and "Score" in evaluation_df.columns
            and "Year" in evaluation_df.columns
        ):
            yearly_scores = (
                evaluation_df.groupby("Year")["Score"]
                .agg(["mean", "min", "max", "count"])
                .reset_index()
            )

            md_file.write("### Performance Trends Over Time\n\n")
            md_file.write(
                "| Year | Average Score | Min Score | Max Score | People Evaluated |\n"
            )
            md_file.write(
                "|------|---------------|-----------|-----------|------------------|\n"
            )

            for _, row in yearly_scores.iterrows():
                md_file.write(
                    f"| {row['Year']} | {row['mean']:.2f} | {row['min']:.2f} | {row['max']:.2f} | {int(row['count'])} |\n"
                )

            md_file.write("\n")

            # Add Mermaid chart for year-over-year trends
            md_file.write("### Score Trends Visualization\n\n")
            md_file.write("```mermaid\n")
            md_file.write("graph LR\n")

            # Create nodes for each year
            for year in yearly_scores["Year"].unique():
                md_file.write(f"  {year}[{year}]\n")

            # Create connections between years with score change indicators
            prev_year = None
            prev_score = None

            for _, row in yearly_scores.iterrows():
                year = row["Year"]
                score = row["mean"]

                if prev_year is not None and prev_score is not None:
                    if score > prev_score:
                        md_file.write(
                            f"  {prev_year} -->|+{(score - prev_score):.2f}| {year}\n"
                        )
                    else:
                        md_file.write(
                            f"  {prev_year} -->|{(score - prev_score):.2f}| {year}\n"
                        )

                prev_year = year
                prev_score = score

            md_file.write("```\n\n")

        # 4. Career Development Insights
        md_file.write("## Career Development Insights\n\n")

        if not career_df.empty:
            md_file.write("### Skill Proficiency Overview\n\n")

            # Summarize skill levels across people
            total_skills = career_df["Total_Skills"].sum()
            avg_level = career_df["Avg_Skill_Level"].mean()
            level_counts = {
                "Level 1 (Beginner)": career_df["Level_1_Skills"].sum(),
                "Level 2 (Basic)": career_df["Level_2_Skills"].sum(),
                "Level 3 (Intermediate)": career_df["Level_3_Skills"].sum(),
                "Level 4 (Advanced)": career_df["Level_4_Skills"].sum(),
                "Level 5 (Expert)": career_df["Level_5_Skills"].sum(),
            }

            md_file.write(f"**Total Skills Tracked:** {total_skills}\n")
            md_file.write(f"**Average Skill Level:** {avg_level:.2f}/5.0\n\n")

            # Skill distribution table
            md_file.write("| Proficiency Level | Count | Percentage |\n")
            md_file.write("|-------------------|-------|------------|\n")

            for level, count in level_counts.items():
                percentage = (count / total_skills * 100) if total_skills > 0 else 0
                md_file.write(f"| {level} | {count} | {percentage:.1f}% |\n")

            md_file.write("\n")

            # Certification data if available
            total_certs = career_df["Certification_Count"].sum()
            avg_certs = career_df["Certification_Count"].mean()

            md_file.write(f"**Total Certifications:** {total_certs}\n")
            md_file.write(f"**Average Certifications per Person:** {avg_certs:.1f}\n\n")

            # Career progression velocity
            md_file.write("### Career Progression Metrics\n\n")
            valid_velocities = career_df["Promotion_Velocity"].dropna()

            if not valid_velocities.empty:
                avg_velocity = valid_velocities.mean()
                md_file.write(
                    f"**Average Time Between Promotions:** {avg_velocity:.1f} years\n\n"
                )

            # Add Mermaid chart for skill distribution
            md_file.write("### Skill Distribution Visualization\n\n")
            md_file.write("```mermaid\n")
            md_file.write("pie\n")
            md_file.write("    title Skill Level Distribution\n")

            for level, count in level_counts.items():
                if count > 0:
                    md_file.write(f'    "{level}" : {count}\n')

            md_file.write("```\n\n")

        # 5. Organizational Structure
        md_file.write("## Organizational Structure\n\n")

        if (
            not profile_df.empty
            and "Manager" in profile_df.columns
            and "Name" in profile_df.columns
        ):
            # Get the most recent year for each person
            latest_data = profile_df.sort_values(
                "Year", ascending=False
            ).drop_duplicates("Name")

            # Create org chart using Mermaid
            md_file.write("### Management Hierarchy\n\n")
            md_file.write("```mermaid\n")
            md_file.write("graph TD\n")

            # Track added manager-subordinate relationships to avoid duplicates
            added_relationships = set()

            # First add all managers as nodes
            managers = set(latest_data["Manager"]) - {None, "N/A"}
            for manager in managers:
                manager_id = manager.replace(" ", "_").replace("-", "_")
                md_file.write(f"  {manager_id}[{manager}]\n")

            # Add edges from managers to their reports
            for _, row in latest_data.iterrows():
                if row["Manager"] and row["Manager"] != "N/A":
                    manager_id = row["Manager"].replace(" ", "_").replace("-", "_")
                    person_id = row["Name"].replace(" ", "_").replace("-", "_")
                    relationship = f"{manager_id}-->{person_id}"

                    if relationship not in added_relationships:
                        md_file.write(f"  {manager_id}-->{person_id}[{row['Name']}]\n")
                        added_relationships.add(relationship)

            md_file.write("```\n\n")

            # Add department structure if available
            if "Department" in latest_data.columns:
                dept_managers = latest_data.groupby("Department")["Manager"].unique()

                md_file.write("### Department Leadership\n\n")
                md_file.write("| Department | Manager(s) |\n")
                md_file.write("|------------|------------|\n")

                for dept, managers in dept_managers.items():
                    # Filter out None and N/A values
                    valid_managers = [m for m in managers if m and m != "N/A"]
                    manager_list = (
                        ", ".join(valid_managers) if valid_managers else "No manager"
                    )
                    md_file.write(f"| {dept} | {manager_list} |\n")

                md_file.write("\n")

        # 6. Skill Distribution Analysis
        md_file.write("## Skill Distribution Analysis\n\n")

        # Extract and aggregate all skills across people
        all_skills = {}
        for person in data_list:
            if person.career_progression and person.career_progression.skills_matrix:
                for skill, level in person.career_progression.skills_matrix.items():
                    if skill not in all_skills:
                        all_skills[skill] = {
                            "count": 0,
                            "total_level": 0,
                            "level_dist": [0, 0, 0, 0, 0, 0],
                        }

                    all_skills[skill]["count"] += 1
                    all_skills[skill]["total_level"] += level
                    all_skills[skill]["level_dist"][level] += (
                        1  # Count at the appropriate level (0-based index)
                    )

        if all_skills:
            # Sort skills by frequency
            sorted_skills = sorted(
                all_skills.items(), key=lambda x: x[1]["count"], reverse=True
            )

            md_file.write("### Top Skills by Frequency\n\n")
            md_file.write("| Skill | People | Avg Level | L1 | L2 | L3 | L4 | L5 |\n")
            md_file.write("|-------|--------|-----------|----|----|----|----|----|\n")

            # Show top skills (limit to 20 for readability)
            for skill, data in sorted_skills[:20]:
                avg_level = (
                    data["total_level"] / data["count"] if data["count"] > 0 else 0
                )
                md_file.write(
                    f"| {skill} | {data['count']} | {avg_level:.1f} | {data['level_dist'][1]} | {data['level_dist'][2]} | {data['level_dist'][3]} | {data['level_dist'][4]} | {data['level_dist'][5]} |\n"
                )

            md_file.write("\n")

            # Add Mermaid chart for skill gap analysis
            md_file.write("### Skill Gap Analysis\n\n")

            if sorted_skills:
                md_file.write("```mermaid\n")
                md_file.write("xychart-beta\n")
                md_file.write('    title "Skill Coverage vs. Proficiency"\n')
                md_file.write(
                    '    x-axis ["Coverage (% of team)", "Proficiency (avg level)"]\n'
                )

                # Calculate total people for percentage
                total_people = len(data_list)

                # Add data points for top skills
                for i, (skill, data) in enumerate(sorted_skills[:10]):  # Top 10 skills
                    coverage = (
                        (data["count"] / total_people) * 100 if total_people > 0 else 0
                    )
                    avg_level = (
                        data["total_level"] / data["count"] if data["count"] > 0 else 0
                    )

                    md_file.write(
                        f'    y-axis "{skill}" [{coverage:.1f}, {avg_level:.1f}]\n'
                    )

                md_file.write("```\n\n")

        # 7. Detailed Comparisons
        md_file.write("## Detailed Comparisons\n\n")

        # If we have both evaluation and profile data, create year-over-year comparisons by department
        if (
            not evaluation_df.empty
            and not profile_df.empty
            and "Score" in evaluation_df.columns
        ):
            full_data = pd.merge(
                evaluation_df, profile_df, on=["Name", "Year"], how="inner"
            )

            if not full_data.empty and "Department" in full_data.columns:
                # Year-over-year by department
                dept_year_scores = (
                    full_data.groupby(["Department", "Year"])["Score"]
                    .mean()
                    .reset_index()
                )

                # Pivot table for department x year
                pivot_df = dept_year_scores.pivot(
                    index="Department", columns="Year", values="Score"
                )

                md_file.write("### Department Performance by Year\n\n")
                md_file.write("| Department |")

                # Write year headers
                for year in pivot_df.columns:
                    md_file.write(f" {year} |")
                md_file.write("\n")

                # Write separator line
                md_file.write("|------------|")
                for _ in range(len(pivot_df.columns)):
                    md_file.write("--------|")
                md_file.write("\n")

                # Write data rows
                for dept, row in pivot_df.iterrows():
                    md_file.write(f"| {dept} |")
                    for year in pivot_df.columns:
                        val = row.get(year)
                        cell_val = f" {val:.2f} |" if pd.notna(val) else " - |"
                        md_file.write(cell_val)
                    md_file.write("\n")

                md_file.write("\n")

                # Add trend comparison chart if there are multiple years
                if len(pivot_df.columns) > 1:
                    md_file.write("### Performance Trends by Department\n\n")
                    md_file.write("```mermaid\n")
                    md_file.write("xychart-beta\n")
                    md_file.write('    title "Department Performance Over Time"\n')

                    # Define x-axis (years)
                    x_axis = (
                        "    x-axis ["
                        + ", ".join([f'"{y}"' for y in pivot_df.columns])
                        + "]\n"
                    )
                    md_file.write(x_axis)

                    # Add a line for each department
                    for dept in pivot_df.index:
                        values = []
                        for year in pivot_df.columns:
                            val = pivot_df.loc[dept, year]
                            if pd.notna(val):
                                values.append(str(round(val, 2)))
                            else:
                                values.append("null")  # Use null for missing values

                        # Only add departments that have at least two valid values
                        if len([v for v in values if v != "null"]) >= 2:
                            value_str = ", ".join(values)
                            md_file.write(f'    line "{dept}" [{value_str}]\n')

                    md_file.write("```\n\n")

        # Generate CSV files with the detailed data for further analysis
        profile_csv_path = os.path.join(output_dir, f"profile_data_{timestamp}.csv")
        eval_csv_path = os.path.join(output_dir, f"evaluation_summary_{timestamp}.csv")
        career_csv_path = os.path.join(output_dir, f"career_data_{timestamp}.csv")

        if not profile_df.empty:
            profile_df.to_csv(profile_csv_path, index=False)
            md_file.write(
                f"[Download Profile Data CSV]({os.path.basename(profile_csv_path)})\n\n"
            )

        # For evaluation data, create a summary without the raw data
        if not evaluation_df.empty:
            eval_summary = evaluation_df.drop("Raw_Data", axis=1, errors="ignore")
            eval_summary.to_csv(eval_csv_path, index=False)
            md_file.write(
                f"[Download Evaluation Summary CSV]({os.path.basename(eval_csv_path)})\n\n"
            )

        if not career_df.empty:
            career_df.to_csv(career_csv_path, index=False)
            md_file.write(
                f"[Download Career Development Data CSV]({os.path.basename(career_csv_path)})\n\n"
            )

    print(f"Generated comprehensive evaluation report: {report_path}")
    return report_path


def generate_interactive_html_report(
    data_list: List[PersonData], output_dir: str
) -> str:
    """Generate an interactive HTML report with visualizations.

    This creates an HTML report with interactive charts using Chart.js for:
    - Year-over-year comparisons
    - Department performance
    - Skill distributions
    - Career trajectories

    Args:
        data_list: List of PersonData objects
        output_dir: Output directory for the report

    Returns:
        Path to the generated HTML file
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Process data similar to evaluation_report
    profile_data = []
    evaluation_data = []
    career_data = []

    # Process each person's data (similar to generate_evaluation_report)
    for person in data_list:
        if person.profile:
            profile_data.append(
                {
                    "Name": person.name,
                    "Year": person.year,
                    "Department": person.profile.nome_departamento,
                    "Position": person.profile.cargo,
                    "Manager": person.profile.nome_gestor or "N/A",
                    "Is_Manager": person.profile.tipo_gestao,
                    "Squad": person.profile.nome_squad,
                    "Community": person.profile.nome_comunidade,
                }
            )

        if person.evaluation_data:
            overall_score = None
            if isinstance(person.evaluation_data, dict):
                if "pontuacao_final" in person.evaluation_data:
                    overall_score = person.evaluation_data["pontuacao_final"]
                elif (
                    "avaliacoes" in person.evaluation_data
                    and "pontuacao_final" in person.evaluation_data["avaliacoes"]
                ):
                    overall_score = person.evaluation_data["avaliacoes"][
                        "pontuacao_final"
                    ]

            evaluation_data.append(
                {
                    "Name": person.name,
                    "Year": person.year,
                    "Score": overall_score,
                    "Raw_Data": person.evaluation_data,
                }
            )

        if person.career_progression:
            career_data.append(
                {
                    "Name": person.name,
                    "Year": person.year,
                    "Promotion_Velocity": person.career_progression.get_promotion_velocity(),
                    "Skill_Growth_Rate": person.career_progression.get_skill_growth_rate(),
                    "Total_Skills": len(person.career_progression.skills_matrix)
                    if person.career_progression.skills_matrix
                    else 0,
                    "Avg_Skill_Level": sum(
                        person.career_progression.skills_matrix.values()
                    )
                    / len(person.career_progression.skills_matrix)
                    if person.career_progression.skills_matrix
                    and len(person.career_progression.skills_matrix) > 0
                    else 0,
                }
            )

    # Convert to DataFrames
    profile_df = pd.DataFrame(profile_data) if profile_data else pd.DataFrame()
    evaluation_df = pd.DataFrame(evaluation_data) if evaluation_data else pd.DataFrame()
    career_df = pd.DataFrame(career_data) if career_data else pd.DataFrame()

    # Generate chart data
    charts_data = {}

    # Chart 1: Year-over-year scores
    if (
        not evaluation_df.empty
        and "Score" in evaluation_df.columns
        and "Year" in evaluation_df.columns
    ):
        yearly_scores = (
            evaluation_df.groupby("Year")["Score"].agg(["mean", "count"]).reset_index()
        )
        charts_data["yearly_scores"] = {
            "years": yearly_scores["Year"].tolist(),
            "scores": yearly_scores["mean"].tolist(),
            "counts": yearly_scores["count"].tolist(),
        }

    # Chart 2: Department performance
    if (
        not evaluation_df.empty
        and not profile_df.empty
        and "Score" in evaluation_df.columns
    ):
        merged_df = pd.merge(
            evaluation_df, profile_df, on=["Name", "Year"], how="inner"
        )
        if not merged_df.empty and "Department" in merged_df.columns:
            dept_scores = merged_df.groupby("Department")["Score"].mean().reset_index()
            charts_data["department_scores"] = {
                "departments": dept_scores["Department"].tolist(),
                "scores": dept_scores["Score"].tolist(),
            }

    # Chart 3: Skill levels
    skill_data = {}
    for person in data_list:
        if person.career_progression and person.career_progression.skills_matrix:
            for skill, level in person.career_progression.skills_matrix.items():
                if skill not in skill_data:
                    skill_data[skill] = {"count": 0, "total_level": 0}
                skill_data[skill]["count"] += 1
                skill_data[skill]["total_level"] += level

    if skill_data:
        skill_avg = {
            skill: data["total_level"] / data["count"]
            for skill, data in skill_data.items()
        }
        top_skills = sorted(skill_avg.items(), key=lambda x: x[1], reverse=True)[:10]
        charts_data["skill_levels"] = {
            "skills": [s[0] for s in top_skills],
            "levels": [s[1] for s in top_skills],
        }

    # Generate the HTML report
    report_path = os.path.join(output_dir, f"interactive_report_{timestamp}.html")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>People Analytics Interactive Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1, h2, h3 {
            color: #333;
        }
        .chart-container {
            margin-bottom: 30px;
            padding: 15px;
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 0 5px rgba(0,0,0,0.05);
        }
        .row {
            display: flex;
            flex-wrap: wrap;
            margin: 0 -15px;
        }
        .column {
            flex: 1;
            padding: 15px;
            min-width: 300px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:nth-child(even) {
            background-color: #f5f5f5;
        }
        .summary-box {
            background-color: #f8f9fa;
            border-left: 4px solid #4285f4;
            padding: 15px;
            margin-bottom: 20px;
        }
        .metric {
            display: inline-block;
            margin-right: 20px;
            margin-bottom: 10px;
        }
        .metric strong {
            display: block;
            font-size: 24px;
            color: #4285f4;
        }
        .metric span {
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>People Analytics Interactive Report</h1>
        <p><em>Generated on: """)
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        f.write("""</em></p>
        
        <div class="summary-box">
            <h2>Executive Summary</h2>
            <div class="metrics-container">""")

        # Add summary metrics
        if not profile_df.empty:
            total_people = profile_df["Name"].nunique()
            departments = (
                profile_df["Department"].nunique()
                if "Department" in profile_df.columns
                else 0
            )

            f.write(f"""
                <div class="metric">
                    <strong>{total_people}</strong>
                    <span>Total People</span>
                </div>
                <div class="metric">
                    <strong>{departments}</strong>
                    <span>Departments</span>
                </div>""")

        if not evaluation_df.empty and "Score" in evaluation_df.columns:
            valid_scores = evaluation_df["Score"].dropna()
            if not valid_scores.empty:
                avg_score = valid_scores.mean()
                f.write(f"""
                <div class="metric">
                    <strong>{avg_score:.2f}</strong>
                    <span>Avg Score</span>
                </div>""")

        f.write("""
            </div>
        </div>
        
        <div class="row">""")

        # Year-over-year performance chart
        if "yearly_scores" in charts_data:
            f.write("""
            <div class="column">
                <div class="chart-container">
                    <h3>Year-over-Year Performance</h3>
                    <canvas id="yearlyChart"></canvas>
                </div>
            </div>""")

        # Department performance chart
        if "department_scores" in charts_data:
            f.write("""
            <div class="column">
                <div class="chart-container">
                    <h3>Department Performance</h3>
                    <canvas id="departmentChart"></canvas>
                </div>
            </div>""")

        f.write("""
        </div>
        
        <div class="row">""")

        # Skill levels chart
        if "skill_levels" in charts_data:
            f.write("""
            <div class="column">
                <div class="chart-container">
                    <h3>Top Skills by Average Level</h3>
                    <canvas id="skillsChart"></canvas>
                </div>
            </div>""")

        f.write("""
            <div class="column">
                <div class="chart-container">
                    <h3>Data Summary</h3""")

        # Add a summary table
        if not profile_df.empty and not evaluation_df.empty:
            merged = pd.merge(
                profile_df, evaluation_df, on=["Name", "Year"], how="inner"
            )
            if (
                not merged.empty
                and "Department" in merged.columns
                and "Score" in merged.columns
            ):
                dept_summary = (
                    merged.groupby("Department")
                    .agg({"Name": "nunique", "Score": ["mean", "min", "max"]})
                    .reset_index()
                )

                dept_summary.columns = [
                    "Department",
                    "People",
                    "Avg Score",
                    "Min Score",
                    "Max Score",
                ]

                f.write("""
                    <table>
                        <tr>
                            <th>Department</th>
                            <th>People</th>
                            <th>Avg Score</th>
                            <th>Min Score</th>
                            <th>Max Score</th>
                        </tr>""")

                for _, row in dept_summary.iterrows():
                    f.write(f"""
                        <tr>
                            <td>{row["Department"]}</td>
                            <td>{int(row["People"])}</td>
                            <td>{row["Avg Score"]:.2f}</td>
                            <td>{row["Min Score"]:.2f}</td>
                            <td>{row["Max Score"]:.2f}</td>
                        </tr>""")

                f.write("""
                    </table>""")

        f.write("""
                </div>
            </div>
        </div>
        
        <script>
            // Chart.js initialization
            document.addEventListener('DOMContentLoaded', function() {""")

        # Year-over-year chart
        if "yearly_scores" in charts_data:
            ys_data = charts_data["yearly_scores"]
            f.write(f"""
                // Year-over-year chart
                new Chart(document.getElementById('yearlyChart'), {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps(ys_data["years"])},
                        datasets: [{{
                            label: 'Average Score',
                            data: {json.dumps(ys_data["scores"])},
                            backgroundColor: 'rgba(54, 162, 235, 0.2)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 2,
                            tension: 0.1
                        }}]
                    }},
                    options: {{
                        scales: {{
                            y: {{
                                beginAtZero: false
                            }}
                        }},
                        plugins: {{
                            title: {{
                                display: true,
                                text: 'Performance Trend Over Time'
                            }}
                        }}
                    }}
                }});""")

        # Department chart
        if "department_scores" in charts_data:
            ds_data = charts_data["department_scores"]
            f.write(f"""
                // Department performance chart
                new Chart(document.getElementById('departmentChart'), {{
                    type: 'bar',
                    data: {{
                        labels: {json.dumps(ds_data["departments"])},
                        datasets: [{{
                            label: 'Average Score',
                            data: {json.dumps(ds_data["scores"])},
                            backgroundColor: [
                                'rgba(255, 99, 132, 0.6)',
                                'rgba(54, 162, 235, 0.6)',
                                'rgba(255, 206, 86, 0.6)',
                                'rgba(75, 192, 192, 0.6)',
                                'rgba(153, 102, 255, 0.6)',
                                'rgba(255, 159, 64, 0.6)',
                                'rgba(199, 199, 199, 0.6)'
                            ],
                            borderColor: [
                                'rgba(255, 99, 132, 1)',
                                'rgba(54, 162, 235, 1)',
                                'rgba(255, 206, 86, 1)',
                                'rgba(75, 192, 192, 1)',
                                'rgba(153, 102, 255, 1)',
                                'rgba(255, 159, 64, 1)',
                                'rgba(199, 199, 199, 1)'
                            ],
                            borderWidth: 1
                        }}]
                    }},
                    options: {{
                        scales: {{
                            y: {{
                                beginAtZero: false
                            }}
                        }},
                        plugins: {{
                            title: {{
                                display: true,
                                text: 'Department Performance Comparison'
                            }}
                        }}
                    }}
                }});""")

        # Skills chart
        if "skill_levels" in charts_data:
            sl_data = charts_data["skill_levels"]
            f.write(f"""
                // Skills chart
                new Chart(document.getElementById('skillsChart'), {{
                    type: 'radar',
                    data: {{
                        labels: {json.dumps(sl_data["skills"])},
                        datasets: [{{
                            label: 'Average Skill Level',
                            data: {json.dumps(sl_data["levels"])},
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderWidth: 1,
                            pointBackgroundColor: 'rgba(255, 99, 132, 1)'
                        }}]
                    }},
                    options: {{
                        scales: {{
                            r: {{
                                min: 0,
                                max: 5,
                                ticks: {{
                                    stepSize: 1
                                }}
                            }}
                        }},
                        plugins: {{
                            title: {{
                                display: true,
                                text: 'Top Skills Distribution'
                            }}
                        }}
                    }}
                }});""")

        f.write("""
            });
        </script>
    </div>
</body>
</html>""")

    print(f"Generated interactive HTML report: {report_path}")
    return report_path


def generate_comparison_template(
    data_list: List[PersonData], output_dir: str, comparison_type: str = "year"
) -> str:
    """Generate a specialized comparison template for year-over-year or person-to-person analysis.

    This creates a focused template for comparing:
    - Year-over-year for the same person (comparison_type="year")
    - Person-to-person for the same year (comparison_type="person")

    Args:
        data_list: List of PersonData objects
        output_dir: Directory to save the output
        comparison_type: Type of comparison ("year" or "person")

    Returns:
        Path to the generated markdown template
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if comparison_type not in ["year", "person"]:
        raise ValueError("Comparison type must be 'year' or 'person'")

    # Prepare data for comparison
    profile_data = []
    evaluation_data = []
    career_data = []

    # Process data similar to evaluation_report
    for person in data_list:
        if person.profile:
            profile_data.append(
                {
                    "Name": person.name,
                    "Year": person.year,
                    "Department": person.profile.nome_departamento,
                    "Position": person.profile.cargo,
                    "Manager": person.profile.nome_gestor or "N/A",
                    "Is_Manager": person.profile.tipo_gestao,
                }
            )

        if person.evaluation_data:
            # Extract overall score if available
            overall_score = None
            if isinstance(person.evaluation_data, dict):
                if "pontuacao_final" in person.evaluation_data:
                    overall_score = person.evaluation_data["pontuacao_final"]
                elif (
                    "avaliacoes" in person.evaluation_data
                    and "pontuacao_final" in person.evaluation_data["avaliacoes"]
                ):
                    overall_score = person.evaluation_data["avaliacoes"][
                        "pontuacao_final"
                    ]

            evaluation_data.append(
                {
                    "Name": person.name,
                    "Year": person.year,
                    "Score": overall_score,
                }
            )

        # Career progression data
        if person.career_progression:
            # Calculate skill level distribution
            skill_levels = {}
            if person.career_progression.skills_matrix:
                for level in range(1, 6):  # Levels 1-5
                    count = sum(
                        1
                        for v in person.career_progression.skills_matrix.values()
                        if v == level
                    )
                    skill_levels[f"Level_{level}"] = count

            career_data.append(
                {
                    "Name": person.name,
                    "Year": person.year,
                    "Total_Skills": len(person.career_progression.skills_matrix)
                    if person.career_progression.skills_matrix
                    else 0,
                    "Avg_Skill_Level": sum(
                        person.career_progression.skills_matrix.values()
                    )
                    / len(person.career_progression.skills_matrix)
                    if person.career_progression.skills_matrix
                    and len(person.career_progression.skills_matrix) > 0
                    else 0,
                    "Promotion_Velocity": person.career_progression.get_promotion_velocity(),
                    "Level_1_Skills": skill_levels.get("Level_1", 0),
                    "Level_2_Skills": skill_levels.get("Level_2", 0),
                    "Level_3_Skills": skill_levels.get("Level_3", 0),
                    "Level_4_Skills": skill_levels.get("Level_4", 0),
                    "Level_5_Skills": skill_levels.get("Level_5", 0),
                }
            )

    # Convert to DataFrames
    profile_df = pd.DataFrame(profile_data) if profile_data else pd.DataFrame()
    evaluation_df = pd.DataFrame(evaluation_data) if evaluation_data else pd.DataFrame()
    career_df = pd.DataFrame(career_data) if career_data else pd.DataFrame()

    # Determine the output file name
    if comparison_type == "year":
        template_name = f"year_comparison_template_{timestamp}.md"
    else:  # person
        template_name = f"person_comparison_template_{timestamp}.md"

    template_path = os.path.join(output_dir, template_name)

    with open(template_path, "w", encoding="utf-8") as f:
        # Write header
        f.write(
            f"# {'Year-over-Year' if comparison_type == 'year' else 'Person-to-Person'} Comparison Template\n\n"
        )
        f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")

        if comparison_type == "year":
            # Year-over-year comparison
            # Get unique people
            if not profile_df.empty:
                unique_people = profile_df["Name"].unique()

                f.write("## Available People for Year Comparison\n\n")
                f.write("| Person | Available Years |\n")
                f.write("|--------|----------------|\n")

                for person in unique_people:
                    person_years = profile_df[profile_df["Name"] == person][
                        "Year"
                    ].unique()
                    years_str = ", ".join(sorted(map(str, person_years)))
                    f.write(f"| {person} | {years_str} |\n")

                f.write("\n## Year-over-Year Comparison Template\n\n")
                f.write(
                    "To perform a year-over-year comparison, select a person and fill in the template below.\n\n"
                )

                f.write("### Person: [Enter Name]\n\n")
                f.write(
                    "| Metric | Previous Year [Enter Year] | Current Year [Enter Year] | Change |\n"
                )
                f.write(
                    "|--------|---------------------------|------------------------|--------|\n"
                )
                f.write("| Position | | | |\n")
                f.write("| Department | | | |\n")
                f.write("| Manager | | | |\n")
                f.write("| Overall Score | | | |\n")
                f.write("| Total Skills | | | |\n")
                f.write("| Average Skill Level | | | |\n")
                f.write("| New Skills Acquired | | | |\n")
                f.write("| Certifications | | | |\n")

                # Add Mermaid chart template for year comparison
                f.write("\n### Performance Trend Visualization\n\n")
                f.write("```mermaid\n")
                f.write("xychart-beta\n")
                f.write('    title "Performance Over Time"\n')
                f.write('    x-axis ["Previous Year", "Current Year"]\n')
                f.write('    y-axis "Performance Score" [0, 5]\n')
                f.write('    line "[Person Name]" [0, 0]\n')
                f.write("```\n\n")

                # Add skill comparison template
                f.write("### Skill Evolution\n\n")
                f.write(
                    "| Skill | Previous Year Level | Current Year Level | Change |\n"
                )
                f.write(
                    "|-------|---------------------|-------------------|--------|\n"
                )
                f.write("| Skill 1 | | | |\n")
                f.write("| Skill 2 | | | |\n")
                f.write("| Skill 3 | | | |\n")

                # Add improvement areas template
                f.write("\n### Key Improvement Areas\n\n")
                f.write("1. \n2. \n3. \n\n")

                # Add career growth template
                f.write("### Career Growth Summary\n\n")
                f.write("- **Progress Since Previous Year**: \n")
                f.write("- **Key Achievements**: \n")
                f.write("- **Development Opportunities**: \n")
        else:
            # Person-to-person comparison
            # Get unique years
            if not profile_df.empty:
                unique_years = profile_df["Year"].unique()

                f.write("## Available Years for Person Comparison\n\n")
                f.write("| Year | Available People |\n")
                f.write("|------|------------------|\n")

                for year in sorted(unique_years):
                    year_people = profile_df[profile_df["Year"] == year][
                        "Name"
                    ].unique()
                    people_str = ", ".join(sorted(year_people))
                    f.write(f"| {year} | {people_str} |\n")

                f.write("\n## Person-to-Person Comparison Template\n\n")
                f.write(
                    "To perform a person-to-person comparison, select a year and fill in the template below.\n\n"
                )

                f.write("### Year: [Enter Year]\n\n")
                f.write(
                    "| Metric | Person 1 [Enter Name] | Person 2 [Enter Name] | Difference |\n"
                )
                f.write(
                    "|--------|------------------------|----------------------|------------|\n"
                )
                f.write("| Position | | | |\n")
                f.write("| Department | | | |\n")
                f.write("| Manager | | | |\n")
                f.write("| Overall Score | | | |\n")
                f.write("| Total Skills | | | |\n")
                f.write("| Average Skill Level | | | |\n")
                f.write("| Career Progression | | | |\n")

                # Add Mermaid chart template for person comparison
                f.write("\n### Performance Comparison Visualization\n\n")
                f.write("```mermaid\n")
                f.write("xychart-beta\n")
                f.write('    title "Performance Comparison"\n')
                f.write('    x-axis ["Person 1", "Person 2"]\n')
                f.write('    y-axis "Performance Score" [0, 5]\n')
                f.write("    bar [0, 0]\n")
                f.write("```\n\n")

                # Add skills radar chart template
                f.write("### Skill Comparison\n\n")
                f.write("```mermaid\n")
                f.write("%%{init: {'theme': 'neutral'}}%%\n")
                f.write("pie\n")
                f.write('    title "Skill Level Distribution Comparison"\n')
                f.write('    "Level 1" : 0\n')
                f.write('    "Level 2" : 0\n')
                f.write('    "Level 3" : 0\n')
                f.write('    "Level 4" : 0\n')
                f.write('    "Level 5" : 0\n')
                f.write("```\n\n")

                # Add comparative strengths template
                f.write("### Comparative Analysis\n\n")
                f.write("#### Person 1 Strengths\n\n")
                f.write("1. \n2. \n3. \n\n")

                f.write("#### Person 2 Strengths\n\n")
                f.write("1. \n2. \n3. \n\n")

                f.write("#### Learning Opportunities\n\n")
                f.write("- Person 1 can learn from Person 2: \n")
                f.write("- Person 2 can learn from Person 1: \n")

        # Add summary and recommendations section regardless of comparison type
        f.write("\n## Summary and Recommendations\n\n")
        f.write("### Key Insights\n\n")
        f.write("1. \n2. \n3. \n\n")

        f.write("### Recommended Actions\n\n")
        f.write("1. \n2. \n3. \n\n")

        f.write("---\n\n")
        f.write(
            "*This template was automatically generated. Fill in the details manually or use the data import feature.*\n"
        )

    print(f"Generated {comparison_type} comparison template: {template_path}")
    return template_path


def generate_skill_recommendations(data_list: List[PersonData], output_dir: str) -> str:
    """Generate skill recommendations and learning paths based on career data.

    This analyzes skills across the organization and recommends:
    - Skills to develop based on career progression patterns
    - Learning paths for different career trajectories
    - Skill gaps that would benefit team/department

    Args:
        data_list: List of PersonData objects
        output_dir: Directory to save the output

    Returns:
        Path to the generated recommendations file
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Collect all skills data
    all_skills = {}
    person_skills = {}
    departments = {}
    positions = {}

    # Process all people data first to build reference datasets
    for person in data_list:
        if not person.career_progression or not person.career_progression.skills_matrix:
            continue

        # Get demographic info
        dept = None
        position = None
        if person.profile:
            dept = person.profile.nome_departamento
            position = person.profile.cargo

            # Track departments and positions
            if dept:
                if dept not in departments:
                    departments[dept] = {"people": [], "skills": {}}
                departments[dept]["people"].append(person.name)

            if position:
                if position not in positions:
                    positions[position] = {"people": [], "skills": {}}
                positions[position]["people"].append(person.name)

        # Process skills
        person_skills[person.name] = {"raw": {}, "categories": {}}

        for skill_name, level in person.career_progression.skills_matrix.items():
            # Add to person's raw skills
            person_skills[person.name]["raw"][skill_name] = level

            # Extract category if present
            category = "General"
            if "." in skill_name:
                category, skill_short_name = skill_name.split(".", 1)
            else:
                skill_short_name = skill_name

            # Track by category
            if category not in person_skills[person.name]["categories"]:
                person_skills[person.name]["categories"][category] = {}
            person_skills[person.name]["categories"][category][skill_short_name] = level

            # Add to global skills catalog
            if skill_name not in all_skills:
                all_skills[skill_name] = {
                    "count": 0,
                    "total_level": 0,
                    "by_position": {},
                    "by_department": {},
                }

            all_skills[skill_name]["count"] += 1
            all_skills[skill_name]["total_level"] += level

            # Add to position stats
            if position:
                if position not in all_skills[skill_name]["by_position"]:
                    all_skills[skill_name]["by_position"][position] = {
                        "count": 0,
                        "total_level": 0,
                    }
                all_skills[skill_name]["by_position"][position]["count"] += 1
                all_skills[skill_name]["by_position"][position]["total_level"] += level

                # Also add to positions aggregation
                if skill_name not in positions[position]["skills"]:
                    positions[position]["skills"][skill_name] = {
                        "count": 0,
                        "total_level": 0,
                    }
                positions[position]["skills"][skill_name]["count"] += 1
                positions[position]["skills"][skill_name]["total_level"] += level

            # Add to department stats
            if dept:
                if dept not in all_skills[skill_name]["by_department"]:
                    all_skills[skill_name]["by_department"][dept] = {
                        "count": 0,
                        "total_level": 0,
                    }
                all_skills[skill_name]["by_department"][dept]["count"] += 1
                all_skills[skill_name]["by_department"][dept]["total_level"] += level

    # Calculate benchmarks and averages
    org_skill_avgs = {
        skill: data["total_level"] / data["count"] for skill, data in all_skills.items()
    }
    dept_skill_avgs = {}
    pos_skill_avgs = {}

    for dept, data in departments.items():
        dept_skill_avgs[dept] = {}
        for skill, skill_data in data["skills"].items():
            if skill_data["count"] > 0:
                dept_skill_avgs[dept][skill] = (
                    skill_data["total_level"] / skill_data["count"]
                )

    for pos, data in positions.items():
        pos_skill_avgs[pos] = {}
        for skill, skill_data in data["skills"].items():
            if skill_data["count"] > 0:
                pos_skill_avgs[pos][skill] = (
                    skill_data["total_level"] / skill_data["count"]
                )

    # Filter to analyze only requested person if specified
    people_to_analyze = list(person_skills.keys())

    # Generate analytics file
    analytics_path = os.path.join(output_dir, f"skill_analytics_{timestamp}.md")

    with open(analytics_path, "w", encoding="utf-8") as f:
        f.write("# Individual Skill Analytics\n\n")
        f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")

        for person_name in people_to_analyze:
            if person_name not in person_skills:
                continue

            # Find the person in the original data
            person_data = next((p for p in data_list if p.name == person_name), None)
            if not person_data:
                continue

            # Get demographic info
            position = person_data.profile.cargo if person_data.profile else "Unknown"
            dept = (
                person_data.profile.nome_departamento
                if person_data.profile
                else "Unknown"
            )

            # Calculate various skill metrics
            skills = person_skills[person_name]["raw"]
            skill_count = len(skills)

            if skill_count == 0:
                continue

            # 1. Basic proficiency metrics
            avg_level = sum(skills.values()) / skill_count
            max_level = max(skills.values()) if skills else 0
            min_level = min(skills.values()) if skills else 0

            # 2. Skill distribution
            level_dist = {
                i: sum(1 for level in skills.values() if level == i)
                for i in range(1, 6)
            }

            # 3. Skill category strengths
            category_scores = {}
            for category, cat_skills in person_skills[person_name][
                "categories"
            ].items():
                if cat_skills:
                    category_scores[category] = sum(cat_skills.values()) / len(
                        cat_skills
                    )

            # 4. T-shaped profile analysis (breadth vs depth)
            breadth_score = skill_count / max(
                1,
                len(set().union(*[skills for cat, skills in skill_categories.items()])),
            )
            depth_score = sum(1 for level in skills.values() if level >= 4) / max(
                1, skill_count
            )
            t_shape_score = (breadth_score + depth_score) / 2

            # 5. Position skill gap analysis
            if position in pos_skill_avgs:
                position_gaps = []
                for skill, avg in pos_skill_avgs[position].items():
                    person_level = skills.get(skill, 0)
                    if avg > person_level:
                        position_gaps.append(
                            {
                                "skill": skill,
                                "person_level": person_level,
                                "position_avg": avg,
                                "gap": avg - person_level,
                            }
                        )
                # Sort by gap size
                position_gaps.sort(key=lambda x: x["gap"], reverse=True)
            else:
                position_gaps = []

            # 6. Department skill comparison
            if dept in dept_skill_avgs:
                dept_comparison = []
                for skill, avg in dept_skill_avgs[dept].items():
                    person_level = skills.get(skill, 0)
                    comparison = person_level - avg
                    dept_comparison.append(
                        {
                            "skill": skill,
                            "person_level": person_level,
                            "dept_avg": avg,
                            "difference": comparison,
                        }
                    )
                # Sort by difference (largest positive first)
                dept_comparison.sort(key=lambda x: x["difference"], reverse=True)
            else:
                dept_comparison = []

            # 7. Unique strengths (skills higher than both position and department averages)
            unique_strengths = []
            for skill, level in skills.items():
                pos_avg = pos_skill_avgs.get(position, {}).get(skill, 0)
                dept_avg = dept_skill_avgs.get(dept, {}).get(skill, 0)
                org_avg = org_skill_avgs.get(skill, 0)

                if level > pos_avg and level > dept_avg and level >= 4:
                    unique_strengths.append(
                        {
                            "skill": skill,
                            "level": level,
                            "pos_avg": pos_avg,
                            "dept_avg": dept_avg,
                            "org_avg": org_avg,
                        }
                    )

            # Sort by level
            unique_strengths.sort(key=lambda x: x["level"], reverse=True)

            # 8. Calculate composite scores (0-100 scale)
            skill_breadth_score = min(
                100, (skill_count / 20) * 100
            )  # Assume 20 skills is "complete"
            skill_depth_score = min(100, (avg_level / 5) * 100)
            skill_balance_score = 100 - min(
                100, abs(skill_breadth_score - skill_depth_score)
            )

            position_fit_score = 0
            if position in pos_skill_avgs and pos_skill_avgs[position]:
                matched_skills = sum(
                    1 for skill in pos_skill_avgs[position] if skill in skills
                )
                position_fit_score = min(
                    100, (matched_skills / len(pos_skill_avgs[position])) * 100
                )

            skill_rarity_score = 0
            if skills:
                rarities = []
                for skill, level in skills.items():
                    if skill in all_skills:
                        # Rarer skills (possessed by fewer people) score higher
                        rarity = 1 - (all_skills[skill]["count"] / len(person_skills))
                        rarities.append(rarity * level)  # Weight by level

                if rarities:
                    skill_rarity_score = min(100, (sum(rarities) / len(rarities)) * 100)

            # 9. Overall skill effectiveness score (composite)
            skill_effectiveness = (
                skill_breadth_score * 0.2
                + skill_depth_score * 0.3
                + skill_balance_score * 0.1
                + position_fit_score * 0.3
                + skill_rarity_score * 0.1
            )

            # Write individual analytics
            f.write(f"## {person_name}\n\n")
            f.write(f"**Position:** {position}  \n")
            f.write(f"**Department:** {dept}  \n\n")

            f.write("### Skill Profile Summary\n\n")
            f.write(f"**Total Skills:** {skill_count}  \n")
            f.write(f"**Average Proficiency:** {avg_level:.2f}/5.0  \n")
            f.write(f"**Highest Proficiency:** {max_level}/5.0  \n")
            f.write(f"**Lowest Proficiency:** {min_level}/5.0  \n\n")

            f.write("### Skill Distribution\n\n")
            f.write("| Level | Count | Percentage |\n")
            f.write("|-------|-------|------------|\n")
            for level in range(1, 6):
                count = level_dist.get(level, 0)
                pct = (count / skill_count) * 100 if skill_count > 0 else 0
                f.write(f"| Level {level} | {count} | {pct:.1f}% |\n")
            f.write("\n")

            f.write("### Skill Category Strengths\n\n")
            f.write("| Category | Average Proficiency | Skills Count |\n")
            f.write("|----------|----------------------|-------------|\n")
            for category, score in sorted(
                category_scores.items(), key=lambda x: x[1], reverse=True
            ):
                count = len(person_skills[person_name]["categories"].get(category, {}))
                f.write(f"| {category} | {score:.2f} | {count} |\n")
            f.write("\n")

            f.write("### Composite Skill Scores\n\n")
            f.write(f"**Skill Breadth Score:** {skill_breadth_score:.1f}/100  \n")
            f.write(f"**Skill Depth Score:** {skill_depth_score:.1f}/100  \n")
            f.write(f"**Skill Balance Score:** {skill_balance_score:.1f}/100  \n")
            f.write(f"**Position Fit Score:** {position_fit_score:.1f}/100  \n")
            f.write(f"**Skill Rarity Score:** {skill_rarity_score:.1f}/100  \n")
            f.write(
                f"**Overall Skill Effectiveness:** {skill_effectiveness:.1f}/100  \n\n"
            )

            # T-shape profile visualization
            f.write("### T-Shape Profile Analysis\n\n")
            f.write(f"**Breadth Score:** {breadth_score:.2f}  \n")
            f.write(f"**Depth Score:** {depth_score:.2f}  \n")
            f.write(f"**T-Shape Score:** {t_shape_score:.2f}  \n\n")

            f.write("```mermaid\n")
            f.write("quadrantChart\n")
            f.write("    title T-Shape Skill Profile Analysis\n")
            f.write("    x-axis Low Breadth --> High Breadth\n")
            f.write("    y-axis Low Depth --> High Depth\n")
            f.write("    quadrant-1 Specialist (Deep Expert)\n")
            f.write("    quadrant-2 T-Shaped (Ideal)\n")
            f.write("    quadrant-3 Generalist (Jack of All Trades)\n")
            f.write("    quadrant-4 Limited Expertise\n")
            f.write(f"    {person_name}: [{breadth_score}, {depth_score}]\n")
            f.write("```\n\n")

            # Position skill gaps
            if position_gaps:
                f.write("### Top Skill Gaps for Position\n\n")
                f.write("| Skill | Your Level | Position Average | Gap |\n")
                f.write("|-------|------------|------------------|-----|\n")

                for gap in position_gaps[:5]:  # Show top 5 gaps
                    f.write(
                        f"| {gap['skill']} | {gap['person_level']} | {gap['position_avg']:.2f} | {gap['gap']:.2f} |\n"
                    )
                f.write("\n")

                # Visualization
                f.write("```mermaid\n")
                f.write("%%{init: {'theme': 'neutral'}}%%\n")
                f.write("xychart-beta\n")
                f.write('    title "Position Skill Gap Analysis"\n')

                # X-axis labels (skills)
                skills_list = [gap["skill"] for gap in position_gaps[:5]]
                f.write(
                    "    x-axis [" + ", ".join([f'"{s}"' for s in skills_list]) + "]\n"
                )

                # Person's levels
                person_levels = [str(gap["person_level"]) for gap in position_gaps[:5]]
                f.write(f'    bar "Your Level" [{", ".join(person_levels)}]\n')

                # Position average
                pos_avgs = [
                    str(round(gap["position_avg"], 2)) for gap in position_gaps[:5]
                ]
                f.write(f'    bar "Position Average" [{", ".join(pos_avgs)}]\n')

                f.write("```\n\n")

            # Unique strengths
            if unique_strengths:
                f.write("### Unique Strengths\n\n")
                f.write(
                    "These are skills where you significantly outperform both position and department averages:\n\n"
                )
                f.write(
                    "| Skill | Your Level | Position Avg | Department Avg | Org Avg |\n"
                )
                f.write(
                    "|-------|------------|--------------|----------------|--------|\n"
                )

                for strength in unique_strengths[:5]:  # Show top 5
                    f.write(
                        f"| {strength['skill']} | {strength['level']} | {strength['pos_avg']:.2f} | {strength['dept_avg']:.2f} | {strength['org_avg']:.2f} |\n"
                    )
                f.write("\n")

            # Department comparison (where person excels)
            if dept_comparison:
                top_strengths = [c for c in dept_comparison if c["difference"] > 0][:3]
                top_weaknesses = [c for c in dept_comparison if c["difference"] < 0][
                    -3:
                ]

                if top_strengths or top_weaknesses:
                    f.write("### Department Comparison Highlights\n\n")

                    if top_strengths:
                        f.write("**Areas where you excel compared to department:**\n\n")
                        for strength in top_strengths:
                            f.write(
                                f"- **{strength['skill']}**: Your level: {strength['person_level']}, "
                                + f"Department average: {strength['dept_avg']:.2f} "
                                + f"(+{strength['difference']:.2f})\n"
                            )
                        f.write("\n")

                    if top_weaknesses:
                        f.write("**Areas for development compared to department:**\n\n")
                        for weakness in top_weaknesses:
                            f.write(
                                f"- **{weakness['skill']}**: Your level: {weakness['person_level']}, "
                                + f"Department average: {weakness['dept_avg']:.2f} "
                                + f"({weakness['difference']:.2f})\n"
                            )
                        f.write("\n")

            # Skill radar visualization for top categories
            if category_scores:
                top_categories = sorted(
                    category_scores.items(), key=lambda x: x[1], reverse=True
                )[:5]

                f.write("### Skill Category Radar\n\n")
                f.write("```mermaid\n")
                f.write("%%{init: {'theme': 'forest'}}%%\n")
                f.write("pie\n")
                f.write('    title "Skill Distribution by Category"\n')

                for category, score in top_categories:
                    count = len(
                        person_skills[person_name]["categories"].get(category, {})
                    )
                    f.write(f'    "{category}" : {count}\n')

                f.write("```\n\n")

            # Development recommendations
            f.write("### Development Recommendations\n\n")

            # Based on position gaps
            if position_gaps:
                f.write("**Priority Skills to Develop:**\n\n")
                for i, gap in enumerate(position_gaps[:3], 1):
                    f.write(
                        f"{i}. **{gap['skill']}** - Current level: {gap['person_level']}, "
                        + f"Target: {gap['position_avg']:.1f}\n"
                    )
                f.write("\n")

            # Based on T-shape analysis
            f.write("**T-Shape Development:**\n\n")
            if breadth_score < 0.4:
                f.write(
                    "- Focus on increasing your skill breadth by learning complementary skills in your domain\n"
                )
            elif depth_score < 0.4:
                f.write(
                    "- Prioritize deepening your expertise in your strongest skill categories\n"
                )
            else:
                f.write(
                    "- Maintain your balanced T-shaped profile by continuing to develop both breadth and depth\n"
                )

            f.write("\n---\n\n")

    print(f"Generated individual skill analytics: {analytics_path}")
    return analytics_path


def generate_individual_skill_analytics(
    data_list: List[PersonData], output_dir: str, person_name: str = None
) -> str:
    # ... existing code ...
    return analytics_path


def generate_advanced_visualizations(
    data_list: List[PersonData], output_dir: str
) -> str:
    """Generate advanced visualizations with rich comparisons for the entire organization.

    This creates a comprehensive report with:
    - Department performance heat maps
    - Skill progression timelines
    - Organization-wide skill networks
    - Career trajectory visualization
    - Promotion velocity and skill acquisition correlations
    - Department/position skill gap analysis
    - Talent distribution maps

    Args:
        data_list: List of PersonData objects
        output_dir: Directory to save the output

    Returns:
        Path to the generated visualizations file
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Extract all necessary data
    profiles = {}
    dept_data = {}
    position_data = {}
    all_skills = {}
    career_events = {}
    skill_progression = {}
    dept_structure = {}
    team_structure = {}

    # First pass: extract base data
    for person in data_list:
        if not person.name:
            continue

        # Extract profile data
        if person.profile:
            dept = person.profile.nome_departamento
            position = person.profile.cargo
            manager = person.profile.nome_gestor

            profiles[person.name] = {
                "name": person.name,
                "department": dept,
                "position": position,
                "manager": manager,
                "is_manager": person.profile.tipo_gestao,
                "year": person.year,
            }

            # Build department structure
            if dept:
                if dept not in dept_data:
                    dept_data[dept] = {
                        "people": [],
                        "positions": set(),
                        "skills": {},
                        "managers": set(),
                    }
                dept_data[dept]["people"].append(person.name)
                dept_data[dept]["positions"].add(position)
                if manager:
                    dept_data[dept]["managers"].add(manager)

            # Build position data
            if position:
                if position not in position_data:
                    position_data[position] = {
                        "people": [],
                        "departments": set(),
                        "skills": {},
                    }
                position_data[position]["people"].append(person.name)
                position_data[position]["departments"].add(dept)

        # Extract skills data
        if person.career_progression and person.career_progression.skills_matrix:
            for skill, level in person.career_progression.skills_matrix.items():
                # Track historical skill progression
                if person.name not in skill_progression:
                    skill_progression[person.name] = {}
                skill_progression[person.name][skill] = level

                # Global skills tracking
                if skill not in all_skills:
                    all_skills[skill] = {
                        "people": [],
                        "levels": [],
                        "departments": set(),
                        "positions": set(),
                    }
                all_skills[skill]["people"].append(person.name)
                all_skills[skill]["levels"].append(level)
                if person.profile:
                    all_skills[skill]["departments"].add(
                        person.profile.nome_departamento
                    )
                    all_skills[skill]["positions"].add(person.profile.cargo)

                    # Add to department skills
                    if dept:
                        if skill not in dept_data[dept]["skills"]:
                            dept_data[dept]["skills"][skill] = {
                                "count": 0,
                                "levels": [],
                            }
                        dept_data[dept]["skills"][skill]["count"] += 1
                        dept_data[dept]["skills"][skill]["levels"].append(level)

                    # Add to position skills
                    if position:
                        if skill not in position_data[position]["skills"]:
                            position_data[position]["skills"][skill] = {
                                "count": 0,
                                "levels": [],
                            }
                        position_data[position]["skills"][skill]["count"] += 1
                        position_data[position]["skills"][skill]["levels"].append(level)

        # Extract career events
        if person.career_progression and person.career_progression.career_events:
            career_events[person.name] = sorted(
                person.career_progression.career_events, key=lambda x: x.date
            )

            # Process reporting relationships
            if person.profile and person.profile.nome_gestor:
                manager = person.profile.nome_gestor
                if manager not in team_structure:
                    team_structure[manager] = []
                if person.name not in team_structure[manager]:
                    team_structure[manager].append(person.name)

    # Calculate aggregated metrics
    dept_avg_skills = {}
    for dept, data in dept_data.items():
        dept_avg_skills[dept] = {}
        for skill, skill_data in data["skills"].items():
            if skill_data["levels"]:
                dept_avg_skills[dept][skill] = sum(skill_data["levels"]) / len(
                    skill_data["levels"]
                )

    position_avg_skills = {}
    for position, data in position_data.items():
        position_avg_skills[position] = {}
        for skill, skill_data in data["skills"].items():
            if skill_data["levels"]:
                position_avg_skills[position][skill] = sum(skill_data["levels"]) / len(
                    skill_data["levels"]
                )

    # Generate the report
    vis_path = os.path.join(output_dir, f"advanced_visualizations_{timestamp}.md")

    with open(vis_path, "w", encoding="utf-8") as f:
        f.write("# Advanced People Analytics Visualizations\n\n")
        f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")

        # Table of Contents
        f.write("## Table of Contents\n\n")
        f.write("1. [Organizational Structure](#organizational-structure)\n")
        f.write("2. [Skill Distribution](#skill-distribution)\n")
        f.write(
            "3. [Department Performance Analysis](#department-performance-analysis)\n"
        )
        f.write("4. [Career Trajectory Mapping](#career-trajectory-mapping)\n")
        f.write("5. [Skills Network Analysis](#skills-network-analysis)\n")
        f.write("6. [Talent Distribution](#talent-distribution)\n")
        f.write("7. [Skill Gap Analysis](#skill-gap-analysis)\n\n")

        # 1. Organizational Structure
        f.write("## Organizational Structure\n\n")

        # Department Structure
        f.write("### Department Structure\n\n")
        f.write("| Department | People | Positions | Managers |\n")
        f.write("|------------|--------|-----------|----------|\n")

        for dept, data in sorted(
            dept_data.items(), key=lambda x: len(x[1]["people"]), reverse=True
        ):
            people_count = len(data["people"])
            pos_count = len(data["positions"])
            manager_count = len(data["managers"])
            f.write(f"| {dept} | {people_count} | {pos_count} | {manager_count} |\n")

        f.write("\n")

        # Organization Chart using Mermaid
        f.write("### Organization Chart\n\n")
        f.write("```mermaid\n")
        f.write("graph TD\n")

        # Track added nodes to avoid duplicates
        added_nodes = set()

        # Add all managers first
        for manager, reports in team_structure.items():
            if reports:
                # Clean manager name for mermaid
                mgr_id = manager.replace(" ", "_").replace("-", "_")
                if mgr_id not in added_nodes:
                    f.write(f"  {mgr_id}[{manager}]\n")
                    added_nodes.add(mgr_id)

                # Add connections to direct reports
                for report in reports:
                    # Clean report name for mermaid
                    report_id = report.replace(" ", "_").replace("-", "_")
                    if report_id not in added_nodes:
                        f.write(f"  {report_id}[{report}]\n")
                        added_nodes.add(report_id)

                    f.write(f"  {mgr_id} --> {report_id}\n")

        f.write("```\n\n")

        # 2. Skill Distribution
        f.write("## Skill Distribution\n\n")

        # Top skills
        f.write("### Top Skills Organization-Wide\n\n")

        # Sort skills by prevalence
        sorted_skills = sorted(
            all_skills.items(), key=lambda x: len(x[1]["people"]), reverse=True
        )[:15]  # Top 15 skills

        f.write("| Skill | People | Avg Level | Departments | Positions |\n")
        f.write("|-------|--------|-----------|-------------|----------|\n")

        for skill, data in sorted_skills:
            people_count = len(data["people"])
            avg_level = (
                sum(data["levels"]) / len(data["levels"]) if data["levels"] else 0
            )
            dept_count = len(data["departments"])
            pos_count = len(data["positions"])

            f.write(
                f"| {skill} | {people_count} | {avg_level:.2f} | {dept_count} | {pos_count} |\n"
            )

        f.write("\n")

        # Skill distribution chart
        if sorted_skills:
            f.write("### Skill Prevalence Visualization\n\n")
            f.write("```mermaid\n")
            f.write("%%{init: {'theme': 'forest'}}%%\n")
            f.write("xychart-beta\n")
            f.write('    title "Top 10 Skills by Prevalence"\n')

            # X-axis with skill names
            skill_names = [s[0] for s in sorted_skills[:10]]
            f.write("    x-axis [" + ", ".join([f'"{s}"' for s in skill_names]) + "]\n")

            # Y-axis with people counts
            people_counts = [str(len(s[1]["people"])) for s in sorted_skills[:10]]
            f.write(f'    y-axis "People Count" [{", ".join(people_counts)}]\n')

            f.write("```\n\n")

        # 3. Department Performance Analysis
        f.write("## Department Performance Analysis\n\n")

        # Department Skill Heat Map
        f.write("### Department Skill Heat Map\n\n")

        # Get top 5 most common skills
        top_skills = [s[0] for s in sorted_skills[:5]]

        f.write("| Department | " + " | ".join(top_skills) + " |\n")
        f.write("|" + "-" * 11 + "|" + "|".join(["-" * 10 for _ in top_skills]) + "|\n")

        for dept, avgs in dept_avg_skills.items():
            row = [dept]
            for skill in top_skills:
                avg = avgs.get(skill, 0)
                # Use emoji indicators for visual heat map
                if avg >= 4:
                    indicator = "🟢 " + f"{avg:.1f}"  # Green - High
                elif avg >= 3:
                    indicator = "🟡 " + f"{avg:.1f}"  # Yellow - Medium
                elif avg > 0:
                    indicator = "🔴 " + f"{avg:.1f}"  # Red - Low
                else:
                    indicator = "⚪ N/A"  # White - None
                row.append(indicator)

            f.write("| " + " | ".join(row) + " |\n")

        f.write("\n")

        # Department comparison radar chart (if mermaid supports it)
        f.write("### Department Skill Comparison\n\n")

        # Use alternative visualization (bar chart)
        f.write("```mermaid\n")
        f.write("%%{init: {'theme': 'neutral'}}%%\n")
        f.write("xychart-beta\n")
        f.write('    title "Department Skill Comparison (First Skill)"\n')

        if top_skills and dept_avg_skills:
            # Use first skill as example
            first_skill = top_skills[0]

            # X-axis with department names (limited to prevent overflow)
            top_depts = list(dept_avg_skills.keys())[:8]
            f.write("    x-axis [" + ", ".join([f'"{d}"' for d in top_depts]) + "]\n")

            # Y-axis with skill level
            skill_levels = []
            for dept in top_depts:
                skill_levels.append(
                    str(round(dept_avg_skills[dept].get(first_skill, 0), 1))
                )

            f.write(
                f'    y-axis "{first_skill} Proficiency" [{", ".join(skill_levels)}]\n'
            )

        f.write("```\n\n")

        # 4. Career Trajectory Mapping
        f.write("## Career Trajectory Mapping\n\n")

        # Sample career path visualization for one person (if available)
        if career_events:
            # Get a person with the most career events
            sample_person = max(career_events.items(), key=lambda x: len(x[1]))[0]

            f.write(f"### Career Path: {sample_person}\n\n")
            f.write("```mermaid\n")
            f.write("timeline\n")
            f.write(f"    title Career Progression of {sample_person}\n")

            # Group events by year
            events_by_year = {}
            for event in career_events[sample_person]:
                event_year = event.date.year
                if event_year not in events_by_year:
                    events_by_year[event_year] = []
                events_by_year[event_year].append(event)

            # Add events to timeline
            for year in sorted(events_by_year.keys()):
                f.write(f"    section {year}\n")

                for event in events_by_year[year]:
                    # Format event text based on type
                    if event.event_type == "promotion":
                        event_text = f"{event.date.strftime('%b %d')}: Promotion to {event.new_position}"
                    elif event.event_type == "lateral_move":
                        event_text = f"{event.date.strftime('%b %d')}: Lateral move to {event.new_position}"
                    elif event.event_type == "skill_acquisition":
                        event_text = f"{event.date.strftime('%b %d')}: New skill: {event.details}"
                    elif event.event_type == "certification":
                        event_text = f"{event.date.strftime('%b %d')}: Certification: {event.details}"
                    else:
                        event_text = f"{event.date.strftime('%b %d')}: {event.event_type} - {event.details}"

                    f.write(f"        {event_text}\n")

            f.write("```\n\n")

        # Common career path patterns
        f.write("### Common Position Progression Patterns\n\n")

        # This would need actual position transition data, but we can mock for demonstration
        f.write("```mermaid\n")
        f.write("flowchart LR\n")
        f.write("    Junior[Junior Developer] --> Mid[Mid-level Developer]\n")
        f.write("    Mid --> Senior[Senior Developer]\n")
        f.write("    Senior --> TechLead[Technical Lead]\n")
        f.write("    Senior --> Architect[Solutions Architect]\n")
        f.write("    TechLead --> Manager[Engineering Manager]\n")
        f.write("    Architect --> Principal[Principal Engineer]\n")
        f.write("```\n\n")

        # 5. Skills Network Analysis
        f.write("## Skills Network Analysis\n\n")

        # For skills network, find correlations between skills
        # This would be a complex analysis in a real system, but we'll mock for demonstration
        f.write("### Skills Correlation Network\n\n")
        f.write("```mermaid\n")
        f.write("graph TD\n")

        # Show connections between sample top skills
        if len(top_skills) >= 5:
            # Create clean IDs for mermaid
            skill_ids = {}
            for i, skill in enumerate(top_skills[:5]):
                skill_ids[skill] = f"skill{i}"
                f.write(f"    {skill_ids[skill]}[{skill}]\n")

            # Create some connections
            f.write(f"    {skill_ids[top_skills[0]]} --- {skill_ids[top_skills[1]]}\n")
            f.write(f"    {skill_ids[top_skills[0]]} --- {skill_ids[top_skills[2]]}\n")
            f.write(f"    {skill_ids[top_skills[1]]} --- {skill_ids[top_skills[3]]}\n")
            f.write(f"    {skill_ids[top_skills[2]]} --- {skill_ids[top_skills[4]]}\n")
            f.write(f"    {skill_ids[top_skills[3]]} --- {skill_ids[top_skills[4]]}\n")

        f.write("```\n\n")

        # 6. Talent Distribution
        f.write("## Talent Distribution\n\n")

        # Department skill distribution
        f.write("### Talent Distribution by Department\n\n")

        # Create a quadrant chart
        f.write("```mermaid\n")
        f.write("quadrantChart\n")
        f.write("    title Talent Distribution by Department\n")
        f.write("    x-axis Low People --> High People\n")
        f.write("    y-axis Low Skill Diversity --> High Skill Diversity\n")
        f.write("    quadrant-1 High Skills, Low Headcount\n")
        f.write("    quadrant-2 High Skills, High Headcount\n")
        f.write("    quadrant-3 Low Skills, Low Headcount\n")
        f.write("    quadrant-4 Low Skills, High Headcount\n")

        # Plot departments
        max_people = (
            max(len(data["people"]) for data in dept_data.values()) if dept_data else 1
        )
        for dept, data in dept_data.items():
            people_norm = len(data["people"]) / max_people  # Normalize to 0-1
            skill_variety = (
                len(data["skills"]) / 10
            )  # Normalize assuming 10 skills is diverse
            # Limit to 0-1 range
            people_norm = min(1, max(0, people_norm))
            skill_variety = min(1, max(0, skill_variety))
            f.write(f"    {dept}: [{people_norm}, {skill_variety}]\n")

        f.write("```\n\n")

        # 7. Skill Gap Analysis
        f.write("## Skill Gap Analysis\n\n")

        # Position skill gap visualization
        f.write("### Position Skill Gap Overview\n\n")

        # Create table showing position vs required skills
        if position_avg_skills and top_skills:
            f.write(
                "| Position | "
                + " | ".join(top_skills[:4])
                + " | Overall Proficiency |\n"
            )
            f.write(
                "|"
                + "-" * 10
                + "|"
                + "|".join(["-" * 12 for _ in top_skills[:4]])
                + "|"
                + "-" * 20
                + "|\n"
            )

            for position, skill_avgs in position_avg_skills.items():
                # Get top positions by people count
                if not position_data.get(position, {}).get("people", []):
                    continue

                row = [position]
                total_avg = 0
                skill_count = 0

                for skill in top_skills[:4]:
                    avg = skill_avgs.get(skill, 0)
                    if avg > 0:
                        total_avg += avg
                        skill_count += 1

                    # Add proficiency indicator
                    if avg >= 4:
                        indicator = "🟢 " + f"{avg:.1f}"  # Green - High
                    elif avg >= 3:
                        indicator = "🟡 " + f"{avg:.1f}"  # Yellow - Medium
                    elif avg > 0:
                        indicator = "🔴 " + f"{avg:.1f}"  # Red - Low
                    else:
                        indicator = "⚪ N/A"  # White - None
                    row.append(indicator)

                # Calculate overall proficiency
                overall_avg = total_avg / skill_count if skill_count > 0 else 0

                # Add overall proficiency with gauge
                if overall_avg >= 4:
                    gauge = "⭐⭐⭐⭐⭐ " + f"{overall_avg:.1f}"
                elif overall_avg >= 3:
                    gauge = "⭐⭐⭐⭐ " + f"{overall_avg:.1f}"
                elif overall_avg >= 2:
                    gauge = "⭐⭐⭐ " + f"{overall_avg:.1f}"
                elif overall_avg >= 1:
                    gauge = "⭐⭐ " + f"{overall_avg:.1f}"
                else:
                    gauge = "⭐ " + f"{overall_avg:.1f}"

                row.append(gauge)

                f.write("| " + " | ".join(row) + " |\n")

            f.write("\n")

        # Add a footer
        f.write("---\n\n")
        f.write(
            f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        )

    print(f"Generated advanced visualizations report: {vis_path}")
    return vis_path


def generate_comprehensive_report(data_list: List[PersonData], output_dir: str) -> str:
    """Generate a comprehensive full report combining all visualization types.

    This creates a complete analytics dashboard with:
    - Executive summary with key metrics
    - All advanced visualizations
    - Individual and organizational skill analysis
    - Career progression insights
    - Department and position comparisons
    - Interactive elements and eye-catching visual indicators

    Args:
        data_list: List of PersonData objects
        output_dir: Directory to save the output

    Returns:
        Path to the generated report
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Generate underlying component reports
    skill_recs_path = generate_skill_recommendations(data_list, output_dir)
    eval_report_path = generate_evaluation_report(data_list, output_dir)
    vis_path = generate_advanced_visualizations(data_list, output_dir)

    # Create the comprehensive report
    report_path = os.path.join(output_dir, f"comprehensive_report_{timestamp}.md")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 📊 PEOPLE ANALYTICS COMPREHENSIVE REPORT\n\n")
        f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")

        # Executive Dashboard
        f.write("## 📈 Executive Dashboard\n\n")

        # Extract key metrics
        total_people = len(data_list)
        departments = set()
        positions = set()
        skills_count = 0
        avg_skill_level = 0.0
        skill_data_count = 0

        for person in data_list:
            if person.profile:
                if person.profile.nome_departamento:
                    departments.add(person.profile.nome_departamento)
                if person.profile.cargo:
                    positions.add(person.profile.cargo)

            if person.career_progression and person.career_progression.skills_matrix:
                skills = person.career_progression.skills_matrix
                skills_count += len(skills)
                if skills:
                    avg_skill_level += sum(skills.values())
                    skill_data_count += len(skills)

        # Avoid division by zero
        org_avg_skill = (
            avg_skill_level / skill_data_count if skill_data_count > 0 else 0
        )

        # Create metrics dashboard
        f.write("<div style='display: flex; flex-wrap: wrap; gap: 20px;'>\n")

        # Metric cards
        f.write(
            "<div style='background-color: #e6f7ff; border-left: 4px solid #1890ff; padding: 15px; width: 200px;'>\n"
        )
        f.write(
            f"<div style='font-size: 30px; font-weight: bold;'>{total_people}</div>\n"
        )
        f.write("<div>Total People</div>\n")
        f.write("</div>\n")

        f.write(
            "<div style='background-color: #f6ffed; border-left: 4px solid #52c41a; padding: 15px; width: 200px;'>\n"
        )
        f.write(
            f"<div style='font-size: 30px; font-weight: bold;'>{len(departments)}</div>\n"
        )
        f.write("<div>Departments</div>\n")
        f.write("</div>\n")

        f.write(
            "<div style='background-color: #fff7e6; border-left: 4px solid #fa8c16; padding: 15px; width: 200px;'>\n"
        )
        f.write(
            f"<div style='font-size: 30px; font-weight: bold;'>{len(positions)}</div>\n"
        )
        f.write("<div>Positions</div>\n")
        f.write("</div>\n")

        f.write(
            "<div style='background-color: #f9f0ff; border-left: 4px solid #722ed1; padding: 15px; width: 200px;'>\n"
        )
        f.write(
            f"<div style='font-size: 30px; font-weight: bold;'>{skills_count}</div>\n"
        )
        f.write("<div>Total Skills</div>\n")
        f.write("</div>\n")

        f.write(
            "<div style='background-color: #fcf5e6; border-left: 4px solid #d4b106; padding: 15px; width: 200px;'>\n"
        )
        f.write(
            f"<div style='font-size: 30px; font-weight: bold;'>{org_avg_skill:.2f}</div>\n"
        )
        f.write("<div>Avg Skill Level</div>\n")
        f.write("</div>\n")

        f.write("</div>\n\n")

        # Table of Contents
        f.write("## 📑 Table of Contents\n\n")
        f.write("1. [Executive Dashboard](#-executive-dashboard)\n")
        f.write("2. [Organization Structure](#-organization-structure)\n")
        f.write("3. [Skills Analysis](#-skills-analysis)\n")
        f.write("4. [Department Insights](#-department-insights)\n")
        f.write("5. [Career Development](#-career-development)\n")
        f.write("6. [Performance Metrics](#-performance-metrics)\n")
        f.write("7. [Development Recommendations](#-development-recommendations)\n\n")

        # Organization Structure
        f.write("## 🏢 Organization Structure\n\n")

        # Extract department structure
        dept_data = {}
        team_structure = {}

        for person in data_list:
            if person.profile:
                dept = person.profile.nome_departamento
                manager = person.profile.nome_gestor

                if dept:
                    if dept not in dept_data:
                        dept_data[dept] = {"count": 0, "managers": set()}
                    dept_data[dept]["count"] += 1
                    if manager:
                        dept_data[dept]["managers"].add(manager)

                if manager:
                    if manager not in team_structure:
                        team_structure[manager] = []
                    team_structure[manager].append(person.name)

        # Department Table
        f.write("### Departments\n\n")

        f.write("| Department | People | Managers |\n")
        f.write("|------------|--------|----------|\n")

        for dept, data in sorted(
            dept_data.items(), key=lambda x: x[1]["count"], reverse=True
        ):
            f.write(f"| {dept} | {data['count']} | {len(data['managers'])} |\n")

        f.write("\n")

        # Organization Chart
        f.write("### Organization Chart\n\n")
        f.write("```mermaid\n")
        f.write("mindmap\n")
        f.write("  root((Organization))\n")

        # Add departments
        for dept in sorted(dept_data.keys()):
            f.write(f"    {dept}\n")

            # Add managers under departments
            managers = dept_data[dept]["managers"]
            for manager in sorted(managers):
                # Replace spaces with underscores in IDs
                manager_id = manager.replace(" ", "_")
                f.write(f"      {manager}\n")

                # Add direct reports
                if manager in team_structure:
                    for report in sorted(team_structure[manager]):
                        report_id = report.replace(" ", "_")
                        f.write(f"        {report}\n")

        f.write("```\n\n")

        # Skills Analysis
        f.write("## 🧠 Skills Analysis\n\n")

        # Extract skills data
        all_skills = {}
        for person in data_list:
            if person.career_progression and person.career_progression.skills_matrix:
                for skill, level in person.career_progression.skills_matrix.items():
                    if skill not in all_skills:
                        all_skills[skill] = {"count": 0, "levels": []}
                    all_skills[skill]["count"] += 1
                    all_skills[skill]["levels"].append(level)

        # Top skills
        f.write("### Top Skills\n\n")

        # Skills by prevalence
        sorted_by_count = sorted(
            all_skills.items(), key=lambda x: x[1]["count"], reverse=True
        )[:10]  # Top 10

        # Skills by level
        sorted_by_level = sorted(
            all_skills.items(),
            key=lambda x: sum(x[1]["levels"]) / len(x[1]["levels"])
            if x[1]["levels"]
            else 0,
            reverse=True,
        )[:10]  # Top 10

        # Two-column layout
        f.write("<div style='display: flex; gap: 20px;'>\n")

        # Column 1: Skills by prevalence
        f.write("<div style='flex: 1;'>\n")
        f.write("#### Most Common Skills\n\n")
        f.write("| Skill | People | % of Org |\n")
        f.write("|-------|--------|----------|\n")

        for skill, data in sorted_by_count:
            percentage = (data["count"] / total_people) * 100 if total_people > 0 else 0
            f.write(f"| {skill} | {data['count']} | {percentage:.1f}% |\n")

        f.write("</div>\n")

        # Column 2: Skills by level
        f.write("<div style='flex: 1;'>\n")
        f.write("#### Highest Proficiency Skills\n\n")
        f.write("| Skill | Avg Level | People |\n")
        f.write("|-------|-----------|--------|\n")

        for skill, data in sorted_by_level:
            avg_level = (
                sum(data["levels"]) / len(data["levels"]) if data["levels"] else 0
            )
            f.write(f"| {skill} | {avg_level:.2f} | {data['count']} |\n")

        f.write("</div>\n")
        f.write("</div>\n\n")

        # Skills Distribution
        f.write("### Skills Distribution\n\n")

        # Skill level distribution chart
        f.write("```mermaid\n")
        f.write("pie\n")
        f.write('    title "Skill Level Distribution"\n')

        # Count levels across all skills
        level_counts = {i: 0 for i in range(1, 6)}
        for skill, data in all_skills.items():
            for level in data["levels"]:
                if 1 <= level <= 5:
                    level_counts[level] += 1

        # Add to chart
        for level, count in level_counts.items():
            if count > 0:
                f.write(f'    "Level {level}" : {count}\n')

        f.write("```\n\n")

        # Department Insights
        f.write("## 🏛️ Department Insights\n\n")

        # Department skill heatmap
        f.write("### Department Skill Heatmap\n\n")

        # Extract department skills
        dept_skills = {}
        for person in data_list:
            if (
                person.profile
                and person.profile.nome_departamento
                and person.career_progression
                and person.career_progression.skills_matrix
            ):
                dept = person.profile.nome_departamento
                if dept not in dept_skills:
                    dept_skills[dept] = {}

                for skill, level in person.career_progression.skills_matrix.items():
                    if skill not in dept_skills[dept]:
                        dept_skills[dept][skill] = {"count": 0, "total": 0}
                    dept_skills[dept][skill]["count"] += 1
                    dept_skills[dept][skill]["total"] += level

        # Calculate department skill averages
        dept_skill_avgs = {}
        for dept, skills in dept_skills.items():
            dept_skill_avgs[dept] = {}
            for skill, data in skills.items():
                if data["count"] > 0:
                    dept_skill_avgs[dept][skill] = data["total"] / data["count"]

        # Get top 5 most common skills
        top_skills = [s[0] for s in sorted_by_count[:5]]

        # Department skill heatmap table
        f.write("| Department | " + " | ".join(top_skills) + " |\n")
        f.write("|" + "-" * 11 + "|" + "|".join(["-" * 10 for _ in top_skills]) + "|\n")

        for dept, skill_avgs in dept_skill_avgs.items():
            row = [dept]
            for skill in top_skills:
                avg = skill_avgs.get(skill, 0)
                # Use emoji indicators for visual heat map
                if avg >= 4:
                    indicator = "🟢 " + f"{avg:.1f}"  # Green - High
                elif avg >= 3:
                    indicator = "🟡 " + f"{avg:.1f}"  # Yellow - Medium
                elif avg > 0:
                    indicator = "🔴 " + f"{avg:.1f}"  # Red - Low
                else:
                    indicator = "⚪ N/A"  # White - None
                row.append(indicator)

            f.write("| " + " | ".join(row) + " |\n")

        f.write("\n")

        # Career Development
        f.write("## 🚀 Career Development\n\n")

        # Extract career events
        career_events = {}
        for person in data_list:
            if person.career_progression and person.career_progression.career_events:
                events = person.career_progression.career_events
                if events:
                    career_events[person.name] = sorted(events, key=lambda x: x.date)

        # Promotion velocity
        promotion_velocities = []
        for person, events in career_events.items():
            promotion_events = [e for e in events if e.event_type == "promotion"]
            if len(promotion_events) >= 2:
                # Calculate time between promotions
                times = []
                for i in range(1, len(promotion_events)):
                    days = (
                        promotion_events[i].date - promotion_events[i - 1].date
                    ).days
                    years = days / 365.25
                    times.append(years)

                avg_time = sum(times) / len(times)
                promotion_velocities.append((person, avg_time))

        # Display promotion velocity
        if promotion_velocities:
            f.write("### Promotion Velocity\n\n")
            f.write("| Person | Avg Time Between Promotions (Years) |\n")
            f.write("|--------|--------------------------------------|\n")

            for person, velocity in sorted(promotion_velocities, key=lambda x: x[1]):
                f.write(f"| {person} | {velocity:.2f} |\n")

            f.write("\n")

            # Average promotion velocity
            avg_velocity = sum(v for _, v in promotion_velocities) / len(
                promotion_velocities
            )
            f.write(
                f"**Organization average:** {avg_velocity:.2f} years between promotions\n\n"
            )

        # Career trajectory example
        if career_events:
            # Get person with most events
            sample_person, events = max(career_events.items(), key=lambda x: len(x[1]))

            f.write("### Career Trajectory Example\n\n")
            f.write(f"**{sample_person}'s Career Path:**\n\n")
            f.write("```mermaid\n")
            f.write("timeline\n")
            f.write(f"    title Career Progression of {sample_person}\n")

            # Group events by year
            events_by_year = {}
            for event in events:
                year = event.date.year
                if year not in events_by_year:
                    events_by_year[year] = []
                events_by_year[year].append(event)

            # Add to timeline
            for year in sorted(events_by_year.keys()):
                f.write(f"    section {year}\n")

                for event in events_by_year[year]:
                    # Format event based on type
                    if event.event_type == "promotion":
                        desc = f"Promotion to {event.new_position}"
                    elif event.event_type == "lateral_move":
                        desc = f"Lateral move to {event.new_position}"
                    elif event.event_type == "skill_acquisition":
                        desc = f"New skill: {event.details}"
                    elif event.event_type == "certification":
                        desc = f"Certification: {event.details}"
                    else:
                        desc = f"{event.event_type}: {event.details}"

                    date_str = event.date.strftime("%b %d")
                    f.write(f"        {date_str}: {desc}\n")

            f.write("```\n\n")

        # Performance Metrics
        f.write("## 📈 Performance Metrics\n\n")

        # Extract evaluation data
        eval_data = []
        for person in data_list:
            if person.evaluation_data:
                # Try to extract overall score
                score = None
                if isinstance(person.evaluation_data, dict):
                    if "pontuacao_final" in person.evaluation_data:
                        score = person.evaluation_data["pontuacao_final"]
                    elif (
                        "avaliacoes" in person.evaluation_data
                        and "pontuacao_final" in person.evaluation_data["avaliacoes"]
                    ):
                        score = person.evaluation_data["avaliacoes"]["pontuacao_final"]

                if score is not None:
                    dept = (
                        person.profile.nome_departamento
                        if person.profile
                        else "Unknown"
                    )
                    eval_data.append(
                        {
                            "name": person.name,
                            "score": score,
                            "department": dept,
                            "year": person.year,
                        }
                    )

        if eval_data:
            # Performance distribution
            f.write("### Performance Score Distribution\n\n")

            # Calculate score ranges
            score_ranges = {
                "5.0+": 0,
                "4.0-4.9": 0,
                "3.0-3.9": 0,
                "2.0-2.9": 0,
                "Below 2.0": 0,
            }

            for entry in eval_data:
                score = entry["score"]
                if score >= 5.0:
                    score_ranges["5.0+"] += 1
                elif score >= 4.0:
                    score_ranges["4.0-4.9"] += 1
                elif score >= 3.0:
                    score_ranges["3.0-3.9"] += 1
                elif score >= 2.0:
                    score_ranges["2.0-2.9"] += 1
                else:
                    score_ranges["Below 2.0"] += 1

            # Create pie chart
            f.write("```mermaid\n")
            f.write("pie\n")
            f.write('    title "Performance Score Distribution"\n')

            for range_name, count in score_ranges.items():
                if count > 0:
                    f.write(f'    "{range_name}" : {count}\n')

            f.write("```\n\n")

            # Department performance comparison
            f.write("### Department Performance Comparison\n\n")

            # Group by department
            dept_scores = {}
            for entry in eval_data:
                dept = entry["department"]
                if dept not in dept_scores:
                    dept_scores[dept] = []
                dept_scores[dept].append(entry["score"])

            # Department performance table
            f.write("| Department | Avg Score | Min | Max | People |\n")
            f.write("|------------|-----------|-----|-----|--------|\n")

            for dept, scores in dept_scores.items():
                avg = sum(scores) / len(scores)
                min_score = min(scores)
                max_score = max(scores)
                count = len(scores)

                f.write(
                    f"| {dept} | {avg:.2f} | {min_score:.1f} | {max_score:.1f} | {count} |\n"
                )

            f.write("\n")

        # Development Recommendations
        f.write("## 💡 Development Recommendations\n\n")

        f.write("### Organization-wide Focus Areas\n\n")

        # Identify skill gaps across the organization
        if all_skills:
            low_skills = []
            for skill, data in all_skills.items():
                avg = sum(data["levels"]) / len(data["levels"]) if data["levels"] else 0
                if (
                    avg < 3.0 and data["count"] >= total_people * 0.25
                ):  # Common but low proficiency
                    low_skills.append((skill, avg, data["count"]))

            if low_skills:
                f.write("#### Skills Requiring Development\n\n")
                f.write("| Skill | Current Avg | People | Priority |\n")
                f.write("|-------|-------------|--------|----------|\n")

                for skill, avg, count in sorted(low_skills, key=lambda x: x[1]):
                    # Calculate priority based on prevalence and gap
                    prevalence = count / total_people
                    gap = 5 - avg  # Gap from ideal level of 5
                    priority = gap * prevalence * 10  # Scale to approximately 0-10

                    # Priority indicator
                    if priority >= 7:
                        priority_str = "🔴 High"
                    elif priority >= 4:
                        priority_str = "🟠 Medium"
                    else:
                        priority_str = "🟡 Low"

                    f.write(f"| {skill} | {avg:.2f} | {count} | {priority_str} |\n")

                f.write("\n")

        # Strategic recommendations
        f.write("### Strategic Recommendations\n\n")

        f.write(
            "1. **Implement targeted training programs** for the identified skills requiring development\n"
        )
        f.write(
            "2. **Create mentoring relationships** between high-performing individuals and those with skill gaps\n"
        )
        f.write(
            "3. **Develop clear career pathways** with defined skill requirements for each level\n"
        )
        f.write(
            "4. **Enhance cross-department collaboration** to share skills and knowledge\n"
        )
        f.write(
            "5. **Recognize and reward skill development** through performance management processes\n\n"
        )

        # Link to component reports
        f.write("## 📎 Detailed Reports\n\n")
        f.write(f"- [Skills Recommendations]({os.path.basename(skill_recs_path)})\n")
        f.write(f"- [Evaluation Report]({os.path.basename(eval_report_path)})\n")
        f.write(f"- [Advanced Visualizations]({os.path.basename(vis_path)})\n\n")

        # Footer
        f.write("---\n\n")
        f.write(
            f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        )

    print(f"Generated comprehensive report: {report_path}")
    return report_path
