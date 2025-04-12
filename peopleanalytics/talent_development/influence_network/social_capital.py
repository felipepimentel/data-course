"""
Mapeamento de Capital Social na Rede de Influência.

Analisa como cada pessoa constrói e mobiliza suas conexões para gerar valor,
identificando padrões colaborativos e estruturas de rede valiosas.
"""
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx
import seaborn as sns
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from pathlib import Path
import matplotlib.cm as cm

from peopleanalytics.data_pipeline import DataPipeline
from peopleanalytics.talent_development.influence_network.network_analyzer import InfluenceNetwork


@dataclass
class Collaboration:
    """Representa uma colaboração entre pessoas."""
    collab_id: str
    participants: List[str]  # Lista de person_ids
    collab_type: str  # 'projeto', 'mentoria', 'evento', etc.
    start_date: datetime.datetime
    end_date: Optional[datetime.datetime] = None
    value_created: float = 0.0  # Valor gerado pela colaboração
    success_rating: float = 0.0  # 0-1, sucesso da colaboração
    attributes: Dict[str, Any] = None


class SocialCapitalMapper:
    """
    Mapeia e analisa o capital social na organização.
    
    Identifica como as pessoas constroem e utilizam suas redes de
    relacionamento para gerar valor, incluindo padrões de:
    - Intermediação estratégica (brokers)
    - Diversidade de rede
    - Força dos vínculos
    - Clusters de inovação
    - Fluxo de valor através da rede
    """
    
    def __init__(self, 
                influence_network: Optional[InfluenceNetwork] = None,
                data_pipeline: Optional[DataPipeline] = None):
        """
        Inicializa o mapeador de capital social.
        
        Args:
            influence_network: Rede de influência para análise
            data_pipeline: Pipeline de dados para carregar/salvar
        """
        self.influence_network = influence_network
        self.data_pipeline = data_pipeline
        self.collaborations = []  # Lista de colaborações
        self.person_collaborations = {}  # person_id -> [colaborações]
        self.social_capital_metrics = {}  # person_id -> métricas
        
    def load_data(self) -> bool:
        """
        Carrega dados de colaborações.
        
        Returns:
            True se os dados foram carregados com sucesso, False caso contrário
        """
        if not self.data_pipeline:
            return False
            
        try:
            # Carregar colaborações
            collab_data = self.data_pipeline.load_collaborations()
            
            # Converter para objetos Collaboration
            self.collaborations = []
            for collab in collab_data:
                collaboration = Collaboration(
                    collab_id=collab['id'],
                    participants=collab['participants'],
                    collab_type=collab.get('type', 'projeto'),
                    start_date=datetime.datetime.fromisoformat(
                        collab.get('start_date', datetime.datetime.now().isoformat())
                    ),
                    end_date=datetime.datetime.fromisoformat(
                        collab.get('end_date', datetime.datetime.now().isoformat())
                    ) if collab.get('end_date') else None,
                    value_created=float(collab.get('value_created', 0.0)),
                    success_rating=float(collab.get('success_rating', 0.5)),
                    attributes=collab.get('attributes', {})
                )
                self.collaborations.append(collaboration)
            
            # Indexar por pessoa para acesso rápido
            self.person_collaborations = {}
            for collab in self.collaborations:
                for person_id in collab.participants:
                    if person_id not in self.person_collaborations:
                        self.person_collaborations[person_id] = []
                    self.person_collaborations[person_id].append(collab)
            
            return True
            
        except Exception as e:
            print(f"Erro ao carregar dados de colaborações: {str(e)}")
            return False
    
    def add_collaboration(self, 
                        participants: List[str],
                        collab_type: str,
                        start_date: Optional[datetime.datetime] = None,
                        end_date: Optional[datetime.datetime] = None,
                        value_created: float = 0.0,
                        success_rating: float = 0.5,
                        attributes: Optional[Dict[str, Any]] = None) -> Collaboration:
        """
        Adiciona uma nova colaboração.
        
        Args:
            participants: Lista de IDs de participantes
            collab_type: Tipo de colaboração
            start_date: Data de início (default: agora)
            end_date: Data de término (opcional)
            value_created: Valor gerado
            success_rating: Taxa de sucesso (0-1)
            attributes: Atributos adicionais
            
        Returns:
            Nova colaboração criada
        """
        if not participants or len(participants) < 2:
            raise ValueError("Uma colaboração precisa de pelo menos 2 participantes")
            
        if not 0 <= success_rating <= 1:
            raise ValueError("Taxa de sucesso deve estar entre 0 e 1")
        
        # Criar ID único
        collab_id = f"sc_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Criar colaboração
        collab = Collaboration(
            collab_id=collab_id,
            participants=participants,
            collab_type=collab_type,
            start_date=start_date or datetime.datetime.now(),
            end_date=end_date,
            value_created=value_created,
            success_rating=success_rating,
            attributes=attributes or {}
        )
        
        # Adicionar à lista
        self.collaborations.append(collab)
        
        # Atualizar índice por pessoa
        for person_id in collab.participants:
            if person_id not in self.person_collaborations:
                self.person_collaborations[person_id] = []
            self.person_collaborations[person_id].append(collab)
        
        # Salvar no pipeline se disponível
        if self.data_pipeline:
            collab_data = {
                'id': collab_id,
                'participants': participants,
                'type': collab_type,
                'start_date': collab.start_date.isoformat(),
                'end_date': collab.end_date.isoformat() if collab.end_date else None,
                'value_created': value_created,
                'success_rating': success_rating,
                'attributes': attributes or {}
            }
            
            self.data_pipeline.save_collaboration(collab_data)
        
        return collab
    
    def calculate_social_capital(self, person_id: str) -> Dict[str, Any]:
        """
        Calcula métricas de capital social para uma pessoa.
        
        Args:
            person_id: ID da pessoa
            
        Returns:
            Dicionário com métricas de capital social
        """
        if not self.influence_network:
            raise ValueError("Rede de influência é necessária para análise")
            
        if person_id not in self.influence_network.graph:
            raise ValueError(f"Pessoa {person_id} não encontrada na rede")
        
        # Obter ego-network (rede centrada na pessoa)
        ego_network = self.influence_network.get_ego_network(person_id, radius=2)
        
        # Métricas básicas
        metrics = {}
        
        # 1. Tamanho da rede
        metrics['network_size'] = len(ego_network) - 1  # excluir o próprio nó
        
        # 2. Densidade (% de conexões possíveis que existem)
        metrics['network_density'] = nx.density(ego_network)
        
        # 3. Centralidade de intermediação (capacidade de conectar grupos)
        # Usar uma versão simplificada para ego-networks
        betweenness = nx.betweenness_centrality(ego_network)
        metrics['betweenness_centrality'] = betweenness.get(person_id, 0.0)
        
        # 4. Diversidade da rede
        # Calcular diversidade baseada em atributos dos nós
        # (departamento, nível, localização, etc.)
        diversity_score = self._calculate_network_diversity(ego_network, person_id)
        metrics['network_diversity'] = diversity_score
        
        # 5. Força média dos vínculos
        tie_strength = self._calculate_tie_strength(ego_network, person_id)
        metrics['avg_tie_strength'] = tie_strength['avg']
        metrics['strong_ties'] = tie_strength['strong']
        metrics['weak_ties'] = tie_strength['weak']
        
        # 6. Valor colaborativo gerado
        collab_value = self._calculate_collaborative_value(person_id)
        metrics['total_value_created'] = collab_value['total']
        metrics['avg_value_per_collab'] = collab_value['avg']
        metrics['collab_success_rate'] = collab_value['success_rate']
        
        # 7. Pontuação de capital social (agregada)
        metrics['social_capital_score'] = self._calculate_social_capital_score(metrics)
        
        # Salvar métricas calculadas
        self.social_capital_metrics[person_id] = metrics
        
        return metrics
    
    def _calculate_network_diversity(self, 
                                  ego_network: nx.DiGraph, 
                                  person_id: str) -> float:
        """
        Calcula a diversidade da rede com base em atributos dos contatos.
        
        Args:
            ego_network: Rede ego-centrada
            person_id: ID da pessoa central
            
        Returns:
            Pontuação de diversidade (0-1)
        """
        # Se não temos atributos suficientes, usar uma estimativa
        if not self.influence_network.person_attributes:
            # Usar uma medida de diversidade estrutural (clustering)
            clustering = nx.clustering(ego_network.to_undirected())
            # Baixo clustering significa contatos menos interconectados, maior diversidade
            return 1.0 - (clustering.get(person_id, 0.0))
        
        # Extrair contatos diretos
        contacts = list(ego_network.neighbors(person_id))
        
        if not contacts:
            return 0.0
        
        # Analisar diversidade por atributos
        diversity_dimensions = ['department', 'role', 'location', 'team', 'level']
        dimension_scores = []
        
        for dimension in diversity_dimensions:
            values = set()
            value_count = 0
            
            for contact_id in contacts:
                attrs = self.influence_network.person_attributes.get(contact_id, {})
                if dimension in attrs:
                    values.add(attrs[dimension])
                    value_count += 1
            
            # Diversidade = proporção de valores únicos entre todos os contatos
            if value_count > 0:
                dimension_scores.append(len(values) / value_count)
        
        # Se não temos dados suficientes
        if not dimension_scores:
            return 0.5  # Valor neutro
        
        # Média das dimensões
        return sum(dimension_scores) / len(dimension_scores)
    
    def _calculate_tie_strength(self, 
                             ego_network: nx.DiGraph, 
                             person_id: str) -> Dict[str, Any]:
        """
        Calcula a força dos vínculos na rede da pessoa.
        
        Args:
            ego_network: Rede ego-centrada
            person_id: ID da pessoa central
            
        Returns:
            Estatísticas de força dos vínculos
        """
        # Pegar pesos das conexões com a pessoa
        tie_weights = []
        strong_ties = 0
        weak_ties = 0
        
        # Verificar conexões de entrada e saída
        for neighbor in set(ego_network.predecessors(person_id)) | set(ego_network.successors(person_id)):
            # Pegar peso da aresta (média das duas direções se bidirecional)
            in_weight = 0
            out_weight = 0
            
            if ego_network.has_edge(neighbor, person_id):
                in_data = ego_network.get_edge_data(neighbor, person_id)
                in_weight = in_data.get('weight', 0.5)
                
            if ego_network.has_edge(person_id, neighbor):
                out_data = ego_network.get_edge_data(person_id, neighbor)
                out_weight = out_data.get('weight', 0.5)
            
            # Se tem nas duas direções, média; senão, o que tiver
            if in_weight and out_weight:
                weight = (in_weight + out_weight) / 2
            else:
                weight = in_weight + out_weight
            
            tie_weights.append(weight)
            
            # Classificar como forte (>0.7) ou fraco (<0.3)
            if weight > 0.7:
                strong_ties += 1
            elif weight < 0.3:
                weak_ties += 1
        
        # Calcular média
        avg_strength = sum(tie_weights) / len(tie_weights) if tie_weights else 0
        
        return {
            'avg': avg_strength,
            'strong': strong_ties,
            'weak': weak_ties,
            'total': len(tie_weights)
        }
    
    def _calculate_collaborative_value(self, person_id: str) -> Dict[str, float]:
        """
        Calcula o valor gerado por colaborações da pessoa.
        
        Args:
            person_id: ID da pessoa
            
        Returns:
            Estatísticas de valor colaborativo
        """
        collaborations = self.person_collaborations.get(person_id, [])
        
        if not collaborations:
            return {
                'total': 0.0,
                'avg': 0.0,
                'success_rate': 0.0
            }
        
        # Somar valor gerado e taxa de sucesso
        total_value = 0.0
        total_success = 0.0
        
        for collab in collaborations:
            # Valor proporcional ao número de participantes
            participant_value = collab.value_created / len(collab.participants)
            total_value += participant_value
            total_success += collab.success_rating
        
        # Calcular médias
        avg_value = total_value / len(collaborations)
        success_rate = total_success / len(collaborations)
        
        return {
            'total': total_value,
            'avg': avg_value,
            'success_rate': success_rate
        }
    
    def _calculate_social_capital_score(self, metrics: Dict[str, Any]) -> float:
        """
        Calcula uma pontuação agregada de capital social.
        
        Args:
            metrics: Métricas calculadas
            
        Returns:
            Pontuação de capital social (0-1)
        """
        # Pesos para cada componente
        weights = {
            'network_size': 0.15,
            'network_density': 0.10,
            'betweenness_centrality': 0.20,
            'network_diversity': 0.15,
            'avg_tie_strength': 0.15,
            'collab_success_rate': 0.25
        }
        
        # Normalizar métricas para escala 0-1
        normalized = {}
        
        # Tamanho da rede (limite superior estimado: 50)
        normalized['network_size'] = min(metrics['network_size'] / 50.0, 1.0)
        
        # Densidade (já está entre 0-1)
        normalized['network_density'] = metrics['network_density']
        
        # Centralidade de intermediação (já está entre 0-1)
        normalized['betweenness_centrality'] = metrics['betweenness_centrality']
        
        # Diversidade da rede (já está entre 0-1)
        normalized['network_diversity'] = metrics['network_diversity']
        
        # Força média dos vínculos (já está entre 0-1)
        normalized['avg_tie_strength'] = metrics['avg_tie_strength']
        
        # Taxa de sucesso em colaboração (já está entre 0-1)
        normalized['collab_success_rate'] = metrics['collab_success_rate']
        
        # Calcular pontuação ponderada
        score = 0.0
        for metric, weight in weights.items():
            score += normalized.get(metric, 0.0) * weight
        
        return score
    
    def identify_brokers(self, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Identifica pessoas que atuam como intermediários estratégicos (brokers).
        
        Args:
            threshold: Limiar para considerar alguém um broker
            
        Returns:
            Lista de brokers identificados
        """
        if not self.influence_network:
            raise ValueError("Rede de influência é necessária para análise")
        
        # Calcular centralidade de intermediação para toda a rede
        betweenness = nx.betweenness_centrality(self.influence_network.graph)
        
        # Ordenar por centralidade
        sorted_betweenness = sorted(
            betweenness.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Identificar brokers (alta centralidade de intermediação)
        if sorted_betweenness:
            max_betweenness = sorted_betweenness[0][1]
            threshold_value = max_betweenness * threshold
            
            brokers = [
                {
                    'person_id': person_id,
                    'betweenness': value,
                    'normalized_score': value / max_betweenness if max_betweenness > 0 else 0
                }
                for person_id, value in sorted_betweenness
                if value >= threshold_value
            ]
            
            return brokers
        
        return []
    
    def identify_collaboration_clusters(self, min_size: int = 3) -> List[Dict[str, Any]]:
        """
        Identifica grupos de pessoas que colaboram frequentemente.
        
        Args:
            min_size: Tamanho mínimo para um cluster
            
        Returns:
            Lista de clusters identificados
        """
        # Construir grafo de colaboração
        collab_graph = nx.Graph()
        
        # Adicionar nós
        for person_id in self.person_collaborations:
            collab_graph.add_node(person_id)
        
        # Adicionar arestas ponderadas pela quantidade de colaborações
        collab_counts = {}
        
        for collab in self.collaborations:
            participants = collab.participants
            for i, p1 in enumerate(participants):
                for p2 in participants[i+1:]:
                    pair = tuple(sorted([p1, p2]))
                    if pair not in collab_counts:
                        collab_counts[pair] = 0
                    collab_counts[pair] += 1
        
        # Adicionar arestas ao grafo
        for (p1, p2), count in collab_counts.items():
            collab_graph.add_edge(p1, p2, weight=count)
        
        # Detectar comunidades
        communities = list(nx.community.greedy_modularity_communities(collab_graph))
        
        # Filtrar por tamanho mínimo e calcular métricas
        clusters = []
        
        for i, community in enumerate(communities):
            if len(community) >= min_size:
                # Extrair subgrafo da comunidade
                subgraph = collab_graph.subgraph(community)
                
                # Calcular força interna (densidade ponderada)
                internal_edges = subgraph.edges(data=True)
                internal_weight = sum(edge[2].get('weight', 1.0) for edge in internal_edges)
                max_edges = len(community) * (len(community) - 1) / 2
                internal_strength = internal_weight / max_edges if max_edges > 0 else 0
                
                # Adicionar à lista
                clusters.append({
                    'id': f"cluster_{i+1}",
                    'members': list(community),
                    'size': len(community),
                    'internal_strength': internal_strength,
                    'max_edge_weight': max(edge[2].get('weight', 0) for edge in internal_edges) if internal_edges else 0
                })
        
        # Ordenar por tamanho e força
        return sorted(clusters, key=lambda x: (x['size'], x['internal_strength']), reverse=True)
    
    def visualize_social_capital(self, 
                              person_id: str,
                              output_path: Optional[Path] = None) -> Path:
        """
        Visualiza o capital social de uma pessoa.
        
        Args:
            person_id: ID da pessoa
            output_path: Caminho para salvar a visualização
            
        Returns:
            Caminho do arquivo salvo
        """
        if person_id not in self.social_capital_metrics:
            # Calcular métricas se não existirem
            self.calculate_social_capital(person_id)
            
        metrics = self.social_capital_metrics[person_id]
        
        # Criar figura
        plt.figure(figsize=(15, 10))
        
        # 1. Gráfico de radar (Perfil de Capital Social)
        plt.subplot(2, 2, 1, polar=True)
        
        # Preparar dados
        categories = [
            'Tamanho da Rede', 
            'Densidade', 
            'Intermediação',
            'Diversidade', 
            'Força de Vínculos', 
            'Sucesso Colaborativo'
        ]
        
        values = [
            min(metrics['network_size'] / 50.0, 1.0),  # Normalizado
            metrics['network_density'],
            metrics['betweenness_centrality'],
            metrics['network_diversity'],
            metrics['avg_tie_strength'],
            metrics['collab_success_rate']
        ]
        
        # Fechar o polígono repetindo o primeiro valor
        values += values[:1]
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        # Plotar
        ax = plt.subplot(2, 2, 1, polar=True)
        ax.plot(angles, values, 'o-', linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        ax.set_thetagrids(np.degrees(angles[:-1]), categories)
        ax.set_ylim(0, 1)
        ax.grid(True)
        plt.title('Perfil de Capital Social', size=14)
        
        # 2. Ego-network (visualização da rede)
        plt.subplot(2, 2, 2)
        
        ego_network = self.influence_network.get_ego_network(person_id, radius=1)
        
        # Layout da rede
        pos = nx.spring_layout(ego_network)
        
        # Tamanho dos nós (ego maior que outros)
        node_sizes = []
        node_colors = []
        labels = {}
        
        for node in ego_network.nodes():
            if node == person_id:
                node_sizes.append(300)
                node_colors.append('red')
                labels[node] = 'EU'
            else:
                node_sizes.append(100)
                node_colors.append('blue')
                labels[node] = ''
        
        # Pesos de arestas para espessura
        edge_widths = []
        for u, v, data in ego_network.edges(data=True):
            edge_widths.append(data.get('weight', 0.5) * 2)
        
        # Plotar rede
        nx.draw_networkx_nodes(ego_network, pos, node_size=node_sizes, node_color=node_colors, alpha=0.8)
        nx.draw_networkx_edges(ego_network, pos, width=edge_widths, alpha=0.5, arrows=True, arrowsize=15)
        nx.draw_networkx_labels(ego_network, pos, labels=labels, font_size=10)
        
        plt.title('Rede de Relacionamentos', size=14)
        plt.axis('off')
        
        # 3. Histórico de colaborações
        plt.subplot(2, 2, 3)
        
        # Agrupar colaborações por trimestre
        collaborations = self.person_collaborations.get(person_id, [])
        quarters = {}
        
        for collab in collaborations:
            # Formato YYYY-Q#
            quarter_key = f"{collab.start_date.year}-Q{(collab.start_date.month-1)//3 + 1}"
            
            if quarter_key not in quarters:
                quarters[quarter_key] = {
                    'count': 0,
                    'value': 0.0,
                    'success': 0.0
                }
                
            quarters[quarter_key]['count'] += 1
            quarters[quarter_key]['value'] += collab.value_created / len(collab.participants)
            quarters[quarter_key]['success'] += collab.success_rating
        
        # Calcular médias
        for q in quarters.values():
            q['success'] = q['success'] / q['count'] if q['count'] > 0 else 0
        
        # Plotar barras de contagem e linha de sucesso
        if quarters:
            sorted_quarters = sorted(quarters.items())
            q_labels = [q[0] for q in sorted_quarters]
            counts = [q[1]['count'] for q in sorted_quarters]
            success = [q[1]['success'] for q in sorted_quarters]
            
            ax1 = plt.subplot(2, 2, 3)
            bars = ax1.bar(q_labels, counts, alpha=0.7, color='skyblue')
            ax1.set_ylabel('Número de Colaborações', color='skyblue')
            ax1.tick_params(axis='y', labelcolor='skyblue')
            ax1.set_xticklabels(q_labels, rotation=45)
            
            ax2 = ax1.twinx()
            line = ax2.plot(q_labels, success, 'ro-', linewidth=2)
            ax2.set_ylabel('Taxa de Sucesso', color='red')
            ax2.tick_params(axis='y', labelcolor='red')
            ax2.set_ylim(0, 1)
            
            plt.title('Histórico de Colaborações', size=14)
        else:
            plt.text(0.5, 0.5, 'Sem dados de colaboração',
                    horizontalalignment='center', verticalalignment='center',
                    transform=plt.gca().transAxes)
        
        # 4. Medidor de capital social
        plt.subplot(2, 2, 4)
        
        score = metrics['social_capital_score']
        
        # Criar um medidor simples
        gauge_img = self._create_gauge_chart(score)
        plt.imshow(gauge_img)
        plt.title(f'Capital Social: {score:.2f}', size=14)
        plt.axis('off')
        
        # Ajustar layout
        plt.tight_layout()
        
        # Salvar figura
        if output_path is None:
            output_path = Path(f'output/capital_social_{person_id}.png')
            
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def _create_gauge_chart(self, value: float) -> np.ndarray:
        """
        Cria uma imagem de medidor para o valor dado.
        
        Args:
            value: Valor entre 0 e 1
            
        Returns:
            Array da imagem gerada
        """
        # Limitar valor
        value = max(0, min(value, 1))
        
        # Criar figura sem margens
        fig = plt.figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Ângulos para o semicírculo
        ang_range = 180
        min_ang = 180
        max_ang = 0
        
        # Calcular ângulo para o valor
        angle = min_ang - value * ang_range
        
        # Desenhar arco de fundo
        arc = plt.matplotlib.patches.Arc(
            (0.5, 0), width=1, height=1, theta1=min_ang, theta2=max_ang,
            linewidth=10, color='lightgray'
        )
        ax.add_patch(arc)
        
        # Desenhar arco de valor
        arc_value = plt.matplotlib.patches.Arc(
            (0.5, 0), width=1, height=1, theta1=angle, theta2=min_ang,
            linewidth=10, color='green' if value > 0.7 else 'orange' if value > 0.3 else 'red'
        )
        ax.add_patch(arc_value)
        
        # Adicionar marcas e texto
        plt.text(0.5, 0.3, f'{int(value*100)}', 
                horizontalalignment='center', verticalalignment='center',
                fontsize=20, fontweight='bold')
        
        # Ajustar limites
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(-0.1, 0.5)
        
        ax.axis('off')
        
        # Capturar figura como imagem
        fig.canvas.draw()
        img = np.array(fig.canvas.renderer.buffer_rgba())
        plt.close(fig)
        
        return img
    
    def generate_social_capital_report(self, 
                                    person_id: str,
                                    output_path: Optional[Path] = None) -> Path:
        """
        Gera um relatório detalhado sobre o capital social.
        
        Args:
            person_id: ID da pessoa
            output_path: Caminho para salvar o relatório
            
        Returns:
            Caminho do relatório salvo
        """
        if person_id not in self.social_capital_metrics:
            # Calcular métricas se não existirem
            self.calculate_social_capital(person_id)
            
        metrics = self.social_capital_metrics[person_id]
        collaborations = self.person_collaborations.get(person_id, [])
        
        # Criar caminho de saída
        if output_path is None:
            output_path = Path(f'output/relatorio_capital_social_{person_id}.txt')
            
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Gerar relatório
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"RELATÓRIO DE CAPITAL SOCIAL\n")
            f.write(f"{'='*50}\n\n")
            
            f.write(f"Pessoa: {person_id}\n")
            f.write(f"Data: {datetime.datetime.now().strftime('%d/%m/%Y')}\n\n")
            
            f.write(f"PONTUAÇÃO DE CAPITAL SOCIAL: {metrics['social_capital_score']:.2f}\n")
            f.write(f"{'-'*50}\n\n")
            
            f.write(f"MÉTRICAS DE REDE\n")
            f.write(f"{'-'*50}\n")
            f.write(f"Tamanho da rede: {metrics['network_size']} contatos\n")
            f.write(f"Densidade da rede: {metrics['network_density']:.2f}\n")
            f.write(f"Centralidade de intermediação: {metrics['betweenness_centrality']:.2f}\n")
            f.write(f"Diversidade da rede: {metrics['network_diversity']:.2f}\n")
            f.write(f"Força média dos vínculos: {metrics['avg_tie_strength']:.2f}\n")
            f.write(f"Vínculos fortes: {metrics['strong_ties']}\n")
            f.write(f"Vínculos fracos: {metrics['weak_ties']}\n\n")
            
            f.write(f"PADRÕES COLABORATIVOS\n")
            f.write(f"{'-'*50}\n")
            f.write(f"Total de colaborações: {len(collaborations)}\n")
            f.write(f"Valor total gerado: {metrics['total_value_created']:.2f}\n")
            f.write(f"Valor médio por colaboração: {metrics['avg_value_per_collab']:.2f}\n")
            f.write(f"Taxa de sucesso em colaborações: {metrics['collab_success_rate']:.2f}\n\n")
            
            # Resumo das colaborações
            if collaborations:
                f.write(f"COLABORAÇÕES RECENTES\n")
                f.write(f"{'-'*50}\n")
                
                # Ordenar por data
                recent_collabs = sorted(
                    collaborations, 
                    key=lambda x: x.start_date,
                    reverse=True
                )[:5]  # Top 5 mais recentes
                
                for i, collab in enumerate(recent_collabs, 1):
                    f.write(f"{i}. {collab.collab_type.title()} (ID: {collab.collab_id})\n")
                    f.write(f"   Data: {collab.start_date.strftime('%d/%m/%Y')}\n")
                    f.write(f"   Participantes: {len(collab.participants)}\n")
                    f.write(f"   Valor gerado: {collab.value_created:.2f}\n")
                    f.write(f"   Sucesso: {collab.success_rating:.2f}\n")
                    f.write("\n")
            
            f.write(f"RECOMENDAÇÕES\n")
            f.write(f"{'-'*50}\n")
            
            # Recomendações baseadas nas métricas
            if metrics['network_diversity'] < 0.5:
                f.write("1. Diversificar contatos para acessar diferentes grupos e departamentos\n")
            elif metrics['network_size'] < 20:
                f.write("1. Expandir rede de contatos para aumentar alcance e oportunidades\n")
            else:
                f.write("1. Manter equilíbrio atual entre tamanho e diversidade da rede\n")
                
            if metrics['weak_ties'] < metrics['strong_ties'] / 2:
                f.write("2. Desenvolver mais vínculos fracos para acesso a novas informações\n")
            elif metrics['strong_ties'] < 5:
                f.write("2. Fortalecer vínculos-chave para melhorar suporte e confiança\n")
            else:
                f.write("2. Balancear entre manutenção de vínculos fortes e desenvolvimento de novos contatos\n")
                
            if metrics['betweenness_centrality'] < 0.3:
                f.write("3. Buscar posições de intermediação entre grupos diferentes\n")
            else:
                f.write("3. Capitalizar posição estratégica de intermediação para gerar valor\n")
            
            # Adicionar visualização
            if output_path.suffix == '.txt':
                viz_path = output_path.with_suffix('.png')
                self.visualize_social_capital(person_id, viz_path)
                f.write(f"\nVisualização salva em: {viz_path}\n")
        
        return output_path 