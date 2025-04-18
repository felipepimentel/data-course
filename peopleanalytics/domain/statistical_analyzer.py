"""
Statistical analysis module for advanced performance evaluations.

This module provides advanced statistical analysis for performance data,
including distribution metrics, significance tests, and principal component analysis.
"""

import logging

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


class StatisticalAnalyzer:
    """Performs advanced statistical analysis on performance evaluation data."""

    def __init__(self):
        """Initialize the statistical analyzer."""
        self.logger = logging.getLogger(__name__)

    def calculate_z_scores(self, individual_data, group_data):
        """
        Calculate Z-scores to compare individual to group.

        Args:
            individual_data: Individual frequency distribution
            group_data: Group frequency distribution

        Returns:
            Dictionary with z-scores for each category
        """
        z_scores = {}

        try:
            for i in range(len(individual_data)):
                # Skip if group has no variation (avoid division by zero)
                if np.std(group_data) == 0:
                    z_scores[i] = 0
                    continue

                # Calculate z-score
                z_scores[i] = (individual_data[i] - np.mean(group_data)) / np.std(
                    group_data
                )
        except Exception as e:
            self.logger.error(f"Error calculating z-scores: {e}")
            z_scores = {i: 0 for i in range(len(individual_data))}

        return z_scores

    def calculate_confidence_intervals(self, data, confidence=0.95):
        """
        Calculate confidence intervals for a data set.

        Args:
            data: List or array of numerical values
            confidence: Confidence level (default: 0.95 for 95%)

        Returns:
            Tuple with (lower_bound, upper_bound)
        """
        try:
            data = np.array(data)
            n = len(data)
            mean = np.mean(data)
            sem = stats.sem(data)
            interval = sem * stats.t.ppf((1 + confidence) / 2, n - 1)
            return (mean - interval, mean + interval)
        except Exception as e:
            self.logger.error(f"Error calculating confidence intervals: {e}")
            return (0, 0)

    def run_significance_test(self, individual_data, group_data):
        """
        Run t-test to determine if differences are statistically significant.

        Args:
            individual_data: Individual frequency distribution
            group_data: Group frequency distribution

        Returns:
            Dictionary with t-statistic, p-value and significance flag
        """
        try:
            t_stat, p_value = stats.ttest_ind(
                individual_data, group_data, equal_var=False
            )
            significance = "not significant"
            if p_value < 0.001:
                significance = "p < 0.001"
            elif p_value < 0.01:
                significance = "p < 0.01"
            elif p_value < 0.05:
                significance = "p < 0.05"
            elif p_value < 0.1:
                significance = "p < 0.1"

            return {
                "t_statistic": t_stat,
                "p_value": p_value,
                "significance": significance,
                "is_significant": p_value < 0.05,
            }
        except Exception as e:
            self.logger.error(f"Error running significance test: {e}")
            return {
                "t_statistic": 0,
                "p_value": 1.0,
                "significance": "error",
                "is_significant": False,
            }

    def calculate_gap_metrics(self, individual_freq, group_freq):
        """
        Calculate gap metrics between individual and group frequencies.

        Args:
            individual_freq: List of individual frequency values
            group_freq: List of group frequency values

        Returns:
            Dictionary with gap metrics
        """
        gaps = [individual_freq[i] - group_freq[i] for i in range(len(individual_freq))]
        absolute_gaps = [abs(gap) for gap in gaps]

        return {
            "gaps": gaps,
            "absolute_gaps": absolute_gaps,
            "total_gap": sum(gaps),
            "total_absolute_gap": sum(absolute_gaps),
            "max_positive_gap": max(gaps),
            "max_negative_gap": min(gaps),
            "max_positive_index": gaps.index(max(gaps)) if max(gaps) > 0 else None,
            "max_negative_index": gaps.index(min(gaps)) if min(gaps) < 0 else None,
        }

    def calculate_normalized_score(self, frequencies):
        """
        Calculate normalized score from frequency distribution.

        The score weights each level with a value:
        - N/A: 0
        - Referência: 100
        - Acima do esperado: 85
        - Dentro do esperado: 70
        - Abaixo do esperado: 40
        - Muito abaixo do esperado: 10

        Args:
            frequencies: List of frequency values [na, ref, acima, dentro, abaixo, muito_abaixo]

        Returns:
            Normalized score (0-100)
        """
        weights = [0, 100, 85, 70, 40, 10]

        try:
            # Make sure frequencies sum to 100%
            total = sum(frequencies)
            if total == 0:
                return 0

            normalized_freq = [f / total * 100 if total > 0 else 0 for f in frequencies]

            # Calculate weighted score
            score = (
                sum(normalized_freq[i] * weights[i] for i in range(len(weights))) / 100
            )
            return score
        except Exception as e:
            self.logger.error(f"Error calculating normalized score: {e}")
            return 0

    def analyze_distributions(self, individual_freq, group_freq):
        """
        Perform comprehensive analysis of frequency distributions.

        Args:
            individual_freq: List of individual frequency values
            group_freq: List of group frequency values

        Returns:
            Dictionary with distribution analysis metrics
        """
        # Calculate basic stats
        individual_score = self.calculate_normalized_score(individual_freq)
        group_score = self.calculate_normalized_score(group_freq)

        # Calculate gaps
        gap_metrics = self.calculate_gap_metrics(individual_freq, group_freq)

        # Run significance test
        sig_test = self.run_significance_test(individual_freq, group_freq)

        # Calculate additional metrics
        # Concentration: higher values mean more concentrated distribution
        individual_entropy = (
            stats.entropy(individual_freq, base=2) if sum(individual_freq) > 0 else 0
        )
        group_entropy = stats.entropy(group_freq, base=2) if sum(group_freq) > 0 else 0

        # Calculate positive/negative gaps
        positive_gaps = sum(1 for g in gap_metrics["gaps"] if g > 0)
        negative_gaps = sum(1 for g in gap_metrics["gaps"] if g < 0)
        neutral_gaps = sum(1 for g in gap_metrics["gaps"] if g == 0)

        # Return comprehensive analysis
        return {
            "individual_score": individual_score,
            "group_score": group_score,
            "score_gap": individual_score - group_score,
            "gap_metrics": gap_metrics,
            "significance_test": sig_test,
            "concentration": {
                "individual_entropy": individual_entropy,
                "group_entropy": group_entropy,
                "entropy_difference": individual_entropy - group_entropy,
            },
            "gap_distribution": {
                "positive_gaps": positive_gaps,
                "negative_gaps": negative_gaps,
                "neutral_gaps": neutral_gaps,
                "gap_ratio": (positive_gaps - negative_gaps) / len(individual_freq)
                if len(individual_freq) > 0
                else 0,
            },
            # Classification of the distribution pattern
            "pattern": self._classify_distribution_pattern(individual_freq, group_freq),
        }

    def _classify_distribution_pattern(self, individual_freq, group_freq):
        """
        Classify the distribution pattern based on comparison with group.

        Args:
            individual_freq: List of individual frequency values
            group_freq: List of group frequency values

        Returns:
            String describing the pattern
        """
        # Calculate basic metrics
        ind_top = individual_freq[1] + individual_freq[2]  # Referência + Acima
        group_top = group_freq[1] + group_freq[2]

        ind_bottom = individual_freq[4] + individual_freq[5]  # Abaixo + Muito abaixo
        group_bottom = group_freq[4] + group_freq[5]

        # Determine pattern
        if ind_top > group_top + 10 and ind_bottom < group_bottom:
            return "superior"
        elif ind_top < group_top - 10 and ind_bottom > group_bottom:
            return "inferior"
        elif individual_freq[1] > group_freq[1] + 10:
            return "referência_destacada"
        elif individual_freq[1] < group_freq[1] - 10:
            return "déficit_referência"
        elif (
            abs(
                sum(
                    individual_freq[i] - group_freq[i]
                    for i in range(len(individual_freq))
                )
            )
            < 10
        ):
            return "alinhado"
        elif abs(individual_freq[3] - group_freq[3]) > 15:
            return "desbalanceado_centro"
        else:
            return "misto"
