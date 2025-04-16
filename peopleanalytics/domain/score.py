"""
Módulo central para manipulação de scores e métricas.

Este módulo contém as classes e funções relacionadas a scores:
- Modelos de pontuação
- Cálculos e agregações
- Normalização e comparação
- Representação e visualização
"""

import logging
import math
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


class ScoreCategory(Enum):
    """Categorias de scores e métricas."""

    PERFORMANCE = "performance"  # Desempenho
    ENGAGEMENT = "engagement"  # Engajamento
    COMPETENCE = "competence"  # Competência
    POTENTIAL = "potential"  # Potencial
    LEADERSHIP = "leadership"  # Liderança
    TEAMWORK = "teamwork"  # Trabalho em equipe
    INNOVATION = "innovation"  # Inovação
    COMMUNICATION = "communication"  # Comunicação
    QUALITY = "quality"  # Qualidade
    PRODUCTIVITY = "productivity"  # Produtividade
    SKILL = "skill"  # Habilidade específica
    COMPOSITE = "composite"  # Score composto (agregação)
    OTHER = "other"  # Outros tipos

    @classmethod
    def from_string(cls, value: str) -> "ScoreCategory":
        """
        Converte uma string para a categoria correspondente.

        Args:
            value: String representando a categoria

        Returns:
            Categoria de score
        """
        value = value.lower()

        if value in ("performance", "desempenho"):
            return cls.PERFORMANCE
        elif value in ("engagement", "engajamento", "compromisso"):
            return cls.ENGAGEMENT
        elif value in ("competence", "competência", "competencia"):
            return cls.COMPETENCE
        elif value in ("potential", "potencial"):
            return cls.POTENTIAL
        elif value in ("leadership", "liderança", "lideranca"):
            return cls.LEADERSHIP
        elif value in ("teamwork", "trabalho em equipe", "equipe"):
            return cls.TEAMWORK
        elif value in ("innovation", "inovação", "inovacao"):
            return cls.INNOVATION
        elif value in ("communication", "comunicação", "comunicacao"):
            return cls.COMMUNICATION
        elif value in ("quality", "qualidade"):
            return cls.QUALITY
        elif value in ("productivity", "produtividade"):
            return cls.PRODUCTIVITY
        elif value in ("skill", "habilidade"):
            return cls.SKILL
        elif value in ("composite", "composto", "agregado"):
            return cls.COMPOSITE
        else:
            return cls.OTHER


