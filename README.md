# People Analytics

A modern data processing system for analyzing people data, including attendance and payment information.

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.6%2B-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Overview

People Analytics provides a complete solution for managing attendance and payment data. The system offers robust data management features with an intuitive command-line interface, making it easy to import, validate, analyze, visualize, and export your people data.

## Features

- **Modern Data Model**: Uses Python dataclasses for a clean, type-hinted data model
- **Standardized File Structure**: Uses a consistent file structure with separate files for each data type (resultado.json, perfil.json)
- **Robust Error Handling**: Comprehensive validation and error handling
- **Structured Output**: All reports, exports, and visualizations stored in the `output` directory
- **Data Visualization**: Built-in plotting capabilities for attendance and payment data
- **Reporting**: Generate detailed reports in various formats (Excel, CSV, JSON, HTML)
- **Backup & Restore**: Simple backup functionality to preserve your data
- **Command Line Interface**: Intuitive CLI for all operations
- **Bilingual Support**: Handles both Portuguese and English field names

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/peopleanalytics.git
cd peopleanalytics

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```bash
# Generate attendance report for all years
python -m peopleanalytics report attendance
# Output: Attendance report generated at: output/reports/attendance_report_TIMESTAMP.xlsx

# Generate payment plots for 2023
python -m peopleanalytics plot payment --year 2023
# Output: Payment plot generated at: output/plots/payment_plot_2023_TIMESTAMP.png

# Create a comprehensive summary
python -m peopleanalytics summary --format html
# Output: Summary generated at: output/summary/summary_TIMESTAMP.html
```

## Getting Started Guide

If you're new to People Analytics, follow these steps to get started quickly:

