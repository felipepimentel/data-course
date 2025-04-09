import argparse
import base64
from datetime import datetime
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# Import the analyzer class and constants
from analyze_evaluations import EvaluationAnalyzer
from constants import (
    ACTION_PLAN_TEMPLATE,
    ANNOTATION_BOX_STYLE,
    BEHAVIOR_RECOMMENDATIONS,
    CAREER_INSIGHTS,
    CHART_COLORS,
    CHART_CONFIG,
    CONCEPT_CHART_COLORS,
    PERFORMANCE_DESCRIPTORS,
    RADAR_CHART_STYLE,
    TIMELINE_COLOR_MAP,
    TREND_DESCRIPTORS,
)


class FeedbackGenerator:
    def __init__(self, base_path, person, output_dir=None):
        self.base_path = Path(base_path)
        self.person = person
        self.output_dir = Path(output_dir) if output_dir else Path("feedback_reports")

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize the analyzer
        self.analyzer = EvaluationAnalyzer(base_path)

        # Get the person's data
        self.data = self.analyzer.person_year_over_year(person)

        # For storing generated images
        self.images = {}

    def generate_feedback_report(self):
        """Generate a complete feedback report for the person"""
        # Check if we have data for this person
        if not self.data or not self.data["Years"]:
            print(f"No data found for {self.person}")
            return None

        # Generate all charts first
        self.generate_charts()

        # Build the markdown
        md = []
        md.append(self.generate_header())
        md.append(self.generate_executive_summary())
        md.append(self.generate_performance_timeline())
        md.append(self.generate_year_by_year_analysis())
        md.append(self.generate_strengths_improvements())
        md.append(self.generate_peer_comparison())

        # Write to file
        output_file = self.output_dir / f"{self.person.replace(' ', '_')}_feedback.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n\n".join(md))

        print(f"Generated feedback report for {self.person} at {output_file}")
        return output_file

    def generate_charts(self):
        """Generate all the charts needed for the report"""
        # Get a high-resolution historical chart
        fig = plt.figure(figsize=CHART_CONFIG["figsize"]["historical"])
        years = self.data["Years"]
        person_scores = [self.data["Person Scores"].get(year, 0) for year in years]
        group_scores = [self.data["Group Scores"].get(year, 0) for year in years]

        plt.plot(
            years,
            person_scores,
            marker="o",
            linestyle="-",
            linewidth=CHART_CONFIG["linewidth"]["primary"],
            markersize=CHART_CONFIG["markersize"]["primary"],
            label=f"{self.person}",
            color=CHART_COLORS["primary"],
        )
        plt.plot(
            years,
            group_scores,
            marker="s",
            linestyle="--",
            linewidth=CHART_CONFIG["linewidth"]["secondary"],
            markersize=CHART_CONFIG["markersize"]["secondary"],
            label="Grupo",
            color=CHART_COLORS["secondary"],
        )

        for i, year in enumerate(years):
            concept = self.data["Concepts"].get(year, "")
            color = CONCEPT_CHART_COLORS.get(concept, CONCEPT_CHART_COLORS["default"])

            plt.scatter(year, person_scores[i], color=color, s=150, zorder=10)
            plt.annotate(
                concept,
                (year, person_scores[i]),
                textcoords="offset points",
                xytext=(0, 15),
                ha="center",
                fontsize=CHART_CONFIG["fontsize"]["annotation"],
                bbox=ANNOTATION_BOX_STYLE,
            )

        plt.grid(True, linestyle="--", alpha=CHART_CONFIG["alpha"]["grid"])
        plt.title(
            f"Evolução de Desempenho - {self.person}",
            fontsize=CHART_CONFIG["fontsize"]["title"],
            pad=20,
        )
        plt.xlabel("Ano", fontsize=CHART_CONFIG["fontsize"]["axis_label"])
        plt.ylabel("Pontuação", fontsize=CHART_CONFIG["fontsize"]["axis_label"])
        plt.legend(fontsize=CHART_CONFIG["fontsize"]["legend"])

        # Make sure y axis starts from a reasonable value
        ymin, ymax = plt.ylim()
        plt.ylim(max(0, ymin - 0.5), ymax + 0.5)

        # Add horizontal lines for reference
        plt.axhline(
            y=CHART_CONFIG["reference"]["average_score"],
            color="gray",
            linestyle="-",
            alpha=CHART_CONFIG["alpha"]["reference_line"],
        )
        plt.text(
            years[0],
            CHART_CONFIG["reference"]["average_score"],
            "Média de Referência",
            verticalalignment="bottom",
            horizontalalignment="left",
            color="gray",
            fontsize=CHART_CONFIG["fontsize"]["tick"],
        )

        plt.tight_layout()

        # Save to BytesIO
        img_data = BytesIO()
        plt.savefig(img_data, format="png", dpi=150)
        img_data.seek(0)
        self.images["historical_chart"] = base64.b64encode(img_data.read()).decode(
            "utf-8"
        )
        plt.close()

        # Generate category comparison chart
        fig = plt.figure(figsize=CHART_CONFIG["figsize"]["category"])

        # Select important categories
        categories = [
            "observo raramente",
            "observo na maior parte das vezes",
            "observo sempre",
            "referencia",
        ]
        cat_diffs = self.data["Category Differences"]

        # Plot each category as a line
        for category in categories:
            values = [cat_diffs[year][category] for year in years]
            plt.plot(years, values, marker="o", label=category)

        plt.axhline(
            y=0, color="r", linestyle="-", alpha=CHART_CONFIG["alpha"]["reference_line"]
        )
        plt.grid(True, linestyle="--", alpha=CHART_CONFIG["alpha"]["grid"])
        plt.title(
            f"Evolução das Categorias de Avaliação - {self.person}",
            fontsize=CHART_CONFIG["fontsize"]["title"],
        )
        plt.xlabel("Ano", fontsize=CHART_CONFIG["fontsize"]["axis_label"])
        plt.ylabel(
            "Diferença do Grupo (%)", fontsize=CHART_CONFIG["fontsize"]["axis_label"]
        )
        plt.legend(fontsize=CHART_CONFIG["fontsize"]["legend"])
        plt.tight_layout()

        # Save to BytesIO
        img_data = BytesIO()
        plt.savefig(img_data, format="png", dpi=150)
        img_data.seek(0)
        self.images["category_chart"] = base64.b64encode(img_data.read()).decode(
            "utf-8"
        )
        plt.close()

        # Generate radar chart for the latest year (if available)
        if years:
            latest_year = max(years)
            self.generate_radar_chart(latest_year)

            # Also generate radar for previous year if available
            if len(years) > 1:
                prev_year = sorted(years)[-2]
                self.generate_radar_chart(prev_year)

    def generate_radar_chart(self, year):
        """Generate a radar chart for a specific year"""
        behavior_scores = self.analyzer.get_behavior_scores(self.person, year)

        if not behavior_scores:
            return

        # Extract direcionador names and average scores
        direcionadores = []
        person_scores = []
        group_scores = []

        for dir_name, behaviors in behavior_scores.items():
            dir_scores_person = []
            dir_scores_group = []

            for comp_name, details in behaviors.items():
                for avaliador, scores in details["scores"].items():
                    if avaliador == "%todos":  # Use the overall evaluation
                        dir_scores_person.append(scores["score_colaborador"])
                        dir_scores_group.append(scores["score_grupo"])

            if dir_scores_person and dir_scores_group:
                direcionadores.append(dir_name.split(".")[0])  # Just use the number
                person_scores.append(sum(dir_scores_person) / len(dir_scores_person))
                group_scores.append(sum(dir_scores_group) / len(dir_scores_group))

        if not direcionadores:
            return

        # Create the radar chart
        fig = plt.figure(figsize=CHART_CONFIG["figsize"]["radar"])
        ax = fig.add_subplot(111, polar=True)

        # Number of categories
        N = len(direcionadores)

        # Angle of each axis
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Close the loop

        # Add the first point again to close the circle
        person_scores += person_scores[:1]
        group_scores += group_scores[:1]

        # Plot the person scores
        ax.plot(
            angles,
            person_scores,
            linewidth=CHART_CONFIG["linewidth"]["primary"],
            linestyle="solid",
            label=f"{self.person}",
            color=RADAR_CHART_STYLE["primary_color"],
        )
        ax.fill(
            angles,
            person_scores,
            alpha=RADAR_CHART_STYLE["primary_alpha"],
            color=RADAR_CHART_STYLE["primary_color"],
        )

        # Plot the group scores
        ax.plot(
            angles,
            group_scores,
            linewidth=CHART_CONFIG["linewidth"]["secondary"],
            linestyle="--",
            label="Grupo",
            color=RADAR_CHART_STYLE["secondary_color"],
        )
        ax.fill(
            angles,
            group_scores,
            alpha=RADAR_CHART_STYLE["secondary_alpha"],
            color=RADAR_CHART_STYLE["secondary_color"],
        )

        # Set category labels
        plt.xticks(angles[:-1], direcionadores, fontsize=RADAR_CHART_STYLE["fontsize"])

        # Draw y-labels (scores)
        ax.set_rlabel_position(0)
        max_score = max(max(person_scores), max(group_scores))
        plt.yticks(
            [1, 2, 3, 4],
            ["1", "2", "3", "4"],
            color=RADAR_CHART_STYLE["tick_color"],
            size=RADAR_CHART_STYLE["tick_size"],
        )
        plt.ylim(0, max_score + 0.5)

        # Add title and legend
        plt.title(
            f"Desempenho por Direcionador - {year}",
            size=CHART_CONFIG["fontsize"]["title"],
            pad=20,
        )
        plt.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))

        # Save to BytesIO
        img_data = BytesIO()
        plt.savefig(img_data, format="png", dpi=150)
        img_data.seek(0)
        self.images[f"radar_chart_{year}"] = base64.b64encode(img_data.read()).decode(
            "utf-8"
        )
        plt.close()

    def generate_header(self):
        """Generate the header section"""
        concept = self.get_latest_concept()

        header = f"""# Avaliação de Desempenho - {self.person}

**Relatório Gerado:** {datetime.now().strftime("%d/%m/%Y")}  
**Conceito Atual:** {concept}  
**Anos Avaliados:** {", ".join(self.data["Years"])}
"""
        return header

    def generate_executive_summary(self):
        """Generate an executive summary"""
        years = self.data["Years"]
        if not years:
            return "## Resumo Executivo\n\nNão há dados suficientes para análise."

        # Calculate the average trend
        person_scores = [self.data["Person Scores"].get(year, 0) for year in years]
        group_scores = [self.data["Group Scores"].get(year, 0) for year in years]

        # Calculate trend
        trend = TREND_DESCRIPTORS["stable"]["description"]
        if len(years) > 1:
            first_year_diff = person_scores[0] - group_scores[0]
            last_year_diff = person_scores[-1] - group_scores[-1]
            trend_diff = last_year_diff - first_year_diff

            if trend_diff > TREND_DESCRIPTORS["significant_up"]["threshold"]:
                trend = TREND_DESCRIPTORS["significant_up"]["description"]
            elif trend_diff > TREND_DESCRIPTORS["up"]["threshold"]:
                trend = TREND_DESCRIPTORS["up"]["description"]
            elif trend_diff < TREND_DESCRIPTORS["significant_down"]["threshold"]:
                trend = TREND_DESCRIPTORS["significant_down"]["description"]
            elif trend_diff < TREND_DESCRIPTORS["down"]["threshold"]:
                trend = TREND_DESCRIPTORS["down"]["description"]

        # Get latest concept and score
        latest_year = max(years)
        latest_concept = self.data["Concepts"].get(latest_year, "")
        latest_score = self.data["Person Scores"].get(latest_year, 0)
        latest_group = self.data["Group Scores"].get(latest_year, 0)

        # Performance descriptors based on latest scores
        performance_desc = PERFORMANCE_DESCRIPTORS["average"]["description"]
        diff = latest_score - latest_group

        if diff > PERFORMANCE_DESCRIPTORS["very_high"]["threshold"]:
            performance_desc = PERFORMANCE_DESCRIPTORS["very_high"]["description"]
        elif diff > PERFORMANCE_DESCRIPTORS["high"]["threshold"]:
            performance_desc = PERFORMANCE_DESCRIPTORS["high"]["description"]
        elif diff < PERFORMANCE_DESCRIPTORS["very_low"]["threshold"]:
            performance_desc = PERFORMANCE_DESCRIPTORS["very_low"]["description"]
        elif diff < PERFORMANCE_DESCRIPTORS["low"]["threshold"]:
            performance_desc = PERFORMANCE_DESCRIPTORS["low"]["description"]

        # Get latest comments
        latest_comments = self.get_comments_for_year(latest_year)
        gestor_comment = latest_comments.get("gestor", "")
        par_comment = latest_comments.get("par/parceiro", "")

        summary = f"""## Resumo Executivo

{self.person} apresenta uma trajetória **{trend}** nos últimos {len(years)} anos, com desempenho atual **{performance_desc}**. 

No ano mais recente ({latest_year}), obteve o conceito "**{latest_concept}**" com uma pontuação de **{latest_score:.2f}** (média do grupo: {latest_group:.2f}).

### Feedback do Gestor
> {gestor_comment}

### Feedback dos Pares
> {par_comment}

![Evolução do Desempenho](data:image/png;base64,{self.images["historical_chart"]})
"""
        return summary

    def generate_performance_timeline(self):
        """Generate a performance timeline using Mermaid"""
        years = self.data["Years"]
        if not years:
            return ""

        # Map concepts to colors
        color_map = TIMELINE_COLOR_MAP

        # Create timeline nodes for each year
        timeline = """## Trajetória de Desempenho

```mermaid
timeline
"""

        for year in sorted(years):
            concept = self.data["Concepts"].get(year, "")
            person_score = self.data["Person Scores"].get(year, 0)
            group_score = self.data["Group Scores"].get(year, 0)
            diff = person_score - group_score

            color = color_map.get(concept, "rgb(128,128,128)")

            timeline += f"    title {year} : {concept}\n"
            timeline += f"      Pontuação: {person_score:.2f} (diff: {diff:+.2f})\n"

        timeline += "```"
        return timeline

    def generate_year_by_year_analysis(self):
        """Generate detailed year-by-year analysis"""
        years = sorted(self.data["Years"])
        if not years:
            return ""

        # Start the section
        section = "## Análise Anual Detalhada\n\n"

        for year in years:
            concept = self.data["Concepts"].get(year, "")
            person_score = self.data["Person Scores"].get(year, 0)
            group_score = self.data["Group Scores"].get(year, 0)
            diff = person_score - group_score

            # Get detailed behavior scores for this year
            behavior_scores = self.analyzer.get_behavior_scores(self.person, year)

            # Get comments
            comments = self.get_comments_for_year(year)
            gestor_comment = comments.get("gestor", "")
            par_comment = comments.get("par/parceiro", "")

            # Create the year subsection
            section += f"### {year} - {concept}\n\n"
            section += f"**Pontuação:** {person_score:.2f} (média do grupo: {group_score:.2f}, diferença: {diff:+.2f})\n\n"

            # Add radar chart if available
            if f"radar_chart_{year}" in self.images:
                section += f"![Desempenho por Direcionador em {year}](data:image/png;base64,{self.images[f'radar_chart_{year}']})\n\n"

            # Add detailed scores by direcionador
            section += "#### Desempenho por Direcionador\n\n"

            score_table = "| Direcionador | Comportamento | Pontuação | Média do Grupo | Diferença |\n"
            score_table += "| --- | --- | ---: | ---: | ---: |\n"

            for dir_name, behaviors in behavior_scores.items():
                dir_first_row = True
                for comp_name, details in behaviors.items():
                    for avaliador, scores in details["scores"].items():
                        if avaliador == "%todos":  # Use the overall evaluation
                            person_comp_score = scores["score_colaborador"]
                            group_comp_score = scores["score_grupo"]
                            comp_diff = person_comp_score - group_comp_score

                            dir_display = dir_name if dir_first_row else ""
                            score_table += f"| {dir_display} | {comp_name} | {person_comp_score:.2f} | {group_comp_score:.2f} | {comp_diff:+.2f} |\n"
                            dir_first_row = False

            section += score_table + "\n"

            # Add feedback
            section += "#### Feedback\n\n"
            section += f"**Gestor:**\n> {gestor_comment}\n\n"
            section += f"**Pares/Parceiros:**\n> {par_comment}\n\n"

            # Add horizontal rule between years except for the last one
            if year != years[-1]:
                section += "---\n\n"

        return section

    def generate_strengths_improvements(self):
        """Generate strengths and improvement opportunities section"""
        years = self.data["Years"]
        if not years:
            return ""

        latest_year = max(years)
        behavior_scores = self.analyzer.get_behavior_scores(self.person, latest_year)

        if not behavior_scores:
            return ""

        # Calculate average score for each behavior
        behavior_data = []

        for dir_name, behaviors in behavior_scores.items():
            for comp_name, details in behaviors.items():
                for avaliador, scores in details["scores"].items():
                    if avaliador == "%todos":  # Use the overall evaluation
                        person_score = scores["score_colaborador"]
                        group_score = scores["score_grupo"]
                        diff = person_score - group_score

                        behavior_data.append({
                            "direcionador": dir_name,
                            "comportamento": comp_name,
                            "score": person_score,
                            "group_score": group_score,
                            "diff": diff,
                        })

        # Sort by difference (high to low) for strengths
        strengths = sorted(behavior_data, key=lambda x: x["diff"], reverse=True)[:3]

        # Sort by difference (low to high) for improvements
        improvements = sorted(behavior_data, key=lambda x: x["diff"])[:3]

        section = "## Pontos Fortes e Oportunidades de Desenvolvimento\n\n"

        # Add strengths
        section += "### Principais Pontos Fortes\n"
        for strength in strengths:
            section += (
                f"- **{strength['comportamento']}** ({strength['direcionador']})\n"
            )
            section += f"  - Pontuação: {strength['score']:.2f} (média do grupo: {strength['group_score']:.2f}, diferença: {strength['diff']:+.2f})\n"

        # Add improvement opportunities
        section += "\n### Principais Oportunidades de Desenvolvimento\n"
        for improvement in improvements:
            section += f"- **{improvement['comportamento']}** ({improvement['direcionador']})\n"
            section += f"  - Pontuação: {improvement['score']:.2f} (média do grupo: {improvement['group_score']:.2f}, diferença: {improvement['diff']:+.2f})\n"

            # Add specific recommendations based on the behavior
            comportamento_key = improvement["comportamento"]
            if comportamento_key in BEHAVIOR_RECOMMENDATIONS:
                recommendations = BEHAVIOR_RECOMMENDATIONS[comportamento_key]
                section += f"  - **Recomendação**: {recommendations[0]}\n"

        section += "\n![Evolução por Categoria](data:image/png;base64,{})".format(
            self.images["category_chart"]
        )

        # Add an action plan section
        section += "\n\n## Plano de Ação Sugerido\n\n"
        section += ACTION_PLAN_TEMPLATE

        return section

    def generate_peer_comparison(self):
        """Generate peer comparison for the latest year"""
        years = self.data["Years"]
        if not years:
            return ""

        latest_year = max(years)

        # Get comparative data for the latest year
        comparative_data = self.analyzer.compare_people_for_year(latest_year)

        if comparative_data.empty:
            return ""

        # Find the person's rank
        comparative_data_sorted = comparative_data.sort_values(
            "Average Score", ascending=False
        )
        person_idx = comparative_data_sorted.index[
            comparative_data_sorted["Person"] == self.person
        ].tolist()

        if not person_idx:
            return ""

        person_rank = person_idx[0] + 1  # +1 because index is 0-based
        total_people = len(comparative_data_sorted)

        # Create the percentile text
        percentile = 100 - (person_rank / total_people * 100)
        percentile_text = f"{percentile:.0f}º"

        # Get the person's row
        person_row = comparative_data_sorted.iloc[person_idx[0]]

        section = f"""## Comparação com o Grupo ({latest_year})

Em {latest_year}, {self.person} ficou na posição **{person_rank}º de {total_people}** avaliados (percentil {percentile_text}).

### Posicionamento no Grupo

```mermaid
xychart-beta
    title "Pontuações em {latest_year}"
    x-axis "{", ".join(comparative_data_sorted["Person"].tolist())}"
    y-axis "Pontuação" 0 --> 5
    bar {", ".join([str(round(score, 2)) for score in comparative_data_sorted["Average Score"].tolist()])}
    line {", ".join([str(round(score, 2)) for score in comparative_data_sorted["Group Average"].tolist()])}
```

### Destaque nas Categorias

Em relação ao grupo, {self.person} se destaca nas seguintes categorias:

"""

        # Get the category differences
        category_diffs = {}
        for col in comparative_data.columns:
            if col.startswith("Diff "):
                category = col[5:]  # Remove "Diff " prefix
                category_diffs[category] = person_row[col]

        # Sort categories by absolute difference
        sorted_categories = sorted(
            category_diffs.items(), key=lambda x: abs(x[1]), reverse=True
        )

        # Show the top 3 categories (highest absolute difference)
        for category, diff in sorted_categories[:3]:
            direction = "acima" if diff > 0 else "abaixo"
            section += (
                f"- **{category}**: {abs(diff):.1f}% {direction} da média do grupo\n"
            )

        # Add a new section for career insights
        section += "\n### Insights para Carreira\n\n"

        # Use career insights from constants
        if percentile >= 75:
            for insight in CAREER_INSIGHTS["high"]:
                section += insight + "\n"
        elif percentile >= 50:
            for insight in CAREER_INSIGHTS["medium"]:
                section += insight + "\n"
        else:
            for insight in CAREER_INSIGHTS["low"]:
                section += insight + "\n"

        return section

    def get_latest_concept(self):
        """Get the concept from the latest year"""
        years = self.data["Years"]
        if not years:
            return "Sem avaliação"

        latest_year = max(years)
        return self.data["Concepts"].get(latest_year, "Sem avaliação")

    def get_comments_for_year(self, year):
        """Get comments for a specific year"""
        comments = {}

        # Get the raw data for this person and year
        if (
            self.person in self.analyzer.evaluations_by_person
            and year in self.analyzer.evaluations_by_person[self.person]
        ):
            data = self.analyzer.evaluations_by_person[self.person][year]

            if data["success"] and "data" in data and "comentarios" in data["data"]:
                for comment in data["data"]["comentarios"]:
                    if "nome_fonte" in comment and "texto" in comment:
                        source = comment["nome_fonte"]
                        # Extract text from the comment - handle different formats
                        if isinstance(comment["texto"], dict):
                            if "comentario" in comment["texto"]:
                                text = comment["texto"]["comentario"]
                            else:
                                # Take the first value in the dict
                                text = next(iter(comment["texto"].values()), "")
                        else:
                            text = str(comment["texto"])

                        comments[source] = text

        return comments


