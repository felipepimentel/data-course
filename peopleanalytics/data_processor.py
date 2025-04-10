"""
Data processor for People Analytics.

This module provides functionality for processing people data, 
including importing, validation, analysis, and reporting.
"""

import json
import os
import glob
import shutil
import pandas as pd
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Union, Tuple
import logging
from datetime import datetime

from .data_model import PersonData, PersonSummary, RecordStatus, AttendanceRecord, PaymentRecord


class DataProcessor:
    """Process and analyze people data."""
    
    def __init__(self, data_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None):
        """Initialize the data processor.
        
        Args:
            data_path: Path to the data directory
            output_path: Path to the output directory (defaults to 'output' in current dir)
        """
        self.data_path = Path(data_path)
        self.output_path = Path(output_path) if output_path else Path("output")
        
        # Ensure directories exist
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Cache for loaded data
        self._person_data_cache = {}
        
    def _setup_logging(self):
        """Set up logging for the data processor."""
        log_path = self.output_path / "logs"
        log_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_path / f"data_processor_{timestamp}.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("DataProcessor")
        self.logger.info(f"DataProcessor initialized with data_path={self.data_path}, output_path={self.output_path}")

    def get_all_people(self) -> List[str]:
        """Get a list of all people in the data directory."""
        people = []
        for item in self.data_path.iterdir():
            if item.is_dir():
                people.append(item.name)
        return sorted(people)
        
    def get_all_years_for_person(self, person: str) -> List[str]:
        """Get all years available for a person."""
        person_dir = self.data_path / person
        years = []
        
        if person_dir.exists() and person_dir.is_dir():
            for item in person_dir.iterdir():
                if item.is_dir():
                    years.append(item.name)
                    
        return sorted(years)
        
    def get_all_years(self) -> Set[str]:
        """Get all years across all people."""
        years = set()
        for person in self.get_all_people():
            years.update(self.get_all_years_for_person(person))
        return years
        
    def get_people_for_year(self, year: str) -> List[str]:
        """Get all people who have data for a specific year."""
        people = []
        for person in self.get_all_people():
            person_years = self.get_all_years_for_person(person)
            if year in person_years:
                people.append(person)
        return sorted(people)
        
    def load_person_data(self, person: str, year: str) -> Optional[PersonData]:
        """Load data for a specific person and year."""
        cache_key = f"{person}_{year}"
        
        # Check cache first
        if cache_key in self._person_data_cache:
            return self._person_data_cache[cache_key]
            
        file_path = self.data_path / person / year / "data.json"
        
        if not file_path.exists():
            self.logger.warning(f"Data file not found: {file_path}")
            return None
            
        try:
            data = PersonData.load(file_path)
            self._person_data_cache[cache_key] = data
            return data
        except Exception as e:
            self.logger.error(f"Error loading data for {person} ({year}): {e}")
            return None
            
    def save_person_data(self, data: PersonData) -> bool:
        """Save person data to the appropriate location."""
        try:
            file_path = data.save(self.data_path)
            
            # Update cache
            cache_key = f"{data.name}_{data.year}"
            self._person_data_cache[cache_key] = data
            
            self.logger.info(f"Saved data for {data.name} ({data.year}) to {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving data for {data.name} ({data.year}): {e}")
            return False
            
    def create_person_data(self, name: str, year: int) -> PersonData:
        """Create a new PersonData object."""
        return PersonData(name=name, year=year)
    
    def import_json_file(self, file_path: Union[str, Path], overwrite: bool = False) -> Tuple[bool, str]:
        """Import a JSON file into the data structure.
        
        Args:
            file_path: Path to the JSON file
            overwrite: Whether to overwrite existing data
            
        Returns:
            Tuple of (success, message)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return False, f"File not found: {file_path}"
            
        try:
            # Load and parse the file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Create PersonData object
            person_data = PersonData.from_dict(data)
            
            # Check if data already exists
            existing_file = self.data_path / person_data.name / str(person_data.year) / "data.json"
            if existing_file.exists() and not overwrite:
                return False, f"Data already exists for {person_data.name} ({person_data.year}). Use overwrite=True to replace."
                
            # Save the data
            file_path = person_data.save(self.data_path)
            
            # Update cache
            cache_key = f"{person_data.name}_{person_data.year}"
            self._person_data_cache[cache_key] = person_data
            
            return True, f"Successfully imported data for {person_data.name} ({person_data.year}) to {file_path}"
        
        except Exception as e:
            self.logger.error(f"Error importing file {file_path}: {e}")
            return False, f"Error importing file: {str(e)}"
            
    def import_directory(self, directory: Union[str, Path], pattern: str = "*.json", 
                        recursive: bool = True) -> Dict[str, Any]:
        """Import all JSON files from a directory.
        
        Args:
            directory: Directory to import from
            pattern: File pattern to match
            recursive: Whether to search recursively
            
        Returns:
            Dict with import statistics
        """
        directory = Path(directory)
        
        if not directory.exists() or not directory.is_dir():
            return {"success": False, "error": f"Directory not found: {directory}"}
            
        # Find all matching files
        if recursive:
            search_pattern = f"**/{pattern}"
        else:
            search_pattern = pattern
            
        files = list(directory.glob(search_pattern))
        
        if not files:
            return {"success": True, "imported": 0, "message": "No files found"}
            
        # Process each file
        results = {
            "success": True,
            "total": len(files),
            "imported": 0,
            "failed": 0,
            "errors": []
        }
        
        for file_path in files:
            success, message = self.import_json_file(file_path, overwrite=True)
            
            if success:
                results["imported"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({"file": str(file_path), "error": message})
                
        return results
        
    def export_person_data(self, person: str, year: str, output_file: Optional[Union[str, Path]] = None) -> Tuple[bool, str]:
        """Export person data to a JSON file.
        
        Args:
            person: Person name
            year: Year
            output_file: Optional output file path
            
        Returns:
            Tuple of (success, message)
        """
        data = self.load_person_data(person, year)
        
        if not data:
            return False, f"No data found for {person} ({year})"
            
        if output_file is None:
            # Default to output directory
            output_dir = self.output_path / "exports" / person
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"{year}.json"
            
        output_file = Path(output_file)
        
        try:
            # Ensure the directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save the data
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data.to_dict(), f, ensure_ascii=False, indent=2)
                
            return True, f"Successfully exported data to {output_file}"
        
        except Exception as e:
            self.logger.error(f"Error exporting data for {person} ({year}): {e}")
            return False, f"Error exporting data: {str(e)}"
            
    def export_all_data(self) -> Dict[str, Any]:
        """Export all data to the output directory."""
        export_dir = self.output_path / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            "total": 0,
            "exported": 0,
            "failed": 0,
            "errors": []
        }
        
        # Export each person's data
        for person in self.get_all_people():
            for year in self.get_all_years_for_person(person):
                results["total"] += 1
                
                success, message = self.export_person_data(person, year)
                
                if success:
                    results["exported"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append({"person": person, "year": year, "error": message})
                    
        return results
        
    def generate_summary(self, output_format: str = "json") -> str:
        """Generate a summary of all people data.
        
        Args:
            output_format: Output format ('json', 'csv', or 'html')
            
        Returns:
            Path to the generated summary file
        """
        summary_dir = self.output_path / "summary"
        summary_dir.mkdir(parents=True, exist_ok=True)
        
        summaries = []
        
        # Generate summary for each person
        for person in self.get_all_people():
            years = self.get_all_years_for_person(person)
            person_summary = PersonSummary(
                name=person,
                years=[int(y) for y in years]
            )
            
            # Collect data across all years
            for year in years:
                data = self.load_person_data(person, year)
                if data:
                    attendance_summary = data.get_attendance_summary()
                    payment_summary = data.get_payment_summary()
                    
                    person_summary.total_attendance += attendance_summary["total"]
                    person_summary.present_count += attendance_summary["present"]
                    person_summary.total_payments += payment_summary["total_payments"]
                    person_summary.total_amount += payment_summary["total_amount"]
            
            summaries.append(person_summary.to_dict())
        
        # Generate file based on format
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format == "json":
            output_file = summary_dir / f"summary_{timestamp}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(summaries, f, ensure_ascii=False, indent=2)
                
        elif output_format == "csv":
            output_file = summary_dir / f"summary_{timestamp}.csv"
            df = pd.DataFrame(summaries)
            df.to_csv(output_file, index=False)
            
        elif output_format == "html":
            output_file = summary_dir / f"summary_{timestamp}.html"
            df = pd.DataFrame(summaries)
            df.to_html(output_file, index=False)
            
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
            
        return str(output_file)
        
    def generate_attendance_report(self, year: Optional[str] = None) -> str:
        """Generate an attendance report.
        
        Args:
            year: Optional year to filter by
            
        Returns:
            Path to the generated report
        """
        report_dir = self.output_path / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        all_attendance = []
        
        # Collect attendance data
        if year:
            years = [year]
            people = self.get_people_for_year(year)
        else:
            years = self.get_all_years()
            people = self.get_all_people()
            
        for person in people:
            for y in years:
                if year and y != year:
                    continue
                    
                data = self.load_person_data(person, y)
                if data:
                    for record in data.attendance_records:
                        all_attendance.append({
                            "person": person,
                            "year": y,
                            "date": record.date.isoformat(),
                            "present": record.present,
                            "notes": record.notes
                        })
        
        # Create DataFrame
        df = pd.DataFrame(all_attendance)
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        year_suffix = f"_{year}" if year else ""
        report_file = report_dir / f"attendance_report{year_suffix}_{timestamp}.xlsx"
        
        if not df.empty:
            # Add summary sheet
            with pd.ExcelWriter(report_file) as writer:
                df.to_excel(writer, sheet_name="Attendance Records", index=False)
                
                # Create summary sheet
                if not df.empty:
                    summary = df.groupby(['person', 'year']).agg({
                        'present': ['count', 'sum']
                    })
                    
                    summary.columns = ['total_days', 'days_present']
                    summary['attendance_rate'] = (summary['days_present'] / summary['total_days']) * 100
                    summary.reset_index().to_excel(writer, sheet_name="Summary", index=False)
        
        return str(report_file)
        
    def generate_payment_report(self, year: Optional[str] = None) -> str:
        """Generate a payment report.
        
        Args:
            year: Optional year to filter by
            
        Returns:
            Path to the generated report
        """
        report_dir = self.output_path / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        all_payments = []
        
        # Collect payment data
        if year:
            years = [year]
            people = self.get_people_for_year(year)
        else:
            years = self.get_all_years()
            people = self.get_all_people()
            
        for person in people:
            for y in years:
                if year and y != year:
                    continue
                    
                data = self.load_person_data(person, y)
                if data:
                    for record in data.payment_records:
                        all_payments.append({
                            "person": person,
                            "year": y,
                            "date": record.date.isoformat(),
                            "amount": record.amount,
                            "status": record.status,
                            "reference": record.reference
                        })
        
        # Create DataFrame
        df = pd.DataFrame(all_payments)
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        year_suffix = f"_{year}" if year else ""
        report_file = report_dir / f"payment_report{year_suffix}_{timestamp}.xlsx"
        
        if not df.empty:
            # Add summary sheet
            with pd.ExcelWriter(report_file) as writer:
                df.to_excel(writer, sheet_name="Payment Records", index=False)
                
                # Create summary sheet
                if not df.empty:
                    summary = df.groupby(['person', 'year']).agg({
                        'amount': ['count', 'sum', 'mean']
                    })
                    
                    summary.columns = ['payment_count', 'total_amount', 'average_payment']
                    summary.reset_index().to_excel(writer, sheet_name="Summary", index=False)
        
        return str(report_file)
        
    def validate_all_data(self) -> Dict[str, Any]:
        """Validate all data files in the system.
        
        Returns:
            Dictionary with validation results
        """
        results = {
            "total": 0,
            "valid": 0,
            "invalid": 0,
            "issues": []
        }
        
        for person in self.get_all_people():
            for year in self.get_all_years_for_person(person):
                results["total"] += 1
                
                data = self.load_person_data(person, year)
                if not data:
                    results["invalid"] += 1
                    results["issues"].append({
                        "person": person,
                        "year": year,
                        "status": "ERROR",
                        "message": "Could not load data"
                    })
                    continue
                    
                status = data.validate()
                
                if status == RecordStatus.VALID:
                    results["valid"] += 1
                else:
                    results["invalid"] += 1
                    results["issues"].append({
                        "person": person,
                        "year": year,
                        "status": status.value,
                        "message": f"Validation failed with status {status.value}"
                    })
                    
        return results
        
    def create_backup(self) -> str:
        """Create a backup of all data.
        
        Returns:
            Path to the backup file
        """
        backup_dir = self.output_path / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"data_backup_{timestamp}.zip"
        
        # Create a zip file of the data directory
        shutil.make_archive(
            str(backup_file).replace('.zip', ''),
            'zip',
            str(self.data_path)
        )
        
        return str(backup_file)
        
    def plot_attendance_summary(self, year: Optional[str] = None) -> str:
        """Plot attendance summary for all people.
        
        Args:
            year: Optional year to filter by
            
        Returns:
            Path to the generated plot
        """
        plot_dir = self.output_path / "plots"
        plot_dir.mkdir(parents=True, exist_ok=True)
        
        # Collect attendance data
        attendance_data = []
        
        if year:
            years = [year]
            people = self.get_people_for_year(year)
        else:
            years = self.get_all_years()
            people = self.get_all_people()
            
        for person in people:
            for y in years:
                if year and y != year:
                    continue
                    
                data = self.load_person_data(person, y)
                if data:
                    summary = data.get_attendance_summary()
                    attendance_data.append({
                        "person": person,
                        "year": y,
                        "attendance_rate": summary["attendance_rate"]
                    })
        
        if not attendance_data:
            return "No data available"
            
        # Create DataFrame
        df = pd.DataFrame(attendance_data)
        
        # Create plot
        plt.figure(figsize=(10, 6))
        
        if year:
            # For a single year, show all people
            plot = df.plot(
                kind='bar',
                x='person',
                y='attendance_rate',
                title=f'Attendance Rate by Person ({year})',
                legend=False
            )
        else:
            # Group by person and show average across years
            avg_attendance = df.groupby('person')['attendance_rate'].mean().reset_index()
            plot = avg_attendance.plot(
                kind='bar',
                x='person',
                y='attendance_rate',
                title='Average Attendance Rate by Person (All Years)',
                legend=False
            )
            
        plt.xlabel('Person')
        plt.ylabel('Attendance Rate (%)')
        plt.tight_layout()
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        year_suffix = f"_{year}" if year else ""
        plot_file = plot_dir / f"attendance_plot{year_suffix}_{timestamp}.png"
        plt.savefig(plot_file)
        plt.close()
        
        return str(plot_file)
        
    def plot_payment_summary(self, year: Optional[str] = None) -> str:
        """Plot payment summary for all people.
        
        Args:
            year: Optional year to filter by
            
        Returns:
            Path to the generated plot
        """
        plot_dir = self.output_path / "plots"
        plot_dir.mkdir(parents=True, exist_ok=True)
        
        # Collect payment data
        payment_data = []
        
        if year:
            years = [year]
            people = self.get_people_for_year(year)
        else:
            years = self.get_all_years()
            people = self.get_all_people()
            
        for person in people:
            for y in years:
                if year and y != year:
                    continue
                    
                data = self.load_person_data(person, y)
                if data:
                    summary = data.get_payment_summary()
                    payment_data.append({
                        "person": person,
                        "year": y,
                        "total_amount": summary["total_amount"]
                    })
        
        if not payment_data:
            return "No data available"
            
        # Create DataFrame
        df = pd.DataFrame(payment_data)
        
        # Create plot
        plt.figure(figsize=(10, 6))
        
        if year:
            # For a single year, show all people
            plot = df.plot(
                kind='bar',
                x='person',
                y='total_amount',
                title=f'Total Payments by Person ({year})',
                legend=False
            )
        else:
            # Group by person and show total across years
            total_payments = df.groupby('person')['total_amount'].sum().reset_index()
            plot = total_payments.plot(
                kind='bar',
                x='person',
                y='total_amount',
                title='Total Payments by Person (All Years)',
                legend=False
            )
            
        plt.xlabel('Person')
        plt.ylabel('Total Amount')
        plt.tight_layout()
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        year_suffix = f"_{year}" if year else ""
        plot_file = plot_dir / f"payment_plot{year_suffix}_{timestamp}.png"
        plt.savefig(plot_file)
        plt.close()
        
        return str(plot_file) 