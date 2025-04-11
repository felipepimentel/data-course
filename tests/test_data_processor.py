"""Tests for the data processor module."""

import json
import os
import shutil
from pathlib import Path
import pytest
from peopleanalytics.data_processor import DataProcessor

@pytest.fixture
def test_data_dir(tmp_path):
    """Create a test data directory with sample files."""
    # Create directory structure
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()
    
    # Create sample data
    sample_data = {
        "success": True,
        "status_code": 200,
        "data": {
            "conceito_ciclo_filho_descricao": "Exceeds Expectations",
            "direcionadores": [
                {
                    "direcionador": "Leadership",
                    "pergunta_final": "How well does the person lead?",
                    "comportamentos": [
                        {
                            "comportamento": "Communication",
                            "pergunta_final": "How well does the person communicate?",
                            "avaliacoes_grupo": [
                                {
                                    "avaliador": "Manager",
                                    "frequencia_colaborador": [0, 1, 2, 1, 0, 0],
                                    "frequencia_grupo": [0, 0, 1, 2, 1, 0]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }
    
    sample_perfil = {
        "cargo": "Software Engineer",
        "nivel_cargo": "Senior"
    }
    
    # Create person/year directories
    person_dir = data_dir / "John Doe" / "2023"
    person_dir.mkdir(parents=True)
    
    # Save files
    with open(person_dir / "resultado.json", 'w') as f:
        json.dump(sample_data, f)
        
    with open(person_dir / "perfil.json", 'w') as f:
        json.dump(sample_perfil, f)
    
    return data_dir

@pytest.fixture
def processor(test_data_dir, tmp_path):
    """Create a DataProcessor instance."""
    return DataProcessor(test_data_dir, tmp_path / "output")

def test_import_directory(processor, test_data_dir):
    """Test importing a directory."""
    result = processor.import_directory(test_data_dir)
    
    assert result["success"] is True
    assert result["total"] == 1
    assert result["imported"] == 1
    assert result["failed"] == 0
    assert result["skipped"] == 0
    assert len(result["errors"]) == 0

def test_import_empty_directory(processor, tmp_path):
    """Test importing an empty directory."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    
    result = processor.import_directory(empty_dir)
    
    assert result["success"] is True
    assert result["imported"] == 0
    assert "No files found" in result["message"]

def test_import_invalid_file(processor, test_data_dir):
    """Test importing a directory with an invalid file."""
    # Create an invalid file
    invalid_dir = test_data_dir / "Invalid" / "2023"
    invalid_dir.mkdir(parents=True)
    
    with open(invalid_dir / "resultado.json", 'w') as f:
        f.write("invalid json")

    # Também criar o arquivo perfil.json para evitar que seja pulado
    with open(invalid_dir / "perfil.json", 'w') as f:
        f.write("{}")
    
    result = processor.import_directory(test_data_dir)
    
    assert result["success"] is True
    assert result["total"] == 2
    assert result["imported"] == 1
    assert result["failed"] == 1
    assert len(result["errors"]) == 1

def test_generate_report(processor, test_data_dir):
    """Test generating a report."""
    # First import the data
    processor.import_directory(test_data_dir)
    
    # Generate report
    report_path = processor.generate_report()
    
    assert report_path is not None
    assert os.path.exists(report_path)
    
    # Check report content
    import pandas as pd
    df = pd.read_excel(report_path, sheet_name='Resumo')
    
    assert len(df) == 1
    assert df.iloc[0]['pessoa'] == 'John Doe'
    assert str(df.iloc[0]['ano']) == '2023'  # Convertendo para string para a comparação
    assert df.iloc[0]['cargo'] == 'Software Engineer'
    assert df.iloc[0]['nivel'] == 'Senior'
    assert df.iloc[0]['conceito'] == 'Exceeds Expectations'

def test_generate_report_no_data(processor, tmp_path):
    """Test generating a report with no data."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    
    processor = DataProcessor(empty_dir, tmp_path / "output")
    report_path = processor.generate_report()
    
    assert report_path is None 