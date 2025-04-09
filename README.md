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

## Data Organization

By default, the tool expects data to be organized in the following directory structure:

```
<base_path>/<year>/<person_name>/result.json
```

Where:
- `<base_path>` is the database root directory (defaults to `~/.peopleanalytics`)
- `<year>` is the evaluation year folder
- `<person_name>` is the evaluated person's name folder
- `result.json` contains the actual evaluation data

### Importing Existing Data

If your data is in a different structure, use the `pipeline import` command to organize it properly:

```bash
# For common structures like <person>/<year>/result.json
peopleanalytics pipeline import --directory /path/to/data --pattern "*/*/result.json" --overwrite

# For single files
peopleanalytics pipeline import --file /path/to/single/file.json
```

### Working with Existing Data Structure

If you prefer to use your existing data structure without importing, specify the parent directory as the base path:

```bash
peopleanalytics --base-path /path/to/parent/directory list people
```

Note: The parent directory is the one containing the expected structure elements (years or people).

### Structure Adapter for Inverted Data Structure

If your data is organized in the inverted structure (`<person>/<year>/result.json` instead of `<year>/<person>/result.json`), you can use the structure adapter:

```bash
# Create symlinks (no duplication of data)
python structure_adapter.py symlink --source /path/to/data --target ~/.peopleanalytics

# Or copy and convert structure (duplicates data)
python structure_adapter.py convert --source /path/to/data --target ~/.peopleanalytics

# Test the adapter directly
python structure_adapter.py test --dir /path/to/data
```

For programmatic access to inverted structure:

```python
from structure_adapter import InvertedStructureAnalyzer

# Use the adapter directly with inverted structure
analyzer = InvertedStructureAnalyzer("/path/to/data")
people = analyzer.get_all_people()
```

### Using ChatGPT to Adapt Your Data Structure

If you have a custom data structure and need help adapting it, you can use ChatGPT to generate transformation functions that override the existing ones in the project. Here's a prompt template:

```
I need to modify the People Analytics tool to work with my custom data structure.

Current structure in my files:
[DESCRIBE YOUR CURRENT FOLDER/FILE STRUCTURE]
Example: My files are organized as <department>/<person_name>/<year>/resultado.json

Target structure needed by the tool:
<year>/<person_name>/result.json

Here's an example of my JSON data:
```json
{
  "person": "João Silva",
  "year": "2022",
  "department": "Engineering",
  "conceito_ciclo_filho_descricao": "Supera Expectativas",
  "comportamentos": [
    {
      "nome": "Liderança",
      "score": 4.2
    },
    {
      "nome": "Comunicação",
      "score": 4.5
    }
  ]
}
```

I need you to create a custom function that will override the existing ingest_file method in the DataPipeline class. The function should:

1. Extract the person, year, and any other metadata from both the filepath and JSON content
2. Handle my specific folder structure correctly
3. Transform the data to the expected format while preserving all original information

Please provide:
1. A complete implementation of a custom ingest_file method that I can use to replace the existing one
2. Instructions on how to properly override this method in the codebase
3. Example usage showing how to call this modified method
```

Tips for using ChatGPT for function overriding:
1. **Be specific** about the function you want to override (method name, class, file)
2. **Share the exact folder structure** you're using
3. **Consider edge cases** like missing fields or unusual filenames
4. **Ask for docstrings and comments** to understand how the custom function works

You can use the generated function to override methods in `data_pipeline.py` or create a custom subclass.

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

#### Data Import and Management

```bash
# Import data from a directory with specific structure
peopleanalytics pipeline import --directory /path/to/data --pattern "*.json" --overwrite

# Import data with debug mode for detailed processing information
peopleanalytics pipeline import --directory /path/to/data --pattern "*/*/result.json" --debug

# Import data preserving original structure (for structures like <person>/<year>/result.json)
peopleanalytics pipeline import --directory /path/to/data --pattern "*/*/result.json" --overwrite

# Create a backup of the database
peopleanalytics pipeline backup --output-directory /path/to/backup/dir

# Export all raw data to a single file
peopleanalytics pipeline export --output /path/to/output.json
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

### Troubleshooting

**"No database" error**: This usually means the tool cannot find properly organized data. Either:
1. Import your data using the pipeline command: `peopleanalytics pipeline import --directory /path/to/data`
2. Specify the correct base path: `peopleanalytics --base-path /path/to/data list people`
3. Use the structure adapter: `python structure_adapter.py symlink --source /path/to/data --target ~/.peopleanalytics`

**Data not showing up**: Check that your file structure matches what the tool expects:
```
<base_path>/<year>/<person_name>/result.json
```

**Inverted structure problems**: If your data is in format `<person>/<year>/result.json`, use the structure adapter or specify `--base-path`.

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