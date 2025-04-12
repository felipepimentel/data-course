"""
Difusão de Conhecimento na Rede de Influência.

Analisa como o conhecimento se difunde pela organização a partir de indivíduos,
identificando caminhos de propagação, barreiras e aceleradores.
"""
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx
import seaborn as sns
from typing import List, Dict, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass
from pathlib import Path
import random

from peopleanalytics.data_pipeline import DataPipeline
from peopleanalytics.talent_development.influence_network.network_analyzer import InfluenceNetwork


@dataclass
class KnowledgeAsset:
    """Representa um elemento de conhecimento dentro da organização."""
    asset_id: str
    title: str 
    description: str
    knowledge_area: str
    creator_id: str
    creation_date: datetime.datetime
    expertise_level: str  # 'básico', 'intermediário', 'avançado', 'especialista'
    format: str  # 'documento', 'vídeo', 'apresentação', 'código', etc.
    tags: List[str]
    visibility: str  # 'público', 'time', 'departamento', 'privado'
    access_count: int = 0
    engagement_score: float = 0.0
    validation_score: float = 0.0
    metadata: Dict[str, Any] = None


@dataclass
class KnowledgeTransfer:
    """Representa uma transferência de conhecimento entre duas pessoas."""
    transfer_id: str
    asset_id: str
    source_id: str
    target_id: str
    transfer_date: datetime.datetime
    transfer_type: str  # 'compartilhamento', 'mentoria', 'treinamento', etc.
    effectiveness: float = 0.0  # 0-1, quanto do conhecimento foi efetivamente absorvido
    context: Dict[str, Any] = None


