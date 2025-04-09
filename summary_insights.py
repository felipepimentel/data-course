#!/usr/bin/env python3
from analyze_evaluations import EvaluationAnalyzer


def main():
    analyzer = EvaluationAnalyzer("test_data")

    print("========== PERFORMANCE INSIGHTS ==========")

    # Get all available years
    years = []
    for person, data in analyzer.evaluations_by_person.items():
        years.extend(data.keys())
    years = sorted(list(set(years)))

    latest_year = years[-1] if years else None
    if not latest_year:
        print("No evaluation data found")
        return

    print(f"\n--- Performance Comparison ({latest_year}) ---")
    comparison_df = analyzer.compare_people_for_year(latest_year)
    # Sort by average score descending
    comparison_df = comparison_df.sort_values("Average Score", ascending=False)

    # Display top 3 performers
    print("\nTop 3 Performers:")
    top_performers = comparison_df.head(3)
    for _, row in top_performers.iterrows():
        print(
            f"- {row['Person']}: {row['Average Score']:.2f} (vs group avg: {row['Group Average']:.2f}, diff: {row['Difference']:.2f})"
        )

    # Display bottom 3 performers
    print("\nBottom 3 Performers:")
    bottom_performers = comparison_df.tail(3)
    for _, row in bottom_performers.iterrows():
        print(
            f"- {row['Person']}: {row['Average Score']:.2f} (vs group avg: {row['Group Average']:.2f}, diff: {row['Difference']:.2f})"
        )

    # Most improved (compare first and last year for each person)
    print("\n--- Most Improved Performers ---")
    improvement_data = []

    for person in analyzer.evaluations_by_person.keys():
        person_years = analyzer.get_person_years(person)
        if len(person_years) < 2:
            continue

        first_year = person_years[0]
        last_year = person_years[-1]

        # Get first year data
        first_comparison = analyzer.compare_people_for_year(first_year)
        first_row = first_comparison[first_comparison["Person"] == person]
        if first_row.empty:
            continue
        first_score = first_row["Average Score"].values[0]

        # Get last year data
        last_comparison = analyzer.compare_people_for_year(last_year)
        last_row = last_comparison[last_comparison["Person"] == person]
        if last_row.empty:
            continue
        last_score = last_row["Average Score"].values[0]

        improvement = last_score - first_score
        improvement_data.append((person, improvement, first_score, last_score))

    # Sort by improvement (descending)
    improvement_data.sort(key=lambda x: x[1], reverse=True)

    # Show top 3 most improved
    print("\nTop 3 Most Improved:")
    for person, improvement, first_score, last_score in improvement_data[:3]:
        print(
            f"- {person}: +{improvement:.2f} (from {first_score:.2f} to {last_score:.2f})"
        )

    # Common behaviors across years
    print("\n--- Evaluation Criteria Evolution ---")

    # Count behaviors per year
    for year in years:
        behavior_count = sum(
            len(behaviors) for behaviors in analyzer.year_criteria[year].values()
        )
        print(f"- {year}: {behavior_count} behaviors evaluated")

    # Find common behaviors across all years
    common_behaviors = analyzer.find_common_behaviors(years)
    common_count = sum(len(behaviors) for behaviors in common_behaviors.values())
    print(f"\nBehaviors consistent across all years: {common_count}")

    # Display some insights about data quality
    print("\n--- Data Quality Insights ---")
    total_people = len(analyzer.evaluations_by_person)
    complete_data = sum(
        1
        for person, years_data in analyzer.evaluations_by_person.items()
        if len(years_data) == len(years)
    )
    print(f"- Total people evaluated: {total_people}")
    print(
        f"- People with complete data across all years: {complete_data} ({(complete_data / total_people * 100):.1f}%)"
    )

    missing_json = 0
    for person_dir in analyzer.base_path.iterdir():
        if not person_dir.is_dir():
            continue
        for year_dir in person_dir.iterdir():
            if not year_dir.is_dir():
                continue
            result_file = year_dir / "resultado.json"
            if not result_file.exists():
                missing_json += 1

    print(f"- Missing JSON files: {missing_json}")


if __name__ == "__main__":
    main()
