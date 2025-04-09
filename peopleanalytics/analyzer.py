"""
Core evaluation analyzer module for processing and analyzing 360-degree evaluations.
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set

import matplotlib.pyplot as plt
import pandas as pd

# Importar as constantes do módulo constants
from peopleanalytics.constants import CONCEPT_CHART_COLORS, FREQUENCY_LABELS, FREQUENCY_WEIGHTS


class EvaluationAnalyzer:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        if not self.base_path.exists():
            print(f"Warning: Base path {base_path} does not exist")
        
        self.evaluations_by_person = defaultdict(dict)
        # Usar constantes importadas
        self.frequency_labels = FREQUENCY_LABELS
        self.frequency_weights = FREQUENCY_WEIGHTS
        
        # Validate frequency labels and weights match in length
        if len(self.frequency_labels) != len(self.frequency_weights):
            print(f"Warning: Frequency labels ({len(self.frequency_labels)}) and weights ({len(self.frequency_weights)}) have different lengths")
        
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
                                    "data": data
                                }
                        except json.JSONDecodeError as e:
                            # More detailed error message including the specific error
                            relative_path = resultado_file.relative_to(self.base_path)
                            print(f"Error decoding JSON from {relative_path}: {str(e)}")
                            # Initialize with empty but valid structure to prevent downstream errors
                            if year not in self.evaluations_by_person[person_name]:
                                self.evaluations_by_person[person_name][year] = {
                                    "success": False, 
                                    "data": {}
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

    def get_all_years(self) -> List[str]:
        """Get all available years in the dataset"""
        all_years = set()
        for person, years in self.evaluations_by_person.items():
            all_years.update(years.keys())
        return sorted(all_years)
    
    def get_all_people(self) -> List[str]:
        """Get all people in the dataset"""
        return sorted(list(self.evaluations_by_person.keys()))

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
        # Check for None or empty input
        if not frequencies:
            return 0.0
        
        # Ensure frequencies list has the right length
        if len(frequencies) < len(self.frequency_weights):
            # Pad with zeros if needed
            frequencies = list(frequencies) + [0] * (len(self.frequency_weights) - len(frequencies))
        elif len(frequencies) > len(self.frequency_weights):
            # Truncate if too long
            frequencies = frequencies[:len(self.frequency_weights)]

        # Calculate weighted sum using weights and frequencies
        try:
            weighted_sum = sum(
                freq * weight for freq, weight in zip(frequencies, self.frequency_weights)
            )
            
            # Normalize by total percentage (excluding n/a)
            total = sum(frequencies)
            
            return weighted_sum / total if total > 0 else 0.0
        except Exception as e:
            print(f"Error in calculate_weighted_score: {str(e)}, frequencies={frequencies}")
            return 0.0

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

        difference = {}
        for label in self.frequency_labels:
            # Ensure both distributions have all labels by defaulting to 0 if missing
            person_value = person_dist.get(label, 0)
            group_value = group_dist.get(label, 0)
            difference[label] = person_value - group_value

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
            not data.get("success", False)
            or "data" not in data
            or "direcionadores" not in data.get("data", {})
        ):
            return result

        # Extract all behavior scores
        for direcionador in data["data"]["direcionadores"]:
            dir_name = direcionador["direcionador"]
            result[dir_name] = {}

            for comportamento in direcionador["comportamentos"]:
                comp_name = comportamento["comportamento"]
                scores = {}

                # Get consolidated scores
                for avaliacao in comportamento.get("consolidado", []):
                    avaliador = avaliacao.get("avaliador", "Unknown")
                    person_freq = avaliacao.get("frequencias_colaborador", [])
                    group_freq = avaliacao.get("frequencias_grupo", [])

                    try:
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
                    except Exception as e:
                        print(f"Error processing scores for {person}, {year}, {dir_name}, {comp_name}, {avaliador}: {str(e)}")
                        # Add empty but valid data structure
                        scores[avaliador] = {
                            "freq_colaborador": [0] * len(self.frequency_labels),
                            "freq_grupo": [0] * len(self.frequency_labels),
                            "score_colaborador": 0,
                            "score_grupo": 0,
                            "difference": 0,
                            "comparison_by_category": {label: 0 for label in self.frequency_labels},
                        }

                # Also get individual evaluations
                individual_evals = {}
                for avaliacao in comportamento.get("avaliacoes_individuais", []):
                    avaliador = avaliacao.get("avaliador", "Unknown")
                    conceito = avaliacao.get("conceito", "n/a")
                    cor = avaliacao.get("cor", "#CCCCCC")
                    individual_evals[avaliador] = {"conceito": conceito, "cor": cor}

                result[dir_name][comp_name] = {
                    "scores": scores,
                    "individual_evaluations": individual_evals,
                }

        return result
    
    def get_evaluations_for_person(self, person: str, year: str) -> Dict[str, Any]:
        """Get raw evaluation data for a person in a specific year"""
        if person in self.evaluations_by_person and year in self.evaluations_by_person[person]:
            return self.evaluations_by_person[person][year]
        return {}
    
    def get_average_score(self, person: str, year: str) -> float:
        """Get the average score for a person in a specific year"""
        behavior_scores = self.get_behavior_scores(person, year)
        if not behavior_scores:
            return None
            
        total_score = 0.0
        count = 0
        
        for dir_name, behaviors in behavior_scores.items():
            for comp_name, details in behaviors.items():
                for avaliador, scores in details.get("scores", {}).items():
                    if avaliador == "%todos":  # Use the overall evaluation
                        total_score += scores.get("score_colaborador", 0)
                        count += 1
        
        return total_score / count if count > 0 else None
    
    def get_criteria_for_year(self, year: str) -> Dict[str, Set[str]]:
        """Get all criteria for a specific year"""
        if year in self.year_criteria:
            return self.year_criteria[year]
        return {}
        
    def get_score_for_criterion(self, person: str, year: str, criterion: str) -> float:
        """Get the score for a specific criterion (behavior)
        
        Args:
            person: The person name
            year: The evaluation year
            criterion: The criterion name (comportamento)
            
        Returns:
            The score or None if not found
        """
        behavior_scores = self.get_behavior_scores(person, year)
        if not behavior_scores:
            return None
            
        # Look for criterion in all direcionadores
        for dir_name, behaviors in behavior_scores.items():
            for comp_name, details in behaviors.items():
                # Check if this is the criterion we're looking for
                if comp_name == criterion or criterion in comp_name:
                    for avaliador, scores in details.get("scores", {}).items():
                        if avaliador == "%todos":  # Use the overall evaluation
                            return scores.get("score_colaborador")
        
        return None

    def compare_people_for_year(self, year: str) -> pd.DataFrame:
        """Compare all people for a specific year"""
        people = self.get_all_people_for_year(year)
        results = []
        
        # Skip processing if no people found
        if not people:
            print(f"Warning: No people found for year {year}")
            return pd.DataFrame()

        for person in people:
            try:
                data = self.evaluations_by_person[person][year]
                if not data.get("success", False) or "data" not in data:
                    print(f"Warning: Invalid data for {person} in {year}")
                    continue

                concept = data["data"].get("conceito_ciclo_filho_descricao", "Unknown")

                # Calculate scores across all behaviors
                total_score = 0
                total_group_score = 0
                count = 0

                # Store detailed comparisons for each category
                category_diffs = {label: 0 for label in self.frequency_labels}

                behavior_scores = self.get_behavior_scores(person, year)
                
                # Skip if no behavior scores found
                if not behavior_scores:
                    print(f"Warning: No behavior scores for {person} in {year}")
                    continue
                    
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
            except Exception as e:
                print(f"Error processing comparison for {person} in {year}: {str(e)}")
                continue

        # Return empty DataFrame if no results
        if not results:
            print(f"Warning: No valid results for year {year}")
            return pd.DataFrame()
        
        return pd.DataFrame(results)

    def find_common_behaviors(self, years: List[str]) -> Dict[str, Set[str]]:
        """Find behaviors that are common across all specified years"""
        if not years:
            return {}

        # Initialize with behaviors from the first year
        first_year = years[0]
        common_behaviors = {}
        
        if first_year not in self.year_criteria:
            return {}
            
        for dir_name, behaviors in self.year_criteria[first_year].items():
            common_behaviors[dir_name] = set(behaviors)

        # Intersect with behaviors from subsequent years
        for year in years[1:]:
            if year not in self.year_criteria:
                continue
                
            # Only keep direcionadores that exist in both
            direcionadores_to_remove = []
            for dir_name in common_behaviors:
                if dir_name not in self.year_criteria[year]:
                    direcionadores_to_remove.append(dir_name)
            
            for dir_name in direcionadores_to_remove:
                del common_behaviors[dir_name]
            
            # For remaining direcionadores, intersect behaviors
            for dir_name in list(common_behaviors.keys()):
                common_behaviors[dir_name] &= self.year_criteria[year][dir_name]
                
                # If no common behaviors left, remove the direcionador
                if not common_behaviors[dir_name]:
                    del common_behaviors[dir_name]

        return common_behaviors

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

        # Count behaviors found versus those in the common set
        common_count = sum(len(behaviors) for behaviors in common_behaviors.values())
        found_count = sum(len(behaviors) for behaviors in found_behaviors.values())

        # Calculate improvement from first to last year
        if len(years) >= 2:
            first_year = years[0]
            last_year = years[-1]
            if first_year in year_scores and last_year in year_scores:
                improvement = year_scores[last_year] - year_scores[first_year]
                relative_improvement = (
                    (year_scores[last_year] - year_scores[first_year])
                    / year_scores[first_year]
                    if year_scores[first_year] > 0
                    else 0
                )
            else:
                improvement = 0
                relative_improvement = 0
        else:
            improvement = 0
            relative_improvement = 0

        # Difference from group
        difference_from_group = {
            year: year_scores[year] - year_group_scores[year] for year in years
        }

        return {
            "person": person,
            "years": years,
            "concepts": concepts,
            "year_scores": year_scores,
            "year_group_scores": year_group_scores,
            "improvement": improvement,
            "relative_improvement": relative_improvement,
            "difference_from_group": difference_from_group,
            "year_categories": year_categories,
            "common_behaviors": {
                "count": common_count,
                "found": found_count,
                "behaviors": common_behaviors,
            },
            "common_year_scores": common_year_scores,
            "common_year_group_scores": common_year_group_scores,
        }

    def generate_comparative_report(self, year, output_path=None):
        """Generate a comparative report for a specific year"""
        try:
            # Get comparison data
            df = self.compare_people_for_year(year)
            
            if df.empty:
                print(f"No data available for year {year}")
                return None
                
            # Save plot if requested
            if output_path:
                self.plot_comparative_report(df, year, output_path)
                
            return df
        except Exception as e:
            print(f"Error generating comparative report for {year}: {str(e)}")
            return None

    def generate_historical_report(self, person: str, output_file: str = None):
        """Generate a historical report for a specific person"""
        data = self.person_year_over_year(person)
        
        if not data["years"]:
            print(f"No data available for {person}")
            return None
            
        years = data["years"]
        concepts = data["concepts"]
        year_scores = data["year_scores"]
        year_group_scores = data["year_group_scores"]
        year_categories = data["year_categories"]
        
        # Create figure with multiple subplots
        fig = plt.figure(figsize=(15, 10))
        
        # 1. Plot scores over time
        ax1 = plt.subplot2grid((2, 2), (0, 0))
        ax1.plot(years, [year_scores[y] for y in years], 'o-', color='#3498db', linewidth=2, label=person)
        ax1.plot(years, [year_group_scores[y] for y in years], 'o--', color='#7f8c8d', linewidth=2, label='Group Average')
        
        # Add concept annotations
        for i, year in enumerate(years):
            if year in concepts:
                concept = concepts[year]
                color = CONCEPT_CHART_COLORS.get(concept, "#7f8c8d")
                ax1.annotate(
                    concept,
                    (year, year_scores[year]),
                    xytext=(0, 10),
                    textcoords='offset points',
                    ha='center',
                    va='bottom',
                    bbox=dict(boxstyle='round,pad=0.3', fc=color, alpha=0.7, color='white'),
                    fontsize=8
                )
        
        ax1.set_title(f'Performance Over Time - {person}')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Average Score')
        ax1.legend()
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # 2. Plot difference from group
        ax2 = plt.subplot2grid((2, 2), (0, 1))
        diff_data = [year_scores[y] - year_group_scores[y] for y in years]
        bars = ax2.bar(years, diff_data)
        
        # Color bars based on positive/negative values
        for i, bar in enumerate(bars):
            if diff_data[i] > 0:
                bar.set_color('#2ecc71')  # Green for positive
            else:
                bar.set_color('#e74c3c')  # Red for negative
        
        ax2.set_title('Difference from Group Average')
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Difference')
        ax2.axhline(y=0, color='#7f8c8d', linestyle='-', alpha=0.5)
        ax2.grid(True, linestyle='--', alpha=0.7, axis='y')
        
        # 3. Plot category differences (heatmap-like)
        ax3 = plt.subplot2grid((2, 2), (1, 0), colspan=2)
        
        # Extract categories and prepare data matrix
        categories = list(self.frequency_labels)
        data_matrix = []
        
        for year in years:
            row = []
            for category in categories:
                row.append(year_categories[year].get(category, 0))
            data_matrix.append(row)
        
        # Create heatmap
        im = ax3.imshow(data_matrix, cmap='RdYlGn', aspect='auto', vmin=-30, vmax=30)
        
        # Add text annotations
        for i in range(len(years)):
            for j in range(len(categories)):
                value = data_matrix[i][j]
                text_color = 'black' if abs(value) < 20 else 'white'
                ax3.text(j, i, f"{value:.1f}%", 
                         ha="center", va="center", color=text_color,
                         fontsize=8)
        
        # Set ticks and labels
        ax3.set_xticks(range(len(categories)))
        ax3.set_xticklabels(categories, rotation=45, ha='right')
        ax3.set_yticks(range(len(years)))
        ax3.set_yticklabels(years)
        
        ax3.set_title('Category Differences from Group (%)')
        ax3.set_xlabel('Category')
        ax3.set_ylabel('Year')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax3, orientation='horizontal', pad=0.2)
        cbar.set_label('Difference from Group (%)')
        
        plt.tight_layout()
        
        # Save or show figure
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Report saved to {output_file}")
        
        # Return the analysis data
        return data

    def plot_comparative_report(self, df, year, output_path=None):
        """Generate plots for the comparative report"""
        # Sort by average score (descending)
        df_sorted = df.sort_values('Average Score', ascending=False)
        
        # Get number of people
        n_people = len(df_sorted)
        
        # Create figure with multiple subplots
        fig = plt.figure(figsize=(15, 10))
        
        # 1. Bar chart of average scores
        ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=2)
        
        # Create bars colored by concept
        bars = ax1.bar(range(n_people), df_sorted['Average Score'])
        
        # Color bars by concept
        concepts = df_sorted['Overall Concept']
        for i, concept in enumerate(concepts):
            color = CONCEPT_CHART_COLORS.get(concept, "#7f8c8d")
            bars[i].set_color(color)
        
        # Add labels and gridlines
        ax1.set_title(f'Average Scores by Person ({year})')
        ax1.set_ylabel('Average Score')
        ax1.set_xticks(range(n_people))
        ax1.set_xticklabels(df_sorted['Person'], rotation=45, ha='right')
        ax1.grid(True, linestyle='--', alpha=0.7, axis='y')
        
        # Add group average line
        group_avg = df_sorted['Group Average'].mean()
        ax1.axhline(y=group_avg, color='#e74c3c', linestyle='--', linewidth=2, 
                   label=f'Group Average: {group_avg:.2f}')
        ax1.legend()
        
        # 2. Concept distribution pie chart
        ax2 = plt.subplot2grid((2, 2), (1, 0))
        
        # Count concepts
        concept_counts = concepts.value_counts()
        
        # Define colors
        colors = [CONCEPT_CHART_COLORS.get(concept, "#7f8c8d") for concept in concept_counts.index]
        
        # Create pie chart
        ax2.pie(concept_counts, labels=concept_counts.index, autopct='%1.1f%%',
               colors=colors, startangle=90)
        ax2.set_title('Concept Distribution')
        
        # 3. Category differences boxplot
        ax3 = plt.subplot2grid((2, 2), (1, 1))
        
        # Extract category difference columns
        diff_columns = [col for col in df.columns if col.startswith('Diff ')]
        
        # Prepare data for boxplot
        box_data = []
        labels = []
        
        for col in diff_columns:
            box_data.append(df[col])
            # Extract just the category name from the column
            labels.append(col.replace('Diff ', ''))
        
        # Create boxplot
        ax3.boxplot(box_data, labels=labels, patch_artist=True)
        ax3.set_title('Category Differences Distribution')
        ax3.set_ylabel('Difference from Group (%)')
        ax3.axhline(y=0, color='#7f8c8d', linestyle='-', alpha=0.5)
        plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Save or show figure
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Report saved to {output_path}")

    def get_available_years(self) -> Set[str]:
        """Get all available years in the dataset (alias for get_all_years)"""
        return set(self.get_all_years())
    
    def get_available_people(self) -> Set[str]:
        """Get all people in the dataset (alias for get_all_people)"""
        return set(self.get_all_people())
        
    def get_years_for_person(self, person: str) -> Set[str]:
        """Get all years for a specific person"""
        if person in self.evaluations_by_person:
            return set(self.evaluations_by_person[person].keys())
        return set()
        
    def get_people_for_year(self, year: str) -> Set[str]:
        """Get all people for a specific year"""
        return set(self.get_all_people_for_year(year))


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
        if result is not None and args.details:
            print("\nHistorical Analysis:")
            for year in result["years"]:
                print(
                    f"\n{year}: Score={result['year_scores'][year]:.2f}, "
                    f"Group={result['year_group_scores'][year]:.2f}, "
                    f"Diff={result['difference_from_group'][year]:.2f}, "
                    f"Concept={result['concepts'].get(year, 'N/A')}"
                )

                print("\nCategory Differences:")
                for category, diff in result["year_categories"][year].items():
                    print(f"  {category}: {diff:.2f}%")

    if not args.year and not args.person and not args.list_criteria:
        parser.print_help() 