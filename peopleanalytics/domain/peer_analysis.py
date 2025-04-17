"""
Peer group analysis functionality for People Analytics.

This module provides analysis functions to compare individual evaluation results
with peer group statistics and track performance over time.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional


class PeerGroupAnalysis:
    """
    Analyzes peer group comparisons and year-over-year performance trends.

    This class provides methods to compare an individual's performance against
    their peer group and to track performance changes over time.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the peer group analysis with optional configuration.

        Args:
            config: Configuration dictionary for analysis parameters
        """
        # Default configuration
        self.config = {
            # Skill category weights for weighted scoring
            "category_weights": {
                "technical": 1.0,
                "behavioral": 1.0,
                "leadership": 1.2,
                "soft_skills": 0.9,
                "domain_knowledge": 1.1,
                "default": 1.0,
            },
            # Performance thresholds for categorization
            "performance_thresholds": {
                "excellent": 9.0,
                "good": 7.0,
                "average": 5.0,
                "needs_improvement": 3.0,
            },
            # Year-over-year comparison settings
            "yoy_comparison": {
                "improvement_threshold": 0.5,  # Significant improvement
                "decline_threshold": -0.5,  # Significant decline
                "steady_range": [-0.2, 0.2],  # Considered steady performance
            },
        }

        # Update with user configuration if provided
        if config:
            self._update_config(config)

        self.logger = logging.getLogger(__name__)

    def _update_config(self, config: Dict[str, Any]) -> None:
        """Update configuration with user-provided values.

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

    def calculate_weighted_score(
        self, scores: Dict[str, float], categories: Dict[str, str] = None
    ) -> float:
        """Calculate a weighted score based on skill categories.

        Args:
            scores: Dictionary mapping skill names to scores
            categories: Dictionary mapping skill names to their categories

        Returns:
            Weighted average score
        """
        if not scores:
            return 0.0

        total_weight = 0.0
        weighted_sum = 0.0

        for skill, score in scores.items():
            # Get category for this skill
            category = "default"
            if categories and skill in categories:
                category = categories[skill]

            # Get weight for this category
            weight = self.config["category_weights"].get(
                category, self.config["category_weights"]["default"]
            )

            weighted_sum += score * weight
            total_weight += weight

        if total_weight > 0:
            return weighted_sum / total_weight
        return 0.0

    def compare_with_peer_group(
        self,
        person_scores: Dict[str, float],
        peer_scores: Dict[str, Dict[str, float]],
        categories: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        """Compare an individual's scores with peer group scores.

        Args:
            person_scores: Dictionary mapping skill names to scores for the individual
            peer_scores: Dictionary mapping person names to their skill scores
            categories: Dictionary mapping skill names to their categories

        Returns:
            Dictionary with comparison results
        """
        results = {
            "overall": {
                "person_score": 0.0,
                "peer_avg": 0.0,
                "difference": 0.0,
                "percentile": 0.0,
            },
            "by_skill": {},
            "by_category": {},
            "strengths": [],
            "gaps": [],
        }

        # Calculate person's weighted score
        person_weighted = self.calculate_weighted_score(person_scores, categories)
        results["overall"]["person_score"] = person_weighted

        # Calculate peer group scores
        peer_weighted_scores = []
        all_skills = set(person_scores.keys())
        all_categories = set()

        # Collect all skills and calculate peer weighted scores
        for peer, scores in peer_scores.items():
            peer_weighted = self.calculate_weighted_score(scores, categories)
            peer_weighted_scores.append(peer_weighted)
            all_skills.update(scores.keys())

        # Calculate overall peer average and percentile
        if peer_weighted_scores:
            results["overall"]["peer_avg"] = sum(peer_weighted_scores) / len(
                peer_weighted_scores
            )
            results["overall"]["difference"] = (
                person_weighted - results["overall"]["peer_avg"]
            )

            # Calculate percentile (what percentage of peers score below this person)
            below_count = sum(1 for s in peer_weighted_scores if s < person_weighted)
            results["overall"]["percentile"] = (
                below_count / len(peer_weighted_scores)
            ) * 100

        # Compare by skill
        for skill in all_skills:
            person_skill_score = person_scores.get(skill, 0.0)
            peer_skill_scores = [
                scores.get(skill, 0.0) for scores in peer_scores.values()
            ]

            if peer_skill_scores:
                peer_avg = sum(peer_skill_scores) / len(peer_skill_scores)
                difference = person_skill_score - peer_avg

                # Calculate percentile for this skill
                below_count = sum(
                    1 for s in peer_skill_scores if s < person_skill_score
                )
                percentile = (below_count / len(peer_skill_scores)) * 100

                results["by_skill"][skill] = {
                    "person_score": person_skill_score,
                    "peer_avg": peer_avg,
                    "difference": difference,
                    "percentile": percentile,
                }

                # Categorize as strength or gap
                if difference > 1.0 and percentile > 75:
                    results["strengths"].append((skill, difference, percentile))
                elif difference < -1.0 and percentile < 25:
                    results["gaps"].append((skill, difference, percentile))

                # Categorize by category if available
                if categories and skill in categories:
                    category = categories[skill]
                    all_categories.add(category)

                    if category not in results["by_category"]:
                        results["by_category"][category] = {
                            "skills": [],
                            "person_avg": 0.0,
                            "peer_avg": 0.0,
                            "difference": 0.0,
                        }

                    results["by_category"][category]["skills"].append(skill)

        # Calculate category averages
        for category in results["by_category"]:
            category_skills = results["by_category"][category]["skills"]
            if category_skills:
                # Calculate person's average for this category
                person_cat_scores = [
                    person_scores.get(skill, 0.0) for skill in category_skills
                ]
                person_cat_avg = sum(person_cat_scores) / len(person_cat_scores)

                # Calculate peer average for this category
                peer_cat_avgs = []
                for peer_score_dict in peer_scores.values():
                    peer_cat_skills = [
                        peer_score_dict.get(skill, 0.0) for skill in category_skills
                    ]
                    if peer_cat_skills:
                        peer_cat_avgs.append(
                            sum(peer_cat_skills) / len(peer_cat_skills)
                        )

                if peer_cat_avgs:
                    peer_cat_avg = sum(peer_cat_avgs) / len(peer_cat_avgs)
                    difference = person_cat_avg - peer_cat_avg

                    results["by_category"][category]["person_avg"] = person_cat_avg
                    results["by_category"][category]["peer_avg"] = peer_cat_avg
                    results["by_category"][category]["difference"] = difference

        # Sort strengths and gaps by significance
        results["strengths"].sort(key=lambda x: (x[1], x[2]), reverse=True)
        results["gaps"].sort(key=lambda x: (x[1], x[2]))

        return results

    def analyze_year_over_year(
        self,
        yearly_scores: Dict[str, Dict[str, float]],
        peer_yearly_scores: Dict[str, Dict[str, Dict[str, float]]] = None,
        categories: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        """Analyze year-over-year performance trends.

        Args:
            yearly_scores: Dictionary mapping years to skill scores for each year
            peer_yearly_scores: Dictionary mapping years to peer scores for each year
            categories: Dictionary mapping skill names to their categories

        Returns:
            Dictionary with year-over-year analysis
        """
        results = {
            "years": sorted(yearly_scores.keys()),
            "overall_trend": {
                "scores": [],
                "peer_avg": [],
                "differences": [],
                "yoy_changes": [],
            },
            "by_skill": {},
            "by_category": {},
            "improved_skills": [],
            "declined_skills": [],
        }

        years = results["years"]
        if not years:
            return results

        # Calculate overall scores for each year
        for year in years:
            scores = yearly_scores.get(year, {})
            weighted_score = self.calculate_weighted_score(scores, categories)
            results["overall_trend"]["scores"].append(weighted_score)

            # Calculate peer average if available
            if peer_yearly_scores and year in peer_yearly_scores:
                peer_scores = peer_yearly_scores[year]
                peer_weighted = [
                    self.calculate_weighted_score(p_scores, categories)
                    for p_scores in peer_scores.values()
                ]

                if peer_weighted:
                    peer_avg = sum(peer_weighted) / len(peer_weighted)
                    results["overall_trend"]["peer_avg"].append(peer_avg)
                    results["overall_trend"]["differences"].append(
                        weighted_score - peer_avg
                    )
                else:
                    results["overall_trend"]["peer_avg"].append(0.0)
                    results["overall_trend"]["differences"].append(0.0)
            else:
                results["overall_trend"]["peer_avg"].append(0.0)
                results["overall_trend"]["differences"].append(0.0)

        # Calculate year-over-year changes
        for i in range(1, len(years)):
            prev_score = results["overall_trend"]["scores"][i - 1]
            curr_score = results["overall_trend"]["scores"][i]
            yoy_change = curr_score - prev_score
            results["overall_trend"]["yoy_changes"].append(yoy_change)

        # Find all unique skills across all years
        all_skills = set()
        for year, scores in yearly_scores.items():
            all_skills.update(scores.keys())

        # Calculate trends by skill
        for skill in all_skills:
            skill_scores = []
            peer_avgs = []

            for year in years:
                year_scores = yearly_scores.get(year, {})
                skill_score = year_scores.get(skill, 0.0)
                skill_scores.append(skill_score)

                # Get peer average for this skill in this year
                if peer_yearly_scores and year in peer_yearly_scores:
                    peer_year_scores = [
                        p_scores.get(skill, 0.0)
                        for p_scores in peer_yearly_scores[year].values()
                        if skill in p_scores
                    ]

                    if peer_year_scores:
                        peer_avg = sum(peer_year_scores) / len(peer_year_scores)
                    else:
                        peer_avg = 0.0
                else:
                    peer_avg = 0.0

                peer_avgs.append(peer_avg)

            # Calculate year-over-year changes for this skill
            yoy_changes = [
                skill_scores[i] - skill_scores[i - 1]
                for i in range(1, len(skill_scores))
            ]

            # Store results for this skill
            results["by_skill"][skill] = {
                "scores": skill_scores,
                "peer_avg": peer_avgs,
                "yoy_changes": yoy_changes,
            }

            # Check if skill has improved or declined
            if len(years) >= 2:
                first_score = skill_scores[0]
                last_score = skill_scores[-1]
                overall_change = last_score - first_score

                if (
                    overall_change
                    > self.config["yoy_comparison"]["improvement_threshold"]
                ):
                    results["improved_skills"].append((skill, overall_change))
                elif (
                    overall_change < self.config["yoy_comparison"]["decline_threshold"]
                ):
                    results["declined_skills"].append((skill, overall_change))

        # Calculate trends by category if available
        if categories:
            category_skills = {}
            for skill, category in categories.items():
                if category not in category_skills:
                    category_skills[category] = []
                category_skills[category].append(skill)

            for category, skills in category_skills.items():
                category_scores = []
                category_peer_avgs = []

                for year in years:
                    year_scores = yearly_scores.get(year, {})
                    cat_scores = [
                        year_scores.get(skill, 0.0)
                        for skill in skills
                        if skill in year_scores
                    ]

                    if cat_scores:
                        category_scores.append(sum(cat_scores) / len(cat_scores))
                    else:
                        category_scores.append(0.0)

                    # Calculate peer average for this category
                    if peer_yearly_scores and year in peer_yearly_scores:
                        peer_cat_avgs = []
                        for peer_scores in peer_yearly_scores[year].values():
                            peer_cat_scores = [
                                peer_scores.get(skill, 0.0)
                                for skill in skills
                                if skill in peer_scores
                            ]
                            if peer_cat_scores:
                                peer_cat_avgs.append(
                                    sum(peer_cat_scores) / len(peer_cat_scores)
                                )

                        if peer_cat_avgs:
                            category_peer_avgs.append(
                                sum(peer_cat_avgs) / len(peer_cat_avgs)
                            )
                        else:
                            category_peer_avgs.append(0.0)
                    else:
                        category_peer_avgs.append(0.0)

                # Calculate year-over-year changes
                yoy_changes = [
                    category_scores[i] - category_scores[i - 1]
                    for i in range(1, len(category_scores))
                ]

                results["by_category"][category] = {
                    "scores": category_scores,
                    "peer_avg": category_peer_avgs,
                    "yoy_changes": yoy_changes,
                }

        # Sort improved and declined skills
        results["improved_skills"].sort(key=lambda x: x[1], reverse=True)
        results["declined_skills"].sort(key=lambda x: x[1])

        return results

    def generate_peer_comparison_report(
        self,
        person_name: str,
        current_year: str,
        comparison_results: Dict[str, Any],
        output_dir: str,
    ) -> str:
        """Generate a detailed peer comparison report.

        Args:
            person_name: Name of the person being analyzed
            current_year: Year of the analysis
            comparison_results: Results from compare_with_peer_group
            output_dir: Directory to save the report

        Returns:
            Path to the generated report
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Create report file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(
            output_dir, f"{person_name}_peer_comparison_{current_year}.md"
        )

        with open(report_file, "w") as f:
            # Header
            f.write(f"# Peer Group Comparison: {person_name} ({current_year})\n\n")
            f.write(
                f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )

            # Overall comparison
            overall = comparison_results["overall"]
            f.write("## Overall Performance\n\n")

            f.write("| Metric | Value | Peer Average | Difference | Percentile |\n")
            f.write("|--------|-------|-------------|------------|------------|\n")

            diff = overall["difference"]
            diff_text = f"+{diff:.2f}" if diff > 0 else f"{diff:.2f}"

            f.write(
                f"| Overall Score | {overall['person_score']:.2f} | {overall['peer_avg']:.2f} | {diff_text} | {overall['percentile']:.1f}% |\n\n"
            )

            # Performance assessment
            f.write("### Performance Assessment\n\n")

            if overall["percentile"] >= 90:
                f.write(
                    "**Outstanding Performance**: You are in the top 10% of your peer group. Your performance is exceptional.\n\n"
                )
            elif overall["percentile"] >= 75:
                f.write(
                    "**Strong Performance**: You are in the top 25% of your peer group. You're performing well above average.\n\n"
                )
            elif overall["percentile"] >= 50:
                f.write(
                    "**Above Average**: You are performing better than half of your peer group.\n\n"
                )
            elif overall["percentile"] >= 25:
                f.write(
                    "**Average Performance**: Your performance is in line with many of your peers.\n\n"
                )
            else:
                f.write(
                    "**Development Opportunity**: Your current performance is lower than most of your peers, indicating opportunities for growth.\n\n"
                )

            # Key strengths
            if comparison_results["strengths"]:
                f.write("## Key Strengths\n\n")
                f.write(
                    "These are areas where you significantly outperform your peer group:\n\n"
                )

                f.write(
                    "| Skill | Your Score | Peer Average | Difference | Percentile |\n"
                )
                f.write(
                    "|-------|------------|-------------|------------|------------|\n"
                )

                for skill, diff, percentile in comparison_results["strengths"][
                    :5
                ]:  # Top 5 strengths
                    skill_data = comparison_results["by_skill"][skill]
                    diff_text = f"+{diff:.2f}" if diff > 0 else f"{diff:.2f}"

                    f.write(
                        f"| {skill} | {skill_data['person_score']:.2f} | {skill_data['peer_avg']:.2f} | {diff_text} | {percentile:.1f}% |\n"
                    )

                f.write("\n")

            # Development areas
            if comparison_results["gaps"]:
                f.write("## Development Opportunities\n\n")
                f.write(
                    "These are areas where you may want to focus your development efforts:\n\n"
                )

                f.write(
                    "| Skill | Your Score | Peer Average | Difference | Percentile |\n"
                )
                f.write(
                    "|-------|------------|-------------|------------|------------|\n"
                )

                for skill, diff, percentile in comparison_results["gaps"][
                    :5
                ]:  # Top 5 gaps
                    skill_data = comparison_results["by_skill"][skill]
                    diff_text = f"{diff:.2f}"

                    f.write(
                        f"| {skill} | {skill_data['person_score']:.2f} | {skill_data['peer_avg']:.2f} | {diff_text} | {percentile:.1f}% |\n"
                    )

                f.write("\n")

            # Category comparison
            if comparison_results["by_category"]:
                f.write("## Skill Category Analysis\n\n")

                f.write("| Category | Your Average | Peer Average | Difference |\n")
                f.write("|----------|-------------|-------------|------------|\n")

                for category, data in comparison_results["by_category"].items():
                    diff = data["difference"]
                    diff_text = f"+{diff:.2f}" if diff > 0 else f"{diff:.2f}"

                    f.write(
                        f"| {category} | {data['person_avg']:.2f} | {data['peer_avg']:.2f} | {diff_text} |\n"
                    )

                f.write("\n")

            # Skill details
            f.write("## Detailed Skill Analysis\n\n")

            f.write("| Skill | Your Score | Peer Average | Difference | Percentile |\n")
            f.write("|-------|------------|-------------|------------|------------|\n")

            # Sort skills by difference
            sorted_skills = sorted(
                comparison_results["by_skill"].items(),
                key=lambda x: x[1]["difference"],
                reverse=True,
            )

            for skill, data in sorted_skills:
                diff = data["difference"]
                diff_text = f"+{diff:.2f}" if diff > 0 else f"{diff:.2f}"

                f.write(
                    f"| {skill} | {data['person_score']:.2f} | {data['peer_avg']:.2f} | {diff_text} | {data['percentile']:.1f}% |\n"
                )

            f.write("\n")

            # Recommendations
            f.write("## Recommendations\n\n")

            if comparison_results["gaps"]:
                f.write("### Focus Areas for Development\n\n")

                for skill, diff, percentile in comparison_results["gaps"][:3]:
                    f.write(
                        f"1. **{skill}**: Consider focusing on developing this skill as it shows the largest gap compared to your peers.\n"
                    )

                f.write("\n")

            f.write("### Leverage Your Strengths\n\n")

            if comparison_results["strengths"]:
                for skill, diff, percentile in comparison_results["strengths"][:3]:
                    f.write(
                        f"1. **{skill}**: This is a significant strength. Consider mentoring others or taking on projects that leverage this skill.\n"
                    )
            else:
                f.write(
                    "Find opportunities to showcase your strongest skills in your current role.\n"
                )

            f.write("\n")

            # Footer
            f.write("---\n")
            f.write("This report was generated by the People Analytics platform.\n")

        return report_file

    def generate_year_over_year_report(
        self, person_name: str, yoy_results: Dict[str, Any], output_dir: str
    ) -> str:
        """Generate a year-over-year comparison report.

        Args:
            person_name: Name of the person being analyzed
            yoy_results: Results from analyze_year_over_year
            output_dir: Directory to save the report

        Returns:
            Path to the generated report
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Create report file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(
            output_dir, f"{person_name}_year_over_year_analysis.md"
        )

        with open(report_file, "w") as f:
            # Header
            f.write(f"# Year-Over-Year Performance Analysis: {person_name}\n\n")
            f.write(
                f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )

            years = yoy_results["years"]
            if len(years) <= 1:
                f.write(
                    "Insufficient data for year-over-year analysis. At least two years of data are required.\n"
                )
                return report_file

            # Overall trend
            f.write("## Performance Trend Summary\n\n")

            scores = yoy_results["overall_trend"]["scores"]
            peer_avgs = yoy_results["overall_trend"]["peer_avg"]

            f.write("| Year | Your Score | Peer Average | Difference | YoY Change |\n")
            f.write("|------|------------|-------------|------------|------------|\n")

            for i, year in enumerate(years):
                score = scores[i]
                peer_avg = peer_avgs[i]
                diff = score - peer_avg
                diff_text = f"+{diff:.2f}" if diff > 0 else f"{diff:.2f}"

                # YoY change (for all except the first year)
                yoy_change = ""
                if i > 0:
                    change = score - scores[i - 1]
                    yoy_change = f"+{change:.2f}" if change > 0 else f"{change:.2f}"

                f.write(
                    f"| {year} | {score:.2f} | {peer_avg:.2f} | {diff_text} | {yoy_change} |\n"
                )

            f.write("\n")

            # Overall trend analysis
            f.write("### Performance Trend Analysis\n\n")

            # Analyze the overall trend
            if len(scores) >= 2:
                first_score = scores[0]
                last_score = scores[-1]
                overall_change = last_score - first_score

                if (
                    overall_change
                    > self.config["yoy_comparison"]["improvement_threshold"]
                ):
                    f.write(
                        f"**Positive Trend**: Your overall performance has improved by {overall_change:.2f} points from {years[0]} to {years[-1]}.\n\n"
                    )
                elif (
                    overall_change < self.config["yoy_comparison"]["decline_threshold"]
                ):
                    f.write(
                        f"**Declining Trend**: Your overall performance has decreased by {abs(overall_change):.2f} points from {years[0]} to {years[-1]}.\n\n"
                    )
                else:
                    f.write(
                        f"**Steady Performance**: Your overall performance has remained relatively stable from {years[0]} to {years[-1]} (change of {overall_change:.2f} points).\n\n"
                    )

                # Compare with peer group trend
                first_peer_avg = peer_avgs[0]
                last_peer_avg = peer_avgs[-1]
                peer_change = last_peer_avg - first_peer_avg

                f.write("### Comparison with Peer Group Trend\n\n")

                if abs(peer_change) < 0.2:
                    f.write(
                        "The peer group average has remained relatively stable over this period.\n\n"
                    )
                elif peer_change > 0:
                    f.write(
                        f"The peer group average has increased by {peer_change:.2f} points over this period.\n\n"
                    )
                else:
                    f.write(
                        f"The peer group average has decreased by {abs(peer_change):.2f} points over this period.\n\n"
                    )

                if overall_change > peer_change + 0.5:
                    f.write(
                        "**You are improving faster than your peer group average.**\n\n"
                    )
                elif overall_change < peer_change - 0.5:
                    f.write(
                        "**Your performance growth is lagging behind the peer group average.**\n\n"
                    )
                else:
                    f.write(
                        "Your performance is changing at a similar rate to the peer group average.\n\n"
                    )

            # Most improved skills
            if yoy_results["improved_skills"]:
                f.write("## Most Improved Skills\n\n")

                f.write("| Skill | First Year | Latest Year | Change |\n")
                f.write("|-------|------------|------------|--------|\n")

                for skill, change in yoy_results["improved_skills"][
                    :5
                ]:  # Top 5 improvements
                    skill_data = yoy_results["by_skill"][skill]
                    first_score = skill_data["scores"][0]
                    last_score = skill_data["scores"][-1]

                    f.write(
                        f"| {skill} | {first_score:.2f} | {last_score:.2f} | +{change:.2f} |\n"
                    )

                f.write("\n")

            # Declining skills
            if yoy_results["declined_skills"]:
                f.write("## Skills with Declining Trends\n\n")

                f.write("| Skill | First Year | Latest Year | Change |\n")
                f.write("|-------|------------|------------|--------|\n")

                for skill, change in yoy_results["declined_skills"][
                    :5
                ]:  # Top 5 declines
                    skill_data = yoy_results["by_skill"][skill]
                    first_score = skill_data["scores"][0]
                    last_score = skill_data["scores"][-1]

                    f.write(
                        f"| {skill} | {first_score:.2f} | {last_score:.2f} | {change:.2f} |\n"
                    )

                f.write("\n")

            # Category trends
            if yoy_results["by_category"]:
                f.write("## Skill Category Trends\n\n")

                for category, data in yoy_results["by_category"].items():
                    f.write(f"### {category}\n\n")

                    f.write("| Year | Your Average | Peer Average | Difference |\n")
                    f.write("|------|-------------|-------------|------------|\n")

                    for i, year in enumerate(years):
                        score = data["scores"][i] if i < len(data["scores"]) else 0
                        peer_avg = (
                            data["peer_avg"][i] if i < len(data["peer_avg"]) else 0
                        )
                        diff = score - peer_avg
                        diff_text = f"+{diff:.2f}" if diff > 0 else f"{diff:.2f}"

                        f.write(
                            f"| {year} | {score:.2f} | {peer_avg:.2f} | {diff_text} |\n"
                        )

                    # Analyze trend for this category
                    if len(data["scores"]) >= 2:
                        first_score = data["scores"][0]
                        last_score = data["scores"][-1]
                        change = last_score - first_score

                        f.write("\n")

                        if (
                            change
                            > self.config["yoy_comparison"]["improvement_threshold"]
                        ):
                            f.write(f"**Trend**: Improving (+{change:.2f} points)\n\n")
                        elif (
                            change < self.config["yoy_comparison"]["decline_threshold"]
                        ):
                            f.write(f"**Trend**: Declining ({change:.2f} points)\n\n")
                        else:
                            f.write(
                                f"**Trend**: Stable (change of {change:.2f} points)\n\n"
                            )

                    f.write("\n")

            # Recommendations
            f.write("## Recommendations\n\n")

            # Focus areas based on declining skills
            if yoy_results["declined_skills"]:
                f.write("### Focus Areas for Development\n\n")

                for skill, change in yoy_results["declined_skills"][:3]:
                    f.write(
                        f"1. **{skill}**: This skill has shown a decline of {abs(change):.2f} points. Consider prioritizing development in this area.\n"
                    )

                f.write("\n")

            # Leverage improving skills
            if yoy_results["improved_skills"]:
                f.write("### Continue Building on Improvements\n\n")

                for skill, change in yoy_results["improved_skills"][:3]:
                    f.write(
                        f"1. **{skill}**: Continue building on your progress in this area (improved by {change:.2f} points).\n"
                    )

                f.write("\n")

            # Overall recommendations
            f.write("### Overall Development Plan\n\n")

            overall_scores = yoy_results["overall_trend"]["scores"]
            if len(overall_scores) >= 2:
                overall_change = overall_scores[-1] - overall_scores[0]

                if overall_change > 1.0:
                    f.write(
                        "Your consistent improvement suggests that your current development approach is working well. Consider setting more challenging goals to maintain momentum.\n\n"
                    )
                elif overall_change > 0:
                    f.write(
                        "You've shown modest improvement. Consider a more structured development plan to accelerate your growth.\n\n"
                    )
                elif overall_change > -0.5:
                    f.write(
                        "Your performance has remained relatively stable. Consider refreshing your development plan to find new areas for growth.\n\n"
                    )
                else:
                    f.write(
                        "The declining trend suggests a need to reassess your development approach. Consider seeking additional feedback and support.\n\n"
                    )

            # Footer
            f.write("---\n")
            f.write("This report was generated by the People Analytics platform.\n")

        return report_file
