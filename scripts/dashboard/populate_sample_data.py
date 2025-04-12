#!/usr/bin/env python3
"""
Populate Sample Data

This script creates sample team members and skills data
to demonstrate the People Analytics Dashboard functionality.
"""

import json
from datetime import datetime
from pathlib import Path

# Set up directories
DATA_DIR = Path("data")
CAREER_DIR = DATA_DIR / "career_progression"

# Ensure directories exist
CAREER_DIR.mkdir(exist_ok=True, parents=True)

# Sample team members data
team_members = [
    {
        "name": "Ana Silva",
        "position": "Team Lead",
        "performance": 9,
        "potential": 8,
        "skills": {
            "technical.python": 5,
            "technical.data_analysis": 4,
            "technical.leadership": 5,
            "soft.communication": 4,
            "soft.teamwork": 5,
            "soft.problem_solving": 4,
        },
    },
    {
        "name": "João Oliveira",
        "position": "Senior Developer",
        "performance": 10,
        "potential": 5,
        "skills": {
            "technical.python": 5,
            "technical.architecture": 5,
            "technical.backend": 5,
            "soft.mentoring": 4,
            "soft.communication": 3,
            "soft.problem_solving": 5,
        },
    },
    {
        "name": "Maria Santos",
        "position": "Data Scientist",
        "performance": 7,
        "potential": 9,
        "skills": {
            "technical.python": 4,
            "technical.machine_learning": 5,
            "technical.data_analysis": 5,
            "soft.communication": 4,
            "soft.teamwork": 3,
            "soft.innovation": 5,
        },
    },
    {
        "name": "Pedro Costa",
        "position": "Junior Developer",
        "performance": 5,
        "potential": 8,
        "skills": {
            "technical.python": 3,
            "technical.frontend": 4,
            "technical.testing": 3,
            "soft.communication": 4,
            "soft.teamwork": 5,
            "soft.adaptability": 5,
        },
    },
    {
        "name": "Carla Ferreira",
        "position": "UX Designer",
        "performance": 8,
        "potential": 6,
        "skills": {
            "technical.design": 5,
            "technical.user_research": 4,
            "technical.prototyping": 5,
            "soft.creativity": 5,
            "soft.communication": 4,
            "soft.empathy": 5,
        },
    },
]


def get_quadrant_name(performance, potential):
    """Get the quadrant name based on performance and potential scores"""
    perf_level = (
        "Baixo" if performance < 3.33 else "Médio" if performance < 6.66 else "Alto"
    )
    pot_level = "Baixo" if potential < 3.33 else "Médio" if potential < 6.66 else "Alto"

    return f"{perf_level} Desempenho / {pot_level} Potencial"


def create_team_member_data():
    """Create sample team members data files"""

    today = datetime.now().strftime("%Y-%m-%d")
    created_count = 0

    for member in team_members:
        name = member["name"]
        file_path = CAREER_DIR / f"{name}.json"

        if file_path.exists():
            print(f"File already exists for {name}, skipping...")
            continue

        # Create member data structure
        member_data = {
            "nome": name,
            "cargo_atual": member["position"],
            "matriz_habilidades": member["skills"],
            "nine_box": {
                "performance": member["performance"],
                "potential": member["potential"],
                "date": today,
                "quadrant": get_quadrant_name(
                    member["performance"], member["potential"]
                ),
            },
            "eventos_carreira": [],
            "metas_carreira": [
                {
                    "title": "Próxima meta de carreira",
                    "target_date": "2024-12-31",
                    "details": "Meta personalizada com base no perfil",
                    "progress": 20,
                    "status": "in_progress",
                }
            ],
            "certificacoes": [],
            "mentoria": [],
        }

        # Save to file
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(member_data, f, indent=2, ensure_ascii=False)
            print(f"Created sample data for {name}")
            created_count += 1
        except Exception as e:
            print(f"Error creating data for {name}: {str(e)}")

    print(f"\nSuccessfully created {created_count} team member files in {CAREER_DIR}")
    print("You can now run the dashboard to view the team analysis:")
    print("python scripts/run_dashboard.py")


if __name__ == "__main__":
    print("Creating sample team data...")
    create_team_member_data()
