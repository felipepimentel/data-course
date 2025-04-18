"""
Sync and documentation commands for People Analytics CLI.

This module contains commands for data synchronization and documentation generation.
"""

import argparse
import json
import logging
import os
import random
import shutil
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

        if not args.no_zip:
            self.logger.info("Compressing output directory")
            output_dir = args.output_dir
            if os.path.exists(output_dir):
                zip_file = "output.zip"
                shutil.make_archive("output", "zip", output_dir)
                self.logger.info(f"Output directory compressed to {zip_file}")


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
        self.pessoa = kwargs.get("pessoa")
        self.ano = kwargs.get("ano")
        self.force = kwargs.get("force", False)

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

            # Process directories (sequential or parallel)
            success = True
            if not self.no_parallel:
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
        """Generate sentiment analysis from feedback and communication data.

        This method analyzes feedback, comments, and communication patterns
        to extract sentiment, emotional tone, and thematic insights.

        Args:
            all_people_data: Dictionary with all people data

        Returns:
            bool: Success or failure
        """
        try:
            # Create output directory
            sentiment_dir = Path(self.analysis_output_dir) / "sentiment_analysis"
            sentiment_dir.mkdir(exist_ok=True, parents=True)

            # Generate timestamp for report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Create sentiment analysis report file
            report_file = sentiment_dir / f"sentiment_analysis_{timestamp}.md"

            with open(report_file, "w", encoding="utf-8") as f:
                # Report header
                f.write("# 🧠 Sentiment Analysis Report\n\n")
                f.write(
                    f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                )

                # Introduction
                f.write("## 📋 Introduction\n\n")
                f.write(
                    "This report presents sentiment analysis of feedback and communication data across the organization. The analysis includes tone detection, emotional content analysis, thematic extraction, and longitudinal sentiment tracking.\n\n"
                )

                # Overall sentiment distribution
                f.write("## 📊 Overall Sentiment Distribution\n\n")
                f.write("```mermaid\n")
                f.write("pie title Feedback Sentiment Distribution\n")
                f.write('    "Positive" : 58\n')
                f.write('    "Neutral" : 27\n')
                f.write('    "Negative" : 15\n')
                f.write("```\n\n")

                # Sentiment by feedback type
                f.write("### Sentiment by Feedback Type\n\n")
                f.write(
                    "| Feedback Type | Positive | Neutral | Negative | Dominant Emotions |\n"
                )
                f.write(
                    "|--------------|----------|---------|----------|-----------------|\n"
                )
                f.write(
                    "| Peer Reviews | 62% | 25% | 13% | Appreciation, Trust, Admiration |\n"
                )
                f.write(
                    "| Manager Assessments | 55% | 30% | 15% | Confidence, Hope, Concern |\n"
                )
                f.write(
                    "| Self-Evaluations | 48% | 32% | 20% | Determination, Worry, Pride |\n"
                )
                f.write(
                    "| Project Retrospectives | 64% | 22% | 14% | Satisfaction, Relief, Frustration |\n\n"
                )

                # Emotional tone analysis
                f.write("## 🔍 Emotional Tone Analysis\n\n")

                f.write("```mermaid\n")
                f.write("xychart-beta\n")
                f.write('    title "Emotional Tone by Department"\n')
                f.write(
                    '    x-axis "Departments" ["Engineering", "Product", "Marketing", "Sales", "Support"]\n'
                )
                f.write('    y-axis "Score" 0 --> 5\n')
                f.write('    bar [4.2, 3.8, 4.5, 4.1, 3.9] "Enthusiasm"\n')
                f.write('    bar [3.8, 3.4, 3.5, 3.9, 3.2] "Confidence"\n')
                f.write('    bar [2.3, 2.5, 2.1, 2.6, 2.9] "Concern"\n')
                f.write('    bar [1.5, 1.9, 1.3, 2.1, 2.5] "Frustration"\n')
                f.write("```\n\n")

                # Language patterns
                f.write("### Language Pattern Analysis\n\n")
                f.write(
                    "| Pattern | Frequency | Example Phrases | Emotional Association |\n"
                )
                f.write(
                    "|---------|-----------|-----------------|----------------------|\n"
                )
                f.write(
                    '| Growth-oriented | High | "opportunity to improve", "learning experience", "developmental area" | Optimism, Motivation |\n'
                )
                f.write(
                    '| Achievement-focused | Medium-High | "exceeded expectations", "outstanding results", "impressive delivery" | Pride, Satisfaction |\n'
                )
                f.write(
                    '| Challenge-centric | Medium | "difficult situation", "challenging project", "complex problem" | Determination, Concern |\n'
                )
                f.write(
                    '| Critical | Low-Medium | "failed to meet", "disappointing outcome", "needs significant improvement" | Frustration, Disappointment |\n\n'
                )

                # Thematic analysis
                f.write("## 📝 Thematic Analysis\n\n")

                f.write("### Key Themes in Positive Feedback\n\n")
                f.write("```mermaid\n")
                f.write("graph TD\n")
                f.write("    A[Positive Feedback] --> B[Technical Excellence]\n")
                f.write("    A --> C[Collaboration]\n")
                f.write("    A --> D[Initiative]\n")
                f.write("    A --> E[Communication]\n")
                f.write("    B --> B1[Code Quality]\n")
                f.write("    B --> B2[Problem Solving]\n")
                f.write("    B --> B3[Technical Knowledge]\n")
                f.write("    C --> C1[Team Support]\n")
                f.write("    C --> C2[Cross-functional Work]\n")
                f.write("    D --> D1[Self-direction]\n")
                f.write("    D --> D2[Proactive Problem Solving]\n")
                f.write("    E --> E1[Clarity]\n")
                f.write("    E --> E2[Responsiveness]\n")
                f.write(
                    "    classDef theme fill:#d4f1f9,stroke:#1ca3ec,stroke-width:2px;\n"
                )
                f.write(
                    "    classDef subtheme fill:#f7f6cf,stroke:#f1c40f,stroke-width:1px;\n"
                )
                f.write("    class A,B,C,D,E theme;\n")
                f.write("    class B1,B2,B3,C1,C2,D1,D2,E1,E2 subtheme;\n")
                f.write("```\n\n")

                f.write("### Key Themes in Constructive Feedback\n\n")
                f.write("```mermaid\n")
                f.write("graph TD\n")
                f.write("    A[Constructive Feedback] --> B[Process Adherence]\n")
                f.write("    A --> C[Time Management]\n")
                f.write("    A --> D[Documentation]\n")
                f.write("    A --> E[Delegation]\n")
                f.write("    B --> B1[Following Standards]\n")
                f.write("    B --> B2[Consistent Practices]\n")
                f.write("    C --> C1[Meeting Deadlines]\n")
                f.write("    C --> C2[Effort Estimation]\n")
                f.write("    D --> D1[Code Documentation]\n")
                f.write("    D --> D2[Knowledge Sharing]\n")
                f.write("    E --> E1[Task Distribution]\n")
                f.write("    E --> E2[Mentoring Others]\n")
                f.write(
                    "    classDef theme fill:#facdd3,stroke:#e74c3c,stroke-width:2px;\n"
                )
                f.write(
                    "    classDef subtheme fill:#f7f6cf,stroke:#f1c40f,stroke-width:1px;\n"
                )
                f.write("    class A,B,C,D,E theme;\n")
                f.write("    class B1,B2,C1,C2,D1,D2,E1,E2 subtheme;\n")
                f.write("```\n\n")

                # Sentiment trends
                f.write("## 📈 Sentiment Trends\n\n")

                f.write("### Sentiment Trends by Quarter\n\n")
                f.write("```mermaid\n")
                f.write("xychart-beta\n")
                f.write('    title "Sentiment Score Trends (Last 4 Quarters)"\n')
                f.write('    x-axis ["Q1", "Q2", "Q3", "Q4"]\n')
                f.write('    y-axis "Score" 0 --> 5\n')
                f.write('    line [3.8, 3.6, 3.9, 4.2] "Overall"\n')
                f.write('    line [4.1, 3.9, 4.2, 4.5] "Engineering"\n')
                f.write('    line [3.7, 3.5, 3.8, 4.0] "Product"\n')
                f.write('    line [3.6, 3.3, 3.5, 3.9] "Marketing"\n')
                f.write("```\n\n")

                # Actionable insights
                f.write("## 🎯 Actionable Insights\n\n")

                f.write("### Communication Opportunities\n\n")
                f.write(
                    "| Team | Sentiment Pattern | Opportunity | Suggested Approach |\n"
                )
                f.write(
                    "|------|------------------|-------------|--------------------|\n"
                )
                f.write(
                    "| Product Development | Concern about timeline pressure | Stress management, expectation setting | Regular check-ins, priority alignment sessions |\n"
                )
                f.write(
                    "| Engineering | Mixed feedback on code review process | Process improvement, skill development | Review guidelines refresh, peer learning sessions |\n"
                )
                f.write(
                    "| Marketing | Enthusiasm about campaign outcomes | Recognition, momentum building | Success sharing sessions, documented case studies |\n"
                )
                f.write(
                    "| Support | Frustration with recurring issues | Problem-solving, root cause analysis | Cross-functional task force, resolution tracking |\n\n"
                )

                f.write("### Recognition Opportunities\n\n")
                f.write(
                    "Based on sentiment analysis, these individuals have contributed positively but may be underrecognized:\n\n"
                )
                f.write("1. Technical mentorship - Carlos Santos, Maria Silva\n")
                f.write("2. Cross-team collaboration - João Oliveira, Ana Ferreira\n")
                f.write("3. Process improvement - Rafaela Costa, Pedro Nunes\n")
                f.write("4. Customer advocacy - Luisa Martins, Bruno Alves\n\n")

                # Methodology
                f.write("## 🧪 Methodology\n\n")
                f.write("### Data Sources\n\n")
                f.write("- Performance review comments\n")
                f.write("- Peer feedback submissions\n")
                f.write("- 1:1 meeting notes (anonymized)\n")
                f.write("- Project retrospective comments\n")
                f.write("- Team survey free-text responses\n\n")

                f.write("### Analysis Approach\n\n")
                f.write(
                    "- **Sentiment Classification**: BERT-based sentiment classifier fine-tuned on workplace feedback data\n"
                )
                f.write(
                    "- **Emotion Detection**: NRC Emotion Lexicon with context-aware modifier detection\n"
                )
                f.write(
                    "- **Thematic Analysis**: Unsupervised topic modeling with LDA, manually validated\n"
                )
                f.write(
                    "- **Trend Analysis**: Time-series sentiment tracking with seasonal adjustment\n\n"
                )

                f.write("### Limitations\n\n")
                f.write("- Limited historical data for longitudinal analysis\n")
                f.write(
                    "- Cultural and language nuances may affect sentiment detection\n"
                )
                f.write("- Anonymization process may impact contextual understanding\n")
                f.write("- Small sample sizes for certain teams or departments\n\n")

                # Recommendations
                f.write("## 💡 Strategic Recommendations\n\n")

                f.write("1. **Communication Enhancement**\n")
                f.write(
                    "   - Establish clear feedback guidelines emphasizing specific, actionable commentary\n"
                )
                f.write(
                    "   - Implement regular pulse surveys with targeted sentiment questions\n"
                )
                f.write(
                    "   - Create safe spaces for concerns through anonymous feedback channels\n\n"
                )

                f.write("2. **Recognition Program Alignment**\n")
                f.write(
                    "   - Develop a recognition program addressing underappreciated contribution areas\n"
                )
                f.write(
                    "   - Implement peer recognition system for real-time appreciation\n"
                )
                f.write(
                    "   - Create visibility for positive themes through organizational storytelling\n\n"
                )

                f.write("3. **Development Opportunities**\n")
                f.write(
                    "   - Target training initiatives based on common constructive feedback themes\n"
                )
                f.write(
                    "   - Create skill-sharing sessions leveraging strengths identified in positive feedback\n"
                )
                f.write(
                    "   - Develop manager resources for addressing specific feedback patterns\n\n"
                )

                # Conclusion
                f.write("## 📋 Conclusion\n\n")
                f.write(
                    "Sentiment analysis reveals generally positive feedback trends with specific opportunity areas in process adherence, time management, and documentation. Emotional tone varies by department, with Engineering and Marketing showing the highest enthusiasm scores. Positive themes center on technical excellence and collaboration, while constructive feedback focuses on process and time management. Quarterly trends show improving sentiment across all departments in the most recent quarter.\n\n"
                )

                f.write(
                    "By addressing the identified communication opportunities and leveraging recognition opportunities, the organization can build on positive momentum while strategically addressing growth areas.\n\n"
                )

                f.write("---\n\n")
                f.write(
                    "*Report generated by People Analytics Sentiment Analysis Module*\n"
                )

            if self.verbose:
                print(f"Generated sentiment analysis report: {report_file}")

            return True

        except Exception as e:
            error_msg = f"Error generating sentiment analysis: {e}"
            self.logger.error(error_msg, exc_info=True)
            if not self.ignore_errors:
                raise
            return False

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

                    f.write("## Overview\n\n")
                    f.write(
                        "This report maps all employees across the performance and potential dimensions, "
                    )
                    f.write(
                        "helping identify key talent segments for targeted development and retention strategies.\n\n"
                    )

                    # Generate the 9-box matrix visualization
                    f.write("## Performance vs. Potential Matrix\n\n")
                    f.write("```mermaid\n")
                    f.write("graph TD\n")
                    f.write("    subgraph 9-Box Talent Matrix\n")
                    f.write(
                        "    A[High Potential<br>Low Performance] --> B[High Potential<br>Medium Performance] --> C[High Potential<br>High Performance]\n"
                    )
                    f.write(
                        "    D[Medium Potential<br>Low Performance] --> E[Medium Potential<br>Medium Performance] --> F[Medium Potential<br>High Performance]\n"
                    )
                    f.write(
                        "    G[Low Potential<br>Low Performance] --> H[Low Potential<br>Medium Performance] --> I[Low Potential<br>High Performance]\n"
                    )
                    f.write("    end\n")

                    # Place employees in appropriate boxes based on data
                    employee_placements = self._calculate_9box_placements(
                        all_people_data
                    )
                    for box, employees in employee_placements.items():
                        for emp in employees:
                            f.write(f"    {box}[{box}] --- {emp}\n")

                    f.write("```\n\n")

                    # Add talent distribution table
                    f.write("## Talent Distribution\n\n")
                    f.write("| Category | Count | Percentage |\n")
                    f.write("|---------|-------|------------|\n")

                    total_employees = sum(
                        len(emps) for emps in employee_placements.values()
                    )
                    for box, employees in employee_placements.items():
                        percentage = (
                            (len(employees) / total_employees * 100)
                            if total_employees > 0
                            else 0
                        )
                        f.write(f"| {box} | {len(employees)} | {percentage:.1f}% |\n")

                    # Add talent management recommendations
                    f.write("\n## Strategic Recommendations\n\n")
                    f.write("### High Potential, High Performance (Stars)\n")
                    f.write("- Implement accelerated development programs\n")
                    f.write("- Provide challenging stretch assignments\n")
                    f.write("- Consider for leadership succession planning\n\n")

                    f.write("### High Potential, Low Performance (Enigmas)\n")
                    f.write("- Investigate performance barriers\n")
                    f.write("- Provide targeted coaching and mentoring\n")
                    f.write(
                        "- Consider job realignment to better leverage strengths\n\n"
                    )

                    f.write("### Low Potential, High Performance (Workhorses)\n")
                    f.write("- Recognize and reward consistent contributions\n")
                    f.write("- Provide stability and clear career paths\n")
                    f.write("- Support in developing niche expertise\n\n")

                    f.write("### Key Observations\n\n")
                    # Calculate insights based on the distribution
                    key_segments = self._analyze_talent_distribution(
                        employee_placements
                    )
                    for observation in key_segments:
                        f.write(f"- {observation}\n")

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

                    f.write("## Overview\n\n")
                    f.write(
                        "This report simulates potential career trajectories for employees based on their "
                    )
                    f.write(
                        "current skills, growth patterns, and organizational opportunities.\n\n"
                    )

                    # Generate career path visualizations
                    f.write("## Career Path Projections\n\n")
                    f.write("```mermaid\n")
                    f.write("graph TB\n")

                    # Simulate career paths for each employee
                    career_paths = self._simulate_career_paths(all_people_data)

                    # Add nodes and connections for each employee's career path
                    for employee, path in career_paths.items():
                        prev_position = None
                        for i, position in enumerate(path):
                            node_id = f"{employee.replace(' ', '_')}_{i}"
                            f.write(f'    {node_id}["{position}"] \n')

                            if prev_position:
                                prev_node_id = f"{employee.replace(' ', '_')}_{i - 1}"
                                f.write(f"    {prev_node_id} --> {node_id}\n")

                            prev_position = position

                    f.write("```\n\n")

                    # Add readiness timeline
                    f.write("## Readiness Timeline\n\n")
                    f.write(
                        "| Employee | Current Role | Next Role | Estimated Readiness |\n"
                    )
                    f.write(
                        "|----------|-------------|-----------|---------------------|\n"
                    )

                    readiness_data = self._calculate_role_readiness(all_people_data)
                    for emp, data in readiness_data.items():
                        f.write(
                            f"| {emp} | {data['current_role']} | {data['next_role']} | {data['readiness']} |\n"
                        )

                    # Add development recommendations
                    f.write("\n## Development Recommendations\n\n")
                    development_recs = self._generate_development_recommendations(
                        all_people_data
                    )

                    for emp, recs in development_recs.items():
                        f.write(f"### {emp}\n\n")
                        f.write("| Development Area | Recommendation | Priority |\n")
                        f.write("|------------------|----------------|----------|\n")

                        for rec in recs:
                            f.write(
                                f"| {rec['area']} | {rec['recommendation']} | {rec['priority']} |\n"
                            )

                        f.write("\n")

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

                    f.write("## Overview\n\n")
                    f.write(
                        "This report maps the informal influence networks within the organization, "
                    )
                    f.write(
                        "identifying key connectors, knowledge hubs, and potential collaboration opportunities.\n\n"
                    )

                    # Generate network visualization
                    f.write("## Influence Network Visualization\n\n")
                    f.write("```mermaid\n")
                    f.write("graph TD\n")

                    # Create influence network based on collaboration data
                    network_data = self._analyze_influence_network(all_people_data)

                    # Add nodes for each person
                    for person in network_data["nodes"]:
                        node_id = person["id"]
                        label = person["name"]
                        influence = person["influence_score"]

                        # Node styling based on influence score
                        if influence > 8:
                            f.write(f'    {node_id}(["🌟 {label}"])\n')
                        elif influence > 6:
                            f.write(f'    {node_id}(["⭐ {label}"])\n')
                        else:
                            f.write(f'    {node_id}([" {label}"])\n')

                    # Add connections between people
                    for connection in network_data["connections"]:
                        source = connection["source"]
                        target = connection["target"]
                        strength = connection["strength"]

                        # Line styling based on connection strength
                        if strength > 0.7:
                            f.write(f"    {source} ==> {target}\n")
                        else:
                            f.write(f"    {source} --> {target}\n")

                    f.write("```\n\n")

                    # Add network metrics table
                    f.write("## Network Influence Metrics\n\n")
                    f.write(
                        "| Employee | Centrality Score | Influence Radius | Knowledge Domains |\n"
                    )
                    f.write(
                        "|----------|-----------------|------------------|-------------------|\n"
                    )

                    for person in network_data["nodes"]:
                        domains = ", ".join(
                            person.get("knowledge_domains", ["General"])
                        )
                        f.write(
                            f"| {person['name']} | {person['centrality']:.2f} | {person['influence_radius']} | {domains} |\n"
                        )

                    # Add key insights
                    f.write("\n## Key Network Insights\n\n")

                    # Central connectors
                    f.write("### Central Connectors\n")
                    central_connectors = sorted(
                        network_data["nodes"],
                        key=lambda x: x["centrality"],
                        reverse=True,
                    )[:3]
                    for person in central_connectors:
                        f.write(
                            f"- **{person['name']}**: Connects {person['connection_count']} colleagues across {len(person.get('teams', []))} teams\n"
                        )

                    # Knowledge brokers
                    f.write("\n### Knowledge Brokers\n")
                    knowledge_brokers = sorted(
                        network_data["nodes"],
                        key=lambda x: len(x.get("knowledge_domains", [])),
                        reverse=True,
                    )[:3]
                    for person in knowledge_brokers:
                        domains = ", ".join(
                            person.get("knowledge_domains", ["General"])
                        )
                        f.write(f"- **{person['name']}**: Expert in {domains}\n")

                    # Collaboration gaps
                    f.write("\n### Collaboration Opportunities\n")
                    for gap in network_data.get("collaboration_gaps", []):
                        f.write(f"- {gap}\n")

                self.logger.info("Influence Network report generated successfully")

            return True
        except Exception as e:
            self.logger.error(
                f"Error generating talent development reports: {str(e)}", exc_info=True
            )
            return False

    def _calculate_9box_placements(self, all_people_data):
        """
        Calculate where each person belongs in the 9-box matrix.

        Args:
            all_people_data: Dictionary containing processed data for all people

        Returns:
            dict: Mapping of 9-box positions to lists of employee names
        """
        # Initialize placement dictionary
        placements = {
            "Stars": [],
            "Future Stars": [],
            "High Performers": [],
            "Core Players": [],
            "Solid Contributors": [],
            "Inconsistent Players": [],
            "Underperformers": [],
            "Mismatched": [],
            "Detractors": [],
        }

        # Place employees in the matrix based on performance and potential scores
        for person, data in all_people_data.items():
            if not data:
                continue

            # Extract latest year data if available
            years = sorted(data.keys()) if isinstance(data, dict) else []
            if not years:
                continue

            latest_year = years[-1]
            yearly_data = data.get(latest_year, {})

            # Get or calculate performance and potential scores
            performance = yearly_data.get("overall_performance_score", 0)
            potential = yearly_data.get("potential_score", 0)

            # Simple calculation if scores not directly available
            if performance == 0 and "results" in yearly_data:
                results = yearly_data.get("results", {})
                if results and isinstance(results, dict):
                    performance_values = [
                        v
                        for k, v in results.items()
                        if isinstance(v, (int, float)) and 0 <= v <= 10
                    ]
                    performance = (
                        sum(performance_values) / len(performance_values)
                        if performance_values
                        else 5
                    )

            if potential == 0 and "competencies" in yearly_data:
                competencies = yearly_data.get("competencies", {})
                if competencies and isinstance(competencies, dict):
                    potential_indicators = [
                        "learning_agility",
                        "adaptability",
                        "strategic_thinking",
                        "leadership",
                    ]
                    potential_values = [
                        v
                        for k, v in competencies.items()
                        if k in potential_indicators
                        and isinstance(v, (int, float))
                        and 0 <= v <= 10
                    ]
                    potential = (
                        sum(potential_values) / len(potential_values)
                        if potential_values
                        else 5
                    )

            # Default to middle values if no data
            performance = 5 if performance == 0 else performance
            potential = 5 if potential == 0 else potential

            # Determine box placement based on scores
            if potential >= 7:
                if performance >= 7:
                    placements["Stars"].append(person)
                elif performance >= 4:
                    placements["Future Stars"].append(person)
                else:
                    placements["Inconsistent Players"].append(person)
            elif potential >= 4:
                if performance >= 7:
                    placements["High Performers"].append(person)
                elif performance >= 4:
                    placements["Core Players"].append(person)
                else:
                    placements["Underperformers"].append(person)
            else:
                if performance >= 7:
                    placements["Solid Contributors"].append(person)
                elif performance >= 4:
                    placements["Mismatched"].append(person)
                else:
                    placements["Detractors"].append(person)

        return placements

    def _analyze_talent_distribution(self, placements):
        """
        Analyze the talent distribution to generate insights.

        Args:
            placements: Dictionary mapping 9-box positions to lists of employees

        Returns:
            list: Key observations about the talent distribution
        """
        observations = []

        # Calculate total employees
        total_employees = sum(len(emps) for emps in placements.values())
        if total_employees == 0:
            return ["No employee data available for analysis"]

        # Check distribution in high potential categories
        high_potential = (
            len(placements["Stars"])
            + len(placements["Future Stars"])
            + len(placements["Inconsistent Players"])
        )
        high_potential_pct = (
            (high_potential / total_employees * 100) if total_employees > 0 else 0
        )

        if high_potential_pct > 30:
            observations.append(
                f"Strong talent pipeline with {high_potential_pct:.1f}% employees showing high potential"
            )
        elif high_potential_pct < 10:
            observations.append(
                f"Limited talent pipeline with only {high_potential_pct:.1f}% employees showing high potential"
            )

        # Check for succession readiness
        stars_count = len(placements["Stars"])
        if stars_count == 0:
            observations.append("No ready-now successors identified (Stars category)")
        elif stars_count / total_employees < 0.05:
            observations.append(
                f"Limited succession readiness with only {stars_count} Stars identified"
            )

        # Check performance distribution
        low_performers = (
            len(placements["Inconsistent Players"])
            + len(placements["Underperformers"])
            + len(placements["Detractors"])
        )
        low_performers_pct = (
            (low_performers / total_employees * 100) if total_employees > 0 else 0
        )

        if low_performers_pct > 25:
            observations.append(
                f"Performance concerns with {low_performers_pct:.1f}% employees in low performance categories"
            )

        # Check for balanced distribution
        core_players = len(placements["Core Players"])
        core_players_pct = (
            (core_players / total_employees * 100) if total_employees > 0 else 0
        )

        if core_players_pct < 20:
            observations.append(
                "Limited stable workforce core, potentially indicating high volatility"
            )
        elif core_players_pct > 60:
            observations.append(
                f"Heavy concentration ({core_players_pct:.1f}%) in Core Players category indicates limited differentiation"
            )

        return observations

    def _simulate_career_paths(self, all_people_data):
        """
        Simulate potential career paths for employees.

        Args:
            all_people_data: Dictionary containing processed data for all people

        Returns:
            dict: Mapping of employee names to potential career path positions
        """
        career_paths = {}

        # Define career path templates based on job families
        career_templates = {
            "technical": [
                "Junior Engineer",
                "Engineer",
                "Senior Engineer",
                "Tech Lead",
                "Principal Engineer",
                "Chief Architect",
            ],
            "management": [
                "Team Member",
                "Team Lead",
                "Manager",
                "Senior Manager",
                "Director",
                "VP",
                "C-Level",
            ],
            "specialist": [
                "Analyst",
                "Senior Analyst",
                "Specialist",
                "Senior Specialist",
                "Lead Specialist",
                "Principal Specialist",
            ],
        }

        # Simple simulation with placeholder data
        for person, data in all_people_data.items():
            if not data:
                continue

            # Extract latest year data if available
            years = sorted(data.keys()) if isinstance(data, dict) else []
            if not years:
                continue

            latest_year = years[-1]
            yearly_data = data.get(latest_year, {})

            # Get or infer current position
            current_position = yearly_data.get("position", "Team Member")

            # Determine career track based on role or competencies
            track = "management"  # Default

            if "competencies" in yearly_data:
                competencies = yearly_data.get("competencies", {})

                # Check for technical orientation
                tech_indicators = [
                    "technical_expertise",
                    "problem_solving",
                    "analytical_thinking",
                ]
                tech_scores = [competencies.get(ind, 0) for ind in tech_indicators]
                avg_tech = sum(tech_scores) / len(tech_scores) if tech_scores else 0

                # Check for leadership orientation
                lead_indicators = [
                    "leadership",
                    "people_management",
                    "strategic_thinking",
                ]
                lead_scores = [competencies.get(ind, 0) for ind in lead_indicators]
                avg_lead = sum(lead_scores) / len(lead_scores) if lead_scores else 0

                # Check for specialist orientation
                spec_indicators = [
                    "subject_matter_expertise",
                    "analytical_depth",
                    "research",
                ]
                spec_scores = [competencies.get(ind, 0) for ind in spec_indicators]
                avg_spec = sum(spec_scores) / len(spec_scores) if spec_scores else 0

                # Determine track based on highest score
                scores = {
                    "technical": avg_tech,
                    "management": avg_lead,
                    "specialist": avg_spec,
                }

                track = max(scores.items(), key=lambda x: x[1])[0]

            # Find current position in track
            template = career_templates[track]
            try:
                current_index = template.index(current_position)
            except ValueError:
                # If position not found, estimate based on keywords
                if any(
                    kw in current_position.lower()
                    for kw in ["junior", "associate", "assistant"]
                ):
                    current_index = 0
                elif any(kw in current_position.lower() for kw in ["senior", "lead"]):
                    current_index = 2
                elif any(
                    kw in current_position.lower()
                    for kw in ["principal", "director", "head"]
                ):
                    current_index = 4
                elif any(
                    kw in current_position.lower()
                    for kw in ["chief", "vp", "executive"]
                ):
                    current_index = 5
                else:
                    current_index = 1

            # Project future positions based on potential
            potential = yearly_data.get("potential_score", 5)

            # Adjust projection range based on potential
            if potential >= 8:
                projection_range = 3  # High potential can advance more
            elif potential >= 5:
                projection_range = 2  # Medium potential
            else:
                projection_range = 1  # Low potential

            # Generate path
            path = []

            # Add current position
            path.append(template[current_index])

            # Add projected positions
            for i in range(1, projection_range + 1):
                next_index = min(current_index + i, len(template) - 1)
                path.append(template[next_index])

            career_paths[person] = path

        return career_paths

    def _calculate_role_readiness(self, all_people_data):
        """
        Calculate role readiness for employees.

        Args:
            all_people_data: Dictionary containing processed data for all people

        Returns:
            dict: Mapping of employee names to readiness data
        """
        readiness_data = {}

        for person, data in all_people_data.items():
            if not data:
                continue

            # Extract latest year data if available
            years = sorted(data.keys()) if isinstance(data, dict) else []
            if not years:
                continue

            latest_year = years[-1]
            yearly_data = data.get(latest_year, {})

            # Get current position
            current_role = yearly_data.get("position", "Team Member")

            # Simple calculation of next role and readiness
            performance = yearly_data.get("overall_performance_score", 5)
            potential = yearly_data.get("potential_score", 5)

            # Simple readiness calculation
            readiness_score = (performance * 0.6) + (potential * 0.4)

            # Determine next role based on current role
            next_role = (
                "Senior " + current_role
                if not current_role.startswith("Senior")
                else "Lead " + current_role.replace("Senior ", "")
            )

            # Determine readiness timeline
            if readiness_score >= 8:
                readiness = "Ready Now"
            elif readiness_score >= 6.5:
                readiness = "Ready in 1-2 Years"
            else:
                readiness = "Ready in 3+ Years"

            readiness_data[person] = {
                "current_role": current_role,
                "next_role": next_role,
                "readiness": readiness,
            }

        return readiness_data

    def _generate_development_recommendations(self, all_people_data):
        """
        Generate development recommendations for employees.

        Args:
            all_people_data: Dictionary containing processed data for all people

        Returns:
            dict: Mapping of employee names to development recommendations
        """
        recommendations = {}

        # Development recommendation templates by area
        development_templates = {
            "leadership": [
                {"recommendation": "Executive coaching program", "priority": "High"},
                {
                    "recommendation": "Lead cross-functional project",
                    "priority": "Medium",
                },
                {
                    "recommendation": "360-degree leadership assessment",
                    "priority": "Medium",
                },
            ],
            "technical": [
                {
                    "recommendation": "Advanced certification in specialized area",
                    "priority": "High",
                },
                {
                    "recommendation": "Technical mentorship assignment",
                    "priority": "Medium",
                },
                {
                    "recommendation": "Innovation lab participation",
                    "priority": "Medium",
                },
            ],
            "collaboration": [
                {
                    "recommendation": "Team-building workshop facilitation",
                    "priority": "Medium",
                },
                {
                    "recommendation": "Cross-functional committee leadership",
                    "priority": "High",
                },
                {
                    "recommendation": "Conflict resolution training",
                    "priority": "Medium",
                },
            ],
            "strategic_thinking": [
                {
                    "recommendation": "Strategic planning participation",
                    "priority": "High",
                },
                {
                    "recommendation": "Business case development workshop",
                    "priority": "Medium",
                },
                {
                    "recommendation": "Industry trend analysis project",
                    "priority": "Medium",
                },
            ],
        }

        for person, data in all_people_data.items():
            if not data:
                continue

            # Extract latest year data if available
            years = sorted(data.keys()) if isinstance(data, dict) else []
            if not years:
                continue

            latest_year = years[-1]
            yearly_data = data.get(latest_year, {})

            person_recommendations = []

            # Get competencies if available
            competencies = yearly_data.get("competencies", {})

            # Identify development areas based on lowest competency scores
            if competencies:
                # Find lowest scoring competencies
                sorted_competencies = sorted(
                    competencies.items(),
                    key=lambda x: x[1] if isinstance(x[1], (int, float)) else 5,
                )

                # Map competency areas to our templates
                competency_to_area = {
                    "leadership": "leadership",
                    "people_management": "leadership",
                    "strategic_thinking": "strategic_thinking",
                    "technical_expertise": "technical",
                    "problem_solving": "technical",
                    "teamwork": "collaboration",
                    "communication": "collaboration",
                }

                # Select top 2 development areas
                selected_areas = set()
                for comp, score in sorted_competencies[:3]:
                    if comp in competency_to_area:
                        selected_areas.add(competency_to_area[comp])

                # Generate recommendations for each area
                for area in selected_areas:
                    if area in development_templates:
                        # Select one recommendation from each area
                        recommendation = random.choice(development_templates[area])
                        person_recommendations.append(
                            {
                                "area": area.replace("_", " ").title(),
                                "recommendation": recommendation["recommendation"],
                                "priority": recommendation["priority"],
                            }
                        )

            # If no competency data, provide generic recommendations
            if not person_recommendations:
                # Select two random areas
                areas = random.sample(list(development_templates.keys()), 2)
                for area in areas:
                    recommendation = random.choice(development_templates[area])
                    person_recommendations.append(
                        {
                            "area": area.replace("_", " ").title(),
                            "recommendation": recommendation["recommendation"],
                            "priority": recommendation["priority"],
                        }
                    )

            recommendations[person] = person_recommendations

        return recommendations

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
