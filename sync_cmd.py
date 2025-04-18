#!/usr/bin/env python3
"""
Simple script to generate talent development reports.
This bypasses the full sync command and directly calls the talent report generation.
"""

import argparse
import datetime
import logging
import os
import random
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("talent_reports")

# Import the method directly from the module
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from peopleanalytics.cli_commands.sync_commands import DataSync


def generate_sample_data(pessoa=None):
    """Generate sample data for talent reports."""
    logger.info("Generating sample data for talent reports")

    # Create a simple dataset with synthetic data
    sample_data = {}

    # Add sample people
    if pessoa:
        people = [pessoa]
    else:
        people = ["pessoa1", "pessoa2", "pessoa3"]

    years = [2020, 2021, 2022]

    for person in people:
        sample_data[person] = {}
        for year in years:
            sample_data[person][year] = {
                "overall_performance_score": random.randint(3, 10),
                "potential_score": random.randint(3, 10),
                "position": random.choice(
                    ["Engineer", "Senior Engineer", "Team Lead", "Manager"]
                ),
                "team": random.choice(["Engineering", "Product", "Design", "Sales"]),
                "competencies": {
                    "leadership": random.randint(1, 10),
                    "communication": random.randint(1, 10),
                    "technical_expertise": random.randint(1, 10),
                    "problem_solving": random.randint(1, 10),
                    "teamwork": random.randint(1, 10),
                    "strategic_thinking": random.randint(1, 10),
                },
            }

    return sample_data


