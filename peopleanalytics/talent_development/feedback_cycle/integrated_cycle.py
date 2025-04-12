"""
Implementação do Ciclo de Feedback Integrado ao Desenvolvimento.

Este módulo constrói um sistema completo que transforma feedback em trilhas
de desenvolvimento concretas e monitoráveis.
"""
import datetime
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from pathlib import Path

from peopleanalytics.data_pipeline import DataPipeline
from peopleanalytics.talent_development.feedback_cycle.learning_path import PersonalizedLearningPath
from peopleanalytics.talent_development.feedback_cycle.gap_analyzer import FeedbackGapAnalyzer
from peopleanalytics.talent_development.feedback_cycle.bias_detector import CognitiveBiasDetector
from peopleanalytics.talent_development.feedback_cycle.progress_tracker import ProgressTracker


@dataclass
class FeedbackItem:
    """Representa um item individual de feedback."""
    feedback_id: str
    person_id: str
    provider_id: Optional[str]  # Pode ser anônimo
    feedback_type: str  # 'manager', 'peer', 'self', 'direct_report', '360'
    competency: str
    score: float  # Escala 1-5
    text: str
    timestamp: datetime.datetime
    context: Dict[str, Any]  # Metadados adicionais
    
    @property
    def is_self_assessment(self) -> bool:
        """Verifica se este é um feedback de autoavaliação."""
        return self.feedback_type == 'self'


@dataclass
class CompetencyAssessment:
    """Avaliação consolidada de uma competência específica."""
    competency: str
    self_score: Optional[float]
    external_scores: List[float]
    external_avg: float
    gap: float  # Diferença entre autoavaliação e média externa
    feedback_texts: List[str]
    
    @property
    def has_bias(self) -> bool:
        """Verifica se há um viés significativo na autopercepção."""
        # Se não tem autoavaliação, não podemos determinar viés
        if self.self_score is None:
            return False
        
        # Definimos viés significativo como gap > 1.0 na escala 1-5
        return abs(self.gap) > 1.0
    
    @property
    def bias_direction(self) -> str:
        """Retorna a direção do viés, se existir."""
        if not self.has_bias:
            return "neutro"
        
        if self.gap > 0:
            return "superestimação"  # Autoavaliação maior que feedback externo
        else:
            return "subestimação"  # Autoavaliação menor que feedback externo


