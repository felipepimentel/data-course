"""
Mermaid visualization module for advanced performance data.

This module generates Mermaid syntax charts and diagrams for visualizing
performance evaluation data.
"""

import logging

logger = logging.getLogger(__name__)


class MermaidVisualizer:
    """Generates Mermaid syntax visualizations for performance data."""

    def __init__(self):
        """Initialize the Mermaid visualizer."""
        self.logger = logging.getLogger(__name__)

    def create_gap_heatmap(
        self, individual_freq, group_freq, title="Análise de Gaps por Nível"
    ):
        """
        Create a Mermaid heatmap visualization of gaps between individual and group.

        Args:
            individual_freq: List of individual frequency values
            group_freq: List of group frequency values
            title: Title for the heatmap

        Returns:
            String with Mermaid syntax for the heatmap
        """
        # Calculate gaps
        gaps = [individual_freq[i] - group_freq[i] for i in range(len(individual_freq))]

        # Category labels
        categories = [
            "N/A",
            "Referência",
            "Acima do esperado",
            "Dentro do esperado",
            "Abaixo do esperado",
            "Muito abaixo do esperado",
        ]

        # Build Mermaid syntax
        mermaid = "graph TD\n"
        mermaid += f'    subgraph "{title}"\n'

        # Create nodes for each category
        for i, (category, gap) in enumerate(zip(categories, gaps)):
            # Determine CSS class based on gap
            css_class = "gap_neutro"
            if gap > 5:
                css_class = "gap_positivo"
            elif gap < -5:
                css_class = "gap_negativo"

            if gap > 10:
                css_class = "gap_positivo_forte"
            elif gap < -10:
                css_class = "gap_negativo_critico"

            # Create node
            node_id = f"cat{i}"
            gap_sign = "+" if gap > 0 else ""
            mermaid += (
                f'        {node_id}["{category}<br>({gap_sign}{gap}%)"]:::{css_class}\n'
            )

        mermaid += "    end\n\n"

        # Add CSS classes
        mermaid += "    classDef gap_positivo fill:#d4edda,stroke:#c3e6cb\n"
        mermaid += (
            "    classDef gap_positivo_forte fill:#28a745,stroke:#28a745,color:#fff\n"
        )
        mermaid += "    classDef gap_negativo fill:#f8d7da,stroke:#f5c6cb\n"
        mermaid += (
            "    classDef gap_negativo_critico fill:#dc3545,stroke:#dc3545,color:#fff\n"
        )
        mermaid += "    classDef gap_neutro fill:#e2e3e5,stroke:#d6d8db\n"

        return mermaid

    def create_quadrant_chart(
        self,
        behaviors,
        scores,
        gaps,
        title="Análise de Posicionamento por Comportamento",
    ):
        """
        Create a Mermaid quadrant chart for behaviors based on scores and gaps.

        Args:
            behaviors: List of behavior names
            scores: List of scores (0-100) for each behavior
            gaps: List of gaps for each behavior
            title: Title for the chart

        Returns:
            String with Mermaid syntax for the quadrant chart
        """
        # Build Mermaid syntax
        mermaid = "quadrantChart\n"
        mermaid += f"    title {title}\n"
        mermaid += "    x-axis Desempenho Absoluto --> 100\n"
        mermaid += "    y-axis Gap Negativo --> Gap Positivo\n"
        mermaid += "    quadrant-1 Força Diferencial\n"
        mermaid += "    quadrant-2 Desenvolvimento Prioritário\n"
        mermaid += "    quadrant-3 Alinhado ao Grupo (Baixo)\n"
        mermaid += "    quadrant-4 Alinhado ao Grupo (Alto)\n"

        # Add behaviors
        for behavior, score, gap in zip(behaviors, scores, gaps):
            mermaid += f'    "{behavior}": [{score:.1f}, {gap:.1f}]\n'

        return mermaid

    def create_correlation_network(self, correlation_data, threshold=0.4, max_nodes=10):
        """
        Create a Mermaid network diagram showing behavior correlations.

        Args:
            correlation_data: Dictionary with correlation matrix data
            threshold: Minimum correlation strength to show (absolute value)
            max_nodes: Maximum number of nodes to include

        Returns:
            String with Mermaid syntax for the network diagram
        """
        names = correlation_data.get("names", [])
        pairs = correlation_data.get("pairs", [])

        # Limit to most correlated pairs
        pairs = [p for p in pairs if abs(p["correlation"]) >= threshold]
        pairs = sorted(pairs, key=lambda x: abs(x["correlation"]), reverse=True)

        # Identify which behaviors to include (top correlated ones)
        behaviors_to_include = set()
        for pair in pairs:
            behaviors_to_include.add(pair["behavior1"])
            behaviors_to_include.add(pair["behavior2"])
            if len(behaviors_to_include) >= max_nodes:
                break

        # Filter to only include the selected behaviors
        filtered_pairs = []
        for pair in pairs:
            if (
                pair["behavior1"] in behaviors_to_include
                and pair["behavior2"] in behaviors_to_include
            ):
                filtered_pairs.append(pair)

        # Build Mermaid syntax
        mermaid = "graph TD\n"

        # Create nodes (with shorter labels for clarity)
        nodes = {}
        for i, behavior in enumerate(behaviors_to_include):
            # Shorten behavior name if too long
            short_name = behavior[:20] + "..." if len(behavior) > 20 else behavior
            node_id = f"B{i + 1}"
            nodes[behavior] = node_id
            mermaid += f"    {node_id}[{short_name}]\n"

        # Create edges
        for pair in filtered_pairs:
            if pair["behavior1"] in nodes and pair["behavior2"] in nodes:
                node1 = nodes[pair["behavior1"]]
                node2 = nodes[pair["behavior2"]]

                # Format correlation for display
                corr = abs(pair["correlation"])
                corr_str = f"{corr:.2f}"

                # Determine line style based on correlation type
                style = "--"  # Dashed for negative
                if pair["direction"] == "positive":
                    style = "---"  # Solid for positive

                mermaid += f"    {node1} {style} |{corr_str}| {node2}\n"

        # Add CSS classes for clusters if we have cluster data
        cluster_data = {}  # This would come from cluster analysis
        if cluster_data and "clusters" in cluster_data:
            # Define cluster styles
            mermaid += "\n    classDef cluster1 fill:#d4edda,stroke:#c3e6cb;\n"
            mermaid += "    classDef cluster2 fill:#fff3cd,stroke:#ffeeba;\n"
            mermaid += "    classDef cluster3 fill:#f8d7da,stroke:#f5c6cb;\n"

            # Assign nodes to clusters
            for i, cluster in enumerate(cluster_data["clusters"]):
                cluster_nodes = [nodes[b] for b in cluster["behaviors"] if b in nodes]
                if cluster_nodes:
                    mermaid += (
                        f"    class {','.join(cluster_nodes)} cluster{(i % 3) + 1};\n"
                    )

        return mermaid

    def create_sankey_diagram(
        self,
        source_distribution,
        target_distribution,
        source_name="Atual",
        target_name="Objetivo",
    ):
        """
        Create a Mermaid Sankey-style diagram showing transition from source to target distribution.

        Args:
            source_distribution: Current frequency distribution
            target_distribution: Target frequency distribution
            source_name: Label for source distribution
            target_name: Label for target distribution

        Returns:
            String with Mermaid syntax for the flow diagram
        """
        # Category labels (simplified for clarity)
        categories = ["N/A", "Referência", "Acima", "Dentro", "Abaixo", "Muito abaixo"]

        # Build Mermaid syntax
        mermaid = "flowchart TD\n"

        # Create subgraphs for source and target
        mermaid += f'    subgraph in["{source_name}"]\n'
        for i, (cat, value) in enumerate(zip(categories, source_distribution)):
            if value > 0:
                mermaid += f'        S{i}["{cat}: {value}%"]\n'
        mermaid += "    end\n"

        mermaid += f'    subgraph out["{target_name}"]\n'
        for i, (cat, value) in enumerate(zip(categories, target_distribution)):
            if value > 0:
                mermaid += f'        T{i}["{cat}: {value}%"]\n'
        mermaid += "    end\n"

        # Create connections
        # For simplicity, we connect from each source category to target categories
        # with values proportional to the target distribution
        # This is a simple approximation and not a true Sankey diagram

        # Find the most important transitions to show (to avoid too many arrows)
        transitions = []
        for i, source_val in enumerate(source_distribution):
            if source_val <= 0:
                continue

            for j, target_val in enumerate(target_distribution):
                if target_val <= 0:
                    continue

                # Basic transition importance - product of values
                importance = source_val * target_val

                # Prioritize closing gaps
                if i == j and abs(source_val - target_val) > 5:
                    importance *= 2

                transitions.append(
                    {
                        "source": i,
                        "target": j,
                        "value": min(source_val, target_val),
                        "importance": importance,
                    }
                )

        # Sort and take top transitions
        transitions.sort(key=lambda x: x["importance"], reverse=True)
        max_transitions = min(len(transitions), 5)  # Limit to avoid clutter

        for t in transitions[:max_transitions]:
            # Calculate percentage of flow relative to source
            pct = int(round((t["value"] / source_distribution[t["source"]]) * 100))
            if pct > 0:
                mermaid += f'    S{t["source"]} --> |"{pct}%"| T{t["target"]}\n'

        # Style nodes based on performance level
        mermaid += "\n    classDef reference fill:#28a745,stroke:#28a745,color:#fff;\n"
        mermaid += "    classDef acima fill:#5cb85c,stroke:#5cb85c,color:#fff;\n"
        mermaid += "    classDef dentro fill:#6c757d,stroke:#6c757d,color:#fff;\n"
        mermaid += "    classDef abaixo fill:#dc3545,stroke:#dc3545,color:#fff;\n"

        # Apply styles
        mermaid += "    class S1,T1 reference;\n"
        mermaid += "    class S2,T2 acima;\n"
        mermaid += "    class S3,T3 dentro;\n"
        mermaid += "    class S4,T4,S5,T5 abaixo;\n"

        return mermaid

    def create_scenario_comparison(self, scenarios):
        """
        Create a Mermaid diagram comparing different development scenarios.

        Args:
            scenarios: List of scenario dictionaries with name, description, delta, difficulty

        Returns:
            String with Mermaid syntax for the comparison chart
        """
        # Build Mermaid syntax
        mermaid = "graph LR\n"
        mermaid += '    subgraph "Comparação de Cenários de Desenvolvimento"\n'

        # Create a node for each scenario
        for i, scenario in enumerate(scenarios):
            # Determine CSS class based on ROI
            css_class = "scenario_medium"
            if "roi_estimado" in scenario:
                roi = scenario["roi_estimado"]
                if roi > 1.5:
                    css_class = "scenario_high"
                elif roi < 0.5:
                    css_class = "scenario_low"

            # Format delta
            delta = scenario.get("delta", 0)
            delta_str = f"+{delta:.1f}" if delta > 0 else f"{delta:.1f}"

            # Create node
            node_id = f"s{i}"
            difficulty = scenario.get("dificuldade_estimada", "Média")
            mermaid += f'        {node_id}["{scenario["nome"]}<br>Ganho: {delta_str}<br>Dificuldade: {difficulty}"]:::{css_class}\n'

        mermaid += "    end\n\n"

        # Add CSS classes
        mermaid += "    classDef scenario_high fill:#d4edda,stroke:#c3e6cb\n"
        mermaid += "    classDef scenario_medium fill:#fff3cd,stroke:#ffeeba\n"
        mermaid += "    classDef scenario_low fill:#f8d7da,stroke:#f5c6cb\n"

        return mermaid

    def create_behavior_impact_chart(self, behaviors, impacts, gaps, difficulties):
        """
        Create a Mermaid diagram showing behavior impact vs difficulty.

        Args:
            behaviors: List of behavior names
            impacts: List of impact scores (higher is more impactful)
            gaps: List of gap values (can be positive or negative)
            difficulties: List of difficulty scores (higher is more difficult)

        Returns:
            String with Mermaid syntax for the impact chart
        """
        # Build Mermaid syntax
        mermaid = "quadrantChart\n"
        mermaid += "    title Matriz de Priorização de Comportamentos\n"
        mermaid += "    x-axis Menor Esforço --> Maior Esforço\n"
        mermaid += "    y-axis Menor Impacto --> Maior Impacto\n"
        mermaid += "    quadrant-1 Alto Impacto / Baixo Esforço (Prioridade 1)\n"
        mermaid += "    quadrant-2 Alto Impacto / Alto Esforço (Prioridade 2)\n"
        mermaid += "    quadrant-3 Baixo Impacto / Baixo Esforço (Prioridade 3)\n"
        mermaid += "    quadrant-4 Baixo Impacto / Alto Esforço (Prioridade 4)\n"

        # Add behaviors - using difficulty as x-axis and impact as y-axis
        for i, (behavior, impact, gap, difficulty) in enumerate(
            zip(behaviors, impacts, gaps, difficulties)
        ):
            # Scale values to 0-100 if needed
            scaled_difficulty = difficulty * 10 if difficulty <= 10 else difficulty
            scaled_impact = impact * 10 if impact <= 10 else impact

            # Shorten behavior name if too long
            short_name = behavior[:20] + "..." if len(behavior) > 20 else behavior

            # For gap indication, we could adjust the label
            gap_sign = "+" if gap > 0 else ""
            behavior_label = f"{short_name} ({gap_sign}{gap:.1f})"

            mermaid += f'    "{behavior_label}": [{scaled_difficulty:.1f}, {scaled_impact:.1f}]\n'

        return mermaid
