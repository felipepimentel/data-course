"""
People Analytics Pro - Uma plataforma para análise e gestão de desenvolvimento de pessoas.

Este pacote fornece ferramentas para análise de desempenho, feedback estruturado,
progressão de carreira e análise de equipes em um sistema unificado.
"""

__version__ = "3.0.0"

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

# Core components
# CLI components
from peopleanalytics.cli import CLI, SyncCommand, main
from peopleanalytics.data_processor import DataProcessor

# Domain models
from peopleanalytics.domain.evaluation import (
    Evaluation,
    EvaluationFrequency,
    EvaluationScore,
    EvaluationSet,
    EvaluationType,
)
from peopleanalytics.domain.score import (
    CompositeScore,
    Score,
    ScoreCategory,
    ScoreHistory,
    ScoreScale,
)
from peopleanalytics.domain.skill_base import (
    Skill,
    SkillLevel,
    SkillMatrix,
    SkillProficiency,
    SkillType,
    compare_skill_matrices,
    derive_skill_gap,
)
from peopleanalytics.evaluation_analyzer import EvaluationAnalyzer
from peopleanalytics.manager_feedback import ManagerFeedback
from peopleanalytics.reports_generator import generate_report
from peopleanalytics.sync import Sync

# Talent development modules
from peopleanalytics.talent_development import (
    CareerSimulator,
    DynamicMatrix9Box,
    HolisticDashboard,
    InfluenceNetwork,
    IntegratedFeedbackCycle,
    PerformancePredictor,
)

# Disponibilizar classes e funções principais
__all__ = [
    # Core components
    "DataProcessor",
    "EvaluationAnalyzer",
    "generate_report",
    "Sync",
    "ManagerFeedback",
    # CLI components
    "CLI",
    "SyncCommand",
    "main",
    # Domain models
    "Evaluation",
    "EvaluationFrequency",
    "EvaluationScore",
    "EvaluationSet",
    "EvaluationType",
    "Score",
    "ScoreCategory",
    "CompositeScore",
    "ScoreHistory",
    "ScoreScale",
    "Skill",
    "SkillLevel",
    "SkillMatrix",
    "SkillProficiency",
    "SkillType",
    "compare_skill_matrices",
    "derive_skill_gap",
    # Talent development modules
    "DynamicMatrix9Box",
    "IntegratedFeedbackCycle",
    "InfluenceNetwork",
    "PerformancePredictor",
    "CareerSimulator",
    "HolisticDashboard",
]
