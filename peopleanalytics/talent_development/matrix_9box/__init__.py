"""
Matriz de Impacto x Potencial Dinâmica (9-Box).

Visualização dinâmica que evolui ao longo do tempo, mostrando a trajetória 
da pessoa na matriz 9-box (potencial x desempenho).
"""

from peopleanalytics.talent_development.matrix_9box.dynamic_matrix import DynamicMatrix9Box
from peopleanalytics.talent_development.matrix_9box.trajectory import (
    TrajectoryAnalyzer, MovementVector, AccelerationTrigger, FutureProjection
)

__all__ = [
    'DynamicMatrix9Box',
    'TrajectoryAnalyzer',
    'MovementVector',
    'AccelerationTrigger',
    'FutureProjection',
] 