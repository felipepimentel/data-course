"""
Sync and documentation commands for People Analytics CLI.

This module contains commands for data synchronization and documentation generation.
"""

import argparse
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List

from ..domain.evaluation import EvaluationScore


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


class SyncCommand:
    """
    Comando sync para processar dados.
    """

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """
        Add command-specific arguments to the parser.

        Args:
            parser: The argparse parser or subparser to add arguments to
        """
        # Input/output options
        parser.add_argument(
            "--data-dir",
            default="data",
            help="Directory containing data files",
        )
        parser.add_argument(
            "--output-dir",
            default="output",
            help="Directory to store output files",
        )

        # Processing filters
        parser.add_argument(
            "--pessoa", type=str, help="Filter processing for a specific person"
        )
        parser.add_argument(
            "--ano", type=str, help="Filter processing for a specific year"
        )
        parser.add_argument(
            "--formats",
            default="all",
            help="Formats to process (comma-separated list)",
            dest="formatos",
        )

        # Control flags
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force reprocessing of files",
        )
        parser.add_argument(
            "--ignore-errors",
            action="store_true",
            help="Ignore errors and continue processing",
        )

        # Skills analysis options (all enabled by default)
        parser.add_argument(
            "--report-output-dir",
            type=str,
            default="output/reports",
            help="Directory to store generated reports",
        )
        parser.add_argument(
            "--include-org-chart",
            action="store_true",
            help="Include organizational chart in skill reports",
            dest="report_include_org_chart",
        )
        parser.add_argument(
            "--year-comparison",
            action="store_true",
            help="Include year-over-year comparisons in skill reports",
            dest="report_year_comparison",
        )

        # Talent development reports options (all enabled by default)
        parser.add_argument(
            "--no-9box",
            action="store_true",
            help="Disable 9-Box Matrix reports",
            dest="no_9box",
        )
        parser.add_argument(
            "--no-career-sim",
            action="store_true",
            help="Disable Career Simulation reports",
            dest="no_career_sim",
        )
        parser.add_argument(
            "--no-network",
            action="store_true",
            help="Disable Influence Network reports",
            dest="no_network",
        )
        parser.add_argument(
            "--talent-report-dir",
            type=str,
            default="output/talent_reports",
            help="Directory to store talent development reports",
        )

        # Feature toggles (disable features)
        parser.add_argument(
            "--no-viz",
            action="store_true",
            help="Skip generation of visualizations",
            dest="skip_viz",
        )
        parser.add_argument(
            "--no-zip",
            action="store_true",
            help="Don't compress output directory after processing",
            dest="no_zip",
        )
        parser.add_argument(
            "--no-dashboard",
            action="store_true",
            help="Skip generation of dashboard",
            dest="skip_dashboard",
        )
        parser.add_argument(
            "--no-excel",
            action="store_true",
            help="Skip Excel export",
            dest="no_excel",
        )
        parser.add_argument(
            "--no-markdown",
            action="store_true",
            help="Skip generation of markdown reports",
            dest="no_markdown",
        )

        # Performance options
        parser.add_argument(
            "--no-parallel",
            action="store_true",
            help="Use sequential processing instead of parallel",
            dest="no_parallel",
        )
        parser.add_argument(
            "--workers",
            type=int,
            default=0,
            help="Number of workers for parallel processing (0 = auto)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=0,
            help="Batch size for parallel processing (0 = all)",
        )

        # Output control
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Show minimal information during processing",
        )

        # Add peer group and year-over-year analysis options
        parser.add_argument(
            "--peer-analysis",
            action="store_true",
            help="Generate peer group comparison analysis",
            dest="peer_analysis",
        )
        parser.add_argument(
            "--yoy-analysis",
            action="store_true",
            help="Generate year-over-year performance analysis",
            dest="yoy_analysis",
        )
        parser.add_argument(
            "--weighted-scoring",
            action="store_true",
            help="Use weighted scoring for skills by category",
            dest="weighted_scoring",
        )
        parser.add_argument(
            "--analysis-output-dir",
            type=str,
            default="output/analysis",
            help="Directory to store analysis reports",
        )

    def execute(self, args):
        """Execute the sync command"""
        logger = setup_logger("sync")

        # Initialize DataSync
        self.sync = DataSync()

        # Set options
        self.sync.data_dir = Path(args.data_dir)
        self.sync.output_dir = Path(args.output_dir)
        self.sync.force = args.force
        self.sync.skip_viz = args.skip_viz
        self.sync.ignore_errors = args.ignore_errors
        self.sync.zip = not args.no_zip
        self.sync.skip_dashboard = args.skip_dashboard
        self.sync.selected_formats = args.formatos
        self.sync.pessoa_filter = args.pessoa
        self.sync.ano_filter = args.ano
        self.sync.export_excel = not args.no_excel
        self.sync.rich_markdown = not args.no_markdown
        self.sync.verbose = not args.quiet
        self.sync.parallel = not args.no_parallel
        self.sync.workers = args.workers
        self.sync.batch_size = args.batch_size
        # Progress is always on unless quiet is specified
        self.sync.progress = not args.quiet

        # Skills analysis options
        if hasattr(args, "generate_evaluation_report"):
            self.sync.generate_evaluation_report = args.generate_evaluation_report
        if hasattr(args, "generate_skill_recommendations"):
            self.sync.generate_skill_recommendations = (
                args.generate_skill_recommendations
            )
        if hasattr(args, "include_radar_charts"):
            self.sync.include_radar_charts = args.include_radar_charts
        if hasattr(args, "generate_skill_analytics"):
            self.sync.generate_skill_analytics = args.generate_skill_analytics
        if hasattr(args, "report_output_dir"):
            self.sync.report_output_dir = args.report_output_dir
        if hasattr(args, "report_include_org_chart"):
            self.sync.report_include_org_chart = args.report_include_org_chart
        if hasattr(args, "report_year_comparison"):
            self.sync.report_year_comparison = args.report_year_comparison

        # Talent development options - enabled by default
        self.sync.use_9box = True
        self.sync.use_career_sim = True
        self.sync.use_network = True

        # Allow disabling individual talent reports
        if hasattr(args, "no_9box") and args.no_9box:
            self.sync.use_9box = False
        if hasattr(args, "no_career_sim") and args.no_career_sim:
            self.sync.use_career_sim = False
        if hasattr(args, "no_network") and args.no_network:
            self.sync.use_network = False
        if hasattr(args, "talent_report_dir"):
            self.sync.talent_report_dir = args.talent_report_dir

        # Peer group and year-over-year analysis options
        if hasattr(args, "peer_analysis"):
            self.sync.peer_analysis = args.peer_analysis
        if hasattr(args, "yoy_analysis"):
            self.sync.yoy_analysis = args.yoy_analysis
        if hasattr(args, "weighted_scoring"):
            self.sync.weighted_scoring = args.weighted_scoring
        if hasattr(args, "analysis_output_dir"):
            self.sync.analysis_output_dir = args.analysis_output_dir

        # Execute
        logger.info("Starting sync command execution")

        print("People Analytics Data Processor")
        print("===============================")
        print(f"Data path: {self.sync.data_dir}")
        print(f"Output path: {self.sync.output_dir}")

        if self.sync.force:
            print("Forcing reprocessing of all files")

        if self.sync.verbose:
            print(f"Formats: {self.sync.selected_formats}")

            if self.sync.pessoa_filter:
                print(f"Filtering by pessoa: {self.sync.pessoa_filter}")
            if self.sync.ano_filter:
                print(f"Filtering by ano: {self.sync.ano_filter}")

            print(f"Ignore errors: {self.sync.ignore_errors}")
            print(f"Skip visualizations: {self.sync.skip_viz}")
            print(f"Compress results: {self.sync.zip}")
            print(f"Skip dashboard: {self.sync.skip_dashboard}")
            print(f"Export to Excel: {self.sync.export_excel}")
            print(f"Parallel processing: {self.sync.parallel}")
            print(f"Rich markdown reports: {self.sync.rich_markdown}")

            # Print skills analysis options if enabled
            if self.sync.generate_evaluation_report:
                print("Skills report generation: Enabled")
            if self.sync.generate_skill_recommendations:
                print("Skill recommendations: Enabled")
            if self.sync.include_radar_charts:
                print("Skills radar charts: Enabled")
            if self.sync.generate_skill_analytics:
                print("Comprehensive skill analytics: Enabled")

            # Print talent development options
            if self.sync.use_9box:
                print("9-Box Matrix reports: Enabled")
            if self.sync.use_career_sim:
                print("Career Simulation reports: Enabled")
            if self.sync.use_network:
                print("Influence Network reports: Enabled")
            print(f"Talent reports directory: {self.sync.talent_report_dir}")

            # Print analysis options
            if self.sync.peer_analysis:
                print("Peer group analysis: Enabled")
            if self.sync.yoy_analysis:
                print("Year-over-year analysis: Enabled")
            if self.sync.weighted_scoring:
                print("Weighted skill scoring: Enabled")
            if hasattr(self.sync, "analysis_output_dir"):
                print(f"Analysis reports directory: {self.sync.analysis_output_dir}")

        print("Expected data structure: <pessoa>/<ano>/resultado.json")
        print(f"Processing started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("===============================")

        try:
            # Execute sync process
            print("Starting data analysis and processing...")
            results = self.sync.sync()

            # Print results
            for result in results:
                print(result)

            print("Analysis processing completed successfully.")
            return 0
        except Exception as e:
            print(f"ERROR in sync processing: {str(e)}")
            if not self.sync.ignore_errors:
                return 1
            print("Continuing with reduced functionality due to error...")
            return 0


class DataSync:
    """
    Classe para sincronizar dados.
    """

    def __init__(self):
        """Initialize the DataSync class"""
        # Data paths
        self.data_dir = Path("data")
        self.output_dir = Path("output")

        # Options - comprehensive defaults
        self.force = False
        self.skip_viz = False  # Generate visualizations by default
        self.ignore_errors = False
        self.zip = True  # Compress results by default
        self.skip_dashboard = False  # Generate dashboard by default
        self.verbose = True  # Show detailed information by default
        self.parallel = True  # Use parallel processing by default
        self.batch_size = 0  # 0 means all at once
        self.workers = 0  # 0 means use CPU count
        self.progress = True  # Show progress by default
        self.clean_data = False
        self.template = None
        self.theme = "default"
        self.output_config = None
        self.selected_formats = "all"  # Process all formats by default
        self.pessoa_filter = None
        self.ano_filter = None
        self.export_excel = True  # Export Excel by default
        self.rich_markdown = True  # Generate rich markdown by default

        # Skills analysis options
        self.generate_evaluation_report = True
        self.generate_skill_recommendations = True
        self.include_radar_charts = True
        self.generate_skill_analytics = True
        self.report_output_dir = "output/reports"
        self.report_include_org_chart = True
        self.report_year_comparison = True
        self.report_include_skills = True
        self.include_mermaid_diagrams = True
        self.generate_comprehensive_report = True
        self.generate_interactive_report = True
        self.generate_comparison_templates = True

        # Talent development options - all enabled by default
        self.use_9box = True
        self.use_career_sim = True
        self.use_network = True
        self.talent_report_dir = "output/talent_reports"

        # Valid formats
        self.valid_formats = {
            "json": [".json"],
            "yaml": [".yaml", ".yml"],
            "csv": [".csv"],
            "excel": [".xlsx", ".xls"],
            "markdown": [".md"],
        }

        # Progress tracking
        self.total_progress = 100
        self.current_progress = 0
        self.progress_increment = 1
        self.last_progress_time = 0

        # Results
        self.processed_directories = []
        self.errors = []

        # Mermaid validation
        self.validate_mermaid = True

        # Logger
        self.logger = logging.getLogger("datasync")

        # Configurações adicionais
        self.export_pdf = False
        self.synthetic = False
        self.bulk_export = False
        self.anonymize = False
        self.template_path = None
        self.show_progress = True
        self.output_config_path = None

        # Performance metrics
        self.total_directories = 0
        self.processed_directories_count = 0
        self.skipped_directories = 0
        self.error_directories = 0
        self.start_time = None
        self.end_time = None

        # Inicializar calculadora de scores
        self.score_calculator = EvaluationScore()

        # Progress tracking
        self.current_progress = 0
        self.total_progress = 100
        self.last_progress_report = 0

        # Estatísticas de processamento
        self.stats = {
            "total_files": 0,
            "processed_files": 0,
            "skipped_files": 0,
            "error_files": 0,
            "generated_reports": 0,
            "generated_visualizations": 0,
        }

        # Rastrear diretórios processados
        self.processed_data_dirs = set()

        # Criar diretórios necessários
        self._ensure_directories()

        # Peer group and year-over-year analysis options
        self.peer_analysis = False
        self.yoy_analysis = False
        self.weighted_scoring = False
        self.analysis_output_dir = "output/analysis"

    def _ensure_directories(self):
        """Garante que todos os diretórios necessários existam."""
        # Skip if directories not set yet
        if self.data_dir is None or self.output_dir is None:
            return

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

        # Diretórios de análise
        if hasattr(self, "analysis_output_dir"):
            Path(self.analysis_output_dir).mkdir(exist_ok=True, parents=True)
            Path(self.analysis_output_dir, "peer_comparison").mkdir(
                exist_ok=True, parents=True
            )
            Path(self.analysis_output_dir, "year_over_year").mkdir(
                exist_ok=True, parents=True
            )

    def _report_progress(self, increment=1, force=False):
        """
        Report progress of a long-running operation.

        Args:
            increment: Amount to increment the progress counter
            force: Force reporting even if percentage hasn't changed
        """
        self.current_progress += increment

        # Calculate percentage
        if self.total_progress > 0:
            percentage = int((self.current_progress / self.total_progress) * 100)
        else:
            percentage = 0

        # Only report if percentage changed or force is True
        if percentage != self.last_progress_report or force:
            self.last_progress_report = percentage
            self.logger.info(
                f"Progresso: {percentage}% ({self.current_progress}/{self.total_progress})"
            )

    def _set_total_progress(self, total):
        """
        Set the total number of steps for progress tracking.

        Args:
            total: Total number of steps
        """
        self.total_progress = max(
            1, total
        )  # Ensure at least 1 to avoid division by zero
        self.current_progress = 0
        self.last_progress_report = 0

        if self.verbose:
            self.logger.info(f"Total de etapas: {self.total_progress}")

    def _reset_progress(self):
        """Reset progress tracking."""
        self.current_progress = 0
        self.last_progress_report = 0

    def _compress_output(self):
        """Compress output if requested"""
        pass  # Placeholder

    def sync(self):
        """
        Execute the sync process.

        This is the main method for data synchronization that processes
        all directories and files according to the configured options.

        Returns:
            List of result messages
        """
        results = []

        try:
            # Log start message
            start_message = (
                f"Starting sync at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            results.append(start_message)

            # Process the pessoa/ano structure
            valid_directories = self._process_pessoa_ano_structure()

            if not valid_directories:
                message = "No valid directories found for processing"
                results.append(message)
                return results

            # Process directories (sequential or parallel)
            if self.parallel:
                success = self._process_directories_parallel(valid_directories)
            else:
                success = self._process_directories_sequential(valid_directories)

            # Complete processing
            if success:
                results.append(
                    f"Successfully processed {len(self.processed_directories)} directories"
                )
                if self.processed_directories:
                    results.append("Processed directories:")
                    for directory in self.processed_directories:
                        results.append(f"  - {directory}")
            else:
                results.append(
                    f"Process completed with errors in {len(self.errors)} directories"
                )
                if self.errors:
                    results.append("Errors:")
                    for error in self.errors:
                        results.append(f"  - {error}")

            # Generate talent development reports
            if (
                hasattr(self, "use_9box")
                or hasattr(self, "use_career_sim")
                or hasattr(self, "use_network")
            ):
                results.append("Generating talent development reports...")
                if self._generate_talent_development_reports():
                    results.append("Talent development reports generated successfully")
                else:
                    results.append("Error generating talent development reports")

            # Generate analysis reports if enabled
            if (
                hasattr(self, "peer_analysis")
                and self.peer_analysis
                or hasattr(self, "yoy_analysis")
                and self.yoy_analysis
            ):
                results.append("Generating analysis reports...")
                if self._generate_analysis_reports():
                    results.append("Analysis reports generated successfully")
                else:
                    results.append("Error generating analysis reports")

            # Complete processing (compress, etc.)
            self._complete_processing()

            # Log end message
            end_message = (
                f"Sync completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            results.append(end_message)

            return results

        except Exception as e:
            error_message = f"Error in sync process: {str(e)}"
            results.append(error_message)
            if not self.ignore_errors:
                raise
            return results

    def _process_file(self, file_path, file_format):
        """Process a file based on its format"""
        if self.verbose:
            print(f"Processing {file_path} as {file_format}")

        # Process based on format
        if file_format == "json":
            return self._process_json_file(file_path, None)
        elif file_format == "yaml":
            return self._process_yaml_file(file_path)
        elif file_format == "csv":
            return self._process_csv_file(file_path)
        elif file_format == "excel":
            return self._process_excel_file(file_path)
        else:
            logging.warning(f"Unsupported format: {file_format}")
            return None

    def _process_json_file(self, json_file, output_dir=None):
        """Process a JSON file and generate outputs

        Args:
            json_file: Path to the JSON file
            output_dir: Path to the output directory (optional)

        Returns:
            dict: The processed data
        """
        # Get information from the file path
        pessoa_dir = json_file.parent.parent.name
        ano_dir = json_file.parent.name

        try:
            # Load the JSON file
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Return the data directly - we'll process it at a higher level
            return data
        except Exception as e:
            self.logger.error(f"Error processing {json_file}: {e}")
            if not self.ignore_errors:
                raise
            return None

    def _process_yaml_file(self, file_path):
        """Process a YAML file"""
        try:
            import yaml

            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            return data
        except Exception as e:
            logging.error(f"Error reading YAML file {file_path}: {e}")
            if not self.ignore_errors:
                raise
            return None

    def _process_csv_file(self, file_path):
        """Process a CSV file"""
        try:
            import pandas as pd

            df = pd.read_csv(file_path)
            return df.to_dict(orient="records")
        except Exception as e:
            logging.error(f"Error reading CSV file {file_path}: {e}")
            if not self.ignore_errors:
                raise
            return None

    def _process_excel_file(self, file_path):
        """Process an Excel file"""
        try:
            import pandas as pd

            # Read all sheets
            sheets = pd.read_excel(file_path, sheet_name=None)

            # Convert to dict
            result = {}
            for sheet_name, df in sheets.items():
                result[sheet_name] = df.to_dict(orient="records")

            return result
        except Exception as e:
            logging.error(f"Error reading Excel file {file_path}: {e}")
            if not self.ignore_errors:
                raise
            return None

    def _combine_data(self, processed_data):
        """Combine data from different formats"""
        if not processed_data:
            return None

        # Default to using the first format's data
        combined = {}

        # If we have JSON data, use it as the base
        if "json" in processed_data:
            combined = processed_data["json"]
        # Otherwise use whatever is available
        else:
            for fmt, data in processed_data.items():
                combined = data
                break

        # Add any additional data from other formats
        for fmt, data in processed_data.items():
            if fmt not in ["json"] and isinstance(data, dict):  # Skip the base format
                # Merge dictionaries
                for key, value in data.items():
                    if key not in combined:
                        combined[key] = value
                    elif isinstance(value, list) and isinstance(combined[key], list):
                        # Extend lists
                        combined[key].extend(value)
                    elif isinstance(value, dict) and isinstance(combined[key], dict):
                        # Recursive merge for nested dicts
                        self._merge_dicts(combined[key], value)

        return combined

    def _merge_dicts(self, dict1, dict2):
        """Merge two dictionaries recursively"""
        for key, value in dict2.items():
            if key in dict1:
                if isinstance(value, dict) and isinstance(dict1[key], dict):
                    # Recursively merge nested dicts
                    self._merge_dicts(dict1[key], value)
                elif isinstance(value, list) and isinstance(dict1[key], list):
                    # Extend lists
                    dict1[key].extend(value)
            else:
                # Add new keys
                dict1[key] = value

    def _process_json_files(self) -> List[str]:
        """Processa todos os arquivos JSON na pasta de entrada."""
        results = []
        json_dir = self.data_path / "json"

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

                # Verificar se já foi processado (a menos que reprocess=True)
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

    def _process_pessoa_ano_structure(self):
        """Process files in pessoa/ano structure"""
        valid_directories = []
        data_dir = Path(self.data_dir)

        # Look for directories in the data path
        for pessoa_dir in data_dir.iterdir():
            if not pessoa_dir.is_dir():
                continue

            # Skip if filtering by pessoa and doesn't match
            if self.pessoa_filter and pessoa_dir.name != self.pessoa_filter:
                if self.verbose:
                    print(
                        f"Skipping directory {pessoa_dir.name} (doesn't match pessoa filter)"
                    )
                continue

            # Look for year directories inside the pessoa directory
            # First, check if it contains subdirectories
            has_subdirectories = False
            for ano_dir in pessoa_dir.iterdir():
                if ano_dir.is_dir():
                    has_subdirectories = True

                    # Skip if filtering by ano and doesn't match
                    if self.ano_filter and ano_dir.name != self.ano_filter:
                        if self.verbose:
                            print(
                                f"Skipping directory {pessoa_dir.name}/{ano_dir.name} (doesn't match ano filter)"
                            )
                        continue

                    # Check for result files
                    result_files = self._check_result_files(ano_dir)
                    if result_files:
                        valid_directories.append(
                            {
                                "pessoa": pessoa_dir,
                                "ano": ano_dir,
                                "path": f"{pessoa_dir.name}/{ano_dir.name}",
                                "files": result_files,
                            }
                        )
                    else:
                        print(
                            f"No result files found in {pessoa_dir.name}/{ano_dir.name}"
                        )

            # If the directory doesn't have subdirectories, check if it contains result files directly
            if not has_subdirectories:
                result_files = self._check_result_files(pessoa_dir)
                if result_files:
                    # If no ano_filter or matches the default
                    if not self.ano_filter or self.ano_filter == "current":
                        valid_directories.append(
                            {
                                "pessoa": pessoa_dir,
                                "ano": pessoa_dir,  # Use the same directory as ano
                                "path": pessoa_dir.name,
                                "files": result_files,
                            }
                        )
                    else:
                        print(
                            f"No result files found in {pessoa_dir.name} matching ano filter"
                        )
                else:
                    print(f"No result files found in {pessoa_dir.name}")

        # Print summary
        print(f"Found {len(valid_directories)} directories to process")

        # Store valid directories for later reference
        self.processed_directories = []

        return valid_directories

    def _process_directories_sequential(self, valid_directories):
        """Process directories sequentially"""
        # Initialize progress bar if requested
        if self.progress:
            self._set_total_progress(len(valid_directories))

        # Process each directory
        for directory in valid_directories:
            pessoa_dir = directory["pessoa"]
            ano_dir = directory["ano"]
            result_files = directory["files"]
            path = directory["path"]

            try:
                print(f"Processing {path}")

                # Create output directories
                pessoa_output = self.output_dir / pessoa_dir.name
                ano_output = pessoa_output / ano_dir.name
                os.makedirs(ano_output, exist_ok=True)

                # Process the directory
                success = self._process_directory(pessoa_dir, ano_dir, result_files)

                if success:
                    self.processed_directories.append(path)
                else:
                    self.errors.append(f"Failed to process {path}")

                # Update progress if enabled
                self._report_progress()

            except Exception as e:
                error_msg = f"Error processing {path}: {str(e)}"
                print(error_msg)
                self.errors.append(error_msg)

                if not self.ignore_errors:
                    raise

        return len(self.errors) == 0

    def _process_directories_parallel(self, valid_directories):
        """Process directories in parallel"""
        # Determine batch size
        batch_size = self.batch_size
        if batch_size <= 0:
            batch_size = len(valid_directories)

        # Determine number of workers
        max_workers = self.workers
        if max_workers <= 0:
            max_workers = os.cpu_count() or 4

        # Cap max_workers to actual directories
        max_workers = min(max_workers, len(valid_directories))

        if self.verbose:
            print(f"Processing with {max_workers} workers in batches of {batch_size}")

        # Initialize progress bar if requested
        if self.progress:
            self._set_total_progress(len(valid_directories))

        # Process in batches
        for i in range(0, len(valid_directories), batch_size):
            batch = valid_directories[i : i + batch_size]
            self._process_batch_parallel(batch, max_workers)

        return len(self.errors) == 0

    def _process_batch_parallel(self, directories, max_workers):
        """Process a batch of directories in parallel"""
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit tasks
            future_to_dir = {}
            for directory in directories:
                pessoa_dir = directory["pessoa"]
                ano_dir = directory["ano"]
                result_files = directory["files"]
                path = directory["path"]

                future = executor.submit(
                    self._process_directory_safe,
                    pessoa_dir,
                    ano_dir,
                    result_files,
                    path,
                )
                future_to_dir[future] = path

            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_dir):
                path = future_to_dir[future]
                try:
                    success = future.result()
                    if success:
                        self.processed_directories.append(path)
                    else:
                        self.errors.append(f"Failed to process {path}")
                except Exception as e:
                    error_msg = f"Error processing {path}: {str(e)}"
                    print(error_msg)
                    self.errors.append(error_msg)

                    if not self.ignore_errors:
                        # Cancel remaining tasks
                        for f in future_to_dir:
                            f.cancel()
                        return False

                # Update progress if enabled
                self._report_progress()

        return True

    def _process_directory_safe(self, pessoa_dir, ano_dir, result_files, path):
        """Process a directory safely for parallel execution"""
        try:
            # Create output directories
            pessoa_output = self.output_dir / pessoa_dir.name
            ano_output = pessoa_output / ano_dir.name
            os.makedirs(ano_output, exist_ok=True)

            # Process the directory
            return self._process_directory(pessoa_dir, ano_dir, result_files)
        except Exception as e:
            if self.verbose:
                print(f"Error processing {path}: {str(e)}")
            if not self.ignore_errors:
                raise
            return False

    def _check_result_files(self, directory):
        """Check for result files in different formats"""
        result_files = {}

        # Get formats to process
        formats_to_check = self._get_formats_to_process()

        # Check for each format
        for format_name, extensions in self.valid_formats.items():
            if format_name in formats_to_check:
                # Check for each extension
                for ext in extensions:
                    # Try resultado files first
                    file_path = directory / f"resultado{ext}"
                    if file_path.exists():
                        result_files[format_name] = file_path
                        break

                    # Try other common names
                    for name in ["result", "data", "evaluation", "assessment"]:
                        file_path = directory / f"{name}{ext}"
                        if file_path.exists():
                            result_files[format_name] = file_path
                            break

        return result_files

    def _get_formats_to_process(self):
        """Get the list of formats to process based on selected_formats"""
        if self.selected_formats.lower() == "all":
            return list(self.valid_formats.keys())

        # Split by comma and clean up
        formats = [f.strip().lower() for f in self.selected_formats.split(",")]

        # Validate formats
        valid_formats = []
        for fmt in formats:
            if fmt in self.valid_formats:
                valid_formats.append(fmt)
            else:
                logging.warning(f"Invalid format: {fmt}")

        return valid_formats

    def _process_directory(self, pessoa_dir, ano_dir, result_files):
        """Process a specific directory"""
        # Get paths
        pessoa_name = pessoa_dir.name
        ano_name = ano_dir.name

        # Create output directory
        output_dir = self.output_dir / pessoa_name / ano_name
        os.makedirs(output_dir, exist_ok=True)

        # Log
        if self.verbose:
            print(f"Processing {pessoa_name}/{ano_name}")

        # Process each result file
        processed_data = {}
        for file_format, file_path in result_files.items():
            try:
                # Process file
                data = self._process_file(file_path, file_format)
                if data:
                    processed_data[file_format] = data
            except Exception as e:
                error_msg = f"Error processing {file_path}: {e}"
                if self.verbose:
                    print(error_msg)
                logging.error(error_msg)
                if not self.ignore_errors:
                    raise

        # Combine processed data
        combined_data = self._combine_data(processed_data)
        if not combined_data:
            error_msg = f"No valid data found in {pessoa_name}/{ano_name}"
            if self.verbose:
                print(error_msg)
            logging.error(error_msg)
            raise ValueError(error_msg)

        # Save the processed data to a JSON file for reference
        data_dir = self.output_dir / "data"
        data_dir.mkdir(exist_ok=True, parents=True)
        data_file = data_dir / f"{pessoa_name}_{ano_name}.json"

        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)

        if self.verbose:
            print(f"Saved processed data to {data_file}")

        # Generate reports
        self._generate_reports(combined_data, output_dir, pessoa_name, ano_name)

        # Generate markdown report if enabled
        if self.rich_markdown:
            try:
                markdown_file = self._generate_markdown_report(
                    pessoa_name, ano_name, combined_data, output_dir
                )
                if self.verbose and markdown_file:
                    print(f"Generated markdown report: {markdown_file}")
            except Exception as e:
                error_msg = f"Error generating markdown report: {e}"
                if self.verbose:
                    print(error_msg)
                logging.error(error_msg)
                if not self.ignore_errors:
                    raise

        # Generate visualizations if not skipped
        if not self.skip_viz:
            self._generate_visualizations(
                combined_data, output_dir, pessoa_name, ano_name
            )

        # Success
        if self.verbose:
            print(f"Successfully processed {pessoa_name}/{ano_name}")

        # Add to processed directories (thread-safe)
        self.processed_directories.append(f"{pessoa_name}/{ano_name}")

        return True

    def _generate_reports(self, data, output_dir, pessoa_name, ano_name):
        """Generate reports from processed data"""
        try:
            # Ensure output_dir is a Path object
            if isinstance(output_dir, str):
                output_dir = Path(output_dir)

            # Create reports directory
            reports_dir = output_dir / "reports"
            reports_dir.mkdir(exist_ok=True, parents=True)

            # Generate individual report
            individual_report = self._generate_individual_report(
                data, pessoa_name, ano_name
            )
            if individual_report:
                report_path = reports_dir / "individual_report.json"
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(individual_report, f, indent=2, ensure_ascii=False)

            # Generate summary report
            summary_report = self._generate_summary_report(data, pessoa_name, ano_name)
            if summary_report:
                report_path = reports_dir / "summary_report.json"
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(summary_report, f, indent=2, ensure_ascii=False)

            # Generate action plan
            action_plan = self._generate_action_plan(data, pessoa_name, ano_name)
            if action_plan:
                report_path = reports_dir / "action_plan.json"
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(action_plan, f, indent=2, ensure_ascii=False)

            # Generate benchmark report
            benchmark_report = self._generate_benchmark_report(
                data, pessoa_name, ano_name
            )
            if benchmark_report:
                report_path = reports_dir / "benchmark_report.json"
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(benchmark_report, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            logging.error(f"Error generating reports for {pessoa_name}/{ano_name}: {e}")
            if not self.ignore_errors:
                raise
            return False

    def _generate_visualizations(self, data, output_dir, pessoa_name, ano_name):
        """Generate visualizations from processed data"""
        # Create visualization directory
        viz_dir = output_dir / "visualizations"
        os.makedirs(viz_dir, exist_ok=True)

        try:
            # Generate radar chart
            radar_data = self._prepare_radar_data(data)
            if radar_data and "categories" in radar_data and "values" in radar_data:
                radar_path = viz_dir / "radar_chart.png"
                self._generate_radar_chart(
                    radar_data["categories"],
                    radar_data["values"],
                    f"{pessoa_name} - {ano_name} Radar Chart",
                    radar_path,
                )

            # Generate heatmap
            heatmap_data = self._prepare_heatmap_data(data)
            if heatmap_data and "data" in heatmap_data:
                heatmap_path = viz_dir / "heatmap.png"
                self._generate_heatmap(
                    heatmap_data["data"],
                    heatmap_data.get("x_labels"),
                    heatmap_data.get("y_labels"),
                    f"{pessoa_name} - {ano_name} Heatmap",
                    heatmap_path,
                )

            # Generate bar chart
            bar_data = self._prepare_bar_data(data)
            if bar_data and "categories" in bar_data and "values" in bar_data:
                bar_path = viz_dir / "bar_chart.png"
                self._generate_bar_chart(
                    bar_data["categories"],
                    bar_data["values"],
                    f"{pessoa_name} - {ano_name} Bar Chart",
                    bar_path,
                )

            return True
        except Exception as e:
            logging.error(
                f"Error generating visualizations for {pessoa_name}/{ano_name}: {e}"
            )
            if not self.ignore_errors:
                raise
            return False

    def _generate_individual_report(self, data, pessoa_name, ano_name):
        """Generate individual report"""
        # Basic implementation - should be extended with actual report logic
        report = {
            "pessoa": pessoa_name,
            "ano": ano_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "data": data,
        }

        return report

    def _generate_summary_report(self, data, pessoa_name, ano_name):
        """Generate summary report"""
        # Extract key metrics from data
        summary = {
            "pessoa": pessoa_name,
            "ano": ano_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "metrics": {},
        }

        # Extract metrics if available (example implementation)
        if isinstance(data, dict):
            # Extract competencies if available
            if "competencies" in data:
                competencies = data["competencies"]
                if isinstance(competencies, list):
                    # Calculate average score
                    scores = [c.get("score", 0) for c in competencies if "score" in c]
                    if scores:
                        summary["metrics"]["avg_competency_score"] = sum(scores) / len(
                            scores
                        )
                        summary["metrics"]["max_competency_score"] = max(scores)
                        summary["metrics"]["min_competency_score"] = min(scores)

            # Extract overall score if available
            if "overall_score" in data:
                summary["metrics"]["overall_score"] = data["overall_score"]

        return summary

    def _generate_action_plan(self, data, pessoa_name, ano_name):
        """Generate action plan"""
        # Basic implementation - should be extended with actual action plan logic
        action_plan = {
            "pessoa": pessoa_name,
            "ano": ano_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "actions": [],
        }

        # Generate actions based on data (example implementation)
        if isinstance(data, dict) and "competencies" in data:
            competencies = data["competencies"]
            if isinstance(competencies, list):
                # Find low-scoring competencies
                for comp in competencies:
                    if "score" in comp and comp["score"] < 3:  # Arbitrary threshold
                        action_plan["actions"].append(
                            {
                                "area": comp.get("name", "Unknown"),
                                "current_score": comp["score"],
                                "target_score": min(
                                    comp["score"] + 1, 5
                                ),  # Improve by 1 point
                                "suggested_actions": [
                                    f"Improve {comp.get('name', 'this area')} through training",
                                    f"Seek feedback on {comp.get('name', 'this area')}",
                                ],
                            }
                        )

        return action_plan

    def _generate_benchmark_report(self, data, pessoa_name, ano_name):
        """Generate benchmark report"""
        # This would typically compare against some reference data
        # For now, just return a placeholder
        return {
            "pessoa": pessoa_name,
            "ano": ano_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "benchmark_data": {
                "note": "Benchmark comparison would be implemented here",
            },
        }

    def _prepare_radar_data(self, data):
        """Prepare data for radar chart"""
        if not isinstance(data, dict):
            return None

        # Extract competencies if available
        if "competencies" in data and isinstance(data["competencies"], list):
            categories = []
            values = []

            for comp in data["competencies"]:
                if "name" in comp and "score" in comp:
                    categories.append(comp["name"])
                    values.append(comp["score"])

            if categories and values:
                return {
                    "categories": categories,
                    "values": values,
                }

        return None

    def _prepare_heatmap_data(self, data):
        """Prepare data for heatmap"""
        # This is a placeholder implementation
        # Real implementation would depend on the structure of your data
        return {
            "data": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],  # Example data
            "x_labels": ["X1", "X2", "X3"],
            "y_labels": ["Y1", "Y2", "Y3"],
        }

    def _prepare_bar_data(self, data):
        """Prepare data for bar chart"""
        if not isinstance(data, dict):
            return None

        # Extract competencies if available
        if "competencies" in data and isinstance(data["competencies"], list):
            categories = []
            values = []

            for comp in data["competencies"]:
                if "name" in comp and "score" in comp:
                    categories.append(comp["name"])
                    values.append(comp["score"])

            if categories and values:
                return {
                    "categories": categories,
                    "values": values,
                }

        return None

    def _generate_radar_chart(self, categories, values, title, output_path):
        """Generate radar chart using matplotlib"""
        try:
            # Import here to avoid dependencies if visualizations are skipped
            import matplotlib.pyplot as plt
            import numpy as np

            # Set up the angles for each category
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()

            # Close the plot (connect first and last point)
            values = values + [values[0]]
            angles = angles + [angles[0]]
            categories = categories + [categories[0]]

            # Create figure and polar axis
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

            # Draw the chart
            ax.plot(angles, values, "o-", linewidth=2)
            ax.fill(angles, values, alpha=0.25)

            # Set category labels
            ax.set_thetagrids(np.degrees(angles), categories)

            # Set chart title
            plt.title(title)

            # Save the chart
            plt.savefig(output_path)
            plt.close()

            return True
        except Exception as e:
            logging.error(f"Error generating radar chart: {e}")
            return False

    def _generate_heatmap(self, data, x_labels, y_labels, title, output_path):
        """Generate heatmap using matplotlib"""
        try:
            # Import here to avoid dependencies if visualizations are skipped
            import matplotlib.pyplot as plt
            import seaborn as sns

            # Create figure
            fig, ax = plt.subplots(figsize=(10, 8))

            # Create heatmap
            sns.heatmap(
                data,
                annot=True,
                cmap="YlGnBu",
                xticklabels=x_labels,
                yticklabels=y_labels,
                ax=ax,
            )

            # Set title
            plt.title(title)

            # Save the chart
            plt.savefig(output_path, bbox_inches="tight")
            plt.close()

            return True
        except Exception as e:
            logging.error(f"Error generating heatmap: {e}")
            return False

    def _generate_bar_chart(self, categories, values, title, output_path):
        """Generate bar chart using matplotlib"""
        try:
            # Import here to avoid dependencies if visualizations are skipped
            import matplotlib.pyplot as plt
            import numpy as np

            # Create figure
            fig, ax = plt.subplots(figsize=(12, 8))

            # Create bar chart
            y_pos = np.arange(len(categories))
            ax.bar(y_pos, values)

            # Set labels and title
            ax.set_xticks(y_pos)
            ax.set_xticklabels(categories, rotation=45, ha="right")
            ax.set_ylabel("Score")
            ax.set_title(title)

            # Adjust layout and save
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()

            return True
        except Exception as e:
            logging.error(f"Error generating bar chart: {e}")
            return False

    def _complete_processing(self):
        """Complete the processing and return status"""
        # Process team data
        if self.rich_markdown or not self.skip_dashboard:
            self._process_team_data()

        # Compress output if requested
        if self.zip:
            self._compress_output()

        # Check results
        if len(self.processed_directories) == 0:
            print("No directories were processed")
            return False

        return True

    def _process_team_data(self):
        """Process team data and generate team reports"""
        try:
            if self.verbose:
                print("Processing team data...")

            # Create team reports directory
            team_reports_dir = self.output_dir / "team_reports"
            team_analysis_dir = self.output_dir / "team_analysis"
            team_viz_dir = self.output_dir / "visualizations" / "teams"

            os.makedirs(team_reports_dir, exist_ok=True)
            os.makedirs(team_analysis_dir, exist_ok=True)
            os.makedirs(team_viz_dir, exist_ok=True)

            # Collect all people data
            people_data = {}
            team_data = {}

            # Find all processed people data
            for pessoa_dir in self.output_dir.iterdir():
                if not pessoa_dir.is_dir() or pessoa_dir.name in [
                    "team_reports",
                    "team_analysis",
                    "visualizations",
                    "consolidated",
                ]:
                    continue

                for ano_dir in pessoa_dir.iterdir():
                    if not ano_dir.is_dir():
                        continue

                    # Check for reports
                    reports_dir = ano_dir / "reports"
                    if not reports_dir.exists():
                        continue

                    # Look for evaluation reports
                    evaluation_files = list(reports_dir.glob("*_evaluation.json"))
                    profile_path = pessoa_dir / "perfil.json"

                    if evaluation_files and profile_path.exists():
                        pessoa_name = pessoa_dir.name
                        ano_name = ano_dir.name

                        # Read profile data to get team assignments
                        try:
                            with open(profile_path, "r", encoding="utf-8") as f:
                                profile_data = json.load(f)

                            # Get teams from profile
                            teams = profile_data.get("teams", [])
                            if not teams:
                                teams = [profile_data.get("team", "Unknown")]

                            if not isinstance(teams, list):
                                teams = [teams]

                            # Get most recent evaluation
                            evaluation_file = sorted(evaluation_files)[-1]
                            with open(evaluation_file, "r", encoding="utf-8") as f:
                                evaluation_data = json.load(f)

                            # Store data for each person
                            people_data[pessoa_name] = {
                                "ano": ano_name,
                                "profile": profile_data,
                                "evaluation": evaluation_data,
                                "teams": teams,
                            }

                            # Aggregate data by team
                            for team_name in teams:
                                if team_name == "Unknown" or not team_name:
                                    continue

                                if team_name not in team_data:
                                    team_data[team_name] = {
                                        "members": {},
                                        "competencias": {},
                                        "pilares": {},
                                        "strengths": [],
                                        "development_areas": [],
                                        "historical": {},
                                        "competencia_pilar_mapping": {},
                                    }

                                # Add member to team
                                competencias = evaluation_data.get("competencias", {})
                                pilares = evaluation_data.get("pilares", {})
                                score_geral = evaluation_data.get("score_geral", 0)

                                team_data[team_name]["members"][pessoa_name] = {
                                    "score_geral": score_geral,
                                    "competencias": competencias,
                                    "pilares": pilares,
                                }

                                # Update team competency and pillar scores
                                for comp_name, comp_value in competencias.items():
                                    # Get or initialize competency in team data
                                    if (
                                        comp_name
                                        not in team_data[team_name]["competencias"]
                                    ):
                                        team_data[team_name]["competencias"][
                                            comp_name
                                        ] = 0

                                    # Add to running sum (will average later)
                                    team_data[team_name]["competencias"][comp_name] += (
                                        comp_value
                                    )

                                    # Map competency to pillar if available
                                    if "competencia_pilar_mapping" in evaluation_data:
                                        pilar = evaluation_data[
                                            "competencia_pilar_mapping"
                                        ].get(comp_name)
                                        if pilar:
                                            team_data[team_name][
                                                "competencia_pilar_mapping"
                                            ][comp_name] = pilar

                                # Update team pillar scores
                                for pilar_name, pilar_value in pilares.items():
                                    if (
                                        pilar_name
                                        not in team_data[team_name]["pilares"]
                                    ):
                                        team_data[team_name]["pilares"][pilar_name] = 0

                                    team_data[team_name]["pilares"][pilar_name] += (
                                        pilar_value
                                    )

                        except Exception as e:
                            logging.error(
                                f"Error processing team data for {pessoa_name}/{ano_name}: {e}"
                            )
                            if not self.ignore_errors:
                                raise

            # Process team data to calculate averages and identify strengths/weaknesses
            if self.verbose:
                print(f"Processing data for {len(team_data)} teams")

            reports_generated = 0
            team_list = []

            for team_name, data in team_data.items():
                members = data["members"]
                num_members = len(members)

                if num_members == 0:
                    continue

                # Calculate average scores for competencies
                for comp_name in data["competencias"]:
                    data["competencias"][comp_name] /= num_members

                # Calculate average scores for pilares
                for pilar_name in data["pilares"]:
                    data["pilares"][pilar_name] /= num_members

                # Identify team strengths and development areas
                sorted_comps = sorted(
                    data["competencias"].items(), key=lambda x: x[1], reverse=True
                )
                data["strengths"] = sorted_comps[:5]  # Top 5 strengths
                data["development_areas"] = sorted_comps[-5:]  # Bottom 5 areas

                # Calculate overall team score
                team_score = (
                    sum(data["competencias"].values()) / len(data["competencias"])
                    if data["competencias"]
                    else 0
                )
                data["team_score"] = team_score

                # Generate team report
                if not self.skip_viz:
                    self._generate_team_report(team_name, data, team_reports_dir)
                    reports_generated += 1

                # Track team for dashboard
                team_data_entry = {
                    "name": team_name,
                    "score": team_score,
                    "members": num_members,
                    "report_path": f"../team_reports/{team_name}_team_report.md",
                }
                team_list.append(team_data_entry)

            # Save team list for dashboard
            teams_json_path = team_reports_dir / "team_list.json"
            with open(teams_json_path, "w", encoding="utf-8") as f:
                json.dump(team_list, f, indent=2)

            if self.verbose:
                print(f"Generated {reports_generated} team reports")

            return True

        except Exception as e:
            logging.error(f"Error processing team data: {e}")
            if not self.ignore_errors:
                raise
            return False

    def _generate_team_report(self, team_name, team_data, output_dir):
        """Generate a comprehensive team report with detailed analytics and visualizations"""
        try:
            # Get the team members' data
            members = team_data.get("members", {})
            overall_score = team_data.get("overall_score", 0)
            competencias = team_data.get("competencias", {})
            pilares = team_data.get("pilares", {})
            historical_data = team_data.get("historical_data", {})

            # Create visualization directory
            viz_dir = self.output_dir / "visualizations" / "teams" / team_name
            os.makedirs(viz_dir, exist_ok=True)

            # Generate radar chart for team competencies
            radar_path = None
            if competencias and not self.skip_viz:
                categories = list(competencias.keys())
                values = list(competencias.values())
                radar_path = viz_dir / "team_radar.png"
                self._generate_radar_chart(
                    categories,
                    values,
                    f"{team_name} Team - Competency Profile",
                    radar_path,
                )

            # Generate bar chart for team pillars
            pillar_path = None
            if pilares and not self.skip_viz:
                categories = list(pilares.keys())
                values = list(pilares.values())
                pillar_path = viz_dir / "team_pillar.png"
                self._generate_bar_chart(
                    categories,
                    values,
                    f"{team_name} Team - Pillar Analysis",
                    pillar_path,
                )

            # Generate trend chart for team if historical data available
            trend_path = None
            if historical_data and not self.skip_viz:
                trend_path = viz_dir / "team_trend.png"
                self._generate_trend_chart(
                    historical_data, f"{team_name} Team", trend_path
                )

            # Generate heatmap of team member competencies
            heatmap_path = None
            if members and not self.skip_viz:
                heatmap_path = viz_dir / "team_heatmap.png"
                self._generate_team_heatmap(members, heatmap_path)

            # Generate team distribution (box plot) of competencies
            dist_path = None
            if members and not self.skip_viz:
                dist_path = viz_dir / "team_distribution.png"
                self._generate_team_distribution(members, dist_path)

            # Create the markdown file
            report_path = output_dir / f"{team_name}_team_report.md"

            with open(report_path, "w", encoding="utf-8") as f:
                # Title and overall score
                f.write(f"# {team_name} Team - Performance Analysis\n\n")
                f.write(f"**Team Overall Score:** {overall_score:.2f}/5.0\n\n")

                # Team size
                f.write(f"**Team Size:** {len(members)} members\n\n")

                # Team summary
                f.write("## Executive Summary\n\n")

                # Determine team performance level
                if overall_score >= 4.5:
                    performance_level = "Outstanding"
                    summary = f"The {team_name} team demonstrates exceptional performance across most competencies, with multiple team members showing mastery in key areas. The team's overall score places it in the top tier of performance."
                elif overall_score >= 4.0:
                    performance_level = "Excellent"
                    summary = f"The {team_name} team shows strong performance across competencies with notable strengths. The team evaluation indicates a high level of capability and effective collaboration."
                elif overall_score >= 3.5:
                    performance_level = "Very Good"
                    summary = f"The {team_name} team demonstrates above-average performance in most areas, with some standout competencies and opportunities for targeted development."
                elif overall_score >= 3.0:
                    performance_level = "Good"
                    summary = f"The {team_name} team performs well in several areas with a solid foundation of competencies. Targeted development in specific areas could enhance overall team performance."
                elif overall_score >= 2.5:
                    performance_level = "Satisfactory"
                    summary = f"The {team_name} team meets basic expectations in most areas, with clear opportunities for improvement in several competencies."
                else:
                    performance_level = "Needs Improvement"
                    summary = f"The {team_name} team requires significant development across multiple competencies. A structured team development plan is recommended to address key areas."

                f.write(f"**Team Performance Level:** {performance_level}\n\n")
                f.write(f"{summary}\n\n")

                # Add radar chart if available
                if radar_path:
                    relative_path = os.path.relpath(radar_path, output_dir.parent)
                    f.write("## Team Competency Profile\n\n")
                    f.write(f"![Team Competency Profile](../{relative_path})\n\n")

                # Add pillar chart if available
                if pillar_path:
                    relative_path = os.path.relpath(pillar_path, output_dir.parent)
                    f.write("## Team Pillar Analysis\n\n")
                    f.write(f"![Team Pillar Analysis](../{relative_path})\n\n")

                # Add trend chart if available
                if trend_path:
                    relative_path = os.path.relpath(trend_path, output_dir.parent)
                    f.write("## Team Performance Trends\n\n")
                    f.write(f"![Team Performance Trends](../{relative_path})\n\n")

                    # Add trend analysis
                    latest_year = max(historical_data.keys())
                    previous_year = max(
                        [y for y in historical_data.keys() if y != latest_year],
                        default=None,
                    )

                    if previous_year:
                        latest_score = historical_data[latest_year]
                        previous_score = historical_data[previous_year]
                        change = latest_score - previous_score
                        change_pct = (
                            (change / previous_score) * 100 if previous_score else 0
                        )

                        f.write("### Year-over-Year Analysis\n\n")
                        f.write(f"**{latest_year} Score:** {latest_score:.2f}\n\n")
                        f.write(f"**{previous_year} Score:** {previous_score:.2f}\n\n")

                        if change > 0:
                            f.write(
                                f"**Change:** +{change:.2f} (+{change_pct:.1f}%)\n\n"
                            )
                            f.write(
                                f"The {team_name} team has shown improvement compared to the previous evaluation period. This positive trend indicates effective team development activities and growing team maturity.\n\n"
                            )
                        elif change < 0:
                            f.write(f"**Change:** {change:.2f} ({change_pct:.1f}%)\n\n")
                            f.write(
                                f"The {team_name} team has experienced a decline compared to the previous evaluation period. This may indicate areas requiring focused attention or team dynamics issues that need addressing.\n\n"
                            )
                        else:
                            f.write("**Change:** 0.00 (0.0%)\n\n")
                            f.write(
                                f"The {team_name} team's performance has remained consistent compared to the previous evaluation period.\n\n"
                            )

                # Add team heatmap if available
                if heatmap_path:
                    relative_path = os.path.relpath(heatmap_path, output_dir.parent)
                    f.write("## Team Competency Heatmap\n\n")
                    f.write(f"![Team Competency Heatmap](../{relative_path})\n\n")
                    f.write(
                        "The heatmap above shows the distribution of competency scores across team members, highlighting areas of collective strength and opportunity.\n\n"
                    )

                # Add team distribution if available
                if dist_path:
                    relative_path = os.path.relpath(dist_path, output_dir.parent)
                    f.write("## Competency Distribution\n\n")
                    f.write(f"![Team Competency Distribution](../{relative_path})\n\n")
                    f.write(
                        "This distribution analysis shows the spread of scores within each competency, highlighting the team's consistency or variability.\n\n"
                    )

                # Detailed team competency analysis
                f.write("## Team Competency Analysis\n\n")

                if competencias:
                    # Sort competencies by score
                    sorted_competencias = sorted(
                        competencias.items(), key=lambda x: x[1], reverse=True
                    )

                    # Create a table of all competencies
                    f.write("### Team Competency Scores\n\n")
                    f.write("| Competency | Team Score | Level | Variability |\n")
                    f.write("|------------|------------|-------|-------------|\n")

                    for comp_name, comp_score in sorted_competencias:
                        # Determine competency level
                        if comp_score >= 4.5:
                            level = "Mastery"
                        elif comp_score >= 4.0:
                            level = "Advanced"
                        elif comp_score >= 3.0:
                            level = "Proficient"
                        elif comp_score >= 2.0:
                            level = "Developing"
                        else:
                            level = "Basic"

                        # Calculate variability across members for this competency
                        member_scores = [
                            m.get("competencias", {}).get(comp_name, 0)
                            for m in members.values()
                        ]
                        if member_scores:
                            variability = (
                                np.std(member_scores) if len(member_scores) > 1 else 0
                            )
                            if variability < 0.5:
                                var_level = "Low"
                            elif variability < 1.0:
                                var_level = "Moderate"
                            else:
                                var_level = "High"
                        else:
                            var_level = "N/A"

                        f.write(
                            f"| {comp_name} | {comp_score:.2f} | {level} | {var_level} |\n"
                        )

                    f.write("\n")

                    # Top 3 team strengths
                    f.write("### Key Team Strengths\n\n")
                    top_strengths = sorted_competencias[:3]

                    for i, (comp_name, comp_score) in enumerate(top_strengths, 1):
                        f.write(f"**{i}. {comp_name} ({comp_score:.2f})**\n\n")

                        # Calculate member distribution for this strength
                        member_scores = [
                            m.get("competencias", {}).get(comp_name, 0)
                            for m in members.values()
                        ]
                        high_performers = sum(1 for s in member_scores if s >= 4.0)
                        high_pct = (
                            (high_performers / len(member_scores)) * 100
                            if member_scores
                            else 0
                        )

                        if comp_score >= 4.5:
                            f.write(
                                f"The team demonstrates exceptional capability in {comp_name}. "
                            )
                        elif comp_score >= 4.0:
                            f.write(
                                f"The team shows strong proficiency in {comp_name}. "
                            )
                        else:
                            f.write(f"The team performs above average in {comp_name}. ")

                        f.write(
                            f"{high_performers} team members ({high_pct:.0f}%) show advanced or mastery level in this area, making it a significant collective strength.\n\n"
                        )

                    # Development areas (bottom 3)
                    f.write("### Team Development Areas\n\n")
                    development_areas = sorted_competencias[-3:]
                    development_areas.reverse()  # Show lowest first

                    for i, (comp_name, comp_score) in enumerate(development_areas, 1):
                        f.write(f"**{i}. {comp_name} ({comp_score:.2f})**\n\n")

                        # Calculate member distribution for this gap
                        member_scores = [
                            m.get("competencias", {}).get(comp_name, 0)
                            for m in members.values()
                        ]
                        low_performers = sum(1 for s in member_scores if s < 3.0)
                        low_pct = (
                            (low_performers / len(member_scores)) * 100
                            if member_scores
                            else 0
                        )

                        if comp_score < 2.0:
                            f.write(
                                f"The team requires significant development in {comp_name}. "
                            )
                        elif comp_score < 3.0:
                            f.write(
                                f"The team shows developing capability in {comp_name}. "
                            )
                        else:
                            f.write(
                                f"The team demonstrates moderate proficiency in {comp_name}. "
                            )

                        f.write(
                            f"{low_performers} team members ({low_pct:.0f}%) score below proficient level in this area, suggesting a need for targeted team development.\n\n"
                        )

                # Team member analysis
                f.write("## Team Member Analysis\n\n")

                if members:
                    # Sort members by overall score
                    sorted_members = sorted(
                        [
                            (name, data.get("overall_score", 0))
                            for name, data in members.items()
                        ],
                        key=lambda x: x[1],
                        reverse=True,
                    )

                    # Create member overview table
                    f.write("### Member Performance Overview\n\n")
                    f.write(
                        "| Team Member | Overall Score | Performance Level | Key Strength |\n"
                    )
                    f.write(
                        "|-------------|---------------|-------------------|-------------|\n"
                    )

                    for member_name, score in sorted_members:
                        # Determine performance level
                        if score >= 4.5:
                            level = "Outstanding"
                        elif score >= 4.0:
                            level = "Excellent"
                        elif score >= 3.5:
                            level = "Very Good"
                        elif score >= 3.0:
                            level = "Good"
                        elif score >= 2.5:
                            level = "Satisfactory"
                        else:
                            level = "Needs Improvement"

                        # Find member's top competency
                        member_competencias = members[member_name].get(
                            "competencias", {}
                        )
                        top_competency = (
                            max(member_competencias.items(), key=lambda x: x[1])[0]
                            if member_competencias
                            else "N/A"
                        )

                        f.write(
                            f"| {member_name} | {score:.2f} | {level} | {top_competency} |\n"
                        )

                    # Team balance analysis
                    f.write("\n### Team Balance Analysis\n\n")

                    # Calculate distribution of performance levels
                    performance_distribution = {
                        "Outstanding": sum(
                            1 for _, score in sorted_members if score >= 4.5
                        ),
                        "Excellent": sum(
                            1 for _, score in sorted_members if 4.0 <= score < 4.5
                        ),
                        "Very Good": sum(
                            1 for _, score in sorted_members if 3.5 <= score < 4.0
                        ),
                        "Good": sum(
                            1 for _, score in sorted_members if 3.0 <= score < 3.5
                        ),
                        "Satisfactory": sum(
                            1 for _, score in sorted_members if 2.5 <= score < 3.0
                        ),
                        "Needs Improvement": sum(
                            1 for _, score in sorted_members if score < 2.5
                        ),
                    }

                    # Identify highest percentage performance level
                    max_level = max(
                        performance_distribution.items(), key=lambda x: x[1]
                    )
                    max_level_pct = (max_level[1] / len(sorted_members)) * 100

                    f.write(
                        f"The team has a {max_level_pct:.0f}% concentration of members at the '{max_level[0]}' performance level.\n\n"
                    )

                    # Identify diversity of strengths
                    all_top_comps = []
                    for member_name, _ in sorted_members:
                        member_competencias = members[member_name].get(
                            "competencias", {}
                        )
                        if member_competencias:
                            top_comp = max(
                                member_competencias.items(), key=lambda x: x[1]
                            )[0]
                            all_top_comps.append(top_comp)

                    unique_top_comps = set(all_top_comps)
                    strength_diversity = (
                        (len(unique_top_comps) / len(competencias)) * 100
                        if competencias
                        else 0
                    )

                    if strength_diversity >= 70:
                        f.write(
                            "The team shows excellent diversity in top strengths, with members excelling across a wide range of competencies. This provides good coverage of different skill areas.\n\n"
                        )
                    elif strength_diversity >= 40:
                        f.write(
                            "The team shows moderate diversity in top strengths, with some concentration in particular competency areas.\n\n"
                        )
                    else:
                        f.write(
                            "The team shows limited diversity in top strengths, with high concentration in a few competency areas. This may indicate gaps in certain competencies.\n\n"
                        )

                    # Calculate score distribution statistics
                    scores = [score for _, score in sorted_members]
                    score_range = max(scores) - min(scores) if scores else 0

                    if score_range < 0.5:
                        f.write(
                            "The team shows very homogeneous performance levels, with minimal variation between highest and lowest performers.\n\n"
                        )
                    elif score_range < 1.0:
                        f.write(
                            "The team shows moderate variation in performance levels, with some differences between highest and lowest performers.\n\n"
                        )
                    else:
                        f.write(
                            "The team shows significant variation in performance levels, with substantial differences between highest and lowest performers.\n\n"
                        )

                # Recommendations for team development
                f.write("## Team Development Recommendations\n\n")

                # General recommendations based on team profile
                f.write("### Strategic Recommendations\n\n")

                # Top team gaps for development
                if development_areas:
                    f.write("#### Focus Areas for Team Development\n\n")
                    for comp_name, score in development_areas:
                        f.write(
                            f"- **{comp_name}**: Implement team training, structured practice sessions, or bring in external expertise\n"
                        )
                    f.write("\n")

                # Recommendations for leveraging team strengths
                if top_strengths:
                    f.write("#### Leveraging Team Strengths\n\n")
                    for comp_name, score in top_strengths:
                        f.write(
                            f"- **{comp_name}**: Assign team members with high scores to mentor others, lead initiatives in this area, or represent the team in cross-functional projects\n"
                        )
                    f.write("\n")

                # Team dynamics recommendations
                f.write("### Team Dynamics Recommendations\n\n")

                if (
                    performance_distribution.get("Outstanding", 0)
                    + performance_distribution.get("Excellent", 0)
                    > len(members) / 2
                ):
                    f.write(
                        "- **High-Performing Team**: Focus on challenging team goals, innovation initiatives, and cross-training to maintain engagement\n"
                    )
                    f.write(
                        "- Consider giving team members opportunities to mentor or lead initiatives outside the team\n"
                    )
                elif (
                    performance_distribution.get("Needs Improvement", 0)
                    > len(members) / 3
                ):
                    f.write(
                        "- **Development-Focused Team**: Implement structured training programs, clear expectations, and regular feedback sessions\n"
                    )
                    f.write(
                        "- Consider pairing team members with mentors from other teams to accelerate development\n"
                    )
                else:
                    f.write(
                        "- **Balanced Team**: Focus on targeted development while leveraging existing strengths\n"
                    )
                    f.write(
                        "- Create opportunities for peer learning and knowledge sharing within the team\n"
                    )

                f.write("\n")

                # Specific recommendations based on variability
                if score_range >= 1.0:
                    f.write(
                        "- **Address Performance Variability**: High variation in performance levels suggests a need for more standardized processes, knowledge transfer, or adjustments in work distribution\n"
                    )

                if strength_diversity < 40:
                    f.write(
                        "- **Expand Competency Coverage**: The limited diversity in strengths suggests a need to develop broader capabilities across the team\n"
                    )

                # Action plan for team development
                f.write("\n### Team Action Plan\n\n")
                f.write(
                    "1. **Review results with the team** - Share the analysis and gather input\n"
                )
                f.write(
                    "2. **Prioritize development areas** - Focus on 1-2 key competencies for team development\n"
                )
                f.write(
                    "3. **Create specific team learning initiatives** - Workshops, projects, or other learning opportunities\n"
                )
                f.write(
                    "4. **Implement peer coaching** - Pair high performers with those developing in specific competencies\n"
                )
                f.write(
                    "5. **Regular check-ins** - Schedule quarterly reviews of team development progress\n"
                )

                # Date of report
                f.write(f"\n\n*Generated on {datetime.now().strftime('%Y-%m-%d')}*\n")

            return report_path

        except Exception as e:
            logging.error(f"Error generating team report for {team_name}: {e}")
            if not self.ignore_errors:
                raise
            return None

    def _generate_markdown_report(self, pessoa_name, ano_name, data, output_dir):
        """Generate a markdown report for a person/year combination.

        Args:
            pessoa_name: Name of the person
            ano_name: Year/period
            data: Processed data
            output_dir: Output directory

        Returns:
            Path to the generated markdown file
        """
        try:
            # Create markdown directory
            md_dir = self.output_dir / "markdown"
            md_dir.mkdir(exist_ok=True, parents=True)

            # Create markdown file
            file_path = md_dir / f"{pessoa_name}_{ano_name}_report.md"

            with open(file_path, "w", encoding="utf-8") as f:
                # Header
                f.write(f"# Performance Report: {pessoa_name} - {ano_name}\n\n")

                # Timestamp
                from datetime import datetime

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"*Generated on: {timestamp}*\n\n")

                # Summary section
                f.write("## Summary\n\n")
                f.write("This is an automatically generated performance report.\n\n")

                # Data summary
                if isinstance(data, dict):
                    # Extract key metrics if available
                    if "data" in data and isinstance(data["data"], dict):
                        if "conceito_ciclo_filho_descricao" in data["data"]:
                            f.write(
                                f"**Conceito:** {data['data']['conceito_ciclo_filho_descricao']}\n\n"
                            )

                        # Add direcionadores if available
                        if "direcionadores" in data["data"] and isinstance(
                            data["data"]["direcionadores"], list
                        ):
                            f.write("## Direcionadores\n\n")
                            for idx, direcionador in enumerate(
                                data["data"]["direcionadores"], 1
                            ):
                                if (
                                    isinstance(direcionador, dict)
                                    and "direcionador" in direcionador
                                ):
                                    f.write(
                                        f"### {idx}. {direcionador['direcionador']}\n\n"
                                    )

                                    # Add pergunta final if available
                                    if "pergunta_final" in direcionador:
                                        f.write(
                                            f"**Pergunta:** {direcionador['pergunta_final']}\n\n"
                                        )

                                    # Add comportamentos if available
                                    if "comportamentos" in direcionador and isinstance(
                                        direcionador["comportamentos"], list
                                    ):
                                        f.write("#### Comportamentos\n\n")
                                        for comp_idx, comportamento in enumerate(
                                            direcionador["comportamentos"], 1
                                        ):
                                            if (
                                                isinstance(comportamento, dict)
                                                and "comportamento" in comportamento
                                            ):
                                                f.write(
                                                    f"- {comportamento['comportamento']}\n"
                                                )
                                        f.write("\n")

                # Placeholder for additional sections
                f.write("## Additional Information\n\n")
                f.write(
                    "For more detailed analysis, please refer to the full report.\n\n"
                )

                # Footer
                f.write("---\n")
                f.write(
                    "*This report was generated by the People Analytics platform.*\n"
                )

            if self.verbose:
                print(f"Generated markdown report: {file_path}")

            return file_path

        except Exception as e:
            if self.verbose:
                print(f"Error generating markdown report: {e}")
            raise

    def _generate_talent_development_reports(self):
        """Generate talent development reports.

        This method uses the talent development modules to generate advanced reports.
        Returns:
            True if successful, False otherwise.
        """
        try:
            from peopleanalytics.data_pipeline import DataPipeline
            from peopleanalytics.talent_development import (
                CareerSimulator,
                DynamicMatrix9Box,
                InfluenceNetwork,
            )

            # Initialize reports directory
            talent_reports_dir = (
                Path(self.talent_report_dir)
                if hasattr(self, "talent_report_dir")
                else Path(self.output_dir) / "talent_reports"
            )
            talent_reports_dir.mkdir(exist_ok=True, parents=True)

            # Initialize data pipeline
            data_pipeline = DataPipeline(str(self.data_dir))

            # Process each directory for people data
            processed_people = set()
            for directory in self.processed_directories:
                try:
                    # Extract person and year
                    parts = directory.split("/")
                    if len(parts) >= 2:
                        person_name = parts[0]
                        if person_name not in processed_people:
                            processed_people.add(person_name)

                            # Generate 9-Box Matrix reports
                            if hasattr(self, "use_9box") and self.use_9box:
                                try:
                                    matrix = DynamicMatrix9Box(data_pipeline)
                                    # Generate visualization and report
                                    report_dir = talent_reports_dir / "matrix_9box"
                                    report_dir.mkdir(exist_ok=True, parents=True)

                                    # Use visualize_matrix method instead of visualize
                                    viz_path = (
                                        report_dir / f"{person_name}_matrix_9box.png"
                                    )
                                    matrix.visualize_matrix(
                                        person_id=person_name, output_path=viz_path
                                    )

                                    # Generate comprehensive report
                                    matrix.generate_report(
                                        person_id=person_name, output_path=report_dir
                                    )

                                    if self.verbose:
                                        print(
                                            f"Generated 9-Box Matrix report for {person_name}"
                                        )
                                except Exception as e:
                                    if self.verbose:
                                        print(
                                            f"Error generating 9-Box Matrix report for {person_name}: {e}"
                                        )
                                    if not self.ignore_errors:
                                        raise

                            # Generate Career Simulation reports
                            if hasattr(self, "use_career_sim") and self.use_career_sim:
                                try:
                                    # Create career sim directory
                                    sim_dir = talent_reports_dir / "career_sim"
                                    sim_dir.mkdir(exist_ok=True, parents=True)

                                    # Create a placeholder report for now since we don't have the position data
                                    report_path = (
                                        sim_dir / f"{person_name}_career_sim_report.md"
                                    )
                                    with open(report_path, "w") as f:
                                        f.write(
                                            f"# Career Simulation Report for {person_name}\n\n"
                                        )
                                        f.write(
                                            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                                        )
                                        f.write("## Career Path Simulation\n\n")
                                        f.write(
                                            "This is a placeholder for the career simulation report. "
                                        )
                                        f.write(
                                            "In a production environment, this would contain:\n\n"
                                        )
                                        f.write(
                                            "- Projected career paths based on skills and interests\n"
                                        )
                                        f.write(
                                            "- Recommended skill development areas\n"
                                        )
                                        f.write(
                                            "- Timeline estimates for career progression\n"
                                        )
                                        f.write(
                                            "- Alternative career tracks that match skill profile\n\n"
                                        )
                                        f.write("## Next Steps\n\n")
                                        f.write(
                                            "1. Discuss career goals with your manager\n"
                                        )
                                        f.write(
                                            "2. Focus on developing key skills identified in your evaluation\n"
                                        )
                                        f.write(
                                            "3. Consider training opportunities in adjacent skill areas\n"
                                        )

                                    if self.verbose:
                                        print(
                                            f"Created placeholder Career Simulation report for {person_name}"
                                        )
                                except Exception as e:
                                    if self.verbose:
                                        print(
                                            f"Error generating Career Simulation report for {person_name}: {e}"
                                        )
                                    if not self.ignore_errors:
                                        raise

                            # Generate Influence Network reports
                            if hasattr(self, "use_network") and self.use_network:
                                try:
                                    # Create network directory
                                    net_dir = talent_reports_dir / "influence_network"
                                    net_dir.mkdir(exist_ok=True, parents=True)

                                    # Create a placeholder report for now
                                    report_path = (
                                        net_dir / f"{person_name}_network_report.md"
                                    )
                                    with open(report_path, "w") as f:
                                        f.write(
                                            f"# Influence Network Analysis for {person_name}\n\n"
                                        )
                                        f.write(
                                            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                                        )
                                        f.write("## Network Impact Summary\n\n")
                                        f.write(
                                            "This is a placeholder for the influence network analysis. "
                                        )
                                        f.write(
                                            "In a production environment, this would contain:\n\n"
                                        )
                                        f.write(
                                            "- Analysis of your impact on other team members\n"
                                        )
                                        f.write(
                                            "- Visualization of knowledge flow and influence patterns\n"
                                        )
                                        f.write("- Key collaborative relationships\n")
                                        f.write("- Social capital assessment\n\n")
                                        f.write("## Network Metrics\n\n")
                                        f.write("| Metric | Value | Percentile |\n")
                                        f.write("|--------|-------|------------|\n")
                                        f.write("| Influence Reach | -- | -- |\n")
                                        f.write("| Knowledge Impact | -- | -- |\n")
                                        f.write("| Collaboration Score | -- | -- |\n")
                                        f.write("| Network Centrality | -- | -- |\n\n")
                                        f.write("## Recommendations\n\n")
                                        f.write(
                                            "1. Expand your cross-functional collaborations\n"
                                        )
                                        f.write(
                                            "2. Share knowledge through documentation and mentoring\n"
                                        )
                                        f.write(
                                            "3. Engage with broader organizational initiatives\n"
                                        )

                                    if self.verbose:
                                        print(
                                            f"Created placeholder Influence Network report for {person_name}"
                                        )
                                except Exception as e:
                                    if self.verbose:
                                        print(
                                            f"Error generating Influence Network report for {person_name}: {e}"
                                        )
                                    if not self.ignore_errors:
                                        raise

                except Exception as e:
                    if self.verbose:
                        print(
                            f"Error processing talent reports for directory {directory}: {e}"
                        )
                    if not self.ignore_errors:
                        raise

            return True
        except ImportError as e:
            if self.verbose:
                print(f"Talent development modules not available: {e}")
            return False
        except Exception as e:
            if self.verbose:
                print(f"Error generating talent development reports: {e}")
            if not self.ignore_errors:
                raise
            return False

    def _generate_analysis_reports(self) -> bool:
        """Generate peer group and year-over-year analysis reports.

        This method analyzes evaluation data to generate comparison reports
        against peer groups and across multiple years.

        Returns:
            True if successful, False otherwise
        """
        try:
            from peopleanalytics.domain.peer_analysis import PeerGroupAnalysis
            from peopleanalytics.domain.skill_base import SkillMatrix

            # Create analysis directories
            analysis_dir = Path(self.analysis_output_dir)
            peer_dir = analysis_dir / "peer_comparison"
            yoy_dir = analysis_dir / "year_over_year"

            os.makedirs(peer_dir, exist_ok=True)
            os.makedirs(yoy_dir, exist_ok=True)

            # Initialize the analyzer
            analyzer = PeerGroupAnalysis()

            # Find all processed people and their data
            all_people_data = self._collect_processed_people_data()

            if not all_people_data:
                print("No processed data found for analysis")
                return False

            # Process each person
            for person_name, person_data in all_people_data.items():
                try:
                    # Skip if no years data available
                    if not person_data["years"]:
                        continue

                    # Extract the skills data
                    skills_by_year = person_data["skills_by_year"]
                    peer_skills_by_year = person_data["peer_skills_by_year"]
                    skill_categories = person_data.get("skill_categories", {})

                    # Generate peer group comparison for the most recent year
                    latest_year = max(skills_by_year.keys())

                    if self.peer_analysis and latest_year in skills_by_year:
                        person_scores = skills_by_year[latest_year]
                        peer_scores = peer_skills_by_year.get(latest_year, {})

                        if person_scores and peer_scores:
                            comparison_results = analyzer.compare_with_peer_group(
                                person_scores, peer_scores, skill_categories
                            )

                            # Generate report
                            report_file = analyzer.generate_peer_comparison_report(
                                person_name,
                                latest_year,
                                comparison_results,
                                str(peer_dir),
                            )

                            if self.verbose:
                                print(
                                    f"Generated peer comparison report for {person_name}"
                                )

                    # Generate year-over-year analysis if we have multiple years
                    if self.yoy_analysis and len(skills_by_year) > 1:
                        yoy_results = analyzer.analyze_year_over_year(
                            skills_by_year, peer_skills_by_year, skill_categories
                        )

                        # Generate report
                        report_file = analyzer.generate_year_over_year_report(
                            person_name, yoy_results, str(yoy_dir)
                        )

                        if self.verbose:
                            print(
                                f"Generated year-over-year analysis for {person_name}"
                            )

                except Exception as e:
                    if self.verbose:
                        print(f"Error generating analysis for {person_name}: {e}")
                    if not self.ignore_errors:
                        raise

            return True

        except ImportError as e:
            if self.verbose:
                print(f"Analysis modules not available: {e}")
            return False
        except Exception as e:
            if self.verbose:
                print(f"Error generating analysis reports: {e}")
            if not self.ignore_errors:
                raise
            return False

    def _collect_processed_people_data(self):
        """Collect processed data for all people.

        Returns:
            Dictionary mapping person names to their data across years
        """
        all_people_data = {}
        data_dir = self.output_dir / "data"

        # Skip if data directory doesn't exist
        if not data_dir.exists():
            return all_people_data

        # Process all JSON files in the data directory
        for data_file in data_dir.glob("*.json"):
            try:
                # Extract person and year from filename (format: person_year.json)
                filename = data_file.stem
                if "_" not in filename:
                    continue

                parts = filename.split("_")
                person_name = "_".join(parts[:-1])  # Handle names with underscores
                year = parts[-1]

                # Read data file
                with open(data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Skip if not a valid data file
                if not isinstance(data, dict):
                    continue

                # Initialize person data if first encounter
                if person_name not in all_people_data:
                    all_people_data[person_name] = {
                        "years": [],
                        "skills_by_year": {},
                        "peer_skills_by_year": {},
                        "skill_categories": {},
                    }

                # Add year to the list
                all_people_data[person_name]["years"].append(year)

                # Extract skill scores
                skills = {}

                # Extract competencias
                if "competencias" in data and isinstance(data["competencias"], dict):
                    for skill, score in data["competencias"].items():
                        skills[skill] = float(score)

                        # Extract skill category from pilares if available
                        if "categorias" in data and skill in data["categorias"]:
                            all_people_data[person_name]["skill_categories"][skill] = (
                                data["categorias"][skill]
                            )
                        elif "pilares" in data and isinstance(data["pilares"], dict):
                            # Try to infer category from pilares
                            # This is a placeholder; real implementation would need to map
                            # skills to their categories more accurately
                            if "técnico" in data["pilares"] and skill in [
                                "Python",
                                "SQL",
                                "Java",
                                "JavaScript",
                                "DevOps",
                                "Data Analysis",
                            ]:
                                all_people_data[person_name]["skill_categories"][
                                    skill
                                ] = "technical"
                            elif "comportamental" in data["pilares"] and skill in [
                                "Communication",
                                "Teamwork",
                                "Problem Solving",
                                "Creativity",
                            ]:
                                all_people_data[person_name]["skill_categories"][
                                    skill
                                ] = "behavioral"
                            elif "liderança" in data["pilares"] and skill in [
                                "Leadership",
                                "Strategy",
                                "Mentoring",
                                "Decision Making",
                            ]:
                                all_people_data[person_name]["skill_categories"][
                                    skill
                                ] = "leadership"

                # Store skills for this year
                all_people_data[person_name]["skills_by_year"][year] = skills

                # Create placeholder for peer group data (will be populated later)
                if year not in all_people_data[person_name]["peer_skills_by_year"]:
                    all_people_data[person_name]["peer_skills_by_year"][year] = {}

            except Exception as e:
                if self.verbose:
                    print(f"Error processing {data_file}: {e}")
                if not self.ignore_errors:
                    raise

        # After collecting all data, populate peer group information
        for person_name, person_data in all_people_data.items():
            for year in person_data["years"]:
                # Get all other people with data for this year
                peer_data = {}

                for peer_name, peer_info in all_people_data.items():
                    # Skip self
                    if peer_name == person_name:
                        continue

                    # Skip peers without data for this year
                    if year not in peer_info["skills_by_year"]:
                        continue

                    # Add peer's skills data
                    peer_skills = peer_info["skills_by_year"][year]
                    if peer_skills:
                        peer_data[peer_name] = peer_skills

                # Store peer data for this year
                person_data["peer_skills_by_year"][year] = peer_data

        return all_people_data
