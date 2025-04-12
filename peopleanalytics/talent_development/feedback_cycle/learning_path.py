"""
Módulo de trilhas de aprendizado personalizadas para desenvolvimento de competências.

Gera recomendações práticas e trilhas de aprendizado baseadas em feedback e gaps
de competências identificados.
"""
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
import datetime
import random


@dataclass
class LearningActivity:
    """Representa uma atividade de aprendizado recomendada."""
    activity_id: str
    title: str
    description: str
    activity_type: str  # 'course', 'book', 'project', 'mentoring', 'practice'
    competency: str
    estimated_hours: int
    difficulty: str  # 'beginner', 'intermediate', 'advanced'
    resources: List[str]
    metrics: List[str]  # Métricas para acompanhar progresso
    prerequisites: List[str] = None


@dataclass
class LearningPath:
    """Representa uma trilha de aprendizado completa."""
    path_id: str
    person_id: str
    title: str
    description: str
    competencies: List[str]
    activities: List[LearningActivity]
    created_at: datetime.datetime
    expires_at: Optional[datetime.datetime] = None
    status: str = "active"  # 'active', 'completed', 'expired'
    
    @property
    def total_hours(self) -> int:
        """Calcula o total de horas estimadas para a trilha."""
        return sum(activity.estimated_hours for activity in self.activities)
    
    @property
    def is_expired(self) -> bool:
        """Verifica se a trilha está expirada."""
        if self.expires_at is None:
            return False
        return datetime.datetime.now() > self.expires_at


