import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
import logging
from datetime import datetime, timedelta
from .manager_feedback import ManagerFeedback
import json

class Sync:
    def __init__(self, data_path: Path, output_path: Path):
        self.data_path = data_path
        self.output_path = output_path
        self.logger = logging.getLogger(__name__)
        self.manager_feedback = ManagerFeedback(data_path, output_path)
    
    def sync(self) -> List[str]:
        """Sync data and generate reports."""
        results = []
        
        # Process career progression data if available
        career_results = self._process_career_progression()
        results.extend(career_results)
        
        # Check for manually created templates and process them
        template_results = self._process_manual_templates()
        results.extend(template_results)
        
        # Generate comprehensive reports
        report_results = self._generate_comprehensive_reports()
        results.extend(report_results)
        
        # Copy NPS model documentation to output directory
        nps_model_path = self.data_path.parent / "README_MODELO_NPS.md"
        if nps_model_path.exists():
            output_docs = self.output_path / "docs"
            output_docs.mkdir(exist_ok=True, parents=True)
            shutil.copy(nps_model_path, output_docs / "MODELO_NPS.md")
            results.append("Copied NPS model documentation to output")
        
        return results
    
    def _sync_individual_reports(self) -> List[str]:
        """Sync individual reports to their respective folders"""
        results = []
        reports_dir = self.output_path / "individual_reports"
        
        if not reports_dir.exists():
            self.logger.warning(f"Reports directory not found: {reports_dir}")
            return ["Error: Reports directory not found"]
        
        # Get all report files
        report_files = list(reports_dir.glob("*.md"))
        if not report_files:
            self.logger.warning("No report files found")
            return ["Error: No report files found"]
        
        # Sync each report
        for report_file in report_files:
            try:
                # Extract person name from filename
                person_name = report_file.stem.split("_")[0]
                
                # Create person's directory if it doesn't exist
                person_dir = self.output_path / person_name
                person_dir.mkdir(exist_ok=True)
                
                # Copy report to person's directory
                dest_file = person_dir / f"individual_report_{report_file.name.split('_')[-1]}"
                shutil.copy2(report_file, dest_file)
                
                results.append(f"Synced {report_file.name} to {person_name}'s directory")
            except Exception as e:
                results.append(f"Error syncing {report_file.name}: {str(e)}")
        
        return results
    
    def _process_manager_feedback(self) -> List[str]:
        """Process manager feedback forms and generate reports"""
        results = []
        feedback_dir = self.data_path / "manager_feedback"
        
        if not feedback_dir.exists():
            # Create templates for each person in individual reports
            results.append(self._create_feedback_templates())
            return results
        
        # Find feedback forms
        feedback_files = list(feedback_dir.glob("*_manager_feedback.md"))
        if not feedback_files:
            results.append("No manager feedback forms found")
            return results
        
        # Process each feedback form
        for feedback_file in feedback_files:
            try:
                # Extract person name from filename
                person_name = feedback_file.stem.split("_")[0]
                
                # Generate feedback report
                feedback_report = self.manager_feedback.generate_feedback_report(person_name)
                if feedback_report:
                    # Create person's directory if it doesn't exist
                    person_dir = self.output_path / person_name
                    person_dir.mkdir(exist_ok=True)
                    
                    # Save feedback report
                    report_file = person_dir / f"manager_feedback_report_{datetime.now().strftime('%Y%m%d')}.md"
                    with open(report_file, 'w') as f:
                        f.write(feedback_report)
                    
                    results.append(f"Generated manager feedback report for {person_name}")
                    
                    # Export to Excel for data analysis
                    excel_path = self.manager_feedback.export_feedback_to_excel(person_name)
                    if excel_path:
                        results.append(f"Exported feedback to Excel for {person_name}")
                
            except Exception as e:
                results.append(f"Error processing feedback for {feedback_file.stem}: {str(e)}")
        
        return results
    
    def _create_feedback_templates(self) -> str:
        """Create feedback templates for all people with individual reports"""
        # Find all people with individual reports
        reports_dir = self.output_path / "individual_reports"
        if not reports_dir.exists():
            return "No individual reports directory found"
        
        report_files = list(reports_dir.glob("*.md"))
        if not report_files:
            return "No individual reports found"
        
        # Create templates for each person
        created_count = 0
        for report_file in report_files:
            person_name = report_file.stem.split("_")[0]
            
            # Determine role level from filename or default to mid
            role_level = "mid"
            
            # Try to determine role level from the report content
            try:
                with open(report_file, 'r') as f:
                    content = f.read().lower()
                    if "senior" in content:
                        role_level = "senior"
                    elif "junior" in content or "jr" in content:
                        role_level = "jr"
                    elif "lead" in content or "tech lead" in content:
                        role_level = "techlead"
            except:
                pass
            
            # Generate template
            self.manager_feedback.generate_template(person_name, role_level)
            created_count += 1
        
        return f"Created {created_count} manager feedback templates"
    
    def _generate_comprehensive_reports(self) -> List[str]:
        """Generate comprehensive reports combining all data sources for each person"""
        results = []
        
        # Find all people directories
        person_dirs = [d for d in self.output_path.glob("*") if d.is_dir() and d.name not in [
            "individual_reports", "logs", "action_plans", "summaries", "heat_maps", 
            "benchmark_reports", "team_reports", "radar_charts", "stakeholder_analysis",
            "ai_prompts", "mermaid", "summary", "reports", "benchmarks", "docs",
            "teams", "time_series", "career_progression"
        ]]
        
        # First, process career progression data
        career_results = self._process_career_progression()
        results.extend(career_results)
        
        for person_dir in person_dirs:
            try:
                person_name = person_dir.name
                
                # Find individual report
                individual_reports = list(person_dir.glob("individual_report_*.md"))
                
                # Find manager feedback report
                manager_reports = list(person_dir.glob("manager_feedback_report_*.md"))
                
                # Find career progression report
                career_reports = list(person_dir.glob("career_progression_*.md"))
                
                # If both types of reports exist, create comprehensive report
                if individual_reports and manager_reports:
                    # Get latest reports
                    individual_report = max(individual_reports, key=lambda x: x.name)
                    manager_report = max(manager_reports, key=lambda x: x.name)
                    
                    # Get career report if available
                    career_report = None
                    if career_reports:
                        career_report = max(career_reports, key=lambda x: x.name)
                    
                    # Create comprehensive report
                    comprehensive_report = self._create_comprehensive_report(
                        person_name, individual_report, manager_report, career_report
                    )
                    
                    # Save report
                    report_file = person_dir / f"comprehensive_report_{datetime.now().strftime('%Y%m%d')}.md"
                    with open(report_file, 'w') as f:
                        f.write(comprehensive_report)
                    
                    results.append(f"Generated comprehensive report for {person_name}")
                    
                    # Create PDI (Personal Development Plan)
                    pdi = self._create_pdi(person_name, individual_report, manager_report, career_report)
                    pdi_file = person_dir / f"personal_development_plan_{datetime.now().strftime('%Y%m%d')}.md"
                    with open(pdi_file, 'w') as f:
                        f.write(pdi)
                    
                    results.append(f"Generated PDI for {person_name}")
                
            except Exception as e:
                results.append(f"Error generating comprehensive report for {person_dir.name}: {str(e)}")
        
        return results
    
    def _process_career_progression(self) -> List[str]:
        """Process career progression data and generate reports"""
        results = []
        career_dir = self.data_path / "career_progression"
        
        if not career_dir.exists():
            # Create directory for career progression data
            career_dir.mkdir(parents=True, exist_ok=True)
            results.append("Created career progression directory")
            return results
        
        # Find career JSON files
        career_files = list(career_dir.glob("*.json"))
        
        if not career_files:
            results.append("No career progression data found")
            return results
        
        # Generate a report for each person with career data
        for career_file in career_files:
            try:
                # Extract person name from filename
                person_name = career_file.stem
                
                # Load the career data
                with open(career_file, 'r', encoding='utf-8') as f:
                    career_data = json.load(f)
                
                # Generate career progression report
                career_report = self._generate_career_report(person_name, career_data)
                
                # Create person's directory if it doesn't exist
                person_dir = self.output_path / person_name
                person_dir.mkdir(exist_ok=True)
                
                # Save career report
                report_file = person_dir / f"career_progression_{datetime.now().strftime('%Y%m%d')}.md"
                with open(report_file, 'w') as f:
                    f.write(career_report)
                
                results.append(f"Generated career progression report for {person_name}")
                
                # Create visualizations for career progression
                self._create_career_visualizations(person_name, career_data, person_dir)
                results.append(f"Created career progression visualizations for {person_name}")
                
            except Exception as e:
                results.append(f"Error processing career data for {career_file.stem}: {str(e)}")
        
        return results
    
    def _create_career_visualizations(self, person_name: str, career_data: Dict[str, Any], output_dir: Path) -> None:
        """Create visualizations for career progression data"""
        try:
            # Create a career timeline visualization (Mermaid format)
            timeline = self._create_career_timeline(person_name, career_data)
            timeline_file = output_dir / f"career_timeline_{datetime.now().strftime('%Y%m%d')}.md"
            with open(timeline_file, 'w') as f:
                f.write(timeline)
            
            # Create a skills radar chart data
            skills_radar = self._create_skills_radar(person_name, career_data)
            skills_file = output_dir / f"skills_radar_{datetime.now().strftime('%Y%m%d')}.json"
            with open(skills_file, 'w') as f:
                json.dump(skills_radar, f, indent=2)
        except Exception as e:
            print(f"Error creating career visualizations for {person_name}: {e}")
    
    def _create_career_timeline(self, person_name: str, career_data: Dict[str, Any]) -> str:
        """Create a Mermaid timeline chart for career events"""
        eventos = career_data.get('eventos_carreira', [])
        
        if not eventos:
            return f"# Linha do Tempo de Carreira: {person_name}\n\nNenhum evento de carreira registrado."
        
        # Sort events by date
        eventos.sort(key=lambda x: x.get('data', ''))
        
        # Create Mermaid timeline
        mermaid = f"""# Linha do Tempo de Carreira: {person_name}

```mermaid
timeline
"""
        
        # Add timeline title
        mermaid += f"    title Trajetória de Carreira de {person_name}\n"
        
        # Group events by year
        years = {}
        for evento in eventos:
            date_str = evento.get('data', '')
            if date_str:
                year = date_str.split('-')[0]
                if year not in years:
                    years[year] = []
                years[year].append(evento)
        
        # Add events to timeline by year
        for year in sorted(years.keys()):
            mermaid += f"    section {year}\n"
            
            for evento in years[year]:
                date = evento.get('data', '').replace('-', '/')
                tipo = evento.get('tipo_evento', '')
                detalhes = evento.get('detalhes', '')
                
                # Format event text based on type
                if tipo == 'promotion':
                    cargo_novo = evento.get('cargo_novo', '')
                    event_text = f"{date}: Promoção para {cargo_novo}"
                elif tipo == 'lateral_move':
                    cargo_novo = evento.get('cargo_novo', '')
                    event_text = f"{date}: Movimento lateral para {cargo_novo}"
                elif tipo == 'role_change':
                    cargo_novo = evento.get('cargo_novo', '')
                    event_text = f"{date}: Mudança de função para {cargo_novo}"
                elif tipo == 'skill_acquisition':
                    event_text = f"{date}: Nova habilidade: {detalhes}"
                elif tipo == 'certification':
                    event_text = f"{date}: Certificação: {detalhes}"
                else:
                    event_text = f"{date}: {tipo} - {detalhes}"
                
                mermaid += f"        {event_text}\n"
        
        mermaid += "```\n"
        
        return mermaid
    
    def _create_skills_radar(self, person_name: str, career_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create data for a skills radar chart"""
        skills = career_data.get('matriz_habilidades', {})
        
        if not skills:
            return {"error": "No skills data available"}
        
        # Group skills by category - assume skills follow a category.skill_name pattern
        # If not, group all under "Technical Skills"
        categorized_skills = {}
        for skill_name, level in skills.items():
            if '.' in skill_name:
                category, name = skill_name.split('.', 1)
            else:
                category = "Habilidades Técnicas"
                name = skill_name
            
            if category not in categorized_skills:
                categorized_skills[category] = []
            
            categorized_skills[category].append({
                "name": name,
                "level": level
            })
        
        # Format for visualization
        radar_data = {
            "name": person_name,
            "categories": []
        }
        
        for category, skills_list in categorized_skills.items():
            radar_data["categories"].append({
                "name": category,
                "skills": skills_list
            })
        
        return radar_data
    
    def _generate_career_report(self, person_name: str, career_data: Dict[str, Any]) -> str:
        """Generate a report based on career progression data"""
        try:
            # Extract career data components
            eventos = career_data.get("eventos_carreira", [])
            habilidades = career_data.get("matriz_habilidades", {})
            metas = career_data.get("metas_carreira", [])
            certificacoes = career_data.get("certificacoes", [])
            mentorias = career_data.get("mentoria", [])
            metricas = career_data.get("metricas", {})
            
            # Initialize metrics that will be used throughout the report
            avg_skill = 0
            leadership = 0
            collab = 0
            
            if metricas:
                avg_skill = metricas.get("media_habilidades", 0)
                leadership = metricas.get("potencial_lideranca", 0)
                collab = metricas.get("crescimento_colaborativo", 0)
            
            # Generate report
            report = f"""# Relatório de Progressão de Carreira: {person_name}
Data de geração: {datetime.now().strftime('%d/%m/%Y')}

## Sumário Executivo

"""
            # Sumário executivo
            if metricas and "growth_score" in metricas:
                growth_score = metricas.get("growth_score", 0)
                high_performer_index = metricas.get("high_performer_index", 0)
                
                # Determine growth level based on score
                if growth_score >= 90:
                    growth_level = "Excepcional"
                elif growth_score >= 75:
                    growth_level = "Acelerado"
                elif growth_score >= 60:
                    growth_level = "Bom"
                elif growth_score >= 40:
                    growth_level = "Moderado"
                else:
                    growth_level = "Necessita Atenção"
                
                # Determine high performer status
                if high_performer_index >= 90:
                    performer_status = "High performer de elite"
                elif high_performer_index >= 75:
                    performer_status = "High performer"
                elif high_performer_index >= 60:
                    performer_status = "Performer sólido"
                elif high_performer_index >= 40:
                    performer_status = "Performer em desenvolvimento"
                else:
                    performer_status = "Necessita desenvolvimento significativo"
                
                report += f"""**Score de Crescimento**: {growth_score:.1f}/100 - Nível de Crescimento: {growth_level}
**High Performer Index**: {high_performer_index:.1f}/100 - Status: {performer_status}

"""
            
            # Team contribution section
            report += """
## Contribuição para Equipe de Alta Performance

"""
            # Leadership potential
            if metricas and "potencial_lideranca" in metricas:
                leadership_score = metricas.get("potencial_lideranca", 0)
                
                if leadership_score >= 8:
                    leadership_message = "Demonstra forte potencial de liderança. Pode ser considerado para papéis formais de liderança ou mentoria."
                elif leadership_score >= 5:
                    leadership_message = "Bom potencial de liderança. Recomenda-se oferecer oportunidades para desenvolver essas habilidades."
                else:
                    leadership_message = "Potencial de liderança em desenvolvimento. Pode se beneficiar de treinamentos formais e mentoria."
                
                report += f"**Potencial de Liderança**: {leadership_score:.1f}/10 - {leadership_message}\n\n"
            
            # Collaborative growth
            if metricas and "crescimento_colaborativo" in metricas:
                collab_score = metricas.get("crescimento_colaborativo", 0)
                
                if collab_score >= 8:
                    collab_message = "Excelente contribuidor para o crescimento da equipe. Compartilha conhecimento e apoia outros membros."
                elif collab_score >= 5:
                    collab_message = "Bom colaborador. Participa ativamente de iniciativas de equipe."
                else:
                    collab_message = "Oportunidade para aumentar colaboração. Pode se beneficiar de mais envolvimento em atividades de equipe."
                
                report += f"**Crescimento Colaborativo**: {collab_score:.1f}/10 - {collab_message}\n\n"
            
            # Skill diversity
            if metricas and "diversidade_habilidades" in metricas:
                skill_diversity = metricas.get("diversidade_habilidades", 0)
                
                if skill_diversity >= 4:
                    diversity_message = "Perfil multidisciplinar com habilidades em diversas áreas. Valioso para equipes cross-funcionais."
                elif skill_diversity >= 2:
                    diversity_message = "Bom equilíbrio de habilidades em algumas áreas. Continuar expandindo para outras áreas."
                else:
                    diversity_message = "Especialização em área específica. Oportunidade para desenvolver habilidades complementares."
                
                report += f"**Diversidade de Habilidades**: {skill_diversity} áreas de competência - {diversity_message}\n\n"
            
            # Team-fit recommendations
            report += """
### Recomendações para Desenvolvimento em Equipe de Alta Performance

"""
            # Generate custom recommendations based on metrics
            recommendations = []
            
            if metricas:
                # Leadership development
                if metricas.get("potencial_lideranca", 0) >= 7:
                    recommendations.append("**Desenvolver liderança formal**: Oferecer oportunidades de liderar projetos ou equipes pequenas para desenvolver habilidades de liderança.")
                elif metricas.get("potencial_lideranca", 0) >= 4:
                    recommendations.append("**Desenvolver liderança técnica**: Incentivar mentoria de colegas menos experientes e liderança em áreas de especialidade.")
                else:
                    recommendations.append("**Fortalecer fundamentos**: Focar em desenvolver domínio técnico e habilidades de comunicação antes de papéis de liderança.")
                
                # Skill development
                if metricas.get("diversidade_habilidades", 0) <= 2:
                    recommendations.append("**Expandir repertório de habilidades**: Identificar áreas complementares para desenvolvimento que aumentem versatilidade na equipe.")
                
                # Collaboration development
                if metricas.get("crescimento_colaborativo", 0) <= 5:
                    recommendations.append("**Aumentar colaboração**: Incentivar participação em comunidades de prática, projetos cross-funcionais e compartilhamento de conhecimento.")
                
                # Team role alignment
                if avg_skill >= 4 and leadership >= 7:
                    recommendations.append("**Papel potencial na equipe**: Tech Lead ou Especialista Técnico Senior - pessoa pode servir como referência técnica e orientar direções tecnológicas.")
                elif avg_skill >= 3.5 and collab >= 7:
                    recommendations.append("**Papel potencial na equipe**: Integrador ou Facilitador - pessoa pode ajudar a conectar diferentes áreas e promover colaboração.")
                elif avg_skill >= 4 and collab <= 5:
                    recommendations.append("**Papel potencial na equipe**: Especialista Técnico - pessoa pode se aprofundar em áreas específicas e servir como referência.")
                elif metricas.get("taxa_aquisicao_habilidades", 0) >= 3:
                    recommendations.append("**Papel potencial na equipe**: Inovador ou Early Adopter - pessoa pode liderar adoção de novas tecnologias e abordagens.")
            
            # Add recommendations to report
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    report += f"{i}. {rec}\n"
            else:
                report += "Dados insuficientes para gerar recomendações personalizadas para equipe de alta performance.\n"
            
            # Add career goals section
            report += """
## Metas de Carreira

| Meta | Data Alvo | Progresso | Status | Detalhes |
|------|-----------|-----------|--------|----------|
"""
            
            if metas:
                # Sort goals by target date
                for meta in sorted(metas, key=lambda x: x.get('target_date', '')):
                    titulo = meta.get('title', '')
                    data_alvo = meta.get('target_date', '').replace('-', '/')
                    progresso = meta.get('progress', 0)
                    
                    # Convert status to Portuguese
                    status_en = meta.get('status', '')
                    status = {
                        'not_started': 'Não Iniciado',
                        'in_progress': 'Em Andamento',
                        'completed': 'Concluído',
                        'delayed': 'Atrasado'
                    }.get(status_en, status_en)
                    
                    detalhes = meta.get('details', '')
                    
                    report += f"| {titulo} | {data_alvo} | {progresso}% | {status} | {detalhes} |\n"
            else:
                report += "| - | - | - | - | Nenhuma meta de carreira registrada |\n"
            
            # Add certifications section
            report += """
## Certificações

| Nome | Emissor | Data de Obtenção | Data de Expiração |
|------|---------|------------------|-------------------|
"""
            
            if certificacoes:
                # Sort certifications by date obtained
                for cert in sorted(certificacoes, key=lambda x: x.get('date_obtained', ''), reverse=True):
                    nome = cert.get('name', '')
                    emissor = cert.get('issuer', '')
                    data_obtencao = cert.get('date_obtained', '').replace('-', '/')
                    data_expiracao = cert.get('expiry_date', '').replace('-', '/') if cert.get('expiry_date') else 'N/A'
                    
                    report += f"| {nome} | {emissor} | {data_obtencao} | {data_expiracao} |\n"
            else:
                report += "| - | - | - | - |\n"
            
            # Add mentorship section
            report += """
## Relações de Mentoria

| Mentor | Início | Fim | Áreas de Foco | Status |
|--------|--------|-----|---------------|--------|
"""
            
            if mentorias:
                # Sort mentorships by start date
                for mentor in sorted(mentorias, key=lambda x: x.get('start_date', ''), reverse=True):
                    nome_mentor = mentor.get('mentor_name', '')
                    data_inicio = mentor.get('start_date', '').replace('-', '/')
                    data_fim = mentor.get('end_date', '').replace('-', '/') if mentor.get('end_date') else 'Ativo'
                    areas_foco = ', '.join(mentor.get('focus_areas', []))
                    status = 'Ativo' if mentor.get('active', False) else 'Encerrado'
                    
                    report += f"| {nome_mentor} | {data_inicio} | {data_fim} | {areas_foco} | {status} |\n"
            else:
                report += "| - | - | - | - | - |\n"
            
            # Add recommendations section
            report += """
## Recomendações

"""
            
            # Add some tailored recommendations based on the data
            if avg_skill < 3.0:
                report += "- **Desenvolvimento de Habilidades:** Foco no desenvolvimento das habilidades existentes para elevar o nível médio de proficiência.\n"
            
            if not certificacoes:
                report += "- **Certificações:** Buscar certificações relevantes para a função atual ou desejada.\n"
            
            if leadership and leadership > 7.0:
                report += "- **Desenvolvimento de Liderança:** A liderança do colaborador está acima da média. Recomenda-se oferecer oportunidades para desenvolver essas habilidades.\n"
            
            active_mentorships = [m for m in mentorias if m.get('active', False)]
            if not active_mentorships:
                report += "- **Mentoria:** Buscar um mentor para acelerar o desenvolvimento profissional.\n"
            
            completed_goals = len([m for m in metas if m.get('status') == 'completed'])
            if completed_goals < 2:
                report += "- **Metas de Carreira:** Definir e concluir mais metas de carreira para demonstrar progresso.\n"
            
            report += """
## Observações Finais

Este relatório representa uma análise automática dos dados de progressão de carreira. As recomendações são baseadas nas informações disponíveis e nas melhores práticas de desenvolvimento profissional.
"""
            
            return report
            
        except Exception as e:
            print(f"Error creating career report: {e}")
            return f"Error creating career report: {e}"
    
    def _create_comprehensive_report(self, person_name: str, individual_report: Path, manager_report: Path, career_report: Optional[Path] = None) -> str:
        """Cria um relatório abrangente combinando feedback 360, do gestor e progressão de carreira"""
        try:
            # Lê relatório individual
            with open(individual_report, 'r') as f:
                individual_content = f.read()
                
            # Lê relatório do gestor
            with open(manager_report, 'r') as f:
                manager_content = f.read()
            
            # Lê relatório de carreira, se disponível
            career_content = None
            if career_report and career_report.exists():
                with open(career_report, 'r') as f:
                    career_content = f.read()
            
            # Extrai dados chave
            indiv_score = self._extract_performance_score(individual_content)
            manager_score = self._extract_manager_score(manager_content)
            
            # Extrai pontos fortes e áreas de desenvolvimento
            indiv_strengths = self._extract_section(individual_content, "Analysis", end_marker="Generated on")
            manager_strengths = self._extract_section(manager_content, "Pontos Fortes", end_marker="Áreas de Desenvolvimento")
            manager_dev_areas = self._extract_section(manager_content, "Áreas de Desenvolvimento", end_marker="Áreas de Foco")
            
            hoje = datetime.now().strftime('%d/%m/%Y')
            
            # Cria relatório combinado
            report = f"""# Relatório Abrangente de Desempenho: {person_name}

## Data do Relatório: {hoje}

---

# PARTE 1: AVALIAÇÃO 360

{individual_content}

---

# PARTE 2: AVALIAÇÃO DO GESTOR

{manager_content}

"""
            
            # Adiciona seção de progressão de carreira, se disponível
            if career_content:
                report += f"""
---

# PARTE 3: PROGRESSÃO DE CARREIRA

{career_content}

"""
            
            # Adiciona seção de análise combinada
            combined_rating = self._calculate_combined_rating(indiv_score, manager_score)
            
            report += f"""
---

# ANÁLISE COMBINADA

## Pontuação Geral

A pontuação combinada, considerando a avaliação 360 e a avaliação do gestor, é **{combined_rating}**.

## Alinhamento entre Avaliações

"""
            
            # Analisa alinhamento entre avaliações
            if indiv_score and manager_score:
                diff = abs(float(indiv_score) - float(manager_score))
                if diff <= 0.5:
                    report += "Há um **alto alinhamento** entre a autopercepção/avaliação dos pares e a avaliação do gestor. Isso indica uma boa calibragem nas avaliações e autoconsciência do colaborador.\n\n"
                elif diff <= 1.0:
                    report += "Há um **alinhamento moderado** entre a autopercepção/avaliação dos pares e a avaliação do gestor. Algumas diferenças de percepção existem e podem ser exploradas em conversas de feedback.\n\n"
                else:
                    report += "Há uma **diferença significativa** entre a autopercepção/avaliação dos pares e a avaliação do gestor. Esta discrepância merece atenção e deve ser explorada em conversas de alinhamento.\n\n"
            
            # Adiciona análise de progressão de carreira, se disponível
            if career_content:
                promotion_velocity = self._extract_context(career_content, "Velocidade média de promoção")
                avg_skill_level = self._extract_context(career_content, "Nível médio de habilidades")
                
                report += "## Análise de Progressão de Carreira\n\n"
                
                if promotion_velocity:
                    report += f"{promotion_velocity}\n\n"
                
                if avg_skill_level:
                    report += f"{avg_skill_level}\n\n"
                
                report += "A progressão de carreira do colaborador deve ser analisada em conjunto com seu desempenho atual, buscando identificar oportunidades de desenvolvimento alinhadas com suas aspirações profissionais e as necessidades da organização.\n\n"
            
            report += """
## Resumo dos Pontos Fortes

"""
            if indiv_strengths:
                report += indiv_strengths + "\n\n"
            
            if manager_strengths:
                report += manager_strengths + "\n\n"
                
            report += """
## Resumo das Áreas de Desenvolvimento

"""
            if manager_dev_areas:
                report += manager_dev_areas + "\n\n"
                
            # Adiciona conclusões e próximos passos
            report += """
## Conclusões e Próximos Passos

1. **Acompanhamento Regular**: Estabelecer check-ins periódicos para monitorar o progresso nas áreas de desenvolvimento identificadas.
2. **Plano de Desenvolvimento**: Criar um plano de desenvolvimento personalizado com base nas áreas de melhoria identificadas.
3. **Reconhecimento**: Reconhecer e valorizar os pontos fortes demonstrados.
4. **Alinhamento de Expectativas**: Garantir que haja clareza sobre as expectativas de desempenho para o próximo ciclo.
5. **Oportunidades de Desenvolvimento**: Identificar projetos, treinamentos ou mentores que possam acelerar o desenvolvimento nas áreas necessárias.

---

_Este relatório foi gerado automaticamente combinando múltiplas fontes de dados. As análises e recomendações devem ser validadas pelo gestor responsável._
"""
            
            return report
            
        except Exception as e:
            print(f"Error creating comprehensive report: {e}")
            return f"Error creating comprehensive report: {e}"
    
    def _extract_manager_score(self, content: str) -> Optional[str]:
        """Extract manager's overall performance rating"""
        score_pattern = r"\*\*Overall Performance:\*\* (\d+)\/5"
        import re
        match = re.search(score_pattern, content)
        if match:
            return match.group(1)
        return None
        
    def _extract_performance_score(self, content: str) -> Optional[str]:
        """Extract performance score from individual report"""
        score_pattern = r"- Score: (\d+\.?\d*)"
        import re
        match = re.search(score_pattern, content)
        if match:
            return match.group(1)
        return None
        
    def _calculate_combined_rating(self, indiv_score: Optional[str], manager_score: Optional[str]) -> str:
        """Calculate a combined rating from individual and manager scores"""
        try:
            if indiv_score and manager_score:
                indiv_val = float(indiv_score)
                manager_val = float(manager_score)
                # Weight manager score slightly higher (60/40)
                combined = (indiv_val * 0.4) + (manager_val * 0.6)
                return f"{combined:.1f}/5"
            elif indiv_score:
                return f"{indiv_score}/5"
            elif manager_score:
                return f"{manager_score}/5"
            else:
                return "Not available"
        except Exception:
            return "Unable to calculate"
            
    def _extract_section(self, content: str, section_name: str, end_marker: str = None) -> str:
        """Extract a section from the content between section name and end marker"""
        start_idx = content.find(f"## {section_name}")
        if start_idx == -1:
            return ""
            
        if end_marker:
            end_idx = content.find(end_marker, start_idx)
            if end_idx == -1:
                end_idx = content.find("##", start_idx + 3)
        else:
            end_idx = content.find("##", start_idx + 3)
            
        if end_idx == -1:
            return content[start_idx:]
        else:
            return content[start_idx:end_idx]
            
    def _extract_context(self, content: str, keyword: str, context_size: int = 100) -> Optional[str]:
        """Extract context around a keyword"""
        keyword_idx = content.find(keyword)
        if keyword_idx == -1:
            return None
            
        # Find the start of the sentence
        start_idx = max(0, content.rfind('.', max(0, keyword_idx - context_size), keyword_idx) + 1)
        if start_idx == 1:  # No period found
            start_idx = max(0, keyword_idx - context_size)
            
        # Find the end of the sentence
        end_idx = content.find('.', keyword_idx)
        if end_idx == -1:
            end_idx = min(len(content), keyword_idx + context_size)
        else:
            end_idx += 1
            
        context = content[start_idx:end_idx].strip()
        
        # Clean up the context (remove markdown formatting)
        import re
        context = re.sub(r'\*\*|\*|##+|>', '', context)
        context = re.sub(r'\n+', ' ', context)
        context = re.sub(r'\s+', ' ', context)
        
        return context.capitalize()
    
    def _create_pdi(self, person_name: str, individual_report: Path, manager_report: Path, career_report: Optional[Path] = None) -> str:
        """Criar Plano de Desenvolvimento Individual (PDI) baseado nos relatórios"""
        try:
            # Lê relatório individual
            with open(individual_report, 'r') as f:
                individual_content = f.read()
                
            # Lê relatório do gestor
            with open(manager_report, 'r') as f:
                manager_content = f.read()
                
            # Lê relatório de carreira, se disponível
            career_content = None
            if career_report and career_report.exists():
                with open(career_report, 'r') as f:
                    career_content = f.read()
            
            # Extrai áreas de desenvolvimento do relatório do gestor
            dev_areas = self._extract_section(manager_content, "Áreas de Desenvolvimento", end_marker="Áreas de Foco")
            
            # Extrai objetivos de carreira do relatório de carreira, se disponível
            career_goals = None
            if career_content:
                career_goals = self._extract_section(career_content, "## Metas de Carreira", end_marker="## Certificações")
            
            hoje = datetime.now().strftime('%d/%m/%Y')
            proximo_trimestre = (datetime.now() + timedelta(days=90)).strftime('%d/%m/%Y')
            
            # Cria PDI
            pdi = f"""# Plano de Desenvolvimento Individual (PDI)

## Colaborador: {person_name}
## Data de Criação: {hoje}
## Período de Referência: {hoje} a {proximo_trimestre}

---

## Objetivos do PDI

Este Plano de Desenvolvimento Individual (PDI) tem como objetivo estruturar ações de desenvolvimento profissional alinhadas com:

1. As áreas de desenvolvimento identificadas nas avaliações
2. Os objetivos de carreira do colaborador
3. As necessidades estratégicas da equipe e da organização

---

## Áreas Prioritárias de Desenvolvimento

"""
            
            if dev_areas:
                pdi += dev_areas + "\n\n"
            else:
                pdi += "_Não foram identificadas áreas específicas de desenvolvimento nas avaliações._\n\n"
            
            # Adiciona seção de objetivos de carreira, se disponível
            if career_goals:
                pdi += "## Objetivos de Carreira\n\n"
                pdi += career_goals + "\n\n"
            
            # Adiciona plano de ação
            pdi += """
## Plano de Ação

| Área de Desenvolvimento | Ação | Recursos Necessários | Prazo | Métrica de Sucesso | Status |
|-------------------------|------|----------------------|-------|-------------------|--------|
| | | | | | |
| | | | | | |
| | | | | | |

---

## Recursos e Suportes

- **Treinamentos Recomendados**: 
- **Mentoria**: 
- **Materiais de Estudo**: 
- **Projetos Sugeridos**: 

---

## Acompanhamento do Progresso

| Data | Progresso | Observações | Próximos Passos |
|------|-----------|-------------|-----------------|
| | | | |
| | | | |

---

## Compromisso

Este PDI representa um compromisso compartilhado entre o colaborador e seu gestor para impulsionar o desenvolvimento profissional alinhado com os objetivos organizacionais e aspirações de carreira.

**Colaborador**: ______________________________ Data: __________

**Gestor**: __________________________________ Data: __________

---

_Este PDI foi gerado automaticamente com base nas avaliações de desempenho e deve ser personalizado em uma conversa entre gestor e colaborador._
"""
            
            return pdi
            
        except Exception as e:
            print(f"Error creating PDI: {e}")
            return f"Error creating PDI: {e}"
    
    def _process_manual_templates(self) -> List[str]:
        """Process manually filled templates."""
        results = []
        
        # Create directories if they don't exist
        templates_dir = self.data_path / "templates"
        career_dir = self.data_path / "career_progression"
        
        if not templates_dir.exists():
            templates_dir.mkdir(parents=True, exist_ok=True)
            results.append("Created templates directory")
        
        if not career_dir.exists():
            career_dir.mkdir(parents=True, exist_ok=True)
            results.append("Created career progression directory")
        
        # Process any JSON templates in the templates directory
        template_files = list(templates_dir.glob("*.json"))
        
        if not template_files:
            results.append("No manual templates found for processing")
            return results
        
        for template_file in template_files:
            try:
                # Determine template type based on content
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if it's a career progression template
                if "eventos_carreira" in data or "matriz_habilidades" in data:
                    # Process career progression template
                    person_name = data.get("nome", template_file.stem)
                    output_file = career_dir / f"{person_name}.json"
                    
                    # Make sure nome is included
                    if "nome" not in data:
                        data["nome"] = person_name
                    
                    # Save to career progression directory
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    # Calculate metrics and update file
                    self._add_metrics_to_career_data(output_file)
                    
                    results.append(f"Processed career template for {person_name}")
                    
                    # Create backup of the original template
                    backup_dir = templates_dir / "processed"
                    backup_dir.mkdir(exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_file = backup_dir / f"{template_file.stem}_{timestamp}.json"
                    shutil.copy(template_file, backup_file)
                    
                    # Remove the original template
                    template_file.unlink()
                    results.append(f"Archived template {template_file.name}")
                else:
                    results.append(f"Skipped {template_file.name}: Unknown template format")
            
            except Exception as e:
                results.append(f"Error processing template {template_file.name}: {str(e)}")
        
        return results
    
    def _add_metrics_to_career_data(self, career_file: Path) -> None:
        """Calculate and add metrics to career progression data."""
        try:
            # Load data
            with open(career_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract components
            eventos = data.get("eventos_carreira", [])
            habilidades = data.get("matriz_habilidades", {})
            certificacoes = data.get("certificacoes", [])
            metas = data.get("metas_carreira", [])
            mentoria = data.get("mentoria", [])
            
            # Calculate metrics
            from peopleanalytics.data_pipeline import DataPipeline
            pipeline = DataPipeline(self.data_path, self.output_path)
            metricas = pipeline._calculate_career_metrics(
                eventos, habilidades, certificacoes, metas, mentoria
            )
            
            # Add metrics to data
            data["metricas"] = metricas
            
            # Save updated data
            with open(career_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Error adding metrics to {career_file.name}: {e}")