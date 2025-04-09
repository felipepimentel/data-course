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
        self.debug_mode = False
        
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
        debug_info = []
        if self.debug_mode:
            debug_info.append(f"Processing file: {file_path}")
            debug_info.append(f"Year override: {year}, Person override: {person}")
        
        try:
            # Read and parse file
            try:
                if self.debug_mode:
                    debug_info.append("Reading file content")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if self.debug_mode:
                    debug_info.append(f"Successfully parsed JSON with {len(data.keys() if isinstance(data, dict) else data)} keys/items")
                
            except json.JSONDecodeError as e:
                error_info = {
                    'success': False,
                    'file': file_path,
                    'error': f'JSON parsing error: {str(e)}',
                    'error_type': 'json_decode'
                }
                if self.debug_mode:
                    error_info['debug_info'] = debug_info
                    error_info['error_trace'] = str(e)
                return error_info
                
            except UnicodeDecodeError as e:
                error_info = {
                    'success': False,
                    'file': file_path,
                    'error': f'File encoding error: {str(e)}',
                    'error_type': 'encoding'
                }
                if self.debug_mode:
                    error_info['debug_info'] = debug_info
                    error_info['error_trace'] = str(e)
                return error_info
                
            except FileNotFoundError:
                error_info = {
                    'success': False,
                    'file': file_path,
                    'error': 'File not found',
                    'error_type': 'not_found'
                }
                if self.debug_mode:
                    error_info['debug_info'] = debug_info
                return error_info
                
            except PermissionError:
                error_info = {
                    'success': False,
                    'file': file_path,
                    'error': 'Permission denied',
                    'error_type': 'permission'
                }
                if self.debug_mode:
                    error_info['debug_info'] = debug_info
                return error_info
                
            # Extract person and year
            extracted_person = person or data.get('person')
            extracted_year = year or data.get('year')
            
            if self.debug_mode:
                debug_info.append(f"Extracted person: {extracted_person}, year: {extracted_year}")
            
            # Attempt to extract from structure like <person>/<year>/result.json
            if not extracted_person or not extracted_year:
                try:
                    parts = os.path.normpath(file_path).split(os.sep)
                    if len(parts) >= 3:
                        # Try to use the parent directories as person/year
                        potential_year = parts[-2]  # Second last component
                        potential_person = parts[-3]  # Third last component
                        
                        if self.debug_mode:
                            debug_info.append(f"Attempting to extract from path - potential year: {potential_year}, person: {potential_person}")
                        
                        extracted_year = extracted_year or potential_year
                        extracted_person = extracted_person or potential_person
                        
                        if self.debug_mode:
                            debug_info.append(f"After path extraction - year: {extracted_year}, person: {extracted_person}")
                except Exception as e:
                    if self.debug_mode:
                        debug_info.append(f"Path extraction error: {str(e)}")
                    # If this fails, continue with the original values
                    pass
                
                # If still no person/year, report error
                if not extracted_person or not extracted_year:
                    missing = []
                    if not extracted_person:
                        missing.append("person")
                    if not extracted_year:
                        missing.append("year")
                        
                    error_info = {
                        'success': False,
                        'file': file_path,
                        'error': f'Missing required fields: {", ".join(missing)}',
                        'error_type': 'missing_fields',
                        'data_keys': list(data.keys()) if isinstance(data, dict) else []
                    }
                    if self.debug_mode:
                        error_info['debug_info'] = debug_info
                    return error_info
                
            # Create directory if it doesn't exist - use <person>/<year>/resultado.json pattern
            target_dir = os.path.join(self.base_path, extracted_person, extracted_year)
            if self.debug_mode:
                debug_info.append(f"Target directory: {target_dir}")
                
            os.makedirs(target_dir, exist_ok=True)
            
            # Determine target filename - use resultado.json as standard
            target_path = os.path.join(target_dir, "resultado.json")
            
            if self.debug_mode:
                debug_info.append(f"Target filename: resultado.json")
                debug_info.append(f"Full target path: {target_path}")
                debug_info.append(f"Checking if target exists: {os.path.exists(target_path)}")
            
            # Check if file already exists
            if os.path.exists(target_path) and not overwrite:
                error_info = {
                    'success': False,
                    'file': file_path,
                    'error': 'File already exists and overwrite is disabled',
                    'error_type': 'exists'
                }
                if self.debug_mode:
                    error_info['debug_info'] = debug_info
                return error_info
                
            # Copy file
            if self.debug_mode:
                debug_info.append(f"Copying file from {file_path} to {target_path}")
                
            shutil.copy2(file_path, target_path)
            
            result = {
                'success': True,
                'file': file_path,
                'target': target_path,
                'person': extracted_person,
                'year': extracted_year
            }
            
            if self.debug_mode:
                result['debug_info'] = debug_info
                
            return result
            
        except Exception as e:
            error_info = {
                'success': False,
                'file': file_path,
                'error': f'Unexpected error: {str(e)}',
                'error_type': 'unexpected'
            }
            if self.debug_mode:
                error_info['debug_info'] = debug_info
                error_info['error_trace'] = str(e)
            return error_info
            
    def ingest_directory(self, directory: str, pattern: str = "*.json", 
                        overwrite: bool = False, parallel: bool = True,
                        debug: bool = False) -> Dict[str, Any]:
        """Ingest all files in a directory.
        
        Args:
            directory: Directory to ingest
            pattern: File pattern to match
            overwrite: Whether to overwrite existing data
            parallel: Whether to process files in parallel
            debug: Enable debug mode for this operation
            
        Returns:
            Dictionary with counts of successes and failures, and detailed errors
        """
        # Set debug mode for this operation
        original_debug_mode = self.debug_mode
        if debug:
            self.debug_mode = True
            
        debug_info = []
        if self.debug_mode:
            debug_info.append(f"Searching for files in {directory} with pattern {pattern}")
        
        # Find all matching files
        files = glob.glob(os.path.join(directory, pattern))
        
        if self.debug_mode:
            debug_info.append(f"Found {len(files)} matching files")
            
        results = []
        for file_path in files:
            if self.debug_mode:
                debug_info.append(f"Processing {file_path}")
                
            result = self.ingest_file(file_path, overwrite=overwrite)
            results.append(result)
            
            if self.debug_mode and 'debug_info' in result:
                debug_info.extend([f"  {info}" for info in result.get('debug_info', [])])
            
        # Count successes and failures
        success_count = sum(1 for r in results if r.get('success', False))
        failed_count = len(results) - success_count
        
        if self.debug_mode:
            debug_info.append(f"Processing complete: {success_count} succeeded, {failed_count} failed")
        
        # Collect error details
        error_details = []
        for result in results:
            if not result.get('success', False):
                error_details.append({
                    'file': result.get('file', 'Unknown file'),
                    'error': result.get('error', 'Unknown error'),
                    'error_type': result.get('error_type', 'unknown')
                })
        
        # Restore original debug mode
        self.debug_mode = original_debug_mode
        
        result_dict = {
            'success': success_count,
            'failed': failed_count,
            'total': len(results),
            'error_details': error_details
        }
        
        if debug:
            result_dict['debug_info'] = debug_info
            
        return result_dict
        
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