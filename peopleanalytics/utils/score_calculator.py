"""
Score calculator utility for processing evaluations.

This module centralizes the logic for calculating scores from various types of evaluations
including self-evaluations and feedback from peers, managers, and partners.
"""

import logging
from typing import Any, Dict, List, Optional


class ScoreCalculator:
    """
    Centralizes calculation of scores based on evaluations from different sources.

    This class provides methods for:
    - Calculating weighted averages based on frequency
    - Normalizing scores across different evaluation types
    - Generating overall scores from multiple evaluation sources
    - Handling missing data and special cases
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the score calculator with optional configuration.

        Args:
            config: Configuration dictionary with weights and normalization factors
        """
        self.logger = logging.getLogger("score_calculator")

        # Default configuration
        self.config = {
            # Default weights for different evaluation types
            "weights": {
                "self": 1.0,
                "peer": 1.0,
                "manager": 1.5,
                "partner": 1.0,
            },
            # Scale normalization factors (if evaluations use different scales)
            "scale_normalization": {
                "5_to_10": 2.0,  # Convert 5-point scale to 10-point
                "7_to_10": 10 / 7,  # Convert 7-point scale to 10-point
            },
            # Minimum number of evaluations required for calculation
            "min_evaluations": {
                "peer": 2,
                "partner": 1,
                "manager": 1,
            },
            # Configure frequency weight calculation
            "frequency": {
                "always": 1.0,
                "often": 0.75,
                "sometimes": 0.5,
                "rarely": 0.25,
                "never": 0.0,
            },
        }

        # Update with user config if provided
        if config:
            self._update_config(config)

    def _update_config(self, config: Dict[str, Any]) -> None:
        """
        Update the configuration with user-provided values.

        Args:
            config: Configuration dictionary to merge with defaults
        """
        for section, values in config.items():
            if section in self.config:
                if isinstance(self.config[section], dict) and isinstance(values, dict):
                    self.config[section].update(values)
                else:
                    self.config[section] = values
            else:
                self.config[section] = values

    def calculate_weighted_average(
        self,
        evaluations: List[Dict[str, Any]],
        value_key: str = "value",
        frequency_key: str = "frequency",
    ) -> float:
        """
        Calculate weighted average based on values and frequencies.

        Args:
            evaluations: List of evaluation dictionaries
            value_key: Key for the value in each evaluation
            frequency_key: Key for the frequency in each evaluation

        Returns:
            Weighted average score or 0.0 if no valid evaluations
        """
        if not evaluations:
            return 0.0

        total_weight = 0.0
        weighted_sum = 0.0

        for eval_item in evaluations:
            if value_key not in eval_item or frequency_key not in eval_item:
                continue

            value = eval_item[value_key]
            frequency = eval_item[frequency_key].lower()

            # Skip if value is not numeric or frequency is not recognized
            if (
                not isinstance(value, (int, float))
                or frequency not in self.config["frequency"]
            ):
                continue

            weight = self.config["frequency"].get(frequency, 0.0)
            weighted_sum += value * weight
            total_weight += weight

        if total_weight > 0:
            return weighted_sum / total_weight
        return 0.0

    def normalize_score(self, score: float, source_scale: str = "10") -> float:
        """
        Normalize a score to the standard 10-point scale.

        Args:
            score: The original score
            source_scale: The scale of the original score ("5", "7", "10")

        Returns:
            Normalized score on 10-point scale
        """
        if score == 0:
            return 0.0

        normalization_key = f"{source_scale}_to_10"
        if normalization_key in self.config["scale_normalization"]:
            return score * self.config["scale_normalization"][normalization_key]
        return score  # Already on the correct scale

    def calculate_overall_score(
        self, evaluation_data: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Calculate overall score from multiple evaluation sources.

        Args:
            evaluation_data: Dictionary with evaluation sources as keys
                             (self, peer, manager, partner) and lists of
                             evaluation items as values

        Returns:
            Dictionary with calculated scores by source and overall score
        """
        results = {
            "by_source": {},
            "overall_score": 0.0,
            "overall_count": 0,
            "valid": False,
        }

        total_weighted_score = 0.0
        total_weight = 0.0

        # Process each evaluation source
        for source, evaluations in evaluation_data.items():
            if not evaluations:
                results["by_source"][source] = {
                    "score": 0.0,
                    "count": 0,
                    "valid": False,
                }
                continue

            # Check if we have enough evaluations for this source
            min_required = self.config["min_evaluations"].get(source, 1)
            if len(evaluations) < min_required:
                results["by_source"][source] = {
                    "score": 0.0,
                    "count": len(evaluations),
                    "valid": False,
                    "reason": f"Insufficient evaluations. Requires at least {min_required}.",
                }
                continue

            # Calculate score for this source
            source_score = self.calculate_weighted_average(evaluations)

            # Store results for this source
            results["by_source"][source] = {
                "score": source_score,
                "count": len(evaluations),
                "valid": True,
            }

            # Add to overall calculation
            source_weight = self.config["weights"].get(source, 1.0)
            total_weighted_score += source_score * source_weight
            total_weight += source_weight
            results["overall_count"] += len(evaluations)

        # Calculate overall score if we have valid sources
        if total_weight > 0:
            results["overall_score"] = total_weighted_score / total_weight
            results["valid"] = True

        return results

    def calculate_skill_scores(
        self, evaluation_data: Dict[str, List[Dict[str, Any]]], skill_key: str = "skill"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate scores for each skill across evaluation sources.

        Args:
            evaluation_data: Dictionary with evaluation sources as keys and lists
                            of evaluation items as values
            skill_key: Key for the skill identifier in each evaluation

        Returns:
            Dictionary with skill IDs as keys and score data as values
        """
        skill_data: Dict[str, Dict[str, Any]] = {}

        # Organize evaluations by skill
        for source, evaluations in evaluation_data.items():
            source_weight = self.config["weights"].get(source, 1.0)

            for eval_item in evaluations:
                if skill_key not in eval_item:
                    continue

                skill_id = eval_item[skill_key]

                # Initialize skill data if not already present
                if skill_id not in skill_data:
                    skill_data[skill_id] = {
                        "by_source": {},
                        "overall_score": 0.0,
                        "overall_count": 0,
                        "valid": False,
                    }

                # Initialize source data for this skill if not already present
                if source not in skill_data[skill_id]["by_source"]:
                    skill_data[skill_id]["by_source"][source] = {
                        "evaluations": [],
                        "score": 0.0,
                        "count": 0,
                        "valid": False,
                    }

                # Add evaluation to this skill's source data
                skill_data[skill_id]["by_source"][source]["evaluations"].append(
                    eval_item
                )
                skill_data[skill_id]["by_source"][source]["count"] += 1

        # Calculate scores for each skill
        for skill_id, data in skill_data.items():
            total_weighted_score = 0.0
            total_weight = 0.0

            # Calculate scores for each source
            for source, source_data in data["by_source"].items():
                evaluations = source_data["evaluations"]

                # Check if we have enough evaluations
                min_required = self.config["min_evaluations"].get(source, 1)
                if len(evaluations) < min_required:
                    source_data["valid"] = False
                    source_data["reason"] = (
                        f"Insufficient evaluations. Requires at least {min_required}."
                    )
                    continue

                # Calculate score for this source
                source_score = self.calculate_weighted_average(evaluations)
                source_data["score"] = source_score
                source_data["valid"] = True

                # Add to overall calculation
                source_weight = self.config["weights"].get(source, 1.0)
                total_weighted_score += source_score * source_weight
                total_weight += source_weight
                data["overall_count"] += len(evaluations)

            # Calculate overall score if we have valid sources
            if total_weight > 0:
                data["overall_score"] = total_weighted_score / total_weight
                data["valid"] = True

            # Remove raw evaluations to clean up the output
            for source_data in data["by_source"].values():
                if "evaluations" in source_data:
                    del source_data["evaluations"]

        return skill_data
