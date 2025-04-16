"""
Sync and documentation commands for People Analytics CLI.

This module contains commands for data synchronization and documentation generation.
"""

import argparse
import json
import logging
import os
import time
from pathlib import Path
from typing import List

from tqdm import tqdm

from ..utils.score_calculator import ScoreCalculator


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
        Adiciona argumentos ao comando.
        """
        parser.add_argument(
            "--data",
            help="Data directory path",
            default="./data",
            type=Path,
        )
        parser.add_argument(
            "--output",
            help="Output directory path",
            default="./output",
            type=Path,
        )
        parser.add_argument(
            "--force",
            help="Force reprocessing of all files",
            action="store_true",
        )
        parser.add_argument(
            "--formatos",
            help="Formatos para processar (all, json, yaml, csv, excel)",
            default="all",
        )
        parser.add_argument(
            "--pessoa",
            help="Filter by pessoa name",
            type=str,
            default=None,
        )
        parser.add_argument(
            "--ano",
            help="Filter by year",
            type=str,
            default=None,
        )
        parser.add_argument(
            "--skip-viz",
            help="Skip visualization generation",
            action="store_true",
        )
        parser.add_argument(
            "--ignore-errors",
            help="Ignore errors and continue processing",
            action="store_true",
        )
        parser.add_argument(
            "--zip",
            help="Compress output files",
            action="store_true",
        )
        parser.add_argument(
            "--skip-dashboard",
            help="Skip dashboard generation",
            action="store_true",
        )
        parser.add_argument(
            "--export-excel",
            help="Export consolidated data to Excel",
            action="store_true",
        )
        parser.add_argument(
            "--verbose",
            help="Show detailed information",
            action="store_true",
        )
        parser.add_argument(
            "--parallel",
            help="Process directories in parallel",
            action="store_true",
        )
        parser.add_argument(
            "--batch-size",
            help="Batch size for parallel processing (0 for all at once)",
            type=int,
            default=0,
        )
        parser.add_argument(
            "--workers",
            help="Maximum number of worker threads (0 for CPU count)",
            type=int,
            default=0,
        )
        parser.add_argument(
            "--progress",
            help="Show progress bar",
            action="store_true",
        )
        parser.add_argument(
            "--clean-data",
            action="store_true",
            help="Limpar arquivos temporários e de cache após processamento",
        )
        parser.add_argument(
            "--template", type=str, help="Custom visualization template path"
        )
        parser.add_argument(
            "--output-config",
            type=str,
            help="Path to JSON file with output configuration",
        )
        parser.add_argument(
            "--theme",
            type=str,
            default="default",
            help="Visualization theme (default, dark, light, corporate)",
        )

    def handle(self, *args, **options):
        """Handle command"""
        data_dir = options.get("data", Path("./data"))
        output_dir = options.get("output", Path("./output"))
        force = options.get("force", False)
        zip_output = options.get("zip", False)
        skip_dashboard = options.get("skip_dashboard", False)

        # Create sync
        sync = DataSync()
        sync.data_dir = data_dir
        sync.output_dir = output_dir
        sync.force = force
        sync.zip = zip_output
        sync.skip_dashboard = skip_dashboard
        sync.skip_viz = options.get("skip_viz", False)
        sync.ignore_errors = options.get("ignore_errors", False)
        sync.selected_formats = options.get("formatos", "all")
        sync.pessoa_filter = options.get("pessoa", None)
        sync.ano_filter = options.get("ano", None)
        sync.export_excel = options.get("export_excel", False)
        sync.verbose = options.get("verbose", False)
        sync.parallel = options.get("parallel", False)
        sync.batch_size = options.get("batch_size", 0)
        sync.workers = options.get("workers", 0)
        sync.progress = options.get("progress", False)

        # Execute sync
        try:
            return sync.execute()
        except Exception as e:
            print(f"Error: {e}")
            return 1


class DataSync:
    """
    Classe para sincronizar dados.
    """

    def __init__(self):
        """
        Inicializa a classe.
        """
        self.data_dir = None
        self.output_dir = None
        self.force = False
        self.zip = False
        self.skip_dashboard = False
        self.skip_viz = False
        self.ignore_errors = False
        self.selected_formats = "all"
        self.pessoa_filter = None
        self.ano_filter = None
        self.export_excel = False
        self.verbose = False
        self.parallel = False
        self.batch_size = 0
        self.workers = 0
        self.progress = False
        self.valid_formats = {
            "json": [".json"],
            "yaml": [".yaml", ".yml"],
            "csv": [".csv"],
            "excel": [".xlsx", ".xls"],
        }
        self.processed_directories = []
        self.errors = []
        self.logger = logging.getLogger("datasync")

        # Configurações adicionais
        self.export_pdf = False
        self.synthetic = False
        self.bulk_export = False
        self.anonymize = False
        self.template_path = None
        self.show_progress = True
        self.output_config_path = None
        self.theme = "default"
        self.output_config = None

        # Performance metrics
        self.total_directories = 0
        self.processed_directories = 0
        self.skipped_directories = 0
        self.error_directories = 0
        self.start_time = None
        self.end_time = None

        # Inicializar calculadora de scores
        self.score_calculator = ScoreCalculator()

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
        """Execute sync"""
        # Validate
        if not self.data_dir or not self.output_dir:
            raise ValueError("Data and output directories are required")

        # Check directories
        if not os.path.exists(self.data_dir):
            raise ValueError(f"Data directory not found: {self.data_dir}")
        os.makedirs(self.output_dir, exist_ok=True)

        # Log options
        print(f"Data path: {self.data_dir}")
        print(f"Output path: {self.output_dir}")
        print(f"Force reprocessing: {self.force}")
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
        print(f"Verbose mode: {self.verbose}")
        print(f"Parallel processing: {self.parallel}")
        if self.parallel:
            workers = "CPU count" if self.workers <= 0 else self.workers
            batch_size = "All at once" if self.batch_size <= 0 else self.batch_size
            print(f"Workers: {workers}")
            print(f"Batch size: {batch_size}")
            print(f"Show progress: {self.progress}")
        print("Expected data structure: <pessoa>/<ano>/resultado.json")

        # Process
        start_time = time.time()
        self._process_pessoa_ano_structure()
        end_time = time.time()

        # Consolidate results
        if not self.skip_dashboard:
            try:
                self._consolidate_data()
            except Exception as e:
                logging.error(f"Error consolidating data: {e}")
                if not self.ignore_errors:
                    raise

        # Log
        total_processed = len(self.processed_directories)
        total_errors = len(self.errors)
        elapsed_time = round(end_time - start_time, 2)
        print(
            f"Processed {total_processed} directories in {elapsed_time} seconds ({round(total_processed / elapsed_time, 2)} directories/second)"
        )
        if total_errors > 0:
            print(f"Errors: {total_errors}")
            for error in self.errors:
                print(f"- {error}")

        # Return
        return 0 if total_errors == 0 else 1

    def _process_file(self, file_path, file_format):
        """Process a file based on its format"""
        if self.verbose:
            print(f"Processing {file_path} as {file_format}")

        # Process based on format
        if file_format == "json":
            return self._process_json_file(file_path)
        elif file_format == "yaml":
            return self._process_yaml_file(file_path)
        elif file_format == "csv":
            return self._process_csv_file(file_path)
        elif file_format == "excel":
            return self._process_excel_file(file_path)
        else:
            logging.warning(f"Unsupported format: {file_format}")
            return None

    def _process_json_file(self, file_path):
        """Process a JSON file"""
        import json

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception as e:
            logging.error(f"Error reading JSON file {file_path}: {e}")
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
        """Process pessoa/ano/resultado.json structure"""
        # Lists
        valid_directories = []

        # Check data dir
        if not self.data_dir.exists():
            print(f"Data directory not found: {self.data_dir}")
            return False

        # Find all pessoa directories
        pessoa_dirs = [d for d in self.data_dir.iterdir() if d.is_dir()]
        self.total_directories = 0

        # Process each pessoa directory
        for pessoa_dir in pessoa_dirs:
            # Skip if pessoa filter is set and doesn't match
            if self.pessoa_filter and pessoa_dir.name != self.pessoa_filter:
                if self.verbose:
                    print(
                        f"Skipping directory {pessoa_dir.name} (doesn't match pessoa filter)"
                    )
                continue

            # Find all ano directories
            ano_dirs = [d for d in pessoa_dir.iterdir() if d.is_dir()]

            # Process each ano directory
            for ano_dir in ano_dirs:
                # Skip if ano filter is set and doesn't match
                if self.ano_filter and ano_dir.name != self.ano_filter:
                    if self.verbose:
                        print(
                            f"Skipping directory {pessoa_dir.name}/{ano_dir.name} (doesn't match ano filter)"
                        )
                    continue

                # Check if resultado.json exists or other supported formats
                result_files = self._check_result_files(ano_dir)

                if result_files:
                    # Valid directory
                    valid_directories.append((pessoa_dir, ano_dir, result_files))
                    self.total_directories += 1
                else:
                    if self.verbose:
                        print(
                            f"No result files found in {pessoa_dir.name}/{ano_dir.name}"
                        )

        # Show directories found
        print(f"Found {self.total_directories} directories to process")

        # Process in parallel or sequential mode
        if self.parallel and self.total_directories > 1:
            return self._process_directories_parallel(valid_directories)
        else:
            return self._process_directories_sequential(valid_directories)

    def _process_directories_sequential(self, valid_directories):
        """Process directories sequentially"""
        # Initialize progress bar if needed
        if self.progress:
            pbar = tqdm(total=self.total_directories, desc="Processing directories")

        # Process each directory
        for pessoa_dir, ano_dir, result_files in valid_directories:
            try:
                # Process directory
                self._process_directory(pessoa_dir, ano_dir, result_files)
                self.processed_directories += 1
            except Exception as e:
                self.error_directories += 1
                logging.error(f"Error processing {pessoa_dir.name}/{ano_dir.name}: {e}")
                if not self.ignore_errors:
                    if self.progress:
                        pbar.close()
                    return False

            # Update progress
            if self.progress:
                pbar.update(1)

        # Close progress bar
        if self.progress:
            pbar.close()

        # Complete
        return self._complete_processing()

    def _process_directories_parallel(self, valid_directories):
        """Process directories in parallel"""
        # Initialize variables
        processed = 0
        errors = 0

        # Determine max workers (default to CPU count)
        max_workers = os.cpu_count() or 4

        # Process in batches if needed
        if self.batch_size > 0:
            batches = [
                valid_directories[i : i + self.batch_size]
                for i in range(0, len(valid_directories), self.batch_size)
            ]
            print(
                f"Processing in {len(batches)} batches of up to {self.batch_size} directories each"
            )

            for batch_num, batch in enumerate(batches, 1):
                print(f"Processing batch {batch_num}/{len(batches)}")
                batch_processed, batch_errors = self._process_batch_parallel(
                    batch, max_workers
                )
                processed += batch_processed
                errors += batch_errors

                # Stop on error if needed
                if errors > 0 and not self.ignore_errors:
                    break
        else:
            # Process all directories in parallel
            processed, errors = self._process_batch_parallel(
                valid_directories, max_workers
            )

        # Update counters
        self.processed_directories = processed
        self.error_directories = errors

        # Complete
        return (
            self._complete_processing() if errors == 0 or self.ignore_errors else False
        )

    def _process_batch_parallel(self, directories, max_workers):
        """Process a batch of directories in parallel"""
        processed = 0
        errors = 0

        # Create progress bar if needed
        if self.progress:
            pbar = tqdm(total=len(directories), desc="Processing directories")

        # Set actual workers based on parameter
        actual_workers = self.workers if self.workers > 0 else max_workers

        # Process using ThreadPoolExecutor
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=actual_workers
        ) as executor:
            # Submit all tasks
            future_to_dir = {
                executor.submit(
                    self._process_directory, pessoa_dir, ano_dir, result_files
                ): (pessoa_dir, ano_dir)
                for pessoa_dir, ano_dir, result_files in directories
            }

            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_dir):
                pessoa_dir, ano_dir = future_to_dir[future]

                try:
                    # Get result (True if successful)
                    result = future.result()
                    if result:
                        processed += 1
                    else:
                        errors += 1
                except Exception as e:
                    errors += 1
                    error_msg = (
                        f"Error processing {pessoa_dir.name}/{ano_dir.name}: {e}"
                    )
                    self.errors.append(error_msg)
                    logging.error(error_msg)

                    # Stop if we shouldn't ignore errors
                    if not self.ignore_errors:
                        # Cancel remaining tasks
                        for f in future_to_dir:
                            f.cancel()
                        break

                # Update progress bar
                if self.progress:
                    pbar.update(1)

        # Close progress bar
        if self.progress:
            pbar.close()

        return processed, errors

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

        # Generate reports
        self._generate_reports(combined_data, output_dir, pessoa_name, ano_name)

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
        # Create reports directory
        reports_dir = output_dir / "reports"
        os.makedirs(reports_dir, exist_ok=True)

        try:
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
        # Compress output if requested
        if self.zip:
            self._compress_output()

        # Check results
        if len(self.processed_directories) == 0:
            print("No directories were processed")
            return False

        return True

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
        from datetime import datetime

        import pandas as pd

        if self.verbose:
            print("Consolidating data...")

        # Create consolidation directory
        consolidation_dir = self.output_dir / "consolidated"
        os.makedirs(consolidation_dir, exist_ok=True)

        # Find processed directories
        processed_paths = []
        for pessoa_name, ano_name in [
            path.split("/") for path in self.processed_directories
        ]:
            pessoa_dir = Path(self.output_dir) / pessoa_name
            ano_dir = pessoa_dir / ano_name

            if ano_dir.exists():
                processed_paths.append((Path(pessoa_name), Path(ano_name), ano_dir))

        if not processed_paths:
            print("No processed directories found for consolidation")
            return False

        # Create HTML dashboard
        dashboard_path = consolidation_dir / "dashboard.html"

        # Create dashboard content
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>People Analytics Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .section {{ margin-bottom: 30px; }}
        .card {{ border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 15px; }}
        .person-section {{ margin-bottom: 30px; background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        .report-link {{ display: block; margin-bottom: 5px; }}
        .visualization-gallery {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .visualization-item {{ width: 300px; text-align: center; }}
        .visualization-item img {{ max-width: 100%; border: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>People Analytics Dashboard</h1>
        <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <div class="section">
            <h2>Processed Data</h2>
            <p>Total directories processed: {len(processed_paths)}</p>
            
            <h3>Individual Reports</h3>
            <div class="card">
                <table>
                    <tr>
                        <th>Person</th>
                        <th>Year</th>
                        <th>Reports</th>
                        <th>Visualizations</th>
                    </tr>
        """

        # Add entries for each processed directory
        for pessoa_path, ano_path, dir_path in processed_paths:
            pessoa_name = pessoa_path.name
            ano_name = ano_path.name

            # Get reports
            reports_dir = dir_path / "reports"
            reports = []
            if reports_dir.exists():
                reports = list(reports_dir.glob("*.json"))

            # Get visualizations
            viz_dir = dir_path / "visualizations"
            visualizations = []
            if viz_dir.exists():
                visualizations = list(viz_dir.glob("*.png"))

            # Add row to table
            html_content += f"""
                    <tr>
                        <td>{pessoa_name}</td>
                        <td>{ano_name}</td>
                        <td>
            """

            # Add report links
            for report in reports:
                report_name = report.name
                report_rel_path = f"{pessoa_name}/{ano_name}/reports/{report_name}"
                html_content += (
                    f'<a href="{report_rel_path}" class="report-link">{report_name}</a>'
                )

            html_content += """
                        </td>
                        <td>
            """

            # Add visualization links
            for viz in visualizations:
                viz_name = viz.name
                viz_rel_path = f"{pessoa_name}/{ano_name}/visualizations/{viz_name}"
                html_content += (
                    f'<a href="{viz_rel_path}" class="report-link">{viz_name}</a>'
                )

            html_content += """
                        </td>
                    </tr>
            """

        # Close table and add visualization gallery
        html_content += """
                </table>
            </div>
            
            <h3>Visualization Gallery</h3>
            <div class="visualization-gallery">
        """

        # Add visualizations to gallery
        for pessoa_path, ano_path, dir_path in processed_paths:
            pessoa_name = pessoa_path.name
            ano_name = ano_path.name

            # Get visualizations
            viz_dir = dir_path / "visualizations"
            if viz_dir.exists():
                for viz in viz_dir.glob("*.png"):
                    viz_name = viz.name
                    viz_rel_path = f"{pessoa_name}/{ano_name}/visualizations/{viz_name}"
                    html_content += f"""
                <div class="visualization-item">
                    <img src="{viz_rel_path}" alt="{viz_name}">
                    <p>{pessoa_name} - {ano_name} - {viz_name}</p>
                </div>
                    """

        # Close document
        html_content += """
            </div>
        </div>
    </div>
</body>
</html>
        """

        # Write HTML file
        with open(dashboard_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"Dashboard generated at {dashboard_path}")

        # Export to Excel if requested
        if self.export_excel:
            try:
                excel_path = (
                    consolidation_dir
                    / f"dados_consolidados_{datetime.now().strftime('%Y%m%d')}.xlsx"
                )
                if self.verbose:
                    print(f"Exporting data to Excel: {excel_path}")

                # Collect data for people
                pessoas_data = []

                for pessoa_path, ano_path, dir_path in processed_paths:
                    pessoa_name = pessoa_path.name
                    ano_name = ano_path.name

                    # Get evaluation reports
                    reports_dir = dir_path / "reports"
                    individual_report_path = reports_dir / "individual_report.json"
                    summary_report_path = reports_dir / "summary_report.json"

                    person_data = {
                        "pessoa": pessoa_name,
                        "ano": ano_name,
                    }

                    # Get summary data
                    if summary_report_path.exists():
                        try:
                            with open(summary_report_path, "r", encoding="utf-8") as f:
                                summary = json.load(f)
                                if "metrics" in summary:
                                    for key, value in summary["metrics"].items():
                                        person_data[f"metric_{key}"] = value
                        except:
                            pass

                    # Get action plans
                    action_plan_path = reports_dir / "action_plan.json"
                    if action_plan_path.exists():
                        try:
                            with open(action_plan_path, "r", encoding="utf-8") as f:
                                action_plan = json.load(f)
                                if "actions" in action_plan:
                                    person_data["action_count"] = len(
                                        action_plan["actions"]
                                    )
                        except:
                            pass

                    pessoas_data.append(person_data)

                # Create Excel file with pandas
                with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
                    # People sheet
                    if pessoas_data:
                        df_pessoas = pd.DataFrame(pessoas_data)
                        df_pessoas.to_excel(writer, sheet_name="Pessoas", index=False)

                    # Team summary sheet if we have team reports
                    team_reports_dir = self.output_dir / "team_reports"
                    if team_reports_dir.exists():
                        team_data = []
                        for team_file in team_reports_dir.glob("*.json"):
                            try:
                                with open(team_file, "r", encoding="utf-8") as f:
                                    team_report = json.load(f)
                                    team_data.append(team_report)
                            except:
                                pass

                        if team_data:
                            df_teams = pd.DataFrame(team_data)
                            df_teams.to_excel(writer, sheet_name="Equipes", index=False)

                    # Reports sheet
                    reports_data = []
                    for pessoa_path, ano_path, dir_path in processed_paths:
                        pessoa_name = pessoa_path.name
                        ano_name = ano_path.name

                        # Get reports
                        reports_dir = dir_path / "reports"
                        if reports_dir.exists():
                            for report in reports_dir.glob("*.json"):
                                reports_data.append(
                                    {
                                        "pessoa": pessoa_name,
                                        "ano": ano_name,
                                        "report_type": report.stem,
                                        "report_path": str(
                                            report.relative_to(self.output_dir)
                                        ),
                                    }
                                )

                    if reports_data:
                        df_reports = pd.DataFrame(reports_data)
                        df_reports.to_excel(
                            writer, sheet_name="Relatórios", index=False
                        )

                print(f"Data exported to Excel: {excel_path}")

            except Exception as e:
                logging.error(f"Error exporting to Excel: {e}")
                if not self.ignore_errors:
                    raise

        return True