def main():
    parser = argparse.ArgumentParser(
        description="Generate feedback reports in Markdown format"
    )
    parser.add_argument("base_path", help="Base path containing evaluation folders")
    parser.add_argument(
        "--person",
        help="Person to generate feedback for (if not specified, generates for all)",
    )
    parser.add_argument("--output-dir", help="Output directory for feedback reports")

    args = parser.parse_args()

    # Initialize the analyzer to get a list of all people
    analyzer = EvaluationAnalyzer(args.base_path)

    if args.person:
        # Generate feedback for specified person
        generator = FeedbackGenerator(args.base_path, args.person, args.output_dir)
        generator.generate_feedback_report()
    else:
        # Get all people with data
        all_years = set()
        for person, years in analyzer.evaluations_by_person.items():
            all_years.update(years.keys())

        if not all_years:
            print("No evaluation data found.")
            return

        latest_year = max(all_years)
        people = analyzer.get_all_people_for_year(latest_year)

        if not people:
            print(f"No people found with data for {latest_year}")
            return

        print(f"Generating feedback reports for {len(people)} people...")

        for person in people:
            generator = FeedbackGenerator(args.base_path, person, args.output_dir)
            generator.generate_feedback_report()

        print(f"Done! All reports saved to {args.output_dir or 'feedback_reports'}")


if __name__ == "__main__":
    main()
