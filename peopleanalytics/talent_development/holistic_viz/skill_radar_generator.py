"""
Skill Radar Chart Generator

This module provides specialized functionality for generating skill radar charts
based on the skill matrix data from the domain models.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from peopleanalytics.data_model import PersonData
from peopleanalytics.talent_development.holistic_viz.visualization_components import (
    create_radar_chart,
)


class SkillRadarGenerator:
    """
    Generator for skill radar charts based on skill matrices and career data.
    """

    def __init__(self, output_dir: str = "output/visualizations"):
        """
        Initialize skill radar chart generator.

        Args:
            output_dir: Directory to save generated visualizations
        """
        self.output_dir = Path(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

        # Subdirectories for different chart types
        self.individual_dir = self.output_dir / "individual_skills"
        self.comparison_dir = self.output_dir / "skill_comparisons"
        self.gap_dir = self.output_dir / "skill_gaps"
        self.team_dir = self.output_dir / "team_skills"

        # Create subdirectories
        os.makedirs(self.individual_dir, exist_ok=True)
        os.makedirs(self.comparison_dir, exist_ok=True)
        os.makedirs(self.gap_dir, exist_ok=True)
        os.makedirs(self.team_dir, exist_ok=True)

    def generate_individual_radar(
        self,
        person_data: PersonData,
        include_categories: bool = True,
        top_n: int = 10,
        filename: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a radar chart for an individual's skills.

        Args:
            person_data: Person data with skills
            include_categories: Whether to include skill categories in the chart
            top_n: Number of top skills to include (by level)
            filename: Optional filename to save the chart

        Returns:
            Path to the saved chart or None if generation failed
        """
        if (
            not person_data
            or not person_data.career_progression
            or not person_data.career_progression.skills_matrix
        ):
            logging.warning(
                f"No skill data available for {person_data.name if person_data else 'unknown'}"
            )
            return None

        # Extract skill matrix
        skills_dict = person_data.career_progression.skills_matrix

        if not skills_dict:
            logging.warning(f"Empty skill matrix for {person_data.name}")
            return None

        # Extract skill categories if present
        skill_categories = {}
        for skill_name in skills_dict:
            if "." in skill_name:
                category, name = skill_name.split(".", 1)
                skill_categories[skill_name] = category

        # Sort skills by level and take top N
        top_skills = dict(
            sorted(skills_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]
        )

        # Determine filename if not provided
        if not filename:
            filename = self.individual_dir / f"{person_data.name}_skills_radar.png"

        # Generate chart title
        title = f"Skill Profile: {person_data.name}"
        if person_data.profile and person_data.profile.cargo:
            title += f" - {person_data.profile.cargo}"

        # Create radar chart
        try:
            create_radar_chart(
                skills=top_skills,
                title=title,
                skill_categories=skill_categories if include_categories else None,
                filename=str(filename),
            )
            logging.info(f"Generated individual skill radar chart: {filename}")
            return str(filename)
        except Exception as e:
            logging.error(f"Error generating skill radar chart: {e}")
            return None

    def generate_gap_analysis_radar(
        self,
        person_data: PersonData,
        target_skills: Dict[str, float],
        title: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a radar chart showing skill gaps between current and target skills.

        Args:
            person_data: Person data with current skills
            target_skills: Target skill levels (e.g., for a role/position)
            title: Optional chart title
            filename: Optional filename to save the chart

        Returns:
            Path to the saved chart or None if generation failed
        """
        if (
            not person_data
            or not person_data.career_progression
            or not person_data.career_progression.skills_matrix
        ):
            logging.warning(
                f"No skill data available for {person_data.name if person_data else 'unknown'}"
            )
            return None

        # Extract current skills
        current_skills = person_data.career_progression.skills_matrix

        if not current_skills:
            logging.warning(f"Empty skill matrix for {person_data.name}")
            return None

        # Find common skills for comparison
        common_skills = {}
        for skill in target_skills:
            if skill in current_skills:
                common_skills[skill] = current_skills[skill]
            else:
                # Include missing skills with level 0
                common_skills[skill] = 0

        # Determine filename if not provided
        if not filename:
            target_name = "target"
            filename = self.gap_dir / f"{person_data.name}_vs_{target_name}_gap.png"

        # Generate chart title
        if not title:
            title = f"Skill Gap Analysis: {person_data.name}"

        # Extract skill categories if present
        skill_categories = {}
        for skill_name in common_skills:
            if "." in skill_name:
                category, name = skill_name.split(".", 1)
                skill_categories[skill_name] = category

        # Create radar chart with target skills
        try:
            create_radar_chart(
                skills=common_skills,
                title=title,
                target_skills=target_skills,
                skill_categories=skill_categories,
                filename=str(filename),
            )
            logging.info(f"Generated skill gap radar chart: {filename}")
            return str(filename)
        except Exception as e:
            logging.error(f"Error generating skill gap radar chart: {e}")
            return None

    def generate_team_radar(
        self,
        team_data: List[PersonData],
        team_name: str,
        filename: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a radar chart showing average skill levels for a team.

        Args:
            team_data: List of person data for team members
            team_name: Name of the team
            filename: Optional filename to save the chart

        Returns:
            Path to the saved chart or None if generation failed
        """
        if not team_data:
            logging.warning(f"No team data provided for {team_name}")
            return None

        # Collect all skills across team members
        all_skills = {}
        skill_counts = {}

        for person in team_data:
            if (
                not person
                or not person.career_progression
                or not person.career_progression.skills_matrix
            ):
                continue

            for skill, level in person.career_progression.skills_matrix.items():
                if skill not in all_skills:
                    all_skills[skill] = 0
                    skill_counts[skill] = 0

                all_skills[skill] += level
                skill_counts[skill] += 1

        # Calculate average skill levels
        avg_skills = {}
        for skill, total in all_skills.items():
            count = skill_counts[skill]
            if count > 0:
                avg_skills[skill] = total / count

        if not avg_skills:
            logging.warning(f"No skills data available for team {team_name}")
            return None

        # Sort by average and take top 10
        top_avg_skills = dict(
            sorted(avg_skills.items(), key=lambda x: x[1], reverse=True)[:10]
        )

        # Determine filename if not provided
        if not filename:
            filename = self.team_dir / f"{team_name}_team_skills.png"

        # Extract skill categories if present
        skill_categories = {}
        for skill_name in top_avg_skills:
            if "." in skill_name:
                category, name = skill_name.split(".", 1)
                skill_categories[skill_name] = category

        # Create radar chart
        try:
            create_radar_chart(
                skills=top_avg_skills,
                title=f"Team Skill Profile: {team_name}",
                skill_categories=skill_categories,
                filename=str(filename),
            )
            logging.info(f"Generated team skill radar chart: {filename}")
            return str(filename)
        except Exception as e:
            logging.error(f"Error generating team skill radar chart: {e}")
            return None

    def generate_person_comparison_radar(
        self,
        person1_data: PersonData,
        person2_data: PersonData,
        filename: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a radar chart comparing skills between two people.

        Args:
            person1_data: First person's data
            person2_data: Second person's data
            filename: Optional filename to save the chart

        Returns:
            Path to the saved chart or None if generation failed
        """
        if (
            not person1_data
            or not person1_data.career_progression
            or not person1_data.career_progression.skills_matrix
        ):
            logging.warning(
                f"No skill data available for {person1_data.name if person1_data else 'unknown'}"
            )
            return None

        if (
            not person2_data
            or not person2_data.career_progression
            or not person2_data.career_progression.skills_matrix
        ):
            logging.warning(
                f"No skill data available for {person2_data.name if person2_data else 'unknown'}"
            )
            return None

        # Extract skill matrices
        skills1 = person1_data.career_progression.skills_matrix
        skills2 = person2_data.career_progression.skills_matrix

        # Find common skills
        common_skills = set(skills1.keys()).intersection(set(skills2.keys()))

        if not common_skills:
            logging.warning(
                f"No common skills between {person1_data.name} and {person2_data.name}"
            )
            return None

        # Create filtered skill dictionaries
        person1_skills = {s: skills1[s] for s in common_skills}
        person2_skills = {s: skills2[s] for s in common_skills}

        # Determine filename if not provided
        if not filename:
            filename = (
                self.comparison_dir / f"{person1_data.name}_vs_{person2_data.name}.png"
            )

        # Extract skill categories if present
        skill_categories = {}
        for skill_name in common_skills:
            if "." in skill_name:
                category, name = skill_name.split(".", 1)
                skill_categories[skill_name] = category

        # Create radar chart with comparison
        try:
            create_radar_chart(
                skills=person1_skills,
                title=f"Skill Comparison: {person1_data.name} vs {person2_data.name}",
                target_skills=person2_skills,
                skill_categories=skill_categories,
                filename=str(filename),
                color_scheme={
                    "current": {
                        "line": "rgb(53, 135, 212)",
                        "fill": "rgba(53, 135, 212, 0.3)",
                    },
                    "target": {
                        "line": "rgb(135, 86, 212)",
                        "fill": "rgba(135, 86, 212, 0.2)",
                    },
                },
            )
            logging.info(f"Generated skill comparison radar chart: {filename}")
            return str(filename)
        except Exception as e:
            logging.error(f"Error generating skill comparison radar chart: {e}")
            return None


def generate_all_radar_charts(
    data_list: List[PersonData], output_dir: str
) -> Dict[str, Any]:
    """
    Generate all skill radar charts for a list of people.

    Args:
        data_list: List of person data objects
        output_dir: Base output directory

    Returns:
        Dictionary with paths to generated charts
    """
    generator = SkillRadarGenerator(output_dir=output_dir)
    results = {
        "individual_charts": {},
        "team_charts": {},
        "comparison_charts": {},
        "gap_charts": {},
    }

    # Generate individual charts
    for person in data_list:
        if not person:
            continue

        chart_path = generator.generate_individual_radar(person)
        if chart_path:
            results["individual_charts"][person.name] = chart_path

    # Group by department for team charts
    departments = {}
    for person in data_list:
        if not person or not person.profile:
            continue

        dept = person.profile.nome_departamento
        if not dept:
            continue

        if dept not in departments:
            departments[dept] = []

        departments[dept].append(person)

    # Generate team charts
    for dept_name, team_members in departments.items():
        if len(team_members) < 2:
            continue

        chart_path = generator.generate_team_radar(team_members, dept_name)
        if chart_path:
            results["team_charts"][dept_name] = chart_path

    # Generate a few comparison charts (if more than one person)
    if len(data_list) > 1:
        # Choose a few pairs to compare (e.g., first few people in same departments)
        compared = set()
        for dept_name, team_members in departments.items():
            if len(team_members) < 2:
                continue

            # Compare first two members of each department
            person1 = team_members[0]
            person2 = team_members[1]

            pair_key = f"{person1.name}_{person2.name}"
            if pair_key in compared:
                continue

            chart_path = generator.generate_person_comparison_radar(person1, person2)
            if chart_path:
                results["comparison_charts"][f"{person1.name}_vs_{person2.name}"] = (
                    chart_path
                )
                compared.add(pair_key)

    # For gap analysis, use positions as targets if available
    positions = {}

    # First, collect position skill requirements across the organization
    for person in data_list:
        if not person or not person.profile:
            continue

        position = person.profile.cargo
        if not position:
            continue

        if position not in positions:
            positions[position] = {"skills": {}, "counts": {}, "people": []}

        positions[position]["people"].append(person)

        # Collect skills for this position
        if person.career_progression and person.career_progression.skills_matrix:
            for skill, level in person.career_progression.skills_matrix.items():
                if skill not in positions[position]["skills"]:
                    positions[position]["skills"][skill] = 0
                    positions[position]["counts"][skill] = 0

                positions[position]["skills"][skill] += level
                positions[position]["counts"][skill] += 1

    # Calculate average skill levels by position
    position_skill_targets = {}
    for position, data in positions.items():
        if not data["skills"]:
            continue

        # Calculate averages
        avg_skills = {}
        for skill, total in data["skills"].items():
            count = data["counts"][skill]
            if count > 0:
                avg_skills[skill] = total / count

        position_skill_targets[position] = avg_skills

    # Generate gap charts for each person against their position's skill target
    for person in data_list:
        if not person or not person.profile:
            continue

        position = person.profile.cargo
        if not position or position not in position_skill_targets:
            continue

        target_skills = position_skill_targets[position]
        if not target_skills:
            continue

        chart_path = generator.generate_gap_analysis_radar(
            person_data=person,
            target_skills=target_skills,
            title=f"Skill Gap Analysis: {person.name} vs {position} Role",
        )

        if chart_path:
            results["gap_charts"][person.name] = chart_path

    return results
