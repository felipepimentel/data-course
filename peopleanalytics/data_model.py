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
class CareerEvent:
    """Single career progression event."""
    date: date
    event_type: str  # promotion, lateral_move, role_change, skill_acquisition, certification
    details: str
    previous_position: Optional[str] = None
    new_position: Optional[str] = None
    impact_score: Optional[int] = None  # 1-5 scale to measure impact
    validated: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CareerEvent':
        """Create a CareerEvent from a dictionary."""
        try:
            if isinstance(data.get('data'), str):
                event_date = datetime.strptime(data['data'], "%Y-%m-%d").date()
            elif isinstance(data.get('date'), str):
                event_date = datetime.strptime(data['date'], "%Y-%m-%d").date()
            else:
                raise ValueError("No valid date field found")
                
            return cls(
                date=event_date,
                event_type=data.get('tipo_evento', data.get('event_type', '')),
                details=data.get('detalhes', data.get('details', '')),
                previous_position=data.get('cargo_anterior', data.get('previous_position')),
                new_position=data.get('cargo_novo', data.get('new_position')),
                impact_score=int(data.get('impacto', data.get('impact_score', 0))) if data.get('impacto') or data.get('impact_score') else None,
                validated=bool(data.get('validado', data.get('validated', False)))
            )
        except Exception as e:
            raise ValueError(f"Invalid career event record: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "data": self.date.isoformat(),
            "tipo_evento": self.event_type,
            "detalhes": self.details,
            "cargo_anterior": self.previous_position,
            "cargo_novo": self.new_position,
            "impacto": self.impact_score,
            "validado": self.validated
        }


