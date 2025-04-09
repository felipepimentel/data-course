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

```bash
# Import evaluation data
peopleanalytics import path/to/data

# List available data
peopleanalytics list people
peopleanalytics list years
peopleanalytics list stats

# Analyze data for a specific person
peopleanalytics analyze --person "John Doe" --year 2023

# Generate visualizations
peopleanalytics visualize --person "John Doe" --year 2023 --type radar
peopleanalytics visualize --person "John Doe" --year 2023 --type heatmap

# Export data
peopleanalytics export --person "John Doe" --year 2023 --format excel
peopleanalytics export --person "John Doe" --year 2023 --format html

# Generate team reports
peopleanalytics team report --team "Engineering" --year 2023
peopleanalytics team compare --teams "Engineering,Marketing" --year 2023

# Backup data
peopleanalytics backup

# Validate data
peopleanalytics validate --output validation_report.json
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