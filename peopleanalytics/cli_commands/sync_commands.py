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

        # Opções adicionais
        self.skip_viz = False
        self.ignore_errors = False
        self.selected_formats = "all"
        self.pessoa_filter = None
        self.ano_filter = None
        self.export_excel = False
        self.verbose = False

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

            # 2. Processar estrutura <pessoa>/<ano>/resultado.json
            pessoa_ano_results = self._process_pessoa_ano_structure()
            results.extend(pessoa_ano_results)

            # 3. Processar dados de carreira
            career_results = self._process_career_data()
            results.extend(career_results)

            # 4. Processar templates personalizados
            template_results = self._process_templates()
            results.extend(template_results)

            # 5. Processar formatos adicionais de dados como CSV, Excel, etc.
            additional_data_results = self._process_additional_data_formats()
            results.extend(additional_data_results)

            # Se não deve pular visualizações
            if not self.skip_viz:
                # 6. Gerar visualizações
                visualization_results = self._generate_visualizations()
                results.extend(visualization_results)

                # 7. Gerar relatórios
                report_results = self._generate_reports()
                results.extend(report_results)

            # 8. Consolidar dados
            consolidation_results = self._consolidate_data()
            results.extend(consolidation_results)

            self.logger.info("Processo de sincronização concluído com sucesso")
            return results

        except Exception as e:
            error_msg = f"Erro no processo de sincronização: {str(e)}"
            self.logger.exception(error_msg)
            results.append(error_msg)

            # Se deve ignorar erros, continua e retorna resultados parciais
            if self.ignore_errors:
                results.append(
                    "Continuando apesar de erros devido à flag ignore_errors"
                )
                return results
            else:
                # Se não deve ignorar erros, propaga a exceção
                raise

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

    def _process_pessoa_ano_structure(self) -> List[str]:
        """Processa a estrutura <pessoa>/<ano>/resultado.json e perfil.json."""
        results = []

        # Importar o DataProcessor
        from peopleanalytics.data_processor import DataProcessor

        # Criar instância do DataProcessor
        processor = DataProcessor(self.data_path, self.output_path)

        # Processar o diretório recursivamente para arquivo padrão resultado.json
        self.logger.info("Processando estrutura <pessoa>/<ano>/resultado.json")
        import_results = processor.import_directory(self.data_path, recursive=True)

        # Verificar arquivos alternativos em formatos diferentes
        self.logger.info(
            "Procurando formatos de arquivo alternativos na estrutura <pessoa>/<ano>/"
        )

        # Buscar padrões de estrutura alternativa, como YAML, CSV e Excel
        valid_directories = []

        # 1. Encontrar diretórios que seguem o padrão <pessoa>/<ano>/
        for pessoa_dir in self.data_path.glob("*"):
            if pessoa_dir.is_dir():
                # Verificar filtro de pessoa
                if self.pessoa_filter and pessoa_dir.name != self.pessoa_filter:
                    if self.verbose:
                        self.logger.info(
                            f"Pulando diretório {pessoa_dir} devido ao filtro de pessoa"
                        )
                    continue

                for ano_dir in pessoa_dir.glob("*"):
                    if ano_dir.is_dir() and ano_dir.name.isdigit():
                        # Verificar filtro de ano
                        if self.ano_filter and ano_dir.name != self.ano_filter:
                            if self.verbose:
                                self.logger.info(
                                    f"Pulando diretório {ano_dir} devido ao filtro de ano"
                                )
                            continue

                        # Este é um diretório no formato <pessoa>/<ano>/
                        valid_directories.append(ano_dir)

        # 2. Para cada diretório válido, verificar arquivos de dados alternativos
        alt_formats_count = 0
        for directory in valid_directories:
            person = directory.parent.name
            year = directory.name

            # Lista de arquivos alternativos para procurar
            alt_files = [
                "resultado.yaml",
                "resultado.yml",
                "resultado.csv",
                "resultado.xlsx",
                "resultado.xls",
                "avaliacao.json",
                "avaliacao.yaml",
                "avaliacao.yml",
                "evaluation.json",
                "evaluation.yaml",
                "evaluation.yml",
            ]

            for alt_file in alt_files:
                file_path = directory / alt_file
                if file_path.exists() and file_path.stat().st_size > 0:
                    self.logger.info(f"Encontrado arquivo alternativo: {file_path}")
                    alt_formats_count += 1

                    # Determinar o formato baseado na extensão
                    format_type = "json"
                    if file_path.suffix in [".yaml", ".yml"]:
                        format_type = "yaml"
                    elif file_path.suffix == ".csv":
                        format_type = "csv"
                    elif file_path.suffix in [".xlsx", ".xls"]:
                        format_type = "excel"

                    # Verificar se este formato deve ser processado
                    if (
                        self.selected_formats != "all"
                        and format_type != self.selected_formats
                    ):
                        self.logger.info(
                            f"Pulando arquivo {file_path} por não corresponder ao formato selecionado ({self.selected_formats})"
                        )
                        continue

                    try:
                        # Importar arquivo usando o formato correto
                        processor.import_file(
                            file_path, format=format_type, data_type="evaluations"
                        )
                        results.append(f"Arquivo alternativo processado: {file_path}")
                    except Exception as e:
                        self.logger.error(f"Erro ao processar {file_path}: {str(e)}")
                        results.append(
                            f"Erro ao processar arquivo alternativo {file_path}: {str(e)}"
                        )
                        if not self.ignore_errors:
                            raise

        if alt_formats_count > 0:
            results.append(
                f"Processados {alt_formats_count} arquivos em formatos alternativos"
            )

        # Verificar resultados do padrão principal
        if import_results["imported"] > 0:
            results.append(
                f"Importados {import_results['imported']} arquivos de resultado.json"
            )

            # Gerar relatórios com base nos dados importados
            try:
                # Gerar relatório individual para cada pessoa
                individual_reports = processor.generate_individual_report()
                if individual_reports:
                    results.append(
                        f"Gerados {len(individual_reports)} relatórios individuais"
                    )

                # Pular visualizações se definido
                if not self.skip_viz:
                    # Gerar sumário
                    summary_path = processor.generate_summary(format="html")
                    if summary_path:
                        results.append(f"Sumário dos dados gerado em {summary_path}")

                    # Gerar versão em markdown também
                    summary_md_path = processor.generate_summary(format="markdown")
                    if summary_md_path:
                        results.append(
                            f"Sumário dos dados em markdown gerado em {summary_md_path}"
                        )

                    # Gerar gráficos
                    radar_charts = processor.generate_radar_chart()
                    if radar_charts:
                        results.append(f"Gerados {len(radar_charts)} gráficos de radar")

                    # Gerar comparação de equipes
                    team_report = processor.generate_team_aggregation()
                    if team_report:
                        results.append(f"Comparação de equipes gerada em {team_report}")

                    # Gerar mapa de calor
                    heat_map = processor.generate_heat_map()
                    if heat_map:
                        results.append("Mapa de calor gerado")

                    # Gerar diagramas
                    mermaid_chart = processor.generate_mermaid_chart()
                    if mermaid_chart:
                        results.append(f"Diagrama Mermaid gerado em {mermaid_chart}")
                else:
                    results.append(
                        "Geração de visualizações pulada devido à flag --skip-viz"
                    )

                # Gerar planos de ação (não é considerado visualização)
                try:
                    action_plans = processor.generate_action_plan()
                    if action_plans:
                        results.append(f"Gerados {len(action_plans)} planos de ação")
                except Exception as e:
                    error_msg = f"Erro ao gerar planos de ação: {str(e)}"
                    self.logger.error(error_msg)
                    results.append(error_msg)
                    if not self.ignore_errors:
                        raise

                # Gerar relatório em linguagem natural (não é considerado visualização)
                try:
                    nl_summaries = processor.generate_natural_language_summary()
                    if nl_summaries:
                        results.append(
                            f"Gerados {len(nl_summaries)} sumários em linguagem natural"
                        )
                except Exception as e:
                    error_msg = f"Erro ao gerar sumários em linguagem natural: {str(e)}"
                    self.logger.error(error_msg)
                    results.append(error_msg)
                    if not self.ignore_errors:
                        raise

                # Gerar relatório de benchmark (não é considerado visualização)
                try:
                    benchmark_reports = processor.generate_benchmark_report()
                    if benchmark_reports:
                        results.append(
                            f"Gerados {len(benchmark_reports)} relatórios de benchmark"
                        )
                except Exception as e:
                    error_msg = f"Erro ao gerar relatórios de benchmark: {str(e)}"
                    self.logger.error(error_msg)
                    results.append(error_msg)
                    if not self.ignore_errors:
                        raise

                # Gerar gráficos individuais para todas as pessoas
                processor.generate_individual_reports()
                results.append("Gerados relatórios individuais consolidados")

            except Exception as e:
                error_msg = f"Erro ao gerar relatórios: {str(e)}"
                self.logger.error(error_msg)
                results.append(error_msg)
        else:
            if import_results["skipped"] > 0:
                results.append(
                    f"Ignorados {import_results['skipped']} arquivos por problemas de estrutura"
                )
            if import_results["failed"] > 0:
                results.append(
                    f"Falha ao processar {import_results['failed']} arquivos"
                )
                for error in import_results["errors"]:
                    self.logger.error(f"Erro: {error['file']} - {error['error']}")

            if alt_formats_count == 0:
                results.append(
                    "Nenhum arquivo válido encontrado na estrutura <pessoa>/<ano>/"
                )

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
        results = []

        try:
            # Criar diretório de consolidação
            consolidation_dir = self.output_path / "consolidated"
            consolidation_dir.mkdir(exist_ok=True, parents=True)

            # Consolidar todos os dados disponíveis
            self.logger.info("Consolidando dados de todas as fontes")

            # Gerar dashboard HTML consolidado
            dashboard_path = (
                consolidation_dir
                / f"dashboard_{datetime.now().strftime('%Y%m%d')}.html"
            )

            html_content = [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                "    <meta charset='UTF-8'>",
                "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
                "    <title>People Analytics Dashboard</title>",
                "    <style>",
                "        body { font-family: Arial, sans-serif; margin: 0; padding: 0; }",
                "        .container { width: 90%; margin: 0 auto; }",
                "        header { background-color: #2c3e50; color: white; padding: 1rem; }",
                "        h1 { margin: 0; }",
                "        .report-section { margin-top: 2rem; }",
                "        .report-list { margin-top: 1rem; }",
                "        footer { margin-top: 2rem; padding: 1rem; background-color: #f5f5f5; text-align: center; }",
                "    </style>",
                "</head>",
                "<body>",
                "    <header>",
                "        <div class='container'>",
                f"            <h1>People Analytics Dashboard - {datetime.now().strftime('%Y-%m-%d')}</h1>",
                "        </div>",
                "    </header>",
                "    <div class='container'>",
            ]

            # Listar relatórios por seção
            sections = {
                "individual_reports": "Relatórios Individuais",
                "team_reports": "Relatórios de Equipes",
                "radar_charts": "Gráficos de Radar",
                "heat_maps": "Mapas de Calor",
                "action_plans": "Planos de Ação",
                "mermaid": "Diagramas",
                "summary": "Sumários",
            }

            for dir_name, section_title in sections.items():
                section_dir = self.output_path / dir_name
                if section_dir.exists():
                    files = list(section_dir.glob("*.*"))
                    if files:
                        html_content.append("        <div class='report-section'>")
                        html_content.append(f"            <h2>{section_title}</h2>")
                        html_content.append("            <div class='report-list'>")

                        for file in files:
                            html_content.append(
                                f"                <p><a href='../{dir_name}/{file.name}' target='_blank'>{file.name}</a></p>"
                            )

                        html_content.append("            </div>")
                        html_content.append("        </div>")

            # Adicionar lista de pessoas
            special_dirs = {
                "individual_reports",
                "logs",
                "action_plans",
                "summaries",
                "heat_maps",
                "benchmark_reports",
                "team_reports",
                "radar_charts",
                "stakeholder_analysis",
                "ai_prompts",
                "mermaid",
                "summary",
                "reports",
                "benchmarks",
                "docs",
                "teams",
                "time_series",
                "career_progression",
                "templates",
                "data",
                "consolidated",
            }

            person_dirs = [
                d
                for d in self.output_path.glob("*")
                if d.is_dir() and d.name not in special_dirs
            ]

            if person_dirs:
                html_content.append("        <div class='report-section'>")
                html_content.append("            <h2>Pessoas</h2>")
                html_content.append("            <div class='report-list'>")

                for person_dir in person_dirs:
                    files = list(person_dir.glob("*.*"))
                    if files:
                        html_content.append(
                            f"                <h3>{person_dir.name}</h3>"
                        )
                        for file in files:
                            html_content.append(
                                f"                <p><a href='../{person_dir.name}/{file.name}' target='_blank'>{file.name}</a></p>"
                            )

                html_content.append("            </div>")
                html_content.append("        </div>")

            # Finalizar HTML
            html_content.extend(
                [
                    "    </div>",
                    "    <footer>",
                    "        <div class='container'>",
                    f"            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
                    "        </div>",
                    "    </footer>",
                    "</body>",
                    "</html>",
                ]
            )

            # Salvar HTML
            with open(dashboard_path, "w", encoding="utf-8") as f:
                f.write("\n".join(html_content))

            results.append(f"Dashboard consolidado gerado em {dashboard_path}")

            return results

        except Exception as e:
            error_msg = f"Erro na consolidação de dados: {str(e)}"
            self.logger.error(error_msg)
            return [error_msg]

    def _process_additional_data_formats(self) -> List[str]:
        """Processa formatos adicionais de dados como CSV, Excel, etc."""
        from peopleanalytics.data_processor import DataProcessor

        results = []
        processor = DataProcessor(self.data_path, self.output_path)

        # Determinar quais formatos processar
        process_csv = self.selected_formats in ["csv", "all"]
        process_excel = self.selected_formats in ["excel", "all"]
        process_yaml = self.selected_formats in ["yaml", "all"]

        # Processar arquivos CSV
        if process_csv:
            csv_files = list(self.data_path.glob("*.csv"))
            csv_files.extend(list(self.data_path.glob("**/*.csv")))

            if csv_files:
                results.append(f"Encontrados {len(csv_files)} arquivos CSV")

                for csv_file in csv_files:
                    try:
                        self.logger.info(f"Processando arquivo CSV: {csv_file}")
                        # Tentar processar como dados de avaliação
                        processor.import_file(
                            csv_file, data_type="evaluations", format="csv"
                        )
                        results.append(f"Arquivo CSV processado: {csv_file.name}")
                    except Exception as e:
                        error_msg = (
                            f"Erro ao processar arquivo CSV {csv_file.name}: {str(e)}"
                        )
                        self.logger.error(error_msg)
                        results.append(error_msg)
                        if not self.ignore_errors:
                            raise

        # Processar arquivos Excel
        if process_excel:
            excel_files = list(self.data_path.glob("*.xlsx"))
            excel_files.extend(list(self.data_path.glob("**/*.xlsx")))
            excel_files.extend(list(self.data_path.glob("*.xls")))
            excel_files.extend(list(self.data_path.glob("**/*.xls")))

            if excel_files:
                results.append(f"Encontrados {len(excel_files)} arquivos Excel")

                for excel_file in excel_files:
                    try:
                        self.logger.info(f"Processando arquivo Excel: {excel_file}")
                        # Tentar processar como dados de avaliação
                        processor.import_file(
                            excel_file, data_type="evaluations", format="excel"
                        )
                        results.append(f"Arquivo Excel processado: {excel_file.name}")
                    except Exception as e:
                        error_msg = f"Erro ao processar arquivo Excel {excel_file.name}: {str(e)}"
                        self.logger.error(error_msg)
                        results.append(error_msg)
                        if not self.ignore_errors:
                            raise

        # Processar arquivos YAML
        if process_yaml:
            yaml_files = list(self.data_path.glob("*.yaml"))
            yaml_files.extend(list(self.data_path.glob("**/*.yaml")))
            yaml_files.extend(list(self.data_path.glob("*.yml")))
            yaml_files.extend(list(self.data_path.glob("**/*.yml")))

            if yaml_files:
                results.append(f"Encontrados {len(yaml_files)} arquivos YAML")

                for yaml_file in yaml_files:
                    try:
                        self.logger.info(f"Processando arquivo YAML: {yaml_file}")
                        # Tentar processar como dados de avaliação
                        processor.import_file(
                            yaml_file, data_type="evaluations", format="yaml"
                        )
                        results.append(f"Arquivo YAML processado: {yaml_file.name}")
                    except Exception as e:
                        error_msg = (
                            f"Erro ao processar arquivo YAML {yaml_file.name}: {str(e)}"
                        )
                        self.logger.error(error_msg)
                        results.append(error_msg)
                        if not self.ignore_errors:
                            raise

        return results


