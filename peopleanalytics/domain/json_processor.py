"""
JSON processor for extracting and analyzing performance evaluation data.

This module is responsible for parsing, validating, and extracting data
from JSON files containing performance evaluation data.
"""

import json
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class JsonProcessor:
    """Processes performance evaluation data from JSON files."""

    def __init__(self):
        """Initialize the JSON processor."""
        self.logger = logging.getLogger(__name__)

    def load_json_file(self, file_path: str) -> Dict:
        """
        Load and parse a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Dictionary with parsed JSON data, or empty dict on error
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception as e:
            self.logger.error(f"Error loading JSON file {file_path}: {e}")
            return {}

    def extract_evaluation_data(self, json_data: Dict) -> Dict:
        """
        Extract relevant evaluation data from JSON.

        Args:
            json_data: JSON data dictionary

        Returns:
            Dictionary with extracted data
        """
        # Check if we have the expected structure
        if not isinstance(json_data, dict):
            self.logger.warning("Invalid JSON data format: not a dictionary")
            return {}

        # Check for the outer structure (success/data structure)
        if "data" in json_data:
            data = json_data["data"]
        else:
            data = json_data  # Assume data is directly in the root

        # Extract basic information
        extracted = {
            "conceito": data.get("conceito_ciclo_filho_descricao", "Não disponível"),
            "peer_group": data.get("nome_peer_group"),
            "direcionadores": {},
            "comportamentos": {},
            "avaliacoes": {},
        }

        # Process direcionadores and comportamentos
        direcionadores = data.get("direcionadores", [])
        if not direcionadores:
            self.logger.warning("No 'direcionadores' found in JSON data")
            return extracted

        # Process each direcionador
        for direcionador_data in direcionadores:
            direcionador_name = direcionador_data.get("direcionador", "Unknown")
            extracted["direcionadores"][direcionador_name] = {
                "pergunta_final": direcionador_data.get("pergunta_final", False),
                "comportamentos": [],
            }

            # Process comportamentos within this direcionador
            comportamentos = direcionador_data.get("comportamentos", [])
            for comportamento_data in comportamentos:
                comportamento_name = comportamento_data.get("comportamento", "Unknown")

                # Add to the direcionador's comportamentos list
                extracted["direcionadores"][direcionador_name]["comportamentos"].append(
                    comportamento_name
                )

                # Add to the global comportamentos dictionary
                extracted["comportamentos"][comportamento_name] = {
                    "direcionador": direcionador_name,
                    "pergunta_final": comportamento_data.get("pergunta_final", False),
                    "avaliacoes": {},
                }

                # Process avaliacoes for this comportamento
                avaliacoes = comportamento_data.get("avaliacoes_grupo", [])
                for avaliacao_data in avaliacoes:
                    avaliador = avaliacao_data.get("avaliador", "Unknown")

                    # Extract frequencies
                    freq_colaborador = avaliacao_data.get(
                        "frequencia_colaborador", [0, 0, 0, 0, 0, 0]
                    )
                    freq_grupo = avaliacao_data.get(
                        "frequencia_grupo", [0, 0, 0, 0, 0, 0]
                    )

                    # Normalize to ensure we have 6 values
                    if len(freq_colaborador) < 6:
                        freq_colaborador.extend([0] * (6 - len(freq_colaborador)))
                    if len(freq_grupo) < 6:
                        freq_grupo.extend([0] * (6 - len(freq_grupo)))

                    # Add to the comportamento's avaliacoes
                    extracted["comportamentos"][comportamento_name]["avaliacoes"][
                        avaliador
                    ] = {"freq_colaborador": freq_colaborador, "freq_grupo": freq_grupo}

                    # Also add to global avaliacoes for easy access
                    avaliacao_key = f"{comportamento_name}:{avaliador}"
                    extracted["avaliacoes"][avaliacao_key] = {
                        "comportamento": comportamento_name,
                        "avaliador": avaliador,
                        "freq_colaborador": freq_colaborador,
                        "freq_grupo": freq_grupo,
                    }

        return extracted

    def process_evaluation_data(self, json_file_path: str) -> Dict:
        """
        Process an evaluation JSON file.

        Args:
            json_file_path: Path to the JSON file

        Returns:
            Dictionary with processed data
        """
        # Load the JSON file
        json_data = self.load_json_file(json_file_path)
        if not json_data:
            return {}

        # Extract evaluation data
        extracted_data = self.extract_evaluation_data(json_data)

        # Enhance the extracted data with additional metrics
        # Like global scores, status summaries, etc.
        enhanced_data = self.enhance_evaluation_data(extracted_data)

        return enhanced_data

    def enhance_evaluation_data(self, extracted_data: Dict) -> Dict:
        """
        Enhance extracted data with additional derived metrics.

        Args:
            extracted_data: Dictionary with extracted evaluation data

        Returns:
            Dictionary with enhanced data
        """
        # Create a copy to avoid modifying the original
        enhanced = extracted_data.copy()

        # Add global metrics
        enhanced["metrics"] = {
            "total_direcionadores": len(enhanced["direcionadores"]),
            "total_comportamentos": len(enhanced["comportamentos"]),
            "total_avaliacoes": len(enhanced["avaliacoes"]),
        }

        # Calculate overall statistics for all comportamentos
        all_freq_colaborador = [0, 0, 0, 0, 0, 0]
        all_freq_grupo = [0, 0, 0, 0, 0, 0]
        count = 0

        # Sum up frequencies across all comportamentos for "todos" avaliador
        for comp_name, comp_data in enhanced["comportamentos"].items():
            if "todos" in comp_data["avaliacoes"]:
                avaliacao = comp_data["avaliacoes"]["todos"]
                for i in range(6):
                    all_freq_colaborador[i] += avaliacao["freq_colaborador"][i]
                    all_freq_grupo[i] += avaliacao["freq_grupo"][i]
                count += 1

        # Calculate averages
        if count > 0:
            all_freq_colaborador = [f / count for f in all_freq_colaborador]
            all_freq_grupo = [f / count for f in all_freq_grupo]

        # Add global frequencies
        enhanced["global_freq"] = {
            "colaborador": all_freq_colaborador,
            "grupo": all_freq_grupo,
        }

        # Calculate global scores
        enhanced["global_scores"] = self.calculate_global_scores(
            all_freq_colaborador, all_freq_grupo
        )

        # Calculate statistics per direcionador
        enhanced["direcionador_stats"] = {}
        for direcionador_name, direcionador_data in enhanced["direcionadores"].items():
            comportamentos = direcionador_data["comportamentos"]

            # Frequencies for this direcionador
            dir_freq_colaborador = [0, 0, 0, 0, 0, 0]
            dir_freq_grupo = [0, 0, 0, 0, 0, 0]
            dir_count = 0

            # Calculate for each comportamento in this direcionador
            for comp_name in comportamentos:
                if comp_name in enhanced["comportamentos"]:
                    comp_data = enhanced["comportamentos"][comp_name]
                    if "todos" in comp_data["avaliacoes"]:
                        avaliacao = comp_data["avaliacoes"]["todos"]
                        for i in range(6):
                            dir_freq_colaborador[i] += avaliacao["freq_colaborador"][i]
                            dir_freq_grupo[i] += avaliacao["freq_grupo"][i]
                        dir_count += 1

            # Calculate averages for this direcionador
            if dir_count > 0:
                dir_freq_colaborador = [f / dir_count for f in dir_freq_colaborador]
                dir_freq_grupo = [f / dir_count for f in dir_freq_grupo]

            # Add direcionador statistics
            enhanced["direcionador_stats"][direcionador_name] = {
                "num_comportamentos": len(comportamentos),
                "freq_colaborador": dir_freq_colaborador,
                "freq_grupo": dir_freq_grupo,
                "scores": self.calculate_global_scores(
                    dir_freq_colaborador, dir_freq_grupo
                ),
            }

        return enhanced

    def calculate_global_scores(
        self, freq_colaborador: List[float], freq_grupo: List[float]
    ) -> Dict:
        """
        Calculate global scores from frequency distributions.

        Args:
            freq_colaborador: List of collaborator frequency values
            freq_grupo: List of group frequency values

        Returns:
            Dictionary with calculated scores
        """
        # Calculate weighted average scores
        # Weights: N/A=0, Referência=5, Acima=4, Dentro=3, Abaixo=2, Muito abaixo=1
        weights = [0, 5, 4, 3, 2, 1]

        # Calculate weighted score for collaborator
        colab_score = 0
        colab_total = sum(freq_colaborador)
        if colab_total > 0:
            for i, freq in enumerate(freq_colaborador):
                colab_score += (freq / colab_total) * weights[i]

        # Calculate weighted score for group
        group_score = 0
        group_total = sum(freq_grupo)
        if group_total > 0:
            for i, freq in enumerate(freq_grupo):
                group_score += (freq / group_total) * weights[i]

        # Normalize to 0-100 scale (max score is 5, min is 0)
        colab_norm = (colab_score / 5) * 100 if colab_score > 0 else 0
        group_norm = (group_score / 5) * 100 if group_score > 0 else 0

        # Calculate gaps
        raw_gap = colab_score - group_score
        normalized_gap = colab_norm - group_norm

        # Category-level gaps
        category_gaps = [
            freq_colaborador[i] - freq_grupo[i] for i in range(len(freq_colaborador))
        ]

        # Calculate status based on gaps
        if abs(normalized_gap) < 5:
            status = "alinhado"
        elif normalized_gap > 10:
            status = "acima"
        elif normalized_gap > 5:
            status = "levemente_acima"
        elif normalized_gap < -10:
            status = "abaixo"
        elif normalized_gap < -5:
            status = "levemente_abaixo"
        else:
            status = "neutro"

        return {
            "colab_score": colab_score,
            "group_score": group_score,
            "colab_normalized": colab_norm,
            "group_normalized": group_norm,
            "raw_gap": raw_gap,
            "normalized_gap": normalized_gap,
            "category_gaps": category_gaps,
            "status": status,
        }

    def process_multiple_files(self, file_paths: List[str]) -> Dict[str, Dict]:
        """
        Process multiple evaluation JSON files.

        Args:
            file_paths: List of paths to JSON files

        Returns:
            Dictionary mapping file paths to processed data
        """
        results = {}

        for file_path in file_paths:
            try:
                results[file_path] = self.process_evaluation_data(file_path)
            except Exception as e:
                self.logger.error(f"Error processing file {file_path}: {e}")
                results[file_path] = {"error": str(e)}

        return results

    def combine_evaluation_data(self, processed_files: Dict[str, Dict]) -> Dict:
        """
        Combine data from multiple processed files into a single dataset.

        Args:
            processed_files: Dictionary mapping file paths to processed data

        Returns:
            Dictionary with combined data
        """
        combined = {
            "files": list(processed_files.keys()),
            "direcionadores": set(),
            "comportamentos": {},
            "global_freq": {
                "colaborador": [0, 0, 0, 0, 0, 0],
                "grupo": [0, 0, 0, 0, 0, 0],
            },
        }

        # Collect all unique direcionadores and comportamentos
        for file_path, data in processed_files.items():
            if "direcionadores" in data:
                for direcionador in data["direcionadores"]:
                    combined["direcionadores"].add(direcionador)

            if "comportamentos" in data:
                for comp_name, comp_data in data["comportamentos"].items():
                    if comp_name not in combined["comportamentos"]:
                        combined["comportamentos"][comp_name] = {
                            "files": [],
                            "avaliacoes": {},
                        }

                    # Add this file to the comportamento's files
                    combined["comportamentos"][comp_name]["files"].append(file_path)

                    # Combine avaliacoes
                    for avaliador, avaliacao in comp_data.get("avaliacoes", {}).items():
                        if (
                            avaliador
                            not in combined["comportamentos"][comp_name]["avaliacoes"]
                        ):
                            combined["comportamentos"][comp_name]["avaliacoes"][
                                avaliador
                            ] = {
                                "freq_colaborador": avaliacao[
                                    "freq_colaborador"
                                ].copy(),
                                "freq_grupo": avaliacao["freq_grupo"].copy(),
                                "count": 1,
                            }
                        else:
                            # Average the frequencies
                            existing = combined["comportamentos"][comp_name][
                                "avaliacoes"
                            ][avaliador]
                            for i in range(6):
                                existing["freq_colaborador"][i] += avaliacao[
                                    "freq_colaborador"
                                ][i]
                                existing["freq_grupo"][i] += avaliacao["freq_grupo"][i]
                            existing["count"] += 1

            # Combine global frequencies
            if "global_freq" in data:
                for i in range(6):
                    combined["global_freq"]["colaborador"][i] += data["global_freq"][
                        "colaborador"
                    ][i]
                    combined["global_freq"]["grupo"][i] += data["global_freq"]["grupo"][
                        i
                    ]

        # Calculate averages for combined data
        num_files = len(processed_files)
        if num_files > 0:
            # Average global frequencies
            combined["global_freq"]["colaborador"] = [
                f / num_files for f in combined["global_freq"]["colaborador"]
            ]
            combined["global_freq"]["grupo"] = [
                f / num_files for f in combined["global_freq"]["grupo"]
            ]

            # Average comportamento frequencies
            for comp_name, comp_data in combined["comportamentos"].items():
                for avaliador, avaliacao in comp_data["avaliacoes"].items():
                    count = avaliacao["count"]
                    if count > 0:
                        avaliacao["freq_colaborador"] = [
                            f / count for f in avaliacao["freq_colaborador"]
                        ]
                        avaliacao["freq_grupo"] = [
                            f / count for f in avaliacao["freq_grupo"]
                        ]

        # Convert direcionadores set to list for JSON serialization
        combined["direcionadores"] = list(combined["direcionadores"])

        # Calculate global scores
        combined["global_scores"] = self.calculate_global_scores(
            combined["global_freq"]["colaborador"], combined["global_freq"]["grupo"]
        )

        return combined
