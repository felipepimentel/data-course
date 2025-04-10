"""
People Analytics package.

A modern data processing system for analyzing people data, 
including attendance and payment information.
"""

__version__ = "2.0.0"

from .data_model import (
    PersonData,
    AttendanceRecord,
    PaymentRecord,
    PersonSummary,
    RecordStatus
)

from .data_processor import DataProcessor

__all__ = [
    "PersonData",
    "AttendanceRecord",
    "PaymentRecord",
    "PersonSummary",
    "RecordStatus",
    "DataProcessor"
] 