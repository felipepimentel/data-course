"""
Data models for People Analytics.

This module provides the core data structures and validation logic
for person data, attendance records, payment history, and profile information.
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
            "status": "presente" if self.present else "ausente",
            "justificativa": self.notes or ""
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
            "descricao": self.reference or ""
        }


@dataclass
class ProfileData:
    """Profile information for a person."""
    full_name: str
    employee_id: str = ""
    position: str = ""
    position_code: str = ""
    position_level: str = ""
    position_level_name: str = ""
    department: str = ""
    manager_id: Optional[str] = None
    manager_name: Optional[str] = None
    career_type: Optional[str] = None
    community_code: Optional[str] = None
    community_name: Optional[str] = None
    squad_code: Optional[str] = None
    squad_name: Optional[str] = None
    role_code: Optional[str] = None
    role_name: Optional[str] = None
    is_manager: bool = False
    is_frozen: bool = False
    freeze_date: Optional[date] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProfileData':
        """Create a ProfileData object from a dictionary."""
        try:
            # Extract freeze date if present
            freeze_date = None
            if data.get('data_congelamento'):
                try:
                    freeze_date = datetime.strptime(data['data_congelamento'], "%Y-%m-%d").date()
                except:
                    pass
                    
            # Create the profile object
            profile = cls(
                full_name=data.get('nome_completo', ''),
                employee_id=data.get('funcional', ''),
                position=data.get('cargo', ''),
                position_code=data.get('codigo_cargo', ''),
                position_level=data.get('nivel_cargo', ''),
                position_level_name=data.get('nome_nivel_cargo', ''),
                department=data.get('nome_departamento', ''),
                manager_id=data.get('funcional_gestor'),
                manager_name=data.get('nome_gestor'),
                career_type=data.get('tipo_carreira'),
                community_code=data.get('codigo_comunidade'),
                community_name=data.get('nome_comunidade'),
                squad_code=data.get('codigo_squad'),
                squad_name=data.get('nome_squad'),
                role_code=data.get('codigo_papel'),
                role_name=data.get('nome_papel'),
                is_manager=bool(data.get('tipo_gestao', False)),
                is_frozen=bool(data.get('is_congelamento', False)),
                freeze_date=freeze_date
            )
            
            # Store any additional metadata
            for key, value in data.items():
                if key not in [
                    'nome_completo', 'funcional', 'funcional_gestor', 'nome_gestor',
                    'cargo', 'codigo_cargo', 'nivel_cargo', 'nome_nivel_cargo',
                    'nome_departamento', 'tipo_carreira', 'codigo_comunidade',
                    'nome_comunidade', 'codigo_squad', 'nome_squad', 'codigo_papel',
                    'nome_papel', 'tipo_gestao', 'is_congelamento', 'data_congelamento'
                ]:
                    profile.metadata[key] = value
            
            return profile
            
        except Exception as e:
            raise ValueError(f"Error creating ProfileData: {e}")
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = {
            "nome_completo": self.full_name,
            "funcional": self.employee_id,
            "cargo": self.position,
            "codigo_cargo": self.position_code,
            "nivel_cargo": self.position_level,
            "nome_nivel_cargo": self.position_level_name,
            "nome_departamento": self.department,
            "tipo_gestao": self.is_manager,
            "is_congelamento": self.is_frozen
        }
        
        # Add optional fields if they exist
        if self.manager_id:
            data["funcional_gestor"] = self.manager_id
        if self.manager_name:
            data["nome_gestor"] = self.manager_name
        if self.career_type:
            data["tipo_carreira"] = self.career_type
        if self.community_code:
            data["codigo_comunidade"] = self.community_code
        if self.community_name:
            data["nome_comunidade"] = self.community_name
        if self.squad_code:
            data["codigo_squad"] = self.squad_code
        if self.squad_name:
            data["nome_squad"] = self.squad_name
        if self.role_code:
            data["codigo_papel"] = self.role_code
        if self.role_name:
            data["nome_papel"] = self.role_name
        if self.freeze_date:
            data["data_congelamento"] = self.freeze_date.isoformat()
        else:
            data["data_congelamento"] = None
            
        # Add metadata
        for key, value in self.metadata.items():
            data[key] = value
            
        return data


@dataclass
class PersonData:
    """Person data for a specific year."""
    name: str
    year: int
    attendance_records: List[AttendanceRecord] = field(default_factory=list)
    payment_records: List[PaymentRecord] = field(default_factory=list)
    profile: Optional[ProfileData] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], profile_data: Optional[Dict[str, Any]] = None) -> 'PersonData':
        """Create a PersonData instance from a dictionary.
        
        Args:
            data: Dictionary containing person data
            profile_data: Optional dictionary containing profile data
            
        Returns:
            PersonData instance
        """
        # Handle only the Portuguese format (no backward compatibility)
        name = data.get('nome', '')
        year = int(data.get('ano', 0))
        
        # Create instance
        person_data = cls(name=name, year=year)
        
        # Handle profile data if provided
        if profile_data:
            # Use full_name from profile data or person name as fallback
            full_name = profile_data.get('nome_completo', name)
            
            # Create ProfileData with required fields
            profile = ProfileData(
                full_name=full_name,
                employee_id=profile_data.get('funcional', ''),
                position=profile_data.get('cargo', ''),
                position_code=profile_data.get('codigo_cargo', ''),
                position_level=profile_data.get('nivel_cargo', ''),
                position_level_name=profile_data.get('nome_nivel_cargo', ''),
                department=profile_data.get('departamento', profile_data.get('nome_departamento', ''))
            )
            
            # Set optional fields if present
            if 'gestor' in profile_data:
                profile.manager_name = profile_data['gestor']
            if 'email' in profile_data:
                profile.metadata['email'] = profile_data['email']
            if 'data_admissao' in profile_data:
                profile.metadata['hire_date'] = profile_data['data_admissao']
            if 'tipo_gestao' in profile_data:
                profile.is_manager = bool(profile_data['tipo_gestao'])
            
            person_data.profile = profile
        
        # Handle attendance records
        if 'frequencias' in data and isinstance(data['frequencias'], list):
            for attendance_dict in data['frequencias']:
                # Convert data and status to present
                date_str = attendance_dict.get('data', '')
                status = attendance_dict.get('status', '').lower()
                present = status == 'presente'
                notes = attendance_dict.get('justificativa', '')
                
                if date_str:
                    try:
                        person_data.add_attendance(date_str, present, notes)
                    except Exception as e:
                        print(f"Error adding attendance record: {e}")
        
        # Handle payment records
        if 'pagamentos' in data and isinstance(data['pagamentos'], list):
            for payment_dict in data['pagamentos']:
                # Extract payment details
                date_str = payment_dict.get('data', '')
                amount = payment_dict.get('valor', 0)
                description = payment_dict.get('descricao', '')
                
                if date_str:
                    try:
                        person_data.add_payment(date_str, amount, 'paid', description)
                    except Exception as e:
                        print(f"Error adding payment record: {e}")
            
        return person_data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the PersonData to a dictionary.
        
        Returns:
            Dictionary representation of the PersonData
        """
        # Only support Portuguese field names format now
        result = {
            'nome': self.name,
            'ano': self.year
        }
        
        # Convert attendance records
        if self.attendance_records:
            result['frequencias'] = []
            for record in self.attendance_records:
                record_dict = record.to_dict()
                # Convert to Portuguese field names
                result['frequencias'].append({
                    'data': record_dict.get('data', ''),
                    'status': record_dict.get('status', ''),
                    'justificativa': record_dict.get('justificativa', '')
                })
        
        # Convert payment records
        if self.payment_records:
            result['pagamentos'] = []
            for record in self.payment_records:
                record_dict = record.to_dict()
                # Convert to Portuguese field names
                result['pagamentos'].append({
                    'data': record_dict.get('data', ''),
                    'valor': record_dict.get('valor', 0),
                    'descricao': record_dict.get('descricao', '')
                })
            
        return result
    
    def get_profile_dict(self) -> Optional[Dict[str, Any]]:
        """Get profile as dictionary for serialization."""
        if self.profile:
            return self.profile.to_dict()
        return None
    
    def validate(self) -> RecordStatus:
        """Validate the person data."""
        if not self.name or not self.year:
            return RecordStatus.INCOMPLETE
            
        # Basic validation - can be expanded based on requirements
        if self.year < 2000 or self.year > datetime.now().year + 1:
            return RecordStatus.INVALID
            
        return RecordStatus.VALID
    
    def save_to_file(self, directory: str) -> None:
        """Save person data to file in the new format.
        
        Args:
            directory: Directory to save the data to
        """
        os.makedirs(directory, exist_ok=True)
        
        # Save profile data if available
        if self.profile:
            profile_file = os.path.join(directory, "perfil.json")
            with open(profile_file, "w", encoding="utf-8") as f:
                json.dump(self.profile.to_dict(), f, ensure_ascii=False, indent=2)
        
        # Save attendance and payment data
        results_file = os.path.join(directory, "resultado.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, file_path: Union[str, Path]) -> 'PersonData':
        """Load person data from a file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Get potential profile file
        dir_path = file_path.parent
        profile_path = dir_path / "perfil.json"
        
        # Load data file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Load profile if it exists
        profile_data = None
        if profile_path.exists():
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
            except:
                pass
                
        return cls.from_dict(data, profile_data)
    
    def add_attendance(self, date_str: str, present: bool, notes: Optional[str] = None) -> None:
        """Add an attendance record."""
        record_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        self.attendance_records.append(AttendanceRecord(date=record_date, present=present, notes=notes))
    
    def add_payment(self, date_str: str, amount: float, status: str = "paid", reference: Optional[str] = None) -> None:
        """Add a payment record."""
        payment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        self.payment_records.append(PaymentRecord(date=payment_date, amount=amount, status=status, reference=reference))
    
    def add_attendance_record(self, record: AttendanceRecord) -> None:
        """Add an attendance record object."""
        self.attendance_records.append(record)
    
    def add_payment_record(self, record: PaymentRecord) -> None:
        """Add a payment record object."""
        self.payment_records.append(record)
    
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
    
    def get_profile_summary(self) -> Dict[str, Any]:
        """Get a summary of the profile information."""
        if not self.profile:
            return {"available": False}
            
        return {
            "available": True,
            "full_name": self.profile.full_name,
            "position": self.profile.position,
            "department": self.profile.department,
            "manager": self.profile.manager_name or "N/A",
            "is_manager": self.profile.is_manager
        }

    @classmethod
    def load_from_file(cls, directory: str) -> 'PersonData':
        """Load person data from files.
        
        Args:
            directory: Directory containing the data files
            
        Returns:
            PersonData object with the loaded data
        """
        results_file = os.path.join(directory, "resultado.json")
        profile_file = os.path.join(directory, "perfil.json")
        
        if not os.path.exists(results_file):
            raise FileNotFoundError(f"Required file not found: {results_file}")
        
        # Load results data
        with open(results_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Create person data from Portuguese format
        person_data = cls.from_dict_pt(data)
        
        # Load profile if it exists
        if os.path.exists(profile_file):
            with open(profile_file, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
            person_data.profile = ProfileData.from_dict(profile_data)
            
        return person_data
    
    @classmethod
    def from_dict_pt(cls, data: Dict) -> 'PersonData':
        """Create a PersonData object from a dictionary with Portuguese field names.
        
        Args:
            data: Dictionary with Portuguese field names
            
        Returns:
            PersonData object
        """
        # Extract basic person data
        name = data.get("nome", "")
        year = data.get("ano", 0)
        
        person_data = cls(name=name, year=year)
        
        # Load attendance records
        for record_data in data.get("frequencias", []):
            try:
                date_str = record_data.get("data", "")
                if date_str:
                    record_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    status = record_data.get("status", "")
                    present = status.lower() == "presente"
                    notes = record_data.get("justificativa", "")
                    
                    person_data.attendance_records.append(
                        AttendanceRecord(date=record_date, present=present, notes=notes)
                    )
            except Exception as e:
                print(f"Error parsing attendance record: {e}")
            
        # Load payment records
        for record_data in data.get("pagamentos", []):
            try:
                date_str = record_data.get("data", "")
                if date_str:
                    payment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    amount = float(record_data.get("valor", 0))
                    reference = record_data.get("descricao", "")
                    
                    person_data.payment_records.append(
                        PaymentRecord(date=payment_date, amount=amount, reference=reference)
                    )
            except Exception as e:
                print(f"Error parsing payment record: {e}")
            
        return person_data


@dataclass
class PersonSummary:
    """Summary of a person's data across all years."""
    name: str
    years: List[int]
    total_attendance: int = 0
    present_count: int = 0
    total_payments: int = 0
    total_amount: float = 0
    department: Optional[str] = None
    position: Optional[str] = None
    manager: Optional[str] = None
    
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
        data = {
            "name": self.name,
            "years": self.years,
            "total_attendance": self.total_attendance,
            "present_count": self.present_count,
            "attendance_rate": self.attendance_rate,
            "total_payments": self.total_payments,
            "total_amount": self.total_amount,
            "average_payment": self.average_payment
        }
        
        # Add profile-related fields if available
        if self.department:
            data["department"] = self.department
        if self.position:
            data["position"] = self.position
        if self.manager:
            data["manager"] = self.manager
            
        return data 