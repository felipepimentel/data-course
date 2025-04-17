# People Analytics

A comprehensive people analytics tool that processes employee data to generate insights on performance, skills, and career development.

## Features

- Data synchronization and consolidation
- Comprehensive evaluation reports
- Skills analysis and recommendations
- Career progression tracking
- Manager feedback processing
- Talent development metrics

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/peopleanalytics.git
cd peopleanalytics

# Install dependencies
pip install -e .
```

## Data Structure

The system expects data in the following structure:
```
data/
├── career_progression/
│   └── person1.json
├── person1/
│   └── 2023/
│       ├── resultado.json
│       └── perfil.json
├── person2/
│   └── 2023/
│       ├── resultado.json
│       └── perfil.json
```

## Basic Usage

Run the sync command to process data:

```bash
python -m peopleanalytics sync --data-dir=data --output-dir=output
```

## Skills Analyzer

The package includes a powerful skills analyzer that can:

1. Generate comprehensive skills reports
2. Create skill recommendations and learning paths
3. Visualize skills using radar charts
4. Produce year-over-year skill growth analysis

### Using the Skills Analyzer

The skills analyzer is enabled by default and will generate comprehensive skills reports, recommendations, and visualizations automatically when you run the sync command:

```bash
python -m peopleanalytics sync --data-dir=data --output-dir=output
```

#### Customizing the Skills Analysis

You can customize the analysis with additional options:

```bash
python -m peopleanalytics sync --data-dir=data --output-dir=output \
  --include-org-chart --year-comparison
```

#### Custom report output directory:
```bash
python -m peopleanalytics sync --data-dir=data --output-dir=output \
  --report-output-dir=custom_reports
```

## Skills Report Features

The skills reports include:

- Top skills by frequency and proficiency
- Skill gaps analysis
- Skill growth over time
- Department and position skill patterns
- Recommended learning paths
- Visualization via radar charts and mermaid diagrams

## Output

Reports are generated in the output directory with the following structure:

```
output/
├── reports/
│   ├── skills_evaluation.md
│   ├── skill_recommendations.md
│   └── comprehensive_analysis.md
├── visualizations/
│   ├── radar_charts/
│   └── mermaid/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.