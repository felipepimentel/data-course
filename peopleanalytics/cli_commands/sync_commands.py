"""
Sync and documentation commands for People Analytics CLI.

This module contains commands for data synchronization and documentation generation.
"""

import argparse
import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress

from .base_command import BaseCommand


class DataSync:
    """Classe responsável por executar todo o processo de sincronização."""

    def __init__(self, data_path: Path, output_path: Path, force: bool = False):
        """
        Inicializa o sincronizador.

        Args:
            data_path: Caminho para o diretório de dados de entrada
            output_path: Caminho para o diretório de saída
            force: Se True, força o reprocessamento mesmo de dados já processados
        """
        self.data_path = data_path
        self.output_path = output_path
        self.force = force
        self.logger = logging.getLogger(__name__)

        # Criar diretórios necessários
        self._ensure_directories()

    def _ensure_directories(self):
        """Garante que todos os diretórios necessários existam."""
        # Diretórios de entrada
        self.data_path.mkdir(exist_ok=True, parents=True)
        (self.data_path / "json").mkdir(exist_ok=True, parents=True)
        (self.data_path / "templates").mkdir(exist_ok=True, parents=True)
        (self.data_path / "raw").mkdir(exist_ok=True, parents=True)
        (self.data_path / "career_progression").mkdir(exist_ok=True, parents=True)

        # Diretórios de saída
        self.output_path.mkdir(exist_ok=True, parents=True)
        (self.output_path / "reports").mkdir(exist_ok=True, parents=True)
        (self.output_path / "visualizations").mkdir(exist_ok=True, parents=True)
        (self.output_path / "data").mkdir(exist_ok=True, parents=True)
        (self.output_path / "logs").mkdir(exist_ok=True, parents=True)

        # Diretório de log
        Path("logs").mkdir(exist_ok=True, parents=True)

    def run(self) -> List[str]:
        """Executa o processo completo de sincronização."""
        results = []
        self.logger.info("Iniciando processo de sincronização")

        try:
            # 1. Processar arquivos JSON
            json_results = self._process_json_files()
            results.extend(json_results)

            # 2. Processar dados de carreira
            career_results = self._process_career_data()
            results.extend(career_results)

            # 3. Processar templates personalizados
            template_results = self._process_templates()
            results.extend(template_results)

            # 4. Gerar visualizações
            visualization_results = self._generate_visualizations()
            results.extend(visualization_results)

            # 5. Gerar relatórios
            report_results = self._generate_reports()
            results.extend(report_results)

            # 6. Consolidar dados
            consolidation_results = self._consolidate_data()
            results.extend(consolidation_results)

            self.logger.info("Processo de sincronização concluído com sucesso")
            return results

        except Exception as e:
            error_msg = f"Erro no processo de sincronização: {str(e)}"
            self.logger.exception(error_msg)
            results.append(error_msg)
            return results

    def _process_json_files(self) -> List[str]:
        """Processa todos os arquivos JSON na pasta de entrada."""
        results = []
        json_dir = self.data_path / "json"

        if not json_dir.exists():
            return ["Diretório JSON não encontrado"]

        json_files = list(json_dir.glob("*.json"))
        if not json_files:
            return ["Nenhum arquivo JSON encontrado para processamento"]

        self.logger.info(f"Processando {len(json_files)} arquivos JSON")

        for json_file in json_files:
            try:
                # Ler o arquivo JSON
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Verificar se já foi processado (a menos que force=True)
                output_file = self.output_path / "data" / f"processed_{json_file.name}"
                if output_file.exists() and not self.force:
                    results.append(
                        f"Arquivo {json_file.name} já processado (use --force para reprocessar)"
                    )
                    continue

                # Processar o arquivo
                processed_data = self._transform_json_data(data, json_file.stem)

                # Salvar o resultado processado
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(processed_data, f, indent=2, ensure_ascii=False)

                results.append(f"Arquivo {json_file.name} processado com sucesso")

            except Exception as e:
                error_msg = f"Erro ao processar {json_file.name}: {str(e)}"
                self.logger.error(error_msg)
                results.append(error_msg)

        return results

    def _transform_json_data(
        self, data: Dict[str, Any], file_name: str
    ) -> Dict[str, Any]:
        """
        Transforma os dados JSON.
        Esta função deve ser adaptada com base na estrutura dos seus dados.
        """
        # Adicionar metadados de processamento
        data["_metadata"] = {
            "processed_at": datetime.now().isoformat(),
            "source_file": file_name,
            "version": "1.0",
        }

        # Aqui você pode adicionar lógica específica para transformar seus dados
        # Por exemplo, calcular métricas, normalizar campos, etc.

        return data

    def _process_career_data(self) -> List[str]:
        """Processa dados de progressão de carreira."""
        results = []
        career_dir = self.data_path / "career_progression"

        if not career_dir.exists():
            return ["Diretório de progressão de carreira não encontrado"]

        career_files = list(career_dir.glob("*.json"))
        if not career_files:
            return ["Nenhum arquivo de progressão de carreira encontrado"]

        self.logger.info(
            f"Processando {len(career_files)} arquivos de progressão de carreira"
        )

        for career_file in career_files:
            try:
                # Ler o arquivo de carreira
                with open(career_file, "r", encoding="utf-8") as f:
                    career_data = json.load(f)

                # Extrair nome da pessoa
                person_name = career_data.get("nome", career_file.stem)

                # Criar diretório da pessoa
                person_dir = self.output_path / person_name
                person_dir.mkdir(exist_ok=True, parents=True)

                # Gerar visualizações de carreira
                self._create_career_visualizations(person_name, career_data, person_dir)

                # Gerar relatório de carreira
                report = self._generate_career_report(person_name, career_data)
                report_file = (
                    person_dir
                    / f"career_progression_{datetime.now().strftime('%Y%m%d')}.md"
                )

                with open(report_file, "w", encoding="utf-8") as f:
                    f.write(report)

                results.append(
                    f"Relatório de progressão de carreira gerado para {person_name}"
                )

            except Exception as e:
                error_msg = (
                    f"Erro ao processar carreira de {career_file.stem}: {str(e)}"
                )
                self.logger.error(error_msg)
                results.append(error_msg)

        return results

    def _create_career_visualizations(
        self, person_name: str, career_data: Dict[str, Any], output_dir: Path
    ) -> None:
        """
        Cria visualizações para dados de carreira.
        Esta função deve ser adaptada para gerar visualizações específicas para seu caso.
        """
        # Na implementação real, você pode criar gráficos, tabelas, etc.
        # Por enquanto, apenas exportamos os dados já processados

        vis_file = output_dir / "career_data.json"
        with open(vis_file, "w", encoding="utf-8") as f:
            json.dump(career_data, f, indent=2, ensure_ascii=False)

    def _generate_career_report(
        self, person_name: str, career_data: Dict[str, Any]
    ) -> str:
        """
        Gera um relatório markdown para a progressão de carreira.
        """
        # Cargo atual e nível
        cargo = career_data.get("cargo_atual", "Não especificado")
        nivel = career_data.get("nivel", "Não especificado")

        # Data de início
        data_inicio = career_data.get("data_inicio", "Não especificada")

        # Construir o relatório
        report = []
        report.append(f"# Progressão de Carreira: {person_name}\n")
        report.append("## Informações Gerais\n")
        report.append(f"- **Cargo Atual:** {cargo}")
        report.append(f"- **Nível:** {nivel}")
        report.append(f"- **Data de Início:** {data_inicio}\n")

        # Habilidades
        report.append("## Habilidades\n")
        habilidades = career_data.get("habilidades", [])
        if habilidades:
            report.append("| Habilidade | Nível | Categoria |")
            report.append("| --- | --- | --- |")
            for hab in habilidades:
                nome = hab.get("nome", "")
                nivel = hab.get("nivel", 0)
                categoria = hab.get("categoria", "")
                report.append(f"| {nome} | {nivel} | {categoria} |")
        else:
            report.append("*Nenhuma habilidade registrada*\n")

        report.append("")

        # Marcos
        report.append("## Marcos\n")
        marcos = career_data.get("marcos", [])
        if marcos:
            for marco in marcos:
                data = marco.get("data", "")
                descricao = marco.get("descricao", "")
                tipo = marco.get("tipo", "")
                report.append(f"- **{data}:** {descricao} _{tipo}_")
        else:
            report.append("*Nenhum marco registrado*\n")

        report.append("")

        # Metas
        report.append("## Metas\n")
        metas = career_data.get("metas", [])
        if metas:
            for meta in metas:
                descricao = meta.get("descricao", "")
                prazo = meta.get("prazo", "")
                status = meta.get("status", "")
                report.append(f"- {descricao} (Prazo: {prazo}, Status: {status})")
        else:
            report.append("*Nenhuma meta registrada*\n")

        report.append("")

        # Feedback
        report.append("## Feedback\n")
        feedbacks = career_data.get("feedback", [])
        if feedbacks:
            for fb in feedbacks:
                data = fb.get("data", "")
                avaliador = fb.get("avaliador", "")
                report.append(f"### Feedback de {avaliador} em {data}\n")

                pontos_fortes = fb.get("pontos_fortes", [])
                if pontos_fortes:
                    report.append("**Pontos Fortes:**")
                    for ponto in pontos_fortes:
                        report.append(f"- {ponto}")
                    report.append("")

                areas_melhoria = fb.get("areas_melhoria", [])
                if areas_melhoria:
                    report.append("**Áreas de Melhoria:**")
                    for area in areas_melhoria:
                        report.append(f"- {area}")
                    report.append("")
        else:
            report.append("*Nenhum feedback registrado*\n")

        # Concatenar todas as linhas
        return "\n".join(report)

    def _process_templates(self) -> List[str]:
        """Processa templates personalizados."""
        results = []
        templates_dir = self.data_path / "templates"

        if not templates_dir.exists():
            return ["Diretório de templates não encontrado"]

        template_files = list(templates_dir.glob("*.json")) + list(
            templates_dir.glob("*.md")
        )
        if not template_files:
            return ["Nenhum template encontrado"]

        self.logger.info(f"Processando {len(template_files)} templates")

        for template_file in template_files:
            try:
                # Copiar o template para o diretório de saída apropriado
                dest_file = self.output_path / "templates" / template_file.name
                dest_file.parent.mkdir(exist_ok=True, parents=True)
                shutil.copy2(template_file, dest_file)

                results.append(f"Template {template_file.name} processado")

            except Exception as e:
                error_msg = f"Erro ao processar template {template_file.name}: {str(e)}"
                self.logger.error(error_msg)
                results.append(error_msg)

        return results

    def _generate_visualizations(self) -> List[str]:
        """Gera visualizações a partir dos dados processados."""
        # Esta função deve ser adaptada para gerar visualizações específicas para seu caso
        # Por enquanto, retorna apenas uma mensagem
        return ["Geração de visualizações não implementada nesta versão"]

    def _generate_reports(self) -> List[str]:
        """Gera relatórios a partir dos dados processados."""
        # Esta função deve ser adaptada para gerar relatórios específicos para seu caso
        # Por enquanto, retorna apenas uma mensagem
        return ["Geração de relatórios não implementada nesta versão"]

    def _consolidate_data(self) -> List[str]:
        """Consolida todos os dados processados em um formato unificado."""
        # Esta função deve ser adaptada para consolidar os dados conforme necessário
        # Por enquanto, retorna apenas uma mensagem
        return ["Consolidação de dados não implementada nesta versão"]


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
        parser.add_argument(
            "--force",
            "-f",
            action="store_true",
            help="Force reprocessing of already processed files",
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

            # Configure logging
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True, parents=True)
            log_file = log_dir / f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.StreamHandler(sys.stdout),
                    logging.FileHandler(log_file),
                ],
            )

            # Display input parameters
            self.console.print(f"[cyan]Data directory:[/cyan] {data_path}")
            self.console.print(f"[cyan]Output directory:[/cyan] {output_path}")
            self.console.print(
                f"[cyan]Force reprocessing:[/cyan] {'Yes' if args.force else 'No'}"
            )
            self.console.print()

            # Initialize sync object
            self.sync = DataSync(data_path, output_path, args.force)

            # Perform sync operations
            with Progress() as progress:
                task = progress.add_task("Synchronizing data...", total=None)

                results = self.sync.run()

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

        docs.append("## Synchronization\n")
        docs.append(
            "1. **Sync Data**: Synchronize data and generate comprehensive reports"
        )
        docs.append("   ```bash")
        docs.append("   people_analytics sync")
        docs.append("   ```\n")

        docs.append("## Analysis\n")
        docs.append("1. **Generate Reports**: Create reports from synchronized data")
        docs.append("   ```bash")
        docs.append("   people_analytics report --type performance")
        docs.append("   ```\n")

        docs.append("2. **Visualize Data**: Generate visualizations")
        docs.append("   ```bash")
        docs.append("   people_analytics plot --type radar --data skills")
        docs.append("   ```\n")

        return "\n".join(docs)

    def _generate_templates_documentation(self) -> str:
        """Generate templates documentation."""
        docs = []
        docs.append("# Templates Documentation\n")
        docs.append(
            "This document describes available templates and how to use them.\n"
        )

        docs.append("## Template Types\n")
        docs.append("The following template types are available:\n")
        docs.append("- **Evaluation**: Templates for performance evaluations")
        docs.append("- **Feedback**: Templates for collecting feedback")
        docs.append("- **Career**: Templates for career progression planning")
        docs.append("- **Development**: Templates for development plans\n")

        docs.append("## Using Templates\n")
        docs.append("Templates can be generated with the following command:\n")
        docs.append("```bash")
        docs.append("people_analytics template --type TYPE [--output PATH]")
        docs.append("```\n")

        docs.append("Where TYPE is one of the template types mentioned above.\n")

        docs.append("## Customizing Templates\n")
        docs.append("Templates can be customized by editing the generated files.\n")
        docs.append("```bash")
        docs.append("# 1. Generate a template")
        docs.append(
            "people_analytics template --type evaluation --output my_template.json"
        )
        docs.append("")
        docs.append("# 2. Edit the template")
        docs.append("# (use your favorite editor)")
        docs.append("")
        docs.append("# 3. Use the modified template")
        docs.append("people_analytics import --template my_template.json")
        docs.append("```\n")

        return "\n".join(docs)
