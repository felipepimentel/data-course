# People Analytics

A tool for analyzing 360-degree evaluations and generating reports.

## Features

- Import evaluation data from JSON files
- Analyze evaluation results and compare with group averages
- Visualize results with various chart types (radar charts, heatmaps, etc.)
- Export results to different formats (Excel, HTML, JSON)
- Generate team reports and comparisons
- Validate and backup data

## Installation

### From Source

```bash
git clone https://github.com/yourusername/peopleanalytics.git
cd peopleanalytics
pip install -e .
```

### Using pip

```bash
pip install peopleanalytics
```

## Usage

### Command Line Interface

#### Global Options

```bash
peopleanalytics [--base-path PATH] [--color-scheme {default,corporate,monochrome}] [--no-cache] [--parallel] [--workers N] COMMAND
```

#### List Commands

```bash
# List all people in the database
peopleanalytics list people [--years YEAR [YEAR ...]]

# List all available years
peopleanalytics list years

# List all evaluation criteria
peopleanalytics list criteria [--year YEAR]

# Show database statistics
peopleanalytics list stats
```

#### Comparison Commands

```bash
# Compare evaluations for a specific year
peopleanalytics compare YEAR [--filter PERSON [PERSON ...]] [--output PATH] [--format {csv,png,all}]

# Generate historical report for a person
peopleanalytics historical PERSON [--years YEAR [YEAR ...]] [--output PATH] [--format {csv,png,all}]
```

#### Data Management Commands

```bash
# Validate evaluation data
peopleanalytics validate [--output PATH] [--fix] [--verbose] [--html]

# Export evaluation data
peopleanalytics export {excel,csv,json} [--output PATH] [--years YEAR [YEAR ...]] [--people PERSON [PERSON ...]]

# Data pipeline operations
peopleanalytics pipeline {import,backup,export,fix} [--file FILE] [--directory DIR] [--pattern PATTERN] [--overwrite] [--sequential] [--output PATH] [--output-dir DIR]
```

#### Advanced Filtering

```bash
# Advanced filtering options
peopleanalytics filter [--name-regex PATTERN] [--behavior-regex PATTERN] [--min-score SCORE] [--max-score SCORE] [--concepts CONCEPT [CONCEPT ...]] [--years YEAR [YEAR ...]] [--output PATH] [--format {csv,excel,json,html}]
```

#### Team Analysis

```bash
# List all teams and managers
peopleanalytics teams --team-file FILE list

# Generate manager report
peopleanalytics teams --team-file FILE manager MANAGER YEAR [--output PATH]

# Compare team performance
peopleanalytics teams --team-file FILE compare TEAM YEAR [--output PATH]
```

#### Visualization Commands

```bash
# Generate visualizations
peopleanalytics visualize --type {radar,heatmap,interactive} --output PATH [--data-file FILE] [--title TITLE] [--person PERSON] [--year YEAR] [--people PERSON [PERSON ...]]
```

### Python API

```python
from peopleanalytics.data_pipeline import DataPipeline
from peopleanalytics.evaluation_analyzer import EvaluationAnalyzer
from peopleanalytics.visualization import Visualization

# Initialize components
data_pipeline = DataPipeline("path/to/database")
analyzer = EvaluationAnalyzer("path/to/database")
visualizer = Visualization()

# Import data
data_pipeline.ingest_directory("path/to/data")

# Analyze data
results = analyzer.analyze_person("John Doe", 2023)

# Compare with group
comparison = analyzer.compare_with_group("John Doe", 2023)

# Generate visualizations
visualizer.generate_radar_chart(comparison, "radar_chart.png")
visualizer.generate_heatmap(comparison, "heatmap.png")
visualizer.generate_interactive_html(comparison, "report.html")
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 