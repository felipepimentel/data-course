"""
Sync and documentation commands for People Analytics CLI.

This module contains commands for data synchronization and documentation generation.
"""

import argparse
import logging
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress

from ..sync import Sync
from .base_command import BaseCommand


class SyncCommand(BaseCommand):
    """Command to synchronize data and generate reports."""

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.sync = None

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "--data-path", "-d", type=str, help="Path to data directory"
        )
        parser.add_argument(
            "--output-path", "-o", type=str, help="Path to output directory"
        )

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the sync command."""
        self.console.print("[bold]Synchronizing data and generating reports...[/bold]")

        try:
            # Convert paths to Path objects
            data_path = Path(args.data_path) if args.data_path else Path.cwd() / "data"
            output_path = (
                Path(args.output_path) if args.output_path else Path.cwd() / "output"
            )

            # Create directories if they don't exist
            data_path.mkdir(parents=True, exist_ok=True)
            output_path.mkdir(parents=True, exist_ok=True)

            # Initialize sync object
            self.sync = Sync(data_path, output_path)

            # Perform sync operations
            with Progress() as progress:
                task = progress.add_task("Synchronizing data...", total=None)

                results = self.sync.sync()

                progress.update(task, completed=1)

            # Display results
            self.console.print("\n[bold]Sync Results:[/bold]")
            for result in results:
                self.console.print(f"- {result}")

            return 0

        except Exception as e:
            self.console.print(f"[red]Error synchronizing data:[/red] {str(e)}")
            logging.exception("Error in sync command")
            return 1


class DocsCommand(BaseCommand):
    """Command to generate documentation."""

    def __init__(self):
        super().__init__()
        self.console = Console()

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "--topic",
            choices=["all", "career", "workflow", "templates"],
            default="all",
            help="Documentation topic",
        )
        parser.add_argument("--output", help="Output file path")

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the docs command."""
        topic = args.topic
        self.console.print(f"[bold]Generating documentation for {topic}...[/bold]")

        try:
            # Determine output path
            if args.output:
                output_path = Path(args.output)
            else:
                output_filename = f"documentation_{topic}.md"
                output_path = Path.cwd() / "docs" / output_filename

            # Create parent directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Generate documentation
            if topic == "all":
                docs = self._generate_all_documentation()
            else:
                docs = self._generate_specific_documentation(topic)

            # Write docs to file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(docs)

            # Show preview
            self.console.print("\n[bold]Documentation Preview:[/bold]")
            preview = "\n".join(docs.split("\n")[:20])
            if len(docs.split("\n")) > 20:
                preview += "\n...\n(Full documentation in file)"

            self.console.print(Markdown(preview))

            self.console.print(
                f"\n[green]Documentation generated at: {output_path}[/green]"
            )
            return 0

        except Exception as e:
            self.console.print(f"[red]Error generating documentation:[/red] {str(e)}")
            logging.exception("Error in docs command")
            return 1

    def _generate_all_documentation(self) -> str:
        """Generate comprehensive documentation."""
        docs = []
        docs.append("# People Analytics Documentation\n")
        docs.append("## Table of Contents\n")
        docs.append("1. [Career Development](#career-development)")
        docs.append("2. [Workflow](#workflow)")
        docs.append("3. [Templates](#templates)\n")

        # Add career documentation
        docs.append("## Career Development <a name='career-development'></a>\n")
        docs.append(self._generate_career_documentation())

        # Add workflow documentation
        docs.append("## Workflow <a name='workflow'></a>\n")
        docs.append(self._generate_workflow_documentation())

        # Add templates documentation
        docs.append("## Templates <a name='templates'></a>\n")
        docs.append(self._generate_templates_documentation())

        return "\n".join(docs)

    def _generate_specific_documentation(self, topic: str) -> str:
        """Generate documentation for a specific topic."""
        if topic == "career":
            return self._generate_career_documentation()
        elif topic == "workflow":
            return self._generate_workflow_documentation()
        elif topic == "templates":
            return self._generate_templates_documentation()
        else:
            return f"Documentation for {topic} not available."

    def _generate_career_documentation(self) -> str:
        """Generate career development documentation."""
        docs = []
        docs.append("# Career Development Documentation\n")
        docs.append(
            "This document describes how to track and manage career development within People Analytics.\n"
        )

        docs.append("## Career Progression Model\n")
        docs.append(
            "The career progression model consists of the following components:\n"
        )
        docs.append(
            "- **Skills**: Technical and soft skills that are tracked over time"
        )
        docs.append("- **Milestones**: Significant achievements in a person's career")
        docs.append("- **Goals**: Short and long-term goals for career development")
        docs.append("- **Feedback**: Structured feedback from managers and peers\n")

        docs.append("## Career Data Structure\n")
        docs.append(
            "Career data is stored in JSON format with the following structure:\n"
        )
        docs.append("```json")
        docs.append("{")
        docs.append('  "nome": "Person Name",')
        docs.append('  "cargo_atual": "Current Position",')
        docs.append('  "nivel": "Level",')
        docs.append('  "data_inicio": "YYYY-MM-DD",')
        docs.append('  "habilidades": [')
        docs.append('    { "nome": "Skill 1", "nivel": 3, "categoria": "Technical" },')
        docs.append('    { "nome": "Skill 2", "nivel": 4, "categoria": "Soft" }')
        docs.append("  ],")
        docs.append('  "marcos": [')
        docs.append(
            '    { "data": "YYYY-MM-DD", "descricao": "Milestone description", "tipo": "promotion" }'
        )
        docs.append("  ],")
        docs.append('  "metas": [')
        docs.append(
            '    { "descricao": "Goal description", "prazo": "YYYY-MM-DD", "status": "in_progress" }'
        )
        docs.append("  ],")
        docs.append('  "feedback": [')
        docs.append(
            '    { "data": "YYYY-MM-DD", "avaliador": "Manager Name", "pontos_fortes": ["Strength 1"], "areas_melhoria": ["Area 1"] }'
        )
        docs.append("  ]")
        docs.append("}")
        docs.append("```\n")

        docs.append("## Career Commands\n")
        docs.append("The following commands are available for career management:\n")
        docs.append("- `people_analytics career`: Manage career progression data")
        docs.append(
            "- `people_analytics update-career`: Update existing career progression data"
        )
        docs.append(
            "- `people_analytics template --type career`: Generate career template\n"
        )

        return "\n".join(docs)

    def _generate_workflow_documentation(self) -> str:
        """Generate workflow documentation."""
        docs = []
        docs.append("# Workflow Documentation\n")
        docs.append(
            "This document describes the standard workflow for using People Analytics.\n"
        )

        docs.append("## Data Collection\n")
        docs.append("1. **Create Templates**: Generate templates for data collection")
        docs.append("   ```bash")
        docs.append("   people_analytics template --type evaluation --format json")
        docs.append("   ```\n")

        docs.append("2. **Import Data**: Import data from various sources")
        docs.append("   ```bash")
        docs.append("   people_analytics import --source data/input --type evaluations")
        docs.append("   ```\n")

        docs.append("## Data Analysis\n")
        docs.append("1. **Generate Reports**: Create reports for different data types")
        docs.append("   ```bash")
        docs.append("   people_analytics report --type performance --format html")
        docs.append("   ```\n")

        docs.append("2. **Generate Plots**: Create visualizations")
        docs.append("   ```bash")
        docs.append("   people_analytics plot --type performance --format png")
        docs.append("   ```\n")

        docs.append(
            "3. **Interactive Analysis**: Use notebooks for interactive analysis"
        )
        docs.append("   ```bash")
        docs.append("   people_analytics notebook --type people")
        docs.append("   ```\n")

        docs.append("## Data Management\n")
        docs.append("1. **Validate Data**: Check data integrity")
        docs.append("   ```bash")
        docs.append("   people_analytics validate --fix")
        docs.append("   ```\n")

        docs.append("2. **Export Data**: Export data in various formats")
        docs.append("   ```bash")
        docs.append("   people_analytics export --type evaluations --format csv --all")
        docs.append("   ```\n")

        docs.append("3. **Backup Data**: Create backups")
        docs.append("   ```bash")
        docs.append("   people_analytics backup")
        docs.append("   ```\n")

        docs.append("## Synchronization\n")
        docs.append(
            "1. **Sync Data**: Synchronize data and generate comprehensive reports"
        )
        docs.append("   ```bash")
        docs.append("   people_analytics sync")
        docs.append("   ```\n")

        return "\n".join(docs)

    def _generate_templates_documentation(self) -> str:
        """Generate templates documentation."""
        docs = []
        docs.append("# Templates Documentation\n")
        docs.append(
            "This document describes the templates available in People Analytics.\n"
        )

        docs.append("## Template Types\n")
        docs.append("The following template types are available:\n")
        docs.append("- **Career**: Templates for career progression tracking")
        docs.append("- **Evaluation**: Templates for performance evaluations")
        docs.append(
            "- **Complete**: Comprehensive templates including all data points\n"
        )

        docs.append("## Template Formats\n")
        docs.append("Templates can be generated in the following formats:\n")
        docs.append("- **JSON**: Structured data format for programmatic use")
        docs.append("- **Markdown (MD)**: Human-readable format for documentation")
        docs.append("- **YAML**: Simplified data format for easy editing\n")

        docs.append("## Template Generation\n")
        docs.append("Templates can be generated using the following command:\n")
        docs.append("```bash")
        docs.append(
            "people_analytics template --type <type> --format <format> --output <output_path>"
        )
        docs.append("```\n")

        docs.append("### Examples\n")
        docs.append("1. Generate a career template in JSON format:")
        docs.append("   ```bash")
        docs.append(
            "   people_analytics template --type career --format json --output templates/career_template.json"
        )
        docs.append("   ```\n")

        docs.append("2. Generate an evaluation template in Markdown format:")
        docs.append("   ```bash")
        docs.append(
            "   people_analytics template --type evaluation --format md --output templates/evaluation_template.md"
        )
        docs.append("   ```\n")

        docs.append("3. Generate a complete template in YAML format:")
        docs.append("   ```bash")
        docs.append(
            "   people_analytics template --type complete --format yaml --output templates/complete_template.yaml"
        )
        docs.append("   ```\n")

        docs.append("## Template Structure\n")
        docs.append(
            "Each template type has a specific structure. Here's an overview of each:\n"
        )

        docs.append("### Career Template\n")
        docs.append("```json")
        docs.append("{")
        docs.append('  "nome": "",')
        docs.append('  "cargo_atual": "",')
        docs.append('  "nivel": "",')
        docs.append('  "data_inicio": "",')
        docs.append('  "habilidades": [],')
        docs.append('  "marcos": [],')
        docs.append('  "metas": [],')
        docs.append('  "feedback": []')
        docs.append("}")
        docs.append("```\n")

        docs.append("### Evaluation Template\n")
        docs.append("```json")
        docs.append("{")
        docs.append('  "pessoa": "",')
        docs.append('  "ano": "",')
        docs.append('  "avaliador": "",')
        docs.append('  "criterios": [')
        docs.append('    { "nome": "", "peso": 0, "nota": 0, "comentario": "" }')
        docs.append("  ],")
        docs.append('  "comentario_geral": "",')
        docs.append('  "metas_proximas": []')
        docs.append("}")
        docs.append("```\n")

        return "\n".join(docs)
