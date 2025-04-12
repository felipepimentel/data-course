"""
Ciclo de Feedback Integrado ao Desenvolvimento.

Implementa um sistema onde o feedback gera automaticamente:
- Trilhas de Aprendizado Personalizadas: Baseadas em gaps específicos identificados
- Calibragem de Expectativas: Comparando autopercepção com feedback externo
- Mapeamento de Viés Cognitivo: Identificando áreas onde a pessoa tem pontos cegos
- Validação de Progresso Objetivo: Evidências quantificáveis de melhoria
"""

from peopleanalytics.talent_development.feedback_cycle.integrated_cycle import IntegratedFeedbackCycle
from peopleanalytics.talent_development.feedback_cycle.learning_path import PersonalizedLearningPath
from peopleanalytics.talent_development.feedback_cycle.gap_analyzer import FeedbackGapAnalyzer
from peopleanalytics.talent_development.feedback_cycle.bias_detector import CognitiveBiasDetector
from peopleanalytics.talent_development.feedback_cycle.progress_tracker import ProgressTracker

__all__ = [
    'IntegratedFeedbackCycle',
    'PersonalizedLearningPath',
    'FeedbackGapAnalyzer',
    'CognitiveBiasDetector',
    'ProgressTracker',
] 