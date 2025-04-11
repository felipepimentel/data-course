import os
import yaml
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union
import logging
from datetime import datetime

class ManagerFeedback:
    def __init__(self, data_path: Path, output_path: Path):
        self.data_path = data_path
        self.output_path = output_path
        self.feedback_path = self.data_path / "manager_feedback"
        self.logger = logging.getLogger(__name__)
        
        # Create manager feedback directory if it doesn't exist
        self.feedback_path.mkdir(parents=True, exist_ok=True)
    
    def generate_template(self, employee_name: str, role_level: str = "mid") -> Path:
        """
        Generate a feedback template for a specific employee based on their role level.
        
        Args:
            employee_name: Name of the employee
            role_level: Level of the employee (jr, mid, senior, techlead)
            
        Returns:
            Path to the generated template file
        """
        valid_levels = ["jr", "mid", "senior", "techlead"]
        if role_level not in valid_levels:
            self.logger.warning(f"Invalid role level: {role_level}. Using 'mid' as default.")
            role_level = "mid"
        
        template_content = self._get_template_by_level(employee_name, role_level)
        
        # Create template file
        template_file = self.feedback_path / f"{employee_name}_manager_feedback.md"
        with open(template_file, 'w') as f:
            f.write(template_content)
            
        return template_file
        
    def _get_template_by_level(self, name: str, level: str) -> str:
        """Get the appropriate template based on employee level"""
        templates = {
            "jr": self._junior_template(name),
            "mid": self._mid_template(name),
            "senior": self._senior_template(name),
            "techlead": self._techlead_template(name)
        }
        
        return templates.get(level, self._mid_template(name))
        
    def _junior_template(self, name: str) -> str:
        """Template para engenheiros de software júnior"""
        return f"""# Formulário de Feedback do Gestor: {name} (Engenheiro de Software Júnior)

## Instruções
- Preencha cada seção com sua avaliação
- Para notas: 1=Precisa de melhoria significativa, 2=Abaixo das expectativas, 3=Atende às expectativas, 4=Excede expectativas, 5=Excepcional
- Para perguntas sim/não: S=Sim, N=Não, P=Parcialmente
- Adicione comentários detalhados para fornecer contexto

## Competências Técnicas

### Fundamentos de Programação
- Estruturas de dados e algoritmos básicos: [1-5]
- Legibilidade e organização de código: [1-5]
- Compreensão de controle de versão: [1-5]
- Comentários:

### Práticas de Desenvolvimento
- Segue padrões de codificação: [S/N/P]
- Habilidades de testes unitários: [1-5]
- Habilidades de depuração: [1-5]
- Comentários:

### Stack Tecnológica
- Proficiência em linguagem principal: [1-5]
- Conhecimento de frameworks: [1-5]
- Conhecimento de banco de dados/armazenamento: [1-5]
- Comentários:

## Competências Comportamentais

### Comunicação
- Faz perguntas quando está bloqueado: [S/N/P]
- Comunica claramente seu progresso: [1-5]
- Receptividade a feedback: [1-5]
- Comentários:

### Trabalho em Equipe
- Colabora efetivamente: [1-5]
- Ajuda colegas de equipe quando possível: [S/N/P]
- Participa de discussões em equipe: [1-5]
- Comentários:

### Gestão de Trabalho
- Cumpre prazos: [S/N/P]
- Gestão de tempo: [1-5]
- Atenção aos detalhes: [1-5]
- Comentários:

## Mentalidade de Crescimento
- Busca ativamente aprender novas tecnologias: [1-5]
- Resiliência diante de desafios: [1-5]
- Aplicação de feedback recebido: [1-5]
- Comentários:

## Áreas de Crescimento

### Áreas de Foco Atuais
- Liste 2-3 áreas principais que precisam de atenção:
  1. 
  2. 
  3. 

### Plano de Aprendizado
- Habilidades específicas para desenvolver nos próximos 6 meses:
  1. 
  2. 
  3. 

## Avaliação Geral
- Nota de desempenho geral: [1-5]
- Pronto para promoção: [S/N]
- Tempo estimado para promoção (meses): 

## Plano de Desenvolvimento
- Objetivos principais de crescimento:
  1. 
  2. 
  3. 

- Recursos necessários:
  1. 
  2. 

## Indicadores para o Próximo Nível
- Demonstra consistência técnica em todos os projetos
- Começa a reconhecer padrões de código e aplicar soluções adequadas
- Requer menos supervisão em tarefas rotineiras
- Identifica e resolve problemas de forma independente
- Contribui para discussões técnicas da equipe

## Comentários Adicionais
"""

    def _mid_template(self, name: str) -> str:
        """Template para engenheiros de software pleno"""
        return f"""# Formulário de Feedback do Gestor: {name} (Engenheiro de Software Pleno)

## Instruções
- Preencha cada seção com sua avaliação
- Para notas: 1=Precisa de melhoria significativa, 2=Abaixo das expectativas, 3=Atende às expectativas, 4=Excede expectativas, 5=Excepcional
- Para perguntas sim/não: S=Sim, N=Não, P=Parcialmente
- Adicione comentários detalhados para fornecer contexto

## Competências Técnicas

### Expertise em Programação
- Qualidade e padrões de código: [1-5]
- Design de sistemas (nível de componente): [1-5]
- Otimização de desempenho: [1-5]
- Comentários:

### Práticas de Desenvolvimento de Software
- Cobertura e qualidade de testes: [1-5]
- Compreensão de CI/CD: [1-5]
- Qualidade das revisões de código: [1-5]
- Comentários:

### Stack Tecnológica
- Proficiência em linguagens (múltiplas): [1-5]
- Compreensão de arquitetura: [1-5]
- Conhecimento de infraestrutura: [1-5]
- Comentários:

## Contribuições em Projetos

### Propriedade
- Assume responsabilidade por features: [S/N/P]
- Entrega soluções completas: [1-5]
- Gerencia complexidade adequadamente: [1-5]
- Comentários:

### Inovação
- Sugere melhorias: [S/N/P]
- Abordagem de resolução de problemas: [1-5]
- Criatividade técnica: [1-5]
- Comentários:

### Impacto no Negócio
- Entende o impacto de seu trabalho: [1-5]
- Prioriza tarefas com base no valor para o negócio: [1-5]
- Equilibra dívida técnica e entregas: [1-5]
- Comentários:

## Competências de Liderança

### Comunicação
- Documentação técnica: [1-5]
- Comunicação entre equipes: [1-5]
- Clarificação de requisitos: [1-5]
- Comentários:

### Liderança
- Mentoria de engenheiros júnior: [S/N/P]
- Toma iniciativa: [1-5]
- Influencia decisões da equipe: [1-5]
- Comentários:

### Gestão de Trabalho
- Planejamento e estimativas: [1-5]
- Gerencia múltiplas prioridades: [1-5]
- Confiabilidade e consistência: [1-5]
- Comentários:

## Mentalidade de Produto
- Foco no usuário final: [1-5]
- Compreensão das necessidades do negócio: [1-5]
- Pensamento orientado a valor: [1-5]
- Comentários:

## Áreas de Crescimento

### Áreas de Foco Atuais
- Liste 2-3 áreas principais que precisam de atenção:
  1. 
  2. 
  3. 

### Trajetória de Carreira
- Preferência por especialista ou líder técnico:
- Interesses de especialização técnica:
- Próximos desafios desejados:

## Avaliação Geral
- Nota de desempenho geral: [1-5]
- Pronto para promoção: [S/N]
- Tempo estimado para promoção (meses): 

## Plano de Desenvolvimento
- Objetivos principais de crescimento:
  1. 
  2. 
  3. 

- Recursos necessários:
  1. 
  2. 

## Indicadores para o Próximo Nível
- Demonstra liderança técnica em projetos significativos
- Influencia arquitetura e decisões técnicas importantes
- Mentora efetivamente outros desenvolvedores
- Resolve problemas complexos com soluções escaláveis
- Simplifica sistemas complexos e reduz dívida técnica
- Comunica-se efetivamente com stakeholders de outras áreas

## Comentários Adicionais
"""

    def _senior_template(self, name: str) -> str:
        """Template para engenheiros de software sênior"""
        return f"""# Formulário de Feedback do Gestor: {name} (Engenheiro de Software Sênior)

## Instruções
- Preencha cada seção com sua avaliação
- Para notas: 1=Precisa de melhoria significativa, 2=Abaixo das expectativas, 3=Atende às expectativas, 4=Excede expectativas, 5=Excepcional
- Para perguntas sim/não: S=Sim, N=Não, P=Parcialmente
- Adicione comentários detalhados para fornecer contexto

## Liderança Técnica

### Design de Sistemas
- Habilidades de design de arquitetura: [1-5]
- Considerações de escalabilidade: [1-5]
- Foco em segurança e desempenho: [1-5]
- Comentários:

### Profundidade Técnica
- Conhecimento profundo de domínio: [1-5]
- Gestão de dívida técnica: [1-5]
- Resolução de problemas complexos: [1-5]
- Comentários:

### Amplitude Técnica
- Capacidades full-stack: [1-5]
- Entendimento cross-platform: [1-5]
- Habilidades de avaliação de tecnologias: [1-5]
- Comentários:

## Impacto em Projetos

### Liderança de Projetos
- Tomada de decisões técnicas: [1-5]
- Participação no planejamento de projetos: [1-5]
- Comunicação com stakeholders: [1-5]
- Comentários:

### Facilitação da Equipe
- Qualidade e profundidade das revisões de código: [1-5]
- Compartilhamento de conhecimento: [1-5]
- Mentoria técnica: [1-5]
- Comentários:

### Impacto no Negócio
- Entende objetivos do negócio: [S/N/P]
- Alinha soluções técnicas com necessidades do negócio: [1-5]
- Entrega alto valor para o negócio: [1-5]
- Comentários:

## Competências de Liderança

### Influência
- Influencia sem autoridade formal: [1-5]
- Resolução de conflitos: [1-5]
- Motivação da equipe: [1-5]
- Comentários:

### Pensamento Estratégico
- Visão técnica de longo prazo: [1-5]
- Análise de trade-offs técnicos: [1-5]
- Mentalidade de inovação: [1-5]
- Comentários:

### Comunicação
- Apresentações técnicas: [1-5]
- Comunicação com executivos: [1-5]
- Escrita técnica: [1-5]
- Comentários:

## Construção de Time de Alta Performance

### Cultura de Excelência
- Estabelece padrões de qualidade: [1-5]
- Promove revisões de código eficazes: [1-5]
- Incentiva práticas de engenharia sólidas: [1-5]
- Comentários:

### Desenvolvimento de Pessoas
- Identifica áreas de crescimento para membros da equipe: [1-5]
- Fornece feedback construtivo: [1-5]
- Cria oportunidades de aprendizado: [1-5]
- Comentários:

### Eficiência Operacional
- Melhora processos de desenvolvimento: [1-5]
- Identifica e resolve gargalos: [1-5]
- Facilita entrega contínua: [1-5]
- Comentários:

## Áreas de Crescimento

### Áreas de Foco Atuais
- Liste 2-3 áreas principais que precisam de atenção:
  1. 
  2. 
  3. 

### Trajetória de Carreira
- Interesse em liderança técnica ou gestão:
- Áreas para maior responsabilidade:
- Próximos desafios desejados:

## Avaliação Geral
- Nota de desempenho geral: [1-5]
- Pronto para promoção: [S/N]
- Potencial de liderança: [1-5]
- Tempo estimado para promoção/mudança de papel (meses): 

## Plano de Desenvolvimento
- Objetivos principais de crescimento:
  1. 
  2. 
  3. 

- Recursos necessários:
  1. 
  2. 

## Indicadores para o Próximo Nível
- Orienta decisões técnicas estratégicas para a organização
- Desenvolve arquiteturas que suportam objetivos de negócio de longo prazo
- Constrói e lidera times de alta performance
- Contribui para a estratégia técnica além de sua própria equipe
- Influencia a cultura de engenharia da organização como um todo
- Representa a empresa em eventos e comunidades técnicas

## Comentários Adicionais
"""

    def _techlead_template(self, name: str) -> str:
        """Template para tech leads"""
        return f"""# Formulário de Feedback do Gestor: {name} (Tech Lead)

## Instruções
- Preencha cada seção com sua avaliação
- Para notas: 1=Precisa de melhoria significativa, 2=Abaixo das expectativas, 3=Atende às expectativas, 4=Excede expectativas, 5=Excepcional
- Para perguntas sim/não: S=Sim, N=Não, P=Parcialmente
- Adicione comentários detalhados para fornecer contexto

## Liderança Técnica

### Arquitetura e Visão
- Qualidade da arquitetura de sistemas: [1-5]
- Planejamento de roadmap técnico: [1-5]
- Seleção de tecnologias: [1-5]
- Comentários:

### Governança Técnica
- Padrões de qualidade de código: [1-5]
- Gestão de dívida técnica: [1-5]
- Processo de revisão de arquitetura: [1-5]
- Comentários:

### Excelência em Engenharia
- Melhorias no processo de desenvolvimento: [1-5]
- Estratégia de testes: [1-5]
- Foco em DevOps/Automação: [1-5]
- Comentários:

## Liderança de Equipe

### Desenvolvimento da Equipe
- Crescimento técnico da equipe: [1-5]
- Efetividade de mentoria: [1-5]
- Distribuição de conhecimento: [1-5]
- Comentários:

### Gestão de Entregas
- Previsibilidade de entregas: [1-5]
- Identificação e mitigação de riscos: [1-5]
- Alocação de recursos: [1-5]
- Comentários:

### Gestão de Stakeholders
- Levantamento de requisitos: [1-5]
- Gestão de expectativas: [1-5]
- Colaboração entre equipes: [1-5]
- Comentários:

## Impacto Estratégico

### Alinhamento com o Negócio
- Entendimento da estratégia de negócios: [1-5]
- Soluções técnicas alinhadas com objetivos de negócio: [1-5]
- Identificação proativa de problemas: [1-5]
- Comentários:

### Liderança de Inovação
- Incentiva inovação na equipe: [S/N/P]
- Experimenta com novas tecnologias: [1-5]
- Equilibra inovação com estabilidade: [1-5]
- Comentários:

### Influência Organizacional
- Influência cross-funcional: [1-5]
- Advocacia técnica: [1-5]
- Impacto na cultura de engenharia: [1-5]
- Comentários:

## Construção de Times de Alta Performance

### Formação de Equipe
- Identificação e desenvolvimento de talentos: [1-5]
- Promoção de diversidade técnica na equipe: [1-5]
- Criação de ambiente psicologicamente seguro: [1-5]
- Comentários:

### Processos Ágeis
- Implementação efetiva de práticas ágeis: [1-5]
- Adaptação de processos às necessidades da equipe: [1-5]
- Facilitação de retrospectivas e melhorias contínuas: [1-5]
- Comentários:

### Cultura de Qualidade
- Estabelecimento de práticas de código limpo: [1-5]
- Implementação de testes automatizados: [1-5]
- Promoção de entregas pequenas e frequentes: [1-5]
- Comentários:

## Áreas de Crescimento

### Áreas de Foco Atuais
- Liste 2-3 áreas principais que precisam de atenção:
  1. 
  2. 
  3. 

### Desenvolvimento de Liderança
- Interesse em gestão de pessoas: [S/N/P]
- Habilidades de liderança a desenvolver:
  1. 
  2. 

## Avaliação Geral
- Nota de desempenho geral: [1-5]
- Pronto para próximo papel: [S/N]
- Papéis futuros potenciais:
- Tempo estimado para mudança de papel (meses): 

## Plano de Desenvolvimento
- Objetivos principais de crescimento:
  1. 
  2. 
  3. 

- Recursos necessários:
  1. 
  2. 

## Indicadores para o Próximo Nível
- Lidera múltiplas equipes ou iniciativas de engenharia de grande porte
- Define a visão técnica para uma área significativa da organização
- Demonstra impacto na construção de times de alta performance
- Influencia a estratégia de produto através de liderança técnica
- Reconhecido como referência técnica dentro e fora da organização
- Contribui para o crescimento e desenvolvimento de outros líderes técnicos

## Comentários Adicionais
"""

    def parse_feedback(self, employee_name: str) -> Optional[Dict]:
        """
        Parse the manager feedback form for a specific employee.
        
        Args:
            employee_name: Name of the employee
            
        Returns:
            Dictionary with parsed feedback data or None if file doesn't exist
        """
        feedback_file = self.feedback_path / f"{employee_name}_manager_feedback.md"
        
        if not feedback_file.exists():
            self.logger.warning(f"Feedback file not found for {employee_name}")
            return None
            
        return self._parse_markdown_feedback(feedback_file)
        
    def _parse_markdown_feedback(self, file_path: Path) -> Dict:
        """Parse a markdown feedback file into a structured dictionary"""
        data = {"raw_content": "", "sections": {}}
        current_section = None
        current_subsection = None
        
        with open(file_path, 'r') as f:
            content = f.readlines()
            data["raw_content"] = "".join(content)
            
            for line in content:
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                    
                # Detect main sections (## headers)
                if line.startswith("## "):
                    current_section = line[3:].strip()
                    current_subsection = None
                    data["sections"][current_section] = {}
                    continue
                    
                # Detect subsections (### headers)
                if line.startswith("### "):
                    current_subsection = line[4:].strip()
                    if current_section:
                        data["sections"][current_section][current_subsection] = {}
                    continue
                
                # Parse ratings and yes/no values
                if ": [" in line and current_section and current_subsection:
                    key, value = line.split(": [", 1)
                    value = value.rstrip("]").strip()
                    data["sections"][current_section][current_subsection][key.strip()] = value
                elif ": " in line and current_section:
                    if not current_subsection:
                        key, value = line.split(": ", 1)
                        data["sections"][current_section][key.strip()] = value.strip()
                        
        return data
        
    def generate_feedback_report(self, employee_name: str) -> Optional[str]:
        """
        Gera um relatório abrangente de feedback com base na avaliação do gestor.
        
        Args:
            employee_name: Nome do colaborador
            
        Returns:
            Conteúdo do relatório em markdown ou None se o feedback não existir
        """
        feedback_data = self.parse_feedback(employee_name)
        if not feedback_data:
            return None
            
        # Extrai o nível do colaborador a partir do título
        title = feedback_data["raw_content"].split("\n")[0]
        level = "Desconhecido"
        if "Júnior" in title or "Junior" in title:
            level = "Júnior"
        elif "Pleno" in title or "Mid-Level" in title:
            level = "Pleno"
        elif "Sênior" in title or "Senior" in title:
            level = "Sênior"
        elif "Tech Lead" in title:
            level = "Tech Lead"
            
        # Gera o relatório
        report = f"""# Relatório de Feedback do Gestor: {employee_name}

## Visão Geral
- **Nível de Carreira:** {level}
- **Data do Relatório:** {datetime.now().strftime('%d/%m/%Y')}

## Resumo de Desempenho
"""

        # Adiciona avaliação geral se disponível
        if "Avaliação Geral" in feedback_data["sections"]:
            assessment = feedback_data["sections"]["Avaliação Geral"]
            overall_rating = "N/A"
            promotion_ready = "N/A"
            
            for key, value in assessment.items():
                if "desempenho geral" in key.lower():
                    overall_rating = value
                if "pronto para promoção" in key.lower() or "pronto para próximo papel" in key.lower():
                    promotion_ready = value
                    
            report += f"""
- **Desempenho Geral:** {overall_rating}/5
- **Pronto para Promoção:** {promotion_ready}

"""

        # Adiciona pontos fortes e áreas de desenvolvimento
        report += "## Pontos Fortes\n"
        strengths = []
        
        # Identifica pontos fortes (notas 4-5 ou S)
        for section_name, section in feedback_data["sections"].items():
            if isinstance(section, dict):
                for subsection_name, subsection in section.items():
                    if isinstance(subsection, dict):
                        for key, value in subsection.items():
                            if (value in ["4", "5"] or (value == "S" and "não" not in key.lower())) and "Comentários" not in key:
                                strengths.append(f"- **{subsection_name}: {key}** - Nota: {value}")
        
        if strengths:
            report += "\n".join(strengths[:5])  # Top 5 pontos fortes
        else:
            # Busca comentários sobre pontos fortes
            strengths_from_comments = []
            for section_name, section in feedback_data["sections"].items():
                if isinstance(section, dict):
                    for subsection_name, subsection in section.items():
                        if isinstance(subsection, dict) and "Comentários" in subsection:
                            comment = subsection["Comentários"]
                            if any(pos_word in comment.lower() for pos_word in ["excelente", "forte", "ótimo", "bom", "impressionante"]):
                                strengths_from_comments.append(f"- **{subsection_name}:** {comment}")
            
            if strengths_from_comments:
                report += "\n".join(strengths_from_comments[:3])
            else:
                report += "- Nenhum ponto forte específico identificado com notas altas\n"
            
        # Adiciona áreas de desenvolvimento
        report += "\n\n## Áreas de Desenvolvimento\n"
        development_areas = []
        
        # Identifica áreas de desenvolvimento (notas 1-2 ou N)
        for section_name, section in feedback_data["sections"].items():
            if isinstance(section, dict):
                for subsection_name, subsection in section.items():
                    if isinstance(subsection, dict):
                        for key, value in subsection.items():
                            if (value in ["1", "2"] or (value == "N" and "não" not in key.lower())) and "Comentários" not in key:
                                development_areas.append(f"- **{subsection_name}: {key}** - Nota: {value}")
        
        if development_areas:
            report += "\n".join(development_areas[:5])  # Top 5 áreas de desenvolvimento
        else:
            # Busca comentários sobre áreas de desenvolvimento
            dev_from_comments = []
            for section_name, section in feedback_data["sections"].items():
                if isinstance(section, dict):
                    for subsection_name, subsection in section.items():
                        if isinstance(subsection, dict) and "Comentários" in subsection:
                            comment = subsection["Comentários"]
                            if any(neg_word in comment.lower() for neg_word in ["melhorar", "precisa", "falta", "desenvolver", "aprimorar"]):
                                dev_from_comments.append(f"- **{subsection_name}:** {comment}")
            
            if dev_from_comments:
                report += "\n".join(dev_from_comments[:3])
            else:
                report += "- Nenhuma área de desenvolvimento específica identificada com notas baixas\n"
            
        # Adiciona áreas de foco específicas
        if "Áreas de Crescimento" in feedback_data["sections"]:
            growth = feedback_data["sections"]["Áreas de Crescimento"]
            if "Áreas de Foco Atuais" in growth:
                report += "\n\n## Áreas de Foco\n"
                for key, value in growth["Áreas de Foco Atuais"].items():
                    if "liste" not in key.lower() and value and len(value.strip()) > 0:
                        report += f"- {value}\n"
            
            # Adiciona informações de trajetória de carreira
            if any(k for k in growth.keys() if "Trajetória de Carreira" in k or "Desenvolvimento de Liderança" in k):
                report += "\n\n## Desenvolvimento de Carreira\n"
                for key, items in growth.items():
                    if "Trajetória de Carreira" in key or "Desenvolvimento de Liderança" in key:
                        for item_key, item_value in items.items():
                            if item_value and len(str(item_value).strip()) > 0:
                                report += f"- **{item_key}:** {item_value}\n"
                        
        # Adiciona plano de desenvolvimento
        if "Plano de Desenvolvimento" in feedback_data["sections"]:
            plan = feedback_data["sections"]["Plano de Desenvolvimento"]
            report += "\n\n## Plano de Desenvolvimento\n"
            
            if "Objetivos principais de crescimento" in plan:
                report += "\n### Objetivos de Crescimento\n"
                for key, value in plan["Objetivos principais de crescimento"].items():
                    if value and len(value.strip()) > 0:
                        report += f"- {value}\n"
                        
            if "Recursos necessários" in plan:
                report += "\n### Recursos Necessários\n"
                for key, value in plan["Recursos necessários"].items():
                    if value and len(value.strip()) > 0:
                        report += f"- {value}\n"
                        
        # Adiciona indicadores para o próximo nível
        if "Indicadores para o Próximo Nível" in feedback_data["sections"]:
            indicators = feedback_data["sections"]["Indicadores para o Próximo Nível"]
            if indicators:
                report += "\n\n## Indicadores para Próximo Nível\n"
                for key, value in indicators.items():
                    if value and len(str(value).strip()) > 0:
                        report += f"- {value}\n"
                        
        # Adiciona comentários adicionais
        if "Comentários Adicionais" in feedback_data["sections"]:
            comments = feedback_data["sections"]["Comentários Adicionais"]
            if comments and any(v for v in comments.values() if v and len(str(v).strip()) > 0):
                report += "\n\n## Comentários Adicionais\n"
                for key, value in comments.items():
                    if value and len(str(value).strip()) > 0:
                        report += f"{value}\n"
                        
        return report
        
    def export_feedback_to_excel(self, employee_name: str) -> Optional[Path]:
        """
        Exporta feedback do gestor para formato Excel para análise mais fácil
        
        Args:
            employee_name: Nome do colaborador
            
        Returns:
            Caminho para o arquivo Excel ou None se o feedback não existir
        """
        feedback_data = self.parse_feedback(employee_name)
        if not feedback_data:
            return None
            
        # Cria uma estrutura para Excel
        excel_data = []
        
        for section_name, section in feedback_data["sections"].items():
            if isinstance(section, dict):
                for subsection_name, subsection in section.items():
                    if isinstance(subsection, dict):
                        for key, value in subsection.items():
                            if "Comentários" not in key:
                                excel_data.append({
                                    "Seção": section_name,
                                    "Subseção": subsection_name,
                                    "Métrica": key,
                                    "Avaliação": value
                                })
        
        # Cria DataFrame e salva em Excel
        if excel_data:
            df = pd.DataFrame(excel_data)
            excel_path = self.output_path / f"{employee_name}_feedback_gestor.xlsx"
            df.to_excel(excel_path, index=False)
            return excel_path
            
        return None 