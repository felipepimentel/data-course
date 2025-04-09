import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set

import matplotlib.pyplot as plt
import pandas as pd


class EvaluationAnalyzer:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.evaluations_by_person = defaultdict(dict)
        # Define the frequency labels
        self.frequency_labels = [
            "n/a",
            "observo nunca",
            "observo raramente",
            "observo na maior parte das vezes",
            "observo sempre",
            "referencia",
        ]
        # Define weights for each category (can be adjusted)
        self.frequency_weights = [0, 1, 2, 3, 4, 5]
        self.load_all_evaluations()
        # Track the criteria for each year
        self.year_criteria = self._extract_year_criteria()

    def load_all_evaluations(self):
        """Load all evaluation files from the base path"""
        for person_dir in self.base_path.iterdir():
            if not person_dir.is_dir():
                continue

            person_name = person_dir.name

            for year_dir in person_dir.iterdir():
                if not year_dir.is_dir():
                    continue

                year = year_dir.name
                result_file = year_dir / "resultado.json"

                if result_file.exists():
                    with open(result_file, "r", encoding="utf-8") as f:
                        try:
                            data = json.load(f)
                            self.evaluations_by_person[person_name][year] = data
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON from {result_file}")

    def _extract_year_criteria(self) -> Dict[str, Dict[str, Set[str]]]:
        """Extract all criteria (direcionadores and comportamentos) for each year"""
        year_criteria = defaultdict(lambda: defaultdict(set))

        # First pass: discover all unique years
        all_years = set()
        for person, years in self.evaluations_by_person.items():
            all_years.update(years.keys())

        # Second pass: extract criteria for each year
        for year in all_years:
            # Find a person who has data for this year
            for person, years in self.evaluations_by_person.items():
                if year in years and years[year]["success"] and "data" in years[year]:
                    data = years[year]["data"]

                    if "direcionadores" in data:
                        for direcionador in data["direcionadores"]:
                            dir_name = direcionador["direcionador"]

                            for comportamento in direcionador["comportamentos"]:
                                comp_name = comportamento["comportamento"]
                                year_criteria[year][dir_name].add(comp_name)

                    # One sample is enough
                    break

        return year_criteria

    def get_person_years(self, person: str) -> List[str]:
        """Get all available years for a specific person"""
        if person in self.evaluations_by_person:
            return sorted(self.evaluations_by_person[person].keys())
        return []

    def get_all_people_for_year(self, year: str) -> List[str]:
        """Get all people who have evaluations for a specific year"""
        return [
            person
            for person, years in self.evaluations_by_person.items()
            if year in years
        ]

    def get_conceito_by_year(self, person: str) -> Dict[str, str]:
        """Get the overall concept for a person across all available years"""
        result = {}
        for year, data in self.evaluations_by_person[person].items():
            if (
                data["success"]
                and "data" in data
                and "conceito_ciclo_filho_descricao" in data["data"]
            ):
                result[year] = data["data"]["conceito_ciclo_filho_descricao"]
        return result

    def calculate_weighted_score(self, frequencies: List[int]) -> float:
        """Calculate a weighted score from frequency percentages"""
        if not frequencies or sum(frequencies) == 0:
            return 0

        # Calculate weighted sum using weights and frequencies
        weighted_sum = sum(
            freq * weight for freq, weight in zip(frequencies, self.frequency_weights)
        )

        # Normalize by total percentage (excluding n/a)
        total = sum(frequencies)

        return weighted_sum / total if total > 0 else 0

    def calculate_score_distribution(self, frequencies: List[int]) -> Dict[str, float]:
        """Calculate the distribution of scores as percentages"""
        total = sum(frequencies)
        if total == 0:
            return {label: 0 for label in self.frequency_labels}

        return {
            label: (freq / total) * 100
            for label, freq in zip(self.frequency_labels, frequencies)
        }

    def compare_with_group(
        self, person_freq: List[int], group_freq: List[int]
    ) -> Dict[str, float]:
        """Compare person's frequencies with group frequencies"""
        person_dist = self.calculate_score_distribution(person_freq)
        group_dist = self.calculate_score_distribution(group_freq)

        difference = {}
        for label in self.frequency_labels:
            difference[label] = person_dist[label] - group_dist[label]

        return difference

    def get_behavior_scores(
        self, person: str, year: str
    ) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Extract behavior scores for all direcionadores"""
        result = {}
        if (
            person not in self.evaluations_by_person
            or year not in self.evaluations_by_person[person]
        ):
            return result

        data = self.evaluations_by_person[person][year]
        if (
            not data["success"]
            or "data" not in data
            or "direcionadores" not in data["data"]
        ):
            return result

        for direcionador in data["data"]["direcionadores"]:
            dir_name = direcionador["direcionador"]
            result[dir_name] = {}

            for comportamento in direcionador["comportamentos"]:
                comp_name = comportamento["comportamento"]
                scores = {}

                for avaliacao in comportamento["avaliacoes_grupo"]:
                    avaliador = avaliacao["avaliador"]
                    person_freq = avaliacao["frequencia_colaborador"]
                    group_freq = avaliacao["frequencia_grupo"]

                    person_score = self.calculate_weighted_score(person_freq)
                    group_score = self.calculate_weighted_score(group_freq)
                    comparison = self.compare_with_group(person_freq, group_freq)

                    scores[avaliador] = {
                        "freq_colaborador": person_freq,
                        "freq_grupo": group_freq,
                        "score_colaborador": person_score,
                        "score_grupo": group_score,
                        "difference": person_score - group_score,
                        "comparison_by_category": comparison,
                    }

                # Also get individual evaluations
                individual_evals = {}
                for avaliacao in comportamento["avaliacoes_individuais"]:
                    avaliador = avaliacao["avaliador"]
                    conceito = avaliacao["conceito"]
                    cor = avaliacao["cor"]
                    individual_evals[avaliador] = {"conceito": conceito, "cor": cor}

                result[dir_name][comp_name] = {
                    "scores": scores,
                    "individual_evaluations": individual_evals,
                }

        return result

    def compare_people_for_year(self, year: str) -> pd.DataFrame:
        """Compare all people for a specific year"""
        people = self.get_all_people_for_year(year)
        results = []

        for person in people:
            data = self.evaluations_by_person[person][year]
            if not data["success"] or "data" not in data:
                continue

            concept = data["data"]["conceito_ciclo_filho_descricao"]

            # Calculate scores across all behaviors
            total_score = 0
            total_group_score = 0
            count = 0

            # Store detailed comparisons for each category
            category_diffs = {label: 0 for label in self.frequency_labels}

            behavior_scores = self.get_behavior_scores(person, year)
            for dir_name, behaviors in behavior_scores.items():
                for comp_name, details in behaviors.items():
                    for avaliador, scores in details["scores"].items():
                        if avaliador == "%todos":  # Use the overall evaluation
                            total_score += scores["score_colaborador"]
                            total_group_score += scores["score_grupo"]
                            count += 1

                            # Accumulate category differences
                            for label, diff in scores["comparison_by_category"].items():
                                category_diffs[label] += diff

            avg_score = total_score / count if count > 0 else 0
            avg_group = total_group_score / count if count > 0 else 0

            # Average the category differences
            for label in category_diffs:
                category_diffs[label] /= count if count > 0 else 1

            result_dict = {
                "Person": person,
                "Overall Concept": concept,
                "Average Score": avg_score,
                "Group Average": avg_group,
                "Difference": avg_score - avg_group,
            }

            # Add category differences
            for label, diff in category_diffs.items():
                result_dict[f"Diff {label}"] = diff

            results.append(result_dict)

        return pd.DataFrame(results)

    def find_common_behaviors(self, years: List[str]) -> Dict[str, Set[str]]:
        """Find behaviors that are common across the given years"""
        if not years:
            return {}

        common_dirs = {}

        # Start with the first year
        for dir_name, behaviors in self.year_criteria[years[0]].items():
            # Check if this direcionador exists in all years
            exists_in_all = True
            common_behaviors = set(behaviors)

            for year in years[1:]:
                if dir_name not in self.year_criteria[year]:
                    exists_in_all = False
                    break

                # Find intersection of behaviors
                common_behaviors &= self.year_criteria[year][dir_name]

            if exists_in_all and common_behaviors:
                common_dirs[dir_name] = common_behaviors

        return common_dirs

    def person_year_over_year(self, person: str) -> Dict[str, Any]:
        """Analyze a person's performance across years"""
        years = self.get_person_years(person)
        concepts = self.get_conceito_by_year(person)

        year_scores = {}
        year_group_scores = {}
        year_categories = {
            year: {label: 0 for label in self.frequency_labels} for year in years
        }

        # Find common behaviors across all years
        common_behaviors = self.find_common_behaviors(years)

        # Track which behaviors were actually found for reporting
        found_behaviors = defaultdict(set)

        for year in years:
            behavior_scores = self.get_behavior_scores(person, year)
            person_scores = []
            group_scores = []
            year_behavior_count = 0  # Count behaviors evaluated in this year

            for dir_name, behaviors in behavior_scores.items():
                for comp_name, details in behaviors.items():
                    year_behavior_count += 1

                    # Check if this is a common behavior (for tracking)
                    if (
                        dir_name in common_behaviors
                        and comp_name in common_behaviors[dir_name]
                    ):
                        found_behaviors[dir_name].add(comp_name)

                    for avaliador, scores in details["scores"].items():
                        if avaliador == "%todos":  # Use the overall evaluation
                            person_scores.append(scores["score_colaborador"])
                            group_scores.append(scores["score_grupo"])

                            # Accumulate category differences
                            for label, diff in scores["comparison_by_category"].items():
                                year_categories[year][label] += diff

            # Average scores for this year
            count = len(person_scores)
            year_scores[year] = sum(person_scores) / count if count > 0 else 0
            year_group_scores[year] = sum(group_scores) / count if count > 0 else 0

            # Average the category differences
            for label in year_categories[year]:
                year_categories[year][label] /= count if count > 0 else 1

        # Also calculate scores using only common behaviors for comparison
        common_year_scores = {}
        common_year_group_scores = {}

        # Only compute if there are common behaviors
        if common_behaviors:
            for year in years:
                behavior_scores = self.get_behavior_scores(person, year)
                person_scores = []
                group_scores = []

                for dir_name, behaviors in common_behaviors.items():
                    if dir_name in behavior_scores:
                        for comp_name in behaviors:
                            if comp_name in behavior_scores[dir_name]:
                                details = behavior_scores[dir_name][comp_name]
                                for avaliador, scores in details["scores"].items():
                                    if avaliador == "%todos":
                                        person_scores.append(
                                            scores["score_colaborador"]
                                        )
                                        group_scores.append(scores["score_grupo"])

                count = len(person_scores)
                if count > 0:
                    common_year_scores[year] = sum(person_scores) / count
                    common_year_group_scores[year] = sum(group_scores) / count

        return {
            "Person": person,
            "Years": years,
            "Concepts": concepts,
            "Person Scores": year_scores,
            "Group Scores": year_group_scores,
            "Category Differences": year_categories,
            "Common Behaviors": common_behaviors,
            "Found Behaviors": found_behaviors,
            "Common Person Scores": common_year_scores,
            "Common Group Scores": common_year_group_scores,
        }

    def generate_comparative_report(self, year: str, output_file: str = None):
        """Generate a comparative report for all people in a specific year"""
        df = self.compare_people_for_year(year)

        if df.empty:
            print(f"No data available for year {year}")
            return

        # Sort by average score
        df = df.sort_values("Average Score", ascending=False)

        # Plot comparative bar chart
        plt.figure(figsize=(14, 8))
        plt.subplot(1, 2, 1)

        bars = plt.bar(df["Person"], df["Average Score"])

        # Add markers for group average
        plt.plot(df["Person"], df["Group Average"], "ro-", label="Group Average")

        # Color bars based on concept
        colors = {
            "alinhado em relação ao grupo": "blue",
            "acima do grupo": "green",
            "abaixo do grupo": "red",
        }

        for i, concept in enumerate(df["Overall Concept"]):
            default_color = "gray"
            bars[i].set_color(colors.get(concept, default_color))

        plt.xlabel("Person")
        plt.ylabel("Score")
        plt.title(f"Comparative Performance for Year {year}")
        plt.xticks(rotation=45, ha="right")
        plt.legend()

        # Add a second plot for category differences
        plt.subplot(1, 2, 2)

        # Select a subset of important categories
        categories_to_plot = [
            "observo raramente",
            "observo na maior parte das vezes",
            "observo sempre",
            "referencia",
        ]
        category_data = df[[f"Diff {cat}" for cat in categories_to_plot]]

        # Create a stacked bar chart
        bottom = None
        for cat in categories_to_plot:
            col = f"Diff {cat}"
            if bottom is None:
                bottom = 0
                plt.bar(df["Person"], df[col], label=cat)
            else:
                plt.bar(df["Person"], df[col], bottom=bottom, label=cat)
            bottom = df[col]

        plt.xlabel("Person")
        plt.ylabel("Difference from Group (%)")
        plt.title("Category Distribution Differences")
        plt.xticks(rotation=45, ha="right")
        plt.legend()

        plt.tight_layout()

        if output_file:
            plt.savefig(output_file)
            print(f"Report saved to {output_file}")
        else:
            plt.show()

        return df

    def generate_historical_report(self, person: str, output_file: str = None):
        """Generate a historical report for a specific person"""
        data = self.person_year_over_year(person)

        if not data["Years"]:
            print(f"No data available for person {person}")
            return

        years = data["Years"]
        person_scores = [data["Person Scores"].get(year, 0) for year in years]
        group_scores = [data["Group Scores"].get(year, 0) for year in years]

        # Data for common behaviors, if available
        has_common_behaviors = bool(data["Common Behaviors"])

        if has_common_behaviors:
            common_person_scores = [
                data["Common Person Scores"].get(year, None) for year in years
            ]
            common_group_scores = [
                data["Common Group Scores"].get(year, None) for year in years
            ]

            # Filter out None values
            common_years = []
            filtered_common_person = []
            filtered_common_group = []

            for i, year in enumerate(years):
                if common_person_scores[i] is not None:
                    common_years.append(year)
                    filtered_common_person.append(common_person_scores[i])
                    filtered_common_group.append(common_group_scores[i])

        plt.figure(figsize=(14, 14))

        # Plot 1: Score Evolution (All Behaviors)
        plt.subplot(3, 1, 1)
        plt.plot(
            years,
            person_scores,
            marker="o",
            linestyle="-",
            label=f"{person} Score (All Behaviors)",
        )
        plt.plot(years, group_scores, marker="s", linestyle="--", label="Group Average")

        for i, year in enumerate(years):
            concept = data["Concepts"].get(year, "")
            color = {
                "alinhado em relação ao grupo": "blue",
                "acima do grupo": "green",
                "abaixo do grupo": "red",
            }.get(concept, "gray")

            plt.scatter(year, person_scores[i], color=color, s=100)
            plt.annotate(
                concept,
                (year, person_scores[i]),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
            )

        plt.xlabel("Year")
        plt.ylabel("Score")
        plt.title(f"Historical Performance for {person} (All Behaviors)")
        plt.legend()
        plt.grid(True)

        # Plot 2: Score Evolution (Common Behaviors)
        plt.subplot(3, 1, 2)

        if has_common_behaviors and filtered_common_person:
            plt.plot(
                common_years,
                filtered_common_person,
                marker="o",
                linestyle="-",
                label=f"{person} Score (Common Behaviors Only)",
            )
            plt.plot(
                common_years,
                filtered_common_group,
                marker="s",
                linestyle="--",
                label="Group Average (Common Behaviors Only)",
            )

            # Annotate points
            for i, year in enumerate(common_years):
                concept = data["Concepts"].get(year, "")
                color = {
                    "alinhado em relação ao grupo": "blue",
                    "acima do grupo": "green",
                    "abaixo do grupo": "red",
                }.get(concept, "gray")

                plt.scatter(year, filtered_common_person[i], color=color, s=100)

            plt.legend()
        else:
            plt.text(
                0.5,
                0.5,
                "No common behaviors found across years",
                horizontalalignment="center",
                verticalalignment="center",
                transform=plt.gca().transAxes,
                fontsize=12,
            )

        plt.xlabel("Year")
        plt.ylabel("Score")
        plt.title(f"Historical Performance for {person} (Common Behaviors Only)")
        plt.grid(True)

        # Plot 3: Category Evolution
        plt.subplot(3, 1, 3)

        # Select key categories for analysis
        categories_to_plot = [
            "observo raramente",
            "observo na maior parte das vezes",
            "observo sempre",
            "referencia",
        ]
        category_diffs = data["Category Differences"]

        for category in categories_to_plot:
            category_values = [category_diffs[year][category] for year in years]
            plt.plot(years, category_values, marker="o", linestyle="-", label=category)

        plt.axhline(y=0, color="r", linestyle="-", alpha=0.3)
        plt.xlabel("Year")
        plt.ylabel("Difference from Group (%)")
        plt.title("Evolution of Category Differences")
        plt.legend()
        plt.grid(True)

        plt.tight_layout()

        if output_file:
            plt.savefig(output_file)
            print(f"Report saved to {output_file}")
        else:
            plt.show()

        # Print common behaviors report
        if has_common_behaviors:
            common_count = sum(
                len(behaviors) for behaviors in data["Common Behaviors"].values()
            )
            print(
                f"\nFound {common_count} behaviors that are consistent across all {len(years)} years:"
            )

            for dir_name, behaviors in data["Common Behaviors"].items():
                print(f"\n{dir_name}:")
                for behavior in behaviors:
                    print(f"  - {behavior}")
        else:
            print(
                "\nNo behaviors are common across all years. This makes year-over-year comparison less reliable."
            )

            # Suggest comparison between specific year pairs
            if len(years) >= 2:
                for i in range(len(years) - 1):
                    year1, year2 = years[i], years[i + 1]
                    common = self.find_common_behaviors([year1, year2])
                    common_count = sum(len(behaviors) for behaviors in common.values())
                    print(f"\n{year1} vs {year2}: {common_count} common behaviors")

        return data


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analyze 360 evaluation data")
    parser.add_argument("base_path", help="Base path containing evaluation folders")
    parser.add_argument("--year", help="Year to analyze for comparative report")
    parser.add_argument("--person", help="Person to analyze for historical report")
    parser.add_argument("--output", help="Output file for reports (PNG format)")
    parser.add_argument(
        "--details", action="store_true", help="Show detailed score breakdown"
    )
    parser.add_argument(
        "--list-criteria", action="store_true", help="List criteria for each year"
    )

    args = parser.parse_args()

    analyzer = EvaluationAnalyzer(args.base_path)

    if args.list_criteria:
        print("Evaluation criteria by year:")
        for year in sorted(analyzer.year_criteria.keys()):
            print(f"\n== {year} ==")
            for dir_name, behaviors in analyzer.year_criteria[year].items():
                print(f"\n{dir_name}:")
                for behavior in behaviors:
                    print(f"  - {behavior}")

    if args.year:
        print(f"\nGenerating comparative report for year {args.year}...")
        result = analyzer.generate_comparative_report(args.year, args.output)
        if result is not None:
            print("\nComparative Results:")
            if args.details:
                print(result)
            else:
                print(
                    result[
                        [
                            "Person",
                            "Overall Concept",
                            "Average Score",
                            "Group Average",
                            "Difference",
                        ]
                    ]
                )

    if args.person:
        print(f"\nGenerating historical report for {args.person}...")
        result = analyzer.generate_historical_report(args.person, args.output)
        if result is not None:
            print("\nHistorical Results:")
            print(f"Years analyzed: {result['Years']}")
            print(f"Concepts by year: {result['Concepts']}")
            print(f"Person scores by year: {result['Person Scores']}")
            print(f"Group scores by year: {result['Group Scores']}")

            if args.details:
                print("\nCategory differences by year:")
                for year in result["Years"]:
                    print(f"  {year}:")
                    for category, diff in result["Category Differences"][year].items():
                        print(f"    {category}: {diff:.2f}%")
