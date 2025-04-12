"""
Classes para análise de trajetória na matriz 9-box.

Implementa a análise de movimento, detecção de gatilhos de aceleração e
projeções futuras para colaboradores na matriz 9-box.
"""
import math
import numpy as np
import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

# Importação condicional para evitar problemas de importação cíclica
try:
    from peopleanalytics.talent_development.matrix_9box.dynamic_matrix import MatrixPosition
except ImportError:
    # Define MatrixPosition para type hints funcionarem
    @dataclass
    class MatrixPosition:
        performance: float
        potential: float
        timestamp: datetime.datetime
        source_data: Dict[str, Any]


@dataclass
class MovementVector:
    """Vetor de movimento na matriz 9-box."""
    direction_radians: float  # Ângulo em radianos
    direction_degrees: float  # Ângulo em graus (0-360)
    velocity: float  # Unidades por trimestre
    performance_delta: float  # Mudança em performance
    potential_delta: float  # Mudança em potencial
    time_delta: float  # Diferença de tempo em dias
    
    @property
    def is_positive(self) -> bool:
        """Verifica se o movimento é positivo (crescimento geral)."""
        # Consideramos positivo se pelo menos um dos eixos está crescendo
        # e o outro não está decrescendo significativamente
        return (self.performance_delta > 0 and self.potential_delta >= -0.5) or \
               (self.potential_delta > 0 and self.performance_delta >= -0.5)
    
    @property
    def primary_dimension(self) -> str:
        """Retorna a dimensão principal do movimento."""
        if abs(self.performance_delta) > abs(self.potential_delta):
            return "desempenho"
        else:
            return "potencial"


@dataclass
class AccelerationTrigger:
    """Evento que causou aceleração na trajetória."""
    timestamp: datetime.datetime
    event_type: str  # 'promotion', 'project', 'training', etc.
    description: str
    impact_description: str
    impact_value: float  # Valor numérico do impacto (0-10)
    position_before: Optional[MatrixPosition] = None
    position_after: Optional[MatrixPosition] = None


@dataclass
class FutureProjection:
    """Projeção futura de posições na matriz 9-box."""
    projected_positions: List[MatrixPosition]
    confidence_level: float  # 0.0 a 1.0
    projection_rationale: str
    recommended_interventions: List[Dict[str, Any]]


