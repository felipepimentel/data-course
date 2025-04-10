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
import re

from .data_model import PersonData, PersonSummary, RecordStatus, AttendanceRecord, PaymentRecord, ProfileData


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
        """
        Load data for a specific person and year.
        
        Args:
            person (str): The name of the person.
            year (str): The year to load data for.
            
        Returns:
            PersonData: A PersonData object containing the loaded data, or None if data could not be loaded.
        """
        cache_key = f"{person}_{year}"
        
        # Check cache first
        if cache_key in self._person_data_cache:
            return self._person_data_cache[cache_key]
            
        try:
            person_data_path = os.path.join(self.data_path, person, year)
            resultado_file = os.path.join(person_data_path, "resultado.json")
            perfil_file = os.path.join(person_data_path, "perfil.json")
            
            # Check if resultado.json exists
            if not os.path.exists(resultado_file):
                # No data found - log at DEBUG level instead of WARNING to reduce noise
                self.logger.debug(f"No data found for {person}/{year} - missing resultado.json")
                return None
                
            # New structure with separate resultado.json file
            with open(resultado_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
                
            # Prepare the data dictionary with Portuguese field mappings
            data_dict = {
                "nome": person,
                "ano": int(year) if year.isdigit() else year,
                "frequencias": [],
                "pagamentos": []
            }
            
            # Copy data from resultado.json
            if "nome" in raw_data:
                data_dict["nome"] = raw_data["nome"]
            if "ano" in raw_data:
                data_dict["ano"] = raw_data["ano"]
            if "frequencias" in raw_data:
                data_dict["frequencias"] = raw_data["frequencias"]
            if "pagamentos" in raw_data:
                data_dict["pagamentos"] = raw_data["pagamentos"]
            
            # Check if profile data exists
            profile_data = None
            if os.path.exists(perfil_file):
                try:
                    with open(perfil_file, 'r', encoding='utf-8') as f:
                        profile_data = json.load(f)
                except Exception as e:
                    self.logger.warning(f"Error reading profile file for {person} ({year}): {e}")
            
            # Create PersonData with profile
            person_data = PersonData.from_dict(data_dict, profile_data)
                
            # Cache the data
            self._person_data_cache[cache_key] = person_data
            return person_data
            
        except Exception as e:
            self.logger.error(f"Error loading data for {person}/{year}: {str(e)}")
            return None
            
    def save_person_data(self, data: PersonData) -> bool:
        """Save person data to the appropriate location."""
        try:
            # Create directory structure if needed
            person_dir = self.data_path / data.name
            year_dir = person_dir / str(data.year)
            year_dir.mkdir(parents=True, exist_ok=True)
            
            # Save resultado.json
            resultado_file = year_dir / "resultado.json"
            with open(resultado_file, 'w', encoding='utf-8') as f:
                json.dump(data.to_dict(), f, ensure_ascii=False, indent=2)
                
            # Save perfil.json if profile data exists
            if data.profile:
                perfil_file = year_dir / "perfil.json"
                with open(perfil_file, 'w', encoding='utf-8') as f:
                    json.dump(data.get_profile_dict(), f, ensure_ascii=False, indent=2)
                
                self.logger.info(f"Saved data for {data.name} ({data.year}) to {resultado_file} and profile to {perfil_file}")
            else:
                self.logger.info(f"Saved data for {data.name} ({data.year}) to {resultado_file}")
            
            # Update cache
            cache_key = f"{data.name}_{data.year}"
            self._person_data_cache[cache_key] = data
            
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
            # Detect file type (resultado.json, perfil.json, or other JSON)
            file_name = file_path.name.lower()
            
            # Check if it's a profile file
            if file_name == "perfil.json":
                # Find the corresponding resultado.json in the same directory
                resultado_file = file_path.parent / "resultado.json"
                if not resultado_file.exists():
                    return False, f"Found profile file but no matching resultado.json in {file_path.parent}"
                    
                # Load both files and create a complete PersonData
                with open(file_path, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                    
                with open(resultado_file, 'r', encoding='utf-8') as f:
                    result_data = json.load(f)
                    
                # Create a new PersonData with both datasets
                person_data = PersonData.from_dict(result_data, profile_data)
                
            # Check if it's a resultado file
            elif file_name == "resultado.json":
                # Load the resultado file
                with open(file_path, 'r', encoding='utf-8') as f:
                    result_data = json.load(f)
                    
                # Check if there's a matching profile file
                profile_file = file_path.parent / "perfil.json"
                profile_data = None
                if profile_file.exists():
                    try:
                        with open(profile_file, 'r', encoding='utf-8') as f:
                            profile_data = json.load(f)
                    except Exception as e:
                        self.logger.warning(f"Error reading profile file {profile_file}: {e}")
                    
                # Create a new PersonData with both datasets
                person_data = PersonData.from_dict(result_data, profile_data)
                
            # Any other JSON file (must be in the new format)
            else:
                # Load and parse the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Create PersonData object
                person_data = PersonData.from_dict(data)
            
            # Check for required fields
            if not person_data.name:
                return False, f"Invalid data file: missing name in {file_path}"
                
            # If year is missing in data file, try to extract it from the file path
            if not person_data.year:
                try:
                    # Extract year from path (expected structure: */nome_pessoa/ano/* or */ano/nome_pessoa/*)
                    parts = file_path.parts
                    
                    # First check for */nome_pessoa/ano/* structure
                    for i, part in enumerate(parts):
                        if part == person_data.name and i+1 < len(parts):
                            # Next part might be the year
                            potential_year = parts[i+1]
                            if potential_year.isdigit():
                                self.logger.info(f"Year not found in file, extracted from path: {potential_year}")
                                person_data.year = int(potential_year)
                                break
                    
                    # If we still don't have a year, check for */ano/nome_pessoa/* structure
                    if not person_data.year:
                        for i, part in enumerate(parts):
                            if i > 0 and part == person_data.name and parts[i-1].isdigit():
                                # Previous part might be the year
                                potential_year = parts[i-1]
                                self.logger.info(f"Year not found in file, extracted from path: {potential_year}")
                                person_data.year = int(potential_year)
                                break
                    
                    # If we still don't have a year, check for any 4-digit year in path
                    if not person_data.year:
                        for part in parts:
                            if part.isdigit() and len(part) == 4:
                                potential_year = part
                                self.logger.info(f"Year not found in file, extracted from path (4-digit number): {potential_year}")
                                person_data.year = int(potential_year)
                                break
                    
                    # If we still don't have a year, check for 4-digit year in the filename
                    if not person_data.year:
                        filename = file_path.name
                        # Look for 4-digit sequences that could be years
                        year_matches = re.findall(r'20\d{2}', filename)
                        if year_matches:
                            potential_year = year_matches[0]
                            self.logger.info(f"Year not found in file, extracted from filename: {potential_year}")
                            person_data.year = int(potential_year)
                    
                    # If we still don't have a year, check for "Year20XX" pattern in path
                    if not person_data.year:
                        for part in parts:
                            year_matches = re.findall(r'Year(20\d{2})', part)
                            if year_matches:
                                potential_year = year_matches[0]
                                self.logger.info(f"Year not found in file, extracted from 'Year' prefix in path: {potential_year}")
                                person_data.year = int(potential_year)
                                break
                    
                    # If we still don't have a year, check for "year_XXXX" pattern in path
                    if not person_data.year:
                        for part in parts:
                            year_matches = re.findall(r'year[_-]?(20\d{2})', part.lower())
                            if year_matches:
                                potential_year = year_matches[0]
                                self.logger.info(f"Year not found in file, extracted from 'year_' pattern in path: {potential_year}")
                                person_data.year = int(potential_year)
                                break
                                
                except Exception as e:
                    self.logger.warning(f"Failed to extract year from path: {e}")
                    
            # Double-check we have a year
            if not person_data.year:
                return False, f"Invalid data file: missing year in {file_path} and could not extract from path"
                
            # Check if data already exists
            existing_path = self.data_path / person_data.name / str(person_data.year)
            existing_resultado = existing_path / "resultado.json"
            
            if existing_resultado.exists() and not overwrite:
                return False, f"Data already exists for {person_data.name} ({person_data.year}). Use overwrite=True to replace."
                
            # Save the data using our save method, which will use the new format
            if self.save_person_data(person_data):
                return True, f"Successfully imported data for {person_data.name} ({person_data.year})"
            else:
                return False, f"Error saving imported data for {person_data.name} ({person_data.year})"
        
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
                    # Get profile information
                    department = ""
                    position = ""
                    manager = ""
                    if data.profile:
                        department = data.profile.department
                        position = data.profile.position
                        manager = data.profile.manager_name or ""
                    
                    for record in data.attendance_records:
                        attendance_entry = {
                            "person": person,
                            "year": y,
                            "date": record.date.isoformat(),
                            "present": record.present,
                            "notes": record.notes
                        }
                        
                        # Add profile information if available
                        if data.profile:
                            attendance_entry.update({
                                "department": department,
                                "position": position,
                                "manager": manager
                            })
                            
                        all_attendance.append(attendance_entry)
        
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
                    # Group by person, department, and year if profile info is available
                    if 'department' in df.columns:
                        summary = df.groupby(['person', 'department', 'position', 'year']).agg({
                            'present': ['count', 'sum']
                        })
                    else:
                        summary = df.groupby(['person', 'year']).agg({
                            'present': ['count', 'sum']
                        })
                    
                    summary.columns = ['total_days', 'days_present']
                    summary['attendance_rate'] = (summary['days_present'] / summary['total_days']) * 100
                    summary.reset_index().to_excel(writer, sheet_name="Summary", index=False)
                    
                    # Add department summary if available
                    if 'department' in df.columns:
                        dept_summary = df.groupby(['department']).agg({
                            'present': ['count', 'sum']
                        })
                        dept_summary.columns = ['total_days', 'days_present']
                        dept_summary['attendance_rate'] = (dept_summary['days_present'] / dept_summary['total_days']) * 100
                        dept_summary.reset_index().to_excel(writer, sheet_name="Department Summary", index=False)
        
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
                    # Get profile information
                    department = ""
                    position = ""
                    manager = ""
                    if data.profile:
                        department = data.profile.department
                        position = data.profile.position
                        manager = data.profile.manager_name or ""
                    
                    for record in data.payment_records:
                        payment_entry = {
                            "person": person,
                            "year": y,
                            "date": record.date.isoformat(),
                            "amount": record.amount,
                            "status": record.status,
                            "reference": record.reference
                        }
                        
                        # Add profile information if available
                        if data.profile:
                            payment_entry.update({
                                "department": department,
                                "position": position,
                                "manager": manager
                            })
                            
                        all_payments.append(payment_entry)
        
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
                    # Group by person, department, and year if profile info is available
                    if 'department' in df.columns:
                        summary = df.groupby(['person', 'department', 'position', 'year']).agg({
                            'amount': ['count', 'sum', 'mean']
                        })
                    else:
                        summary = df.groupby(['person', 'year']).agg({
                            'amount': ['count', 'sum', 'mean']
                        })
                    
                    summary.columns = ['payment_count', 'total_amount', 'average_payment']
                    summary.reset_index().to_excel(writer, sheet_name="Summary", index=False)
                    
                    # Add department summary if available
                    if 'department' in df.columns:
                        dept_summary = df.groupby(['department']).agg({
                            'amount': ['count', 'sum', 'mean']
                        })
                        dept_summary.columns = ['payment_count', 'total_amount', 'average_payment']
                        dept_summary.reset_index().to_excel(writer, sheet_name="Department Summary", index=False)
        
        return str(report_file)
        
    def validate_person_data(self, person: str, year: str) -> Dict[str, Any]:
        """Validate data for a specific person and year.
        
        Args:
            person: Person name
            year: Year
            
        Returns:
            Dict with validation status and messages
        """
        try:
            # Load the data
            data = self.load_person_data(person, year)
            
            if not data:
                return {
                    "status": RecordStatus.ERROR,
                    "message": f"Could not load data for {person}/{year}"
                }
                
            # Basic validation
            status = data.validate()
            
            # Prepare result
            result = {
                "status": status,
                "message": ""
            }
            
            # Add more detailed validation
            if status == RecordStatus.INCOMPLETE:
                result["message"] = "Missing required fields"
            elif status == RecordStatus.INVALID:
                result["message"] = "Invalid data"
            elif status == RecordStatus.ERROR:
                result["message"] = "Error validating data"
            
            # Check for errors in attendance records
            errors = []
            warnings = []
            
            # Validate attendance records
            if not data.attendance_records:
                warnings.append("No attendance records found")
            else:
                for i, record in enumerate(data.attendance_records):
                    if not record.date:
                        errors.append(f"Missing date in attendance record #{i+1}")
            
            # Validate payment records
            if not data.payment_records:
                warnings.append("No payment records found")
            else:
                for i, record in enumerate(data.payment_records):
                    if not record.date:
                        errors.append(f"Missing date in payment record #{i+1}")
                    if record.amount <= 0:
                        errors.append(f"Invalid amount in payment record #{i+1}")
            
            # Validate profile
            if not data.profile:
                warnings.append("No profile data found")
            elif not data.profile.full_name:
                warnings.append("Profile missing full name")
            
            # Add error and warning messages
            if errors:
                result["status"] = RecordStatus.INVALID
                result["message"] = "; ".join(errors)
            elif warnings and not result["message"]:
                result["message"] = "; ".join(warnings)
                
            return result
            
        except Exception as e:
            return {
                "status": RecordStatus.ERROR,
                "message": str(e)
            }
        
    def validate_all_data(self) -> Dict[str, Any]:
        """Validate all data in the system.
        
        Returns:
            Dict with validation results
        """
        results = {
            "total": 0,
            "valid": 0,
            "invalid": 0,
            "issues": []
        }
        
        # Get all people and years
        people = self.get_all_people()
        
        # Validate each person's data
        for person in people:
            years = self.get_all_years_for_person(person)
            
            for year in years:
                results["total"] += 1
                
                # Validate the data
                validation_result = self.validate_person_data(person, year)
                
                if validation_result["status"] == RecordStatus.VALID:
                    results["valid"] += 1
                else:
                    results["invalid"] += 1
                    
                    # Add issue details
                    results["issues"].append({
                        "person": person,
                        "year": year,
                        "status": validation_result["status"].value,
                        "message": validation_result["message"]
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