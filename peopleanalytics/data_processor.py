"""
Data processor for People Analytics.

This module provides functionality for processing people evaluation data,
focusing on importing and validating resultado.json files.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any
import pandas as pd

class DataProcessor:
    """Process and validate people evaluation data."""
    
    def __init__(self, data_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None):
        """Initialize the data processor.
        
        Args:
            data_path: Path to the data directory
            output_path: Path to the output directory (defaults to 'output' in current dir)
        """
        self.data_path = Path(data_path).resolve()
        self.output_path = Path(output_path).resolve() if output_path else Path("output").resolve()
        
        # Ensure output directory exists
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Set up logging for the data processor."""
        log_path = self.output_path / "logs"
        log_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_path / f"data_processor_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("DataProcessor")
        self.logger.info(f"DataProcessor initialized with data_path={self.data_path}, output_path={self.output_path}")

    def import_directory(self, directory: Union[str, Path], recursive: bool = True) -> Dict[str, Any]:
        """Import all resultado.json files from a directory.
        
        Args:
            directory: Directory to import from
            recursive: Whether to search recursively
            
        Returns:
            Dict with import statistics
        """
        directory = Path(directory)
        
        if not directory.exists() or not directory.is_dir():
            return {"success": False, "error": f"Directory not found: {directory}"}
            
        # Find all resultado.json files
        if recursive:
            files = list(directory.glob("**/resultado.json"))
        else:
            files = list(directory.glob("*/resultado.json"))
            
        if not files:
            self.logger.info(f"No files found in {directory}")
            return {"success": True, "imported": 0, "message": "No files found"}
            
        # Process each file
        results = {
            "success": True,
            "total": len(files),
            "imported": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }
        
        for file_path in files:
            try:
                # Skip empty files
                if file_path.stat().st_size == 0:
                    self.logger.warning(f"Skipping empty file: {file_path}")
                    results["skipped"] += 1
                    continue
                
                # Extract person and year from path
                parts = file_path.parts
                if len(parts) < 3:
                    raise ValueError(f"Invalid file path structure: {file_path}")
                    
                person = parts[-3]
                year = parts[-2]
                
                # Check if perfil.json exists and is not empty
                perfil_path = file_path.parent / "perfil.json"
                if not perfil_path.exists() or perfil_path.stat().st_size == 0:
                    self.logger.warning(f"Skipping {file_path} - perfil.json missing or empty")
                    results["skipped"] += 1
                    continue
                
                # Load and validate the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Validate schema
                if not self._validate_schema(data):
                    raise ValueError(f"Invalid data structure in {file_path}")
                
                results["imported"] += 1
                
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"file": str(file_path), "error": str(e)})
                
        return results

    def _validate_schema(self, data: Dict) -> bool:
        """Validate the data against the required schema.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check basic structure
            if not isinstance(data, dict):
                return False
                
            # Check success fields
            if 'success' not in data or 'status_code' not in data or 'data' not in data:
                return False
                
            # Check data structure
            if not isinstance(data['data'], dict):
                return False
                
            # Check required fields in data
            if 'conceito_ciclo_filho_descricao' not in data['data'] or 'direcionadores' not in data['data']:
                return False
                
            # Validate direcionadores
            for direcionador in data['data']['direcionadores']:
                if not isinstance(direcionador, dict):
                    return False
                    
                # Check required fields in direcionador
                if 'direcionador' not in direcionador or 'pergunta_final' not in direcionador or 'comportamentos' not in direcionador:
                    return False
                    
                # Validate comportamentos
                for comportamento in direcionador['comportamentos']:
                    if not isinstance(comportamento, dict):
                        return False
                        
                    # Check required fields in comportamento
                    if 'comportamento' not in comportamento or 'pergunta_final' not in comportamento or 'avaliacoes_grupo' not in comportamento:
                        return False
                        
                    # Validate avaliacoes_grupo
                    for avaliacao in comportamento['avaliacoes_grupo']:
                        if not isinstance(avaliacao, dict):
                            return False
                            
                        # Check required fields in avaliacao
                        if 'avaliador' not in avaliacao or 'frequencia_colaborador' not in avaliacao or 'frequencia_grupo' not in avaliacao:
                            return False
                            
                        # Check frequencia arrays
                        if not isinstance(avaliacao['frequencia_colaborador'], list) or not isinstance(avaliacao['frequencia_grupo'], list):
                            return False
                            
            return True
            
        except Exception:
            return False

    def generate_report(self) -> str:
        """Generate a report of all evaluation data.
        
        Returns:
            Path to the generated report file
        """
        # Find all resultado.json files
        files = list(self.data_path.glob("**/resultado.json"))
        
        if not files:
            self.logger.warning("No files found to generate report")
            return None
            
        # Collect all data
        all_data = []
        
        for file_path in files:
            try:
                # Skip empty files
                if file_path.stat().st_size == 0:
                    continue
                    
                # Extract person and year from path
                parts = file_path.parts
                person = parts[-3]
                year = parts[-2]
                
                # Load the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load profile
                perfil_path = file_path.parent / "perfil.json"
                with open(perfil_path, 'r', encoding='utf-8') as f:
                    perfil = json.load(f)
                
                # Process data
                for direcionador in data['data']['direcionadores']:
                    for comportamento in direcionador['comportamentos']:
                        for avaliacao in comportamento['avaliacoes_grupo']:
                            row = {
                                "pessoa": person,
                                "ano": year,
                                "cargo": perfil['cargo'],
                                "nivel": perfil['nivel_cargo'],
                                "conceito": data['data']['conceito_ciclo_filho_descricao'],
                                "direcionador": direcionador['direcionador'],
                                "comportamento": comportamento['comportamento'],
                                "avaliador": avaliacao['avaliador'],
                                "frequencia_colaborador": sum(i * v for i, v in enumerate(avaliacao['frequencia_colaborador'])) / sum(avaliacao['frequencia_colaborador']),
                                "frequencia_grupo": sum(i * v for i, v in enumerate(avaliacao['frequencia_grupo'])) / sum(avaliacao['frequencia_grupo'])
                            }
                            all_data.append(row)
                            
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                continue
        
        if not all_data:
            self.logger.warning("No valid data found to generate report")
            return None
            
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save to Excel
        report_dir = self.output_path / "reports"
        report_dir.mkdir(exist_ok=True)
        report_file = report_dir / f"report_{timestamp}.xlsx"
        
        with pd.ExcelWriter(report_file) as writer:
            # Overall summary
            summary = df.groupby(['pessoa', 'ano', 'cargo', 'nivel', 'conceito']).agg({
                'frequencia_colaborador': 'mean',
                'frequencia_grupo': 'mean'
            }).reset_index()
            summary.to_excel(writer, sheet_name='Resumo', index=False)
            
            # Detailed data
            df.to_excel(writer, sheet_name='Detalhado', index=False)
            
            # By direction
            for direcionador in df['direcionador'].unique():
                direcionador_df = df[df['direcionador'] == direcionador]
                direcionador_df.to_excel(writer, sheet_name=direcionador[:31], index=False)
        
        self.logger.info(f"Report generated: {report_file}")
        return str(report_file)

    def generate_summary(self, format: str = "html") -> str:
        """Generate a summary of all evaluation data.
        
        Args:
            format: Output format (html or markdown)
            
        Returns:
            Path to the generated summary file
        """
        # Find all resultado.json files
        files = list(self.data_path.glob("**/resultado.json"))
        
        if not files:
            self.logger.warning("No files found to generate summary")
            return None
            
        # Collect all data
        all_data = []
        
        for file_path in files:
            try:
                # Skip empty files
                if file_path.stat().st_size == 0:
                    continue
                    
                # Extract person and year from path
                parts = file_path.parts
                person = parts[-3]
                year = parts[-2]
                
                # Load the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load profile
                perfil_path = file_path.parent / "perfil.json"
                with open(perfil_path, 'r', encoding='utf-8') as f:
                    perfil = json.load(f)
                
                # Process data
                for direcionador in data['data']['direcionadores']:
                    for comportamento in direcionador['comportamentos']:
                        for avaliacao in comportamento['avaliacoes_grupo']:
                            row = {
                                "pessoa": person,
                                "ano": year,
                                "cargo": perfil['cargo'],
                                "nivel": perfil['nivel_cargo'],
                                "conceito": data['data']['conceito_ciclo_filho_descricao'],
                                "direcionador": direcionador['direcionador'],
                                "comportamento": comportamento['comportamento'],
                                "avaliador": avaliacao['avaliador'],
                                "frequencia_colaborador": sum(i * v for i, v in enumerate(avaliacao['frequencia_colaborador'])) / sum(avaliacao['frequencia_colaborador']),
                                "frequencia_grupo": sum(i * v for i, v in enumerate(avaliacao['frequencia_grupo'])) / sum(avaliacao['frequencia_grupo'])
                            }
                            all_data.append(row)
                            
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                continue
        
        if not all_data:
            self.logger.warning("No valid data found to generate summary")
            return None
            
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory
        output_dir = self.output_path / "summary"
        output_dir.mkdir(exist_ok=True)
        
        if format == "html":
            # Load template
            template_path = Path(__file__).parent / "templates" / "summary.html"
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
                
            # Generate HTML content
            content = []
            for person in df['pessoa'].unique():
                person_data = df[df['pessoa'] == person]
                content.append(f"<h2>{person}</h2>")
                
                for year in person_data['ano'].unique():
                    year_data = person_data[person_data['ano'] == year]
                    content.append(f"<h3>{year}</h3>")
                    
                    # Add summary table
                    content.append("<table>")
                    content.append("<tr><th>Direcionador</th><th>Comportamento</th><th>Média</th></tr>")
                    
                    for direcionador in year_data['direcionador'].unique():
                        direcionador_data = year_data[year_data['direcionador'] == direcionador]
                        for comportamento in direcionador_data['comportamento'].unique():
                            comportamento_data = direcionador_data[direcionador_data['comportamento'] == comportamento]
                            media = comportamento_data['frequencia_colaborador'].mean()
                            content.append(f"<tr><td>{direcionador}</td><td>{comportamento}</td><td>{media:.2f}</td></tr>")
                            
                    content.append("</table>")
                    
            # Save HTML file
            output_file = output_dir / f"summary_{timestamp}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(template.replace("{{content}}", "\n".join(content)))
                
        elif format == "markdown":
            # Generate markdown content
            content = []
            for person in df['pessoa'].unique():
                person_data = df[df['pessoa'] == person]
                content.append(f"# {person}")
                
                for year in person_data['ano'].unique():
                    year_data = person_data[person_data['ano'] == year]
                    content.append(f"## {year}")
                    
                    # Add summary table
                    content.append("| Direcionador | Comportamento | Média |")
                    content.append("|--------------|---------------|-------|")
                    
                    for direcionador in year_data['direcionador'].unique():
                        direcionador_data = year_data[year_data['direcionador'] == direcionador]
                        for comportamento in direcionador_data['comportamento'].unique():
                            comportamento_data = direcionador_data[direcionador_data['comportamento'] == comportamento]
                            media = comportamento_data['frequencia_colaborador'].mean()
                            content.append(f"| {direcionador} | {comportamento} | {media:.2f} |")
                            
                    content.append("")
                    
            # Save markdown file
            output_file = output_dir / f"summary_{timestamp}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
                
        else:
            self.logger.error(f"Unsupported format: {format}")
            return None
            
        self.logger.info(f"Summary generated: {output_file}")
        return str(output_file)

    def generate_mermaid_chart(self) -> str:
        """Generate a MermaidJS chart visualization of evaluation data.
        
        Returns:
            Path to the generated mermaid file
        """
        # Find all resultado.json files
        files = list(self.data_path.glob("**/resultado.json"))
        
        if not files:
            self.logger.warning("No files found to generate mermaid chart")
            return None
            
        # Collect all data
        all_data = []
        
        for file_path in files:
            try:
                # Skip empty files
                if file_path.stat().st_size == 0:
                    continue
                    
                # Extract person and year from path
                parts = file_path.parts
                person = parts[-3]
                year = parts[-2]
                
                # Load the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load profile
                perfil_path = file_path.parent / "perfil.json"
                with open(perfil_path, 'r', encoding='utf-8') as f:
                    perfil = json.load(f)
                
                # Process data
                for direcionador in data['data']['direcionadores']:
                    for comportamento in direcionador['comportamentos']:
                        for avaliacao in comportamento['avaliacoes_grupo']:
                            row = {
                                "pessoa": person,
                                "ano": year,
                                "cargo": perfil['cargo'],
                                "nivel": perfil['nivel_cargo'],
                                "conceito": data['data']['conceito_ciclo_filho_descricao'],
                                "direcionador": direcionador['direcionador'],
                                "comportamento": comportamento['comportamento'],
                                "avaliador": avaliacao['avaliador'],
                                "frequencia_colaborador": sum(i * v for i, v in enumerate(avaliacao['frequencia_colaborador'])) / sum(avaliacao['frequencia_colaborador']),
                                "frequencia_grupo": sum(i * v for i, v in enumerate(avaliacao['frequencia_grupo'])) / sum(avaliacao['frequencia_grupo'])
                            }
                            all_data.append(row)
                            
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                continue
        
        if not all_data:
            self.logger.warning("No valid data found to generate mermaid chart")
            return None
            
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory
        output_dir = self.output_path / "mermaid"
        output_dir.mkdir(exist_ok=True)
        
        # Generate mermaid content per person
        mermaid_files = {}
        
        for person in df['pessoa'].unique():
            person_data = df[df['pessoa'] == person]
            
            content = []
            content.append(f"# Performance Visualization for {person}")
            content.append("")
            
            # Add bar chart for competencies
            content.append("## Performance by Competency Area")
            content.append("")
            content.append("```mermaid")
            content.append("%%{init: {'theme':'forest'}}%%")
            content.append("barchart")
            content.append(f"    title Performance Scores for {person}")
            content.append("    x-axis [Competency Areas]")
            content.append("    y-axis [Score (0-4)]")
            
            for direcionador in person_data['direcionador'].unique():
                direcionador_data = person_data[person_data['direcionador'] == direcionador]
                avg_score = direcionador_data['frequencia_colaborador'].mean()
                content.append(f"    \"{direcionador}\" {avg_score:.2f}")
                
            content.append("```")
            content.append("")
            
            # Add pie chart for overall assessment
            content.append("## Overall Assessment Distribution")
            content.append("")
            content.append("```mermaid")
            content.append("%%{init: {'theme':'forest'}}%%")
            content.append("pie")
            content.append(f"    title Assessment Distribution for {person}")
            
            conceitos = person_data.groupby('conceito').size()
            for conceito, count in conceitos.items():
                content.append(f"    \"{conceito}\" : {count}")
                
            content.append("```")
            content.append("")
            
            # Add comparison chart between person and group
            content.append("## Individual vs. Group Performance")
            content.append("")
            content.append("```mermaid")
            content.append("%%{init: {'theme':'forest'}}%%")
            content.append("barchart")
            content.append(f"    title Individual vs. Group Performance for {person}")
            content.append("    x-axis [Competency Areas]")
            content.append("    y-axis [Score Difference]")
            
            for direcionador in person_data['direcionador'].unique():
                direcionador_data = person_data[person_data['direcionador'] == direcionador]
                avg_indiv = direcionador_data['frequencia_colaborador'].mean()
                avg_group = direcionador_data['frequencia_grupo'].mean()
                diff = avg_indiv - avg_group
                content.append(f"    \"{direcionador}\" {diff:.2f}")
                
            content.append("```")
            
            # Save mermaid file
            output_file = output_dir / f"mermaid_{person.replace(' ', '_')}_{timestamp}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
                
            mermaid_files[person] = str(output_file)
            self.logger.info(f"Mermaid chart generated for {person}: {output_file}")
            
        return mermaid_files
        
    def generate_ai_prompt(self) -> str:
        """Generate AI prompts for feedback reports.
        
        Returns:
            Dictionary mapping person names to prompt file paths
        """
        # Find all resultado.json files
        files = list(self.data_path.glob("**/resultado.json"))
        
        if not files:
            self.logger.warning("No files found to generate AI prompts")
            return None
            
        # Collect all data by person
        person_data = {}
        
        for file_path in files:
            try:
                # Skip empty files
                if file_path.stat().st_size == 0:
                    continue
                    
                # Extract person and year from path
                parts = file_path.parts
                person = parts[-3]
                year = parts[-2]
                
                if person not in person_data:
                    person_data[person] = []
                
                # Load the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load profile
                perfil_path = file_path.parent / "perfil.json"
                with open(perfil_path, 'r', encoding='utf-8') as f:
                    perfil = json.load(f)
                
                # Add year data
                year_data = {
                    "year": year,
                    "job_title": perfil['cargo'],
                    "job_level": perfil['nivel_cargo'],
                    "overall_assessment": data['data']['conceito_ciclo_filho_descricao'],
                    "competencies": []
                }
                
                # Process competencies
                for direcionador in data['data']['direcionadores']:
                    competency = {
                        "name": direcionador['direcionador'],
                        "final_question": direcionador['pergunta_final'],
                        "behaviors": []
                    }
                    
                    for comportamento in direcionador['comportamentos']:
                        behavior = {
                            "name": comportamento['comportamento'],
                            "final_question": comportamento['pergunta_final'],
                            "evaluations": []
                        }
                        
                        for avaliacao in comportamento['avaliacoes_grupo']:
                            evaluation = {
                                "evaluator": avaliacao['avaliador'],
                                "individual_freq": avaliacao['frequencia_colaborador'],
                                "group_freq": avaliacao['frequencia_grupo'],
                                "individual_score": sum(i * v for i, v in enumerate(avaliacao['frequencia_colaborador'])) / sum(avaliacao['frequencia_colaborador']),
                                "group_score": sum(i * v for i, v in enumerate(avaliacao['frequencia_grupo'])) / sum(avaliacao['frequencia_grupo'])
                            }
                            behavior["evaluations"].append(evaluation)
                            
                        competency["behaviors"].append(behavior)
                        
                    year_data["competencies"].append(competency)
                    
                person_data[person].append(year_data)
                            
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                continue
        
        if not person_data:
            self.logger.warning("No valid data found to generate AI prompts")
            return None
            
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory
        output_dir = self.output_path / "ai_prompts"
        output_dir.mkdir(exist_ok=True)
        
        # Generate prompts for each person
        prompt_files = {}
        
        for person, years_data in person_data.items():
            content = []
            content.append(f"# AI Feedback Generation Prompt for {person}")
            content.append("")
            content.append("## Instructions")
            content.append("You are an expert HR consultant specializing in performance evaluations and feedback. Your task is to write a comprehensive feedback report for the employee based on the data provided below. The report should:")
            content.append("")
            content.append("1. Start with a personalized introduction that mentions the employee's name, job title, and overall assessment")
            content.append("2. Include a summary of strengths and development areas")
            content.append("3. Provide detailed feedback for each competency area, highlighting specific behaviors")
            content.append("4. Compare individual performance with group averages when relevant")
            content.append("5. Suggest specific development actions for improvement")
            content.append("6. End with a forward-looking conclusion that is encouraging and motivational")
            content.append("")
            content.append("Please maintain a balanced, constructive, and professional tone throughout the feedback.")
            content.append("")
            content.append("## Employee Information")
            content.append("")
            
            # Sort years data by year
            years_data.sort(key=lambda x: x["year"])
            
            # Get latest job info
            latest_year = years_data[-1]
            
            content.append(f"- **Name**: {person}")
            content.append(f"- **Current Job Title**: {latest_year['job_title']}")
            content.append(f"- **Current Level**: {latest_year['job_level']}")
            content.append(f"- **Years of Evaluation Data**: {', '.join(y['year'] for y in years_data)}")
            content.append(f"- **Most Recent Overall Assessment**: {latest_year['overall_assessment']}")
            content.append("")
            
            # Add detailed evaluation data for each year
            content.append("## Detailed Evaluation Data")
            content.append("")
            
            for year_data in years_data:
                content.append(f"### Year: {year_data['year']}")
                content.append(f"- **Job Title**: {year_data['job_title']}")
                content.append(f"- **Job Level**: {year_data['job_level']}")
                content.append(f"- **Overall Assessment**: {year_data['overall_assessment']}")
                content.append("")
                
                content.append("#### Competency Areas")
                content.append("")
                
                for comp in year_data['competencies']:
                    content.append(f"##### {comp['name']}")
                    content.append(f"- **Assessment Question**: {comp['final_question']}")
                    content.append("")
                    
                    for behavior in comp['behaviors']:
                        content.append(f"###### Behavior: {behavior['name']}")
                        content.append(f"- **Behavior Question**: {behavior['final_question']}")
                        content.append("")
                        
                        for eval in behavior['evaluations']:
                            content.append(f"- **Evaluator**: {eval['evaluator']}")
                            content.append(f"- **Individual Score**: {eval['individual_score']:.2f}/4.0")
                            content.append(f"- **Group Score**: {eval['group_score']:.2f}/4.0")
                            content.append(f"- **Score Difference**: {(eval['individual_score'] - eval['group_score']):.2f}")
                            content.append("")
                    
                    content.append("")
                
                content.append("---")
                content.append("")
            
            # Prompt closing
            content.append("## Request")
            content.append("Based on the above data, please write a comprehensive performance feedback report for this employee that is detailed, balanced, and actionable.")
            
            # Save prompt file
            output_file = output_dir / f"ai_prompt_{person.replace(' ', '_')}_{timestamp}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
                
            prompt_files[person] = str(output_file)
            self.logger.info(f"AI prompt generated for {person}: {output_file}")
            
        return prompt_files

    def generate_stakeholder_comparison(self) -> dict:
        """Generate a comparative analysis between different stakeholder evaluations.
        
        This compares evaluations from managers, peers/partners, and self-evaluations
        against the peer group averages.
        
        Returns:
            Dictionary mapping person names to report file paths
        """
        # Find all resultado.json files
        files = list(self.data_path.glob("**/resultado.json"))
        
        if not files:
            self.logger.warning("No files found to generate stakeholder comparison")
            return None
            
        # Collect all data by person
        all_data = []
        
        for file_path in files:
            try:
                # Skip empty files
                if file_path.stat().st_size == 0:
                    continue
                    
                # Extract person and year from path
                parts = file_path.parts
                person = parts[-3]
                year = parts[-2]
                
                # Load the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load profile
                perfil_path = file_path.parent / "perfil.json"
                with open(perfil_path, 'r', encoding='utf-8') as f:
                    perfil = json.load(f)
                
                # Process data
                for direcionador in data['data']['direcionadores']:
                    for comportamento in direcionador['comportamentos']:
                        for avaliacao in comportamento['avaliacoes_grupo']:
                            # Determine the stakeholder type - assuming 'avaliador' field contains this info
                            stakeholder = avaliacao['avaliador'].lower()
                            if 'gestor' in stakeholder or 'manager' in stakeholder:
                                stakeholder_type = 'manager'
                            elif 'auto' in stakeholder or 'self' in stakeholder:
                                stakeholder_type = 'self'
                            else:
                                stakeholder_type = 'peer'
                                
                            row = {
                                "pessoa": person,
                                "ano": year,
                                "cargo": perfil['cargo'],
                                "nivel": perfil['nivel_cargo'],
                                "conceito": data['data']['conceito_ciclo_filho_descricao'],
                                "direcionador": direcionador['direcionador'],
                                "comportamento": comportamento['comportamento'],
                                "avaliador": avaliacao['avaliador'],
                                "stakeholder_type": stakeholder_type,
                                "frequencia_colaborador": sum(i * v for i, v in enumerate(avaliacao['frequencia_colaborador'])) / sum(avaliacao['frequencia_colaborador']),
                                "frequencia_grupo": sum(i * v for i, v in enumerate(avaliacao['frequencia_grupo'])) / sum(avaliacao['frequencia_grupo'])
                            }
                            all_data.append(row)
                            
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                continue
        
        if not all_data:
            self.logger.warning("No valid data found to generate stakeholder comparison")
            return None
            
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory
        output_dir = self.output_path / "stakeholder_analysis"
        output_dir.mkdir(exist_ok=True)
        
        # Generate analysis for each person
        report_files = {}
        
        for person in df['pessoa'].unique():
            person_data = df[df['pessoa'] == person]
            
            content = []
            content.append(f"# Stakeholder Comparison Analysis for {person}")
            content.append("")
            content.append("## Overview")
            content.append("")
            content.append("This analysis compares evaluations from different stakeholders (manager, peers/partners, and self) against the peer group averages.")
            content.append("")
            
            # Get latest year data
            latest_year = max(person_data['ano'].unique())
            latest_data = person_data[person_data['ano'] == latest_year]
            
            # Summary by stakeholder type
            content.append("## Summary by Stakeholder Type")
            content.append("")
            
            summary_table = []
            summary_table.append("| Stakeholder | Average Score | Peer Group Average | Difference |")
            summary_table.append("|------------|--------------|-------------------|-----------|")
            
            stakeholder_avgs = latest_data.groupby('stakeholder_type')['frequencia_colaborador'].mean()
            group_avgs = latest_data.groupby('stakeholder_type')['frequencia_grupo'].mean()
            
            for stakeholder in ['manager', 'peer', 'self']:
                if stakeholder in stakeholder_avgs:
                    avg_score = stakeholder_avgs[stakeholder]
                    group_avg = group_avgs[stakeholder]
                    diff = avg_score - group_avg
                    diff_str = f"+{diff:.2f}" if diff > 0 else f"{diff:.2f}"
                    summary_table.append(f"| {stakeholder.capitalize()} | {avg_score:.2f} | {group_avg:.2f} | {diff_str} |")
            
            content.extend(summary_table)
            content.append("")
            
            # Overall average
            overall_avg = latest_data['frequencia_colaborador'].mean()
            group_overall_avg = latest_data['frequencia_grupo'].mean()
            overall_diff = overall_avg - group_overall_avg
            overall_diff_str = f"+{overall_diff:.2f}" if overall_diff > 0 else f"{overall_diff:.2f}"
            
            content.append(f"**Overall Average:** {overall_avg:.2f} (Peer Group: {group_overall_avg:.2f}, Difference: {overall_diff_str})")
            content.append("")
            
            # Analysis by competency area
            content.append("## Analysis by Competency Area")
            content.append("")
            
            for direcionador in latest_data['direcionador'].unique():
                content.append(f"### {direcionador}")
                content.append("")
                
                dir_data = latest_data[latest_data['direcionador'] == direcionador]
                
                # Competency table
                comp_table = []
                comp_table.append("| Stakeholder | Behavior | Score | Peer Group | Diff |")
                comp_table.append("|------------|----------|-------|------------|------|")
                
                for comportamento in dir_data['comportamento'].unique():
                    comp_data = dir_data[dir_data['comportamento'] == comportamento]
                    
                    for stakeholder in ['manager', 'peer', 'self']:
                        stakeholder_data = comp_data[comp_data['stakeholder_type'] == stakeholder]
                        if not stakeholder_data.empty:
                            score = stakeholder_data['frequencia_colaborador'].mean()
                            group_score = stakeholder_data['frequencia_grupo'].mean()
                            diff = score - group_score
                            diff_str = f"+{diff:.2f}" if diff > 0 else f"{diff:.2f}"
                            comp_table.append(f"| {stakeholder.capitalize()} | {comportamento} | {score:.2f} | {group_score:.2f} | {diff_str} |")
                
                content.extend(comp_table)
                content.append("")
                
            # Performance map (description of high/low areas)
            content.append("## Performance Map")
            content.append("")
            
            # High performance areas
            high_perf = latest_data.groupby(['direcionador', 'comportamento'])['frequencia_colaborador'].mean()
            high_perf = high_perf.sort_values(ascending=False).head(3)
            
            content.append("### Strongest Areas")
            content.append("")
            content.append("| Competency | Behavior | Score |")
            content.append("|------------|----------|-------|")
            
            for (dir_name, comp_name), score in high_perf.items():
                content.append(f"| {dir_name} | {comp_name} | {score:.2f} |")
            
            content.append("")
            
            # Low performance areas
            low_perf = latest_data.groupby(['direcionador', 'comportamento'])['frequencia_colaborador'].mean()
            low_perf = low_perf.sort_values().head(3)
            
            content.append("### Development Areas")
            content.append("")
            content.append("| Competency | Behavior | Score |")
            content.append("|------------|----------|-------|")
            
            for (dir_name, comp_name), score in low_perf.items():
                content.append(f"| {dir_name} | {comp_name} | {score:.2f} |")
            
            content.append("")
            
            # Stakeholder perspective gaps
            content.append("## Stakeholder Perspective Gaps")
            content.append("")
            content.append("Areas with the largest differences between stakeholder perspectives:")
            content.append("")
            
            # Prepare data for gap analysis
            gap_data = []
            
            for direcionador in latest_data['direcionador'].unique():
                for comportamento in latest_data[latest_data['direcionador'] == direcionador]['comportamento'].unique():
                    comp_data = latest_data[(latest_data['direcionador'] == direcionador) & 
                                           (latest_data['comportamento'] == comportamento)]
                    
                    stakeholder_scores = comp_data.groupby('stakeholder_type')['frequencia_colaborador'].mean()
                    if len(stakeholder_scores) > 1:  # Need at least 2 stakeholders to compare
                        max_score = stakeholder_scores.max()
                        min_score = stakeholder_scores.min()
                        gap = max_score - min_score
                        max_stakeholder = stakeholder_scores.idxmax().capitalize()
                        min_stakeholder = stakeholder_scores.idxmin().capitalize()
                        
                        gap_data.append({
                            'direcionador': direcionador,
                            'comportamento': comportamento,
                            'gap': gap,
                            'max_stakeholder': max_stakeholder,
                            'min_stakeholder': min_stakeholder,
                            'max_score': max_score,
                            'min_score': min_score
                        })
            
            if gap_data:
                # Sort by gap size
                gap_data.sort(key=lambda x: x['gap'], reverse=True)
                
                # Table of largest gaps
                content.append("| Competency | Behavior | Gap Size | Highest Rating | Lowest Rating |")
                content.append("|------------|----------|----------|---------------|---------------|")
                
                for item in gap_data[:5]:  # Top 5 gaps
                    content.append(f"| {item['direcionador']} | {item['comportamento']} | {item['gap']:.2f} | " +
                                  f"{item['max_stakeholder']} ({item['max_score']:.2f}) | " +
                                  f"{item['min_stakeholder']} ({item['min_score']:.2f}) |")
                
                content.append("")
            else:
                content.append("Not enough data from different stakeholders to analyze perspective gaps.")
                content.append("")
            
            # Save analysis file
            output_file = output_dir / f"stakeholder_analysis_{person.replace(' ', '_')}_{timestamp}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
                
            report_files[person] = str(output_file)
            self.logger.info(f"Stakeholder comparison report generated for {person}: {output_file}")
            
        return report_files

    def generate_time_series_analysis(self) -> dict:
        """Generate time series analysis of performance over multiple years.
        
        Returns:
            Dictionary mapping person names to report file paths
        """
        # Find all resultado.json files
        files = list(self.data_path.glob("**/resultado.json"))
        
        if not files:
            self.logger.warning("No files found to generate time series analysis")
            return None
            
        # Collect all data by person and year
        all_data = []
        
        for file_path in files:
            try:
                # Skip empty files
                if file_path.stat().st_size == 0:
                    continue
                    
                # Extract person and year from path
                parts = file_path.parts
                person = parts[-3]
                year = parts[-2]
                
                # Load the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load profile
                perfil_path = file_path.parent / "perfil.json"
                with open(perfil_path, 'r', encoding='utf-8') as f:
                    perfil = json.load(f)
                
                # Process data
                for direcionador in data['data']['direcionadores']:
                    for comportamento in direcionador['comportamentos']:
                        for avaliacao in comportamento['avaliacoes_grupo']:
                            row = {
                                "pessoa": person,
                                "ano": year,
                                "cargo": perfil['cargo'],
                                "nivel": perfil['nivel_cargo'],
                                "conceito": data['data']['conceito_ciclo_filho_descricao'],
                                "direcionador": direcionador['direcionador'],
                                "comportamento": comportamento['comportamento'],
                                "avaliador": avaliacao['avaliador'],
                                "frequencia_colaborador": sum(i * v for i, v in enumerate(avaliacao['frequencia_colaborador'])) / sum(avaliacao['frequencia_colaborador']),
                                "frequencia_grupo": sum(i * v for i, v in enumerate(avaliacao['frequencia_grupo'])) / sum(avaliacao['frequencia_grupo'])
                            }
                            all_data.append(row)
                            
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                continue
        
        if not all_data:
            self.logger.warning("No valid data found to generate time series analysis")
            return None
            
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory
        output_dir = self.output_path / "time_series"
        output_dir.mkdir(exist_ok=True)
        
        # Generate analysis for each person
        report_files = {}
        
        for person in df['pessoa'].unique():
            person_data = df[df['pessoa'] == person]
            years = person_data['ano'].unique()
            
            # Skip if there's only one year of data
            if len(years) < 2:
                self.logger.info(f"Skipping time series for {person}: not enough years of data")
                continue
                
            content = []
            content.append(f"# Performance Time Series Analysis for {person}")
            content.append("")
            content.append("## Overview")
            content.append("")
            content.append(f"This analysis tracks performance trends for {person} over {len(years)} years ({min(years)} - {max(years)}).")
            content.append("")
            
            # Overall performance trend
            content.append("## Overall Performance Trend")
            content.append("")
            
            # MermaidJS line chart for overall trends
            content.append("```mermaid")
            content.append("%%{init: {'theme':'forest'}}%%")
            content.append("xychart-beta")
            content.append(f"    title \"Overall Performance Score by Year for {person}\"")
            content.append("    x-axis [Year]")
            content.append("    y-axis \"Score (0-4)\" [0 - 4]")
            
            # Sort years
            years = sorted(years)
            
            # Plot overall scores by year
            content.append("    line [Overall Score]")
            for year in years:
                year_data = person_data[person_data['ano'] == year]
                avg_score = year_data['frequencia_colaborador'].mean()
                content.append(f"      {year} {avg_score:.2f}")
                
            # Plot peer group scores by year for comparison
            content.append("    line [Peer Group Average]")
            for year in years:
                year_data = person_data[person_data['ano'] == year]
                avg_score = year_data['frequencia_grupo'].mean()
                content.append(f"      {year} {avg_score:.2f}")
                
            content.append("```")
            content.append("")
            
            # Competency area trends
            content.append("## Competency Area Trends")
            content.append("")
            
            # Get all unique competency areas
            direcionadores = person_data['direcionador'].unique()
            
            for direcionador in direcionadores:
                dir_data = person_data[person_data['direcionador'] == direcionador]
                
                # Skip if not present in multiple years
                if len(dir_data['ano'].unique()) < 2:
                    continue
                    
                content.append(f"### {direcionador}")
                content.append("")
                
                # MermaidJS line chart for competency area
                content.append("```mermaid")
                content.append("%%{init: {'theme':'forest'}}%%")
                content.append("xychart-beta")
                content.append(f"    title \"{direcionador} Performance Over Time\"")
                content.append("    x-axis [Year]")
                content.append("    y-axis \"Score (0-4)\" [0 - 4]")
                
                # Plot competency scores by year
                content.append("    line [Score]")
                for year in years:
                    if year in dir_data['ano'].values:
                        year_dir_data = dir_data[dir_data['ano'] == year]
                        avg_score = year_dir_data['frequencia_colaborador'].mean()
                        content.append(f"      {year} {avg_score:.2f}")
                    
                # Plot peer group scores by year for comparison
                content.append("    line [Peer Group]")
                for year in years:
                    if year in dir_data['ano'].values:
                        year_dir_data = dir_data[dir_data['ano'] == year]
                        avg_score = year_dir_data['frequencia_grupo'].mean()
                        content.append(f"      {year} {avg_score:.2f}")
                    
                content.append("```")
                content.append("")
                
            # Year-over-year comparison table
            content.append("## Year-over-Year Comparison")
            content.append("")
            content.append("| Competency | " + " | ".join(years) + " | Trend |")
            content.append("|" + "-" * 12 + "|" + "".join(["-" * 8 + "|" for _ in years]) + "-" * 8 + "|")
            
            for direcionador in direcionadores:
                dir_data = person_data[person_data['direcionador'] == direcionador]
                
                scores = []
                for year in years:
                    if year in dir_data['ano'].values:
                        year_dir_data = dir_data[dir_data['ano'] == year]
                        avg_score = year_dir_data['frequencia_colaborador'].mean()
                        scores.append(avg_score)
                    else:
                        scores.append(None)
                
                # Calculate trend
                valid_scores = [s for s in scores if s is not None]
                if len(valid_scores) >= 2:
                    first_valid = valid_scores[0]
                    last_valid = valid_scores[-1]
                    diff = last_valid - first_valid
                    if diff > 0.2:
                        trend = "🔼 Improving"
                    elif diff < -0.2:
                        trend = "🔽 Declining"
                    else:
                        trend = "➡️ Stable"
                else:
                    trend = "N/A"
                
                # Format scores for the table
                score_cells = []
                for score in scores:
                    if score is not None:
                        score_cells.append(f"{score:.2f}")
                    else:
                        score_cells.append("N/A")
                
                content.append(f"| {direcionador} | " + " | ".join(score_cells) + f" | {trend} |")
            
            content.append("")
            
            # Key insights
            content.append("## Key Insights")
            content.append("")
            
            # Calculate year-over-year changes
            insights = []
            
            # Most improved areas
            improved_areas = []
            
            for direcionador in direcionadores:
                dir_data = person_data[person_data['direcionador'] == direcionador]
                if len(dir_data['ano'].unique()) >= 2:
                    first_year = min(dir_data['ano'].unique())
                    last_year = max(dir_data['ano'].unique())
                    
                    first_score = dir_data[dir_data['ano'] == first_year]['frequencia_colaborador'].mean()
                    last_score = dir_data[dir_data['ano'] == last_year]['frequencia_colaborador'].mean()
                    
                    change = last_score - first_score
                    improved_areas.append((direcionador, change, first_score, last_score))
            
            # Sort by largest improvement
            improved_areas.sort(key=lambda x: x[1], reverse=True)
            
            # Add top improvements
            if improved_areas:
                content.append("### Most Improved Areas")
                content.append("")
                for area, change, first, last in improved_areas[:3]:
                    if change > 0:
                        content.append(f"- **{area}**: {first:.2f} → {last:.2f} (+{change:.2f})")
                content.append("")
                
                # Add areas needing attention
                content.append("### Areas Needing Attention")
                content.append("")
                for area, change, first, last in improved_areas[-3:]:
                    if change < 0:
                        content.append(f"- **{area}**: {first:.2f} → {last:.2f} ({change:.2f})")
                content.append("")
            
            # Overall trend summary
            all_years_data = []
            for year in years:
                year_data = person_data[person_data['ano'] == year]
                avg_score = year_data['frequencia_colaborador'].mean()
                all_years_data.append((year, avg_score))
            
            all_years_data.sort()
            if len(all_years_data) >= 2:
                first_year, first_score = all_years_data[0]
                last_year, last_score = all_years_data[-1]
                total_change = last_score - first_score
                
                if total_change > 0.2:
                    content.append(f"Overall, {person}'s performance has **improved** from {first_score:.2f} in {first_year} to {last_score:.2f} in {last_year} (+{total_change:.2f}).")
                elif total_change < -0.2:
                    content.append(f"Overall, {person}'s performance has **declined** from {first_score:.2f} in {first_year} to {last_score:.2f} in {last_year} ({total_change:.2f}).")
                else:
                    content.append(f"Overall, {person}'s performance has remained **stable** from {first_score:.2f} in {first_year} to {last_score:.2f} in {last_year} ({total_change:.2f}).")
            
            # Save analysis file
            output_file = output_dir / f"time_series_{person.replace(' ', '_')}_{timestamp}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
                
            report_files[person] = str(output_file)
            self.logger.info(f"Time series analysis generated for {person}: {output_file}")
            
        return report_files
        
    def generate_radar_chart(self) -> dict:
        """Generate radar chart visualization of competencies.
        
        Returns:
            Dictionary mapping person names to report file paths
        """
        # Find all resultado.json files
        files = list(self.data_path.glob("**/resultado.json"))
        
        if not files:
            self.logger.warning("No files found to generate radar chart")
            return None
            
        # Collect all data by person
        all_data = []
        
        for file_path in files:
            try:
                # Skip empty files
                if file_path.stat().st_size == 0:
                    continue
                    
                # Extract person and year from path
                parts = file_path.parts
                person = parts[-3]
                year = parts[-2]
                
                # Load the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load profile
                perfil_path = file_path.parent / "perfil.json"
                with open(perfil_path, 'r', encoding='utf-8') as f:
                    perfil = json.load(f)
                
                # Process data
                for direcionador in data['data']['direcionadores']:
                    for comportamento in direcionador['comportamentos']:
                        for avaliacao in comportamento['avaliacoes_grupo']:
                            # Determine the stakeholder type
                            stakeholder = avaliacao['avaliador'].lower()
                            if 'gestor' in stakeholder or 'manager' in stakeholder:
                                stakeholder_type = 'manager'
                            elif 'auto' in stakeholder or 'self' in stakeholder:
                                stakeholder_type = 'self'
                            else:
                                stakeholder_type = 'peer'
                                
                            row = {
                                "pessoa": person,
                                "ano": year,
                                "cargo": perfil['cargo'],
                                "nivel": perfil['nivel_cargo'],
                                "conceito": data['data']['conceito_ciclo_filho_descricao'],
                                "direcionador": direcionador['direcionador'],
                                "comportamento": comportamento['comportamento'],
                                "avaliador": avaliacao['avaliador'],
                                "stakeholder_type": stakeholder_type,
                                "frequencia_colaborador": sum(i * v for i, v in enumerate(avaliacao['frequencia_colaborador'])) / sum(avaliacao['frequencia_colaborador']),
                                "frequencia_grupo": sum(i * v for i, v in enumerate(avaliacao['frequencia_grupo'])) / sum(avaliacao['frequencia_grupo'])
                            }
                            all_data.append(row)
                            
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                continue
        
        if not all_data:
            self.logger.warning("No valid data found to generate radar chart")
            return None
            
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory
        output_dir = self.output_path / "radar_charts"
        output_dir.mkdir(exist_ok=True)
        
        # Generate radar chart for each person
        report_files = {}
        
        for person in df['pessoa'].unique():
            person_data = df[df['pessoa'] == person]
            
            # Get latest year
            latest_year = max(person_data['ano'].unique())
            latest_data = person_data[person_data['ano'] == latest_year]
            
            content = []
            content.append(f"# Competency Radar Chart for {person}")
            content.append("")
            content.append("## Overview")
            content.append("")
            content.append(f"This radar chart visualization shows {person}'s competency scores from different perspectives.")
            content.append("The chart displays scores on a scale of 0-4 across all competency areas.")
            content.append("")
            
            # Create chart data by competency area
            competency_data = latest_data.groupby('direcionador')['frequencia_colaborador'].mean().reset_index()
            competency_data = competency_data.sort_values('direcionador')
            
            # Create chart data by stakeholder type
            stakeholder_data = {}
            for stakeholder in ['manager', 'peer', 'self']:
                stakeholder_latest = latest_data[latest_data['stakeholder_type'] == stakeholder]
                if not stakeholder_latest.empty:
                    temp_data = stakeholder_latest.groupby('direcionador')['frequencia_colaborador'].mean().reset_index()
                    temp_data = temp_data.sort_values('direcionador')
                    stakeholder_data[stakeholder] = temp_data
            
            # Create radar chart diagram using HTML
            content.append("## Competency Radar Chart")
            content.append("")
            content.append("<div style=\"background-color: white; padding: 20px; border-radius: 5px;\">")
            content.append("<script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>")
            content.append("<script src=\"https://cdn.jsdelivr.net/npm/chartjs-chart-radar\"></script>")
            content.append("<canvas id=\"radar-chart\" width=\"800\" height=\"600\"></canvas>")
            content.append("<script>")
            content.append("var ctx = document.getElementById('radar-chart').getContext('2d');")
            content.append("var myRadarChart = new Chart(ctx, {")
            content.append("    type: 'radar',")
            content.append("    data: {")
            content.append("        labels: ['" + "', '".join(competency_data['direcionador']) + "'],")
            content.append("        datasets: [")
            
            colors = {
                'overall': {'border': 'rgb(54, 162, 235)', 'background': 'rgba(54, 162, 235, 0.2)'},
                'manager': {'border': 'rgb(255, 99, 132)', 'background': 'rgba(255, 99, 132, 0.2)'},
                'peer': {'border': 'rgb(75, 192, 192)', 'background': 'rgba(75, 192, 192, 0.2)'},
                'self': {'border': 'rgb(255, 159, 64)', 'background': 'rgba(255, 159, 64, 0.2)'},
                'peer_group': {'border': 'rgb(153, 102, 255)', 'background': 'rgba(153, 102, 255, 0.2)'}
            }
            
            # Add overall scores
            content.append("            {")
            content.append("                label: 'Overall',")
            content.append("                data: [" + ", ".join([f"{x:.2f}" for x in competency_data['frequencia_colaborador']]) + "],")
            content.append(f"                borderColor: '{colors['overall']['border']}',")
            content.append(f"                backgroundColor: '{colors['overall']['background']}',")
            content.append("                borderWidth: 2")
            content.append("            },")
            
            # Add stakeholder perspective scores
            for stakeholder, data in stakeholder_data.items():
                content.append("            {")
                content.append(f"                label: '{stakeholder.capitalize()}',")
                content.append("                data: [" + ", ".join([f"{x:.2f}" for x in data['frequencia_colaborador']]) + "],")
                content.append(f"                borderColor: '{colors[stakeholder]['border']}',")
                content.append(f"                backgroundColor: '{colors[stakeholder]['background']}',")
                content.append("                borderWidth: 2")
                content.append("            },")
            
            # Add peer group scores
            peer_group_data = latest_data.groupby('direcionador')['frequencia_grupo'].mean().reset_index()
            peer_group_data = peer_group_data.sort_values('direcionador')
            
            content.append("            {")
            content.append("                label: 'Peer Group',")
            content.append("                data: [" + ", ".join([f"{x:.2f}" for x in peer_group_data['frequencia_grupo']]) + "],")
            content.append(f"                borderColor: '{colors['peer_group']['border']}',")
            content.append(f"                backgroundColor: '{colors['peer_group']['background']}',")
            content.append("                borderWidth: 2,")
            content.append("                borderDash: [5, 5]")
            content.append("            }")
            
            content.append("        ]")
            content.append("    },")
            content.append("    options: {")
            content.append("        responsive: true,")
            content.append("        maintainAspectRatio: false,")
            content.append("        scales: {")
            content.append("            r: {")
            content.append("                angleLines: {")
            content.append("                    display: true")
            content.append("                },")
            content.append("                suggestedMin: 0,")
            content.append("                suggestedMax: 4")
            content.append("            }")
            content.append("        }")
            content.append("    }")
            content.append("});")
            content.append("</script>")
            content.append("</div>")
            content.append("")
            content.append("> **Note**: The radar chart requires a browser with JavaScript enabled to view. If you're viewing this in a markdown viewer without JavaScript support, please open in a web browser.")
            content.append("")
            
            # Add alternative text representation
            content.append("## Competency Scores (Text Version)")
            content.append("")
            content.append("| Competency | Overall | Peer Group | Gap |")
            content.append("|------------|---------|------------|-----|")
            
            for i, row in competency_data.iterrows():
                direcionador = row['direcionador']
                overall = row['frequencia_colaborador']
                peer_group = peer_group_data[peer_group_data['direcionador'] == direcionador]['frequencia_grupo'].values[0]
                gap = overall - peer_group
                gap_text = f"+{gap:.2f}" if gap > 0 else f"{gap:.2f}"
                
                content.append(f"| {direcionador} | {overall:.2f} | {peer_group:.2f} | {gap_text} |")
            
            content.append("")
            
            # Add stakeholder perspective table
            if stakeholder_data:
                content.append("## Stakeholder Perspective Comparison")
                content.append("")
                
                # Header
                header = ["Competency"]
                for stakeholder in stakeholder_data.keys():
                    header.append(stakeholder.capitalize())
                header.append("Peer Group")
                
                content.append("| " + " | ".join(header) + " |")
                content.append("|" + "|".join(["-" * 12] * len(header)) + "|")
                
                # Data rows
                for direcionador in competency_data['direcionador']:
                    row = [direcionador]
                    
                    for stakeholder in stakeholder_data.keys():
                        if direcionador in stakeholder_data[stakeholder]['direcionador'].values:
                            score = stakeholder_data[stakeholder][stakeholder_data[stakeholder]['direcionador'] == direcionador]['frequencia_colaborador'].values[0]
                            row.append(f"{score:.2f}")
                        else:
                            row.append("N/A")
                    
                    peer_group_score = peer_group_data[peer_group_data['direcionador'] == direcionador]['frequencia_grupo'].values[0]
                    row.append(f"{peer_group_score:.2f}")
                    
                    content.append("| " + " | ".join(row) + " |")
                
                content.append("")
            
            # Save analysis file
            output_file = output_dir / f"radar_chart_{person.replace(' ', '_')}_{timestamp}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
                
            report_files[person] = str(output_file)
            self.logger.info(f"Radar chart generated for {person}: {output_file}")
            
        return report_files

    def generate_team_aggregation(self) -> str:
        """Generate a team/department aggregation report.
        
        Returns:
            Path to the generated report file
        """
        # Find all resultado.json files
        files = list(self.data_path.glob("**/resultado.json"))
        
        if not files:
            self.logger.warning("No files found to generate team aggregation")
            return None
            
        # Collect all data
        all_data = []
        
        for file_path in files:
            try:
                # Skip empty files
                if file_path.stat().st_size == 0:
                    continue
                    
                # Extract person and year from path
                parts = file_path.parts
                person = parts[-3]
                year = parts[-2]
                
                # Load the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load profile
                perfil_path = file_path.parent / "perfil.json"
                with open(perfil_path, 'r', encoding='utf-8') as f:
                    perfil = json.load(f)
                
                # Extract team/department info (assuming it's in the profile)
                department = "Unknown"
                if "department" in perfil:
                    department = perfil["department"]
                
                # Process data
                for direcionador in data['data']['direcionadores']:
                    for comportamento in direcionador['comportamentos']:
                        for avaliacao in comportamento['avaliacoes_grupo']:
                            row = {
                                "pessoa": person,
                                "ano": year,
                                "cargo": perfil['cargo'],
                                "nivel": perfil['nivel_cargo'],
                                "department": department,
                                "conceito": data['data']['conceito_ciclo_filho_descricao'],
                                "direcionador": direcionador['direcionador'],
                                "comportamento": comportamento['comportamento'],
                                "avaliador": avaliacao['avaliador'],
                                "frequencia_colaborador": sum(i * v for i, v in enumerate(avaliacao['frequencia_colaborador'])) / sum(avaliacao['frequencia_colaborador']),
                                "frequencia_grupo": sum(i * v for i, v in enumerate(avaliacao['frequencia_grupo'])) / sum(avaliacao['frequencia_grupo'])
                            }
                            all_data.append(row)
                            
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                continue
        
        if not all_data:
            self.logger.warning("No valid data found to generate team aggregation")
            return None
            
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory
        output_dir = self.output_path / "team_reports"
        output_dir.mkdir(exist_ok=True)
        
        # Generate report
        content = []
        content.append("# Team and Department Performance Analysis")
        content.append("")
        content.append("## Overview")
        content.append("")
        content.append("This report provides an aggregated view of performance across teams/departments.")
        content.append("It highlights collective strengths and development areas to enable targeted interventions.")
        content.append("")
        
        # Get latest year for analysis
        latest_year = max(df['ano'].unique())
        latest_data = df[df['ano'] == latest_year]
        
        # Department-level analysis
        content.append("## Department Performance Summary")
        content.append("")
        
        # Department performance table
        dept_avg = latest_data.groupby('department')['frequencia_colaborador'].agg(['mean', 'count']).reset_index()
        dept_avg = dept_avg.sort_values('mean', ascending=False)
        
        content.append("| Department | Average Score | Number of Evaluations |")
        content.append("|------------|---------------|------------------------|")
        
        for _, row in dept_avg.iterrows():
            content.append(f"| {row['department']} | {row['mean']:.2f} | {int(row['count'])} |")
            
        content.append("")
        
        # Department performance visualization
        content.append("### Department Performance Comparison")
        content.append("")
        content.append("```mermaid")
        content.append("%%{init: {'theme':'forest'}}%%")
        content.append("barchart")
        content.append("    title Department Performance Comparison")
        content.append("    x-axis [Departments]")
        content.append("    y-axis [Average Score (0-4)]")
        
        for _, row in dept_avg.iterrows():
            content.append(f"    \"{row['department']}\" {row['mean']:.2f}")
            
        content.append("```")
        content.append("")
        
        # Competency analysis by department
        content.append("## Competency Analysis by Department")
        content.append("")
        
        # Get top departments
        top_departments = dept_avg.head(5)['department'].tolist()
        
        for department in top_departments:
            dept_data = latest_data[latest_data['department'] == department]
            
            content.append(f"### {department}")
            content.append("")
            
            # Department competency barchart
            content.append("```mermaid")
            content.append("%%{init: {'theme':'forest'}}%%")
            content.append("barchart")
            content.append(f"    title Competency Scores for {department}")
            content.append("    x-axis [Competency Areas]")
            content.append("    y-axis [Score (0-4)]")
            
            # Aggregate by competency
            comp_avg = dept_data.groupby('direcionador')['frequencia_colaborador'].mean().reset_index()
            comp_avg = comp_avg.sort_values('frequencia_colaborador', ascending=False)
            
            for _, row in comp_avg.iterrows():
                content.append(f"    \"{row['direcionador']}\" {row['frequencia_colaborador']:.2f}")
                
            content.append("```")
            content.append("")
            
            # Competency table
            content.append("| Competency | Score | Rank |")
            content.append("|------------|-------|------|")
            
            for i, (_, row) in enumerate(comp_avg.iterrows()):
                content.append(f"| {row['direcionador']} | {row['frequencia_colaborador']:.2f} | {i+1} |")
                
            content.append("")
            
            # Team strengths and improvements
            strengths = comp_avg.head(2)
            improvements = comp_avg.tail(2)
            
            content.append("#### Team Strengths")
            content.append("")
            for _, row in strengths.iterrows():
                content.append(f"- **{row['direcionador']}**: {row['frequencia_colaborador']:.2f}")
            content.append("")
            
            content.append("#### Development Opportunities")
            content.append("")
            for _, row in improvements.iterrows():
                content.append(f"- **{row['direcionador']}**: {row['frequencia_colaborador']:.2f}")
            content.append("")
        
        # Cross-department competency comparison
        content.append("## Cross-Department Competency Comparison")
        content.append("")
        
        # Get top competencies
        top_competencies = latest_data.groupby('direcionador')['frequencia_colaborador'].mean().sort_values(ascending=False).head(5).index.tolist()
        
        for competency in top_competencies:
            comp_data = latest_data[latest_data['direcionador'] == competency]
            
            content.append(f"### {competency}")
            content.append("")
            
            # Department performance on this competency
            dept_comp_avg = comp_data.groupby('department')['frequencia_colaborador'].mean().reset_index()
            dept_comp_avg = dept_comp_avg.sort_values('frequencia_colaborador', ascending=False)
            
            # Department comparison barchart
            content.append("```mermaid")
            content.append("%%{init: {'theme':'forest'}}%%")
            content.append("barchart")
            content.append(f"    title {competency} Scores by Department")
            content.append("    x-axis [Departments]")
            content.append("    y-axis [Score (0-4)]")
            
            for _, row in dept_comp_avg.iterrows():
                content.append(f"    \"{row['department']}\" {row['frequencia_colaborador']:.2f}")
                
            content.append("```")
            content.append("")
            
            # Department comparison table
            content.append("| Department | Score | +/- Org Average |")
            content.append("|------------|-------|----------------|")
            
            # Calculate organizational average for this competency
            org_avg = comp_data['frequencia_colaborador'].mean()
            
            for _, row in dept_comp_avg.iterrows():
                dept_score = row['frequencia_colaborador']
                diff = dept_score - org_avg
                diff_text = f"+{diff:.2f}" if diff > 0 else f"{diff:.2f}"
                
                content.append(f"| {row['department']} | {dept_score:.2f} | {diff_text} |")
                
            content.append("")
        
        # Heatmap representation
        content.append("## Department-Competency Heatmap")
        content.append("")
        content.append("This table shows the relative performance of departments across different competency areas:")
        content.append("")
        
        # Get top departments and competencies for the heatmap
        top_departments = dept_avg.head(6)['department'].tolist()
        
        # Calculate competency averages
        comp_avg = latest_data.groupby('direcionador')['frequencia_colaborador'].mean().reset_index()
        comp_avg = comp_avg.sort_values('frequencia_colaborador', ascending=False)
        top_competencies = comp_avg.head(6)['direcionador'].tolist()
        
        # Create the heatmap header
        content.append("| Department | " + " | ".join(top_competencies) + " | Overall |")
        content.append("|" + "-" * 12 + "|" + "".join(["-" * 12 + "|" for _ in top_competencies]) + "-" * 9 + "|")
        
        # Calculate and populate the heatmap
        for dept in top_departments:
            dept_data = latest_data[latest_data['department'] == dept]
            overall_avg = dept_data['frequencia_colaborador'].mean()
            
            row_values = [dept]
            
            for comp in top_competencies:
                comp_data = dept_data[dept_data['direcionador'] == comp]
                if not comp_data.empty:
                    comp_avg = comp_data['frequencia_colaborador'].mean()
                    
                    # Format based on performance (higher is better)
                    if comp_avg >= 3.5:
                        cell = f"🟢 {comp_avg:.2f}"
                    elif comp_avg >= 2.5:
                        cell = f"🟡 {comp_avg:.2f}"
                    else:
                        cell = f"🔴 {comp_avg:.2f}"
                    
                    row_values.append(cell)
                else:
                    row_values.append("N/A")
            
            # Format overall score
            if overall_avg >= 3.5:
                overall_cell = f"🟢 {overall_avg:.2f}"
            elif overall_avg >= 2.5:
                overall_cell = f"🟡 {overall_avg:.2f}"
            else:
                overall_cell = f"🔴 {overall_avg:.2f}"
                
            row_values.append(overall_cell)
            
            content.append("| " + " | ".join(row_values) + " |")
        
        content.append("")
        content.append("**Legend**: 🟢 Strong (≥3.5) | 🟡 Satisfactory (2.5-3.5) | 🔴 Needs Improvement (<2.5)")
        content.append("")
        
        # Overall recommendations
        content.append("## Recommendations for Team Development")
        content.append("")
        
        # Find common development areas
        overall_comp_avg = latest_data.groupby('direcionador')['frequencia_colaborador'].mean().reset_index()
        overall_comp_avg = overall_comp_avg.sort_values('frequencia_colaborador')
        bottom_competencies = overall_comp_avg.head(3)['direcionador'].tolist()
        
        content.append("Based on the aggregated data, the following organization-wide focus areas are recommended:")
        content.append("")
        
        for comp in bottom_competencies:
            comp_data = latest_data[latest_data['direcionador'] == comp]
            comp_avg = comp_data['frequencia_colaborador'].mean()
            content.append(f"1. **{comp}** ({comp_avg:.2f})")
            content.append("   - Consider organization-wide training programs focused on this area")
            content.append("   - Identify and leverage high performers as internal coaches")
            content.append("   - Set specific team-level improvement goals for this competency")
            content.append("")
        
        # Save report file
        output_file = output_dir / f"team_analysis_{timestamp}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))
            
        self.logger.info(f"Team aggregation report generated: {output_file}")
        return str(output_file)

    def generate_benchmark_report(self) -> dict:
        """Generate benchmark comparison reports for individuals.
        
        Returns:
            Dictionary mapping person names to report file paths
        """
        # Find all resultado.json files
        files = list(self.data_path.glob("**/resultado.json"))
        
        if not files:
            self.logger.warning("No files found to generate benchmark reports")
            return None
            
        # Collect all data by person
        all_data = []
        
        for file_path in files:
            try:
                # Skip empty files
                if file_path.stat().st_size == 0:
                    continue
                    
                # Extract person and year from path
                parts = file_path.parts
                person = parts[-3]
                year = parts[-2]
                
                # Load the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load profile
                perfil_path = file_path.parent / "perfil.json"
                with open(perfil_path, 'r', encoding='utf-8') as f:
                    perfil = json.load(f)
                
                # Process data
                for direcionador in data['data']['direcionadores']:
                    for comportamento in direcionador['comportamentos']:
                        for avaliacao in comportamento['avaliacoes_grupo']:
                            row = {
                                "pessoa": person,
                                "ano": year,
                                "cargo": perfil['cargo'],
                                "nivel": perfil['nivel_cargo'],
                                "conceito": data['data']['conceito_ciclo_filho_descricao'],
                                "direcionador": direcionador['direcionador'],
                                "comportamento": comportamento['comportamento'],
                                "avaliador": avaliacao['avaliador'],
                                "frequencia_colaborador": sum(i * v for i, v in enumerate(avaliacao['frequencia_colaborador'])) / sum(avaliacao['frequencia_colaborador']),
                                "frequencia_grupo": sum(i * v for i, v in enumerate(avaliacao['frequencia_grupo'])) / sum(avaliacao['frequencia_grupo'])
                            }
                            all_data.append(row)
                            
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                continue
        
        if not all_data:
            self.logger.warning("No valid data found to generate benchmark reports")
            return None
            
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory
        output_dir = self.output_path / "benchmark_reports"
        output_dir.mkdir(exist_ok=True)
        
        # Define expected benchmark thresholds by level
        # These could come from a configuration file in a real implementation
        benchmarks = {
            "Junior": {
                "threshold": 2.5,
                "next_level": "Mid-level",
                "next_threshold": 3.0
            },
            "Mid-level": {
                "threshold": 3.0,
                "next_level": "Senior",
                "next_threshold": 3.5
            },
            "Senior": {
                "threshold": 3.5,
                "next_level": "Principal",
                "next_threshold": 3.8
            },
            "Principal": {
                "threshold": 3.8,
                "next_level": "Director",
                "next_threshold": 4.0
            },
            "Director": {
                "threshold": 4.0,
                "next_level": None,
                "next_threshold": None
            },
            "Executive": {
                "threshold": 4.0,
                "next_level": None,
                "next_threshold": None
            }
        }
        
        # Generate benchmark report for each person
        report_files = {}
        
        for person in df['pessoa'].unique():
            person_data = df[df['pessoa'] == person]
            
            # Get latest year
            latest_year = max(person_data['ano'].unique())
            latest_data = person_data[person_data['ano'] == latest_year]
            
            # Get level info
            levels = latest_data['nivel'].unique()
            if not levels.size:
                self.logger.warning(f"Skipping benchmark for {person}: missing level information")
                continue
                
            current_level = levels[0]
            # Map to standardized level if not in benchmarks
            if current_level not in benchmarks:
                if "junior" in current_level.lower() or "trainee" in current_level.lower():
                    level_key = "Junior"
                elif "mid" in current_level.lower() or "intermediate" in current_level.lower():
                    level_key = "Mid-level"
                elif "senior" in current_level.lower():
                    level_key = "Senior"
                elif "principal" in current_level.lower() or "staff" in current_level.lower():
                    level_key = "Principal"
                elif "director" in current_level.lower() or "manager" in current_level.lower():
                    level_key = "Director"
                elif "exec" in current_level.lower() or "cxo" in current_level.lower():
                    level_key = "Executive"
                else:
                    # Default to Mid-level if we can't determine
                    level_key = "Mid-level"
            else:
                level_key = current_level
                
            # Get benchmark data
            if level_key in benchmarks:
                benchmark = benchmarks[level_key]
            else:
                self.logger.warning(f"Using default benchmarks for {person}: level {level_key} not found")
                benchmark = benchmarks["Mid-level"]
            
            content = []
            content.append(f"# Performance Benchmark Report for {person}")
            content.append("")
            content.append("## Overview")
            content.append("")
            content.append(f"This report compares {person}'s performance against expected benchmarks for their current level ({current_level}) and the requirements for the next level.")
            content.append("")
            
            # Current level benchmark comparison
            content.append("## Current Level Benchmark")
            content.append("")
            
            # Calculate overall score
            overall_score = latest_data['frequencia_colaborador'].mean()
            meets_benchmark = overall_score >= benchmark["threshold"]
            
            content.append(f"**Current Level:** {current_level}")
            content.append(f"**Expected Benchmark:** {benchmark['threshold']:.2f}")
            content.append(f"**Overall Score:** {overall_score:.2f}")
            content.append(f"**Status:** {'✅ Meets' if meets_benchmark else '❌ Below'} benchmark for current level")
            content.append("")
            
            # Next level comparison
            if benchmark["next_level"]:
                content.append("## Next Level Readiness")
                content.append("")
                
                next_level = benchmark["next_level"]
                next_threshold = benchmark["next_threshold"]
                ready_for_next = overall_score >= next_threshold
                
                content.append(f"**Next Level:** {next_level}")
                content.append(f"**Required Benchmark:** {next_threshold:.2f}")
                content.append(f"**Overall Score:** {overall_score:.2f}")
                content.append(f"**Status:** {'✅ Ready' if ready_for_next else '❌ Not yet ready'} for {next_level}")
                content.append("")
                
                # Gap to next level
                if not ready_for_next:
                    gap = next_threshold - overall_score
                    content.append(f"**Gap to Next Level:** {gap:.2f}")
                    content.append("")
            
            # Competency benchmark comparison
            content.append("## Competency Benchmark Comparison")
            content.append("")
            
            # Prepare data
            comp_avg = latest_data.groupby('direcionador')['frequencia_colaborador'].mean().reset_index()
            
            # Chart
            content.append("```mermaid")
            content.append("%%{init: {'theme':'forest'}}%%")
            content.append("xychart-beta")
            content.append(f"    title \"Competency Scores vs. Benchmarks for {person}\"")
            content.append("    x-axis [Competency]")
            content.append("    y-axis \"Score\" [0 - 4]")
            
            # Plot competency scores
            content.append("    bar [Your Score]")
            for _, row in comp_avg.iterrows():
                content.append(f"      \"{row['direcionador']}\" {row['frequencia_colaborador']:.2f}")
                
            # Plot current level benchmark
            content.append("    line [Current Level Benchmark]")
            for _ in comp_avg.iterrows():
                content.append(f"      \"{row['direcionador']}\" {benchmark['threshold']:.2f}")
                
            # Plot next level benchmark if applicable
            if benchmark["next_level"]:
                content.append("    line [Next Level Benchmark]")
                for _ in comp_avg.iterrows():
                    content.append(f"      \"{row['direcionador']}\" {benchmark['next_threshold']:.2f}")
                    
            content.append("```")
            content.append("")
            
            # Detailed competency table
            content.append("| Competency | Your Score | Current Benchmark | Status | Next Level Benchmark | Gap |")
            content.append("|------------|------------|-------------------|--------|---------------------|-----|")
            
            for _, row in comp_avg.iterrows():
                direcionador = row['direcionador']
                score = row['frequencia_colaborador']
                
                meets_current = score >= benchmark["threshold"]
                status = "✅ Meets" if meets_current else "❌ Below"
                
                if benchmark["next_level"]:
                    next_threshold = benchmark["next_threshold"]
                    gap = max(0, next_threshold - score)
                    gap_text = f"{gap:.2f}" if gap > 0 else "—"
                    content.append(f"| {direcionador} | {score:.2f} | {benchmark['threshold']:.2f} | {status} | {next_threshold:.2f} | {gap_text} |")
                else:
                    content.append(f"| {direcionador} | {score:.2f} | {benchmark['threshold']:.2f} | {status} | — | — |")
            
            content.append("")
            
            # Skills gap analysis
            if benchmark["next_level"]:
                content.append("## Skills Gap Analysis")
                content.append("")
                
                # Find competencies furthest from next level
                comp_avg['gap'] = benchmark["next_threshold"] - comp_avg['frequencia_colaborador']
                comp_gaps = comp_avg[comp_avg['gap'] > 0].sort_values('gap', ascending=False)
                
                if not comp_gaps.empty:
                    content.append(f"To reach the {benchmark['next_level']} level, focus on improving these competencies:")
                    content.append("")
                    
                    for _, row in comp_gaps.iterrows():
                        content.append(f"- **{row['direcionador']}**: Current score {row['frequencia_colaborador']:.2f}, " +
                                      f"gap of {row['gap']:.2f} to reach {benchmark['next_threshold']:.2f}")
                    
                    content.append("")
                else:
                    content.append(f"You're meeting all competency benchmarks for the {benchmark['next_level']} level!")
                    content.append("")
            
            # Peer comparison
            content.append("## Peer Group Comparison")
            content.append("")
            
            # Calculate peer group averages by competency
            peer_avg = latest_data.groupby('direcionador')['frequencia_grupo'].mean().reset_index()
            peer_avg = peer_avg.merge(comp_avg, on='direcionador')
            peer_avg['diff'] = peer_avg['frequencia_colaborador'] - peer_avg['frequencia_grupo']
            
            # Sort by difference
            peer_avg = peer_avg.sort_values('diff', ascending=False)
            
            # Table of peer comparisons
            content.append("| Competency | Your Score | Peer Average | Difference |")
            content.append("|------------|------------|--------------|------------|")
            
            for _, row in peer_avg.iterrows():
                diff = row['diff']
                diff_text = f"+{diff:.2f}" if diff > 0 else f"{diff:.2f}"
                content.append(f"| {row['direcionador']} | {row['frequencia_colaborador']:.2f} | {row['frequencia_grupo']:.2f} | {diff_text} |")
                
            content.append("")
            
            # Summary and recommendations
            content.append("## Summary and Recommendations")
            content.append("")
            
            if meets_benchmark:
                content.append(f"✅ **Overall Assessment**: You are meeting the performance expectations for your current level ({current_level}).")
            else:
                content.append(f"❌ **Overall Assessment**: You are currently below the benchmark for your level ({current_level}).")
            content.append("")
            
            if benchmark["next_level"]:
                if ready_for_next:
                    content.append(f"✅ **Next Level Readiness**: Your performance meets the benchmarks for {benchmark['next_level']}.")
                else:
                    content.append(f"❓ **Next Level Readiness**: You have a gap of {(next_threshold - overall_score):.2f} to reach the benchmark for {benchmark['next_level']}.")
                content.append("")
            
            # Add top strengths
            top_strengths = peer_avg.sort_values('frequencia_colaborador', ascending=False).head(3)
            content.append("**Key Strengths:**")
            content.append("")
            for _, row in top_strengths.iterrows():
                content.append(f"- {row['direcionador']} ({row['frequencia_colaborador']:.2f})")
            content.append("")
            
            # Add improvement areas
            if benchmark["next_level"] and not ready_for_next:
                top_gaps = comp_gaps.head(3)
                content.append("**Focus Areas for Growth:**")
                content.append("")
                for _, row in top_gaps.iterrows():
                    content.append(f"- {row['direcionador']} (current: {row['frequencia_colaborador']:.2f}, target: {benchmark['next_threshold']:.2f})")
                content.append("")
            
            # Save report file
            output_file = output_dir / f"benchmark_{person.replace(' ', '_')}_{timestamp}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
                
            report_files[person] = str(output_file)
            self.logger.info(f"Benchmark report generated for {person}: {output_file}")
        
        return report_files 

    def generate_heat_map(self) -> dict:
        """Generate heat map visualizations of evaluation data.
        
        Returns:
            Dictionary mapping person names to report file paths
        """
        # Find all resultado.json files
        files = list(self.data_path.glob("**/resultado.json"))
        
        if not files:
            self.logger.warning("No files found to generate heat maps")
            return None
            
        # Collect all data by person
        all_data = []
        
        for file_path in files:
            try:
                # Skip empty files
                if file_path.stat().st_size == 0:
                    continue
                    
                # Extract person and year from path
                parts = file_path.parts
                person = parts[-3]
                year = parts[-2]
                
                # Load the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load profile
                perfil_path = file_path.parent / "perfil.json"
                with open(perfil_path, 'r', encoding='utf-8') as f:
                    perfil = json.load(f)
                
                # Process data
                for direcionador in data['data']['direcionadores']:
                    for comportamento in direcionador['comportamentos']:
                        for avaliacao in comportamento['avaliacoes_grupo']:
                            # Determine the stakeholder type
                            stakeholder = avaliacao['avaliador'].lower()
                            if 'gestor' in stakeholder or 'manager' in stakeholder:
                                stakeholder_type = 'manager'
                            elif 'auto' in stakeholder or 'self' in stakeholder:
                                stakeholder_type = 'self'
                            else:
                                stakeholder_type = 'peer'
                                
                            row = {
                                "pessoa": person,
                                "ano": year,
                                "cargo": perfil['cargo'],
                                "nivel": perfil['nivel_cargo'],
                                "conceito": data['data']['conceito_ciclo_filho_descricao'],
                                "direcionador": direcionador['direcionador'],
                                "comportamento": comportamento['comportamento'],
                                "avaliador": avaliacao['avaliador'],
                                "stakeholder_type": stakeholder_type,
                                "frequencia_colaborador": sum(i * v for i, v in enumerate(avaliacao['frequencia_colaborador'])) / sum(avaliacao['frequencia_colaborador']),
                                "frequencia_grupo": sum(i * v for i, v in enumerate(avaliacao['frequencia_grupo'])) / sum(avaliacao['frequencia_grupo'])
                            }
                            all_data.append(row)
                            
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                continue
        
        if not all_data:
            self.logger.warning("No valid data found to generate heat maps")
            return None
            
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory
        output_dir = self.output_path / "heat_maps"
        output_dir.mkdir(exist_ok=True)
        
        # Generate heat map for each person
        report_files = {}
        
        for person in df['pessoa'].unique():
            person_data = df[df['pessoa'] == person]
            
            # Get latest year
            latest_year = max(person_data['ano'].unique())
            latest_data = person_data[person_data['ano'] == latest_year]
            
            content = []
            content.append(f"# Performance Heat Map for {person}")
            content.append("")
            content.append("## Overview")
            content.append("")
            content.append("This heat map visualization shows performance scores across different competencies and behaviors.")
            content.append("The colors indicate performance level (red = low, yellow = medium, green = high).")
            content.append("")
            
            # Create heat map by competency and behavior
            content.append("## Competency-Behavior Heat Map")
            content.append("")
            
            # Get all direcionadores and comportamentos
            direcionadores = latest_data['direcionador'].unique()
            
            # Create heat map
            for direcionador in direcionadores:
                dir_data = latest_data[latest_data['direcionador'] == direcionador]
                comportamentos = dir_data['comportamento'].unique()
                
                content.append(f"### {direcionador}")
                content.append("")
                content.append("| Behavior | Manager | Self | Peer | Overall | Group Avg |")
                content.append("|----------|---------|------|------|---------|-----------|")
                
                for comportamento in comportamentos:
                    comp_data = dir_data[dir_data['comportamento'] == comportamento]
                    
                    # Get scores by stakeholder type
                    row = [comportamento]
                    
                    # Function to format score with color
                    def format_score(score):
                        if score is None:
                            return "N/A"
                        elif score >= 3.5:
                            return f"🟢 {score:.2f}"
                        elif score >= 2.5:
                            return f"🟡 {score:.2f}"
                        else:
                            return f"🔴 {score:.2f}"
                    
                    # Manager score
                    manager_data = comp_data[comp_data['stakeholder_type'] == 'manager']
                    if not manager_data.empty:
                        manager_score = manager_data['frequencia_colaborador'].mean()
                        row.append(format_score(manager_score))
                    else:
                        row.append("N/A")
                    
                    # Self score
                    self_data = comp_data[comp_data['stakeholder_type'] == 'self']
                    if not self_data.empty:
                        self_score = self_data['frequencia_colaborador'].mean()
                        row.append(format_score(self_score))
                    else:
                        row.append("N/A")
                    
                    # Peer score
                    peer_data = comp_data[comp_data['stakeholder_type'] == 'peer']
                    if not peer_data.empty:
                        peer_score = peer_data['frequencia_colaborador'].mean()
                        row.append(format_score(peer_score))
                    else:
                        row.append("N/A")
                    
                    # Overall score
                    overall_score = comp_data['frequencia_colaborador'].mean()
                    row.append(format_score(overall_score))
                    
                    # Group average
                    group_avg = comp_data['frequencia_grupo'].mean()
                    row.append(format_score(group_avg))
                    
                    content.append("| " + " | ".join(row) + " |")
                
                content.append("")
            
            # Create overall heat map
            content.append("## Overall Competency Heat Map")
            content.append("")
            
            # Calculate averages by competency and stakeholder
            comp_data = latest_data.groupby(['direcionador', 'stakeholder_type'])['frequencia_colaborador'].mean().reset_index()
            comp_overall = latest_data.groupby('direcionador')['frequencia_colaborador'].mean().reset_index()
            comp_group = latest_data.groupby('direcionador')['frequencia_grupo'].mean().reset_index()
            
            # Create table
            content.append("| Competency | Manager | Self | Peer | Overall | Group Avg |")
            content.append("|------------|---------|------|------|---------|-----------|")
            
            for direcionador in direcionadores:
                row = [direcionador]
                
                # Manager score
                manager_row = comp_data[(comp_data['direcionador'] == direcionador) & (comp_data['stakeholder_type'] == 'manager')]
                if not manager_row.empty:
                    manager_score = manager_row['frequencia_colaborador'].values[0]
                    row.append(format_score(manager_score))
                else:
                    row.append("N/A")
                
                # Self score
                self_row = comp_data[(comp_data['direcionador'] == direcionador) & (comp_data['stakeholder_type'] == 'self')]
                if not self_row.empty:
                    self_score = self_row['frequencia_colaborador'].values[0]
                    row.append(format_score(self_score))
                else:
                    row.append("N/A")
                
                # Peer score
                peer_row = comp_data[(comp_data['direcionador'] == direcionador) & (comp_data['stakeholder_type'] == 'peer')]
                if not peer_row.empty:
                    peer_score = peer_row['frequencia_colaborador'].values[0]
                    row.append(format_score(peer_score))
                else:
                    row.append("N/A")
                
                # Overall score
                overall_row = comp_overall[comp_overall['direcionador'] == direcionador]
                if not overall_row.empty:
                    overall_score = overall_row['frequencia_colaborador'].values[0]
                    row.append(format_score(overall_score))
                else:
                    row.append("N/A")
                
                # Group average
                group_row = comp_group[comp_group['direcionador'] == direcionador]
                if not group_row.empty:
                    group_score = group_row['frequencia_grupo'].values[0]
                    row.append(format_score(group_score))
                else:
                    row.append("N/A")
                
                content.append("| " + " | ".join(row) + " |")
            
            content.append("")
            content.append("**Legend**: 🟢 Strong (≥3.5) | 🟡 Satisfactory (2.5-3.5) | 🔴 Needs Improvement (<2.5)")
            content.append("")
            
            # Save heat map file
            output_file = output_dir / f"heat_map_{person.replace(' ', '_')}_{timestamp}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
                
            report_files[person] = str(output_file)
            self.logger.info(f"Heat map generated for {person}: {output_file}")
            
        return report_files
        
    def generate_natural_language_summary(self) -> dict:
        """Generate natural language summaries of evaluation data.
        
        Returns:
            Dictionary mapping person names to report file paths
        """
        # Find all resultado.json files
        files = list(self.data_path.glob("**/resultado.json"))
        
        if not files:
            self.logger.warning("No files found to generate natural language summaries")
            return None
            
        # Collect all data by person
        all_data = []
        
        for file_path in files:
            try:
                # Skip empty files
                if file_path.stat().st_size == 0:
                    continue
                    
                # Extract person and year from path
                parts = file_path.parts
                person = parts[-3]
                year = parts[-2]
                
                # Load the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load profile
                perfil_path = file_path.parent / "perfil.json"
                with open(perfil_path, 'r', encoding='utf-8') as f:
                    perfil = json.load(f)
                
                # Process data
                for direcionador in data['data']['direcionadores']:
                    for comportamento in direcionador['comportamentos']:
                        for avaliacao in comportamento['avaliacoes_grupo']:
                            # Determine the stakeholder type
                            stakeholder = avaliacao['avaliador'].lower()
                            if 'gestor' in stakeholder or 'manager' in stakeholder:
                                stakeholder_type = 'manager'
                            elif 'auto' in stakeholder or 'self' in stakeholder:
                                stakeholder_type = 'self'
                            else:
                                stakeholder_type = 'peer'
                                
                            row = {
                                "pessoa": person,
                                "ano": year,
                                "cargo": perfil['cargo'],
                                "nivel": perfil['nivel_cargo'],
                                "conceito": data['data']['conceito_ciclo_filho_descricao'],
                                "direcionador": direcionador['direcionador'],
                                "comportamento": comportamento['comportamento'],
                                "avaliador": avaliacao['avaliador'],
                                "stakeholder_type": stakeholder_type,
                                "frequencia_colaborador": sum(i * v for i, v in enumerate(avaliacao['frequencia_colaborador'])) / sum(avaliacao['frequencia_colaborador']),
                                "frequencia_grupo": sum(i * v for i, v in enumerate(avaliacao['frequencia_grupo'])) / sum(avaliacao['frequencia_grupo'])
                            }
                            all_data.append(row)
                            
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                continue
        
        if not all_data:
            self.logger.warning("No valid data found to generate natural language summaries")
            return None
            
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory
        output_dir = self.output_path / "summaries"
        output_dir.mkdir(exist_ok=True)
        
        # Generate natural language summary for each person
        report_files = {}
        
        for person in df['pessoa'].unique():
            person_data = df[df['pessoa'] == person]
            
            # Get latest year
            latest_year = max(person_data['ano'].unique())
            latest_data = person_data[person_data['ano'] == latest_year]
            
            # Get job info
            job_title = latest_data['cargo'].iloc[0] if 'cargo' in latest_data else "Unknown Role"
            job_level = latest_data['nivel'].iloc[0] if 'nivel' in latest_data else "Unknown Level"
            
            # Get overall assessment
            overall_assessment = latest_data['conceito'].iloc[0] if 'conceito' in latest_data else "Unknown"
            
            # Calculate overall score
            overall_score = latest_data['frequencia_colaborador'].mean()
            group_score = latest_data['frequencia_grupo'].mean()
            score_diff = overall_score - group_score
            
            # Get top and bottom competencies
            comp_scores = latest_data.groupby('direcionador')['frequencia_colaborador'].mean()
            top_comps = comp_scores.nlargest(2)
            bottom_comps = comp_scores.nsmallest(2)
            
            # Generate content
            content = []
            content.append(f"# Natural Language Summary for {person}")
            content.append("")
            
            # Generate natural language summary
            summary = []
            
            # Introduction paragraph
            intro = f"{person} is a {job_level} {job_title} with an overall assessment of \"{overall_assessment}\". "
            
            if score_diff > 0.5:
                intro += f"Their performance is considerably above the peer group average, scoring {overall_score:.2f} versus the group average of {group_score:.2f}. "
            elif score_diff > 0.1:
                intro += f"Their performance is slightly above the peer group average, scoring {overall_score:.2f} versus the group average of {group_score:.2f}. "
            elif score_diff < -0.5:
                intro += f"Their performance is considerably below the peer group average, scoring {overall_score:.2f} versus the group average of {group_score:.2f}. "
            elif score_diff < -0.1:
                intro += f"Their performance is slightly below the peer group average, scoring {overall_score:.2f} versus the group average of {group_score:.2f}. "
            else:
                intro += f"Their performance is in line with the peer group average, scoring {overall_score:.2f} versus the group average of {group_score:.2f}. "
                
            summary.append(intro)
            
            # Strengths paragraph
            strengths = f"{person}'s key strengths are in "
            
            for i, (comp, score) in enumerate(top_comps.items()):
                if i == len(top_comps) - 1 and i > 0:
                    strengths += f"and {comp} ({score:.2f}). "
                else:
                    strengths += f"{comp} ({score:.2f})"
                    if i < len(top_comps) - 1:
                        strengths += ", "
                    else:
                        strengths += ". "
            
            # Add comparison to peer group for strengths
            strongest_comp = top_comps.index[0]
            strongest_peer = latest_data[latest_data['direcionador'] == strongest_comp]['frequencia_grupo'].mean()
            strength_diff = top_comps.iloc[0] - strongest_peer
            
            if strength_diff > 0.5:
                strengths += f"They particularly excel in {strongest_comp}, scoring significantly higher than peers. "
            elif strength_diff > 0.1:
                strengths += f"Their {strongest_comp} skills are above the peer group average. "
                
            summary.append(strengths)
            
            # Development areas paragraph
            development = f"Areas for potential development include "
            
            for i, (comp, score) in enumerate(bottom_comps.items()):
                if i == len(bottom_comps) - 1 and i > 0:
                    development += f"and {comp} ({score:.2f}). "
                else:
                    development += f"{comp} ({score:.2f})"
                    if i < len(bottom_comps) - 1:
                        development += ", "
                    else:
                        development += ". "
            
            # Add comparison to peer group for development areas
            weakest_comp = bottom_comps.index[0]
            weakest_peer = latest_data[latest_data['direcionador'] == weakest_comp]['frequencia_grupo'].mean()
            weakness_diff = bottom_comps.iloc[0] - weakest_peer
            
            if weakness_diff < -0.5:
                development += f"Their {weakest_comp} score is significantly below the peer group average and should be a focus area. "
            elif weakness_diff < -0.1:
                development += f"Their {weakest_comp} score is somewhat below the peer group average. "
            else:
                development += f"While {weakest_comp} is their lowest-scoring area, it's still within range of the peer group average. "
                
            summary.append(development)
            
            # Stakeholder perspective paragraph
            stakeholder_data = latest_data.groupby('stakeholder_type')['frequencia_colaborador'].mean()
            
            if len(stakeholder_data) > 1:
                perspective = "In terms of different perspectives, "
                
                # Manager perspective
                if 'manager' in stakeholder_data:
                    manager_score = stakeholder_data['manager']
                    if manager_score > overall_score + 0.3:
                        perspective += f"their manager rates them higher ({manager_score:.2f}) than the overall average. "
                    elif manager_score < overall_score - 0.3:
                        perspective += f"their manager rates them lower ({manager_score:.2f}) than the overall average. "
                    else:
                        perspective += f"their manager's assessment ({manager_score:.2f}) aligns with the overall ratings. "
                
                # Self perspective
                if 'self' in stakeholder_data:
                    self_score = stakeholder_data['self']
                    if self_score > overall_score + 0.3:
                        perspective += f"Their self-assessment ({self_score:.2f}) is higher than others' ratings. "
                    elif self_score < overall_score - 0.3:
                        perspective += f"Their self-assessment ({self_score:.2f}) is lower than others' ratings. "
                    else:
                        perspective += f"Their self-perception ({self_score:.2f}) closely matches how others see them. "
                
                # Peer perspective
                if 'peer' in stakeholder_data:
                    peer_score = stakeholder_data['peer']
                    if peer_score > overall_score + 0.3:
                        perspective += f"Peers rate them higher ({peer_score:.2f}) than the overall average. "
                    elif peer_score < overall_score - 0.3:
                        perspective += f"Peers rate them lower ({peer_score:.2f}) than the overall average. "
                    else:
                        perspective += f"Peer assessments ({peer_score:.2f}) are in line with the overall ratings. "
                
                summary.append(perspective)
                
            # Final conclusion
            conclusion = "In conclusion, "
            
            if overall_score >= 3.5:
                conclusion += f"{person} is performing very well overall, particularly in {top_comps.index[0]}. "
                if len(bottom_comps) > 0:
                    conclusion += f"For continued growth, some attention could be given to {bottom_comps.index[0]}."
            elif overall_score >= 2.5:
                conclusion += f"{person} is performing adequately overall. "
                conclusion += f"To strengthen their performance, focus on developing {bottom_comps.index[0]} while leveraging their strength in {top_comps.index[0]}."
            else:
                conclusion += f"{person} has opportunities for improvement in several areas. "
                conclusion += f"Priority should be given to development in {', '.join(bottom_comps.index.tolist())}."
                
            summary.append(conclusion)
            
            # Join paragraphs
            content.append("\n\n".join(summary))
            
            # Save summary file
            output_file = output_dir / f"natural_summary_{person.replace(' ', '_')}_{timestamp}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
                
            report_files[person] = str(output_file)
            self.logger.info(f"Natural language summary generated for {person}: {output_file}")
            
        return report_files
        
    def generate_action_plan(self) -> dict:
        """Generate action plan templates based on evaluation data.
        
        Returns:
            Dictionary mapping person names to report file paths
        """
        # Find all resultado.json files
        files = list(self.data_path.glob("**/resultado.json"))
        
        if not files:
            self.logger.warning("No files found to generate action plans")
            return None
            
        # Collect all data by person
        all_data = []
        
        for file_path in files:
            try:
                # Skip empty files
                if file_path.stat().st_size == 0:
                    continue
                    
                # Extract person and year from path
                parts = file_path.parts
                person = parts[-3]
                year = parts[-2]
                
                # Load the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load profile
                perfil_path = file_path.parent / "perfil.json"
                with open(perfil_path, 'r', encoding='utf-8') as f:
                    perfil = json.load(f)
                
                # Process data
                for direcionador in data['data']['direcionadores']:
                    for comportamento in direcionador['comportamentos']:
                        for avaliacao in comportamento['avaliacoes_grupo']:
                            row = {
                                "pessoa": person,
                                "ano": year,
                                "cargo": perfil['cargo'],
                                "nivel": perfil['nivel_cargo'],
                                "conceito": data['data']['conceito_ciclo_filho_descricao'],
                                "direcionador": direcionador['direcionador'],
                                "comportamento": comportamento['comportamento'],
                                "avaliador": avaliacao['avaliador'],
                                "frequencia_colaborador": sum(i * v for i, v in enumerate(avaliacao['frequencia_colaborador'])) / sum(avaliacao['frequencia_colaborador']),
                                "frequencia_grupo": sum(i * v for i, v in enumerate(avaliacao['frequencia_grupo'])) / sum(avaliacao['frequencia_grupo'])
                            }
                            all_data.append(row)
                            
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                continue
        
        if not all_data:
            self.logger.warning("No valid data found to generate action plans")
            return None
            
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory
        output_dir = self.output_path / "action_plans"
        output_dir.mkdir(exist_ok=True)
        
        # Development suggestions by competency
        # In a real implementation, this could come from a database or configuration file
        development_suggestions = {
            "Leadership": [
                "Shadow senior leaders in key meetings",
                "Lead a cross-functional project",
                "Mentor junior team members",
                "Complete leadership training program",
                "Read 'The 21 Irrefutable Laws of Leadership' by John Maxwell"
            ],
            "Communication": [
                "Join Toastmasters or similar public speaking group",
                "Practice active listening techniques",
                "Get feedback on written communication",
                "Take a course on presentation skills",
                "Lead more team meetings"
            ],
            "Technical Skills": [
                "Complete advanced certification in your field",
                "Contribute to open source projects",
                "Attend technical conferences",
                "Set up regular knowledge sharing sessions",
                "Take online courses to broaden technical knowledge"
            ],
            "Teamwork": [
                "Volunteer for cross-functional projects",
                "Practice giving constructive feedback",
                "Organize team building activities",
                "Take a conflict resolution workshop",
                "Improve follow-through on team commitments"
            ],
            "Problem Solving": [
                "Practice root cause analysis techniques",
                "Learn design thinking methodologies",
                "Tackle complex problems outside your comfort zone",
                "Document your problem-solving process",
                "Study how others in your field solve problems"
            ]
        }
        
        # Generic suggestions for any competency not covered above
        generic_suggestions = [
            "Identify a mentor who excels in this area",
            "Read books or articles on this topic",
            "Take relevant courses online or in-person",
            "Set specific, measurable goals for improvement",
            "Request regular feedback on progress"
        ]
        
        # Generate action plan for each person
        report_files = {}
        
        for person in df['pessoa'].unique():
            person_data = df[df['pessoa'] == person]
            
            # Get latest year
            latest_year = max(person_data['ano'].unique())
            latest_data = person_data[person_data['ano'] == latest_year]
            
            # Calculate scores by competency
            comp_scores = latest_data.groupby('direcionador')['frequencia_colaborador'].mean().reset_index()
            
            # Sort from lowest to highest (focus on improvement areas)
            comp_scores = comp_scores.sort_values('frequencia_colaborador')
            
            content = []
            content.append(f"# Development Action Plan for {person}")
            content.append("")
            content.append("## Overview")
            content.append("")
            content.append(f"This action plan is based on {person}'s performance evaluation data and focused on key development areas.")
            content.append("The plan includes specific actions, resources, and timeframes to support growth in targeted competencies.")
            content.append("")
            content.append("## Focus Areas")
            content.append("")
            
            # Add the lowest 3 competencies as focus areas
            focus_areas = comp_scores.head(3)
            
            for i, (_, row) in enumerate(focus_areas.iterrows()):
                direcionador = row['direcionador']
                score = row['frequencia_colaborador']
                
                content.append(f"### {i+1}. {direcionador} (Current Score: {score:.2f})")
                content.append("")
                content.append(f"**Target**: Improve {direcionador} skills to meet or exceed peer group average.")
                content.append("")
                content.append("**Suggested Actions:**")
                content.append("")
                
                # Add development suggestions
                if direcionador in development_suggestions:
                    suggestions = development_suggestions[direcionador]
                else:
                    # Look for partial matches
                    found = False
                    for key in development_suggestions:
                        if key.lower() in direcionador.lower() or direcionador.lower() in key.lower():
                            suggestions = development_suggestions[key]
                            found = True
                            break
                    
                    if not found:
                        suggestions = generic_suggestions
                
                # Add suggestions with checkboxes
                for suggestion in suggestions[:3]:  # Limit to 3 suggestions
                    content.append(f"- [ ] {suggestion}")
                content.append("")
                
                # Add timeline and success measures
                content.append("**Timeline:**")
                content.append("")
                content.append("- [ ] Start Date: ___________________")
                content.append("- [ ] 30-Day Check-in: ___________________")
                content.append("- [ ] 90-Day Review: ___________________")
                content.append("")
                
                content.append("**Success Measures:**")
                content.append("")
                content.append("1. _________________________________________________")
                content.append("2. _________________________________________________")
                content.append("3. _________________________________________________")
                content.append("")
                
                # Add resources
                content.append("**Resources Needed:**")
                content.append("")
                content.append("- [ ] Training budget: ___________________")
                content.append("- [ ] Mentor/Coach: ___________________")
                content.append("- [ ] Time allocation: ___________________")
                content.append("- [ ] Other: ___________________")
                content.append("")
            
            # Add strengths to leverage
            content.append("## Strengths to Leverage")
            content.append("")
            
            # Get top 2 competencies
            strengths = comp_scores.tail(2).iloc[::-1]
            
            for i, (_, row) in enumerate(strengths.iterrows()):
                direcionador = row['direcionador']
                score = row['frequencia_colaborador']
                
                content.append(f"### {i+1}. {direcionador} (Current Score: {score:.2f})")
                content.append("")
                content.append("**How to leverage this strength:**")
                content.append("")
                content.append("1. _________________________________________________")
                content.append("2. _________________________________________________")
                content.append("3. _________________________________________________")
                content.append("")
            
            # Add tracking and accountability
            content.append("## Tracking and Accountability")
            content.append("")
            content.append("**Regular Check-ins:**")
            content.append("")
            content.append("- [ ] Weekly self-reflection")
            content.append("- [ ] Monthly one-on-one with manager")
            content.append("- [ ] Quarterly review of progress")
            content.append("")
            
            content.append("**Accountability Partner:**")
            content.append("")
            content.append("Name: ___________________")
            content.append("Role: ___________________")
            content.append("Check-in Frequency: ___________________")
            content.append("")
            
            # Add commitment section
            content.append("## Commitment")
            content.append("")
            content.append("I commit to following this development plan to the best of my ability.")
            content.append("")
            content.append("Employee Signature: ___________________ Date: ___________________")
            content.append("")
            content.append("Manager Signature: ___________________ Date: ___________________")
            content.append("")
            
            # Save action plan file
            output_file = output_dir / f"action_plan_{person.replace(' ', '_')}_{timestamp}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
                
            report_files[person] = str(output_file)
            self.logger.info(f"Action plan generated for {person}: {output_file}")
            
        return report_files