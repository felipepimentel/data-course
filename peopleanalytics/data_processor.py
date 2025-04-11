"""
Data processor for People Analytics.

This module provides functionality for processing people evaluation data,
focusing on importing and validating resultado.json files.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any

class DataProcessor:
    """Process and validate people evaluation data."""
    
    def __init__(self, data_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None):
        """Initialize the data processor.
        
        Args:
            data_path: Path to the data directory
            output_path: Path to the output directory (defaults to 'output' in current dir)
        """
        self.data_path = Path(data_path).resolve()
        self.output_path = Path(output_path).resolve() if output_path else Path("output").resolve()
        
        # Ensure directories exist
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Set up logging for the data processor."""
        log_path = self.output_path / "logs"
        log_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_path / f"data_processor_{timestamp}.log"
        
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

    def import_directory(self, directory: Union[str, Path], recursive: bool = True) -> Dict[str, Any]:
        """Import all resultado.json files from a directory.
        
        Args:
            directory: Directory to import from
            recursive: Whether to search recursively
            
        Returns:
            Dict with import statistics
        """
        directory = Path(directory)
        
        if not directory.exists() or not directory.is_dir():
            return {"success": False, "error": f"Directory not found: {directory}"}
            
        # Find all resultado.json files
        if recursive:
            files = list(directory.glob("**/resultado.json"))
        else:
            files = list(directory.glob("*/resultado.json"))
            
        if not files:
            self.logger.info(f"No files found in {directory}")
            return {"success": True, "imported": 0, "message": "No files found"}
            
        # Process each file
        results = {
            "success": True,
            "total": len(files),
            "imported": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }
        
        for file_path in files:
            try:
                # Skip empty files
                if file_path.stat().st_size == 0:
                    self.logger.warning(f"Skipping empty file: {file_path}")
                    results["skipped"] += 1
                    continue
                
                # Extract person and year from path
                parts = file_path.parts
                if len(parts) < 3:
                    raise ValueError(f"Invalid file path structure: {file_path}")
                    
                person = parts[-3]
                year = parts[-2]
                
                # Check if perfil.json exists and is not empty
                perfil_path = file_path.parent / "perfil.json"
                if not perfil_path.exists() or perfil_path.stat().st_size == 0:
                    self.logger.warning(f"Skipping {file_path} - perfil.json missing or empty")
                    results["skipped"] += 1
                    continue
                
                # Load and validate the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Validate schema
                if not self._validate_schema(data):
                    raise ValueError(f"Invalid data structure in {file_path}")
                
                # Save the data
                self._save_data(person, year, data)
                results["imported"] += 1
                
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"file": str(file_path), "error": str(e)})
                
        return results

    def _validate_schema(self, data: Dict) -> bool:
        """Validate the data against the required schema.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check basic structure
            if not isinstance(data, dict):
                return False
                
            # Check success fields
            if 'success' not in data or 'status_code' not in data or 'data' not in data:
                return False
                
            # Check data structure
            if not isinstance(data['data'], dict):
                return False
                
            # Check required fields in data
            if 'conceito_ciclo_filho_descricao' not in data['data'] or 'direcionadores' not in data['data']:
                return False
                
            # Validate direcionadores
            for direcionador in data['data']['direcionadores']:
                if not isinstance(direcionador, dict):
                    return False
                    
                # Check required fields in direcionador
                if 'direcionador' not in direcionador or 'pergunta_final' not in direcionador or 'comportamentos' not in direcionador:
                    return False
                    
                # Validate comportamentos
                for comportamento in direcionador['comportamentos']:
                    if not isinstance(comportamento, dict):
                        return False
                        
                    # Check required fields in comportamento
                    if 'comportamento' not in comportamento or 'pergunta_final' not in comportamento or 'avaliacoes_grupo' not in comportamento:
                        return False
                        
                    # Validate avaliacoes_grupo
                    for avaliacao in comportamento['avaliacoes_grupo']:
                        if not isinstance(avaliacao, dict):
                            return False
                            
                        # Check required fields in avaliacao
                        if 'avaliador' not in avaliacao or 'frequencia_colaborador' not in avaliacao or 'frequencia_grupo' not in avaliacao:
                            return False
                            
                        # Check frequencia arrays
                        if not isinstance(avaliacao['frequencia_colaborador'], list) or not isinstance(avaliacao['frequencia_grupo'], list):
                            return False
                            
            return True
            
        except Exception:
            return False

    def _save_data(self, person: str, year: str, data: Dict) -> None:
        """Save evaluation data for a person and year.
        
        Args:
            person: Person name
            year: Year
            data: Evaluation data to save
        """
        # Create directory structure if needed
        person_dir = self.data_path / person / year
        person_dir.mkdir(parents=True, exist_ok=True)
        
        # Save resultado.json
        file_path = person_dir / "resultado.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        self.logger.info(f"Saved data for {person} ({year}) to {file_path}")

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
        
        # Find all resultado.json files
        files = list(self.data_path.glob("**/resultado.json"))
        
        for file_path in files:
            results["total"] += 1
            
            try:
                # Extract person and year from path
                parts = file_path.parts
                person = parts[-3]
                year = parts[-2]
                
                # Load and validate the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if self._validate_schema(data):
                    results["valid"] += 1
                else:
                    results["invalid"] += 1
                    results["issues"].append({
                        "person": person,
                        "year": year,
                        "status": "invalid",
                        "message": "Invalid data structure"
                    })
                    
            except Exception as e:
                results["invalid"] += 1
                results["issues"].append({
                    "person": person,
                    "year": year,
                    "status": "error",
                    "message": str(e)
                })
        
        return results 