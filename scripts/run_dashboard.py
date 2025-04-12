#!/usr/bin/env python3
"""
Run the People Analytics Dashboard

This script launches the People Analytics Dashboard application
providing an interface for managing and visualizing team data.
"""

import os
import sys
from pathlib import Path

# Ensure we're in the project root directory
project_dir = Path(__file__).parent.parent
os.chdir(project_dir)

# Ensure required directories exist
data_dir = Path("data")
career_dir = data_dir / "career_progression"
output_dir = Path("output")

for directory in [data_dir, career_dir, output_dir]:
    directory.mkdir(exist_ok=True, parents=True)

try:
    # Try importing dash to check if installed
    import dash
    import dash_bootstrap_components as dbc
except ImportError:
    print("Error: Required packages not installed. Please run:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def main():
    """Run the dashboard application"""
    try:
        # Import dashboard_app directly from the dashboard directory
        from scripts.dashboard.dashboard_app import app

        print("==" * 30)
        print("People Analytics Dashboard")
        print("==" * 30)
        print("\nAccess the dashboard at: http://127.0.0.1:8050/")
        print("\nPress Ctrl+C to stop the server")

        # Run the dashboard
        app.run(debug=True, host="127.0.0.1", port=8050)
    except ImportError as e:
        print(f"Error importing dashboard_app: {e}")
        print("Make sure scripts/dashboard/dashboard_app.py exists")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting dashboard: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