class IntegratedFeedbackCycle:
    """
    Ciclo de Feedback Integrado que transforma feedback em desenvolvimento.
    
    Funcionalidades:
    - Consolidação de múltiplas fontes de feedback
    - Identificação de gaps entre autopercepção e feedback externo
    - Detecção de vieses cognitivos
    - Geração de trilhas de aprendizado personalizadas
    - Acompanhamento de progresso objetivo
    """
    
    def __init__(self, data_pipeline: Optional[DataPipeline] = None):
        """
        Inicializa o ciclo de feedback integrado.
        
        Args:
            data_pipeline: Pipeline de dados opcional para carregar dados existentes
        """
        self.data_pipeline = data_pipeline
        self.feedback_data = {}  # person_id -> List[FeedbackItem]
        self.assessments = {}  # person_id -> Dict[competency, CompetencyAssessment]
        
        # Componentes do ciclo
        self.gap_analyzer = FeedbackGapAnalyzer()
        self.bias_detector = CognitiveBiasDetector()
        self.learning_path_generator = PersonalizedLearningPath()
        self.progress_tracker = ProgressTracker()
    
    def load_feedback_data(self, person_id: str) -> List[FeedbackItem]:
        """
        Carrega dados de feedback para uma pessoa.
        
        Args:
            person_id: ID da pessoa
            
        Returns:
            Lista de itens de feedback
        """
        if self.data_pipeline is None:
            return []
        
        # Se já temos os dados em cache, retorna diretamente
        if person_id in self.feedback_data:
            return self.feedback_data[person_id]
        
        # Carregar dados do pipeline
        feedback_records = self.data_pipeline.load_feedback(person_id)
        
        # Converter para objetos FeedbackItem
        feedback_items = []
        for record in feedback_records:
            item = FeedbackItem(
                feedback_id=record.get('id', f"fb_{len(feedback_items)}"),
                person_id=person_id,
                provider_id=record.get('provider_id'),
                feedback_type=record.get('type', 'unknown'),
                competency=record.get('competency', 'general'),
                score=float(record.get('score', 0)),
                text=record.get('text', ''),
                timestamp=datetime.datetime.fromisoformat(record.get('timestamp', datetime.datetime.now().isoformat())),
                context=record.get('context', {})
            )
            feedback_items.append(item)
        
        # Ordenar por data
        feedback_items.sort(key=lambda x: x.timestamp)
        
        # Armazenar no cache
        self.feedback_data[person_id] = feedback_items
        
        return feedback_items
    
    def add_feedback(self, 
                    person_id: str, 
                    provider_id: Optional[str], 
                    feedback_type: str,
                    competency: str,
                    score: float,
                    text: str,
                    context: Optional[Dict[str, Any]] = None) -> FeedbackItem:
        """
        Adiciona um novo feedback para uma pessoa.
        
        Args:
            person_id: ID da pessoa que recebe o feedback
            provider_id: ID de quem deu o feedback (None se anônimo)
            feedback_type: Tipo de feedback ('manager', 'peer', 'self', etc)
            competency: Competência avaliada
            score: Pontuação (escala 1-5)
            text: Texto descritivo do feedback
            context: Informações adicionais sobre o contexto do feedback
            
        Returns:
            Novo item de feedback criado
        """
        # Validar score
        if not 1 <= score <= 5:
            raise ValueError("Score deve estar entre 1 e 5")
        
        # Criar novo item
        feedback_id = f"fb_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{person_id}"
        
        new_item = FeedbackItem(
            feedback_id=feedback_id,
            person_id=person_id,
            provider_id=provider_id,
            feedback_type=feedback_type,
            competency=competency,
            score=score,
            text=text,
            timestamp=datetime.datetime.now(),
            context=context or {}
        )
        
        # Adicionar ao cache
        if person_id not in self.feedback_data:
            self.feedback_data[person_id] = []
        
        self.feedback_data[person_id].append(new_item)
        
        # Salvar no pipeline se disponível
        if self.data_pipeline:
            feedback_record = {
                'id': feedback_id,
                'person_id': person_id,
                'provider_id': provider_id,
                'type': feedback_type,
                'competency': competency,
                'score': score,
                'text': text,
                'timestamp': new_item.timestamp.isoformat(),
                'context': context or {}
            }
            
            self.data_pipeline.save_feedback(feedback_record)
        
        # Invalidar avaliações em cache, pois temos novos dados
        if person_id in self.assessments:
            del self.assessments[person_id]
        
        return new_item
    
    def get_competency_assessment(self, person_id: str, competency: str,
                                 timespan_days: int = 365) -> Optional[CompetencyAssessment]:
        """
        Obtém a avaliação consolidada de uma competência específica.
        
        Args:
            person_id: ID da pessoa
            competency: Competência a ser avaliada
            timespan_days: Janela de tempo a considerar (em dias)
            
        Returns:
            Avaliação da competência ou None se dados insuficientes
        """
        # Carregar dados se necessário
        if person_id not in self.feedback_data:
            self.load_feedback_data(person_id)
        
        # Se não temos dados, retorna None
        if person_id not in self.feedback_data or not self.feedback_data[person_id]:
            return None
        
        # Filtrar feedback pela competência e período
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=timespan_days)
        
        relevant_items = [
            item for item in self.feedback_data[person_id]
            if item.competency == competency and item.timestamp >= cutoff_date
        ]
        
        if not relevant_items:
            return None
        
        # Separar autoavaliação do feedback externo
        self_feedback = [item for item in relevant_items if item.is_self_assessment]
        external_feedback = [item for item in relevant_items if not item.is_self_assessment]
        
        # Se não temos feedback externo, não podemos fazer uma avaliação completa
        if not external_feedback:
            return None
        
        # Calcular score de autoavaliação (mais recente, se houver múltiplos)
        self_score = None
        if self_feedback:
            self_feedback.sort(key=lambda x: x.timestamp, reverse=True)
            self_score = self_feedback[0].score
        
        # Calcular scores externos
        external_scores = [item.score for item in external_feedback]
        external_avg = sum(external_scores) / len(external_scores)
        
        # Calcular gap entre autoavaliação e feedback externo
        gap = (self_score - external_avg) if self_score is not None else 0
        
        # Coletar textos de feedback
        feedback_texts = [item.text for item in relevant_items if item.text.strip()]
        
        # Criar e retornar avaliação
        assessment = CompetencyAssessment(
            competency=competency,
            self_score=self_score,
            external_scores=external_scores,
            external_avg=external_avg,
            gap=gap,
            feedback_texts=feedback_texts
        )
        
        return assessment
    
    def analyze_all_competencies(self, person_id: str, 
                                timespan_days: int = 365) -> Dict[str, CompetencyAssessment]:
        """
        Analisa todas as competências para uma pessoa.
        
        Args:
            person_id: ID da pessoa
            timespan_days: Janela de tempo a considerar (em dias)
            
        Returns:
            Dicionário de competência -> avaliação
        """
        # Verificar cache
        if person_id in self.assessments:
            return self.assessments[person_id]
        
        # Carregar dados se necessário
        if person_id not in self.feedback_data:
            self.load_feedback_data(person_id)
        
        # Se não temos dados, retorna dicionário vazio
        if person_id not in self.feedback_data or not self.feedback_data[person_id]:
            return {}
        
        # Identificar todas as competências disponíveis
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=timespan_days)
        
        recent_feedback = [
            item for item in self.feedback_data[person_id]
            if item.timestamp >= cutoff_date
        ]
        
        competencies = set(item.competency for item in recent_feedback)
        
        # Analisar cada competência
        assessments = {}
        for competency in competencies:
            assessment = self.get_competency_assessment(
                person_id, competency, timespan_days
            )
            
            if assessment:
                assessments[competency] = assessment
        
        # Armazenar cache
        self.assessments[person_id] = assessments
        
        return assessments
    
    def identify_blindspots(self, person_id: str, 
                           timespan_days: int = 365) -> List[Dict[str, Any]]:
        """
        Identifica pontos cegos no autoconhecimento.
        
        Args:
            person_id: ID da pessoa
            timespan_days: Janela de tempo a considerar (em dias)
            
        Returns:
            Lista de pontos cegos identificados
        """
        assessments = self.analyze_all_competencies(person_id, timespan_days)
        
        # Filtrar para competências com gap significativo
        blindspots = []
        
        for competency, assessment in assessments.items():
            if assessment.has_bias:
                blindspot = {
                    "competency": competency,
                    "self_score": assessment.self_score,
                    "external_avg": assessment.external_avg,
                    "gap": assessment.gap,
                    "direction": assessment.bias_direction,
                    "feedback_examples": assessment.feedback_texts[:3]  # Até 3 exemplos
                }
                
                # Adicionar análise específica usando o detector de viés
                bias_analysis = self.bias_detector.analyze_bias(
                    assessment.self_score,
                    assessment.external_scores,
                    assessment.feedback_texts
                )
                
                blindspot.update(bias_analysis)
                
                blindspots.append(blindspot)
        
        # Ordenar por magnitude do gap (absoluto)
        blindspots.sort(key=lambda x: abs(x["gap"]), reverse=True)
        
        return blindspots
    
    def generate_learning_path(self, person_id: str, 
                              timespan_days: int = 365) -> Dict[str, Any]:
        """
        Gera uma trilha de aprendizado personalizada.
        
        Args:
            person_id: ID da pessoa
            timespan_days: Janela de tempo a considerar (em dias)
            
        Returns:
            Trilha de aprendizado personalizada
        """
        # Analisar todas as competências
        assessments = self.analyze_all_competencies(person_id, timespan_days)
        
        # Identificar pontos cegos
        blindspots = self.identify_blindspots(person_id, timespan_days)
        
        # Gerar trilha de aprendizado
        path = self.learning_path_generator.generate_path(
            person_id=person_id,
            competency_assessments=assessments,
            blindspots=blindspots,
            data_pipeline=self.data_pipeline
        )
        
        return path
    
    def track_progress(self, person_id: str, 
                     timespan_days: int = 365,
                     previous_timespan_days: int = 730) -> Dict[str, Any]:
        """
        Acompanha o progresso objetivo nas competências.
        
        Args:
            person_id: ID da pessoa
            timespan_days: Janela de tempo atual (em dias)
            previous_timespan_days: Janela de tempo anterior para comparação (em dias)
            
        Returns:
            Análise de progresso
        """
        # Analisar competências no período atual
        current_assessments = self.analyze_all_competencies(person_id, timespan_days)
        
        # Analisar competências no período anterior
        # Usamos um hack: temporariamente sobrescrevemos o cache, depois restauramos
        original_assessments = self.assessments.get(person_id, {})
        
        # Forçar recálculo para período anterior
        if person_id in self.assessments:
            del self.assessments[person_id]
            
        previous_assessments = self.analyze_all_competencies(
            person_id, previous_timespan_days
        )
        
        # Restaurar cache original
        self.assessments[person_id] = original_assessments
        
        # Rastrear progresso usando componente específico
        progress = self.progress_tracker.analyze_progress(
            person_id=person_id,
            current_assessments=current_assessments,
            previous_assessments=previous_assessments,
            data_pipeline=self.data_pipeline
        )
        
        return progress
    
    def generate_dashboard(self, person_id: str, 
                          output_path: Optional[Path] = None) -> Path:
        """
        Gera um dashboard completo do ciclo de feedback integrado.
        
        Args:
            person_id: ID da pessoa
            output_path: Caminho para salvar o dashboard (opcional)
            
        Returns:
            Caminho para o dashboard gerado
        """
        # Configurar caminho de saída
        if not output_path:
            output_dir = Path("output") / "feedback_cycle"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{person_id}_feedback_dashboard_{datetime.datetime.now().strftime('%Y%m%d')}.html"
        
        # Coletar dados para o dashboard
        assessments = self.analyze_all_competencies(person_id)
        blindspots = self.identify_blindspots(person_id)
        learning_path = self.generate_learning_path(person_id)
        progress = self.track_progress(person_id)
        
        # Gerar HTML
        html_content = self._generate_html_dashboard(
            person_id=person_id,
            assessments=assessments,
            blindspots=blindspots,
            learning_path=learning_path,
            progress=progress
        )
        
        # Salvar arquivo
        with open(output_path, 'w') as f:
            f.write(html_content)
            
        return output_path
    
    def _generate_html_dashboard(self, person_id: str,
                                assessments: Dict[str, CompetencyAssessment],
                                blindspots: List[Dict[str, Any]],
                                learning_path: Dict[str, Any],
                                progress: Dict[str, Any]) -> str:
        """
        Gera o HTML para o dashboard do ciclo de feedback.
        
        Args:
            person_id: ID da pessoa
            assessments: Avaliações de competências
            blindspots: Pontos cegos identificados
            learning_path: Trilha de aprendizado
            progress: Progresso objetivo
            
        Returns:
            HTML do dashboard
        """
        # Simplificado para implementação. Em produção, usar templates
        # e bibliotecas de visualização como Plotly, Bokeh ou D3.js
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ciclo de Feedback Integrado - {person_id}</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            color: #333; 
            line-height: 1.6;
        }}
        .dashboard {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            background: #f7f9fc; 
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        header {{ 
            background: linear-gradient(135deg, #2c3e50, #4ca1af);
            color: white;
            padding: 20px 30px;
        }}
        h1, h2, h3, h4 {{ margin-top: 0; }}
        .section {{ 
            padding: 20px 30px;
            margin-bottom: 20px;
            background: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        .competency {{ 
            margin-bottom: 15px; 
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
        }}
        .competency-header {{ 
            display: flex; 
            justify-content: space-between;
            align-items: center;
        }}
        .scores {{ 
            display: flex; 
            align-items: center; 
            gap: 15px;
        }}
        .score {{ 
            padding: 8px 12px;
            border-radius: 20px;
            font-weight: bold;
        }}
        .self-score {{ background: #e3f2fd; color: #0d47a1; }}
        .external-score {{ background: #f1f8e9; color: #33691e; }}
        .gap-score {{ 
            background: #ffebee; 
            color: #b71c1c;
            font-size: 0.9em;
        }}
        .positive-gap {{ 
            background: #fffde7; 
            color: #f57f17;
        }}
        .blindspot {{ 
            background: #fff8e1; 
            border-left: 4px solid #ffb300;
            padding: 15px;
            margin-bottom: 15px;
        }}
        .learning-module {{ 
            background: #e8f5e9; 
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 10px;
        }}
        .progress-item {{ 
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }}
        .progress-bar {{ 
            flex-grow: 1;
            height: 30px;
            background: #eceff1;
            border-radius: 15px;
            overflow: hidden;
            margin: 0 15px;
        }}
        .progress-value {{ 
            height: 100%;
            background: linear-gradient(90deg, #4caf50, #8bc34a);
        }}
        .negative-progress {{ 
            background: linear-gradient(90deg, #f44336, #ff9800);
        }}
        footer {{ 
            text-align: center;
            padding: 20px;
            color: #777;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <header>
            <h1>Ciclo de Feedback Integrado</h1>
            <p>Dashboard personalizado para: <strong>{person_id}</strong></p>
            <p>Data de geração: {datetime.datetime.now().strftime('%d/%m/%Y')}</p>
        </header>

        <div class="section">
            <h2>Avaliação de Competências</h2>
"""
        
        # Adicionar competências
        if assessments:
            for competency, assessment in assessments.items():
                gap_class = "positive-gap" if assessment.gap >= 0 else "gap-score"
                html += f"""
            <div class="competency">
                <div class="competency-header">
                    <h3>{competency}</h3>
                    <div class="scores">
"""
                if assessment.self_score is not None:
                    html += f'<div class="score self-score">Auto: {assessment.self_score:.1f}</div>'
                    
                html += f"""
                        <div class="score external-score">Externo: {assessment.external_avg:.1f}</div>
                        <div class="score {gap_class}">Gap: {assessment.gap:+.1f}</div>
                    </div>
                </div>
                <div class="feedback-examples">
"""
                
                if assessment.feedback_texts:
                    html += "<ul>"
                    for text in assessment.feedback_texts[:3]:  # Mostrar até 3 exemplos
                        html += f"<li>{text}</li>"
                    if len(assessment.feedback_texts) > 3:
                        html += f"<li>... e mais {len(assessment.feedback_texts) - 3} comentários</li>"
                    html += "</ul>"
                else:
                    html += "<p><em>Sem comentários de feedback</em></p>"
                    
                html += """
                </div>
            </div>"""
        else:
            html += "<p><em>Nenhuma competência avaliada no período</em></p>"
            
        # Adicionar pontos cegos
        html += """
        </div>

        <div class="section">
            <h2>Pontos Cegos Identificados</h2>
"""
        
        if blindspots:
            for spot in blindspots:
                html += f"""
            <div class="blindspot">
                <h3>{spot['competency']}</h3>
                <p><strong>Viés de {spot['direction']}</strong>: 
                   Você se avalia como <strong>{spot['self_score']:.1f}</strong>, 
                   enquanto a percepção externa é <strong>{spot['external_avg']:.1f}</strong>
                   (diferença de {spot['gap']:+.1f}).</p>
"""
                
                if 'pattern' in spot:
                    html += f"<p><strong>Padrão identificado:</strong> {spot['pattern']}</p>"
                    
                if 'recommendations' in spot:
                    html += "<p><strong>Recomendações:</strong></p><ul>"
                    for rec in spot['recommendations']:
                        html += f"<li>{rec}</li>"
                    html += "</ul>"
                    
                html += """
            </div>"""
        else:
            html += "<p><em>Nenhum ponto cego significativo identificado</em></p>"
        
        # Adicionar trilha de aprendizado
        html += """
        </div>

        <div class="section">
            <h2>Trilha de Aprendizado Personalizada</h2>
"""
        
        if learning_path and 'modules' in learning_path:
            for module in learning_path['modules']:
                html += f"""
            <div class="learning-module">
                <h3>{module['title']}</h3>
                <p>{module['description']}</p>
"""
                
                if 'activities' in module:
                    html += "<ol>"
                    for activity in module['activities']:
                        html += f"<li><strong>{activity['title']}</strong>: {activity['description']}</li>"
                    html += "</ol>"
                    
                if 'resources' in module:
                    html += "<p><strong>Recursos:</strong></p><ul>"
                    for resource in module['resources']:
                        html += f"<li>{resource['title']}: {resource['url'] if 'url' in resource else resource['description']}</li>"
                    html += "</ul>"
                    
                html += """
            </div>"""
        else:
            html += "<p><em>Nenhuma trilha de aprendizado disponível</em></p>"
        
        # Adicionar progresso
        html += """
        </div>

        <div class="section">
            <h2>Progresso Objetivo</h2>
"""
        
        if progress and 'competencies' in progress:
            for comp in progress['competencies']:
                progress_class = "" if comp['delta'] >= 0 else "negative-progress"
                progress_value = abs(comp['delta']) * 20  # 20% por ponto na escala 1-5
                progress_value = min(100, progress_value)  # Limitar a 100%
                
                html += f"""
            <div class="progress-item">
                <div>{comp['competency']}</div>
                <div class="progress-bar">
                    <div class="progress-value {progress_class}" style="width: {progress_value}%;"></div>
                </div>
                <div>{comp['delta']:+.1f}</div>
            </div>"""
            
            if 'summary' in progress:
                html += f"<p><strong>Resumo:</strong> {progress['summary']}</p>"
        else:
            html += "<p><em>Dados insuficientes para analisar progresso</em></p>"
        
        # Fechar o HTML
        html += """
        </div>

        <footer>
            <p>Este dashboard é gerado automaticamente pelo sistema de People Analytics.</p>
            <p>Os dados são confidenciais e devem ser tratados de acordo com as políticas da empresa.</p>
        </footer>
    </div>
</body>
</html>
"""
        
        return html 