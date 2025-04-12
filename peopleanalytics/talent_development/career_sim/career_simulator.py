"""
Simulador de Carreira para Desenvolvimento de Talentos.

Permite projetar trajetórias de carreira, simular diferentes cenários
de desenvolvimento e identificar caminhos ótimos de evolução profissional.
"""
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from pathlib import Path

from peopleanalytics.data_pipeline import DataPipeline


@dataclass
class CareerPosition:
    """Representa uma posição na carreira."""
    position_id: str
    title: str
    level: int  # Nível hierárquico (1, 2, 3...)
    track: str  # Trilha (técnica, gestão, especialista...)
    department: str
    skills_required: Dict[str, float]  # Habilidade -> nível requerido
    avg_tenure: float  # Tempo médio na posição (anos)
    growth_potential: float  # Potencial de crescimento (0-1)
    attributes: Dict[str, Any] = None


@dataclass
class CareerPath:
    """Representa um caminho de carreira simulado."""
    path_id: str
    person_id: str
    positions: List[Tuple[str, int]]  # (position_id, time_in_position)
    total_time: int  # Tempo total simulado (anos)
    growth_score: float  # Score de crescimento
    probability: float  # Probabilidade deste caminho
    attributes: Dict[str, Any] = None


class CareerSimulator:
    """
    Simulador de carreira que projeta possíveis caminhos profissionais.
    
    Utiliza dados históricos e modelos probabilísticos para simular
    diferentes trajetórias, ajudando no planejamento de desenvolvimento
    e nas decisões estratégicas de carreira.
    """
    
    def __init__(self, data_pipeline: Optional[DataPipeline] = None):
        """
        Inicializa o simulador de carreira.
        
        Args:
            data_pipeline: Pipeline de dados opcional para carregar dados existentes
        """
        self.data_pipeline = data_pipeline
        self.positions = {}  # position_id -> CareerPosition
        self.transitions = {}  # (from_id, to_id) -> probabilidade
        self.person_skills = {}  # person_id -> {skill -> nível}
        self.simulated_paths = {}  # person_id -> [CareerPath]
        
    def load_data(self) -> bool:
        """
        Carrega dados de posições, transições e habilidades.
        
        Returns:
            True se os dados foram carregados com sucesso, False caso contrário
        """
        if not self.data_pipeline:
            return False
            
        try:
            # Carregar posições
            positions_data = self.data_pipeline.load_career_positions()
            
            # Converter para objetos CareerPosition
            self.positions = {}
            for pos in positions_data:
                position = CareerPosition(
                    position_id=pos['id'],
                    title=pos['title'],
                    level=int(pos.get('level', 1)),
                    track=pos.get('track', 'geral'),
                    department=pos.get('department', ''),
                    skills_required=pos.get('skills_required', {}),
                    avg_tenure=float(pos.get('avg_tenure', 2.0)),
                    growth_potential=float(pos.get('growth_potential', 0.5)),
                    attributes=pos.get('attributes', {})
                )
                self.positions[pos['id']] = position
            
            # Carregar transições
            transitions_data = self.data_pipeline.load_career_transitions()
            self.transitions = {
                (t['from_id'], t['to_id']): float(t.get('probability', 0.0)) 
                for t in transitions_data
            }
            
            # Carregar habilidades das pessoas
            self.person_skills = self.data_pipeline.load_person_skills()
            
            return True
            
        except Exception as e:
            print(f"Erro ao carregar dados de carreira: {str(e)}")
            return False
    
    def add_position(self, 
                   title: str,
                   level: int,
                   track: str,
                   department: str,
                   skills_required: Dict[str, float],
                   avg_tenure: float = 2.0,
                   growth_potential: float = 0.5,
                   attributes: Optional[Dict[str, Any]] = None) -> CareerPosition:
        """
        Adiciona uma nova posição de carreira.
        
        Args:
            title: Título da posição
            level: Nível hierárquico
            track: Trilha de carreira
            department: Departamento
            skills_required: Habilidades requeridas
            avg_tenure: Tempo médio de permanência
            growth_potential: Potencial de crescimento
            attributes: Atributos adicionais
            
        Returns:
            Nova posição de carreira criada
        """
        # Validar dados
        if not title or level < 1:
            raise ValueError("Título e nível são obrigatórios")
            
        # Criar ID único
        position_id = f"pos_{len(self.positions) + 1:03d}"
        
        # Criar posição
        position = CareerPosition(
            position_id=position_id,
            title=title,
            level=level,
            track=track,
            department=department,
            skills_required=skills_required,
            avg_tenure=avg_tenure,
            growth_potential=growth_potential,
            attributes=attributes or {}
        )
        
        # Adicionar ao dicionário
        self.positions[position_id] = position
        
        # Salvar no pipeline se disponível
        if self.data_pipeline:
            position_data = {
                'id': position_id,
                'title': title,
                'level': level,
                'track': track,
                'department': department,
                'skills_required': skills_required,
                'avg_tenure': avg_tenure,
                'growth_potential': growth_potential,
                'attributes': attributes or {}
            }
            
            self.data_pipeline.save_career_position(position_data)
        
        return position
    
    def add_transition(self, 
                     from_position_id: str,
                     to_position_id: str,
                     probability: float) -> bool:
        """
        Adiciona uma transição entre posições.
        
        Args:
            from_position_id: ID da posição de origem
            to_position_id: ID da posição de destino
            probability: Probabilidade de transição (0-1)
            
        Returns:
            True se adicionado com sucesso, False caso contrário
        """
        # Validar posições
        if from_position_id not in self.positions:
            raise ValueError(f"Posição de origem {from_position_id} não encontrada")
            
        if to_position_id not in self.positions:
            raise ValueError(f"Posição de destino {to_position_id} não encontrada")
            
        if not 0 <= probability <= 1:
            raise ValueError("Probabilidade deve estar entre 0 e 1")
        
        # Adicionar transição
        self.transitions[(from_position_id, to_position_id)] = probability
        
        # Salvar no pipeline se disponível
        if self.data_pipeline:
            transition_data = {
                'from_id': from_position_id,
                'to_id': to_position_id,
                'probability': probability
            }
            
            self.data_pipeline.save_career_transition(transition_data)
        
        return True
    
    def update_person_skills(self, 
                          person_id: str, 
                          skills: Dict[str, float]) -> bool:
        """
        Atualiza as habilidades de uma pessoa.
        
        Args:
            person_id: ID da pessoa
            skills: Dicionário de habilidades -> nível
            
        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        # Validar skills
        for skill, level in skills.items():
            if not 0 <= level <= 1:
                raise ValueError(f"Nível da habilidade {skill} deve estar entre 0 e 1")
        
        # Atualizar ou criar entry para a pessoa
        if person_id not in self.person_skills:
            self.person_skills[person_id] = {}
            
        # Atualizar habilidades
        for skill, level in skills.items():
            self.person_skills[person_id][skill] = level
        
        # Salvar no pipeline se disponível
        if self.data_pipeline:
            self.data_pipeline.update_person_skills(person_id, skills)
        
        return True
    
    def calculate_position_match(self, person_id: str, position_id: str) -> Dict[str, Any]:
        """
        Calcula o grau de compatibilidade entre uma pessoa e uma posição.
        
        Args:
            person_id: ID da pessoa
            position_id: ID da posição
            
        Returns:
            Métricas de compatibilidade
        """
        if position_id not in self.positions:
            raise ValueError(f"Posição {position_id} não encontrada")
            
        if person_id not in self.person_skills:
            raise ValueError(f"Habilidades da pessoa {person_id} não encontradas")
        
        position = self.positions[position_id]
        person_skills = self.person_skills[person_id]
        
        # Calcular match por habilidade
        skill_matches = {}
        total_match = 0.0
        required_skills = 0
        
        for skill, required_level in position.skills_required.items():
            person_level = person_skills.get(skill, 0.0)
            
            # Match para esta habilidade
            if required_level > 0:
                skill_match = min(person_level / required_level, 1.0)
                skill_matches[skill] = skill_match
                total_match += skill_match
                required_skills += 1
            else:
                skill_matches[skill] = 1.0
        
        # Match geral
        overall_match = total_match / required_skills if required_skills > 0 else 0.0
        
        # Habilidades ausentes ou com baixo match
        skill_gaps = {
            skill: required - person_skills.get(skill, 0.0)
            for skill, required in position.skills_required.items()
            if required > person_skills.get(skill, 0.0)
        }
        
        return {
            'person_id': person_id,
            'position_id': position_id,
            'position_title': position.title,
            'overall_match': overall_match,
            'skill_matches': skill_matches,
            'skill_gaps': skill_gaps,
            'readiness': 'Alto' if overall_match >= 0.8 else 'Médio' if overall_match >= 0.5 else 'Baixo'
        }
    
    def find_next_positions(self, 
                         person_id: str, 
                         current_position_id: str,
                         limit: int = 5) -> List[Dict[str, Any]]:
        """
        Encontra as melhores próximas posições para uma pessoa.
        
        Args:
            person_id: ID da pessoa
            current_position_id: ID da posição atual
            limit: Número máximo de posições a retornar
            
        Returns:
            Lista de próximas posições com métricas
        """
        if current_position_id not in self.positions:
            raise ValueError(f"Posição atual {current_position_id} não encontrada")
            
        current_position = self.positions[current_position_id]
        
        # Encontrar todas as possíveis transições a partir da posição atual
        possible_next = []
        
        for (from_id, to_id), probability in self.transitions.items():
            if from_id == current_position_id and probability > 0:
                # Calcular match para esta posição
                match_data = self.calculate_position_match(person_id, to_id)
                
                # Combinar probabilidade de transição com match de habilidades
                combined_score = probability * 0.4 + match_data['overall_match'] * 0.6
                
                # Obter informações da posição
                position = self.positions[to_id]
                
                possible_next.append({
                    'position_id': to_id,
                    'title': position.title,
                    'level': position.level,
                    'track': position.track,
                    'department': position.department,
                    'transition_probability': probability,
                    'skill_match': match_data['overall_match'],
                    'combined_score': combined_score,
                    'level_change': position.level - current_position.level,
                    'track_change': position.track != current_position.track,
                    'department_change': position.department != current_position.department
                })
        
        # Ordenar por score combinado
        possible_next.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return possible_next[:limit]
    
    def simulate_career_path(self, 
                          person_id: str,
                          current_position_id: str,
                          years: int = 5,
                          num_paths: int = 3) -> List[CareerPath]:
        """
        Simula possíveis caminhos de carreira para uma pessoa.
        
        Args:
            person_id: ID da pessoa
            current_position_id: ID da posição atual
            years: Anos a simular
            num_paths: Número de caminhos a gerar
            
        Returns:
            Lista de caminhos de carreira simulados
        """
        if current_position_id not in self.positions:
            raise ValueError(f"Posição atual {current_position_id} não encontrada")
            
        # Simular múltiplos caminhos
        paths = []
        
        for i in range(num_paths):
            path_id = f"path_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{i+1}"
            
            # Iniciar com posição atual
            positions = [(current_position_id, 0)]  # (position_id, time_in_position)
            total_time = 0
            current_id = current_position_id
            
            # Simular até atingir o tempo total
            while total_time < years:
                current_position = self.positions[current_id]
                
                # Decidir quanto tempo fica nesta posição
                # Usar distribuição normal em torno da média
                tenure = max(1, min(
                    round(np.random.normal(current_position.avg_tenure, 1.0)),
                    years - total_time
                ))
                
                # Atualizar tempo na posição atual
                positions[-1] = (current_id, tenure)
                total_time += tenure
                
                # Se ainda não atingiu o tempo total, buscar próxima posição
                if total_time < years:
                    # Encontrar possíveis próximas posições
                    next_positions = []
                    
                    for (from_id, to_id), probability in self.transitions.items():
                        if from_id == current_id and probability > 0:
                            next_positions.append((to_id, probability))
                    
                    # Se não há transições, permanecer na mesma posição
                    if not next_positions:
                        positions[-1] = (current_id, positions[-1][1] + (years - total_time))
                        total_time = years
                        break
                    
                    # Escolher próxima posição baseado nas probabilidades
                    ids, probs = zip(*next_positions)
                    probs = np.array(probs) / sum(probs)  # Normalizar
                    next_id = np.random.choice(ids, p=probs)
                    
                    # Adicionar próxima posição
                    positions.append((next_id, 0))
                    current_id = next_id
            
            # Calcular métrica de crescimento
            growth_score = self._calculate_growth_score(positions)
            
            # Calcular probabilidade deste caminho
            path_probability = self._calculate_path_probability(positions)
            
            # Criar objeto de caminho
            path = CareerPath(
                path_id=path_id,
                person_id=person_id,
                positions=positions,
                total_time=years,
                growth_score=growth_score,
                probability=path_probability,
                attributes={
                    'final_level': self.positions[positions[-1][0]].level,
                    'positions_count': len(positions),
                    'tracks': set(self.positions[pos[0]].track for pos, _ in positions),
                    'departments': set(self.positions[pos[0]].department for pos, _ in positions)
                }
            )
            
            paths.append(path)
        
        # Ordenar caminhos por score de crescimento
        paths.sort(key=lambda x: x.growth_score, reverse=True)
        
        # Armazenar caminhos simulados
        self.simulated_paths[person_id] = paths
        
        return paths
    
    def _calculate_growth_score(self, positions: List[Tuple[str, int]]) -> float:
        """
        Calcula score de crescimento para um caminho.
        
        Args:
            positions: Lista de posições e tempos
            
        Returns:
            Score de crescimento (0-1)
        """
        # Se só tem uma posição, não houve crescimento
        if len(positions) <= 1:
            return 0.0
        
        # Inicializar métricas
        level_growth = 0
        total_potential = 0
        
        # Calcular mudanças de nível e potencial acumulado
        prev_level = self.positions[positions[0][0]].level
        
        for (pos_id, time) in positions[1:]:
            current_level = self.positions[pos_id].level
            level_growth += max(0, current_level - prev_level)
            total_potential += self.positions[pos_id].growth_potential * time
            prev_level = current_level
        
        # Normalizar em 0-1
        normalized_growth = min(level_growth / 3.0, 1.0)  # Assumindo que crescer 3 níveis é máximo
        normalized_potential = min(total_potential / 5.0, 1.0)  # Normalizando pelo tempo total
        
        # Combinar métricas
        return normalized_growth * 0.7 + normalized_potential * 0.3
    
    def _calculate_path_probability(self, positions: List[Tuple[str, int]]) -> float:
        """
        Calcula probabilidade de um caminho ocorrer.
        
        Args:
            positions: Lista de posições e tempos
            
        Returns:
            Probabilidade (0-1)
        """
        # Se só tem uma posição, probabilidade é 1
        if len(positions) <= 1:
            return 1.0
        
        # Multiplicar probabilidades de transição
        probability = 1.0
        
        for i in range(len(positions) - 1):
            from_id = positions[i][0]
            to_id = positions[i+1][0]
            
            trans_prob = self.transitions.get((from_id, to_id), 0.0)
            probability *= trans_prob
        
        return probability
    
    def visualize_career_path(self, 
                           path: CareerPath,
                           output_path: Optional[Path] = None) -> Path:
        """
        Visualiza um caminho de carreira simulado.
        
        Args:
            path: Caminho a visualizar
            output_path: Caminho para salvar a visualização
            
        Returns:
            Caminho do arquivo salvo
        """
        # Criar figura
        plt.figure(figsize=(12, 6))
        
        # Preparar dados para visualização
        positions = []
        levels = []
        durations = []
        colors = []
        
        current_year = 0
        for pos_id, duration in path.positions:
            position = self.positions[pos_id]
            positions.append(position.title)
            levels.append(position.level)
            durations.append(duration)
            
            # Cor com base na trilha
            if position.track == 'técnica':
                colors.append('royalblue')
            elif position.track == 'gestão':
                colors.append('darkgreen')
            elif position.track == 'especialista':
                colors.append('purple')
            else:
                colors.append('gray')
            
            current_year += duration
        
        # Criar timeline
        fig, ax = plt.subplots(figsize=(12, 6))
        
        current_year = 0
        y_positions = []
        
        for i, (title, level, duration, color) in enumerate(zip(positions, levels, durations, colors)):
            # Posição horizontal
            start = current_year
            end = current_year + duration
            
            # Posição vertical (baseada no nível)
            y_pos = level * 2  # Espaçamento entre níveis
            y_positions.append(y_pos)
            
            # Desenhar barra
            ax.barh(y_pos, duration, left=start, height=1.5, color=color, alpha=0.7)
            
            # Adicionar texto
            ax.text(start + duration/2, y_pos, title, 
                   ha='center', va='center', color='black',
                   fontweight='bold' if i == 0 or i == len(positions)-1 else 'normal')
            
            # Se não for a última posição, adicionar seta
            if i < len(positions) - 1:
                next_level = levels[i+1] * 2
                ax.annotate('', xy=(end, next_level), xytext=(end, y_pos),
                           arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
            
            current_year = end
        
        # Configurar eixos
        ax.set_yticks([level * 2 for level in sorted(set(levels))])
        ax.set_yticklabels([f'Nível {level}' for level in sorted(set(levels))])
        ax.set_xlabel('Anos')
        ax.set_title(f'Simulação de Carreira - Score de Crescimento: {path.growth_score:.2f}', fontsize=14)
        ax.set_xlim(0, path.total_time)
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Adicionar métricas
        info_text = f"Pessoa: {path.person_id}\n"
        info_text += f"Posições: {len(path.positions)}\n"
        info_text += f"Probabilidade: {path.probability:.2f}\n"
        info_text += f"Nível Final: {levels[-1]}"
        
        plt.figtext(0.02, 0.02, info_text, fontsize=10, 
                  bbox=dict(facecolor='white', alpha=0.8, boxstyle='round'))
        
        plt.tight_layout()
        
        # Salvar figura
        if output_path is None:
            output_path = Path(f'output/carreira_simulacao_{path.path_id}.png')
            
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_career_report(self, 
                            person_id: str,
                            current_position_id: str,
                            output_path: Optional[Path] = None) -> Path:
        """
        Gera um relatório completo de carreira.
        
        Args:
            person_id: ID da pessoa
            current_position_id: ID da posição atual
            output_path: Caminho para salvar o relatório
            
        Returns:
            Caminho do relatório salvo
        """
        # Simular caminhos de carreira se não existir
        if person_id not in self.simulated_paths:
            self.simulate_career_path(person_id, current_position_id)
            
        paths = self.simulated_paths[person_id]
        
        # Calcular match da posição atual
        current_match = self.calculate_position_match(person_id, current_position_id)
        
        # Encontrar próximas posições potenciais
        next_positions = self.find_next_positions(person_id, current_position_id)
        
        # Criar caminho de saída
        if output_path is None:
            output_path = Path(f'output/relatorio_carreira_{person_id}.txt')
            
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Gerar relatório
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"RELATÓRIO DE CARREIRA SIMULADA\n")
            f.write(f"{'='*50}\n\n")
            
            f.write(f"Pessoa: {person_id}\n")
            f.write(f"Data: {datetime.datetime.now().strftime('%d/%m/%Y')}\n\n")
            
            f.write(f"POSIÇÃO ATUAL\n")
            f.write(f"{'-'*50}\n")
            current_position = self.positions[current_position_id]
            f.write(f"Título: {current_position.title}\n")
            f.write(f"Nível: {current_position.level}\n")
            f.write(f"Trilha: {current_position.track}\n")
            f.write(f"Departamento: {current_position.department}\n")
            f.write(f"Compatibilidade: {current_match['overall_match']:.2f} ({current_match['readiness']})\n\n")
            
            # Adicionar lacunas de habilidades
            if current_match['skill_gaps']:
                f.write(f"LACUNAS DE HABILIDADES\n")
                f.write(f"{'-'*50}\n")
                
                for skill, gap in sorted(current_match['skill_gaps'].items(), 
                                       key=lambda x: x[1], reverse=True):
                    f.write(f"{skill}: {gap:.2f}\n")
                f.write("\n")
            
            # Adicionar próximas posições
            f.write(f"PRÓXIMAS POSIÇÕES RECOMENDADAS\n")
            f.write(f"{'-'*50}\n")
            
            for i, position in enumerate(next_positions, 1):
                f.write(f"{i}. {position['title']} (Nível {position['level']})\n")
                f.write(f"   Trilha: {position['track']}\n")
                f.write(f"   Compatibilidade de habilidades: {position['skill_match']:.2f}\n")
                f.write(f"   Probabilidade de transição: {position['transition_probability']:.2f}\n")
                f.write(f"   Score combinado: {position['combined_score']:.2f}\n\n")
            
            # Adicionar simulação de longo prazo
            f.write(f"SIMULAÇÃO DE CARREIRA A LONGO PRAZO\n")
            f.write(f"{'-'*50}\n")
            
            # Ordenar caminhos por score de crescimento
            sorted_paths = sorted(paths, key=lambda x: x.growth_score, reverse=True)
            
            for i, path in enumerate(sorted_paths[:3], 1):  # Top 3 caminhos
                f.write(f"Caminho {i} - Score de Crescimento: {path.growth_score:.2f}\n")
                f.write(f"Probabilidade: {path.probability:.2f}\n")
                f.write(f"Posições: {len(path.positions)}\n")
                f.write(f"Nível final: {self.positions[path.positions[-1][0]].level}\n")
                
                # Detalhes do caminho
                f.write("Sequência:\n")
                
                for j, (pos_id, duration) in enumerate(path.positions, 1):
                    position = self.positions[pos_id]
                    f.write(f"  {j}. {position.title} ({position.track}) - {duration} anos\n")
                
                f.write("\n")
            
            # Adicionar visualizações
            viz_paths = []
            for i, path in enumerate(sorted_paths[:3]):
                viz_path = output_path.parent / f"carreira_simulacao_{person_id}_{i+1}.png"
                self.visualize_career_path(path, viz_path)
                viz_paths.append(viz_path)
                
            if viz_paths:
                f.write(f"VISUALIZAÇÕES\n")
                f.write(f"{'-'*50}\n")
                for i, viz_path in enumerate(viz_paths, 1):
                    f.write(f"Caminho {i}: {viz_path}\n")
                f.write("\n")
            
            f.write(f"RECOMENDAÇÕES\n")
            f.write(f"{'-'*50}\n")
            
            # Gerar recomendações baseadas na análise
            if current_match['overall_match'] < 0.7:
                f.write("1. Focar no desenvolvimento das habilidades com maior lacuna para a posição atual\n")
            else:
                f.write("1. Começar a desenvolver habilidades para próximas posições potenciais\n")
                
            if next_positions and next_positions[0]['transition_probability'] < 0.5:
                f.write("2. Buscar experiências que aumentem a visibilidade para transições futuras\n")
            else:
                f.write("2. Preparar-se ativamente para a próxima transição de carreira\n")
                
            if paths and paths[0].growth_score > 0.6:
                f.write("3. Seguir o caminho de maior crescimento identificado na simulação\n")
            else:
                f.write("3. Explorar trilhas alternativas que possam oferecer maior potencial de crescimento\n")
        
        return output_path 