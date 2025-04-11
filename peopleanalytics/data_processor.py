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