@dataclass
class CareerProgressionData:
    """Career progression data for a person."""
    career_events: List[CareerEvent] = field(default_factory=list)
    career_goals: List[Dict[str, Any]] = field(default_factory=list)
    skills_matrix: Dict[str, int] = field(default_factory=dict)  # skill_name -> proficiency (1-5)
    mentorship: List[Dict[str, Any]] = field(default_factory=list)
    certifications: List[Dict[str, Any]] = field(default_factory=list)
    growth_metrics: Dict[str, List[float]] = field(default_factory=dict)  # metric_name -> [values over time]
    
    def add_career_event(self, event: CareerEvent) -> None:
        """Add a career event."""
        self.career_events.append(event)
        # Sort events by date
        self.career_events.sort(key=lambda x: x.date)
    
    def add_skill(self, skill_name: str, proficiency: int) -> None:
        """Add or update a skill."""
        if proficiency < 1 or proficiency > 5:
            raise ValueError("Proficiency must be between 1 and 5")
        self.skills_matrix[skill_name] = proficiency
    
    def add_career_goal(self, title: str, target_date: date, details: str, 
                         progress: int = 0, status: str = "not_started") -> None:
        """Add a career goal."""
        self.career_goals.append({
            "title": title,
            "target_date": target_date.isoformat(),
            "details": details,
            "progress": progress,  # 0-100%
            "status": status  # not_started, in_progress, completed, delayed
        })
    
    def add_certification(self, name: str, issuer: str, date_obtained: date, 
                          expiry_date: Optional[date] = None, url: Optional[str] = None) -> None:
        """Add a certification."""
        self.certifications.append({
            "name": name,
            "issuer": issuer,
            "date_obtained": date_obtained.isoformat(),
            "expiry_date": expiry_date.isoformat() if expiry_date else None,
            "url": url
        })
    
    def add_mentor_relationship(self, mentor_name: str, start_date: date, 
                               focus_areas: List[str], end_date: Optional[date] = None) -> None:
        """Add a mentorship relationship."""
        self.mentorship.append({
            "mentor_name": mentor_name,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat() if end_date else None,
            "focus_areas": focus_areas,
            "active": end_date is None
        })
    
    def add_growth_metric(self, metric_name: str, value: float, date: Optional[date] = None) -> None:
        """Add a growth metric value."""
        if metric_name not in self.growth_metrics:
            self.growth_metrics[metric_name] = []
        self.growth_metrics[metric_name].append(value)
    
    def get_promotion_velocity(self) -> Optional[float]:
        """Calculate promotion velocity (years between promotions)."""
        promotion_events = [e for e in self.career_events if e.event_type == 'promotion']
        if len(promotion_events) < 2:
            return None
        
        # Sort by date
        promotion_events.sort(key=lambda x: x.date)
        
        # Calculate average time between promotions
        time_diffs = []
        for i in range(1, len(promotion_events)):
            days_diff = (promotion_events[i].date - promotion_events[i-1].date).days
            years_diff = days_diff / 365.25
            time_diffs.append(years_diff)
        
        return sum(time_diffs) / len(time_diffs)
    
    def get_skill_growth_rate(self) -> Optional[float]:
        """Calculate skill growth rate from career events and skills matrix."""
        skill_events = [e for e in self.career_events if e.event_type == 'skill_acquisition']
        if not skill_events:
            return None
        
        earliest_event = min(skill_events, key=lambda x: x.date)
        latest_event = max(skill_events, key=lambda x: x.date)
        
        days_diff = (latest_event.date - earliest_event.date).days
        if days_diff == 0:
            return None
        
        skills_per_year = (len(skill_events) / days_diff) * 365.25
        return skills_per_year
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CareerProgressionData':
        """Create a CareerProgressionData from a dictionary."""
        career_data = cls()
        
        # Load career events
        for event_data in data.get('eventos_carreira', data.get('career_events', [])):
            try:
                event = CareerEvent.from_dict(event_data)
                career_data.career_events.append(event)
            except Exception as e:
                print(f"Error loading career event: {e}")
        
        # Load skills matrix
        career_data.skills_matrix = data.get('matriz_habilidades', data.get('skills_matrix', {}))
        
        # Load career goals
        career_data.career_goals = data.get('metas_carreira', data.get('career_goals', []))
        
        # Load certifications
        career_data.certifications = data.get('certificacoes', data.get('certifications', []))
        
        # Load mentorship
        career_data.mentorship = data.get('mentoria', data.get('mentorship', []))
        
        # Load growth metrics
        career_data.growth_metrics = data.get('metricas_crescimento', data.get('growth_metrics', {}))
        
        return career_data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "eventos_carreira": [event.to_dict() for event in self.career_events],
            "matriz_habilidades": self.skills_matrix,
            "metas_carreira": self.career_goals,
            "certificacoes": self.certifications,
            "mentoria": self.mentorship,
            "metricas_crescimento": self.growth_metrics
        }


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
    nome_completo: str
    funcional: str = ""
    funcional_gestor: Optional[str] = None
    nome_gestor: Optional[str] = None
    cargo: str = ""
    codigo_cargo: str = ""
    nivel_cargo: str = ""
    nome_nivel_cargo: str = ""
    nome_departamento: str = ""
    tipo_carreira: Optional[str] = None
    codigo_comunidade: Optional[str] = None
    nome_comunidade: Optional[str] = None
    codigo_squad: Optional[str] = None
    nome_squad: Optional[str] = None
    codigo_papel: Optional[str] = None
    nome_papel: Optional[str] = None
    tipo_gestao: bool = False
    is_congelamento: bool = False
    data_congelamento: Optional[date] = None

    @property
    def full_name(self) -> str:
        """Return the full name of the person."""
        return self.nome_completo
    
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
                nome_completo=data.get('nome_completo', ''),
                funcional=data.get('funcional', ''),
                funcional_gestor=data.get('funcional_gestor'),
                nome_gestor=data.get('nome_gestor'),
                cargo=data.get('cargo', ''),
                codigo_cargo=data.get('codigo_cargo', ''),
                nivel_cargo=data.get('nivel_cargo', ''),
                nome_nivel_cargo=data.get('nome_nivel_cargo', ''),
                nome_departamento=data.get('nome_departamento', ''),
                tipo_carreira=data.get('tipo_carreira'),
                codigo_comunidade=data.get('codigo_comunidade'),
                nome_comunidade=data.get('nome_comunidade'),
                codigo_squad=data.get('codigo_squad'),
                nome_squad=data.get('nome_squad'),
                codigo_papel=data.get('codigo_papel'),
                nome_papel=data.get('nome_papel'),
                tipo_gestao=bool(data.get('tipo_gestao', False)),
                is_congelamento=bool(data.get('is_congelamento', False)),
                data_congelamento=freeze_date
            )
            
            return profile
            
        except Exception as e:
            raise ValueError(f"Error creating ProfileData: {e}")
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = {
            "nome_completo": self.nome_completo,
            "funcional": self.funcional,
            "funcional_gestor": self.funcional_gestor,
            "nome_gestor": self.nome_gestor,
            "cargo": self.cargo,
            "codigo_cargo": self.codigo_cargo,
            "nivel_cargo": self.nivel_cargo,
            "nome_nivel_cargo": self.nome_nivel_cargo,
            "nome_departamento": self.nome_departamento,
            "tipo_carreira": self.tipo_carreira,
            "codigo_comunidade": self.codigo_comunidade,
            "nome_comunidade": self.nome_comunidade,
            "codigo_squad": self.codigo_squad,
            "nome_squad": self.nome_squad,
            "codigo_papel": self.codigo_papel,
            "nome_papel": self.nome_papel,
            "tipo_gestao": self.tipo_gestao,
            "is_congelamento": self.is_congelamento,
            "data_congelamento": self.data_congelamento.isoformat() if self.data_congelamento else None
        }
            
        return data


