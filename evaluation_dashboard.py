#!/usr/bin/env python3
import argparse
from datetime import datetime
from pathlib import Path

from analyze_evaluations import EvaluationAnalyzer
from generate_comparative_spreadsheet import ComparativeSpreadsheetGenerator
from generate_feedback import FeedbackGenerator


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluation Dashboard - Generate comprehensive evaluation reports"
    )
    parser.add_argument("input_dir", help="Directory containing evaluation data")
    parser.add_argument(
        "--output-dir",
        default="dashboard_output",
        help="Output directory for all reports",
    )
    parser.add_argument("--year", help="Specific year to analyze")
    parser.add_argument("--person", help="Specific person to analyze")
    parser.add_argument(
        "--all", action="store_true", help="Generate all possible reports"
    )
    parser.add_argument(
        "--skip-feedback", action="store_true", help="Skip feedback report generation"
    )
    parser.add_argument(
        "--skip-spreadsheet",
        action="store_true",
        help="Skip comparative spreadsheet generation",
    )
    parser.add_argument(
        "--skip-charts", action="store_true", help="Skip chart generation"
    )
    return parser.parse_args()


def ensure_dir(directory):
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def generate_charts(analyzer, output_dir, year=None, person=None):
    """Generate appropriate charts based on the input parameters"""
    charts_dir = ensure_dir(output_dir / "charts")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # If specific year is provided
    if year:
        print(f"Generating comparison chart for year {year}...")
        output_file = charts_dir / f"comparison_{year}_{timestamp}.png"
        analyzer.generate_comparative_chart(year, str(output_file))

    # If specific person is provided
    if person:
        print(f"Generating historical chart for {person}...")
        output_file = charts_dir / f"{person.replace(' ', '_')}_history_{timestamp}.png"
        analyzer.generate_historical_report(person, str(output_file))

    # If no specific parameters, generate overview charts
    if not year and not person:
        # Generate latest year comparison
        years = sorted(
            list(
                set([
                    y for p in analyzer.evaluations_by_person.values() for y in p.keys()
                ])
            )
        )
        if years:
            latest_year = years[-1]
            print(f"Generating comparison chart for latest year ({latest_year})...")
            output_file = charts_dir / f"latest_comparison_{timestamp}.png"
            analyzer.generate_comparative_chart(latest_year, str(output_file))

        # Generate historical charts for top performers
        comparison_df = analyzer.compare_people_for_year(latest_year)
        top_performers = (
            comparison_df.sort_values("Average Score", ascending=False)
            .head(2)["Person"]
            .tolist()
        )

        for person in top_performers:
            print(f"Generating historical chart for top performer {person}...")
            output_file = (
                charts_dir / f"{person.replace(' ', '_')}_history_{timestamp}.png"
            )
            analyzer.generate_historical_report(person, str(output_file))

    print(f"All charts saved to {charts_dir}")
    return charts_dir


def generate_feedback_reports(input_dir, output_dir, person=None):
    """Generate feedback reports for all people or a specific person"""
    feedback_dir = ensure_dir(output_dir / "feedback_reports")

    args = ["--output-dir", str(feedback_dir)]
    if person:
        args.extend(["--person", person])

    generator = FeedbackGenerator(input_dir, args)
    generator.generate()

    print(f"Feedback reports saved to {feedback_dir}")
    return feedback_dir