class PersonalizedLearningPath:
    """
    Gera trilhas de aprendizado personalizadas com base em feedback e gaps.
    
    Funcionalidades:
    - Recomendação de atividades de aprendizado específicas
    - Priorização baseada em impacto e urgência
    - Sequenciamento lógico de atividades
    - Adaptação ao estilo de aprendizagem da pessoa
    """
    
    def __init__(self):
        """Inicializa o gerador de trilhas de aprendizado."""
        # Aqui teriam recursos de aprendizado pré-cadastrados
        self.learning_resources = {
            "comunicação": self._get_communication_resources(),
            "liderança": self._get_leadership_resources(),
            "pensamento_crítico": self._get_critical_thinking_resources(),
            "trabalho_em_equipe": self._get_teamwork_resources(),
            "resolução_de_problemas": self._get_problem_solving_resources(),
            # Outras competências
        }
    
    def generate_path(self, 
                     person_id: str, 
                     competencies: Dict[str, float],  # competência -> gap (0-4)
                     learning_style: Optional[Dict[str, float]] = None,
                     timeframe_months: int = 6) -> LearningPath:
        """
        Gera uma trilha de aprendizado personalizada.
        
        Args:
            person_id: ID da pessoa
            competencies: Dicionário com competências e seus gaps
            learning_style: Preferências de aprendizado (opcional)
            timeframe_months: Duração da trilha em meses
            
        Returns:
            Trilha de aprendizado personalizada
        """
        # Priorizar competências com maior gap
        prioritized = sorted(
            competencies.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Selecionar os top 3 gaps ou todos se menor que 3
        focus_competencies = [comp for comp, gap in prioritized[:3] if gap > 0.5]
        
        if not focus_competencies:
            # Se não temos gaps significativos, escolher a competência com maior gap
            if prioritized:
                focus_competencies = [prioritized[0][0]]
            else:
                # Caso não haja competências informadas
                focus_competencies = ["comunicação"]  # Default
        
        # Atividades selecionadas para a trilha
        selected_activities = []
        
        # Para cada competência focal, selecionar atividades
        for competency in focus_competencies:
            # Pegar o gap para esta competência
            gap = competencies.get(competency, 1.0)
            
            # Determinar quantas atividades selecionar com base no gap
            num_activities = min(3, max(1, int(gap * 2)))
            
            # Obter recursos disponíveis para esta competência
            available_resources = self.learning_resources.get(
                competency, 
                self.learning_resources.get("comunicação")  # fallback
            )
            
            # Selecionar atividades adequadas ao nível do gap
            if gap < 1.0:  # Gap pequeno
                difficulty = "beginner"
            elif gap < 2.0:  # Gap médio
                difficulty = "intermediate"
            else:  # Gap grande
                difficulty = "advanced"
            
            # Filtrar por dificuldade
            filtered_resources = [
                r for r in available_resources 
                if r.get("difficulty", "intermediate") == difficulty
            ]
            
            # Se não tiver suficientes na dificuldade específica, usar todos
            if len(filtered_resources) < num_activities:
                filtered_resources = available_resources
            
            # Selecionar aleatoriamente (em uma implementação real, seria mais sofisticado)
            selected = random.sample(
                filtered_resources, 
                min(num_activities, len(filtered_resources))
            )
            
            # Converter para objetos LearningActivity
            for i, resource in enumerate(selected):
                activity = LearningActivity(
                    activity_id=f"act_{person_id}_{competency}_{i}",
                    title=resource.get("title", "Atividade sem título"),
                    description=resource.get("description", ""),
                    activity_type=resource.get("type", "practice"),
                    competency=competency,
                    estimated_hours=resource.get("hours", 10),
                    difficulty=resource.get("difficulty", "intermediate"),
                    resources=resource.get("resources", []),
                    metrics=resource.get("metrics", ["autoavaliação"])
                )
                selected_activities.append(activity)
        
        # Criar a trilha completa
        expiration = datetime.datetime.now() + datetime.timedelta(days=30*timeframe_months)
        
        path = LearningPath(
            path_id=f"path_{person_id}_{datetime.datetime.now().strftime('%Y%m%d')}",
            person_id=person_id,
            title=f"Desenvolvimento de {', '.join(focus_competencies)}",
            description=f"Trilha personalizada para desenvolvimento de {len(focus_competencies)} competências prioritárias",
            competencies=focus_competencies,
            activities=selected_activities,
            created_at=datetime.datetime.now(),
            expires_at=expiration,
            status="active"
        )
        
        return path
    
    def _get_communication_resources(self) -> List[Dict[str, Any]]:
        """Retorna recursos de aprendizado para comunicação."""
        return [
            {
                "title": "Comunicação Assertiva no Ambiente de Trabalho",
                "description": "Aprenda técnicas para comunicar suas ideias com clareza e assertividade.",
                "type": "course",
                "difficulty": "beginner",
                "hours": 8,
                "resources": ["https://example.com/course1", "Livro: Comunicação Não-Violenta"],
                "metrics": ["feedback 360 sobre clareza", "autoavaliação de confiança"]
            },
            {
                "title": "Storytelling para Apresentações de Impacto",
                "description": "Técnicas para estruturar narrativas envolventes em apresentações profissionais.",
                "type": "workshop",
                "difficulty": "intermediate",
                "hours": 12,
                "resources": ["Workshop interno", "Template de estrutura narrativa"],
                "metrics": ["avaliação de apresentações", "engajamento da audiência"]
            },
            {
                "title": "Projeto: Liderar Reuniões Estratégicas",
                "description": "Planeje e conduza 3 reuniões estratégicas aplicando técnicas de facilitação avançadas.",
                "type": "project",
                "difficulty": "advanced",
                "hours": 20,
                "resources": ["Guia de facilitação", "Mentoria com líder sênior"],
                "metrics": ["feedback dos participantes", "eficácia das decisões tomadas"]
            }
        ]
    
    def _get_leadership_resources(self) -> List[Dict[str, Any]]:
        """Retorna recursos de aprendizado para liderança."""
        return [
            {
                "title": "Fundamentos de Liderança Situacional",
                "description": "Entenda como adaptar seu estilo de liderança às necessidades da equipe.",
                "type": "course",
                "difficulty": "beginner",
                "hours": 10,
                "resources": ["Curso online", "Estudo de caso"],
                "metrics": ["autoavaliação", "feedback da equipe"]
            },
            {
                "title": "Mentoria em Gestão de Equipes",
                "description": "Sessões de mentoria com um líder experiente para discutir desafios reais.",
                "type": "mentoring",
                "difficulty": "intermediate",
                "hours": 15,
                "resources": ["Sessões quinzenais", "Diário de aprendizado"],
                "metrics": ["aplicação prática", "crescimento da equipe"]
            },
            {
                "title": "Projeto de Transformação de Equipe",
                "description": "Lidere uma iniciativa para melhorar a performance e engajamento da sua equipe.",
                "type": "project",
                "difficulty": "advanced",
                "hours": 30,
                "resources": ["Framework de transformação", "Workshops de equipe"],
                "metrics": ["indicadores de performance", "pesquisa de clima"]
            }
        ]
    
    def _get_critical_thinking_resources(self) -> List[Dict[str, Any]]:
        """Retorna recursos de aprendizado para pensamento crítico."""
        return [
            {
                "title": "Análise de Decisões e Vieses Cognitivos",
                "description": "Aprenda a identificar e mitigar vieses em processos decisórios.",
                "type": "course",
                "difficulty": "beginner",
                "hours": 6,
                "resources": ["Artigos selecionados", "Exercícios práticos"],
                "metrics": ["teste de reconhecimento de vieses", "qualidade das decisões"]
            },
            {
                "title": "Técnicas de Resolução de Problemas Complexos",
                "description": "Frameworks e métodos para abordar problemas não-estruturados.",
                "type": "workshop",
                "difficulty": "intermediate",
                "hours": 16,
                "resources": ["Oficina prática", "Toolkit de resolução de problemas"],
                "metrics": ["aplicação em casos reais", "feedback de stakeholders"]
            },
            {
                "title": "Clube do Livro de Pensamento Crítico",
                "description": "Grupo de discussão sobre obras que estimulam o pensamento crítico.",
                "type": "practice",
                "difficulty": "advanced",
                "hours": 24,
                "resources": ["Lista de leituras", "Roteiro de discussão"],
                "metrics": ["contribuições às discussões", "insights implementados"]
            }
        ]
    
    def _get_teamwork_resources(self) -> List[Dict[str, Any]]:
        """Retorna recursos de aprendizado para trabalho em equipe."""
        return [
            {
                "title": "Colaboração Efetiva em Ambientes Diversos",
                "description": "Estratégias para colaborar produtivamente em equipes multidisciplinares.",
                "type": "course",
                "difficulty": "beginner",
                "hours": 8,
                "resources": ["Módulos online", "Simulações de caso"],
                "metrics": ["autoavaliação", "percepção dos colegas"]
            },
            {
                "title": "Facilitação de Dinâmicas Colaborativas",
                "description": "Aprenda a facilitar sessões de trabalho que maximizam a contribuição do grupo.",
                "type": "workshop",
                "difficulty": "intermediate",
                "hours": 12,
                "resources": ["Workshop presencial", "Kit de ferramentas de facilitação"],
                "metrics": ["feedback dos participantes", "resultados das sessões"]
            },
            {
                "title": "Projeto Interfuncional",
                "description": "Participe de um projeto que exige colaboração entre diferentes áreas.",
                "type": "project",
                "difficulty": "advanced",
                "hours": 40,
                "resources": ["Mentoria de projeto", "Framework de colaboração"],
                "metrics": ["avaliação 360", "entrega de resultados"]
            }
        ]
    
    def _get_problem_solving_resources(self) -> List[Dict[str, Any]]:
        """Retorna recursos de aprendizado para resolução de problemas."""
        return [
            {
                "title": "Fundamentos de Design Thinking",
                "description": "Introdução à abordagem centrada no usuário para resolução de problemas.",
                "type": "course",
                "difficulty": "beginner",
                "hours": 10,
                "resources": ["Curso interativo", "Toolkit de Design Thinking"],
                "metrics": ["aplicação das etapas", "feedback do instrutor"]
            },
            {
                "title": "Análise de Causa Raiz e Técnicas 5-Whys",
                "description": "Métodos para identificar causas fundamentais em vez de sintomas superficiais.",
                "type": "workshop",
                "difficulty": "intermediate",
                "hours": 8,
                "resources": ["Workshop prático", "Modelos de análise"],
                "metrics": ["qualidade das análises", "eficácia das soluções"]
            },
            {
                "title": "Resolução de Casos Estratégicos",
                "description": "Aplique metodologias avançadas em casos complexos da organização.",
                "type": "project",
                "difficulty": "advanced",
                "hours": 30,
                "resources": ["Biblioteca de casos", "Mentoria especializada"],
                "metrics": ["impacto das soluções", "adoção pelos stakeholders"]
            }
        ] 