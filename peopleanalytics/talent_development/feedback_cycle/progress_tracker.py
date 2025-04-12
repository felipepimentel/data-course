"""
Rastreador de progresso para acompanhar evolução das competências ao longo do tempo.

Monitora o desenvolvimento das competências com base em feedback contínuo,
fornecendo métricas objetivas de evolução.
"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import datetime
import statistics
import numpy as np
from scipy.stats import linregress


@dataclass
class ProgressMetric:
    """Métrica de progresso para uma competência específica."""
    competency: str
    baseline_score: float  # Score inicial
    current_score: float  # Score atual
    absolute_change: float  # Mudança absoluta
    percentage_change: float  # Mudança percentual
    trend_slope: float  # Inclinação da linha de tendência
    confidence: float  # Confiabilidade da medida (0-1)
    timespan_days: int  # Período de tempo analisado
    data_points: int  # Quantidade de pontos de dados utilizados


class ProgressTracker:
    """
    Rastreador de progresso que monitora a evolução das competências.
    
    Funcionalidades:
    - Cálculo de métricas de evolução
    - Análise de tendências
    - Detecção de plateaus e regressões
    - Visualização de progresso ao longo do tempo
    """
    
    def __init__(self):
        """Inicializa o rastreador de progresso."""
        pass
    
    def calculate_progress(self, 
                         timeline_data: Dict[datetime.datetime, Dict[str, float]],
                         competencies: Optional[List[str]] = None) -> Dict[str, ProgressMetric]:
        """
        Calcula métricas de progresso com base em dados históricos.
        
        Args:
            timeline_data: Dicionário com datas e scores por competência
            competencies: Lista de competências para analisar (opcional)
            
        Returns:
            Dicionário com métricas de progresso por competência
        """
        # Verificar se temos dados suficientes
        if len(timeline_data) < 2:
            return {}
            
        # Ordenar datas
        sorted_dates = sorted(timeline_data.keys())
        first_date = sorted_dates[0]
        last_date = sorted_dates[-1]
        
        # Calcular timespan em dias
        timespan_days = (last_date - first_date).days
        if timespan_days < 1:
            timespan_days = 1  # Evitar divisão por zero
        
        # Encontrar todas as competências se não foram especificadas
        if not competencies:
            competencies = set()
            for date_data in timeline_data.values():
                competencies.update(date_data.keys())
            competencies = list(competencies)
        
        # Calcular métricas para cada competência
        progress_metrics = {}
        
        for competency in competencies:
            # Coletar pontos de dados para esta competência
            data_points = []
            
            for date in sorted_dates:
                if competency in timeline_data[date]:
                    score = timeline_data[date][competency]
                    days_from_start = (date - first_date).days
                    data_points.append((days_from_start, score))
            
            # Precisamos de pelo menos 2 pontos para calcular progresso
            if len(data_points) < 2:
                continue
                
            # Extrair scores
            days, scores = zip(*data_points)
            
            # Calcular scores de referência
            baseline_score = scores[0]
            current_score = scores[-1]
            
            # Calcular mudanças
            absolute_change = current_score - baseline_score
            if baseline_score > 0:
                percentage_change = (absolute_change / baseline_score) * 100
            else:
                percentage_change = 0
            
            # Calcular tendência (regressão linear)
            if len(data_points) >= 3:
                try:
                    slope, intercept, r_value, p_value, std_err = linregress(days, scores)
                    # Normalizar slope para taxa por 30 dias
                    trend_slope = slope * 30
                    # Usar r² como medida de confiança
                    confidence = r_value ** 2
                except:
                    # Fallback se não puder calcular regressão
                    trend_slope = absolute_change / timespan_days * 30
                    confidence = 0.5
            else:
                # Com apenas 2 pontos, calcular a taxa de mudança simples
                trend_slope = absolute_change / timespan_days * 30
                confidence = 0.5  # Confiança moderada com poucos dados
            
            # Criar métrica de progresso
            metric = ProgressMetric(
                competency=competency,
                baseline_score=baseline_score,
                current_score=current_score,
                absolute_change=absolute_change,
                percentage_change=percentage_change,
                trend_slope=trend_slope,
                confidence=confidence,
                timespan_days=timespan_days,
                data_points=len(data_points)
            )
            
            progress_metrics[competency] = metric
        
        return progress_metrics
    
    def detect_plateaus(self, 
                      timeline_data: Dict[datetime.datetime, Dict[str, float]],
                      min_points: int = 3,
                      tolerance: float = 0.1) -> Dict[str, Any]:
        """
        Detecta plateaus no desenvolvimento de competências.
        
        Args:
            timeline_data: Dicionário com datas e scores por competência
            min_points: Número mínimo de pontos para detectar plateau
            tolerance: Variação máxima considerada como plateau
            
        Returns:
            Dicionário com informações sobre plateaus detectados
        """
        plateaus = {}
        
        # Precisamos de dados suficientes
        if len(timeline_data) < min_points:
            return plateaus
            
        # Ordenar datas
        sorted_dates = sorted(timeline_data.keys())
        
        # Encontrar todas as competências
        all_competencies = set()
        for date_data in timeline_data.values():
            all_competencies.update(date_data.keys())
        
        # Verificar cada competência
        for competency in all_competencies:
            # Coletar scores para esta competência
            scores = []
            
            for date in sorted_dates:
                if competency in timeline_data[date]:
                    scores.append(timeline_data[date][competency])
            
            # Precisamos de pontos suficientes
            if len(scores) < min_points:
                continue
                
            # Calcular variação nos últimos "min_points" pontos
            recent_scores = scores[-min_points:]
            min_score = min(recent_scores)
            max_score = max(recent_scores)
            
            # Verificar se a variação está dentro da tolerância
            if max_score - min_score <= tolerance:
                # Calcular duração do plateau
                plateau_start_idx = len(scores) - min_points
                plateau_start_date = sorted_dates[plateau_start_idx]
                plateau_duration = (sorted_dates[-1] - plateau_start_date).days
                
                plateaus[competency] = {
                    'start_date': plateau_start_date,
                    'duration_days': plateau_duration,
                    'score_range': (min_score, max_score),
                    'avg_score': sum(recent_scores) / len(recent_scores)
                }
        
        return plateaus
    
    def generate_recommendations(self, 
                               progress_metrics: Dict[str, ProgressMetric],
                               plateaus: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Gera recomendações com base nas métricas de progresso.
        
        Args:
            progress_metrics: Métricas de progresso por competência
            plateaus: Informações sobre plateaus detectados (opcional)
            
        Returns:
            Lista de recomendações para continuar o desenvolvimento
        """
        recommendations = []
        
        if not progress_metrics:
            return recommendations
            
        # Analisar progresso para cada competência
        for competency, metric in progress_metrics.items():
            recommendation = {
                'competency': competency,
                'current_score': metric.current_score,
                'absolute_change': metric.absolute_change,
                'percentage_change': metric.percentage_change
            }
            
            # Verificar se está em plateau
            if plateaus and competency in plateaus:
                plateau_info = plateaus[competency]
                recommendation['status'] = 'plateau'
                recommendation['plateau_duration'] = plateau_info['duration_days']
                recommendation['message'] = (
                    f"Desenvolvimento em {competency} estagnado há {plateau_info['duration_days']} dias. "
                    f"Considere mudar abordagem de aprendizado ou buscar desafios mais complexos."
                )
                
            # Verificar regressão (tendência negativa)
            elif metric.trend_slope < -0.1 and metric.confidence > 0.6:
                recommendation['status'] = 'regression'
                recommendation['message'] = (
                    f"Regressão detectada em {competency}. "
                    f"Revisite práticas anteriores e solicite feedback adicional."
                )
                
            # Verificar progresso lento
            elif 0 <= metric.trend_slope < 0.2:
                recommendation['status'] = 'slow_progress'
                recommendation['message'] = (
                    f"Progresso lento em {competency}. "
                    f"Considere intensificar práticas ou buscar novas abordagens de aprendizado."
                )
                
            # Progresso satisfatório
            elif metric.trend_slope >= 0.2:
                recommendation['status'] = 'good_progress'
                recommendation['message'] = (
                    f"Bom progresso em {competency}. "
                    f"Continue com as práticas atuais e considere compartilhar seu aprendizado."
                )
                
            # Caso não tenhamos tendência clara
            else:
                recommendation['status'] = 'undefined'
                recommendation['message'] = (
                    f"Progresso em {competency} não apresenta padrão claro. "
                    f"Considere aumentar frequência de feedback para melhor acompanhamento."
                )
                
            recommendations.append(recommendation)
        
        # Ordenar por status (priorizar regressões e plateaus)
        status_priority = {
            'regression': 0,
            'plateau': 1,
            'slow_progress': 2,
            'undefined': 3,
            'good_progress': 4
        }
        
        recommendations.sort(key=lambda x: status_priority.get(x['status'], 99))
        
        return recommendations
    
    def visualize_progress(self, 
                         timeline_data: Dict[datetime.datetime, Dict[str, float]],
                         competencies: List[str],
                         output_path: str = None):
        """
        Cria visualização do progresso para competências selecionadas.
        
        Args:
            timeline_data: Dicionário com datas e scores por competência
            competencies: Lista de competências para visualizar
            output_path: Caminho para salvar a visualização (opcional)
            
        Returns:
            Objeto de figura (implementação dependeria da biblioteca gráfica)
        """
        # Esta função teria a implementação completa com matplotlib ou similar
        # Aqui apenas retornamos um placeholder
        
        visualization = {
            "type": "progress_chart",
            "competencies": competencies,
            "data_points": len(timeline_data),
            "output_path": output_path
        }
        
        return visualization 