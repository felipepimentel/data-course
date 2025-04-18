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

## License

See the LICENSE file for details.