def generate_comparative_spreadsheet(input_dir, output_dir):
    """Generate a comparative spreadsheet with all evaluation data"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = output_dir / f"comparative_{timestamp}.xlsx"

    generator = ComparativeSpreadsheetGenerator(input_dir, str(output_file))
    generator.generate()

    print(f"Comparative spreadsheet saved to {output_file}")
    return output_file


def generate_summary_insights(analyzer, output_dir):
    """Generate a summary insights report"""
    summary_file = output_dir / "summary_insights.md"

    # Get all available years
    years = []
    for person, data in analyzer.evaluations_by_person.items():
        years.extend(data.keys())
    years = sorted(list(set(years)))

    latest_year = years[-1] if years else None
    if not latest_year:
        print("No evaluation data found")
        return

    # Get comparison data for latest year
    comparison_df = analyzer.compare_people_for_year(latest_year)
    comparison_df = comparison_df.sort_values("Average Score", ascending=False)

    # Get improvement data
    improvement_data = []
    for person in analyzer.evaluations_by_person.keys():
        person_years = analyzer.get_person_years(person)
        if len(person_years) < 2:
            continue

        first_year = person_years[0]
        last_year = person_years[-1]

        # Get scores for first and last year
        first_comparison = analyzer.compare_people_for_year(first_year)
        first_row = first_comparison[first_comparison["Person"] == person]
        if first_row.empty:
            continue
        first_score = first_row["Average Score"].values[0]

        last_comparison = analyzer.compare_people_for_year(last_year)
        last_row = last_comparison[last_comparison["Person"] == person]
        if last_row.empty:
            continue
        last_score = last_row["Average Score"].values[0]

        improvement = last_score - first_score
        improvement_data.append((person, improvement, first_score, last_score))

    # Sort by improvement
    improvement_data.sort(key=lambda x: x[1], reverse=True)

    # Calculate concepts distribution
    concepts = comparison_df["Overall Concept"].value_counts()
    concept_distribution = {
        "above": concepts.get("acima do grupo", 0),
        "aligned": concepts.get("alinhado em relação ao grupo", 0),
        "below": concepts.get("abaixo do grupo", 0),
    }

    # Generate the report
    with open(summary_file, "w") as f:
        f.write("# Insights Summary Report\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")

        f.write("## Team Performance Overview\n\n")
        f.write(f"Latest evaluation year: **{latest_year}**\n\n")
        f.write("### Concept Distribution\n\n")
        f.write(
            f"- **Above Group**: {concept_distribution['above']} ({concept_distribution['above'] / len(comparison_df) * 100:.1f}%)\n"
        )
        f.write(
            f"- **Aligned with Group**: {concept_distribution['aligned']} ({concept_distribution['aligned'] / len(comparison_df) * 100:.1f}%)\n"
        )
        f.write(
            f"- **Below Group**: {concept_distribution['below']} ({concept_distribution['below'] / len(comparison_df) * 100:.1f}%)\n\n"
        )

        f.write("### Top Performers\n\n")
        for i, (_, row) in enumerate(comparison_df.head(3).iterrows()):
            f.write(f"{i + 1}. **{row['Person']}**: {row['Average Score']:.2f} ")
            f.write(
                f"(vs group avg: {row['Group Average']:.2f}, diff: {row['Difference']:.2f})\n"
            )

        f.write("\n### Bottom Performers\n\n")
        for i, (_, row) in enumerate(comparison_df.tail(3).iterrows()):
            f.write(f"{i + 1}. **{row['Person']}**: {row['Average Score']:.2f} ")
            f.write(
                f"(vs group avg: {row['Group Average']:.2f}, diff: {row['Difference']:.2f})\n"
            )

        f.write("\n## Improvement Trends\n\n")
        f.write("### Most Improved\n\n")
        for i, (person, improvement, first, last) in enumerate(improvement_data[:3]):
            f.write(
                f"{i + 1}. **{person}**: +{improvement:.2f} (from {first:.2f} to {last:.2f})\n"
            )

        f.write("\n## Evaluation Criteria Evolution\n\n")
        for year in years:
            behavior_count = sum(
                len(behaviors) for behaviors in analyzer.year_criteria[year].values()
            )
            f.write(f"- **{year}**: {behavior_count} behaviors evaluated\n")

        common_behaviors = analyzer.find_common_behaviors(years)
        common_count = sum(len(behaviors) for behaviors in common_behaviors.values())
        f.write(f"\nBehaviors consistent across all years: **{common_count}**\n")

        f.write("\n## Data Quality\n\n")
        total_people = len(analyzer.evaluations_by_person)
        complete_data = sum(
            1
            for person, years_data in analyzer.evaluations_by_person.items()
            if len(years_data) == len(years)
        )
        f.write(f"- Total people evaluated: **{total_people}**\n")
        f.write(
            f"- People with complete data: **{complete_data}** ({complete_data / total_people * 100:.1f}%)\n"
        )

    print(f"Summary insights saved to {summary_file}")
    return summary_file


def main():
    args = parse_args()

    # Ensure output directory exists
    output_dir = ensure_dir(args.output_dir)

    print("Initializing Evaluation Dashboard...")
    print(f"Input directory: {args.input_dir}")
    print(f"Output directory: {output_dir}")

    # Initialize analyzer
    analyzer = EvaluationAnalyzer(args.input_dir)

    # Generate insights summary
    summary_file = generate_summary_insights(analyzer, output_dir)

    # Generate charts if not skipped
    if not args.skip_charts:
        charts_dir = generate_charts(analyzer, output_dir, args.year, args.person)

    # Generate feedback reports if not skipped
    if not args.skip_feedback:
        if args.person:
            feedback_dir = generate_feedback_reports(
                args.input_dir, output_dir, args.person
            )
        elif args.all:
            feedback_dir = generate_feedback_reports(args.input_dir, output_dir)

    # Generate comparative spreadsheet if not skipped
    if not args.skip_spreadsheet:
        spreadsheet_file = generate_comparative_spreadsheet(args.input_dir, output_dir)

    print("\nEvaluation Dashboard generation complete!")
    print(f"All outputs saved to: {output_dir}")


if __name__ == "__main__":
    main()
