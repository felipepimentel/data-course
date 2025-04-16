"""
Módulo central para manipulação de habilidades (skills).

Este módulo contém as estruturas centrais para lidar com habilidades técnicas e comportamentais,
incluindo classificação, níveis, análise de conjuntos de habilidades e proficiência.
"""

import logging
import re
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union


class SkillType(Enum):
    """Tipos de habilidades."""

    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    LEADERSHIP = "leadership"
    BUSINESS = "business"
    FUNCTIONAL = "functional"
    COGNITIVE = "cognitive"
    SOCIAL = "social"
    DOMAIN = "domain"
    PROCESS = "process"
    UNKNOWN = "unknown"

    @classmethod
    def from_string(cls, value: str) -> "SkillType":
        """
        Converte uma string para o tipo de habilidade correspondente.

        Args:
            value: String representando o tipo

        Returns:
            Tipo de habilidade
        """
        value = value.lower()

        # Mapeamento expandido para melhor cobertura
        mappings = {
            "tech": cls.TECHNICAL,
            "técn": cls.TECHNICAL,
            "tecn": cls.TECHNICAL,
            "behav": cls.BEHAVIORAL,
            "comport": cls.BEHAVIORAL,
            "soft": cls.BEHAVIORAL,
            "lead": cls.LEADERSHIP,
            "lider": cls.LEADERSHIP,
            "bus": cls.BUSINESS,
            "negóc": cls.BUSINESS,
            "negoc": cls.BUSINESS,
            "func": cls.FUNCTIONAL,
            "funcional": cls.FUNCTIONAL,
            "cog": cls.COGNITIVE,
            "cognit": cls.COGNITIVE,
            "soc": cls.SOCIAL,
            "interpes": cls.SOCIAL,
            "dom": cls.DOMAIN,
            "domínio": cls.DOMAIN,
            "proc": cls.PROCESS,
            "processo": cls.PROCESS,
        }

        # Procura correspondência no início da string
        for prefix, skill_type in mappings.items():
            if value.startswith(prefix):
                return skill_type

        return cls.UNKNOWN


class SkillLevel(Enum):
    """Níveis de proficiência em habilidades."""

    NOVICE = 1  # Iniciante
    BEGINNER = 2  # Básico
    INTERMEDIATE = 3  # Intermediário
    ADVANCED = 4  # Avançado
    EXPERT = 5  # Especialista

    @classmethod
    def get_description(cls, level: int) -> str:
        """
        Obtém a descrição textual de um nível de habilidade.

        Args:
            level: Nível de habilidade (1-5)

        Returns:
            Descrição do nível
        """
        descriptions = {
            1: "Iniciante/Novato",
            2: "Básico",
            3: "Intermediário",
            4: "Avançado",
            5: "Especialista",
        }

        return descriptions.get(level, "Nível desconhecido")

    @classmethod
    def from_value(cls, value: Union[int, float, str]) -> "SkillLevel":
        """
        Converte um valor numérico ou string para nível de proficiência.

        Args:
            value: Valor numérico (1-5) ou string descritiva

        Returns:
            Nível de proficiência correspondente
        """
        if isinstance(value, str):
            value = value.lower()
            if value in ("novice", "iniciante", "novato"):
                return cls.NOVICE
            elif value in ("beginner", "básico", "basico"):
                return cls.BEGINNER
            elif value in (
                "intermediate",
                "intermediário",
                "intermediario",
                "médio",
                "medio",
            ):
                return cls.INTERMEDIATE
            elif value in ("advanced", "avançado", "avancado"):
                return cls.ADVANCED
            elif value in ("expert", "especialista", "master"):
                return cls.EXPERT

            # Tenta extrair um número da string
            match = re.search(r"(\d+)", value)
            if match:
                try:
                    num_value = int(match.group(1))
                    return cls.from_value(num_value)
                except (ValueError, IndexError):
                    pass

            # Se não conseguir determinar, retorna nível intermediário como padrão
            logging.warning(
                f"Nível de proficiência desconhecido: {value}. Usando intermediário como padrão."
            )
            return cls.INTERMEDIATE

        # Lida com valores numéricos
        try:
            num_value = float(value)
            # Mapeia o valor para o nível mais próximo
            if num_value <= 1.5:
                return cls.NOVICE
            elif num_value <= 2.5:
                return cls.BEGINNER
            elif num_value <= 3.5:
                return cls.INTERMEDIATE
            elif num_value <= 4.5:
                return cls.ADVANCED
            else:
                return cls.EXPERT
        except (ValueError, TypeError):
            logging.warning(
                f"Valor de proficiência inválido: {value}. Usando intermediário como padrão."
            )
            return cls.INTERMEDIATE

    def to_scale(self, max_value: float = 10) -> float:
        """
        Converte o nível de proficiência para uma escala personalizada.

        Args:
            max_value: Valor máximo da escala desejada

        Returns:
            Valor na escala especificada
        """
        # Converte de escala 1-5 para a escala desejada
        return (self.value / 5) * max_value


