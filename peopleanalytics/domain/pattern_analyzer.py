"""
Pattern analysis module for advanced performance evaluations.

This module provides functionality for identifying patterns, correlations,
and clusters in performance evaluation data.
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)


class PatternAnalyzer:
    """Analyzes patterns and correlations in performance evaluation data."""

    def __init__(self):
        """Initialize the pattern analyzer."""
        self.logger = logging.getLogger(__name__)

    def calculate_correlation_matrix(self, behaviors_data):
        """
        Calculate correlation matrix between behaviors.

        Args:
            behaviors_data: Dictionary mapping behavior names to frequency lists

        Returns:
            Dictionary with correlation matrix and related metrics
        """
        try:
            # Extract behavior names and data
            names = list(behaviors_data.keys())
            data = list(behaviors_data.values())

            # Calculate correlation matrix
            corr_matrix = np.corrcoef(data)

            # Build result
            result = {"names": names, "matrix": corr_matrix.tolist(), "pairs": []}

            # Find strong correlations
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    corr = corr_matrix[i][j]
                    strength = "none"

                    if abs(corr) > 0.8:
                        strength = "very strong"
                    elif abs(corr) > 0.6:
                        strength = "strong"
                    elif abs(corr) > 0.4:
                        strength = "moderate"
                    elif abs(corr) > 0.2:
                        strength = "weak"

                    if abs(corr) > 0.2:  # Only include non-trivial correlations
                        result["pairs"].append(
                            {
                                "behavior1": names[i],
                                "behavior2": names[j],
                                "correlation": corr,
                                "strength": strength,
                                "direction": "positive" if corr > 0 else "negative",
                            }
                        )

            # Sort pairs by correlation strength
            result["pairs"].sort(key=lambda x: abs(x["correlation"]), reverse=True)

            return result
        except Exception as e:
            self.logger.error(f"Error calculating correlation matrix: {e}")
            return {"names": [], "matrix": [], "pairs": []}

    def analyze_clusters(self, behaviors_data, num_clusters=None):
        """
        Group behaviors into clusters based on similarity.

        Args:
            behaviors_data: Dictionary mapping behavior names to frequency lists
            num_clusters: Optional number of clusters (auto-determined if None)

        Returns:
            Dictionary with cluster analysis results
        """
        try:
            # Check if sklearn is available
            try:
                from sklearn.cluster import KMeans
                from sklearn.metrics import silhouette_score
            except ImportError:
                self.logger.warning(
                    "scikit-learn not available, using basic clustering"
                )
                # Fallback to basic clustering
                return self._basic_clustering(behaviors_data)

            # Extract behavior names and data
            names = list(behaviors_data.keys())
            data = np.array(list(behaviors_data.values()))

            if len(data) < 2:
                return {"clusters": [{"name": "all", "behaviors": names}]}

            # Determine optimal number of clusters if not specified
            if num_clusters is None:
                num_clusters = self._determine_optimal_clusters(data)

            # Perform K-means clustering
            kmeans = KMeans(n_clusters=num_clusters, random_state=42)
            labels = kmeans.fit_predict(data)

            # Organize behaviors by cluster
            clusters = [[] for _ in range(num_clusters)]
            for i, label in enumerate(labels):
                clusters[label].append(names[i])

            # Calculate silhouette score if more than one cluster
            silhouette = (
                silhouette_score(data, labels)
                if num_clusters > 1 and len(data) > num_clusters
                else 0
            )

            # Build result
            result = {
                "num_clusters": num_clusters,
                "silhouette_score": silhouette,
                "clusters": [],
            }

            for i, cluster_behaviors in enumerate(clusters):
                result["clusters"].append(
                    {
                        "id": i,
                        "behaviors": cluster_behaviors,
                        "size": len(cluster_behaviors),
                    }
                )

            # Sort clusters by size
            result["clusters"].sort(key=lambda x: x["size"], reverse=True)

            return result
        except Exception as e:
            self.logger.error(f"Error performing cluster analysis: {e}")
            return {
                "clusters": [
                    {"name": "error", "behaviors": list(behaviors_data.keys())}
                ]
            }

    def _determine_optimal_clusters(self, data):
        """
        Determine the optimal number of clusters using silhouette score.

        Args:
            data: Array of behavior frequency data

        Returns:
            Optimal number of clusters
        """
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score

        max_clusters = min(len(data) - 1, 5)  # Cap at 5 clusters or n-1

        if max_clusters <= 1:
            return 1

        # Try different numbers of clusters
        silhouette_scores = []
        for n_clusters in range(2, max_clusters + 1):
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            labels = kmeans.fit_predict(data)

            # Calculate silhouette score
            score = silhouette_score(data, labels)
            silhouette_scores.append(score)

        # Find the number of clusters with the best silhouette score
        best_num_clusters = silhouette_scores.index(max(silhouette_scores)) + 2

        return best_num_clusters

    def _basic_clustering(self, behaviors_data):
        """
        Basic clustering fallback when sklearn is not available.

        Args:
            behaviors_data: Dictionary mapping behavior names to frequency lists

        Returns:
            Dictionary with cluster analysis results
        """
        # Calculate a simple correlation-based clustering
        names = list(behaviors_data.keys())
        data = list(behaviors_data.values())

        if len(data) <= 1:
            return {"clusters": [{"name": "all", "behaviors": names}]}

        # Calculate correlation matrix
        corr_matrix = np.corrcoef(data)

        # Simple threshold-based clustering
        clusters = []
        unclustered = set(range(len(names)))

        while unclustered:
            # Start a new cluster with the first unclustered behavior
            current = unclustered.pop()
            current_cluster = [current]

            # Find related behaviors
            for i in list(unclustered):
                if abs(corr_matrix[current][i]) > 0.6:  # Correlation threshold
                    current_cluster.append(i)
                    unclustered.remove(i)

            # Add to clusters
            clusters.append([names[i] for i in current_cluster])

        # Build result
        result = {"num_clusters": len(clusters), "clusters": []}

        for i, cluster_behaviors in enumerate(clusters):
            result["clusters"].append(
                {
                    "id": i,
                    "behaviors": cluster_behaviors,
                    "size": len(cluster_behaviors),
                }
            )

        # Sort clusters by size
        result["clusters"].sort(key=lambda x: x["size"], reverse=True)

        return result

    def analyze_principal_components(self, behaviors_data, n_components=3):
        """
        Perform Principal Component Analysis (PCA) on behavior data.

        Args:
            behaviors_data: Dictionary mapping behavior names to frequency lists
            n_components: Number of principal components to extract

        Returns:
            Dictionary with PCA results
        """
        try:
            # Check if sklearn is available
            try:
                from sklearn.decomposition import PCA
            except ImportError:
                self.logger.warning("scikit-learn not available, skipping PCA")
                return {"error": "scikit-learn not available"}

            # Extract behavior names and data
            names = list(behaviors_data.keys())
            data = np.array(list(behaviors_data.values()))

            if len(data) < 2:
                return {"error": "Not enough data for PCA"}

            # Adjust number of components if necessary
            n_components = min(n_components, len(data))

            # Perform PCA
            pca = PCA(n_components=n_components)
            pca.fit(data)

            # Build result
            result = {
                "n_components": n_components,
                "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
                "total_explained_variance": sum(pca.explained_variance_ratio_),
                "components": [],
            }

            # For each component, identify dominant behaviors
            for i, component in enumerate(pca.components_):
                # Get behavior contributions (loadings)
                loadings = component

                # Get dominant behaviors (those with high absolute loadings)
                dominant_behaviors = []
                for j, loading in enumerate(loadings):
                    if abs(loading) > 0.3:  # Threshold for "dominant"
                        dominant_behaviors.append(
                            {
                                "behavior": names[j],
                                "loading": loading,
                                "absolute_loading": abs(loading),
                                "direction": "positive" if loading > 0 else "negative",
                            }
                        )

                # Sort by absolute loading
                dominant_behaviors.sort(
                    key=lambda x: x["absolute_loading"], reverse=True
                )

                # Build component info
                result["components"].append(
                    {
                        "id": i,
                        "explained_variance_ratio": pca.explained_variance_ratio_[i],
                        "dominant_behaviors": dominant_behaviors,
                        "num_dominant_behaviors": len(dominant_behaviors),
                    }
                )

            return result
        except Exception as e:
            self.logger.error(f"Error performing PCA: {e}")
            return {"error": str(e)}

    def identify_gap_patterns(self, behaviors_data, group_data):
        """
        Identify patterns in gaps across behaviors.

        Args:
            behaviors_data: Dict mapping behavior names to individual frequency lists
            group_data: Dict mapping behavior names to group frequency lists

        Returns:
            Dictionary with gap pattern analysis
        """
        # Calculate gaps for each behavior
        gaps = {}
        for behavior in behaviors_data:
            if behavior in group_data:
                individual = behaviors_data[behavior]
                group = group_data[behavior]

                # Calculate gaps
                behavior_gaps = [
                    individual[i] - group[i] for i in range(len(individual))
                ]
                gaps[behavior] = behavior_gaps

        # Identify consistent gap patterns
        consistent_patterns = {
            "positive_ref": [],  # Consistently higher in "Referência"
            "negative_ref": [],  # Consistently lower in "Referência"
            "positive_acima": [],  # Consistently higher in "Acima do esperado"
            "negative_acima": [],  # Consistently lower in "Acima do esperado"
            "positive_abaixo": [],  # Consistently higher in "Abaixo do esperado"
            "negative_abaixo": [],  # Consistently lower in "Abaixo do esperado"
        }

        # Check each behavior for patterns
        for behavior, behavior_gaps in gaps.items():
            # Check for patterns in specific categories
            if behavior_gaps[1] > 10:  # Positive gap in "Referência"
                consistent_patterns["positive_ref"].append(behavior)
            elif behavior_gaps[1] < -10:  # Negative gap in "Referência"
                consistent_patterns["negative_ref"].append(behavior)

            if behavior_gaps[2] > 10:  # Positive gap in "Acima do esperado"
                consistent_patterns["positive_acima"].append(behavior)
            elif behavior_gaps[2] < -10:  # Negative gap in "Acima do esperado"
                consistent_patterns["negative_acima"].append(behavior)

            if (
                behavior_gaps[4] > 5 or behavior_gaps[5] > 5
            ):  # Positive gap in "Abaixo" or "Muito abaixo"
                consistent_patterns["positive_abaixo"].append(behavior)
            elif (
                behavior_gaps[4] < -5 and behavior_gaps[5] < -5
            ):  # Negative gap in "Abaixo" and "Muito abaixo"
                consistent_patterns["negative_abaixo"].append(behavior)

        # Calculate average gap by category across behaviors
        category_avg_gaps = [0] * 6
        for behavior_gaps in gaps.values():
            for i, gap in enumerate(behavior_gaps):
                category_avg_gaps[i] += gap

        if gaps:
            category_avg_gaps = [gap / len(gaps) for gap in category_avg_gaps]

        # Return the results
        return {
            "consistent_patterns": consistent_patterns,
            "category_avg_gaps": category_avg_gaps,
            "num_behaviors_analyzed": len(gaps),
            "primary_pattern": self._determine_primary_gap_pattern(category_avg_gaps),
            "category_labels": [
                "N/A",
                "Referência",
                "Acima",
                "Dentro",
                "Abaixo",
                "Muito abaixo",
            ],
        }

    def _determine_primary_gap_pattern(self, category_gaps):
        """
        Determine the primary gap pattern based on category gaps.

        Args:
            category_gaps: List of average gaps by category

        Returns:
            String describing the primary pattern
        """
        # Skip N/A category
        gaps = category_gaps[1:]

        # Check for different patterns
        if gaps[0] < -10:  # Large negative gap in Referência
            return "déficit_referência"
        elif gaps[0] > 10:  # Large positive gap in Referência
            return "excesso_referência"
        elif gaps[1] < -10 and gaps[0] < -5:  # Deficit in both Referência and Acima
            return "déficit_superior"
        elif gaps[3] > 5 or gaps[4] > 5:  # Excess in lower categories
            return "excesso_inferior"
        elif abs(sum(gaps)) < 10:  # Small overall gap
            return "alinhado_global"
        elif gaps[2] > 10 and (
            gaps[0] < 0 and gaps[1] < 0
        ):  # Excess in middle, deficit at top
            return "concentração_média"
        else:
            return "misto"
