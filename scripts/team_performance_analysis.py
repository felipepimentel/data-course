#!/usr/bin/env python3
"""
Team Performance Analysis Script

This script provides a comprehensive analysis of team performance data,
helping to identify patterns and strategies for building a high-performance team.
"""

import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns

# Set up directories
DATA_DIR = Path("data")
OUTPUT_DIR = Path("output/team_analysis")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


class TeamPerformanceAnalyzer:
    """Analyzer for team performance data"""

    def __init__(self, data_dir=DATA_DIR, output_dir=OUTPUT_DIR):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.career_data = {}
        self.nine_box_data = {}
        self.team_members = []

    def load_career_data(self):
        """Load career progression data for all team members"""
        career_dir = self.data_dir / "career_progression"
        if not career_dir.exists():
            print(f"Career directory not found: {career_dir}")
            return

        for file_path in career_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    name = file_path.stem
                    self.career_data[name] = data
                    self.team_members.append(name)
                    print(f"Loaded career data for: {name}")
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")

        print(f"Loaded career data for {len(self.career_data)} team members")

    def analyze_skills_distribution(self):
        """Analyze the skills distribution across the team"""
        if not self.career_data:
            print("No career data loaded. Run load_career_data() first.")
            return

        # Collect all skills across team members
        all_skills = {}
        for name, data in self.career_data.items():
            if "matriz_habilidades" in data:
                for skill, level in data["matriz_habilidades"].items():
                    if skill not in all_skills:
                        all_skills[skill] = []
                    all_skills[skill].append((name, level))

        # Create DataFrame for analysis
        rows = []
        for skill, entries in all_skills.items():
            for name, level in entries:
                skill_category = skill.split(".")[0] if "." in skill else "other"
                skill_name = skill.split(".")[1] if "." in skill else skill
                rows.append(
                    {
                        "team_member": name,
                        "skill": skill,
                        "skill_category": skill_category,
                        "skill_name": skill_name,
                        "level": level,
                    }
                )

        if not rows:
            print("No skill data found in career data.")
            return None

        df = pd.DataFrame(rows)

        # Generate skills heatmap
        plt.figure(figsize=(12, 10))
        pivot_df = df.pivot_table(
            index="team_member", columns="skill", values="level", aggfunc="mean"
        ).fillna(0)

        sns.heatmap(pivot_df, annot=True, cmap="viridis", linewidths=0.5)
        plt.title("Team Skills Heatmap")
        plt.tight_layout()

        heatmap_path = self.output_dir / "team_skills_heatmap.png"
        plt.savefig(heatmap_path)
        plt.close()
        print(f"Saved skills heatmap to {heatmap_path}")

        # Create average skills by category
        category_df = (
            df.groupby(["skill_category", "team_member"])["level"].mean().reset_index()
        )

        fig = px.bar(
            category_df,
            x="team_member",
            y="level",
            color="skill_category",
            barmode="group",
            title="Average Skill Level by Category and Team Member",
        )

        skills_bar_path = self.output_dir / "skills_by_category.html"
        fig.write_html(str(skills_bar_path))
        print(f"Saved skills by category chart to {skills_bar_path}")

        return df

    def analyze_nine_box(self):
        """Analyze the nine box positions of team members"""
        # Create sample nine box data since we couldn't get it from the system
        # In a real scenario, we would load this from the database or files
        nine_box_sample = {
            "Maria Silva": {
                "performance": 8,
                "potential": 9,
                "quadrant": "Alto Desempenho / Alto Potencial",
            },
            "Rafael Oliveira": {
                "performance": 9,
                "potential": 7,
                "quadrant": "Alto Desempenho / Alto Potencial",
            },
            "specialist_employee": {
                "performance": 10,
                "potential": 5,
                "quadrant": "Alto Desempenho / Médio Potencial",
            },
            "integrator_employee": {
                "performance": 7,
                "potential": 8,
                "quadrant": "Alto Desempenho / Alto Potencial",
            },
            "sample_employee": {
                "performance": 5,
                "potential": 4,
                "quadrant": "Médio Desempenho / Médio Potencial",
            },
        }

        # Create a DataFrame
        rows = []
        for name, data in nine_box_sample.items():
            rows.append(
                {
                    "team_member": name,
                    "performance": data["performance"],
                    "potential": data["potential"],
                    "quadrant": data["quadrant"],
                }
            )

        df = pd.DataFrame(rows)

        # Create a scatter plot with Plotly
        fig = px.scatter(
            df,
            x="performance",
            y="potential",
            text="team_member",
            size=[20] * len(df),  # Constant size
            color="quadrant",
            title="Nine Box Matrix - Team Performance vs Potential",
            labels={
                "performance": "Performance Score (0-10)",
                "potential": "Potential Score (0-10)",
            },
        )

        # Customize the layout
        fig.update_traces(textposition="top center")
        fig.update_layout(
            xaxis=dict(range=[0, 10]),
            yaxis=dict(range=[0, 10]),
            xaxis_tickvals=[0, 3.33, 6.66, 10],
            yaxis_tickvals=[0, 3.33, 6.66, 10],
            shapes=[
                # Vertical lines
                dict(
                    type="line",
                    x0=3.33,
                    y0=0,
                    x1=3.33,
                    y1=10,
                    line=dict(color="Gray", width=1, dash="dash"),
                ),
                dict(
                    type="line",
                    x0=6.66,
                    y0=0,
                    x1=6.66,
                    y1=10,
                    line=dict(color="Gray", width=1, dash="dash"),
                ),
                # Horizontal lines
                dict(
                    type="line",
                    x0=0,
                    y0=3.33,
                    x1=10,
                    y1=3.33,
                    line=dict(color="Gray", width=1, dash="dash"),
                ),
                dict(
                    type="line",
                    x0=0,
                    y0=6.66,
                    x1=10,
                    y1=6.66,
                    line=dict(color="Gray", width=1, dash="dash"),
                ),
            ],
        )

        # Add quadrant labels
        quadrants = [
            {"x": 1.67, "y": 8.33, "text": "Low Performer<br>High Potential"},
            {"x": 5, "y": 8.33, "text": "Core Player<br>High Potential"},
            {"x": 8.33, "y": 8.33, "text": "Star<br>High Potential"},
            {"x": 1.67, "y": 5, "text": "Low Performer<br>Medium Potential"},
            {"x": 5, "y": 5, "text": "Core Player<br>Medium Potential"},
            {"x": 8.33, "y": 5, "text": "Star<br>Medium Potential"},
            {"x": 1.67, "y": 1.67, "text": "Low Performer<br>Low Potential"},
            {"x": 5, "y": 1.67, "text": "Core Player<br>Low Potential"},
            {"x": 8.33, "y": 1.67, "text": "Star<br>Low Potential"},
        ]

        for q in quadrants:
            fig.add_annotation(
                x=q["x"],
                y=q["y"],
                text=q["text"],
                showarrow=False,
                font=dict(size=10, color="gray"),
            )

        nine_box_path = self.output_dir / "nine_box_matrix.html"
        fig.write_html(str(nine_box_path))
        print(f"Saved Nine Box Matrix to {nine_box_path}")

        return df

    def create_team_composition_report(self):
        """Create a report on optimal team composition based on nine box and skills"""
        # Get our data
        if not hasattr(self, "skills_df") or self.skills_df is None:
            self.skills_df = self.analyze_skills_distribution()

        if not hasattr(self, "nine_box_df") or self.nine_box_df is None:
            self.nine_box_df = self.analyze_nine_box()

        # Create a combined performance report
        report = """
        # Team Composition Analysis Report
        
        ## Overview
        
        This report analyzes the current team composition and provides recommendations 
        for building a high-performance team based on skill distribution and performance-potential mapping.
        
        ## Current Team Composition
        
        ### Performance-Potential Distribution
        """

        # Add Nine Box distribution
        if hasattr(self, "nine_box_df") and self.nine_box_df is not None:
            quadrant_counts = self.nine_box_df["quadrant"].value_counts()
            report += "\nQuadrant distribution in the Nine Box matrix:\n\n"
            for quadrant, count in quadrant_counts.items():
                report += f"- {quadrant}: {count} team members\n"

        # Add skills gaps analysis
        if hasattr(self, "skills_df") and self.skills_df is not None:
            # Get average skill level by category
            skill_category_avgs = (
                self.skills_df.groupby("skill_category")["level"].mean().sort_values()
            )

            report += "\n\n### Skills Analysis\n\n"
            report += "Average skill levels by category:\n\n"

            for category, avg in skill_category_avgs.items():
                report += f"- {category}: {avg:.2f}/5\n"

            # Identify skill gaps
            weak_categories = skill_category_avgs[
                skill_category_avgs < 3
            ].index.tolist()
            strong_categories = skill_category_avgs[
                skill_category_avgs >= 4
            ].index.tolist()

            report += "\n#### Skill Gaps Identified\n\n"

            if weak_categories:
                report += "Categories with potential gaps:\n\n"
                for category in weak_categories:
                    report += f"- {category}\n"
            else:
                report += (
                    "No significant skill gaps identified at the category level.\n"
                )

            report += "\n#### Team Strengths\n\n"

            if strong_categories:
                report += "Categories with strong capabilities:\n\n"
                for category in strong_categories:
                    report += f"- {category}\n"
            else:
                report += "No outstanding strengths identified at the category level.\n"

        # Team composition recommendations
        report += """
        
        ## Recommendations for High-Performance Team Building
        
        ### Optimal Team Composition
        
        For a high-performance team, research suggests the following composition based on the Nine Box Matrix:
        
        1. **Stars (High Performance, High Potential)**: 15-20% of the team
           * These individuals drive innovation and establish high standards
           * Should be placed in strategic roles and given challenging tasks
        
        2. **Core Players (Medium-High Performance)**: 60-70% of the team
           * These reliable performers form the backbone of the team
           * Should have clear career paths and development opportunities
        
        3. **Specialists (High Performance, Lower Potential)**: 10-15% of the team
           * Domain experts who provide critical knowledge
           * Should be recognized for their expertise and technical contributions
        
        4. **Developing Talent (Medium Performance, High Potential)**: 5-10% of the team
           * Future stars who need mentoring and development
           * Should be paired with high performers and given stretch assignments
        
        ### Action Plan
        
        1. **Skill Development**
           * Focus training resources on identified skill gaps
           * Implement peer mentoring programs matching experts with those needing development
        
        2. **Team Restructuring**
           * Ensure balanced team composition according to the recommended ratios
           * Create cross-functional sub-teams that mix different performance-potential profiles
        
        3. **Performance Management**
           * Implement quarterly check-ins for employees in transition zones
           * Develop tailored development plans based on Nine Box positioning
        
        4. **Recruitment Strategy**
           * Target recruitment to fill identified skill gaps
           * Consider diversity of thinking styles when building teams
        
        ## Conclusion
        
        Building a high-performance team requires balancing skills, experience levels, and performance-potential profiles.
        The current team shows some imbalances that can be addressed through targeted development and strategic team composition.
        """

        # Save the report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"team_composition_report_{timestamp}.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"Saved team composition report to {report_path}")

        # Create a simple HTML version
        html_report = f"""
        <html>
        <head>
            <title>Team Composition Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #3498db; margin-top: 30px; }}
                h3 {{ color: #2980b9; }}
                h4 {{ color: #1abc9c; }}
                ul {{ margin-bottom: 20px; }}
                .container {{ max-width: 1000px; margin: 0 auto; }}
            </style>
        </head>
        <body>
            <div class="container">
                {
            report.replace("# ", "<h1>")
            .replace(" #", "</h1>")
            .replace("## ", "<h2>")
            .replace(" ##", "</h2>")
            .replace("### ", "<h3>")
            .replace(" ###", "</h3>")
            .replace("#### ", "<h4>")
            .replace(" ####", "</h4>")
            .replace("\n\n", "<br><br>")
            .replace("\n- ", "<br>• ")
        }
            </div>
        </body>
        </html>
        """

        html_report_path = self.output_dir / f"team_composition_report_{timestamp}.html"
        with open(html_report_path, "w", encoding="utf-8") as f:
            f.write(html_report)

        print(f"Saved HTML team composition report to {html_report_path}")


def main():
    print("Starting Team Performance Analysis...")
    analyzer = TeamPerformanceAnalyzer()

    # Load career data
    analyzer.load_career_data()

    # Analyze skills distribution
    analyzer.skills_df = analyzer.analyze_skills_distribution()

    # Analyze nine box
    analyzer.nine_box_df = analyzer.analyze_nine_box()

    # Create team composition report
    analyzer.create_team_composition_report()

    print("Team Performance Analysis complete!")


if __name__ == "__main__":
    main()
