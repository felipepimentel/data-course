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
        
    def _is_empty_directory(self, directory: Path) -> bool:
        """Check if a directory is empty or contains only empty files.
        
        Args:
            directory: Path to the directory
            
        Returns:
            True if directory is empty or contains only empty files
        """
        if not directory.exists() or not directory.is_dir():
            return True
            
        # Check if directory is empty
        if not any(directory.iterdir()):
            return True
            
        # Check if all files are empty
        for file in directory.iterdir():
            if file.is_file():
                try:
                    if file.stat().st_size == 0:
                        continue
                    # Check if file is valid JSON
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content or content == '{}' or content == '[]':
                            continue
                except:
                    continue
                return False
                
        return True

    def load_person_data(self, person: str, year: str) -> Optional[PersonData]:
        """Load data for a specific person and year.
        
        Args:
            person: Person name
            year: Year
            
        Returns:
            PersonData object or None if not found
        """
        try:
            # Get the directory path
            person_dir = self.data_path / person / year
            
            if not person_dir.exists():
                return None
                
            # Skip empty directories
            if self._is_empty_directory(person_dir):
                self.logger.debug(f"Skipping empty directory: {person_dir}")
                return None
                
            # Initialize data dictionary
            data_dict = {
                "nome": person,
                "ano": year,
                "frequencias": [],
                "pagamentos": []
            }
            
            # Load profile data if exists
            profile_file = person_dir / "perfil.json"
            if profile_file.exists() and profile_file.stat().st_size > 0:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content and content != '{}' and content != '[]':
                        profile_data = json.loads(content)
                        data_dict["perfil"] = profile_data
            
            # Load attendance data if exists
            attendance_file = person_dir / "frequencias.json"
            if attendance_file.exists() and attendance_file.stat().st_size > 0:
                with open(attendance_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content and content != '{}' and content != '[]':
                        attendance_data = json.loads(content)
                        data_dict["frequencias"] = attendance_data
            
            # Load payment data if exists
            payment_file = person_dir / "pagamentos.json"
            if payment_file.exists() and payment_file.stat().st_size > 0:
                with open(payment_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content and content != '{}' and content != '[]':
                        payment_data = json.loads(content)
                        data_dict["pagamentos"] = payment_data
            
            # Load resultado.json if exists (legacy format)
            resultado_file = person_dir / "resultado.json"
            if resultado_file.exists() and resultado_file.stat().st_size > 0:
                with open(resultado_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content and content != '{}' and content != '[]':
                        resultado_data = json.loads(content)
                        # Merge with existing data, but don't overwrite if already exists
                        if "frequencias" not in data_dict or not data_dict["frequencias"]:
                            data_dict["frequencias"] = resultado_data.get("frequencias", [])
                        if "pagamentos" not in data_dict or not data_dict["pagamentos"]:
                            data_dict["pagamentos"] = resultado_data.get("pagamentos", [])
                        if "perfil" not in data_dict and "perfil" in resultado_data:
                            data_dict["perfil"] = resultado_data["perfil"]
            
            # Skip if no valid data was found
            if not data_dict["frequencias"] and not data_dict["pagamentos"] and "perfil" not in data_dict:
                self.logger.debug(f"No valid data found in directory: {person_dir}")
                return None
            
            # Create PersonData object
            return PersonData.from_dict(data_dict)
            
        except Exception as e:
            self.logger.error(f"Error loading data for {person}/{year}: {e}")
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
        try:
            file_path = Path(file_path)
            
            # Skip if file is empty
            if file_path.stat().st_size == 0:
                return True, f"Skipping empty file: {file_path}"
                
            # Check if file is valid JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content or content == '{}' or content == '[]':
                    return True, f"Skipping empty JSON file: {file_path}"
                    
            # Extract person and year from path
            # Expected structure: data/person/year/file.json
            parts = file_path.parts
            if len(parts) < 4:
                return False, f"Invalid file path structure: {file_path}"
                
            person = parts[-3]
            year = parts[-2]
            filename = parts[-1]
            
            # Create person directory if needed
            person_dir = self.data_path / person / year
            person_dir.mkdir(parents=True, exist_ok=True)
            
            # Load existing data if any
            existing_data = self.load_person_data(person, year)
            data_dict = existing_data.to_dict() if existing_data else {
                "nome": person,
                "ano": year,
                "frequencias": [],
                "pagamentos": []
            }
            
            # Load the new file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content or content == '{}' or content == '[]':
                    return True, f"Skipping empty JSON file: {file_path}"
                new_data = json.loads(content)
            
            # Update data based on file type
            if filename == "perfil.json":
                data_dict["perfil"] = new_data
            elif filename == "frequencias.json":
                data_dict["frequencias"] = new_data
            elif filename == "pagamentos.json":
                data_dict["pagamentos"] = new_data
            elif filename == "resultado.json":
                # Legacy format - merge data
                if "frequencias" in new_data:
                    data_dict["frequencias"] = new_data["frequencias"]
                if "pagamentos" in new_data:
                    data_dict["pagamentos"] = new_data["pagamentos"]
                if "perfil" in new_data:
                    data_dict["perfil"] = new_data["perfil"]
            
            # Create and save PersonData
            person_data = PersonData.from_dict(data_dict)
            if self.save_person_data(person_data):
                return True, f"Successfully imported {filename} for {person} ({year})"
            else:
                return False, f"Error saving data for {person} ({year})"
                
        except Exception as e:
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
                    
                    # Add profile information if available
                    if data.profile:
                        person_summary.nome_departamento = data.profile.nome_departamento
                        person_summary.cargo = data.profile.cargo
                        person_summary.nome_gestor = data.profile.nome_gestor
            
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
                        department = data.profile.nome_departamento
                        position = data.profile.cargo
                        manager = data.profile.nome_gestor or ""
                    
                    for record in data.attendance_records:
                        attendance_entry = {
                            "pessoa": person,
                            "ano": y,
                            "data": record.date.isoformat(),
                            "presente": record.present,
                            "justificativa": record.notes
                        }
                        
                        # Add profile information if available
                        if data.profile:
                            attendance_entry.update({
                                "departamento": department,
                                "cargo": position,
                                "gestor": manager
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
                df.to_excel(writer, sheet_name="Registros de Frequência", index=False)
                
                # Create summary sheet
                if not df.empty:
                    # Group by person, department, and year if profile info is available
                    if 'departamento' in df.columns:
                        summary = df.groupby(['pessoa', 'departamento', 'cargo', 'ano']).agg({
                            'presente': ['count', 'sum']
                        })
                    else:
                        summary = df.groupby(['pessoa', 'ano']).agg({
                            'presente': ['count', 'sum']
                        })
                    
                    summary.columns = ['total_dias', 'dias_presente']
                    summary['taxa_frequencia'] = (summary['dias_presente'] / summary['total_dias']) * 100
                    summary.reset_index().to_excel(writer, sheet_name="Resumo", index=False)
                    
                    # Add department summary if available
                    if 'departamento' in df.columns:
                        dept_summary = df.groupby(['departamento']).agg({
                            'presente': ['count', 'sum']
                        })
                        dept_summary.columns = ['total_dias', 'dias_presente']
                        dept_summary['taxa_frequencia'] = (dept_summary['dias_presente'] / dept_summary['total_dias']) * 100
                        dept_summary.reset_index().to_excel(writer, sheet_name="Resumo por Departamento", index=False)
        
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
                        department = data.profile.nome_departamento
                        position = data.profile.cargo
                        manager = data.profile.nome_gestor or ""
                    
                    for record in data.payment_records:
                        payment_entry = {
                            "pessoa": person,
                            "ano": y,
                            "data": record.date.isoformat(),
                            "valor": record.amount,
                            "status": record.status,
                            "referencia": record.reference
                        }
                        
                        # Add profile information if available
                        if data.profile:
                            payment_entry.update({
                                "departamento": department,
                                "cargo": position,
                                "gestor": manager
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
                df.to_excel(writer, sheet_name="Registros de Pagamento", index=False)
                
                # Create summary sheet
                if not df.empty:
                    # Group by person, department, and year if profile info is available
                    if 'departamento' in df.columns:
                        summary = df.groupby(['pessoa', 'departamento', 'cargo', 'ano']).agg({
                            'valor': ['count', 'sum', 'mean']
                        })
                    else:
                        summary = df.groupby(['pessoa', 'ano']).agg({
                            'valor': ['count', 'sum', 'mean']
                        })
                    
                    summary.columns = ['total_pagamentos', 'valor_total', 'valor_medio']
                    summary.reset_index().to_excel(writer, sheet_name="Resumo", index=False)
                    
                    # Add department summary if available
                    if 'departamento' in df.columns:
                        dept_summary = df.groupby(['departamento']).agg({
                            'valor': ['count', 'sum', 'mean']
                        })
                        dept_summary.columns = ['total_pagamentos', 'valor_total', 'valor_medio']
                        dept_summary.reset_index().to_excel(writer, sheet_name="Resumo por Departamento", index=False)
        
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