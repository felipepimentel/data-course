"""
Data Pipeline for People Analytics.

This module provides functionality for importing, exporting, and transforming
evaluation data.
"""

import json
import os
import shutil
import glob
import datetime
from typing import Dict, List, Any, Optional, Callable, Union


class DataPipeline:
    """Handles data import, export, and transformation."""
    
    def __init__(self, base_path: str, schema_manager = None):
        """Initialize the data pipeline.
        
        Args:
            base_path: Base directory for data storage
            schema_manager: Optional schema manager for validation
        """
        self.base_path = base_path
        self.schema_manager = schema_manager
        
        # Ensure the base directory exists
        os.makedirs(base_path, exist_ok=True)
        
    def ingest_file(self, file_path: str, year: Optional[str] = None, 
                   person: Optional[str] = None, overwrite: bool = False) -> Dict[str, Any]:
        """Ingest a single file into the database.
        
        Args:
            file_path: Path to the file to ingest
            year: Optional override for the year
            person: Optional override for the person
            overwrite: Whether to overwrite existing data
            
        Returns:
            Dictionary with status information
        """
        try:
            # Read and parse file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Extract person and year
            extracted_person = person or data.get('person')
            extracted_year = year or data.get('year')
            
            if not extracted_person or not extracted_year:
                return {
                    'success': False,
                    'file': file_path,
                    'error': 'Could not determine person or year from data'
                }
                
            # Create directory if it doesn't exist
            target_dir = os.path.join(self.base_path, extracted_year, extracted_person)
            os.makedirs(target_dir, exist_ok=True)
            
            # Determine target filename
            filename = os.path.basename(file_path)
            target_path = os.path.join(target_dir, filename)
            
            # Check if file already exists
            if os.path.exists(target_path) and not overwrite:
                return {
                    'success': False,
                    'file': file_path,
                    'error': 'File already exists and overwrite is disabled'
                }
                
            # Copy file
            shutil.copy2(file_path, target_path)
            
            return {
                'success': True,
                'file': file_path,
                'target': target_path,
                'person': extracted_person,
                'year': extracted_year
            }
            
        except Exception as e:
            return {
                'success': False,
                'file': file_path,
                'error': str(e)
            }
            
    def ingest_directory(self, directory: str, pattern: str = "*.json", 
                        overwrite: bool = False, parallel: bool = True) -> Dict[str, int]:
        """Ingest all files in a directory.
        
        Args:
            directory: Directory to ingest
            pattern: File pattern to match
            overwrite: Whether to overwrite existing data
            parallel: Whether to process files in parallel
            
        Returns:
            Dictionary with counts of successes and failures
        """
        # Find all matching files
        files = glob.glob(os.path.join(directory, pattern))
        
        results = []
        for file_path in files:
            result = self.ingest_file(file_path, overwrite=overwrite)
            results.append(result)
            
        # Count successes and failures
        success_count = sum(1 for r in results if r.get('success', False))
        failed_count = len(results) - success_count
        
        return {
            'success': success_count,
            'failed': failed_count,
            'total': len(results)
        }
        
    def create_backup(self, output_dir: Optional[str] = None) -> str:
        """Create a backup of the current database.
        
        Args:
            output_dir: Directory to save the backup (default: current dir)
            
        Returns:
            Path to the backup file
        """
        if not output_dir:
            output_dir = os.getcwd()
            
        # Create timestamp for filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"peopleanalytics_backup_{timestamp}.zip"
        backup_path = os.path.join(output_dir, backup_filename)
        
        # Create zip file
        shutil.make_archive(
            os.path.splitext(backup_path)[0],  # Remove .zip extension
            'zip',
            self.base_path
        )
        
        return backup_path
        
    def export_raw_data(self, output_file: str) -> Dict[str, Any]:
        """Export all raw data as a single JSON file.
        
        Args:
            output_file: Path to the output file
            
        Returns:
            Dictionary with export status
        """
        try:
            # Find all JSON files
            files = []
            for root, _, filenames in os.walk(self.base_path):
                for filename in filenames:
                    if filename.endswith('.json'):
                        files.append(os.path.join(root, filename))
                        
            # Read all files
            all_data = []
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_data.append(data)
                except Exception:
                    # Skip files that can't be read
                    pass
                    
            # Write to output file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2)
                
            return {
                'success': True,
                'file_count': len(all_data),
                'output_file': output_file
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
            
    def fix_all_data(self, parallel: bool = True) -> Dict[str, int]:
        """Fix common issues in all data files.
        
        Args:
            parallel: Whether to process files in parallel
            
        Returns:
            Dictionary with counts of fixed and unfixed files
        """
        # This is a placeholder for a real implementation
        return {
            'fixed': 0,
            'unfixed': 0,
            'errors': 0
        } 