class SyncCommand(BaseCommand):
    """Command to synchronize data and generate reports."""

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.sync = None

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "--data-path",
            "-d",
            type=str,
            help="Caminho para o diretório de dados. Processa recursivamente a estrutura <pessoa>/<ano>/resultado.json",
        )
        parser.add_argument(
            "--output-path",
            "-o",
            type=str,
            help="Caminho para o diretório de saída onde serão salvos os relatórios e visualizações",
        )
        parser.add_argument(
            "--force",
            "-f",
            action="store_true",
            help="Forçar reprocessamento de arquivos já processados",
        )
        parser.add_argument(
            "--formatos",
            choices=["json", "yaml", "csv", "excel", "all"],
            default="all",
            help="Formatos de arquivo a serem processados (padrão: todos)",
        )
        parser.add_argument(
            "--pessoa",
            type=str,
            help="Filtrar processamento para uma pessoa específica",
        )
        parser.add_argument(
            "--ano", type=str, help="Filtrar processamento para um ano específico"
        )
        parser.add_argument(
            "--gerar-dashboard",
            action="store_true",
            default=True,
            help="Gerar dashboard consolidado (padrão: True)",
        )
        parser.add_argument(
            "--skip-viz",
            action="store_true",
            help="Pular geração de visualizações (gráficos, diagramas) para processamento mais rápido",
        )
        parser.add_argument(
            "--ignore-errors",
            action="store_true",
            help="Continuar processamento mesmo quando encontrar erros",
        )
        parser.add_argument(
            "--compress-output",
            action="store_true",
            help="Comprimir resultados em um arquivo ZIP após processamento",
        )
        parser.add_argument(
            "--export-excel",
            action="store_true",
            help="Exportar dados consolidados para Excel",
        )
        parser.add_argument(
            "--verbose",
            "-v",
            action="store_true",
            help="Mostrar informações detalhadas durante o processamento",
        )

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the sync command."""
        self.console.print("[bold]Synchronizing data and generating reports...[/bold]")
        self.console.print(
            "[bold]Processando estrutura <pessoa>/<ano>/resultado.json e perfil.json[/bold]"
        )

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

            # Configurar nível de log baseado na flag ignore_errors
            log_level = logging.WARNING if args.ignore_errors else logging.INFO

            logging.basicConfig(
                level=log_level,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.StreamHandler(sys.stdout),
                    logging.FileHandler(log_file),
                ],
            )

            # Display input parameters
            self.console.print(f"[cyan]Diretório de dados:[/cyan] {data_path}")
            self.console.print(f"[cyan]Diretório de saída:[/cyan] {output_path}")
            self.console.print(
                f"[cyan]Forçar reprocessamento:[/cyan] {'Sim' if args.force else 'Não'}"
            )
            self.console.print(f"[cyan]Formatos a processar:[/cyan] {args.formatos}")

            if args.pessoa:
                self.console.print(f"[cyan]Filtro de pessoa:[/cyan] {args.pessoa}")
            if args.ano:
                self.console.print(f"[cyan]Filtro de ano:[/cyan] {args.ano}")

            self.console.print(
                f"[cyan]Ignorar erros:[/cyan] {'Sim' if args.ignore_errors else 'Não'}"
            )
            self.console.print(
                f"[cyan]Pular visualizações:[/cyan] {'Sim' if args.skip_viz else 'Não'}"
            )
            self.console.print(
                f"[cyan]Compactar resultados:[/cyan] {'Sim' if args.compress_output else 'Não'}"
            )
            self.console.print(
                f"[cyan]Exportar para Excel:[/cyan] {'Sim' if args.export_excel else 'Não'}"
            )
            self.console.print(
                f"[cyan]Modo verboso:[/cyan] {'Sim' if args.verbose else 'Não'}"
            )
            self.console.print(
                "[cyan]Estrutura esperada:[/cyan] <pessoa>/<ano>/resultado.json"
            )
            self.console.print()

            # Initialize sync object
            self.sync = DataSync(data_path, output_path, args.force)

            # Configurar opções adicionais
            self.sync.skip_viz = args.skip_viz
            self.sync.ignore_errors = args.ignore_errors
            self.sync.selected_formats = args.formatos
            self.sync.pessoa_filter = args.pessoa
            self.sync.ano_filter = args.ano
            self.sync.export_excel = args.export_excel
            self.sync.verbose = args.verbose

            # Perform sync operations
            with Progress() as progress:
                task = progress.add_task("Processando dados...", total=None)

                try:
                    results = self.sync.run()
                except Exception as e:
                    if args.ignore_errors:
                        self.console.print(
                            f"[yellow]Erro durante o processamento, mas continuando:[/yellow] {str(e)}"
                        )
                        results = [
                            "Erro durante o processamento, mas continuando devido à flag --ignore-errors"
                        ]
                    else:
                        raise

                progress.update(task, completed=1)

            # Display results
            self.console.print("\n[bold]Resultados da Sincronização:[/bold]")
            for result in results:
                self.console.print(f"- {result}")

            # Compress results if requested
            if args.compress_output:
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    zip_path = Path.cwd() / f"output_sync_{timestamp}.zip"

                    import os
                    import zipfile

                    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                        for root, dirs, files in os.walk(output_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, output_path)
                                zipf.write(file_path, arcname)

                    self.console.print(
                        f"\n[green]Resultados compactados em:[/green] {zip_path}"
                    )
                except Exception as e:
                    self.console.print(
                        f"[red]Erro ao compactar resultados:[/red] {str(e)}"
                    )

            return 0

        except Exception as e:
            self.console.print(f"[red]Erro na sincronização:[/red] {str(e)}")
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
