"""
People Analytics Platform

Uma plataforma completa para processamento de dados de funcionários,
feedback, avaliações e progressão de carreira, com ferramentas avançadas
de visualização e desenvolvimento de talentos.
"""

__version__ = '1.0.0'

# Importar submódulos principais
from peopleanalytics.data_pipeline import DataPipeline
from peopleanalytics.visualization import create_visualization
from peopleanalytics.reports_generator import generate_report
from peopleanalytics.talent_development import (
    DynamicMatrix9Box,
    IntegratedFeedbackCycle,
    InfluenceNetwork,
    PerformancePredictor,
    CareerSimulator,
    HolisticDashboard
)

# Disponibilizar classes e funções principais
__all__ = [
    'DataPipeline',
    'create_visualization',
    'generate_report',
    'DynamicMatrix9Box',
    'IntegratedFeedbackCycle',
    'InfluenceNetwork',
    'PerformancePredictor',
    'CareerSimulator',
    'HolisticDashboard',
] 