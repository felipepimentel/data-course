"""
People Analytics Pro - Uma plataforma para análise e gestão de desenvolvimento de pessoas.

Este pacote fornece ferramentas para análise de desempenho, feedback estruturado,
progressão de carreira e análise de equipes em um sistema unificado.
"""

__version__ = "2.0.0"

# Configuração básica de logging
import logging
import os
from pathlib import Path

# Configuração de caminhos padrão
DEFAULT_DATA_PATH = os.environ.get(
    "PEOPLEANALYTICS_DATA_PATH", str(Path.home() / ".peopleanalytics" / "data")
)

DEFAULT_OUTPUT_PATH = os.environ.get(
    "PEOPLEANALYTICS_OUTPUT_PATH", str(Path.home() / ".peopleanalytics" / "output")
)

DEFAULT_TEMPLATES_PATH = os.environ.get(
    "PEOPLEANALYTICS_TEMPLATES_PATH",
    str(Path(__file__).parent.parent / "assets" / "templates"),
)

DEFAULT_SCHEMAS_PATH = os.environ.get(
    "PEOPLEANALYTICS_SCHEMAS_PATH",
    str(Path(__file__).parent.parent / "assets" / "schemas"),
)

# Formatadores para logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Exportar componentes principais
from peopleanalytics.analyzer import PerformanceAnalyzer
from peopleanalytics.data_pipeline import DataPipeline
from peopleanalytics.data_processor import DataProcessor
from peopleanalytics.reports_generator import generate_report
from peopleanalytics.talent_development import (
    CareerSimulator,
    DynamicMatrix9Box,
    HolisticDashboard,
    InfluenceNetwork,
    IntegratedFeedbackCycle,
    PerformancePredictor,
)

# Importar submódulos principais
from peopleanalytics.visualization import DataVisualizer, create_visualization

# Disponibilizar classes e funções principais
__all__ = [
    "DataPipeline",
    "create_visualization",
    "generate_report",
    "DynamicMatrix9Box",
    "IntegratedFeedbackCycle",
    "InfluenceNetwork",
    "PerformancePredictor",
    "CareerSimulator",
    "HolisticDashboard",
]
