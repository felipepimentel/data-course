# People Analytics System

## Overview

The People Analytics system analyzes employee data to generate comprehensive performance reports, talent development recommendations, and organization-wide insights.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/data-course.git
cd data-course
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Executing Commands

Always execute commands through the main CLI interface:

```bash
python -m peopleanalytics [command] [options]
```

### Sync Command

The primary command for data processing and report generation:

```bash
python -m peopleanalytics sync --data-dir=data --output-dir=output
```

#### Key Options

- `--data-dir=DIR`: Source directory containing input data
- `--output-dir=DIR`: Output directory for reports
- `--pessoa=NAME`: Process a specific person only
- `--ano=YEAR`: Process a specific year only
- `--include-org-chart`: Include organizational chart in reports
- `--peer-analysis`: Generate peer group comparison analysis
- `--yoy-analysis`: Generate year-over-year performance analysis

For complete documentation, run:

```bash
python -m peopleanalytics sync --help
```

## Data Structure

The system expects data organized in a structure like:
```
data/
  <pessoa>/
    <ano>/
      resultado.json
```

## Report Types

The system generates several report types:

1. **Individual Reports**: Person-specific performance evaluations
2. **Talent Development Reports**: 9-Box Matrix, Career Simulation, Influence Network
3. **Analysis Reports**: Peer Comparison, Year-over-Year Analysis

## Talent Development Reports

The system includes a standalone script for generating talent development reports without running the full sync process. These reports provide insights into employee performance, potential, career paths, and organizational networks.

### Available Reports

1. **9-Box Matrix Report**: Maps employees on a grid based on performance and potential
2. **Career Simulation Report**: Projects potential career paths for employees
3. **Influence Network Report**: Visualizes informal influence networks within the organization
4. **Talent Dashboard**: Provides a consolidated view of key talent metrics

### Running the Report Generator

```bash
# Generate all reports with default settings
./sync_cmd.py

# Generate reports for a specific person
./sync_cmd.py --pessoa pessoa1 --output-dir output/pessoa1_reports

# Generate only specific reports
./sync_cmd.py --no-9box --no-career

# Show all available options
./sync_cmd.py --help
```

### Command Line Options

```
--data-dir DATA_DIR     Directory containing talent data (default: data/synthetic)
--output-dir OUTPUT_DIR Directory for generated reports (default: output/talent_reports_test)
--no-9box               Skip generation of 9-Box Matrix report
--no-career             Skip generation of Career Simulation report
--no-network            Skip generation of Influence Network report
--no-dashboard          Skip generation of Talent Dashboard
--pessoa PESSOA         Generate reports for a specific person only
--verbose               Show verbose output
```

The reports are generated in Markdown format with Mermaid.js visualizations, making them viewable in any modern Markdown viewer.

## License

See the LICENSE file for details.