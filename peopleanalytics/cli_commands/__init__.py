"""
CLI Commands for People Analytics.

This package contains all CLI commands for the People Analytics system,
organized by domain areas.
"""

from typing import Dict, Type

from .base_command import BaseCommand
from .career_commands import CareerSimCommand

# Import commands by domain
from .data_commands import (
    BackupCommand,
    ExportCommand,
    ImportCommand,
    ListCommand,
    ValidateCommand,
)
from .feedback_commands import FeedbackCycleCommand
from .network_commands import InfluenceNetworkCommand
from .people_commands import (
    AddAttendanceCommand,
    AddPaymentCommand,
    CreateSampleCommand,
    UpdateProfileCommand,
)
from .report_commands import (
    PlotCommand,
    ReportCommand,
    SummaryCommand,
)
from .sync_commands import SyncCommand
from .talent_development_commands import NineBoxCommand

# Dictionary mapping command names to their implementations
COMMANDS: Dict[str, Type[BaseCommand]] = {
    # Data commands
    "validate": ValidateCommand,
    "list": ListCommand,
    "import": ImportCommand,
    "export": ExportCommand,
    "backup": BackupCommand,
    # Report commands
    "summary": SummaryCommand,
    "report": ReportCommand,
    "plot": PlotCommand,
    # People commands
    "add-attendance": AddAttendanceCommand,
    "add-payment": AddPaymentCommand,
    "update-profile": UpdateProfileCommand,
    "create-sample": CreateSampleCommand,
    # Talent development commands
    "nine-box": NineBoxCommand,
    # Sync command
    "sync": SyncCommand,
    # Feedback command
    "feedback-cycle": FeedbackCycleCommand,
    # Career simulation command
    "career-sim": CareerSimCommand,
    # Network analysis command
    "influence-network": InfluenceNetworkCommand,
}

__all__ = [
    "BaseCommand",
    "COMMANDS",
    # Data commands
    "ValidateCommand",
    "ListCommand",
    "ImportCommand",
    "ExportCommand",
    "BackupCommand",
    # Report commands
    "SummaryCommand",
    "ReportCommand",
    "PlotCommand",
    # People commands
    "AddAttendanceCommand",
    "AddPaymentCommand",
    "UpdateProfileCommand",
    "CreateSampleCommand",
    # Talent development commands
    "NineBoxCommand",
    # Sync command
    "SyncCommand",
    # Feedback command
    "FeedbackCycleCommand",
    # Career simulation command
    "CareerSimCommand",
    # Network analysis command
    "InfluenceNetworkCommand",
]