class ScoreScale:
    """
    Representa uma escala para scores.

    Esta classe define:
    - Valores mínimo e máximo
    - Pontos de referência (benchmarks)
    - Conversão entre escalas
    """

    def __init__(
        self,
        min_value: float = 0.0,
        max_value: float = 10.0,
        benchmarks: Optional[Dict[str, float]] = None,
        name: str = "",
    ):
        """
        Inicializa uma escala de score.

        Args:
            min_value: Valor mínimo da escala
            max_value: Valor máximo da escala
            benchmarks: Dicionário com pontos de referência
            name: Nome da escala
        """
        if min_value >= max_value:
            raise ValueError("min_value deve ser menor que max_value")

        self.min_value = min_value
        self.max_value = max_value
        self.benchmarks = benchmarks or {}
        self.name = name

    def get_range(self) -> float:
        """
        Obtém a amplitude da escala.

        Returns:
            Diferença entre máximo e mínimo
        """
        return self.max_value - self.min_value

    def normalize(self, value: float) -> float:
        """
        Normaliza um valor para o intervalo [0, 1].

        Args:
            value: Valor a ser normalizado

        Returns:
            Valor normalizado entre 0 e 1
        """
        if value <= self.min_value:
            return 0.0
        if value >= self.max_value:
            return 1.0

        return (value - self.min_value) / self.get_range()

    def denormalize(self, normalized_value: float) -> float:
        """
        Converte um valor normalizado [0, 1] para a escala original.

        Args:
            normalized_value: Valor normalizado entre 0 e 1

        Returns:
            Valor na escala original
        """
        if normalized_value <= 0:
            return self.min_value
        if normalized_value >= 1:
            return self.max_value

        return self.min_value + (normalized_value * self.get_range())

    def convert_to(self, value: float, target_scale: "ScoreScale") -> float:
        """
        Converte um valor desta escala para outra escala.

        Args:
            value: Valor na escala atual
            target_scale: Escala de destino

        Returns:
            Valor convertido para a escala de destino
        """
        normalized = self.normalize(value)
        return target_scale.denormalize(normalized)

    def add_benchmark(self, name: str, value: float) -> None:
        """
        Adiciona um ponto de referência à escala.

        Args:
            name: Nome do benchmark
            value: Valor do benchmark
        """
        if value < self.min_value or value > self.max_value:
            logging.warning(
                f"Benchmark '{name}' com valor {value} está fora da escala [{self.min_value}, {self.max_value}]"
            )

        self.benchmarks[name] = value

    def get_benchmark(self, name: str) -> Optional[float]:
        """
        Obtém um benchmark pelo nome.

        Args:
            name: Nome do benchmark

        Returns:
            Valor do benchmark ou None se não existir
        """
        return self.benchmarks.get(name)

    def get_percentile(self, value: float) -> float:
        """
        Converte um valor para percentil na escala.

        Args:
            value: Valor a converter

        Returns:
            Valor como percentil (0-100)
        """
        return self.normalize(value) * 100

    def from_percentile(self, percentile: float) -> float:
        """
        Converte um percentil para valor na escala.

        Args:
            percentile: Percentil (0-100)

        Returns:
            Valor correspondente na escala
        """
        return self.denormalize(percentile / 100)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a escala para um dicionário.

        Returns:
            Dicionário com informações da escala
        """
        return {
            "name": self.name,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "benchmarks": self.benchmarks,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScoreScale":
        """
        Cria uma escala a partir de um dicionário.

        Args:
            data: Dicionário com informações da escala

        Returns:
            Instância de ScoreScale
        """
        return cls(
            min_value=data.get("min_value", 0.0),
            max_value=data.get("max_value", 10.0),
            benchmarks=data.get("benchmarks", {}),
            name=data.get("name", ""),
        )

    @classmethod
    def create_common_scales(cls) -> Dict[str, "ScoreScale"]:
        """
        Cria um conjunto de escalas comuns.

        Returns:
            Dicionário com escalas comuns
        """
        scales = {
            "decimal": cls(0.0, 10.0, name="Decimal (0-10)"),
            "percentage": cls(0.0, 100.0, name="Percentual (0-100%)"),
            "five_point": cls(1.0, 5.0, name="Cinco pontos (1-5)"),
            "nine_box": cls(1.0, 9.0, name="Nine Box (1-9)"),
            "z_score": cls(-3.0, 3.0, name="Z-Score (-3 a +3)"),
        }

        # Adiciona benchmarks para escala decimal
        scales["decimal"].add_benchmark("baixo", 3.0)
        scales["decimal"].add_benchmark("médio", 5.0)
        scales["decimal"].add_benchmark("alto", 7.0)
        scales["decimal"].add_benchmark("excelente", 9.0)

        # Adiciona benchmarks para escala percentual
        scales["percentage"].add_benchmark("baixo", 30.0)
        scales["percentage"].add_benchmark("médio", 50.0)
        scales["percentage"].add_benchmark("alto", 70.0)
        scales["percentage"].add_benchmark("excelente", 90.0)

        # Adiciona benchmarks para escala de cinco pontos
        scales["five_point"].add_benchmark("baixo", 2.0)
        scales["five_point"].add_benchmark("médio", 3.0)
        scales["five_point"].add_benchmark("alto", 4.0)
        scales["five_point"].add_benchmark("excelente", 4.5)

        return scales


@dataclass
class Score:
    """
    Representa um score individual.

    Esta classe armazena:
    - Valor do score
    - Metadata e contexto
    - Histórico e evolução
    """

    value: float
    name: str
    category: Union[ScoreCategory, str] = ScoreCategory.OTHER
    scale: Optional[ScoreScale] = None
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    person_id: str = ""
    confidence: float = 1.0  # 0.0 a 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """
        Inicialização posterior à criação.
        """
        # Define escala padrão se não fornecida
        if self.scale is None:
            self.scale = ScoreScale()

        # Converte categoria se for string
        if isinstance(self.category, str):
            self.category = ScoreCategory.from_string(self.category)

        # Garante que o valor está dentro da escala
        self._validate_value()

    def _validate_value(self) -> None:
        """
        Valida se o valor está dentro da escala.
        """
        if self.value < self.scale.min_value:
            logging.warning(
                f"Score '{self.name}' com valor {self.value} está abaixo do mínimo da escala ({self.scale.min_value})"
            )
            self.value = self.scale.min_value

        elif self.value > self.scale.max_value:
            logging.warning(
                f"Score '{self.name}' com valor {self.value} está acima do máximo da escala ({self.scale.max_value})"
            )
            self.value = self.scale.max_value

    def normalized_value(self) -> float:
        """
        Retorna o valor normalizado entre 0 e 1.

        Returns:
            Valor normalizado
        """
        return self.scale.normalize(self.value)

    def as_percentile(self) -> float:
        """
        Retorna o valor como percentil (0-100).

        Returns:
            Valor como percentil
        """
        return self.scale.get_percentile(self.value)

    def convert_to_scale(self, target_scale: ScoreScale) -> float:
        """
        Converte o valor para outra escala.

        Args:
            target_scale: Escala de destino

        Returns:
            Valor na escala de destino
        """
        return self.scale.convert_to(self.value, target_scale)

    def is_above_benchmark(self, benchmark_name: str) -> bool:
        """
        Verifica se o valor está acima de um benchmark.

        Args:
            benchmark_name: Nome do benchmark

        Returns:
            True se valor estiver acima do benchmark
        """
        benchmark = self.scale.get_benchmark(benchmark_name)
        if benchmark is None:
            return False

        return self.value >= benchmark

    def is_recent(self, days: int = 90) -> bool:
        """
        Verifica se o score é recente.

        Args:
            days: Número de dias para considerar recente

        Returns:
            True se o score for recente
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        return self.timestamp >= cutoff_date

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o score para um dicionário.

        Returns:
            Dicionário com informações do score
        """
        return {
            "value": self.value,
            "name": self.name,
            "category": self.category.value,
            "scale": self.scale.to_dict() if self.scale else None,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "person_id": self.person_id,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "normalized_value": self.normalized_value(),
            "percentile": self.as_percentile(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Score":
        """
        Cria um score a partir de um dicionário.

        Args:
            data: Dicionário com informações do score

        Returns:
            Instância de Score
        """
        # Processa timestamp
        timestamp = datetime.now()
        if "timestamp" in data:
            try:
                if isinstance(data["timestamp"], str):
                    timestamp = datetime.fromisoformat(data["timestamp"])
                elif isinstance(data["timestamp"], (int, float)):
                    timestamp = datetime.fromtimestamp(data["timestamp"])
            except (ValueError, TypeError):
                pass

        # Processa escala
        scale = None
        if "scale" in data and isinstance(data["scale"], dict):
            try:
                scale = ScoreScale.from_dict(data["scale"])
            except (ValueError, TypeError):
                scale = ScoreScale()

        return cls(
            value=data.get("value", 0.0),
            name=data.get("name", ""),
            category=data.get("category", ScoreCategory.OTHER),
            scale=scale,
            timestamp=timestamp,
            source=data.get("source", ""),
            person_id=data.get("person_id", ""),
            confidence=data.get("confidence", 1.0),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ScoreHistory:
    """
    Representa o histórico de um score ao longo do tempo.

    Esta classe permite:
    - Armazenar múltiplas medições de um score
    - Analisar tendências e progresso
    - Calcular estatísticas sobre a evolução
    """

    name: str
    category: Union[ScoreCategory, str] = ScoreCategory.OTHER
    person_id: str = ""
    entries: List[Score] = field(default_factory=list)
    scale: Optional[ScoreScale] = None

    def __post_init__(self):
        """
        Inicialização posterior à criação.
        """
        # Define escala padrão se não fornecida
        if self.scale is None:
            self.scale = ScoreScale()

        # Converte categoria se for string
        if isinstance(self.category, str):
            self.category = ScoreCategory.from_string(self.category)

    def add_entry(self, score: Score) -> None:
        """
        Adiciona uma entrada ao histórico.

        Args:
            score: Score a adicionar
        """
        # Verifica se o score é para a mesma pessoa
        if self.person_id and score.person_id and score.person_id != self.person_id:
            logging.warning(
                f"Tentativa de adicionar score para pessoa {score.person_id} em histórico da pessoa {self.person_id}"
            )
            return

        # Se for a primeira entrada, define pessoa_id se não estiver definido
        if not self.person_id and score.person_id:
            self.person_id = score.person_id

        # Adiciona entrada, mantendo ordem cronológica
        self.entries.append(score)
        self.entries.sort(key=lambda x: x.timestamp)

    def get_entries(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_confidence: float = 0.0,
    ) -> List[Score]:
        """
        Obtém entradas filtradas por período e confiança.

        Args:
            start_date: Data inicial do período
            end_date: Data final do período
            min_confidence: Confiança mínima

        Returns:
            Lista de entradas filtradas
        """
        filtered = self.entries

        if start_date:
            filtered = [entry for entry in filtered if entry.timestamp >= start_date]

        if end_date:
            filtered = [entry for entry in filtered if entry.timestamp <= end_date]

        if min_confidence > 0:
            filtered = [
                entry for entry in filtered if entry.confidence >= min_confidence
            ]

        return filtered

    def get_latest(self, min_confidence: float = 0.0) -> Optional[Score]:
        """
        Obtém a entrada mais recente.

        Args:
            min_confidence: Confiança mínima

        Returns:
            Score mais recente ou None se não houver entradas
        """
        filtered = [
            entry for entry in self.entries if entry.confidence >= min_confidence
        ]

        if not filtered:
            return None

        return max(filtered, key=lambda x: x.timestamp)

    def get_average(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_confidence: float = 0.0,
        weighted_by_confidence: bool = True,
    ) -> Optional[float]:
        """
        Calcula a média das entradas.

        Args:
            start_date: Data inicial do período
            end_date: Data final do período
            min_confidence: Confiança mínima
            weighted_by_confidence: Se True, pondera valores pela confiança

        Returns:
            Média ou None se não houver entradas
        """
        entries = self.get_entries(start_date, end_date, min_confidence)

        if not entries:
            return None

        if weighted_by_confidence:
            total_weight = sum(entry.confidence for entry in entries)
            if total_weight == 0:
                return None

            weighted_sum = sum(entry.value * entry.confidence for entry in entries)
            return weighted_sum / total_weight
        else:
            return sum(entry.value for entry in entries) / len(entries)

    def get_trend(
        self, days: int = 365, min_entries: int = 2, min_confidence: float = 0.0
    ) -> Optional[float]:
        """
        Calcula a tendência de evolução do score.

        Args:
            days: Número de dias a considerar
            min_entries: Número mínimo de entradas para cálculo
            min_confidence: Confiança mínima

        Returns:
            Taxa de variação (positiva=melhora, negativa=piora) ou None
        """
        start_date = datetime.now() - timedelta(days=days)
        entries = self.get_entries(start_date, None, min_confidence)

        if len(entries) < min_entries:
            return None

        # Simplificação: usa primeira e última entrada para calcular tendência
        first = entries[0]
        last = entries[-1]

        if first.timestamp == last.timestamp:
            return 0.0

        # Normaliza valores para comparação justa se escalas forem diferentes
        if first.scale != last.scale:
            first_normalized = first.normalized_value()
            last_normalized = last.normalized_value()
            delta = last_normalized - first_normalized
        else:
            delta = last.value - first.value

        # Calcula tempo em dias
        time_delta = (last.timestamp - first.timestamp).days
        if time_delta < 1:
            time_delta = 1  # Evita divisão por zero

        # Calcula taxa de variação diária
        daily_rate = delta / time_delta

        # Converte para taxa anual (aproximadamente)
        return daily_rate * 365

    def get_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_confidence: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Calcula estatísticas sobre as entradas.

        Args:
            start_date: Data inicial do período
            end_date: Data final do período
            min_confidence: Confiança mínima

        Returns:
            Dicionário com estatísticas
        """
        entries = self.get_entries(start_date, end_date, min_confidence)

        if not entries:
            return {
                "count": 0,
                "min": None,
                "max": None,
                "avg": None,
                "median": None,
                "std_dev": None,
                "trend": None,
            }

        values = [entry.value for entry in entries]

        stats = {
            "count": len(entries),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "first": entries[0].value,
            "last": entries[-1].value,
            "first_date": entries[0].timestamp,
            "last_date": entries[-1].timestamp,
        }

        # Estatísticas que requerem pelo menos 2 entradas
        if len(entries) >= 2:
            stats["median"] = statistics.median(values)

            try:
                stats["std_dev"] = statistics.stdev(values)
            except statistics.StatisticsError:
                stats["std_dev"] = 0

            # Calcula tendência
            if entries[-1].timestamp > entries[0].timestamp:
                time_span = (entries[-1].timestamp - entries[0].timestamp).days
                if time_span > 0:
                    value_change = entries[-1].value - entries[0].value
                    stats["trend"] = value_change / time_span
                else:
                    stats["trend"] = 0
            else:
                stats["trend"] = 0
        else:
            stats["median"] = values[0]
            stats["std_dev"] = 0
            stats["trend"] = 0

        return stats

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o histórico para um dicionário.

        Returns:
            Dicionário com informações do histórico
        """
        latest = self.get_latest()
        stats = self.get_stats()

        return {
            "name": self.name,
            "category": self.category.value,
            "person_id": self.person_id,
            "scale": self.scale.to_dict() if self.scale else None,
            "entries": [entry.to_dict() for entry in self.entries],
            "stats": stats,
            "latest_value": latest.value if latest else None,
            "latest_date": latest.timestamp.isoformat() if latest else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScoreHistory":
        """
        Cria um histórico a partir de um dicionário.

        Args:
            data: Dicionário com informações do histórico

        Returns:
            Instância de ScoreHistory
        """
        # Processa escala
        scale = None
        if "scale" in data and isinstance(data["scale"], dict):
            try:
                scale = ScoreScale.from_dict(data["scale"])
            except (ValueError, TypeError):
                scale = ScoreScale()

        history = cls(
            name=data.get("name", ""),
            category=data.get("category", ScoreCategory.OTHER),
            person_id=data.get("person_id", ""),
            scale=scale,
        )

        # Adiciona entradas
        for entry_data in data.get("entries", []):
            try:
                score = Score.from_dict(entry_data)
                history.add_entry(score)
            except Exception as e:
                logging.warning(f"Erro ao processar entrada de histórico: {e}")

        return history


class CompositeScore:
    """
    Representa um score composto por múltiplos scores individuais.

    Esta classe permite:
    - Combinar múltiplos scores com pesos
    - Aplicar transformações e normalizações
    - Calcular scores compostos complexos
    """

    def __init__(
        self,
        name: str,
        scale: Optional[ScoreScale] = None,
        category: Union[ScoreCategory, str] = ScoreCategory.COMPOSITE,
        weights: Optional[Dict[str, float]] = None,
        transform_func: Optional[
            Callable[[List[Tuple[str, float, float]]], float]
        ] = None,
    ):
        """
        Inicializa um score composto.

        Args:
            name: Nome do score composto
            scale: Escala do score resultante
            category: Categoria do score
            weights: Dicionário de pesos para cada componente
            transform_func: Função personalizada para cálculo do score composto
        """
        self.name = name
        self.scale = scale or ScoreScale()

        # Converte categoria se for string
        if isinstance(category, str):
            self.category = ScoreCategory.from_string(category)
        else:
            self.category = category

        self.weights = weights or {}
        self.transform_func = transform_func
        self.components: Dict[str, Score] = {}

    def add_component(self, score: Score, weight: Optional[float] = None) -> None:
        """
        Adiciona um componente ao score composto.

        Args:
            score: Score a adicionar
            weight: Peso do componente (sobrescreve peso do dicionário)
        """
        self.components[score.name] = score

        if weight is not None:
            self.weights[score.name] = weight

    def remove_component(self, name: str) -> None:
        """
        Remove um componente do score composto.

        Args:
            name: Nome do componente a remover
        """
        if name in self.components:
            del self.components[name]

        if name in self.weights:
            del self.weights[name]

    def get_weight(self, name: str) -> float:
        """
        Obtém o peso de um componente.

        Args:
            name: Nome do componente

        Returns:
            Peso do componente (1.0 se não definido)
        """
        return self.weights.get(name, 1.0)

    def calculate(self) -> Score:
        """
        Calcula o score composto.

        Returns:
            Score resultante do cálculo
        """
        if not self.components:
            return Score(
                value=0.0,
                name=self.name,
                category=self.category,
                scale=self.scale,
                confidence=0.0,
            )

        # Se há função personalizada, usa-a
        if self.transform_func:
            component_data = [
                (name, score.value, self.get_weight(name))
                for name, score in self.components.items()
            ]
            try:
                value = self.transform_func(component_data)
            except Exception as e:
                logging.error(
                    f"Erro ao calcular score composto usando função personalizada: {e}"
                )
                value = 0.0
        else:
            # Cálculo padrão: média ponderada
            total_weight = sum(self.get_weight(name) for name in self.components)
            if total_weight == 0:
                value = 0.0
            else:
                weighted_sum = sum(
                    score.value * self.get_weight(name)
                    for name, score in self.components.items()
                )
                value = weighted_sum / total_weight

        # Calcula confiança agregada (média das confianças dos componentes)
        avg_confidence = sum(
            score.confidence for score in self.components.values()
        ) / len(self.components)

        # Metadata agregada
        metadata = {
            "components": [name for name in self.components],
            "weights": {name: self.get_weight(name) for name in self.components},
            "calculation_method": "custom"
            if self.transform_func
            else "weighted_average",
            "component_values": {
                name: score.value for name, score in self.components.items()
            },
        }

        # Obtém a fonte mais recente
        latest_source = max(self.components.values(), key=lambda x: x.timestamp).source

        # Cria o score resultante
        return Score(
            value=value,
            name=self.name,
            category=self.category,
            scale=self.scale,
            confidence=avg_confidence,
            source=f"composite:{latest_source}",
            metadata=metadata,
            timestamp=datetime.now(),
        )

    @staticmethod
    def weighted_average(components: List[Tuple[str, float, float]]) -> float:
        """
        Calcula média ponderada de componentes.

        Args:
            components: Lista de tuplas (nome, valor, peso)

        Returns:
            Média ponderada
        """
        total_weight = sum(weight for _, _, weight in components)
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(value * weight for _, value, weight in components)
        return weighted_sum / total_weight

    @staticmethod
    def geometric_mean(components: List[Tuple[str, float, float]]) -> float:
        """
        Calcula média geométrica de componentes.
        Útil quando queremos considerar a proporção entre os valores.

        Args:
            components: Lista de tuplas (nome, valor, peso)

        Returns:
            Média geométrica
        """
        # Filtra valores <= 0 para evitar problemas com log
        positive_components = [(n, v, w) for n, v, w in components if v > 0]

        if not positive_components:
            return 0.0

        # Para média geométrica ponderada:
        # (v1^w1 * v2^w2 * ... * vn^wn)^(1/soma_pesos)
        total_weight = sum(weight for _, _, weight in positive_components)
        if total_weight == 0:
            return 0.0

        log_sum = sum(
            weight * math.log(value) for _, value, weight in positive_components
        )

        return math.exp(log_sum / total_weight)

    @staticmethod
    def min_value(components: List[Tuple[str, float, float]]) -> float:
        """
        Retorna o menor valor dos componentes.
        Útil quando queremos limitar pelo pior resultado.

        Args:
            components: Lista de tuplas (nome, valor, peso)

        Returns:
            Valor mínimo
        """
        if not components:
            return 0.0

        return min(value for _, value, _ in components)

    @staticmethod
    def max_value(components: List[Tuple[str, float, float]]) -> float:
        """
        Retorna o maior valor dos componentes.
        Útil quando queremos destacar o melhor resultado.

        Args:
            components: Lista de tuplas (nome, valor, peso)

        Returns:
            Valor máximo
        """
        if not components:
            return 0.0

        return max(value for _, value, _ in components)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o score composto para um dicionário.

        Returns:
            Dicionário com informações do score composto
        """
        return {
            "name": self.name,
            "category": self.category.value,
            "scale": self.scale.to_dict(),
            "weights": self.weights,
            "has_custom_transform": self.transform_func is not None,
            "components": {
                name: score.to_dict() for name, score in self.components.items()
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompositeScore":
        """
        Cria um score composto a partir de um dicionário.

        Args:
            data: Dicionário com informações do score composto

        Returns:
            Instância de CompositeScore
        """
        # Processa escala
        scale = None
        if "scale" in data and isinstance(data["scale"], dict):
            try:
                scale = ScoreScale.from_dict(data["scale"])
            except (ValueError, TypeError):
                scale = ScoreScale()

        composite = cls(
            name=data.get("name", ""),
            category=data.get("category", ScoreCategory.COMPOSITE),
            scale=scale,
            weights=data.get("weights", {}),
        )

        # Adiciona componentes
        for name, component_data in data.get("components", {}).items():
            try:
                score = Score.from_dict(component_data)
                composite.add_component(score)
            except Exception as e:
                logging.warning(f"Erro ao processar componente do score composto: {e}")

        return composite