1. **Check your data**: Ensure your data follows the expected structure (see [Data Structure](#data-structure))
2. **Import your data**: Use the `import` command to bring your data into the system
3. **Validate data**: Run the `validate` command to verify your data is correctly formatted
4. **Generate reports**: Use the `report` command to create detailed reports
5. **Visualize data**: Generate plots with the `plot` command
6. **Create summaries**: Generate comprehensive summaries with the `summary` command

Here's a sample workflow:

```bash
# Import data from a directory
python -m peopleanalytics import path/to/my/data --recursive
# Output: Imported X files

# Validate all data
python -m peopleanalytics validate
# Output: Shows validation results with total, valid, and invalid files

# Generate all reports for 2023
python -m peopleanalytics report all --year 2023
# Output: Generates both attendance and payment reports

# Create a HTML summary
python -m peopleanalytics summary --format html
# Output: Summary generated at: output/summary/summary_TIMESTAMP.html

# Back up all data
python -m peopleanalytics backup
# Output: Backup created at: output/backups/data_backup_TIMESTAMP.zip
```

## Data Structure

The system uses a modern and intuitive data structure:

```
data/
  ├── Person Name/
  │   ├── Year/
  │   │   ├── resultado.json  # Contains attendance & payment records
  │   │   └── perfil.json     # Optional profile data
  │   └── ...
  └── ...
```

Each person's data for a specific year is stored in two files:

1. `resultado.json` - Contains attendance and payment records:
```json
{
  "nome": "Ana Costa",
  "ano": 2023,
  "frequencias": [
    {"data": "2023-01-01", "status": "presente", "justificativa": ""},
    {"data": "2023-01-08", "status": "ausente", "justificativa": "Feriado"}
  ],
  "pagamentos": [
    {"data": "2023-01-15", "valor": 1000, "descricao": ""},
    {"data": "2023-02-15", "valor": 1000, "descricao": "Invoice #123"}
  ]
}
```

2. `perfil.json` (optional) - Contains profile information:
```json
{
  "nome_completo": "Ana Maria Costa",
  "email": "ana.costa@example.com",
  "departamento": "Marketing",
  "cargo": "Marketing Manager",
  "data_admissao": "2020-01-15",
  "gestor": "Carlos Souza"
}
```

### Field Mappings

The system uses standard Portuguese field names:

| Field Name    | Description                   |
|---------------|-------------------------------|
| nome          | Person's name                 |
| ano           | Year of the data              |
| frequencias   | List of attendance records    |
| data          | Date of record                |
| status        | Attendance status             |
| justificativa | Optional justification        |
| pagamentos    | List of payment records       |
| valor         | Payment amount                |
| descricao     | Payment description           |

## Command Line Interface

### Global Options

```bash
python -m peopleanalytics [--data-path PATH] [--output-path PATH] COMMAND
```

- `--data-path`: Path to the data directory (default: `data`)
- `--output-path`: Path to the output directory (default: `output`)

### Commands

#### List Information

```bash
# List all people
python -m peopleanalytics list people
# Output:
#     All People    
# ┏━━━━━━━━━━━━━━━━┓
# ┃ Name           ┃
# ┡━━━━━━━━━━━━━━━━┩
# │ Ana Costa      │
# │ João Silva     │
# │ Maria Oliveira │
# └────────────────┘

# List people for a specific year
python -m peopleanalytics list people --year 2023
# Output: Shows people for the specified year

# List all years for a person
python -m peopleanalytics list years --person "Ana Costa"
# Output: Shows years available for the specified person

# Show detailed data for a person/year
python -m peopleanalytics list data --person "Ana Costa" --year 2023
# Output: Shows detailed information, attendance, and payment summaries
```

#### Import Data

```bash
# Import data from a file
python -m peopleanalytics import path/to/resultado.json
# Output: Successfully imported data for Person (Year)

# Import all files from a directory
python -m peopleanalytics import path/to/directory --recursive
# Output: Imported X files
```

#### Export Data

```bash
# Export all data
python -m peopleanalytics export --all
# Output: Exported X files

# Export data for a specific person and year
python -m peopleanalytics export --person "Ana Costa" --year 2023
# Output: Successfully exported data to output/exports/Ana Costa/2023.json
```

#### Generate Reports

```bash
# Generate attendance report for all years
python -m peopleanalytics report attendance
# Output: Attendance report generated at: output/reports/attendance_report_TIMESTAMP.xlsx

# Generate payment report for a specific year
python -m peopleanalytics report payment --year 2023
# Output: Payment report generated at: output/reports/payment_report_2023_TIMESTAMP.xlsx

# Generate all reports for a specific year
python -m peopleanalytics report all --year 2023
# Output: Generates both attendance and payment reports for the specified year
```

#### Create Visualizations

```bash
# Generate attendance plots for all years
python -m peopleanalytics plot attendance
# Output: Attendance plot generated at: output/plots/attendance_plot_TIMESTAMP.png

# Generate payment plots for a specific year
python -m peopleanalytics plot payment --year 2023
# Output: Payment plot generated at: output/plots/payment_plot_2023_TIMESTAMP.png

# Generate all plots for a specific year
python -m peopleanalytics plot all --year 2023
# Output: Generates both attendance and payment plots for the specified year
```

#### Generate Summary

```bash
# Generate JSON summary
python -m peopleanalytics summary
# Output: Summary generated at: output/summary/summary_TIMESTAMP.json

# Generate CSV summary
python -m peopleanalytics summary --format csv
# Output: Summary generated at: output/summary/summary_TIMESTAMP.csv

# Generate HTML summary
python -m peopleanalytics summary --format html
# Output: Summary generated at: output/summary/summary_TIMESTAMP.html
```

#### Create Backup

```bash
# Create a backup of all data
python -m peopleanalytics backup
# Output: Backup created at: output/backups/data_backup_TIMESTAMP.zip
```

#### Validate Data

```bash
# Validate all data
python -m peopleanalytics validate
# Output:
#   Validation Results   
# ┏━━━━━━━━━━━━━┳━━━━━━━┓
# ┃ Metric      ┃ Value ┃
# ┡━━━━━━━━━━━━━╇━━━━━━━┩
# │ Total Files │ 6     │
# │ Valid       │ 6     │
# │ Invalid     │ 0     │
# └─────────────┴───────┘
```

## Sample Outputs

### Reports

The system generates Excel reports with multiple sheets:

- **Main Data Sheet**: Contains the raw data records
- **Summary Sheet**: Provides aggregated information

### Plots

The system generates various visualization plots:

- **Attendance Plots**: Bar charts showing attendance rates for people
- **Payment Plots**: Bar charts showing payment totals and averages

### Validation

The validation output shows:

- Total number of files checked
- Number of valid and invalid files
- Details of any validation issues

## Output Directory Structure

All generated files are organized in the `output` directory:

```
output/
  ├── backups/                 # Backup archives
  ├── exports/                 # Exported data files
  │   └── Person Name/
  ├── logs/                    # Log files
  ├── plots/                   # Generated plots/visualizations
  ├── reports/                 # Generated reports
  └── summary/                 # Summary data
```

## Python API

You can also use the system programmatically in your Python code:

```python
from peopleanalytics import DataProcessor, PersonData

# Initialize processor
processor = DataProcessor("data", "output")

# Load person data
data = processor.load_person_data("Ana Costa", "2023")

# Create new person data
new_person = processor.create_person_data("João Silva", 2023)
new_person.add_attendance("2023-01-01", True)
new_person.add_payment("2023-01-15", 1000)

# Save data
processor.save_person_data(new_person)

# Generate reports
attendance_report = processor.generate_attendance_report()
payment_report = processor.generate_payment_report()

# Create visualizations
attendance_plot = processor.plot_attendance_summary()
payment_plot = processor.plot_payment_summary()

# Generate summary
summary_path = processor.generate_summary(output_format="html")

# Create backup
backup_path = processor.create_backup()
```

## Data Model

The system uses a structured data model with the following components:

### PersonData

Core data structure for a person in a specific year.

```python
person = PersonData(name="Ana Costa", year=2023)
person.add_attendance("2023-01-01", True)
person.add_payment("2023-01-15", 1000)

# Get summaries
attendance_summary = person.get_attendance_summary()
payment_summary = person.get_payment_summary()

# Save to file
person.save("data/")
```

### AttendanceRecord

Individual attendance records.

```python
attendance = AttendanceRecord(date=date(2023, 1, 1), present=True, notes="Optional notes")
```

### PaymentRecord

Individual payment records.

```python
payment = PaymentRecord(date=date(2023, 1, 15), amount=1000, status="paid", reference="Invoice #123")
```

### PersonSummary

Summary of a person's data across all years.

```python
summary = PersonSummary(
    name="Ana Costa",
    years=[2022, 2023],
    total_attendance=50,
    present_count=45,
    total_payments=24,
    total_amount=24000
)

# Calculated properties
attendance_rate = summary.attendance_rate  # 90.0
average_payment = summary.average_payment  # 1000.0
```

## Extending the System

The modular architecture makes it easy to extend the system with new features:

1. Add new data models in `data_model.py`
2. Implement processing logic in `data_processor.py`
3. Add CLI commands in `cli.py`

### Adding a New Command

```python
# In cli.py
def _create_parser(self):
    # ... existing parser code ...
    
    # Add a new command
    new_command_parser = subparsers.add_parser("new_command", help="Description of new command")
    new_command_parser.add_argument("--option", help="Option description")
    
    # ... rest of parser code ...

def handle_new_command(self):
    """Handle the new command."""
    option = self.args.option
    # Implement command logic here
```

## Example Workflow

1. **Import Data**:
   ```bash
   python -m peopleanalytics import sample_data/ --recursive
   # Output: Imported X files
   ```

2. **Validate Data**:
   ```bash
   python -m peopleanalytics validate
   # Output: Shows validation results
   ```

3. **Generate Reports**:
   ```bash
   python -m peopleanalytics report all
   # Output: Generates attendance and payment reports
   ```

4. **Create Visualizations**:
   ```bash
   python -m peopleanalytics plot all
   # Output: Generates attendance and payment plots
   ```

5. **Export as Summary**:
   ```bash
   python -m peopleanalytics summary --format html
   # Output: Summary generated at: output/summary/summary_TIMESTAMP.html
   ```

6. **Backup Your Data**:
   ```bash
   python -m peopleanalytics backup
   # Output: Backup created at: output/backups/data_backup_TIMESTAMP.zip
   ```

## Troubleshooting

### Common Issues

- **Missing data files**: Ensure your data follows the expected structure
- **Import failures**: Check that your JSON files are properly formatted
- **Empty reports**: Verify that you have data for the specified person/year

### Logging

The system creates detailed logs in the `output/logs` directory. Check these logs for troubleshooting.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 