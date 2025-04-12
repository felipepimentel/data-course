"""
Analisador de Rede de Influência.

Identifica relações de influência entre pessoas na organização e
constrói grafos direcionados para análise de impacto.
"""
import datetime
import math
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from pathlib import Path
import community  # python-louvain

from peopleanalytics.data_pipeline import DataPipeline


@dataclass
class InfluenceRelation:
    """Relação de influência entre duas pessoas."""
    source_id: str  # ID da pessoa de origem
    target_id: str  # ID da pessoa de destino
    weight: float  # Força da influência (0-1)
    relation_type: str  # Tipo de relação: mentor, peer, manager, etc.
    channels: List[str]  # Canais de influência: conhecimento, suporte, recursos, etc.
    timestamp: datetime.datetime
    context: Dict[str, Any]  # Metadados adicionais


class InfluenceNetwork:
    """
    Analisador de Rede de Influência organizacional.
    
    Constrói e analisa grafos de influência entre pessoas, permitindo
    identificar hubs de conhecimento, multiplicadores de impacto e
    padrões de difusão na organização.
    """
    
    def __init__(self, data_pipeline: Optional[DataPipeline] = None):
        """
        Inicializa o analisador de rede de influência.
        
        Args:
            data_pipeline: Pipeline de dados opcional para carregar dados existentes
        """
        self.data_pipeline = data_pipeline
        self.relations = []  # Lista de relações de influência
        self.graph = nx.DiGraph()  # Grafo direcionado de influência
        self.person_attributes = {}  # Atributos das pessoas (nós)
        
    def load_data(self) -> bool:
        """
        Carrega dados de relações de influência do pipeline de dados.
        
        Returns:
            True se os dados foram carregados com sucesso, False caso contrário
        """
        if not self.data_pipeline:
            return False
            
        try:
            # Carregar relações do pipeline
            relations_data = self.data_pipeline.load_influence_relations()
            
            # Carregar atributos das pessoas
            self.person_attributes = self.data_pipeline.load_person_attributes()
            
            # Converter para objetos InfluenceRelation
            self.relations = []
            for rel in relations_data:
                relation = InfluenceRelation(
                    source_id=rel['source_id'],
                    target_id=rel['target_id'],
                    weight=float(rel.get('weight', 0.5)),
                    relation_type=rel.get('relation_type', 'unspecified'),
                    channels=rel.get('channels', []),
                    timestamp=datetime.datetime.fromisoformat(
                        rel.get('timestamp', datetime.datetime.now().isoformat())
                    ),
                    context=rel.get('context', {})
                )
                self.relations.append(relation)
            
            # Construir grafo
            self._build_graph()
            
            return True
            
        except Exception as e:
            print(f"Erro ao carregar dados de influência: {str(e)}")
            return False
    
    def add_relation(self, 
                    source_id: str, 
                    target_id: str,
                    weight: float = 0.5,
                    relation_type: str = 'peer',
                    channels: Optional[List[str]] = None) -> InfluenceRelation:
        """
        Adiciona uma nova relação de influência.
        
        Args:
            source_id: ID da pessoa de origem (influenciadora)
            target_id: ID da pessoa de destino (influenciada)
            weight: Força da influência (0-1)
            relation_type: Tipo de relação
            channels: Canais de influência
            
        Returns:
            Nova relação de influência criada
        """
        # Validar peso
        if not 0 <= weight <= 1:
            raise ValueError("Peso da influência deve estar entre 0 e 1")
            
        # Criar relação
        relation = InfluenceRelation(
            source_id=source_id,
            target_id=target_id,
            weight=weight,
            relation_type=relation_type,
            channels=channels or [],
            timestamp=datetime.datetime.now(),
            context={}
        )
        
        # Adicionar à lista
        self.relations.append(relation)
        
        # Atualizar grafo
        self._add_relation_to_graph(relation)
        
        # Salvar no pipeline se disponível
        if self.data_pipeline:
            relation_data = {
                'source_id': source_id,
                'target_id': target_id,
                'weight': weight,
                'relation_type': relation_type,
                'channels': channels or [],
                'timestamp': relation.timestamp.isoformat(),
                'context': {}
            }
            
            self.data_pipeline.save_influence_relation(relation_data)
        
        return relation
    
    def _build_graph(self):
        """Constrói o grafo de influência a partir das relações."""
        # Limpar grafo existente
        self.graph = nx.DiGraph()
        
        # Adicionar atributos às pessoas (nós)
        for person_id, attrs in self.person_attributes.items():
            self.graph.add_node(person_id, **attrs)
        
        # Adicionar relações (arestas)
        for relation in self.relations:
            self._add_relation_to_graph(relation)
    
    def _add_relation_to_graph(self, relation: InfluenceRelation):
        """
        Adiciona uma relação ao grafo.
        
        Args:
            relation: Relação a ser adicionada
        """
        # Garantir que os nós existem
        if relation.source_id not in self.graph:
            self.graph.add_node(relation.source_id)
            
        if relation.target_id not in self.graph:
            self.graph.add_node(relation.target_id)
        
        # Adicionar aresta com atributos
        self.graph.add_edge(
            relation.source_id,
            relation.target_id,
            weight=relation.weight,
            relation_type=relation.relation_type,
            channels=relation.channels,
            timestamp=relation.timestamp
        )
    
    def get_ego_network(self, person_id: str, radius: int = 2) -> nx.DiGraph:
        """
        Obtém a rede ego-centrada para uma pessoa.
        
        Args:
            person_id: ID da pessoa central
            radius: Raio da rede ego (em passos)
            
        Returns:
            Subgrafo representando a rede ego
        """
        if person_id not in self.graph:
            # Pessoa não está na rede
            return nx.DiGraph()
        
        # Inicializar conjunto de nós
        nodes = {person_id}
        
        # Expandir para vizinhos dentro do raio
        current_layer = {person_id}
        for _ in range(radius):
            next_layer = set()
            for node in current_layer:
                # Adicionar vizinhos de saída (quem a pessoa influencia)
                next_layer.update(self.graph.successors(node))
                # Adicionar vizinhos de entrada (quem influencia a pessoa)
                next_layer.update(self.graph.predecessors(node))
            
            # Remover nós já visitados
            next_layer = next_layer - nodes
            # Adicionar à rede ego
            nodes.update(next_layer)
            # Atualizar camada atual
            current_layer = next_layer
            
            if not current_layer:
                # Se não há mais nós para explorar, interrompe
                break
        
        # Extrair subgrafo
        return self.graph.subgraph(nodes).copy()
    
    def calculate_centrality_metrics(self, subgraph: Optional[nx.DiGraph] = None) -> Dict[str, Dict[str, float]]:
        """
        Calcula métricas de centralidade para o grafo.
        
        Args:
            subgraph: Subgrafo a ser analisado (se None, usa grafo completo)
            
        Returns:
            Dicionário com métricas de centralidade por pessoa
        """
        graph = subgraph if subgraph is not None else self.graph
        
        # Calcular diferentes métricas de centralidade
        metrics = {}
        
        # Se o grafo está vazio, retornar dicionário vazio
        if len(graph) == 0:
            return metrics
        
        # Degree Centrality (quem tem mais conexões diretas)
        in_degree_centrality = nx.in_degree_centrality(graph)  # Quem é mais influenciado
        out_degree_centrality = nx.out_degree_centrality(graph)  # Quem mais influencia
        
        # Betweenness Centrality (quem está nos caminhos mais curtos)
        try:
            betweenness = nx.betweenness_centrality(graph, weight='weight')
        except:
            betweenness = {node: 0.0 for node in graph.nodes()}
        
        # Eigenvector Centrality (quem está conectado a nós importantes)
        try:
            eigenvector = nx.eigenvector_centrality(graph, weight='weight', max_iter=1000)
        except:
            eigenvector = {node: 0.0 for node in graph.nodes()}
        
        # PageRank (influência considerando pesos)
        try:
            pagerank = nx.pagerank(graph, weight='weight')
        except:
            pagerank = {node: 0.0 for node in graph.nodes()}
        
        # Consolidar métricas
        for node in graph.nodes():
            metrics[node] = {
                'in_degree': in_degree_centrality.get(node, 0.0),
                'out_degree': out_degree_centrality.get(node, 0.0),
                'betweenness': betweenness.get(node, 0.0),
                'eigenvector': eigenvector.get(node, 0.0),
                'pagerank': pagerank.get(node, 0.0),
                # Métrica composta personalizada
                'influence_score': (
                    0.3 * out_degree_centrality.get(node, 0.0) +
                    0.3 * betweenness.get(node, 0.0) +
                    0.4 * pagerank.get(node, 0.0)
                )
            }
        
        return metrics
    
    def identify_key_influencers(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Identifica as pessoas mais influentes na rede.
        
        Args:
            top_n: Número de influenciadores a retornar
            
        Returns:
            Lista de influenciadores com suas métricas
        """
        # Calcular métricas
        metrics = self.calculate_centrality_metrics()
        
        # Ordenar por influence_score
        influencers = [
            {
                'person_id': person_id,
                'metrics': person_metrics,
                'attributes': self.person_attributes.get(person_id, {})
            }
            for person_id, person_metrics in metrics.items()
        ]
        
        influencers.sort(key=lambda x: x['metrics']['influence_score'], reverse=True)
        
        return influencers[:top_n]
    
    def identify_communities(self) -> Dict[str, int]:
        """
        Identifica comunidades dentro da rede usando o algoritmo Louvain.
        
        Returns:
            Dicionário mapeando person_id para comunidade
        """
        # Converter para grafo não-direcionado para detecção de comunidades
        undirected_graph = self.graph.to_undirected()
        
        # Aplicar algoritmo Louvain
        try:
            communities = community.best_partition(undirected_graph, weight='weight')
        except Exception as e:
            print(f"Erro ao detectar comunidades: {str(e)}")
            # Fallback simples
            communities = {node: 0 for node in self.graph.nodes()}
        
        return communities
    
    def calculate_person_impact(self, person_id: str) -> Dict[str, Any]:
        """
        Calcula o impacto de uma pessoa na rede.
        
        Args:
            person_id: ID da pessoa
            
        Returns:
            Dicionário com métricas de impacto
        """
        if person_id not in self.graph:
            return {
                'influence_score': 0.0,
                'reach': 0,
                'affected_communities': 0,
                'knowledge_flow': 0.0,
                'overall_impact': "Não encontrado na rede"
            }
        
        # Obter ego-network para cálculos
        ego_network = self.get_ego_network(person_id)
        
        # Calcular métricas centrais
        centrality_metrics = self.calculate_centrality_metrics(ego_network)
        person_metrics = centrality_metrics.get(person_id, {})
        
        # Calcular alcance (quantas pessoas são alcançadas)
        influenced_nodes = set(nx.descendants(self.graph, person_id))
        reach = len(influenced_nodes)
        
        # Calcular comunidades afetadas
        communities = self.identify_communities()
        person_community = communities.get(person_id, -1)
        affected_communities = set()
        
        for node in influenced_nodes:
            community_id = communities.get(node, -1)
            if community_id != -1 and community_id != person_community:
                affected_communities.add(community_id)
        
        # Fluxo de conhecimento (baseado no PageRank)
        pagerank = nx.pagerank(self.graph, weight='weight')
        knowledge_flow = pagerank.get(person_id, 0.0) * 100  # Escalar para percentual
        
        # Determinar impacto geral
        influence_score = person_metrics.get('influence_score', 0.0)
        
        if influence_score > 0.8:
            overall_impact = "Influenciador Organizacional Crítico"
        elif influence_score > 0.6:
            overall_impact = "Forte Influenciador de Múltiplas Comunidades"
        elif influence_score > 0.4:
            overall_impact = "Influenciador Significativo"
        elif influence_score > 0.2:
            overall_impact = "Influenciador Moderado"
        else:
            overall_impact = "Influência Limitada"
        
        return {
            'influence_score': influence_score,
            'reach': reach,
            'affected_communities': len(affected_communities),
            'knowledge_flow': knowledge_flow,
            'overall_impact': overall_impact
        }
    
    def visualize_network(self, 
                         person_id: Optional[str] = None,
                         highlight_communities: bool = True,
                         output_path: Optional[Path] = None,
                         figsize: Tuple[int, int] = (14, 10)) -> Path:
        """
        Visualiza a rede de influência.
        
        Args:
            person_id: ID da pessoa para centralizar (se None, mostra rede completa)
            highlight_communities: Se deve destacar comunidades com cores
            output_path: Caminho para salvar a visualização (opcional)
            figsize: Tamanho da figura
            
        Returns:
            Caminho para a visualização gerada
        """
        # Determinar grafo a visualizar
        if person_id:
            graph = self.get_ego_network(person_id)
            title = f"Rede de Influência: {person_id}"
        else:
            graph = self.graph
            title = "Rede de Influência Organizacional"
        
        # Se grafo vazio, criar visualização mínima
        if len(graph) == 0:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, "Rede vazia ou pessoa não encontrada",
                   ha='center', va='center', fontsize=14)
            ax.axis('off')
        else:
            fig, ax = plt.subplots(figsize=figsize)
            
            # Calcular layout
            pos = nx.spring_layout(graph, k=0.15, iterations=100, seed=42)
            
            # Configurar nós
            node_size = []
            for node in graph.nodes():
                # Tamanho baseado em métricas de centralidade
                if person_id and node == person_id:
                    # Pessoa central maior
                    node_size.append(800)
                else:
                    # Outros nós baseados em grau
                    in_degree = graph.in_degree(node, weight='weight')
                    out_degree = graph.out_degree(node, weight='weight')
                    size = 100 + 50 * (in_degree + out_degree)
                    node_size.append(size)
            
            # Configurar cores dos nós por comunidade
            if highlight_communities:
                communities = self.identify_communities()
                community_colors = {}
                
                # Mapear comunidades para cores
                unique_communities = set(communities.values())
                colormap = plt.cm.rainbow
                colors = [colormap(i / len(unique_communities)) for i in range(len(unique_communities))]
                
                for i, comm in enumerate(unique_communities):
                    community_colors[comm] = colors[i]
                
                # Gerar lista de cores na ordem dos nós
                node_colors = [community_colors[communities.get(node, 0)] for node in graph.nodes()]
            else:
                # Cor padrão
                node_colors = ['#1f78b4' for _ in graph.nodes()]
                
                # Se tem person_id, destacar
                if person_id:
                    for i, node in enumerate(graph.nodes()):
                        if node == person_id:
                            node_colors[i] = '#e31a1c'  # Vermelho para destaque
            
            # Configurar arestas
            edge_width = []
            for u, v, data in graph.edges(data=True):
                weight = data.get('weight', 0.5)
                edge_width.append(weight * 3)
            
            # Desenhar grafo
            nx.draw_networkx_nodes(graph, pos, 
                                  node_size=node_size, 
                                  node_color=node_colors, 
                                  alpha=0.8)
            
            nx.draw_networkx_edges(graph, pos, 
                                  width=edge_width, 
                                  alpha=0.5, 
                                  edge_color='gray',
                                  arrows=True, 
                                  arrowsize=15, 
                                  arrowstyle='-|>')
            
            # Adicionar labels
            labels = {}
            for node in graph.nodes():
                name = self.person_attributes.get(node, {}).get('name', node)
                # Truncar nomes longos
                if len(name) > 15:
                    name = name[:12] + '...'
                labels[node] = name
                
            nx.draw_networkx_labels(graph, pos, labels, font_size=10, font_weight='bold')
            
            # Adicionar legenda para comunidades
            if highlight_communities:
                legend_elements = []
                for comm, color in community_colors.items():
                    from matplotlib.lines import Line2D
                    legend_elements.append(
                        Line2D([0], [0], marker='o', color='w', markerfacecolor=color, 
                              markersize=10, label=f'Comunidade {comm}')
                    )
                ax.legend(handles=legend_elements, loc='upper right')
            
            # Configurar título e limites
            plt.title(title, fontsize=16)
            plt.axis('off')
        
        # Salvar figura
        if output_path:
            plt.savefig(output_path, bbox_inches='tight')
        else:
            # Gerar um nome padrão na pasta output
            output_dir = Path("output") / "influence_network"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            if person_id:
                filename = f"{person_id}_influence_network_{datetime.datetime.now().strftime('%Y%m%d')}.png"
            else:
                filename = f"organization_influence_network_{datetime.datetime.now().strftime('%Y%m%d')}.png"
                
            output_file = output_dir / filename
            plt.savefig(output_file, bbox_inches='tight')
            plt.close()
            
            return output_file
    
    def generate_person_report(self, person_id: str, output_path: Optional[Path] = None) -> Path:
        """
        Gera um relatório completo de influência para uma pessoa.
        
        Args:
            person_id: ID da pessoa
            output_path: Caminho para salvar o relatório (opcional)
            
        Returns:
            Caminho para o relatório gerado
        """
        # Configurar caminho de saída
        if output_path:
            report_file = output_path
        else:
            output_dir = Path("output") / "influence_network"
            output_dir.mkdir(parents=True, exist_ok=True)
            report_file = output_dir / f"{person_id}_influence_report_{datetime.datetime.now().strftime('%Y%m%d')}.md"
        
        # Obter dados da pessoa
        person_data = self.person_attributes.get(person_id, {})
        person_name = person_data.get('name', person_id)
        
        # Calcular impacto
        impact = self.calculate_person_impact(person_id)
        
        # Obter ego-network para cálculos adicionais
        ego_network = self.get_ego_network(person_id)
        
        # Identificar principais influenciadores e influenciados
        influencers = []
        influenced = []
        
        for node in ego_network.nodes():
            if node == person_id:
                continue
                
            # Verificar se este nó influencia a pessoa
            if ego_network.has_edge(node, person_id):
                weight = ego_network.get_edge_data(node, person_id).get('weight', 0.0)
                node_data = self.person_attributes.get(node, {})
                node_name = node_data.get('name', node)
                
                influencers.append({
                    'id': node,
                    'name': node_name,
                    'weight': weight,
                    'attributes': node_data
                })
            
            # Verificar se a pessoa influencia este nó
            if ego_network.has_edge(person_id, node):
                weight = ego_network.get_edge_data(person_id, node).get('weight', 0.0)
                node_data = self.person_attributes.get(node, {})
                node_name = node_data.get('name', node)
                
                influenced.append({
                    'id': node,
                    'name': node_name,
                    'weight': weight,
                    'attributes': node_data
                })
        
        # Ordenar por peso
        influencers.sort(key=lambda x: x['weight'], reverse=True)
        influenced.sort(key=lambda x: x['weight'], reverse=True)
        
        # Gerar visualização da rede
        network_viz = self.visualize_network(person_id, highlight_communities=True)
        
        # Escrever relatório
        with open(report_file, 'w') as f:
            f.write(f"# Relatório de Influência: {person_name}\n\n")
            f.write(f"Data: {datetime.datetime.now().strftime('%d/%m/%Y')}\n\n")
            
            f.write("## Resumo de Impacto\n\n")
            f.write(f"**Pontuação de Influência:** {impact['influence_score']:.2f}/1.0\n\n")
            f.write(f"**Classificação:** {impact['overall_impact']}\n\n")
            f.write(f"**Alcance:** {impact['reach']} pessoas\n\n")
            f.write(f"**Comunidades Afetadas:** {impact['affected_communities']}\n\n")
            f.write(f"**Fluxo de Conhecimento:** {impact['knowledge_flow']:.2f}%\n\n")
            
            f.write("## Pessoas que Influenciam\n\n")
            if influencers:
                f.write("| Pessoa | Força da Influência | Departamento |\n")
                f.write("|--------|---------------------|-------------|\n")
                for inf in influencers[:10]:  # Top 10
                    dept = inf['attributes'].get('department', 'N/A')
                    f.write(f"| {inf['name']} | {inf['weight']:.2f} | {dept} |\n")
            else:
                f.write("Nenhuma influência de entrada identificada.\n")
            
            f.write("\n## Pessoas Influenciadas\n\n")
            if influenced:
                f.write("| Pessoa | Força da Influência | Departamento |\n")
                f.write("|--------|---------------------|-------------|\n")
                for inf in influenced[:10]:  # Top 10
                    dept = inf['attributes'].get('department', 'N/A')
                    f.write(f"| {inf['name']} | {inf['weight']:.2f} | {dept} |\n")
            else:
                f.write("Nenhuma influência de saída identificada.\n")
            
            f.write("\n## Rede de Influência\n\n")
            f.write(f"![Rede de Influência]({network_viz.name})\n\n")
            
            f.write("## Recomendações\n\n")
            
            # Gerar recomendações baseadas na análise
            if impact['influence_score'] < 0.3:
                f.write("1. **Expandir rede de contatos:** Buscar ativamente conexões além do departamento atual\n")
                f.write("2. **Participar de projetos cross-funcionais:** Aumentar visibilidade em diferentes áreas\n")
                f.write("3. **Compartilhar conhecimento:** Criar conteúdo ou conduzir workshops em áreas de expertise\n")
            elif impact['influence_score'] < 0.6:
                f.write("1. **Fortalecer conexões existentes:** Aprofundar relacionamentos com influenciadores-chave\n")
                f.write("2. **Facilitar conexões:** Atuar como ponte entre diferentes grupos da organização\n")
                f.write("3. **Buscar posições de liderança informal:** Coordenar iniciativas ou comunidades de prática\n")
            else:
                f.write("1. **Desenvolver sucessores:** Transferir conhecimento a pessoas de alto potencial\n")
                f.write("2. **Alavancar influência para iniciativas estratégicas:** Mobilizar a rede para objetivos organizacionais\n")
                f.write("3. **Mentorar influenciadores emergentes:** Multiplicar impacto através de outros líderes\n")
        
        return report_file 