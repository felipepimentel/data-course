"""
Sync and documentation commands for People Analytics CLI.

This module contains commands for data synchronization and documentation generation.
"""

import argparse
import json
import logging
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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

        # Execute
        logger.info("Starting sync command execution")
        return self.sync.execute()


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

    def execute(self):
        """Execute the sync command"""

        print("People Analytics Data Processor")
        print("===============================")
        print(f"Data path: {self.data_dir}")
        print(f"Output path: {self.output_dir}")

        if self.force:
            print("Forcing reprocessing of all files")

        if self.verbose:
            print(f"Formats: {self.selected_formats}")

            if self.pessoa_filter:
                print(f"Filtering by pessoa: {self.pessoa_filter}")
            if self.ano_filter:
                print(f"Filtering by ano: {self.ano_filter}")

            print(f"Ignore errors: {self.ignore_errors}")
            print(f"Skip visualizations: {self.skip_viz}")
            print(f"Compress results: {self.zip}")
            print(f"Skip dashboard: {self.skip_dashboard}")
            print(f"Export to Excel: {self.export_excel}")
            print(f"Parallel processing: {self.parallel}")
            print(f"Rich markdown reports: {self.rich_markdown}")

        print("Expected data structure: <pessoa>/<ano>/resultado.json")
        print(f"Processing started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("===============================")

        # Ensure directories exist
        self._ensure_directories()

        # Set progress params
        self._reset_progress()

        # Process the pessoa/ano structure and get directories to process
        valid_directories = self._process_pessoa_ano_structure()

        # Check processed directories
        if not valid_directories:
            if not self.ignore_errors:
                print("No directories to process")
                return 1
            else:
                return 0

        # Process Directories
        start_time = time.time()

        if self.parallel:
            # Process in parallel
            self._process_directories_parallel(valid_directories)
        else:
            # Process sequentially
            self._process_directories_sequential(valid_directories)

        # Complete processing
        if not self._complete_processing():
            return 1

        # Consolidate data
        self._consolidate_data()

        # Calculate and display statistics
        elapsed_time = time.time() - start_time
        if elapsed_time > 0:
            directories_per_second = len(self.processed_directories) / elapsed_time
        else:
            directories_per_second = 0  # Avoid division by zero

        print("===============================")
        print(f"Processing completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(
            f"Processed {len(self.processed_directories)} directories in {elapsed_time:.2f} seconds ({directories_per_second:.2f} directories/second)"
        )

        if self.verbose and self.errors:
            print(f"Encountered {len(self.errors)} errors during processing")

        print(f"Output available at {self.output_dir}")
        if self.export_excel:
            print(f"Excel report generated at {self.output_dir}/consolidated/")
        if not self.skip_dashboard:
            print(
                f"Dashboard available at {self.output_dir}/consolidated/dashboard.html"
            )

        return 0

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
            logging.error(f"Error generating team report: {e}")
            if not self.ignore_errors:
                raise
            return None

    def _generate_team_heatmap(self, members, output_path):
        """Generate a heatmap visualization of team member competencies"""
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns

            # Extract member names and competency data
            member_names = list(members.keys())

            # Get list of all unique competencies across all members
            all_competencies = set()
            for member_data in members.values():
                all_competencies.update(member_data.get("competencias", {}).keys())

            competency_list = sorted(list(all_competencies))

            # Create data matrix
            data = np.zeros((len(member_names), len(competency_list)))

            for i, member_name in enumerate(member_names):
                member_competencies = members[member_name].get("competencias", {})
                for j, comp in enumerate(competency_list):
                    data[i, j] = member_competencies.get(comp, 0)

            # Create figure
            plt.figure(figsize=(12, max(8, len(member_names) * 0.5)))

            # Create heatmap
            ax = sns.heatmap(
                data,
                annot=True,
                fmt=".1f",
                cmap="YlGnBu",
                cbar_kws={"label": "Competency Score"},
                vmin=1,
                vmax=5,
                linewidths=0.5,
            )

            # Set labels
            plt.yticks(np.arange(len(member_names)) + 0.5, member_names, rotation=0)
            plt.xticks(
                np.arange(len(competency_list)) + 0.5,
                competency_list,
                rotation=45,
                ha="right",
            )

            plt.title("Team Competency Heatmap")
            plt.tight_layout()

            # Save figure
            plt.savefig(output_path)
            plt.close()

            return output_path

        except Exception as e:
            logging.error(f"Error generating team heatmap: {e}")
            if not self.ignore_errors:
                raise
            return None

    def _generate_team_distribution(self, members, output_path):
        """Generate a box plot visualization of competency distribution across team members"""
        try:
            import matplotlib.pyplot as plt

            # Get list of all unique competencies across all members
            all_competencies = set()
            for member_data in members.values():
                all_competencies.update(member_data.get("competencias", {}).keys())

            competency_list = sorted(list(all_competencies))

            # Prepare data for box plot
            data = []

            for comp in competency_list:
                scores = []
                for member_data in members.values():
                    comp_score = member_data.get("competencias", {}).get(comp, None)
                    if comp_score is not None:
                        scores.append(comp_score)
                data.append(scores)

            # Create figure
            plt.figure(figsize=(12, 8))

            # Create box plot
            box = plt.boxplot(
                data, patch_artist=True, labels=competency_list, vert=False, widths=0.6
            )

            # Color boxes
            for patch in box["boxes"]:
                patch.set(color="#3366FF", alpha=0.7)

            # Add grid lines
            plt.grid(axis="x", linestyle="--", alpha=0.7)

            # Set axis labels and title
            plt.xlabel("Score")
            plt.ylabel("Competencies")
            plt.title("Team Competency Distribution")

            # Adjust x-axis limits
            plt.xlim(0, 5.5)

            # Rotate x-labels for better readability
            plt.xticks(rotation=45, ha="right")

            plt.tight_layout()

            # Save figure
            plt.savefig(output_path)
            plt.close()

            return output_path

        except Exception as e:
            logging.error(f"Error generating team distribution chart: {e}")
            if not self.ignore_errors:
                raise
            return None

    def _calculate_team_balance(self, members):
        """Calculate team balance score based on competency distribution"""
        try:
            if not members:
                return 0

            # Extract all competencies across members
            all_competencies = {}
            for member_name, member_data in members.items():
                competencias = member_data.get("competencias", {})
                for comp_name, comp_value in competencias.items():
                    if comp_name not in all_competencies:
                        all_competencies[comp_name] = []
                    all_competencies[comp_name].append(comp_value)

            # Calculate standard deviation for each competency
            import numpy as np

            stdevs = []
            for comp_name, values in all_competencies.items():
                if len(values) > 1:  # Need at least 2 values for std
                    stdev = np.std(values)
                    stdevs.append(stdev)

            if not stdevs:
                return 5.0  # Default mid-point if we can't calculate

            # Average standard deviation (lower is better, more balanced)
            avg_stdev = sum(stdevs) / len(stdevs)

            # Convert to 0-10 scale (inversely related to stdev)
            # 0 stdev = perfect balance = 10 score
            # High stdev = poor balance = low score
            balance_score = max(0, min(10, 10 - (avg_stdev * 2)))

            return balance_score

        except Exception as e:
            logging.error(f"Error calculating team balance: {e}")
            return 5.0  # Default mid-point on error

    def _calculate_competency_coverage(self, members, team_competencias):
        """Calculate the coverage percentage for each competency in the team"""
        try:
            coverage = {}

            # For each competency, calculate what percentage of team members have it above threshold
            threshold = 3.0  # Consider a competency 'covered' if score is 3 or higher

            for comp_name in team_competencias:
                covered_count = 0
                for member_name, member_data in members.items():
                    comp_value = member_data.get("competencias", {}).get(comp_name, 0)
                    if comp_value >= threshold:
                        covered_count += 1

                coverage_pct = (covered_count / len(members)) * 100 if members else 0
                coverage[comp_name] = coverage_pct

            return coverage

        except Exception as e:
            logging.error(f"Error calculating competency coverage: {e}")
            return {}

    def _generate_heatmap(self, row_labels, col_labels, data, title, output_path):
        """Generate a heatmap visualization"""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            import seaborn as sns

            # Convert data to numpy array
            data_array = np.array(data)

            # Create figure and axes
            plt.figure(
                figsize=(max(8, len(col_labels) * 0.5), max(6, len(row_labels) * 0.4))
            )

            # Create heatmap
            sns.heatmap(
                data_array,
                annot=True,
                fmt=".1f",
                cmap="YlGnBu",
                xticklabels=col_labels,
                yticklabels=row_labels,
            )

            # Set title and labels
            plt.title(title)
            plt.tight_layout()

            # Save figure
            plt.savefig(output_path)
            plt.close()

            return output_path

        except Exception as e:
            logging.error(f"Error generating heatmap: {e}")
            if not self.ignore_errors:
                raise
            return None

    def _compress_output(self):
        """Compress output directory"""
        try:
            import shutil

            # Create zip file
            zip_path = self.output_dir.with_suffix(".zip")
            if self.verbose:
                print(f"Compressing output to {zip_path}")

            # Create zip file
            shutil.make_archive(
                base_name=self.output_dir,
                format="zip",
                root_dir=self.output_dir.parent,
                base_dir=self.output_dir.name,
            )

            print(f"Output compressed to {zip_path}")
            return True
        except Exception as e:
            logging.error(f"Error compressing output: {e}")
            if not self.ignore_errors:
                raise
            return False

    def _consolidate_data(self):
        """Consolidate processed data into HTML dashboard"""

        if self.verbose:
            print("Consolidating data...")

        # Create consolidation directory
        consolidation_dir = self.output_dir / "consolidated"
        os.makedirs(consolidation_dir, exist_ok=True)

        # Find processed directories
        processed_paths = []

        # Check if processed_directories is a list and has entries
        if isinstance(self.processed_directories, list) and self.processed_directories:
            for path_str in self.processed_directories:
                if "/" in path_str:  # Ensure it has the expected format
                    parts = path_str.split("/")
                    if len(parts) >= 2:
                        pessoa_name, ano_name = parts[0], parts[1]
                        pessoa_dir = Path(self.output_dir) / pessoa_name
                        ano_dir = pessoa_dir / ano_name

                        if ano_dir.exists():
                            processed_paths.append(
                                (Path(pessoa_name), Path(ano_name), ano_dir)
                            )

        # If we didn't find any paths using processed_directories list, try searching the output dir
        if not processed_paths:
            if self.verbose:
                print(
                    "No paths found in processed_directories, searching output directory..."
                )
            # Search for pessoa/ano structure in output directory
            for pessoa_dir in self.output_dir.iterdir():
                if pessoa_dir.is_dir() and pessoa_dir.name != "consolidated":
                    for ano_dir in pessoa_dir.iterdir():
                        if ano_dir.is_dir():
                            # Check if it has reports or visualizations
                            reports_dir = ano_dir / "reports"
                            viz_dir = ano_dir / "visualizations"
                            if reports_dir.exists() or viz_dir.exists():
                                processed_paths.append((pessoa_dir, ano_dir, ano_dir))

        if not processed_paths:
            print("No processed directories found for consolidation")
            return False

        if self.skip_dashboard:
            if self.verbose:
                print("Dashboard generation skipped")

            # If export to Excel is enabled, we should still do that even if dashboard is skipped
            if self.export_excel:
                try:
                    self._export_to_excel(processed_paths, consolidation_dir)
                except Exception as e:
                    print(f"Error exporting to Excel: {e}")
                    if not self.ignore_errors:
                        raise

            return True

        # Create HTML dashboard
        dashboard_file = consolidation_dir / "dashboard.html"

        # Structure for the dashboard
        html_content = (
            """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>People Analytics Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        h1, h2, h3 { color: #333; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { border: 1px solid #ddd; border-radius: 4px; padding: 15px; margin-bottom: 20px; }
        .section { margin-bottom: 30px; }
        .flex-container { display: flex; flex-wrap: wrap; gap: 20px; }
        .item { flex: 1; min-width: 200px; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .tag { background-color: #e1e1e1; padding: 3px 8px; border-radius: 3px; font-size: 0.8em; margin-right: 5px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        tr:hover { background-color: #f5f5f5; }
    </style>
</head>
<body>
    <div class="container">
        <h1>People Analytics Dashboard</h1>
        <p>Dados processados em """
            + datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            + """</p>
        
        <div class="section">
            <h2>Pessoas Analisadas</h2>
            <div class="flex-container">
"""
        )

        # Add individual people
        person_data = {}
        for pessoa_path, ano_path, full_path in processed_paths:
            pessoa_name = pessoa_path.name
            ano_name = ano_path.name

            # Store data for Excel export
            if pessoa_name not in person_data:
                person_data[pessoa_name] = {}

            if ano_name not in person_data[pessoa_name]:
                person_data[pessoa_name][ano_name] = {
                    "reports": [],
                    "visualizations": [],
                }

            # Add to HTML
            html_content += f"""
                <div class="card item">
                    <h3>{pessoa_name}</h3>
                    <p>Ano: {ano_name}</p>
                    <p>
            """

            # Add reports
            reports_dir = full_path / "reports"
            if reports_dir.exists():
                report_files = list(reports_dir.glob("*.json"))
                if report_files:
                    html_content += "<strong>Relatórios:</strong><br>"
                    for report in report_files:
                        report_link = (
                            f"../{pessoa_name}/{ano_name}/reports/{report.name}"
                        )
                        report_name = report.stem.replace("_", " ").title()
                        html_content += f"<a href='{report_link}'>{report_name}</a><br>"

                        # Store for Excel export
                        person_data[pessoa_name][ano_name]["reports"].append(
                            str(report)
                        )

            # Add visualizations
            viz_dir = full_path / "visualizations"
            if viz_dir.exists():
                viz_files = list(viz_dir.glob("*.*"))
                if viz_files:
                    html_content += "<strong>Visualizações:</strong><br>"
                    for viz in viz_files:
                        viz_link = (
                            f"../{pessoa_name}/{ano_name}/visualizations/{viz.name}"
                        )
                        viz_name = viz.stem.replace("_", " ").title()
                        html_content += f"<a href='{viz_link}'>{viz_name}</a><br>"

                        # Store for Excel export
                        person_data[pessoa_name][ano_name]["visualizations"].append(
                            str(viz)
                        )

            html_content += """
                    </p>
                </div>
            """

        # Close HTML structure
        html_content += """
            </div>
        </div>
    </div>
</body>
</html>
"""

        # Write HTML dashboard
        with open(dashboard_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        if self.verbose:
            print(f"Dashboard generated at {dashboard_file}")

        # Export to Excel if enabled
        if self.export_excel:
            try:
                self._export_to_excel(processed_paths, consolidation_dir)
            except Exception as e:
                print(f"Error exporting to Excel: {e}")
                if not self.ignore_errors:
                    raise

        return True

    def _export_to_excel(self, processed_paths, consolidation_dir):
        """Export consolidated data to Excel file"""
        try:
            from datetime import datetime

            import pandas as pd

            if self.verbose:
                print("Exporting data to Excel...")

            # Define the Excel file path
            timestamp = datetime.now().strftime("%Y%m%d")
            excel_file = consolidation_dir / f"dados_consolidados_{timestamp}.xlsx"

            # Create a Pandas ExcelWriter object
            with pd.ExcelWriter(excel_file) as writer:
                # Prepare data for pessoas sheet
                pessoas_data = []

                for pessoa_path, ano_path, full_path in processed_paths:
                    pessoa_name = pessoa_path.name
                    ano_name = ano_path.name

                    # Get reports
                    reports_dir = full_path / "reports"
                    reports_found = []
                    metrics = {}
                    action_items = []

                    if reports_dir.exists():
                        # Check for individual report
                        indiv_report = reports_dir / "individual_report.json"
                        if indiv_report.exists():
                            try:
                                with open(indiv_report, "r", encoding="utf-8") as f:
                                    report_data = json.load(f)
                                    # Extract metrics
                                    if isinstance(report_data, dict):
                                        scores = report_data.get("scores", {})
                                        for key, value in scores.items():
                                            metrics[f"score_{key}"] = value
                                    reports_found.append("individual_report")
                            except:
                                pass

                        # Check for action plan
                        action_plan = reports_dir / "action_plan.json"
                        if action_plan.exists():
                            try:
                                with open(action_plan, "r", encoding="utf-8") as f:
                                    plan_data = json.load(f)
                                    # Extract action items
                                    if (
                                        isinstance(plan_data, dict)
                                        and "items" in plan_data
                                    ):
                                        action_items = [
                                            item.get("description", "")
                                            for item in plan_data["items"]
                                        ]
                                    reports_found.append("action_plan")
                            except:
                                pass

                    # Prepare row data
                    row_data = {
                        "pessoa": pessoa_name,
                        "ano": ano_name,
                        "reports": ", ".join(reports_found),
                        "action_items": len(action_items),
                    }

                    # Add metrics
                    for k, v in metrics.items():
                        row_data[k] = v

                    pessoas_data.append(row_data)

                # Create pessoa DataFrame and save to Excel
                if pessoas_data:
                    df_pessoas = pd.DataFrame(pessoas_data)
                    df_pessoas.to_excel(writer, sheet_name="Pessoas", index=False)

                # Create a summary of reports
                reports_data = []
                for pessoa_path, ano_path, full_path in processed_paths:
                    reports_dir = full_path / "reports"
                    if reports_dir.exists():
                        for report_file in reports_dir.glob("*.json"):
                            reports_data.append(
                                {
                                    "pessoa": pessoa_path.name,
                                    "ano": ano_path.name,
                                    "report_type": report_file.stem,
                                    "file_path": str(report_file),
                                }
                            )

                # Save reports to Excel
                if reports_data:
                    df_reports = pd.DataFrame(reports_data)
                    df_reports.to_excel(writer, sheet_name="Relatórios", index=False)

                # Look for team reports
                team_reports = []
                team_dir = self.output_dir / "team_reports"
                if team_dir.exists():
                    for team_file in team_dir.glob("*.json"):
                        team_reports.append(
                            {"team": team_file.stem, "file_path": str(team_file)}
                        )

                # Save team reports to Excel
                if team_reports:
                    df_teams = pd.DataFrame(team_reports)
                    df_teams.to_excel(writer, sheet_name="Equipes", index=False)

            if self.verbose:
                print(f"Data exported to {excel_file}")
            return True

        except ImportError:
            print(
                "Pandas is required for Excel export. Install it with: pip install pandas openpyxl"
            )
            return False
        except Exception as e:
            print(f"Error exporting to Excel: {str(e)}")
            if not self.ignore_errors:
                raise
            return False

    def _validate_mermaid_syntax(
        self, mermaid_content: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates MermaidJS syntax to ensure diagrams will render correctly.

        Args:
            mermaid_content: The MermaidJS content to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for basic structure issues
        if not mermaid_content or not isinstance(mermaid_content, str):
            return False, "Empty or non-string content"

        # Extract the mermaid code block
        mermaid_match = re.search(
            r"```mermaid\s*(.*?)\s*```", mermaid_content, re.DOTALL
        )
        if not mermaid_match:
            return False, "No mermaid code block found"

        mermaid_code = mermaid_match.group(1)

        # Common syntax errors to check for
        common_errors = [
            # Check for unbalanced braces, brackets, parentheses
            (r"\{[^}]*$", "Unbalanced curly braces"),
            (r"\[[^\]]*$", "Unbalanced square brackets"),
            (r"\([^)]*$", "Unbalanced parentheses"),
            # Check for invalid diagram types
            (
                r"^(graph|flowchart|sequenceDiagram|classDiagram|stateDiagram|entityRelationshipDiagram|gantt|pie|timeline|mindmap)(\s|$)",
                None,
                True,
                "Invalid diagram type",
            ),
            # Missing required elements
            (r"timeline\s*$", "Timeline missing title or sections"),
            (r"graph\s*(TD|LR|RL|BT)\s*$", "Graph defined but empty"),
            # Check for syntax errors in different diagram types
            (r"-->-->", "Invalid arrow syntax (too many arrows)"),
            (r"--[^>]--", "Invalid connection syntax"),
            # Check for invalid style syntax
            (r"style\s+\w+\s+[^{]", "Invalid style definition (missing curly braces)"),
        ]

        # Check each error pattern
        for pattern_info in common_errors:
            if len(pattern_info) == 2:
                pattern, error_msg = pattern_info
                is_valid_pattern = False
            else:
                pattern, error_msg, is_valid_pattern, *_ = pattern_info

            match = re.search(pattern, mermaid_code)
            if match and not is_valid_pattern:
                return False, error_msg
            elif not match and is_valid_pattern:
                return False, error_msg

        # Check for diagram type and validate basic structure
        if re.search(r"^\s*graph", mermaid_code, re.MULTILINE):
            # Check for valid graph direction
            if not re.search(r"graph\s+(TD|TB|BT|RL|LR)", mermaid_code):
                return False, "Graph missing valid direction (TD, TB, BT, RL, LR)"

            # Check for at least one node
            if not re.search(r"[A-Za-z0-9_-]+(\[|\(|\{)", mermaid_code):
                return False, "Graph has no nodes defined"

        elif re.search(r"^\s*timeline", mermaid_code, re.MULTILINE):
            # Check for required timeline sections
            if not re.search(r"title\s+", mermaid_code):
                return False, "Timeline missing title"

            if not re.search(r"section\s+", mermaid_code):
                return False, "Timeline missing sections"

        # Additional checks for specific diagrams could be added here

        return True, None

    def _save_mermaid_file(self, content, output_path, pessoa_name=None):
        """
        Save MermaidJS content to file with validation

        Args:
            content: The MermaidJS content to save
            output_path: Path to save the file
            pessoa_name: Name of person (for logging)

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Validate MermaidJS syntax if enabled
            if self.validate_mermaid:
                is_valid, error_msg = self._validate_mermaid_syntax(content)
                if not is_valid:
                    person_info = f" for {pessoa_name}" if pessoa_name else ""
                    self.logger.warning(
                        f"Invalid MermaidJS syntax{person_info}: {error_msg}"
                    )

                    # Try to fix common issues
                    fixed_content = self._try_fix_mermaid(content, error_msg)
                    if fixed_content:
                        content = fixed_content
                        self.logger.info(
                            f"Attempted to fix MermaidJS syntax{person_info}"
                        )
                    elif not self.ignore_errors:
                        return False

            # Save the file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

            return True
        except Exception as e:
            self.logger.error(f"Error saving MermaidJS file: {e}")
            if not self.ignore_errors:
                raise
            return False

    def _try_fix_mermaid(self, content, error_msg):
        """
        Attempt to fix common MermaidJS syntax issues

        Args:
            content: The MermaidJS content to fix
            error_msg: The error message from validation

        Returns:
            Fixed content if possible, None otherwise
        """
        # Extract mermaid code block
        mermaid_match = re.search(r"```mermaid\s*(.*?)\s*```", content, re.DOTALL)
        if not mermaid_match:
            return None

        mermaid_code = mermaid_match.group(1)
        code_start = mermaid_match.start(1)
        code_end = mermaid_match.end(1)

        fixed_code = None

        # Apply fixes based on error
        if "Graph missing valid direction" in error_msg:
            # Add TD direction if missing
            if re.search(r"^\s*graph\s*$", mermaid_code, re.MULTILINE):
                fixed_code = mermaid_code.replace("graph", "graph TD")

        elif "Timeline missing title" in error_msg:
            # Add a title
            if "timeline" in mermaid_code:
                fixed_code = re.sub(
                    r"(timeline\s*)", r"\1\n    title Timeline\n", mermaid_code
                )

        elif "Unbalanced" in error_msg:
            # Try to balance brackets/braces/parentheses
            if "curly braces" in error_msg:
                open_count = mermaid_code.count("{")
                close_count = mermaid_code.count("}")
                if open_count > close_count:
                    fixed_code = mermaid_code + "}" * (open_count - close_count)
            elif "square brackets" in error_msg:
                open_count = mermaid_code.count("[")
                close_count = mermaid_code.count("]")
                if open_count > close_count:
                    fixed_code = mermaid_code + "]" * (open_count - close_count)
            elif "parentheses" in error_msg:
                open_count = mermaid_code.count("(")
                close_count = mermaid_code.count(")")
                if open_count > close_count:
                    fixed_code = mermaid_code + ")" * (open_count - close_count)

        # Apply the fix if found
        if fixed_code:
            return content[:code_start] + fixed_code + content[code_end:]

        return None

    def _create_career_timeline(
        self, person_name: str, career_data: Dict[str, Any]
    ) -> str:
        """Create a Mermaid timeline chart for career events"""
        eventos = career_data.get("eventos_carreira", [])

        if not eventos:
            return f"# Linha do Tempo de Carreira: {person_name}\n\nNenhum evento de carreira registrado."

        # Sort events by date
        eventos.sort(key=lambda x: x.get("data", ""))

        # Create Mermaid timeline
        mermaid = f"""# Linha do Tempo de Carreira: {person_name}

```mermaid
timeline
    title Trajetória de Carreira de {person_name}
"""

        # Group events by year
        years = {}
        for evento in eventos:
            date_str = evento.get("data", "")
            if date_str:
                try:
                    year = date_str.split("-")[0]
                    if year not in years:
                        years[year] = []
                    years[year].append(evento)
                except (IndexError, AttributeError):
                    # Handle invalid date formats
                    continue

        # Add events to timeline by year
        for year in sorted(years.keys()):
            mermaid += f"    section {year}\n"

            for evento in years[year]:
                date = evento.get("data", "").replace("-", "/")
                tipo = evento.get("tipo_evento", "")
                detalhes = evento.get("detalhes", "")

                # Format event text based on type
                if tipo == "promotion":
                    cargo_novo = evento.get("cargo_novo", "")
                    event_text = f"{date}: Promoção para {cargo_novo}"
                elif tipo == "lateral_move":
                    cargo_novo = evento.get("cargo_novo", "")
                    event_text = f"{date}: Movimento lateral para {cargo_novo}"
                elif tipo == "role_change":
                    cargo_novo = evento.get("cargo_novo", "")
                    event_text = f"{date}: Mudança de função para {cargo_novo}"
                elif tipo == "skill_acquisition":
                    event_text = f"{date}: Nova habilidade: {detalhes}"
                elif tipo == "certification":
                    event_text = f"{date}: Certificação: {detalhes}"
                else:
                    event_text = f"{date}: {tipo} - {detalhes}"

                # Sanitize event text to prevent mermaid syntax issues
                event_text = re.sub(r'[:"\\{}\[\]]+', "_", event_text)

                mermaid += f"        {event_text}\n"

        mermaid += "```\n"

        # Validate mermaid syntax
        if self.validate_mermaid:
            is_valid, error_msg = self._validate_mermaid_syntax(mermaid)
            if not is_valid:
                self.logger.warning(
                    f"Generated invalid MermaidJS for {person_name}: {error_msg}"
                )
                # Try to fix if possible
                fixed_mermaid = self._try_fix_mermaid(mermaid, error_msg)
                if fixed_mermaid:
                    mermaid = fixed_mermaid
                    self.logger.info(f"Fixed MermaidJS for {person_name}")

        return mermaid

    def _generate_markdown_report(self, pessoa_name, ano, data, output_dir):
        """Generate a markdown report for a person's evaluation data"""
        try:
            # Extract data from the input
            score_geral = data.get("score_geral", 0)
            competencias = data.get("competencias", {})
            pilares = data.get("pilares", {})

            # Get career data if available
            career_data = data.get("career_data", {})
            plano_acao = data.get("plano_acao", [])

            # Get historical data if available
            historical_data = data.get("historical_data", {})

            # Create visualization directory
            viz_dir = self.output_dir / "visualizations" / pessoa_name / ano
            os.makedirs(viz_dir, exist_ok=True)

            # Generate radar chart for competencies
            radar_path = None
            if competencias and not self.skip_viz:
                categories = list(competencias.keys())
                values = list(competencias.values())
                radar_path = viz_dir / "radar_chart.png"
                self._generate_radar_chart(
                    categories,
                    values,
                    f"{pessoa_name} - {ano} Competency Profile",
                    radar_path,
                )

            # Generate bar chart for pillars
            pillar_path = None
            if pilares and not self.skip_viz:
                categories = list(pilares.keys())
                values = list(pilares.values())
                pillar_path = viz_dir / "pillar_chart.png"
                self._generate_bar_chart(
                    categories,
                    values,
                    f"{pessoa_name} - {ano} Pillar Analysis",
                    pillar_path,
                )

            # Generate trend chart if historical data is available
            trend_path = None
            if historical_data and not self.skip_viz:
                trend_path = viz_dir / "trend_chart.png"
                self._generate_trend_chart(historical_data, pessoa_name, trend_path)

            # Create the markdown file
            report_path = output_dir / f"{pessoa_name}_{ano}_report.md"

            with open(report_path, "w", encoding="utf-8") as f:
                # Title and overall score
                f.write(f"# {pessoa_name} - {ano} Performance Analysis\n\n")
                f.write(f"**Overall Score:** {score_geral:.2f}/5.0\n\n")

                # Executive summary
                f.write("## Executive Summary\n\n")

                # Determine performance level
                if score_geral >= 4.5:
                    performance_level = "Outstanding"
                    summary = f"{pessoa_name} demonstrates exceptional performance across most competencies, showing mastery in key areas. Their overall score places them in the top tier of performers."
                elif score_geral >= 4.0:
                    performance_level = "Excellent"
                    summary = f"{pessoa_name} shows strong performance across competencies with notable strengths. Their overall evaluation indicates a high level of professional capability."
                elif score_geral >= 3.5:
                    performance_level = "Very Good"
                    summary = f"{pessoa_name} demonstrates above-average performance in most areas, with some standout competencies and opportunities for targeted development."
                elif score_geral >= 3.0:
                    performance_level = "Good"
                    summary = f"{pessoa_name} performs well in several areas with a solid foundation of competencies. Targeted development in specific areas could enhance overall performance."
                elif score_geral >= 2.5:
                    performance_level = "Satisfactory"
                    summary = f"{pessoa_name} meets basic expectations in most areas, with clear opportunities for improvement in several competencies."
                else:
                    performance_level = "Needs Improvement"
                    summary = f"{pessoa_name} requires significant development across multiple competencies. A structured development plan is recommended to address key areas."

                f.write(f"**Performance Level:** {performance_level}\n\n")
                f.write(f"{summary}\n\n")

                # Add radar chart if available
                if radar_path:
                    relative_path = os.path.relpath(radar_path, output_dir.parent)
                    f.write("## Competency Profile\n\n")
                    f.write(f"![Competency Profile](../{relative_path})\n\n")

                # Add pillar chart if available
                if pillar_path:
                    relative_path = os.path.relpath(pillar_path, output_dir.parent)
                    f.write("## Pillar Analysis\n\n")
                    f.write(f"![Pillar Analysis](../{relative_path})\n\n")

                # Add trend chart if available
                if trend_path:
                    relative_path = os.path.relpath(trend_path, output_dir.parent)
                    f.write("## Performance Trends\n\n")
                    f.write(f"![Performance Trends](../{relative_path})\n\n")

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
                                f"{pessoa_name} has shown improvement compared to the previous evaluation period. This positive trend indicates effective development activities and growing professional maturity.\n\n"
                            )
                        elif change < 0:
                            f.write(f"**Change:** {change:.2f} ({change_pct:.1f}%)\n\n")
                            f.write(
                                f"{pessoa_name} has experienced a decline compared to the previous evaluation period. This may indicate areas requiring focused attention or external factors affecting performance.\n\n"
                            )
                        else:
                            f.write("**Change:** 0.00 (0.0%)\n\n")
                            f.write(
                                f"{pessoa_name}'s performance has remained consistent compared to the previous evaluation period.\n\n"
                            )

                # Detailed competency analysis
                f.write("## Competency Analysis\n\n")

                if competencias:
                    # Sort competencies by score
                    sorted_competencias = sorted(
                        competencias.items(), key=lambda x: x[1], reverse=True
                    )

                    # Create a table of all competencies
                    f.write("### Competency Scores\n\n")
                    f.write("| Competency | Score | Level |\n")
                    f.write("|------------|-------|-------|\n")

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

                        f.write(f"| {comp_name} | {comp_score:.2f} | {level} |\n")

                    f.write("\n")

                    # Top 3 strengths
                    f.write("### Key Strengths\n\n")
                    top_strengths = sorted_competencias[:3]

                    for i, (comp_name, comp_score) in enumerate(top_strengths, 1):
                        f.write(f"**{i}. {comp_name} ({comp_score:.2f})**\n\n")

                        if comp_score >= 4.5:
                            f.write(
                                f"Demonstrates exceptional capability in {comp_name}. This represents a significant asset that can be leveraged for organizational benefit and mentoring others.\n\n"
                            )
                        elif comp_score >= 4.0:
                            f.write(
                                f"Shows strong proficiency in {comp_name}. This competency is well-developed and represents a valuable strength.\n\n"
                            )
                        else:
                            f.write(
                                f"Performs above average in {comp_name}. While not exceptional, this represents a reliable area of strength.\n\n"
                            )

                    # Development areas (bottom 3)
                    f.write("### Development Areas\n\n")
                    development_areas = sorted_competencias[-3:]
                    development_areas.reverse()  # Show lowest first

                    for i, (comp_name, comp_score) in enumerate(development_areas, 1):
                        f.write(f"**{i}. {comp_name} ({comp_score:.2f})**\n\n")

                        if comp_score < 2.0:
                            f.write(
                                f"Requires significant development in {comp_name}. Focused training and regular practice are recommended to build basic proficiency.\n\n"
                            )
                        elif comp_score < 3.0:
                            f.write(
                                f"Shows developing capability in {comp_name}. Targeted improvement activities would help strengthen this area.\n\n"
                            )
                        else:
                            f.write(
                                f"Demonstrates moderate proficiency in {comp_name}. While not a critical gap, enhancing this competency would improve overall performance.\n\n"
                            )

                # Pillar analysis
                if pilares:
                    f.write("## Pillar Analysis\n\n")

                    # Sort pillars by score
                    sorted_pilares = sorted(
                        pilares.items(), key=lambda x: x[1], reverse=True
                    )

                    # Create a table of all pillars
                    f.write("| Pillar | Score | Assessment |\n")
                    f.write("|--------|-------|------------|\n")

                    for pilar_name, pilar_score in sorted_pilares:
                        # Determine pillar assessment
                        if pilar_score >= 4.5:
                            assessment = "Exceptional"
                        elif pilar_score >= 4.0:
                            assessment = "Strong"
                        elif pilar_score >= 3.0:
                            assessment = "Solid"
                        elif pilar_score >= 2.0:
                            assessment = "Developing"
                        else:
                            assessment = "Needs Focus"

                        f.write(
                            f"| {pilar_name} | {pilar_score:.2f} | {assessment} |\n"
                        )

                    f.write("\n")

                    # Detailed analysis of top and bottom pillar
                    top_pilar = sorted_pilares[0]
                    bottom_pilar = sorted_pilares[-1]

                    f.write("### Pillar Insights\n\n")

                    # Top pillar analysis
                    f.write(
                        f"**Strongest Pillar: {top_pilar[0]} ({top_pilar[1]:.2f})**\n\n"
                    )
                    f.write(
                        f"{pessoa_name} demonstrates notable strength in the {top_pilar[0]} pillar. This indicates solid capability in this fundamental area, which serves as a foundation for related competencies.\n\n"
                    )

                    # Bottom pillar analysis
                    f.write(
                        f"**Focus Area: {bottom_pilar[0]} ({bottom_pilar[1]:.2f})**\n\n"
                    )
                    f.write(
                        f"The {bottom_pilar[0]} pillar represents an opportunity for development. Strengthening this foundational area would likely improve several related competencies and overall performance.\n\n"
                    )

                # Career data analysis if available
                if career_data:
                    f.write("## Career Development\n\n")

                    # Current role and level
                    current_role = career_data.get("current_role", "Not specified")
                    current_level = career_data.get("current_level", "Not specified")

                    f.write(f"**Current Role:** {current_role}\n\n")
                    f.write(f"**Current Level:** {current_level}\n\n")

                    # Role fit analysis
                    role_fit = career_data.get("role_fit", 0)

                    f.write("### Role Fit Analysis\n\n")

                    if role_fit >= 4.0:
                        f.write(
                            f"**Role Fit Score: {role_fit:.2f}/5.0 (Excellent)**\n\n"
                        )
                        f.write(
                            f"{pessoa_name} shows excellent alignment with their current role. Their competency profile strongly matches the role requirements, suggesting they are well-positioned for success and growth in this position.\n\n"
                        )
                    elif role_fit >= 3.0:
                        f.write(f"**Role Fit Score: {role_fit:.2f}/5.0 (Good)**\n\n")
                        f.write(
                            f"{pessoa_name} demonstrates good alignment with their current role. Most key competencies match role requirements, though some targeted development could enhance performance further.\n\n"
                        )
                    else:
                        f.write(
                            f"**Role Fit Score: {role_fit:.2f}/5.0 (Needs Review)**\n\n"
                        )
                        f.write(
                            f"{pessoa_name}'s competency profile shows gaps compared to the requirements of their current role. A review of role expectations, additional support, or possible role adjustment may be warranted.\n\n"
                        )

                    # Career path options
                    career_paths = career_data.get("career_paths", [])

                    if career_paths:
                        f.write("### Career Path Options\n\n")

                        for path in career_paths:
                            path_name = path.get("path", "Not specified")
                            path_fit = path.get("fit", 0)
                            path_gaps = path.get("gaps", [])

                            f.write(f"**{path_name}**\n\n")
                            f.write(f"Alignment Score: {path_fit:.2f}/5.0\n\n")

                            if path_gaps:
                                f.write("Development needs for this path:\n")
                                for gap in path_gaps:
                                    f.write(f"- {gap}\n")
                                f.write("\n")
                            else:
                                f.write(
                                    "No specific gaps identified for this career path.\n\n"
                                )

                # Action plan
                if plano_acao:
                    f.write("## Action Plan\n\n")

                    for i, action in enumerate(plano_acao, 1):
                        competency = action.get("competencia", "Not specified")
                        description = action.get("acao", "Not specified")
                        deadline = action.get("prazo", "Not specified")
                        priority = action.get("prioridade", "Medium")

                        f.write(f"### Action {i}: {competency}\n\n")
                        f.write(f"**Description:** {description}\n\n")
                        f.write(f"**Deadline:** {deadline}\n\n")
                        f.write(f"**Priority:** {priority}\n\n")

                # Additional recommendations
                f.write("## Recommendations\n\n")

                # Calculate statistics for recommendations
                avg_score = (
                    sum(competencias.values()) / len(competencias)
                    if competencias
                    else 0
                )
                below_avg = [c for c, s in competencias.items() if s < 3.0]
                strengths = [c for c, s in competencias.items() if s >= 4.0]

                # Generate personalized recommendations
                f.write("### Development Focus\n\n")

                if below_avg:
                    f.write("Focus development efforts on these key areas:\n\n")
                    for comp in below_avg[:3]:  # Top 3 development needs
                        f.write(
                            f"- **{comp}**: Consider targeted training, mentoring, or structured practice opportunities\n"
                        )
                    f.write("\n")
                else:
                    f.write(
                        "No critical development areas identified. Consider stretch assignments to continue growth.\n\n"
                    )

                f.write("### Leveraging Strengths\n\n")

                if strengths:
                    f.write("These strengths can be leveraged for greater impact:\n\n")
                    for comp in strengths[:3]:  # Top 3 strengths
                        f.write(
                            f"- **{comp}**: Consider opportunities for mentoring others, leading initiatives, or taking on complex challenges in this area\n"
                        )
                    f.write("\n")
                else:
                    f.write(
                        "Focus on developing areas of potential strength to create distinctive capabilities.\n\n"
                    )

                # Next steps
                f.write("### Next Steps\n\n")
                f.write("1. Review this analysis with the individual\n")
                f.write("2. Jointly prioritize development areas\n")
                f.write("3. Create specific, measurable action items with deadlines\n")
                f.write("4. Schedule regular check-ins to monitor progress\n")
                f.write("5. Review progress formally at mid-year point\n\n")

                # Date of report
                f.write(f"\n\n*Generated on {datetime.now().strftime('%Y-%m-%d')}*\n")

                # Add enhanced content if rich_markdown is enabled
                if self.rich_markdown:
                    self._enhance_markdown_report(f, pessoa_name, ano, data)

            return report_path

        except Exception as e:
            logging.error(
                f"Error generating markdown report for {pessoa_name} - {ano}: {e}"
            )
            if not self.ignore_errors:
                raise
            return None

    def _enhance_markdown_report(self, file_handle, pessoa_name, ano, data):
        """
        Enhance markdown report with additional analysis and insights

        Args:
            file_handle: Open file handle for the markdown report
            pessoa_name: Name of the person
            ano: Year of evaluation
            data: Evaluation data dictionary
        """
        try:
            # Extract relevant data
            competencias = data.get("competencias", {})
            pilares = data.get("pilares", {})
            career_data = data.get("career_data", {})
            historical_data = data.get("historical_data", {})

            # Add SWOT analysis
            file_handle.write("\n\n## SWOT Analysis\n\n")

            # Sort competencies by score
            sorted_competencias = sorted(
                competencias.items(), key=lambda x: x[1], reverse=True
            )

            # Internal factors (Strengths, Weaknesses)
            file_handle.write(
                "<table>\n<tr>\n<th>Strengths</th>\n<th>Weaknesses</th>\n</tr>\n<tr>\n<td>\n\n"
            )

            # Strengths (top 3-5 competencies)
            strengths = sorted_competencias[:4]
            for comp_name, comp_score in strengths:
                file_handle.write(f"- **{comp_name}** ({comp_score:.2f}): ")
                if comp_score >= 4.5:
                    file_handle.write(
                        "Exceptional mastery, can lead and mentor others\n"
                    )
                elif comp_score >= 4.0:
                    file_handle.write("Strong capability, reliable performance\n")
                else:
                    file_handle.write("Above average, consistent performer\n")

            file_handle.write("\n</td>\n<td>\n\n")

            # Weaknesses (bottom 3-5 competencies)
            weaknesses = sorted_competencias[-4:]
            weaknesses.reverse()
            for comp_name, comp_score in weaknesses:
                file_handle.write(f"- **{comp_name}** ({comp_score:.2f}): ")
                if comp_score < 2.5:
                    file_handle.write("Significant development needed\n")
                elif comp_score < 3.0:
                    file_handle.write("Requires structured improvement\n")
                else:
                    file_handle.write("Below average, needs attention\n")

            file_handle.write(
                "\n</td>\n</tr>\n<tr>\n<th>Opportunities</th>\n<th>Threats</th>\n</tr>\n<tr>\n<td>\n\n"
            )

            # Opportunities (based on career data and improving competencies)
            career_paths = career_data.get("career_paths", [])
            if career_paths:
                # Get potential growth opportunities
                top_path = max(career_paths, key=lambda x: x.get("fit", 0))
                file_handle.write(
                    f"- Potential for **{top_path.get('path', 'career advancement')}**\n"
                )

            # Add opportunities based on competencies that are close to next level
            almost_strong = [c for c, s in competencias.items() if 3.7 <= s < 4.0]
            for comp in almost_strong[:2]:
                file_handle.write(
                    f"- **{comp}** is close to becoming a strong capability\n"
                )

            # Add learning opportunities
            file_handle.write(
                "- Targeted training in development areas could yield quick improvements\n"
            )

            if historical_data:
                years = sorted(historical_data.keys())
                if len(years) >= 2:
                    latest = years[-1]
                    previous = years[-2]
                    if historical_data[latest] > historical_data[previous]:
                        file_handle.write(
                            "- Positive growth trend indicates good learning capacity\n"
                        )

            file_handle.write("\n</td>\n<td>\n\n")

            # Threats (performance risks, career obstacles)
            critical_gaps = [c for c, s in competencias.items() if s < 2.5]
            if critical_gaps:
                file_handle.write(
                    "- Critical gaps in fundamental competencies could limit growth:\n"
                )
                for gap in critical_gaps[:2]:
                    file_handle.write(f"  - **{gap}**\n")

            # Trend-based threats
            if historical_data:
                years = sorted(historical_data.keys())
                if len(years) >= 2:
                    latest = years[-1]
                    previous = years[-2]
                    if historical_data[latest] < historical_data[previous]:
                        file_handle.write(
                            "- Declining performance trend requires attention\n"
                        )

            # Role fit threats
            role_fit = career_data.get("role_fit", 0)
            if role_fit < 3.0:
                file_handle.write("- Current role may not align well with strengths\n")

            # General threats
            file_handle.write(
                "- Without addressing key development areas, career growth may stall\n"
            )

            file_handle.write("\n</td>\n</tr>\n</table>\n\n")

            # Add Skills Gap Analysis
            file_handle.write("## Skills Gap Analysis\n\n")

            # Career path analysis
            desired_role = None
            if career_paths:
                desired_role = max(career_paths, key=lambda x: x.get("fit", 0)).get(
                    "path"
                )

            if desired_role:
                file_handle.write(f"### Gap Analysis for {desired_role} Path\n\n")

                # Get gaps for this path
                path_obj = next(
                    (p for p in career_paths if p.get("path") == desired_role), None
                )
                if path_obj:
                    gaps = path_obj.get("gaps", [])

                    if gaps:
                        file_handle.write(
                            "The following gaps were identified for this career path:\n\n"
                        )
                        file_handle.write(
                            "| Competency | Importance | Current Level | Gap |\n"
                        )
                        file_handle.write(
                            "|------------|------------|---------------|-----|\n"
                        )

                        for gap in gaps:
                            comp_name = gap
                            current = competencias.get(comp_name, 0)
                            target = 4.0  # Assuming target level is 4.0 for career advancement
                            importance = "High" if current < 3.0 else "Medium"

                            file_handle.write(
                                f"| {comp_name} | {importance} | {current:.2f} | {target - current:.2f} |\n"
                            )
                    else:
                        file_handle.write(
                            "No significant gaps identified for this career path.\n\n"
                        )

            # Add Learning Recommendations
            file_handle.write("\n## Learning & Development Recommendations\n\n")

            # Sort development needs by gap size
            dev_needs = []
            for comp, score in competencias.items():
                if score < 3.5:  # Consider anything below 3.5 as development need
                    gap = 4.0 - score  # Gap to reach "strong" level
                    dev_needs.append((comp, score, gap))

            dev_needs.sort(key=lambda x: x[2], reverse=True)  # Sort by gap size

            if dev_needs:
                file_handle.write("### Prioritized Learning Plan\n\n")
                file_handle.write(
                    "| Competency | Current | Target | Priority | Recommended Actions |\n"
                )
                file_handle.write(
                    "|------------|---------|--------|----------|--------------------|\n"
                )

                for comp, score, gap in dev_needs[:5]:  # Top 5 development needs
                    # Determine priority
                    if gap > 2.0:
                        priority = "Critical"
                    elif gap > 1.5:
                        priority = "High"
                    elif gap > 1.0:
                        priority = "Medium"
                    else:
                        priority = "Low"

                    # Generate recommendations based on competency and score
                    if score < 2.0:
                        rec = f"Structured training program; weekly mentoring sessions; start with basics of {comp}"
                    elif score < 3.0:
                        rec = f"Focused improvement projects; monthly coaching; targeted learning resources on {comp}"
                    else:
                        rec = f"Practice opportunities; self-directed learning; stretch assignments related to {comp}"

                    file_handle.write(
                        f"| {comp} | {score:.2f} | 4.00 | {priority} | {rec} |\n"
                    )

                # Add visual learning path using Mermaid diagram
                file_handle.write("\n### Development Roadmap\n\n")
                file_handle.write("```mermaid\ngantt\n")
                file_handle.write(f"    title {pessoa_name}'s Development Roadmap\n")
                file_handle.write("    dateFormat  YYYY-MM-DD\n")
                file_handle.write("    axisFormat %m-%y\n")

                # Set today and timeframes
                today = datetime.now()
                start_date = today.strftime("%Y-%m-%d")

                # Calculate timeframes based on priority
                file_handle.write("    section Critical Skills\n")

                # Add critical and high priority items
                month_offset = 0
                for comp, score, gap in dev_needs:
                    if gap > 1.5:  # Critical or High priority
                        duration = int(gap * 2)  # Duration in months based on gap size
                        end_date = today.replace(day=1).replace(
                            month=((today.month + duration - 1) % 12) + 1
                        )
                        if today.month + duration > 12:
                            end_date = end_date.replace(
                                year=today.year + ((today.month + duration - 1) // 12)
                            )

                        end_date_str = end_date.strftime("%Y-%m-%d")
                        file_handle.write(f"    {comp} :{start_date}, {end_date_str}\n")
                        month_offset += 1

                file_handle.write("    section Growth Areas\n")

                # Add medium priority items
                for comp, score, gap in dev_needs:
                    if 1.0 <= gap <= 1.5:  # Medium priority
                        duration = int(gap * 2)  # Duration in months based on gap size
                        delay = month_offset * 15  # Stagger start dates
                        start_delayed = (today + timedelta(days=delay)).strftime(
                            "%Y-%m-%d"
                        )
                        end_date = today.replace(day=1).replace(
                            month=((today.month + duration + (delay // 30) - 1) % 12)
                            + 1
                        )
                        if today.month + duration + (delay // 30) > 12:
                            end_date = end_date.replace(
                                year=today.year
                                + ((today.month + duration + (delay // 30) - 1) // 12)
                            )

                        end_date_str = end_date.strftime("%Y-%m-%d")
                        file_handle.write(
                            f"    {comp} :{start_delayed}, {end_date_str}\n"
                        )
                        month_offset += 1

                file_handle.write("```\n\n")
            else:
                file_handle.write(
                    "No significant development needs identified. Focus on maintaining current strengths and exploring advanced opportunities for growth.\n\n"
                )

            # Add Benchmark comparison if we have team or historical data
            file_handle.write("## Benchmark Comparison\n\n")

            if historical_data:
                years = sorted(historical_data.keys())
                scores = [historical_data[year] for year in years]

                file_handle.write("### Year-over-Year Performance\n\n")
                file_handle.write("```mermaid\nxychart-beta\n")
                file_handle.write("    title Year-over-Year Performance\n")
                file_handle.write(
                    "    x-axis [" + ", ".join([f'"{y}"' for y in years]) + "]\n"
                )
                file_handle.write('    y-axis "Score" 0 --> 5\n')
                file_handle.write(
                    "    bar [" + ", ".join([f"{s}" for s in scores]) + "]\n"
                )
                file_handle.write("```\n\n")

            # Add certification and learning path recommendations
            file_handle.write("## Certification & Learning Path\n\n")

            # Based on competency profile, recommend relevant certifications
            tech_comps = [
                c
                for c in competencias.keys()
                if c.lower()
                in [
                    "technical skills",
                    "technical knowledge",
                    "programming",
                    "data analysis",
                    "analytics",
                ]
            ]
            leadership_comps = [
                c
                for c in competencias.keys()
                if c.lower()
                in ["leadership", "management", "team lead", "people management"]
            ]

            if tech_comps:
                file_handle.write("### Technical Path\n\n")
                file_handle.write(
                    "Based on your competency profile, these certifications may be valuable:\n\n"
                )
                file_handle.write(
                    "1. **Data Science Certification** - Enhance analytical capabilities\n"
                )
                file_handle.write(
                    "2. **Advanced Analytics Tools** - Build technical proficiency\n"
                )
                file_handle.write(
                    "3. **Project Management for Technical Teams** - Improve delivery capabilities\n\n"
                )

            if leadership_comps:
                file_handle.write("### Leadership Path\n\n")
                file_handle.write(
                    "To strengthen leadership capabilities, consider:\n\n"
                )
                file_handle.write(
                    "1. **People Management Excellence** - Develop team leadership skills\n"
                )
                file_handle.write(
                    "2. **Strategic Leadership** - Build business acumen and strategy skills\n"
                )
                file_handle.write(
                    "3. **Executive Communication** - Enhance influence and stakeholder management\n\n"
                )

            # Add final recommendations section
            file_handle.write("## Key Takeaways\n\n")
            file_handle.write(
                "1. **Focus on top development priorities** - Address critical gaps first\n"
            )
            file_handle.write(
                "2. **Leverage existing strengths** - Use current capabilities to accelerate growth\n"
            )
            file_handle.write(
                "3. **Align development with career aspirations** - Target learning for desired path\n"
            )
            file_handle.write(
                "4. **Set specific, measurable goals** - Define clear success metrics\n"
            )
            file_handle.write(
                "5. **Regular progress reviews** - Schedule quarterly check-ins to assess development\n\n"
            )

        except Exception as e:
            logging.error(f"Error enhancing markdown report for {pessoa_name}: {e}")
            file_handle.write(
                "\n\n*Note: Some enhanced content could not be generated due to an error.*\n"
            )

    def _generate_trend_chart(self, historical_data, pessoa_name, output_path):
        """Generate a trend chart for historical performance data"""
        try:
            import matplotlib.pyplot as plt

            # Sort years
            years = sorted(historical_data.keys())
            scores = [historical_data[year] for year in years]

            # Create the plot
            plt.figure(figsize=(10, 6))

            # Plot line with markers
            plt.plot(
                years, scores, marker="o", linestyle="-", linewidth=2, markersize=8
            )

            # Add value labels
            for i, score in enumerate(scores):
                plt.text(i, score + 0.05, f"{score:.2f}", ha="center")

            # Add title and labels
            plt.title(f"{pessoa_name} - Performance Trend")
            plt.xlabel("Year")
            plt.ylabel("Overall Score")

            # Set y-axis limits
            plt.ylim(0, 5.5)

            # Add grid
            plt.grid(True, linestyle="--", alpha=0.7)

            # Tight layout
            plt.tight_layout()

            # Save the chart
            plt.savefig(output_path)
            plt.close()

            return output_path

        except Exception as e:
            logging.error(f"Error generating trend chart: {e}")
            if not self.ignore_errors:
                raise
            return None

    def _generate_team_markdown_report(self, team_name, team_data, output_dir):
        """
        Generate a detailed markdown report for a team

        Args:
            team_name: The team name
            team_data: The processed team data
            output_dir: The output directory for reports

        Returns:
            Path to the generated markdown file
        """
        try:
            # Ensure output directory exists
            reports_dir = output_dir / "reports" / "markdown" / "teams"
            reports_dir.mkdir(exist_ok=True, parents=True)

            # Define markdown file path
            md_file = reports_dir / f"{team_name}_report.md"

            # Get data from team_data
            team_score = team_data.get("score_geral", 0)
            team_competencias = team_data.get("competencias", {})
            team_pilares = team_data.get("pilares", {})
            members = team_data.get("members", {})
            strengths = team_data.get("strengths", [])
            development_areas = team_data.get("development_areas", [])
            historical = team_data.get("historical", {})
            comp_pilar_map = team_data.get("competencia_pilar_mapping", {})

            # Get visualization paths
            viz_dir = output_dir / "visualizations" / "teams"
            viz_dir.mkdir(exist_ok=True, parents=True)

            radar_path = viz_dir / f"{team_name}_radar.png"
            historical_path = viz_dir / f"{team_name}_historical.png"
            pilares_path = viz_dir / f"{team_name}_pilares.png"
            heatmap_path = viz_dir / f"{team_name}_heatmap.png"

            # Create relative paths for markdown
            rel_radar_path = f"../../../visualizations/teams/{team_name}_radar.png"
            rel_historical_path = (
                f"../../../visualizations/teams/{team_name}_historical.png"
            )
            rel_pilares_path = f"../../../visualizations/teams/{team_name}_pilares.png"
            rel_heatmap_path = f"../../../visualizations/teams/{team_name}_heatmap.png"

            # Sort competencies by score
            sorted_comps = sorted(
                team_competencias.items(), key=lambda x: x[1], reverse=True
            )
            # Sort pillars by score
            sorted_pilares = sorted(
                team_pilares.items(), key=lambda x: x[1], reverse=True
            )
            # Sort members by score
            sorted_members = sorted(
                members.items(),
                key=lambda x: x[1].get("score_geral", 0)
                if isinstance(x[1], dict)
                else 0,
                reverse=True,
            )

            # Calculate overall performance level based on team_score
            if team_score >= 9:
                level = "🌟 High-Performing Team"
                level_desc = "Outstanding team performance across all areas"
            elif team_score >= 7.5:
                level = "✅ Strong Team"
                level_desc = "Strong team performance with few areas for improvement"
            elif team_score >= 6:
                level = "✓ Solid Team"
                level_desc = "Good team performance with some development opportunities"
            elif team_score >= 4:
                level = "⚠️ Developing Team"
                level_desc = "Team needs improvement in several key areas"
            else:
                level = "❗ Underperforming Team"
                level_desc = "Significant team development needed across most areas"

            # Create markdown content
            markdown_content = f"""# Team Assessment Report: {team_name}

## Executive Summary

**Overall Team Score:** {team_score:.2f}/5.0

"""
            # Add performance level and summary
            if team_score >= 4.5:
                performance_level = "Outstanding"
                summary = f"The {team_name} team demonstrates exceptional performance across most competencies, showing mastery in key areas. The team's overall score places it in the top tier of performers."
            elif team_score >= 4.0:
                performance_level = "Excellent"
                summary = f"The {team_name} team shows strong performance across competencies with notable strengths. The team's overall evaluation indicates a high level of capability."
            elif team_score >= 3.5:
                performance_level = "Very Good"
                summary = f"The {team_name} team demonstrates above-average performance in most areas, with some standout competencies and opportunities for targeted development."
            elif team_score >= 3.0:
                performance_level = "Good"
                summary = f"The {team_name} team performs well in several areas with a solid foundation of competencies. Targeted development in specific areas could enhance overall performance."
            elif team_score >= 2.5:
                performance_level = "Satisfactory"
                summary = f"The {team_name} team meets basic expectations in most areas, with clear opportunities for improvement in several competencies."
            else:
                performance_level = "Needs Improvement"
                summary = f"The {team_name} team requires significant development across multiple competencies. A structured development plan is recommended to address key areas."

            markdown_content += f"**Performance Level:** {performance_level}\n\n"
            markdown_content += f"{summary}\n\n"

            # Add visualizations if available
            if os.path.exists(radar_path):
                markdown_content += f"## Team Competency Profile\n\n"
                markdown_content += f"![Team Competency Profile]({rel_radar_path})\n\n"

            if os.path.exists(pilares_path):
                markdown_content += f"## Team Pillar Analysis\n\n"
                markdown_content += f"![Team Pillar Analysis]({rel_pilares_path})\n\n"

            if os.path.exists(heatmap_path):
                markdown_content += f"## Team Competency Heatmap\n\n"
                markdown_content += f"![Team Competency Heatmap]({rel_heatmap_path})\n\n"

            if os.path.exists(historical_path):
                markdown_content += f"## Team Performance Trends\n\n"
                markdown_content += f"![Team Performance Trends]({rel_historical_path})\n\n"

            # Competency Analysis
            markdown_content += "## Competency Analysis\n\n"

            if team_competencias:
                # Sort competencies by score
                sorted_competencias = sorted(
                    team_competencias.items(), key=lambda x: x[1], reverse=True
                )

                # Create a table of all competencies
                markdown_content += "### Team Competency Scores\n\n"
                markdown_content += "| Competency | Score | Pillar | Classification | Range |\n"
                markdown_content += "|------------|-------|--------|----------------|-------|\n"

                for comp_name, score in sorted_competencias:
                    # Get pillar for this competency
                    pilar = comp_pilar_map.get(comp_name, "Not Specified")

                    # Determine competency level
                    if score >= 4.5:
                        classification = "Mastery"
                        range_str = "Outstanding"
                    elif score >= 4.0:
                        classification = "Advanced"
                        range_str = "Excellent"
                    elif score >= 3.5:
                        classification = "Proficient+"
                        range_str = "Very Good"
                    elif score >= 3.0:
                        classification = "Proficient"
                        range_str = "Good"
                    elif score >= 2.5:
                        classification = "Developing"
                        range_str = "Satisfactory"
                    else:
                        classification = "Basic"
                        range_str = "Needs Improvement"

                    markdown_content += f"| {comp_name} | {score:.2f} | {pilar} | {classification} | {range_str} |\n"

                markdown_content += """

### Key Team Strengths

"""
                # Top 3 competencies
                for i, (comp_name, score) in enumerate(sorted_competencias[:3], 1):
                    markdown_content += f"**{i}. {comp_name} ({score:.2f})**\n\n"
                    if score >= 4.5:
                        markdown_content += f"The team demonstrates exceptional capability in {comp_name}. This is a significant collective strength that can be leveraged for organizational benefit.\n\n"
                    elif score >= 4.0:
                        markdown_content += f"The team shows strong proficiency in {comp_name}. This competency is well-developed across the team and represents a valuable strength.\n\n"
                    else:
                        markdown_content += f"The team performs above average in {comp_name}. While not exceptional, this represents a reliable area of team strength.\n\n"

                # Development areas
                markdown_content += "### Team Development Areas\n\n"
                # Bottom 3 competencies
                bottom_comps = sorted_competencias[-3:]
                bottom_comps.reverse()  # Show lowest first
                for i, (comp_name, score) in enumerate(bottom_comps, 1):
                    markdown_content += f"**{i}. {comp_name} ({score:.2f})**\n\n"
                    if score < 2.5:
                        markdown_content += f"The team requires significant development in {comp_name}. A focused team training plan should be implemented to build collective capability.\n\n"
                    elif score < 3.0:
                        markdown_content += f"The team shows developing capability in {comp_name}. Targeted improvement activities would help strengthen this collective area.\n\n"
                    else:
                        markdown_content += f"The team demonstrates moderate proficiency in {comp_name}. While not a critical gap, enhancing this team competency would improve overall performance.\n\n"

            # Team composition analysis
            if members:
                markdown_content += "## Team Composition Analysis\n\n"

                # Distribution of competency levels
                markdown_content += "### Competency Level Distribution\n\n"
                markdown_content += "```javascript\n"
                markdown_content += "{\n"
                
                # Count how many team members fall into each performance band
                performance_bands = {
                    "Outstanding (4.5-5.0)": 0,
                    "Excellent (4.0-4.49)": 0,
                    "Very Good (3.5-3.99)": 0,
                    "Good (3.0-3.49)": 0,
                    "Satisfactory (2.5-2.99)": 0,
                    "Needs Improvement (<2.5)": 0,
                }
                
                for member_name, member_data in members.items():
                    member_score = member_data.get("score_geral", 0)
                    if member_score >= 4.5:
                        performance_bands["Outstanding (4.5-5.0)"] += 1
                    elif member_score >= 4.0:
                        performance_bands["Excellent (4.0-4.49)"] += 1
                    elif member_score >= 3.5:
                        performance_bands["Very Good (3.5-3.99)"] += 1
                    elif member_score >= 3.0:
                        performance_bands["Good (3.0-3.49)"] += 1
                    elif member_score >= 2.5:
                        performance_bands["Satisfactory (2.5-2.99)"] += 1
                    else:
                        performance_bands["Needs Improvement (<2.5)"] += 1
                
                # Write to file
                for category, count in performance_bands.items():
                    markdown_content += f'    "{category}" : {count}\n'
                
                markdown_content += """```

            ### Team Balance Visualization

            ```mermaid
            pie
                title Team Performance Distribution
            """
            # Add pie chart slices
            for category, count in performance_bands.items():
                if count > 0:
                    markdown_content += f'    "{category}" : {count}\n'
                
            markdown_content += "```\n\n"
            
            # Table of team members
            markdown_content += "### Individual Performance\n\n"
            markdown_content += "| Team Member | Overall Score | Top Strength | Development Area | Performance Level |\n"
            markdown_content += "|-------------|---------------|--------------|------------------|------------------|\n"
            
            # Sort by performance score
            sorted_members = sorted(
                members.items(), 
                key=lambda x: x[1].get("score_geral", 0), 
                reverse=True
            )
            
            for member_name, member_data in sorted_members:
                member_score = member_data.get("score_geral", 0)
                
                # Get top strength and development area
                member_competencias = member_data.get("competencias", {})
                if member_competencias:
                    sorted_comps = sorted(
                        member_competencias.items(), key=lambda x: x[1], reverse=True
                    )
                    top_strength = sorted_comps[0][0] if sorted_comps else "N/A"
                    top_dev_area = sorted_comps[-1][0] if sorted_comps else "N/A"
                else:
                    top_strength = "N/A"
                    top_dev_area = "N/A"
                
                # Determine performance level
                if member_score >= 4.5:
                    performance_level = "Outstanding"
                elif member_score >= 4.0:
                    performance_level = "Excellent"
                elif member_score >= 3.5:
                    performance_level = "Very Good"
                elif member_score >= 3.0:
                    performance_level = "Good"
                elif member_score >= 2.5:
                    performance_level = "Satisfactory"
                else:
                    performance_level = "Needs Improvement"
                
                markdown_content += f"| {member_name} | {member_score:.2f} | {top_strength} | {top_dev_area} | {performance_level} |\n"
            
            markdown_content += """

            ### Team Member Scores

            ```mermaid
            xychart-beta
                title Member Performance Comparison
                x-axis ["""
                
                # Add member names to x-axis
                member_names = [f'"m"' for m, _ in sorted_members]
                markdown_content += ", ".join(member_names) + "]\n"
                
                markdown_content += '    y-axis "Score" 0 --> 5\n    bar ['
                
                # Add scores to bar chart
                scores = [str(m.get("score_geral", 0)) for _, m in sorted_members]
                markdown_content += ", ".join(scores) + "]\n```\n"

            # Add skill gaps and training recommendations
            markdown_content += """
            ## Team Skill Gaps Analysis

            """
            # Calculate team skill gaps
            if team_competencias:
                gaps = {comp: score for comp, score in team_competencias.items() if score < 3.5}
                sorted_gaps = sorted(gaps.items(), key=lambda x: x[1])
                
                if sorted_gaps:
                    markdown_content += "### Priority Development Areas\n\n"
                    markdown_content += "| Competency | Current Score | Gap to Target | Priority | Impact |\n"
                    markdown_content += "|------------|---------------|---------------|----------|--------|\n"
                    
                    for comp, score in sorted_gaps:
                        gap = 4.0 - score
                        
                        # Determine priority
                        if gap > 2.0:
                            priority = "Critical"
                        elif gap > 1.5:
                            priority = "High"
                        elif gap > 1.0:
                            priority = "Medium"
                        else:
                            priority = "Low"
                        
                        # Determine organizational impact
                        pilar = comp_pilar_map.get(comp, "Not Specified")
                        if pilar in ["Core", "Technical", "Leadership"] and gap > 1.5:
                            impact = "Major"
                        elif gap > 1.0:
                            impact = "Significant"
                        else:
                            impact = "Moderate"
                        
                        markdown_content += f"| {comp} | {score:.2f} | {gap:.2f} | {priority} | {impact} |\n"
                    
                    # Generate team training recommendations
                    markdown_content += "\n### Team Training Recommendations\n\n"
                    
                    # Focus on top 3 gaps
                    for i, (comp, score) in enumerate(sorted_gaps[:3], 1):
                        markdown_content += f"**{i}. {comp} Training Initiative**\n\n"
                        
                        gap = 4.0 - score
                        if gap > 2.0:
                            markdown_content += f"* **Approach**: Comprehensive team workshop series on {comp}\n"
                            markdown_content += "* **Duration**: 3-month intensive program\n"
                            markdown_content += "* **Format**: Combination of external training, internal workshops, and practical application\n"
                            markdown_content += f"* **Expected Outcome**: Raise team {comp} score to at least 3.0 within 6 months\n\n"
                        elif gap > 1.5:
                            markdown_content += f"* **Approach**: Targeted skill-building program for {comp}\n"
                            markdown_content += "* **Duration**: 2-month focused initiative\n"
                            markdown_content += "* **Format**: Weekly workshops with specific deliverables\n"
                            markdown_content += f"* **Expected Outcome**: Improve team {comp} score by at least 1.0 point\n\n"
                        else:
                            markdown_content += f"* **Approach**: Skill enhancement sessions for {comp}\n"
                            markdown_content += "* **Duration**: 4-6 weekly sessions\n"
                            markdown_content += "* **Format**: Internal knowledge sharing and practice sessions\n"
                            markdown_content += f"* **Expected Outcome**: Raise team {comp} score above 3.5\n\n"
                else:
                    markdown_content += "No significant skill gaps identified at the team level. Focus should be on advancing existing capabilities and addressing individual development needs.\n\n"

            # Competency Coverage Analysis
            if members and team_competencias:
                markdown_content += "## Competency Coverage Analysis\n\n"
                
                # Calculate how many team members have each competency as a strength
                comp_coverage = {}
                for comp in team_competencias.keys():
                    strong_members = []
                    for member_name, member_data in members.items():
                        member_comps = member_data.get("competencias", {})
                        if member_comps.get(comp, 0) >= 4.0:
                            strong_members.append(member_name)
                    comp_coverage[comp] = strong_members
                
                # Distribution of competency coverage
                markdown_content += "```javascript\n"
                markdown_content += "{\n"
                
                # Count distribution
                coverage_dist = {}
                for comp, members_list in comp_coverage.items():
                    count = len(members_list)
                    category = f"{count} Members"
                    coverage_dist[category] = coverage_dist.get(category, 0) + 1
                
                for category, count in sorted(coverage_dist.items()):
                    markdown_content += f'    "{category}" : {count}\n'
                
                markdown_content += """```

            ### Competency Distribution

            ```mermaid
            xychart-beta
                title Competency Coverage
                x-axis ["""
                
                # List competencies with low coverage
                comp_names = [f'"{c}"' for c, m in comp_coverage.items() if len(m) < 2][:8]
                markdown_content += ", ".join(comp_names) + "]\n"
                
                markdown_content += '    y-axis "Number of Members" 0 --> 5\n    bar ['
                
                # Add member counts to bar chart
                counts = [str(len(m)) for c, m in comp_coverage.items() if len(m) < 2][:8]
                markdown_content += ", ".join(counts) + "]\n```\n"
                
                # Identify critical coverage gaps
                critical_gaps = [comp for comp, members in comp_coverage.items() if not members]
                if critical_gaps:
                    markdown_content += "\n### Critical Coverage Gaps\n\n"
                    markdown_content += "The following competencies have no team members with strong capability (score >= 4.0):\n\n"
                    for gap in critical_gaps:
                        markdown_content += f"- **{gap}**\n"
                    
                    markdown_content += "\nRecommendation: Consider targeted recruitment or focused development to ensure coverage of these critical competencies.\n\n"

            # Add enhanced team analysis if rich_markdown is enabled
            if self.rich_markdown:
                # SWOT Analysis
                markdown_content += """
            ## Team SWOT Analysis

            <table>
            <tr>
            <th>Strengths</th>
            <th>Weaknesses</th>
            </tr>
            <tr>
            <td>

            """
                # Team strengths
                team_strengths = [comp for comp, score in team_competencias.items() if score >= 4.0]
                if team_strengths:
                    for strength in team_strengths[:4]:
                        markdown_content += f"- Strong collective capability in **{strength}**\n"
                
                # Good score distribution
                above_avg_count = sum(1 for _, data in members.items() if data.get("score_geral", 0) >= 3.5)
                if above_avg_count > len(members) / 2:
                    markdown_content += f"- {above_avg_count} team members perform above average\n"
                
                # Balanced competency coverage
                well_covered = sum(1 for _, member_list in comp_coverage.items() if len(member_list) >= 2)
                if well_covered > len(team_competencias) / 2:
                    markdown_content += f"- Good coverage across {well_covered} key competencies\n"
                
                markdown_content += """
            </td>
            <td>

            """
                # Team weaknesses
                team_weaknesses = [comp for comp, score in team_competencias.items() if score < 3.0]
                if team_weaknesses:
                    for weakness in team_weaknesses[:4]:
                        markdown_content += f"- Collective gap in **{weakness}**\n"
                
                # Poor performers
                poor_performers = sum(1 for _, data in members.items() if data.get("score_geral", 0) < 3.0)
                if poor_performers > 0:
                    markdown_content += f"- {poor_performers} team members require significant development\n"
                
                # Critical competency gaps
                if critical_gaps:
                    markdown_content += f"- No strong capability in {len(critical_gaps)} critical competencies\n"
                
                markdown_content += """
            </td>
            </tr>
            <tr>
            <th>Opportunities</th>
            <th>Threats</th>
            </tr>
            <tr>
            <td>

            """
                # Opportunities
                # Nearly strong competencies
                near_strong = [comp for comp, score in team_competencias.items() if 3.7 <= score < 4.0]
                if near_strong:
                    for comp in near_strong[:2]:
                        markdown_content += f"- **{comp}** is close to becoming a team strength\n"
                
                # Knowledge sharing potential
                if well_covered > 0:
                    markdown_content += f"- Internal knowledge sharing for {well_covered} well-covered competencies\n"
                
                # Cross-training
                markdown_content += "- Cross-training opportunities to address coverage gaps\n"
                
                # High performers as mentors
                high_performers = sum(1 for _, data in members.items() if data.get("score_geral", 0) >= 4.0)
                if high_performers > 0:
                    markdown_content += f"- Leverage {high_performers} high performers as internal mentors\n"
                
                markdown_content += """
            </td>
            <td>

            """
                # Threats
                if poor_performers > len(members) / 3:
                    markdown_content += "- Significant portion of team requires development\n"
                
                if critical_gaps:
                    markdown_content += "- Critical competency gaps may impact team delivery\n"
                
                # Performance variance
                scores = [data.get("score_geral", 0) for _, data in members.items()]
                if scores:
                    variance = max(scores) - min(scores)
                    if variance > 1.5:
                        markdown_content += f"- High performance variance ({variance:.1f} points) may create team imbalance\n"
                
                # Potential skill loss
                markdown_content += "- Risk of knowledge/skill gaps if key team members leave\n"
                
                markdown_content += """
            </td>
            </tr>
            </table>

            """

                # Add Team Collaboration Assessment
                markdown_content += """
            ## Team Collaboration Assessment

            ### Collaboration Network Analysis

            Team members with complementary skills who should work closely together:

            """
                # Identify complementary skills for collaboration
                collaborations = []
                for comp, score in sorted_competencias:
                    if score < 3.5:  # Focus on team's weaker areas
                        # Find members strong in this area
                        strong_members = []
                        for member_name, member_data in members.items():
                            member_comps = member_data.get("competencias", {})
                            if member_comps.get(comp, 0) >= 4.0:
                                strong_members.append(member_name)
                            
                            # Find members weak in this area
                            weak_members = []
                            for member_name, member_data in members.items():
                                member_comps = member_data.get("competencias", {})
                                if member_comps.get(comp, 0) < 3.0:
                                    weak_members.append(member_name)
                            
                            # If we have both strong and weak members, suggest collaboration
                            if strong_members and weak_members:
                                collaborations.append((comp, strong_members, weak_members))
                
                # Generate collaboration recommendations
                if collaborations:
                    for i, (comp, strong, weak) in enumerate(collaborations[:3], 1):
                        markdown_content += f"**{i}. {comp} Knowledge Transfer**\n\n"
                        markdown_content += f"- **Mentors:** {', '.join(strong[:2])}\n"
                        markdown_content += f"- **Mentees:** {', '.join(weak[:3])}\n"
                        markdown_content += f"- **Activity:** Structured knowledge sharing sessions on {comp}\n"
                        markdown_content += "- **Format:** Pair programming, shadowing, and guided practice\n\n"
                else:
                    markdown_content += "No clear collaboration patterns identified based on competency data. Consider team-building activities to identify natural collaboration channels.\n\n"
                
                # Add Team Dynamics Visualization
                markdown_content += """
            ### Team Dynamics Visualization

            ```mermaid
            flowchart LR
                classDef highPerformer fill:#baf,stroke:#333,stroke-width:2px;
                classDef mediumPerformer fill:#fdb,stroke:#333,stroke-width:1px;
                classDef developmentNeeded fill:#fcc,stroke:#333,stroke-width:1px;
            """
                
                # Create nodes for each team member
                for i, (member_name, member_data) in enumerate(members.items(), 1):
                    member_score = member_data.get("score_geral", 0)
                    node_id = f"M{i}"
                    markdown_content += f"    {node_id}[{member_name}]\n"
                    
                    # Style based on performance
                    if member_score >= 4.0:
                        markdown_content += f"    class {node_id} highPerformer;\n"
                    elif member_score >= 3.0:
                        markdown_content += f"    class {node_id} mediumPerformer;\n"
                    else:
                        markdown_content += f"    class {node_id} developmentNeeded;\n"
                
                # Create collaboration connections
                if collaborations:
                    for comp_idx, (comp, strong, weak) in enumerate(collaborations[:2], 1):
                        for strong_idx, strong_member in enumerate(strong[:2]):
                            strong_id = None
                            for i, (member_name, _) in enumerate(members.items(), 1):
                                if member_name == strong_member:
                                    strong_id = f"M{i}"
                                    break
                                
                            for weak_idx, weak_member in enumerate(weak[:2]):
                                weak_id = None
                                for i, (member_name, _) in enumerate(members.items(), 1):
                                    if member_name == weak_member:
                                        weak_id = f"M{i}"
                                        break
                                    
                                    if strong_id and weak_id:\n                                        markdown_content += f"    {strong_id} -->|{comp}| {weak_id}\n"
                
                markdown_content += "```\n\n"
                
                # Add Team Action Plan
                markdown_content += """
            ## Team Action Plan

            ### Short-term Actions (1-3 months)
            """
                
                # Generate short-term actions
                if team_weaknesses:
                    for i, weakness in enumerate(team_weaknesses[:2], 1):
                        markdown_content += f"{i}. Conduct team workshop on **{weakness}** to address critical gap\n"
                
                if collaborations:
                    markdown_content += f"{len(team_weaknesses[:2])+1}. Establish structured mentoring program for knowledge transfer\n"
                
                if poor_performers > 0:
                    markdown_content += f"{len(team_weaknesses[:2])+2}. Develop individual improvement plans for team members needing support\n"
                
                markdown_content += """
            ### Medium-term Goals (3-6 months)
            """
                
                # Generate medium-term goals
                if team_weaknesses:
                    markdown_content += f"1. Improve team score in {team_weaknesses[0]} to at least 3.0\n"
                
                if near_strong:
                    markdown_content += f"2. Develop {near_strong[0]} into a team strength (>4.0)\n"
                
                markdown_content += "3. Reduce performance variance across the team by 30%\n"
                
                markdown_content += """
            ### Long-term Vision (6-12 months)
            """
                
                markdown_content += "1. Achieve balanced competency coverage across all critical skills\n"
                markdown_content += "2. Develop internal capability to self-train on all key competencies\n"
                markdown_content += "3. Raise overall team performance score to at least 4.0\n\n"
            
            # Date of report
            markdown_content += f"\n\n*Generated on {datetime.now().strftime('%Y-%m-%d')}*\n"
            
            # Write the markdown content to the file
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            return md_file

        except Exception as e:
            logging.error(f"Error generating team markdown report for {team_name}: {e}")
            if not self.ignore_errors:
                raise
            return None