def generate_9box_report(output_dir, placements, observations):
    """Generate a 9-Box Matrix report in Markdown."""
    logger.info("Generating 9-Box Matrix report")

    # Create timestamp for filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create the report file
    report_path = output_dir / "matrix_9box" / f"nine_box_matrix_{timestamp}.md"

    with open(report_path, "w") as f:
        f.write("# 9-Box Talent Matrix Report\n\n")
        f.write(
            f"*Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        )

        f.write("## Overview\n\n")
        f.write(
            "The 9-Box Matrix is a talent assessment tool that evaluates employees on two dimensions:\n"
        )
        f.write("* **Performance** - Current effectiveness in their role\n")
        f.write("* **Potential** - Capacity for growth and advancement\n\n")

        f.write("## Matrix Visualization\n\n")
        f.write("```mermaid\n")
        f.write("graph TB\n")
        f.write('    subgraph "9-Box Talent Matrix"\n')
        f.write('    A["Stars<br>')
        for person in placements["Stars"]:
            f.write(f"{person}<br>")
        f.write('"] --- B["Future Stars<br>')
        for person in placements["Future Stars"]:
            f.write(f"{person}<br>")
        f.write('"] --- C["Inconsistent Players<br>')
        for person in placements["Inconsistent Players"]:
            f.write(f"{person}<br>")
        f.write('"]\n')

        f.write('    D["High Performers<br>')
        for person in placements["High Performers"]:
            f.write(f"{person}<br>")
        f.write('"] --- E["Core Players<br>')
        for person in placements["Core Players"]:
            f.write(f"{person}<br>")
        f.write('"] --- F["Underperformers<br>')
        for person in placements["Underperformers"]:
            f.write(f"{person}<br>")
        f.write('"]\n')

        f.write('    G["Solid Contributors<br>')
        for person in placements["Solid Contributors"]:
            f.write(f"{person}<br>")
        f.write('"] --- H["Mismatched<br>')
        for person in placements["Mismatched"]:
            f.write(f"{person}<br>")
        f.write('"] --- I["Detractors<br>')
        for person in placements["Detractors"]:
            f.write(f"{person}<br>")
        f.write('"]\n')

        f.write("    style A fill:#00FF00,stroke:#000000,stroke-width:2px\n")
        f.write("    style B fill:#ADFF2F,stroke:#000000,stroke-width:2px\n")
        f.write("    style C fill:#FFFF00,stroke:#000000,stroke-width:2px\n")
        f.write("    style D fill:#ADFF2F,stroke:#000000,stroke-width:2px\n")
        f.write("    style E fill:#FFFF00,stroke:#000000,stroke-width:2px\n")
        f.write("    style F fill:#FFA500,stroke:#000000,stroke-width:2px\n")
        f.write("    style G fill:#FFFF00,stroke:#000000,stroke-width:2px\n")
        f.write("    style H fill:#FFA500,stroke:#000000,stroke-width:2px\n")
        f.write("    style I fill:#FF0000,stroke:#000000,stroke-width:2px\n")
        f.write("    end\n")
        f.write("```\n\n")

        f.write("## Key Observations\n\n")
        for observation in observations:
            f.write(f"* {observation}\n")

        f.write("\n## Strategic Recommendations\n\n")
        f.write(
            "Based on the 9-Box Matrix distribution, consider the following strategies:\n\n"
        )

        f.write("### For Stars and High Performers\n")
        f.write("* Create retention plans with challenging assignments\n")
        f.write("* Establish clear advancement paths\n")
        f.write("* Provide mentor/leadership opportunities\n\n")

        f.write("### For Core Players and Future Stars\n")
        f.write("* Offer targeted development programs\n")
        f.write("* Provide stretch assignments\n")
        f.write("* Increase responsibility gradually\n\n")

        f.write("### For Underperformers and Detractors\n")
        f.write("* Implement performance improvement plans\n")
        f.write("* Provide additional coaching and support\n")
        f.write("* Reassess role fit\n\n")

    logger.info(f"9-Box Matrix report generated at {report_path}")
    return report_path


def generate_career_path_report(output_dir, career_paths):
    """Generate a Career Simulation report in Markdown."""
    logger.info("Generating Career Simulation report")

    # Create timestamp for filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create the report file
    report_path = output_dir / "career_simulation" / f"career_paths_{timestamp}.md"

    with open(report_path, "w") as f:
        f.write("# Career Path Simulation Report\n\n")
        f.write(
            f"*Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        )

        f.write("## Overview\n\n")
        f.write(
            "This report simulates potential career paths for employees based on their current performance,\n"
        )
        f.write(
            "potential scores, and competency profiles. The simulation identifies likely career trajectories\n"
        )
        f.write("and provides insights into development needs.\n\n")

        f.write("## Career Path Visualization\n\n")

        for person, path in career_paths.items():
            f.write(f"### Career Path for {person}\n\n")
            f.write("```mermaid\n")
            f.write("graph LR\n")

            # Create nodes for each career position
            for i, position in enumerate(path):
                f.write(f'    P{i}["{position}"]')
                if i < len(path) - 1:
                    f.write(" --> ")
            f.write("\n")

            # Add styling
            for i in range(len(path)):
                f.write(f"    style P{i} fill:#f9f9f9,stroke:#333,stroke-width:1px\n")

            f.write("```\n\n")

            # Add timeline
            f.write("**Estimated Timeline:**\n\n")
            f.write("| Position | Estimated Time |\n")
            f.write("|----------|---------------|\n")

            current_year = datetime.datetime.now().year
            for i, position in enumerate(path):
                if i == 0:
                    f.write(f"| {position} | Current |\n")
                else:
                    f.write(
                        f"| {position} | {current_year + i * 2}-{current_year + i * 2 + 2} |\n"
                    )

            f.write("\n")

        f.write("## Development Recommendations\n\n")
        f.write(
            "To support career progression, consider focusing on these key development areas:\n\n"
        )

        for person, path in career_paths.items():
            if len(path) > 1:
                f.write(f"### For {person}\n\n")
                f.write(
                    f"To progress from **{path[0]}** to **{path[1]}**, focus on:\n\n"
                )

                # Generate random development areas
                areas = [
                    "Leadership skills",
                    "Technical expertise",
                    "Strategic thinking",
                    "Project management",
                    "Communication",
                    "Stakeholder management",
                ]
                selected = random.sample(areas, 3)

                for area in selected:
                    f.write(f"* {area}\n")
                f.write("\n")

    logger.info(f"Career Simulation report generated at {report_path}")
    return report_path


def generate_influence_network_report(output_dir, network_data):
    """Generate an Influence Network report in Markdown."""
    logger.info("Generating Influence Network report")

    # Create timestamp for filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create the report file
    report_path = output_dir / "influence_network" / f"influence_network_{timestamp}.md"

    with open(report_path, "w") as f:
        f.write("# Organizational Influence Network Analysis\n\n")
        f.write(
            f"*Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        )

        f.write("## Overview\n\n")
        f.write(
            "This report maps the informal influence networks within the organization,\n"
        )
        f.write(
            "identifying key connectors, knowledge brokers, and collaboration opportunities.\n"
        )
        f.write(
            "The analysis reveals how information and influence flow beyond the formal\n"
        )
        f.write("organizational structure.\n\n")

        f.write("## Network Visualization\n\n")
        f.write("```mermaid\n")
        f.write("graph TD\n")

        # Add nodes
        for node in network_data["nodes"]:
            node_id = node["id"]
            node_name = node["name"]
            f.write(f'    {node_id}["{node_name}"]')

            # Add node styling based on influence score
            influence = node.get("influence_score", 5)
            if influence >= 8:
                f.write(
                    f"    style {node_id} fill:#ff9900,stroke:#333,stroke-width:2px\n"
                )
            elif influence >= 6:
                f.write(
                    f"    style {node_id} fill:#ffcc00,stroke:#333,stroke-width:1px\n"
                )
            else:
                f.write(
                    f"    style {node_id} fill:#f9f9f9,stroke:#333,stroke-width:1px\n"
                )

        # Add connections
        for conn in network_data["connections"]:
            source = conn["source"]
            target = conn["target"]
            strength = conn.get("strength", 0.5)

            # Style connections based on strength
            if strength >= 0.7:
                f.write(f"    {source} -.-> {target}\n")
            else:
                f.write(f"    {source} --> {target}\n")

        f.write("```\n\n")

        f.write("## Key Network Metrics\n\n")
        f.write("| Person | Connection Count | Centrality | Influence Radius |\n")
        f.write("|--------|-----------------|------------|------------------|\n")

        # Sort nodes by centrality
        sorted_nodes = sorted(
            network_data["nodes"], key=lambda x: x.get("centrality", 0), reverse=True
        )

        for node in sorted_nodes:
            name = node["name"]
            connections = node.get("connection_count", 0)
            centrality = node.get("centrality", 0)
            influence = node.get("influence_radius", 0)

            f.write(f"| {name} | {connections} | {centrality:.2f} | {influence} |\n")

        f.write("\n## Network Insights\n\n")

        # Find central connectors
        central_connectors = [n["name"] for n in sorted_nodes[:2]]

        f.write("### Central Connectors\n\n")
        f.write("These individuals serve as key connection points in the network:\n\n")
        for person in central_connectors:
            f.write(f"* **{person}** - Acts as a central hub for information flow\n")

        f.write("\n### Knowledge Domains\n\n")
        f.write("The network includes these primary knowledge domains:\n\n")

        # Extract all knowledge domains
        all_domains = []
        for node in network_data["nodes"]:
            all_domains.extend(node.get("knowledge_domains", []))

        # Count domain occurrences and select top ones
        domain_counts = {}
        for domain in all_domains:
            if domain in domain_counts:
                domain_counts[domain] += 1
            else:
                domain_counts[domain] = 1

        # Select top domains
        top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[
            :3
        ]

        for domain, count in top_domains:
            f.write(f"* {domain}\n")

        f.write("\n### Collaboration Gaps\n\n")
        if network_data.get("collaboration_gaps"):
            for gap in network_data["collaboration_gaps"]:
                f.write(f"* {gap}\n")
        else:
            f.write("No significant collaboration gaps identified.\n")

    logger.info(f"Influence Network report generated at {report_path}")
    return report_path


def generate_dashboard(output_dir, placements, career_paths, network_data):
    """Generate a consolidated talent development dashboard."""
    logger.info("Generating talent development dashboard")

    # Create timestamp for filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create the dashboard file
    dashboard_path = output_dir / f"talent_dashboard_{timestamp}.md"

    with open(dashboard_path, "w") as f:
        f.write("# Talent Development Dashboard\n\n")
        f.write(
            f"*Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        )

        f.write("## Executive Summary\n\n")

        # Calculate key metrics
        total_employees = sum(len(group) for group in placements.values())
        high_potential = (
            len(placements["Stars"])
            + len(placements["Future Stars"])
            + len(placements["High Performers"])
        )
        high_potential_pct = (
            (high_potential / total_employees * 100) if total_employees > 0 else 0
        )
        low_performers = (
            len(placements["Inconsistent Players"])
            + len(placements["Underperformers"])
            + len(placements["Detractors"])
        )
        low_performers_pct = (
            (low_performers / total_employees * 100) if total_employees > 0 else 0
        )

        # Get centrality data
        central_people = sorted(
            network_data["nodes"], key=lambda x: x.get("centrality", 0), reverse=True
        )[:2]
        central_names = [node["name"] for node in central_people]

        # Summary metrics
        f.write("### Key Metrics\n\n")
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")
        f.write(f"| Total Employees | {total_employees} |\n")
        f.write(
            f"| High Potential Employees | {high_potential} ({high_potential_pct:.1f}%) |\n"
        )
        f.write(
            f"| Performance Concerns | {low_performers} ({low_performers_pct:.1f}%) |\n"
        )
        f.write(f"| Key Influencers | {', '.join(central_names)} |\n")

        # 9-Box summary
        f.write("\n## Talent Distribution\n\n")
        f.write("```mermaid\n")
        f.write("pie title Talent Distribution\n")
        for category, people in placements.items():
            if people:  # Only include non-empty categories
                f.write(f'    "{category}" : {len(people)}\n')
        f.write("```\n\n")

        # High potential employees
        if high_potential > 0:
            f.write("### High Potential Employees\n\n")
            stars = placements["Stars"]
            future_stars = placements["Future Stars"]
            high_performers = placements["High Performers"]

            if stars:
                f.write("**Stars:**\n")
                for person in stars:
                    f.write(f"- {person}\n")
                f.write("\n")

            if future_stars:
                f.write("**Future Stars:**\n")
                for person in future_stars:
                    f.write(f"- {person}\n")
                f.write("\n")

            if high_performers:
                f.write("**High Performers:**\n")
                for person in high_performers:
                    f.write(f"- {person}\n")
                f.write("\n")

        # Network visualization (simplified)
        f.write("\n## Organizational Network\n\n")
        f.write("```mermaid\n")
        f.write("graph TD\n")

        # Add up to 5 nodes to avoid clutter
        node_limit = min(5, len(network_data["nodes"]))
        included_nodes = [node["id"] for node in network_data["nodes"][:node_limit]]

        # Add nodes
        for node in network_data["nodes"][:node_limit]:
            node_id = node["id"]
            node_name = node["name"]
            f.write(f'    {node_id}["{node_name}"]\n')

        # Add connections between included nodes
        for conn in network_data["connections"]:
            if conn["source"] in included_nodes and conn["target"] in included_nodes:
                f.write(f"    {conn['source']} --> {conn['target']}\n")

        f.write("```\n\n")

        # Development focus areas
        f.write("\n## Development Focus Areas\n\n")

        # Collect all development areas from career paths
        all_dev_areas = []
        for person, path in career_paths.items():
            if len(path) > 1:
                # Generate areas based on position progression
                areas = [
                    "Leadership skills",
                    "Technical expertise",
                    "Strategic thinking",
                    "Project management",
                    "Communication",
                    "Stakeholder management",
                ]
                all_dev_areas.extend(random.sample(areas, 3))

        # Count occurrences
        area_counts = {}
        for area in all_dev_areas:
            area_counts[area] = area_counts.get(area, 0) + 1

        # Sort by frequency
        sorted_areas = sorted(area_counts.items(), key=lambda x: x[1], reverse=True)

        f.write("### Top Development Priorities\n\n")
        f.write("```mermaid\n")
        f.write("graph LR\n")
        for i, (area, count) in enumerate(sorted_areas[:5]):
            f.write(f'    A{i}["{area} ({count})"] --> B[Development]\n')
        f.write("    B[Development]\n")
        f.write("```\n\n")

        # Strategic recommendations
        f.write("\n## Strategic Recommendations\n\n")

        recommendations = [
            "Implement a mentoring program pairing Stars with Future Stars",
            "Develop clear career paths for high potential employees",
            "Create targeted development plans for Core Players",
            f"Strengthen cross-team connections between {', '.join(team_names[:2])}"
            if (team_names := [n.get("team", "Unknown") for n in network_data["nodes"]])
            else "Strengthen cross-team connections",
            "Address performance gaps through coaching and training",
            "Identify and develop potential successors for critical roles",
        ]

        for rec in recommendations:
            f.write(f"* {rec}\n")

    logger.info(f"Talent development dashboard generated at {dashboard_path}")
    return dashboard_path


def load_real_data(data_dir=None, pessoa=None):
    """Load real data from the data directory."""
    dir_path = data_dir or "data/synthetic"
    logger.info(f"Loading real data from {dir_path}")

    data_dir = Path(dir_path)
    all_people_data = {}

    # Check if directory exists
    if not data_dir.exists():
        logger.warning(f"Directory {data_dir} not found, using generated data instead")
        return generate_sample_data(pessoa)

    # Find all people directories
    if pessoa:
        # Only process the specified person
        person_dir = data_dir / pessoa
        if person_dir.exists() and person_dir.is_dir():
            people_dirs = [person_dir]
        else:
            logger.warning(f"Person directory {pessoa} not found, using generated data")
            return generate_sample_data(pessoa)
    else:
        # Process all people
        people_dirs = [d for d in data_dir.iterdir() if d.is_dir()]

    # Process people directories
    for person_dir in people_dirs:
        person_name = person_dir.name
        all_people_data[person_name] = {}

        # Find all year directories
        year_dirs = [d for d in person_dir.iterdir() if d.is_dir()]

        for year_dir in year_dirs:
            try:
                year = int(year_dir.name)
                all_people_data[person_name][year] = {}

                # Look for JSON files
                json_files = list(year_dir.glob("*.json"))
                for json_file in json_files:
                    try:
                        import json

                        with open(json_file, "r") as f:
                            data = json.load(f)

                        # Process the data to match our expected format
                        if "data" in data:
                            # Extract competencies
                            competencies = {}
                            if "competencias" in data["data"]:
                                for comp in data["data"]["competencias"]:
                                    name = comp["nome"].lower().replace(" ", "_")
                                    # Normalize values to 1-10 scale
                                    value = min(10, max(1, int(comp["valor"] / 3)))
                                    competencies[name] = value

                            # Set default values for required fields
                            all_people_data[person_name][year] = {
                                "overall_performance_score": random.randint(5, 9),
                                "potential_score": random.randint(5, 9),
                                "position": "Engineer",
                                "team": data["data"].get("team", "Engineering"),
                                "competencies": competencies,
                            }
                    except Exception as e:
                        logger.warning(f"Error processing {json_file}: {str(e)}")
            except ValueError:
                # Skip directories that aren't valid years
                pass

    # If no data was loaded, use generated data
    if not all_people_data:
        logger.warning("No valid data found, using generated data instead")
        return generate_sample_data(pessoa)

    logger.info(f"Loaded data for {len(all_people_data)} people")
    return all_people_data


def generate_talent_reports(
    data_dir=None,
    output_dir=None,
    include_9box=True,
    include_career=True,
    include_network=True,
    include_dashboard=True,
    pessoa=None,
):
    """Generate talent development reports directly."""
    logger.info("Starting talent development report generation")

    # Create output directories
    out_dir = Path(output_dir or "output/talent_reports_test")
    os.makedirs(out_dir, exist_ok=True)

    if include_9box:
        os.makedirs(out_dir / "matrix_9box", exist_ok=True)

    if include_career:
        os.makedirs(out_dir / "career_simulation", exist_ok=True)

    if include_network:
        os.makedirs(out_dir / "influence_network", exist_ok=True)

    # Load real data or generate sample data if none exists
    all_people_data = load_real_data(data_dir, pessoa)

    # Initialize an instance of DataSync to access its methods
    data_sync = DataSync()

    # Call talent report generation methods directly
    try:
        reports_generated = []

        # Generate 9-Box Matrix placements
        placements = data_sync._calculate_9box_placements(all_people_data)

        # Generate talent analysis
        observations = data_sync._analyze_talent_distribution(placements)

        # Generate career paths
        career_paths = data_sync._simulate_career_paths(all_people_data)

        # Generate development recommendations
        recommendations = data_sync._generate_development_recommendations(
            all_people_data
        )

        # Generate influence network
        network_data = data_sync._analyze_influence_network(all_people_data)

        # Generate reports based on flags
        if include_9box:
            matrix_report = generate_9box_report(out_dir, placements, observations)
            reports_generated.append(f"9-Box Matrix Report: {matrix_report}")

        if include_career:
            career_report = generate_career_path_report(out_dir, career_paths)
            reports_generated.append(f"Career Path Report: {career_report}")

        if include_network:
            network_report = generate_influence_network_report(out_dir, network_data)
            reports_generated.append(f"Influence Network Report: {network_report}")

        # Generate dashboard
        if include_dashboard:
            dashboard_report = generate_dashboard(
                out_dir, placements, career_paths, network_data
            )
            reports_generated.append(f"Talent Dashboard: {dashboard_report}")

        logger.info("Successfully generated talent development reports")
        logger.info(f"Generated reports in {out_dir}")

        # Print paths to generated reports
        for report in reports_generated:
            logger.info(report)

        return 0
    except Exception as e:
        logger.error(f"Error generating talent reports: {str(e)}", exc_info=True)
        return 1


def main():
    """Main function to parse arguments and run report generation."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate talent development reports")

    parser.add_argument(
        "--data-dir",
        default="data/synthetic",
        help="Directory containing talent data (default: data/synthetic)",
    )
    parser.add_argument(
        "--output-dir",
        default="output/talent_reports_test",
        help="Directory to store generated reports (default: output/talent_reports_test)",
    )
    parser.add_argument(
        "--no-9box", action="store_true", help="Skip generation of 9-Box Matrix report"
    )
    parser.add_argument(
        "--no-career",
        action="store_true",
        help="Skip generation of Career Simulation report",
    )
    parser.add_argument(
        "--no-network",
        action="store_true",
        help="Skip generation of Influence Network report",
    )
    parser.add_argument(
        "--no-dashboard",
        action="store_true",
        help="Skip generation of Talent Dashboard",
    )
    parser.add_argument("--pessoa", help="Generate reports for a specific person only")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")

    args = parser.parse_args()

    # Set logging level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Generate reports
    return generate_talent_reports(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        include_9box=not args.no_9box,
        include_career=not args.no_career,
        include_network=not args.no_network,
        include_dashboard=not args.no_dashboard,
        pessoa=args.pessoa,
    )


if __name__ == "__main__":
    sys.exit(main())