@dataclass
class PersonData:
    """Person data for a specific year."""
    name: str
    year: int
    attendance_records: List[AttendanceRecord] = field(default_factory=list)
    payment_records: List[PaymentRecord] = field(default_factory=list)
    profile: Optional[ProfileData] = None
    evaluation_data: Optional[Dict[str, Any]] = None
    career_progression: Optional[CareerProgressionData] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], profile_data: Optional[Dict[str, Any]] = None) -> 'PersonData':
        """Create a PersonData instance from a dictionary.
        
        Args:
            data: Dictionary containing person data
            profile_data: Optional dictionary containing profile data
            
        Returns:
            PersonData instance
        """
        # Get year from data
        year = int(data.get('ano', 0))
        
        # Get name from data or use empty string
        name = data.get('nome', '')
        
        # Create instance with name and year
        person_data = cls(name=name, year=year)
        
        # Handle profile data if provided
        if profile_data:
            person_data.profile = ProfileData.from_dict(profile_data)
            # Update name from profile if available
            if person_data.profile.nome_completo:
                person_data.name = person_data.profile.nome_completo
        
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
        
        # Handle evaluation data
        if 'avaliacao' in data:
            person_data.evaluation_data = data['avaliacao']
            
        # Handle career progression data
        if 'progressao_carreira' in data:
            person_data.career_progression = CareerProgressionData.from_dict(data['progressao_carreira'])
        
        return person_data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the PersonData to a dictionary.
        
        Returns:
            Dictionary representation of the PersonData
        """
        # Only support Portuguese field names format
        result = {
            'ano': self.year
        }
        
        # Convert attendance records
        if self.attendance_records:
            result['frequencias'] = []
            for record in self.attendance_records:
                record_dict = record.to_dict()
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
                result['pagamentos'].append({
                    'data': record_dict.get('data', ''),
                    'valor': record_dict.get('valor', 0),
                    'descricao': record_dict.get('descricao', '')
                })
        
        # Add evaluation data if available
        if self.evaluation_data:
            result['avaliacao'] = self.evaluation_data
            
        # Add career progression data if available
        if self.career_progression:
            result['progressao_carreira'] = self.career_progression.to_dict()
        
        return result
    
    def get_profile_dict(self) -> Optional[Dict[str, Any]]:
        """Get profile as dictionary for serialization."""
        if self.profile:
            return self.profile.to_dict()
        return None
    
    def validate(self) -> RecordStatus:
        """Validate the person data.
        
        Returns:
            RecordStatus indicating validation result
        """
        try:
            # Check required fields
            if not self.name:
                return RecordStatus.INVALID
                
            if not self.year:
                return RecordStatus.INVALID
                
            # Validate profile if exists
            if self.profile:
                if not self.profile.nome_completo:
                    return RecordStatus.INCOMPLETE
                    
            # Validate attendance records
            for record in self.attendance_records:
                if not record.date:
                    return RecordStatus.INVALID
                    
            # Validate payment records
            for record in self.payment_records:
                if not record.date or record.amount <= 0:
                    return RecordStatus.INVALID
                    
            return RecordStatus.VALID
            
        except Exception:
            return RecordStatus.ERROR
    
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
            "total_days": total,
            "present_days": present,
            "absent_days": total - present,
            "attendance_rate": (present / total) * 100 if total > 0 else 0
        }
    
    def get_payment_summary(self) -> Dict[str, Any]:
        """Get a summary of payments."""
        if not self.payment_records:
            return {
                "total_payments": 0,
                "total_amount": 0,
                "average_amount": 0,
                "min_amount": 0,
                "max_amount": 0
            }
            
        amounts = [record.amount for record in self.payment_records]
        total_amount = sum(amounts)
        
        return {
            "total_payments": len(self.payment_records),
            "total_amount": total_amount,
            "average_amount": total_amount / len(self.payment_records),
            "min_amount": min(amounts),
            "max_amount": max(amounts)
        }
    
    def get_profile_summary(self) -> Dict[str, Any]:
        """Get a summary of the profile information."""
        if not self.profile:
            return {"available": False}
            
        return {
            "available": True,
            "full_name": self.profile.nome_completo,
            "position": self.profile.cargo,
            "department": self.profile.nome_departamento,
            "manager": self.profile.nome_gestor or "N/A",
            "is_manager": self.profile.tipo_gestao
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

    # Funções relacionadas à progressão de carreira
    def init_career_progression(self) -> None:
        """Initialize career progression data if not already initialized."""
        if not self.career_progression:
            self.career_progression = CareerProgressionData()
    
    def add_career_event(self, date_str: str, event_type: str, details: str, 
                        prev_position: Optional[str] = None, new_position: Optional[str] = None,
                        impact_score: Optional[int] = None) -> None:
        """Add a career event."""
        self.init_career_progression()
        event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        event = CareerEvent(
            date=event_date,
            event_type=event_type,
            details=details,
            previous_position=prev_position,
            new_position=new_position,
            impact_score=impact_score
        )
        self.career_progression.add_career_event(event)
        
    def add_skill(self, skill_name: str, proficiency: int) -> None:
        """Add or update a skill in the skills matrix."""
        self.init_career_progression()
        self.career_progression.add_skill(skill_name, proficiency)
        
    def add_career_goal(self, title: str, target_date_str: str, details: str, 
                       progress: int = 0, status: str = "not_started") -> None:
        """Add a career goal."""
        self.init_career_progression()
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        self.career_progression.add_career_goal(title, target_date, details, progress, status)
        
    def add_certification(self, name: str, issuer: str, date_obtained_str: str, 
                         expiry_date_str: Optional[str] = None, url: Optional[str] = None) -> None:
        """Add a certification."""
        self.init_career_progression()
        date_obtained = datetime.strptime(date_obtained_str, "%Y-%m-%d").date()
        expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date() if expiry_date_str else None
        self.career_progression.add_certification(name, issuer, date_obtained, expiry_date, url)
    
    def get_career_summary(self) -> Dict[str, Any]:
        """Get a summary of career progression."""
        if not self.career_progression:
            return {"available": False}
            
        # Get promotion velocity
        promotion_velocity = self.career_progression.get_promotion_velocity()
        
        # Get skill stats
        total_skills = len(self.career_progression.skills_matrix)
        avg_skill_level = sum(self.career_progression.skills_matrix.values()) / total_skills if total_skills > 0 else 0
        
        # Get certification count
        cert_count = len(self.career_progression.certifications)
        
        # Calculate growth score (combination of various metrics)
        growth_score = 0
        if promotion_velocity is not None:
            # Lower promotion velocity (faster promotions) gives higher score
            growth_score += min(5, 5 / promotion_velocity) if promotion_velocity > 0 else 0
        
        growth_score += min(5, avg_skill_level)
        growth_score += min(5, cert_count / 2)  # 2 certs = 1 point, max 5 points
        
        growth_score = min(10, growth_score / 3 * 10)  # Scale to 0-10
        
        return {
            "available": True,
            "total_events": len(self.career_progression.career_events),
            "promotion_count": len([e for e in self.career_progression.career_events if e.event_type == 'promotion']),
            "promotion_velocity": promotion_velocity,
            "total_skills": total_skills,
            "average_skill_level": avg_skill_level,
            "certification_count": cert_count,
            "active_mentorships": len([m for m in self.career_progression.mentorship if m.get('active', False)]),
            "growth_score": growth_score
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
    nome_departamento: Optional[str] = None
    cargo: Optional[str] = None
    nome_gestor: Optional[str] = None
    
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
        if self.nome_departamento:
            data["nome_departamento"] = self.nome_departamento
        if self.cargo:
            data["cargo"] = self.cargo
        if self.nome_gestor:
            data["nome_gestor"] = self.nome_gestor
            
        return data 