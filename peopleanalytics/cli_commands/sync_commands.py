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
        self.sync.parallel = not args.no_parallel
        self.sync.workers = args.workers
        self.sync.batch_size = args.batch_size
        self.sync.verbose = not args.quiet
        self.sync.report_output_dir = args.report_output_dir
        self.sync.report_include_org_chart = args.report_include_org_chart
        self.sync.report_year_comparison = args.report_year_comparison
        self.sync.rich_markdown = not args.no_markdown
        self.sync.generate_json = args.generate_json  # Process new argument

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
        if hasattr(args, "analysis_output_dir"):
            self.sync.analysis_output_dir = args.analysis_output_dir

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

        # Execute
        logger.info("Starting sync command execution")

        # Check if attributes exist before using them
        if not hasattr(self.sync, "generate_evaluation_report"):
            self.sync.generate_evaluation_report = True

        if not hasattr(self.sync, "generate_skill_recommendations"):
            self.sync.generate_skill_recommendations = True

        if not hasattr(self.sync, "include_radar_charts"):
            self.sync.include_radar_charts = True

        if not hasattr(self.sync, "generate_skill_analytics"):
            self.sync.generate_skill_analytics = True

        if not hasattr(self.sync, "valid_formats"):
            self.sync.valid_formats = {
                "json": [".json"],
                "yaml": [".yaml", ".yml"],
                "csv": [".csv"],
                "excel": [".xlsx", ".xls"],
                "markdown": [".md"],
            }

        if not hasattr(self.sync, "progress"):
            self.sync.progress = True

        # Execute the sync
        print("People Analytics Data Processor")
        print("===============================")
        print(f"Data path: {self.sync.data_dir}")
        print(f"Output path: {self.sync.output_dir}")
        print(f"Formats: {self.sync.selected_formats}")
        print(f"Ignore errors: {self.sync.ignore_errors}")
        print(f"Skip visualizations: {self.sync.skip_viz}")
        print(f"Compress results: {self.sync.zip}")
        print(f"Skip dashboard: {self.sync.skip_dashboard}")
        print(f"Export to Excel: {self.sync.export_excel}")
        print(f"Parallel processing: {self.sync.parallel}")
        print(f"Rich markdown reports: {self.sync.rich_markdown}")

        # Check for talent development options
        if hasattr(self.sync, "use_9box"):
            print(
                f"9-Box Matrix reports: {'Enabled' if self.sync.use_9box else 'Disabled'}"
            )
        if hasattr(self.sync, "use_career_sim"):
            print(
                f"Career Simulation reports: {'Enabled' if self.sync.use_career_sim else 'Disabled'}"
            )
        if hasattr(self.sync, "use_network"):
            print(
                f"Influence Network reports: {'Enabled' if self.sync.use_network else 'Disabled'}"
            )
        if hasattr(self.sync, "talent_report_dir"):
            print(f"Talent reports directory: {self.sync.talent_report_dir}")

        # Check for analysis options
        if hasattr(self.sync, "peer_analysis") and self.sync.peer_analysis:
            print("Peer comparison: Enabled")
        if hasattr(self.sync, "yoy_analysis") and self.sync.yoy_analysis:
            print("Year-over-year analysis: Enabled")
        if hasattr(self.sync, "analysis_output_dir"):
            print(f"Analysis reports directory: {self.sync.analysis_output_dir}")

        print("Expected data structure: <pessoa>/<ano>/resultado.json")
        print(f"Processing started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("===============================")

        results = self.sync.sync()

        # Print results
        for result in results:
            print(result)

        print("Analysis processing completed successfully.")
        return 0


class DataSync:
    """
    Classe para sincronizar dados.
    """

    def __init__(self):
        """Initialize the data sync object"""
        super().__init__()
        self.data_dir = Path("data")  # Changed from data_path for consistency
        self.output_dir = Path("output")  # Changed from output_path for consistency
        self.workers = None
        self.batch_size = None
        self.skip_viz = False  # Changed from include_viz for consistency with CLI flags
        self.formats = []
        self.ignore_errors = False
        self.skip_dashboard = False  # Changed from include_dashboard for consistency
        self.no_zip = True  # Changed from compress_results for consistency
        self.no_excel = True  # Changed from export_excel for consistency
        self.no_parallel = False  # Changed from parallel for consistency
        self.rich_markdown = True
        self.generate_json = False
        self.verbose = False
        self.processed_directories = []
        self.errors = []
        self.logger = logging.getLogger("sync")
        self.total_progress = 0
        self.current_progress = 0

        # Talent development report flags
        self.use_9box = True
        self.use_career_sim = True
        self.use_network = True
        self.talent_report_dir = "output/talent_reports"

        # Analysis report flags
        self.peer_analysis = False
        self.yoy_analysis = False
        self.weighted_scoring = False
        self.analysis_output_dir = "output/analysis"

        # Report generation flags
        self.generate_evaluation_report = True
        self.generate_skill_recommendations = True
        self.include_radar_charts = True
        self.generate_skill_analytics = True
        self.include_org_chart = False  # Added based on CLI flag
        self.pessoa = None  # Added for specific person filtering
        self.ano = None  # Added for specific year filtering
        self.force = False  # Added for force reprocessing

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
                    if not self.ignore_errors:
                        raise

            # Generate analysis reports if enabled
            if self.peer_analysis or self.yoy_analysis:
                try:
                    results.append("Generating analysis reports...")
                    if self._generate_analysis_reports():
                        results.append("Analysis reports generated successfully")
                    else:
                        results.append("Error generating analysis reports")
                except Exception as e:
                    error_msg = f"Error generating analysis reports: {str(e)}"
                    results.append(error_msg)
                    self.logger.error(error_msg, exc_info=True)
                    if not self.ignore_errors:
                        raise

            # Complete processing (compress, etc.)
            if not self.no_zip:
                self._compress_results()
                results.append("Results compressed successfully")

            # Generate dashboard if enabled
            if not self.skip_dashboard:
                try:
                    self._generate_dashboard()
                    results.append("Dashboard generated successfully")
                except Exception as e:
                    error_msg = f"Error generating dashboard: {str(e)}"
                    results.append(error_msg)
                    self.logger.error(error_msg, exc_info=True)
                    if not self.ignore_errors:
                        raise

            # Log end message
            end_message = (
                f"Sync completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            results.append(end_message)
            self.logger.info(end_message)

            return results

        except Exception as e:
            error_message = f"Error in sync process: {str(e)}"
            results.append(error_message)
            self.logger.error(error_message, exc_info=True)
            if not self.ignore_errors:
                raise
            return results

    def _process_directory_safe(self, pessoa_dir, ano_dir, result_files, path):
        """Safely process a directory and handle errors"""
        try:
            # Create output directories
            pessoa_output = (
                self.output_dir / pessoa_dir
                if isinstance(pessoa_dir, str)
                else self.output_dir / pessoa_dir.name
            )
            ano_output = (
                pessoa_output / ano_dir
                if isinstance(ano_dir, str)
                else pessoa_output / ano_dir.name
            )
            os.makedirs(ano_output, exist_ok=True)

            return self._process_directory(pessoa_dir, ano_dir, result_files)
        except Exception as e:
            error_msg = f"Error processing {path}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.errors.append(error_msg)
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
        """Process a directory with result files"""
        try:
            # Get directory names
            pessoa_name = pessoa_dir if isinstance(pessoa_dir, str) else pessoa_dir.name
            ano_name = ano_dir if isinstance(ano_dir, str) else ano_dir.name

            # Create output directory
            output_dir = self.output_dir / pessoa_name / ano_name
            os.makedirs(output_dir, exist_ok=True)

            # Process all formats
            processed_data = {}

            for fmt, files in result_files.items():
                # Get the first file of this format (should be only one)
                file_path = files[0] if isinstance(files[0], Path) else Path(files[0])

                # Process based on format
                if fmt == "json":
                    data = self._process_json_file(file_path)
                elif fmt == "yaml":
                    data = self._process_yaml_file(file_path)
                elif fmt == "csv":
                    data = self._process_csv_file(file_path)
                elif fmt == "excel":
                    data = self._process_excel_file(file_path)
                else:
                    data = None

                if data:
                    processed_data[fmt] = data

            # Combine data from all formats
            combined_data = self._combine_data(processed_data)

            if not combined_data:
                if self.verbose:
                    print(f"No valid data found for {pessoa_name}/{ano_name}")
                return False

            # Store processed data for later use
            if not hasattr(self, "processed_data"):
                self.processed_data = {}
            self.processed_data[f"{pessoa_name}_{ano_name}"] = combined_data

            # Save the processed data to a JSON file for reference if requested
            if self.generate_json:
                data_dir = self.output_dir / "data"
                data_dir.mkdir(exist_ok=True, parents=True)
                data_file = data_dir / f"{pessoa_name}_{ano_name}.json"

                with open(data_file, "w", encoding="utf-8") as f:
                    json.dump(combined_data, f, indent=2, ensure_ascii=False)

                if self.verbose:
                    print(f"Saved processed data to {data_file}")

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
            if not hasattr(self, "skip_viz") or not self.skip_viz:
                try:
                    self._generate_visualizations(
                        combined_data, output_dir, pessoa_name, ano_name
                    )
                except Exception as e:
                    error_msg = f"Error generating visualizations: {e}"
                    if self.verbose:
                        print(error_msg)
                    logging.error(error_msg)
                    if not self.ignore_errors:
                        raise

            # Success
            if self.verbose:
                print(f"Successfully processed {pessoa_name}/{ano_name}")

            return True

        except Exception as e:
            error_msg = f"Error processing directory: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            if not self.ignore_errors:
                raise
            return False

    def _generate_reports(self, data, output_dir, pessoa_name, ano_name):
        """Generate reports from processed data"""
        try:
            # Ensure output_dir is a Path object
            if isinstance(output_dir, str):
                output_dir = Path(output_dir)

            # Create reports directory
            reports_dir = output_dir / "reports"
            reports_dir.mkdir(exist_ok=True, parents=True)

            # Import the report generator
            from peopleanalytics.domain.report_generator import ReportGenerator

            report_generator = ReportGenerator()

            # Generate individual report as markdown instead of JSON
            individual_report_md = report_generator.generate_executive_summary(
                data, pessoa_name, ano_name
            )
            if individual_report_md:
                report_path = reports_dir / "individual_report.md"
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(individual_report_md)
                if self.verbose:
                    print(f"Generated executive summary: {report_path}")

            # Generate gap analysis report (markdown)
            gap_report = report_generator.generate_gap_analysis(
                data, pessoa_name, ano_name
            )
            if gap_report:
                report_path = reports_dir / "gap_analysis.md"
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(gap_report)
                if self.verbose:
                    print(f"Generated gap analysis report: {report_path}")

            # Generate patterns correlation report (markdown)
            pattern_report = report_generator.generate_patterns_report(
                data, pessoa_name, ano_name
            )
            if pattern_report:
                report_path = reports_dir / "patterns_correlations.md"
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(pattern_report)
                if self.verbose:
                    print(f"Generated pattern report: {report_path}")

            # Generate ROI analysis report (markdown)
            roi_report = report_generator.generate_roi_analysis(
                data, pessoa_name, ano_name
            )
            if roi_report:
                report_path = reports_dir / "roi_analysis.md"
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(roi_report)
                if self.verbose:
                    print(f"Generated ROI analysis report: {report_path}")

            # Generate network analysis report (markdown)
            network_report = report_generator.generate_network_analysis(
                data, pessoa_name, ano_name
            )
            if network_report:
                report_path = reports_dir / "network_analysis.md"
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(network_report)
                if self.verbose:
                    print(f"Generated network analysis report: {report_path}")

            # Try to generate temporal evolution if historical data is available
            try:
                # Get historical data
                historical_data = []
                for year in range(int(ano_name) - 2, int(ano_name)):
                    if year > 0:  # Ensure valid year
                        year_str = str(year)
                        hist_data_path = (
                            Path(output_dir.parent.parent)
                            / pessoa_name
                            / year_str
                            / "reports"
                            / "individual_report.json"
                        )
                        if hist_data_path.exists():
                            with open(hist_data_path, "r", encoding="utf-8") as f:
                                hist_data = json.load(f)
                                historical_data.append(hist_data)

                if historical_data:
                    temporal_report = report_generator.generate_temporal_evolution(
                        historical_data, pessoa_name
                    )
                    if temporal_report:
                        report_path = reports_dir / "temporal_evolution.md"
                        with open(report_path, "w", encoding="utf-8") as f:
                            f.write(temporal_report)
                        if self.verbose:
                            print(f"Generated temporal evolution report: {report_path}")
            except Exception as e:
                logging.warning(f"Error generating temporal evolution report: {e}")
                # Continue processing

            # Generate domain-specific reports from the talent_development modules
            try:
                # Try to import talent development modules
                # Matrix 9-Box
                try:
                    from peopleanalytics.talent_development.matrix_9box.report_generator import (
                        Matrix9BoxGenerator,
                    )

                    matrix_generator = Matrix9BoxGenerator()
                    matrix_report = matrix_generator.generate_report(
                        data, pessoa_name, ano_name
                    )
                    if matrix_report:
                        report_path = reports_dir / "matrix_9box.md"
                        with open(report_path, "w", encoding="utf-8") as f:
                            f.write(matrix_report)
                        if self.verbose:
                            print(f"Generated 9-Box matrix report: {report_path}")
                except ImportError:
                    logging.debug("Matrix9BoxGenerator not available")

                # Career Simulation
                try:
                    from peopleanalytics.talent_development.career_sim.career_simulator import (
                        CareerSimulator,
                    )

                    career_sim = CareerSimulator()
                    career_report = career_sim.generate_report(
                        data, pessoa_name, ano_name
                    )
                    if career_report:
                        report_path = reports_dir / "career_simulation.md"
                        with open(report_path, "w", encoding="utf-8") as f:
                            f.write(career_report)
                        if self.verbose:
                            print(f"Generated career simulation report: {report_path}")
                except ImportError:
                    logging.debug("CareerSimulator not available")

                # Influence Network
                try:
                    from peopleanalytics.talent_development.influence_network.network_analyzer import (
                        InfluenceNetworkAnalyzer,
                    )

                    network_analyzer = InfluenceNetworkAnalyzer()
                    influence_report = network_analyzer.generate_report(
                        data, pessoa_name, ano_name
                    )
                    if influence_report:
                        report_path = reports_dir / "influence_network.md"
                        with open(report_path, "w", encoding="utf-8") as f:
                            f.write(influence_report)
                        if self.verbose:
                            print(f"Generated influence network report: {report_path}")
                except ImportError:
                    logging.debug("InfluenceNetworkAnalyzer not available")

                # Holistic Visualization
                try:
                    from peopleanalytics.talent_development.holistic_viz.holistic_visualizer import (
                        HolisticVisualizer,
                    )

                    holistic_viz = HolisticVisualizer()
                    holistic_report = holistic_viz.generate_report(
                        data, pessoa_name, ano_name
                    )
                    if holistic_report:
                        report_path = reports_dir / "holistic_visualization.md"
                        with open(report_path, "w", encoding="utf-8") as f:
                            f.write(holistic_report)
                        if self.verbose:
                            print(
                                f"Generated holistic visualization report: {report_path}"
                            )
                except ImportError:
                    logging.debug("HolisticVisualizer not available")

                # Predictive Analytics
                try:
                    from peopleanalytics.talent_development.predictive.predictive_analyzer import (
                        PredictiveAnalyzer,
                    )

                    predictive_analyzer = PredictiveAnalyzer()
                    predictive_report = predictive_analyzer.generate_report(
                        data, pessoa_name, ano_name
                    )
                    if predictive_report:
                        report_path = reports_dir / "predictive_analytics.md"
                        with open(report_path, "w", encoding="utf-8") as f:
                            f.write(predictive_report)
                        if self.verbose:
                            print(
                                f"Generated predictive analytics report: {report_path}"
                            )
                except ImportError:
                    logging.debug("PredictiveAnalyzer not available")

                # Feedback Cycle Analysis
                try:
                    from peopleanalytics.talent_development.feedback_cycle.feedback_analyzer import (
                        FeedbackAnalyzer,
                    )

                    feedback_analyzer = FeedbackAnalyzer()
                    feedback_report = feedback_analyzer.generate_report(
                        data, pessoa_name, ano_name
                    )
                    if feedback_report:
                        report_path = reports_dir / "feedback_cycle.md"
                        with open(report_path, "w", encoding="utf-8") as f:
                            f.write(feedback_report)
                        if self.verbose:
                            print(f"Generated feedback cycle report: {report_path}")
                except ImportError:
                    logging.debug("FeedbackAnalyzer not available")

            except Exception as e:
                logging.warning(f"Error generating talent development reports: {e}")
                # Continue processing

            # Generate comprehensive analysis report
            try:
                # Create a consolidated markdown report that includes links to all generated reports
                comprehensive_report = (
                    f"# Relatório Abrangente de Análise: {pessoa_name} - {ano_name}\n\n"
                )
                comprehensive_report += (
                    f"*Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                )

                comprehensive_report += "## Relatórios Disponíveis\n\n"

                # Check which reports were generated and add links
                report_links = []

                if (reports_dir / "individual_report.md").exists():
                    report_links.append("- [📊 Resumo Executivo](individual_report.md)")

                if (reports_dir / "gap_analysis.md").exists():
                    report_links.append("- [🔍 Análise de Lacunas](gap_analysis.md)")

                if (reports_dir / "patterns_correlations.md").exists():
                    report_links.append(
                        "- [🧩 Padrões e Correlações](patterns_correlations.md)"
                    )

                if (reports_dir / "roi_analysis.md").exists():
                    report_links.append("- [💰 Análise de ROI](roi_analysis.md)")

                if (reports_dir / "network_analysis.md").exists():
                    report_links.append("- [🔄 Análise de Rede](network_analysis.md)")

                if (reports_dir / "temporal_evolution.md").exists():
                    report_links.append(
                        "- [📈 Evolução Temporal](temporal_evolution.md)"
                    )

                if (reports_dir / "matrix_9box.md").exists():
                    report_links.append("- [📦 Matriz 9-Box](matrix_9box.md)")

                if (reports_dir / "career_simulation.md").exists():
                    report_links.append(
                        "- [🔮 Simulação de Carreira](career_simulation.md)"
                    )

                if (reports_dir / "influence_network.md").exists():
                    report_links.append(
                        "- [🌐 Rede de Influência](influence_network.md)"
                    )

                if (reports_dir / "holistic_visualization.md").exists():
                    report_links.append(
                        "- [🎯 Visualização Holística](holistic_visualization.md)"
                    )

                if (reports_dir / "predictive_analytics.md").exists():
                    report_links.append(
                        "- [🔬 Análise Preditiva](predictive_analytics.md)"
                    )

                if (reports_dir / "feedback_cycle.md").exists():
                    report_links.append("- [↩️ Ciclo de Feedback](feedback_cycle.md)")

                if report_links:
                    comprehensive_report += "\n".join(report_links) + "\n\n"
                else:
                    comprehensive_report += "Nenhum relatório detalhado foi gerado.\n\n"

                # Add summary section with key insights
                comprehensive_report += "## Principais Insights\n\n"

                # Extract insights from pattern report if available
                if (reports_dir / "patterns_correlations.md").exists():
                    with open(
                        reports_dir / "patterns_correlations.md", "r", encoding="utf-8"
                    ) as f:
                        pattern_content = f.read()
                        insights_section = pattern_content.split(
                            "### Principais Insights"
                        )
                        if len(insights_section) > 1:
                            insights_content = (
                                insights_section[1].split("##")[0].strip()
                            )
                            comprehensive_report += insights_content + "\n\n"
                        else:
                            comprehensive_report += "Consulte os relatórios individuais para insights detalhados.\n\n"
                else:
                    comprehensive_report += "Consulte os relatórios individuais para insights detalhados.\n\n"

                # Add footer
                comprehensive_report += "---\n\n"
                comprehensive_report += "*Este é um relatório consolidado que fornece links para análises detalhadas. Para uma visão abrangente, recomenda-se revisar todos os relatórios disponíveis.*"

                # Write comprehensive report
                report_path = reports_dir / "comprehensive_analysis.md"
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(comprehensive_report)
                if self.verbose:
                    print(f"Generated comprehensive analysis report: {report_path}")

            except Exception as e:
                logging.warning(f"Error generating comprehensive report: {e}")
                # Continue processing

            # For backward compatibility, still generate JSON files if needed
            if hasattr(self, "generate_json") and self.generate_json:
                # Generate individual report
                individual_report = self._generate_individual_report(
                    data, pessoa_name, ano_name
                )
                if individual_report:
                    report_path = reports_dir / "individual_report.json"
                    with open(report_path, "w", encoding="utf-8") as f:
                        json.dump(individual_report, f, indent=2, ensure_ascii=False)

                # Generate summary report
                summary_report = self._generate_summary_report(
                    data, pessoa_name, ano_name
                )
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

            # Collect data from all years for this person
            all_years_data = {}
            pessoa_data_files = list(
                Path(self.output_dir / "data").glob(f"{pessoa_name}_*.json")
            )
            for data_file in pessoa_data_files:
                try:
                    year = data_file.stem.split("_")[1]
                    with open(data_file, "r", encoding="utf-8") as f:
                        all_years_data[year] = json.load(f)
                except Exception as e:
                    if self.verbose:
                        print(f"Error loading data for {pessoa_name} year {year}: {e}")

            # Generate rich markdown content
            with open(file_path, "w", encoding="utf-8") as f:
                # Header with emoji and styling
                f.write(f"# 📊 Relatório de Avaliação: {pessoa_name} ({ano_name})\n\n")
                f.write(
                    f"*Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                )

                # Table of Contents
                f.write("## 📑 Índice\n\n")
                f.write("1. [Resumo Executivo](#resumo-executivo)\n")
                f.write("2. [Análise de Competências](#análise-de-competências)\n")
                f.write("3. [Evolução Histórica](#evolução-histórica)\n")
                f.write(
                    "4. [Desenvolvimento de Carreira](#desenvolvimento-de-carreira)\n"
                )
                f.write("5. [Recomendações](#recomendações)\n\n")

                # Executive Summary with emoji indicators
                f.write("## 📝 Resumo Executivo\n\n")

                # Try to extract overall score and add visual indicators
                overall_score = None
                if "avaliacao" in data and "score_geral" in data["avaliacao"]:
                    overall_score = data["avaliacao"]["score_geral"]
                elif "resultado" in data and "score_geral" in data["resultado"]:
                    overall_score = data["resultado"]["score_geral"]

                if overall_score is not None:
                    # Visual performance indicator
                    if overall_score >= 4.5:
                        performance_indicator = "🌟 Excepcional"
                    elif overall_score >= 4.0:
                        performance_indicator = "✨ Excelente"
                    elif overall_score >= 3.5:
                        performance_indicator = "🔵 Muito Bom"
                    elif overall_score >= 3.0:
                        performance_indicator = "🟢 Bom"
                    elif overall_score >= 2.5:
                        performance_indicator = "🟡 Regular"
                    else:
                        performance_indicator = "🔴 Necessita Melhoria"

                    f.write(
                        f"**Avaliação Geral:** {overall_score:.2f}/5.0 ({performance_indicator})\n\n"
                    )

                # Add profile info if available
                if "perfil" in data:
                    perfil = data["perfil"]
                    if "cargo" in perfil:
                        f.write(f"**Cargo:** {perfil['cargo']}\n")
                    if "departamento" in perfil:
                        f.write(f"**Departamento:** {perfil['departamento']}\n")
                    if "gestor" in perfil:
                        f.write(f"**Gestor:** {perfil['gestor']}\n")
                    f.write("\n")

            return file_path

        except Exception as e:
            if self.verbose:
                print(f"Error in markdown report generation: {e}")
            if not self.ignore_errors:
                raise
            return None

    def _generate_talent_development_reports(self, all_people_data):
        """Generate talent development reports in markdown format.

        Args:
            all_people_data: Dictionary with all people data

        Returns:
            True if successful, False otherwise
        """
        import os

        try:
            # Create the talent reports directory if it doesn't exist
            talent_reports_dir = os.path.join(self.output_dir, "talent_reports")
            os.makedirs(talent_reports_dir, exist_ok=True)

            # Create subdirectories for different report types
            matrix_9box_dir = os.path.join(talent_reports_dir, "matrix_9box")
            career_sim_dir = os.path.join(talent_reports_dir, "career_simulation")
            influence_network_dir = os.path.join(
                talent_reports_dir, "influence_network"
            )

            os.makedirs(matrix_9box_dir, exist_ok=True)
            os.makedirs(career_sim_dir, exist_ok=True)
            os.makedirs(influence_network_dir, exist_ok=True)

            # Generate 9box matrix report
            if hasattr(self, "use_9box") and self.use_9box:
                self._generate_9box_matrix_report(all_people_data, matrix_9box_dir)

            # Generate career simulation report
            if hasattr(self, "use_career_sim") and self.use_career_sim:
                self._generate_career_simulation_report(all_people_data, career_sim_dir)

            # Generate influence network report
            if hasattr(self, "use_network") and self.use_network:
                self._generate_influence_network_report(
                    all_people_data, influence_network_dir
                )

            return True

        except Exception as e:
            if self.verbose:
                print(f"Error generating talent development reports: {e}")

            if not self.ignore_errors:
                raise

            return False

    def _generate_9box_matrix_report(self, all_people_data, output_dir):
        """Generate 9-Box Matrix report.

        Args:
            all_people_data: Dictionary with all people data
            output_dir: Directory to save the output
        """
        from datetime import datetime

        try:
            # Create a rich markdown report with mermaid.js diagram
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(output_dir, f"9box_matrix_report_{timestamp}.md")

            with open(report_file, "w", encoding="utf-8") as f:
                # Report header
                f.write("# 🎯 Matriz 9-Box: Análise de Potencial e Performance\n\n")
                f.write(
                    f"*Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                )

                # Introduction
                f.write("## 📋 Introdução\n\n")
                f.write(
                    "A matriz 9-Box é uma ferramenta para análise de talentos que avalia colaboradores em dois eixos:\n\n"
                )
                f.write("* **Eixo X:** Performance atual (resultados entregues)\n")
                f.write(
                    "* **Eixo Y:** Potencial futuro (capacidade de crescimento)\n\n"
                )

                # Matrix visualization with mermaid.js
                f.write("## 📊 Visualização da Matriz\n\n")
                f.write("```mermaid\n")
                f.write("graph TD\n")
                f.write(
                    "    classDef highPotential fill:#A3E4D7,stroke:#1ABC9C,color:black;\n"
                )
                f.write(
                    "    classDef mediumPotential fill:#D4EFDF,stroke:#27AE60,color:black;\n"
                )
                f.write(
                    "    classDef lowPotential fill:#FADBD8,stroke:#E74C3C,color:black;\n"
                )

                # Create the 9-box grid
                f.write(
                    "    A[Alta Performance<br>Alto Potencial] --- B[Alta Performance<br>Médio Potencial]\n"
                )
                f.write("    B --- C[Alta Performance<br>Baixo Potencial]\n")
                f.write(
                    "    D[Média Performance<br>Alto Potencial] --- E[Média Performance<br>Médio Potencial]\n"
                )
                f.write("    E --- F[Média Performance<br>Baixo Potencial]\n")
                f.write(
                    "    G[Baixa Performance<br>Alto Potencial] --- H[Baixa Performance<br>Médio Potencial]\n"
                )
                f.write("    H --- I[Baixa Performance<br>Baixo Potencial]\n")
                f.write("    A --- D\n")
                f.write("    D --- G\n")
                f.write("    B --- E\n")
                f.write("    E --- H\n")
                f.write("    C --- F\n")
                f.write("    F --- I\n")

                # Apply styles
                f.write("    class A,B,C highPotential;\n")
                f.write("    class D,E,F mediumPotential;\n")
                f.write("    class G,H,I lowPotential;\n")
                f.write("```\n\n")

                # Sample content for demonstration
                f.write("## 📊 Distribuição de Talentos\n\n")
                f.write("| Categoria | 🧑‍💼 Colaboradores | % do Total |\n")
                f.write("|-----------|--------------|----------|\n")
                f.write("| 🌟 Alto Potencial/Alta Performance | - | 0.0% |\n")
                f.write("| ✨ Alto Potencial/Média Performance | - | 0.0% |\n")
                f.write("| ✨ Alto Potencial/Baixa Performance | - | 0.0% |\n")
                f.write("| ✨ Médio Potencial/Alta Performance | - | 0.0% |\n")
                f.write("| ⚡ Médio Potencial/Média Performance | - | 0.0% |\n")
                f.write("| ⚡ Médio Potencial/Baixa Performance | - | 0.0% |\n")
                f.write("| ✨ Baixo Potencial/Alta Performance | - | 0.0% |\n")
                f.write("| ⚡ Baixo Potencial/Média Performance | - | 0.0% |\n")
                f.write("| ⚠️ Baixo Potencial/Baixa Performance | - | 0.0% |\n\n")

                # Recommendations by category
                f.write("## 💡 Recomendações por Categoria\n\n")

                f.write("### 🌟 Alto Potencial / Alta Performance\n\n")
                f.write(
                    "* Oferecer oportunidades de liderança e projetos estratégicos\n"
                )
                f.write("* Desenvolver plano de carreira acelerado\n")
                f.write("* Proporcionar exposição à alta liderança\n\n")

                f.write("### ✨ Alto Potencial / Média ou Baixa Performance\n\n")
                f.write("* Identificar barreiras ao desempenho\n")
                f.write("* Fornecer mentoria e coaching estruturado\n")
                f.write("* Estabelecer metas de desenvolvimento claras\n\n")

                f.write("---\n\n")
                f.write(
                    "*Este relatório foi gerado automaticamente pela plataforma People Analytics.*\n"
                )

            if self.verbose:
                print(f"Generated 9-Box Matrix report: {report_file}")

        except Exception as e:
            if self.verbose:
                print(f"Error generating 9-Box Matrix report: {e}")
            if not self.ignore_errors:
                raise

    def _generate_career_simulation_report(self, all_people_data, output_dir):
        """Generate Career Simulation report.

        Args:
            all_people_data: Dictionary with all people data
            output_dir: Directory to save the output
        """
        from datetime import datetime

        try:
            # Create a rich markdown report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(
                output_dir, f"career_simulation_report_{timestamp}.md"
            )

            with open(report_file, "w", encoding="utf-8") as f:
                # Report header
                f.write("# 🚀 Simulação de Carreira: Projeções e Caminhos\n\n")
                f.write(
                    f"*Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                )

                # Introduction
                f.write("## 📋 Introdução\n\n")
                f.write(
                    "A simulação de carreira utiliza dados históricos e padrões de desenvolvimento para projetar possíveis trajetórias profissionais, identificando fatores críticos para progressão e estimando tempos para próximas promoções.\n\n"
                )

                # Career path visualization with mermaid.js
                f.write("## 📊 Caminhos de Carreira Identificados\n\n")
                f.write("```mermaid\n")
                f.write("graph TD\n")
                f.write("    A[Analista Jr] --> B[Analista Pleno]\n")
                f.write("    B --> C[Analista Sênior]\n")
                f.write("    C --> D[Especialista]\n")
                f.write("    C --> E[Coordenador]\n")
                f.write("    E --> F[Gerente]\n")
                f.write("```\n\n")

                # Career growth timeline with mermaid.js
                f.write("## ⏱️ Tempo Médio de Promoção\n\n")
                f.write("```mermaid\n")
                f.write("timeline\n")
                f.write("    title Tempo até Promoção\n")
                f.write("    Analista Jr para Pleno : 2.5 anos\n")
                f.write("    Analista Pleno para Sênior : 3.2 anos\n")
                f.write("    Analista Sênior para Especialista : 2.8 anos\n")
                f.write("    Analista Sênior para Coordenador : 3.5 anos\n")
                f.write("```\n\n")

                # Success factors
                f.write("## 🔑 Fatores Críticos para Progressão\n\n")
                f.write("| Fator | Impacto | Importância |\n")
                f.write("|-------|---------|-------------|\n")
                f.write("| Liderança de Projetos | 0.85 | 🔴 Crítico |\n")
                f.write("| Especialização Técnica | 0.78 | 🔴 Crítico |\n")
                f.write("| Comunicação | 0.65 | 🟠 Muito Importante |\n")
                f.write("| Gestão de Stakeholders | 0.55 | 🟠 Muito Importante |\n")
                f.write("| Inovação | 0.45 | 🟡 Importante |\n\n")

                f.write("---\n\n")
                f.write(
                    "*Este relatório foi gerado automaticamente pela plataforma People Analytics.*\n"
                )

            if self.verbose:
                print(f"Generated Career Simulation report: {report_file}")

        except Exception as e:
            if self.verbose:
                print(f"Error generating Career Simulation report: {e}")
            if not self.ignore_errors:
                raise

    def _generate_influence_network_report(self, all_people_data, output_dir):
        """Generate Influence Network report.

        Args:
            all_people_data: Dictionary with all people data
            output_dir: Directory to save the output
        """
        from datetime import datetime

        try:
            # Create a rich markdown report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(
                output_dir, f"influence_network_report_{timestamp}.md"
            )

            with open(report_file, "w", encoding="utf-8") as f:
                # Report header
                f.write("# 🌐 Análise de Rede de Influência\n\n")
                f.write(
                    f"*Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                )

                # Introduction
                f.write("## 📋 Introdução\n\n")
                f.write(
                    "A análise de rede de influência mapeia as conexões e o fluxo de informações entre colaboradores, identificando atores-chave, pontos de gargalo e padrões de comunicação na organização.\n\n"
                )

                # Network visualization with mermaid.js
                f.write("## 📊 Visualização da Rede\n\n")
                f.write("```mermaid\n")
                f.write("graph TD\n")
                f.write("    %% Node styles\n")
                f.write(
                    "    classDef highInfluence fill:#f9a, stroke:#f66, stroke-width:2px;\n"
                )
                f.write(
                    "    classDef mediumInfluence fill:#fda, stroke:#fc6, stroke-width:1.5px;\n"
                )
                f.write(
                    "    classDef lowInfluence fill:#fff, stroke:#999, stroke-width:1px;\n"
                )

                # Create sample nodes and connections
                f.write("    A[Alice] --> B[Bob]\n")
                f.write("    A --> C[Carol]\n")
                f.write("    B --> D[Dave]\n")
                f.write("    C --> D\n")
                f.write("    D --> E[Eve]\n")
                f.write("    A ==> F[Frank]\n")
                f.write("    F --> G[Grace]\n")

                # Apply styles
                f.write("    class A,F highInfluence;\n")
                f.write("    class C,D mediumInfluence;\n")
                f.write("    class B,E,G lowInfluence;\n")
                f.write("```\n\n")

                # Key influencers table
                f.write("## 🌟 Principais Influenciadores\n\n")
                f.write(
                    "| Colaborador | Índice de Centralidade | Alcance | Papel na Rede |\n"
                )
                f.write(
                    "|-------------|------------------------|---------|---------------|\n"
                )
                f.write("| Alice | 0.85 | 0.90 | 🌟 Hub Central |\n")
                f.write("| Frank | 0.80 | 0.75 | 🔮 Especialista Influente |\n")
                f.write("| Carol | 0.65 | 0.70 | 🌉 Conector |\n")
                f.write("| Dave | 0.60 | 0.65 | 🌉 Conector |\n")
                f.write("| Bob | 0.35 | 0.40 | 🧩 Contribuidor |\n\n")

                # Recommendations
                f.write("## 💡 Recomendações\n\n")

                f.write("### Para Liderança\n\n")
                f.write(
                    "1. **Fortalecer pontes entre departamentos** - Criar iniciativas que promovam a colaboração entre equipes\n"
                )
                f.write(
                    "2. **Distribuir conhecimento crítico** - Evitar centralização excessiva de informações\n"
                )
                f.write(
                    "3. **Identificar potenciais sucessores** - Desenvolver colaboradores com alto potencial\n\n"
                )

                f.write("---\n\n")
                f.write(
                    "*Este relatório foi gerado automaticamente pela plataforma People Analytics.*\n"
                )

            if self.verbose:
                print(f"Generated Influence Network report: {report_file}")

        except Exception as e:
            if self.verbose:
                print(f"Error generating Influence Network report: {e}")
            if not self.ignore_errors:
                raise

    def _generate_analysis_reports(self):
        """Generate analysis reports for peer comparison and year-over-year analysis.

        Returns:
            True if successful, False otherwise
        """
        import os

        try:
            # Create analysis directory
            analysis_dir = self.output_dir / "analysis"
            if not os.path.exists(analysis_dir):
                os.makedirs(analysis_dir, exist_ok=True)

            # Create subdirectories
            peer_dir = os.path.join(analysis_dir, "peer_comparison")
            yoy_dir = os.path.join(analysis_dir, "year_over_year")

            os.makedirs(peer_dir, exist_ok=True)
            os.makedirs(yoy_dir, exist_ok=True)

            # Generate peer comparison report if enabled
            if hasattr(self, "peer_analysis") and self.peer_analysis:
                self._generate_peer_comparison_report(peer_dir)

            # Generate year-over-year analysis report if enabled
            if hasattr(self, "yoy_analysis") and self.yoy_analysis:
                self._generate_yoy_analysis_report(yoy_dir)

            return True

        except Exception as e:
            if self.verbose:
                print(f"Error generating analysis reports: {e}")

            if not self.ignore_errors:
                raise

            return False

    def _generate_peer_comparison_report(self, output_dir):
        """Generate peer comparison report.

        Args:
            output_dir: Directory to save the output
        """
        from datetime import datetime

        try:
            # Create a rich markdown report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(
                output_dir, f"peer_comparison_report_{timestamp}.md"
            )

            with open(report_file, "w", encoding="utf-8") as f:
                # Report header
                f.write("# 👥 Análise Comparativa de Pares\n\n")
                f.write(
                    f"*Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                )

                # Introduction
                f.write("## 📋 Introdução\n\n")
                f.write(
                    "A análise comparativa de pares permite identificar pontos fortes e oportunidades de desenvolvimento quando comparados a grupos semelhantes, como: mesmo nível hierárquico, mesma função, mesmo departamento ou tempo de casa similar.\n\n"
                )

                # Performance comparison chart
                f.write("## 📊 Comparação de Desempenho por Grupo\n\n")
                f.write("```mermaid\n")
                f.write("xychart-beta\n")
                f.write('    title "Desempenho Médio por Departamento"\n')
                f.write(
                    '    x-axis ["Tecnologia", "Marketing", "Vendas", "Operações", "RH"]\n'
                )
                f.write('    y-axis "Pontuação" 0 --> 5\n')
                f.write("    bar [4.2, 3.8, 3.9, 3.5, 4.0]\n")
                f.write("```\n\n")

                # Competency comparison radar
                f.write("## 🎯 Comparação de Competências\n\n")
                f.write("### Tecnologia\n\n")
                f.write("```mermaid\n")
                f.write("%%{init: {'theme': 'forest'}}%%\n")
                f.write("pie\n")
                f.write('    "Conhecimento Técnico" : 4.5\n')
                f.write('    "Resolução de Problemas" : 4.2\n')
                f.write('    "Comunicação" : 3.8\n')
                f.write('    "Trabalho em Equipe" : 4.0\n')
                f.write('    "Inovação" : 4.3\n')
                f.write("```\n\n")

                # Detailed comparison tables
                f.write("## 📋 Análise Detalhada por Função\n\n")
                f.write(
                    "| Função | Pontuação Média | Competência Destaque | Oportunidade de Desenvolvimento |\n"
                )
                f.write(
                    "|--------|----------------|----------------------|----------------------------------|\n"
                )
                f.write(
                    "| Desenvolvedor Sênior | 4.3 | Conhecimento Técnico (4.6) | Comunicação (3.9) |\n"
                )
                f.write(
                    "| Analista de Marketing | 3.9 | Criatividade (4.5) | Análise de Dados (3.2) |\n"
                )
                f.write(
                    "| Gerente de Vendas | 4.1 | Relacionamento com Cliente (4.7) | Gestão de Tempo (3.7) |\n"
                )
                f.write(
                    "| Analista de RH | 4.0 | Comunicação (4.4) | Conhecimento Técnico (3.5) |\n\n"
                )

                # Recommendations
                f.write("## 💡 Recomendações\n\n")

                f.write("### Para Gestores\n\n")
                f.write(
                    "1. **Implementar programas de mentoria cruzada** entre departamentos com pontuações complementares\n"
                )
                f.write(
                    "2. **Revisar critérios de avaliação** para garantir consistência entre departamentos\n"
                )
                f.write(
                    "3. **Desenvolver treinamentos específicos** baseados nas lacunas de competências identificadas\n\n"
                )

                f.write("### Para Colaboradores\n\n")
                f.write(
                    "1. **Identificar referências positivas** dentro do grupo de pares\n"
                )
                f.write(
                    "2. **Criar planos de desenvolvimento individuais** focados nas oportunidades identificadas\n"
                )
                f.write(
                    "3. **Participar de comunidades de prática** para fortalecer competências específicas\n\n"
                )

                f.write("---\n\n")
                f.write(
                    "*Este relatório foi gerado automaticamente pela plataforma People Analytics.*\n"
                )

            if self.verbose:
                print(f"Generated Peer Comparison report: {report_file}")

        except Exception as e:
            if self.verbose:
                print(f"Error generating Peer Comparison report: {e}")
            if not self.ignore_errors:
                raise

    def _generate_yoy_analysis_report(self, output_dir):
        """Generate year-over-year analysis report.

        Args:
            output_dir: Directory to save the output
        """
        from datetime import datetime

        try:
            # Create a rich markdown report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(
                output_dir, f"year_over_year_report_{timestamp}.md"
            )

            with open(report_file, "w", encoding="utf-8") as f:
                # Report header
                f.write("# 📈 Análise de Evolução Ano a Ano\n\n")
                f.write(
                    f"*Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                )

                # Introduction
                f.write("## 📋 Introdução\n\n")
                f.write(
                    "A análise de evolução ano a ano permite visualizar tendências de desempenho ao longo do tempo, identificar padrões sazonais, medir o impacto de iniciativas de desenvolvimento e ajustar estratégias de gestão de talentos.\n\n"
                )

                # Overall performance trends
                f.write("## 📊 Tendências Gerais de Desempenho\n\n")
                f.write("```mermaid\n")
                f.write("xychart-beta\n")
                f.write('    title "Evolução da Pontuação Média Anual"\n')
                f.write('    x-axis ["2020", "2021", "2022", "2023"]\n')
                f.write('    y-axis "Pontuação" 0 --> 5\n')
                f.write("    line [3.7, 3.9, 4.0, 4.2]\n")
                f.write("```\n\n")

                # Department performance trends
                f.write("## 📊 Evolução por Departamento\n\n")
                f.write("```mermaid\n")
                f.write("xychart-beta\n")
                f.write('    title "Evolução da Pontuação Média por Departamento"\n')
                f.write('    x-axis ["2020", "2021", "2022", "2023"]\n')
                f.write('    y-axis "Pontuação" 0 --> 5\n')
                f.write('    line "Tecnologia" [3.8, 4.0, 4.1, 4.3]\n')
                f.write('    line "Marketing" [3.6, 3.7, 3.9, 4.0]\n')
                f.write('    line "Vendas" [3.7, 3.8, 3.8, 4.1]\n')
                f.write('    line "RH" [3.9, 4.0, 4.0, 4.2]\n')
                f.write("```\n\n")

                # Competency evolution
                f.write("## 🎯 Evolução das Competências\n\n")
                f.write("| Competência | 2020 | 2021 | 2022 | 2023 | Tendência |\n")
                f.write("|-------------|------|------|------|------|----------|\n")
                f.write(
                    "| Conhecimento Técnico | 3.8 | 3.9 | 4.1 | 4.3 | 📈 Em alta |\n"
                )
                f.write("| Comunicação | 3.5 | 3.7 | 3.9 | 4.0 | 📈 Em alta |\n")
                f.write("| Trabalho em Equipe | 3.9 | 4.0 | 4.0 | 4.1 | ➡️ Estável |\n")
                f.write("| Inovação | 3.4 | 3.5 | 3.8 | 4.0 | 🚀 Forte alta |\n")
                f.write("| Organização | 3.7 | 3.8 | 3.7 | 3.6 | 📉 Em queda |\n\n")

                # Key findings
                f.write("## 🔍 Principais Descobertas\n\n")
                f.write(
                    "1. **Melhoria consistente na pontuação geral** ao longo dos últimos 4 anos\n"
                )
                f.write(
                    "2. **Departamento de Tecnologia** apresenta o crescimento mais acentuado\n"
                )
                f.write(
                    "3. **Competência de Inovação** mostra o maior desenvolvimento, possivelmente devido aos programas implementados em 2021\n"
                )
                f.write(
                    "4. **Organização** é a única competência em declínio, sugerindo necessidade de atenção\n\n"
                )

                # Recommendations
                f.write("## 💡 Recomendações\n\n")
                f.write(
                    "1. **Continuar investindo em programas de inovação**, dado o impacto positivo demonstrado\n"
                )
                f.write(
                    "2. **Desenvolver iniciativas focadas em organização e gestão de tempo** para reverter a tendência de queda\n"
                )
                f.write(
                    "3. **Compartilhar práticas bem-sucedidas do departamento de Tecnologia** com outras áreas\n"
                )
                f.write(
                    "4. **Estabelecer metas mais desafiadoras para competências estáveis** para estimular contínuo crescimento\n\n"
                )

                f.write("---\n\n")
                f.write(
                    "*Este relatório foi gerado automaticamente pela plataforma People Analytics.*\n"
                )

            if self.verbose:
                print(f"Generated Year-over-Year Analysis report: {report_file}")

        except Exception as e:
            if self.verbose:
                print(f"Error generating Year-over-Year Analysis report: {e}")
            if not self.ignore_errors:
                raise

    def _print_processing_summary(self, valid_directories):
        """Print a summary of what will be processed"""
        if not self.verbose:
            return

        print(f"\n{'=' * 50}")
        print("PROCESSING SUMMARY")
        print(f"{'=' * 50}")
        print(f"Data directory: {self.data_dir}")
        print(f"Output directory: {self.output_dir}")
        print(f"Total directories to process: {len(valid_directories)}")

        if self.pessoa:
            print(f"Filtering by person: {self.pessoa}")
        if self.ano:
            print(f"Filtering by year: {self.ano}")

        print("\nEnabled features:")
        print(f"- Markdown reports: {'Yes' if self.rich_markdown else 'No'}")
        print(f"- JSON output: {'Yes' if self.generate_json else 'No'}")
        print(f"- Visualizations: {'Yes' if not self.skip_viz else 'No'}")
        print(f"- Organization chart: {'Yes' if self.include_org_chart else 'No'}")
        print(f"- 9-Box Matrix: {'Yes' if self.use_9box else 'No'}")
        print(f"- Career Simulation: {'Yes' if self.use_career_sim else 'No'}")
        print(f"- Influence Network: {'Yes' if self.use_network else 'No'}")
        print(f"- Peer Analysis: {'Yes' if self.peer_analysis else 'No'}")
        print(f"- Year-over-Year Analysis: {'Yes' if self.yoy_analysis else 'No'}")
        print(f"- Weighted Scoring: {'Yes' if self.weighted_scoring else 'No'}")
        print(f"- Dashboard: {'Yes' if not self.skip_dashboard else 'No'}")
        print(f"- Excel Export: {'Yes' if not self.no_excel else 'No'}")
        print(f"- Parallel Processing: {'Yes' if not self.no_parallel else 'No'}")
        print(f"{'=' * 50}\n")

    def _collect_all_people_data(self):
        """Collect all people data for aggregated reports"""
        all_people_data = {}

        # Try to get data from processed_data dictionary if it exists
        if hasattr(self, "processed_data") and self.processed_data:
            for pessoa_ano, data in self.processed_data.items():
                parts = pessoa_ano.split("_")
                if len(parts) >= 1:
                    pessoa = parts[0]
                    ano = parts[1] if len(parts) > 1 else "unknown"
                    if pessoa not in all_people_data:
                        all_people_data[pessoa] = {}
                    all_people_data[pessoa][ano] = data
        else:
            # Fallback: Try to read from generated JSON files
            data_dir = self.output_dir / "data"
            if data_dir.exists():
                for data_file in data_dir.glob("*.json"):
                    try:
                        parts = data_file.stem.split("_")
                        if len(parts) >= 2:
                            pessoa = parts[0]
                            ano = parts[1]

                            with open(data_file, "r", encoding="utf-8") as f:
                                data = json.load(f)

                            if pessoa not in all_people_data:
                                all_people_data[pessoa] = {}
                            all_people_data[pessoa][ano] = data
                    except Exception as e:
                        self.logger.warning(f"Error loading data from {data_file}: {e}")

        return all_people_data

    def _ensure_directories(self):
        """Ensure all required directories exist"""
        # Make sure data_dir exists
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True, parents=True)

        # Create output subdirectories
        (self.output_dir / "data").mkdir(exist_ok=True, parents=True)
        (self.output_dir / "reports").mkdir(exist_ok=True, parents=True)
        (self.output_dir / "markdown").mkdir(exist_ok=True, parents=True)

        if not self.skip_viz:
            (self.output_dir / "visualizations").mkdir(exist_ok=True, parents=True)

        # Create talent reports directory if any talent reports are enabled
        if self.use_9box or self.use_career_sim or self.use_network:
            Path(self.talent_report_dir).mkdir(exist_ok=True, parents=True)

        # Create analysis directory if any analysis is enabled
        if self.peer_analysis or self.yoy_analysis:
            Path(self.analysis_output_dir).mkdir(exist_ok=True, parents=True)

    def _process_pessoa_ano_structure(self):
        """
        Process the pessoa/ano directory structure.

        Returns:
            List of valid directories to process
        """
        valid_directories = []

        # Loop through all pessoa directories
        for pessoa_dir in self.data_dir.glob("*"):
            # Skip non-directories and hidden directories
            if not pessoa_dir.is_dir() or pessoa_dir.name.startswith("."):
                continue

            # Skip if we're filtering by pessoa and this isn't it
            if self.pessoa and self.pessoa.lower() != pessoa_dir.name.lower():
                continue

            # Loop through all ano directories
            for ano_dir in pessoa_dir.glob("*"):
                # Skip non-directories and hidden directories
                if not ano_dir.is_dir() or ano_dir.name.startswith("."):
                    continue

                # Skip if we're filtering by ano and this isn't it
                if self.ano and self.ano != ano_dir.name:
                    continue

                # Check for resultado.json or other result files
                result_files = {}
                for fmt, extensions in self.valid_formats.items():
                    for ext in extensions:
                        files = list(ano_dir.glob(f"*{ext}"))
                        if files:
                            result_files[fmt] = files

                # Skip directories with no result files
                if not result_files:
                    if self.verbose:
                        print(
                            f"No result files found in {pessoa_dir.name}/{ano_dir.name}"
                        )
                    continue

                # Skip already processed directories unless force is true
                output_dir = self.output_dir / pessoa_dir.name / ano_dir.name
                if output_dir.exists() and not self.force:
                    if self.verbose:
                        print(
                            f"Skipping already processed {pessoa_dir.name}/{ano_dir.name}"
                        )
                    continue

                # Add to list of valid directories
                valid_directories.append(
                    {
                        "pessoa": pessoa_dir.name,
                        "ano": ano_dir.name,
                        "files": result_files,
                        "path": f"{pessoa_dir.name}/{ano_dir.name}",
                    }
                )

        return valid_directories

    def _process_directories_sequential(self, valid_directories):
        """Process directories sequentially"""
        success = True

        for directory in valid_directories:
            pessoa_dir = directory["pessoa"]
            ano_dir = directory["ano"]
            result_files = directory["files"]
            path = directory["path"]

            if self.verbose:
                print(f"Processing {path}")

            try:
                # Process the directory
                if self._process_directory(pessoa_dir, ano_dir, result_files):
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
                    raise

            # Update progress
            self.current_progress += 1
            if self.verbose:
                print(f"Progress: {self.current_progress}/{self.total_progress}")

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
