"""
Commands related to skills analysis and visualization.

This module contains CLI commands for analyzing, visualizing, 
and managing skills data within the People Analytics platform.
"""

import argparse
import os
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from peopleanalytics.data_model import PersonData
from peopleanalytics.evaluation_analyzer import EvaluationAnalyzer
from peopleanalytics.reports_generator import (
    generate_skill_recommendations, 
    generate_evaluation_report
)
from peopleanalytics.talent_development.holistic_viz.skill_radar_generator import (
    SkillRadarGenerator,
    generate_all_radar_charts
)
from peopleanalytics.domain.skill_base import (
    SkillMatrix,
    Skill,
    derive_skill_gap
)

class SkillsRadarCommand:
    """
    Command to generate skill radar visualizations.
    """
    
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """
        Add command-specific arguments to the parser.
        
        Args:
            parser: The argparse parser to add arguments to
        """
        # Input/output options
        parser.add_argument(
            "--data-dir",
            default="data",
            help="Directory containing data files",
        )
        parser.add_argument(
            "--output-dir",
            default="output/visualizations",
            help="Directory to store generated charts",
        )
        
        # Filtering options
        parser.add_argument(
            "--person",
            type=str,
            help="Generate charts for a specific person only",
        )
        parser.add_argument(
            "--department",
            type=str,
            help="Generate charts for a specific department only",
        )
        parser.add_argument(
            "--year",
            type=str,
            help="Use data from a specific year only",
        )
        
        # Chart types
        parser.add_argument(
            "--individual",
            action="store_true",
            help="Generate individual skill radar charts",
        )
        parser.add_argument(
            "--team",
            action="store_true",
            help="Generate team/department skill radar charts",
        )
        parser.add_argument(
            "--gap",
            action="store_true",
            help="Generate skill gap analysis charts",
        )
        parser.add_argument(
            "--comparison",
            action="store_true",
            help="Generate skill comparison charts",
        )
        parser.add_argument(
            "--all-charts",
            action="store_true",
            help="Generate all types of charts",
        )
        
        # Additional options
        parser.add_argument(
            "--top-skills",
            type=int,
            default=10,
            help="Number of top skills to include in charts",
        )
        parser.add_argument(
            "--format",
            choices=["png", "html", "both"],
            default="both",
            help="Output format for charts (png, html, or both)",
        )
        
    def execute(self, args):
        """
        Execute the skill radar command.
        
        Args:
            args: Parsed arguments from argparse
        """
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger = logging.getLogger("skills-radar")
        
        # Validate directories
        data_dir = Path(args.data_dir)
        output_dir = Path(args.output_dir)
        
        if not data_dir.exists():
            logger.error(f"Data directory does not exist: {data_dir}")
            return 1
            
        # Create output directory if it doesn't exist
        if not output_dir.exists():
            logger.info(f"Creating output directory: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)
            
        # Initialize the evaluation analyzer
        analyzer = EvaluationAnalyzer(str(data_dir))
        
        # Load all people data
        logger.info("Loading people data...")
        try:
            all_people = analyzer.get_all_people()
            
            # Filter by person if specified
            if args.person:
                if args.person in all_people:
                    all_people = [args.person]
                else:
                    logger.warning(f"Person not found: {args.person}")
                    return 1
                    
            # Load data for each person
            people_data = []
            
            for person in all_people:
                try:
                    # Apply year filter if specified
                    years = analyzer.get_years_for_person(person)
                    
                    if args.year:
                        if args.year in years:
                            years = [args.year]
                        else:
                            logger.warning(f"Year {args.year} not found for {person}")
                            continue
                    elif years:
                        # Default to latest year
                        years = [years[-1]]
                        
                    # Load data for each year
                    for year in years:
                        person_data = analyzer.load_person_data(person, year)
                        
                        # Apply department filter if specified
                        if args.department and person_data.profile:
                            if person_data.profile.nome_departamento != args.department:
                                continue
                                
                        people_data.append(person_data)
                        
                except Exception as e:
                    logger.warning(f"Error loading data for {person}: {e}")
                    continue
                    
            if not people_data:
                logger.error("No valid people data found with the specified filters")
                return 1
                
            # Determine which charts to generate
            generate_individual = args.individual or args.all_charts
            generate_team = args.team or args.all_charts
            generate_gap = args.gap or args.all_charts
            generate_comparison = args.comparison or args.all_charts
            
            # If no specific chart types are requested, generate individual charts by default
            if not (generate_individual or generate_team or generate_gap or generate_comparison):
                generate_individual = True
                
            # Initialize the skill radar generator
            radar_generator = SkillRadarGenerator(str(output_dir))
            chart_results = {
                "individual_charts": {},
                "team_charts": {},
                "comparison_charts": {},
                "gap_charts": {}
            }
            
            # Generate requested charts
            if generate_individual:
                logger.info("Generating individual skill radar charts...")
                for person_data in people_data:
                    try:
                        chart_path = radar_generator.generate_individual_radar(
                            person_data=person_data,
                            top_n=args.top_skills
                        )
                        if chart_path:
                            chart_results["individual_charts"][person_data.name] = chart_path
                    except Exception as e:
                        logger.warning(f"Error generating individual chart for {person_data.name}: {e}")
                        
            if generate_team and len(people_data) > 1:
                logger.info("Generating team skill radar charts...")
                # Group by department
                departments = {}
                for person_data in people_data:
                    if not person_data.profile:
                        continue
                        
                    dept = person_data.profile.nome_departamento
                    if not dept:
                        continue
                        
                    if dept not in departments:
                        departments[dept] = []
                        
                    departments[dept].append(person_data)
                    
                # Generate team charts
                for dept_name, team_members in departments.items():
                    if len(team_members) < 2:
                        continue
                        
                    try:
                        chart_path = radar_generator.generate_team_radar(
                            team_data=team_members,
                            team_name=dept_name
                        )
                        if chart_path:
                            chart_results["team_charts"][dept_name] = chart_path
                    except Exception as e:
                        logger.warning(f"Error generating team chart for {dept_name}: {e}")
                        
            if generate_comparison and len(people_data) > 1:
                logger.info("Generating skill comparison radar charts...")
                # Generate comparison charts for people in the same department
                compared = set()
                for dept_name, team_members in departments.items() if 'departments' in locals() else []:
                    if len(team_members) < 2:
                        continue
                        
                    # Compare first two members of each department
                    person1 = team_members[0]
                    person2 = team_members[1]
                    
                    pair_key = f"{person1.name}_{person2.name}"
                    if pair_key in compared:
                        continue
                        
                    try:
                        chart_path = radar_generator.generate_person_comparison_radar(
                            person1_data=person1,
                            person2_data=person2
                        )
                        if chart_path:
                            chart_results["comparison_charts"][f"{person1.name}_vs_{person2.name}"] = chart_path
                            compared.add(pair_key)
                    except Exception as e:
                        logger.warning(f"Error generating comparison chart for {person1.name} vs {person2.name}: {e}")
                        
            if generate_gap:
                logger.info("Generating skill gap analysis radar charts...")
                # Calculate position skill targets
                positions = {}
                
                # First, collect position skill requirements across the organization
                for person_data in people_data:
                    if not person_data.profile:
                        continue
                        
                    position = person_data.profile.cargo
                    if not position:
                        continue
                        
                    if position not in positions:
                        positions[position] = {
                            "skills": {},
                            "counts": {},
                            "people": []
                        }
                        
                    positions[position]["people"].append(person_data)
                    
                    # Collect skills for this position
                    if person_data.career_progression and person_data.career_progression.skills_matrix:
                        for skill, level in person_data.career_progression.skills_matrix.items():
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
                for person_data in people_data:
                    if not person_data.profile:
                        continue
                        
                    position = person_data.profile.cargo
                    if not position or position not in position_skill_targets:
                        continue
                        
                    target_skills = position_skill_targets[position]
                    if not target_skills:
                        continue
                        
                    try:
                        chart_path = radar_generator.generate_gap_analysis_radar(
                            person_data=person_data,
                            target_skills=target_skills,
                            title=f"Skill Gap Analysis: {person_data.name} vs {position} Role"
                        )
                        
                        if chart_path:
                            chart_results["gap_charts"][person_data.name] = chart_path
                    except Exception as e:
                        logger.warning(f"Error generating gap chart for {person_data.name}: {e}")
                        
            # Print summary of generated charts
            logger.info("Chart generation complete.")
            
            individual_count = len(chart_results["individual_charts"])
            team_count = len(chart_results["team_charts"])
            comparison_count = len(chart_results["comparison_charts"])
            gap_count = len(chart_results["gap_charts"])
            
            logger.info(f"Generated {individual_count} individual charts")
            logger.info(f"Generated {team_count} team charts")
            logger.info(f"Generated {comparison_count} comparison charts")
            logger.info(f"Generated {gap_count} gap analysis charts")
            
            # Print output directory
            logger.info(f"All charts saved to: {output_dir}")
            
            return 0
            
        except Exception as e:
            logger.error(f"Error executing skills radar command: {e}")
            import traceback
            traceback.print_exc()
            return 1
            
class SkillsAnalysisCommand:
    """
    Command to perform comprehensive skills analysis.
    """
    
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """
        Add command-specific arguments to the parser.
        
        Args:
            parser: The argparse parser to add arguments to
        """
        # Input/output options
        parser.add_argument(
            "--data-dir",
            default="data",
            help="Directory containing data files",
        )
        parser.add_argument(
            "--output-dir",
            default="output/skills_analysis",
            help="Directory to store analysis results",
        )
        
        # Filtering options
        parser.add_argument(
            "--person",
            type=str,
            help="Analyze a specific person only",
        )
        parser.add_argument(
            "--department",
            type=str,
            help="Analyze a specific department only",
        )
        parser.add_argument(
            "--year",
            type=str,
            help="Use data from a specific year only",
        )
        
        # Analysis types
        parser.add_argument(
            "--recommendations",
            action="store_true",
            help="Generate skill recommendations",
        )
        parser.add_argument(
            "--gaps",
            action="store_true",
            help="Perform skill gap analysis",
        )
        parser.add_argument(
            "--visualizations",
            action="store_true",
            help="Generate skill visualizations",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Perform all analysis types",
        )
        
    def execute(self, args):
        """
        Execute the skills analysis command.
        
        Args:
            args: Parsed arguments from argparse
        """
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger = logging.getLogger("skills-analysis")
        
        # Validate directories
        data_dir = Path(args.data_dir)
        output_dir = Path(args.output_dir)
        
        if not data_dir.exists():
            logger.error(f"Data directory does not exist: {data_dir}")
            return 1
            
        # Create output directory if it doesn't exist
        if not output_dir.exists():
            logger.info(f"Creating output directory: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)
            
        # Initialize the evaluation analyzer
        analyzer = EvaluationAnalyzer(str(data_dir))
        
        # Determine which analyses to perform
        do_recommendations = args.recommendations or args.all
        do_gaps = args.gaps or args.all
        do_visualizations = args.visualizations or args.all
        
        # If no specific analysis types are requested, perform all
        if not (do_recommendations or do_gaps or do_visualizations):
            do_recommendations = True
            do_gaps = True
            do_visualizations = True
            
        # Load all people data
        logger.info("Loading people data...")
        try:
            all_people = analyzer.get_all_people()
            
            # Filter by person if specified
            if args.person:
                if args.person in all_people:
                    all_people = [args.person]
                else:
                    logger.warning(f"Person not found: {args.person}")
                    return 1
                    
            # Load data for each person
            people_data = []
            
            for person in all_people:
                try:
                    # Apply year filter if specified
                    years = analyzer.get_years_for_person(person)
                    
                    if args.year:
                        if args.year in years:
                            years = [args.year]
                        else:
                            logger.warning(f"Year {args.year} not found for {person}")
                            continue
                    elif years:
                        # Default to latest year
                        years = [years[-1]]
                        
                    # Load data for each year
                    for year in years:
                        person_data = analyzer.load_person_data(person, year)
                        
                        # Apply department filter if specified
                        if args.department and person_data.profile:
                            if person_data.profile.nome_departamento != args.department:
                                continue
                                
                        people_data.append(person_data)
                        
                except Exception as e:
                    logger.warning(f"Error loading data for {person}: {e}")
                    continue
                    
            if not people_data:
                logger.error("No valid people data found with the specified filters")
                return 1
                
            # Perform requested analyses
            if do_recommendations:
                logger.info("Generating skill recommendations...")
                recommendations_dir = output_dir / "recommendations"
                os.makedirs(recommendations_dir, exist_ok=True)
                
                try:
                    report_path = generate_skill_recommendations(
                        data_list=people_data,
                        output_dir=str(recommendations_dir)
                    )
                    logger.info(f"Skill recommendations saved to: {report_path}")
                except Exception as e:
                    logger.error(f"Error generating skill recommendations: {e}")
                    
            if do_gaps:
                logger.info("Performing skill gap analysis...")
                gaps_dir = output_dir / "gaps"
                os.makedirs(gaps_dir, exist_ok=True)
                
                try:
                    # Create position skill targets
                    positions = {}
                    
                    # First, collect position skill requirements across the organization
                    for person_data in people_data:
                        if not person_data.profile:
                            continue
                            
                        position = person_data.profile.cargo
                        if not position:
                            continue
                            
                        if position not in positions:
                            positions[position] = {
                                "skills": {},
                                "counts": {},
                                "people": []
                            }
                            
                        positions[position]["people"].append(person_data)
                        
                        # Collect skills for this position
                        if person_data.career_progression and person_data.career_progression.skills_matrix:
                            for skill, level in person_data.career_progression.skills_matrix.items():
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
                    
                    # Perform gap analysis for each person
                    gap_results = []
                    
                    for person_data in people_data:
                        if not person_data.profile or not person_data.career_progression:
                            continue
                            
                        position = person_data.profile.cargo
                        if not position or position not in position_skill_targets:
                            continue
                            
                        target_skills = position_skill_targets[position]
                        if not target_skills or not person_data.career_progression.skills_matrix:
                            continue
                            
                        # Create skill matrices
                        current_matrix = SkillMatrix()
                        target_matrix = SkillMatrix()
                        
                        for skill_name, level in person_data.career_progression.skills_matrix.items():
                            current_matrix.add_skill(Skill(name=skill_name, level=level))
                            
                        for skill_name, level in target_skills.items():
                            target_matrix.add_skill(Skill(name=skill_name, level=level))
                            
                        # Calculate skill gaps
                        gaps, coverage = derive_skill_gap(current_matrix, target_matrix)
                        
                        # Save gap analysis to a file
                        person_gaps_file = gaps_dir / f"{person_data.name}_gaps.json"
                        
                        with open(person_gaps_file, "w") as f:
                            import json
                            json.dump({
                                "name": person_data.name,
                                "position": position,
                                "skill_coverage": coverage,
                                "gaps": gaps
                            }, f, indent=2)
                            
                        gap_results.append({
                            "name": person_data.name,
                            "position": position,
                            "skill_coverage": coverage,
                            "top_gaps": gaps[:5] if gaps else []
                        })
                        
                    # Create summary report
                    summary_file = gaps_dir / "gap_analysis_summary.md"
                    
                    with open(summary_file, "w") as f:
                        f.write("# Skill Gap Analysis Summary\n\n")
                        
                        f.write("| Name | Position | Skill Coverage | Top Gap |\n")
                        f.write("|------|----------|----------------|--------|\n")
                        
                        for result in sorted(gap_results, key=lambda x: x["skill_coverage"]):
                            top_gap = result["top_gaps"][0]["name"] if result["top_gaps"] else "None"
                            
                            f.write(f"| {result['name']} | {result['position']} | {result['skill_coverage']:.1f}% | {top_gap} |\n")
                            
                    logger.info(f"Skill gap analysis saved to: {gaps_dir}")
                    
                except Exception as e:
                    logger.error(f"Error performing skill gap analysis: {e}")
                    import traceback
                    traceback.print_exc()
                    
            if do_visualizations:
                logger.info("Generating skill visualizations...")
                viz_dir = output_dir / "visualizations"
                os.makedirs(viz_dir, exist_ok=True)
                
                try:
                    charts = generate_all_radar_charts(
                        data_list=people_data,
                        output_dir=str(viz_dir)
                    )
                    
                    # Create visualization index
                    index_file = viz_dir / "index.md"
                    
                    with open(index_file, "w") as f:
                        f.write("# Skill Visualization Index\n\n")
                        
                        f.write("## Individual Skill Charts\n\n")
                        for name, path in charts["individual_charts"].items():
                            f.write(f"- [{name}]({os.path.basename(path)})\n")
                            
                        f.write("\n## Team Skill Charts\n\n")
                        for name, path in charts["team_charts"].items():
                            f.write(f"- [{name}]({os.path.basename(path)})\n")
                            
                        f.write("\n## Skill Comparison Charts\n\n")
                        for name, path in charts["comparison_charts"].items():
                            f.write(f"- [{name}]({os.path.basename(path)})\n")
                            
                        f.write("\n## Skill Gap Charts\n\n")
                        for name, path in charts["gap_charts"].items():
                            f.write(f"- [{name}]({os.path.basename(path)})\n")
                            
                    logger.info(f"Skill visualizations saved to: {viz_dir}")
                    logger.info(f"Visualization index: {index_file}")
                    
                except Exception as e:
                    logger.error(f"Error generating skill visualizations: {e}")
                    
            logger.info("Skills analysis complete.")
            return 0
            
        except Exception as e:
            logger.error(f"Error executing skills analysis command: {e}")
            import traceback
            traceback.print_exc()
            return 1 