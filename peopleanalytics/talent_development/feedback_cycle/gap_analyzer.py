"""
Analisador de gaps de feedback para identificação de áreas de desenvolvimento.

Este módulo identifica e quantifica diferenças entre autopercepção e feedback
externo, permitindo identificar pontos cegos no desenvolvimento profissional.
"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import datetime
import statistics


@dataclass
class FeedbackGap:
    """Representa um gap identificado em uma competência específica."""
    competency: str
    self_score: Optional[float]
    external_avg: float
    gap_value: float  # Diferença numérica entre autoavaliação e média externa
    gap_percentage: float  # Gap como percentual da escala total
    feedback_count: int  # Número de feedbacks externos analisados
    confidence: float  # Confiança estatística no gap (0-1)
    

class FeedbackGapAnalyzer:
    """
    Analisa dados de feedback para identificar gaps entre autopercepção
    e percepção externa, permitindo foco em áreas de desenvolvimento.
    
    Funcionalidades:
    - Cálculo de gaps por competência
    - Análise de confiabilidade estatística
    - Priorização de gaps para desenvolvimento
    - Identificação de tendências temporais nos gaps
    """
    
    def __init__(self):
        """Inicializa o analisador de gaps de feedback."""
        self.scale_min = 1.0  # Mínimo da escala de avaliação
        self.scale_max = 5.0  # Máximo da escala de avaliação
        self.scale_range = self.scale_max - self.scale_min
        
    def analyze_gaps(self, 
                    feedback_items: List[Dict[str, Any]],
                    competencies: Optional[List[str]] = None) -> Dict[str, FeedbackGap]:
        """
        Analisa uma lista de itens de feedback para identificar gaps.
        
        Args:
            feedback_items: Lista de itens de feedback
            competencies: Lista de competências a considerar (opcional)
            
        Returns:
            Dicionário de gaps por competência
        """
        # Agrupar feedback por competência
        by_competency = {}
        
        for item in feedback_items:
            competency = item.get('competency', 'general')
            
            if competencies and competency not in competencies:
                continue
                
            if competency not in by_competency:
                by_competency[competency] = {
                    'self': [],
                    'external': []
                }
                
            score = item.get('score', 0)
            
            if item.get('feedback_type') == 'self':
                by_competency[competency]['self'].append(score)
            else:
                by_competency[competency]['external'].append(score)
        
        # Calcular gaps para cada competência
        gaps = {}
        
        for competency, data in by_competency.items():
            self_scores = data['self']
            external_scores = data['external']
            
            # Só calcular gap se tivermos ambos tipos de feedback
            if external_scores:  # Sempre calcular se tiver feedback externo
                # Calcular médias
                self_score = statistics.mean(self_scores) if self_scores else None
                external_avg = statistics.mean(external_scores)
                
                # Calcular gap
                gap_value = (self_score or external_avg) - external_avg
                gap_percentage = (gap_value / self.scale_range) * 100
                
                # Calcular confiança baseada no número de feedbacks externos
                # e desvio padrão (se disponível)
                confidence = min(1.0, len(external_scores) / 5)  # Máximo com 5+ feedbacks
                
                if len(external_scores) > 1:
                    try:
                        std_dev = statistics.stdev(external_scores)
                        # Menor desvio padrão = maior confiança
                        std_confidence = 1.0 - (std_dev / self.scale_range)
                        confidence = (confidence + std_confidence) / 2  # Média das duas confiança
                    except statistics.StatisticsError:
                        pass  # Ignorar erros de cálculo
                
                # Criar objeto de gap
                gap = FeedbackGap(
                    competency=competency,
                    self_score=self_score,
                    external_avg=external_avg,
                    gap_value=gap_value,
                    gap_percentage=gap_percentage,
                    feedback_count=len(external_scores),
                    confidence=confidence
                )
                
                gaps[competency] = gap
        
        return gaps
    
    def prioritize_gaps(self, gaps: Dict[str, FeedbackGap]) -> List[Tuple[str, float]]:
        """
        Prioriza gaps para desenvolvimento com base na magnitude e confiança.
        
        Args:
            gaps: Dicionário de gaps por competência
            
        Returns:
            Lista de tuplas (competência, score de prioridade) ordenada por prioridade
        """
        if not gaps:
            return []
            
        # Calcular score de prioridade para cada gap
        # Score = |gap_value| * confidence
        priorities = []
        
        for competency, gap in gaps.items():
            priority_score = abs(gap.gap_value) * gap.confidence
            priorities.append((competency, priority_score))
            
        # Ordenar por prioridade (maior primeiro)
        return sorted(priorities, key=lambda x: x[1], reverse=True)
    
    def analyze_gap_trends(self, 
                        historical_gaps: Dict[datetime.datetime, Dict[str, FeedbackGap]],
                        competencies: Optional[List[str]] = None) -> Dict[str, List[Tuple[datetime.datetime, float]]]:
        """
        Analisa tendências nos gaps ao longo do tempo.
        
        Args:
            historical_gaps: Dicionário de gaps por data
            competencies: Lista de competências a considerar (opcional)
            
        Returns:
            Dicionário com tendências de gap por competência
        """
        trends = {}
        
        # Ordenar datas
        sorted_dates = sorted(historical_gaps.keys())
        
        # Para cada competência, extrair valores de gap ao longo do tempo
        all_competencies = set()
        for date_gaps in historical_gaps.values():
            all_competencies.update(date_gaps.keys())
            
        # Filtrar competências se necessário
        if competencies:
            all_competencies = [c for c in all_competencies if c in competencies]
            
        # Construir tendências
        for competency in all_competencies:
            trends[competency] = []
            
            for date in sorted_dates:
                date_gaps = historical_gaps[date]
                if competency in date_gaps:
                    gap_value = date_gaps[competency].gap_value
                    trends[competency].append((date, gap_value))
        
        return trends
    
    def get_development_recommendations(self, 
                                      gaps: Dict[str, FeedbackGap], 
                                      threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Gera recomendações de desenvolvimento com base nos gaps identificados.
        
        Args:
            gaps: Dicionário de gaps por competência
            threshold: Limite mínimo de gap para gerar recomendações
            
        Returns:
            Lista de recomendações
        """
        recommendations = []
        
        # Priorizar gaps
        priorities = self.prioritize_gaps(gaps)
        
        for competency, priority in priorities:
            gap = gaps[competency]
            
            # Só considerar gaps significativos e com confiança mínima
            if abs(gap.gap_value) < threshold or gap.confidence < 0.5:
                continue
                
            recommendation = {
                'competency': competency,
                'gap_value': gap.gap_value,
                'confidence': gap.confidence,
                'priority': priority
            }
            
            # Adicionar recomendação específica com base na direção do gap
            if gap.self_score is None:
                recommendation['type'] = 'missing_self_assessment'
                recommendation['message'] = f"Realize uma autoavaliação em {competency} para identificar pontos cegos."
            elif gap.gap_value > 0:
                recommendation['type'] = 'overestimation'
                recommendation['message'] = f"Busque feedback adicional sobre {competency} para alinhar sua percepção."
            else:
                recommendation['type'] = 'underestimation'
                recommendation['message'] = f"Reconheça suas forças em {competency} e construa autoconfiança nesta área."
                
            recommendations.append(recommendation)
            
        return recommendations 