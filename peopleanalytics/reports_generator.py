import json
import os
from datetime import datetime
from typing import Any, Dict, List, Union

import matplotlib.pyplot as plt
import pandas as pd

from .data_model import PersonData


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

    elif report_type.lower() == "custom":
        if not isinstance(data, dict):
            raise ValueError(
                "Custom report requires a dictionary with report parameters"
            )
        return generate_custom_report(data, output_dir)

    else:
        raise ValueError(f"Unknown report type: {report_type}")


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
                    <h3>Data Summary</h3>""")

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

    # Process all people data
    for person in data_list:
        # Skip if no career progression data
        if not person.career_progression or not person.career_progression.skills_matrix:
            continue

        # Get department and position if profile exists
        dept = None
        position = None
        if person.profile:
            dept = person.profile.nome_departamento
            position = person.profile.cargo

            # Add to departments dict
            if dept:
                if dept not in departments:
                    departments[dept] = {}
                if position not in departments[dept]:
                    departments[dept][position] = []
                departments[dept][position].append(person.name)

            # Add to positions dict
            if position:
                if position not in positions:
                    positions[position] = {"count": 0, "skills": {}}
                positions[position]["count"] += 1

        # Process skills
        person_skills[person.name] = {}

        for skill, level in person.career_progression.skills_matrix.items():
            # Add to person's skills
            person_skills[person.name][skill] = level

            # Add to global skills
            if skill not in all_skills:
                all_skills[skill] = {
                    "count": 0,
                    "total_level": 0,
                    "by_position": {},
                    "by_department": {},
                }

            all_skills[skill]["count"] += 1
            all_skills[skill]["total_level"] += level

            # Add to position stats
            if position:
                if position not in all_skills[skill]["by_position"]:
                    all_skills[skill]["by_position"][position] = {
                        "count": 0,
                        "total_level": 0,
                    }
                all_skills[skill]["by_position"][position]["count"] += 1
                all_skills[skill]["by_position"][position]["total_level"] += level

                # Also update the positions dict
                if skill not in positions[position]["skills"]:
                    positions[position]["skills"][skill] = {
                        "count": 0,
                        "total_level": 0,
                    }
                positions[position]["skills"][skill]["count"] += 1
                positions[position]["skills"][skill]["total_level"] += level

            # Add to department stats
            if dept:
                if dept not in all_skills[skill]["by_department"]:
                    all_skills[skill]["by_department"][dept] = {
                        "count": 0,
                        "total_level": 0,
                    }
                all_skills[skill]["by_department"][dept]["count"] += 1
                all_skills[skill]["by_department"][dept]["total_level"] += level

    # Calculate averages and find common skills by position
    position_core_skills = {}
    for position, data in positions.items():
        if data["count"] >= 2:  # Only consider positions with at least 2 people
            skills_avg = {
                skill: stats["total_level"] / stats["count"]
                for skill, stats in data["skills"].items()
                if stats["count"]
                >= data["count"]
                * 0.5  # Skills that at least 50% of people in this position have
            }
            # Sort by average level
            position_core_skills[position] = sorted(
                skills_avg.items(), key=lambda x: x[1], reverse=True
            )

    # Generate skill gap analysis and recommendations
    recommendations = {}
    for person_name, skills in person_skills.items():
        # Find the person in the original data
        person_data = next((p for p in data_list if p.name == person_name), None)
        if not person_data or not person_data.profile:
            continue

        position = person_data.profile.cargo
        if position not in position_core_skills:
            continue

        # Find skill gaps - core skills for position that person doesn't have or has low level
        skill_gaps = []
        for skill, avg_level in position_core_skills[position]:
            if skill not in skills:
                skill_gaps.append(
                    {
                        "skill": skill,
                        "avg_level": avg_level,
                        "current_level": 0,
                        "gap": avg_level,
                    }
                )
            elif skills[skill] < avg_level - 0.5:  # At least 0.5 below average
                skill_gaps.append(
                    {
                        "skill": skill,
                        "avg_level": avg_level,
                        "current_level": skills[skill],
                        "gap": avg_level - skills[skill],
                    }
                )

        # Sort gaps by size
        skill_gaps.sort(key=lambda x: x["gap"], reverse=True)

        # Generate recommendations
        if skill_gaps:
            recommendations[person_name] = {
                "position": position,
                "skill_gaps": skill_gaps[:5],  # Top 5 gaps
                "recommended_learning_path": [gap["skill"] for gap in skill_gaps[:3]],
                "core_skills_mastered": sum(
                    1
                    for skill, avg in position_core_skills[position]
                    if skill in skills and skills[skill] >= avg
                ),
            }

    # Create recommendations markdown file
    recs_path = os.path.join(output_dir, f"skill_recommendations_{timestamp}.md")

    with open(recs_path, "w", encoding="utf-8") as f:
        f.write("# Skill Recommendations & Learning Paths\n\n")
        f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")

        # Table of Contents
        f.write("## Table of Contents\n\n")
        f.write("1. [Organization Skill Landscape](#organization-skill-landscape)\n")
        f.write("2. [Core Skills by Position](#core-skills-by-position)\n")
        f.write("3. [Individual Recommendations](#individual-recommendations)\n")
        f.write("4. [Learning Paths](#learning-paths)\n\n")

        # 1. Organization Skill Landscape
        f.write("## Organization Skill Landscape\n\n")

        # Top skills across organization
        if all_skills:
            # Calculate skill averages
            skill_avgs = {
                skill: data["total_level"] / data["count"]
                for skill, data in all_skills.items()
            }

            # Sort by frequency and then average level
            sorted_skills = sorted(
                all_skills.items(),
                key=lambda x: (x[1]["count"], skill_avgs[x[0]]),
                reverse=True,
            )

            f.write("### Top Skills by Prevalence\n\n")
            f.write("| Skill | People | Avg Level | Importance |\n")
            f.write("|-------|--------|-----------|------------|\n")

            for skill, data in sorted_skills[:15]:  # Top 15 skills
                avg_level = data["total_level"] / data["count"]
                prevalence = data["count"] / len(person_skills) * 100
                importance = prevalence * avg_level / 5  # Scaled importance metric

                f.write(
                    f"| {skill} | {data['count']} | {avg_level:.1f} | {importance:.1f}% |\n"
                )

            f.write("\n")

            # Add Mermaid chart for top skills
            f.write("### Top Skills Visualization\n\n")
            f.write("```mermaid\n")
            f.write("%%{init: {'theme': 'forest'}}%%\n")
            f.write("xychart-beta\n")
            f.write('    title "Top 10 Skills by Prevalence"\n')
            f.write("    x-axis [")

            # X-axis labels (skill names)
            top_10_skills = [skill for skill, _ in sorted_skills[:10]]
            x_labels = ", ".join([f'"{skill}"' for skill in top_10_skills])
            f.write(f"{x_labels}]\n")

            # Y-axis values (prevalence percentages)
            y_values = []
            for skill, data in sorted_skills[:10]:
                prevalence = data["count"] / len(person_skills) * 100
                y_values.append(str(round(prevalence, 1)))

            f.write(f'    y-axis "Prevalence (%)" [{", ".join(y_values)}]\n')
            f.write("```\n\n")

        # 2. Core Skills by Position
        f.write("## Core Skills by Position\n\n")

        for position, skills in position_core_skills.items():
            if skills:
                f.write(f"### {position}\n\n")
                f.write("| Skill | Avg Level | Importance |\n")
                f.write("|-------|-----------|------------|\n")

                for skill, avg_level in skills[:8]:  # Top 8 skills per position
                    # Calculate importance (arbitrary formula)
                    importance = min(100, avg_level * 20)  # Scale to percentage
                    f.write(f"| {skill} | {avg_level:.1f} | {importance:.0f}% |\n")

                f.write("\n")

        # 3. Individual Recommendations
        f.write("## Individual Recommendations\n\n")

        for person_name, recs in recommendations.items():
            f.write(f"### {person_name} ({recs['position']})\n\n")

            # Progress on core skills
            position = recs["position"]
            total_core_skills = len(position_core_skills.get(position, []))
            mastered = recs["core_skills_mastered"]

            if total_core_skills > 0:
                progress_pct = mastered / total_core_skills * 100
                f.write(
                    f"**Core Skills Progress:** {mastered}/{total_core_skills} ({progress_pct:.0f}%)\n\n"
                )

            # Skill gaps
            if recs["skill_gaps"]:
                f.write("#### Recommended Focus Areas\n\n")
                f.write("| Skill | Your Level | Target Level | Gap |\n")
                f.write("|-------|------------|--------------|-----|\n")

                for gap in recs["skill_gaps"]:
                    f.write(
                        f"| {gap['skill']} | {gap['current_level']:.1f} | {gap['avg_level']:.1f} | {gap['gap']:.1f} |\n"
                    )

                f.write("\n")

                # Learning path
                f.write("#### Suggested Learning Path\n\n")
                for i, skill in enumerate(recs["recommended_learning_path"], 1):
                    f.write(
                        f"{i}. **{skill}** - Focus on advancing skills with industry-standard frameworks and advanced techniques\n"
                    )

                f.write("\n")

        # 4. Learning Paths
        f.write("## Learning Paths\n\n")

        # Generic learning paths by common career trajectories
        # This is simplified - in a real system you'd analyze actual career progression data
        common_paths = {
            "Technical Leadership": [
                "Team Leadership",
                "Technical Mentoring",
                "Project Planning",
                "Architecture Design",
                "Code Review",
            ],
            "Specialist Track": [
                "Deep Domain Knowledge",
                "Performance Optimization",
                "Advanced Debugging",
                "Research & Innovation",
                "Technical Documentation",
            ],
            "Management Track": [
                "People Management",
                "Resource Allocation",
                "Performance Evaluation",
                "Strategic Planning",
                "Stakeholder Communication",
            ],
        }

        for path_name, skills in common_paths.items():
            f.write(f"### {path_name}\n\n")
            f.write("This career path focuses on the following skill progression:\n\n")

            for i, skill in enumerate(skills, 1):
                f.write(f"{i}. **{skill}**\n")

            f.write("\n")

            # Add recommended external resources
            f.write("#### Recommended Resources\n\n")
            f.write("- Professional certifications in relevant domains\n")
            f.write("- Industry conferences and workshops\n")
            f.write("- Mentorship programs\n")
            f.write("- Online courses and learning platforms\n\n")

        # Footer
        f.write("---\n\n")
        f.write(
            "*This report provides general recommendations based on organizational patterns. Individual career plans should be discussed with managers and tailored to personal goals.*\n"
        )

    print(f"Generated skill recommendations: {recs_path}")
    return recs_path
