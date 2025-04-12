"""
Dashboard Holístico de Desenvolvimento de Talentos.

Integra dados de múltiplas fontes e módulos para fornecer uma visão
completa e multidimensional do desenvolvimento de colaboradores.
"""
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from pathlib import Path
import networkx as nx
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from peopleanalytics.data_pipeline import DataPipeline
from peopleanalytics.talent_development.predictive import PerformancePredictor
from peopleanalytics.talent_development.career_sim import CareerSimulator
from peopleanalytics.talent_development.matrix_9box import DynamicMatrix9Box
from peopleanalytics.talent_development.influence_network import InfluenceNetwork


@dataclass
class PersonSummary:
    """Resumo holístico de uma pessoa."""
    person_id: str
    name: str
    current_position: str
    performance_score: float
    potential_score: float
    nine_box_position: Tuple[int, int]  # (potencial, desempenho) em escala 1-3
    career_growth_score: float
    influence_score: float
    key_skills: Dict[str, float]
    development_areas: List[str]
    trends: Dict[str, List[float]]
    predictions: Dict[str, Any]
    network_centrality: float
    learning_velocity: float
    top_recommendations: List[str]


class HolisticDashboard:
    """
    Dashboard holístico integrando todas as dimensões de análise de talentos.
    
    Este módulo combina dados de todos os outros módulos para criar uma
    visualização unificada de alto nível do desenvolvimento, desempenho,
    potencial e trajetória de carreira dos colaboradores.
    """
    
    def __init__(self, 
                data_pipeline: Optional[DataPipeline] = None,
                performance_predictor: Optional[PerformancePredictor] = None,
                career_simulator: Optional[CareerSimulator] = None,
                matrix_9box: Optional[DynamicMatrix9Box] = None,
                influence_network: Optional[InfluenceNetwork] = None):
        """
        Inicializa o dashboard holístico.
        
        Args:
            data_pipeline: Pipeline de dados opcional
            performance_predictor: Preditor de performance opcional
            career_simulator: Simulador de carreira opcional
            matrix_9box: Matriz 9-box dinâmica opcional
            influence_network: Rede de influência opcional
        """
        self.data_pipeline = data_pipeline
        self.performance_predictor = performance_predictor
        self.career_simulator = career_simulator
        self.matrix_9box = matrix_9box
        self.influence_network = influence_network
        
        # Dados integrados
        self.person_data = {}  # person_id -> dados consolidados
        self.person_summaries = {}  # person_id -> PersonSummary
        self.team_insights = {}  # team_id -> insights da equipe
        self.organization_metrics = {}  # métricas organizacionais
        
        # Cache de visualizações
        self.visualization_cache = {}  # person_id_tipo -> figura
        
    def load_data(self) -> bool:
        """
        Carrega e integra dados de todos os módulos.
        
        Returns:
            True se os dados foram carregados com sucesso, False caso contrário
        """
        try:
            # Carregar dados básicos do pipeline se disponível
            if self.data_pipeline:
                self._load_base_data()
            
            # Carregar e integrar dados específicos de cada módulo
            if self.performance_predictor:
                self._integrate_performance_data()
                
            if self.career_simulator:
                self._integrate_career_data()
                
            if self.matrix_9box:
                self._integrate_9box_data()
                
            if self.influence_network:
                self._integrate_network_data()
            
            # Gerar sumários consolidados para cada pessoa
            self._generate_person_summaries()
            
            # Calcular métricas organizacionais
            self._calculate_organization_metrics()
            
            return True
            
        except Exception as e:
            print(f"Erro ao carregar dados para o dashboard holístico: {str(e)}")
            return False
            
    def _load_base_data(self):
        """Carrega dados básicos das pessoas pelo pipeline de dados."""
        if not self.data_pipeline:
            return
            
        # Carregar dados básicos de todas as pessoas
        persons_data = self.data_pipeline.load_persons_data()
        
        for person_data in persons_data:
            person_id = person_data.get('id')
            if person_id:
                # Inicializar dicionário de dados para esta pessoa
                self.person_data[person_id] = {
                    'basic_info': person_data,
                    'performance': {},
                    'potential': {},
                    'career': {},
                    'network': {},
                    'skills': {},
                    'history': {}
                }
    
    def _integrate_performance_data(self):
        """Integra dados de performance do preditor."""
        if not self.performance_predictor:
            return
            
        # Obter métricas de desempenho do preditor
        metrics = self.performance_predictor.performance_metrics
        
        # Agrupar por pessoa
        metrics_by_person = {}
        for metric in metrics:
            if metric.person_id not in metrics_by_person:
                metrics_by_person[metric.person_id] = []
            metrics_by_person[metric.person_id].append(metric)
            
        # Calcular métricas consolidadas por pessoa
        for person_id, person_metrics in metrics_by_person.items():
            if person_id not in self.person_data:
                self.person_data[person_id] = {
                    'basic_info': {'id': person_id},
                    'performance': {},
                    'potential': {},
                    'career': {},
                    'network': {},
                    'skills': {},
                    'history': {}
                }
            
            # Ordenar métricas por data
            sorted_metrics = sorted(person_metrics, key=lambda m: m.timestamp)
            
            # Calcular tendências por tipo de métrica
            trends = {}
            recent_values = {}
            
            for metric_type in set(m.metric_type for m in person_metrics):
                type_metrics = [m for m in sorted_metrics if m.metric_type == metric_type]
                if type_metrics:
                    values = [m.value for m in type_metrics]
                    trends[metric_type] = values
                    recent_values[metric_type] = values[-1]
            
            # Obter previsões se disponíveis
            predictions = {}
            if person_id in self.performance_predictor.person_predictions:
                for pred in self.performance_predictor.person_predictions[person_id]:
                    predictions[pred['target_metric']] = {
                        'value': pred['prediction'],
                        'confidence_interval': pred['confidence_interval'],
                        'timestamp': pred['timestamp']
                    }
            
            # Integrar ao dicionário da pessoa
            self.person_data[person_id]['performance'] = {
                'metrics': sorted_metrics,
                'trends': trends,
                'recent_values': recent_values,
                'predictions': predictions
            }
    
    def _integrate_career_data(self):
        """Integra dados de carreira do simulador."""
        if not self.career_simulator:
            return
            
        # Obter dados de habilidades
        skills_data = self.career_simulator.person_skills
        
        # Obter posições simuladas para cada pessoa
        for person_id, paths in self.career_simulator.simulated_paths.items():
            if person_id not in self.person_data:
                self.person_data[person_id] = {
                    'basic_info': {'id': person_id},
                    'performance': {},
                    'potential': {},
                    'career': {},
                    'network': {},
                    'skills': {},
                    'history': {}
                }
            
            # Obter posição atual (assumindo que é a primeira posição do melhor caminho)
            current_position_id = None
            if paths:
                # Ordenar por score de crescimento
                sorted_paths = sorted(paths, key=lambda p: p.growth_score, reverse=True)
                best_path = sorted_paths[0]
                if best_path.positions:
                    current_position_id = best_path.positions[0][0]
            
            # Obter detalhes da posição atual
            current_position = None
            if current_position_id and current_position_id in self.career_simulator.positions:
                current_position = self.career_simulator.positions[current_position_id]
            
            # Calcular gaps de habilidades
            skill_gaps = {}
            if current_position and person_id in skills_data:
                person_skills = skills_data[person_id]
                for skill, required in current_position.skills_required.items():
                    current = person_skills.get(skill, 0)
                    if current < required:
                        skill_gaps[skill] = required - current
            
            # Integrar ao dicionário da pessoa
            self.person_data[person_id]['career'] = {
                'paths': paths,
                'current_position': current_position,
                'skills': skills_data.get(person_id, {}),
                'skill_gaps': skill_gaps
            }
    
    def _integrate_9box_data(self):
        """Integra dados da matriz 9-box."""
        if not self.matrix_9box:
            return
            
        # Obter posições na matriz para cada pessoa
        for person_id, position_data in self.matrix_9box.get_all_positions().items():
            if person_id not in self.person_data:
                self.person_data[person_id] = {
                    'basic_info': {'id': person_id},
                    'performance': {},
                    'potential': {},
                    'career': {},
                    'network': {},
                    'skills': {},
                    'history': {}
                }
                
            # Obter trajetória temporal
            trajectory = self.matrix_9box.get_trajectory(person_id)
            
            # Integrar ao dicionário da pessoa
            self.person_data[person_id]['potential'] = {
                'nine_box_position': position_data,
                'trajectory': trajectory,
                'potential_score': position_data.get('potential', 0),
                'performance_score': position_data.get('performance', 0)
            }
    
    def _integrate_network_data(self):
        """Integra dados da rede de influência."""
        if not self.influence_network:
            return
            
        # Obter rede de influência
        network = self.influence_network.get_network()
        
        # Calcular métricas de centralidade
        centrality = {}
        if network:
            # Calcular diferentes métricas de centralidade
            degree_cent = nx.degree_centrality(network)
            closeness_cent = nx.closeness_centrality(network)
            betweenness_cent = nx.betweenness_centrality(network)
            eigenvector_cent = nx.eigenvector_centrality_numpy(network)
            
            # Consolidar em um único score
            for node in network.nodes():
                centrality[node] = {
                    'degree': degree_cent.get(node, 0),
                    'closeness': closeness_cent.get(node, 0),
                    'betweenness': betweenness_cent.get(node, 0),
                    'eigenvector': eigenvector_cent.get(node, 0),
                    # Score composto ponderado
                    'composite': (
                        degree_cent.get(node, 0) * 0.3 +
                        closeness_cent.get(node, 0) * 0.2 +
                        betweenness_cent.get(node, 0) * 0.3 +
                        eigenvector_cent.get(node, 0) * 0.2
                    )
                }
        
        # Obter métricas de multiplicador de impacto
        impact_multipliers = self.influence_network.get_impact_multipliers()
        
        # Obter dados de capital social
        social_capital = self.influence_network.get_social_capital()
        
        # Integrar por pessoa
        for person_id in list(centrality.keys()) + list(impact_multipliers.keys()) + list(social_capital.keys()):
            if person_id not in self.person_data:
                self.person_data[person_id] = {
                    'basic_info': {'id': person_id},
                    'performance': {},
                    'potential': {},
                    'career': {},
                    'network': {},
                    'skills': {},
                    'history': {}
                }
                
            # Integrar ao dicionário da pessoa
            self.person_data[person_id]['network'] = {
                'centrality': centrality.get(person_id, {}),
                'impact_multiplier': impact_multipliers.get(person_id, 0),
                'social_capital': social_capital.get(person_id, {})
            }
            
    def _generate_person_summaries(self):
        """Gera sumários integrados para cada pessoa."""
        for person_id, data in self.person_data.items():
            # Extrair dados básicos
            basic_info = data.get('basic_info', {})
            performance_data = data.get('performance', {})
            potential_data = data.get('potential', {})
            career_data = data.get('career', {})
            network_data = data.get('network', {})
            
            # Obter nome
            name = basic_info.get('name', person_id)
            
            # Obter posição atual
            current_position = "Desconhecida"
            if career_data.get('current_position'):
                current_position = career_data['current_position'].title
                
            # Obter scores de performance e potencial
            performance_score = potential_data.get('performance_score', 0)
            potential_score = potential_data.get('potential_score', 0)
            
            # Calcular posição na matriz 9-box (escala 1-3)
            nine_box_x = min(max(int(potential_score * 3), 1), 3)
            nine_box_y = min(max(int(performance_score * 3), 1), 3)
            nine_box_position = (nine_box_x, nine_box_y)
            
            # Obter score de crescimento de carreira
            career_growth_score = 0
            if career_data.get('paths'):
                # Pegar o melhor caminho
                sorted_paths = sorted(career_data['paths'], key=lambda p: p.growth_score, reverse=True)
                career_growth_score = sorted_paths[0].growth_score
                
            # Obter score de influência
            influence_score = network_data.get('centrality', {}).get('composite', 0)
            
            # Obter habilidades principais
            key_skills = {}
            if career_data.get('skills'):
                # Ordenar por nível e pegar as top 5
                sorted_skills = sorted(
                    career_data['skills'].items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:5]
                key_skills = dict(sorted_skills)
                
            # Obter áreas de desenvolvimento
            development_areas = []
            if career_data.get('skill_gaps'):
                # Ordenar por gap e pegar as top 3
                sorted_gaps = sorted(
                    career_data['skill_gaps'].items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:3]
                development_areas = [skill for skill, _ in sorted_gaps]
                
            # Obter tendências de métricas
            trends = performance_data.get('trends', {})
            
            # Obter previsões
            predictions = performance_data.get('predictions', {})
            
            # Calcular centralidade na rede
            network_centrality = network_data.get('centrality', {}).get('composite', 0)
            
            # Calcular velocidade de aprendizado
            learning_velocity = 0
            if career_data.get('skills') and len(career_data['skills']) > 0:
                skill_levels = list(career_data['skills'].values())
                learning_velocity = sum(skill_levels) / len(skill_levels)
                
            # Gerar recomendações
            top_recommendations = self._generate_recommendations(person_id)
            
            # Criar sumário da pessoa
            summary = PersonSummary(
                person_id=person_id,
                name=name,
                current_position=current_position,
                performance_score=performance_score,
                potential_score=potential_score,
                nine_box_position=nine_box_position,
                career_growth_score=career_growth_score,
                influence_score=influence_score,
                key_skills=key_skills,
                development_areas=development_areas,
                trends=trends,
                predictions=predictions,
                network_centrality=network_centrality,
                learning_velocity=learning_velocity,
                top_recommendations=top_recommendations
            )
            
            # Armazenar sumário
            self.person_summaries[person_id] = summary
            
    def _generate_recommendations(self, person_id: str) -> List[str]:
        """
        Gera recomendações personalizadas para uma pessoa.
        
        Args:
            person_id: ID da pessoa
            
        Returns:
            Lista de recomendações
        """
        recommendations = []
        data = self.person_data.get(person_id, {})
        
        # Verificar dados disponíveis
        if not data:
            return ["Dados insuficientes para gerar recomendações."]
        
        # Recomendações baseadas em gaps de habilidades
        skill_gaps = data.get('career', {}).get('skill_gaps', {})
        if skill_gaps:
            top_gap = sorted(skill_gaps.items(), key=lambda x: x[1], reverse=True)[0]
            recommendations.append(f"Desenvolver a habilidade {top_gap[0]} para aumentar adequação à posição atual.")
        
        # Recomendações baseadas em potencial vs desempenho
        potential = data.get('potential', {})
        performance_score = potential.get('performance_score', 0)
        potential_score = potential.get('potential_score', 0)
        
        if potential_score > performance_score + 0.2:
            recommendations.append("Focar em converter alto potencial em resultados concretos.")
        elif performance_score > potential_score + 0.2:
            recommendations.append("Buscar novos desafios que permitam expandir o potencial além da zona de conforto.")
        
        # Recomendações baseadas em rede de influência
        network = data.get('network', {})
        centrality = network.get('centrality', {}).get('composite', 0)
        
        if centrality < 0.3:
            recommendations.append("Ampliar rede de conexões para aumentar impacto e influência organizacional.")
        
        # Recomendações baseadas em carreira
        career = data.get('career', {})
        paths = career.get('paths', [])
        
        if paths:
            best_path = sorted(paths, key=lambda p: p.growth_score, reverse=True)[0]
            if len(best_path.positions) > 1:
                next_position = best_path.positions[1][0]
                pos_title = "próxima posição"
                if next_position in self.career_simulator.positions:
                    pos_title = self.career_simulator.positions[next_position].title
                recommendations.append(f"Preparar-se para {pos_title} adquirindo experiências estratégicas.")
        
        # Garantir pelo menos 3 recomendações
        if len(recommendations) < 3:
            generic_recs = [
                "Participar de projetos multidisciplinares para ampliar perspectiva.",
                "Buscar mentoria com líderes de outras áreas da organização.",
                "Desenvolver habilidades de comunicação e influência para aumentar impacto.",
                "Dedicar tempo para aprendizado contínuo em áreas emergentes."
            ]
            
            # Adicionar recomendações genéricas até atingir 3
            for rec in generic_recs:
                if rec not in recommendations:
                    recommendations.append(rec)
                    if len(recommendations) >= 3:
                        break
        
        return recommendations[:3]  # Limitar a 3 recomendações
    
    def _calculate_organization_metrics(self):
        """Calcula métricas agregadas a nível organizacional."""
        if not self.person_summaries:
            return
            
        # Inicializar métricas
        self.organization_metrics = {
            'avg_performance': 0,
            'avg_potential': 0,
            'avg_growth_score': 0,
            'avg_influence': 0,
            'talent_distribution': {
                (1,1): 0, (1,2): 0, (1,3): 0,
                (2,1): 0, (2,2): 0, (2,3): 0,
                (3,1): 0, (3,2): 0, (3,3): 0
            },
            'top_development_areas': {},
            'skill_coverage': {}
        }
        
        # Calcular médias
        total_persons = len(self.person_summaries)
        
        for person_id, summary in self.person_summaries.items():
            self.organization_metrics['avg_performance'] += summary.performance_score
            self.organization_metrics['avg_potential'] += summary.potential_score
            self.organization_metrics['avg_growth_score'] += summary.career_growth_score
            self.organization_metrics['avg_influence'] += summary.influence_score
            
            # Incrementar contagem na distribuição da matriz 9-box
            self.organization_metrics['talent_distribution'][summary.nine_box_position] += 1
            
            # Contabilizar áreas de desenvolvimento
            for area in summary.development_areas:
                if area not in self.organization_metrics['top_development_areas']:
                    self.organization_metrics['top_development_areas'][area] = 0
                self.organization_metrics['top_development_areas'][area] += 1
                
            # Contabilizar cobertura de habilidades
            for skill, level in summary.key_skills.items():
                if skill not in self.organization_metrics['skill_coverage']:
                    self.organization_metrics['skill_coverage'][skill] = {'count': 0, 'avg_level': 0}
                self.organization_metrics['skill_coverage'][skill]['count'] += 1
                self.organization_metrics['skill_coverage'][skill]['avg_level'] += level
        
        # Finalizar médias
        if total_persons > 0:
            self.organization_metrics['avg_performance'] /= total_persons
            self.organization_metrics['avg_potential'] /= total_persons
            self.organization_metrics['avg_growth_score'] /= total_persons
            self.organization_metrics['avg_influence'] /= total_persons
            
        # Finalizar médias de níveis de habilidades
        for skill, data in self.organization_metrics['skill_coverage'].items():
            if data['count'] > 0:
                data['avg_level'] /= data['count']
                
        # Ordenar áreas de desenvolvimento
        self.organization_metrics['top_development_areas'] = {
            k: v for k, v in sorted(
                self.organization_metrics['top_development_areas'].items(),
                key=lambda item: item[1],
                reverse=True
            )
        } 

    def create_person_dashboard(self, 
                             person_id: str, 
                             output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Cria um dashboard holístico para uma pessoa específica.
        
        Args:
            person_id: ID da pessoa
            output_path: Caminho para salvar o dashboard
            
        Returns:
            Caminho do arquivo salvo ou None em caso de erro
        """
        if person_id not in self.person_summaries:
            print(f"Sumário não encontrado para a pessoa {person_id}")
            return None
            
        summary = self.person_summaries[person_id]
        
        try:
            # Criar layout com 6 visualizações principais
            fig = plt.figure(figsize=(20, 12))
            gs = gridspec.GridSpec(2, 3, figure=fig)
            
            # 1. Radar de competências
            self._plot_skills_radar(fig, gs[0, 0], summary)
            
            # 2. Trajetória na matriz 9-box
            self._plot_matrix_trajectory(fig, gs[0, 1], summary)
            
            # 3. Rede de influência
            self._plot_influence_network(fig, gs[0, 2], summary)
            
            # 4. Tendências de performance
            self._plot_performance_trends(fig, gs[1, 0], summary)
            
            # 5. Simulação de carreira
            self._plot_career_simulation(fig, gs[1, 1], summary)
            
            # 6. Recomendações e insights
            self._plot_recommendations(fig, gs[1, 2], summary)
            
            # Adicionar título geral
            fig.suptitle(f"Dashboard Holístico de Desenvolvimento de Talentos - {summary.name}", 
                       fontsize=16, y=0.98)
            
            # Ajustar layout
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            
            # Salvar visualização
            if output_path is None:
                output_path = Path(f'output/dashboard_holistico_{person_id}.png')
                
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return output_path
            
        except Exception as e:
            print(f"Erro ao criar dashboard para {person_id}: {str(e)}")
            return None
    
    def _plot_skills_radar(self, fig: Figure, position, summary: PersonSummary):
        """
        Plota o radar de competências.
        
        Args:
            fig: Figura matplotlib
            position: Posição no grid
            summary: Sumário da pessoa
        """
        ax = fig.add_subplot(position, polar=True)
        
        # Obter habilidades e valores
        skills = list(summary.key_skills.keys())
        values = list(summary.key_skills.values())
        
        if not skills:
            ax.text(0.5, 0.5, "Dados insuficientes para radar de competências", 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title("Radar de Competências")
            return
            
        # Adicionar o primeiro valor novamente para fechar o círculo
        values.append(values[0])
        skills.append(skills[0])
        
        # Calcular ângulos
        angles = np.linspace(0, 2*np.pi, len(skills), endpoint=True)
        
        # Plotar
        ax.plot(angles, values, 'o-', linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        
        # Adicionar linhas de grid
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(skills[:-1])
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'])
        
        # Adicionar título
        ax.set_title("Radar de Competências")
    
    def _plot_matrix_trajectory(self, fig: Figure, position, summary: PersonSummary):
        """
        Plota a trajetória na matriz 9-box.
        
        Args:
            fig: Figura matplotlib
            position: Posição no grid
            summary: Sumário da pessoa
        """
        ax = fig.add_subplot(position)
        
        # Obter dados de trajetória
        trajectory = self.person_data.get(summary.person_id, {}) \
                        .get('potential', {}) \
                        .get('trajectory', [])
        
        if not trajectory:
            # Plotar apenas a posição atual
            x = summary.potential_score
            y = summary.performance_score
            ax.scatter(x, y, s=100, c='blue', marker='o', label='Posição Atual')
            ax.text(x+0.02, y+0.02, 'Atual', fontsize=10)
        else:
            # Plotar trajetória completa
            points = [(p['potential'], p['performance']) for p in trajectory]
            if points:
                xs, ys = zip(*points)
                ax.plot(xs, ys, 'b-', alpha=0.5)
                ax.scatter(xs, ys, s=50, c='lightblue', marker='o')
                
                # Adicionar labels para início e fim
                ax.text(xs[0]+0.02, ys[0]+0.02, 'Início', fontsize=8)
                ax.text(xs[-1]+0.02, ys[-1]+0.02, 'Atual', fontsize=8)
                
                # Destacar posição atual
                ax.scatter(xs[-1], ys[-1], s=100, c='blue', marker='o')
        
        # Configurar limites e grid
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel('Potencial')
        ax.set_ylabel('Desempenho')
        
        # Adicionar linhas divisórias da matriz 9-box
        ax.axhline(y=0.33, color='gray', linestyle='--', alpha=0.5)
        ax.axhline(y=0.67, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=0.33, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=0.67, color='gray', linestyle='--', alpha=0.5)
        
        # Adicionar rótulos
        for i, x_pos in enumerate([0.17, 0.5, 0.83]):
            for j, y_pos in enumerate([0.17, 0.5, 0.83]):
                # Converter de índice de matriz 9-box para texto
                labels = [
                    ['Performer em Risco', 'Performer Sólido', 'Performer Forte'],
                    ['Enigma', 'Core', 'Alta Performance'],
                    ['Novo Enquadramento', 'Futuro Promissor', 'Estrela']
                ]
                ax.text(x_pos, y_pos, labels[2-j][i], 
                       ha='center', va='center', fontsize=8, alpha=0.6)
        
        # Adicionar título
        ax.set_title("Trajetória na Matriz 9-Box")
    
    def _plot_influence_network(self, fig: Figure, position, summary: PersonSummary):
        """
        Plota visualização da rede de influência.
        
        Args:
            fig: Figura matplotlib
            position: Posição no grid
            summary: Sumário da pessoa
        """
        ax = fig.add_subplot(position)
        
        # Tentar obter rede de influência
        if not self.influence_network:
            ax.text(0.5, 0.5, "Dados de rede de influência não disponíveis", 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title("Rede de Influência")
            return
            
        # Obter rede centrada na pessoa
        person_network = self.influence_network.get_ego_network(summary.person_id)
        
        if not person_network or person_network.number_of_nodes() <= 1:
            ax.text(0.5, 0.5, "Rede de influência insuficiente para visualização", 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title("Rede de Influência")
            return
        
        # Usar posicionamento baseado em força
        pos = nx.spring_layout(person_network, seed=42)
        
        # Calcular métricas de centralidade para definir tamanhos dos nós
        centrality = nx.degree_centrality(person_network)
        
        # Definir cores e tamanhos
        node_colors = []
        node_sizes = []
        
        for node in person_network.nodes():
            if node == summary.person_id:
                node_colors.append('red')
                node_sizes.append(300)
            else:
                node_colors.append('skyblue')
                node_sizes.append(100 + 500 * centrality[node])
        
        # Desenhar rede
        nx.draw_networkx(
            person_network, pos, ax=ax,
            node_color=node_colors,
            node_size=node_sizes,
            font_size=8,
            width=1.5,
            edge_color='gray',
            arrows=True,
            arrowsize=10,
            with_labels=True
        )
        
        # Remover eixos
        ax.set_axis_off()
        
        # Adicionar título
        ax.set_title("Rede de Influência")
        
        # Adicionar legenda
        ax.text(0.05, 0.05, 
               f"Centralidade: {summary.network_centrality:.2f}\n"
               f"Multiplicador de Impacto: {self.person_data.get(summary.person_id, {}).get('network', {}).get('impact_multiplier', 0):.2f}",
               transform=ax.transAxes, fontsize=8,
               bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))
    
    def _plot_performance_trends(self, fig: Figure, position, summary: PersonSummary):
        """
        Plota tendências de performance com previsões futuras.
        
        Args:
            fig: Figura matplotlib
            position: Posição no grid
            summary: Sumário da pessoa
        """
        ax = fig.add_subplot(position)
        
        # Verificar se há tendências
        if not summary.trends:
            ax.text(0.5, 0.5, "Dados de tendências não disponíveis", 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title("Tendências de Performance")
            return
        
        # Selecionar até 3 métricas principais
        metrics = list(summary.trends.keys())[:3]
        colors = ['blue', 'green', 'purple']
        
        # Plotar cada métrica
        for i, metric in enumerate(metrics):
            values = summary.trends[metric]
            x = range(len(values))
            ax.plot(x, values, marker='o', color=colors[i % len(colors)], 
                  label=metric)
            
            # Adicionar previsão se disponível
            if metric in summary.predictions:
                pred = summary.predictions[metric]
                next_x = len(values)
                ax.scatter(next_x, pred['value'], marker='*', 
                         s=100, color=colors[i % len(colors)])
                
                # Adicionar intervalo de confiança
                if 'confidence_interval' in pred:
                    ci = pred['confidence_interval']
                    ax.fill_between([next_x-0.1, next_x+0.1], 
                                  [ci[0], ci[0]], 
                                  [ci[1], ci[1]], 
                                  color=colors[i % len(colors)], alpha=0.3)
        
        # Configurar eixos
        ax.set_xlabel('Período')
        ax.set_ylabel('Valor')
        ax.legend(loc='best')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Adicionar título
        ax.set_title("Tendências de Performance")
    
    def _plot_career_simulation(self, fig: Figure, position, summary: PersonSummary):
        """
        Plota simulação de carreira.
        
        Args:
            fig: Figura matplotlib
            position: Posição no grid
            summary: Sumário da pessoa
        """
        ax = fig.add_subplot(position)
        
        # Verificar se há simulação de carreira
        career_data = self.person_data.get(summary.person_id, {}).get('career', {})
        paths = career_data.get('paths', [])
        
        if not paths:
            ax.text(0.5, 0.5, "Dados de simulação de carreira não disponíveis", 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title("Simulação de Carreira")
            return
        
        # Ordenar por score de crescimento
        sorted_paths = sorted(paths, key=lambda p: p.growth_score, reverse=True)
        best_path = sorted_paths[0]
        
        # Extrair posições e durações
        positions = []
        durations = []
        
        for pos_id, duration in best_path.positions:
            if pos_id in self.career_simulator.positions:
                position = self.career_simulator.positions[pos_id]
                positions.append(position.title)
                durations.append(duration)
        
        if not positions:
            ax.text(0.5, 0.5, "Caminho de carreira sem posições definidas", 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title("Simulação de Carreira")
            return
        
        # Criar barras horizontais para timeline
        y_pos = range(len(positions))
        start_times = [0]
        for i in range(len(durations) - 1):
            start_times.append(start_times[i] + durations[i])
        
        # Cores por posição (com base no nível)
        levels = [self.career_simulator.positions[pos_id].level 
                 for pos_id, _ in best_path.positions]
        colors = plt.cm.viridis(np.array(levels) / max(levels))
        
        # Plotar barras horizontais
        for i, (pos, duration, start, color) in enumerate(zip(positions, durations, start_times, colors)):
            ax.barh(i, duration, left=start, height=0.5, color=color, alpha=0.7)
            ax.text(start + duration/2, i, pos, ha='center', va='center', fontsize=8)
        
        # Configurar eixos
        ax.set_yticks([])
        ax.set_xlabel('Anos')
        ax.invert_yaxis()  # Para manter a primeira posição no topo
        
        # Adicionar título
        ax.set_title("Simulação de Carreira")
        
        # Adicionar informação adicional
        info_text = (f"Score de Crescimento: {best_path.growth_score:.2f}\n"
                    f"Probabilidade: {best_path.probability:.2f}\n"
                    f"Total de Anos: {best_path.total_time}")
        
        ax.text(0.05, 0.05, info_text, transform=ax.transAxes, fontsize=8,
               bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))
    
    def _plot_recommendations(self, fig: Figure, position, summary: PersonSummary):
        """
        Plota recomendações e insights.
        
        Args:
            fig: Figura matplotlib
            position: Posição no grid
            summary: Sumário da pessoa
        """
        ax = fig.add_subplot(position)
        
        # Remover eixos
        ax.axis('off')
        
        # Adicionar título
        ax.set_title("Recomendações e Insights")
        
        # Criar texto de métricas-chave
        metrics_text = (
            f"MÉTRICAS-CHAVE\n"
            f"-------------------------------------------\n"
            f"Performance: {summary.performance_score:.2f}\n"
            f"Potencial: {summary.potential_score:.2f}\n"
            f"Crescimento: {summary.career_growth_score:.2f}\n"
            f"Influência: {summary.influence_score:.2f}\n"
            f"Velocidade de Aprendizado: {summary.learning_velocity:.2f}\n"
        )
        
        # Criar texto de recomendações
        rec_text = (
            f"\nRECOMENDAÇÕES\n"
            f"-------------------------------------------\n"
        )
        
        for i, rec in enumerate(summary.top_recommendations, 1):
            rec_text += f"{i}. {rec}\n"
            
        # Criar texto de áreas de desenvolvimento
        dev_text = (
            f"\nÁREAS DE DESENVOLVIMENTO\n"
            f"-------------------------------------------\n"
        )
        
        for area in summary.development_areas:
            dev_text += f"• {area}\n"
            
        # Combinar textos
        full_text = metrics_text + rec_text + dev_text
        
        # Adicionar texto ao plot
        ax.text(0.05, 0.95, full_text, transform=ax.transAxes,
               fontsize=9, va='top',
               bbox=dict(boxstyle="round,pad=0.5", facecolor='lightyellow', alpha=0.8))
    
    def generate_holistic_report(self, 
                               person_id: str,
                               output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Gera um relatório holístico detalhado para uma pessoa.
        
        Args:
            person_id: ID da pessoa
            output_path: Caminho para salvar o relatório
            
        Returns:
            Caminho do relatório salvo ou None em caso de erro
        """
        if person_id not in self.person_summaries:
            print(f"Sumário não encontrado para a pessoa {person_id}")
            return None
            
        summary = self.person_summaries[person_id]
        
        # Criar caminho de saída
        if output_path is None:
            output_path = Path(f'output/relatorio_holistico_{person_id}.md')
            
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Gerar visualização antes do relatório
            img_path = self.create_person_dashboard(person_id)
            
            # Gerar relatório
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# RELATÓRIO HOLÍSTICO DE DESENVOLVIMENTO\n\n")
                
                f.write(f"## Informações Básicas\n\n")
                f.write(f"**Nome**: {summary.name}\n")
                f.write(f"**Posição Atual**: {summary.current_position}\n")
                f.write(f"**Data**: {datetime.datetime.now().strftime('%d/%m/%Y')}\n\n")
                
                f.write(f"## Análise Multidimensional\n\n")
                
                # Adicionar referência à visualização
                if img_path:
                    f.write(f"![Dashboard Holístico]({img_path})\n\n")
                
                # Quadrante na matriz 9-box
                nine_box_labels = [
                    ['Performer em Risco', 'Performer Sólido', 'Performer Forte'],
                    ['Enigma', 'Core', 'Alta Performance'],
                    ['Novo Enquadramento', 'Futuro Promissor', 'Estrela']
                ]
                x, y = summary.nine_box_position
                quadrant = nine_box_labels[3-y][x-1]
                
                f.write(f"### Potencial e Desempenho\n\n")
                f.write(f"**Quadrante Atual**: {quadrant}\n")
                f.write(f"**Score de Desempenho**: {summary.performance_score:.2f}\n")
                f.write(f"**Score de Potencial**: {summary.potential_score:.2f}\n\n")
                
                f.write(f"### Análise de Competências\n\n")
                f.write(f"**Competências Principais**:\n")
                for skill, level in summary.key_skills.items():
                    f.write(f"- {skill}: {level:.2f}\n")
                
                f.write(f"\n**Áreas de Desenvolvimento**:\n")
                for area in summary.development_areas:
                    f.write(f"- {area}\n")
                
                f.write(f"\n### Análise de Carreira\n\n")
                f.write(f"**Score de Crescimento de Carreira**: {summary.career_growth_score:.2f}\n")
                
                # Adicionar detalhes do melhor caminho de carreira
                career_data = self.person_data.get(person_id, {}).get('career', {})
                paths = career_data.get('paths', [])
                
                if paths:
                    sorted_paths = sorted(paths, key=lambda p: p.growth_score, reverse=True)
                    best_path = sorted_paths[0]
                    
                    f.write(f"\n**Trajetória Recomendada**:\n")
                    for i, (pos_id, duration) in enumerate(best_path.positions):
                        if pos_id in self.career_simulator.positions:
                            position = self.career_simulator.positions[pos_id]
                            f.write(f"{i+1}. {position.title} ({position.track}) - {duration} anos\n")
                
                f.write(f"\n### Análise de Rede de Influência\n\n")
                f.write(f"**Score de Influência**: {summary.influence_score:.2f}\n")
                f.write(f"**Centralidade na Rede**: {summary.network_centrality:.2f}\n")
                
                network_data = self.person_data.get(person_id, {}).get('network', {})
                impact = network_data.get('impact_multiplier', 0)
                f.write(f"**Multiplicador de Impacto**: {impact:.2f}\n\n")
                
                f.write(f"### Previsões de Desempenho\n\n")
                if summary.predictions:
                    for metric, pred in summary.predictions.items():
                        f.write(f"**{metric}**:\n")
                        f.write(f"- Valor Previsto: {pred['value']:.2f}\n")
                        if 'confidence_interval' in pred:
                            ci = pred['confidence_interval']
                            f.write(f"- Intervalo de Confiança: [{ci[0]:.2f}, {ci[1]:.2f}]\n")
                else:
                    f.write(f"Previsões não disponíveis.\n")
                
                f.write(f"\n## Recomendações\n\n")
                for i, rec in enumerate(summary.top_recommendations, 1):
                    f.write(f"{i}. {rec}\n")
                
                f.write(f"\n## Próximos Passos\n\n")
                f.write(f"1. Revisar plano de desenvolvimento pessoal\n")
                f.write(f"2. Agendar reunião de feedback com gestor\n")
                f.write(f"3. Definir objetivos de desenvolvimento para os próximos 6 meses\n")
                
            return output_path
            
        except Exception as e:
            print(f"Erro ao gerar relatório para {person_id}: {str(e)}")
            return None
    
    def generate_team_report(self, 
                          team_id: str,
                          person_ids: List[str],
                          output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Gera um relatório holístico para uma equipe.
        
        Args:
            team_id: ID da equipe
            person_ids: Lista de IDs de pessoas na equipe
            output_path: Caminho para salvar o relatório
            
        Returns:
            Caminho do relatório salvo ou None em caso de erro
        """
        # Filtrar pessoas disponíveis
        available_persons = [pid for pid in person_ids if pid in self.person_summaries]
        
        if not available_persons:
            print(f"Nenhuma pessoa encontrada para a equipe {team_id}")
            return None
            
        # Criar caminho de saída
        if output_path is None:
            output_path = Path(f'output/relatorio_equipe_{team_id}.md')
            
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Calcular métricas da equipe
            team_metrics = {
                'avg_performance': 0,
                'avg_potential': 0,
                'avg_growth': 0,
                'avg_influence': 0,
                'talent_distribution': {
                    (1,1): 0, (1,2): 0, (1,3): 0,
                    (2,1): 0, (2,2): 0, (2,3): 0,
                    (3,1): 0, (3,2): 0, (3,3): 0
                },
                'skill_coverage': {},
                'development_areas': {}
            }
            
            # Calcular médias e agregar dados
            for person_id in available_persons:
                summary = self.person_summaries[person_id]
                
                team_metrics['avg_performance'] += summary.performance_score
                team_metrics['avg_potential'] += summary.potential_score
                team_metrics['avg_growth'] += summary.career_growth_score
                team_metrics['avg_influence'] += summary.influence_score
                
                # Incrementar contagem na distribuição da matriz 9-box
                team_metrics['talent_distribution'][summary.nine_box_position] += 1
                
                # Agregar competências
                for skill, level in summary.key_skills.items():
                    if skill not in team_metrics['skill_coverage']:
                        team_metrics['skill_coverage'][skill] = {'count': 0, 'avg_level': 0}
                    team_metrics['skill_coverage'][skill]['count'] += 1
                    team_metrics['skill_coverage'][skill]['avg_level'] += level
                
                # Agregar áreas de desenvolvimento
                for area in summary.development_areas:
                    if area not in team_metrics['development_areas']:
                        team_metrics['development_areas'][area] = 0
                    team_metrics['development_areas'][area] += 1
            
            # Finalizar médias
            num_persons = len(available_persons)
            team_metrics['avg_performance'] /= num_persons
            team_metrics['avg_potential'] /= num_persons
            team_metrics['avg_growth'] /= num_persons
            team_metrics['avg_influence'] /= num_persons
            
            # Finalizar médias de níveis de habilidades
            for skill, data in team_metrics['skill_coverage'].items():
                if data['count'] > 0:
                    data['avg_level'] /= data['count']
            
            # Ordenar habilidades por cobertura
            sorted_skills = sorted(
                team_metrics['skill_coverage'].items(),
                key=lambda x: (x[1]['count'], x[1]['avg_level']),
                reverse=True
            )
            
            # Ordenar áreas de desenvolvimento
            sorted_areas = sorted(
                team_metrics['development_areas'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Gerar relatório
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# RELATÓRIO HOLÍSTICO DE EQUIPE\n\n")
                
                f.write(f"## Informações Básicas\n\n")
                f.write(f"**Equipe**: {team_id}\n")
                f.write(f"**Membros**: {len(available_persons)}\n")
                f.write(f"**Data**: {datetime.datetime.now().strftime('%d/%m/%Y')}\n\n")
                
                f.write(f"## Métricas da Equipe\n\n")
                f.write(f"**Performance Média**: {team_metrics['avg_performance']:.2f}\n")
                f.write(f"**Potencial Médio**: {team_metrics['avg_potential']:.2f}\n")
                f.write(f"**Crescimento Médio**: {team_metrics['avg_growth']:.2f}\n")
                f.write(f"**Influência Média**: {team_metrics['avg_influence']:.2f}\n\n")
                
                f.write(f"## Distribuição de Talentos\n\n")
                f.write(f"| Quadrante | Quantidade | Porcentagem |\n")
                f.write(f"|-----------|------------|-------------|\n")
                
                nine_box_labels = [
                    ['Performer em Risco', 'Performer Sólido', 'Performer Forte'],
                    ['Enigma', 'Core', 'Alta Performance'],
                    ['Novo Enquadramento', 'Futuro Promissor', 'Estrela']
                ]
                
                for x in range(1, 4):
                    for y in range(1, 4):
                        pos = (x, y)
                        count = team_metrics['talent_distribution'][pos]
                        percentage = (count / num_persons) * 100
                        label = nine_box_labels[3-y][x-1]
                        f.write(f"| {label} | {count} | {percentage:.1f}% |\n")
                
                f.write(f"\n## Cobertura de Competências\n\n")
                f.write(f"| Competência | Cobertura | Nível Médio |\n")
                f.write(f"|-------------|-----------|-------------|\n")
                
                for skill, data in sorted_skills[:10]:  # Top 10
                    coverage = (data['count'] / num_persons) * 100
                    f.write(f"| {skill} | {coverage:.1f}% | {data['avg_level']:.2f} |\n")
                
                f.write(f"\n## Áreas de Desenvolvimento\n\n")
                f.write(f"| Área | Frequência |\n")
                f.write(f"|------|------------|\n")
                
                for area, count in sorted_areas[:5]:  # Top 5
                    f.write(f"| {area} | {count} |\n")
                
                f.write(f"\n## Resumo Individual\n\n")
                
                # Adicionar resumo de cada pessoa
                for person_id in available_persons:
                    summary = self.person_summaries[person_id]
                    x, y = summary.nine_box_position
                    quadrant = nine_box_labels[3-y][x-1]
                    
                    f.write(f"### {summary.name}\n\n")
                    f.write(f"- **Posição**: {summary.current_position}\n")
                    f.write(f"- **Quadrante**: {quadrant}\n")
                    f.write(f"- **Performance**: {summary.performance_score:.2f}\n")
                    f.write(f"- **Potencial**: {summary.potential_score:.2f}\n")
                    f.write(f"- **Influência**: {summary.influence_score:.2f}\n")
                    f.write(f"- **Áreas de Desenvolvimento**: {', '.join(summary.development_areas)}\n\n")
                
                f.write(f"\n## Recomendações para a Equipe\n\n")
                
                # Gerar recomendações baseadas nos dados da equipe
                f.write(f"1. **Desenvolvimento de Competências**: ")
                if sorted_areas:
                    f.write(f"Focar no desenvolvimento de {sorted_areas[0][0]}, ")
                    if len(sorted_areas) > 1:
                        f.write(f"que é uma área de desenvolvimento comum para vários membros.\n")
                    else:
                        f.write(f"que é uma área de desenvolvimento prioritária.\n")
                else:
                    f.write(f"Desenvolver um plano estruturado de capacitação.\n")
                
                f.write(f"2. **Balanceamento de Talentos**: ")
                high_performers = team_metrics['talent_distribution'][(3,3)] + team_metrics['talent_distribution'][(2,3)] + team_metrics['talent_distribution'][(3,2)]
                high_potential = team_metrics['talent_distribution'][(3,1)] + team_metrics['talent_distribution'][(3,2)]
                
                if high_performers < num_persons * 0.2:
                    f.write(f"Considerar integrar mais pessoas de alta performance à equipe.\n")
                elif high_potential < num_persons * 0.2:
                    f.write(f"Buscar talentos com alto potencial para renovação da equipe.\n")
                else:
                    f.write(f"A equipe tem um bom balanceamento entre performance e potencial.\n")
                
                f.write(f"3. **Fortalecimento da Rede de Influência**: Promover mais colaboração entre membros ")
                if team_metrics['avg_influence'] < 0.4:
                    f.write(f"para aumentar o impacto coletivo, que está abaixo do ideal.\n")
                else:
                    f.write(f"para manter o bom nível de influência organizacional.\n")
            
            return output_path
            
        except Exception as e:
            print(f"Erro ao gerar relatório para equipe {team_id}: {str(e)}")
            return None 