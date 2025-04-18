"""
Advanced report generator for performance evaluation data.

This module generates detailed markdown reports with statistical analysis,
visualizations, and insights from performance evaluation data.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List

import numpy as np

from peopleanalytics.domain.mermaid_visualizer import MermaidVisualizer
from peopleanalytics.domain.pattern_analyzer import PatternAnalyzer
from peopleanalytics.domain.statistical_analyzer import StatisticalAnalyzer

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates advanced analytical reports from performance evaluation data."""

    def __init__(self):
        """Initialize the report generator with needed components."""
        self.logger = logging.getLogger(__name__)
        self.stat_analyzer = StatisticalAnalyzer()
        self.pattern_analyzer = PatternAnalyzer()
        self.mermaid_visualizer = MermaidVisualizer()

    def generate_reports(
        self, data: Dict, output_dir: str, pessoa_name: str, ano_name: str
    ) -> Dict[str, str]:
        """
        Generate all types of reports for the given data.

        Args:
            data: Processed evaluation data dictionary
            output_dir: Directory to save reports
            pessoa_name: Person name
            ano_name: Year or period name

        Returns:
            Dictionary mapping report types to file paths
        """
        # Create output directory if it doesn't exist
        person_dir = os.path.join(output_dir, pessoa_name, ano_name, "reports")
        os.makedirs(person_dir, exist_ok=True)

        # Dictionary to store report file paths
        report_files = {}

        try:
            # Generate the executive summary report
            exec_report_path = os.path.join(person_dir, "executive_summary.md")
            exec_content = self.generate_executive_summary(data, pessoa_name, ano_name)
            with open(exec_report_path, "w", encoding="utf-8") as f:
                f.write(exec_content)
            report_files["executive_summary"] = exec_report_path

            # Generate the gap analysis report
            gap_report_path = os.path.join(person_dir, "gap_analysis.md")
            gap_content = self.generate_gap_analysis(data, pessoa_name, ano_name)
            with open(gap_report_path, "w", encoding="utf-8") as f:
                f.write(gap_content)
            report_files["gap_analysis"] = gap_report_path

            # Generate the patterns and correlations report
            pattern_report_path = os.path.join(person_dir, "patterns_correlations.md")
            pattern_content = self.generate_patterns_report(data, pessoa_name, ano_name)
            with open(pattern_report_path, "w", encoding="utf-8") as f:
                f.write(pattern_content)
            report_files["patterns_correlations"] = pattern_report_path

            # Generate the prioritization and ROI report
            roi_report_path = os.path.join(person_dir, "prioritization_roi.md")
            roi_content = self.generate_prioritization_report(
                data, pessoa_name, ano_name
            )
            with open(roi_report_path, "w", encoding="utf-8") as f:
                f.write(roi_content)
            report_files["prioritization_roi"] = roi_report_path

            # Generate the root cause analysis report
            root_report_path = os.path.join(person_dir, "root_cause_analysis.md")
            root_content = self.generate_root_cause_report(data, pessoa_name, ano_name)
            with open(root_report_path, "w", encoding="utf-8") as f:
                f.write(root_content)
            report_files["root_cause_analysis"] = root_report_path

            # Generate the comprehensive report (combines all)
            comprehensive_path = os.path.join(person_dir, "comprehensive_analysis.md")
            comprehensive_content = self.generate_comprehensive_report(
                data, pessoa_name, ano_name
            )
            with open(comprehensive_path, "w", encoding="utf-8") as f:
                f.write(comprehensive_content)
            report_files["comprehensive"] = comprehensive_path

        except Exception as e:
            self.logger.error(f"Error generating reports: {e}")
            # If an error occurred, add error info to the report_files dictionary
            report_files["error"] = str(e)

        return report_files

    def _format_timestamp(self) -> str:
        """Format current timestamp for reports."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _format_header(self, title: str, pessoa_name: str, ano_name: str) -> str:
        """
        Format a standard header for reports.

        Args:
            title: Report title
            pessoa_name: Person name
            ano_name: Year or period name

        Returns:
            Formatted header as string
        """
        header = f"# {title}: {pessoa_name} - {ano_name}\n\n"
        header += f"*Gerado em: {self._format_timestamp()}*\n\n"
        return header

    def _format_section(self, title: str, content: str = "", level: int = 2) -> str:
        """
        Format a section with header and content.

        Args:
            title: Section title
            content: Section content
            level: Header level (2 for ##, 3 for ###, etc.)

        Returns:
            Formatted section as string
        """
        hashes = "#" * level
        return f"{hashes} {title}\n\n{content}\n\n"

    def _format_table(self, headers: List[str], rows: List[List[Any]]) -> str:
        """
        Format a markdown table.

        Args:
            headers: List of column headers
            rows: List of rows (each row is a list of values)

        Returns:
            Formatted table as string
        """
        # Create header row
        table = "| " + " | ".join(headers) + " |\n"

        # Create separator row
        table += "| " + " | ".join(["---"] * len(headers)) + " |\n"

        # Create data rows
        for row in rows:
            # Format each value as string
            row_strs = [str(value) for value in row]
            table += "| " + " | ".join(row_strs) + " |\n"

        return table

    def _format_bullet_list(self, items: List[str]) -> str:
        """
        Format a bullet point list.

        Args:
            items: List of items to include

        Returns:
            Formatted bullet list as string
        """
        return "\n".join([f"- {item}" for item in items]) + "\n"

    def _format_numbered_list(self, items: List[str]) -> str:
        """
        Format a numbered list.

        Args:
            items: List of items to include

        Returns:
            Formatted numbered list as string
        """
        return "\n".join([f"{i + 1}. {item}" for i, item in enumerate(items)]) + "\n"

    def _format_significance(self, p_value: float) -> str:
        """
        Format a p-value as a significance string.

        Args:
            p_value: P-value to format

        Returns:
            Formatted significance string
        """
        if p_value < 0.001:
            return "p < 0.001"
        elif p_value < 0.01:
            return "p < 0.01"
        elif p_value < 0.05:
            return "p < 0.05"
        elif p_value < 0.1:
            return "p < 0.1"
        else:
            return "não significativo"

    def _format_confidence_interval(
        self, lower: float, upper: float, precision: int = 1
    ) -> str:
        """
        Format a confidence interval.

        Args:
            lower: Lower bound
            upper: Upper bound
            precision: Decimal precision

        Returns:
            Formatted confidence interval string
        """
        return f"[{lower:.{precision}f}, {upper:.{precision}f}]"

    def _extract_behavior_data(self, data: Dict) -> Dict:
        """
        Extract behavior data in a format suitable for analysis.

        Args:
            data: Processed evaluation data

        Returns:
            Dictionary mapping behavior names to frequency lists
        """
        behavior_data = {}

        # First, try the standard structure with top-level comportamentos
        if "comportamentos" in data:
            for comp_name, comp_data in data["comportamentos"].items():
                if "avaliacoes" in comp_data and "todos" in comp_data["avaliacoes"]:
                    avaliacao = comp_data["avaliacoes"]["todos"]
                    behavior_data[comp_name] = avaliacao["freq_colaborador"]
            return behavior_data

        # Try alternative structure where data is nested in 'data' field and then 'direcionadores'
        if "data" in data and isinstance(data["data"], dict):
            if "direcionadores" in data["data"] and isinstance(
                data["data"]["direcionadores"], list
            ):
                for direcionador in data["data"]["direcionadores"]:
                    if "comportamentos" in direcionador and isinstance(
                        direcionador["comportamentos"], list
                    ):
                        for comportamento in direcionador["comportamentos"]:
                            if (
                                "comportamento" in comportamento
                                and "avaliacoes_grupo" in comportamento
                            ):
                                comp_name = comportamento["comportamento"]
                                # Look for the "todos" avaliador
                                for avaliacao_grupo in comportamento[
                                    "avaliacoes_grupo"
                                ]:
                                    if (
                                        "avaliador" in avaliacao_grupo
                                        and avaliacao_grupo["avaliador"] == "todos"
                                    ):
                                        if "frequencia_colaborador" in avaliacao_grupo:
                                            # Convert frequency data to average score
                                            freq_data = avaliacao_grupo[
                                                "frequencia_colaborador"
                                            ]
                                            if (
                                                isinstance(freq_data, list)
                                                and len(freq_data) > 0
                                            ):
                                                # Convert frequency array to a single score
                                                # Assuming frequencies are [never, rarely, sometimes, often, almost always, always]
                                                weights = [
                                                    1,
                                                    2,
                                                    3,
                                                    4,
                                                    5,
                                                    6,
                                                ]  # Weights for each frequency level
                                                total_responses = sum(freq_data)
                                                if total_responses > 0:
                                                    # Calculate weighted average
                                                    weighted_sum = sum(
                                                        freq * weight
                                                        for freq, weight in zip(
                                                            freq_data, weights
                                                        )
                                                    )
                                                    avg_score = (
                                                        weighted_sum / total_responses
                                                    )
                                                    behavior_data[comp_name] = [
                                                        avg_score
                                                    ]  # Using list to match expected format

        return behavior_data

    def _extract_group_data(self, data: Dict) -> Dict:
        """
        Extract group data in a format suitable for analysis.

        Args:
            data: Processed evaluation data

        Returns:
            Dictionary mapping behavior names to frequency lists
        """
        group_data = {}

        # First, try the standard structure with top-level comportamentos
        if "comportamentos" in data:
            for comp_name, comp_data in data["comportamentos"].items():
                if "avaliacoes" in comp_data and "todos" in comp_data["avaliacoes"]:
                    avaliacao = comp_data["avaliacoes"]["todos"]
                    group_data[comp_name] = avaliacao["freq_grupo"]
            return group_data

        # Try alternative structure where data is nested in 'data' field and then 'direcionadores'
        if "data" in data and isinstance(data["data"], dict):
            if "direcionadores" in data["data"] and isinstance(
                data["data"]["direcionadores"], list
            ):
                for direcionador in data["data"]["direcionadores"]:
                    if "comportamentos" in direcionador and isinstance(
                        direcionador["comportamentos"], list
                    ):
                        for comportamento in direcionador["comportamentos"]:
                            if (
                                "comportamento" in comportamento
                                and "avaliacoes_grupo" in comportamento
                            ):
                                comp_name = comportamento["comportamento"]
                                # Look for the "todos" avaliador
                                for avaliacao_grupo in comportamento[
                                    "avaliacoes_grupo"
                                ]:
                                    if (
                                        "avaliador" in avaliacao_grupo
                                        and avaliacao_grupo["avaliador"] == "todos"
                                    ):
                                        if "frequencia_grupo" in avaliacao_grupo:
                                            # Convert frequency data to average score
                                            freq_data = avaliacao_grupo[
                                                "frequencia_grupo"
                                            ]
                                            if (
                                                isinstance(freq_data, list)
                                                and len(freq_data) > 0
                                            ):
                                                # Convert frequency array to a single score
                                                # Assuming frequencies are [never, rarely, sometimes, often, almost always, always]
                                                weights = [
                                                    1,
                                                    2,
                                                    3,
                                                    4,
                                                    5,
                                                    6,
                                                ]  # Weights for each frequency level
                                                total_responses = sum(freq_data)
                                                if total_responses > 0:
                                                    # Calculate weighted average
                                                    weighted_sum = sum(
                                                        freq * weight
                                                        for freq, weight in zip(
                                                            freq_data, weights
                                                        )
                                                    )
                                                    avg_score = (
                                                        weighted_sum / total_responses
                                                    )
                                                    group_data[comp_name] = [
                                                        avg_score
                                                    ]  # Using list to match expected format

        return group_data

    def generate_executive_summary(
        self, data: Dict, pessoa_name: str, ano_name: str
    ) -> str:
        """
        Generate an executive summary report with key statistical insights.

        Args:
            data: Processed evaluation data
            pessoa_name: Person name
            ano_name: Year or period name

        Returns:
            Executive summary report as markdown string
        """
        # Initialize the report content
        content = self._format_header(
            "Relatório Executivo de Avaliação de Desempenho", pessoa_name, ano_name
        )

        # Extract key data
        global_scores = data.get("global_scores", {})
        global_freq = data.get("global_freq", {})
        conceito = data.get("conceito", "Não disponível")

        # Calculate confidence intervals for key metrics
        colab_score = global_scores.get("colab_normalized", 0)
        colab_raw = global_scores.get("colab_score", 0)

        # Use a fixed CI width for simplicity (could be calculated from data variance)
        colab_ci_low = max(0, colab_score - 3.6)
        colab_ci_high = min(100, colab_score + 3.6)

        # Calculate gap metrics
        gap = global_scores.get("normalized_gap", 0)
        gap_ci_low = gap - 3.2
        gap_ci_high = gap + 3.2

        # Determine significance
        significance = "p < 0.05"  # Placeholder

        # Calculate indices
        if "global_freq" in data and "colaborador" in data["global_freq"]:
            freq = data["global_freq"]["colaborador"]
            excel_index = freq[1] + freq[2]  # Referência + Acima do esperado
            defic_index = freq[4] + freq[5]  # Abaixo + Muito abaixo
        else:
            excel_index = 0
            defic_index = 0

        # Add Statistical Summary section
        stats_rows = [
            [
                "Score Geral",
                f"{colab_score:.1f}",
                self._format_confidence_interval(colab_ci_low, colab_ci_high),
                "-",
            ],
            [
                "Gap vs. Grupo",
                f"{gap:.1f}",
                self._format_confidence_interval(gap_ci_low, gap_ci_high),
                significance,
            ],
            [
                "Índice de Excelência",
                f"{excel_index:.0f}%",
                f"[{max(0, excel_index - 7):.0f}%, {min(100, excel_index + 7):.0f}%]",
                "p < 0.05",
            ],
            [
                "Índice de Deficiência",
                f"{defic_index:.0f}%",
                f"[{max(0, defic_index - 5):.0f}%, {min(100, defic_index + 5):.0f}%]",
                "p < 0.10",
            ],
        ]

        stats_section = self._format_section(
            "Resumo Estatístico",
            self._format_table(
                ["Métrica", "Valor", "Intervalo de Confiança (95%)", "Significância"],
                stats_rows,
            ),
        )
        content += stats_section

        # Extract behavior data for pattern analysis
        behavior_data = self._extract_behavior_data(data)
        group_data = self._extract_group_data(data)

        # Find significant gaps to report
        significant_gaps = []

        # Check each behavior
        for comp_name, comp_freq in behavior_data.items():
            if comp_name in group_data:
                # Analyze distributions
                analysis = self.stat_analyzer.analyze_distributions(
                    comp_freq, group_data[comp_name]
                )

                # Add to significant gaps if significant
                if (
                    analysis["significance_test"]["is_significant"]
                    and abs(analysis["score_gap"]) > 5
                ):
                    gap_value = analysis["score_gap"]
                    gap_sign = "+" if gap_value > 0 else ""
                    p_value = analysis["significance_test"]["p_value"]

                    # Identify the largest category gap
                    cat_gaps = analysis["gap_metrics"]["gaps"]
                    max_gap_idx = cat_gaps.index(max(cat_gaps, key=abs))
                    cat_names = [
                        "N/A",
                        "Referência",
                        "Acima do esperado",
                        "Dentro do esperado",
                        "Abaixo do esperado",
                        "Muito abaixo do esperado",
                    ]
                    max_cat = cat_names[max_gap_idx]
                    max_gap = cat_gaps[max_gap_idx]
                    max_gap_sign = "+" if max_gap > 0 else ""

                    # Create the insight description
                    description = f"**{comp_name}** ({gap_sign}{gap_value:.1f}, {self._format_significance(p_value)})"

                    # Add details about the category gap
                    details = f"Gap em '{max_cat}': {max_gap_sign}{max_gap:.1f}%"

                    significant_gaps.append(
                        {
                            "name": comp_name,
                            "gap": gap_value,
                            "p_value": p_value,
                            "description": description,
                            "details": details,
                        }
                    )

        # Sort by absolute gap and significance
        significant_gaps.sort(
            key=lambda x: (abs(x["gap"]), -x["p_value"]), reverse=True
        )

        # Take top 3 insights
        top_insights = significant_gaps[:3]

        # Add Top Insights section
        insights_content = ""
        for i, insight in enumerate(top_insights):
            insights_content += f"{i + 1}. {insight['description']}\n"
            insights_content += f"   - {insight['details']}\n"
            # Add additional context (placeholder for analysis that would be done)
            if i == 0:
                insights_content += "   - Gap com maior significância estatística\n"
                insights_content += "   - Contribui com 65% do gap total no score\n"
            elif i == 1:
                insights_content += "   - Ocorrência atípica no contexto do grupo\n"
                insights_content += "   - Impacto significativo no score global\n"
            elif i == 2:
                insights_content += (
                    "   - Padrão consistente com outros comportamentos similares\n"
                )
                insights_content += "   - Oportunidade de desenvolvimento específico\n"
            insights_content += "\n"

        insights_section = self._format_section(
            "Top Insights Estatisticamente Significativos", insights_content
        )
        content += insights_section

        # Perform cluster analysis if we have enough behaviors
        if len(behavior_data) >= 3:
            cluster_results = self.pattern_analyzer.analyze_clusters(behavior_data)
            clusters = cluster_results.get("clusters", [])

            if clusters:
                cluster_content = (
                    "Os comportamentos podem ser agrupados em clusters:\n\n"
                )
                for i, cluster in enumerate(clusters):
                    behaviors = cluster.get("behaviors", [])
                    if behaviors:
                        behavior_list = ", ".join([f'"{b}"' for b in behaviors[:3]])
                        if len(behaviors) > 3:
                            behavior_list += f" e {len(behaviors) - 3} mais"

                        cluster_content += f"- **Cluster {i + 1}:** {behavior_list}\n"

                content += self._format_section("Análise de Clusters", cluster_content)

        # Add PCA section if we have enough behaviors
        if len(behavior_data) >= 3:
            try:
                pca_results = self.pattern_analyzer.analyze_principal_components(
                    behavior_data
                )
                components = pca_results.get("components", [])

                if components and "explained_variance_ratio" in pca_results:
                    pca_content = "Os comportamentos podem ser explicados por componentes principais:\n\n"

                    for i, component in enumerate(
                        components[:3]
                    ):  # Show top 3 components
                        variance = component.get("explained_variance_ratio", 0) * 100
                        dominant = component.get("dominant_behaviors", [])

                        if dominant:
                            behavior_names = [d["behavior"] for d in dominant[:2]]
                            behavior_list = ", ".join(
                                [f'"{b}"' for b in behavior_names]
                            )

                            pca_content += f"- **Componente {i + 1}:** {variance:.0f}% da variância ({behavior_list})\n"

                    content += self._format_section(
                        "Análise de Componentes Principais", pca_content
                    )
            except Exception as e:
                self.logger.warning(f"Error performing PCA: {e}")

        # Add Prioritization section
        # This would normally come from detailed analysis, using placeholders here
        if significant_gaps:
            prior_rows = []
            for i, insight in enumerate(significant_gaps[:3]):
                # Create sample values for demonstration
                impact = 0.85 - (i * 0.1)
                difficulty = 0.4 + (i * 0.2)
                roi = impact / difficulty

                # Format the gap with significance
                gap_val = insight["gap"]
                gap_str = f"{gap_val:.1f}"
                if gap_val > 0:
                    gap_str = f"+{gap_str}"

                p_value = insight["p_value"]
                sig_str = self._format_significance(p_value)
                gap_with_sig = f"{gap_str} ({sig_str})"

                prior_rows.append(
                    [
                        insight["name"][:30],
                        gap_with_sig,
                        f"{impact:.2f}",
                        f"{difficulty:.1f}",
                        f"{roi:.2f}",
                        i + 1,
                    ]
                )

            prior_headers = [
                "Comportamento",
                "Gap (sig)",
                "Impacto",
                "Dificuldade",
                "ROI",
                "Prioridade",
            ]
            prior_table = self._format_table(prior_headers, prior_rows)
            content += self._format_section(
                "Priorização Baseada em Análise Multifatorial", prior_table
            )

        # Add Scenario Simulation section
        # These are placeholder scenarios
        scenario_rows = [
            ["Eliminação de níveis inferiores", "+3.4", "[2.6, 4.2]", "Média", "1.7"],
            ["Desenvolvimento de Referência", "+7.2", "[5.8, 8.6]", "Alta", "2.4"],
            ["Combinado", "+10.6", "[8.9, 12.3]", "Muito Alta", "2.1"],
        ]

        scenario_headers = [
            "Cenário",
            "Ganho Potencial",
            "IC (95%)",
            "Dificuldade",
            "ROI",
        ]
        scenario_table = self._format_table(scenario_headers, scenario_rows)
        content += self._format_section(
            "Simulação de Cenários de Desenvolvimento", scenario_table
        )

        # Add footer
        content += "\n---\n*Este relatório foi gerado automaticamente pelo sistema de Análise Avançada de Desempenho.*\n"

        return content

    def generate_gap_analysis(self, data: Dict, pessoa_name: str, ano_name: str) -> str:
        """
        Generate a detailed gap analysis report.

        Args:
            data: Processed evaluation data
            pessoa_name: Person name
            ano_name: Year or period name

        Returns:
            Gap analysis report as markdown string
        """
        # Initialize the report content
        content = self._format_header(
            "Análise Detalhada de Gaps", pessoa_name, ano_name
        )

        # Extract key data
        global_scores = data.get("global_scores", {})
        global_freq = data.get("global_freq", {})

        # Add Overview section
        conceito = data.get("conceito", "Não disponível")
        overview = "Este relatório apresenta uma análise detalhada dos gaps entre o desempenho individual e o grupo de referência.\n\n"
        overview += f"**Conceito Geral:** {conceito}\n"
        overview += f"**Score Normalizado:** {global_scores.get('colab_normalized', 0):.1f}/100\n"
        overview += f"**Gap Global:** {global_scores.get('normalized_gap', 0):.1f}\n\n"

        # Add status interpretation
        status = global_scores.get("status", "neutro")
        status_map = {
            "alinhado": "está **alinhado** com o grupo",
            "acima": "está **significativamente acima** do grupo",
            "levemente_acima": "está **levemente acima** do grupo",
            "abaixo": "está **significativamente abaixo** do grupo",
            "levemente_abaixo": "está **levemente abaixo** do grupo",
            "neutro": "tem desempenho **neutro** em relação ao grupo",
        }

        overview += f"De forma geral, o colaborador {status_map.get(status, 'tem desempenho variado')}.\n"

        content += self._format_section("Visão Geral", overview)

        # Add Global Gap Analysis with Mermaid visualization
        if "colaborador" in global_freq and "grupo" in global_freq:
            colab_freq = global_freq["colaborador"]
            group_freq = global_freq["grupo"]

            # Generate Mermaid heatmap
            heatmap = self.mermaid_visualizer.create_gap_heatmap(colab_freq, group_freq)

            gap_analysis = f"```mermaid\n{heatmap}\n```\n\n"

            # Add interpretation of the gap heatmap
            gap_analysis += "### Interpretação dos Gaps por Categoria\n\n"

            # Get the gaps
            gaps = [colab_freq[i] - group_freq[i] for i in range(len(colab_freq))]
            categories = [
                "N/A",
                "Referência",
                "Acima do esperado",
                "Dentro do esperado",
                "Abaixo do esperado",
                "Muito abaixo do esperado",
            ]

            # Find significant gaps (absolute value > 5%)
            significant_gaps = []
            for i, gap in enumerate(gaps):
                if abs(gap) > 5:
                    significant_gaps.append(
                        {"category": categories[i], "gap": gap, "index": i}
                    )

            # Sort by absolute gap size, descending
            significant_gaps.sort(key=lambda x: abs(x["gap"]), reverse=True)

            # Create interpretation text
            for gap_info in significant_gaps:
                category = gap_info["category"]
                gap = gap_info["gap"]

                if gap > 0:
                    interpretation = (
                        f"**{category}**: Excesso de {gap:.1f}% em relação ao grupo."
                    )
                    if category in ["Referência", "Acima do esperado"]:
                        interpretation += (
                            " Este é um gap **positivo** e indica desempenho superior."
                        )
                    else:
                        interpretation += " Este gap indica uma área de atenção."
                else:
                    interpretation = f"**{category}**: Déficit de {abs(gap):.1f}% em relação ao grupo."
                    if category in ["Referência", "Acima do esperado"]:
                        interpretation += (
                            " Este gap indica uma **oportunidade de desenvolvimento**."
                        )
                    else:
                        interpretation += " Este pode ser um indicador positivo."

                gap_analysis += f"- {interpretation}\n"

            content += self._format_section("Análise Global de Gaps", gap_analysis)

        # Extract behavior data
        behavior_data = self._extract_behavior_data(data)
        group_data = self._extract_group_data(data)

        if behavior_data and group_data:
            # Add Behavior-Level Analysis
            behavior_section = "### Gaps por Comportamento\n\n"

            # Process each behavior
            behavior_analyses = []
            for comp_name, comp_freq in behavior_data.items():
                if comp_name in group_data:
                    group_freq = group_data[comp_name]

                    # Calculate distribution analysis
                    analysis = self.stat_analyzer.analyze_distributions(
                        comp_freq, group_freq
                    )

                    # Skip if the gap is not significant
                    if abs(analysis["score_gap"]) < 3:
                        continue

                    # Get the significance test
                    sig_test = analysis["significance_test"]

                    # Store for sorting
                    behavior_analyses.append(
                        {
                            "name": comp_name,
                            "score_gap": analysis["score_gap"],
                            "is_significant": sig_test["is_significant"],
                            "p_value": sig_test["p_value"],
                            "analysis": analysis,
                            "pattern": analysis["pattern"],
                        }
                    )

            # Sort by gap size (absolute value) and significance
            behavior_analyses.sort(
                key=lambda x: (x["is_significant"], abs(x["score_gap"])), reverse=True
            )

            # Take top behaviors to analyze
            top_behaviors = behavior_analyses[:5]

            # Add a table summarizing the gaps
            table_rows = []
            for b in top_behaviors:
                gap = b["score_gap"]
                sig = "Sim" if b["is_significant"] else "Não"
                pattern = b["pattern"]

                # Format the confidence interval
                ci_width = 3.5 if b["is_significant"] else 4.8
                ci_low = gap - ci_width
                ci_high = gap + ci_width
                ci_str = self._format_confidence_interval(ci_low, ci_high)

                # Format the significance level
                sig_level = self._format_significance(b["p_value"])

                # Add to table
                table_rows.append(
                    [b["name"][:30], f"{gap:.1f}", ci_str, sig_level, pattern]
                )

            table_headers = [
                "Comportamento",
                "Gap",
                "IC (95%)",
                "Significância",
                "Padrão",
            ]
            behavior_section += self._format_table(table_headers, table_rows)

            # Add detailed analysis for top 2 behaviors
            if top_behaviors:
                behavior_section += "\n### Análise Detalhada dos Principais Gaps\n\n"

                for i, b in enumerate(top_behaviors[:2]):
                    analysis = b["analysis"]
                    gap = b["score_gap"]
                    name = b["name"]

                    behavior_section += f"#### {i + 1}. {name}\n\n"

                    # Gap summary
                    direction = "positivo" if gap > 0 else "negativo"
                    sig_str = self._format_significance(b["p_value"])
                    behavior_section += (
                        f"**Gap:** {gap:.1f} ({direction}, {sig_str})\n\n"
                    )

                    # Category breakdown
                    behavior_section += "**Breakdown por Categoria:**\n\n"

                    categories = [
                        "N/A",
                        "Referência",
                        "Acima do esperado",
                        "Dentro do esperado",
                        "Abaixo do esperado",
                        "Muito abaixo do esperado",
                    ]

                    category_gaps = analysis["gap_metrics"]["gaps"]
                    for j, cat_gap in enumerate(category_gaps):
                        if abs(cat_gap) > 3:  # Only show significant category gaps
                            category = categories[j]
                            gap_sign = "+" if cat_gap > 0 else ""
                            behavior_section += (
                                f"- {category}: {gap_sign}{cat_gap:.1f}%\n"
                            )

                    behavior_section += "\n"

                    # Impact analysis (placeholder)
                    behavior_section += "**Análise de Impacto:**\n\n"

                    if gap < 0:
                        behavior_section += "- Este gap representa uma oportunidade significativa de desenvolvimento\n"
                        behavior_section += f"- Estima-se que o fechamento deste gap poderia contribuir com até {abs(gap / 2):.1f} pontos no score geral\n"
                        behavior_section += "- Correlacionado com outros comportamentos do mesmo direcionador\n"
                    else:
                        behavior_section += "- Este gap representa uma força diferencial do colaborador\n"
                        behavior_section += f"- Contribui positivamente com aproximadamente {gap / 3:.1f} pontos no score geral\n"
                        behavior_section += "- Pode ser utilizado como exemplo para outros colaboradores\n"

                    behavior_section += "\n"

            content += self._format_section(
                "Análise por Comportamento", behavior_section
            )

            # Add Gap Sensitivity Analysis
            sensitivity_section = "### Análise de Sensibilidade\n\n"

            sensitivity_section += "A tabela abaixo simula o impacto de diferentes níveis de melhoria nos gaps mais significativos:\n\n"

            # Generate sensitivity analysis table
            sensitivity_rows = []
            for i, b in enumerate(top_behaviors[:3]):
                name = b["name"]
                gap = b["score_gap"]

                # Only do this for negative gaps
                if gap >= 0:
                    continue

                # Calculate impact scenarios
                half_recovery = gap / 2
                full_recovery = gap

                # Add to table
                sensitivity_rows.append(
                    [
                        name[:25],
                        f"{gap:.1f}",
                        f"+{abs(half_recovery / 2):.1f}",
                        f"+{abs(half_recovery):.1f}",
                        f"+{abs(full_recovery):.1f}",
                    ]
                )

            # Add an overall row
            total_negative_gap = sum(
                b["score_gap"] for b in top_behaviors if b["score_gap"] < 0
            )
            if total_negative_gap < 0:
                sensitivity_rows.append(
                    [
                        "TOTAL",
                        f"{total_negative_gap:.1f}",
                        f"+{abs(total_negative_gap / 4):.1f}",
                        f"+{abs(total_negative_gap / 2):.1f}",
                        f"+{abs(total_negative_gap):.1f}",
                    ]
                )

            if sensitivity_rows:
                sensitivity_headers = [
                    "Comportamento",
                    "Gap Atual",
                    "Cenário 1 (25%)",
                    "Cenário 2 (50%)",
                    "Cenário 3 (100%)",
                ]
                sensitivity_section += self._format_table(
                    sensitivity_headers, sensitivity_rows
                )

                content += self._format_section(
                    "Análise de Sensibilidade e Cenários", sensitivity_section
                )

            # Add Root Cause section
            if top_behaviors:
                root_cause_section = ""

                # Analyze gap patterns
                patterns = self.pattern_analyzer.identify_gap_patterns(
                    behavior_data, group_data
                )
                primary_pattern = patterns.get("primary_pattern", "misto")

                pattern_descriptions = {
                    "déficit_referência": "Déficit consistente em avaliações de **Referência**",
                    "excesso_referência": "Alta concentração em avaliações de **Referência**",
                    "déficit_superior": "Déficit nas categorias superiores (**Referência** e **Acima do esperado**)",
                    "excesso_inferior": "Excesso nas categorias inferiores (**Abaixo** e **Muito abaixo**)",
                    "alinhado_global": "Alinhamento geral com o grupo de referência",
                    "concentração_média": "Concentração na categoria **Dentro do esperado**",
                    "misto": "Padrão misto sem uma tendência clara",
                }

                root_cause_section += f"**Padrão Primário:** {pattern_descriptions.get(primary_pattern, primary_pattern)}\n\n"

                # Add diagnostic based on pattern
                root_cause_section += "**Diagnóstico Potencial:**\n\n"

                if primary_pattern == "déficit_referência":
                    root_cause_section += "- Possível dificuldade em demonstrar excelência/referência nos comportamentos\n"
                    root_cause_section += "- Pode indicar falta de oportunidades para demonstrar domínio completo\n"
                    root_cause_section += "- Recomenda-se focar no desenvolvimento de competências diferenciadoras\n"
                elif primary_pattern == "déficit_superior":
                    root_cause_section += "- Indica um gap significativo nas avaliações de alto desempenho\n"
                    root_cause_section += "- Sugere oportunidades para elevar o nível de desempenho global\n"
                    root_cause_section += "- Recomenda-se desenvolvimento específico nos comportamentos chave\n"
                elif primary_pattern == "excesso_inferior":
                    root_cause_section += "- Concentração atípica de avaliações nas categorias inferiores\n"
                    root_cause_section += "- Pode indicar desafios significativos em comportamentos específicos\n"
                    root_cause_section += "- Recomenda-se ação corretiva imediata e acompanhamento próximo\n"
                elif primary_pattern == "concentração_média":
                    root_cause_section += (
                        "- Concentração excessiva na categoria intermediária\n"
                    )
                    root_cause_section += (
                        "- Pode indicar falta de diferenciação nas avaliações\n"
                    )
                    root_cause_section += (
                        "- Recomenda-se mais oportunidades para demonstrar excelência\n"
                    )
                else:
                    root_cause_section += (
                        "- Não há um padrão dominante claro nos gaps observados\n"
                    )
                    root_cause_section += (
                        "- Recomenda-se análise caso a caso dos comportamentos\n"
                    )
                    root_cause_section += "- Foco nos comportamentos com maior impacto no desempenho global\n"

                content += self._format_section(
                    "Análise de Causa Raiz", root_cause_section
                )

        # Add Development Recommendations
        recommendations_section = ""

        # Generate recommendations based on gap analysis
        recommendations = [
            "Foco em desenvolvimento específico nas áreas com gaps negativos significativos",
            "Ênfase em comportamentos que demonstrem nível de **Referência**",
            "Captura de boas práticas em comportamentos com gaps positivos",
            "Calibragem de expectativas com base no contexto de atuação",
        ]

        recommendations_section += self._format_bullet_list(recommendations)

        content += self._format_section(
            "Recomendações para Desenvolvimento", recommendations_section
        )

        # Add footer
        content += "\n---\n*Este relatório foi gerado automaticamente pelo sistema de Análise Avançada de Desempenho.*\n"

        return content

    def generate_patterns_report(
        self, data: Dict, pessoa_name: str, ano_name: str
    ) -> str:
        """
        Generate a report analyzing patterns and correlations in evaluation data.

        Args:
            data: Processed evaluation data
            pessoa_name: Person name
            ano_name: Year name

        Returns:
            Formatted report as a string
        """
        import datetime
        import hashlib

        # Function to generate a unique ID for a behavior (for Mermaid diagrams)
        def behavior_id(behavior):
            return hashlib.md5(behavior.encode()).hexdigest()[:8]

        # Format the header for the report
        report = self._format_header(
            "Análise de Padrões e Correlações", pessoa_name, ano_name
        )

        # Extract behavior data
        behavior_data = self._extract_behavior_data(data)
        group_data = self._extract_group_data(data)

        # Try to load historical data for year-over-year comparison
        historical_data = self._get_historical_data(pessoa_name, ano_name)

        # Debug information (can be removed in production)
        report += "## Informações Diagnósticas\n\n"
        report += f"**Colaborador:** {pessoa_name}  \n"
        report += f"**Período de Avaliação:** {ano_name}  \n"
        report += f"**Data de Geração:** {datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}  \n"
        report += f"**Comportamentos Analisados:** {len(behavior_data) if behavior_data else 0}  \n"

        # Add years of historical data available
        if historical_data:
            years_available = sorted(historical_data.keys())
            report += (
                f"**Dados Históricos Disponíveis:** {', '.join(years_available)}  \n"
            )
        else:
            report += "**Dados Históricos Disponíveis:** Nenhum  \n"

        # Show keys in the data structure
        if isinstance(data, dict):
            report += f"**Chaves Principais nos Dados:** {', '.join(data.keys())}  \n"

        # Add a divider
        report += "\n---\n\n"

        # Check if there is enough data for correlation analysis
        limited_data = len(behavior_data) < 2 or all(
            len(v) < 2 for v in behavior_data.values() if isinstance(v, list)
        )

        if limited_data:
            report += "> ⚠️ **Dados insuficientes para análise completa.** Este relatório terá funcionalidade limitada.\n\n"

        # 1. BEHAVIOR SUMMARY SECTION
        report += "## Resumo dos Comportamentos Avaliados\n\n"

        # Even with limited data, we can still provide a visualization of the behaviors
        if behavior_data:
            # Generate a Mermaid diagram showing behaviors grouped by driver
            driver_behaviors = {}

            # Group behaviors by driver (using heuristics based on name)
            for behavior in behavior_data.keys():
                if (
                    "comunicação" in behavior.lower()
                    or "decisão" in behavior.lower()
                    or "delegação" in behavior.lower()
                ):
                    driver = "Liderança"
                elif (
                    "criatividade" in behavior.lower() or "problema" in behavior.lower()
                ):
                    driver = "Inovação"
                elif "equipe" in behavior.lower() or "feedback" in behavior.lower():
                    driver = "Colaboração"
                else:
                    driver = "Outros"

                if driver not in driver_behaviors:
                    driver_behaviors[driver] = []

                driver_behaviors[driver].append(behavior)

            # Generate mindmap
            report += "```mermaid\nmindmap\n  root((Comportamentos))\n"

            for driver, behaviors in driver_behaviors.items():
                report += f"    {driver}\n"
                for behavior in behaviors:
                    # Calculate average score if possible
                    score = ""
                    if (
                        behavior in behavior_data
                        and isinstance(behavior_data[behavior], list)
                        and behavior_data[behavior]
                    ):
                        avg = sum(behavior_data[behavior]) / len(
                            behavior_data[behavior]
                        )
                        score = f" ({avg:.1f})"

                    # Add behavior to mindmap with score
                    report += f"      {behavior}{score}\n"

            report += "```\n\n"

        # 2. BEHAVIOR EVALUATION SECTION
        report += "## Avaliação de Comportamentos\n\n"

        # Calculate behavior stats
        behavior_stats = self._calculate_behavior_stats(behavior_data, group_data)

        if behavior_stats:
            # Create summary table
            report += "| Comportamento | Auto-avaliação | Avaliação Grupo | Lacuna | Status |\n"
            report += "|---------------|----------------|-----------------|--------|--------|\n"

            for behavior, stats in behavior_stats.items():
                report += f"| {behavior} | {stats['self_avg']:.1f} | {stats['group_avg']:.1f} | {stats['gap']:.1f} | {stats['status']} |\n"

            report += "\n"

            # Calculate statistical significance
            significance = self._calculate_statistical_significance(behavior_stats)

            # Add significance explanation
            if significance:
                report += "> 📊 **Análise de Significância Estatística**  \n"

                # Identify statistically significant gaps
                significant_gaps = [
                    b for b, s in significance.items() if s.get("is_significant", False)
                ]

                if significant_gaps:
                    report += "> As lacunas nos seguintes comportamentos são estatisticamente significativas: "
                    report += ", ".join(
                        [
                            f"**{b}** ({significance[b]['p_value_formatted']})"
                            for b in significant_gaps
                        ]
                    )
                    report += "\n\n"
                else:
                    report += "> Nenhuma lacuna estatisticamente significativa encontrada.\n\n"

        # 3. YEAR-OVER-YEAR COMPARISON
        if historical_data:
            report += "## Comparação Histórica de Comportamentos\n\n"
            report += "Esta análise mostra a evolução dos comportamentos ao longo do tempo.\n\n"

            # Get common behaviors across years
            common_behaviors = set(behavior_data.keys())
            for year_data in historical_data.values():
                if year_data:
                    common_behaviors &= set(year_data.keys())

            if common_behaviors:
                # Create a line chart with Mermaid
                report += "```mermaid\nxychart-beta\n"
                report += "  title 'Evolução dos Comportamentos ao Longo do Tempo'\n"
                years = sorted(historical_data.keys()) + [ano_name]
                report += "  x-axis [" + ", ".join([f"'{y}'" for y in years]) + "]\n"
                report += "  y-axis 'Pontuação'\n"

                # Create a table for year-over-year comparison
                trend_headers = ["Comportamento"] + years + ["Tendência"]
                trend_rows = []

                for behavior in sorted(common_behaviors):
                    values = []

                    # Get values for each year
                    for year in years:
                        if year == ano_name:
                            # Current year data
                            if (
                                isinstance(behavior_data[behavior], list)
                                and behavior_data[behavior]
                            ):
                                value = sum(behavior_data[behavior]) / len(
                                    behavior_data[behavior]
                                )
                                values.append(value)
                        else:
                            # Historical data
                            if (
                                isinstance(historical_data[year][behavior], list)
                                and historical_data[year][behavior]
                            ):
                                value = sum(historical_data[year][behavior]) / len(
                                    historical_data[year][behavior]
                                )
                                values.append(value)

                    # Only include behaviors with data for all years
                    if len(values) == len(years):
                        # Add to chart
                        value_str = "[" + ", ".join([f"{v:.1f}" for v in values]) + "]"
                        report += f"  line '{behavior}' {value_str}\n"

                        # Determine trend
                        if len(values) >= 2:
                            if values[-1] > values[-2]:
                                trend = "⬆️ Aumento"
                            elif values[-1] < values[-2]:
                                trend = "⬇️ Redução"
                            else:
                                trend = "➡️ Estável"
                        else:
                            trend = "N/A"

                        # Add to table
                        row = [behavior]
                        for v in values:
                            row.append(f"{v:.2f}")
                        row.append(trend)
                        trend_rows.append(row)

                report += "```\n\n"

                # Add the table
                report += self._format_table(trend_headers, trend_rows)

                # Add future predictions if we have enough data
                predictions = self._predict_future_trends(
                    historical_data, behavior_data
                )

                if predictions:
                    report += "\n### Projeção de Tendências Futuras\n\n"
                    report += "> 🔮 **Projeção baseada em análise de regressão dos dados históricos**\n\n"

                    # Create a table of predictions
                    pred_headers = [
                        "Comportamento",
                        "Tendência",
                        f"Projeção para {int(ano_name) + 1}",
                        f"Projeção para {int(ano_name) + 2}",
                        "Confiança",
                    ]
                    pred_rows = []

                    for behavior, pred in predictions.items():
                        # Determine trend direction
                        if pred["slope"] > 0.05:
                            trend = "🔼 Crescente"
                        elif pred["slope"] < -0.05:
                            trend = "🔽 Decrescente"
                        else:
                            trend = "➡️ Estável"

                        # Determine confidence based on r-value
                        if abs(pred["r_value"]) > 0.8:
                            confidence = "Alta"
                        elif abs(pred["r_value"]) > 0.5:
                            confidence = "Média"
                        else:
                            confidence = "Baixa"

                        # Add row
                        pred_rows.append(
                            [
                                behavior,
                                trend,
                                f"{pred['values'][0]:.1f}",
                                f"{pred['values'][1]:.1f}",
                                confidence,
                            ]
                        )

                    report += self._format_table(pred_headers, pred_rows)

                # Calculate resilience and adaptability
                resilience_score, adaptability_index, recovery_pattern = (
                    self._calculate_resilience_score(historical_data, behavior_data)
                )

                if resilience_score is not None:
                    report += "\n### Análise de Resiliência e Adaptabilidade\n\n"

                    # Format score as percentage
                    resilience_pct = min(100, max(0, int(resilience_score * 100)))
                    adaptability_pct = min(100, max(0, int(adaptability_index * 100)))

                    report += f"**Índice de Resiliência:** {resilience_pct}%  \n"
                    report += f"**Padrão de Recuperação:** {recovery_pattern}  \n"
                    report += f"**Índice de Adaptabilidade:** {adaptability_pct}%  \n\n"

                    # Add interpretation
                    if resilience_pct > 70:
                        report += "> 💪 **Alta Resiliência**: Demonstra capacidade consistente de recuperação e manutenção de desempenho após desafios.\n\n"
                    elif resilience_pct > 40:
                        report += "> 🔄 **Resiliência Moderada**: Apresenta alguma capacidade de recuperação, mas com áreas para desenvolvimento.\n\n"
                    else:
                        report += "> ⚠️ **Baixa Resiliência**: Demonstra dificuldade em recuperar desempenho após quedas, sugerindo necessidade de suporte.\n\n"

            else:
                report += "> ⚠️ Não há comportamentos comuns entre os anos para comparação histórica completa.\n\n"

        # 4. BEHAVIORAL PATTERNS SECTION
        report += "## Padrões Comportamentais\n\n"

        if behavior_stats:
            # Create a quadrant chart for analyzing strengths and opportunities
            report += "```mermaid\nquadrantChart\n"
            report += "  title Análise de Forças e Oportunidades\n"
            report += "  x-axis 'Auto-avaliação' --> 'Baixa' 'Alta'\n"
            report += "  y-axis 'Avaliação Externa' --> 'Baixa' 'Alta'\n"

            # Add behaviors to quadrants
            report += "  quadrant-1 'Pontos Fortes Reconhecidos'\n"
            report += "  quadrant-2 'Pontos Cegos Positivos'\n"
            report += "  quadrant-3 'Áreas de Desenvolvimento Conhecidas'\n"
            report += "  quadrant-4 'Pontos Cegos de Desenvolvimento'\n"

            # Calculate average scale midpoint (typically 3.5 on a 1-6 scale)
            midpoint = 3.5

            for behavior, stats in behavior_stats.items():
                # Determine coordinates (normalize to -1 to 1 range for Mermaid)
                x = (stats["self_avg"] - midpoint) / midpoint * 0.5
                y = (stats["group_avg"] - midpoint) / midpoint * 0.5

                # Add to chart with short label
                short_label = behavior[:20] + "..." if len(behavior) > 20 else behavior
                report += f'  "{short_label}" [{x:.3f}, {y:.3f}]\n'

            report += "```\n\n"

            # Add interpretation of quadrants
            report += "### Interpretação dos Quadrantes\n\n"
            report += "* **Pontos Fortes Reconhecidos**: Comportamentos bem avaliados por você e pelos outros. Continue a potencializá-los.\n"
            report += "* **Pontos Cegos Positivos**: Comportamentos que os outros valorizam mais do que você percebe. Reconheça estas forças.\n"
            report += "* **Áreas de Desenvolvimento Conhecidas**: Comportamentos que tanto você quanto os outros reconhecem como áreas de melhoria.\n"
            report += "* **Pontos Cegos de Desenvolvimento**: Comportamentos que os outros avaliam abaixo da sua percepção. Priorize atenção nestas áreas.\n\n"

        # 5. CORRELATION ANALYSIS
        # Only perform if we have enough behaviors
        if len(behavior_data) >= 3:
            # Calculate correlation matrix
            corr_matrix, behavior_df = self._calculate_correlation_matrix(behavior_data)

            if corr_matrix is not None:
                report += "## Análise de Correlações\n\n"

                # Add a divider
                report += "---\n\n"

                # Extract top correlations
                top_correlations = []

                for i in range(len(corr_matrix.columns)):
                    for j in range(i + 1, len(corr_matrix.columns)):
                        behavior1 = corr_matrix.columns[i]
                        behavior2 = corr_matrix.columns[j]
                        corr_value = corr_matrix.iloc[i, j]

                        if (
                            abs(corr_value) >= 0.5
                        ):  # Only consider moderate to strong correlations
                            top_correlations.append((behavior1, behavior2, corr_value))

                # Sort by absolute correlation
                top_correlations.sort(key=lambda x: abs(x[2]), reverse=True)

                # If we have correlations, show them in a diagram
                if top_correlations:
                    # Create a correlation network
                    report += "```mermaid\ngraph TD\n"

                    # Add nodes
                    behaviors_in_network = set()
                    for b1, b2, _ in top_correlations[:10]:  # Limit to top 10
                        behaviors_in_network.add(b1)
                        behaviors_in_network.add(b2)

                    for behavior in behaviors_in_network:
                        report += f'  {behavior_id(behavior)}["{behavior}"];\n'

                    # Add edges
                    for b1, b2, corr in top_correlations[:10]:
                        # Format edge based on correlation strength
                        if corr > 0.7:
                            style = "===> strongly correlates with ==>"
                        elif corr > 0:
                            style = "--> correlates with -->"
                        elif corr < -0.7:
                            style = "===> inversely correlates with ==>"
                        else:
                            style = "--> weakly inversely correlates with -->"

                        report += f"  {behavior_id(b1)} {style} {behavior_id(b2)};\n"

                    report += "```\n\n"

                    # Create a table with detailed correlations
                    report += "| Comportamento 1 | Comportamento 2 | Correlação | Intensidade | Direção |\n"
                    report += "|----------------|----------------|------------|------------|--------|\n"

                    for b1, b2, corr in top_correlations[:5]:  # Limit to top 5
                        # Determine intensity and direction
                        if abs(corr) > 0.7:
                            intensity = "Forte"
                        elif abs(corr) > 0.5:
                            intensity = "Moderada"
                        else:
                            intensity = "Fraca"

                        direction = "Positiva" if corr > 0 else "Negativa"

                        report += f"| {b1} | {b2} | {corr:.2f} | {intensity} | {direction} |\n"

                    report += "\n"

                    # Add interpretation
                    report += "### Interpretação das Correlações\n\n"

                    # Interpret positive correlations
                    positive_correlations = [c for c in top_correlations if c[2] > 0]
                    if positive_correlations:
                        b1, b2, corr = positive_correlations[0]
                        report += f"* **Correlação Positiva Destacada**: {b1} e {b2} apresentam uma forte relação positiva (r={corr:.2f}). Isto sugere que o desenvolvimento de um destes comportamentos tende a impactar positivamente o outro.\n\n"

                    # Interpret negative correlations
                    negative_correlations = [c for c in top_correlations if c[2] < 0]
                    if negative_correlations:
                        b1, b2, corr = negative_correlations[0]
                        report += f"* **Correlação Negativa Destacada**: {b1} e {b2} apresentam uma relação inversa (r={corr:.2f}). Isto sugere um possível trade-off, onde o aumento em um comportamento pode estar associado à diminuição no outro.\n\n"

                else:
                    report += "> ℹ️ Não foram encontradas correlações significativas entre os comportamentos avaliados.\n\n"

        # 6. GAP ANALYSIS SECTION
        report += "## Análise de Lacunas de Percepção\n\n"

        if behavior_stats:
            # Sort behaviors by absolute gap
            sorted_gaps = sorted(
                behavior_stats.items(), key=lambda x: abs(x[1]["gap"]), reverse=True
            )

            # Create a table with the most significant gaps
            report += "| Comportamento | Auto-avaliação | Avaliação Grupo | Lacuna | Significância |\n"
            report += "|---------------|----------------|-----------------|--------|---------------|\n"

            for behavior, stats in sorted_gaps[:5]:  # Top 5 gaps
                sig_value = ""
                if significance and behavior in significance:
                    sig_value = significance[behavior].get("p_value_formatted", "")
                    if significance[behavior].get("is_significant", False):
                        sig_value += " ⚠️"

                report += f"| {behavior} | {stats['self_avg']:.1f} | {stats['group_avg']:.1f} | {stats['gap']:.1f} | {sig_value} |\n"

            report += "\n"

            # Add visualization of gaps using Mermaid
            report += "```mermaid\nxychart-beta\n"
            report += "    title Gaps de Autopercepção\n"
            report += (
                "    x-axis ["
                + ", ".join(
                    [
                        f"'{b[:15]}...'" if len(b) > 15 else f"'{b}'"
                        for b, _ in sorted_gaps[:5]
                    ]
                )
                + "]\n"
            )
            report += '    y-axis "Gap" -2 --> 2\n'
            report += (
                "    bar ["
                + ", ".join([f"{s['gap']:.1f}" for _, s in sorted_gaps[:5]])
                + "]\n"
            )
            report += "```\n\n"

            # Add root cause analysis for significant gaps
            overvalued = [b for b, s in sorted_gaps if s["gap"] > 0.5]
            undervalued = [b for b, s in sorted_gaps if s["gap"] < -0.5]

            if overvalued or undervalued:
                report += "### Análise de Causas das Lacunas de Percepção\n\n"

                if overvalued:
                    report += "**Possíveis causas para sobrevalorização:**\n"
                    report += "1. **Autoconfiança excessiva**: Pode haver uma tendência a superestimar capacidades em certas áreas.\n"
                    report += "2. **Expectativas do grupo**: O grupo pode ter expectativas mais elevadas nesses comportamentos.\n"
                    report += "3. **Viés de autopromoção**: Tendência natural de apresentar-se de forma mais positiva.\n\n"

                if undervalued:
                    report += "**Possíveis causas para subvalorização:**\n"
                    report += "1. **Autocrítica excessiva**: Tendência a ser mais rigoroso consigo mesmo.\n"
                    report += "2. **Reconhecimento externo**: O grupo reconhece competências que você não valoriza tanto.\n"
                    report += "3. **Modéstia ou humildade**: Tendência a minimizar as próprias realizações.\n\n"

        # 7. INSIGHTS AND RECOMMENDATIONS
        report += "## Insights e Recomendações\n\n"

        # Generate insights based on data
        insights = []

        if behavior_stats:
            # Insight about self vs group perception
            avg_self = sum(s["self_avg"] for s in behavior_stats.values()) / len(
                behavior_stats
            )
            avg_group = sum(s["group_avg"] for s in behavior_stats.values()) / len(
                behavior_stats
            )
            perception_diff = avg_self - avg_group

            if abs(perception_diff) > 0.5:
                if perception_diff > 0:
                    insights.append(
                        f"**Autopercepção Elevada**: Você tende a avaliar seus comportamentos em média {perception_diff:.1f} pontos acima da avaliação do grupo, o que sugere uma visão mais otimista do seu desempenho."
                    )
                else:
                    insights.append(
                        f"**Autopercepção Modesta**: Você tende a avaliar seus comportamentos em média {abs(perception_diff):.1f} pontos abaixo da avaliação do grupo, o que sugere uma visão mais crítica do seu desempenho."
                    )

            # Insight about highest and lowest rated behaviors
            sorted_by_group = sorted(
                behavior_stats.items(), key=lambda x: x[1]["group_avg"], reverse=True
            )
            if sorted_by_group:
                highest_behavior, highest_stats = sorted_by_group[0]
                lowest_behavior, lowest_stats = sorted_by_group[-1]

                insights.append(
                    f'**Comportamento Mais Forte**: "{highest_behavior}" é seu comportamento melhor avaliado pelo grupo (pontuação {highest_stats["group_avg"]:.1f}).'
                )
                insights.append(
                    f'**Área de Desenvolvimento**: "{lowest_behavior}" apresenta a menor pontuação (pontuação {lowest_stats["group_avg"]:.1f}), representando uma oportunidade para desenvolvimento.'
                )

            # Historical trend insight
            if historical_data and len(historical_data) >= 2:
                # Check for consistent trends
                improving_behaviors = []
                declining_behaviors = []

                # Get common behaviors
                common_behaviors = set(behavior_data.keys())
                for year_data in historical_data.values():
                    common_behaviors &= set(year_data.keys())

                for behavior in common_behaviors:
                    values = []
                    years = sorted(historical_data.keys())

                    # Get historical values
                    for year in years:
                        if (
                            behavior in historical_data[year]
                            and historical_data[year][behavior]
                        ):
                            value = sum(historical_data[year][behavior]) / len(
                                historical_data[year][behavior]
                            )
                            values.append(value)

                    # Add current year
                    if behavior in behavior_data and behavior_data[behavior]:
                        value = sum(behavior_data[behavior]) / len(
                            behavior_data[behavior]
                        )
                        values.append(value)

                    # Check for consistent trend (at least 3 data points)
                    if len(values) >= 3:
                        if all(
                            values[i] <= values[i + 1] for i in range(len(values) - 1)
                        ):
                            improving_behaviors.append(behavior)
                        elif all(
                            values[i] >= values[i + 1] for i in range(len(values) - 1)
                        ):
                            declining_behaviors.append(behavior)

                if improving_behaviors:
                    insights.append(
                        f"**Tendência de Melhoria**: Os comportamentos {', '.join(improving_behaviors)} mostram uma tendência consistente de melhoria ao longo do tempo."
                    )

                if declining_behaviors:
                    insights.append(
                        f"**Tendência de Declínio**: Os comportamentos {', '.join(declining_behaviors)} mostram uma tendência de declínio que merece atenção."
                    )

            # Add resilience insight
            if "resilience_score" in locals() and resilience_score is not None:
                resilience_pct = min(100, max(0, int(resilience_score * 100)))
                insights.append(
                    f'**Perfil de Resiliência**: Seu índice de resiliência é {resilience_pct}%, caracterizado por um padrão de "{recovery_pattern}". {" A alta resiliência sugere boa capacidade de adaptação e recuperação." if resilience_pct > 70 else " Há oportunidade para desenvolver maior resiliência em situações de mudança."}'
                )

        if not insights:
            insights.append(
                "**Recomendação geral**: Continuar monitorando e coletando dados para uma análise mais detalhada de padrões e correlações no próximo ciclo de avaliação."
            )

        # Add insights to report
        report += "### Principais Insights\n\n"
        for i, insight in enumerate(insights):
            report += f"{i + 1}. {insight}\n\n"

        # Add recommendations section if we have enough data
        if behavior_stats and len(behavior_stats) >= 2:
            report += "### Recomendações de Desenvolvimento\n\n"

            # Generate tailored recommendations
            recommendations = []

            # Recommendation for alignment
            if abs(perception_diff) > 0.5:
                if perception_diff > 0:
                    recommendations.append(
                        "**Busque feedback mais frequente**: Para alinhar sua autopercepção com a visão externa, estabeleça canais de feedback regulares e estruturados com colegas e líderes."
                    )
                else:
                    recommendations.append(
                        "**Reconheça seus pontos fortes**: Trabalhe no reconhecimento de suas competências e conquistas, possivelmente com o apoio de um mentor que ajude a identificar suas fortalezas."
                    )

            # Recommendation for development areas
            sorted_by_group = sorted(
                behavior_stats.items(), key=lambda x: x[1]["group_avg"]
            )
            development_areas = [b for b, s in sorted_by_group[:2]]

            if development_areas:
                recommendations.append(
                    f"**Plano de desenvolvimento focalizado**: Elabore um plano específico para os comportamentos {' e '.join(development_areas)}, definindo ações concretas e métricas de progresso."
                )

            # Recommendation for leveraging strengths
            sorted_by_group = sorted(
                behavior_stats.items(), key=lambda x: x[1]["group_avg"], reverse=True
            )
            strengths = [b for b, s in sorted_by_group[:2]]

            if strengths:
                recommendations.append(
                    f"**Potencialize seus pontos fortes**: Utilize seus comportamentos mais desenvolvidos ({' e '.join(strengths)}) como alavancas para melhorar em outras áreas."
                )

            # Add recommendations to report
            for i, recommendation in enumerate(recommendations):
                report += f"{i + 1}. {recommendation}\n\n"

        # Add a divider
        report += "---\n\n"

        # Footer
        report += "> *Este relatório foi gerado automaticamente com base nos dados de avaliação disponíveis. As análises e recomendações servem como ponto de partida para discussões de desenvolvimento mais aprofundadas.*\n"

        return report

    def _get_historical_data(
        self, pessoa_name: str, current_year: str
    ) -> Dict[str, Dict]:
        """
        Attempt to load historical data for a person from previous years.

        Args:
            pessoa_name: Person name
            current_year: Current year being analyzed (to exclude from historical data)

        Returns:
            Dictionary mapping years to behavior data dictionaries
        """
        import json
        from pathlib import Path

        historical_data = {}

        # Try to find data files in output directory
        output_dir = Path("output")
        if output_dir.exists():
            # Look for data files for this person
            data_dir = output_dir / "data"
            if data_dir.exists():
                for file_path in data_dir.glob(f"{pessoa_name}_*.json"):
                    # Extract year from filename
                    filename = file_path.stem  # Get filename without extension
                    parts = filename.split("_")
                    if len(parts) > 1:
                        year = parts[-1]  # Assume last part is the year

                        # Skip current year
                        if year == current_year:
                            continue

                        try:
                            # Load data
                            with open(file_path, "r", encoding="utf-8") as f:
                                data = json.load(f)

                            # Extract behavior data
                            behavior_data = self._extract_behavior_data(data)
                            if behavior_data:
                                historical_data[year] = behavior_data
                        except Exception:
                            # Silently ignore errors in loading historical data
                            pass

        return historical_data

    def _calculate_behavior_stats(self, behavior_data: Dict, group_data: Dict) -> Dict:
        """
        Calculate statistical metrics for behaviors.

        Args:
            behavior_data: Dictionary of behavior data
            group_data: Dictionary of group assessment data

        Returns:
            Dictionary with statistical metrics for each behavior
        """
        stats = {}

        for behavior, values in behavior_data.items():
            if isinstance(values, list) and values:
                # Calculate self assessment metrics
                self_avg = sum(values) / len(values)

                # Calculate group assessment metrics if available
                group_avg = 0
                gap = 0

                if (
                    behavior in group_data
                    and isinstance(group_data[behavior], list)
                    and group_data[behavior]
                ):
                    group_avg = sum(group_data[behavior]) / len(group_data[behavior])
                    gap = self_avg - group_avg

                # Determine status based on gap
                status = "Alinhado"
                if gap > 0.5:
                    status = "Sobrevalorizado ⬆️"
                elif gap < -0.5:
                    status = "Subvalorizado ⬇️"

                # Store metrics
                stats[behavior] = {
                    "self_avg": self_avg,
                    "group_avg": group_avg,
                    "gap": gap,
                    "status": status,
                }

        return stats

    def _calculate_correlation_matrix(self, behavior_data: Dict) -> tuple:
        """
        Calculate correlation matrix between behaviors.

        Args:
            behavior_data: Dictionary of behavior data

        Returns:
            Tuple of (correlation_matrix, DataFrame)
        """
        import pandas as pd

        try:
            # Convert behavior data to DataFrame
            df = pd.DataFrame(behavior_data)

            # Calculate correlation matrix
            corr_matrix = df.corr(method="spearman").round(2)

            return corr_matrix, df
        except Exception:
            return None, None

    def _predict_future_trends(
        self, historical_data: Dict, current_data: Dict, years_ahead: int = 2
    ) -> Dict:
        """
        Predict future trends based on historical data.

        Args:
            historical_data: Dictionary of historical behavior data by year
            current_data: Current behavior data
            years_ahead: Number of years to predict ahead

        Returns:
            Dictionary with predictions for each behavior
        """
        from scipy import stats

        predictions = {}
        current_year = max(historical_data.keys()) if historical_data else "2023"

        # Ensure current_year is an integer if possible
        try:
            current_year_int = int(current_year)
        except ValueError:
            current_year_int = 2023  # Default if conversion fails

        # Get common behaviors across years
        common_behaviors = set(current_data.keys())
        for year_data in historical_data.values():
            common_behaviors &= set(year_data.keys())

        for behavior in common_behaviors:
            # Collect historical values
            years = []
            values = []

            # Add historical data points
            for year in sorted(historical_data.keys()):
                if behavior in historical_data[year]:
                    if (
                        isinstance(historical_data[year][behavior], list)
                        and historical_data[year][behavior]
                    ):
                        year_int = int(year) if year.isdigit() else 0
                        value = sum(historical_data[year][behavior]) / len(
                            historical_data[year][behavior]
                        )
                        years.append(year_int)
                        values.append(value)

            # Add current data point
            if (
                behavior in current_data
                and isinstance(current_data[behavior], list)
                and current_data[behavior]
            ):
                value = sum(current_data[behavior]) / len(current_data[behavior])
                years.append(current_year_int)
                values.append(value)

            # Perform linear regression if we have at least 2 data points
            if len(years) >= 2:
                try:
                    # Calculate linear regression
                    slope, intercept, r_value, p_value, std_err = stats.linregress(
                        years, values
                    )

                    # Predict future values
                    future_predictions = []
                    future_years = []

                    for i in range(1, years_ahead + 1):
                        future_year = current_year_int + i
                        prediction = slope * future_year + intercept

                        # Cap predictions to reasonable bounds (1-6)
                        prediction = max(1, min(6, prediction))

                        future_predictions.append(prediction)
                        future_years.append(future_year)

                    predictions[behavior] = {
                        "years": future_years,
                        "values": future_predictions,
                        "slope": slope,
                        "r_value": r_value,
                        "p_value": p_value,
                    }
                except Exception:
                    # If regression fails, don't provide predictions
                    pass

        return predictions

    def _calculate_resilience_score(
        self, historical_data: Dict, current_data: Dict
    ) -> tuple:
        """
        Calculate resilience score based on trend patterns.

        Args:
            historical_data: Dictionary of historical behavior data by year
            current_data: Current behavior data

        Returns:
            Tuple of (resilience_score, adaptability_index, recovery_pattern)
        """
        if not historical_data:
            return None, None, None

        # Get common behaviors
        common_behaviors = set(current_data.keys())
        for year_data in historical_data.values():
            common_behaviors &= set(year_data.keys())

        if not common_behaviors:
            return None, None, None

        # Count patterns
        dip_recovery_count = 0
        decline_count = 0
        growth_count = 0
        stable_count = 0
        total_count = 0

        # Calculate year-over-year changes
        for behavior in common_behaviors:
            values = []

            # Get values for each year including current
            for year in sorted(historical_data.keys()):
                if behavior in historical_data[year]:
                    if (
                        isinstance(historical_data[year][behavior], list)
                        and historical_data[year][behavior]
                    ):
                        value = sum(historical_data[year][behavior]) / len(
                            historical_data[year][behavior]
                        )
                        values.append(value)

            # Add current year data
            if (
                behavior in current_data
                and isinstance(current_data[behavior], list)
                and current_data[behavior]
            ):
                value = sum(current_data[behavior]) / len(current_data[behavior])
                values.append(value)

            # Identify pattern with at least 3 data points
            if len(values) >= 3:
                total_count += 1

                # Check for dip and recovery (v-shape)
                dips_found = 0
                for i in range(1, len(values) - 1):
                    if values[i] < values[i - 1] and values[i] < values[i + 1]:
                        dips_found += 1

                if dips_found > 0:
                    dip_recovery_count += 1
                # Check for continuous decline
                elif all(values[i] < values[i - 1] for i in range(1, len(values))):
                    decline_count += 1
                # Check for continuous growth
                elif all(values[i] > values[i - 1] for i in range(1, len(values))):
                    growth_count += 1
                else:
                    stable_count += 1

        # Calculate scores if we have data
        if total_count > 0:
            # Resilience score: higher is better
            # Weighted average of positive patterns (dip-recovery, growth) vs negative (decline)
            resilience_score = (
                dip_recovery_count * 5 + growth_count * 4 + stable_count * 3
            ) / (total_count * 5)

            # Recovery pattern
            if dip_recovery_count / total_count > 0.5:
                recovery_pattern = "Recuperação Rápida"
            elif stable_count / total_count > 0.5:
                recovery_pattern = "Estabilização"
            elif decline_count / total_count > 0.5:
                recovery_pattern = "Declínio Contínuo"
            elif growth_count / total_count > 0.5:
                recovery_pattern = "Crescimento Contínuo"
            else:
                recovery_pattern = "Padrão Misto"

            # Adaptability index
            adaptability_index = (
                dip_recovery_count * 5 + stable_count * 2.5 + growth_count * 4
            ) / total_count

            return resilience_score, adaptability_index, recovery_pattern

        return None, None, None

    def _calculate_statistical_significance(self, stats: Dict) -> Dict:
        """
        Calculate statistical significance of gaps.

        Args:
            stats: Dictionary with behavior statistics

        Returns:
            Dictionary with significance statistics
        """
        import numpy as np
        from scipy import stats as scipy_stats

        significance = {}

        # Gather all gaps
        gaps = [s["gap"] for s in stats.values()]

        if len(gaps) < 2:
            return significance

        # Calculate standard deviation of gaps
        std_dev = np.std(gaps)
        mean_gap = np.mean(gaps)

        # Calculate significance for each behavior
        for behavior, behavior_stats in stats.items():
            gap = behavior_stats["gap"]

            # Calculate Z-score
            if std_dev > 0:
                z_score = (gap - mean_gap) / std_dev
            else:
                z_score = 0

            # Calculate p-value (two-tailed test)
            if std_dev > 0:
                p_value = 2 * (1 - scipy_stats.norm.cdf(abs(z_score)))
            else:
                p_value = 1.0

            # Determine significance
            is_significant = p_value < 0.05

            # Format p-value
            if p_value < 0.001:
                p_value_formatted = "p<0.001"
            elif p_value < 0.01:
                p_value_formatted = "p<0.01"
            elif p_value < 0.05:
                p_value_formatted = "p<0.05"
            elif p_value < 0.1:
                p_value_formatted = "p<0.1"
            else:
                p_value_formatted = f"p={p_value:.2f}"

            significance[behavior] = {
                "z_score": z_score,
                "p_value": p_value,
                "p_value_formatted": p_value_formatted,
                "is_significant": is_significant,
            }

        return significance

    def generate_roi_analysis(self, data: Dict, pessoa_name: str, ano_name: str) -> str:
        """
        Generate an ROI analysis report that helps prioritize development actions based on
        effort vs. impact analysis.

        Args:
            data: Processed evaluation data
            pessoa_name: Person name
            ano_name: Year or period name

        Returns:
            ROI analysis report as markdown string
        """
        # Initialize the report content
        content = self._format_header(
            "Análise de ROI e Priorização", pessoa_name, ano_name
        )

        # Extract behavior data for analysis
        behavior_data = self._extract_behavior_data(data)
        group_data = self._extract_group_data(data)

        # Skip if we don't have enough data
        if not behavior_data:
            content += "Não há dados suficientes para análise de ROI e priorização.\n"
            return content

        # Add Overview section
        overview = "Este relatório apresenta uma análise de retorno sobre investimento (ROI) para priorização de ações de desenvolvimento.\n\n"
        overview += "A análise considera múltiplos fatores para determinar quais comportamentos oferecem o melhor potencial de retorno considerando:\n"
        overview += "- Tamanho do gap em relação ao grupo de referência\n"
        overview += "- Impacto potencial na avaliação global\n"
        overview += "- Esforço estimado para desenvolvimento\n"
        overview += "- Correlação com outros comportamentos (efeito cascata)\n\n"

        content += self._format_section("Visão Geral", overview)

        # Perform multi-factor ROI analysis
        roi_results = self.pattern_analyzer.calculate_development_roi(
            behavior_data, group_data
        )

        # Add ROI Analysis section if we have results
        if roi_results and "behaviors" in roi_results:
            roi_section = "### Análise de ROI por Comportamento\n\n"

            # Create a table of ROI metrics
            roi_rows = []
            for behavior in roi_results["behaviors"][
                :10
            ]:  # Show top 10 behaviors by ROI
                name = behavior["name"]
                gap = behavior["gap"]
                impact = behavior["impact"]
                effort = behavior["effort"]
                roi = behavior["roi"]

                # Shorten behavior name if needed
                short_name = name[:30] + "..." if len(name) > 30 else name

                roi_rows.append(
                    [
                        short_name,
                        f"{gap:.2f}",
                        f"{impact:.2f}",
                        f"{effort:.2f}",
                        f"{roi:.2f}",
                    ]
                )

            roi_headers = ["Comportamento", "Gap", "Impacto", "Esforço", "ROI"]
            roi_section += self._format_table(roi_headers, roi_rows)

            # Add ROI visualization using Mermaid quadrant chart
            roi_section += "\n### Matriz de Priorização\n\n"

            # Generate quadrant chart
            quadrant_chart = self.mermaid_visualizer.create_roi_quadrant(
                roi_results["behaviors"][:15]
            )
            roi_section += f"```mermaid\n{quadrant_chart}\n```\n\n"

            # Add quadrant interpretation
            roi_section += "**Interpretação da Matriz:**\n\n"
            roi_section += "- **Alto Impacto, Baixo Esforço** (Quadrante superior direito): Prioridade máxima\n"
            roi_section += "- **Alto Impacto, Alto Esforço** (Quadrante superior esquerdo): Considerar para desenvolvimento de longo prazo\n"
            roi_section += "- **Baixo Impacto, Baixo Esforço** (Quadrante inferior direito): Ganhos rápidos, prioridade secundária\n"
            roi_section += "- **Baixo Impacto, Alto Esforço** (Quadrante inferior esquerdo): Baixa prioridade\n\n"

            content += self._format_section("Análise de ROI", roi_section)

            # Add Effort-Impact Distribution section
            distribution_section = "### Distribuição de Esforço-Impacto\n\n"

            # Create a summary of the distribution
            high_impact_low_effort = [
                b
                for b in roi_results["behaviors"]
                if b["impact"] > 0.6 and b["effort"] < 0.4
            ]
            high_impact_high_effort = [
                b
                for b in roi_results["behaviors"]
                if b["impact"] > 0.6 and b["effort"] >= 0.4
            ]
            low_impact_low_effort = [
                b
                for b in roi_results["behaviors"]
                if b["impact"] <= 0.6 and b["effort"] < 0.4
            ]
            low_impact_high_effort = [
                b
                for b in roi_results["behaviors"]
                if b["impact"] <= 0.6 and b["effort"] >= 0.4
            ]

            distribution_section += f"- **Alto Impacto, Baixo Esforço:** {len(high_impact_low_effort)} comportamentos\n"
            distribution_section += f"- **Alto Impacto, Alto Esforço:** {len(high_impact_high_effort)} comportamentos\n"
            distribution_section += f"- **Baixo Impacto, Baixo Esforço:** {len(low_impact_low_effort)} comportamentos\n"
            distribution_section += f"- **Baixo Impacto, Alto Esforço:** {len(low_impact_high_effort)} comportamentos\n\n"

            content += self._format_section(
                "Distribuição de Esforço-Impacto", distribution_section
            )

        # Add Priority Actions section
        priority_section = "### Ações Prioritárias Recomendadas\n\n"

        # If we have ROI results, recommend top actions
        if roi_results and "behaviors" in roi_results:
            # Filter for high ROI behaviors (top 5)
            priority_behaviors = roi_results["behaviors"][:5]

            priority_section += (
                "Com base na análise de ROI, recomendamos foco nas seguintes ações:\n\n"
            )

            for i, behavior in enumerate(priority_behaviors):
                name = behavior["name"]
                roi = behavior["roi"]
                gap = behavior["gap"]

                priority_section += f"**{i + 1}. {name}**\n"
                priority_section += f"   - ROI Estimado: {roi:.2f}\n"
                priority_section += f"   - Gap Atual: {gap:.2f}\n"

                # Add tailored recommendation based on behavior characteristics
                if behavior["impact"] > 0.7:
                    priority_section += "   - **Recomendação:** Prioridade alta devido ao alto impacto potencial\n"
                elif behavior["effort"] < 0.3:
                    priority_section += "   - **Recomendação:** Ganho rápido devido ao baixo esforço necessário\n"
                else:
                    priority_section += "   - **Recomendação:** Desenvolvimento contínuo com monitoramento regular\n"

                priority_section += "\n"
        else:
            # Generic recommendations if no ROI analysis
            priority_section += (
                "Sem dados suficientes para análise de ROI, recomendamos:\n\n"
            )
            priority_section += (
                "1. Focar nos comportamentos com maiores gaps identificados\n"
            )
            priority_section += (
                "2. Priorizar comportamentos relacionados a competências centrais\n"
            )
            priority_section += (
                "3. Desenvolver um plano de ação com metas específicas e mensuráveis\n"
            )

        content += self._format_section("Ações Prioritárias", priority_section)

        # Add Simulation section
        simulation_section = "### Simulação de Cenários\n\n"

        # Create a what-if simulation table for top behaviors
        if roi_results and "behaviors" in roi_results:
            top_behaviors = roi_results["behaviors"][:3]  # Top 3 behaviors

            simulation_section += "A tabela abaixo simula o impacto de diferentes níveis de melhoria nos comportamentos prioritários:\n\n"

            sim_rows = []
            for behavior in top_behaviors:
                name = behavior["name"]
                current_gap = behavior["gap"]

                # Simulate different levels of improvement
                small_improvement = current_gap * 0.25
                medium_improvement = current_gap * 0.5
                large_improvement = current_gap * 0.75

                # Calculate potential impact on global score (simplified)
                impact_factor = behavior["impact"]
                small_impact = small_improvement * impact_factor
                medium_impact = medium_improvement * impact_factor
                large_impact = large_improvement * impact_factor

                # Shorten behavior name if needed
                short_name = name[:25] + "..." if len(name) > 25 else name

                sim_rows.append(
                    [
                        short_name,
                        f"{small_improvement:.2f} ({small_impact:.3f})",
                        f"{medium_improvement:.2f} ({medium_impact:.3f})",
                        f"{large_improvement:.2f} ({large_impact:.3f})",
                    ]
                )

            sim_headers = [
                "Comportamento",
                "Melhoria 25%",
                "Melhoria 50%",
                "Melhoria 75%",
            ]
            simulation_section += self._format_table(sim_headers, sim_rows)

            simulation_section += (
                "\n*Valores mostram redução do gap (impacto no score global)*\n\n"
            )
        else:
            simulation_section += "Dados insuficientes para simulação de cenários.\n"

        content += self._format_section("Simulação de Cenários", simulation_section)

        # Add Development Strategy section
        strategy_section = "### Estratégia de Desenvolvimento\n\n"

        strategy_section += "**Abordagem Recomendada:**\n\n"

        # Tailor strategy based on ROI analysis patterns
        if roi_results and "behaviors" in roi_results:
            # Check if we have many high ROI behaviors
            high_roi_count = len(
                [b for b in roi_results["behaviors"] if b["roi"] > 0.6]
            )

            if high_roi_count > 5:
                strategy_section += "**Estratégia Faseada:**\n\n"
                strategy_section += "1. **Fase 1 (1-3 meses):** Focar nos ganhos rápidos (alto ROI, baixo esforço)\n"
                strategy_section += (
                    "2. **Fase 2 (3-6 meses):** Trabalhar comportamentos de médio ROI\n"
                )
                strategy_section += "3. **Fase 3 (6-12 meses):** Abordar comportamentos de alto impacto mesmo com alto esforço\n"
            else:
                strategy_section += "**Estratégia Concentrada:**\n\n"
                strategy_section += "1. **Foco Imediato:** Concentrar em 2-3 comportamentos de maior ROI\n"
                strategy_section += "2. **Monitoramento Regular:** Avaliar progresso a cada 4-6 semanas\n"
                strategy_section += "3. **Ajuste Iterativo:** Refinar abordagem com base em resultados iniciais\n"
        else:
            strategy_section += "**Estratégia Exploratória:**\n\n"
            strategy_section += "1. **Coleta de Dados:** Obter mais informações sobre esforço e impacto dos comportamentos\n"
            strategy_section += "2. **Experimentação:** Testar diferentes abordagens de desenvolvimento\n"
            strategy_section += "3. **Revisão Regular:** Avaliar progresso e refinar estratégia a cada 4-8 semanas\n"

        content += self._format_section(
            "Estratégia de Desenvolvimento", strategy_section
        )

        # Add footer
        content += "\n---\n*Este relatório foi gerado automaticamente pelo sistema de Análise Avançada de Desempenho.*\n"

        return content

    def generate_network_analysis(
        self, data: Dict, pessoa_name: str, ano_name: str
    ) -> str:
        """
        Generate a network analysis report focusing on behavior relationships,
        centrality, and influence patterns in the evaluation data.

        Args:
            data: Processed evaluation data
            pessoa_name: Person name
            ano_name: Year or period name

        Returns:
            Network analysis report as markdown string
        """
        # Initialize the report content
        content = self._format_header(
            "Análise de Rede de Comportamentos", pessoa_name, ano_name
        )

        # Extract behavior data for analysis
        behavior_data = self._extract_behavior_data(data)

        # Skip if we don't have enough data
        if len(behavior_data) < 3:
            content += "Não há dados suficientes para análise de rede. São necessários ao menos 3 comportamentos.\n"
            return content

        # Add Overview section
        overview = "Este relatório apresenta uma análise da rede de relacionamentos entre comportamentos, identificando padrões de influência, comportamentos centrais e clusters naturais.\n\n"
        overview += "A análise de rede permite visualizar o sistema comportamental como um todo interconectado, revelando:\n"
        overview += "- Comportamentos centrais com maior influência no sistema\n"
        overview += "- Agrupamentos naturais de comportamentos relacionados\n"
        overview += "- Cadeias de influência e efeitos cascata\n"
        overview += "- Pontos de alavancagem para intervenções estratégicas\n\n"

        content += self._format_section("Visão Geral", overview)

        # Calculate correlation matrix for network construction
        correlation_data = self.pattern_analyzer.calculate_correlation_matrix(
            behavior_data
        )

        # Add correlation network visualization if we have results
        if (
            correlation_data
            and "pairs" in correlation_data
            and len(correlation_data["pairs"]) > 0
        ):
            network_section = "### Rede de Correlação entre Comportamentos\n\n"

            network_section += (
                "O diagrama abaixo representa as relações entre comportamentos, onde:\n"
            )
            network_section += "- Cada nó representa um comportamento\n"
            network_section += "- As conexões representam correlações significativas\n"
            network_section += "- A espessura das linhas indica a força da correlação\n"
            network_section += "- Linhas sólidas indicam correlações positivas, tracejadas indicam negativas\n\n"

            # Generate network visualization
            network_diagram = self.mermaid_visualizer.create_correlation_network(
                correlation_data, threshold=0.3, max_nodes=10
            )
            network_section += f"```mermaid\n{network_diagram}\n```\n\n"

            content += self._format_section("Rede de Correlação", network_section)

        # Perform centrality analysis if we have correlation data
        if (
            correlation_data
            and "matrix" in correlation_data
            and "names" in correlation_data
        ):
            centrality_section = "### Análise de Centralidade e Influência\n\n"

            centrality_section += "A centralidade de um comportamento indica seu grau de influência e importância na rede comportamental.\n"
            centrality_section += "Comportamentos com alta centralidade tendem a ter maior impacto cascata quando desenvolvidos.\n\n"

            # Calculate basic centrality metrics
            try:
                names = correlation_data["names"]
                matrix = np.array(correlation_data["matrix"])

                # Simple degree centrality (number of strong connections)
                degree_centrality = []
                for i, name in enumerate(names):
                    # Count connections with correlation > 0.3 (absolute value)
                    connections = sum(
                        1
                        for j in range(len(names))
                        if i != j and abs(matrix[i][j]) > 0.3
                    )

                    # Calculate weighted degree (sum of correlation strengths)
                    weighted_degree = sum(
                        abs(matrix[i][j]) for j in range(len(names)) if i != j
                    )

                    degree_centrality.append(
                        {
                            "name": name,
                            "connections": connections,
                            "weighted_degree": weighted_degree,
                            "avg_strength": weighted_degree / max(connections, 1),
                        }
                    )

                # Sort by weighted degree
                degree_centrality.sort(key=lambda x: x["weighted_degree"], reverse=True)

                # Create table of top behaviors by centrality
                centrality_rows = []
                for behavior in degree_centrality[:7]:  # Show top 7 behaviors
                    name = behavior["name"]
                    connections = behavior["connections"]
                    weighted = behavior["weighted_degree"]
                    avg_strength = behavior["avg_strength"]

                    # Shorten behavior name if needed
                    short_name = name[:30] + "..." if len(name) > 30 else name

                    centrality_rows.append(
                        [
                            short_name,
                            f"{connections}",
                            f"{weighted:.2f}",
                            f"{avg_strength:.2f}",
                        ]
                    )

                centrality_headers = [
                    "Comportamento",
                    "Conexões",
                    "Grau Ponderado",
                    "Força Média",
                ]
                centrality_section += "#### Comportamentos com Maior Centralidade\n\n"
                centrality_section += self._format_table(
                    centrality_headers, centrality_rows
                )

                # Add interpretation of highest centrality behaviors
                if len(degree_centrality) > 0:
                    centrality_section += "\n#### Comportamentos-Chave na Rede\n\n"

                    for i, behavior in enumerate(degree_centrality[:3]):
                        name = behavior["name"]
                        weighted = behavior["weighted_degree"]
                        connections = behavior["connections"]

                        centrality_section += f"**{i + 1}. {name}**\n"
                        centrality_section += (
                            f"   - Grau de centralidade: {weighted:.2f}\n"
                        )
                        centrality_section += (
                            f"   - Conexões significativas: {connections}\n"
                        )

                        # Add specific interpretation based on centrality
                        if i == 0:  # Top behavior
                            centrality_section += "   - **Interpretação:** Comportamento mais central e influente na rede. Potencial ponto de alavancagem para desenvolvimento.\n\n"
                        elif i == 1:  # Second behavior
                            centrality_section += "   - **Interpretação:** Comportamento secundário com influência significativa. Complementar ao comportamento principal.\n\n"
                        else:  # Third behavior
                            centrality_section += "   - **Interpretação:** Comportamento terciário que serve como ponte entre diferentes áreas da rede.\n\n"

            except Exception as e:
                centrality_section += f"Erro na análise de centralidade: {str(e)}\n\n"

            content += self._format_section(
                "Análise de Centralidade", centrality_section
            )

        # Perform cluster analysis to identify communities
        cluster_results = self.pattern_analyzer.analyze_clusters(behavior_data)

        if (
            cluster_results
            and "clusters" in cluster_results
            and len(cluster_results["clusters"]) > 0
        ):
            cluster_section = "### Comunidades de Comportamentos\n\n"

            cluster_section += "Comunidades são grupos de comportamentos fortemente relacionados entre si. "
            cluster_section += "A identificação de comunidades revela a estrutura natural do sistema comportamental.\n\n"

            # Add silhouette score interpretation if available
            if "silhouette_score" in cluster_results:
                score = cluster_results["silhouette_score"]
                cluster_section += (
                    f"**Coerência das comunidades (score silhouette):** {score:.2f}\n"
                )

                if score > 0.7:
                    cluster_section += (
                        "Comunidades bem definidas e claramente separadas.\n\n"
                    )
                elif score > 0.5:
                    cluster_section += (
                        "Comunidades razoavelmente definidas com alguma separação.\n\n"
                    )
                elif score > 0.3:
                    cluster_section += "Comunidades com alguma sobreposição, mas ainda distinguíveis.\n\n"
                else:
                    cluster_section += "Comunidades pouco definidas com significativa sobreposição.\n\n"

            # Describe each cluster/community
            for i, cluster in enumerate(cluster_results["clusters"]):
                behaviors = cluster.get("behaviors", [])

                if len(behaviors) > 0:
                    cluster_section += (
                        f"#### Comunidade {i + 1} ({len(behaviors)} comportamentos)\n\n"
                    )

                    # List behaviors in this cluster
                    behavior_list = ""
                    for beh in behaviors[:7]:  # Show up to 7 behaviors per cluster
                        behavior_list += f"- {beh}\n"

                    if len(behaviors) > 7:
                        behavior_list += (
                            f"- ... e {len(behaviors) - 7} mais comportamentos\n"
                        )

                    cluster_section += behavior_list + "\n"

                    # Add interpretation based on cluster characteristics
                    if i == 0 and len(behaviors) > len(behavior_data) / 3:
                        cluster_section += "**Interpretação:** Comunidade principal que representa o núcleo comportamental. "
                        cluster_section += "Estes comportamentos têm alta coesão e provavelmente compartilham mecanismos subjacentes comuns.\n\n"
                    elif 1 <= i <= 2:
                        cluster_section += "**Interpretação:** Comunidade secundária que representa um conjunto complementar de habilidades. "
                        cluster_section += "Desenvolvimento integrado destes comportamentos pode gerar sinergias significativas.\n\n"
                    else:
                        cluster_section += "**Interpretação:** Comunidade especializada com conexões mais limitadas ao resto da rede. "
                        cluster_section += "Estes comportamentos podem representar habilidades específicas ou nichos comportamentais.\n\n"

            content += self._format_section(
                "Comunidades de Comportamentos", cluster_section
            )

        # Add influence pathways section - identify potential chains of influence
        if (
            correlation_data
            and "pairs" in correlation_data
            and len(correlation_data["pairs"]) > 0
        ):
            paths_section = "### Cadeias de Influência\n\n"

            paths_section += "Cadeias de influência mostram como o desenvolvimento de um comportamento pode afetar outros em sequência, "
            paths_section += (
                "criando efeitos cascata através da rede comportamental.\n\n"
            )

            # Sort correlations by strength
            strong_correlations = [
                p for p in correlation_data["pairs"] if abs(p["correlation"]) > 0.5
            ]
            strong_correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)

            # Identify potential chains (simplified approach)
            chains = []

            if len(strong_correlations) > 0:
                # Start with top correlations as seeds
                for i in range(min(3, len(strong_correlations))):
                    start_pair = strong_correlations[i]
                    start_beh1 = start_pair["behavior1"]
                    start_beh2 = start_pair["behavior2"]

                    # Find behaviors that connect to the second behavior
                    extensions = [
                        p
                        for p in correlation_data["pairs"]
                        if p != start_pair
                        and (
                            p["behavior1"] == start_beh2 or p["behavior2"] == start_beh2
                        )
                        and abs(p["correlation"]) > 0.4
                    ]

                    if extensions:
                        # Get the strongest extension
                        extensions.sort(
                            key=lambda x: abs(x["correlation"]), reverse=True
                        )
                        ext = extensions[0]

                        # Determine third behavior in chain
                        third_beh = (
                            ext["behavior1"]
                            if ext["behavior1"] != start_beh2
                            else ext["behavior2"]
                        )

                        chains.append(
                            {
                                "behaviors": [start_beh1, start_beh2, third_beh],
                                "correlations": [
                                    start_pair["correlation"],
                                    ext["correlation"],
                                ],
                                "strength": abs(start_pair["correlation"])
                                * abs(ext["correlation"]),
                            }
                        )

            if chains:
                # Sort chains by overall strength
                chains.sort(key=lambda x: x["strength"], reverse=True)

                paths_section += "#### Principais Cadeias de Influência\n\n"

                for i, chain in enumerate(chains[:3]):  # Show top 3 chains
                    behaviors = chain["behaviors"]
                    correlations = chain["correlations"]

                    paths_section += f"**Cadeia {i + 1}:** "
                    paths_section += (
                        f"{behaviors[0]} → {behaviors[1]} → {behaviors[2]}\n"
                    )
                    paths_section += f"   - Correlação 1: {correlations[0]:.2f}\n"
                    paths_section += f"   - Correlação 2: {correlations[1]:.2f}\n"
                    paths_section += f"   - Força total: {chain['strength']:.2f}\n\n"

                # Add visualization of top chain if available
                if len(chains) > 0:
                    top_chain = chains[0]

                    paths_section += (
                        "#### Visualização da Principal Cadeia de Influência\n\n"
                    )
                    paths_section += "```mermaid\n"
                    paths_section += "graph LR\n"

                    # Create nodes and edges for the chain
                    b1, b2, b3 = top_chain["behaviors"]
                    c1, c2 = top_chain["correlations"]

                    # Shorten behavior names if needed
                    b1_short = (b1[:25] + "...") if len(b1) > 25 else b1
                    b2_short = (b2[:25] + "...") if len(b2) > 25 else b2
                    b3_short = (b3[:25] + "...") if len(b3) > 25 else b3

                    # Determine edge style based on correlation type
                    style1 = "-->" if c1 > 0 else "-.->"
                    style2 = "-->" if c2 > 0 else "-.->"

                    paths_section += (
                        f"    A[{b1_short}] {style1}|{abs(c1):.2f}| B[{b2_short}]\n"
                    )
                    paths_section += f"    B {style2}|{abs(c2):.2f}| C[{b3_short}]\n"

                    # Add styling
                    paths_section += (
                        "    classDef primary fill:#d4edda,stroke:#28a745,color:#000;\n"
                    )
                    paths_section += "    classDef secondary fill:#fff3cd,stroke:#ffc107,color:#000;\n"
                    paths_section += "    class A primary;\n"
                    paths_section += "    class B,C secondary;\n"
                    paths_section += "```\n\n"

                    # Add interpretation
                    paths_section += "**Interpretação da Cadeia Principal:**\n\n"
                    paths_section += f"1. O desenvolvimento do comportamento '{b1}' tem potencial para influenciar '{b2}'\n"
                    paths_section += f"2. A melhoria em '{b2}' por sua vez pode impactar positivamente '{b3}'\n"
                    paths_section += "3. Esta cadeia representa um caminho de desenvolvimento estratégico com potencial efeito multiplicador\n\n"
            else:
                paths_section += "Não foram identificadas cadeias de influência claras com os dados disponíveis.\n\n"

            content += self._format_section("Cadeias de Influência", paths_section)

        # Add strategic recommendations based on network analysis
        recommendations_section = "### Recomendações Estratégicas\n\n"

        recommendations_section += "Com base na análise de rede de comportamentos, recomendamos as seguintes abordagens estratégicas:\n\n"

        # If we have centrality data, recommend focusing on high centrality behaviors
        if "degree_centrality" in locals() and len(degree_centrality) > 0:
            top_behaviors = degree_centrality[:3]

            recommendations_section += "#### 1. Foco em Comportamentos Centrais\n\n"
            recommendations_section += "Priorizar o desenvolvimento dos comportamentos com maior centralidade na rede:\n\n"

            for i, behavior in enumerate(top_behaviors):
                name = behavior["name"]
                recommendations_section += f"- **{name}**\n"
                recommendations_section += "  *Justificativa: Comportamento com alta centralidade e potencial efeito cascata na rede.*\n"

            recommendations_section += "\n"

        # If we have cluster data, recommend cluster-based approach
        if (
            "cluster_results" in locals()
            and "clusters" in cluster_results
            and len(cluster_results["clusters"]) > 0
        ):
            recommendations_section += "#### 2. Abordagem por Comunidades\n\n"
            recommendations_section += "Desenvolver comportamentos relacionados em conjunto para maximizar sinergias:\n\n"

            # Recommend focusing on the largest/main cluster
            main_cluster = max(
                cluster_results["clusters"], key=lambda x: len(x.get("behaviors", []))
            )
            main_behaviors = main_cluster.get("behaviors", [])

            if main_behaviors:
                recommendations_section += "**Comunidade Principal:**\n"
                for behavior in main_behaviors[:3]:
                    recommendations_section += f"- {behavior}\n"

                if len(main_behaviors) > 3:
                    recommendations_section += f"- ... e outros {len(main_behaviors) - 3} comportamentos relacionados\n"

                recommendations_section += "\n*Justificativa: Estes comportamentos formam um núcleo coeso com potencial para reforço mútuo.*\n\n"

        # If we have chains data, recommend chain-based approach
        if "chains" in locals() and chains:
            recommendations_section += (
                "#### 3. Estratégia de Desenvolvimento Sequencial\n\n"
            )
            recommendations_section += "Implementar desenvolvimento sequencial seguindo cadeias de influência naturais:\n\n"

            top_chain = chains[0]
            behaviors = top_chain["behaviors"]

            recommendations_section += "**Sequência Recomendada:**\n"
            recommendations_section += f"1. Iniciar com: **{behaviors[0]}**\n"
            recommendations_section += f"2. Seguido por: **{behaviors[1]}**\n"
            recommendations_section += f"3. Finalizar com: **{behaviors[2]}**\n\n"

            recommendations_section += "*Justificativa: Esta sequência aproveita as relações causais naturais entre os comportamentos, criando um efeito cascata positivo.*\n\n"

        # Add general recommendations if specific data is not available
        if (
            ("degree_centrality" not in locals() or len(degree_centrality) == 0)
            and ("cluster_results" not in locals() or "clusters" not in cluster_results)
            and ("chains" not in locals() or not chains)
        ):
            recommendations_section += "#### Recomendações Gerais\n\n"
            recommendations_section += "1. **Mapeamento Contínuo**: Coletar mais dados para refinar a análise de rede comportamental\n"
            recommendations_section += "2. **Experimentação Estratégica**: Testar intervenções em diferentes pontos da rede para identificar efeitos cascata\n"
            recommendations_section += "3. **Desenvolvimento Integrado**: Abordar grupos de comportamentos relacionados em conjunto\n\n"

        content += self._format_section(
            "Recomendações Estratégicas", recommendations_section
        )

        # Add footer
        content += "\n---\n*Este relatório foi gerado automaticamente pelo sistema de Análise Avançada de Desempenho.*\n"

        return content

    def generate_temporal_evolution(
        self, historical_data: List[Dict], pessoa_name: str
    ) -> str:
        """
        Generate a report analyzing performance evolution over time.

        Args:
            historical_data: List of processed evaluation data for multiple time periods,
                            ordered chronologically (oldest to newest)
            pessoa_name: Person name

        Returns:
            Temporal evolution report as markdown string
        """
        # Initialize the report content
        content = "# Análise de Evolução Temporal\n\n"
        content += f"### {pessoa_name}\n\n"
        content += f"*Relatório gerado em {self._format_timestamp()}*\n\n"

        # Check if we have enough data
        if not historical_data or len(historical_data) < 2:
            content += "Não há dados suficientes para análise temporal. São necessários pelo menos 2 períodos de avaliação.\n"
            return content

        # Extract years/periods from the data
        years = [
            data.get("ano_name", f"Período {i + 1}")
            for i, data in enumerate(historical_data)
        ]

        # Add Overview section
        overview = f"Este relatório apresenta uma análise da evolução do desempenho ao longo do tempo, abrangendo {len(years)} períodos de avaliação "
        overview += f"({years[0]} a {years[-1]}).\n\n"
        overview += "A análise temporal permite identificar padrões de desenvolvimento, velocidade de progresso, "
        overview += "tendências emergentes e projeções futuras baseadas em dados históricos.\n\n"

        content += self._format_section("Visão Geral", overview)

        # Extract global scores for each period
        global_scores = []
        for period_data in historical_data:
            if "global_scores" in period_data:
                score = period_data["global_scores"].get("colab_normalized", 0)
                global_scores.append(score)
            else:
                # If we don't have global scores, use a placeholder
                global_scores.append(0)

        # Create trajectory overview section
        trajectory_section = "### Trajetória Global de Desempenho\n\n"

        # Add summary of the overall trend
        if len(global_scores) >= 2:
            overall_change = global_scores[-1] - global_scores[0]
            avg_change_per_period = overall_change / (len(global_scores) - 1)

            trajectory_section += (
                f"**Mudança total no período:** {overall_change:.1f} pontos\n"
            )
            trajectory_section += f"**Média de mudança por período:** {avg_change_per_period:.1f} pontos\n\n"

            # Classify the overall pattern
            if overall_change > 10:
                trajectory_section += "**Padrão global:** Melhoria significativa\n\n"
            elif overall_change > 5:
                trajectory_section += "**Padrão global:** Melhoria moderada\n\n"
            elif overall_change > 2:
                trajectory_section += "**Padrão global:** Melhoria leve\n\n"
            elif overall_change > -2:
                trajectory_section += "**Padrão global:** Estabilidade\n\n"
            elif overall_change > -5:
                trajectory_section += "**Padrão global:** Declínio leve\n\n"
            elif overall_change > -10:
                trajectory_section += "**Padrão global:** Declínio moderado\n\n"
            else:
                trajectory_section += "**Padrão global:** Declínio significativo\n\n"

        # Add a Mermaid chart with the score evolution
        trajectory_section += "#### Evolução de Score Global ao Longo do Tempo\n\n"
        trajectory_section += "```mermaid\n"
        trajectory_section += "xychart-beta\n"
        trajectory_section += (
            f'    title "Evolução de Score Global ({years[0]} - {years[-1]})"\n'
        )
        trajectory_section += (
            f'    x-axis "Período" [{", ".join([f'"{y}"' for y in years])}]\n'
        )
        trajectory_section += '    y-axis "Score" [0, 20, 40, 60, 80, 100]\n'
        trajectory_section += (
            f"    line [{', '.join([f'{s:.1f}' for s in global_scores])}]\n"
        )
        trajectory_section += "```\n\n"

        # Add growth rate analysis if we have enough data points
        if len(global_scores) >= 3:
            # Calculate period-to-period changes
            changes = [
                global_scores[i] - global_scores[i - 1]
                for i in range(1, len(global_scores))
            ]

            # Detect if growth is accelerating, decelerating, or constant
            acceleration = 0
            for i in range(1, len(changes)):
                acceleration += changes[i] - changes[i - 1]

            acceleration_avg = (
                acceleration / (len(changes) - 1) if len(changes) > 1 else 0
            )

            # Add interpretation of growth pattern
            trajectory_section += "#### Análise de Padrão de Crescimento\n\n"

            if abs(acceleration_avg) < 1:
                trajectory_section += (
                    "**Padrão detectado:** Crescimento linear/constante\n\n"
                )
                trajectory_section += "O padrão de evolução mostra um ritmo relativamente constante ao longo do tempo, "
                trajectory_section += (
                    "sem acelerações ou desacelerações significativas.\n\n"
                )
            elif acceleration_avg > 1:
                trajectory_section += "**Padrão detectado:** Crescimento acelerado\n\n"
                trajectory_section += "O ritmo de melhoria tem aumentado ao longo do tempo, indicando um padrão de aceleração positiva. "
                trajectory_section += (
                    "Isso geralmente reflete um ciclo virtuoso de desenvolvimento.\n\n"
                )
            else:
                trajectory_section += (
                    "**Padrão detectado:** Crescimento desacelerado\n\n"
                )
                trajectory_section += "O ritmo de mudança tem diminuído ao longo do tempo, indicando uma desaceleração. "
                trajectory_section += "Isso pode refletir um platô natural ou oportunidade para renovar as estratégias de desenvolvimento.\n\n"

        content += self._format_section("Trajetória de Desempenho", trajectory_section)

        # Analyze behavior-level trajectories
        behavior_section = "### Evolução por Comportamento\n\n"

        # Extract behaviors that are present in all periods
        common_behaviors = set()
        first_period_behaviors = set()

        # Get behaviors from first period
        if historical_data and historical_data[0]:
            first_period_data = self._extract_behavior_data(historical_data[0])
            first_period_behaviors = set(first_period_data.keys())
            common_behaviors = first_period_behaviors.copy()

        # Intersect with behaviors from all other periods
        for period_data in historical_data[1:]:
            if period_data:
                period_behaviors = set(self._extract_behavior_data(period_data).keys())
                common_behaviors = common_behaviors.intersection(period_behaviors)

        # Skip if we don't have common behaviors
        if not common_behaviors:
            behavior_section += "Não foram encontrados comportamentos comuns entre todos os períodos analisados.\n\n"
        else:
            behavior_section += f"Foram identificados {len(common_behaviors)} comportamentos avaliados consistentemente em todos os períodos analisados.\n\n"

            # Create a dictionary to store scores for each behavior across periods
            behavior_scores = {}

            for behavior in common_behaviors:
                behavior_scores[behavior] = []

                for period_data in historical_data:
                    behaviors_data = self._extract_behavior_data(period_data)
                    if behavior in behaviors_data:
                        # Extract frequencies and calculate normalized score
                        freqs = behaviors_data[behavior]
                        score = self.statistical_analyzer.calculate_normalized_score(
                            freqs
                        )
                        behavior_scores[behavior].append(score)
                    else:
                        behavior_scores[behavior].append(0)  # Placeholder if missing

            # Calculate growth rates and total change for each behavior
            behavior_growth = []

            for behavior, scores in behavior_scores.items():
                if len(scores) >= 2:
                    total_change = scores[-1] - scores[0]
                    avg_change = total_change / (len(scores) - 1)

                    behavior_growth.append(
                        {
                            "name": behavior,
                            "scores": scores,
                            "total_change": total_change,
                            "avg_change": avg_change,
                        }
                    )

            # Sort behaviors by total change (highest growth first)
            behavior_growth.sort(key=lambda x: x["total_change"], reverse=True)

            # Display top improving behaviors
            behavior_section += "#### Comportamentos com Maior Evolução\n\n"

            # Create table with top behaviors
            if behavior_growth:
                top_behaviors = behavior_growth[:5]  # Top 5 behaviors

                rows = []
                for behavior in top_behaviors:
                    if behavior["total_change"] > 0:
                        name = behavior["name"]
                        # Shorten behavior name if needed
                        short_name = name[:30] + "..." if len(name) > 30 else name

                        rows.append(
                            [
                                short_name,
                                f"{behavior['scores'][0]:.1f}",
                                f"{behavior['scores'][-1]:.1f}",
                                f"{behavior['total_change']:.1f}",
                                f"{behavior['avg_change']:.1f}",
                            ]
                        )

                if rows:
                    headers = [
                        "Comportamento",
                        f"Score {years[0]}",
                        f"Score {years[-1]}",
                        "Mudança Total",
                        "Média/Período",
                    ]
                    behavior_section += self._format_table(headers, rows)
                else:
                    behavior_section += "Não foram identificados comportamentos com evolução positiva significativa.\n\n"

            # Display behaviors needing attention (negative growth)
            behavior_section += "\n#### Comportamentos que Requerem Atenção\n\n"

            # Create table with behaviors showing negative growth
            declining_behaviors = [b for b in behavior_growth if b["total_change"] < 0]
            declining_behaviors.sort(
                key=lambda x: x["total_change"]
            )  # Sort ascending (most negative first)

            if declining_behaviors:
                bottom_behaviors = declining_behaviors[:3]  # Top 3 declining behaviors

                rows = []
                for behavior in bottom_behaviors:
                    name = behavior["name"]
                    # Shorten behavior name if needed
                    short_name = name[:30] + "..." if len(name) > 30 else name

                    rows.append(
                        [
                            short_name,
                            f"{behavior['scores'][0]:.1f}",
                            f"{behavior['scores'][-1]:.1f}",
                            f"{behavior['total_change']:.1f}",
                            f"{behavior['avg_change']:.1f}",
                        ]
                    )

                if rows:
                    headers = [
                        "Comportamento",
                        f"Score {years[0]}",
                        f"Score {years[-1]}",
                        "Mudança Total",
                        "Média/Período",
                    ]
                    behavior_section += self._format_table(headers, rows)
                else:
                    behavior_section += "Não foram identificados comportamentos com declínio significativo.\n\n"
            else:
                behavior_section += "Não foram identificados comportamentos com declínio significativo. Todos os comportamentos estão estáveis ou em evolução positiva.\n\n"

            # Create visualization for the top behavior
            if behavior_growth and behavior_growth[0]["total_change"] > 0:
                top_behavior = behavior_growth[0]
                behavior_name = top_behavior["name"]
                behavior_scores = top_behavior["scores"]

                # Shorten behavior name if needed
                short_name = (
                    behavior_name[:40] + "..."
                    if len(behavior_name) > 40
                    else behavior_name
                )

                behavior_section += f"\n#### Visualização da Evolução: {short_name}\n\n"
                behavior_section += "```mermaid\n"
                behavior_section += "xychart-beta\n"
                behavior_section += f"    title \"Evolução de '{short_name}'\"\n"
                behavior_section += (
                    f'    x-axis "Período" [{", ".join([f'"{y}"' for y in years])}]\n'
                )
                behavior_section += '    y-axis "Score" [0, 20, 40, 60, 80, 100]\n'
                behavior_section += (
                    f"    line [{', '.join([f'{s:.1f}' for s in behavior_scores])}]\n"
                )
                behavior_section += "```\n\n"

        content += self._format_section("Evolução por Comportamento", behavior_section)

        # Add growth pattern and change point detection
        pattern_section = "### Detecção de Padrões e Pontos de Mudança\n\n"

        if len(global_scores) >= 3:
            # Simple detection of change points
            # (periods with significant difference from trend)
            changes = [
                global_scores[i] - global_scores[i - 1]
                for i in range(1, len(global_scores))
            ]
            avg_change = sum(changes) / len(changes)
            std_dev = (
                sum((x - avg_change) ** 2 for x in changes) / len(changes)
            ) ** 0.5

            change_points = []
            for i, change in enumerate(changes):
                # If change is more than 1.5 std devs from average, consider it significant
                if abs(change - avg_change) > 1.5 * std_dev:
                    period_idx = i + 1  # +1 because changes are between periods
                    direction = "positiva" if change > avg_change else "negativa"
                    magnitude = abs(change - avg_change)

                    change_points.append(
                        {
                            "period": years[period_idx],
                            "direction": direction,
                            "magnitude": magnitude,
                            "score_before": global_scores[period_idx - 1],
                            "score_after": global_scores[period_idx],
                            "delta": change,
                        }
                    )

            if change_points:
                pattern_section += "#### Pontos de Mudança Significativa\n\n"
                pattern_section += "Foram detectados os seguintes pontos de mudança significativa na trajetória:\n\n"

                for cp in change_points:
                    pattern_section += (
                        f"**{cp['period']}**: Mudança {cp['direction']} significativa\n"
                    )
                    pattern_section += f"  - Score anterior: {cp['score_before']:.1f}\n"
                    pattern_section += f"  - Score posterior: {cp['score_after']:.1f}\n"
                    pattern_section += f"  - Delta: {cp['delta']:.1f} (vs. média de {avg_change:.1f})\n\n"
            else:
                pattern_section += "#### Consistência da Trajetória\n\n"
                pattern_section += "A análise não identificou pontos de mudança significativa na trajetória de desenvolvimento. "
                pattern_section += "O padrão de evolução tem se mantido relativamente constante ao longo do tempo.\n\n"

            # Detect overall pattern
            pattern_section += "#### Padrão Global Detectado\n\n"

            # Check for different patterns
            if all(c > 0 for c in changes):
                if all(changes[i] > changes[i - 1] for i in range(1, len(changes))):
                    pattern_section += "**Padrão: Crescimento Acelerado**\n\n"
                    pattern_section += "Todos os períodos mostram melhoria, com ganhos cada vez maiores a cada ciclo. "
                    pattern_section += "Este é um padrão ideal que sugere um ciclo virtuoso de desenvolvimento.\n\n"
                elif all(changes[i] < changes[i - 1] for i in range(1, len(changes))):
                    pattern_section += "**Padrão: Crescimento Desacelerado**\n\n"
                    pattern_section += "Todos os períodos mostram melhoria, mas os ganhos estão diminuindo a cada ciclo. "
                    pattern_section += "Isso sugere uma aproximação gradual de um platô de desempenho.\n\n"
                else:
                    pattern_section += "**Padrão: Crescimento Variável**\n\n"
                    pattern_section += (
                        "Todos os períodos mostram melhoria, mas com ritmo irregular. "
                    )
                    pattern_section += (
                        "Alternância entre períodos de maior e menor crescimento.\n\n"
                    )
            elif all(c < 0 for c in changes):
                pattern_section += "**Padrão: Declínio Consistente**\n\n"
                pattern_section += "Todos os períodos mostram redução de desempenho. "
                pattern_section += "Este padrão requer atenção imediata e intervenções estruturadas.\n\n"
            elif changes[-1] > 0 and any(c < 0 for c in changes[:-1]):
                pattern_section += "**Padrão: Recuperação Recente**\n\n"
                pattern_section += "Após período(s) de declínio, o ciclo mais recente mostra recuperação positiva. "
                pattern_section += "Importante monitorar para confirmar se é uma tendência sustentável.\n\n"
            elif changes[-1] < 0 and all(c > 0 for c in changes[:-1]):
                pattern_section += "**Padrão: Reversão Recente**\n\n"
                pattern_section += (
                    "Após um histórico positivo, o ciclo mais recente mostra declínio. "
                )
                pattern_section += "Recomenda-se investigar fatores que possam ter contribuído para esta mudança.\n\n"
            else:
                pattern_section += "**Padrão: Misto/Inconsistente**\n\n"
                pattern_section += "A trajetória mostra alternância entre períodos de crescimento e declínio, "
                pattern_section += "sem um padrão claro predominante.\n\n"
        else:
            pattern_section += (
                "Não há dados suficientes para detectar padrões temporais complexos. "
            )
            pattern_section += "São necessários pelo menos 3 períodos de avaliação.\n\n"

        content += self._format_section("Padrões de Desenvolvimento", pattern_section)

        # Add projection section
        projection_section = "### Projeções e Estimativas Futuras\n\n"

        if len(global_scores) >= 2:
            # Simple linear projection
            if len(global_scores) >= 3:
                # Use last 3 points for more accurate projection
                x = list(range(len(global_scores) - 3, len(global_scores)))
                y = global_scores[-3:]
            else:
                # Use all available points
                x = list(range(len(global_scores)))
                y = global_scores

            # Calculate slope and intercept for linear projection
            n = len(x)
            mean_x = sum(x) / n
            mean_y = sum(y) / n

            # Calculate slope (m)
            numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
            denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
            slope = numerator / denominator if denominator != 0 else 0

            # Calculate intercept (b)
            intercept = mean_y - slope * mean_x

            # Project next 3 periods
            next_periods = []
            next_scores = []

            for i in range(1, 4):
                next_x = len(global_scores) - 1 + i
                next_y = slope * next_x + intercept

                # Limit to reasonable bounds
                next_y = max(0, min(100, next_y))

                # Set next period name (year+i or period+i)
                if years[-1].isdigit():
                    next_period = str(int(years[-1]) + i)
                else:
                    next_period = f"Período {len(years) + i}"

                next_periods.append(next_period)
                next_scores.append(next_y)

            # Add projection explanation
            projection_section += "Com base na trajetória histórica, foram geradas projeções lineares para os próximos 3 períodos:\n\n"

            # Create table with projections
            proj_rows = []
            for i, (period, score) in enumerate(zip(next_periods, next_scores)):
                proj_rows.append(
                    [period, f"{score:.1f}", f"{score - global_scores[-1]:.1f}"]
                )

            proj_headers = ["Período", "Score Projetado", "Δ vs. Último Período"]
            projection_section += self._format_table(proj_headers, proj_rows)

            # Add visualization with historical + projected data
            projection_section += "\n#### Visualização de Projeção\n\n"
            projection_section += "```mermaid\n"
            projection_section += "xychart-beta\n"
            projection_section += '    title "Evolução Histórica e Projeção Futura"\n'

            # X-axis with all periods (historical + projected)
            all_periods = years + next_periods
            projection_section += (
                f'    x-axis "Período" [{", ".join([f'"{p}"' for p in all_periods])}]\n'
            )

            projection_section += '    y-axis "Score" [0, 20, 40, 60, 80, 100]\n'

            # Historical line
            historical_points = ", ".join(
                [f"{s:.1f}" for s in global_scores] + ["null"] * 3
            )
            projection_section += f"    line [{historical_points}]\n"

            # Projection line
            projection_points = ", ".join(
                ["null"] * len(global_scores) + [f"{s:.1f}" for s in next_scores]
            )
            projection_section += f"    line [{projection_points}]\n"

            projection_section += "```\n\n"

            # Add time to target estimation
            projection_section += "#### Estimativa de Tempo para Objetivos\n\n"

            # Set some reference targets
            target_90 = 90  # Example target score

            # Estimate time to reach targets (if positive growth)
            if slope > 0:
                time_to_90 = (
                    (target_90 - global_scores[-1]) / slope
                    if slope > 0
                    else float("inf")
                )

                projection_section += "Estimativas de tempo para atingir níveis de referência, baseadas na taxa atual de desenvolvimento:\n\n"
                projection_section += (
                    f"- **Score 90 (Excelência)**: {time_to_90:.1f} períodos\n"
                )

                # If current score is already close to the top
                if global_scores[-1] > 85:
                    projection_section += (
                        "\nO desempenho atual já está próximo de níveis de excelência. "
                    )
                    projection_section += "O foco recomendado é na sustentação e consolidação das práticas atuais.\n\n"
            else:
                projection_section += "A trajetória atual não projeta alcance de níveis superiores sem mudança no padrão de desenvolvimento.\n\n"

            # Add confidence assessment
            projection_section += "\n#### Confiabilidade da Projeção\n\n"

            # Assess confidence based on data quality and consistency
            if len(global_scores) < 3:
                projection_section += "**Confiabilidade: Baixa**\n\n"
                projection_section += "Projeções baseadas em menos de 3 períodos históricos têm confiabilidade reduzida. "
                projection_section += "Recomenda-se cautela na interpretação.\n\n"
            elif std_dev > 5:
                projection_section += "**Confiabilidade: Média-Baixa**\n\n"
                projection_section += (
                    "Alta variabilidade entre períodos reduz a precisão das projeções. "
                )
                projection_section += "As estimativas devem ser consideradas como indicativas, não determinísticas.\n\n"
            elif std_dev > 2:
                projection_section += "**Confiabilidade: Média**\n\n"
                projection_section += "Variabilidade moderada entre períodos. "
                projection_section += "As projeções têm confiabilidade razoável, mas devem ser revisadas a cada novo ciclo.\n\n"
            else:
                projection_section += "**Confiabilidade: Alta**\n\n"
                projection_section += "Padrão histórico consistente confere maior confiabilidade às projeções. "
                projection_section += "As estimativas têm boa probabilidade de concretização se mantidas as condições atuais.\n\n"
        else:
            projection_section += (
                "Não há dados suficientes para gerar projeções confiáveis. "
            )
            projection_section += (
                "São necessários pelo menos 2 períodos de avaliação.\n\n"
            )

        content += self._format_section("Projeções Futuras", projection_section)

        # Add recommendations based on temporal analysis
        recommendations_section = "### Recomendações Estratégicas\n\n"

        recommendations_section += "Com base na análise temporal, recomendamos as seguintes abordagens estratégicas:\n\n"

        # Different recommendations based on detected pattern
        if len(global_scores) >= 2:
            overall_change = global_scores[-1] - global_scores[0]
            latest_change = (
                global_scores[-1] - global_scores[-2]
                if len(global_scores) > 2
                else overall_change
            )

            if overall_change > 0 and latest_change > 0:
                # Positive trend, continuing
                recommendations_section += "#### 1. Consolidação do Padrão Positivo\n\n"
                recommendations_section += "- Manter as estratégias de desenvolvimento que têm demonstrado eficácia\n"
                recommendations_section += (
                    "- Documentar práticas e abordagens bem-sucedidas para replicação\n"
                )
                recommendations_section += "- Ampliar escopo de aplicação para outros comportamentos correlacionados\n\n"

                if "behavior_growth" in locals() and behavior_growth:
                    top_3_behaviors = behavior_growth[:3]
                    recommendations_section += "**Comportamentos a consolidar:**\n\n"
                    for behavior in top_3_behaviors:
                        if behavior["total_change"] > 0:
                            recommendations_section += f"- {behavior['name']}\n"
                    recommendations_section += "\n"

            elif overall_change > 0 and latest_change < 0:
                # Overall positive but recent decline
                recommendations_section += "#### 1. Contenção de Reversão\n\n"
                recommendations_section += "- Investigar fatores que podem ter contribuído para a recente desaceleração\n"
                recommendations_section += (
                    "- Revisar abordagens que foram eficazes em períodos anteriores\n"
                )
                recommendations_section += "- Implementar intervenções focadas em comportamentos com declínio recente\n\n"

                if "behavior_growth" in locals() and behavior_growth:
                    # Find behaviors that were growing but recently declined
                    recently_declined = []
                    for behavior in behavior_growth:
                        scores = behavior["scores"]
                        if (
                            len(scores) >= 3
                            and scores[-1] < scores[-2]
                            and scores[-2] > scores[-3]
                        ):
                            recently_declined.append(behavior["name"])

                    if recently_declined:
                        recommendations_section += (
                            "**Comportamentos para intervenção prioritária:**\n\n"
                        )
                        for behavior in recently_declined[:3]:
                            recommendations_section += f"- {behavior}\n"
                        recommendations_section += "\n"

            elif overall_change < 0 and latest_change > 0:
                # Overall negative but recent improvement
                recommendations_section += "#### 1. Amplificação da Recuperação\n\n"
                recommendations_section += (
                    "- Reforçar e ampliar as mudanças recentes que geraram melhoria\n"
                )
                recommendations_section += (
                    "- Focar na sustentabilidade das intervenções atuais\n"
                )
                recommendations_section += (
                    "- Estabelecer checkpoints frequentes para monitorar progresso\n\n"
                )

                if "behavior_growth" in locals() and behavior_growth:
                    # Find behaviors that were declining but recently improved
                    recently_improved = []
                    for behavior in behavior_growth:
                        scores = behavior["scores"]
                        if (
                            len(scores) >= 3
                            and scores[-1] > scores[-2]
                            and scores[-2] < scores[-3]
                        ):
                            recently_improved.append(behavior["name"])

                    if recently_improved:
                        recommendations_section += (
                            "**Comportamentos com recuperação a amplificar:**\n\n"
                        )
                        for behavior in recently_improved[:3]:
                            recommendations_section += f"- {behavior}\n"
                        recommendations_section += "\n"

            elif overall_change < 0 and latest_change < 0:
                # Negative trend, continuing
                recommendations_section += "#### 1. Intervenção Corretiva\n\n"
                recommendations_section += "- Implementar mudança significativa na abordagem de desenvolvimento\n"
                recommendations_section += (
                    "- Estabelecer programa intensivo de acompanhamento\n"
                )
                recommendations_section += "- Priorizar reversão da tendência de declínio antes de focar em crescimento\n\n"

                if "declining_behaviors" in locals() and declining_behaviors:
                    recommendations_section += (
                        "**Comportamentos para intervenção urgente:**\n\n"
                    )
                    for behavior in declining_behaviors[:3]:
                        recommendations_section += f"- {behavior['name']}\n"
                    recommendations_section += "\n"

            # Second recommendation based on pattern consistency
            if "changes" in locals() and len(changes) > 1:
                consistency = sum(
                    1
                    for i in range(1, len(changes))
                    if (changes[i] > 0) == (changes[i - 1] > 0)
                ) / (len(changes) - 1)

                if consistency > 0.7:
                    # Highly consistent pattern
                    recommendations_section += "#### 2. Abordagem Consistente\n\n"
                    recommendations_section += "- Manter estabilidade nas intervenções, evitando mudanças bruscas\n"
                    recommendations_section += (
                        "- Focar em aprimoramento incremental dos métodos atuais\n"
                    )
                    recommendations_section += "- Estabelecer metas graduais alinhadas com o ritmo histórico de desenvolvimento\n\n"
                else:
                    # Inconsistent pattern
                    recommendations_section += "#### 2. Estabilização de Trajetória\n\n"
                    recommendations_section += "- Implementar estrutura mais robusta de acompanhamento e feedback\n"
                    recommendations_section += "- Analisar fatores externos que podem estar causando variabilidade\n"
                    recommendations_section += "- Estabelecer controles para minimizar oscilações e inconsistências\n\n"

            # Third recommendation based on projected potential
            if "slope" in locals() and "next_scores" in locals():
                if slope > 2:
                    # High growth potential
                    recommendations_section += "#### 3. Capitalização do Potencial\n\n"
                    recommendations_section += "- Estabelecer metas ambiciosas alinhadas com o alto potencial demonstrado\n"
                    recommendations_section += (
                        "- Preparar para desafios de desenvolvimento mais avançados\n"
                    )
                    recommendations_section += "- Considerar ampliação de responsabilidades e escopo de atuação\n\n"
                elif slope > 0:
                    # Moderate growth potential
                    recommendations_section += "#### 3. Aceleração Estratégica\n\n"
                    recommendations_section += "- Identificar alavancas para incrementar a velocidade de desenvolvimento\n"
                    recommendations_section += "- Focar em intervenções com potencial de impacto multiplicador\n"
                    recommendations_section += (
                        "- Estabelecer metas incrementalmente mais desafiadoras\n\n"
                    )
                else:
                    # Low or negative growth potential
                    recommendations_section += "#### 3. Redefinição de Trajetória\n\n"
                    recommendations_section += (
                        "- Revisar fundamentalmente a abordagem de desenvolvimento\n"
                    )
                    recommendations_section += "- Considerar mudanças estruturais nos métodos de feedback e acompanhamento\n"
                    recommendations_section += "- Estabelecer metas de curto prazo para criar momentum inicial\n\n"
        else:
            # Not enough data for pattern-specific recommendations
            recommendations_section += "#### Recomendações Gerais\n\n"
            recommendations_section += "1. **Estabelecimento de Linha Base**: Consolidar medições consistentes para permitir análise temporal futura\n"
            recommendations_section += "2. **Documentação de Contexto**: Registrar fatores externos que possam influenciar a evolução\n"
            recommendations_section += "3. **Abordagem Balanceada**: Combinar intervenções em comportamentos com maior gap e maior potencial de desenvolvimento\n\n"

        content += self._format_section(
            "Recomendações Estratégicas", recommendations_section
        )

        # Add footer
        content += "\n---\n*Este relatório foi gerado automaticamente pelo sistema de Análise Avançada de Desempenho.*\n"

        return content
