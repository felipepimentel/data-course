#!/usr/bin/env python
import json
import os
from pathlib import Path

from peopleanalytics.domain.report_generator import ReportGenerator


def main():
    """Test script to generate pattern reports for test users"""
    print("Pattern Report Generator Test")

    # Define paths
    data_dirs = [Path("data"), Path("data/test")]
    output_dir = Path("output")

    # Create report generator
    report_generator = ReportGenerator()

    # Test users to process
    test_users = [
        ("TestPerson", "2023"),
        ("TestUser1", "2023"),
        ("TestUser2", "2023"),
        ("sample_person", "2023"),
    ]

    # Process each test user
    for pessoa_name, ano_name in test_users:
        print(f"\nProcessing {pessoa_name}/{ano_name}")

        # Try to find data file in each data directory
        found = False
        for data_dir in data_dirs:
            json_path = data_dir / pessoa_name / ano_name / "resultado.json"
            if json_path.exists():
                found = True
                break

        if not found:
            print(f"  - Data file not found for {pessoa_name}/{ano_name}")
            continue

        # Create output directory
        person_dir = output_dir / pessoa_name / ano_name / "reports"
        os.makedirs(person_dir, exist_ok=True)

        # Load data
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"  - Loaded data from {json_path}")
        except Exception as e:
            print(f"  - Error loading data: {e}")
            continue

        # Generate pattern report
        try:
            pattern_report_path = os.path.join(person_dir, "patterns_correlations.md")
            pattern_content = report_generator.generate_patterns_report(
                data, pessoa_name, ano_name
            )
            with open(pattern_report_path, "w", encoding="utf-8") as f:
                f.write(pattern_content)
            print(f"  - Generated pattern report: {pattern_report_path}")
        except Exception as e:
            print(f"  - Error generating pattern report: {e}")

    print("\nTest completed!")


if __name__ == "__main__":
    main()
