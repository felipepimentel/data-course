import os
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import json
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt

from peopleanalytics.constants import FREQUENCY_LABELS, FREQUENCY_WEIGHTS, calculate_score

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
        self.frequency_labels = ["n/a", "referencia", "sempre", "quase sempre", "poucas vezes", "raramente"]
        self.frequency_weights = [0, 2.5, 4, 3, 2, 1]
        
        # For storing evaluations by person and year
        self.evaluations_by_person = defaultdict(dict)
        
        # Ensure the base directory exists
        os.makedirs(self.base_path, exist_ok=True)
        
        # Load schema manager for validation
        self.schema_manager = SchemaManager()
        
        # Load all evaluations
        self.load_all_evaluations()

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

    def get_all_people(self) -> List[str]:
        """Get all people in the dataset"""
        return sorted(list(self.evaluations_by_person.keys()))
        
    def get_all_years(self) -> List[str]:
        """Get all available years in the dataset"""
        all_years = set()
        for person, years in self.evaluations_by_person.items():
            all_years.update(years.keys())
        return sorted(all_years)
        
    def get_evaluations_for_person(self, person: str, year: str) -> Dict[str, Any]:
        """Get raw evaluation data for a person in a specific year"""
        if person in self.evaluations_by_person and year in self.evaluations_by_person[person]:
            return self.evaluations_by_person[person][year]
        return {}
        
    def get_behavior_scores(self, person: str, year: str) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Extract behavior scores for all direcionadores"""
        result = {}
        if person not in self.evaluations_by_person or year not in self.evaluations_by_person[person]:
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
                        result[dir_name][comp_name] = {
                            "scores": {}
                        }
                        
                        # First try to get scores from consolidado
                        has_consolidado_scores = False
                        for avaliacao in comportamento.get("consolidado", []):
                            avaliador = avaliacao.get("avaliador", "Unknown")
                            freq_colaborador = avaliacao.get("frequencias_colaborador", [])
                            freq_grupo = avaliacao.get("frequencias_grupo", [])
                            
                            try:
                                result[dir_name][comp_name]["scores"][avaliador] = {
                                    "score_colaborador": self.calculate_weighted_score(freq_colaborador),
                                    "score_grupo": self.calculate_weighted_score(freq_grupo),
                                    "comparison_by_category": self.compare_with_group(freq_colaborador, freq_grupo)
                                }
                                has_consolidado_scores = True
                            except Exception as e:
                                print(f"Error processing consolidado scores for {person}, {year}, {dir_name}, {comp_name}, {avaliador}: {str(e)}")
                        
                        # If no consolidado scores, try avaliacoes_grupo
                        if not has_consolidado_scores:
                            for avaliacao in comportamento.get("avaliacoes_grupo", []):
                                avaliador = avaliacao.get("avaliador", "Unknown")
                                freq_colaborador = avaliacao.get("frequencia_colaborador", [])
                                freq_grupo = avaliacao.get("frequencia_grupo", [])
                                
                                try:
                                    result[dir_name][comp_name]["scores"][avaliador] = {
                                        "score_colaborador": self.calculate_weighted_score(freq_colaborador),
                                        "score_grupo": self.calculate_weighted_score(freq_grupo),
                                        "comparison_by_category": self.compare_with_group(freq_colaborador, freq_grupo)
                                    }
                                except Exception as e:
                                    print(f"Error processing avaliacoes_grupo scores for {person}, {year}, {dir_name}, {comp_name}, {avaliador}: {str(e)}")
                return result
            
        # Original code for standard structure
        if "direcionadores" not in data.get("data", {}):
            return result
            
        for direcionador in data["data"]["direcionadores"]:
            dir_name = direcionador.get("direcionador", "Unknown")
            result[dir_name] = {}
            
            for comportamento in direcionador.get("comportamentos", []):
                comp_name = comportamento.get("comportamento", "Unknown")
                result[dir_name][comp_name] = {
                    "scores": {}
                }
                
                # First try to get scores from consolidado
                has_consolidado_scores = False
                for avaliacao in comportamento.get("consolidado", []):
                    avaliador = avaliacao.get("avaliador", "Unknown")
                    freq_colaborador = avaliacao.get("frequencias_colaborador", [])
                    freq_grupo = avaliacao.get("frequencias_grupo", [])
                    
                    try:
                        result[dir_name][comp_name]["scores"][avaliador] = {
                            "score_colaborador": self.calculate_weighted_score(freq_colaborador),
                            "score_grupo": self.calculate_weighted_score(freq_grupo),
                            "comparison_by_category": self.compare_with_group(freq_colaborador, freq_grupo)
                        }
                        has_consolidado_scores = True
                    except Exception as e:
                        print(f"Error processing consolidado scores for {person}, {year}, {dir_name}, {comp_name}, {avaliador}: {str(e)}")
                
                # If no consolidado scores, try avaliacoes_grupo
                if not has_consolidado_scores:
                    for avaliacao in comportamento.get("avaliacoes_grupo", []):
                        avaliador = avaliacao.get("avaliador", "Unknown")
                        freq_colaborador = avaliacao.get("frequencia_colaborador", [])
                        freq_grupo = avaliacao.get("frequencia_grupo", [])
                        
                        try:
                            result[dir_name][comp_name]["scores"][avaliador] = {
                                "score_colaborador": self.calculate_weighted_score(freq_colaborador),
                                "score_grupo": self.calculate_weighted_score(freq_grupo),
                                "comparison_by_category": self.compare_with_group(freq_colaborador, freq_grupo)
                            }
                        except Exception as e:
                            print(f"Error processing avaliacoes_grupo scores for {person}, {year}, {dir_name}, {comp_name}, {avaliador}: {str(e)}")
        
        return result
        
    def calculate_weighted_score(self, frequencies: List[int], use_nps_model: bool = False) -> float:
        """Calculate a weighted score from frequency distribution vectors
        
        Args:
            frequencies: List of integers representing the frequency distribution
                where positions mean: [n/a, referencia, sempre, quase sempre, poucas vezes, raramente]
            use_nps_model: Whether to use the improved NPS-like scoring model
                
        Returns:
            A weighted score based on the significance of each position in the vector
        """
        try:
            # Use the centralized scoring function from constants module
            return calculate_score(frequencies, use_nps_model)
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
    
    def compare_with_group(self, person_freq: List[int], group_freq: List[int]) -> Dict[str, float]:
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
        
    def compare_people_for_year(self, year: str) -> pd.DataFrame:
        """Compare all people for a specific year"""
        people = self.get_all_people()
        results = []
        
        # Skip processing if no people found
        if not people:
            print(f"Warning: No people found for year {year}")
            return pd.DataFrame()

        for person in people:
            try:
                if year not in self.evaluations_by_person.get(person, {}):
                    continue
                    
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
        
    def plot_comparative_report(self, df, year, output_path=None):
        """Create a simple plot of comparative results"""
        try:
            import seaborn as sns
            
            # Basic bar chart of scores
            plt.figure(figsize=(12, 6))
            
            # Sort by average score
            df_sorted = df.sort_values("Average Score", ascending=False)
            
            # Create position for bars
            x = range(len(df_sorted))
            width = 0.35
            
            # Plot bars
            plt.bar([pos - width/2 for pos in x], df_sorted["Average Score"], width, label="Person Score")
            plt.bar([pos + width/2 for pos in x], df_sorted["Group Average"], width, label="Group Average")
            
            # Add labels and title
            plt.xlabel("Person")
            plt.ylabel("Score")
            plt.title(f"Comparative Analysis - {year}")
            plt.xticks(x, df_sorted["Person"], rotation=45, ha="right")
            plt.legend()
            
            # Add grid
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            
            # Adjust layout
            plt.tight_layout()
            
            # Save or show
            if output_path:
                plt.savefig(output_path)
                plt.close()
            else:
                plt.show()
                
            return True
        except Exception as e:
            print(f"Error creating plot: {str(e)}")
            return False