class TrajectoryAnalyzer:
    """
    Analisador de trajetória para a matriz 9-box.
    
    Responsável por:
    - Calcular vetores de movimento
    - Identificar gatilhos de aceleração
    - Gerar projeções futuras
    """
    
    def calculate_movement_vector(self, positions: List[MatrixPosition]) -> Optional[MovementVector]:
        """
        Calcula o vetor de movimento baseado nas posições históricas.
        
        Args:
            positions: Lista ordenada de posições históricas
            
        Returns:
            Vetor de movimento ou None se não houver dados suficientes
        """
        if len(positions) < 2:
            return None
            
        # Pegar primeira e última posição para cálculo geral
        first = positions[0]
        last = positions[-1]
        
        # Calcular deltas
        perf_delta = last.performance - first.performance
        pot_delta = last.potential - first.potential
        
        # Calcular tempo em dias
        time_delta = (last.timestamp - first.timestamp).days
        if time_delta == 0:
            time_delta = 1  # Evitar divisão por zero
        
        # Calcular direção do vetor (ângulo)
        # 0 graus = movimento para direita (desempenho puro)
        # 90 graus = movimento para cima (potencial puro)
        direction_radians = math.atan2(pot_delta, perf_delta) if perf_delta != 0 else (
            math.pi/2 if pot_delta > 0 else -math.pi/2 if pot_delta < 0 else 0
        )
        
        # Converter para graus e normalizar para 0-360
        direction_degrees = math.degrees(direction_radians)
        if direction_degrees < 0:
            direction_degrees += 360
        
        # Calcular velocidade (unidades por trimestre)
        # Magnitude do vetor = sqrt(perf_delta² + pot_delta²)
        magnitude = math.sqrt(perf_delta**2 + pot_delta**2)
        # Converter para velocidade trimestral
        velocity = magnitude / (time_delta / 90)  # 90 dias = 1 trimestre
        
        return MovementVector(
            direction_radians=direction_radians,
            direction_degrees=direction_degrees,
            velocity=velocity,
            performance_delta=perf_delta,
            potential_delta=pot_delta,
            time_delta=time_delta
        )
    
    def identify_acceleration_triggers(
        self, positions: List[MatrixPosition], person_id: str, 
        data_pipeline: Any = None
    ) -> List[AccelerationTrigger]:
        """
        Identifica eventos que causaram aceleração significativa na trajetória.
        
        Args:
            positions: Lista ordenada de posições históricas
            person_id: ID da pessoa
            data_pipeline: Pipeline de dados para buscar eventos associados
            
        Returns:
            Lista de gatilhos de aceleração identificados
        """
        if len(positions) < 3:
            return []
            
        triggers = []
        
        # Calcular velocidades locais (entre pontos consecutivos)
        for i in range(1, len(positions)):
            prev = positions[i-1]
            curr = positions[i]
            
            # Calcular vetor local
            perf_delta = curr.performance - prev.performance
            pot_delta = curr.potential - prev.potential
            time_delta = (curr.timestamp - prev.timestamp).days
            if time_delta == 0:
                time_delta = 1
            
            # Magnitude do vetor local
            local_magnitude = math.sqrt(perf_delta**2 + pot_delta**2)
            # Velocidade local
            local_velocity = local_magnitude / (time_delta / 90)
            
            # Calcular velocidade média até o ponto anterior
            if i > 1:
                prev_velocities = []
                for j in range(1, i):
                    p1 = positions[j-1]
                    p2 = positions[j]
                    pd = p2.performance - p1.performance
                    ptd = p2.potential - p1.potential
                    td = (p2.timestamp - p1.timestamp).days or 1
                    mag = math.sqrt(pd**2 + ptd**2)
                    vel = mag / (td / 90)
                    prev_velocities.append(vel)
                
                avg_velocity = sum(prev_velocities) / len(prev_velocities)
                
                # Detectar aceleração significativa (mais de 50% acima da média)
                if local_velocity > avg_velocity * 1.5:
                    # Temos um gatilho potencial
                    
                    # Buscar eventos próximos a esta data
                    events = []
                    if data_pipeline:
                        # Janela de 30 dias antes da data da posição
                        from_date = curr.timestamp - datetime.timedelta(days=30)
                        to_date = curr.timestamp
                        events = data_pipeline.load_career_events(
                            person_id, from_date, to_date
                        )
                    
                    # Se não encontrou eventos ou não tem data_pipeline,
                    # criar um trigger genérico
                    if not events:
                        trigger = AccelerationTrigger(
                            timestamp=curr.timestamp,
                            event_type="Aceleração Detectada",
                            description="Aceleração significativa detectada sem evento associado",
                            impact_description=f"Aumento de {local_velocity/avg_velocity:.1f}x na velocidade de evolução",
                            impact_value=local_velocity,
                            position_before=prev,
                            position_after=curr
                        )
                        triggers.append(trigger)
                    else:
                        # Criar um trigger para cada evento encontrado
                        for event in events:
                            event_type = event.get('tipo_evento', 'Evento Desconhecido')
                            description = event.get('detalhes', 'Sem detalhes disponíveis')
                            
                            # Mapear tipos de evento para descrições de impacto
                            impact_descriptions = {
                                'promotion': 'Promoção acelerou significativamente a trajetória',
                                'lateral_move': 'Movimentação lateral trouxe nova perspectiva e aceleração',
                                'role_change': 'Mudança de função trouxe novos desafios e crescimento',
                                'skill_acquisition': 'Aquisição de nova habilidade impulsionou o desenvolvimento',
                                'certification': 'Certificação formalizou competências e abriu novas oportunidades',
                                'project': 'Projeto desafiador acelerou o desenvolvimento',
                                'training': 'Treinamento específico produziu resultados tangíveis',
                                'mentoring': 'Relação de mentoria trouxe insights transformadores'
                            }
                            
                            impact = impact_descriptions.get(
                                event_type, 'Evento coincide com aceleração significativa'
                            )
                            
                            trigger = AccelerationTrigger(
                                timestamp=datetime.datetime.fromisoformat(event.get('data', str(curr.timestamp))),
                                event_type=event_type,
                                description=description,
                                impact_description=impact,
                                impact_value=local_velocity,
                                position_before=prev,
                                position_after=curr
                            )
                            triggers.append(trigger)
        
        return triggers
    
    def generate_future_projection(
        self, positions: List[MatrixPosition], 
        movement_vector: Optional[MovementVector],
        acceleration_triggers: List[AccelerationTrigger],
        quarters_ahead: int = 4
    ) -> Optional[FutureProjection]:
        """
        Gera projeção futura baseada na trajetória histórica.
        
        Args:
            positions: Lista ordenada de posições históricas
            movement_vector: Vetor de movimento calculado
            acceleration_triggers: Gatilhos de aceleração identificados
            quarters_ahead: Número de trimestres para projetar
            
        Returns:
            Projeção futura ou None se não houver dados suficientes
        """
        if not positions or not movement_vector:
            return None
            
        # Última posição conhecida
        last_position = positions[-1]
        
        # Projetar posições futuras
        projected_positions = []
        
        # Data da última posição
        last_date = last_position.timestamp
        
        # Calcular peso dos gatilhos recentes (quanto mais recente, maior impacto)
        trigger_weights = []
        for trigger in acceleration_triggers:
            # Calcular dias desde o gatilho
            days_since = (last_date - trigger.timestamp).days
            if days_since <= 0:
                days_since = 1
            
            # Peso inversamente proporcional ao tempo (mais recente = mais peso)
            weight = 365 / days_since if days_since <= 365 else 0
            trigger_weights.append((trigger, weight))
        
        # Ordenar por peso
        trigger_weights.sort(key=lambda x: x[1], reverse=True)
        
        # Parâmetros de ajuste da curva de projeção
        # Determinam o quanto a projeção é afetada por acelerações recentes
        acceleration_factor = 1.0
        if trigger_weights:
            # Calcular o fator de aceleração baseado nos gatilhos recentes
            top_triggers = trigger_weights[:min(3, len(trigger_weights))]
            acceleration_factor = 1.0 + sum(w/10 for _, w in top_triggers) / len(top_triggers)
        
        # Fator de decaimento - a velocidade tende a reduzir ao longo do tempo
        decay_factor = 0.95
        
        # Confiança inicial da projeção
        confidence = min(0.9, 0.5 + (len(positions) / 20))
        
        # Confiança diminui para cada trimestre projetado
        confidence_decay = 0.15
        
        # Ângulo e velocidade iniciais (do vetor de movimento)
        angle = movement_vector.direction_radians
        velocity = movement_vector.velocity * acceleration_factor
        
        # Calcular projeções para cada trimestre
        for i in range(quarters_ahead):
            # Calcular nova data (trimestre)
            new_date = last_date + datetime.timedelta(days=90 * (i + 1))
            
            # Calcular componentes de deslocamento
            perf_increment = velocity * math.cos(angle) * 90  # 90 dias
            pot_increment = velocity * math.sin(angle) * 90
            
            # Calcular nova posição
            new_perf = min(10, max(0, last_position.performance + perf_increment))
            new_pot = min(10, max(0, last_position.potential + pot_increment))
            
            # Criar nova posição
            new_position = MatrixPosition(
                performance=new_perf,
                potential=new_pot,
                timestamp=new_date,
                source_data={
                    "projected": True,
                    "based_on": f"Posição em {last_date.strftime('%Y-%m-%d')}",
                    "confidence": confidence - (i * confidence_decay)
                }
            )
            
            projected_positions.append(new_position)
            
            # Atualizar a velocidade (diminui com o tempo a menos que haja gatilhos recentes)
            velocity *= decay_factor
            
            # A última posição projetada se torna a base para a próxima
            last_position = new_position
        
        # Calcular nível de confiança global da projeção
        confidence_level = confidence - (quarters_ahead * confidence_decay / 2)
        confidence_level = max(0.1, min(0.9, confidence_level))
        
        # Gerar intervenções recomendadas baseadas na trajetória
        recommended_interventions = self._generate_recommended_interventions(
            positions, movement_vector, acceleration_triggers, projected_positions
        )
        
        # Gerar explicação
        rationale = self._generate_projection_rationale(
            positions, movement_vector, acceleration_triggers, projected_positions
        )
        
        return FutureProjection(
            projected_positions=projected_positions,
            confidence_level=confidence_level,
            projection_rationale=rationale,
            recommended_interventions=recommended_interventions
        )
    
    def _generate_recommended_interventions(
        self, positions: List[MatrixPosition], 
        movement_vector: MovementVector,
        acceleration_triggers: List[AccelerationTrigger],
        projected_positions: List[MatrixPosition]
    ) -> List[Dict[str, Any]]:
        """
        Gera intervenções recomendadas baseadas na trajetória.
        
        Args:
            positions: Lista ordenada de posições históricas
            movement_vector: Vetor de movimento calculado
            acceleration_triggers: Gatilhos de aceleração identificados
            projected_positions: Posições projetadas
            
        Returns:
            Lista de intervenções recomendadas
        """
        interventions = []
        
        # Extrair informações principais
        current = positions[-1]
        quadrant = current.quadrant
        perf_trajectory = "crescente" if movement_vector.performance_delta > 0 else \
                          "estável" if abs(movement_vector.performance_delta) < 0.3 else "decrescente"
        pot_trajectory = "crescente" if movement_vector.potential_delta > 0 else \
                         "estável" if abs(movement_vector.potential_delta) < 0.3 else "decrescente"
        
        # Analisar gatilhos de aceleração para entender o que funcionou
        effective_triggers = [t for t in acceleration_triggers 
                             if t.impact_value > 0.5]
        
        # Mapa de intervenções por quadrante
        # Cada quadrante tem intervenções específicas
        quadrant_interventions = {
            (0, 0): [  # Baixo Desempenho / Baixo Potencial
                {
                    "title": "Programa de Recuperação de Desempenho",
                    "description": "Estruturar plano detalhado com metas claras e curto prazo, com checkpoints frequentes.",
                    "estimated_impact": "Alto em desempenho, moderado em potencial"
                },
                {
                    "title": "Reavaliação de Fit na Função",
                    "description": "Avaliar se a pessoa está na posição adequada ao seu perfil e habilidades.",
                    "estimated_impact": "Transformador para ambas dimensões"
                },
                {
                    "title": "Mentoria Técnica Intensiva",
                    "description": "Acompanhamento diário por profissional sênior para identificar e corrigir gaps.",
                    "estimated_impact": "Alto em desempenho, moderado em potencial"
                }
            ],
            (0, 1): [  # Baixo Desempenho / Médio Potencial
                {
                    "title": "Investigação de Barreiras",
                    "description": "Diagnóstico aprofundado de fatores que impedem a realização do potencial.",
                    "estimated_impact": "Alto em desempenho, baixo em potencial"
                },
                {
                    "title": "Redesenho de Responsabilidades",
                    "description": "Ajustar escopo para maior alinhamento com pontos fortes da pessoa.",
                    "estimated_impact": "Alto em desempenho, moderado em potencial"
                },
                {
                    "title": "Projeto de Recuperação",
                    "description": "Designar projeto de impacto, mas bem estruturado, para recuperar confiança.",
                    "estimated_impact": "Moderado em ambas dimensões"
                }
            ],
            (0, 2): [  # Baixo Desempenho / Alto Potencial
                {
                    "title": "Realocação Estratégica",
                    "description": "Movimentação para função que aproveite melhor o alto potencial identificado.",
                    "estimated_impact": "Transformador para desempenho"
                },
                {
                    "title": "Gap Analysis e Plano de Desenvolvimento",
                    "description": "Mapear lacunas específicas que impedem a expressão do potencial.",
                    "estimated_impact": "Alto em desempenho, moderado em potencial"
                },
                {
                    "title": "Mentorias Cruzadas",
                    "description": "Combinar mentoria técnica e comportamental para visão holística.",
                    "estimated_impact": "Alto em desempenho, moderado em potencial"
                }
            ],
            (1, 0): [  # Médio Desempenho / Baixo Potencial
                {
                    "title": "Plano de Especialização",
                    "description": "Investir no desenvolvimento técnico aprofundado na área atual.",
                    "estimated_impact": "Moderado em desempenho, baixo em potencial"
                },
                {
                    "title": "Estabilização de Responsabilidades",
                    "description": "Definir escopo claro e estável para maximizar contribuição.",
                    "estimated_impact": "Moderado em desempenho, baixo em potencial"
                },
                {
                    "title": "Reconhecimento Técnico",
                    "description": "Criar mecanismos para valorizar contribuições técnicas específicas.",
                    "estimated_impact": "Moderado em desempenho, baixo em potencial"
                }
            ],
            (1, 1): [  # Médio Desempenho / Médio Potencial
                {
                    "title": "Diversificação de Experiências",
                    "description": "Oferecer variedade de projetos para identificar áreas de maior aptidão.",
                    "estimated_impact": "Moderado em ambas dimensões"
                },
                {
                    "title": "Desafios Incrementais",
                    "description": "Aumentar gradualmente a complexidade dos desafios e responsabilidades.",
                    "estimated_impact": "Moderado em ambas dimensões"
                },
                {
                    "title": "Treinamentos Específicos",
                    "description": "Investir em formação para preencher gaps técnicos identificados.",
                    "estimated_impact": "Moderado em desempenho, moderado em potencial"
                }
            ],
            (1, 2): [  # Médio Desempenho / Alto Potencial
                {
                    "title": "Aceleração de Desenvolvimento",
                    "description": "Programa estruturado com exposição a projetos estratégicos.",
                    "estimated_impact": "Alto em desempenho, moderado em potencial"
                },
                {
                    "title": "Mentoria Executiva",
                    "description": "Acompanhamento por líder sênior com foco em liderança e gestão.",
                    "estimated_impact": "Alto em ambas dimensões"
                },
                {
                    "title": "Protagonismo em Projetos Estratégicos",
                    "description": "Atribuir responsabilidade significativa em iniciativas de alta visibilidade.",
                    "estimated_impact": "Alto em desempenho, moderado em potencial"
                }
            ],
            (2, 0): [  # Alto Desempenho / Baixo Potencial
                {
                    "title": "Solidificação de Expertise",
                    "description": "Investir na construção de reputação como referência técnica na área.",
                    "estimated_impact": "Moderado em desempenho, baixo em potencial"
                },
                {
                    "title": "Programa de Mentoria Reversa",
                    "description": "Estruturar como a pessoa pode multiplicar seu conhecimento técnico.",
                    "estimated_impact": "Baixo em desempenho, moderado em potencial"
                },
                {
                    "title": "Carreira em Y",
                    "description": "Estruturar caminho de carreira técnica com reconhecimento e visibilidade.",
                    "estimated_impact": "Moderado em desempenho, baixo em potencial"
                }
            ],
            (2, 1): [  # Alto Desempenho / Médio Potencial
                {
                    "title": "Expansão de Responsabilidades",
                    "description": "Ampliar gradualmente o escopo e complexidade das atribuições.",
                    "estimated_impact": "Moderado em desempenho, alto em potencial"
                },
                {
                    "title": "Liderança de Projetos Complexos",
                    "description": "Atribuir responsabilidade por projetos multidisciplinares.",
                    "estimated_impact": "Moderado em desempenho, alto em potencial"
                },
                {
                    "title": "Exposição Estratégica",
                    "description": "Criar oportunidades de exposição a contextos estratégicos e liderança sênior.",
                    "estimated_impact": "Baixo em desempenho, alto em potencial"
                }
            ],
            (2, 2): [  # Alto Desempenho / Alto Potencial
                {
                    "title": "Programa de Desenvolvimento Acelerado",
                    "description": "Estruturar experiências diversificadas com crescente complexidade e escopo.",
                    "estimated_impact": "Alto em ambas dimensões"
                },
                {
                    "title": "Exposição Executiva",
                    "description": "Criar oportunidades de interação e aprendizado com liderança executiva.",
                    "estimated_impact": "Moderado em desempenho, alto em potencial"
                },
                {
                    "title": "Rotação para Áreas Estratégicas",
                    "description": "Planejar movimentações que exponham a diferentes contextos do negócio.",
                    "estimated_impact": "Alto em ambas dimensões"
                }
            ]
        }
        
        # Selecionar intervenções do quadrante atual
        default_interventions = quadrant_interventions.get(quadrant, [])
        
        # Ajustar baseado na trajetória
        if perf_trajectory == "decrescente":
            interventions.append({
                "title": "Investigação de Queda de Desempenho",
                "description": "Análise detalhada dos fatores contribuindo para a redução de desempenho.",
                "estimated_impact": "Alto em desempenho, baixo em potencial"
            })
        
        if pot_trajectory == "decrescente":
            interventions.append({
                "title": "Realinhamento de Expectativas e Propósito",
                "description": "Diálogo estruturado para reconexão com propósito e motivação intrínseca.",
                "estimated_impact": "Baixo em desempenho, alto em potencial"
            })
        
        # Analisar os gatilhos efetivos para recomendar mais do que funcionou
        trigger_types = [t.event_type for t in effective_triggers]
        
        if "promotion" in trigger_types or "role_change" in trigger_types:
            interventions.append({
                "title": "Redesenho de Escopo",
                "description": "Ajustar responsabilidades para maximizar áreas de maior impacto.",
                "estimated_impact": "Alto em desempenho, moderado em potencial"
            })
            
        if "skill_acquisition" in trigger_types or "training" in trigger_types:
            interventions.append({
                "title": "Aprofundamento Técnico Específico",
                "description": "Investir em capacitação avançada nas áreas que demonstraram maior impacto.",
                "estimated_impact": "Alto em desempenho, moderado em potencial"
            })
            
        if "project" in trigger_types:
            interventions.append({
                "title": "Projeto Desafiador Estratégico",
                "description": "Atribuir responsabilidade em projeto com alto impacto organizacional.",
                "estimated_impact": "Alto em ambas dimensões"
            })
            
        if "mentoring" in trigger_types:
            interventions.append({
                "title": "Expansão de Rede de Mentoria",
                "description": "Estruturar mentoria com múltiplos mentores em áreas complementares.",
                "estimated_impact": "Moderado em ambas dimensões"
            })
        
        # Combinar intervenções específicas com as padrão do quadrante
        # e garantir que temos pelo menos 3 intervenções
        while len(interventions) < 3 and default_interventions:
            interventions.append(default_interventions.pop(0))
        
        # Limitar a 5 intervenções no máximo
        return interventions[:5]
    
    def _generate_projection_rationale(
        self, positions: List[MatrixPosition], 
        movement_vector: MovementVector,
        acceleration_triggers: List[AccelerationTrigger],
        projected_positions: List[MatrixPosition]
    ) -> str:
        """
        Gera explicação para a projeção futura.
        
        Args:
            positions: Lista ordenada de posições históricas
            movement_vector: Vetor de movimento calculado
            acceleration_triggers: Gatilhos de aceleração identificados
            projected_positions: Posições projetadas
            
        Returns:
            Explicação da projeção
        """
        # Construir explicação
        rationale_parts = []
        
        # Explicar base histórica
        num_positions = len(positions)
        timespan_days = (positions[-1].timestamp - positions[0].timestamp).days
        timespan_months = round(timespan_days / 30)
        
        rationale_parts.append(
            f"Projeção baseada em {num_positions} avaliações ao longo de {timespan_months} meses. "
        )
        
        # Explicar tendência de movimento
        direction = movement_vector.direction_degrees
        if 45 <= direction <= 135:
            direction_text = "prioritariamente em potencial"
        elif 225 <= direction <= 315:
            direction_text = "com redução preocupante de potencial"
        elif 135 < direction < 225:
            direction_text = "com redução preocupante de desempenho"
        else:
            direction_text = "prioritariamente em desempenho"
            
        velocity = movement_vector.velocity
        if velocity > 1.0:
            velocity_text = "acelerada"
        elif velocity > 0.5:
            velocity_text = "consistente"
        elif velocity > 0:
            velocity_text = "lenta"
        else:
            velocity_text = "estagnada ou regressiva"
            
        rationale_parts.append(
            f"A trajetória atual mostra evolução {velocity_text} {direction_text}. "
        )
        
        # Explicar gatilhos
        if acceleration_triggers:
            trigger_types = [t.event_type for t in acceleration_triggers]
            rationale_parts.append(
                f"Foram identificados {len(acceleration_triggers)} gatilhos de aceleração, "
                f"principalmente relacionados a {', '.join(set(trigger_types)[:3])}. "
            )
        else:
            rationale_parts.append(
                "Não foram identificados gatilhos específicos de aceleração no período analisado. "
            )
        
        # Explicar projeção
        first_proj = projected_positions[0]
        last_proj = projected_positions[-1]
        
        proj_perf_delta = last_proj.performance - positions[-1].performance
        proj_pot_delta = last_proj.potential - positions[-1].potential
        
        if proj_perf_delta > 0 and proj_pot_delta > 0:
            proj_text = "crescimento em ambas dimensões"
        elif proj_perf_delta > 0:
            proj_text = "crescimento principalmente em desempenho"
        elif proj_pot_delta > 0:
            proj_text = "crescimento principalmente em potencial"
        else:
            proj_text = "estagnação ou retrocesso"
            
        rationale_parts.append(
            f"A projeção para os próximos {len(projected_positions)} trimestres indica {proj_text}."
        )
        
        return " ".join(rationale_parts) 