class KnowledgeDiffusion:
    """
    Analisa como o conhecimento se difunde e propaga pela organização.
    
    Utiliza modelos de difusão para mapear como conhecimentos específicos
    se propagam na rede, identificando:
    - Aceleradores de difusão
    - Barreiras de difusão
    - Tempo médio de propagação
    - Padrões de adoção (curva-S)
    - Lacunas de conhecimento
    """
    
    def __init__(self, 
                influence_network: Optional[InfluenceNetwork] = None,
                data_pipeline: Optional[DataPipeline] = None):
        """
        Inicializa o analisador de difusão de conhecimento.
        
        Args:
            influence_network: Rede de influência para análise
            data_pipeline: Pipeline de dados opcional para carregar dados existentes
        """
        self.influence_network = influence_network
        self.data_pipeline = data_pipeline
        self.knowledge_assets = {}  # asset_id -> KnowledgeAsset
        self.knowledge_transfers = []  # Lista de transferências
        self.person_knowledge = {}  # person_id -> {asset_id -> nível_domínio (0-1)}
        self.diffusion_simulations = {}  # asset_id -> resultados de simulação
        
    def load_data(self) -> bool:
        """
        Carrega dados de conhecimentos e transferências.
        
        Returns:
            True se os dados foram carregados com sucesso, False caso contrário
        """
        if not self.data_pipeline:
            return False
            
        try:
            # Carregar ativos de conhecimento
            assets_data = self.data_pipeline.load_knowledge_assets()
            
            # Converter para objetos KnowledgeAsset
            self.knowledge_assets = {}
            for asset in assets_data:
                knowledge_asset = KnowledgeAsset(
                    asset_id=asset['id'],
                    title=asset['title'],
                    description=asset.get('description', ''),
                    knowledge_area=asset.get('area', 'Geral'),
                    creator_id=asset['creator_id'],
                    creation_date=datetime.datetime.fromisoformat(
                        asset.get('creation_date', datetime.datetime.now().isoformat())
                    ),
                    expertise_level=asset.get('expertise_level', 'intermediário'),
                    format=asset.get('format', 'documento'),
                    tags=asset.get('tags', []),
                    visibility=asset.get('visibility', 'público'),
                    access_count=int(asset.get('access_count', 0)),
                    engagement_score=float(asset.get('engagement_score', 0.0)),
                    validation_score=float(asset.get('validation_score', 0.0)),
                    metadata=asset.get('metadata', {})
                )
                self.knowledge_assets[asset['id']] = knowledge_asset
            
            # Carregar transferências de conhecimento
            transfers_data = self.data_pipeline.load_knowledge_transfers()
            
            # Converter para objetos KnowledgeTransfer
            self.knowledge_transfers = []
            for transfer in transfers_data:
                knowledge_transfer = KnowledgeTransfer(
                    transfer_id=transfer['id'],
                    asset_id=transfer['asset_id'],
                    source_id=transfer['source_id'],
                    target_id=transfer['target_id'],
                    transfer_date=datetime.datetime.fromisoformat(
                        transfer.get('transfer_date', datetime.datetime.now().isoformat())
                    ),
                    transfer_type=transfer.get('transfer_type', 'compartilhamento'),
                    effectiveness=float(transfer.get('effectiveness', 0.5)),
                    context=transfer.get('context', {})
                )
                self.knowledge_transfers.append(knowledge_transfer)
            
            # Carregar mapeamento de conhecimento das pessoas
            self.person_knowledge = self.data_pipeline.load_person_knowledge()
            
            return True
            
        except Exception as e:
            print(f"Erro ao carregar dados de conhecimento: {str(e)}")
            return False
    
    def add_knowledge_asset(self, 
                          title: str,
                          description: str,
                          knowledge_area: str,
                          creator_id: str,
                          expertise_level: str = 'intermediário',
                          format: str = 'documento',
                          tags: Optional[List[str]] = None,
                          visibility: str = 'público',
                          metadata: Optional[Dict[str, Any]] = None) -> KnowledgeAsset:
        """
        Adiciona um novo ativo de conhecimento.
        
        Args:
            title: Título do conhecimento
            description: Descrição detalhada
            knowledge_area: Área de conhecimento
            creator_id: ID da pessoa criadora
            expertise_level: Nível de expertise necessário
            format: Formato do conteúdo
            tags: Tags para categorização
            visibility: Visibilidade do conteúdo
            metadata: Metadados adicionais
            
        Returns:
            Novo ativo de conhecimento criado
        """
        # Criar ID único
        asset_id = f"k_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{creator_id}"
        
        # Criar ativo
        asset = KnowledgeAsset(
            asset_id=asset_id,
            title=title,
            description=description,
            knowledge_area=knowledge_area,
            creator_id=creator_id,
            creation_date=datetime.datetime.now(),
            expertise_level=expertise_level,
            format=format,
            tags=tags or [],
            visibility=visibility,
            access_count=0,
            engagement_score=0.0,
            validation_score=0.0,
            metadata=metadata or {}
        )
        
        # Adicionar ao dicionário
        self.knowledge_assets[asset_id] = asset
        
        # Atualizar conhecimento do criador
        if creator_id not in self.person_knowledge:
            self.person_knowledge[creator_id] = {}
        self.person_knowledge[creator_id][asset_id] = 1.0  # Criador tem domínio total
        
        # Salvar no pipeline se disponível
        if self.data_pipeline:
            asset_data = {
                'id': asset_id,
                'title': title,
                'description': description,
                'area': knowledge_area,
                'creator_id': creator_id,
                'creation_date': asset.creation_date.isoformat(),
                'expertise_level': expertise_level,
                'format': format,
                'tags': tags or [],
                'visibility': visibility,
                'access_count': 0,
                'engagement_score': 0.0,
                'validation_score': 0.0,
                'metadata': metadata or {}
            }
            
            self.data_pipeline.save_knowledge_asset(asset_data)
            
            # Atualizar mapeamento de conhecimento da pessoa
            self.data_pipeline.update_person_knowledge(creator_id, {asset_id: 1.0})
        
        return asset
    
    def record_knowledge_transfer(self,
                                asset_id: str,
                                source_id: str,
                                target_id: str,
                                transfer_type: str = 'compartilhamento',
                                effectiveness: float = 0.5,
                                context: Optional[Dict[str, Any]] = None) -> KnowledgeTransfer:
        """
        Registra uma transferência de conhecimento entre pessoas.
        
        Args:
            asset_id: ID do ativo de conhecimento
            source_id: ID da pessoa fonte
            target_id: ID da pessoa destino
            transfer_type: Tipo de transferência
            effectiveness: Efetividade da transferência (0-1)
            context: Contexto adicional
            
        Returns:
            Transferência de conhecimento registrada
        """
        # Validar parâmetros
        if asset_id not in self.knowledge_assets:
            raise ValueError(f"Ativo de conhecimento {asset_id} não encontrado")
            
        if not 0 <= effectiveness <= 1:
            raise ValueError("Efetividade deve estar entre 0 e 1")
        
        # Criar ID único
        transfer_id = f"kt_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{source_id}_{target_id}"
        
        # Criar transferência
        transfer = KnowledgeTransfer(
            transfer_id=transfer_id,
            asset_id=asset_id,
            source_id=source_id,
            target_id=target_id,
            transfer_date=datetime.datetime.now(),
            transfer_type=transfer_type,
            effectiveness=effectiveness,
            context=context or {}
        )
        
        # Adicionar à lista
        self.knowledge_transfers.append(transfer)
        
        # Atualizar conhecimento do destinatário
        source_knowledge = self.person_knowledge.get(source_id, {}).get(asset_id, 0.0)
        
        if target_id not in self.person_knowledge:
            self.person_knowledge[target_id] = {}
            
        # Novo conhecimento = max(atual, fonte * efetividade)
        current_knowledge = self.person_knowledge.get(target_id, {}).get(asset_id, 0.0)
        transferred_knowledge = source_knowledge * effectiveness
        new_knowledge = max(current_knowledge, transferred_knowledge)
        
        self.person_knowledge[target_id][asset_id] = new_knowledge
        
        # Salvar no pipeline se disponível
        if self.data_pipeline:
            transfer_data = {
                'id': transfer_id,
                'asset_id': asset_id,
                'source_id': source_id,
                'target_id': target_id,
                'transfer_date': transfer.transfer_date.isoformat(),
                'transfer_type': transfer_type,
                'effectiveness': effectiveness,
                'context': context or {}
            }
            
            self.data_pipeline.save_knowledge_transfer(transfer_data)
            
            # Atualizar mapeamento de conhecimento da pessoa
            self.data_pipeline.update_person_knowledge(target_id, {asset_id: new_knowledge})
        
        return transfer
    
    def calculate_knowledge_coverage(self, asset_id: str) -> Dict[str, Any]:
        """
        Calcula a cobertura de um conhecimento na organização.
        
        Args:
            asset_id: ID do ativo de conhecimento
            
        Returns:
            Estatísticas de cobertura do conhecimento
        """
        if asset_id not in self.knowledge_assets:
            raise ValueError(f"Ativo de conhecimento {asset_id} não encontrado")
        
        # Contar pessoas com algum nível de conhecimento
        people_with_knowledge = 0
        total_people = 0
        knowledge_levels = []
        
        for person_id, knowledge in self.person_knowledge.items():
            total_people += 1
            
            if asset_id in knowledge and knowledge[asset_id] > 0:
                people_with_knowledge += 1
                knowledge_levels.append(knowledge[asset_id])
        
        if not knowledge_levels:
            return {
                'asset_id': asset_id,
                'title': self.knowledge_assets[asset_id].title,
                'coverage_percentage': 0.0,
                'avg_knowledge_level': 0.0,
                'max_knowledge_level': 0.0,
                'min_knowledge_level': 0.0,
                'std_knowledge_level': 0.0,
                'people_with_knowledge': 0,
                'total_people': total_people
            }
        
        # Calcular estatísticas
        coverage = people_with_knowledge / total_people if total_people > 0 else 0
        avg_level = sum(knowledge_levels) / len(knowledge_levels)
        max_level = max(knowledge_levels)
        min_level = min(knowledge_levels)
        std_level = np.std(knowledge_levels) if len(knowledge_levels) > 1 else 0
        
        return {
            'asset_id': asset_id,
            'title': self.knowledge_assets[asset_id].title,
            'coverage_percentage': coverage * 100.0,
            'avg_knowledge_level': avg_level,
            'max_knowledge_level': max_level,
            'min_knowledge_level': min_level,
            'std_knowledge_level': std_level,
            'people_with_knowledge': people_with_knowledge,
            'total_people': total_people
        }
    
    def identify_knowledge_gaps(self, threshold: float = 0.3) -> Dict[str, List[str]]:
        """
        Identifica lacunas de conhecimento na organização.
        
        Args:
            threshold: Limiar para considerar conhecimento relevante
            
        Returns:
            Dicionário de áreas de conhecimento -> assets com baixa cobertura
        """
        gaps_by_area = {}
        
        for asset_id, asset in self.knowledge_assets.items():
            coverage = self.calculate_knowledge_coverage(asset_id)
            
            # Verificar se é uma lacuna (baixa cobertura)
            if coverage['coverage_percentage'] < threshold * 100:
                area = asset.knowledge_area
                
                if area not in gaps_by_area:
                    gaps_by_area[area] = []
                    
                gaps_by_area[area].append({
                    'asset_id': asset_id,
                    'title': asset.title,
                    'coverage': coverage['coverage_percentage'],
                    'avg_level': coverage['avg_knowledge_level']
                })
        
        # Ordenar por cobertura (crescente)
        for area in gaps_by_area:
            gaps_by_area[area].sort(key=lambda x: x['coverage'])
        
        return gaps_by_area
    
    def simulate_diffusion(self, 
                         asset_id: str,
                         source_ids: List[str],
                         steps: int = 10,
                         transfer_probability: float = 0.3,
                         decay_factor: float = 0.8) -> Dict[str, Any]:
        """
        Simula a difusão de um conhecimento pela rede organizacional.
        
        Args:
            asset_id: ID do ativo de conhecimento
            source_ids: IDs das pessoas iniciais com o conhecimento
            steps: Número de passos de simulação
            transfer_probability: Probabilidade base de transferência
            decay_factor: Fator de decaimento por passo
            
        Returns:
            Resultados da simulação
        """
        if not self.influence_network:
            raise ValueError("Rede de influência é necessária para simulação")
            
        if asset_id not in self.knowledge_assets:
            raise ValueError(f"Ativo de conhecimento {asset_id} não encontrado")
        
        # Inicializar conhecimento
        knowledge_state = {}
        
        # Estado inicial: apenas as fontes têm conhecimento
        for person_id in self.influence_network.graph.nodes():
            if person_id in source_ids:
                knowledge_state[person_id] = 1.0
            else:
                knowledge_state[person_id] = 0.0
        
        # Histórico de difusão (para cada passo)
        diffusion_history = [knowledge_state.copy()]
        coverage_history = [self._calculate_coverage(knowledge_state)]
        
        # Executar simulação
        for step in range(steps):
            # Copiar estado atual
            new_knowledge_state = knowledge_state.copy()
            
            # Para cada pessoa na rede
            for person_id in self.influence_network.graph.nodes():
                # Se já tem conhecimento máximo, não muda
                if knowledge_state[person_id] >= 1.0:
                    continue
                
                # Verificar vizinhos de entrada (influenciadores)
                for influencer_id in self.influence_network.graph.predecessors(person_id):
                    # Se o influenciador tem conhecimento
                    if knowledge_state[influencer_id] > 0:
                        # Obter peso da relação
                        edge_data = self.influence_network.graph.get_edge_data(
                            influencer_id, person_id)
                        relation_weight = edge_data.get('weight', 0.5)
                        
                        # Calcular probabilidade de transferência
                        p_transfer = transfer_probability * relation_weight * knowledge_state[influencer_id]
                        
                        # Tentar transferir conhecimento
                        if random.random() < p_transfer:
                            # Transferência bem sucedida
                            transferred_knowledge = knowledge_state[influencer_id] * decay_factor
                            new_knowledge_state[person_id] = max(
                                new_knowledge_state[person_id], transferred_knowledge)
            
            # Atualizar estado
            knowledge_state = new_knowledge_state
            
            # Registrar histórico
            diffusion_history.append(knowledge_state.copy())
            coverage_history.append(self._calculate_coverage(knowledge_state))
        
        # Calcular métricas finais
        total_people = len(knowledge_state)
        people_with_knowledge = sum(1 for v in knowledge_state.values() if v > 0)
        coverage_percentage = (people_with_knowledge / total_people) * 100 if total_people > 0 else 0
        
        avg_knowledge = sum(knowledge_state.values()) / total_people if total_people > 0 else 0
        
        # Identificar difusores-chave (pessoas que mais contribuíram)
        key_diffusers = self._identify_key_diffusers(diffusion_history)
        
        # Salvar resultados
        results = {
            'asset_id': asset_id,
            'title': self.knowledge_assets[asset_id].title,
            'steps': steps,
            'initial_sources': source_ids,
            'final_coverage_percentage': coverage_percentage,
            'final_avg_knowledge': avg_knowledge,
            'coverage_history': coverage_history,
            'diffusion_history': diffusion_history,
            'key_diffusers': key_diffusers
        }
        
        self.diffusion_simulations[asset_id] = results
        
        return results
    
    def _calculate_coverage(self, knowledge_state: Dict[str, float]) -> float:
        """
        Calcula a cobertura do conhecimento em um estado.
        
        Args:
            knowledge_state: Estado de conhecimento {person_id -> nível}
            
        Returns:
            Percentual de cobertura
        """
        total_people = len(knowledge_state)
        if total_people == 0:
            return 0.0
            
        people_with_knowledge = sum(1 for v in knowledge_state.values() if v > 0)
        return (people_with_knowledge / total_people) * 100
    
    def _identify_key_diffusers(self, diffusion_history: List[Dict[str, float]]) -> List[Dict[str, Any]]:
        """
        Identifica pessoas-chave na difusão do conhecimento.
        
        Args:
            diffusion_history: Histórico da difusão
            
        Returns:
            Lista de difusores-chave
        """
        # Se não houver história suficiente
        if len(diffusion_history) < 3:
            return []
        
        # Para cada pessoa, calcular contribuição
        contributions = {}
        
        for person_id in diffusion_history[0].keys():
            # Contar quantas pessoas receberam conhecimento a partir desta
            influence_count = 0
            
            # Para cada passo após o inicial
            for step in range(1, len(diffusion_history)):
                prev_state = diffusion_history[step-1]
                curr_state = diffusion_history[step]
                
                # Se a pessoa tinha conhecimento no passo anterior
                if prev_state[person_id] > 0:
                    # Para cada vizinho de saída (influenciados)
                    for neighbor_id in self.influence_network.graph.successors(person_id):
                        # Se o vizinho ganhou conhecimento neste passo
                        if prev_state[neighbor_id] == 0 and curr_state[neighbor_id] > 0:
                            influence_count += 1
            
            contributions[person_id] = influence_count
        
        # Ordenar por contribuição e pegar os top 10
        top_diffusers = sorted(
            contributions.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return [
            {'person_id': person_id, 'influence_count': count}
            for person_id, count in top_diffusers
            if count > 0
        ]
    
    def visualize_diffusion(self, 
                          asset_id: str,
                          output_path: Optional[Path] = None) -> Path:
        """
        Visualiza a difusão de um conhecimento na organização.
        
        Args:
            asset_id: ID do ativo de conhecimento
            output_path: Caminho para salvar a visualização
            
        Returns:
            Caminho do arquivo salvo
        """
        if asset_id not in self.diffusion_simulations:
            raise ValueError(f"Não há simulação para o ativo {asset_id}")
        
        simulation = self.diffusion_simulations[asset_id]
        
        # Criar figura
        plt.figure(figsize=(15, 10))
        
        # 1. Curva de adoção (superior)
        plt.subplot(2, 1, 1)
        
        coverage_history = simulation['coverage_history']
        steps = range(len(coverage_history))
        
        plt.plot(steps, coverage_history, 'b-', linewidth=2, marker='o')
        plt.title(f'Difusão de Conhecimento: {simulation["title"]}', fontsize=14)
        plt.xlabel('Passos de Simulação', fontsize=12)
        plt.ylabel('Cobertura (%)', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Adicionar anotações
        plt.annotate(
            f'Cobertura Final: {simulation["final_coverage_percentage"]:.2f}%',
            xy=(steps[-1], coverage_history[-1]),
            xytext=(steps[-1]-2, coverage_history[-1]+10),
            arrowprops=dict(arrowstyle='->', color='red'),
            fontsize=10
        )
        
        # 2. Mapa de difusão (inferior)
        plt.subplot(2, 1, 2)
        
        # Se temos uma rede e simulação com pelo menos 3 passos
        if self.influence_network and len(simulation['diffusion_history']) >= 3:
            # Selecionamos 3 momentos da simulação para mostrar
            total_steps = len(simulation['diffusion_history'])
            step_indices = [0, total_steps // 2, total_steps - 1]
            
            # Para cada momento, plotamos a rede
            pos = None  # Manter a mesma posição em todos os plots
            
            for i, step_idx in enumerate(step_indices):
                ax = plt.subplot(2, 3, i+4)
                
                # Obter estado naquele ponto
                state = simulation['diffusion_history'][step_idx]
                
                # Criar um subgrafo apenas com nós que têm conhecimento
                know_nodes = [n for n, v in state.items() if v > 0]
                
                # Colorir nós por nível de conhecimento
                node_colors = [state.get(n, 0) for n in self.influence_network.graph.nodes()]
                
                # Plotar a rede
                if pos is None:
                    pos = nx.spring_layout(self.influence_network.graph)
                
                nx.draw_networkx_nodes(
                    self.influence_network.graph, pos,
                    node_color=node_colors,
                    cmap=plt.cm.Reds,
                    alpha=0.8,
                    node_size=100
                )
                
                # Desenhar as conexões apenas entre nós com conhecimento
                edges = [
                    (u, v) for u, v in self.influence_network.graph.edges()
                    if u in know_nodes and v in know_nodes
                ]
                
                nx.draw_networkx_edges(
                    self.influence_network.graph, pos,
                    edgelist=edges,
                    alpha=0.5,
                    arrows=True,
                    arrowsize=10,
                    width=0.8
                )
                
                step_percent = int(step_idx / (total_steps-1) * 100)
                ax.set_title(f'Passo {step_idx} ({step_percent}%)')
                ax.axis('off')
        
        plt.tight_layout()
        
        # Salvar figura
        if output_path is None:
            output_path = Path(f'output/knowledge_diffusion_{asset_id}.png')
            
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_diffusion_report(self, 
                               asset_id: str,
                               output_path: Optional[Path] = None) -> Path:
        """
        Gera um relatório detalhado sobre a difusão de conhecimento.
        
        Args:
            asset_id: ID do ativo de conhecimento
            output_path: Caminho para salvar o relatório
            
        Returns:
            Caminho do relatório salvo
        """
        if asset_id not in self.knowledge_assets:
            raise ValueError(f"Ativo de conhecimento {asset_id} não encontrado")
            
        asset = self.knowledge_assets[asset_id]
        
        # Calcular cobertura atual
        coverage = self.calculate_knowledge_coverage(asset_id)
        
        # Verificar se há simulação
        has_simulation = asset_id in self.diffusion_simulations
        simulation = self.diffusion_simulations.get(asset_id, {})
        
        # Criar caminho de saída
        if output_path is None:
            output_path = Path(f'output/relatorio_difusao_{asset_id}.txt')
            
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Gerar relatório
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"RELATÓRIO DE DIFUSÃO DE CONHECIMENTO\n")
            f.write(f"{'='*50}\n\n")
            
            f.write(f"Título: {asset.title}\n")
            f.write(f"Área: {asset.knowledge_area}\n")
            f.write(f"Formato: {asset.format}\n")
            f.write(f"Nível: {asset.expertise_level}\n")
            f.write(f"Criado por: {asset.creator_id}\n")
            f.write(f"Data: {asset.creation_date.strftime('%d/%m/%Y')}\n\n")
            
            f.write(f"COBERTURA ATUAL\n")
            f.write(f"{'-'*50}\n")
            f.write(f"Pessoas com conhecimento: {coverage['people_with_knowledge']} de {coverage['total_people']} ({coverage['coverage_percentage']:.2f}%)\n")
            f.write(f"Nível médio: {coverage['avg_knowledge_level']:.2f}\n")
            f.write(f"Nível máximo: {coverage['max_knowledge_level']:.2f}\n")
            f.write(f"Nível mínimo: {coverage['min_knowledge_level']:.2f}\n")
            f.write(f"Desvio padrão: {coverage['std_knowledge_level']:.2f}\n\n")
            
            # Adicionar resultados da simulação se disponível
            if has_simulation:
                f.write(f"SIMULAÇÃO DE DIFUSÃO\n")
                f.write(f"{'-'*50}\n")
                f.write(f"Passos simulados: {simulation['steps']}\n")
                f.write(f"Cobertura projetada: {simulation['final_coverage_percentage']:.2f}%\n")
                f.write(f"Nível médio projetado: {simulation['final_avg_knowledge']:.2f}\n\n")
                
                f.write(f"DIFUSORES-CHAVE\n")
                f.write(f"{'-'*50}\n")
                if simulation['key_diffusers']:
                    for i, diffuser in enumerate(simulation['key_diffusers'], 1):
                        f.write(f"{i}. {diffuser['person_id']} - Impactou {diffuser['influence_count']} pessoas\n")
                else:
                    f.write("Nenhum difusor-chave identificado.\n")
                f.write("\n")
                
                # Adicionar visualização
                if output_path.suffix == '.txt':
                    viz_path = output_path.with_suffix('.png')
                    self.visualize_diffusion(asset_id, viz_path)
                    f.write(f"Visualização salva em: {viz_path}\n\n")
            
            f.write(f"RECOMENDAÇÕES\n")
            f.write(f"{'-'*50}\n")
            
            # Recomendações baseadas na cobertura
            if coverage['coverage_percentage'] < 30:
                f.write("1. Promover treinamentos formais para aumentar a cobertura deste conhecimento\n")
                f.write("2. Identificar pessoas de alta influência para atuar como difusores\n")
                f.write("3. Criar materiais de apoio mais acessíveis para facilitar o aprendizado\n")
            elif coverage['coverage_percentage'] < 70:
                f.write("1. Fomentar comunidades de prática para compartilhamento\n")
                f.write("2. Criar mecanismos de reconhecimento para quem difunde o conhecimento\n")
                f.write("3. Desenvolver aplicações práticas para consolidar o aprendizado\n")
            else:
                f.write("1. Desenvolver níveis avançados deste conhecimento\n")
                f.write("2. Identificar oportunidades de inovação a partir deste conhecimento\n")
                f.write("3. Documentar casos de sucesso e melhores práticas\n")
        
        return output_path 