class Skill:
    """
    Modela uma habilidade com seus atributos e nível de proficiência.

    Esta classe representa uma habilidade individual com seu nível de proficiência,
    categoria, e dados relacionados.
    """

    def __init__(
        self,
        name: str,
        level: int = 1,
        skill_type: Optional[SkillType] = None,
        category: Optional[str] = None,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Inicializa uma habilidade.

        Args:
            name: Nome da habilidade
            level: Nível de proficiência (1-5)
            skill_type: Tipo de habilidade
            category: Categoria específica ou subcategoria
            description: Descrição da habilidade
            metadata: Metadados adicionais
        """
        self.name = name
        self._level = max(1, min(5, level))  # Normaliza para 1-5
        self.skill_type = skill_type or self._infer_type()
        self.category = category
        self.description = description
        self.metadata = metadata or {}

        # Relacionamentos com outras habilidades
        self.prerequisites: Set[str] = set()
        self.related_skills: Set[str] = set()
        self.parent_skills: Set[str] = set()
        self.child_skills: Set[str] = set()

    @property
    def level(self) -> int:
        """Nível de proficiência (1-5)."""
        return self._level

    @level.setter
    def level(self, value: int) -> None:
        """Define o nível de proficiência, normalizando para 1-5."""
        self._level = max(1, min(5, value))

    @property
    def level_description(self) -> str:
        """Descrição textual do nível de proficiência."""
        return SkillLevel.get_description(self.level)

    def _infer_type(self) -> SkillType:
        """
        Infere o tipo de habilidade a partir do nome.

        Returns:
            Tipo de habilidade
        """
        # Verifica prefixos de categorias comuns (tech., soft., etc.)
        if "." in self.name:
            prefix = self.name.split(".", 1)[0]
            return SkillType.from_string(prefix)

        # Palavras-chave para tipos técnicos
        tech_keywords = {
            "python",
            "java",
            "javascript",
            "typescript",
            "html",
            "css",
            "react",
            "angular",
            "vue",
            "node",
            "sql",
            "database",
            "nosql",
            "mongodb",
            "aws",
            "azure",
            "cloud",
            "docker",
            "kubernetes",
            "linux",
            "git",
            "programação",
            "programming",
            "código",
            "code",
            "development",
            "algorithm",
            "software",
            "hardware",
            "network",
        }

        # Palavras-chave para tipos comportamentais
        behavioral_keywords = {
            "communication",
            "comunicação",
            "teamwork",
            "trabalho em equipe",
            "collaboration",
            "colaboração",
            "leadership",
            "liderança",
            "creativity",
            "criatividade",
            "problem solving",
            "resolução de problemas",
            "adaptability",
            "adaptabilidade",
            "time management",
            "gestão de tempo",
            "empatia",
            "empathy",
            "feedback",
            "emotional",
            "emocional",
        }

        # Palavras-chave para liderança
        leadership_keywords = {
            "liderança",
            "leadership",
            "gestão",
            "management",
            "coaching",
            "mentoring",
            "mentoria",
            "estratégia",
            "strategy",
            "vision",
            "visão",
        }

        # Palavras-chave para negócios
        business_keywords = {
            "negócio",
            "business",
            "marketing",
            "vendas",
            "sales",
            "finanças",
            "finance",
            "estratégia",
            "strategy",
            "mercado",
            "market",
        }

        # Verifica palavras-chave no nome (normalizado para minúsculas)
        name_lower = self.name.lower()

        for keyword in tech_keywords:
            if keyword in name_lower:
                return SkillType.TECHNICAL

        for keyword in behavioral_keywords:
            if keyword in name_lower:
                return SkillType.BEHAVIORAL

        for keyword in leadership_keywords:
            if keyword in name_lower:
                return SkillType.LEADERSHIP

        for keyword in business_keywords:
            if keyword in name_lower:
                return SkillType.BUSINESS

        # Se não identificou, retorna desconhecido
        return SkillType.UNKNOWN

    def add_prerequisite(self, skill_name: str) -> None:
        """
        Adiciona uma habilidade como pré-requisito.

        Args:
            skill_name: Nome da habilidade pré-requisito
        """
        self.prerequisites.add(skill_name)

    def add_related_skill(self, skill_name: str) -> None:
        """
        Adiciona uma habilidade relacionada.

        Args:
            skill_name: Nome da habilidade relacionada
        """
        self.related_skills.add(skill_name)

    def add_parent_skill(self, skill_name: str) -> None:
        """
        Adiciona uma habilidade pai (mais abrangente).

        Args:
            skill_name: Nome da habilidade pai
        """
        self.parent_skills.add(skill_name)

    def add_child_skill(self, skill_name: str) -> None:
        """
        Adiciona uma habilidade filha (mais específica).

        Args:
            skill_name: Nome da habilidade filha
        """
        self.child_skills.add(skill_name)

    def get_all_relationships(self) -> Dict[str, Set[str]]:
        """
        Obtém todos os relacionamentos da habilidade.

        Returns:
            Dicionário com tipos de relacionamento e conjuntos de habilidades
        """
        return {
            "prerequisites": self.prerequisites,
            "related": self.related_skills,
            "parents": self.parent_skills,
            "children": self.child_skills,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Skill":
        """
        Cria uma habilidade a partir de um dicionário.

        Args:
            data: Dicionário com dados da habilidade

        Returns:
            Instância de Skill
        """
        # Extrai nome, com fallbacks
        name = (
            data.get("name")
            or data.get("nome")
            or data.get("skill_name")
            or data.get("nome_habilidade", "")
        )

        # Extrai nível, com fallbacks
        level_value = (
            data.get("level")
            or data.get("nivel")
            or data.get("proficiency")
            or data.get("proficiencia", 1)
        )

        # Converte nível para inteiro se necessário
        if isinstance(level_value, str):
            try:
                level_value = int(level_value)
            except ValueError:
                level_value = 1

        # Extrai categoria, com fallbacks
        category = (
            data.get("category")
            or data.get("categoria")
            or data.get("type")
            or data.get("tipo")
            or data.get("subcategory")
        )

        # Extrai descrição
        description = data.get("description", "") or data.get("descricao", "")

        # Extrai tipo de habilidade se presente
        skill_type = None
        if "skill_type" in data:
            try:
                if isinstance(data["skill_type"], str):
                    skill_type = SkillType.from_string(data["skill_type"])
            except (ValueError, AttributeError):
                pass

        # Cria habilidade
        skill = cls(
            name=name,
            level=level_value,
            category=category,
            skill_type=skill_type,
            description=description,
            metadata=data.get("metadata", {}),
        )

        # Adiciona relacionamentos se presentes
        if "relationships" in data:
            relationships = data["relationships"]

            for prereq in relationships.get("prerequisites", []):
                skill.add_prerequisite(prereq)

            for related in relationships.get("related", []):
                skill.add_related_skill(related)

            for parent in relationships.get("parents", []):
                skill.add_parent_skill(parent)

            for child in relationships.get("children", []):
                skill.add_child_skill(child)

        return skill

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a habilidade para um dicionário.

        Returns:
            Dicionário com dados da habilidade
        """
        result = {
            "name": self.name,
            "level": self.level,
            "level_description": self.level_description,
            "skill_type": self.skill_type.value if self.skill_type else None,
            "category": self.category,
        }

        # Adiciona campos não vazios
        if self.description:
            result["description"] = self.description

        if self.metadata:
            result["metadata"] = self.metadata

        # Adiciona relacionamentos se não estiverem vazios
        relationships = {}
        if self.prerequisites:
            relationships["prerequisites"] = list(self.prerequisites)
        if self.related_skills:
            relationships["related"] = list(self.related_skills)
        if self.parent_skills:
            relationships["parents"] = list(self.parent_skills)
        if self.child_skills:
            relationships["children"] = list(self.child_skills)

        if relationships:
            result["relationships"] = relationships

        return result


class SkillMatrix:
    """
    Modela uma matriz de habilidades.

    Esta classe representa um conjunto de habilidades de uma pessoa ou equipe,
    permitindo análise, agrupamento e comparação.
    """

    def __init__(self, skills: Optional[List[Skill]] = None, name: str = ""):
        """
        Inicializa uma matriz de habilidades.

        Args:
            skills: Lista de habilidades (opcional)
            name: Nome da matriz (opcional)
        """
        self.skills = skills or []
        self.name = name

    def add_skill(self, skill: Skill) -> None:
        """
        Adiciona uma habilidade à matriz.

        Args:
            skill: Habilidade a adicionar
        """
        # Verifica se já existe uma habilidade com o mesmo nome
        existing = self.get_skill_by_name(skill.name)
        if existing:
            # Atualiza o nível se a habilidade já existir
            existing.level = skill.level
        else:
            # Adiciona nova habilidade
            self.skills.append(skill)

    def get_skill_by_name(self, name: str) -> Optional[Skill]:
        """
        Obtém uma habilidade pelo nome.

        Args:
            name: Nome da habilidade

        Returns:
            Habilidade encontrada ou None
        """
        for skill in self.skills:
            if skill.name.lower() == name.lower():
                return skill
        return None

    def get_skills_by_type(self, skill_type: SkillType) -> List[Skill]:
        """
        Obtém habilidades de um tipo específico.

        Args:
            skill_type: Tipo de habilidade

        Returns:
            Lista de habilidades do tipo
        """
        return [skill for skill in self.skills if skill.skill_type == skill_type]

    def get_skills_by_category(self, category: str) -> List[Skill]:
        """
        Obtém habilidades de uma categoria específica.

        Args:
            category: Categoria de habilidade

        Returns:
            Lista de habilidades da categoria
        """
        return [
            skill
            for skill in self.skills
            if skill.category and skill.category.lower() == category.lower()
        ]

    def get_average_level(self) -> float:
        """
        Calcula o nível médio de todas as habilidades.

        Returns:
            Nível médio de habilidade
        """
        if not self.skills:
            return 0.0

        total = sum(skill.level for skill in self.skills)
        return total / len(self.skills)

    def get_average_level_by_type(self, skill_type: SkillType) -> float:
        """
        Calcula o nível médio de habilidades de um tipo específico.

        Args:
            skill_type: Tipo de habilidade

        Returns:
            Nível médio para o tipo de habilidade
        """
        skills = self.get_skills_by_type(skill_type)
        if not skills:
            return 0.0

        total = sum(skill.level for skill in skills)
        return total / len(skills)

    def get_unique_categories(self) -> List[str]:
        """
        Obtém lista de categorias únicas.

        Returns:
            Lista de categorias únicas
        """
        categories = set()
        for skill in self.skills:
            if skill.category:
                categories.add(skill.category)
        return sorted(list(categories))

    def get_skill_counts_by_level(self) -> Dict[int, int]:
        """
        Conta habilidades por nível.

        Returns:
            Dicionário com contagens (nível -> quantidade)
        """
        counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for skill in self.skills:
            counts[skill.level] += 1
        return counts

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillMatrix":
        """
        Cria uma matriz de habilidades a partir de um dicionário.

        Suporta dois formatos diferentes:
        1. {"skills": [{"name": "Python", "level": 4}, ...]}
        2. {"Python": 4, "JavaScript": 3, ...}

        Args:
            data: Dicionário com dados de habilidades

        Returns:
            Instância de SkillMatrix
        """
        skills = []
        name = data.get("name", "")

        # Verifica formato 1 (lista de habilidades)
        if "skills" in data and isinstance(data["skills"], list):
            for skill_data in data["skills"]:
                try:
                    skill = Skill.from_dict(skill_data)
                    skills.append(skill)
                except Exception as e:
                    logging.warning(f"Erro ao processar habilidade: {e}")

        # Verifica formato 2 (dicionário de nome -> nível)
        else:
            for skill_name, level in data.items():
                # Ignora chaves que não são habilidades
                if skill_name in ("name", "nome", "id", "data"):
                    continue

                try:
                    skill = Skill(name=skill_name, level=level)
                    skills.append(skill)
                except Exception as e:
                    logging.warning(f"Erro ao processar habilidade '{skill_name}': {e}")

        return cls(skills=skills, name=name)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a matriz de habilidades para um dicionário.

        Returns:
            Dicionário com dados da matriz de habilidades
        """
        skill_data = [skill.to_dict() for skill in self.skills]

        return {
            "name": self.name,
            "skills": skill_data,
            "average_level": self.get_average_level(),
            "skill_count": len(self.skills),
            "categories": self.get_unique_categories(),
        }

    def to_simple_dict(self) -> Dict[str, int]:
        """
        Converte para um dicionário simples (nome -> nível).

        Returns:
            Dicionário com nome da habilidade -> nível
        """
        return {skill.name: skill.level for skill in self.skills}


class SkillProficiency:
    """
    Representa a proficiência de uma pessoa em uma habilidade.

    Esta classe armazena:
    - Nível de proficiência
    - Histórico de avaliações
    - Experiência e tempo de prática
    - Certificações e validações
    """

    def __init__(
        self,
        skill_name: str,
        person_id: str,
        proficiency_level: Union[SkillLevel, int, float, str] = SkillLevel.NOVICE,
        last_updated: Optional[datetime] = None,
        source: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Inicializa uma proficiência em habilidade.

        Args:
            skill_name: Nome da habilidade
            person_id: ID da pessoa
            proficiency_level: Nível de proficiência
            last_updated: Data da última atualização
            source: Fonte da informação de proficiência
            metadata: Metadados adicionais
        """
        self.skill_name = skill_name
        self.person_id = person_id

        # Converte nível se não for do tipo SkillLevel
        if not isinstance(proficiency_level, SkillLevel):
            self.proficiency_level = SkillLevel.from_value(proficiency_level)
        else:
            self.proficiency_level = proficiency_level

        self.last_updated = last_updated or datetime.now()
        self.source = source
        self.metadata = metadata or {}

        # Histórico de avaliações
        self.assessment_history: List[Dict[str, Any]] = []

    def update_proficiency(
        self,
        new_level: Union[SkillLevel, int, float, str],
        source: str = "",
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Atualiza o nível de proficiência e registra no histórico.

        Args:
            new_level: Novo nível de proficiência
            source: Fonte da atualização
            timestamp: Data/hora da atualização
            metadata: Metadados adicionais
        """
        # Converte nível se não for do tipo SkillLevel
        if not isinstance(new_level, SkillLevel):
            new_level = SkillLevel.from_value(new_level)

        # Adiciona entrada atual ao histórico
        self.assessment_history.append(
            {
                "level": self.proficiency_level.value,
                "timestamp": self.last_updated,
                "source": self.source,
                "metadata": self.metadata,
            }
        )

        # Atualiza proficiência atual
        self.proficiency_level = new_level
        self.last_updated = timestamp or datetime.now()
        self.source = source

        if metadata:
            self.metadata = metadata

    def add_assessment(
        self,
        level: Union[SkillLevel, int, float, str],
        source: str = "",
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Adiciona uma avaliação ao histórico sem alterar a proficiência atual.

        Args:
            level: Nível de proficiência avaliado
            source: Fonte da avaliação
            timestamp: Data/hora da avaliação
            metadata: Metadados adicionais
        """
        # Converte nível se não for do tipo SkillLevel
        if not isinstance(level, SkillLevel):
            level_enum = SkillLevel.from_value(level)
        else:
            level_enum = level

        self.assessment_history.append(
            {
                "level": level_enum.value,
                "timestamp": timestamp or datetime.now(),
                "source": source,
                "metadata": metadata or {},
            }
        )

    def get_progress_rate(self, days: int = 365) -> float:
        """
        Calcula a taxa de progresso na habilidade.

        Args:
            days: Número de dias a considerar no histórico

        Returns:
            Taxa de progresso (negativa para regressão)
        """
        if len(self.assessment_history) < 2:
            return 0.0

        # Filtra histórico pelo período especificado
        cutoff_date = datetime.now() - timedelta(days=days)
        relevant_history = [
            entry
            for entry in self.assessment_history
            if entry["timestamp"] >= cutoff_date
        ]

        if len(relevant_history) < 2:
            return 0.0

        # Ordena por data
        sorted_history = sorted(relevant_history, key=lambda x: x["timestamp"])

        # Calcula diferença entre primeira e última avaliação
        first = sorted_history[0]["level"]
        last = sorted_history[-1]["level"]

        # Calcula tempo decorrido em dias
        time_delta = (
            sorted_history[-1]["timestamp"] - sorted_history[0]["timestamp"]
        ).days
        if time_delta < 1:
            time_delta = 1  # Evita divisão por zero

        # Calcula taxa de progresso diária
        daily_rate = (last - first) / time_delta

        # Converte para taxa anual (aproximadamente)
        return daily_rate * 365

    def is_stale(self, days: int = 180) -> bool:
        """
        Verifica se a proficiência está desatualizada.

        Args:
            days: Número de dias para considerar desatualizado

        Returns:
            True se a proficiência estiver desatualizada
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        return self.last_updated < cutoff_date

    def get_level_as_scale(self, max_value: float = 10) -> float:
        """
        Obtém o nível de proficiência em uma escala específica.

        Args:
            max_value: Valor máximo da escala desejada

        Returns:
            Valor na escala especificada
        """
        return self.proficiency_level.to_scale(max_value)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a proficiência para um dicionário.

        Returns:
            Dicionário com informações de proficiência
        """
        return {
            "skill_name": self.skill_name,
            "person_id": self.person_id,
            "proficiency_level": self.proficiency_level.value,
            "level_name": self.proficiency_level.name,
            "last_updated": self.last_updated.isoformat(),
            "source": self.source,
            "metadata": self.metadata,
            "assessment_history": [
                {
                    "level": entry["level"],
                    "timestamp": entry["timestamp"].isoformat(),
                    "source": entry["source"],
                    "metadata": entry["metadata"],
                }
                for entry in self.assessment_history
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillProficiency":
        """
        Cria uma proficiência a partir de um dicionário.

        Args:
            data: Dicionário com informações de proficiência

        Returns:
            Instância de SkillProficiency
        """
        # Converte timestamp
        last_updated = None
        if "last_updated" in data:
            try:
                if isinstance(data["last_updated"], str):
                    last_updated = datetime.fromisoformat(data["last_updated"])
                elif isinstance(data["last_updated"], (int, float)):
                    last_updated = datetime.fromtimestamp(data["last_updated"])
            except (ValueError, TypeError):
                last_updated = datetime.now()

        proficiency = cls(
            skill_name=data.get("skill_name", ""),
            person_id=data.get("person_id", ""),
            proficiency_level=data.get("proficiency_level", SkillLevel.NOVICE),
            last_updated=last_updated,
            source=data.get("source", ""),
            metadata=data.get("metadata", {}),
        )

        # Adiciona histórico
        for entry in data.get("assessment_history", []):
            timestamp = None
            if "timestamp" in entry:
                try:
                    if isinstance(entry["timestamp"], str):
                        timestamp = datetime.fromisoformat(entry["timestamp"])
                    elif isinstance(entry["timestamp"], (int, float)):
                        timestamp = datetime.fromtimestamp(entry["timestamp"])
                except (ValueError, TypeError):
                    timestamp = datetime.now()

            proficiency.assessment_history.append(
                {
                    "level": entry.get("level", 1),
                    "timestamp": timestamp or datetime.now(),
                    "source": entry.get("source", ""),
                    "metadata": entry.get("metadata", {}),
                }
            )

        return proficiency


def compare_skill_matrices(
    matrix1: SkillMatrix, matrix2: SkillMatrix
) -> Dict[str, Any]:
    """
    Compara duas matrizes de habilidade.

    Args:
        matrix1: Primeira matriz de habilidades
        matrix2: Segunda matriz de habilidades

    Returns:
        Dicionário com dados comparativos
    """
    result = {
        "common_skills": [],
        "only_in_first": [],
        "only_in_second": [],
        "level_differences": {},
        "average_difference": 0.0,
    }

    # Obtém todos os nomes de habilidades
    names1 = {skill.name.lower() for skill in matrix1.skills}
    names2 = {skill.name.lower() for skill in matrix2.skills}

    # Encontra habilidades comuns e exclusivas
    common_names = names1.intersection(names2)
    only_in_first = names1 - names2
    only_in_second = names2 - names1

    # Preenche habilidades exclusivas de cada matriz
    result["only_in_first"] = [
        skill.to_dict()
        for skill in matrix1.skills
        if skill.name.lower() in only_in_first
    ]

    result["only_in_second"] = [
        skill.to_dict()
        for skill in matrix2.skills
        if skill.name.lower() in only_in_second
    ]

    # Analisa diferenças nas habilidades comuns
    level_diffs = []
    for name in common_names:
        skill1 = matrix1.get_skill_by_name(name)
        skill2 = matrix2.get_skill_by_name(name)

        if skill1 and skill2:
            diff = skill2.level - skill1.level
            level_diffs.append(diff)

            result["common_skills"].append(
                {
                    "name": name,
                    "level1": skill1.level,
                    "level2": skill2.level,
                    "difference": diff,
                }
            )

            result["level_differences"][name] = diff

    # Calcula diferença média de nível
    if level_diffs:
        result["average_difference"] = sum(level_diffs) / len(level_diffs)

    return result


def derive_skill_gap(
    current: SkillMatrix, target: SkillMatrix
) -> Tuple[List[Dict[str, Any]], float]:
    """
    Calcula a lacuna de habilidades entre matriz atual e alvo.

    Args:
        current: Matriz de habilidades atual
        target: Matriz de habilidades alvo

    Returns:
        Tupla contendo:
        1. Lista de habilidades com lacunas, ordenadas por prioridade
        2. Percentual geral de cobertura das habilidades alvo
    """
    gaps = []
    all_target_skills = {skill.name.lower(): skill for skill in target.skills}

    # Dicionário para habilidades atuais
    current_skills = {skill.name.lower(): skill for skill in current.skills}

    # Total de pontos possíveis e obtidos para calcular cobertura
    total_possible = sum(skill.level for skill in target.skills)
    total_achieved = 0

    # Analisa cada habilidade alvo
    for name, target_skill in all_target_skills.items():
        current_skill = current_skills.get(name)

        if current_skill:
            # Atualiza pontos obtidos
            achieved = min(current_skill.level, target_skill.level)
            total_achieved += achieved

            # Se nível atual é menor que o alvo, há uma lacuna
            if current_skill.level < target_skill.level:
                gap = target_skill.level - current_skill.level
                gaps.append(
                    {
                        "name": name,
                        "current_level": current_skill.level,
                        "target_level": target_skill.level,
                        "gap": gap,
                        "skill_type": target_skill.skill_type.value
                        if target_skill.skill_type
                        else None,
                        "exists": True,
                    }
                )
        else:
            # Habilidade não existe atualmente
            gaps.append(
                {
                    "name": name,
                    "current_level": 0,
                    "target_level": target_skill.level,
                    "gap": target_skill.level,
                    "skill_type": target_skill.skill_type.value
                    if target_skill.skill_type
                    else None,
                    "exists": False,
                }
            )

    # Calcula percentual de cobertura
    coverage = (total_achieved / total_possible * 100) if total_possible > 0 else 0

    # Ordena as lacunas por prioridade (maior lacuna primeiro)
    gaps.sort(key=lambda x: x["gap"], reverse=True)

    return gaps, coverage
