"""
Módulo central para avaliações e cálculos de score.

Este módulo contém as classes e funções principais para manipulação
de avaliações, incluindo:
- Modelo de avaliação
- Cálculo de scores
- Normalização de pontuações
- Análise de resultados
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class EvaluationType(Enum):
    """Tipos de avaliação."""

    SELF = "self"  # Autoavaliação
    PEER = "peer"  # Avaliação de pares
    MANAGER = "manager"  # Avaliação de gestor
    PARTNER = "partner"  # Avaliação de parceiro
    CLIENT = "client"  # Avaliação de cliente
    CERTIFICATION = "cert"  # Certificação
    ASSESSMENT = "assess"  # Assessment técnico
    UNKNOWN = "unknown"  # Tipo desconhecido

    @classmethod
    def from_string(cls, value: str) -> "EvaluationType":
        """
        Converte uma string para o tipo de avaliação correspondente.

        Args:
            value: String representando o tipo

        Returns:
            Tipo de avaliação
        """
        value = value.lower()

        if value in ("self", "auto", "autoavaliação", "autoavaliacao"):
            return cls.SELF
        elif value in ("peer", "par", "pares"):
            return cls.PEER
        elif value in ("manager", "gestor", "gestora", "lider", "líder"):
            return cls.MANAGER
        elif value in ("partner", "parceiro", "parceira"):
            return cls.PARTNER
        elif value in ("client", "cliente"):
            return cls.CLIENT
        elif value in ("cert", "certification", "certificação", "certificacao"):
            return cls.CERTIFICATION
        elif value in ("assess", "assessment", "técnico", "tecnico"):
            return cls.ASSESSMENT
        else:
            return cls.UNKNOWN


class EvaluationFrequency(Enum):
    """Frequências de comportamento em avaliações."""

    ALWAYS = "always"  # Sempre
    OFTEN = "often"  # Frequentemente
    SOMETIMES = "sometimes"  # Às vezes
    RARELY = "rarely"  # Raramente
    NEVER = "never"  # Nunca

    @classmethod
    def from_string(cls, value: str) -> "EvaluationFrequency":
        """
        Converte uma string para a frequência correspondente.

        Args:
            value: String representando a frequência

        Returns:
            Frequência de avaliação
        """
        value = value.lower()

        if value in ("always", "sempre"):
            return cls.ALWAYS
        elif value in ("often", "frequentemente", "frequente"):
            return cls.OFTEN
        elif value in ("sometimes", "às vezes", "as vezes", "eventualmente"):
            return cls.SOMETIMES
        elif value in ("rarely", "raramente", "raro"):
            return cls.RARELY
        elif value in ("never", "nunca"):
            return cls.NEVER
        else:
            # Padrão para casos desconhecidos
            return cls.SOMETIMES


class EvaluationScore:
    """
    Classe para calcular e normalizar scores de avaliações.

    Esta classe implementa métodos para:
    - Calcular scores ponderados por frequência
    - Normalizar pontuações entre diferentes escalas
    - Calcular scores gerais a partir de múltiplas fontes
    - Aplicar diferentes modelos de pontuação (padrão, NPS)
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        use_nps_model: bool = False,
        log_level: int = logging.INFO,
    ):
        """
        Inicializa o calculador de scores.

        Args:
            config: Configuração personalizada (opcional)
            use_nps_model: Se deve usar modelo de pontuação NPS
            log_level: Nível de log
        """
        self.logger = logging.getLogger("evaluation_score")
        self.logger.setLevel(log_level)

        # Indica se devemos usar modelo NPS para cálculos
        self.use_nps_model = use_nps_model

        # Configuração padrão
        self.config = {
            # Pesos para diferentes tipos de avaliação
            "weights": {
                "self": 1.0,
                "peer": 1.0,
                "manager": 1.5,
                "partner": 1.0,
                "client": 1.2,
                "cert": 1.3,
                "assess": 1.3,
            },
            # Fatores de normalização de escala
            "scale_normalization": {
                "5_to_10": 2.0,  # Converter escala de 5 pontos para 10
                "7_to_10": 10 / 7,  # Converter escala de 7 pontos para 10
            },
            # Mínimo de avaliações necessárias
            "min_evaluations": {
                "self": 1,
                "peer": 2,
                "manager": 1,
                "partner": 1,
                "client": 1,
            },
            # Configuração de pesos por frequência
            "frequency": {
                "always": 1.0,
                "often": 0.75,
                "sometimes": 0.5,
                "rarely": 0.25,
                "never": 0.0,
            },
            # Configuração de modelo NPS
            "nps": {
                "promoter_threshold": 9,
                "detractor_threshold": 6,
                "promoter_weight": 1,
                "passive_weight": 0,
                "detractor_weight": -1,
            },
        }

        # Atualiza com configuração do usuário
        if config:
            self._update_config(config)

    def _update_config(self, config: Dict[str, Any]) -> None:
        """
        Atualiza a configuração com valores fornecidos pelo usuário.

        Args:
            config: Dicionário de configuração para mesclar com os padrões
        """
        for section, values in config.items():
            if section in self.config:
                if isinstance(self.config[section], dict) and isinstance(values, dict):
                    self.config[section].update(values)
                else:
                    self.config[section] = values
            else:
                self.config[section] = values

    def calculate_weighted_score(
        self,
        evaluations: List[Dict[str, Any]],
        value_key: str = "value",
        frequency_key: Optional[str] = "frequency",
    ) -> float:
        """
        Calcula score ponderado com base em valores e frequências.

        Args:
            evaluations: Lista de dicionários de avaliações
            value_key: Chave para o valor em cada avaliação
            frequency_key: Chave para frequência (opcional)

        Returns:
            Score médio ponderado ou 0.0 se não houver avaliações válidas
        """
        if not evaluations:
            return 0.0

        # Se estamos usando modelo NPS, delegate para método específico
        if self.use_nps_model:
            return self._calculate_nps_score(evaluations, value_key)

        # Cálculo ponderado padrão
        total_weight = 0.0
        weighted_sum = 0.0

        for eval_item in evaluations:
            if value_key not in eval_item:
                continue

            value = eval_item[value_key]

            # Pula se valor não for numérico
            if not isinstance(value, (int, float)):
                continue

            # Determina o peso com base na frequência (se aplicável)
            if frequency_key and frequency_key in eval_item:
                frequency_str = str(eval_item[frequency_key]).lower()
                frequency = EvaluationFrequency.from_string(frequency_str)
                weight = self.config["frequency"].get(frequency.value, 0.5)
            else:
                weight = 1.0

            weighted_sum += value * weight
            total_weight += weight

        if total_weight > 0:
            return weighted_sum / total_weight
        return 0.0

    def _calculate_nps_score(
        self, evaluations: List[Dict[str, Any]], value_key: str = "value"
    ) -> float:
        """
        Calcula score usando modelo Net Promoter Score (NPS).

        Args:
            evaluations: Lista de dicionários de avaliações
            value_key: Chave para o valor em cada avaliação

        Returns:
            Score NPS (-100 a 100) ou 0.0 se não houver avaliações válidas
        """
        if not evaluations:
            return 0.0

        # Conta promoters, passives e detractors
        promoters = 0
        passives = 0
        detractors = 0
        total = 0

        # Thresholds configuráveis
        promoter_threshold = self.config["nps"].get("promoter_threshold", 9)
        detractor_threshold = self.config["nps"].get("detractor_threshold", 6)

        for eval_item in evaluations:
            if value_key not in eval_item:
                continue

            value = eval_item[value_key]

            # Pula se valor não for numérico
            if not isinstance(value, (int, float)):
                continue

            # Classifica o valor
            if value >= promoter_threshold:
                promoters += 1
            elif value > detractor_threshold:
                passives += 1
            else:
                detractors += 1

            total += 1

        # Retorna 0 se não tiver avaliações válidas
        if total == 0:
            return 0.0

        # Calcula o NPS como (% promoters - % detractors) * 100
        return ((promoters / total) - (detractors / total)) * 100

    def normalize_score(
        self, score: float, min_value: float = 0, max_value: float = 10
    ) -> float:
        """
        Normaliza um score para uma escala específica.

        Args:
            score: O score original
            min_value: Valor mínimo da escala desejada
            max_value: Valor máximo da escala desejada

        Returns:
            Score normalizado
        """
        if score == 0:
            return min_value

        # Se estamos normalizando NPS para uma escala padrão
        if self.use_nps_model and min_value == 0:
            # Converte de -100~100 para min~max
            normalized = (score + 100) / 200 * (max_value - min_value) + min_value
            return normalized

        # Normalização simples para a escala desejada
        # Assume que o score original já está em escala de 0 a 10
        scale_factor = (max_value - min_value) / 10
        return min_value + (score * scale_factor)

    def calculate_overall_score(
        self,
        evaluation_data: Dict[str, List[Dict[str, Any]]],
        value_key: str = "value",
        frequency_key: Optional[str] = "frequency",
    ) -> Dict[str, Any]:
        """
        Calcula score geral a partir de múltiplas fontes de avaliação.

        Args:
            evaluation_data: Dicionário com fontes de avaliação como chaves
                            e listas de itens de avaliação como valores
            value_key: Chave para o valor em cada avaliação
            frequency_key: Chave para frequência (opcional)

        Returns:
            Dicionário com scores calculados por fonte e score geral
        """
        results = {
            "by_source": {},
            "overall_score": 0.0,
            "overall_count": 0,
            "valid": False,
        }

        total_weighted_score = 0.0
        total_weight = 0.0

        # Processa cada fonte de avaliação
        for source_str, evaluations in evaluation_data.items():
            source = EvaluationType.from_string(source_str).value

            if not evaluations:
                results["by_source"][source] = {
                    "score": 0.0,
                    "count": 0,
                    "valid": False,
                }
                continue

            # Verifica se temos avaliações suficientes
            min_required = self.config["min_evaluations"].get(source, 1)
            if len(evaluations) < min_required:
                results["by_source"][source] = {
                    "score": 0.0,
                    "count": len(evaluations),
                    "valid": False,
                    "reason": f"Insuficiente. Requer no mínimo {min_required}.",
                }
                continue

            # Calcula score para esta fonte
            source_score = self.calculate_weighted_score(
                evaluations, value_key, frequency_key
            )

            # Armazena resultados para esta fonte
            results["by_source"][source] = {
                "score": source_score,
                "count": len(evaluations),
                "valid": True,
            }

            # Adiciona ao score geral com peso apropriado
            source_weight = self.config["weights"].get(source, 1.0)
            total_weighted_score += source_score * source_weight
            total_weight += source_weight

        # Calcula score geral se tivermos fontes válidas
        if total_weight > 0:
            results["overall_score"] = total_weighted_score / total_weight
            results["overall_count"] = sum(
                len(evals) for evals in evaluation_data.values()
            )
            results["valid"] = True

        return results

    def calculate_skill_scores(
        self,
        evaluation_data: Dict[str, List[Dict[str, Any]]],
        skill_key: str = "skill",
        value_key: str = "value",
        frequency_key: Optional[str] = "frequency",
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calcula scores para habilidades individuais.

        Args:
            evaluation_data: Dicionário com fontes de avaliação como chaves
                            e listas de itens de avaliação como valores
            skill_key: Chave para nome da habilidade em cada avaliação
            value_key: Chave para o valor em cada avaliação
            frequency_key: Chave para frequência (opcional)

        Returns:
            Dicionário com scores calculados por habilidade
        """
        skill_scores = {}

        # Processa cada fonte de avaliação
        for source_str, evaluations in evaluation_data.items():
            source = EvaluationType.from_string(source_str).value
            source_weight = self.config["weights"].get(source, 1.0)

            # Agrupa avaliações por habilidade
            skills_by_name = {}
            for eval_item in evaluations:
                if skill_key not in eval_item:
                    continue

                skill_name = eval_item[skill_key]
                if skill_name not in skills_by_name:
                    skills_by_name[skill_name] = []
                skills_by_name[skill_name].append(eval_item)

            # Calcula score para cada habilidade
            for skill_name, skill_evals in skills_by_name.items():
                skill_score = self.calculate_weighted_score(
                    skill_evals, value_key, frequency_key
                )

                # Inicializa habilidade no dicionário de resultados se não existir
                if skill_name not in skill_scores:
                    skill_scores[skill_name] = {
                        "scores_by_source": {},
                        "overall_score": 0.0,
                        "total_weight": 0.0,
                        "eval_count": 0,
                    }

                # Adiciona o score desta fonte
                skill_scores[skill_name]["scores_by_source"][source] = {
                    "score": skill_score,
                    "count": len(skill_evals),
                }

                # Atualiza cálculos gerais
                skill_scores[skill_name]["total_weight"] += source_weight
                skill_scores[skill_name]["eval_count"] += len(skill_evals)
                skill_scores[skill_name]["overall_score"] += skill_score * source_weight

        # Finaliza scores gerais
        for skill_name, skill_data in skill_scores.items():
            if skill_data["total_weight"] > 0:
                skill_data["overall_score"] /= skill_data["total_weight"]

        return skill_scores

    def calculate_percentile(
        self, score: float, reference_scores: List[float]
    ) -> float:
        """
        Calcula o percentil de um score em relação a outros scores de referência.

        Args:
            score: Score para calcular o percentil
            reference_scores: Lista de scores de referência

        Returns:
            Percentil (0-100)
        """
        if not reference_scores:
            return 50.0  # Valor padrão se não houver scores de referência

        # Remove valores nulos
        valid_scores = [s for s in reference_scores if s is not None]

        if not valid_scores:
            return 50.0

        # Conta quantos scores estão abaixo do nosso
        below_count = sum(1 for s in valid_scores if s < score)

        # Calcula o percentil
        return (below_count / len(valid_scores)) * 100


class Evaluation:
    """
    Representa uma avaliação completa com metadados.

    Esta classe modela uma avaliação individual, incluindo:
    - Dados da pessoa avaliada e avaliador
    - Timestamp e metadados da avaliação
    - Itens de avaliação (respostas, scores)
    - Relação com outras avaliações
    """

    def __init__(
        self,
        evaluee_id: str,
        evaluator_id: Optional[str] = None,
        evaluation_type: Union[EvaluationType, str] = EvaluationType.UNKNOWN,
        items: Optional[List[Dict[str, Any]]] = None,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Inicializa uma avaliação.

        Args:
            evaluee_id: ID da pessoa avaliada
            evaluator_id: ID do avaliador (opcional)
            evaluation_type: Tipo de avaliação
            items: Itens de avaliação (respostas)
            timestamp: Data/hora da avaliação
            metadata: Metadados adicionais
        """
        self.evaluee_id = evaluee_id
        self.evaluator_id = evaluator_id

        # Converte tipo se for string
        if isinstance(evaluation_type, str):
            self.evaluation_type = EvaluationType.from_string(evaluation_type)
        else:
            self.evaluation_type = evaluation_type

        self.items = items or []
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}

        # Cache para scores calculados
        self._calculated_scores = {}

    @property
    def is_self_evaluation(self) -> bool:
        """Verifica se é uma autoavaliação."""
        return self.evaluation_type == EvaluationType.SELF or (
            self.evaluee_id == self.evaluator_id and self.evaluator_id is not None
        )

    def add_item(self, item: Dict[str, Any]) -> None:
        """
        Adiciona um item de avaliação.

        Args:
            item: Dicionário do item de avaliação
        """
        self.items.append(item)
        # Invalida cache de scores
        self._calculated_scores = {}

    def get_score(self, calculator: Optional[EvaluationScore] = None) -> float:
        """
        Obtém o score geral da avaliação.

        Args:
            calculator: Calculador de score (opcional)

        Returns:
            Score geral da avaliação
        """
        # Usa cache se possível
        if "overall" in self._calculated_scores:
            return self._calculated_scores["overall"]

        # Cria calculador se não fornecido
        if calculator is None:
            calculator = EvaluationScore()

        # Calcula score
        score = calculator.calculate_weighted_score(self.items)

        # Armazena em cache
        self._calculated_scores["overall"] = score

        return score

    def get_scores_by_category(
        self,
        calculator: Optional[EvaluationScore] = None,
        category_key: str = "category",
    ) -> Dict[str, float]:
        """
        Obtém scores agrupados por categoria.

        Args:
            calculator: Calculador de score (opcional)
            category_key: Chave para a categoria em cada item

        Returns:
            Dicionário com categoria -> score
        """
        # Usa cache se possível
        cache_key = f"by_category_{category_key}"
        if cache_key in self._calculated_scores:
            return self._calculated_scores[cache_key]

        # Cria calculador se não fornecido
        if calculator is None:
            calculator = EvaluationScore()

        # Agrupa itens por categoria
        items_by_category: Dict[str, List[Dict[str, Any]]] = {}

        for item in self.items:
            if category_key not in item:
                continue

            category = item[category_key]
            if category not in items_by_category:
                items_by_category[category] = []

            items_by_category[category].append(item)

        # Calcula score para cada categoria
        scores = {}
        for category, items in items_by_category.items():
            scores[category] = calculator.calculate_weighted_score(items)

        # Armazena em cache
        self._calculated_scores[cache_key] = scores

        return scores

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a avaliação para um dicionário.

        Returns:
            Dicionário com dados da avaliação
        """
        return {
            "evaluee_id": self.evaluee_id,
            "evaluator_id": self.evaluator_id,
            "evaluation_type": self.evaluation_type.value,
            "is_self_evaluation": self.is_self_evaluation,
            "items": self.items,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "score": self.get_score() if self.items else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Evaluation":
        """
        Cria uma avaliação a partir de um dicionário.

        Args:
            data: Dicionário com dados da avaliação

        Returns:
            Instância de Evaluation
        """
        # Extrai timestamp
        timestamp = None
        if "timestamp" in data:
            try:
                if isinstance(data["timestamp"], str):
                    timestamp = datetime.fromisoformat(data["timestamp"])
                elif isinstance(data["timestamp"], (int, float)):
                    timestamp = datetime.fromtimestamp(data["timestamp"])
            except (ValueError, TypeError):
                timestamp = None

        # Cria avaliação
        return cls(
            evaluee_id=data.get("evaluee_id") or data.get("avaliado_id", ""),
            evaluator_id=data.get("evaluator_id") or data.get("avaliador_id"),
            evaluation_type=data.get("evaluation_type")
            or data.get("tipo", EvaluationType.UNKNOWN),
            items=data.get("items") or data.get("itens", []),
            timestamp=timestamp,
            metadata=data.get("metadata") or data.get("metadados", {}),
        )


class EvaluationSet:
    """
    Conjunto de avaliações relacionadas a uma pessoa ou equipe.

    Esta classe gerencia múltiplas avaliações, facilitando:
    - Agregação de scores
    - Filtragem por tipo, período ou avaliador
    - Análise comparativa
    - Extração de insights
    """

    def __init__(
        self,
        evaluations: Optional[List[Evaluation]] = None,
        evaluee_id: Optional[str] = None,
        name: str = "",
    ):
        """
        Inicializa um conjunto de avaliações.

        Args:
            evaluations: Lista de avaliações (opcional)
            evaluee_id: ID da pessoa avaliada
            name: Nome do conjunto (opcional)
        """
        self.evaluations = evaluations or []
        self.evaluee_id = evaluee_id
        self.name = name

        # Extrai ID da pessoa avaliada da primeira avaliação, se não fornecido
        if not self.evaluee_id and self.evaluations:
            self.evaluee_id = self.evaluations[0].evaluee_id

        # Valida que todas as avaliações são da mesma pessoa
        self._validate_evaluations()

    def _validate_evaluations(self) -> None:
        """
        Valida que todas as avaliações são da mesma pessoa.
        """
        if not self.evaluee_id or not self.evaluations:
            return

        for eval_item in self.evaluations:
            if eval_item.evaluee_id != self.evaluee_id:
                logging.warning(
                    f"Avaliação com ID de avaliado diferente: {eval_item.evaluee_id} "
                    f"(esperado: {self.evaluee_id})"
                )

    def add_evaluation(self, evaluation: Evaluation) -> None:
        """
        Adiciona uma avaliação ao conjunto.

        Args:
            evaluation: Avaliação a adicionar
        """
        # Define ID da pessoa avaliada se for a primeira avaliação
        if not self.evaluee_id:
            self.evaluee_id = evaluation.evaluee_id

        # Verifica se a avaliação é da mesma pessoa
        if evaluation.evaluee_id != self.evaluee_id:
            logging.warning(
                f"Adicionando avaliação com ID de avaliado diferente: {evaluation.evaluee_id} "
                f"(esperado: {self.evaluee_id})"
            )

        self.evaluations.append(evaluation)

    def get_evaluations_by_type(
        self, eval_type: Union[EvaluationType, str]
    ) -> List[Evaluation]:
        """
        Obtém avaliações de um tipo específico.

        Args:
            eval_type: Tipo de avaliação

        Returns:
            Lista de avaliações do tipo especificado
        """
        # Converte tipo se for string
        if isinstance(eval_type, str):
            type_enum = EvaluationType.from_string(eval_type)
        else:
            type_enum = eval_type

        return [
            eval_item
            for eval_item in self.evaluations
            if eval_item.evaluation_type == type_enum
        ]

    def get_evaluations_by_evaluator(self, evaluator_id: str) -> List[Evaluation]:
        """
        Obtém avaliações de um avaliador específico.

        Args:
            evaluator_id: ID do avaliador

        Returns:
            Lista de avaliações do avaliador
        """
        return [
            eval_item
            for eval_item in self.evaluations
            if eval_item.evaluator_id == evaluator_id
        ]

    def get_self_evaluations(self) -> List[Evaluation]:
        """
        Obtém autoavaliações.

        Returns:
            Lista de autoavaliações
        """
        return [
            eval_item for eval_item in self.evaluations if eval_item.is_self_evaluation
        ]

    def get_most_recent_evaluation(
        self, eval_type: Optional[Union[EvaluationType, str]] = None
    ) -> Optional[Evaluation]:
        """
        Obtém a avaliação mais recente, opcionalmente de um tipo específico.

        Args:
            eval_type: Tipo de avaliação (opcional)

        Returns:
            Avaliação mais recente ou None
        """
        filtered_evals = self.evaluations

        # Filtra por tipo se especificado
        if eval_type:
            if isinstance(eval_type, str):
                type_enum = EvaluationType.from_string(eval_type)
            else:
                type_enum = eval_type

            filtered_evals = [
                eval_item
                for eval_item in self.evaluations
                if eval_item.evaluation_type == type_enum
            ]

        if not filtered_evals:
            return None

        # Retorna a avaliação mais recente
        return max(filtered_evals, key=lambda x: x.timestamp)

    def calculate_overall_score(
        self, calculator: Optional[EvaluationScore] = None
    ) -> Dict[str, Any]:
        """
        Calcula score geral a partir de todas as avaliações.

        Args:
            calculator: Calculador de score (opcional)

        Returns:
            Dicionário com scores por tipo e score geral
        """
        # Cria calculador se não fornecido
        if calculator is None:
            calculator = EvaluationScore()

        # Organiza itens de avaliação por tipo
        eval_data: Dict[str, List[Dict[str, Any]]] = {}

        for evaluation in self.evaluations:
            eval_type = evaluation.evaluation_type.value

            if eval_type not in eval_data:
                eval_data[eval_type] = []

            # Adiciona todos os itens desta avaliação
            eval_data[eval_type].extend(evaluation.items)

        # Calcula score geral
        return calculator.calculate_overall_score(eval_data)

    def calculate_skill_scores(
        self, calculator: Optional[EvaluationScore] = None, skill_key: str = "skill"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calcula scores para habilidades individuais.

        Args:
            calculator: Calculador de score (opcional)
            skill_key: Chave para nome da habilidade em cada item

        Returns:
            Dicionário com scores por habilidade
        """
        # Cria calculador se não fornecido
        if calculator is None:
            calculator = EvaluationScore()

        # Organiza itens de avaliação por tipo
        eval_data: Dict[str, List[Dict[str, Any]]] = {}

        for evaluation in self.evaluations:
            eval_type = evaluation.evaluation_type.value

            if eval_type not in eval_data:
                eval_data[eval_type] = []

            # Adiciona todos os itens desta avaliação
            eval_data[eval_type].extend(evaluation.items)

        # Calcula scores por habilidade
        return calculator.calculate_skill_scores(eval_data, skill_key)

    def calculate_score_history(self, interval_days: int = 90) -> List[Dict[str, Any]]:
        """
        Calcula histórico de scores ao longo do tempo.

        Args:
            interval_days: Intervalo em dias entre pontos do histórico

        Returns:
            Lista de pontos de histórico com timestamp e score
        """
        if not self.evaluations:
            return []

        # Ordena avaliações por data
        sorted_evals = sorted(self.evaluations, key=lambda x: x.timestamp)

        # Obtém período total
        start_date = sorted_evals[0].timestamp
        end_date = sorted_evals[-1].timestamp

        # Se período for muito curto, retorna score por avaliação
        if (end_date - start_date).days < interval_days:
            return [
                {
                    "timestamp": e.timestamp,
                    "score": e.get_score(),
                    "type": e.evaluation_type.value,
                }
                for e in sorted_evals
            ]

        # Caso contrário, calcula pontos em intervalos regulares
        history = []
        current_date = start_date

        while current_date <= end_date:
            # Filtra avaliações até a data atual
            evals_until_now = [e for e in sorted_evals if e.timestamp <= current_date]

            if evals_until_now:
                # Calcula score médio para o período
                total_score = sum(e.get_score() for e in evals_until_now)
                avg_score = total_score / len(evals_until_now)

                history.append(
                    {
                        "timestamp": current_date,
                        "score": avg_score,
                        "evaluations_count": len(evals_until_now),
                    }
                )

            # Avança para o próximo intervalo
            current_date = current_date.replace(day=current_date.day + interval_days)

        return history

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o conjunto de avaliações para um dicionário.

        Returns:
            Dicionário com dados do conjunto
        """
        return {
            "evaluee_id": self.evaluee_id,
            "name": self.name,
            "evaluations_count": len(self.evaluations),
            "evaluations": [e.to_dict() for e in self.evaluations],
            "types": list(set(e.evaluation_type.value for e in self.evaluations)),
            "period": {
                "start": min(e.timestamp for e in self.evaluations).isoformat()
                if self.evaluations
                else None,
                "end": max(e.timestamp for e in self.evaluations).isoformat()
                if self.evaluations
                else None,
            }
            if self.evaluations
            else {},
            "overall_score": self.calculate_overall_score() if self.evaluations else {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluationSet":
        """
        Cria um conjunto de avaliações a partir de um dicionário.

        Args:
            data: Dicionário com dados do conjunto

        Returns:
            Instância de EvaluationSet
        """
        evaluations = []

        # Processa lista de avaliações
        eval_data = data.get("evaluations", [])
        for eval_item in eval_data:
            try:
                evaluation = Evaluation.from_dict(eval_item)
                evaluations.append(evaluation)
            except Exception as e:
                logging.warning(f"Erro ao processar avaliação: {e}")

        return cls(
            evaluations=evaluations,
            evaluee_id=data.get("evaluee_id"),
            name=data.get("name", ""),
        )

    @classmethod
    def from_raw_data(
        cls, data: Dict[str, List[Dict[str, Any]]], evaluee_id: str, name: str = ""
    ) -> "EvaluationSet":
        """
        Cria um conjunto de avaliações a partir de dados brutos.

        Args:
            data: Dicionário com tipos de avaliação como chaves
                 e listas de itens como valores
            evaluee_id: ID da pessoa avaliada
            name: Nome do conjunto (opcional)

        Returns:
            Instância de EvaluationSet
        """
        evaluations = []

        for eval_type, items in data.items():
            # Cria uma avaliação para cada tipo
            evaluation = Evaluation(
                evaluee_id=evaluee_id, evaluation_type=eval_type, items=items
            )
            evaluations.append(evaluation)

        return cls(evaluations=evaluations, evaluee_id=evaluee_id, name=name)
