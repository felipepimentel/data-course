"""
Multiplicador de Impacto da Rede de Influência.

Avalia como uma pessoa amplifica resultados do time, identificando
padrões de colaboração e alavancagem de resultados coletivos.
"""
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from pathlib import Path

from peopleanalytics.data_pipeline import DataPipeline
from peopleanalytics.talent_development.influence_network.network_analyzer import InfluenceNetwork


@dataclass
class TeamOutcome:
    """Resultado obtido por um time ou projeto."""
    outcome_id: str
    team_id: str
    project_id: Optional[str]
    outcome_type: str  # 'deliverable', 'metric', 'award', etc.
    value: float  # Valor quantitativo (se aplicável)
    qualitative_result: str  # Descrição qualitativa
    timestamp: datetime.datetime
    contributors: Dict[str, float]  # person_id -> contribuição (0-1)
    context: Dict[str, Any]  # Metadados adicionais


class ImpactMultiplier:
    """
    Analisa como uma pessoa amplifica resultados coletivos através de sua
    influência na rede organizacional.
    """
    
    def __init__(self, 
                influence_network: Optional[InfluenceNetwork] = None,
                data_pipeline: Optional[DataPipeline] = None):
        """
        Inicializa o analisador de multiplicação de impacto.
        
        Args:
            influence_network: Rede de influência para análise
            data_pipeline: Pipeline de dados opcional para carregar dados existentes
        """
        self.influence_network = influence_network
        self.data_pipeline = data_pipeline
        self.team_outcomes = []  # Lista de resultados de times
        self.person_outcomes = {}  # person_id -> [resultados associados]
        
    def load_data(self) -> bool:
        """
        Carrega dados de resultados de times e projetos.
        
        Returns:
            True se os dados foram carregados com sucesso, False caso contrário
        """
        if not self.data_pipeline:
            return False
            
        try:
            # Carregar resultados de times/projetos
            outcomes_data = self.data_pipeline.load_team_outcomes()
            
            # Converter para objetos TeamOutcome
            self.team_outcomes = []
            for outcome in outcomes_data:
                team_outcome = TeamOutcome(
                    outcome_id=outcome['id'],
                    team_id=outcome['team_id'],
                    project_id=outcome.get('project_id'),
                    outcome_type=outcome.get('type', 'deliverable'),
                    value=float(outcome.get('value', 0.0)),
                    qualitative_result=outcome.get('description', ''),
                    timestamp=datetime.datetime.fromisoformat(
                        outcome.get('timestamp', datetime.datetime.now().isoformat())
                    ),
                    contributors=outcome.get('contributors', {}),
                    context=outcome.get('context', {})
                )
                self.team_outcomes.append(team_outcome)
            
            # Indexar por pessoa para acesso rápido
            self.person_outcomes = {}
            for outcome in self.team_outcomes:
                for person_id in outcome.contributors.keys():
                    if person_id not in self.person_outcomes:
                        self.person_outcomes[person_id] = []
                    self.person_outcomes[person_id].append(outcome)
            
            return True
            
        except Exception as e:
            print(f"Erro ao carregar dados de resultados: {str(e)}")
            return False
    
    def add_team_outcome(self, 
                        team_id: str,
                        outcome_type: str,
                        value: float,
                        qualitative_result: str,
                        contributors: Dict[str, float],
                        project_id: Optional[str] = None,
                        context: Optional[Dict[str, Any]] = None) -> TeamOutcome:
        """
        Adiciona um novo resultado de time/projeto.
        
        Args:
            team_id: ID do time
            outcome_type: Tipo de resultado
            value: Valor quantitativo
            qualitative_result: Descrição qualitativa
            contributors: Dicionário de person_id -> contribuição (0-1)
            project_id: ID do projeto (opcional)
            context: Metadados adicionais
            
        Returns:
            Novo resultado de time criado
        """
        # Validar contribuições
        for contribution in contributors.values():
            if not 0 <= contribution <= 1:
                raise ValueError("Contribuições devem estar entre 0 e 1")
                
        # Normalizar contribuições para somar 1
        total_contribution = sum(contributors.values())
        if total_contribution > 0:
            normalized_contributors = {
                person_id: contribution / total_contribution
                for person_id, contribution in contributors.items()
            }
        else:
            normalized_contributors = contributors
        
        # Criar ID único
        outcome_id = f"out_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{team_id}"
        
        # Criar resultado
        outcome = TeamOutcome(
            outcome_id=outcome_id,
            team_id=team_id,
            project_id=project_id,
            outcome_type=outcome_type,
            value=value,
            qualitative_result=qualitative_result,
            timestamp=datetime.datetime.now(),
            contributors=normalized_contributors,
            context=context or {}
        )
        
        # Adicionar à lista
        self.team_outcomes.append(outcome)
        
        # Atualizar índice por pessoa
        for person_id in outcome.contributors.keys():
            if person_id not in self.person_outcomes:
                self.person_outcomes[person_id] = []
            self.person_outcomes[person_id].append(outcome)
        
        # Salvar no pipeline se disponível
        if self.data_pipeline:
            outcome_data = {
                'id': outcome_id,
                'team_id': team_id,
                'project_id': project_id,
                'type': outcome_type,
                'value': value,
                'description': qualitative_result,
                'timestamp': outcome.timestamp.isoformat(),
                'contributors': normalized_contributors,
                'context': context or {}
            }
            
            self.data_pipeline.save_team_outcome(outcome_data)
        
        return outcome
    
    def calculate_direct_impact(self, person_id: str) -> Dict[str, Any]:
        """
        Calcula o impacto direto de uma pessoa com base em sua contribuição
        para resultados específicos.
        
        Args:
            person_id: ID da pessoa
            
        Returns:
            Dicionário com métricas de impacto direto
        """
        # Obter outcomes associados à pessoa
        outcomes = self.person_outcomes.get(person_id, [])
        
        if not outcomes:
            return {
                'total_outcomes': 0,
                'total_value': 0.0,
                'avg_contribution': 0.0,
                'value_generated': 0.0,
                'outcomes_by_type': {},
                'top_contributions': []
            }
        
        # Calcular métricas gerais
        total_outcomes = len(outcomes)
        total_value = sum(outcome.value for outcome in outcomes)
        contributions = [
            outcome.contributors.get(person_id, 0.0)
            for outcome in outcomes
        ]
        avg_contribution = sum(contributions) / len(contributions)
        
        # Calcular valor gerado (valor * contribuição)
        value_generated = sum(
            outcome.value * outcome.contributors.get(person_id, 0.0)
            for outcome in outcomes
        )
        
        # Calcular resultados por tipo
        outcomes_by_type = {}
        for outcome in outcomes:
            outcome_type = outcome.outcome_type
            if outcome_type not in outcomes_by_type:
                outcomes_by_type[outcome_type] = {
                    'count': 0,
                    'total_value': 0.0,
                    'avg_contribution': 0.0,
                    'value_generated': 0.0
                }
            
            contribution = outcome.contributors.get(person_id, 0.0)
            value_gen = outcome.value * contribution
            
            outcomes_by_type[outcome_type]['count'] += 1
            outcomes_by_type[outcome_type]['total_value'] += outcome.value
            outcomes_by_type[outcome_type]['value_generated'] += value_gen
        
        # Calcular médias por tipo
        for otype, stats in outcomes_by_type.items():
            if stats['count'] > 0:
                stats['avg_contribution'] = stats['value_generated'] / stats['total_value'] if stats['total_value'] > 0 else 0.0
        
        # Obter top contribuições
        top_contributions = []
        for outcome in sorted(outcomes, key=lambda x: x.contributors.get(person_id, 0.0) * x.value, reverse=True)[:5]:
            top_contributions.append({
                'outcome_id': outcome.outcome_id,
                'team_id': outcome.team_id,
                'project_id': outcome.project_id,
                'outcome_type': outcome.outcome_type,
                'value': outcome.value,
                'contribution': outcome.contributors.get(person_id, 0.0),
                'value_generated': outcome.value * outcome.contributors.get(person_id, 0.0),
                'timestamp': outcome.timestamp,
                'description': outcome.qualitative_result[:100] + '...' if len(outcome.qualitative_result) > 100 else outcome.qualitative_result
            })
        
        return {
            'total_outcomes': total_outcomes,
            'total_value': total_value,
            'avg_contribution': avg_contribution,
            'value_generated': value_generated,
            'outcomes_by_type': outcomes_by_type,
            'top_contributions': top_contributions
        }
    
    def calculate_network_impact(self, person_id: str) -> Dict[str, Any]:
        """
        Calcula o impacto de rede da pessoa, combinando contribuição direta
        com influência na rede para determinar o impacto total.
        
        Args:
            person_id: ID da pessoa
            
        Returns:
            Dicionário com métricas de impacto de rede
        """
        # Verificar se temos rede de influência
        if not self.influence_network:
            return {
                'network_impact_score': 0.0,
                'direct_impact': 0.0,
                'indirect_impact': 0.0,
                'impact_multiplier': 0.0,
                'reach': 0,
                'impacted_people': []
            }
        
        # Calcular impacto direto
        direct_impact = self.calculate_direct_impact(person_id)
        direct_value = direct_impact['value_generated']
        
        # Obter rede de influência
        try:
            # Tentar obter ego-network para análise
            ego_network = self.influence_network.get_ego_network(person_id)
            influence_metrics = self.influence_network.calculate_centrality_metrics(ego_network)
            person_influence = influence_metrics.get(person_id, {})
            
            # Pessoas influenciadas diretamente
            influenced_nodes = list(ego_network.successors(person_id))
            
            # Calcular impacto indireto (através da rede)
            indirect_impact = 0.0
            impacted_people = []
            
            for node in influenced_nodes:
                # Obter força da influência
                edge_data = ego_network.get_edge_data(person_id, node)
                influence_weight = edge_data.get('weight', 0.0) if edge_data else 0.0
                
                # Calcular impacto direto da pessoa influenciada
                node_impact = self.calculate_direct_impact(node)
                node_value = node_impact['value_generated']
                
                # Calcular contribuição indireta
                # (porcentagem do valor que pode ser atribuída à influência)
                indirect_contribution = node_value * influence_weight * 0.3  # Fator de atenuação
                indirect_impact += indirect_contribution
                
                # Adicionar à lista de pessoas impactadas
                if indirect_contribution > 0:
                    impacted_people.append({
                        'person_id': node,
                        'influence_weight': influence_weight,
                        'direct_value': node_value,
                        'indirect_contribution': indirect_contribution
                    })
            
            # Ordenar por contribuição indireta
            impacted_people.sort(key=lambda x: x['indirect_contribution'], reverse=True)
            
            # Calcular multiplicador de impacto
            # (quanto valor indireto é gerado para cada unidade de valor direto)
            impact_multiplier = indirect_impact / direct_value if direct_value > 0 else 0.0
            
            # Calcular pontuação total de impacto (combinando direto e indireto)
            network_impact_score = direct_value + (indirect_impact * 0.7)  # Peso reduzido para impacto indireto
            
            return {
                'network_impact_score': network_impact_score,
                'direct_impact': direct_value,
                'indirect_impact': indirect_impact,
                'impact_multiplier': impact_multiplier,
                'reach': len(influenced_nodes),
                'impacted_people': impacted_people[:10]  # Top 10
            }
            
        except Exception as e:
            print(f"Erro ao calcular impacto de rede: {str(e)}")
            return {
                'network_impact_score': direct_value,  # Fallback para impacto direto apenas
                'direct_impact': direct_value,
                'indirect_impact': 0.0,
                'impact_multiplier': 0.0,
                'reach': 0,
                'impacted_people': [],
                'error': str(e)
            }
    
    def identify_impact_patterns(self, person_id: str) -> Dict[str, Any]:
        """
        Identifica padrões de impacto para uma pessoa, analisando
        em quais tipos de resultados a pessoa tem maior efeito.
        
        Args:
            person_id: ID da pessoa
            
        Returns:
            Dicionário com padrões de impacto identificados
        """
        # Calcular impacto direto para obter dados
        direct_impact = self.calculate_direct_impact(person_id)
        
        # Se não temos dados suficientes, retornar resultado limitado
        if direct_impact['total_outcomes'] < 3:
            return {
                'impact_profile': "Dados insuficientes",
                'strengths': [],
                'growth_areas': [],
                'collaboration_pattern': "Dados insuficientes"
            }
        
        # Analisar outcomes por tipo
        outcomes_by_type = direct_impact['outcomes_by_type']
        
        # Identificar áreas de força
        strengths = []
        for outcome_type, stats in outcomes_by_type.items():
            # Considerar força se contribuição média é alta
            if stats['avg_contribution'] > 0.4:
                strengths.append({
                    'type': outcome_type,
                    'avg_contribution': stats['avg_contribution'],
                    'value_generated': stats['value_generated'],
                    'count': stats['count']
                })
        
        # Ordenar por valor gerado
        strengths.sort(key=lambda x: x['value_generated'], reverse=True)
        
        # Identificar áreas para crescimento
        growth_areas = []
        for outcome_type, stats in outcomes_by_type.items():
            # Considerar área de crescimento se contribuição média é baixa
            if stats['avg_contribution'] < 0.2 and stats['count'] >= 2:
                growth_areas.append({
                    'type': outcome_type,
                    'avg_contribution': stats['avg_contribution'],
                    'value_generated': stats['value_generated'],
                    'count': stats['count']
                })
        
        # Ordenar por potencial de crescimento (valor total * (1 - contribuição média))
        growth_areas.sort(key=lambda x: x['value_generated'] / x['avg_contribution'] if x['avg_contribution'] > 0 else 0, reverse=True)
        
        # Determinar perfil de impacto
        if len(strengths) == 0:
            impact_profile = "Contribuidor Emergente"
        elif len(strengths) == 1:
            impact_profile = f"Especialista em {strengths[0]['type']}"
        elif len(strengths) >= 3:
            impact_profile = "Contribuidor Versátil"
        else:
            # Verificar valor gerado
            total_value = direct_impact['value_generated']
            if total_value > 100:  # Threshold ajustável
                impact_profile = "Alto Impacto Focalizado"
            else:
                impact_profile = "Contribuidor Balanceado"
        
        # Analisar padrão de colaboração
        collaboration_pattern = self._analyze_collaboration_pattern(person_id)
        
        return {
            'impact_profile': impact_profile,
            'strengths': strengths,
            'growth_areas': growth_areas,
            'collaboration_pattern': collaboration_pattern
        }
    
    def _analyze_collaboration_pattern(self, person_id: str) -> str:
        """
        Analisa o padrão de colaboração de uma pessoa.
        
        Args:
            person_id: ID da pessoa
            
        Returns:
            Descrição do padrão de colaboração
        """
        # Obter outcomes associados à pessoa
        outcomes = self.person_outcomes.get(person_id, [])
        
        if not outcomes:
            return "Dados insuficientes"
        
        # Contar colaboradores únicos
        all_collaborators = set()
        for outcome in outcomes:
            for collaborator in outcome.contributors.keys():
                if collaborator != person_id:
                    all_collaborators.add(collaborator)
        
        # Calcular média de colaboradores por outcome
        avg_collaborators = sum(len(outcome.contributors) - 1 for outcome in outcomes) / len(outcomes)
        
        # Calcular contribuição média
        avg_contribution = sum(
            outcome.contributors.get(person_id, 0.0)
            for outcome in outcomes
        ) / len(outcomes)
        
        # Determinar padrão
        if len(all_collaborators) <= 3:
            if avg_contribution > 0.5:
                return "Colaborador Focal (trabalha intensamente com poucas pessoas)"
            else:
                return "Contribuidor Secundário em Equipe Pequena"
        elif avg_collaborators > 5:
            if avg_contribution > 0.4:
                return "Líder de Equipe Grande"
            else:
                return "Colaborador em Redes Amplas"
        elif len(all_collaborators) > 10:
            return "Colaborador Diversificado (trabalha com muitas pessoas diferentes)"
        else:
            return "Colaborador Balanceado"
    
    def visualize_impact(self, person_id: str, output_path: Optional[Path] = None) -> Path:
        """
        Gera visualização do impacto da pessoa.
        
        Args:
            person_id: ID da pessoa
            output_path: Caminho para salvar a visualização (opcional)
            
        Returns:
            Caminho para a visualização gerada
        """
        # Calcular impacto direto e de rede
        direct_impact = self.calculate_direct_impact(person_id)
        network_impact = self.calculate_network_impact(person_id)
        patterns = self.identify_impact_patterns(person_id)
        
        # Configurar caminho de saída
        if not output_path:
            output_dir = Path("output") / "influence_network"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{person_id}_impact_multiplier_{datetime.datetime.now().strftime('%Y%m%d')}.png"
        
        # Configurar figura com subplots
        fig = plt.figure(figsize=(15, 10))
        fig.suptitle(f"Análise de Multiplicador de Impacto: {person_id}", fontsize=16)
        
        # Layout de subplots
        gs = fig.add_gridspec(2, 2)
        
        # 1. Impacto Direto vs Indireto
        ax1 = fig.add_subplot(gs[0, 0])
        impact_values = [direct_impact['value_generated'], network_impact['indirect_impact']]
        bars = ax1.bar(['Impacto Direto', 'Impacto Indireto'], impact_values, color=['#3498db', '#2ecc71'])
        ax1.set_title('Impacto Direto vs. Indireto')
        ax1.set_ylabel('Valor')
        
        # Adicionar rótulos nas barras
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.1f}', ha='center', va='bottom')
        
        # 2. Multiplicador de Impacto
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.axis('equal')
        multiplier = network_impact['impact_multiplier']
        
        # Usar gráfico de pizza para mostrar multiplicador
        if multiplier > 0:
            sizes = [1, multiplier]
            labels = ['Impacto Direto', f'Multiplicador ({multiplier:.2f}x)']
            colors = ['#3498db', '#2ecc71']
        else:
            sizes = [1]
            labels = ['Impacto Direto (Sem multiplicador)']
            colors = ['#3498db']
            
        ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax2.set_title('Multiplicador de Impacto')
        
        # 3. Impacto por Tipo de Outcome
        ax3 = fig.add_subplot(gs[1, 0])
        
        # Extrair dados por tipo
        outcome_types = []
        direct_values = []
        total_values = []
        
        for outcome_type, stats in direct_impact['outcomes_by_type'].items():
            outcome_types.append(outcome_type)
            direct_values.append(stats['value_generated'])
            total_values.append(stats['total_value'])
        
        # Verificar se temos dados para mostrar
        if outcome_types:
            x = np.arange(len(outcome_types))
            width = 0.35
            
            ax3.bar(x - width/2, direct_values, width, label='Valor Gerado', color='#3498db')
            ax3.bar(x + width/2, total_values, width, label='Valor Total', color='#95a5a6', alpha=0.7)
            
            ax3.set_title('Impacto por Tipo de Resultado')
            ax3.set_xticks(x)
            ax3.set_xticklabels(outcome_types, rotation=45, ha='right')
            ax3.legend()
        else:
            ax3.text(0.5, 0.5, "Sem dados por tipo", ha='center', va='center', fontsize=14)
            ax3.axis('off')
        
        # 4. Alcance e Pessoas Impactadas
        ax4 = fig.add_subplot(gs[1, 1])
        
        # Extrair dados de pessoas impactadas
        impacted_people = network_impact['impacted_people']
        
        if impacted_people:
            people_ids = [p['person_id'] for p in impacted_people[:5]]  # Top 5
            influence_weights = [p['influence_weight'] for p in impacted_people[:5]]
            indirect_values = [p['indirect_contribution'] for p in impacted_people[:5]]
            
            # Criar barras horizontais
            y_pos = np.arange(len(people_ids))
            ax4.barh(y_pos, indirect_values, color='#2ecc71')
            
            # Configurar eixos
            ax4.set_yticks(y_pos)
            ax4.set_yticklabels(people_ids)
            ax4.invert_yaxis()  # Pessoas no topo ficam em primeiro
            ax4.set_title('Top Pessoas Impactadas')
            ax4.set_xlabel('Contribuição Indireta')
            
            # Adicionar rótulos com peso de influência
            for i, v in enumerate(indirect_values):
                ax4.text(v + 0.1, i, f"Infl: {influence_weights[i]:.2f}", va='center')
        else:
            ax4.text(0.5, 0.5, "Sem dados de impacto em rede", ha='center', va='center', fontsize=14)
            ax4.axis('off')
        
        # Adicionar informações de resumo na parte inferior
        plt.figtext(0.5, 0.01, 
                   f"Perfil de Impacto: {patterns['impact_profile']} | "
                   f"Padrão de Colaboração: {patterns['collaboration_pattern']} | "
                   f"Alcance: {network_impact['reach']} pessoas",
                   ha="center", fontsize=12, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
        
        # Ajustar layout
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        # Salvar figura
        plt.savefig(output_path)
        plt.close()
        
        return output_path
    
    def generate_impact_report(self, person_id: str, output_path: Optional[Path] = None) -> Path:
        """
        Gera um relatório completo do multiplicador de impacto para uma pessoa.
        
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
            report_file = output_dir / f"{person_id}_impact_report_{datetime.datetime.now().strftime('%Y%m%d')}.md"
        
        # Calcular todos os dados necessários
        direct_impact = self.calculate_direct_impact(person_id)
        network_impact = self.calculate_network_impact(person_id)
        patterns = self.identify_impact_patterns(person_id)
        
        # Gerar visualização
        viz_path = self.visualize_impact(person_id)
        
        # Escrever relatório
        with open(report_file, 'w') as f:
            f.write(f"# Relatório de Multiplicador de Impacto: {person_id}\n\n")
            f.write(f"Data: {datetime.datetime.now().strftime('%d/%m/%Y')}\n\n")
            
            f.write("## Resumo de Impacto\n\n")
            f.write(f"**Pontuação de Impacto em Rede:** {network_impact['network_impact_score']:.2f}\n\n")
            f.write(f"**Perfil de Impacto:** {patterns['impact_profile']}\n\n")
            f.write(f"**Padrão de Colaboração:** {patterns['collaboration_pattern']}\n\n")
            f.write(f"**Multiplicador de Impacto:** {network_impact['impact_multiplier']:.2f}x\n\n")
            f.write(f"**Alcance:** {network_impact['reach']} pessoas\n\n")
            
            f.write("## Impacto Direto\n\n")
            f.write(f"**Total de Resultados:** {direct_impact['total_outcomes']}\n\n")
            f.write(f"**Valor Total Gerado:** {direct_impact['value_generated']:.2f}\n\n")
            f.write(f"**Contribuição Média:** {direct_impact['avg_contribution']*100:.1f}%\n\n")
            
            f.write("### Top Contribuições\n\n")
            if direct_impact['top_contributions']:
                f.write("| Data | Tipo | Valor | Contribuição | Valor Gerado |\n")
                f.write("|------|------|-------|--------------|---------------|\n")
                for contrib in direct_impact['top_contributions']:
                    date = contrib['timestamp'].strftime('%d/%m/%Y')
                    contrib_pct = f"{contrib['contribution']*100:.1f}%"
                    f.write(f"| {date} | {contrib['outcome_type']} | {contrib['value']:.2f} | {contrib_pct} | {contrib['value_generated']:.2f} |\n")
            else:
                f.write("Nenhuma contribuição direta identificada.\n")
            
            f.write("\n## Áreas de Força\n\n")
            if patterns['strengths']:
                f.write("| Tipo de Resultado | Contribuição Média | Valor Gerado | Ocorrências |\n")
                f.write("|-------------------|--------------------|--------------|--------------|\n")
                for strength in patterns['strengths']:
                    contrib_pct = f"{strength['avg_contribution']*100:.1f}%"
                    f.write(f"| {strength['type']} | {contrib_pct} | {strength['value_generated']:.2f} | {strength['count']} |\n")
            else:
                f.write("Nenhuma área de força claramente identificada.\n")
                
            f.write("\n## Áreas para Crescimento\n\n")
            if patterns['growth_areas']:
                f.write("| Tipo de Resultado | Contribuição Atual | Potencial |\n")
                f.write("|-------------------|--------------------|-----------|\n")
                for area in patterns['growth_areas']:
                    contrib_pct = f"{area['avg_contribution']*100:.1f}%"
                    potential = area['value_generated'] / area['avg_contribution'] if area['avg_contribution'] > 0 else 0
                    f.write(f"| {area['type']} | {contrib_pct} | {potential:.2f} |\n")
            else:
                f.write("Nenhuma área de crescimento claramente identificada.\n")
            
            f.write("\n## Impacto em Rede\n\n")
            f.write(f"**Impacto Direto:** {network_impact['direct_impact']:.2f}\n\n")
            f.write(f"**Impacto Indireto:** {network_impact['indirect_impact']:.2f}\n\n")
            f.write(f"**Multiplicador:** {network_impact['impact_multiplier']:.2f}x\n\n")
            
            f.write("### Pessoas Mais Impactadas\n\n")
            if network_impact['impacted_people']:
                f.write("| Pessoa | Influência | Valor Indireto |\n")
                f.write("|--------|------------|----------------|\n")
                for person in network_impact['impacted_people']:
                    influence_pct = f"{person['influence_weight']*100:.1f}%"
                    f.write(f"| {person['person_id']} | {influence_pct} | {person['indirect_contribution']:.2f} |\n")
            else:
                f.write("Nenhuma pessoa diretamente impactada identificada.\n")
            
            f.write("\n## Visualização\n\n")
            f.write(f"![Multiplicador de Impacto]({viz_path.name})\n\n")
            
            f.write("## Recomendações\n\n")
            
            # Gerar recomendações baseadas na análise
            multiplier = network_impact['impact_multiplier']
            if multiplier < 0.5:
                f.write("1. **Expandir influência na rede:** Compartilhar mais conhecimento e recursos com colegas\n")
                f.write("2. **Intensificar colaborações estratégicas:** Focar em parcerias com multiplicadores de impacto\n")
                f.write("3. **Aumentar visibilidade do trabalho:** Comunicar resultados e conquistas de forma mais ampla\n")
            elif multiplier < 1.5:
                f.write("1. **Alavancar áreas de força existentes:** Expandir atuação nos tipos de resultado com maior contribuição\n")
                f.write("2. **Desenvolver mentoria formal:** Estruturar transferência de conhecimento para amplificar impacto\n")
                f.write("3. **Equilibrar atuação direta e indireta:** Otimizar tempo entre fazer e influenciar\n")
            else:
                f.write("1. **Escalar modelo de influência:** Formalizar práticas que amplificam resultados coletivos\n")
                f.write("2. **Desenvolver sucessores:** Identificar e nutrir próxima geração de multiplicadores\n")
                f.write("3. **Focar em resultados estratégicos:** Direcionar influência para áreas de maior impacto organizacional\n")
        
        return report_file 