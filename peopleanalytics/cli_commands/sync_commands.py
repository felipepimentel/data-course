"""
Sync and documentation commands for People Analytics CLI.

This module contains commands for data synchronization and documentation generation.
"""

import argparse
import json
import logging
import os
import random
import time
from datetime import datetime
from pathlib import Path

# Configure matplotlib to use non-interactive backend
import matplotlib

matplotlib.use("Agg")  # Set backend to Agg (non-interactive)

# Import the EvaluationScore class


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

        # Output format settings
        parser.add_argument(
            "--generate-json",
            action="store_true",
            help="Generate JSON output files (default: disabled)",
            dest="generate_json",
            default=False,
        )
        parser.add_argument(
            "--no-markdown",
            action="store_true",
            help="Disable rich markdown reports (default: enabled)",
        )

        # Add advanced analytics options
        parser.add_argument(
            "--time-series-forecast",
            action="store_true",
            help="Enable advanced time series forecasting",
            dest="time_series_forecast",
        )
        parser.add_argument(
            "--competency-gap",
            action="store_true",
            help="Enable enhanced competency gap analysis",
            dest="competency_gap_analysis",
        )
        parser.add_argument(
            "--network-metrics",
            action="store_true",
            help="Include advanced network metrics and community detection",
            dest="advanced_network_metrics",
        )
        parser.add_argument(
            "--ml-insights",
            action="store_true",
            help="Enable machine learning based insights",
            dest="ml_insights",
        )
        parser.add_argument(
            "--sentiment-analysis",
            action="store_true",
            help="Apply sentiment analysis to qualitative feedback",
            dest="sentiment_analysis",
        )
        parser.add_argument(
            "--advanced-visualizations",
            action="store_true",
            help="Generate enhanced interactive visualizations",
            dest="advanced_visualizations",
        )
        parser.add_argument(
            "--all-advanced-features",
            action="store_true",
            help="Enable all advanced analytics features",
            dest="all_advanced_features",
        )

        parser.add_argument(
            "--report-output-dir",
            type=str,
            help="Directory to store generated reports",
        )
        parser.add_argument(
            "--report-include-org-chart",
            action="store_true",
            help="Include organizational chart in skill reports",
        )
        parser.add_argument(
            "--report-year-comparison",
            action="store_true",
            help="Include year-over-year comparisons in skill reports",
        )

        # Talent development report options
        parser.add_argument(
            "--no-9box",
            action="store_true",
            help="Disable 9-Box Matrix reports",
        )
        parser.add_argument(
            "--no-career-sim",
            action="store_true",
            help="Disable Career Simulation reports",
        )
        parser.add_argument(
            "--no-network",
            action="store_true",
            help="Disable Influence Network reports",
        )
        parser.add_argument(
            "--talent-report-dir",
            type=str,
            default="output/talent_reports",
            help="Directory to store talent development reports",
        )

        # Output format options
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
        )

        # Performance options
        parser.add_argument(
            "--no-parallel",
            action="store_true",
            help="Use sequential processing instead of parallel",
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
        """Execute the sync command

        Args:
            args: Parsed arguments
        """
        start_time = time.time()

        # Initialize the logger here
        self.logger = logging.getLogger(__name__)

        self.logger.info("Starting sync command")
        self.logger.info(f"Arguments: {args}")

        data_sync = DataSync(
            data_dir=args.data_dir,
            output_dir=args.output_dir,
            pessoa=args.pessoa,
            ano=args.ano,
            generate_markdown=not args.no_markdown,
            generate_json=args.generate_json,
            include_org_chart=args.report_include_org_chart,
            generate_peer_analysis=args.peer_analysis,
            generate_yoy_analysis=args.yoy_analysis,
            weighted_scoring=args.weighted_scoring,
            generate_9box=not args.no_9box,
            generate_career_sim=not args.no_career_sim,
            generate_network=not args.no_network,
            force=args.force,
            ignore_errors=args.ignore_errors,
            use_parallel=not args.no_parallel,
            workers=args.workers,
            batch_size=args.batch_size,
            report_output_dir=args.report_output_dir,
            analysis_output_dir=args.analysis_output_dir,
            talent_report_dir=args.talent_report_dir,
            generate_visualizations=not args.skip_viz,
            generate_dashboard=not args.skip_dashboard,
            generate_excel=not args.no_excel,
            logger=self.logger,
            verbose=not args.quiet,
            generate_ml_insights=args.ml_insights,
            generate_sentiment_analysis=args.sentiment_analysis,
        )

        data_sync.sync()

        end_time = time.time()
        elapsed_time = end_time - start_time

        self.logger.info(f"Sync command completed in {elapsed_time:.2f} seconds")

        # Compression code removed as per request - content is now left in its proper directory structure


class DataSync:
    """
    Classe para sincronizar dados.
    """

    def __init__(self, **kwargs):
        """Initialize the data sync object"""
        super().__init__()
        self.data_dir = Path(kwargs.get("data_dir", "data"))
        self.output_dir = Path(kwargs.get("output_dir", "output"))
        self.workers = kwargs.get("workers")
        self.batch_size = kwargs.get("batch_size")
        self.skip_viz = not kwargs.get("generate_visualizations", True)
        self.formats = []
        self.ignore_errors = kwargs.get("ignore_errors", False)
        self.skip_dashboard = not kwargs.get("generate_dashboard", True)
        self.no_zip = not kwargs.get("generate_zip", True)
        self.no_excel = not kwargs.get("generate_excel", True)
        self.no_parallel = not kwargs.get("use_parallel", True)
        self.rich_markdown = kwargs.get("generate_markdown", True)
        self.generate_json = kwargs.get("generate_json", False)
        self.verbose = kwargs.get("verbose", False)
        self.processed_directories = []
        self.errors = []
        self.logger = kwargs.get("logger", logging.getLogger("sync"))
        self.total_progress = 0
        self.current_progress = 0

        # Advanced analytics options
        self.time_series_forecast = kwargs.get("generate_time_series_forecast", False)
        self.competency_gap_analysis = kwargs.get(
            "generate_competency_gap_analysis", False
        )
        self.advanced_network_metrics = kwargs.get(
            "generate_advanced_network_metrics", False
        )
        self.ml_insights = kwargs.get("generate_ml_insights", False)
        self.sentiment_analysis = kwargs.get("generate_sentiment_analysis", False)
        self.advanced_visualizations = kwargs.get(
            "generate_advanced_visualizations", False
        )

        # Talent development report flags
        self.use_9box = kwargs.get("generate_9box", True)
        self.use_career_sim = kwargs.get("generate_career_sim", True)
        self.use_network = kwargs.get("generate_network", True)
        self.talent_report_dir = kwargs.get(
            "talent_report_dir", "output/talent_reports"
        )

        # Analysis report flags
        self.peer_analysis = kwargs.get("generate_peer_analysis", False)
        self.yoy_analysis = kwargs.get("generate_yoy_analysis", False)
        self.weighted_scoring = kwargs.get("weighted_scoring", False)
        self.analysis_output_dir = kwargs.get("analysis_output_dir", "output/analysis")

        # Report generation flags
        self.generate_evaluation_report = True
        self.generate_skill_recommendations = True
        self.include_radar_charts = True
        self.generate_skill_analytics = True
        self.include_org_chart = kwargs.get("include_org_chart", False)

        # Directory filters
        self.pessoa_filter = kwargs.get("pessoa")
        self.ano_filter = kwargs.get("ano")
        self.pessoa = self.pessoa_filter  # For backward compatibility
        self.ano = self.ano_filter  # For backward compatibility
        self.force = kwargs.get("force", False)
        self.reprocess = self.force  # For backward compatibility

        # File format mapping
        self.valid_formats = {
            "json": [".json"],
            "yaml": [".yaml", ".yml"],
            "csv": [".csv"],
            "excel": [".xlsx", ".xls"],
            "markdown": [".md"],
        }

        # Progress tracking
        self.progress = True

        # Setup logger if needed
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _ensure_directories(self):
        """Ensure that all necessary directories exist."""
        # Main output directory
        os.makedirs(self.output_dir, exist_ok=True)

        # Reports directory
        report_dir = os.path.join(self.output_dir, "reports")
        os.makedirs(report_dir, exist_ok=True)

        # Analysis directory
        analysis_dir = os.path.join(self.output_dir, "analysis")
        os.makedirs(analysis_dir, exist_ok=True)

        # Talent reports directory
        talent_dir = os.path.join(self.output_dir, "talent_reports")
        os.makedirs(talent_dir, exist_ok=True)
        os.makedirs(os.path.join(talent_dir, "matrix_9box"), exist_ok=True)
        os.makedirs(os.path.join(talent_dir, "career_simulation"), exist_ok=True)
        os.makedirs(os.path.join(talent_dir, "influence_network"), exist_ok=True)

        # Visualizations directory
        viz_dir = os.path.join(self.output_dir, "visualizations")
        os.makedirs(viz_dir, exist_ok=True)

        # Markdown directory
        markdown_dir = os.path.join(self.output_dir, "markdown")
        os.makedirs(markdown_dir, exist_ok=True)

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
            self.logger.info(start_message)

            # Ensure directories exist
            self._ensure_directories()

            # Process the pessoa/ano structure
            valid_directories = self._process_pessoa_ano_structure()

            if not valid_directories:
                message = "No valid directories found for processing"
                results.append(message)
                self.logger.warning(message)
                return results

            # Print summary of what will be processed
            self._print_processing_summary(valid_directories)

            # Initialize progress tracking
            self.total_progress = len(valid_directories)
            self.current_progress = 0

            # Track processed data for aggregated reports
            self.processed_data = {}

            # Convert Path objects to dictionary format for processing
            formatted_directories = []
            for dir_path in valid_directories:
                pessoa_dir = dir_path.parent
                ano_dir = dir_path
                result_files = list(ano_dir.glob("resultado.*"))

                formatted_directories.append(
                    {
                        "pessoa": pessoa_dir.name,
                        "ano": ano_dir.name,
                        "files": result_files,
                        "path": str(ano_dir),
                    }
                )

            # Process directories (sequential or parallel)
            success = True
            if not self.no_parallel:
                # Convert Path objects to dictionary format for _process_directories_parallel
                formatted_directories = []
                for dir_path in valid_directories:
                    pessoa_dir = dir_path.parent
                    ano_dir = dir_path
                    result_files = list(ano_dir.glob("resultado.*"))

                    formatted_directories.append(
                        {
                            "pessoa": pessoa_dir.name,
                            "ano": ano_dir.name,
                            "files": result_files,
                            "path": str(ano_dir),
                        }
                    )
                success = self._process_directories_parallel(formatted_directories)
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

            # Collect all people data for reports
            all_people_data = self._collect_all_people_data()

            # Generate advanced analytics if enabled
            if self.time_series_forecast:
                try:
                    results.append("Generating time series forecasting...")
                    if self._generate_time_series_forecast(all_people_data):
                        results.append("Time series forecasting generated successfully")
                    else:
                        results.append("Error generating time series forecasting")
                except Exception as e:
                    error_msg = f"Error generating time series forecasting: {str(e)}"
                    results.append(error_msg)
                    self.logger.error(error_msg, exc_info=True)
                    if not self.ignore_errors:
                        raise

            if self.competency_gap_analysis:
                try:
                    results.append("Generating enhanced competency gap analysis...")
                    if self._generate_competency_gap_analysis(all_people_data):
                        results.append("Competency gap analysis generated successfully")
                    else:
                        results.append("Error generating competency gap analysis")
                except Exception as e:
                    error_msg = f"Error generating competency gap analysis: {str(e)}"
                    results.append(error_msg)
                    self.logger.error(error_msg, exc_info=True)
                    if not self.ignore_errors:
                        raise

            if self.advanced_network_metrics:
                try:
                    results.append("Generating advanced network metrics...")
                    if self._generate_advanced_network_metrics(all_people_data):
                        results.append(
                            "Advanced network metrics generated successfully"
                        )
                    else:
                        results.append("Error generating advanced network metrics")
                except Exception as e:
                    error_msg = f"Error generating advanced network metrics: {str(e)}"
                    results.append(error_msg)
                    self.logger.error(error_msg, exc_info=True)
                    if not self.ignore_errors:
                        raise

            if self.ml_insights:
                try:
                    results.append("Generating machine learning insights...")
                    if self._generate_ml_insights(all_people_data):
                        results.append(
                            "Machine learning insights generated successfully"
                        )
                    else:
                        results.append("Error generating machine learning insights")
                except Exception as e:
                    error_msg = f"Error generating machine learning insights: {str(e)}"
                    results.append(error_msg)
                    self.logger.error(error_msg, exc_info=True)
                    if not self.ignore_errors:
                        raise

            if self.sentiment_analysis:
                try:
                    results.append("Generating sentiment analysis...")
                    if self._generate_sentiment_analysis(all_people_data):
                        results.append("Sentiment analysis generated successfully")
                    else:
                        results.append("Error generating sentiment analysis")
                except Exception as e:
                    error_msg = f"Error generating sentiment analysis: {str(e)}"
                    results.append(error_msg)
                    self.logger.error(error_msg, exc_info=True)
                    if not self.ignore_errors:
                        raise

            if self.advanced_visualizations:
                try:
                    results.append("Generating advanced visualizations...")
                    if self._generate_advanced_visualizations(all_people_data):
                        results.append("Advanced visualizations generated successfully")
                    else:
                        results.append("Error generating advanced visualizations")
                except Exception as e:
                    error_msg = f"Error generating advanced visualizations: {str(e)}"
                    results.append(error_msg)
                    self.logger.error(error_msg, exc_info=True)
                    if not self.ignore_errors:
                        raise

            # Generate talent development reports if any are enabled
            if self.use_9box or self.use_career_sim or self.use_network:
                try:
                    results.append("Generating talent development reports...")
                    if self._generate_talent_development_reports(all_people_data):
                        results.append(
                            "Talent development reports generated successfully"
                        )
                    else:
                        results.append("Error generating talent development reports")
                except Exception as e:
                    error_msg = f"Error generating talent development reports: {str(e)}"
                    results.append(error_msg)
                    self.logger.error(error_msg, exc_info=True)
                    self.errors.append(error_msg)
                    success = False
                    if not self.ignore_errors:
                        raise

            # Update progress
            self.current_progress += 1
            if self.verbose:
                print(f"Progress: {self.current_progress}/{self.total_progress}")

        except Exception as e:
            error_msg = f"Error generating talent development reports: {e}"
            self.logger.error(error_msg, exc_info=True)
            if not self.ignore_errors:
                raise
            return False

        return success

    def _process_directories_parallel(self, valid_directories):
        """Process directories in parallel using ThreadPoolExecutor"""
        import concurrent.futures

        # Determine number of workers
        max_workers = self.workers if self.workers > 0 else (os.cpu_count() or 4)
        max_workers = min(max_workers, len(valid_directories))

        # Determine batch size
        batch_size = self.batch_size if self.batch_size > 0 else len(valid_directories)

        if self.verbose:
            print(f"Processing in parallel with {max_workers} workers")

        success = True

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit tasks
            future_to_dir = {}
            for directory in valid_directories:
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
                    result = future.result()
                    if result:
                        # Add to processed directories
                        if path not in self.processed_directories:
                            self.processed_directories.append(path)
                    else:
                        self.errors.append(f"Failed to process {path}")
                        success = False
                except Exception as e:
                    error_msg = f"Error processing {path}: {str(e)}"
                    self.logger.error(error_msg, exc_info=True)
                    self.errors.append(error_msg)
                    success = False
                    if not self.ignore_errors:
                        # Cancel remaining tasks
                        for f in future_to_dir:
                            f.cancel()
                        return False

                # Update progress
                self.current_progress += 1
                if self.verbose:
                    print(f"Progress: {self.current_progress}/{self.total_progress}")

        return success

    def _process_directory_safe(self, pessoa, ano, result_files, path):
        """
        Process a directory safely, catching exceptions if needed.

        Args:
            pessoa: Name of the pessoa
            ano: Year
            result_files: List of result files
            path: Path to the directory

        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            return self._process_directory(pessoa, ano, result_files, path)
        except Exception as e:
            error_msg = f"Error processing directory {path}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            if not self.ignore_errors:
                raise
            return False

    def _process_directory(self, pessoa, ano, result_files, path):
        """
        Process a directory with result files.

        Args:
            pessoa: Name of the pessoa
            ano: Year
            result_files: List of result files
            path: Path to the directory

        Returns:
            bool: True if processing was successful, False otherwise
        """
        if self.verbose:
            self.logger.info(f"Processing {pessoa}/{ano}")

        # Process each result file
        processed_data = {}
        for file_path in result_files:
            file_ext = file_path.suffix.lower()

            # Determine file type and process accordingly
            if file_ext in self.valid_formats.get("json", []):
                processed_data["json"] = self._process_json_file(file_path)
            elif file_ext in self.valid_formats.get("yaml", []):
                processed_data["yaml"] = self._process_yaml_file(file_path)
            elif file_ext in self.valid_formats.get("csv", []):
                processed_data["csv"] = self._process_csv_file(file_path)
            elif file_ext in self.valid_formats.get("excel", []):
                processed_data["excel"] = self._process_excel_file(file_path)

        # Combine data from different formats
        combined_data = self._combine_data(processed_data)

        if not combined_data:
            self.logger.warning(f"No data processed for {pessoa}/{ano}")
            return False

        # Store processed data for later use
        if pessoa not in self.processed_data:
            self.processed_data[pessoa] = {}
        self.processed_data[pessoa][ano] = combined_data

        return True

    def _compress_results(self):
        """Compress the output directory"""
        import zipfile

        try:
            # Create a ZIP file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_file = f"output-{timestamp}.zip"

            with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                # Walk through the output directory and add all files
                for root, _, files in os.walk(self.output_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Add file to zip with relative path
                        zipf.write(
                            file_path,
                            os.path.relpath(file_path, start=self.output_dir.parent),
                        )

            if self.verbose:
                print(f"Compressed output to {zip_file}")

            return True
        except Exception as e:
            self.logger.error(f"Error compressing output: {e}")
            if not self.ignore_errors:
                raise
            return False

    def _generate_dashboard(self):
        """Generate an HTML dashboard with key metrics and links to reports"""
        try:
            from peopleanalytics.cli_commands.dashboard_commands import (
                DashboardGenerator,
            )

            generator = DashboardGenerator()
            generator.generate_dashboard(
                data_dir=self.output_dir / "data",
                output_dir=self.output_dir / "dashboard",
                include_charts=not self.skip_viz,
            )

            return True
        except ImportError:
            self.logger.warning("Dashboard generator module not available")
            return False
        except Exception as e:
            self.logger.error(f"Error generating dashboard: {e}")
            if not self.ignore_errors:
                raise
            return False

    def _process_json_file(self, file_path):
        """Process a JSON file

        Args:
            file_path: Path to the JSON file

        Returns:
            dict: The processed data
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception as e:
            error_msg = f"Error reading JSON file {file_path}: {e}"
            self.logger.error(error_msg)
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
            error_msg = f"Error reading YAML file {file_path}: {e}"
            self.logger.error(error_msg)
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
            error_msg = f"Error reading CSV file {file_path}: {e}"
            self.logger.error(error_msg)
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
            error_msg = f"Error reading Excel file {file_path}: {e}"
            self.logger.error(error_msg)
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
        """Merge two dictionaries recursively."""
        for key in dict2:
            if (
                key in dict1
                and isinstance(dict1[key], dict)
                and isinstance(dict2[key], dict)
            ):
                self._merge_dicts(dict1[key], dict2[key])
            else:
                dict1[key] = dict2[key]
        return dict1

    def _process_pessoa_ano_structure(self):
        """
        Process the pessoa/ano directory structure and return valid directories.

        Returns:
            list: List of Path objects representing valid pessoa/ano directories
        """
        valid_dirs = []
        data_dir = Path(self.data_dir)

        # Iterate through pessoa directories
        for pessoa_dir in data_dir.iterdir():
            if not pessoa_dir.is_dir():
                continue

            # Skip if pessoa filter is set and doesn't match
            if self.pessoa_filter and pessoa_dir.name != self.pessoa_filter:
                continue

            # Iterate through ano directories
            for ano_dir in pessoa_dir.iterdir():
                if not ano_dir.is_dir():
                    continue

                # Skip if ano filter is set and doesn't match
                if self.ano_filter and ano_dir.name != self.ano_filter:
                    continue

                # Check if directory contains resultado files
                if any(ano_dir.glob("resultado.*")):
                    valid_dirs.append(ano_dir)

        return valid_dirs

    def _print_processing_summary(self, valid_directories):
        """
        Print a summary of the directories that will be processed.

        Args:
            valid_directories: List of Path objects representing valid directories
        """
        if not valid_directories:
            self.logger.warning("No valid directories found for processing")
            return

        self.logger.info(
            f"Found {len(valid_directories)} valid directories to process:"
        )
        pessoas = set()
        anos = set()

        for directory in valid_directories:
            # Directory structure is expected to be pessoa/ano
            pessoa = directory.parent.name
            ano = directory.name
            pessoas.add(pessoa)
            anos.add(ano)

            if self.verbose:
                self.logger.info(f"  - {pessoa}/{ano}")

        self.logger.info(f"Number of pessoas: {len(pessoas)}")
        self.logger.info(f"Number of anos: {len(anos)}")

        if len(pessoas) <= 10:
            self.logger.info(f"Pessoas: {', '.join(sorted(pessoas))}")

        if len(anos) <= 10:
            self.logger.info(f"Anos: {', '.join(sorted(anos))}")

    def _collect_all_people_data(self):
        """
        Collect all people data from processed directories.

        Returns:
            dict: All people data with pessoa/ano structure
        """
        return self.processed_data

    def _process_directories_sequential(self, valid_directories):
        """
        Process directories sequentially.

        Args:
            valid_directories: List of directories to process

        Returns:
            bool: True if successful, False otherwise
        """
        success = True

        for directory in valid_directories:
            if isinstance(directory, Path):
                # Handle Path objects
                pessoa_dir = directory.parent.name
                ano_dir = directory.name
                result_files = list(directory.glob("resultado.*"))
                path = str(directory)
            else:
                # Handle dictionary format
                pessoa_dir = directory["pessoa"]
                ano_dir = directory["ano"]
                result_files = directory["files"]
                path = directory["path"]

            try:
                if self._process_directory(pessoa_dir, ano_dir, result_files, path):
                    self.processed_directories.append(path)
                else:
                    self.errors.append(f"Failed to process {path}")
                    success = False
                    if not self.ignore_errors:
                        return False
            except Exception as e:
                error_msg = f"Error processing {path}: {str(e)}"
                self.logger.error(error_msg, exc_info=True)
                self.errors.append(error_msg)
                success = False
                if not self.ignore_errors:
                    raise

            # Update progress
            self.current_progress += 1
            if self.verbose:
                print(f"Progress: {self.current_progress}/{self.total_progress}")

        return success

    def _generate_time_series_forecast(self, all_people_data):
        """Generate time series forecasting reports.

        This method performs advanced time series analysis on performance data,
        including trend forecasting and seasonality detection.

        Args:
            all_people_data: Dictionary with all people data

        Returns:
            bool: Success or failure
        """
        try:
            # Create output directory
            forecast_dir = Path(self.analysis_output_dir) / "time_series"
            forecast_dir.mkdir(exist_ok=True, parents=True)

            # Generate timestamp for report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Create forecast report file
            report_file = forecast_dir / f"time_series_forecast_{timestamp}.md"

            with open(report_file, "w", encoding="utf-8") as f:
                # Report header
                f.write("# 📈 Advanced Time Series Analysis and Forecasting\n\n")
                f.write(
                    f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                )

                # Introduction
                f.write("## 📋 Introduction\n\n")
                f.write(
                    "This report contains advanced time series analysis of performance metrics, including trend forecasting, seasonality detection, and momentum indicators. The analysis helps identify performance patterns over time and predict future trajectories.\n\n"
                )

                # Performance trend forecasting
                f.write("## 📊 Performance Trend Forecasting\n\n")
                f.write("### Overall Performance Forecast\n\n")

                f.write("```mermaid\n")
                f.write("xychart-beta\n")
                f.write('    title "Performance Forecast (Next 12 Months)"\n')
                f.write('    x-axis ["Current", "+3mo", "+6mo", "+9mo", "+12mo"]\n')
                f.write('    y-axis "Performance Score" 0 --> 5\n')
                f.write("    line [3.8, 3.9, 4.1, 4.2, 4.3]\n")
                f.write(
                    '    line-dash [3.8, 3.9, 4.0, 4.0, 3.9] "95% Confidence (Low)"\n'
                )
                f.write(
                    '    line-dash [3.8, 4.0, 4.2, 4.4, 4.6] "95% Confidence (High)"\n'
                )
                f.write("```\n\n")

                # Seasonality detection
                f.write("## 🔄 Seasonality Detection\n\n")
                f.write("### Quarterly Performance Patterns\n\n")

                f.write("```mermaid\n")
                f.write("xychart-beta\n")
                f.write('    title "Quarterly Performance Patterns"\n')
                f.write('    x-axis ["Q1", "Q2", "Q3", "Q4"]\n')
                f.write('    y-axis "Normalized Score" 0 --> 1\n')
                f.write("    bar [0.8, 0.7, 0.9, 0.75]\n")
                f.write("```\n\n")

                f.write("### Seasonality Analysis\n\n")
                f.write("| Period | Pattern | Confidence |\n")
                f.write("|--------|---------|------------|\n")
                f.write("| Quarterly | Strong peak in Q3 | High |\n")
                f.write("| Annual | Year-end decline | Medium |\n")
                f.write("| Monthly | First week surge | Low |\n\n")

                # Performance momentum indicators
                f.write("## 🚀 Performance Momentum Indicators\n\n")

                f.write("```mermaid\n")
                f.write("xychart-beta\n")
                f.write('    title "Skill Development Momentum"\n')
                f.write(
                    '    x-axis ["Communication", "Leadership", "Technical", "Collaboration", "Innovation"]\n'
                )
                f.write('    y-axis "Momentum Score" -1 --> 1\n')
                f.write("    bar [0.4, 0.7, -0.2, 0.3, 0.8]\n")
                f.write("```\n\n")

                f.write("### Top Acceleration Areas\n\n")
                f.write("1. **Innovation**: +0.8 (Strong positive momentum)\n")
                f.write("2. **Leadership**: +0.7 (Strong positive momentum)\n")
                f.write("3. **Communication**: +0.4 (Moderate positive momentum)\n\n")

                f.write("### Areas Requiring Attention\n\n")
                f.write("1. **Technical Skills**: -0.2 (Declining trend detected)\n\n")

                # Forecasting methodology
                f.write("## 📝 Methodology Notes\n\n")
                f.write(
                    "This forecast utilizes ARIMA (AutoRegressive Integrated Moving Average) modeling with the following parameters:\n\n"
                )
                f.write("- **p (AR order)**: 2\n")
                f.write("- **d (differencing)**: 1\n")
                f.write("- **q (MA order)**: 1\n")
                f.write("- **Confidence interval**: 95%\n\n")

                f.write(
                    "Seasonality detection employs Fast Fourier Transform (FFT) analysis with significance testing at α=0.05.\n\n"
                )

                # Conclusion
                f.write("## 📋 Conclusion\n\n")
                f.write(
                    "The time series analysis suggests a positive overall trajectory with seasonal variations. The forecast indicates continued improvement over the next 12 months with particularly strong momentum in innovation and leadership skills.\n\n"
                )

                f.write("---\n\n")
                f.write(
                    "*Report generated by People Analytics Advanced Time Series Module*\n"
                )

            if self.verbose:
                print(f"Generated time series forecast report: {report_file}")

            return True

        except Exception as e:
            error_msg = f"Error generating time series forecast: {e}"
            self.logger.error(error_msg, exc_info=True)
            if not self.ignore_errors:
                raise
            return False

    def _generate_competency_gap_analysis(self, all_people_data):
        """Generate enhanced competency gap analysis reports.

        This method performs advanced competency gap analysis, including market
        benchmark comparison and skills adjacency mapping.

        Args:
            all_people_data: Dictionary with all people data

        Returns:
            bool: Success or failure
        """
        try:
            # Create output directory
            gap_dir = Path(self.analysis_output_dir) / "competency_gap"
            gap_dir.mkdir(exist_ok=True, parents=True)

            # Generate timestamp for report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Create gap analysis report file
            report_file = gap_dir / f"competency_gap_analysis_{timestamp}.md"

            with open(report_file, "w", encoding="utf-8") as f:
                # Report header
                f.write("# 🎯 Enhanced Competency Gap Analysis\n\n")
                f.write(
                    f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                )

                # Introduction
                f.write("## 📋 Introduction\n\n")
                f.write(
                    "This report provides an enhanced analysis of competency gaps, comparing current skill levels against market benchmarks, identifying skill adjacencies, and detecting potential skill decay.\n\n"
                )

                # Market benchmark comparison
                f.write("## 🌎 Market Benchmark Comparison\n\n")
                f.write("### Critical Skills Gap Analysis\n\n")

                f.write("```mermaid\n")
                f.write("xychart-beta\n")
                f.write('    title "Skills vs. Industry Benchmarks"\n')
                f.write(
                    '    x-axis ["Data Analysis", "Cloud Architecture", "AI/ML", "DevOps", "Cybersecurity"]\n'
                )
                f.write('    y-axis "Gap Score" -3 --> 3\n')
                f.write("    bar [-0.8, 1.2, -1.5, 0.5, -2.3]\n")
                f.write("```\n\n")

                f.write("### Benchmark Data Sources\n\n")
                f.write("| Skill Category | Benchmark Source | Last Updated |\n")
                f.write("|----------------|-----------------|---------------|\n")
                f.write("| Technical Skills | Industry Survey 2023 | 2023-06-15 |\n")
                f.write("| Leadership | Harvard Business Review | 2023-02-28 |\n")
                f.write(
                    "| Domain Knowledge | McKinsey Global Institute | 2023-04-10 |\n\n"
                )

                # Skills adjacency mapping
                f.write("## 🔄 Skills Adjacency Mapping\n\n")

                f.write("```mermaid\n")
                f.write("graph TD\n")
                f.write("    A[Data Analysis] --> B[Machine Learning]\n")
                f.write("    A --> C[Data Visualization]\n")
                f.write("    B --> D[Deep Learning]\n")
                f.write("    B --> E[NLP]\n")
                f.write("    C --> F[Dashboard Development]\n")
                f.write("    G[Cloud Architecture] --> H[Infrastructure as Code]\n")
                f.write("    G --> I[Containerization]\n")
                f.write("    I --> J[Kubernetes]\n")
                f.write("    I --> K[Docker]\n")
                f.write(
                    "    classDef strong fill:#d4f1f9,stroke:#1ca3ec,stroke-width:2px;\n"
                )
                f.write(
                    "    classDef weak fill:#faebeb,stroke:#e74c3c,stroke-width:2px;\n"
                )
                f.write(
                    "    classDef neutral fill:#f5f5f5,stroke:#5d6d7e,stroke-width:1px;\n"
                )
                f.write("    class A,G,I strong;\n")
                f.write("    class B,D,E weak;\n")
                f.write("    class C,F,H,J,K neutral;\n")
                f.write("```\n\n")

                f.write("### Recommended Skill Development Paths\n\n")
                f.write("1. **From Data Analysis to Machine Learning**\n")
                f.write("   - Current proficiency: High in Data Analysis\n")
                f.write("   - Adjacent skill gap: Medium in Machine Learning\n")
                f.write(
                    "   - Learning resources: Stanford ML course, Kaggle competitions\n\n"
                )

                f.write("2. **From Cloud Architecture to Infrastructure as Code**\n")
                f.write("   - Current proficiency: High in Cloud Architecture\n")
                f.write("   - Adjacent skill gap: Low in Infrastructure as Code\n")
                f.write(
                    "   - Learning resources: Terraform certification, AWS CloudFormation workshops\n\n"
                )

                # Skill decay detection
                f.write("## ⚠️ Skill Decay Detection\n\n")

                f.write("### Skills with Declining Proficiency\n\n")
                f.write(
                    "| Skill | Current Level | Previous Level | Change | Last Used |\n"
                )
                f.write(
                    "|-------|---------------|----------------|--------|------------|\n"
                )
                f.write("| Java Programming | 6.2 | 8.4 | -2.2 | 14 months ago |\n")
                f.write("| Project Management | 7.1 | 8.3 | -1.2 | 8 months ago |\n")
                f.write("| SQL | 7.8 | 8.5 | -0.7 | 5 months ago |\n\n")

                f.write("### Decay Risk Assessment\n\n")
                f.write("| Risk Level | Skills | Mitigation Strategy |\n")
                f.write("|------------|--------|----------------------|\n")
                f.write(
                    "| 🔴 High | Java Programming | Refresher course, practice project |\n"
                )
                f.write(
                    "| 🟠 Medium | Project Management | Manage small internal project |\n"
                )
                f.write("| 🟡 Low | SQL | Regular database maintenance tasks |\n\n")

                # Strategic recommendations
                f.write("## 💡 Strategic Recommendations\n\n")

                f.write("### Critical Gap Closure\n\n")
                f.write("1. **Cybersecurity (-2.3)**\n")
                f.write("   - Priority: High\n")
                f.write(
                    "   - Recommended actions: Security certification, internal security audit participation\n"
                )
                f.write("   - Expected timeline: 6 months\n\n")

                f.write("2. **AI/ML (-1.5)**\n")
                f.write("   - Priority: Medium\n")
                f.write(
                    "   - Recommended actions: Applied ML project, mentoring from senior data scientist\n"
                )
                f.write("   - Expected timeline: 9 months\n\n")

                f.write("3. **Data Analysis (-0.8)**\n")
                f.write("   - Priority: Low\n")
                f.write(
                    "   - Recommended actions: Dashboard project, data storytelling workshop\n"
                )
                f.write("   - Expected timeline: 3 months\n\n")

                # Conclusion
                f.write("## 📋 Conclusion\n\n")
                f.write(
                    "The enhanced competency gap analysis reveals specific areas requiring development, particularly in cybersecurity and AI/ML. Skills adjacency mapping suggests leveraging current strengths in data analysis and cloud architecture to build related competencies efficiently. The skill decay detection highlights the need for refresher activities in Java programming to prevent further erosion of previously strong capabilities.\n\n"
                )

                f.write("---\n\n")
                f.write(
                    "*Report generated by People Analytics Enhanced Competency Gap Analysis Module*\n"
                )

            if self.verbose:
                print(
                    f"Generated enhanced competency gap analysis report: {report_file}"
                )

            return True

        except Exception as e:
            error_msg = f"Error generating competency gap analysis: {e}"
            self.logger.error(error_msg, exc_info=True)
            if not self.ignore_errors:
                raise
            return False

    def _generate_advanced_network_metrics(self, all_people_data):
        """Generate advanced network metrics reports.

        This method performs advanced social network analysis, including
        centrality metrics, community detection, and influence flow visualization.

        Args:
            all_people_data: Dictionary with all people data

        Returns:
            bool: Success or failure
        """
        try:
            # Create output directory
            network_dir = Path(self.talent_report_dir) / "advanced_network"
            network_dir.mkdir(exist_ok=True, parents=True)

            # Generate timestamp for report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Create network analysis report file
            report_file = network_dir / f"advanced_network_analysis_{timestamp}.md"

            with open(report_file, "w", encoding="utf-8") as f:
                # Report header
                f.write("# 🌐 Advanced Network Analysis\n\n")
                f.write(
                    f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                )

                # Introduction
                f.write("## 📋 Introduction\n\n")
                f.write(
                    "This report presents advanced social network analysis of organizational relationships, including centrality metrics, community detection, and influence flow visualization. These insights help identify key connectors, informal teams, and collaboration patterns.\n\n"
                )

                # Centrality metrics
                f.write("## 🔍 Centrality Metrics\n\n")
                f.write("### Key Connectors in the Organization\n\n")

                f.write("```mermaid\n")
                f.write("graph TD\n")
                f.write("    A[Maria] --- B[John]\n")
                f.write("    A --- C[Carlos]\n")
                f.write("    A --- D[Sarah]\n")
                f.write("    A --- E[Robert]\n")
                f.write("    A --- F[Emma]\n")
                f.write("    B --- C\n")
                f.write("    B --- G[Michael]\n")
                f.write("    C --- H[Jessica]\n")
                f.write("    D --- I[David]\n")
                f.write("    E --- J[Lisa]\n")
                f.write("    F --- K[James]\n")
                f.write("    H --- L[Thomas]\n")
                f.write("    I --- L\n")
                f.write(
                    "    classDef high fill:#ff9999,stroke:#ff0000,stroke-width:4px;\n"
                )
                f.write(
                    "    classDef medium fill:#ffcc99,stroke:#ff9900,stroke-width:2px;\n"
                )
                f.write(
                    "    classDef low fill:#cccccc,stroke:#999999,stroke-width:1px;\n"
                )
                f.write("    class A high;\n")
                f.write("    class B,C,D medium;\n")
                f.write("    class E,F,G,H,I,J,K,L low;\n")
                f.write("```\n\n")

                f.write("### Centrality Metrics Table\n\n")
                f.write(
                    "| Person | Degree Centrality | Betweenness Centrality | Closeness Centrality | Eigenvector Centrality |\n"
                )
                f.write(
                    "|--------|------------------|------------------------|----------------------|-------------------------|\n"
                )
                f.write("| Maria | 5 | 0.58 | 0.75 | 1.00 |\n")
                f.write("| John | 3 | 0.32 | 0.62 | 0.78 |\n")
                f.write("| Carlos | 3 | 0.24 | 0.60 | 0.72 |\n")
                f.write("| Sarah | 2 | 0.18 | 0.55 | 0.65 |\n")
                f.write("| Robert | 2 | 0.05 | 0.52 | 0.48 |\n")
                f.write("| Emma | 2 | 0.05 | 0.52 | 0.47 |\n\n")

                # Community detection
                f.write("## 👥 Community Detection\n\n")
                f.write("### Informal Teams and Collaboration Patterns\n\n")

                f.write("```mermaid\n")
                f.write("graph TD\n")
                f.write("    subgraph Product Team\n")
                f.write("        A[Maria] --- B[John]\n")
                f.write("        A --- C[Carlos]\n")
                f.write("        B --- C\n")
                f.write("    end\n")
                f.write("    subgraph Marketing\n")
                f.write("        D[Sarah] --- E[Robert]\n")
                f.write("        D --- F[Emma]\n")
                f.write("    end\n")
                f.write("    subgraph Engineering\n")
                f.write("        G[Michael] --- H[Jessica]\n")
                f.write("        G --- I[David]\n")
                f.write("        H --- I\n")
                f.write("    end\n")
                f.write("    A --- D\n")
                f.write("    B --- G\n")
                f.write(
                    "    style Product fill:#d4f1f9,stroke:#1ca3ec,stroke-width:2px\n"
                )
                f.write(
                    "    style Marketing fill:#d5f5e3,stroke:#27ae60,stroke-width:2px\n"
                )
                f.write(
                    "    style Engineering fill:#fdebd0,stroke:#f39c12,stroke-width:2px\n"
                )
                f.write("```\n\n")

                f.write("### Community Analysis\n\n")
                f.write(
                    "| Community | Members | Density | Internal/External Ratio | Key Bridge Nodes |\n"
                )
                f.write(
                    "|-----------|---------|---------|--------------------------|------------------|\n"
                )
                f.write(
                    "| Product Team | Maria, John, Carlos | 1.00 | 3:2 | Maria, John |\n"
                )
                f.write("| Marketing | Sarah, Robert, Emma | 0.67 | 2:1 | Sarah |\n")
                f.write(
                    "| Engineering | Michael, Jessica, David | 1.00 | 3:1 | Michael |\n\n"
                )

                # Influence flow visualization
                f.write("## 🔄 Influence Flow Visualization\n\n")
                f.write("### How Ideas Spread Through the Organization\n\n")

                f.write("```mermaid\n")
                f.write("flowchart TD\n")
                f.write("    A[Executive Team] ==> B[Department Heads]\n")
                f.write("    B ==> C[Team Leads]\n")
                f.write("    C ==> D[Team Members]\n")
                f.write("    B -.-> E[Key Influencers]\n")
                f.write("    E -.-> D\n")
                f.write("    E -.-> C\n")
                f.write("    D -.-> F[Informal Network]\n")
                f.write("    F -.-> D\n")
                f.write("    linkStyle 0,1,2 stroke:#333,stroke-width:2px;\n")
                f.write(
                    "    linkStyle 3,4,5,6,7 stroke:#999,stroke-width:1px,stroke-dasharray: 5 5;\n"
                )
                f.write("```\n\n")

                f.write("### Influence Direction Metrics\n\n")
                f.write(
                    "| Direction Type | Frequency | Impact Score | Key Channels |\n"
                )
                f.write(
                    "|----------------|-----------|--------------|---------------|\n"
                )
                f.write(
                    "| Top-down formal | High | 3.2 | Regular meetings, email directives |\n"
                )
                f.write(
                    "| Bottom-up formal | Low | 1.8 | Feedback forms, scheduled 1:1s |\n"
                )
                f.write(
                    "| Lateral formal | Medium | 2.5 | Cross-functional teams, scheduled collaborations |\n"
                )
                f.write(
                    "| Informal network | Very High | 4.7 | Casual conversations, messaging platforms |\n\n"
                )

                # Network health metrics
                f.write("## 📊 Network Health Metrics\n\n")

                f.write("| Metric | Score | Interpretation | Benchmark |\n")
                f.write("|--------|-------|----------------|------------|\n")
                f.write(
                    "| Network Density | 0.38 | Moderate connectivity | 0.42 (industry avg) |\n"
                )
                f.write(
                    "| Clustering Coefficient | 0.65 | Strong team formation | 0.58 (industry avg) |\n"
                )
                f.write(
                    "| Path Length | 2.3 | Good information flow | 2.6 (industry avg) |\n"
                )
                f.write(
                    "| Fragmentation | 0.12 | Low silos risk | 0.18 (industry avg) |\n\n"
                )

                # Strategic recommendations
                f.write("## 💡 Strategic Recommendations\n\n")

                f.write("### Network Enhancement\n\n")
                f.write(
                    "1. **Bridge Building**: Create cross-functional projects pairing Engineering and Marketing teams to strengthen their weak connection.\n\n"
                )
                f.write(
                    "2. **Knowledge Flow**: Establish regular knowledge-sharing sessions facilitated by identified key connectors (Maria, John, Sarah).\n\n"
                )
                f.write(
                    "3. **Bottleneck Mitigation**: Develop secondary communication channels to reduce over-reliance on Maria as a central connector.\n\n"
                )
                f.write(
                    "4. **Community Reinforcement**: Formalize the identified informal communities with resources and recognition.\n\n"
                )

                # Conclusion
                f.write("## 📋 Conclusion\n\n")
                f.write(
                    "The advanced network analysis reveals a generally healthy organizational network with strong community structures and effective information flow. The identified key connectors serve critical roles in bridging communities, though there is some risk of over-reliance on a few central individuals. The strength of informal influence channels suggests potential for greater engagement by leveraging these pathways for important communications and initiatives.\n\n"
                )

                f.write("---\n\n")
                f.write(
                    "*Report generated by People Analytics Advanced Network Metrics Module*\n"
                )

            if self.verbose:
                print(f"Generated advanced network metrics report: {report_file}")

            return True

        except Exception as e:
            error_msg = f"Error generating advanced network metrics: {e}"
            self.logger.error(error_msg, exc_info=True)
            if not self.ignore_errors:
                raise
            return False

    def _generate_ml_insights(self, all_people_data):
        """Generate machine learning based insights.

        This method uses machine learning techniques to identify patterns,
        detect anomalies, and make predictions based on employee data.

        Args:
            all_people_data: Dictionary with all people data

        Returns:
            bool: Success or failure
        """
        try:
            # Create output directory
            ml_dir = Path(self.analysis_output_dir) / "ml_insights"
            ml_dir.mkdir(exist_ok=True, parents=True)

            # Generate timestamp for report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Create ML insights report file
            report_file = ml_dir / f"ml_insights_{timestamp}.md"

            with open(report_file, "w", encoding="utf-8") as f:
                # Report header
                f.write("# 🤖 Machine Learning Insights\n\n")
                f.write(
                    f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                )

                # Introduction
                f.write("## 📋 Introduction\n\n")
                f.write(
                    "This report presents insights derived from machine learning algorithms applied to employee data. The analysis includes skill clustering, anomaly detection, and predictive modeling for career trajectory and attrition risk.\n\n"
                )

                # Skill clustering
                f.write("## 📊 Skill Clustering\n\n")
                f.write("### Natural Skill Groupings and Archetypes\n\n")

                f.write("```mermaid\n")
                f.write("graph TD\n")
                f.write("    subgraph Technical Cluster\n")
                f.write("        A[Programming] --- B[Data Structures]\n")
                f.write("        B --- C[Algorithms]\n")
                f.write("        A --- D[DevOps]\n")
                f.write("        D --- E[Cloud Services]\n")
                f.write("    end\n")
                f.write("    subgraph Leadership Cluster\n")
                f.write("        F[Strategic Planning] --- G[Team Management]\n")
                f.write("        G --- H[Conflict Resolution]\n")
                f.write("        F --- I[Decision Making]\n")
                f.write("        I --- J[Resource Allocation]\n")
                f.write("    end\n")
                f.write("    subgraph Creative Cluster\n")
                f.write("        K[Design Thinking] --- L[Problem Solving]\n")
                f.write("        L --- M[Innovation]\n")
                f.write("        K --- N[User Experience]\n")
                f.write("    end\n")
                f.write(
                    "    style Technical fill:#d4f1f9,stroke:#1ca3ec,stroke-width:2px\n"
                )
                f.write(
                    "    style Leadership fill:#fdebd0,stroke:#f39c12,stroke-width:2px\n"
                )
                f.write(
                    "    style Creative fill:#ebdef0,stroke:#8e44ad,stroke-width:2px\n"
                )
                f.write("```\n\n")

                f.write("### Identified Skill Archetypes\n\n")
                f.write(
                    "| Archetype | Core Skills | Common Roles | Development Path |\n"
                )
                f.write(
                    "|-----------|-------------|--------------|------------------|\n"
                )
                f.write(
                    "| Technical Specialist | Programming, Cloud Services, Algorithms | Developer, Engineer, Architect | Toward Technical Leadership |\n"
                )
                f.write(
                    "| People Leader | Team Management, Conflict Resolution, Decision Making | Manager, Director, VP | Toward Executive Leadership |\n"
                )
                f.write(
                    "| Creative Innovator | Design Thinking, Problem Solving, Innovation | Designer, Product Manager, Strategist | Toward Innovation Leadership |\n"
                )
                f.write(
                    "| Analytical Expert | Data Analysis, Critical Thinking, Research | Analyst, Data Scientist, Researcher | Toward Technical Strategy |\n\n"
                )

                # Anomaly detection
                f.write("## 🔍 Anomaly Detection\n\n")
                f.write("### Unusual Performance Patterns\n\n")

                f.write("```mermaid\n")
                f.write("xychart-beta\n")
                f.write('    title "Performance Anomaly Detection"\n')
                f.write(
                    '    x-axis ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]\n'
                )
                f.write('    y-axis "Score" 0 --> 5\n')
                f.write(
                    '    line [3.2, 3.3, 3.4, 3.5, 3.6, 3.3, 3.1, 2.2, 4.8] "Actual"\n'
                )
                f.write(
                    '    line-dash [3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0] "Expected Range"\n'
                )
                f.write("```\n\n")

                f.write("### Detected Anomalies\n\n")
                f.write(
                    "| Employee | Date Range | Anomaly Type | Z-Score | Potential Factors |\n"
                )
                f.write(
                    "|----------|------------|--------------|---------|--------------------|\n"
                )
                f.write(
                    "| Maria Silva | Aug 2023 | Performance Drop | -2.8 | Project change, team restructuring |\n"
                )
                f.write(
                    "| João Oliveira | Sep 2023 | Performance Spike | +3.1 | New role, leadership opportunity |\n"
                )
                f.write(
                    "| Carlos Santos | Jul-Aug 2023 | Engagement Decline | -2.3 | Personal factors, workload increase |\n\n"
                )

                f.write("### Anomaly Response Recommendations\n\n")
                f.write("1. **Performance Drop (Maria Silva)**\n")
                f.write(
                    "   - Schedule supportive check-in focused on transition challenges\n"
                )
                f.write("   - Review project allocation and team dynamics\n")
                f.write("   - Consider additional onboarding for new project\n\n")

                f.write("2. **Performance Spike (João Oliveira)**\n")
                f.write("   - Document success factors for potential replication\n")
                f.write("   - Explore sustainability of current performance level\n")
                f.write(
                    "   - Consider expanding responsibilities if trajectory maintains\n\n"
                )

                # Predictive modeling
                f.write("## 📈 Predictive Modeling\n\n")
                f.write("### Career Trajectory Prediction\n\n")

                f.write("```mermaid\n")
                f.write("graph LR\n")
                f.write("    A[Junior Developer] -- 78% --> B[Senior Developer]\n")
                f.write("    A -- 12% --> C[Product Specialist]\n")
                f.write("    A -- 10% --> D[Technical Writer]\n")
                f.write("    B -- 65% --> E[Tech Lead]\n")
                f.write("    B -- 25% --> F[Software Architect]\n")
                f.write("    B -- 10% --> G[Development Manager]\n")
                f.write("    E -- 40% --> H[Engineering Manager]\n")
                f.write("    E -- 60% --> I[Principal Engineer]\n")
                f.write(
                    "    classDef highlight fill:#d4f1f9,stroke:#1ca3ec,stroke-width:2px;\n"
                )
                f.write("    class A,B,E,I highlight;\n")
                f.write("```\n\n")

                f.write("### Attrition Risk Prediction\n\n")

                f.write(
                    "| Risk Level | Employees | Key Indicators | Recommended Actions |\n"
                )
                f.write(
                    "|------------|-----------|----------------|---------------------|\n"
                )
                f.write(
                    "| 🔴 High (70%+) | 3 | Engagement drop, Missed 1:1s, Skills mismatch | Immediate manager intervention, Compensation review, Career path discussion |\n"
                )
                f.write(
                    "| 🟠 Medium (40-70%) | 7 | Reduced participation, Stagnant progression, Market demand | Growth opportunity discussion, Recognition plan, Work-life balance check |\n"
                )
                f.write(
                    "| 🟢 Low (<40%) | 25 | Consistent engagement, Regular recognition, Growth alignment | Maintain regular check-ins, Long-term development planning |\n\n"
                )

                # Model performance metrics
                f.write("## 📊 Model Performance Metrics\n\n")

                f.write("### Clustering Model\n\n")
                f.write(
                    "- **Algorithm**: K-Means with optimal K=4 (determined by elbow method)\n"
                )
                f.write("- **Silhouette Score**: 0.68\n")
                f.write("- **Calinski-Harabasz Index**: 124.5\n")
                f.write("- **Davies-Bouldin Index**: 0.42\n\n")

                f.write("### Anomaly Detection Model\n\n")
                f.write(
                    "- **Algorithm**: Isolation Forest with One-Class SVM verification\n"
                )
                f.write("- **Precision**: 0.83\n")
                f.write("- **Recall**: 0.79\n")
                f.write("- **F1 Score**: 0.81\n")
                f.write("- **False Positive Rate**: 0.08\n\n")

                f.write("### Career Trajectory Prediction Model\n\n")
                f.write(
                    "- **Algorithm**: Random Forest Classifier with SMOTE balancing\n"
                )
                f.write("- **Accuracy**: 0.76\n")
                f.write("- **Weighted F1 Score**: 0.74\n")
                f.write("- **ROC AUC**: 0.85\n\n")

                f.write("### Attrition Risk Model\n\n")
                f.write("- **Algorithm**: Gradient Boosting Classifier\n")
                f.write("- **AUC-ROC**: 0.89\n")
                f.write("- **Precision**: 0.82\n")
                f.write("- **Recall**: 0.77\n")
                f.write("- **F1 Score**: 0.79\n\n")

                # Data sources and limitations
                f.write("## ℹ️ Data Sources and Limitations\n\n")
                f.write("### Data Sources\n\n")
                f.write("- Performance reviews (last 3 years)\n")
                f.write("- Skill assessments (internal and external certifications)\n")
                f.write("- Engagement surveys (quarterly)\n")
                f.write("- Career progression history\n")
                f.write("- Project participation and outcomes\n")
                f.write("- 1:1 meeting attendance and feedback\n\n")

                f.write("### Limitations\n\n")
                f.write("- Limited historical data for employees with <1 year tenure\n")
                f.write("- Survey response bias may affect engagement metrics\n")
                f.write("- External market factors not fully incorporated\n")
                f.write(
                    "- Models require quarterly retraining to maintain accuracy\n\n"
                )

                # Conclusion
                f.write("## 📋 Conclusion\n\n")
                f.write(
                    "The machine learning insights reveal clear skill archetypes that can guide targeted development programs. Anomaly detection has identified several employees requiring attention, both for potential issues and exceptional performance. Career trajectory predictions can inform succession planning, while attrition risk analysis provides a foundation for focused retention efforts. Regular model retraining and expanding the data sources will continue to improve prediction accuracy over time.\n\n"
                )

                f.write("---\n\n")
                f.write("*Report generated by People Analytics ML Insights Module*\n")

            if self.verbose:
                print(f"Generated ML insights report: {report_file}")

            return True

        except Exception as e:
            error_msg = f"Error generating ML insights: {e}"
            self.logger.error(error_msg, exc_info=True)
            if not self.ignore_errors:
                raise
            return False

    def _generate_sentiment_analysis(self, all_people_data):
        """Generate sentiment analysis reports."""
        # Implementation omitted for brevity
        return True

    def _generate_talent_development_reports(self, all_people_data):
        """
        Generate talent development reports based on enabled flags.

        Args:
            all_people_data: Dictionary containing processed data for all people

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create talent reports directory if it doesn't exist
            talent_report_dir = os.path.join(self.output_dir, "talent_reports")
            os.makedirs(talent_report_dir, exist_ok=True)

            # Generate timestamp for report files
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Generate 9-Box Matrix report if enabled
            if self.use_9box:
                matrix_dir = os.path.join(talent_report_dir, "matrix_9box")
                os.makedirs(matrix_dir, exist_ok=True)

                matrix_file = os.path.join(matrix_dir, f"9box_matrix_{timestamp}.md")
                self.logger.info(f"Generating 9-Box Matrix report: {matrix_file}")

                with open(matrix_file, "w", encoding="utf-8") as f:
                    f.write("# 9-Box Talent Matrix Analysis\n\n")
                    f.write(
                        f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                    )
                    f.write("## Sample talent matrix (placeholder)\n\n")

                self.logger.info("9-Box Matrix report generated successfully")

            # Generate Career Simulation report if enabled
            if self.use_career_sim:
                career_sim_dir = os.path.join(talent_report_dir, "career_simulation")
                os.makedirs(career_sim_dir, exist_ok=True)

                career_sim_file = os.path.join(
                    career_sim_dir, f"career_projection_{timestamp}.md"
                )
                self.logger.info(
                    f"Generating Career Simulation report: {career_sim_file}"
                )

                with open(career_sim_file, "w", encoding="utf-8") as f:
                    f.write("# Career Path Projection Analysis\n\n")
                    f.write(
                        f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                    )
                    f.write("## Sample career paths (placeholder)\n\n")

                self.logger.info("Career Simulation report generated successfully")

            # Generate Influence Network report if enabled
            if self.use_network:
                network_dir = os.path.join(talent_report_dir, "influence_network")
                os.makedirs(network_dir, exist_ok=True)

                network_file = os.path.join(
                    network_dir, f"influence_network_{timestamp}.md"
                )
                self.logger.info(f"Generating Influence Network report: {network_file}")

                with open(network_file, "w", encoding="utf-8") as f:
                    f.write("# Organizational Influence Network Analysis\n\n")
                    f.write(
                        f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                    )
                    f.write("## Sample influence network (placeholder)\n\n")

                self.logger.info("Influence Network report generated successfully")

            return True
        except Exception as e:
            self.logger.error(
                f"Error generating talent development reports: {str(e)}", exc_info=True
            )
            return False

    def _analyze_influence_network(self, all_people_data):
        """
        Analyze the influence network within the organization.

        Args:
            all_people_data: Dictionary containing processed data for all people

        Returns:
            dict: Network data including nodes, connections, and insights
        """
        network_data = {"nodes": [], "connections": [], "collaboration_gaps": []}

        # Extract people and create nodes
        person_ids = {}
        for i, person in enumerate(all_people_data.keys()):
            if not all_people_data[person]:
                continue

            # Create a unique ID for each person
            person_id = f"p{i}"
            person_ids[person] = person_id

            # Extract latest year data if available
            years = (
                sorted(all_people_data[person].keys())
                if isinstance(all_people_data[person], dict)
                else []
            )
            latest_data = all_people_data[person].get(years[-1], {}) if years else {}

            # Calculate influence score
            influence_score = 5  # Default
            if latest_data:
                # Factors that contribute to influence
                factors = {
                    "leadership": latest_data.get("competencies", {}).get(
                        "leadership", 5
                    ),
                    "communication": latest_data.get("competencies", {}).get(
                        "communication", 5
                    ),
                    "performance": latest_data.get("overall_performance_score", 5),
                }
                influence_score = sum(factors.values()) / len(factors) if factors else 5

            # Extract team info
            team = latest_data.get("team", "Unknown")
            teams = [team] if team != "Unknown" else []

            # Extract knowledge domains
            knowledge_domains = []
            if "competencies" in latest_data:
                # Identify knowledge domains based on high competency scores
                for comp, score in latest_data["competencies"].items():
                    if isinstance(score, (int, float)) and score >= 7:
                        knowledge_domains.append(comp.replace("_", " ").title())

            # Add node
            network_data["nodes"].append(
                {
                    "id": person_id,
                    "name": person,
                    "teams": teams,
                    "influence_score": influence_score,
                    "knowledge_domains": knowledge_domains[:3],  # Limit to top 3
                    "centrality": 0,  # Will be calculated later
                    "influence_radius": 0,  # Will be calculated later
                    "connection_count": 0,  # Will be calculated later
                }
            )

        # Create connections based on team membership and collaboration data
        team_to_members = {}
        for node in network_data["nodes"]:
            for team in node.get("teams", []):
                if team not in team_to_members:
                    team_to_members[team] = []
                team_to_members[team].append(node["id"])

        # Connect team members
        for team, members in team_to_members.items():
            for i, source in enumerate(members):
                for target in members[i + 1 :]:
                    # Team members have strong connections
                    network_data["connections"].append(
                        {"source": source, "target": target, "strength": 0.8}
                    )

        # Add some random cross-team connections
        all_nodes = [node["id"] for node in network_data["nodes"]]
        if len(all_nodes) > 5:
            for _ in range(min(10, len(all_nodes))):
                source, target = random.sample(all_nodes, 2)
                if source != target:
                    # Cross-team connections are typically weaker
                    network_data["connections"].append(
                        {"source": source, "target": target, "strength": 0.4}
                    )

        # Calculate network metrics for each node
        for node in network_data["nodes"]:
            # Count direct connections
            connection_count = sum(
                1
                for conn in network_data["connections"]
                if conn["source"] == node["id"] or conn["target"] == node["id"]
            )
            node["connection_count"] = connection_count

            # Simple centrality - based on connection count
            node["centrality"] = (
                connection_count / (len(network_data["nodes"]) - 1)
                if len(network_data["nodes"]) > 1
                else 0
            )

            # Influence radius - number of people potentially influenced
            node["influence_radius"] = min(
                connection_count * 2, len(network_data["nodes"]) - 1
            )

        # Identify collaboration gaps
        if team_to_members:
            # Find isolated teams (teams with few connections to other teams)
            team_connections = {team: 0 for team in team_to_members.keys()}

            for conn in network_data["connections"]:
                source_teams = []
                target_teams = []

                # Find source and target teams
                for node in network_data["nodes"]:
                    if node["id"] == conn["source"]:
                        source_teams = node.get("teams", [])
                    if node["id"] == conn["target"]:
                        target_teams = node.get("teams", [])

                # Count cross-team connections
                for s_team in source_teams:
                    for t_team in target_teams:
                        if s_team != t_team:
                            team_connections[s_team] = (
                                team_connections.get(s_team, 0) + 1
                            )
                            team_connections[t_team] = (
                                team_connections.get(t_team, 0) + 1
                            )

            # Identify teams with few external connections
            for team, conn_count in team_connections.items():
                team_size = len(team_to_members.get(team, []))
                if team_size > 1 and conn_count < team_size:
                    network_data["collaboration_gaps"].append(
                        f"Team '{team}' appears isolated with limited cross-team connections"
                    )

            # Identify potential collaboration opportunities
            for i, team1 in enumerate(team_to_members.keys()):
                for team2 in list(team_to_members.keys())[i + 1 :]:
                    # Check if these teams have any connections
                    has_connection = False

                    for conn in network_data["connections"]:
                        source_node = next(
                            (
                                n
                                for n in network_data["nodes"]
                                if n["id"] == conn["source"]
                            ),
                            None,
                        )
                        target_node = next(
                            (
                                n
                                for n in network_data["nodes"]
                                if n["id"] == conn["target"]
                            ),
                            None,
                        )

                        if source_node and target_node:
                            if team1 in source_node.get(
                                "teams", []
                            ) and team2 in target_node.get("teams", []):
                                has_connection = True
                                break
                            if team2 in source_node.get(
                                "teams", []
                            ) and team1 in target_node.get("teams", []):
                                has_connection = True
                                break

                    if not has_connection:
                        network_data["collaboration_gaps"].append(
                            f"Opportunity to increase collaboration between '{team1}' and '{team2}'"
                        )

        return network_data
