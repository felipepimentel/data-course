"""
Data models for People Analytics.

This module provides the core data structures and validation logic
for person data, attendance records, and payment history.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
import json
import os
from pathlib import Path


class RecordStatus(Enum):
    """Status of a data record."""
    VALID = "valid"
    INCOMPLETE = "incomplete"
    INVALID = "invalid"
    ERROR = "error"


@dataclass
class AttendanceRecord:
    """Single attendance record for a person."""
    date: date
    present: bool
    notes: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttendanceRecord':
        """Create an AttendanceRecord from a dictionary."""
        try:
            # Handle different date formats
            if isinstance(data.get('data'), str):
                record_date = datetime.strptime(data['data'], "%Y-%m-%d").date()
            elif isinstance(data.get('date'), str):
                record_date = datetime.strptime(data['date'], "%Y-%m-%d").date()
            else:
                raise ValueError("No valid date field found")
                
            return cls(
                date=record_date,
                present=bool(data.get('presente', data.get('present', False))),
                notes=data.get('notas', data.get('notes', None))
            )
        except Exception as e:
            raise ValueError(f"Invalid attendance record: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "data": self.date.isoformat(),
            "presente": self.present,
            "notas": self.notes
        }


@dataclass
class PaymentRecord:
    """Single payment record for a person."""
    date: date
    amount: float
    status: str = "paid"
    reference: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PaymentRecord':
        """Create a PaymentRecord from a dictionary."""
        try:
            # Handle different date formats
            if isinstance(data.get('data'), str):
                payment_date = datetime.strptime(data['data'], "%Y-%m-%d").date()
            elif isinstance(data.get('date'), str):
                payment_date = datetime.strptime(data['date'], "%Y-%m-%d").date()
            else:
                raise ValueError("No valid date field found")
                
            return cls(
                date=payment_date,
                amount=float(data.get('valor', data.get('amount', 0))),
                status=data.get('status', "paid"),
                reference=data.get('referencia', data.get('reference', None))
            )
        except Exception as e:
            raise ValueError(f"Invalid payment record: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "data": self.date.isoformat(),
            "valor": self.amount,
            "status": self.status,
            "referencia": self.reference
        }


@dataclass
class PersonData:
    """Person data for a specific year."""
    name: str
    year: int
    attendance_records: List[AttendanceRecord] = field(default_factory=list)
    payment_records: List[PaymentRecord] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersonData':
        """Create a PersonData object from a dictionary."""
        try:
            # Extract name and year
            name = data.get('nome', data.get('name', ''))
            year = int(data.get('ano', data.get('year', 0)))
            
            if not name or not year:
                raise ValueError("Missing required fields: name and year")
                
            # Create the base object
            person_data = cls(name=name, year=year)
            
            # Add attendance records
            attendance_data = data.get('frequencias', data.get('attendance', []))
            for record in attendance_data:
                person_data.attendance_records.append(AttendanceRecord.from_dict(record))
                
            # Add payment records
            payment_data = data.get('pagamentos', data.get('payments', []))
            for record in payment_data:
                person_data.payment_records.append(PaymentRecord.from_dict(record))
                
            # Store any additional metadata
            for key, value in data.items():
                if key not in ['nome', 'name', 'ano', 'year', 'frequencias', 'attendance', 'pagamentos', 'payments']:
                    person_data.metadata[key] = value
                    
            return person_data
        
        except Exception as e:
            raise ValueError(f"Error creating PersonData: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = {
            "nome": self.name,
            "ano": self.year,
            "frequencias": [record.to_dict() for record in self.attendance_records],
            "pagamentos": [record.to_dict() for record in self.payment_records]
        }
        
        # Add metadata
        for key, value in self.metadata.items():
            data[key] = value
            
        return data
    
    def validate(self) -> RecordStatus:
        """Validate the person data."""
        if not self.name or not self.year:
            return RecordStatus.INCOMPLETE
            
        # Basic validation - can be expanded based on requirements
        if self.year < 2000 or self.year > datetime.now().year + 1:
            return RecordStatus.INVALID
            
        return RecordStatus.VALID
    
    def save(self, base_path: Union[str, Path]) -> str:
        """Save the person data to a file."""
        base_path = Path(base_path)
        person_dir = base_path / self.name
        year_dir = person_dir / str(self.year)
        
        # Create directories if they don't exist
        year_dir.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        file_path = year_dir / "data.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
            
        return str(file_path)
    
    @classmethod
    def load(cls, file_path: Union[str, Path]) -> 'PersonData':
        """Load person data from a file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        return cls.from_dict(data)
    
    def add_attendance(self, date_str: str, present: bool, notes: Optional[str] = None) -> None:
        """Add an attendance record."""
        record_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        self.attendance_records.append(AttendanceRecord(date=record_date, present=present, notes=notes))
    
    def add_payment(self, date_str: str, amount: float, status: str = "paid", reference: Optional[str] = None) -> None:
        """Add a payment record."""
        payment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        self.payment_records.append(PaymentRecord(date=payment_date, amount=amount, status=status, reference=reference))
    
    def get_attendance_summary(self) -> Dict[str, Any]:
        """Get a summary of attendance."""
        total = len(self.attendance_records)
        present = sum(1 for record in self.attendance_records if record.present)
        
        return {
            "total": total,
            "present": present,
            "absent": total - present,
            "attendance_rate": (present / total) * 100 if total > 0 else 0
        }
    
    def get_payment_summary(self) -> Dict[str, Any]:
        """Get a summary of payments."""
        total_amount = sum(record.amount for record in self.payment_records)
        return {
            "total_payments": len(self.payment_records),
            "total_amount": total_amount,
            "average_payment": total_amount / len(self.payment_records) if self.payment_records else 0
        }


@dataclass
class PersonSummary:
    """Summary of a person's data across all years."""
    name: str
    years: List[int]
    total_attendance: int = 0
    present_count: int = 0
    total_payments: int = 0
    total_amount: float = 0
    
    @property
    def attendance_rate(self) -> float:
        """Calculate the attendance rate."""
        return (self.present_count / self.total_attendance) * 100 if self.total_attendance > 0 else 0
    
    @property
    def average_payment(self) -> float:
        """Calculate the average payment."""
        return self.total_amount / self.total_payments if self.total_payments > 0 else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "years": self.years,
            "total_attendance": self.total_attendance,
            "present_count": self.present_count,
            "attendance_rate": self.attendance_rate,
            "total_payments": self.total_payments,
            "total_amount": self.total_amount,
            "average_payment": self.average_payment
        } 