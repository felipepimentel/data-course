"""
Módulos de domínio do People Analytics.

Contém as estruturas centrais dos conceitos de negócio.
"""

# Import principais classes do módulo skill_base para facilitar o acesso
# Import principais classes do módulo evaluation
from peopleanalytics.domain.evaluation import (
    Evaluation,
    EvaluationFrequency,
    EvaluationScore,
    EvaluationSet,
    EvaluationType,
)

# Import principais classes do módulo score
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
