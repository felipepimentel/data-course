"""Command-line interface commands for the People Analytics system."""

from .analysis_commands import AnalysisCommand
from .base_command import BaseCommand
from .career_commands import CareerSimCommand
from .doc_commands import DocCommand
from .skills_commands import SkillsAnalysisCommand, SkillsRadarCommand
from .sync_commands import SyncCommand
from .talent_development_commands import (
    NineBoxCommand,
    TalentDevelopmentCommands,
)

__all__ = [
    "AnalysisCommand",
    "BaseCommand",
    "CareerSimCommand",
    "DocCommand",
    "SkillsAnalysisCommand",
    "SkillsRadarCommand",
    "SyncCommand",
    "NineBoxCommand",
    "TalentDevelopmentCommands",
]
