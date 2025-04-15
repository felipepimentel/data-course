"""
Sync and documentation commands for People Analytics CLI.

This module contains commands for data synchronization and documentation generation.
"""

import argparse
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader


def setup_logger(name):
    """Setup and return a logger with the given name."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Set level
        logger.setLevel(logging.INFO)

        # Create console handler
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

    return logger


class DataSync:
    """Class that implements the sync functionality."""

    def __init__(
        self,
        data_dir="./data",
        output_dir="./output",
        force=False,
        skip_viz=False,
        ignore_errors=False,
        selected_formats="all",
        compress=False,
        pessoa_filter=None,
        ano_filter=None,
        export_excel=False,
        verbose=False,
        skip_benchmark=False,
    ):
        """
        Initialize the DataSync class

        Args:
            data_dir (str): Path to the data directory
            output_dir (str): Path to the output directory
            force (bool): Force reprocessing of files
            skip_viz (bool): Skip generation of visualizations
            ignore_errors (bool): Ignore errors during processing
            selected_formats (str): Formats to process (comma-separated, e.g., 'json,yaml,csv,excel')
            compress (bool): Compress output files
            pessoa_filter (str): Filter processing for a specific person
            ano_filter (str): Filter processing for a specific year
            export_excel (bool): Export consolidated data to Excel
            verbose (bool): Show detailed information during processing
            skip_benchmark (bool): Skip generation of benchmark reports
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        # Alias for compatibility with existing code
        self.data_path = self.data_dir
        self.output_path = self.output_dir

        self.force = force
        self.skip_viz = skip_viz
        self.ignore_errors = ignore_errors
        self.selected_formats = selected_formats
        self.compress = compress
        self.pessoa_filter = pessoa_filter
        self.ano_filter = ano_filter
        self.export_excel = export_excel
        self.verbose = verbose
        self.skip_benchmark = skip_benchmark
        self.log = setup_logger(self.__class__.__name__)
        # Alias for compatibility with existing code
        self.logger = self.log

        # Configurações adicionais
        self.export_pdf = False
        self.synthetic = False
        self.bulk_export = False

        # Estatísticas de processamento
        self.stats = {
            "total_files": 0,
            "processed_files": 0,
            "skipped_files": 0,
            "error_files": 0,
            "generated_reports": 0,
            "generated_visualizations": 0,
        }

        # Criar diretórios necessários
        self._ensure_directories()

    def _ensure_directories(self):
        """Garante que todos os diretórios necessários existam."""
        # Diretórios de entrada
        self.data_dir.mkdir(exist_ok=True, parents=True)
        (self.data_dir / "json").mkdir(exist_ok=True, parents=True)
        (self.data_dir / "templates").mkdir(exist_ok=True, parents=True)
        (self.data_dir / "raw").mkdir(exist_ok=True, parents=True)
        (self.data_dir / "career_progression").mkdir(exist_ok=True, parents=True)

        # Diretórios de saída
        self.output_dir.mkdir(exist_ok=True, parents=True)
        (self.output_dir / "reports").mkdir(exist_ok=True, parents=True)
        (self.output_dir / "visualizations").mkdir(exist_ok=True, parents=True)
        (self.output_dir / "data").mkdir(exist_ok=True, parents=True)
        (self.output_dir / "logs").mkdir(exist_ok=True, parents=True)

        # Diretório de log
        Path("logs").mkdir(exist_ok=True, parents=True)

    def run(self) -> List[str]:
        """Executa o processo completo de sincronização."""
        results = []
        self.log.info("Iniciando processo de sincronização")

        if self.verbose:
            self.log.info(f"Diretório de entrada: {self.data_dir}")
            self.log.info(f"Diretório de saída: {self.output_dir}")
            self.log.info(f"Forçar reprocessamento: {self.force}")
            self.log.info(f"Pular visualizações: {self.skip_viz}")
            self.log.info(f"Formatos selecionados: {self.selected_formats}")
            if self.pessoa_filter:
                self.log.info(f"Filtro de pessoa: {self.pessoa_filter}")
            if self.ano_filter:
                self.log.info(f"Filtro de ano: {self.ano_filter}")
            if self.synthetic:
                self.log.info("Modo de dados sintéticos ativado")
            if self.bulk_export:
                self.log.info("Exportação em massa ativada")

        try:
            # Gerar dados sintéticos se solicitado
            if self.synthetic:
                if self.verbose:
                    self.log.info("Gerando dados sintéticos para teste...")
                synthetic_results = self._generate_synthetic_data()
                results.extend(synthetic_results)

            # 1. Processar arquivos JSON
            if self.verbose:
                self.log.info("Iniciando processamento de arquivos JSON...")
            json_results = self._process_json_files()
            results.extend(json_results)

            # 2. Processar estrutura <pessoa>/<ano>/resultado.json
            if self.verbose:
                self.log.info(
                    "Iniciando processamento da estrutura <pessoa>/<ano>/resultado.json..."
                )
            pessoa_ano_results = self._process_pessoa_ano_structure_files()
            results.extend(pessoa_ano_results)

            # 3. Processar dados de carreira
            if self.verbose:
                self.log.info("Iniciando processamento de dados de carreira...")
            career_results = self._process_career_data()
            results.extend(career_results)

            # 4. Processar templates personalizados
            if self.verbose:
                self.log.info("Iniciando processamento de templates...")
            template_results = self._process_templates()
            results.extend(template_results)

            # 5. Processar formatos adicionais de dados como CSV, Excel, etc.
            if self.verbose:
                self.log.info("Iniciando processamento de formatos adicionais...")
            additional_data_results = self._process_additional_data_formats()
            results.extend(additional_data_results)

            # Se não deve pular visualizações
            if not self.skip_viz:
                # 6. Gerar visualizações
                if self.verbose:
                    self.log.info("Iniciando geração de visualizações...")
                visualization_results = self._generate_visualizations()
                results.extend(visualization_results)

                # 7. Gerar relatórios
                if self.verbose:
                    self.log.info("Iniciando geração de relatórios...")
                report_results = self._generate_reports()
                results.extend(report_results)

            # 8. Consolidar dados
            if self.verbose:
                self.log.info("Iniciando consolidação de dados...")
            consolidation_results = self._consolidate_data()
            results.extend(consolidation_results)

            # 9. Realizar exportação em massa se solicitado
            if self.bulk_export:
                if self.verbose:
                    self.log.info("Iniciando exportação em massa...")
                bulk_export_results = self._bulk_export()
                results.extend(bulk_export_results)

            self.log.info("Processo de sincronização concluído com sucesso")
            if self.verbose:
                self.log.info(f"Total de resultados gerados: {len(results)}")
            return results

        except Exception as e:
            error_msg = f"Erro no processo de sincronização: {str(e)}"
            self.log.exception(error_msg)
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
        json_dir = self.data_dir / "json"

        if not json_dir.exists():
            return ["Diretório JSON não encontrado"]

        json_files = list(json_dir.glob("*.json"))
        if not json_files:
            return ["Nenhum arquivo JSON encontrado para processamento"]

        self.log.info(f"Processando {len(json_files)} arquivos JSON")

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

    def _process_pessoa_ano_structure_files(self) -> List[str]:
        """
        Processa a estrutura de diretórios <pessoa>/<ano> e seus arquivos resultado.json e perfil.json.
        Foco na estrutura de direcionadores no arquivo resultado.json.

        Returns:
            List[str]: Lista de mensagens de resultado do processamento
        """
        results = []

        if self.verbose:
            self.logger.info(
                "Processando estrutura <pessoa>/<ano> com arquivos resultado.json e perfil.json..."
            )

        # Encontrar diretórios de pessoas
        pessoa_dirs = []
        for item in self.data_path.glob("*"):
            if item.is_dir():
                # Aplicar filtro de pessoa se existir
                if self.pessoa_filter and item.name != self.pessoa_filter:
                    if self.verbose:
                        self.logger.info(
                            f"Pulando diretório {item.name} devido ao filtro de pessoa"
                        )
                    continue
                pessoa_dirs.append(item)

        if not pessoa_dirs:
            msg = "Nenhum diretório de pessoa encontrado"
            self.logger.warning(msg)
            results.append(msg)
            return results

        # Estatísticas
        pessoas_processadas = 0
        anos_processados = 0
        resultados_processados = 0
        perfis_processados = 0

        # Para cada pessoa, processar seus anos
        for pessoa_dir in pessoa_dirs:
            pessoa_nome = pessoa_dir.name

            # Encontrar diretórios de anos
            ano_dirs = []
            for ano_item in pessoa_dir.glob("*"):
                if ano_item.is_dir() and ano_item.name.isdigit():
                    # Aplicar filtro de ano se existir
                    if self.ano_filter and ano_item.name != self.ano_filter:
                        if self.verbose:
                            self.logger.info(
                                f"Pulando diretório {ano_item.name} devido ao filtro de ano"
                            )
                        continue
                    ano_dirs.append(ano_item)

            if not ano_dirs:
                if self.verbose:
                    self.logger.info(
                        f"Nenhum diretório de ano encontrado para {pessoa_nome}"
                    )
                continue

            # Processar cada ano
            for ano_dir in ano_dirs:
                ano = ano_dir.name

                if self.verbose:
                    self.logger.info(f"Processando {pessoa_nome}/{ano}")

                # Verificar existência de resultado.json
                resultado_file = ano_dir / "resultado.json"
                if not resultado_file.exists() or not resultado_file.is_file():
                    if self.verbose:
                        self.logger.warning(
                            f"Arquivo resultado.json não encontrado em {pessoa_nome}/{ano}"
                        )
                    continue

                # Verificar existência de perfil.json (opcional)
                perfil_file = ano_dir / "perfil.json"
                perfil_data = None
                if perfil_file.exists() and perfil_file.is_file():
                    try:
                        with open(perfil_file, "r", encoding="utf-8") as f:
                            perfil_data = json.load(f)
                        perfis_processados += 1
                        if self.verbose:
                            self.logger.info(
                                f"Perfil encontrado para {pessoa_nome}/{ano}"
                            )
                    except Exception as e:
                        error_msg = f"Erro ao processar perfil.json para {pessoa_nome}/{ano}: {str(e)}"
                        self.logger.error(error_msg)
                        results.append(error_msg)
                        if not self.ignore_errors:
                            raise
                else:
                    if self.verbose:
                        self.logger.warning(
                            f"Arquivo perfil.json não encontrado em {pessoa_nome}/{ano}"
                        )

                # Processar resultado.json
                try:
                    with open(resultado_file, "r", encoding="utf-8") as f:
                        resultado_data = json.load(f)

                    # Verificar estrutura esperada
                    if not self._validate_resultado_json(resultado_data):
                        error_msg = (
                            f"Formato inválido de resultado.json em {pessoa_nome}/{ano}"
                        )
                        self.logger.error(error_msg)
                        results.append(error_msg)
                        if not self.ignore_errors:
                            continue
                        else:
                            raise ValueError(error_msg)

                    # Processar os dados
                    self._process_resultado_json(
                        pessoa_nome, ano, resultado_data, perfil_data
                    )

                    resultados_processados += 1
                    anos_processados += 1
                    if self.verbose:
                        self.logger.info(
                            f"Resultado processado para {pessoa_nome}/{ano}"
                        )

                except Exception as e:
                    error_msg = f"Erro ao processar resultado.json para {pessoa_nome}/{ano}: {str(e)}"
                    self.logger.error(error_msg)
                    results.append(error_msg)
                    if not self.ignore_errors:
                        continue
                    else:
                        raise

            # Incrementar contador de pessoas se pelo menos um ano foi processado
            if anos_processados > pessoas_processadas:
                pessoas_processadas += 1

        # Resumo
        results.append(f"Pessoas processadas: {pessoas_processadas}")
        results.append(f"Anos processados: {anos_processados}")
        results.append(f"Arquivos resultado.json processados: {resultados_processados}")
        results.append(f"Arquivos perfil.json processados: {perfis_processados}")

        return results

    def _validate_resultado_json(self, data: Dict[str, Any]) -> bool:
        """
        Valida a estrutura do arquivo resultado.json.

        Args:
            data: Dados do resultado.json

        Returns:
            bool: True se a estrutura for válida, False caso contrário
        """
        # Verificar estrutura básica
        if not isinstance(data, dict):
            self.logger.error("resultado.json: Não é um objeto JSON válido")
            return False

        # Verificar campos obrigatórios
        if "success" not in data:
            self.logger.error("resultado.json: Campo 'success' não encontrado")
            return False

        if "data" not in data:
            self.logger.error("resultado.json: Campo 'data' não encontrado")
            return False

        if not isinstance(data["data"], dict):
            self.logger.error(
                "resultado.json: Campo 'data' não é um objeto JSON válido"
            )
            return False

        # Verificar campo de direcionadores
        if "direcionadores" not in data["data"]:
            self.logger.error(
                "resultado.json: Campo 'direcionadores' não encontrado em 'data'"
            )
            return False

        if not isinstance(data["data"]["direcionadores"], list):
            self.logger.error("resultado.json: Campo 'direcionadores' não é uma lista")
            return False

        # Verificar pelo menos um direcionador
        if len(data["data"]["direcionadores"]) == 0:
            self.logger.warning("resultado.json: Lista de direcionadores vazia")
            # Não consideramos isso um erro, apenas um aviso

        return True

    def _process_resultado_json(
        self,
        pessoa: str,
        ano: str,
        resultado_data: Dict[str, Any],
        perfil_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Processa os dados do resultado.json e perfil.json para uma pessoa/ano.

        Args:
            pessoa: Nome da pessoa
            ano: Ano dos dados
            resultado_data: Dados do resultado.json
            perfil_data: Dados do perfil.json (opcional)
        """
        if self.verbose:
            self.logger.info(f"Processando dados para {pessoa}/{ano}")

        # Criar diretório de saída
        output_dir = self.output_path / "processed" / pessoa / ano
        output_dir.mkdir(parents=True, exist_ok=True)

        # Salvar dados combinados
        combined_data = {
            "pessoa": pessoa,
            "ano": ano,
            "timestamp": datetime.now().isoformat(),
            "resultado": resultado_data,
        }

        if perfil_data:
            combined_data["perfil"] = perfil_data

        # Salvar dados combinados
        combined_file = output_dir / "data_combined.json"
        with open(combined_file, "w", encoding="utf-8") as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)

        # Extrair e processar direcionadores
        direcionadores = resultado_data["data"]["direcionadores"]
        self._process_direcionadores(pessoa, ano, direcionadores, output_dir)

        # Gerar relatórios
        self._generate_reports_from_direcionadores(
            pessoa, ano, direcionadores, perfil_data, output_dir
        )

        # Gerar visualizações se não estiver pulando
        if not self.skip_viz:
            self._generate_visualizations_from_direcionadores(
                pessoa, ano, direcionadores, output_dir
            )

    def _process_direcionadores(
        self,
        pessoa: str,
        ano: str,
        direcionadores: List[Dict[str, Any]],
        output_dir: Path,
    ) -> None:
        """
        Processa os direcionadores do resultado.json.

        Args:
            pessoa: Nome da pessoa
            ano: Ano dos dados
            direcionadores: Lista de direcionadores
            output_dir: Diretório de saída
        """
        # Extrair todos os comportamentos
        all_comportamentos = []

        for direcionador in direcionadores:
            dir_nome = direcionador.get("direcionador", "Sem nome")

            if "comportamentos" not in direcionador or not isinstance(
                direcionador["comportamentos"], list
            ):
                continue

            for comportamento in direcionador["comportamentos"]:
                comp_nome = comportamento.get("comportamento", "Sem descrição")

                if "avaliacoes_grupo" not in comportamento or not isinstance(
                    comportamento["avaliacoes_grupo"], list
                ):
                    continue

                for avaliacao in comportamento["avaliacoes_grupo"]:
                    avaliador = avaliacao.get("avaliador", "Não especificado")
                    freq_colaborador = avaliacao.get("frequencia_colaborador", [])
                    freq_grupo = avaliacao.get("frequencia_grupo", [])

                    # Calcular valor médio
                    valor_colaborador = self._calculate_weighted_average(
                        freq_colaborador
                    )
                    valor_grupo = self._calculate_weighted_average(freq_grupo)

                    all_comportamentos.append(
                        {
                            "direcionador": dir_nome,
                            "comportamento": comp_nome,
                            "avaliador": avaliador,
                            "valor_colaborador": valor_colaborador,
                            "valor_grupo": valor_grupo,
                            "diferenca": valor_colaborador - valor_grupo,
                        }
                    )

        # Salvar dados processados
        processed_file = output_dir / "comportamentos_processed.json"
        with open(processed_file, "w", encoding="utf-8") as f:
            json.dump(all_comportamentos, f, indent=2, ensure_ascii=False)

        # Calcular estatísticas por direcionador
        dir_stats = {}
        for comp in all_comportamentos:
            dir_nome = comp["direcionador"]
            if dir_nome not in dir_stats:
                dir_stats[dir_nome] = {
                    "total": 0,
                    "soma_colaborador": 0,
                    "soma_grupo": 0,
                    "comportamentos": [],
                }

            dir_stats[dir_nome]["total"] += 1
            dir_stats[dir_nome]["soma_colaborador"] += comp["valor_colaborador"]
            dir_stats[dir_nome]["soma_grupo"] += comp["valor_grupo"]
            dir_stats[dir_nome]["comportamentos"].append(comp["comportamento"])

        # Calcular médias
        for dir_nome, stats in dir_stats.items():
            if stats["total"] > 0:
                stats["media_colaborador"] = stats["soma_colaborador"] / stats["total"]
                stats["media_grupo"] = stats["soma_grupo"] / stats["total"]
                stats["diferenca_media"] = (
                    stats["media_colaborador"] - stats["media_grupo"]
                )

        # Salvar estatísticas
        stats_file = output_dir / "direcionadores_stats.json"
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(dir_stats, f, indent=2, ensure_ascii=False)

    def _calculate_weighted_average(self, frequencias: List[int]) -> float:
        """
        Calcula a média ponderada de uma lista de frequências.

        Args:
            frequencias: Lista de frequências

        Returns:
            float: Média ponderada
        """
        if not frequencias or sum(frequencias) == 0:
            return 0

        # Calcular média ponderada (cada índice é um peso)
        total = 0
        peso_total = 0

        for i, freq in enumerate(frequencias):
            total += i * freq
            peso_total += freq

        return total / peso_total if peso_total > 0 else 0

    def _generate_reports_from_direcionadores(
        self,
        pessoa: str,
        ano: str,
        direcionadores: List[Dict[str, Any]],
        perfil_data: Optional[Dict[str, Any]],
        output_dir: Path,
    ) -> None:
        """
        Gera relatórios a partir dos direcionadores.

        Args:
            pessoa: Nome da pessoa
            ano: Ano dos dados
            direcionadores: Lista de direcionadores
            perfil_data: Dados do perfil (opcional)
            output_dir: Diretório de saída
        """
        # Carregar dados processados
        try:
            with open(
                output_dir / "comportamentos_processed.json", "r", encoding="utf-8"
            ) as f:
                comportamentos = json.load(f)

            with open(
                output_dir / "direcionadores_stats.json", "r", encoding="utf-8"
            ) as f:
                dir_stats = json.load(f)
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados processados: {str(e)}")
            if not self.ignore_errors:
                raise
            return

        # Extrair nome completo do perfil, se disponível
        nome_completo = pessoa
        if perfil_data and "nome_completo" in perfil_data:
            nome_completo = perfil_data["nome_completo"]

        # 1. Gerar relatório HTML
        html_file = output_dir / f"relatorio_{ano}.html"

        html_content = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Relatório {nome_completo} - {ano}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #333; }}
                .section {{ margin-bottom: 30px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .header {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #777; text-align: center; }}
                .positive {{ color: green; }}
                .negative {{ color: red; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Relatório Individual</h1>
                <p><strong>Nome:</strong> {nome_completo}</p>
                <p><strong>Ano:</strong> {ano}</p>
        """

        # Adicionar informações do perfil se disponível
        if perfil_data:
            html_content += f"""
                <p><strong>Cargo:</strong> {perfil_data.get("cargo", "Não especificado")}</p>
                <p><strong>Nível:</strong> {perfil_data.get("nivel_cargo", "Não especificado")}</p>
                <p><strong>Departamento:</strong> {perfil_data.get("nome_departamento", "Não especificado")}</p>
                <p><strong>Gestor:</strong> {perfil_data.get("nome_gestor", "Não especificado")}</p>
            """

        html_content += """
            </div>
            
            <div class="section">
                <h2>Resumo por Direcionador</h2>
                <table>
                    <tr>
                        <th>Direcionador</th>
                        <th>Média Colaborador</th>
                        <th>Média Grupo</th>
                        <th>Diferença</th>
                    </tr>
        """

        # Adicionar estatísticas por direcionador
        for dir_nome, stats in dir_stats.items():
            if "media_colaborador" in stats:
                diferenca = stats.get("diferenca_media", 0)
                diferenca_class = "positive" if diferenca >= 0 else "negative"

                html_content += f"""
                    <tr>
                        <td>{dir_nome}</td>
                        <td>{stats["media_colaborador"]:.2f}</td>
                        <td>{stats["media_grupo"]:.2f}</td>
                        <td class="{diferenca_class}">{diferenca:.2f}</td>
                    </tr>
                """

        html_content += """
                </table>
            </div>
            
            <div class="section">
                <h2>Detalhes dos Comportamentos</h2>
                <table>
                    <tr>
                        <th>Direcionador</th>
                        <th>Comportamento</th>
                        <th>Avaliador</th>
                        <th>Valor Colaborador</th>
                        <th>Valor Grupo</th>
                        <th>Diferença</th>
                    </tr>
        """

        # Adicionar detalhes de cada comportamento
        for comp in comportamentos:
            diferenca = comp.get("diferenca", 0)
            diferenca_class = "positive" if diferenca >= 0 else "negative"

            html_content += f"""
                <tr>
                    <td>{comp["direcionador"]}</td>
                    <td>{comp["comportamento"]}</td>
                    <td>{comp["avaliador"]}</td>
                    <td>{comp["valor_colaborador"]:.2f}</td>
                    <td>{comp["valor_grupo"]:.2f}</td>
                    <td class="{diferenca_class}">{diferenca:.2f}</td>
                </tr>
            """

        html_content += (
            """
                </table>
            </div>
            
            <div class="footer">
                <p>Relatório gerado automaticamente em """
            + datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            + """</p>
            </div>
        </body>
        </html>
        """
        )

        # Salvar o relatório HTML
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        # 2. Gerar relatório Markdown (resumido)
        md_file = output_dir / f"relatorio_{ano}.md"

        md_content = f"""# Relatório {nome_completo} - {ano}

## Informações Gerais
- **Nome:** {nome_completo}
- **Ano:** {ano}
"""

        if perfil_data:
            md_content += f"""- **Cargo:** {perfil_data.get("cargo", "Não especificado")}
- **Nível:** {perfil_data.get("nivel_cargo", "Não especificado")}
- **Departamento:** {perfil_data.get("nome_departamento", "Não especificado")}
- **Gestor:** {perfil_data.get("nome_gestor", "Não especificado")}
"""

        md_content += """
## Resumo por Direcionador

| Direcionador | Média Colaborador | Média Grupo | Diferença |
|--------------|-------------------|-------------|-----------|
"""

        # Adicionar estatísticas por direcionador
        for dir_nome, stats in dir_stats.items():
            if "media_colaborador" in stats:
                md_content += f"| {dir_nome} | {stats['media_colaborador']:.2f} | {stats['media_grupo']:.2f} | {stats['diferenca_media']:.2f} |\n"

        md_content += f"""
---
Relatório gerado automaticamente em {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
"""

        # Salvar o relatório Markdown
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

    def _generate_visualizations_from_direcionadores(
        self,
        pessoa: str,
        ano: str,
        direcionadores: List[Dict[str, Any]],
        output_dir: Path,
    ) -> None:
        """
        Gera visualizações a partir dos direcionadores.

        Args:
            pessoa: Nome da pessoa
            ano: Ano dos dados
            direcionadores: Lista de direcionadores
            output_dir: Diretório de saída
        """
        # Carregar dados processados
        try:
            with open(
                output_dir / "direcionadores_stats.json", "r", encoding="utf-8"
            ) as f:
                dir_stats = json.load(f)
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados processados: {str(e)}")
            if not self.ignore_errors:
                raise
            return

        try:
            import matplotlib.pyplot as plt
            import numpy as np

            # 1. Criar gráfico de barras comparando médias por direcionador
            plt.figure(figsize=(12, 6))

            # Preparar dados
            dir_nomes = list(dir_stats.keys())
            colaborador_vals = [
                dir_stats[d]["media_colaborador"]
                for d in dir_nomes
                if "media_colaborador" in dir_stats[d]
            ]
            grupo_vals = [
                dir_stats[d]["media_grupo"]
                for d in dir_nomes
                if "media_grupo" in dir_stats[d]
            ]

            # Configurar posições das barras
            x = np.arange(len(dir_nomes))
            width = 0.35

            # Criar barras
            plt.bar(x - width / 2, colaborador_vals, width, label="Colaborador")
            plt.bar(x + width / 2, grupo_vals, width, label="Grupo")

            # Configurar gráfico
            plt.xlabel("Direcionador")
            plt.ylabel("Média")
            plt.title(f"Comparação por Direcionador - {pessoa} ({ano})")
            plt.xticks(x, dir_nomes, rotation=45, ha="right")
            plt.legend()
            plt.tight_layout()

            # Salvar gráfico
            bar_file = output_dir / f"direcionadores_bar_{ano}.png"
            plt.savefig(bar_file)
            plt.close()

            # 2. Criar gráfico de radar comparando médias
            plt.figure(figsize=(10, 10), subplot_kw=dict(polar=True))

            # Preparar dados para radar
            angles = np.linspace(0, 2 * np.pi, len(dir_nomes), endpoint=False).tolist()

            # Fechar o círculo repetindo o primeiro valor
            colaborador_vals_closed = colaborador_vals + [colaborador_vals[0]]
            grupo_vals_closed = grupo_vals + [grupo_vals[0]]
            angles_closed = angles + [angles[0]]
            dir_nomes_closed = dir_nomes + [dir_nomes[0]]

            # Plotar radar
            plt.polar(
                angles_closed,
                colaborador_vals_closed,
                "b-",
                linewidth=2,
                label="Colaborador",
            )
            plt.fill(angles_closed, colaborador_vals_closed, "b", alpha=0.1)
            plt.polar(
                angles_closed, grupo_vals_closed, "r-", linewidth=2, label="Grupo"
            )
            plt.fill(angles_closed, grupo_vals_closed, "r", alpha=0.1)

            # Configurar radar
            plt.xticks(angles, dir_nomes, size=10)
            plt.yticks([])
            plt.title(f"Radar de Direcionadores - {pessoa} ({ano})")
            plt.legend(loc="upper right")

            # Salvar radar
            radar_file = output_dir / f"direcionadores_radar_{ano}.png"
            plt.savefig(radar_file)
            plt.close()

        except ImportError:
            self.logger.warning(
                "Matplotlib não disponível. Impossível gerar visualizações."
            )
        except Exception as e:
            error_msg = f"Erro ao gerar visualizações: {str(e)}"
            self.logger.error(error_msg)
            if not self.ignore_errors:
                raise

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

    def _consolidate_data(self):
        """
        Consolidate all the data in the output directory into a single dashboard.
        """
        try:
            # Create consolidation directory
            consolidation_dir = self.output_path / "dashboard"
            consolidation_dir.mkdir(exist_ok=True)

            self.logger.info(f"Consolidating data in {consolidation_dir}")

            # Create HTML index
            template_env = Environment(
                loader=FileSystemLoader(Path(__file__).parent.parent / "templates")
            )
            template = template_env.get_template("dashboard.html")

            # Find all reports
            individual_reports = []
            team_reports = []
            summary_reports = []
            benchmark_reports = []

            # Individual reports
            pessoas_dir = self.output_path / "pessoas"
            if pessoas_dir.exists():
                for person_dir in pessoas_dir.glob("*"):
                    if not person_dir.is_dir():
                        continue

                    pessoa = person_dir.name

                    for year_dir in person_dir.glob("*"):
                        if not year_dir.is_dir():
                            continue

                        ano = year_dir.name
                        report_html = year_dir / "report.html"

                        if report_html.exists():
                            individual_reports.append(
                                {
                                    "path": report_html.relative_to(self.output_path),
                                    "name": f"{pessoa} - {ano}",
                                }
                            )

            # Team reports
            team_dir = self.output_path / "equipes"
            if team_dir.exists():
                for report_html in team_dir.glob("**/*.html"):
                    if report_html.is_file():
                        team_reports.append(
                            {
                                "path": report_html.relative_to(self.output_path),
                                "name": report_html.stem,
                            }
                        )

            # Summary reports
            summary_dir = self.output_path / "resumos"
            if summary_dir.exists():
                for report_html in summary_dir.glob("**/*.html"):
                    if report_html.is_file():
                        summary_reports.append(
                            {
                                "path": report_html.relative_to(self.output_path),
                                "name": report_html.stem,
                            }
                        )

            # Benchmark reports
            benchmark_dir = self.output_path / "benchmark"
            if benchmark_dir.exists():
                # Use index.html if available
                benchmark_index = benchmark_dir / "index.html"
                if benchmark_index.exists():
                    benchmark_reports.append(
                        {
                            "path": benchmark_index.relative_to(self.output_path),
                            "name": "Índice de Benchmarks",
                            "is_index": True,
                        }
                    )

                # Add individual benchmark reports
                for subdir in ["por_ano", "por_equipe", "evolucao"]:
                    subdir_path = benchmark_dir / subdir
                    if subdir_path.exists():
                        for report_html in subdir_path.glob("*.html"):
                            if report_html.is_file():
                                benchmark_reports.append(
                                    {
                                        "path": report_html.relative_to(
                                            self.output_path
                                        ),
                                        "name": f"{subdir.replace('_', ' ').title()}: {report_html.stem}",
                                        "is_index": False,
                                    }
                                )

                # Add main summary report
                resumo_geral = benchmark_dir / "resumo_geral.html"
                if resumo_geral.exists():
                    benchmark_reports.append(
                        {
                            "path": resumo_geral.relative_to(self.output_path),
                            "name": "Resumo Geral",
                            "is_index": False,
                        }
                    )

            # Render template
            html_content = template.render(
                individual_reports=individual_reports,
                team_reports=team_reports,
                summary_reports=summary_reports,
                benchmark_reports=benchmark_reports,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )

            # Save the HTML index
            index_path = consolidation_dir / "index.html"
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            self.logger.info(f"Dashboard created at {index_path}")

            # Export to Excel if requested
            if self.export_excel:
                self.logger.info("Exporting consolidated data to Excel...")

                try:
                    import pandas as pd

                    # Define the Excel file path
                    excel_path = (
                        consolidation_dir
                        / f"dados_consolidados_{datetime.now().strftime('%Y%m%d')}.xlsx"
                    )

                    # Create a Pandas Excel writer using XlsxWriter as the engine
                    with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
                        # Sheet for people data
                        pessoas_data = []

                        for person_dir in pessoas_dir.glob("*"):
                            if not person_dir.is_dir():
                                continue

                            pessoa = person_dir.name

                            for year_dir in person_dir.glob("*"):
                                if not year_dir.is_dir():
                                    continue

                                ano = year_dir.name
                                report_json = year_dir / "report.json"

                                if report_json.exists():
                                    try:
                                        with open(
                                            report_json, "r", encoding="utf-8"
                                        ) as f:
                                            report_data = json.load(f)

                                        person_data = {"Pessoa": pessoa, "Ano": ano}

                                        # Add evaluation data
                                        if "resultados" in report_data:
                                            for categoria, valor in report_data[
                                                "resultados"
                                            ].items():
                                                person_data[
                                                    f"Avaliação - {categoria}"
                                                ] = valor

                                        # Add career data
                                        if "carreira" in report_data:
                                            for key, value in report_data[
                                                "carreira"
                                            ].items():
                                                person_data[f"Carreira - {key}"] = value

                                        # Add action plan data
                                        if "plano_acao" in report_data:
                                            for i, item in enumerate(
                                                report_data["plano_acao"], 1
                                            ):
                                                person_data[f"Ação {i} - Descrição"] = (
                                                    item.get("descricao", "")
                                                )
                                                person_data[f"Ação {i} - Prazo"] = (
                                                    item.get("prazo", "")
                                                )
                                                person_data[
                                                    f"Ação {i} - Prioridade"
                                                ] = item.get("prioridade", "")

                                        pessoas_data.append(person_data)
                                    except Exception as e:
                                        self.logger.error(
                                            f"Error processing {report_json}: {str(e)}"
                                        )
                                        if not self.ignore_errors:
                                            raise

                        # Create DataFrame and save to Excel
                        if pessoas_data:
                            df_pessoas = pd.DataFrame(pessoas_data)
                            df_pessoas.to_excel(
                                writer, sheet_name="Pessoas", index=False
                            )

                        # Sheet for team data
                        if team_dir.exists():
                            team_data = []

                            for report_json in team_dir.glob("**/*.json"):
                                if report_json.is_file():
                                    try:
                                        with open(
                                            report_json, "r", encoding="utf-8"
                                        ) as f:
                                            team_report = json.load(f)

                                        team_info = {
                                            "Equipe": report_json.stem,
                                            "Caminho": str(
                                                report_json.relative_to(
                                                    self.output_path
                                                )
                                            ),
                                        }

                                        # Add team data
                                        for key, value in team_report.items():
                                            if isinstance(
                                                value, (str, int, float, bool)
                                            ):
                                                team_info[key] = value

                                        team_data.append(team_info)
                                    except Exception as e:
                                        self.logger.error(
                                            f"Error processing team report {report_json}: {str(e)}"
                                        )
                                        if not self.ignore_errors:
                                            raise

                            if team_data:
                                df_teams = pd.DataFrame(team_data)
                                df_teams.to_excel(
                                    writer, sheet_name="Equipes", index=False
                                )

                        # Sheet for all reports
                        reports_data = []

                        # Add all reports
                        for section_name, reports_list in [
                            ("Individual", individual_reports),
                            ("Equipe", team_reports),
                            ("Resumo", summary_reports),
                            ("Benchmark", benchmark_reports),
                        ]:
                            for report in reports_list:
                                reports_data.append(
                                    {
                                        "Tipo": section_name,
                                        "Nome": report["name"],
                                        "Caminho": str(report["path"]),
                                    }
                                )

                        if reports_data:
                            df_reports = pd.DataFrame(reports_data)
                            df_reports.to_excel(
                                writer, sheet_name="Relatórios", index=False
                            )

                    self.logger.info(f"Excel export completed: {excel_path}")

                except Exception as e:
                    self.logger.error(f"Error exporting to Excel: {str(e)}")
                    if not self.ignore_errors:
                        raise

        except Exception as e:
            self.logger.error(f"Error consolidating data: {str(e)}")
            if not self.ignore_errors:
                raise

    def _generate_comparisons_for_all_people(self) -> None:
        """Gera relatórios comparativos ano a ano para todas as pessoas."""
        logging.info("Generating year-over-year comparisons for all people...")

        # Encontrar todas as pessoas com dados processados
        pessoas = set()
        processed_dir = self.output_path / "processed"

        if not processed_dir.exists():
            logging.warning("Processed data directory not found. Skipping comparisons.")
            return

        # Coletar nomes de pessoas
        for person_dir in processed_dir.glob("*"):
            if person_dir.is_dir():
                pessoas.add(person_dir.name)

        if not pessoas:
            logging.warning(
                "No processed data found for any person. Skipping comparisons."
            )
            return

        # Gerar comparativos para cada pessoa
        for pessoa in sorted(pessoas):
            try:
                if self.verbose:
                    logging.info(f"Generating comparisons for {pessoa}")
                self._generate_year_over_year_comparisons(pessoa)
            except Exception as e:
                error_msg = f"Error generating comparisons for {pessoa}: {str(e)}"
                logging.error(error_msg)
                if not self.ignore_errors:
                    raise

    def _export_reports_to_pdf(self, consolidation_dir: Path) -> None:
        """
        Exporta os relatórios principais para PDF.

        Args:
            consolidation_dir: Diretório de consolidação
        """
        try:
            logging.info("Exporting reports to PDF...")

            # Create PDF directory
            pdf_dir = consolidation_dir / "pdf"
            pdf_dir.mkdir(exist_ok=True)

            # Try to use pdfkit if available, otherwise use a simple HTML approach
            try:
                import pdfkit

                has_pdfkit = True
            except ImportError:
                has_pdfkit = False
                logging.warning("pdfkit not installed. Using basic PDF export.")

            # Track exported PDFs
            exported_count = 0
            pdf_reports = []

            # Collect all HTML reports
            all_html_reports = []

            # 1. Individual reports by year
            for report_file in self.output_path.glob("processed/**/*.html"):
                all_html_reports.append(report_file)

            # 2. Comparative reports
            for report_file in self.output_path.glob("comparativos/**/*.html"):
                all_html_reports.append(report_file)

            # Export each report to PDF
            if has_pdfkit:
                for html_file in all_html_reports:
                    try:
                        # Create appropriate subdirectory in PDF folder
                        relative_path = html_file.relative_to(self.output_path)

                        # Extract parent directories
                        parent_dirs = list(relative_path.parents)[
                            :-1
                        ]  # Exclude the root
                        parent_dirs.reverse()  # Get them in order

                        # Create the subdirectory structure
                        pdf_subdir = pdf_dir
                        for parent in parent_dirs:
                            pdf_subdir = pdf_subdir / parent.name
                            pdf_subdir.mkdir(exist_ok=True)

                        # Define PDF output path
                        pdf_name = f"{html_file.stem}.pdf"
                        pdf_path = pdf_subdir / pdf_name

                        if self.verbose:
                            logging.info(f"Converting {html_file} to PDF...")

                        # Convert to PDF using pdfkit
                        pdfkit.from_file(str(html_file), str(pdf_path))
                        exported_count += 1
                        pdf_reports.append(pdf_path)

                    except Exception as e:
                        logging.error(f"Error converting {html_file} to PDF: {e}")
                        if not self.ignore_errors:
                            raise
            else:
                # Simple placeholder if pdfkit not available
                pdf_index_path = pdf_dir / "pdf_export.html"
                with open(pdf_index_path, "w") as f:
                    f.write(
                        "<html><head><title>PDF Export Not Available</title></head>"
                    )
                    f.write("<body><h1>PDF Export Not Available</h1>")
                    f.write(
                        "<p>To enable PDF export, install pdfkit and wkhtmltopdf:</p>"
                    )
                    f.write("<pre>pip install pdfkit</pre>")
                    f.write(
                        "<p>And install wkhtmltopdf from: https://wkhtmltopdf.org/downloads.html</p>"
                    )
                    f.write("</body></html>")

                pdf_reports.append(pdf_index_path)

            # Create a consolidated PDF index
            pdf_index_path = pdf_dir / "pdf_index.html"
            with open(pdf_index_path, "w") as f:
                f.write("<html><head><title>PDF Reports Index</title>")
                f.write("<style>body{font-family:Arial,sans-serif;margin:20px;}")
                f.write("h1{color:#333}h2{color:#666;margin-top:30px}")
                f.write("ul{list-style-type:none;padding:0}")
                f.write("li{margin:10px 0;padding:5px;border-bottom:1px solid #eee}")
                f.write("a{text-decoration:none;color:#0066cc}")
                f.write("</style></head><body>")
                f.write("<h1>PDF Reports Index</h1>")
                f.write(
                    f"<p>Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
                )

                if pdf_reports:
                    f.write("<ul>")
                    for pdf_path in sorted(pdf_reports):
                        rel_path = pdf_path.relative_to(self.output_path)
                        f.write(f"<li><a href='../{rel_path}'>{pdf_path.name}</a></li>")
                    f.write("</ul>")
                else:
                    f.write("<p>No PDF reports generated</p>")

                f.write("</body></html>")

            logging.info(f"Exported {exported_count} reports to PDF in {pdf_dir}")

        except Exception as e:
            logging.error(f"Error exporting to PDF: {e}")
            if not self.ignore_errors:
                raise

    def _export_data_to_excel(self, consolidation_dir: Path) -> None:
        """
        Exporta dados consolidados para Excel.

        Args:
            consolidation_dir: Diretório de consolidação
        """
        try:
            import pandas as pd

            logging.info("Exporting consolidated data to Excel...")

            excel_path = (
                consolidation_dir
                / f"dados_consolidados_{datetime.now().strftime('%Y%m%d')}.xlsx"
            )

            # Collect data for Excel workbook
            with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
                # 1. Pessoas sheet - Lista todas as pessoas com informações básicas
                pessoas_data = []
                for person_dir in self.output_path.glob("processed/*/"):
                    if person_dir.is_dir():
                        pessoa_name = person_dir.name
                        pessoa_info = {"Nome": pessoa_name, "Anos Disponíveis": []}

                        # Verificar anos disponíveis
                        for year_dir in person_dir.glob("*/"):
                            if year_dir.is_dir() and year_dir.name.isdigit():
                                pessoa_info["Anos Disponíveis"].append(year_dir.name)

                                # Tentar carregar informações do perfil
                                combined_file = year_dir / "data_combined.json"
                                if combined_file.exists():
                                    try:
                                        with open(
                                            combined_file, "r", encoding="utf-8"
                                        ) as f:
                                            combined_data = json.load(f)

                                            # Extrair dados do perfil mais recente
                                            if "perfil" in combined_data:
                                                perfil = combined_data["perfil"]
                                                for key, value in perfil.items():
                                                    # Não sobrescrever se já tiver um valor
                                                    if key not in pessoa_info:
                                                        pessoa_info[key] = value
                                    except Exception as e:
                                        if self.verbose:
                                            logging.warning(
                                                f"Error loading data for {pessoa_name}/{year_dir.name}: {e}"
                                            )

                        # Formatar a lista de anos como string
                        pessoa_info["Anos Disponíveis"] = ", ".join(
                            sorted(pessoa_info["Anos Disponíveis"])
                        )
                        pessoas_data.append(pessoa_info)

                # Criar DataFrame e exportar
                if pessoas_data:
                    df_pessoas = pd.DataFrame(pessoas_data)
                    df_pessoas.to_excel(writer, sheet_name="Pessoas", index=False)

                # 2. Direcionadores sheet - Compilar todos os direcionadores por pessoa/ano
                direcionadores_data = []

                for person_dir in self.output_path.glob("processed/*/"):
                    if person_dir.is_dir():
                        pessoa_name = person_dir.name

                        for year_dir in person_dir.glob("*/"):
                            if year_dir.is_dir() and year_dir.name.isdigit():
                                ano = year_dir.name

                                # Carregar estatísticas de direcionadores
                                stats_file = year_dir / "direcionadores_stats.json"
                                if stats_file.exists():
                                    try:
                                        with open(
                                            stats_file, "r", encoding="utf-8"
                                        ) as f:
                                            dir_stats = json.load(f)

                                            for dir_nome, stats in dir_stats.items():
                                                if "media_colaborador" in stats:
                                                    direcionadores_data.append(
                                                        {
                                                            "Pessoa": pessoa_name,
                                                            "Ano": ano,
                                                            "Direcionador": dir_nome,
                                                            "Média Colaborador": stats[
                                                                "media_colaborador"
                                                            ],
                                                            "Média Grupo": stats.get(
                                                                "media_grupo", "N/A"
                                                            ),
                                                            "Diferença": stats.get(
                                                                "diferenca_media", "N/A"
                                                            ),
                                                        }
                                                    )
                                    except Exception as e:
                                        if self.verbose:
                                            logging.warning(
                                                f"Error loading direcionadores for {pessoa_name}/{ano}: {e}"
                                            )

                # Criar DataFrame e exportar
                if direcionadores_data:
                    df_direcionadores = pd.DataFrame(direcionadores_data)
                    df_direcionadores.to_excel(
                        writer, sheet_name="Direcionadores", index=False
                    )

                # 3. Comportamentos sheet - Compilar todos os comportamentos por pessoa/ano
                comportamentos_data = []

                for person_dir in self.output_path.glob("processed/*/"):
                    if person_dir.is_dir():
                        pessoa_name = person_dir.name

                        for year_dir in person_dir.glob("*/"):
                            if year_dir.is_dir() and year_dir.name.isdigit():
                                ano = year_dir.name

                                # Carregar comportamentos processados
                                comp_file = year_dir / "comportamentos_processed.json"
                                if comp_file.exists():
                                    try:
                                        with open(
                                            comp_file, "r", encoding="utf-8"
                                        ) as f:
                                            comportamentos = json.load(f)

                                            for comp in comportamentos:
                                                comportamentos_data.append(
                                                    {
                                                        "Pessoa": pessoa_name,
                                                        "Ano": ano,
                                                        "Direcionador": comp.get(
                                                            "direcionador", ""
                                                        ),
                                                        "Comportamento": comp.get(
                                                            "comportamento", ""
                                                        ),
                                                        "Avaliador": comp.get(
                                                            "avaliador", ""
                                                        ),
                                                        "Valor Colaborador": comp.get(
                                                            "valor_colaborador", ""
                                                        ),
                                                        "Valor Grupo": comp.get(
                                                            "valor_grupo", ""
                                                        ),
                                                        "Diferença": comp.get(
                                                            "diferenca", ""
                                                        ),
                                                    }
                                                )
                                    except Exception as e:
                                        if self.verbose:
                                            logging.warning(
                                                f"Error loading comportamentos for {pessoa_name}/{ano}: {e}"
                                            )

                # Criar DataFrame e exportar
                if comportamentos_data:
                    df_comportamentos = pd.DataFrame(comportamentos_data)
                    df_comportamentos.to_excel(
                        writer, sheet_name="Comportamentos", index=False
                    )

                # 4. Evolução sheet - Mostrar evolução ao longo dos anos por pessoa
                evolucao_data = []

                # Coletar todos os direcionadores
                all_direcionadores = set()
                all_anos = sorted(list({comp["Ano"] for comp in direcionadores_data}))

                for item in direcionadores_data:
                    all_direcionadores.add(item["Direcionador"])

                # Para cada pessoa e direcionador, criar uma linha com valores para cada ano
                pessoas_list = sorted(
                    list({comp["Pessoa"] for comp in direcionadores_data})
                )

                for pessoa in pessoas_list:
                    for direcionador in sorted(all_direcionadores):
                        row_data = {"Pessoa": pessoa, "Direcionador": direcionador}

                        # Adicionar valores para cada ano
                        has_values = False
                        for ano in all_anos:
                            # Encontrar o valor para este ano/direcionador
                            for item in direcionadores_data:
                                if (
                                    item["Pessoa"] == pessoa
                                    and item["Direcionador"] == direcionador
                                    and item["Ano"] == ano
                                ):
                                    row_data[f"Valor {ano}"] = item["Média Colaborador"]
                                    has_values = True
                                    break
                            else:
                                row_data[f"Valor {ano}"] = None

                        # Só adicionar se tiver algum valor
                        if has_values:
                            evolucao_data.append(row_data)

                # Criar DataFrame e exportar
                if evolucao_data:
                    df_evolucao = pd.DataFrame(evolucao_data)
                    df_evolucao.to_excel(writer, sheet_name="Evolução", index=False)

            logging.info(f"Excel export completed: {excel_path}")

        except ImportError:
            logging.error("pandas not installed. Cannot export to Excel.")
        except Exception as e:
            logging.error(f"Error exporting to Excel: {e}")
            if not self.ignore_errors:
                raise

    def _process_file(self, file_path: Path) -> str:
        """Process a single data file.

        Args:
            file_path: Path to the data file

        Returns:
            str: Status message for this file
        """
        try:
            # Check if file should be processed based on format
            file_format = file_path.suffix.lower()[1:]  # Remove the dot

            # Map xlsx to excel
            if file_format == "xlsx":
                file_format = "excel"

            # Skip if format doesn't match selected formats
            if (
                self.selected_formats != "all"
                and file_format not in self.selected_formats.split(",")
            ):
                if self.verbose:
                    logging.info(
                        f"Skipping {file_path.name} (format {file_format} not selected)"
                    )
                return f"Skipped {file_path} (format not selected)"

            # Get output directory based on file structure
            relative_path = file_path.relative_to(self.data_path)
            parts = list(relative_path.parts)

            # Generate appropriate report name
            if len(parts) >= 2 and parts[-1] == "resultado.json":
                # This is the <pessoa>/<ano>/resultado.json structure
                pessoa = parts[0]
                ano = parts[1]
                report_prefix = f"{pessoa}_{ano}"
            else:
                # Use file name as prefix
                report_prefix = file_path.stem

            # Report generation would happen here
            # For each report type, create a different output file

            # Carrega os dados de acordo com a extensão
            data = None
            file_extension = file_path.suffix.lower()

            if file_extension == ".json":
                data = self._load_json(file_path)
            elif file_extension in [".yml", ".yaml"]:
                data = self._load_yaml(file_path)
            elif file_extension == ".csv":
                data = self._load_csv(file_path)
            elif file_extension in [".xls", ".xlsx", ".xlsm"]:
                data = self._load_excel(file_path)
            else:
                self.logger.warning(
                    f"Formato não suportado: {file_extension} para o arquivo {file_path}"
                )
                return False

            if not data:
                self.logger.error(f"Não foi possível carregar dados de {file_path}")
                return False

            # Gera a pasta de saída se não existir
            output_dir = self.output_path / "processed" / file_format
            output_dir.mkdir(parents=True, exist_ok=True)

            # Gera os relatórios
            self._generate_reports(data, file_path, output_dir)

            # Gera visualizações se não estiver pulando
            if not self.skip_viz:
                self._generate_visualizations(data, file_path, output_dir)

            # Gera plano de ação se os dados permitirem
            self._generate_action_plan(data, file_path, output_dir)

            return True
        except Exception as e:
            error_message = f"Erro ao processar arquivo {file_path}: {str(e)}"
            self.logger.error(error_message)
            if self.verbose:
                import traceback

                self.logger.error(traceback.format_exc())

            if not self.ignore_errors:
                raise Exception(error_message) from e

            return False

    def _process_additional_data_formats(self) -> List[str]:
        """Processa formatos adicionais de dados como CSV, Excel, YAML, etc."""
        results = []
        formats_to_process = {}

        # Verificar quais formatos devem ser processados
        if self.selected_formats == "all":
            formats_to_process = {
                "csv": "*.csv",
                "excel": ["*.xlsx", "*.xls"],
                "yaml": ["*.yaml", "*.yml"],
            }
        else:
            for fmt in self.selected_formats.split(","):
                fmt = fmt.strip().lower()
                if fmt == "csv":
                    formats_to_process["csv"] = "*.csv"
                elif fmt == "excel":
                    formats_to_process["excel"] = ["*.xlsx", "*.xls"]
                elif fmt == "yaml":
                    formats_to_process["yaml"] = ["*.yaml", "*.yml"]

        if not formats_to_process:
            return ["Nenhum formato adicional selecionado para processamento"]

        # Diretório para dados adicionais
        raw_dir = self.data_path / "raw"
        if not raw_dir.exists():
            return ["Diretório 'raw' para formatos adicionais não encontrado"]

        raw_dir.mkdir(exist_ok=True, parents=True)

        # Processar cada formato
        for fmt, patterns in formats_to_process.items():
            if not isinstance(patterns, list):
                patterns = [patterns]

            for pattern in patterns:
                files = list(raw_dir.glob(pattern))
                if files:
                    if self.verbose:
                        self.logger.info(f"Processando {len(files)} arquivos {fmt}")

                    for file_path in files:
                        try:
                            # Processar o arquivo
                            process_result = self._process_file(file_path)
                            if process_result:
                                results.append(f"Processado: {file_path}")
                            else:
                                results.append(f"Falha ao processar: {file_path}")

                        except Exception as e:
                            error_msg = f"Erro ao processar {file_path}: {str(e)}"
                            self.logger.error(error_msg)
                            results.append(error_msg)
                            if not self.ignore_errors:
                                raise

        if not results:
            results.append("Nenhum arquivo adicional encontrado para processamento")

        return results

    def _generate_synthetic_data(self) -> List[str]:
        """Gera dados sintéticos para teste."""
        results = []

        try:
            if self.verbose:
                self.logger.info("Gerando dados sintéticos para teste")

            # Criar diretório para dados sintéticos
            synthetic_dir = self.data_path / "synthetic"
            synthetic_dir.mkdir(exist_ok=True, parents=True)

            # Exemplo de dados sintéticos
            # 1. Estrutura pessoa/ano
            for pessoa_idx in range(1, 4):  # 3 pessoas
                pessoa_name = f"pessoa{pessoa_idx}"
                pessoa_dir = synthetic_dir / pessoa_name
                pessoa_dir.mkdir(exist_ok=True, parents=True)

                # Criar anos para cada pessoa
                for ano in range(2020, 2023):
                    ano_dir = pessoa_dir / str(ano)
                    ano_dir.mkdir(exist_ok=True, parents=True)

                    # Criar perfil.json DENTRO do diretório do ano
                    perfil_data = {
                        "nome_completo": f"Pessoa {pessoa_idx} Completo",
                        "funcional": f"F{pessoa_idx}00{ano - 2019}",
                        "funcional_gestor": f"G{pessoa_idx % 2 + 1}001",
                        "nome_gestor": f"Gestor {pessoa_idx % 2 + 1}",
                        "cargo": f"Cargo {pessoa_idx % 3 + 1}",
                        "codigo_cargo": f"CD{pessoa_idx % 3 + 1}",
                        "nivel_cargo": pessoa_idx % 5 + 1,
                        "nome_nivel_cargo": f"Nível {pessoa_idx % 5 + 1}",
                        "nome_departamento": f"Departamento {pessoa_idx % 3 + 1}",
                        "tipo_carreira": f"Tipo {pessoa_idx % 2 + 1}",
                        "codigo_comunidade": f"COM{pessoa_idx % 3 + 1}",
                        "nome_comunidade": f"Comunidade {pessoa_idx % 3 + 1}",
                        "codigo_squad": f"SQ{pessoa_idx}",
                        "nome_squad": f"Squad {pessoa_idx}",
                        "codigo_papel": f"PP{pessoa_idx}",
                        "nome_papel": f"Papel {pessoa_idx}",
                        "tipo_gestao": pessoa_idx % 2 == 0,
                        "is_congelamento": False,
                        "data_congelamento": None,
                    }

                    perfil_file = ano_dir / "perfil.json"
                    with open(perfil_file, "w", encoding="utf-8") as f:
                        json.dump(perfil_data, f, ensure_ascii=False, indent=2)

                    # Criar resultado.json para o ano com a estrutura correta
                    resultado_data = {
                        "success": True,
                        "status_code": 200,
                        "message": None,
                        "data": {
                            "conceito_ciclo_filho_descricao": "alinhado em relação ao grupo",
                            "nome_peer_group": None,
                            "direcionadores": [
                                {
                                    "direcionador": f"{i}. direcionador sintético {i}",
                                    "pergunta_final": False,
                                    "comportamentos": [
                                        {
                                            "comportamento": f"comportamento {j} do direcionador {i}.",
                                            "pergunta_final": False,
                                            "avaliacoes_grupo": [
                                                {
                                                    "avaliador": "todos",
                                                    "frequencia_colaborador": [
                                                        0,
                                                        0,
                                                        55,
                                                        36,
                                                        0,
                                                        9,
                                                    ],
                                                    "frequencia_grupo": [
                                                        1,
                                                        31,
                                                        47,
                                                        17,
                                                        4,
                                                        0,
                                                    ],
                                                },
                                                {
                                                    "avaliador": "pares e parceiros",
                                                    "frequencia_colaborador": [
                                                        0,
                                                        0,
                                                        60,
                                                        30,
                                                        0,
                                                        10,
                                                    ],
                                                    "frequencia_grupo": [
                                                        1,
                                                        33,
                                                        48,
                                                        15,
                                                        3,
                                                        0,
                                                    ],
                                                },
                                            ],
                                        }
                                        for j in range(
                                            1, 3
                                        )  # 2 comportamentos por direcionador
                                    ],
                                }
                                for i in range(1, 4)  # 3 direcionadores
                            ],
                        },
                    }

                    resultado_file = ano_dir / "resultado.json"
                    with open(resultado_file, "w", encoding="utf-8") as f:
                        json.dump(resultado_data, f, ensure_ascii=False, indent=2)

                    # Criar versões em outros formatos
                    if (
                        ano == 2022
                    ):  # Apenas para o último ano, criar em outros formatos
                        # YAML
                        import yaml

                        yaml_file = ano_dir / "resultado.yaml"
                        with open(yaml_file, "w", encoding="utf-8") as f:
                            yaml.dump(resultado_data, f, allow_unicode=True)

                        # CSV - simplificado, apenas competências
                        csv_file = ano_dir / "resultado.csv"
                        with open(csv_file, "w", encoding="utf-8") as f:
                            f.write(
                                "direcionador,comportamento,avaliador,valor_medio\n"
                            )
                            for dir in resultado_data["data"]["direcionadores"]:
                                for comp in dir["comportamentos"]:
                                    for aval in comp["avaliacoes_grupo"]:
                                        # Calcular um valor médio baseado nas frequências
                                        valores = aval["frequencia_colaborador"]
                                        peso_total = sum(valores)
                                        valor_medio = (
                                            sum([i * v for i, v in enumerate(valores)])
                                            / peso_total
                                            if peso_total > 0
                                            else 0
                                        )
                                        f.write(
                                            f'"{dir["direcionador"]}","{comp["comportamento"]}","{aval["avaliador"]}",{valor_medio:.2f}\n'
                                        )

            # 2. Arquivo JSON standalone
            json_dir = self.data_path / "json"
            json_dir.mkdir(exist_ok=True, parents=True)

            for idx in range(1, 3):
                standalone_data = {
                    "success": True,
                    "status_code": 200,
                    "message": None,
                    "data": {
                        "id": f"report_{idx}",
                        "descricao": f"Relatório sintético {idx}",
                        "data": datetime.now().isoformat(),
                        "direcionadores": [
                            {
                                "direcionador": f"Direcionador {j}",
                                "comportamentos": [
                                    {
                                        "comportamento": f"Comportamento {k}",
                                        "valor": (j * k * 10) % 100,
                                    }
                                    for k in range(1, 3)
                                ],
                            }
                            for j in range(1, 4)
                        ],
                    },
                }

                json_file = json_dir / f"report_{idx}.json"
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(standalone_data, f, ensure_ascii=False, indent=2)

            # 3. Arquivo raw no formato Excel/CSV
            raw_dir = self.data_path / "raw"
            raw_dir.mkdir(exist_ok=True, parents=True)

            # CSV
            csv_file = raw_dir / "dados_sinteticos.csv"
            with open(csv_file, "w", encoding="utf-8") as f:
                f.write("id,nome,valor,categoria\n")
                for i in range(1, 10):
                    f.write(f"{i},Item {i},{i * 11 % 100},Categoria {i % 3 + 1}\n")

            # Excel - simulado como JSON neste caso
            excel_data = {
                "success": True,
                "status_code": 200,
                "message": None,
                "data": {
                    "simulado": "Dados que seriam de um Excel",
                    "direcionadores": [
                        {
                            "direcionador": f"Direcionador Excel {i}",
                            "comportamentos": [
                                {
                                    "comportamento": f"Comportamento Excel {j}",
                                    "valor": (i * j * 7) % 100,
                                }
                                for j in range(1, 3)
                            ],
                        }
                        for i in range(1, 3)
                    ],
                },
            }

            excel_file = raw_dir / "dados_sinteticos.json"
            with open(excel_file, "w", encoding="utf-8") as f:
                json.dump(excel_data, f, ensure_ascii=False, indent=2)

            results.append(f"Gerados dados sintéticos em {synthetic_dir}")
            results.append(
                f"- {len(list(synthetic_dir.glob('**/resultado.json')))} arquivos estruturados"
            )
            results.append(f"- {len(list(json_dir.glob('*.json')))} arquivos JSON")
            results.append(f"- {len(list(raw_dir.glob('*.*')))} arquivos raw")

        except Exception as e:
            error_msg = f"Erro ao gerar dados sintéticos: {str(e)}"
            self.logger.error(error_msg)
            results.append(error_msg)
            if not self.ignore_errors:
                raise

        return results

    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Carrega dados de um arquivo JSON."""
        try:
            if self.verbose:
                self.logger.info(f"Carregando arquivo JSON: {file_path}")
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if self.verbose:
                self.logger.info(f"JSON carregado com sucesso: {file_path}")
            return data
        except Exception as e:
            self.logger.error(f"Erro ao carregar arquivo JSON {file_path}: {str(e)}")
            if not self.ignore_errors:
                raise
            return None

    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Carrega dados de um arquivo YAML."""
        try:
            if self.verbose:
                self.logger.info(f"Carregando arquivo YAML: {file_path}")
            import yaml

            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if self.verbose:
                self.logger.info(f"YAML carregado com sucesso: {file_path}")
            return data
        except Exception as e:
            self.logger.error(f"Erro ao carregar arquivo YAML {file_path}: {str(e)}")
            if not self.ignore_errors:
                raise
            return None

    def _load_csv(self, file_path: Path) -> Dict[str, Any]:
        """Carrega dados de um arquivo CSV e converte para dicionário."""
        try:
            if self.verbose:
                self.logger.info(f"Carregando arquivo CSV: {file_path}")
            import pandas as pd

            df = pd.read_csv(file_path, encoding="utf-8")

            # Converter DataFrame para dicionário estruturado
            result = {
                "data": df.to_dict(orient="records"),
                "columns": df.columns.tolist(),
                "shape": {"rows": df.shape[0], "columns": df.shape[1]},
            }
            if self.verbose:
                self.logger.info(
                    f"CSV carregado com sucesso: {file_path} ({df.shape[0]} linhas)"
                )
            return result
        except Exception as e:
            self.logger.error(f"Erro ao carregar arquivo CSV {file_path}: {str(e)}")
            if not self.ignore_errors:
                raise
            return None

    def _load_excel(self, file_path: Path) -> Dict[str, Any]:
        """Carrega dados de um arquivo Excel e converte para dicionário."""
        try:
            if self.verbose:
                self.logger.info(f"Carregando arquivo Excel: {file_path}")
            import pandas as pd

            # Ler todas as planilhas
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names

            result = {"sheets": {}, "sheet_names": sheet_names}

            for sheet in sheet_names:
                if self.verbose:
                    self.logger.info(f"Carregando planilha: {sheet}")
                df = pd.read_excel(file_path, sheet_name=sheet)
                result["sheets"][sheet] = {
                    "data": df.to_dict(orient="records"),
                    "columns": df.columns.tolist(),
                    "shape": {"rows": df.shape[0], "columns": df.shape[1]},
                }

            if self.verbose:
                self.logger.info(
                    f"Excel carregado com sucesso: {file_path} ({len(sheet_names)} planilhas)"
                )
            return result
        except Exception as e:
            self.logger.error(f"Erro ao carregar arquivo Excel {file_path}: {str(e)}")
            if not self.ignore_errors:
                raise
            return None

    def _generate_reports(
        self, data: Dict[str, Any], input_file: Path, output_dir: Path
    ) -> None:
        """
        Gera relatórios a partir dos dados processados.

        Args:
            data: Dados processados
            input_file: Arquivo de entrada
            output_dir: Diretório de saída
        """
        try:
            # Gera relatório individual
            self._generate_individual_report(data, input_file, output_dir)

            # Gera relatório de resumo
            self._generate_summary_report(data, input_file, output_dir)

            # Gera relatório de benchmark se tiver dados de equipe
            if "team" in data or "equipe" in data:
                self._generate_benchmark_report(data, input_file, output_dir)

            if self.verbose:
                self.logger.info(f"Relatórios gerados com sucesso para {input_file}")
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatórios para {input_file}: {str(e)}")
            if not self.ignore_errors:
                raise

    def _generate_individual_report(
        self, data: Dict[str, Any], input_file: Path, output_dir: Path
    ) -> None:
        """
        Gera relatório individual a partir dos dados.

        Args:
            data: Dados processados
            input_file: Arquivo de entrada
            output_dir: Diretório de saída
        """
        report_file = output_dir / "report.html"

        try:
            # Extrai informações principais
            nome = data.get("nome", "Sem nome")
            periodo = data.get("periodo", data.get("ano", "N/A"))
            resultados = data.get("resultados", data.get("resultados_avaliacao", {}))

            # Template simples para relatório individual
            html_content = f"""<!DOCTYPE html>
            <html>
            <head>
                <title>Relatório Individual - {nome}</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }}
                    .container {{ max-width: 1000px; margin: 0 auto; }}
                    .header {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .section {{ margin-bottom: 30px; }}
                    h1, h2, h3 {{ color: #2c3e50; }}
                    table {{ width: 100%; border-collapse: collapse; }}
                    th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                    th {{ background-color: #f2f2f2; }}
                    .footer {{ margin-top: 50px; text-align: center; font-size: 12px; color: #777; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Relatório Individual</h1>
                        <p><strong>Nome:</strong> {nome}</p>
                        <p><strong>Período:</strong> {periodo}</p>
                        <p><strong>Data de Geração:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
                    </div>
                    
                    <div class="section">
                        <h2>Resultados da Avaliação</h2>
            """

            # Adiciona resultados da avaliação
            if resultados:
                html_content += "<table><tr><th>Competência</th><th>Valor</th></tr>"
                for competencia, valor in resultados.items():
                    html_content += f"<tr><td>{competencia}</td><td>{valor}</td></tr>"
                html_content += "</table>"
            else:
                html_content += "<p>Nenhum resultado disponível.</p>"

            # Adiciona outras seções relevantes
            for section_name, section_data in data.items():
                if section_name in [
                    "nome",
                    "periodo",
                    "ano",
                    "resultados",
                    "resultados_avaliacao",
                ]:
                    continue

                if isinstance(section_data, dict) and section_data:
                    html_content += f"""
                    <div class="section">
                        <h2>{section_name.replace("_", " ").title()}</h2>
                    """

                    html_content += "<table><tr>"
                    for header in section_data.keys():
                        html_content += f"<th>{header}</th>"
                    html_content += "</tr><tr>"

                    for value in section_data.values():
                        html_content += f"<td>{value}</td>"

                    html_content += "</tr></table></div>"

            # Finaliza o HTML
            html_content += """
                    </div>
                    <div class="footer">
                        <p>Este relatório foi gerado automaticamente.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Salva o relatório
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            if self.verbose:
                self.logger.info(f"Relatório individual gerado: {report_file}")

        except Exception as e:
            self.logger.error(
                f"Erro ao gerar relatório individual para {input_file}: {str(e)}"
            )
            if not self.ignore_errors:
                raise

    def _generate_summary_report(
        self, data: Dict[str, Any], input_file: Path, output_dir: Path
    ) -> None:
        """
        Gera relatório de resumo a partir dos dados.

        Args:
            data: Dados processados
            input_file: Arquivo de entrada
            output_dir: Diretório de saída
        """
        summary_file = output_dir / "summary.html"

        try:
            # Extrai informações principais
            nome = data.get("nome", "Sem nome")
            periodo = data.get("periodo", data.get("ano", "N/A"))

            # Calcula estatísticas se houver resultados
            resultados = data.get("resultados", data.get("resultados_avaliacao", {}))
            estatisticas = {}

            if resultados:
                valores = [
                    float(v)
                    for v in resultados.values()
                    if isinstance(v, (int, float))
                    or (isinstance(v, str) and v.replace(".", "").isdigit())
                ]
                if valores:
                    estatisticas = {
                        "Média": round(sum(valores) / len(valores), 2),
                        "Máximo": max(valores),
                        "Mínimo": min(valores),
                        "Total de Competências": len(resultados),
                    }

            # Template para o relatório de resumo
            html_content = f"""<!DOCTYPE html>
            <html>
            <head>
                <title>Resumo - {nome}</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }}
                    .container {{ max-width: 800px; margin: 0 auto; }}
                    .header {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .stats {{ display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 30px; }}
                    .stat-card {{ background-color: #fff; border: 1px solid #ddd; border-radius: 5px; padding: 15px; flex: 1; min-width: 120px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .stat-value {{ font-size: 24px; font-weight: bold; margin: 10px 0; color: #3498db; }}
                    .stat-label {{ font-size: 14px; color: #7f8c8d; }}
                    h1, h2, h3 {{ color: #2c3e50; }}
                    .footer {{ margin-top: 50px; text-align: center; font-size: 12px; color: #777; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Resumo da Avaliação</h1>
                        <p><strong>Nome:</strong> {nome}</p>
                        <p><strong>Período:</strong> {periodo}</p>
                        <p><strong>Data de Geração:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
                    </div>
                    
                    <h2>Estatísticas Gerais</h2>
                    <div class="stats">
            """

            # Adiciona estatísticas
            if estatisticas:
                for label, value in estatisticas.items():
                    html_content += f"""
                    <div class="stat-card">
                        <div class="stat-label">{label}</div>
                        <div class="stat-value">{value}</div>
                    </div>
                    """
            else:
                html_content += (
                    "<p>Não há dados suficientes para calcular estatísticas.</p>"
                )

            # Finaliza o HTML
            html_content += """
                    </div>
                    <div class="footer">
                        <p>Este resumo foi gerado automaticamente.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Salva o relatório de resumo
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            if self.verbose:
                self.logger.info(f"Relatório de resumo gerado: {summary_file}")

        except Exception as e:
            self.logger.error(
                f"Erro ao gerar relatório de resumo para {input_file}: {str(e)}"
            )
            if not self.ignore_errors:
                raise

    def _generate_benchmark_report(
        self, data: Dict[str, Any], input_file: Path, output_dir: Path
    ) -> None:
        """
        Gera relatório de benchmark a partir dos dados.

        Args:
            data: Dados processados
            input_file: Arquivo de entrada
            output_dir: Diretório de saída
        """
        benchmark_file = output_dir / "benchmark.html"

        try:
            # Extrai informações principais
            nome = data.get("nome", "Sem nome")
            team_data = data.get("team", data.get("equipe", {}))

            if not team_data:
                return

            # Template para o relatório de benchmark
            html_content = f"""<!DOCTYPE html>
            <html>
            <head>
                <title>Benchmark - {nome}</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }}
                    .container {{ max-width: 1000px; margin: 0 auto; }}
                    .header {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .section {{ margin-bottom: 30px; }}
                    h1, h2, h3 {{ color: #2c3e50; }}
                    table {{ width: 100%; border-collapse: collapse; }}
                    th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                    th {{ background-color: #f2f2f2; }}
                    .highlight {{ background-color: #e8f4f8; font-weight: bold; }}
                    .footer {{ margin-top: 50px; text-align: center; font-size: 12px; color: #777; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Relatório de Benchmark</h1>
                        <p><strong>Nome:</strong> {nome}</p>
                        <p><strong>Data de Geração:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
                    </div>
                    
                    <div class="section">
                        <h2>Comparação com a Equipe</h2>
            """

            # Adiciona tabela de comparação
            html_content += "<table><tr><th>Competência</th><th>Seu Resultado</th><th>Média da Equipe</th><th>Diferença</th></tr>"

            resultados = data.get("resultados", data.get("resultados_avaliacao", {}))
            team_averages = team_data.get("average", team_data.get("media", {}))

            for competencia, valor in resultados.items():
                if competencia in team_averages:
                    try:
                        individual = float(valor)
                        team_avg = float(team_averages[competencia])
                        difference = individual - team_avg
                        highlight = "highlight" if abs(difference) > 1 else ""

                        html_content += f"<tr class='{highlight}'><td>{competencia}</td><td>{individual}</td><td>{team_avg}</td><td>{difference:+.2f}</td></tr>"
                    except (ValueError, TypeError):
                        html_content += f"<tr><td>{competencia}</td><td>{valor}</td><td>{team_averages[competencia]}</td><td>N/A</td></tr>"

            html_content += "</table>"

            # Finaliza o HTML
            html_content += """
                    </div>
                    <div class="footer">
                        <p>Este relatório foi gerado automaticamente.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Salva o relatório de benchmark
            with open(benchmark_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            if self.verbose:
                self.logger.info(f"Relatório de benchmark gerado: {benchmark_file}")

        except Exception as e:
            self.logger.error(
                f"Erro ao gerar relatório de benchmark para {input_file}: {str(e)}"
            )
            if not self.ignore_errors:
                raise

    def _generate_visualizations(
        self, data: Dict[str, Any], input_file: Path, output_dir: Path
    ) -> None:
        """
        Gera visualizações a partir dos dados processados.

        Args:
            data: Dados processados
            input_file: Arquivo de entrada
            output_dir: Diretório de saída
        """
        try:
            # Gera radar chart
            self._generate_radar_chart(data, input_file, output_dir)

            # Gera heat map
            self._generate_heat_map(data, input_file, output_dir)

            if self.verbose:
                self.logger.info(f"Visualizações geradas com sucesso para {input_file}")
        except Exception as e:
            self.logger.error(
                f"Erro ao gerar visualizações para {input_file}: {str(e)}"
            )
            if not self.ignore_errors:
                raise

    def _generate_radar_chart(
        self, data: Dict[str, Any], input_file: Path, output_dir: Path
    ) -> None:
        """
        Gera um gráfico de radar a partir dos dados.

        Args:
            data: Dados processados
            input_file: Arquivo de entrada
            output_dir: Diretório de saída
        """
        radar_file = output_dir / "radar_chart.html"

        try:
            # Verifica se há bibliotecas necessárias
            try:
                import plotly.graph_objects as go
            except ImportError:
                self.logger.warning(
                    "Biblioteca plotly não disponível. Não será possível gerar o radar chart."
                )
                return

            # Extrai informações principais
            nome = data.get("nome", "Sem nome")
            resultados = data.get("resultados", data.get("resultados_avaliacao", {}))

            if not resultados:
                self.logger.warning(
                    f"Sem dados para gerar radar chart para {input_file}"
                )
                return

            # Filtra apenas valores numéricos
            competencias = []
            valores = []

            for comp, val in resultados.items():
                try:
                    valor_num = float(val)
                    competencias.append(comp)
                    valores.append(valor_num)
                except (ValueError, TypeError):
                    pass

            if not competencias:
                self.logger.warning(
                    f"Sem dados numéricos para gerar radar chart para {input_file}"
                )
                return

            # Cria o gráfico de radar
            fig = go.Figure()

            # Adiciona radar chart individual
            fig.add_trace(
                go.Scatterpolar(r=valores, theta=competencias, fill="toself", name=nome)
            )

            # Adiciona média da equipe se disponível
            team_data = data.get("team", data.get("equipe", {}))
            team_averages = (
                team_data.get("average", team_data.get("media", {}))
                if team_data
                else {}
            )

            if team_averages:
                team_valores = []
                for comp in competencias:
                    try:
                        team_valores.append(float(team_averages.get(comp, 0)))
                    except (ValueError, TypeError):
                        team_valores.append(0)

                fig.add_trace(
                    go.Scatterpolar(
                        r=team_valores,
                        theta=competencias,
                        fill="toself",
                        name="Média da Equipe",
                    )
                )

            # Ajusta o layout
            fig.update_layout(
                title=f"Radar Chart - {nome}",
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(valores) * 1.2],  # Ajusta o range com margem
                    )
                ),
                showlegend=True,
            )

            # Salva o gráfico
            fig.write_html(radar_file)

            if self.verbose:
                self.logger.info(f"Radar chart gerado: {radar_file}")

        except Exception as e:
            self.logger.error(f"Erro ao gerar radar chart para {input_file}: {str(e)}")
            if not self.ignore_errors:
                raise

    def _generate_heat_map(
        self, data: Dict[str, Any], input_file: Path, output_dir: Path
    ) -> None:
        """
        Gera um mapa de calor a partir dos dados.

        Args:
            data: Dados processados
            input_file: Arquivo de entrada
            output_dir: Diretório de saída
        """
        heatmap_file = output_dir / "heatmap.html"

        try:
            # Verifica se há bibliotecas necessárias
            try:
                import numpy as np
                import plotly.graph_objects as go
            except ImportError:
                self.logger.warning(
                    "Bibliotecas plotly ou numpy não disponíveis. Não será possível gerar o mapa de calor."
                )
                return

            # Extrai informações principais
            nome = data.get("nome", "Sem nome")
            resultados = data.get("resultados", data.get("resultados_avaliacao", {}))

            if not resultados:
                self.logger.warning(
                    f"Sem dados para gerar mapa de calor para {input_file}"
                )
                return

            # Filtra apenas valores numéricos
            competencias = []
            valores = []

            for comp, val in resultados.items():
                try:
                    valor_num = float(val)
                    competencias.append(comp)
                    valores.append(valor_num)
                except (ValueError, TypeError):
                    pass

            if not competencias:
                self.logger.warning(
                    f"Sem dados numéricos para gerar mapa de calor para {input_file}"
                )
                return

            # Prepara os dados para o mapa de calor
            z = np.array([valores])

            # Função para determinar cores
            def get_colorscale():
                max_val = max(valores) if valores else 5
                thresholds = [0, max_val * 0.25, max_val * 0.5, max_val * 0.75, max_val]
                return [
                    [0, "red"],
                    [thresholds[1] / max_val, "orange"],
                    [thresholds[2] / max_val, "yellow"],
                    [thresholds[3] / max_val, "yellowgreen"],
                    [1, "green"],
                ]

            # Cria o mapa de calor
            fig = go.Figure(
                data=go.Heatmap(
                    z=z,
                    x=competencias,
                    y=[nome],
                    colorscale=get_colorscale(),
                    showscale=True,
                    text=[[f"{v:.2f}" for v in valores]],
                    texttemplate="%{text}",
                    textfont={"size": 12},
                )
            )

            # Ajusta o layout
            fig.update_layout(
                title=f"Mapa de Calor - {nome}",
                xaxis=dict(title="Competências"),
                yaxis=dict(title=""),
                height=300,
                margin=dict(l=100, r=20, t=70, b=100),
            )

            # Salva o gráfico
            fig.write_html(heatmap_file)

            if self.verbose:
                self.logger.info(f"Mapa de calor gerado: {heatmap_file}")

        except Exception as e:
            self.logger.error(
                f"Erro ao gerar mapa de calor para {input_file}: {str(e)}"
            )
            if not self.ignore_errors:
                raise

    def _generate_action_plan(
        self, data: Dict[str, Any], input_file: Path, output_dir: Path
    ) -> None:
        """
        Gera um plano de ação baseado nos resultados.

        Args:
            data: Dados processados
            input_file: Arquivo de entrada
            output_dir: Diretório de saída
        """
        action_plan_file = output_dir / "action_plan.html"

        try:
            # Extrai informações principais
            nome = data.get("nome", "Sem nome")
            resultados = data.get("resultados", data.get("resultados_avaliacao", {}))

            if not resultados:
                return

            # Identifica áreas de melhoria (resultados abaixo da média)
            valores = []
            for val in resultados.values():
                try:
                    valores.append(float(val))
                except (ValueError, TypeError):
                    pass

            if not valores:
                return

            media = sum(valores) / len(valores) if valores else 0
            areas_melhoria = {}

            for comp, val in resultados.items():
                try:
                    valor_num = float(val)
                    if valor_num < media:
                        areas_melhoria[comp] = valor_num
                except (ValueError, TypeError):
                    pass

            # Ordena as áreas de melhoria (pior para melhor)
            areas_ordenadas = sorted(areas_melhoria.items(), key=lambda x: x[1])

            # Template para o plano de ação
            html_content = f"""<!DOCTYPE html>
            <html>
            <head>
                <title>Plano de Ação - {nome}</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }}
                    .container {{ max-width: 800px; margin: 0 auto; }}
                    .header {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .section {{ margin-bottom: 30px; }}
                    .action-item {{ background-color: #fff; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .priority-high {{ border-left: 5px solid #e74c3c; }}
                    .priority-medium {{ border-left: 5px solid #f39c12; }}
                    .priority-low {{ border-left: 5px solid #2ecc71; }}
                    h1, h2, h3 {{ color: #2c3e50; }}
                    .footer {{ margin-top: 50px; text-align: center; font-size: 12px; color: #777; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Plano de Ação</h1>
                        <p><strong>Nome:</strong> {nome}</p>
                        <p><strong>Data de Geração:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
                    </div>
                    
                    <div class="section">
                        <h2>Áreas para Desenvolvimento</h2>
                        <p>Baseado nos resultados da avaliação, as seguintes áreas foram identificadas para desenvolvimento:</p>
            """

            # Adiciona itens de ação
            if areas_ordenadas:
                for i, (competencia, valor) in enumerate(areas_ordenadas):
                    # Determina a prioridade com base na ordem
                    if i < len(areas_ordenadas) // 3:
                        priority = "high"
                    elif i < (len(areas_ordenadas) * 2) // 3:
                        priority = "medium"
                    else:
                        priority = "low"

                    html_content += f"""
                    <div class="action-item priority-{priority}">
                        <h3>{competencia} (Resultado: {valor})</h3>
                        <p><strong>Prioridade:</strong> {"Alta" if priority == "high" else "Média" if priority == "medium" else "Baixa"}</p>
                        <p><strong>Sugestões de desenvolvimento:</strong></p>
                        <ul>
                            <li>Participar de treinamentos específicos em {competencia}</li>
                            <li>Buscar feedback com colegas e gestores sobre {competencia}</li>
                            <li>Definir metas de desenvolvimento relacionadas a {competencia}</li>
                        </ul>
                    </div>
                    """
            else:
                html_content += (
                    "<p>Nenhuma área específica identificada para desenvolvimento.</p>"
                )

            # Finaliza o HTML
            html_content += """
                    </div>
                    <div class="footer">
                        <p>Este plano de ação foi gerado automaticamente e deve ser discutido com seu gestor.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Salva o plano de ação
            with open(action_plan_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            if self.verbose:
                self.logger.info(f"Plano de ação gerado: {action_plan_file}")

        except Exception as e:
            self.logger.error(
                f"Erro ao gerar plano de ação para {input_file}: {str(e)}"
            )
            if not self.ignore_errors:
                raise

    def _bulk_export(self) -> List[str]:
        """Realiza exportação em massa de todos os dados processados."""
        results = []
        try:
            if self.verbose:
                self.logger.info("Iniciando exportação em massa")

            # Criar diretório para exportação em massa
            bulk_dir = self.output_path / "bulk_export"
            bulk_dir.mkdir(exist_ok=True, parents=True)

            # Exportar todas as visualizações em um único arquivo PDF
            if not self.skip_viz and self.export_pdf:
                try:
                    pdf_path = (
                        bulk_dir
                        / f"all_visualizations_{datetime.now().strftime('%Y%m%d')}.pdf"
                    )

                    # Simular exportação PDF
                    with open(pdf_path, "w", encoding="utf-8") as f:
                        f.write("Simulação de PDF com todas as visualizações")

                    results.append(
                        f"Todas as visualizações exportadas para PDF: {pdf_path}"
                    )
                except Exception as e:
                    error_msg = f"Erro ao exportar visualizações para PDF: {str(e)}"
                    self.logger.error(error_msg)
                    results.append(error_msg)

            # Exportar todos os dados processados em um único arquivo Excel
            if self.export_excel:
                try:
                    excel_path = (
                        bulk_dir / f"all_data_{datetime.now().strftime('%Y%m%d')}.xlsx"
                    )

                    # Simular exportação Excel
                    with open(excel_path, "w", encoding="utf-8") as f:
                        f.write("Simulação de Excel com todos os dados")

                    results.append(
                        f"Todos os dados exportados para Excel: {excel_path}"
                    )
                except Exception as e:
                    error_msg = f"Erro ao exportar dados para Excel: {str(e)}"
                    self.logger.error(error_msg)
                    results.append(error_msg)

            if not results:
                results.append(
                    "Nenhuma exportação em massa realizada - defina export_excel ou export_pdf"
                )

            return results
        except Exception as e:
            error_msg = f"Erro na exportação em massa: {str(e)}"
            self.logger.error(error_msg)
            if not self.ignore_errors:
                raise
            return [error_msg]

    def _log_configuration(self):
        """Log the configuration settings."""
        logging.info(f"Data path: {self.data_path}")
        logging.info(f"Output path: {self.output_path}")
        logging.info(f"Force reprocessing: {self.force}")
        logging.info(f"Formats: {self.selected_formats}")
        if self.pessoa_filter:
            logging.info(f"Filtering for pessoa: {self.pessoa_filter}")
        if self.ano_filter:
            logging.info(f"Filtering for ano: {self.ano_filter}")
        logging.info(f"Ignore errors: {self.ignore_errors}")
        logging.info(f"Skip visualizations: {self.skip_viz}")
        logging.info(f"Skip benchmark reports: {self.skip_benchmark}")
        logging.info(f"Export to Excel: {self.export_excel}")
        logging.info(f"Export to PDF: {self.export_pdf}")
        logging.info(f"Generate synthetic data: {self.synthetic}")
        logging.info(f"Verbose mode: {self.verbose}")
        logging.info("Expected data structure: <pessoa>/<ano>/resultado.json")

    def process(self):
        """Process the data files and generate reports.

        Returns:
            int: Number of files processed
        """
        processed_count = 0

        # Generate synthetic data if requested
        if self.synthetic:
            logging.info("Generating synthetic data for testing...")
            synthetic_results = self._generate_synthetic_data()
            if synthetic_results:
                logging.info(f"Generated {len(synthetic_results)} synthetic data files")
                if self.verbose:
                    for result in synthetic_results:
                        logging.info(f"  - {result}")
                processed_count += len(synthetic_results)

        # First try to process with pessoa/ano structure
        pessoa_ano_results = self._process_pessoa_ano_structure_files()
        if pessoa_ano_results:
            processed_count += len(pessoa_ano_results)
            logging.info(
                f"Processed {len(pessoa_ano_results)} files using pessoa/ano structure"
            )

        # Generate benchmark reports if not skipped
        if processed_count > 0 and not self.skip_benchmark:
            logging.info("Generating benchmark reports...")
            benchmark_results = self._generate_benchmark_reports()
            if benchmark_results:
                logging.info(f"Generated {len(benchmark_results)} benchmark reports")

        # Consolidate data after processing
        if processed_count > 0:
            logging.info("Consolidating data...")
            self._consolidate_data()

        # Return the total count of processed files
        return processed_count

    def _generate_year_over_year_comparisons(self, pessoa: str) -> None:
        """
        Gera comparativos ano a ano para uma pessoa específica.

        Args:
            pessoa: Nome da pessoa para gerar comparativos
        """
        if self.verbose:
            self.logger.info(f"Gerando comparativos ano a ano para {pessoa}")

        # Criar diretório para relatórios comparativos
        output_dir = self.output_path / "comparativos" / pessoa
        output_dir.mkdir(parents=True, exist_ok=True)

        # Buscar todos os anos disponíveis para a pessoa
        anos_disponiveis = []
        dados_por_ano = {}

        # Caminho para os dados processados
        processed_dir = self.output_path / "processed" / pessoa

        if not processed_dir.exists():
            self.logger.warning(
                f"Diretório de dados processados não encontrado para {pessoa}"
            )
            return

        # Coletar dados de todos os anos
        for ano_dir in processed_dir.glob("*"):
            if not ano_dir.is_dir() or not ano_dir.name.isdigit():
                continue

            ano = ano_dir.name
            anos_disponiveis.append(ano)

            # Carregar dados combinados
            combined_file = ano_dir / "data_combined.json"
            if combined_file.exists():
                try:
                    with open(combined_file, "r", encoding="utf-8") as f:
                        dados_por_ano[ano] = json.load(f)
                except Exception as e:
                    self.logger.error(
                        f"Erro ao carregar dados do ano {ano} para {pessoa}: {str(e)}"
                    )
                    continue

            # Carregar estatísticas de direcionadores
            stats_file = ano_dir / "direcionadores_stats.json"
            if stats_file.exists():
                try:
                    with open(stats_file, "r", encoding="utf-8") as f:
                        if "stats" not in dados_por_ano[ano]:
                            dados_por_ano[ano]["stats"] = {}
                        dados_por_ano[ano]["stats"]["direcionadores"] = json.load(f)
                except Exception as e:
                    self.logger.error(
                        f"Erro ao carregar estatísticas do ano {ano} para {pessoa}: {str(e)}"
                    )

        # Ordenar anos
        anos_disponiveis.sort()

        if len(anos_disponiveis) <= 1:
            self.logger.warning(
                f"Não há dados suficientes para gerar comparativos ano a ano para {pessoa}"
            )
            return

        # Gerar relatório comparativo
        self._generate_comparative_report(
            pessoa, anos_disponiveis, dados_por_ano, output_dir
        )

        # Gerar visualizações comparativas
        if not self.skip_viz:
            self._generate_comparative_visualizations(
                pessoa, anos_disponiveis, dados_por_ano, output_dir
            )

    def _generate_comparative_report(
        self, pessoa: str, anos: List[str], dados: Dict[str, Dict], output_dir: Path
    ) -> None:
        """
        Gera um relatório comparativo entre anos.

        Args:
            pessoa: Nome da pessoa
            anos: Lista de anos disponíveis
            dados: Dicionário com dados por ano
            output_dir: Diretório de saída
        """
        # Extrair nome completo do perfil, se disponível
        nome_completo = pessoa
        for ano, ano_data in dados.items():
            if "perfil" in ano_data and "nome_completo" in ano_data["perfil"]:
                nome_completo = ano_data["perfil"]["nome_completo"]
                break

        # Gerar HTML
        html_file = output_dir / "comparativo_anual.html"

        html_content = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Comparativo Anual - {nome_completo}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #333; }}
                .section {{ margin-bottom: 30px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .header {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #777; text-align: center; }}
                .highlight {{ background-color: #e8f4ff; }}
                .positive {{ color: green; }}
                .negative {{ color: red; }}
                .no-change {{ color: gray; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Relatório Comparativo Anual</h1>
                <p><strong>Nome:</strong> {nome_completo}</p>
                <p><strong>Anos analisados:</strong> {", ".join(anos)}</p>
            </div>
            
            <div class="section">
                <h2>Evolução de Carreira</h2>
                <table>
                    <tr>
                        <th>Ano</th>
                        <th>Cargo</th>
                        <th>Nível</th>
                        <th>Departamento</th>
                        <th>Gestor</th>
                    </tr>
        """

        # Adicionar dados de carreira por ano
        for ano in anos:
            if ano not in dados or "perfil" not in dados[ano]:
                continue

            perfil = dados[ano]["perfil"]

            html_content += f"""
                    <tr>
                        <td><strong>{ano}</strong></td>
                        <td>{perfil.get("cargo", "N/A")}</td>
                        <td>{perfil.get("nivel_cargo", "N/A")}</td>
                        <td>{perfil.get("nome_departamento", "N/A")}</td>
                        <td>{perfil.get("nome_gestor", "N/A")}</td>
                    </tr>
            """

        html_content += """
                </table>
            </div>
            
            <div class="section">
                <h2>Evolução por Direcionador</h2>
                <table>
                    <tr>
                        <th>Direcionador</th>
        """

        # Adicionar cabeçalhos para cada ano
        for ano in anos:
            html_content += f"""
                        <th>{ano}</th>
            """

        # Adicionar colunas para variação percentual
        if len(anos) >= 2:
            html_content += """
                        <th>Variação Absoluta</th>
                        <th>Variação %</th>
            """

        html_content += """
                    </tr>
        """

        # Coletar todos os direcionadores de todos os anos
        todos_direcionadores = set()
        for ano in anos:
            if (
                ano in dados
                and "stats" in dados[ano]
                and "direcionadores" in dados[ano]["stats"]
            ):
                for dir_nome in dados[ano]["stats"]["direcionadores"].keys():
                    todos_direcionadores.add(dir_nome)

        # Adicionar linhas para cada direcionador
        for direcionador in sorted(todos_direcionadores):
            html_content += f"""
                    <tr>
                        <td>{direcionador}</td>
            """

            # Valores para cada ano
            valores_por_ano = {}
            for ano in anos:
                valor = "N/A"
                if (
                    ano in dados
                    and "stats" in dados[ano]
                    and "direcionadores" in dados[ano]["stats"]
                    and direcionador in dados[ano]["stats"]["direcionadores"]
                    and "media_colaborador"
                    in dados[ano]["stats"]["direcionadores"][direcionador]
                ):
                    valor = dados[ano]["stats"]["direcionadores"][direcionador][
                        "media_colaborador"
                    ]
                    valores_por_ano[ano] = valor

                if isinstance(valor, (int, float)):
                    html_content += f"""
                        <td>{valor:.2f}</td>
                    """
                else:
                    html_content += f"""
                        <td>{valor}</td>
                    """

            # Calcular variação se houver pelo menos dois anos com dados
            if len(valores_por_ano) >= 2 and len(anos) >= 2:
                primeiro_ano = anos[0]
                ultimo_ano = anos[-1]

                if primeiro_ano in valores_por_ano and ultimo_ano in valores_por_ano:
                    primeiro_valor = valores_por_ano[primeiro_ano]
                    ultimo_valor = valores_por_ano[ultimo_ano]

                    variacao_abs = ultimo_valor - primeiro_valor

                    if primeiro_valor != 0:
                        variacao_pct = (variacao_abs / primeiro_valor) * 100.0
                        class_variacao = "positive" if variacao_pct >= 0 else "negative"

                        html_content += f"""
                        <td class="{class_variacao}">{variacao_abs:.2f}</td>
                        <td class="{class_variacao}">{variacao_pct:.1f}%</td>
                        """
                    else:
                        html_content += """
                        <td>N/A</td>
                        <td>N/A</td>
                        """
                else:
                    html_content += """
                        <td>N/A</td>
                        <td>N/A</td>
                    """

            html_content += """
                    </tr>
            """

        html_content += (
            """
                </table>
            </div>
            
            <div class="section">
                <h2>Conclusões</h2>
                <p>Este relatório apresenta a evolução do colaborador ao longo dos anos analisados. 
                Observe as tendências de crescimento ou oportunidades de desenvolvimento comparando os valores de cada ano.</p>
            </div>
            
            <div class="footer">
                <p>Relatório gerado automaticamente em """
            + datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            + """</p>
            </div>
        </body>
        </html>
        """
        )

        # Salvar o HTML
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Gerar versão Markdown (resumida)
        md_file = output_dir / "comparativo_anual.md"

        md_content = f"""# Relatório Comparativo Anual - {nome_completo}

## Anos analisados
{", ".join(anos)}

## Evolução de Carreira

| Ano | Cargo | Nível | Departamento | Gestor |
|-----|-------|-------|--------------|--------|
"""

        # Adicionar dados de carreira por ano
        for ano in anos:
            if ano not in dados or "perfil" not in dados[ano]:
                continue

            perfil = dados[ano]["perfil"]
            md_content += f"| {ano} | {perfil.get('cargo', 'N/A')} | {perfil.get('nivel_cargo', 'N/A')} | {perfil.get('nome_departamento', 'N/A')} | {perfil.get('nome_gestor', 'N/A')} |\n"

        # Adicionar evolução por direcionador
        md_content += """
## Evolução por Direcionador

| Direcionador """

        # Adicionar cabeçalhos para cada ano
        for ano in anos:
            md_content += f"| {ano} "

        # Adicionar colunas para variação
        if len(anos) >= 2:
            md_content += "| Variação "

        md_content += "|\n|-------------- "

        # Adicionar separadores de tabela
        for _ in range(len(anos)):
            md_content += "| ---- "

        if len(anos) >= 2:
            md_content += "| ---- "

        md_content += "|\n"

        # Adicionar linhas para cada direcionador
        for direcionador in sorted(todos_direcionadores):
            md_content += f"| {direcionador} "

            # Valores para cada ano
            valores_por_ano = {}
            for ano in anos:
                valor = "N/A"
                if (
                    ano in dados
                    and "stats" in dados[ano]
                    and "direcionadores" in dados[ano]["stats"]
                    and direcionador in dados[ano]["stats"]["direcionadores"]
                    and "media_colaborador"
                    in dados[ano]["stats"]["direcionadores"][direcionador]
                ):
                    valor = dados[ano]["stats"]["direcionadores"][direcionador][
                        "media_colaborador"
                    ]
                    valores_por_ano[ano] = valor

                if isinstance(valor, (int, float)):
                    md_content += f"| {valor:.2f} "
                else:
                    md_content += f"| {valor} "

            # Calcular variação se houver pelo menos dois anos com dados
            if len(valores_por_ano) >= 2 and len(anos) >= 2:
                primeiro_ano = anos[0]
                ultimo_ano = anos[-1]

                if primeiro_ano in valores_por_ano and ultimo_ano in valores_por_ano:
                    primeiro_valor = valores_por_ano[primeiro_ano]
                    ultimo_valor = valores_por_ano[ultimo_ano]

                    variacao_abs = ultimo_valor - primeiro_valor

                    if primeiro_valor != 0:
                        variacao_pct = (variacao_abs / primeiro_valor) * 100.0
                        sinal = "+" if variacao_pct >= 0 else ""
                        md_content += f"| {sinal}{variacao_pct:.1f}% "
                    else:
                        md_content += "| N/A "
                else:
                    md_content += "| N/A "

            md_content += "|\n"

        md_content += f"""
---
Relatório gerado automaticamente em {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
"""

        # Salvar o Markdown
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

    def _generate_comparative_visualizations(
        self, pessoa: str, anos: List[str], dados: Dict[str, Dict], output_dir: Path
    ) -> None:
        """
        Gera visualizações comparativas entre anos.

        Args:
            pessoa: Nome da pessoa
            anos: Lista de anos disponíveis
            dados: Dicionário com dados por ano
            output_dir: Diretório de saída
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            from matplotlib.colors import LinearSegmentedColormap

            # Extrair nome completo se disponível
            nome_completo = pessoa
            for ano in anos:
                if (
                    ano in dados
                    and "perfil" in dados[ano]
                    and "nome_completo" in dados[ano]["perfil"]
                ):
                    nome_completo = dados[ano]["perfil"]["nome_completo"]
                    break

            # 1. Gráfico de evolução por direcionador
            plt.figure(figsize=(14, 8))

            # Coletar todos os direcionadores
            todos_direcionadores = set()
            for ano in anos:
                if (
                    ano in dados
                    and "stats" in dados[ano]
                    and "direcionadores" in dados[ano]["stats"]
                ):
                    for dir_nome in dados[ano]["stats"]["direcionadores"].keys():
                        todos_direcionadores.add(dir_nome)

            # Preparar dados para o gráfico
            labels = sorted(todos_direcionadores)
            data_by_year = {}

            for ano in anos:
                valores = []
                for dir_nome in labels:
                    valor = None
                    if (
                        ano in dados
                        and "stats" in dados[ano]
                        and "direcionadores" in dados[ano]["stats"]
                        and dir_nome in dados[ano]["stats"]["direcionadores"]
                        and "media_colaborador"
                        in dados[ano]["stats"]["direcionadores"][dir_nome]
                    ):
                        valor = dados[ano]["stats"]["direcionadores"][dir_nome][
                            "media_colaborador"
                        ]

                    valores.append(valor if valor is not None else 0)

                data_by_year[ano] = valores

            # Configurar posições no eixo X
            x = np.arange(len(labels))
            width = 0.8 / len(anos)  # Largura das barras ajustada pelo número de anos

            # Plotar barras para cada ano
            for i, ano in enumerate(anos):
                if ano in data_by_year:
                    offset = width * i - width * len(anos) / 2 + width / 2
                    plt.bar(x + offset, data_by_year[ano], width, label=ano)

            # Configurar o gráfico
            plt.title(f"Evolução por Direcionador - {nome_completo}", fontsize=14)
            plt.xlabel("Direcionador", fontsize=12)
            plt.ylabel("Valor Médio", fontsize=12)
            plt.xticks(x, labels, rotation=45, ha="right")
            plt.legend()
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            plt.tight_layout()

            # Salvar o gráfico
            evolution_file = output_dir / "evolucao_direcionadores.png"
            plt.savefig(evolution_file)
            plt.close()

            # 2. Gráfico de radar para evolução anual
            if len(anos) > 1:  # Só faz sentido se tiver mais de um ano
                # Selecionar o primeiro e último ano para comparação
                primeiro_ano = anos[0]
                ultimo_ano = anos[-1]

                if primeiro_ano in data_by_year and ultimo_ano in data_by_year:
                    fig, ax = plt.subplots(
                        figsize=(10, 10), subplot_kw=dict(polar=True)
                    )

                    # Organizar dados para o radar
                    valores_primeiro = data_by_year[primeiro_ano]
                    valores_ultimo = data_by_year[ultimo_ano]

                    # Calcular ângulos para cada direcionador
                    num_vars = len(labels)
                    angles = np.linspace(
                        0, 2 * np.pi, num_vars, endpoint=False
                    ).tolist()

                    # Fechar o círculo repetindo o primeiro valor
                    valores_primeiro = valores_primeiro + [valores_primeiro[0]]
                    valores_ultimo = valores_ultimo + [valores_ultimo[0]]
                    angles += [angles[0]]
                    labels_wrap = labels + [labels[0]]

                    # Plotar os dados
                    ax.plot(
                        angles,
                        valores_primeiro,
                        "b-",
                        linewidth=2,
                        label=f"Ano {primeiro_ano}",
                    )
                    ax.fill(angles, valores_primeiro, "b", alpha=0.1)

                    ax.plot(
                        angles,
                        valores_ultimo,
                        "r-",
                        linewidth=2,
                        label=f"Ano {ultimo_ano}",
                    )
                    ax.fill(angles, valores_ultimo, "r", alpha=0.1)

                    # Configurar o gráfico
                    ax.set_xticks(angles[:-1])
                    ax.set_xticklabels(labels, fontsize=10)

                    ax.set_title(
                        f"Comparativo {primeiro_ano} vs {ultimo_ano} - {nome_completo}",
                        fontsize=14,
                    )
                    ax.legend(loc="upper right")

                    # Salvar o gráfico
                    radar_file = (
                        output_dir
                        / f"radar_comparativo_{primeiro_ano}_vs_{ultimo_ano}.png"
                    )
                    plt.savefig(radar_file)
                    plt.close()

            # 3. Gráfico de calor (heatmap) para todos os anos e direcionadores
            if len(anos) >= 2 and len(labels) >= 2:
                plt.figure(figsize=(12, 8))

                # Criar matriz de dados para heatmap
                matrix = np.zeros((len(labels), len(anos)))

                for j, ano in enumerate(anos):
                    if ano in data_by_year:
                        for i, valor in enumerate(data_by_year[ano]):
                            matrix[i, j] = valor

                # Criar colormap personalizado
                cmap = LinearSegmentedColormap.from_list(
                    "custom_cmap", ["#f7fbff", "#08306b"]
                )

                # Plotar heatmap
                plt.imshow(matrix, cmap=cmap, aspect="auto")

                # Configurar eixos
                plt.xticks(np.arange(len(anos)), anos)
                plt.yticks(np.arange(len(labels)), labels)

                # Adicionar valores na matriz
                for i in range(len(labels)):
                    for j in range(len(anos)):
                        color = "white" if matrix[i, j] > 2.5 else "black"
                        plt.text(
                            j,
                            i,
                            f"{matrix[i, j]:.1f}",
                            ha="center",
                            va="center",
                            color=color,
                        )

                plt.colorbar(label="Valor")
                plt.title(f"Mapa de Calor por Ano - {nome_completo}", fontsize=14)
                plt.xlabel("Ano")
                plt.ylabel("Direcionador")
                plt.tight_layout()

                # Salvar o gráfico
                heatmap_file = output_dir / "heatmap_anual.png"
                plt.savefig(heatmap_file)
                plt.close()

        except ImportError:
            self.logger.warning(
                "Matplotlib não disponível. Impossível gerar visualizações comparativas."
            )
        except Exception as e:
            error_msg = (
                f"Erro ao gerar visualizações comparativas para {pessoa}: {str(e)}"
            )
            self.logger.error(error_msg)
            if not self.ignore_errors:
                raise

    def _generate_benchmark_reports(self):
        """
        Gera relatórios comparativos avançados entre pessoas e anos.
        Análise de benchmarks, tendências e métricas comparativas.
        """
        if self.skip_benchmark:
            self.logger.info(
                "Pulando geração de relatórios de benchmark (--skip-benchmark)"
            )
            return ["Geração de relatórios comparativos ignorada"]

        results = []
        benchmark_dir = self.output_path / "reports" / "benchmarks"
        benchmark_dir.mkdir(exist_ok=True, parents=True)

        try:
            # Coletar dados de todas as pessoas e anos
            all_data = self._collect_all_evaluation_data()
            if not all_data:
                return ["Nenhum dado encontrado para gerar relatórios comparativos"]

            # Gerar relatório de progresso ano a ano
            yearly_progress_file = benchmark_dir / "yearly_progress.json"
            yearly_progress = self._generate_yearly_progress_report(all_data)
            with open(yearly_progress_file, "w", encoding="utf-8") as f:
                json.dump(yearly_progress, f, indent=2, ensure_ascii=False)
            results.append(
                f"Relatório de progresso anual gerado: {yearly_progress_file}"
            )

            # Gerar relatório de benchmarks por competência
            competency_benchmark_file = benchmark_dir / "competency_benchmarks.json"
            competency_benchmarks = self._generate_competency_benchmarks(all_data)
            with open(competency_benchmark_file, "w", encoding="utf-8") as f:
                json.dump(competency_benchmarks, f, indent=2, ensure_ascii=False)
            results.append(
                f"Relatório de benchmarks por competência gerado: {competency_benchmark_file}"
            )

            # Gerar relatório de tendências gerais
            trends_file = benchmark_dir / "trends_analysis.json"
            trends_analysis = self._generate_trends_analysis(all_data)
            with open(trends_file, "w", encoding="utf-8") as f:
                json.dump(trends_analysis, f, indent=2, ensure_ascii=False)
            results.append(f"Análise de tendências gerada: {trends_file}")

            # Gerar relatório de análise de pares
            peer_analysis_file = benchmark_dir / "peer_analysis.json"
            peer_analysis = self._generate_peer_analysis(all_data)
            with open(peer_analysis_file, "w", encoding="utf-8") as f:
                json.dump(peer_analysis, f, indent=2, ensure_ascii=False)
            results.append(f"Análise de pares gerada: {peer_analysis_file}")

            # Gerar relatório de evolução de equipes
            team_evolution_file = benchmark_dir / "team_evolution.json"
            team_evolution = self._generate_team_evolution_report(all_data)
            with open(team_evolution_file, "w", encoding="utf-8") as f:
                json.dump(team_evolution, f, indent=2, ensure_ascii=False)
            results.append(f"Evolução de equipes gerada: {team_evolution_file}")

            # Gerar relatório de distribuição de habilidades
            skills_distribution_file = benchmark_dir / "skills_distribution.json"
            skills_distribution = self._generate_skills_distribution(all_data)
            with open(skills_distribution_file, "w", encoding="utf-8") as f:
                json.dump(skills_distribution, f, indent=2, ensure_ascii=False)
            results.append(
                f"Distribuição de habilidades gerada: {skills_distribution_file}"
            )

            # Contabilizar estatísticas
            self.stats["generated_reports"] += 6

            self.logger.info(f"Gerados {len(results)} relatórios comparativos")
            return results

        except Exception as e:
            error_msg = f"Erro ao gerar relatórios comparativos: {str(e)}"
            self.logger.error(error_msg)
            if self.ignore_errors:
                return [error_msg]
            raise

    def _collect_all_evaluation_data(self):
        """
        Coleta todos os dados de avaliação para análise comparativa.

        Returns:
            Dict: Estrutura com todos os dados organizados por pessoa/ano
        """
        all_data = {}

        # Percorre a estrutura pessoa/ano
        for pessoa_dir in self.data_path.glob("*"):
            if not pessoa_dir.is_dir():
                continue

            pessoa = pessoa_dir.name
            all_data[pessoa] = {}

            for ano_dir in pessoa_dir.glob("*"):
                if not ano_dir.is_dir():
                    continue

                ano = ano_dir.name
                resultado_file = ano_dir / "resultado.json"
                perfil_file = ano_dir / "perfil.json"

                if resultado_file.exists():
                    try:
                        with open(resultado_file, "r", encoding="utf-8") as f:
                            resultado_data = json.load(f)
                        all_data[pessoa][ano] = {"resultado": resultado_data}
                    except Exception as e:
                        self.logger.error(f"Erro ao ler {resultado_file}: {str(e)}")
                        if not self.ignore_errors:
                            raise

                if perfil_file.exists():
                    try:
                        with open(perfil_file, "r", encoding="utf-8") as f:
                            perfil_data = json.load(f)
                        if ano in all_data[pessoa]:
                            all_data[pessoa][ano]["perfil"] = perfil_data
                        else:
                            all_data[pessoa][ano] = {"perfil": perfil_data}
                    except Exception as e:
                        self.logger.error(f"Erro ao ler {perfil_file}: {str(e)}")
                        if not self.ignore_errors:
                            raise

        return all_data

    def _generate_yearly_progress_report(self, all_data):
        """
        Gera relatório de progresso ano a ano para cada pessoa.

        Args:
            all_data: Dados coletados organizados por pessoa/ano

        Returns:
            Dict: Relatório de progresso anual
        """
        progress_report = {}

        for pessoa, anos_data in all_data.items():
            progress_report[pessoa] = {
                "yearly_comparison": {},
                "growth_areas": [],
                "consistent_strengths": [],
            }

            # Organizar anos em ordem cronológica
            sorted_anos = sorted(anos_data.keys())

            if len(sorted_anos) < 2:
                progress_report[pessoa]["summary"] = (
                    "Dados insuficientes para análise de progresso (menos de 2 anos)"
                )
                continue

            # Analisar progresso entre anos consecutivos
            for i in range(len(sorted_anos) - 1):
                ano_atual = sorted_anos[i]
                ano_seguinte = sorted_anos[i + 1]

                if (
                    "resultado" not in anos_data[ano_atual]
                    or "resultado" not in anos_data[ano_seguinte]
                ):
                    continue

                # Comparar resultados entre anos
                resultado_atual = anos_data[ano_atual]["resultado"]
                resultado_seguinte = anos_data[ano_seguinte]["resultado"]

                comparison = self._compare_resultados(
                    resultado_atual, resultado_seguinte
                )
                progress_report[pessoa]["yearly_comparison"][
                    f"{ano_atual}_to_{ano_seguinte}"
                ] = comparison

            # Identificar áreas de crescimento e pontos fortes consistentes
            progress_report[pessoa]["growth_areas"] = self._identify_growth_areas(
                progress_report[pessoa]["yearly_comparison"]
            )
            progress_report[pessoa]["consistent_strengths"] = (
                self._identify_consistent_strengths(anos_data)
            )

            # Gerar resumo geral
            progress_report[pessoa]["summary"] = self._generate_progress_summary(
                progress_report[pessoa]
            )

        return progress_report

    def _compare_resultados(self, resultado_anterior, resultado_atual):
        """
        Compara resultados entre dois anos consecutivos.

        Args:
            resultado_anterior: Dados do resultado do ano anterior
            resultado_atual: Dados do resultado do ano atual

        Returns:
            Dict: Análise comparativa entre os dois anos
        """
        comparison = {
            "improved_areas": [],
            "declined_areas": [],
            "stable_areas": [],
            "overall_change": 0,
            "percent_change": 0,
        }

        # Extrair competências/direcionadores para comparação
        # Esta lógica depende da estrutura exata dos dados, então é genérica
        all_areas = set()
        previous_scores = {}
        current_scores = {}

        # Tenta extrair competências de diferentes estruturas possíveis
        if "direcionadores" in resultado_anterior:
            for area, score in resultado_anterior["direcionadores"].items():
                all_areas.add(area)
                previous_scores[area] = score
        elif "competencias" in resultado_anterior:
            for area, score in resultado_anterior["competencias"].items():
                all_areas.add(area)
                previous_scores[area] = score
        elif isinstance(resultado_anterior, dict):
            for area, score in resultado_anterior.items():
                if isinstance(score, (int, float)):
                    all_areas.add(area)
                    previous_scores[area] = score

        if "direcionadores" in resultado_atual:
            for area, score in resultado_atual["direcionadores"].items():
                all_areas.add(area)
                current_scores[area] = score
        elif "competencias" in resultado_atual:
            for area, score in resultado_atual["competencias"].items():
                all_areas.add(area)
                current_scores[area] = score
        elif isinstance(resultado_atual, dict):
            for area, score in resultado_atual.items():
                if isinstance(score, (int, float)):
                    all_areas.add(area)
                    current_scores[area] = score

        # Calcular diferenças
        total_previous = 0
        total_current = 0
        compared_areas = 0

        for area in all_areas:
            prev_score = previous_scores.get(area)
            curr_score = current_scores.get(area)

            if prev_score is not None and curr_score is not None:
                compared_areas += 1
                total_previous += prev_score
                total_current += curr_score

                difference = curr_score - prev_score

                if difference > 0:
                    comparison["improved_areas"].append(
                        {"area": area, "change": difference}
                    )
                elif difference < 0:
                    comparison["declined_areas"].append(
                        {"area": area, "change": difference}
                    )
                else:
                    comparison["stable_areas"].append(area)

        # Calcular mudança geral
        if compared_areas > 0:
            comparison["overall_change"] = total_current - total_previous
            if total_previous > 0:
                comparison["percent_change"] = (
                    (total_current - total_previous) / total_previous * 100
                )

        return comparison

    def _identify_growth_areas(self, yearly_comparisons):
        """
        Identifica áreas de crescimento consistente ao longo dos anos.

        Args:
            yearly_comparisons: Comparações ano a ano

        Returns:
            List: Áreas com crescimento consistente
        """
        area_improvements = {}

        for year_comparison in yearly_comparisons.values():
            for improved in year_comparison["improved_areas"]:
                area = improved["area"]
                if area not in area_improvements:
                    area_improvements[area] = 0
                area_improvements[area] += 1

        # Áreas que melhoraram em pelo menos metade das comparações anuais
        min_improvements = max(1, len(yearly_comparisons) // 2)
        growth_areas = [
            area
            for area, count in area_improvements.items()
            if count >= min_improvements
        ]

        return growth_areas

    def _identify_consistent_strengths(self, anos_data):
        """
        Identifica pontos fortes consistentes ao longo dos anos.

        Args:
            anos_data: Dados organizados por ano

        Returns:
            List: Pontos fortes consistentes
        """
        # Mapeia áreas para contagem de anos em que foram pontos fortes
        strength_counts = {}
        total_years = 0

        for ano, data in anos_data.items():
            if "resultado" not in data:
                continue

            total_years += 1
            resultado = data["resultado"]

            # Encontra as áreas com maior pontuação (top 25%)
            scores = {}

            if "direcionadores" in resultado:
                scores.update(resultado["direcionadores"])
            elif "competencias" in resultado:
                scores.update(resultado["competencias"])
            elif isinstance(resultado, dict):
                for area, score in resultado.items():
                    if isinstance(score, (int, float)):
                        scores[area] = score

            if not scores:
                continue

            # Identifica o quartil superior
            sorted_scores = sorted(scores.values())
            if len(sorted_scores) >= 4:
                threshold = sorted_scores[int(len(sorted_scores) * 0.75)]
            else:
                threshold = sorted_scores[-1]  # Pelo menos o maior valor

            # Registra áreas fortes deste ano
            for area, score in scores.items():
                if score >= threshold:
                    if area not in strength_counts:
                        strength_counts[area] = 0
                    strength_counts[area] += 1

        # Áreas que foram pontos fortes em pelo menos 75% dos anos
        min_years = max(1, int(total_years * 0.75))
        consistent_strengths = [
            area for area, count in strength_counts.items() if count >= min_years
        ]

        return consistent_strengths

    def _generate_progress_summary(self, person_progress):
        """
        Gera um resumo textual do progresso da pessoa.

        Args:
            person_progress: Dados de progresso da pessoa

        Returns:
            str: Resumo do progresso
        """
        summary = []

        yearly_comparisons = person_progress["yearly_comparison"]
        growth_areas = person_progress["growth_areas"]
        strengths = person_progress["consistent_strengths"]

        # Verifica tendência geral
        overall_trend = 0
        for comparison in yearly_comparisons.values():
            overall_trend += comparison["overall_change"]

        if overall_trend > 0:
            summary.append("Tendência geral de melhoria ao longo dos anos.")
        elif overall_trend < 0:
            summary.append("Tendência geral de declínio ao longo dos anos.")
        else:
            summary.append("Desempenho estável ao longo dos anos.")

        # Resume áreas de crescimento
        if growth_areas:
            areas_text = ", ".join(growth_areas[:3])
            if len(growth_areas) > 3:
                areas_text += f" e outras {len(growth_areas) - 3} áreas"
            summary.append(f"Crescimento consistente em: {areas_text}.")

        # Resume pontos fortes
        if strengths:
            strengths_text = ", ".join(strengths[:3])
            if len(strengths) > 3:
                strengths_text += f" e outras {len(strengths) - 3} áreas"
            summary.append(f"Pontos fortes consistentes em: {strengths_text}.")

        return " ".join(summary)

    def _generate_competency_benchmarks(self, all_data):
        """
        Gera benchmarks de competências comparando todas as pessoas.

        Args:
            all_data: Dados coletados de todas as pessoas

        Returns:
            Dict: Benchmarks de competências
        """
        benchmarks = {
            "competency_rankings": {},
            "avg_by_competency": {},
            "top_performers": {},
            "year_by_year": {},
        }

        # Coletar todos os anos disponíveis
        all_years = set()
        for pessoa_data in all_data.values():
            all_years.update(pessoa_data.keys())

        sorted_years = sorted(all_years)

        # Coletar todas as competências/direcionadores disponíveis
        all_competencies = set()
        for pessoa_data in all_data.values():
            for ano_data in pessoa_data.values():
                if "resultado" in ano_data:
                    resultado = ano_data["resultado"]
                    if "direcionadores" in resultado:
                        all_competencies.update(resultado["direcionadores"].keys())
                    elif "competencias" in resultado:
                        all_competencies.update(resultado["competencias"].keys())
                    elif isinstance(resultado, dict):
                        all_competencies.update(
                            k
                            for k, v in resultado.items()
                            if isinstance(v, (int, float))
                        )

        # Para cada competência, calcular estatísticas
        for competency in all_competencies:
            # Inicializar dados para esta competência
            benchmarks["competency_rankings"][competency] = {}
            benchmarks["avg_by_competency"][competency] = 0
            benchmarks["top_performers"][competency] = []

            # Coletar pontuações de todas as pessoas para esta competência
            all_scores = []
            scores_by_person = {}

            for pessoa, anos_data in all_data.items():
                person_scores = []

                for ano, data in anos_data.items():
                    if "resultado" not in data:
                        continue

                    score = None
                    resultado = data["resultado"]

                    if (
                        "direcionadores" in resultado
                        and competency in resultado["direcionadores"]
                    ):
                        score = resultado["direcionadores"][competency]
                    elif (
                        "competencias" in resultado
                        and competency in resultado["competencias"]
                    ):
                        score = resultado["competencias"][competency]
                    elif isinstance(resultado, dict) and competency in resultado:
                        if isinstance(resultado[competency], (int, float)):
                            score = resultado[competency]

                    if score is not None:
                        person_scores.append(score)
                        all_scores.append(score)

                if person_scores:
                    # Usar média dos anos como pontuação da pessoa
                    avg_score = sum(person_scores) / len(person_scores)
                    scores_by_person[pessoa] = avg_score

            # Calcular média geral
            if all_scores:
                benchmarks["avg_by_competency"][competency] = sum(all_scores) / len(
                    all_scores
                )

            # Classificar pessoas por pontuação
            ranked_persons = sorted(
                scores_by_person.items(), key=lambda x: x[1], reverse=True
            )
            benchmarks["competency_rankings"][competency] = {
                pessoa: {"score": score, "rank": i + 1}
                for i, (pessoa, score) in enumerate(ranked_persons)
            }

            # Identificar top performers (25% superior)
            top_count = max(1, len(ranked_persons) // 4)
            benchmarks["top_performers"][competency] = [
                pessoa for pessoa, _ in ranked_persons[:top_count]
            ]

        # Análise ano a ano
        for year in sorted_years:
            benchmarks["year_by_year"][year] = {
                "avg_by_competency": {},
                "top_performers": {},
            }

            # Para cada competência neste ano
            for competency in all_competencies:
                scores_this_year = []
                person_scores = {}

                for pessoa, anos_data in all_data.items():
                    if year in anos_data and "resultado" in anos_data[year]:
                        resultado = anos_data[year]["resultado"]
                        score = None

                        if (
                            "direcionadores" in resultado
                            and competency in resultado["direcionadores"]
                        ):
                            score = resultado["direcionadores"][competency]
                        elif (
                            "competencias" in resultado
                            and competency in resultado["competencias"]
                        ):
                            score = resultado["competencias"][competency]
                        elif isinstance(resultado, dict) and competency in resultado:
                            if isinstance(resultado[competency], (int, float)):
                                score = resultado[competency]

                        if score is not None:
                            scores_this_year.append(score)
                            person_scores[pessoa] = score

                # Calcular média para esta competência neste ano
                if scores_this_year:
                    benchmarks["year_by_year"][year]["avg_by_competency"][
                        competency
                    ] = sum(scores_this_year) / len(scores_this_year)

                # Identificar top performers neste ano
                ranked_persons = sorted(
                    person_scores.items(), key=lambda x: x[1], reverse=True
                )
                top_count = max(1, len(ranked_persons) // 4)
                benchmarks["year_by_year"][year]["top_performers"][competency] = [
                    pessoa for pessoa, _ in ranked_persons[:top_count]
                ]

        return benchmarks

    def _generate_trends_analysis(self, all_data):
        """
        Gera análise de tendências gerais nos dados coletados.

        Args:
            all_data: Dados coletados de todas as pessoas

        Returns:
            Dict: Análise de tendências
        """
        trends = {
            "overall_trend": {},
            "year_over_year": {},
            "most_improved_areas": [],
            "most_declined_areas": [],
            "team_performance": {},
        }

        # Coletar todos os anos disponíveis
        all_years = set()
        for pessoa_data in all_data.values():
            all_years.update(pessoa_data.keys())

        sorted_years = sorted(all_years)
        if len(sorted_years) < 2:
            trends["summary"] = (
                "Dados insuficientes para análise de tendências (menos de 2 anos)"
            )
            return trends

        # Coletar todas as competências/direcionadores
        all_competencies = set()
        for pessoa_data in all_data.values():
            for ano_data in pessoa_data.values():
                if "resultado" in ano_data:
                    resultado = ano_data["resultado"]
                    if "direcionadores" in resultado:
                        all_competencies.update(resultado["direcionadores"].keys())
                    elif "competencias" in resultado:
                        all_competencies.update(resultado["competencias"].keys())
                    elif isinstance(resultado, dict):
                        all_competencies.update(
                            k
                            for k, v in resultado.items()
                            if isinstance(v, (int, float))
                        )

        # Inicializar dados para competências
        competency_trends = {
            comp: {"scores_by_year": {}, "changes": []} for comp in all_competencies
        }

        # Coletar pontuações médias por ano para cada competência
        for year in sorted_years:
            year_scores = {comp: [] for comp in all_competencies}

            for pessoa, anos_data in all_data.items():
                if year in anos_data and "resultado" in anos_data[year]:
                    resultado = anos_data[year]["resultado"]

                    for comp in all_competencies:
                        score = None

                        if (
                            "direcionadores" in resultado
                            and comp in resultado["direcionadores"]
                        ):
                            score = resultado["direcionadores"][comp]
                        elif (
                            "competencias" in resultado
                            and comp in resultado["competencias"]
                        ):
                            score = resultado["competencias"][comp]
                        elif isinstance(resultado, dict) and comp in resultado:
                            if isinstance(resultado[comp], (int, float)):
                                score = resultado[comp]

                        if score is not None:
                            year_scores[comp].append(score)

            # Calcular média por competência para este ano
            for comp, scores in year_scores.items():
                if scores:
                    avg_score = sum(scores) / len(scores)
                    competency_trends[comp]["scores_by_year"][year] = avg_score

        # Calcular mudanças ano a ano para cada competência
        for comp, data in competency_trends.items():
            scores_by_year = data["scores_by_year"]

            for i in range(len(sorted_years) - 1):
                year1 = sorted_years[i]
                year2 = sorted_years[i + 1]

                if year1 in scores_by_year and year2 in scores_by_year:
                    change = scores_by_year[year2] - scores_by_year[year1]
                    data["changes"].append(
                        {
                            "from_year": year1,
                            "to_year": year2,
                            "change": change,
                            "percent_change": (change / scores_by_year[year1] * 100)
                            if scores_by_year[year1]
                            else 0,
                        }
                    )

        # Calcular tendência geral para cada competência
        for comp, data in competency_trends.items():
            scores = list(data["scores_by_year"].values())
            if len(scores) >= 2:
                first_score = scores[0]
                last_score = scores[-1]
                overall_change = last_score - first_score
                overall_percent = (
                    (overall_change / first_score * 100) if first_score else 0
                )

                trends["overall_trend"][comp] = {
                    "first_year": sorted_years[0],
                    "last_year": sorted_years[-1],
                    "overall_change": overall_change,
                    "overall_percent_change": overall_percent,
                    "trend_direction": "up"
                    if overall_change > 0
                    else "down"
                    if overall_change < 0
                    else "stable",
                }

        # Identificar áreas com maior melhoria e declínio
        trend_changes = []
        for comp in all_competencies:
            if comp in trends["overall_trend"]:
                trend_changes.append(
                    (comp, trends["overall_trend"][comp]["overall_change"])
                )

        sorted_changes = sorted(trend_changes, key=lambda x: x[1], reverse=True)

        top_improved = sorted_changes[: min(5, len(sorted_changes))]
        trends["most_improved_areas"] = [
            {"area": comp, "change": change}
            for comp, change in top_improved
            if change > 0
        ]

        bottom_declined = sorted_changes[-min(5, len(sorted_changes)) :]
        trends["most_declined_areas"] = [
            {"area": comp, "change": change}
            for comp, change in bottom_declined
            if change < 0
        ]

        # Calcular tendências ano a ano
        for i in range(len(sorted_years) - 1):
            year1 = sorted_years[i]
            year2 = sorted_years[i + 1]

            year_pair = f"{year1}_to_{year2}"
            trends["year_over_year"][year_pair] = {
                "improved_areas": [],
                "declined_areas": [],
                "stable_areas": [],
                "overall_change": 0,
            }

            total_change = 0
            count = 0

            for comp, data in competency_trends.items():
                for change_data in data["changes"]:
                    if (
                        change_data["from_year"] == year1
                        and change_data["to_year"] == year2
                    ):
                        count += 1
                        total_change += change_data["change"]

                        if change_data["change"] > 0:
                            trends["year_over_year"][year_pair][
                                "improved_areas"
                            ].append({"area": comp, "change": change_data["change"]})
                        elif change_data["change"] < 0:
                            trends["year_over_year"][year_pair][
                                "declined_areas"
                            ].append({"area": comp, "change": change_data["change"]})
                        else:
                            trends["year_over_year"][year_pair]["stable_areas"].append(
                                comp
                            )

            if count > 0:
                trends["year_over_year"][year_pair]["overall_change"] = (
                    total_change / count
                )

        return trends

    def _clean_unused_files(self, output_path: Path) -> None:
        """
        Limpa arquivos temporários e antigos não utilizados.

        Args:
            output_path: Caminho da pasta de saída
        """
        try:
            # Lista de diretórios para verificar
            subdirs_to_check = ["temp", "cache", "logs", "old_reports"]

            # Removendo arquivos temporários
            for subdir in subdirs_to_check:
                dir_path = output_path / subdir
                if dir_path.exists():
                    # Remover arquivos com mais de 30 dias
                    import time

                    now = time.time()
                    for item in dir_path.glob("*"):
                        is_old = (now - item.stat().st_mtime) > (30 * 86400)  # 30 dias
                        if is_old:
                            if item.is_file():
                                item.unlink()
                                if self.sync.verbose:
                                    print(f"Removed old file: {item}")
                            elif item.is_dir():
                                import shutil

                                shutil.rmtree(item)
                                if self.sync.verbose:
                                    print(f"Removed old directory: {item}")

            # Remove arquivos de cache do Python
            for pycache in output_path.glob("**/__pycache__"):
                import shutil

                shutil.rmtree(pycache)
                if self.sync.verbose:
                    print(f"Removed Python cache: {pycache}")

            # Remover arquivos temporários
            for temp_file in output_path.glob("**/temp_*.*"):
                temp_file.unlink()
                if self.sync.verbose:
                    print(f"Removed temporary file: {temp_file}")

        except Exception as e:
            logging.warning(f"Warning during cleanup: {str(e)}")
            # Não interromper o processamento por falha na limpeza
            pass

    def _generate_overall_benchmark(self, processed_data, output_path):
        """
        Generate overall benchmark report comparing all people and years.

        Args:
            processed_data: Dictionary with processed data
            output_path: Path to save the report
        """
        self.logger.info(f"Generating overall benchmark report: {output_path}")

        try:
            # Prepare benchmark data
            benchmark_data = []
            for person_id, person_data in processed_data.items():
                for year, year_data in person_data.items():
                    if not year_data:
                        continue

                    # Extract key metrics for benchmarking
                    scores = year_data.get("scores", {})
                    if not scores:
                        continue

                    # Get average score if available
                    avg_score = 0
                    if isinstance(scores, dict) and scores:
                        avg_score = sum(scores.values()) / len(scores)

                    # Add to benchmark data
                    benchmark_data.append(
                        {
                            "pessoa": person_id,
                            "ano": year,
                            "media_pontuacao": avg_score,
                            "pontuacoes": scores,
                            "dados_completos": year_data,
                        }
                    )

            # Create HTML content
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Relatório de Benchmark Geral</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1 { color: #333366; }
                    table { border-collapse: collapse; width: 100%; margin-top: 20px; }
                    th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
                    th { background-color: #f2f2f2; }
                    tr:hover {background-color: #f5f5f5;}
                    .chart-container { margin-top: 30px; height: 400px; }
                </style>
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            </head>
            <body>
                <h1>Relatório de Benchmark Geral</h1>
                <p>Este relatório apresenta uma comparação entre todos os colaboradores e anos disponíveis.</p>
                
                <h2>Tabela Comparativa</h2>
                <table>
                    <tr>
                        <th>Pessoa</th>
                        <th>Ano</th>
                        <th>Média de Pontuação</th>
                    </tr>
            """

            # Add rows to the table
            for item in sorted(benchmark_data, key=lambda x: (x["pessoa"], x["ano"])):
                html_content += f"""
                    <tr>
                        <td>{item["pessoa"]}</td>
                        <td>{item["ano"]}</td>
                        <td>{item["media_pontuacao"]:.2f}</td>
                    </tr>
                """

            html_content += """
                </table>
                
                <div class="chart-container">
                    <canvas id="benchmarkChart"></canvas>
                </div>
                
                <script>
                    // Prepare data for chart
                    const chartData = {
            """

            # Prepare data for chart
            pessoas = sorted(set(item["pessoa"] for item in benchmark_data))
            anos = sorted(set(item["ano"] for item in benchmark_data))

            # Labels for chart
            html_content += f"        labels: {json.dumps(pessoas)},\n"

            # Datasets for chart (one per year)
            html_content += "        datasets: [\n"
            for ano in anos:
                ano_data = [
                    next(
                        (
                            item["media_pontuacao"]
                            for item in benchmark_data
                            if item["pessoa"] == pessoa and item["ano"] == ano
                        ),
                        None,
                    )
                    for pessoa in pessoas
                ]

                # Replace None with null for JavaScript
                ano_data_js = [
                    score if score is not None else "null" for score in ano_data
                ]

                html_content += f"""
                    {{
                        label: '{ano}',
                        data: {json.dumps(ano_data_js)},
                        backgroundColor: 'rgba({hash(ano) % 200}, {(hash(ano) * 3) % 200}, {(hash(ano) * 7) % 200}, 0.2)',
                        borderColor: 'rgba({hash(ano) % 200}, {(hash(ano) * 3) % 200}, {(hash(ano) * 7) % 200}, 1)',
                        borderWidth: 1
                    }},
                """

            html_content += """
                    ]
                };
                
                // Create chart
                const ctx = document.getElementById('benchmarkChart').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: chartData,
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'Média de Pontuação'
                                }
                            },
                            x: {
                                title: {
                                    display: true,
                                    text: 'Pessoa'
                                }
                            }
                        },
                        plugins: {
                            title: {
                                display: true,
                                text: 'Comparação de Desempenho por Ano'
                            },
                            legend: {
                                position: 'top',
                            }
                        }
                    }
                });
                </script>
            </body>
            </html>
            """

            # Write the HTML content to the file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            return True
        except Exception as e:
            self.logger.error(f"Error generating overall benchmark: {str(e)}")
            if not self.ignore_errors:
                raise
            return False

    def _generate_yoy_comparison(self, processed_data, year1, year2, output_path):
        """
        Generate year-over-year comparison report.

        Args:
            processed_data: Dictionary with processed data
            year1: First year to compare
            year2: Second year to compare
            output_path: Path to save the report
        """
        self.logger.info(
            f"Generating year-over-year comparison report: {year1} to {year2} - {output_path}"
        )

        try:
            # Prepare comparison data
            comparison_data = []
            for person_id, person_data in processed_data.items():
                # Skip if person doesn't have data for both years
                if year1 not in person_data or year2 not in person_data:
                    continue

                year1_data = person_data[year1]
                year2_data = person_data[year2]

                # Skip if any year data is empty
                if not year1_data or not year2_data:
                    continue

                # Extract scores for comparison
                scores1 = year1_data.get("scores", {})
                scores2 = year2_data.get("scores", {})

                if not scores1 or not scores2:
                    continue

                # Calculate averages and growth
                avg_score1 = sum(scores1.values()) / len(scores1) if scores1 else 0
                avg_score2 = sum(scores2.values()) / len(scores2) if scores2 else 0
                growth = avg_score2 - avg_score1
                growth_percent = (growth / avg_score1 * 100) if avg_score1 else 0

                # Compare specific competencies that exist in both years
                competency_comparison = {}
                for comp in set(scores1.keys()) & set(scores2.keys()):
                    comp_growth = scores2[comp] - scores1[comp]
                    comp_growth_percent = (
                        (comp_growth / scores1[comp] * 100) if scores1[comp] else 0
                    )
                    competency_comparison[comp] = {
                        "year1": scores1[comp],
                        "year2": scores2[comp],
                        "growth": comp_growth,
                        "growth_percent": comp_growth_percent,
                    }

                comparison_data.append(
                    {
                        "pessoa": person_id,
                        "media_ano1": avg_score1,
                        "media_ano2": avg_score2,
                        "crescimento": growth,
                        "crescimento_percentual": growth_percent,
                        "comparacao_competencias": competency_comparison,
                    }
                )

            # Create HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Comparação Ano a Ano: {year1} para {year2}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1, h2 {{ color: #333366; }}
                    table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                    th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                    th {{ background-color: #f2f2f2; }}
                    tr:hover {{background-color: #f5f5f5;}}
                    .positive {{ color: green; }}
                    .negative {{ color: red; }}
                    .chart-container {{ margin-top: 30px; height: 400px; }}
                </style>
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            </head>
            <body>
                <h1>Comparação Ano a Ano: {year1} para {year2}</h1>
                <p>Este relatório apresenta a evolução dos colaboradores entre {year1} e {year2}.</p>
                
                <h2>Tabela de Evolução</h2>
                <table>
                    <tr>
                        <th>Pessoa</th>
                        <th>Média {year1}</th>
                        <th>Média {year2}</th>
                        <th>Crescimento</th>
                        <th>Crescimento %</th>
                    </tr>
            """

            # Add rows to the table
            for item in sorted(
                comparison_data, key=lambda x: x["crescimento_percentual"], reverse=True
            ):
                growth_class = "positive" if item["crescimento"] >= 0 else "negative"
                html_content += f"""
                    <tr>
                        <td>{item["pessoa"]}</td>
                        <td>{item["media_ano1"]:.2f}</td>
                        <td>{item["media_ano2"]:.2f}</td>
                        <td class="{growth_class}">{item["crescimento"]:.2f}</td>
                        <td class="{growth_class}">{item["crescimento_percentual"]:.2f}%</td>
                    </tr>
                """

            html_content += """
                </table>
                
                <div class="chart-container">
                    <canvas id="growthChart"></canvas>
                </div>
                
                <script>
                    // Prepare data for chart
                    const chartData = {
            """

            # Prepare data for chart
            pessoas = [item["pessoa"] for item in comparison_data]
            growth_percentages = [
                item["crescimento_percentual"] for item in comparison_data
            ]

            # Colors based on positive/negative growth
            colors = [
                "rgba(75, 192, 192, 0.2)" if g >= 0 else "rgba(255, 99, 132, 0.2)"
                for g in growth_percentages
            ]
            borders = [
                "rgba(75, 192, 192, 1)" if g >= 0 else "rgba(255, 99, 132, 1)"
                for g in growth_percentages
            ]

            html_content += f"""
                        labels: {json.dumps(pessoas)},
                        datasets: [{{
                            label: 'Crescimento Percentual',
                            data: {json.dumps(growth_percentages)},
                            backgroundColor: {json.dumps(colors)},
                            borderColor: {json.dumps(borders)},
                            borderWidth: 1
                        }}]
                    }};
                    
                    // Create chart
                    const ctx = document.getElementById('growthChart').getContext('2d');
                    new Chart(ctx, {{
                        type: 'bar',
                        data: chartData,
                        options: {{
                            responsive: true,
                            scales: {{
                                y: {{
                                    title: {{
                                        display: true,
                                        text: 'Crescimento (%)'
                                    }}
                                }},
                                x: {{
                                    title: {{
                                        display: true,
                                        text: 'Pessoa'
                                    }}
                                }}
                            }},
                            plugins: {{
                                title: {{
                                    display: true,
                                    text: 'Evolução Percentual {year1} → {year2}'
                                }},
                                legend: {{
                                    position: 'top',
                                }}
                            }}
                        }}
                    }});
                </script>
                
                <h2>Detalhamento por Competência</h2>
            """

            # Add detailed competency breakdown for each person
            for item in sorted(comparison_data, key=lambda x: x["pessoa"]):
                html_content += f"""
                <h3>{item["pessoa"]}</h3>
                <table>
                    <tr>
                        <th>Competência</th>
                        <th>{year1}</th>
                        <th>{year2}</th>
                        <th>Crescimento</th>
                        <th>Crescimento %</th>
                    </tr>
                """

                for comp, comp_data in sorted(item["comparacao_competencias"].items()):
                    growth_class = (
                        "positive" if comp_data["growth"] >= 0 else "negative"
                    )
                    html_content += f"""
                    <tr>
                        <td>{comp}</td>
                        <td>{comp_data["year1"]:.2f}</td>
                        <td>{comp_data["year2"]:.2f}</td>
                        <td class="{growth_class}">{comp_data["growth"]:.2f}</td>
                        <td class="{growth_class}">{comp_data["growth_percent"]:.2f}%</td>
                    </tr>
                    """

                html_content += """
                </table>
                <div class="chart-container">
                    <canvas id="competencyChart_{pessoa}"></canvas>
                </div>
                <script>
                """.format(pessoa=item["pessoa"].replace(" ", "_"))

                # Add competency chart for this person
                comp_names = list(item["comparacao_competencias"].keys())
                year1_values = [
                    item["comparacao_competencias"][c]["year1"] for c in comp_names
                ]
                year2_values = [
                    item["comparacao_competencias"][c]["year2"] for c in comp_names
                ]

                html_content += f"""
                    // Prepare competency data for {item["pessoa"]}
                    const compData_{item["pessoa"].replace(" ", "_")} = {{
                        labels: {json.dumps(comp_names)},
                        datasets: [
                            {{
                                label: '{year1}',
                                data: {json.dumps(year1_values)},
                                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                                borderColor: 'rgba(54, 162, 235, 1)',
                                borderWidth: 1
                            }},
                            {{
                                label: '{year2}',
                                data: {json.dumps(year2_values)},
                                backgroundColor: 'rgba(255, 159, 64, 0.2)',
                                borderColor: 'rgba(255, 159, 64, 1)',
                                borderWidth: 1
                            }}
                        ]
                    }};
                    
                    // Create competency chart for {item["pessoa"]}
                    const compCtx_{item["pessoa"].replace(" ", "_")} = document.getElementById('competencyChart_{item["pessoa"].replace(" ", "_")}').getContext('2d');
                    new Chart(compCtx_{item["pessoa"].replace(" ", "_")}, {{
                        type: 'radar',
                        data: compData_{item["pessoa"].replace(" ", "_")},
                        options: {{
                            responsive: true,
                            scales: {{
                                r: {{
                                    beginAtZero: true,
                                    min: 0,
                                    max: 5
                                }}
                            }},
                            plugins: {{
                                title: {{
                                    display: true,
                                    text: 'Competências: {year1} vs {year2}'
                                }}
                            }}
                        }}
                    }});
                </script>
                """

            html_content += """
            </body>
            </html>
            """

            # Write the HTML content to the file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            return True
        except Exception as e:
            self.logger.error(f"Error generating year-over-year comparison: {str(e)}")
            if not self.ignore_errors:
                raise
            return False

    def _generate_peer_analysis(self, all_data):
        """
        Gera análise de pares baseada nos dados coletados.

        Args:
            all_data: Dados coletados de todas as pessoas

        Returns:
            Dict: Análise de pares
        """
        # Implementação básica para evitar erros
        peer_analysis = {
            "pairs": [],
            "similar_profiles": [],
            "complementary_skills": [],
            "team_composition": {},
        }

        # Se houver menos de 2 pessoas, não há como fazer análise de pares
        if len(all_data) < 2:
            peer_analysis["summary"] = (
                "Dados insuficientes para análise de pares (menos de 2 pessoas)"
            )
            return peer_analysis

        # Adicionar resumo genérico
        peer_analysis["summary"] = (
            f"Análise de pares baseada em {len(all_data)} pessoas"
        )

        return peer_analysis

    def _generate_team_evolution_report(self, all_data):
        """
        Gera relatório de evolução de equipes.

        Args:
            all_data: Dados coletados de todas as pessoas

        Returns:
            Dict: Relatório de evolução de equipes
        """
        # Implementação básica para evitar erros
        team_evolution = {
            "teams": {},
            "overall_trend": "stable",
            "improvement_areas": [],
            "challenge_areas": [],
        }

        # Adicionar resumo genérico
        team_evolution["summary"] = (
            f"Análise de evolução de equipes baseada em {len(all_data)} pessoas"
        )

        return team_evolution

    def _generate_skills_distribution(self, all_data):
        """
        Gera relatório de distribuição de habilidades.

        Args:
            all_data: Dados coletados de todas as pessoas

        Returns:
            Dict: Relatório de distribuição de habilidades
        """
        # Implementação básica para evitar erros
        skills_distribution = {
            "skills": {},
            "distribution": {},
            "gaps": [],
            "strengths": [],
        }

        # Adicionar resumo genérico
        skills_distribution["summary"] = (
            f"Análise de distribuição de habilidades baseada em {len(all_data)} pessoas"
        )

        return skills_distribution


class SyncCommand:
    """Command class for data synchronization."""

    def add_arguments(self, parser):
        """Add command-specific arguments to the parser."""
        parser.add_argument(
            "--data-dir", help="Diretório com os dados", default="./data"
        )
        parser.add_argument(
            "--output-dir", help="Diretório para saída", default="./output"
        )
        parser.add_argument(
            "--force", help="Força o reprocessamento", action="store_true"
        )
        parser.add_argument(
            "--skip-viz", help="Pula a geração de visualizações", action="store_true"
        )
        parser.add_argument(
            "--ignore-errors",
            help="Ignora erros durante a execução",
            action="store_true",
        )
        parser.add_argument(
            "--formatos",
            help="Formatos a processar (json,yaml,csv,excel,all)",
            default="all",
        )
        parser.add_argument(
            "--compress", help="Comprime os resultados", action="store_true"
        )
        parser.add_argument(
            "--pessoa", help="Filtra processamento para uma pessoa específica"
        )
        parser.add_argument("--ano", help="Filtra processamento para um ano específico")
        parser.add_argument(
            "--export-excel",
            help="Exporta dados consolidados para Excel",
            action="store_true",
        )
        parser.add_argument(
            "--verbose", help="Mostra informações detalhadas", action="store_true"
        )
        parser.add_argument(
            "--skip-benchmark",
            help="Pula a geração de relatórios de benchmark",
            action="store_true",
        )
        return parser

    def execute(self, args):
        """Execute the command with the given arguments."""
        sync = DataSync(
            data_dir=args.data_dir,
            output_dir=args.output_dir,
            force=args.force,
            skip_viz=args.skip_viz,
            ignore_errors=args.ignore_errors,
            selected_formats=args.formatos,
            compress=args.compress,
            pessoa_filter=args.pessoa,
            ano_filter=args.ano,
            export_excel=args.export_excel,
            verbose=args.verbose,
            skip_benchmark=args.skip_benchmark,
        )
        processed = sync.process()
        return 0 if processed > 0 else 1


if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="Synchronize data and generate reports"
    )

    # Create command
    cmd = SyncCommand()

    # Add arguments
    cmd.add_arguments(parser)

    # Parse arguments
    args = parser.parse_args()

    # Execute command
    exit_code = cmd.execute(args)

    # Exit with appropriate code
    exit(exit_code)
