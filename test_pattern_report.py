#!/usr/bin/env python3

import json
import os
import sys

from peopleanalytics.domain.report_generator import ReportGenerator


def main():
    # Initialize report generator
    rg = ReportGenerator()

    # Define test user and year
    pessoa_name = "TestUser1"
    ano = "2023"

    # Load test data
    data_path = f"data/test/{pessoa_name}/{ano}/resultado.json"
    if not os.path.exists(data_path):
        print(f"Error: Test data not found at {data_path}")
        data_path = f"tests/data/{pessoa_name}/{ano}/resultado.json"
        if not os.path.exists(data_path):
            print(f"Error: Test data not found at {data_path}")
            return 1

    print(f"Loading data from {data_path}")
    with open(data_path, "r") as f:
        data = json.load(f)

    # Generate patterns report
    print("Generating patterns report...")
    report = rg.generate_patterns_report(data, pessoa_name, ano)

    # Save report
    output_dir = f"output/{pessoa_name}/{ano}/reports"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/patterns_report.md"

    with open(output_path, "w") as f:
        f.write(report)

    print(f"Report generated at {output_path}")

    # Also check if data directory exists for synthetic users
    synthetic_data = "data/synthetic/pessoa1/2022/resultado.json"
    if os.path.exists(synthetic_data):
        print(f"Found synthetic data at {synthetic_data}")
        with open(synthetic_data, "r") as f:
            syn_data = json.load(f)

        syn_report = rg.generate_patterns_report(syn_data, "pessoa1", "2022")
        syn_output_dir = "output/pessoa1/2022/reports"
        os.makedirs(syn_output_dir, exist_ok=True)
        with open(f"{syn_output_dir}/patterns_report.md", "w") as f:
            f.write(syn_report)
        print(f"Synthetic user report generated at {syn_output_dir}/patterns_report.md")

    return 0


if __name__ == "__main__":
    sys.exit(main())
