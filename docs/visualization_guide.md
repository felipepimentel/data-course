# Visualization Quick Guide

This guide shows you how to quickly create visualizations with People Analytics.

## Basic CLI Usage

The simplest way to create visualizations is directly through the CLI:

```bash
# Generate a radar chart for a person
python -m peopleanalytics --base-path ./test_data visualize --type radar --person "john" --year "2023" --output "./output/john_radar.png"

# Generate a heatmap comparing multiple people
python -m peopleanalytics --base-path ./test_data visualize --type heatmap --year "2023" --output "./output/heatmap.png"

# Generate an interactive HTML report
python -m peopleanalytics --base-path ./test_data visualize --type interactive --year "2023" --output "./output/report.html"
```

## Using the Visualize Bash Script

For even easier usage, use the `visualize.sh` script:

```bash
# Generate a radar chart
./bin/visualize.sh --type radar --person "john" --year "2023"

# Generate a heatmap
./bin/visualize.sh --type heatmap --year "2023"

# Generate an interactive report (default type)
./bin/visualize.sh --year "2023"
```

## Visualization Types

The People Analytics tool supports three types of visualizations:

1. **Radar Charts**: Compare a person's scores across different categories with group averages
2. **Heatmaps**: Visualize scores across multiple criteria for multiple people
3. **Interactive HTML Reports**: Create interactive reports with charts and tables

## Running Examples

To see examples of all visualization types, run:

```bash
python examples/simple_visualize.py
```

This will generate example visualizations in the `output` directory.

## Advanced Usage: Python API

If you need more control, you can use the Visualization API directly:

```python
from peopleanalytics.analyzer import EvaluationAnalyzer
from peopleanalytics.visualization import Visualization

# Initialize components
analyzer = EvaluationAnalyzer("./test_data")
viz = Visualization()

# Generate a radar chart for a person
behavior_scores = analyzer.get_behavior_scores("john", "2023")
# ... process the data ...
viz.generate_radar_chart(data, title="John's Performance", output_path="radar.png")

# Generate a heatmap
# ... prepare the data ...
viz.generate_heatmap(data_df, x_col="Criterion", y_col="Person", value_col="Score",
                     title="Performance Comparison", output_path="heatmap.png")

# Generate an interactive HTML report
# ... prepare the data ...
viz.generate_interactive_html(data, output_path="report.html")
```

For more details, check the example files:
- `examples/simple_visualize.py` - Simple visualization examples
- `examples/visualization_examples.py` - More detailed visualization examples
- `examples/evaluation_visualization.py` - Complete examples with evaluation data 