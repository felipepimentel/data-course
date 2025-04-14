"""
CLI Commands for People Analytics.

This package contains all CLI commands for the People Analytics system,
organized by domain areas.
"""

from typing import Dict, Type

from .base_command import BaseCommand

# Import commands by domain
from .data_commands import (
    BackupCommand,
    ExportCommand,
    ImportCommand,
    ListCommand,
    ValidateCommand,
)
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
]
