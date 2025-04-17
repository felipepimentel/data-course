import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set

import matplotlib.pyplot as plt
import pandas as pd

from peopleanalytics.constants import (
    CONCEPT_CHART_COLORS,
    FREQUENCY_LABELS,
    FREQUENCY_WEIGHTS,
    calculate_score,
)


class SchemaManager:
    """Simplified schema manager for validation."""

    def __init__(self):
        self.schema = {}

    def validate(self, data):
        """Placeholder for schema validation."""
        return True


class EvaluationAnalyzer:
    """Analyze evaluation data within a structured directory."""

    def __init__(self, base_path: str, use_cache: bool = True):
        """Initialize the evaluation analyzer.

        Args:
            base_path: Path to the directory containing evaluation data.
                Expected structure: <person>/<year>/resultado.json
            use_cache: Whether to cache results for faster lookups
        """
        self.base_path = Path(base_path)
        self.use_cache = use_cache
        self._cache = {}

        # Default values for frequency analysis
        self.frequency_labels = FREQUENCY_LABELS
        self.frequency_weights = FREQUENCY_WEIGHTS

        # For storing evaluations by person and year
        self.evaluations_by_person = defaultdict(dict)

        # Ensure the base directory exists
        os.makedirs(self.base_path, exist_ok=True)

        # Load schema manager for validation
        self.schema_manager = SchemaManager()

        # Load all evaluations
        self.load_all_evaluations()

        # Track the criteria for each year
        self.year_criteria = self._extract_year_criteria()

    def load_all_evaluations(self):
        """Load all evaluation files from the base path"""
        if not self.base_path.exists():
            # If the base path doesn't exist, return without attempting to load files
            return

        # First level should be people
        for person_dir in self.base_path.iterdir():
            if not person_dir.is_dir():
                continue

            person_name = person_dir.name

            # Second level should be years
            for year_dir in person_dir.iterdir():
                if not year_dir.is_dir():
                    continue

                year = year_dir.name

                # Look specifically for resultado.json
                resultado_file = year_dir / "resultado.json"
                if not resultado_file.exists():
                    continue

                # Process the resultado.json file
                try:
                    with open(resultado_file, "r", encoding="utf-8") as f:
                        try:
                            data = json.load(f)
                            # Initialize the year data if not already present
                            if year not in self.evaluations_by_person[person_name]:
                                self.evaluations_by_person[person_name][year] = {
                                    "success": True,
                                    "data": data,
                                }
                        except json.JSONDecodeError as e:
                            # More detailed error message including the specific error
                            relative_path = resultado_file.relative_to(self.base_path)
                            print(f"Error decoding JSON from {relative_path}: {str(e)}")
                            # Initialize with empty but valid structure to prevent downstream errors
                            if year not in self.evaluations_by_person[person_name]:
                                self.evaluations_by_person[person_name][year] = {
                                    "success": False,
                                    "data": {},
                                }
                except Exception as e:
                    # Catch other potential errors like permission issues
                    relative_path = resultado_file.relative_to(self.base_path)
                    print(f"Error reading file {relative_path}: {str(e)}")

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

                    # Check if data has a nested "data" structure
                    actual_data = data
                    if (
                        isinstance(data, dict)
                        and "data" in data
                        and isinstance(data["data"], dict)
                    ):
                        actual_data = data["data"]

                    if "direcionadores" in actual_data:
                        for direcionador in actual_data["direcionadores"]:
                            dir_name = direcionador.get("direcionador", "Unknown")

                            for comportamento in direcionador.get("comportamentos", []):
                                comp_name = comportamento.get(
                                    "comportamento", "Unknown"
                                )
                                year_criteria[year][dir_name].add(comp_name)

                    # One sample is enough
                    break

        return year_criteria

    def get_all_people(self) -> List[str]:
        """Get all people in the dataset"""
        return sorted(list(self.evaluations_by_person.keys()))

    def get_all_years(self) -> List[str]:
        """Get all available years in the dataset"""
        all_years = set()
        for person, years in self.evaluations_by_person.items():
            all_years.update(years.keys())
        return sorted(all_years)

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
            if data["success"] and "data" in data:
                # Handle nested data structure
                actual_data = data["data"]
                if isinstance(actual_data, dict) and "data" in actual_data:
                    actual_data = actual_data["data"]

                if "conceito_ciclo_filho_descricao" in actual_data:
                    result[year] = actual_data["conceito_ciclo_filho_descricao"]
        return result

    def get_evaluations_for_person(self, person: str, year: str) -> Dict[str, Any]:
        """Get raw evaluation data for a person in a specific year"""
        if (
            person in self.evaluations_by_person
            and year in self.evaluations_by_person[person]
        ):
            return self.evaluations_by_person[person][year]
        return {}

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
        if not data.get("success", False) or "data" not in data:
            return result

        # Handle nested data structure - check if data["data"] is a dictionary with "data"
        if "data" in data and isinstance(data["data"], dict) and "data" in data["data"]:
            # Handle nested structure - one level deep
            inner_data = data["data"]["data"]
            if "direcionadores" in inner_data:
                for direcionador in inner_data["direcionadores"]:
                    dir_name = direcionador.get("direcionador", "Unknown")
                    result[dir_name] = {}

                    for comportamento in direcionador.get("comportamentos", []):
                        comp_name = comportamento.get("comportamento", "Unknown")
                        result[dir_name][comp_name] = {"scores": {}}

                        # First try to get scores from consolidado
                        has_consolidado_scores = False
                        for avaliacao in comportamento.get("consolidado", []):
                            avaliador = avaliacao.get("avaliador", "Unknown")
                            freq_colaborador = avaliacao.get(
                                "frequencias_colaborador", []
                            )
                            freq_grupo = avaliacao.get("frequencias_grupo", [])

                            try:
                                result[dir_name][comp_name]["scores"][avaliador] = {
                                    "score_colaborador": self.calculate_weighted_score(
                                        freq_colaborador
                                    ),
                                    "score_grupo": self.calculate_weighted_score(
                                        freq_grupo
                                    ),
                                    "comparison_by_category": self.compare_with_group(
                                        freq_colaborador, freq_grupo
                                    ),
                                }
                                has_consolidado_scores = True
                            except Exception as e:
                                print(
                                    f"Error processing consolidado scores for {person}, {year}, {dir_name}, {comp_name}, {avaliador}: {str(e)}"
                                )

                        # If no consolidado scores, try avaliacoes_grupo
                        if not has_consolidado_scores:
                            for avaliacao in comportamento.get("avaliacoes_grupo", []):
                                avaliador = avaliacao.get("avaliador", "Unknown")
                                freq_colaborador = avaliacao.get(
                                    "frequencia_colaborador", []
                                )
                                freq_grupo = avaliacao.get("frequencia_grupo", [])

                                try:
                                    result[dir_name][comp_name]["scores"][avaliador] = {
                                        "score_colaborador": self.calculate_weighted_score(
                                            freq_colaborador
                                        ),
                                        "score_grupo": self.calculate_weighted_score(
                                            freq_grupo
                                        ),
                                        "comparison_by_category": self.compare_with_group(
                                            freq_colaborador, freq_grupo
                                        ),
                                    }
                                except Exception as e:
                                    print(
                                        f"Error processing avaliacoes_grupo scores for {person}, {year}, {dir_name}, {comp_name}, {avaliador}: {str(e)}"
                                    )
                return result

        # Original code for standard structure
        if "direcionadores" not in data.get("data", {}):
            return result

        for direcionador in data["data"]["direcionadores"]:
            dir_name = direcionador.get("direcionador", "Unknown")
            result[dir_name] = {}

            for comportamento in direcionador.get("comportamentos", []):
                comp_name = comportamento.get("comportamento", "Unknown")
                result[dir_name][comp_name] = {"scores": {}}

                # First try to get scores from consolidado
                has_consolidado_scores = False
                for avaliacao in comportamento.get("consolidado", []):
                    avaliador = avaliacao.get("avaliador", "Unknown")
                    freq_colaborador = avaliacao.get("frequencias_colaborador", [])
                    freq_grupo = avaliacao.get("frequencias_grupo", [])

                    try:
                        result[dir_name][comp_name]["scores"][avaliador] = {
                            "score_colaborador": self.calculate_weighted_score(
                                freq_colaborador
                            ),
                            "score_grupo": self.calculate_weighted_score(freq_grupo),
                            "comparison_by_category": self.compare_with_group(
                                freq_colaborador, freq_grupo
                            ),
                        }
                        has_consolidado_scores = True
                    except Exception as e:
                        print(
                            f"Error processing consolidado scores for {person}, {year}, {dir_name}, {comp_name}, {avaliador}: {str(e)}"
                        )

                # If no consolidado scores, try avaliacoes_grupo
                if not has_consolidado_scores:
                    for avaliacao in comportamento.get("avaliacoes_grupo", []):
                        avaliador = avaliacao.get("avaliador", "Unknown")
                        freq_colaborador = avaliacao.get("frequencia_colaborador", [])
                        freq_grupo = avaliacao.get("frequencia_grupo", [])

                        try:
                            result[dir_name][comp_name]["scores"][avaliador] = {
                                "score_colaborador": self.calculate_weighted_score(
                                    freq_colaborador
                                ),
                                "score_grupo": self.calculate_weighted_score(
                                    freq_grupo
                                ),
                                "comparison_by_category": self.compare_with_group(
                                    freq_colaborador, freq_grupo
                                ),
                            }
                        except Exception as e:
                            print(
                                f"Error processing avaliacoes_grupo scores for {person}, {year}, {dir_name}, {comp_name}, {avaliador}: {str(e)}"
                            )

        return result

    def calculate_weighted_score(
        self, frequencies: List[int], use_nps_model: bool = False
    ) -> float:
        """Calculate a weighted score from frequency distribution vectors"""
        # Use the centralized scoring function from constants module
        return calculate_score(frequencies, use_nps_model)

    def calculate_score_distribution(self, frequencies: List[int]) -> Dict[str, float]:
        """Calculate the distribution of scores as percentages"""
        # Check if frequencies is None or empty
        if not frequencies:
            return {label: 0.0 for label in self.frequency_labels}

        total = sum(frequencies)
        if total == 0:
            return {label: 0.0 for label in self.frequency_labels}

        # Ensure we have values for all expected labels by creating a complete dictionary
        distribution = {label: 0.0 for label in self.frequency_labels}

        # Then fill in the actual calculated percentages
        for i, label in enumerate(self.frequency_labels):
            if i < len(frequencies):
                distribution[label] = (frequencies[i] / total) * 100

        return distribution

    def compare_with_group(
        self, person_freq: List[int], group_freq: List[int]
    ) -> Dict[str, float]:
        """Compare person's frequencies with group frequencies"""
        person_dist = self.calculate_score_distribution(person_freq)
        group_dist = self.calculate_score_distribution(group_freq)

        result = {}
        for label in self.frequency_labels:
            result[label] = person_dist.get(label, 0.0) - group_dist.get(label, 0.0)

        return result

    def get_average_score(self, person: str, year: str) -> float:
        """Calculate average score across all behaviors for a person in a specific year"""
        scores = []
        behavior_scores = self.get_behavior_scores(person, year)

        for direcionador, comportamentos in behavior_scores.items():
            for comportamento, data in comportamentos.items():
                for avaliador, scores_data in data["scores"].items():
                    scores.append(scores_data["score_colaborador"])

        if scores:
            return sum(scores) / len(scores)
        return 0.0

    def get_criteria_for_year(self, year: str) -> Dict[str, Set[str]]:
        """Get all the criteria (direcionadores and comportamentos) for a year"""
        return self.year_criteria.get(year, {})

    def get_score_for_criterion(self, person: str, year: str, criterion: str) -> float:
        """Get score for a specific criterion (direcionador) for a person in a year"""
        scores = []
        behavior_scores = self.get_behavior_scores(person, year)

        if criterion in behavior_scores:
            for comportamento, data in behavior_scores[criterion].items():
                for avaliador, scores_data in data["scores"].items():
                    scores.append(scores_data["score_colaborador"])

        if scores:
            return sum(scores) / len(scores)
        return 0.0

    def compare_people_for_year(self, year: str) -> pd.DataFrame:
        """Compare all people for a specific year and return as a DataFrame

        Returns a DataFrame with people as rows and the following columns:
        - Name: Person's name
        - Average Score: Average score across all behaviors
        - Concept: Overall concept for the year
        - One column per criterion showing the score for that criterion
        """
        # Get people who have data for this year
        people = self.get_all_people_for_year(year)
        if not people:
            return pd.DataFrame()  # Return empty DataFrame if no people found

        # Get all criteria for this year
        criteria = self.get_criteria_for_year(year)

        # Create results list
        results = []

        for person in people:
            # Get data for this person
            behavior_scores = self.get_behavior_scores(person, year)
            conceito_by_year = self.get_conceito_by_year(person)

            # Calculate overall average score
            avg_score = self.get_average_score(person, year)

            # Create row data
            row = {
                "Name": person,
                "Average Score": avg_score,
                "Concept": conceito_by_year.get(year, "Unknown"),
            }

            # Add scores for each criterion
            for criterion in criteria:
                criterion_score = 0.0
                count = 0

                if criterion in behavior_scores:
                    for comportamento, data in behavior_scores[criterion].items():
                        for avaliador, scores_data in data["scores"].items():
                            criterion_score += scores_data["score_colaborador"]
                            count += 1

                if count > 0:
                    row[criterion] = criterion_score / count
                else:
                    row[criterion] = 0.0

            results.append(row)

        # Create DataFrame
        df = pd.DataFrame(results)

        # Calculate average scores per criterion
        if len(df) > 0:
            # Calculate group averages
            avg_row = {
                "Name": "Group Average",
                "Average Score": df["Average Score"].mean(),
            }

            for criterion in criteria:
                if criterion in df.columns:
                    avg_row[criterion] = df[criterion].mean()

            # Add to DataFrame
            df = pd.concat([df, pd.DataFrame([avg_row])], ignore_index=True)

        return df

    def find_common_behaviors(self, years: List[str]) -> Dict[str, Set[str]]:
        """Find behaviors that are common across multiple years"""
        if not years:
            return {}

        # Get criteria for first year
        common_criteria = self.get_criteria_for_year(years[0])

        # For each remaining year, keep only criteria that exist in all years
        for year in years[1:]:
            year_criteria = self.get_criteria_for_year(year)

            # Update common criteria to keep only those that exist in this year too
            for direcionador in list(common_criteria.keys()):
                if direcionador not in year_criteria:
                    del common_criteria[direcionador]
                else:
                    # Keep only common behaviors
                    common_criteria[direcionador] = common_criteria[
                        direcionador
                    ].intersection(year_criteria[direcionador])

                    # If no common behaviors left, remove the direcionador
                    if not common_criteria[direcionador]:
                        del common_criteria[direcionador]

        return common_criteria

    def person_year_over_year(self, person: str) -> Dict[str, Any]:
        """Generate year-over-year comparison data for a person"""
        years = self.get_person_years(person)
        if not years:
            return {}

        # Sort years
        years = sorted(years)

        # Get conceito by year
        conceito_by_year = self.get_conceito_by_year(person)

        # Find common behaviors across all years
        common_behaviors = self.find_common_behaviors(years)

        # Create results structure
        results = {
            "person": person,
            "years": years,
            "conceito_by_year": conceito_by_year,
            "common_behaviors": common_behaviors,
            "average_score_by_year": {},
            "direcionador_scores_by_year": defaultdict(dict),
            "behavior_scores_by_year": defaultdict(lambda: defaultdict(dict)),
        }

        # For each year, get the average score
        for year in years:
            results["average_score_by_year"][year] = self.get_average_score(
                person, year
            )

            # Get scores for all direcionadores
            behavior_scores = self.get_behavior_scores(person, year)

            # Calculate average score per direcionador
            for direcionador, comportamentos in behavior_scores.items():
                direcionador_scores = []

                for comportamento, data in comportamentos.items():
                    behavior_scores_by_avaliador = []

                    for avaliador, scores_data in data["scores"].items():
                        behavior_scores_by_avaliador.append(
                            scores_data["score_colaborador"]
                        )

                        # Store individual behavior scores
                        if (
                            direcionador in common_behaviors
                            and comportamento in common_behaviors[direcionador]
                        ):
                            results["behavior_scores_by_year"][direcionador][
                                comportamento
                            ][year] = scores_data["score_colaborador"]

                    # Add to direcionador scores if we have data
                    if behavior_scores_by_avaliador:
                        direcionador_scores.append(
                            sum(behavior_scores_by_avaliador)
                            / len(behavior_scores_by_avaliador)
                        )

                # Calculate average for this direcionador
                if direcionador_scores:
                    results["direcionador_scores_by_year"][direcionador][year] = sum(
                        direcionador_scores
                    ) / len(direcionador_scores)

        return results

    def generate_comparative_report(self, year, output_path=None):
        """Generate a comparative report for a specific year"""
        df = self.compare_people_for_year(year)
        if df.empty:
            print(f"No data available for year {year}")
            return None

        # Create visualization
        self.plot_comparative_report(df, year, output_path)

        return df

    def generate_historical_report(self, person: str, output_file: str = None):
        """Generate a historical report for a person"""
        yoy_data = self.person_year_over_year(person)
        if not yoy_data:
            print(f"No data available for person {person}")
            return None

        years = yoy_data["years"]
        avg_scores = [yoy_data["average_score_by_year"].get(year, 0) for year in years]

        # Create plots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Plot 1: Average score by year
        ax1.plot(years, avg_scores, "o-", linewidth=2)
        ax1.set_title(f"Average Score by Year - {person}")
        ax1.set_xlabel("Year")
        ax1.set_ylabel("Average Score")
        ax1.grid(True)

        # Plot 2: Score by direcionador
        legend_items = []
        for direcionador, scores_by_year in yoy_data[
            "direcionador_scores_by_year"
        ].items():
            if (
                len(scores_by_year) >= len(years) * 0.7
            ):  # Only plot if we have data for at least 70% of years
                values = [scores_by_year.get(year, None) for year in years]
                # Filter out None values
                valid_years = [y for y, v in zip(years, values) if v is not None]
                valid_values = [v for v in values if v is not None]

                if valid_values:  # Only plot if we have some valid values
                    (line,) = ax2.plot(valid_years, valid_values, "o-", linewidth=2)
                    legend_items.append((line, direcionador))

        ax2.set_title(f"Score by Direcionador - {person}")
        ax2.set_xlabel("Year")
        ax2.set_ylabel("Score")
        ax2.grid(True)

        # Add legend if we have items
        if legend_items:
            ax2.legend(
                [item[0] for item in legend_items], [item[1] for item in legend_items]
            )

        plt.tight_layout()

        # Save or show
        if output_file:
            plt.savefig(output_file)
            plt.close()
            return output_file
        else:
            plt.show()
            plt.close()
            return True

    def plot_comparative_report(self, df, year, output_path=None):
        """Plot a comparative report for all people in a given year"""
        if df.empty:
            print("No data to plot")
            return None

        # Only use actual people, not the Group Average
        people_df = df[df["Name"] != "Group Average"].copy()

        # Sort by Average Score
        people_df = people_df.sort_values("Average Score", ascending=False)

        # Create plots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 14))

        # Plot 1: Average score by person
        bars = ax1.bar(people_df["Name"], people_df["Average Score"])

        # Color bars by concept
        concept_colors = CONCEPT_CHART_COLORS

        for i, concept in enumerate(people_df["Concept"]):
            if concept in concept_colors:
                bars[i].set_color(concept_colors.get(concept, "#1f77b4"))

        ax1.set_title(f"Average Score by Person - {year}")
        ax1.set_xlabel("Person")
        ax1.set_ylabel("Average Score")
        ax1.set_ylim(0, 4.5)
        ax1.grid(True, axis="y")
        plt.setp(ax1.get_xticklabels(), rotation=45, ha="right")

        # Plot 2: Heatmap of scores by criterion
        # Get criteria columns (excluding metadata)
        criteria_cols = [
            col for col in df.columns if col not in ["Name", "Average Score", "Concept"]
        ]

        if criteria_cols:
            # Create heatmap data - use all rows including Group Average
            heatmap_data = df.pivot(index="Name", columns=None, values=criteria_cols)

            # Plot heatmap
            sns.heatmap(heatmap_data, annot=True, cmap="YlGnBu", ax=ax2)
            ax2.set_title(f"Scores by Criterion - {year}")
            plt.yticks(rotation=0)
        else:
            ax2.text(
                0.5,
                0.5,
                "No criterion data available",
                ha="center",
                va="center",
                fontsize=14,
            )
            ax2.set_title(f"Scores by Criterion - {year}")
            ax2.axis("off")

        plt.tight_layout()

        # Save or show
        if output_path:
            # Ensure directory exists
            os.makedirs(output_path, exist_ok=True)
            output_file = os.path.join(output_path, f"comparative_report_{year}.png")
            plt.savefig(output_file)
            plt.close()
            return output_file
        else:
            plt.show()
            plt.close()
            return True
