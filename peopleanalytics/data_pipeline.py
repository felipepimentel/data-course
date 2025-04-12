"""
Data Pipeline for People Analytics.

This module provides functionality for importing, exporting, and transforming
evaluation data.
"""

import glob
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class DataPipeline:
    """Handles data import, export, and transformation."""

    def __init__(self, base_path: str, schema_manager=None):
        """Initialize the data pipeline.

        Args:
            base_path: Base directory for data storage
            schema_manager: Optional schema manager for validation
        """
        self.base_path = base_path
        self.schema_manager = schema_manager
        self.debug_mode = False

        # Ensure the base directory exists
        os.makedirs(base_path, exist_ok=True)

    def ingest_file(
        self,
        file_path: str,
        year: Optional[str] = None,
        person: Optional[str] = None,
        overwrite: bool = False,
    ) -> Dict[str, Any]:
        """Ingest a single file into the database.

        Args:
            file_path: Path to the file to ingest
            year: Optional override for the year
            person: Optional override for the person
            overwrite: Whether to overwrite existing data

        Returns:
            Dictionary with status information
        """
        debug_info = []
        if self.debug_mode:
            debug_info.append(f"Processing file: {file_path}")
            debug_info.append(f"Year override: {year}, Person override: {person}")

        try:
            # Read and parse file
            try:
                if self.debug_mode:
                    debug_info.append("Reading file content")

                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if self.debug_mode:
                    debug_info.append(
                        f"Successfully parsed JSON with {len(data.keys() if isinstance(data, dict) else data)} keys/items"
                    )

            except json.JSONDecodeError as e:
                error_info = {
                    "success": False,
                    "file": file_path,
                    "error": f"JSON parsing error: {str(e)}",
                    "error_type": "json_decode",
                }
                if self.debug_mode:
                    error_info["debug_info"] = debug_info
                    error_info["error_trace"] = str(e)
                return error_info

            except UnicodeDecodeError as e:
                error_info = {
                    "success": False,
                    "file": file_path,
                    "error": f"File encoding error: {str(e)}",
                    "error_type": "encoding",
                }
                if self.debug_mode:
                    error_info["debug_info"] = debug_info
                    error_info["error_trace"] = str(e)
                return error_info

            except FileNotFoundError:
                error_info = {
                    "success": False,
                    "file": file_path,
                    "error": "File not found",
                    "error_type": "not_found",
                }
                if self.debug_mode:
                    error_info["debug_info"] = debug_info
                return error_info

            except PermissionError:
                error_info = {
                    "success": False,
                    "file": file_path,
                    "error": "Permission denied",
                    "error_type": "permission",
                }
                if self.debug_mode:
                    error_info["debug_info"] = debug_info
                return error_info

            # Extract person and year
            extracted_person = person or data.get("person")
            extracted_year = year or data.get("year")

            if self.debug_mode:
                debug_info.append(
                    f"Extracted person: {extracted_person}, year: {extracted_year}"
                )

            # Attempt to extract from structure like <person>/<year>/result.json
            if not extracted_person or not extracted_year:
                try:
                    parts = os.path.normpath(file_path).split(os.sep)
                    if len(parts) >= 3:
                        # Try to use the parent directories as person/year
                        potential_year = parts[-2]  # Second last component
                        potential_person = parts[-3]  # Third last component

                        if self.debug_mode:
                            debug_info.append(
                                f"Attempting to extract from path - potential year: {potential_year}, person: {potential_person}"
                            )

                        extracted_year = extracted_year or potential_year
                        extracted_person = extracted_person or potential_person

                        if self.debug_mode:
                            debug_info.append(
                                f"After path extraction - year: {extracted_year}, person: {extracted_person}"
                            )
                except Exception as e:
                    if self.debug_mode:
                        debug_info.append(f"Path extraction error: {str(e)}")
                    # If this fails, continue with the original values
                    pass

                # If still no person/year, report error
                if not extracted_person or not extracted_year:
                    missing = []
                    if not extracted_person:
                        missing.append("person")
                    if not extracted_year:
                        missing.append("year")

                    error_info = {
                        "success": False,
                        "file": file_path,
                        "error": f"Missing required fields: {', '.join(missing)}",
                        "error_type": "missing_fields",
                        "data_keys": list(data.keys())
                        if isinstance(data, dict)
                        else [],
                    }
                    if self.debug_mode:
                        error_info["debug_info"] = debug_info
                    return error_info

            # Create directory if it doesn't exist - use <person>/<year>/resultado.json pattern
            target_dir = os.path.join(self.base_path, extracted_person, extracted_year)
            if self.debug_mode:
                debug_info.append(f"Target directory: {target_dir}")

            os.makedirs(target_dir, exist_ok=True)

            # Determine target filename - use resultado.json as standard
            target_path = os.path.join(target_dir, "resultado.json")

            if self.debug_mode:
                debug_info.append("Target filename: resultado.json")
                debug_info.append(f"Full target path: {target_path}")
                debug_info.append(
                    f"Checking if target exists: {os.path.exists(target_path)}"
                )

            # Check if file already exists
            if os.path.exists(target_path) and not overwrite:
                error_info = {
                    "success": False,
                    "file": file_path,
                    "error": "File already exists and overwrite is disabled",
                    "error_type": "exists",
                }
                if self.debug_mode:
                    error_info["debug_info"] = debug_info
                return error_info

            # Copy file
            if self.debug_mode:
                debug_info.append(f"Copying file from {file_path} to {target_path}")

            shutil.copy2(file_path, target_path)

            result = {
                "success": True,
                "file": file_path,
                "target": target_path,
                "person": extracted_person,
                "year": extracted_year,
            }

            if self.debug_mode:
                result["debug_info"] = debug_info

            return result

        except Exception as e:
            error_info = {
                "success": False,
                "file": file_path,
                "error": f"Unexpected error: {str(e)}",
                "error_type": "unexpected",
            }
            if self.debug_mode:
                error_info["debug_info"] = debug_info
                error_info["error_trace"] = str(e)
            return error_info

    def ingest_directory(
        self,
        directory: str,
        pattern: str = "*.json",
        overwrite: bool = False,
        parallel: bool = True,
        debug: bool = False,
    ) -> Dict[str, Any]:
        """Ingest all files in a directory.

        Args:
            directory: Directory to ingest
            pattern: File pattern to match
            overwrite: Whether to overwrite existing data
            parallel: Whether to process files in parallel
            debug: Enable debug mode for this operation

        Returns:
            Dictionary with counts of successes and failures, and detailed errors
        """
        # Set debug mode for this operation
        original_debug_mode = self.debug_mode
        if debug:
            self.debug_mode = True

        debug_info = []
        if self.debug_mode:
            debug_info.append(
                f"Searching for files in {directory} with pattern {pattern}"
            )

        # Find all matching files
        files = glob.glob(os.path.join(directory, pattern))

        if self.debug_mode:
            debug_info.append(f"Found {len(files)} matching files")

        results = []
        for file_path in files:
            if self.debug_mode:
                debug_info.append(f"Processing {file_path}")

            result = self.ingest_file(file_path, overwrite=overwrite)
            results.append(result)

            if self.debug_mode and "debug_info" in result:
                debug_info.extend(
                    [f"  {info}" for info in result.get("debug_info", [])]
                )

        # Count successes and failures
        success_count = sum(1 for r in results if r.get("success", False))
        failed_count = len(results) - success_count

        if self.debug_mode:
            debug_info.append(
                f"Processing complete: {success_count} succeeded, {failed_count} failed"
            )

        # Collect error details
        error_details = []
        for result in results:
            if not result.get("success", False):
                error_details.append(
                    {
                        "file": result.get("file", "Unknown file"),
                        "error": result.get("error", "Unknown error"),
                        "error_type": result.get("error_type", "unknown"),
                    }
                )

        # Restore original debug mode
        self.debug_mode = original_debug_mode

        result_dict = {
            "success": success_count,
            "failed": failed_count,
            "total": len(results),
            "error_details": error_details,
        }

        if debug:
            result_dict["debug_info"] = debug_info

        return result_dict

    def create_backup(self, output_dir: Optional[str] = None) -> str:
        """Create a backup of the current database.

        Args:
            output_dir: Directory to save the backup (default: current dir)

        Returns:
            Path to the backup file
        """
        if not output_dir:
            output_dir = os.getcwd()

        # Create timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"peopleanalytics_backup_{timestamp}.zip"
        backup_path = os.path.join(output_dir, backup_filename)

        # Create zip file
        shutil.make_archive(
            os.path.splitext(backup_path)[0],  # Remove .zip extension
            "zip",
            self.base_path,
        )

        return backup_path

    def export_raw_data(self, output_file: str) -> Dict[str, Any]:
        """Export all raw data as a single JSON file.

        Args:
            output_file: Path to the output file

        Returns:
            Dictionary with export status
        """
        try:
            # Find all JSON files
            files = []
            for root, _, filenames in os.walk(self.base_path):
                for filename in filenames:
                    if filename.endswith(".json"):
                        files.append(os.path.join(root, filename))

            # Read all files
            all_data = []
            for file_path in files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        all_data.append(data)
                except Exception:
                    # Skip files that can't be read
                    pass

            # Write to output file
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(all_data, f, indent=2)

            return {
                "success": True,
                "file_count": len(all_data),
                "output_file": output_file,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def fix_all_data(self, parallel: bool = True) -> Dict[str, int]:
        """Fix common issues in all data files.

        Args:
            parallel: Whether to process files in parallel

        Returns:
            Dictionary with counts of fixed and unfixed files
        """
        # This is a placeholder for a real implementation
        return {"fixed": 0, "unfixed": 0, "errors": 0}

    def load_person_data(self, person_id: str, year: int) -> Optional[Dict[str, Any]]:
        """Load data for a specific person and year.

        Args:
            person_id: The ID of the person
            year: The year to load data for

        Returns:
            Optional[Dict[str, Any]]: Data dictionary or None if not found
        """
        try:
            # Check if person directory exists
            person_dir = self.base_path / f"{person_id}_{year}"
            if not person_dir.exists() or not person_dir.is_dir():
                return None

            # Check if results file exists
            results_file = person_dir / "resultado.json"
            if not results_file.exists():
                return None

            # Load results data
            with open(results_file, "r", encoding="utf-8") as f:
                results_data = json.load(f)

            # Check if profile file exists and load it
            profile_data = None
            profile_file = person_dir / "perfil.json"
            if profile_file.exists():
                with open(profile_file, "r", encoding="utf-8") as f:
                    profile_data = json.load(f)

            # Check if career progression file exists and load it
            career_data = None
            career_file = person_dir / "carreira.json"
            if career_file.exists():
                with open(career_file, "r", encoding="utf-8") as f:
                    career_data = json.load(f)

            # Combine all data
            person_data = {"id": person_id, "year": year, "results": results_data}

            if profile_data:
                person_data["profile"] = profile_data

            if career_data:
                person_data["career_progression"] = career_data

            return person_data

        except Exception as e:
            self.logger.error(f"Error loading data for {person_id} ({year}): {e}")
            return None

    def save_person_data(self, person_id: str, year: int, data: Dict[str, Any]) -> bool:
        """Save data for a specific person and year.

        Args:
            person_id: The ID of the person
            year: The year to save data for
            data: The data to save

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create person directory if it doesn't exist
            person_dir = self.base_path / f"{person_id}_{year}"
            person_dir.mkdir(parents=True, exist_ok=True)

            # Extract components of the data
            results_data = data.get("results", {})
            profile_data = data.get("profile", None)
            career_data = data.get("career_progression", None)

            # Save results data
            results_file = person_dir / "resultado.json"
            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(results_data, f, ensure_ascii=False, indent=2)

            # Save profile data if available
            if profile_data:
                profile_file = person_dir / "perfil.json"
                with open(profile_file, "w", encoding="utf-8") as f:
                    json.dump(profile_data, f, ensure_ascii=False, indent=2)

            # Save career data if available
            if career_data:
                career_file = person_dir / "carreira.json"
                with open(career_file, "w", encoding="utf-8") as f:
                    json.dump(career_data, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            self.logger.error(f"Error saving data for {person_id} ({year}): {e}")
            return False

    def process_career_data(self, person_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process career progression data for analysis.

        Args:
            person_data: Dictionary containing person data

        Returns:
            Dict[str, Any]: Processed career data with metrics
        """
        person_id = person_data.get("id", "unknown")
        year = person_data.get("year", 0)
        career_data = person_data.get("career_progression", {})

        if not career_data:
            # Return empty template
            return {
                "id": person_id,
                "year": year,
                "has_career_data": False,
                "eventos_carreira": [],
                "matriz_habilidades": {},
                "metas_carreira": [],
                "certificacoes": [],
                "mentoria": [],
                "metricas": {},
            }

        try:
            # Extract core career components
            eventos = career_data.get("eventos_carreira", [])
            habilidades = career_data.get("matriz_habilidades", {})
            metas = career_data.get("metas_carreira", [])
            certificacoes = career_data.get("certificacoes", [])
            mentoria = career_data.get("mentoria", [])

            # Calculate metrics
            metricas = self._calculate_career_metrics(
                eventos, habilidades, certificacoes, metas, mentoria
            )

            # Compile processed data
            processed_data = {
                "id": person_id,
                "year": year,
                "has_career_data": True,
                "eventos_carreira": eventos,
                "matriz_habilidades": habilidades,
                "metas_carreira": metas,
                "certificacoes": certificacoes,
                "mentoria": mentoria,
                "metricas": metricas,
            }

            return processed_data

        except Exception as e:
            self.logger.error(f"Error processing career data for {person_id}: {e}")
            return {
                "id": person_id,
                "year": year,
                "has_career_data": False,
                "error": str(e),
            }

    def _calculate_career_metrics(
        self,
        eventos: List[Dict[str, Any]],
        habilidades: Dict[str, int],
        certificacoes: List[Dict[str, Any]],
        metas: List[Dict[str, Any]],
        mentoria: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Calculate career metrics from career progression data.

        Args:
            eventos: List of career events
            habilidades: Dictionary mapping skill names to proficiency levels
            certificacoes: List of certifications
            metas: List of career goals
            mentoria: List of mentorship relationships

        Returns:
            Dictionary with calculated metrics
        """
        metricas = {}

        # Process promotion events
        promocoes = [e for e in eventos if e.get("tipo_evento") == "promotion"]

        # Calculate time since last promotion
        if promocoes:
            # Sort promotions by date
            promocoes.sort(key=lambda x: x.get("data", ""))
            ultima_promocao = promocoes[-1].get("data", "")

            if ultima_promocao:
                try:
                    data_promocao = datetime.strptime(
                        ultima_promocao, "%Y-%m-%d"
                    ).date()
                    metricas["dias_ultima_promocao"] = (
                        datetime.now().date() - data_promocao
                    ).days
                    metricas["meses_ultima_promocao"] = (
                        metricas["dias_ultima_promocao"] / 30.44
                    )  # Average days per month
                except:
                    pass

        # Calculate promotion velocity
        if len(promocoes) >= 2:
            try:
                # Sort by date
                promocoes.sort(key=lambda x: x.get("data", ""))

                # Calculate all intervals
                intervalos = []
                for i in range(1, len(promocoes)):
                    data_anterior = datetime.strptime(
                        promocoes[i - 1].get("data", ""), "%Y-%m-%d"
                    ).date()
                    data_atual = datetime.strptime(
                        promocoes[i].get("data", ""), "%Y-%m-%d"
                    ).date()
                    dias = (data_atual - data_anterior).days
                    intervalos.append(dias)

                # Calculate average
                if intervalos:
                    metricas["media_dias_entre_promocoes"] = sum(intervalos) / len(
                        intervalos
                    )
                    metricas["media_anos_entre_promocoes"] = (
                        metricas["media_dias_entre_promocoes"] / 365.25
                    )
            except:
                pass

        # Process skill metrics
        if habilidades:
            valores = list(habilidades.values())
            metricas["total_habilidades"] = len(habilidades)
            metricas["media_habilidades"] = sum(valores) / len(valores)
            metricas["max_habilidade"] = max(valores)
            metricas["min_habilidade"] = min(valores)

            # Calculate distribution
            distribuicao = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for nivel in valores:
                distribuicao[nivel] = distribuicao.get(nivel, 0) + 1

            metricas["distribuicao_habilidades"] = {
                "nivel_1": distribuicao.get(1, 0),
                "nivel_2": distribuicao.get(2, 0),
                "nivel_3": distribuicao.get(3, 0),
                "nivel_4": distribuicao.get(4, 0),
                "nivel_5": distribuicao.get(5, 0),
            }

            # Calculate skill acquisition rate
            skill_events = [
                e for e in eventos if e.get("tipo_evento") == "skill_acquisition"
            ]
            if len(skill_events) >= 2:
                try:
                    # Get earliest and latest skill events
                    skill_events.sort(key=lambda x: x.get("data", ""))
                    primeiro = datetime.strptime(
                        skill_events[0].get("data", ""), "%Y-%m-%d"
                    ).date()
                    ultimo = datetime.strptime(
                        skill_events[-1].get("data", ""), "%Y-%m-%d"
                    ).date()
                    dias_total = (ultimo - primeiro).days

                    if dias_total > 0:
                        metricas["taxa_aquisicao_habilidades_anual"] = (
                            len(skill_events) / dias_total
                        ) * 365.25
                except:
                    pass

        # Process certification metrics
        if certificacoes:
            metricas["total_certificacoes"] = len(certificacoes)

            # Check how many are active
            hoje = datetime.now().date()
            ativas = 0
            for cert in certificacoes:
                expiracao = cert.get("expiry_date")
                if not expiracao:
                    ativas += 1
                else:
                    try:
                        data_expiracao = datetime.strptime(expiracao, "%Y-%m-%d").date()
                        if data_expiracao >= hoje:
                            ativas += 1
                    except:
                        ativas += 1  # Count as active if date parsing fails

            metricas["certificacoes_ativas"] = ativas

            # Calculate certification acquisition rate
            if len(certificacoes) >= 2:
                try:
                    # Sort by date obtained
                    sorted_certs = sorted(
                        certificacoes, key=lambda x: x.get("date_obtained", "")
                    )
                    primeiro = datetime.strptime(
                        sorted_certs[0].get("date_obtained", ""), "%Y-%m-%d"
                    ).date()
                    ultimo = datetime.strptime(
                        sorted_certs[-1].get("date_obtained", ""), "%Y-%m-%d"
                    ).date()
                    dias_total = (ultimo - primeiro).days

                    if dias_total > 0:
                        metricas["taxa_aquisicao_certificacoes_anual"] = (
                            len(certificacoes) / dias_total
                        ) * 365.25
                except:
                    pass

        # Process career goals metrics
        if metas:
            metricas["total_metas"] = len(metas)
            metricas["metas_concluidas"] = len(
                [m for m in metas if m.get("status") == "completed"]
            )
            metricas["metas_em_andamento"] = len(
                [m for m in metas if m.get("status") == "in_progress"]
            )
            metricas["metas_nao_iniciadas"] = len(
                [m for m in metas if m.get("status") == "not_started"]
            )
            metricas["metas_atrasadas"] = len(
                [m for m in metas if m.get("status") == "delayed"]
            )

            if metricas["total_metas"] > 0:
                metricas["taxa_conclusao_metas"] = (
                    metricas["metas_concluidas"] / metricas["total_metas"] * 100
                )

        # Process mentorship metrics
        if mentoria:
            metricas["total_mentorias"] = len(mentoria)
            metricas["mentorias_ativas"] = len(
                [m for m in mentoria if m.get("active", False)]
            )

            # Calculate average mentorship duration
            duracoes = []
            for mentor in mentoria:
                try:
                    inicio = datetime.strptime(
                        mentor.get("start_date", ""), "%Y-%m-%d"
                    ).date()

                    if mentor.get("active", False):
                        # Still active, use current date
                        fim = datetime.now().date()
                    else:
                        # Use end date
                        fim = datetime.strptime(
                            mentor.get("end_date", ""), "%Y-%m-%d"
                        ).date()

                    dias = (fim - inicio).days
                    duracoes.append(dias)
                except:
                    pass

            if duracoes:
                metricas["media_dias_mentoria"] = sum(duracoes) / len(duracoes)
                metricas["media_meses_mentoria"] = (
                    metricas["media_dias_mentoria"] / 30.44
                )

        # Calculate overall growth score (0-100)
        growth_score = 0

        # Component 1: Promotion velocity (lower is better) - max 25 points
        if "media_anos_entre_promocoes" in metricas:
            anos = metricas["media_anos_entre_promocoes"]
            if anos <= 1:
                growth_score += 25
            elif anos <= 2:
                growth_score += 20
            elif anos <= 3:
                growth_score += 15
            elif anos <= 4:
                growth_score += 10
            else:
                growth_score += 5

        # Component 2: Skill level - max 25 points
        if "media_habilidades" in metricas:
            growth_score += (
                metricas["media_habilidades"] * 5
            )  # 1-5 scale becomes 5-25 points

        # Component 3: Certifications - max 20 points
        if "total_certificacoes" in metricas:
            growth_score += min(20, metricas["total_certificacoes"] * 5)

        # Component 4: Goal completion rate - max 15 points
        if "taxa_conclusao_metas" in metricas:
            growth_score += metricas["taxa_conclusao_metas"] * 0.15

        # Component 5: Active mentorships - max 15 points
        if "mentorias_ativas" in metricas:
            growth_score += min(15, metricas["mentorias_ativas"] * 7.5)

        # Enhanced components for high-performance teams

        # Component 6: Skill diversity - max 10 points
        if len(habilidades) > 0:
            # Calculate skill categories
            categorias = {}
            for skill_name in habilidades:
                categoria = (
                    skill_name.split(".")[0] if "." in skill_name else "technical"
                )
                if categoria not in categorias:
                    categorias[categoria] = 0
                categorias[categoria] += 1

            # More categories with at least 2 skills is better
            categorias_relevantes = len(
                [c for c, count in categorias.items() if count >= 2]
            )
            growth_score += min(10, categorias_relevantes * 2)
            metricas["diversidade_habilidades"] = categorias_relevantes

        # Component 7: Skill acquisition rate - max 10 points
        if (
            "taxa_aquisicao_habilidades" in metricas
            and metricas["taxa_aquisicao_habilidades"] > 0
        ):
            # More skills per year is better (cap at 5 skills per year for max score)
            growth_score += min(10, metricas["taxa_aquisicao_habilidades"] * 2)

        # Component 8: Leadership potential - max 10 points
        leadership_score = 0

        # Check for leadership skills
        leadership_skills = [
            s
            for s in habilidades.keys()
            if "lideranca" in s.lower() or "leadership" in s.lower()
        ]
        if leadership_skills:
            avg_leadership = sum(habilidades[s] for s in leadership_skills) / len(
                leadership_skills
            )
            leadership_score += min(5, avg_leadership)

        # Check for mentoring others
        if "mentor_para_outros" in metricas:
            leadership_score += min(5, metricas["mentor_para_outros"] * 2.5)

        growth_score += leadership_score
        metricas["potencial_lideranca"] = leadership_score

        # Component 9: Collaborative growth - max 10 points
        collaborative_score = 0

        # Check for collaborative events (presentations, knowledge sharing, etc.)
        collaborative_events = [
            e
            for e in eventos
            if "compartilhamento" in e.get("detalhes", "").lower()
            or "apresentacao" in e.get("detalhes", "").lower()
            or "sharing" in e.get("detalhes", "").lower()
            or "presentation" in e.get("detalhes", "").lower()
            or "workshop" in e.get("detalhes", "").lower()
        ]

        collaborative_score += min(5, len(collaborative_events) * 1.25)

        # Check for cross-functional skills/experiences
        cross_functional = len(
            set(
                [
                    e.get("tipo_evento")
                    for e in eventos
                    if e.get("tipo_evento") in ["lateral_move", "role_change"]
                ]
            )
        )
        collaborative_score += min(5, cross_functional * 2.5)

        growth_score += collaborative_score
        metricas["crescimento_colaborativo"] = collaborative_score

        # Calculate high performer index (0-100) - adds separate metric without changing existing growth score
        high_performer_index = 0

        # Technical excellence (30%)
        if "media_habilidades" in metricas:
            high_performer_index += metricas["media_habilidades"] * 6  # max 30 points

        # Learning velocity (20%)
        learning_velocity = 0
        if (
            "taxa_aquisicao_habilidades" in metricas
            and metricas["taxa_aquisicao_habilidades"] > 0
        ):
            learning_velocity += min(10, metricas["taxa_aquisicao_habilidades"] * 2)
        if "total_certificacoes" in metricas:
            learning_velocity += min(10, metricas["total_certificacoes"] * 2.5)
        high_performer_index += learning_velocity

        # Leadership & influence (20%)
        high_performer_index += min(20, leadership_score * 2)

        # Execution & reliability (30%)
        execution_score = 0
        if "taxa_conclusao_metas" in metricas:
            execution_score += metricas["taxa_conclusao_metas"] * 0.3  # max 30 points
        else:
            # Default score if no goals tracked
            execution_score += 15
        high_performer_index += execution_score

        metricas["high_performer_index"] = min(100, high_performer_index)

        # Final growth score - original scale
        metricas["growth_score"] = min(100, growth_score)

        return metricas

    def generate_team_development_report(self) -> Optional[Path]:
        """Generate a team development report based on career progression data.

        Analyzes career progression data for all team members and provides recommendations
        for building a high-performance team, including role suggestions, skill gaps,
        and team composition recommendations.

        Returns:
            Path to the generated report or None if no data is available
        """
        try:
            # Create team development directory
            team_dev_dir = self.base_path / "team_development"
            team_dev_dir.mkdir(exist_ok=True, parents=True)

            # Get all career progression data
            career_data = {}
            career_dir = self.base_path / "career_progression"

            if not career_dir.exists():
                return None

            # Load all career data files
            for file in career_dir.glob("*.json"):
                person_name = file.stem
                with open(file, "r", encoding="utf-8") as f:
                    person_data = json.load(f)

                # Calculate metrics if they don't exist
                if "metricas" not in person_data:
                    # Extract components
                    eventos = person_data.get("eventos_carreira", [])
                    habilidades = person_data.get("matriz_habilidades", {})
                    certificacoes = person_data.get("certificacoes", [])
                    metas = person_data.get("metas_carreira", [])
                    mentoria = person_data.get("mentoria", [])

                    # Calculate metrics
                    metricas = self._calculate_career_metrics(
                        eventos, habilidades, certificacoes, metas, mentoria
                    )
                    person_data["metricas"] = metricas

                career_data[person_name] = person_data

            if not career_data:
                return None

            # Create the team analysis
            current_time = datetime.now()
            report_path = (
                team_dev_dir
                / f"team_development_{current_time.strftime('%Y%m%d_%H%M%S')}.md"
            )

            # Generate report content
            content = self._generate_team_development_content(career_data)

            # Write report to file
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(content)

            return report_path

        except Exception as e:
            print(f"Error generating team development report: {e}")
            return None

    def _generate_team_development_content(
        self, career_data: Dict[str, Dict[str, Any]]
    ) -> str:
        """Generate content for team development report.

        Args:
            career_data: Dictionary mapping person names to their career data

        Returns:
            String with report content
        """
        # Start with report header
        current_time = datetime.now()
        content = f"""# Relatório de Desenvolvimento de Equipe de Alta Performance
Data: {current_time.strftime("%d/%m/%Y")}

## Visão Geral da Equipe

Total de membros analisados: {len(career_data)}

"""

        # Analyze high performer distribution
        high_performers = []
        solid_performers = []
        developing_performers = []

        for person, data in career_data.items():
            metricas = data.get("metricas", {})
            high_performer_index = metricas.get("high_performer_index", 0)

            if high_performer_index >= 75:
                high_performers.append((person, high_performer_index))
            elif high_performer_index >= 60:
                solid_performers.append((person, high_performer_index))
            else:
                developing_performers.append((person, high_performer_index))

        # Sort each list by score (descending)
        high_performers.sort(key=lambda x: x[1], reverse=True)
        solid_performers.sort(key=lambda x: x[1], reverse=True)
        developing_performers.sort(key=lambda x: x[1], reverse=True)

        # Add distribution summary
        content += f"""### Distribuição de Performers

- **High Performers ({len(high_performers)})**: {", ".join([p[0] for p in high_performers]) if high_performers else "Nenhum"}
- **Performers Sólidos ({len(solid_performers)})**: {", ".join([p[0] for p in solid_performers]) if solid_performers else "Nenhum"}
- **Performers em Desenvolvimento ({len(developing_performers)})**: {", ".join([p[0] for p in developing_performers]) if developing_performers else "Nenhum"}

"""

        # Analyze team skill composition
        all_skills = {}
        skill_levels = {}

        for person, data in career_data.items():
            habilidades = data.get("matriz_habilidades", {})

            for skill, level in habilidades.items():
                # Extract category if available
                category = skill.split(".")[0] if "." in skill else skill

                if category not in all_skills:
                    all_skills[category] = 0
                    skill_levels[category] = []

                all_skills[category] += 1
                skill_levels[category].append(level)

        # Calculate average level for each skill category
        avg_skill_levels = {}
        for category, levels in skill_levels.items():
            if levels:
                avg_skill_levels[category] = sum(levels) / len(levels)
            else:
                avg_skill_levels[category] = 0

        # Sort skill categories by count (descending)
        sorted_skills = sorted(all_skills.items(), key=lambda x: x[1], reverse=True)

        # Add skill composition
        content += """## Composição de Habilidades da Equipe

| Categoria | Quantidade | Nível Médio | Status |
|-----------|------------|-------------|--------|
"""

        for category, count in sorted_skills:
            avg_level = avg_skill_levels.get(category, 0)

            # Determine status
            if avg_level >= 4.0:
                status = "🟢 Excelente"
            elif avg_level >= 3.0:
                status = "🟡 Bom"
            else:
                status = "🔴 Necessita Desenvolvimento"

            content += f"| {category} | {count} | {avg_level:.1f} | {status} |\n"

        # Identify skill gaps
        content += "\n### Lacunas de Habilidades Identificadas\n\n"

        if avg_skill_levels:
            weak_skills = [
                category for category, avg in avg_skill_levels.items() if avg < 3.0
            ]

            if weak_skills:
                content += (
                    "As seguintes áreas de habilidades precisam de desenvolvimento:\n\n"
                )
                for skill in weak_skills:
                    content += (
                        f"- **{skill}**: Nível médio {avg_skill_levels[skill]:.1f}/5\n"
                    )
            else:
                content += "Não foram identificadas lacunas significativas de habilidades na equipe.\n"
        else:
            content += "Dados insuficientes para análise de lacunas de habilidades.\n"

        # Team roles analysis
        content += "\n## Análise de Papéis na Equipe\n\n"

        # Identify potential roles based on metrics
        tech_leads = []
        specialists = []
        integrators = []
        innovators = []

        for person, data in career_data.items():
            metricas = data.get("metricas", {})
            avg_skill = metricas.get("media_habilidades", 0)
            leadership = metricas.get("potencial_lideranca", 0)
            collab = metricas.get("crescimento_colaborativo", 0)
            skill_acquisition = metricas.get("taxa_aquisicao_habilidades", 0)

            if avg_skill >= 4 and leadership >= 7:
                tech_leads.append((person, leadership))
            elif avg_skill >= 4 and collab <= 5:
                specialists.append((person, avg_skill))
            elif avg_skill >= 3.5 and collab >= 7:
                integrators.append((person, collab))
            elif skill_acquisition and skill_acquisition >= 3:
                innovators.append((person, skill_acquisition))

        # Sort each list
        tech_leads.sort(key=lambda x: x[1], reverse=True)
        specialists.sort(key=lambda x: x[1], reverse=True)
        integrators.sort(key=lambda x: x[1], reverse=True)
        innovators.sort(key=lambda x: x[1], reverse=True)

        # Add role distribution
        content += """A equipe possui os seguintes papéis potenciais:

"""

        if tech_leads:
            content += f"- **Tech Leads/Líderes Técnicos**: {', '.join([p[0] for p in tech_leads])}\n"
        if specialists:
            content += f"- **Especialistas Técnicos**: {', '.join([p[0] for p in specialists])}\n"
        if integrators:
            content += f"- **Integradores/Facilitadores**: {', '.join([p[0] for p in integrators])}\n"
        if innovators:
            content += f"- **Inovadores/Early Adopters**: {', '.join([p[0] for p in innovators])}\n"

        if not (tech_leads or specialists or integrators or innovators):
            content += (
                "Dados insuficientes para identificar papéis potenciais na equipe.\n"
            )

        # Team balance analysis
        content += "\n### Análise de Balanceamento da Equipe\n\n"

        has_tech_leadership = len(tech_leads) > 0
        has_specialists = len(specialists) >= 2  # At least 2 specialists
        has_integrators = len(integrators) > 0
        has_innovators = len(innovators) > 0

        if (
            has_tech_leadership
            and has_specialists
            and has_integrators
            and has_innovators
        ):
            content += "✅ **Equipe Bem Balanceada**: A equipe possui uma boa distribuição de papéis, com líderes técnicos, especialistas, integradores e inovadores.\n"
        else:
            content += "⚠️ **Oportunidades de Balanceamento**:\n\n"

            if not has_tech_leadership:
                content += "- **Necessidade de Liderança Técnica**: A equipe pode se beneficiar de membros com maior capacidade de liderança técnica.\n"
            if not has_specialists:
                content += "- **Necessidade de Especialistas**: A equipe pode precisar desenvolver ou contratar mais especialistas técnicos.\n"
            if not has_integrators:
                content += "- **Necessidade de Integradores**: A equipe pode se beneficiar de membros com maior foco em colaboração e integração.\n"
            if not has_innovators:
                content += "- **Necessidade de Inovadores**: A equipe pode precisar de membros com maior foco em aprendizado e adoção de novas tecnologias.\n"

        # Team development recommendations
        content += (
            "\n## Recomendações para Desenvolvimento de Equipe de Alta Performance\n\n"
        )

        # General recommendations
        content += """### Recomendações Gerais

1. **Cultura de Feedback Contínuo**: Implementar ciclos de feedback mais curtos e frequentes para acelerar o desenvolvimento.
2. **Desenvolvimento de Liderança Distribuída**: Criar oportunidades para que diferentes membros da equipe liderem iniciativas específicas.
3. **Aprendizado Colaborativo**: Estabelecer sessões regulares de compartilhamento de conhecimento, como tech talks ou workshops internos.
4. **Clareza nos Roteiros de Carreira**: Assegurar que todos os membros da equipe tenham clareza sobre seus caminhos de desenvolvimento.
5. **Experimentação e Inovação**: Reservar tempo para experimentação e exploração de novas tecnologias ou abordagens.

"""

        # Specific recommendations based on team analysis
        content += "### Recomendações Específicas\n\n"

        # Add recommendations based on team composition
        recommendations = []

        # Check team balance
        if not has_tech_leadership:
            recommendations.append(
                "**Desenvolver Liderança Técnica**: Identificar membros com potencial de liderança e oferecer oportunidades de desenvolvimento através de mentoria, cursos especializados e responsabilidades incrementais em projetos."
            )

        if not has_integrators:
            recommendations.append(
                "**Fomentar Colaboração Cross-Funcional**: Implementar projetos que exijam colaboração entre diferentes especialidades e reconhecer explicitamente contribuições colaborativas."
            )

        if not has_innovators:
            recommendations.append(
                "**Estimular Cultura de Aprendizado**: Estabelecer comunidades de prática, clubes de estudo ou tempo dedicado para exploração de novas tecnologias."
            )

        # Check skill gaps
        if avg_skill_levels:
            weak_skills = [
                category for category, avg in avg_skill_levels.items() if avg < 3.0
            ]
            if weak_skills:
                skill_recommendations = f"**Desenvolvimento de Habilidades em {', '.join(weak_skills)}**: Organizar treinamentos focados, contratar especialistas ou estabelecer parcerias para desenvolvimento dessas habilidades."
                recommendations.append(skill_recommendations)

        # Check high performer distribution
        high_performer_ratio = (
            len(high_performers) / len(career_data) if career_data else 0
        )
        if high_performer_ratio < 0.2:  # Less than 20% high performers
            recommendations.append(
                "**Elevação de Performance**: Implementar programas específicos para identificar e desenvolver potenciais high performers, como programas de aceleração e mentoria com líderes experientes."
            )

        # Add recommendations to report
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                content += f"{i}. {rec}\n\n"
        else:
            content += "Dados insuficientes para gerar recomendações específicas.\n"

        # Implementation roadmap
        content += """## Roteiro de Implementação

1. **Curto Prazo (1-3 meses)**
   - Realizar workshops para alinhar expectativas e definir objetivos claros de desenvolvimento
   - Iniciar programas de mentoria internos
   - Estabelecer rituais de compartilhamento de conhecimento

2. **Médio Prazo (3-6 meses)**
   - Implementar iniciativas de desenvolvimento focadas nas lacunas identificadas
   - Revisar e ajustar estruturas de equipe para melhor aproveitamento dos perfis
   - Criar sistemas de reconhecimento alinhados às competências desejadas

3. **Longo Prazo (6-12 meses)**
   - Avaliar o progresso e ajustar estratégias de desenvolvimento
   - Expandir programas bem-sucedidos e descontinuar os ineficazes
   - Desenvolver roteiros de carreira personalizados baseados no desenvolvimento observado

---

*Este relatório foi gerado automaticamente baseado na análise de dados de progressão de carreira. As recomendações devem ser adaptadas ao contexto específico da organização.*
"""

        return content

    def load_performance_evaluations(self, person_id: str) -> Dict[str, float]:
        """
        Load performance evaluations for a person.

        Args:
            person_id: ID of the person

        Returns:
            Dictionary mapping periods to performance values
        """
        # Check if the person exists in career data
        career_path = os.path.join(
            self.base_path, "career_progression", f"{person_id}.json"
        )

        if not os.path.exists(career_path):
            return {}

        try:
            with open(career_path, "r", encoding="utf-8") as f:
                career_data = json.load(f)

            # Extract nine_box performance if available
            performance = {}

            if "nine_box" in career_data and "performance" in career_data["nine_box"]:
                # Get date or use current quarter as default
                date_str = career_data["nine_box"].get(
                    "date", datetime.now().strftime("%Y-%m-%d")
                )
                date = datetime.strptime(date_str, "%Y-%m-%d")
                period = f"{date.year}-Q{(date.month - 1) // 3 + 1}"

                performance[period] = career_data["nine_box"]["performance"]

            return performance

        except Exception as e:
            print(f"Error loading performance data for {person_id}: {str(e)}")
            return {}

    def load_potential_assessments(self, person_id: str) -> Dict[str, float]:
        """
        Load potential assessments for a person.

        Args:
            person_id: ID of the person

        Returns:
            Dictionary mapping periods to potential values
        """
        # Check if the person exists in career data
        career_path = os.path.join(
            self.base_path, "career_progression", f"{person_id}.json"
        )

        if not os.path.exists(career_path):
            return {}

        try:
            with open(career_path, "r", encoding="utf-8") as f:
                career_data = json.load(f)

            # Extract nine_box potential if available
            potential = {}

            if "nine_box" in career_data and "potential" in career_data["nine_box"]:
                # Get date or use current quarter as default
                date_str = career_data["nine_box"].get(
                    "date", datetime.now().strftime("%Y-%m-%d")
                )
                date = datetime.strptime(date_str, "%Y-%m-%d")
                period = f"{date.year}-Q{(date.month - 1) // 3 + 1}"

                potential[period] = career_data["nine_box"]["potential"]

            return potential

        except Exception as e:
            print(f"Error loading potential data for {person_id}: {str(e)}")
            return {}

    def save_nine_box_position(self, position_data: Dict[str, Any]) -> bool:
        """
        Save a nine-box position for a person.

        Args:
            position_data: Dictionary with position data

        Returns:
            Boolean indicating success
        """
        person_id = position_data.get("person_id")
        if not person_id:
            print("Error: Missing person_id in position data")
            return False

        # Check if the person exists in career data
        career_path = os.path.join(
            self.base_path, "career_progression", f"{person_id}.json"
        )

        career_data = {}
        if os.path.exists(career_path):
            try:
                with open(career_path, "r", encoding="utf-8") as f:
                    career_data = json.load(f)
            except Exception as e:
                print(f"Error reading career data for {person_id}: {str(e)}")
                return False
        else:
            # Create new career data
            career_data = {
                "nome": person_id,
                "cargo_atual": position_data.get("position", "Unknown"),
                "matriz_habilidades": {},
                "eventos_carreira": [],
                "metas_carreira": [],
                "certificacoes": [],
                "mentoria": [],
            }

        # Update nine_box data
        career_data["nine_box"] = {
            "performance": position_data.get("performance", 5.0),
            "potential": position_data.get("potential", 5.0),
            "date": position_data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "quadrant": position_data.get("quadrant_name", "Unknown"),
        }

        # Save updated career data
        try:
            os.makedirs(os.path.dirname(career_path), exist_ok=True)
            with open(career_path, "w", encoding="utf-8") as f:
                json.dump(career_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving career data for {person_id}: {str(e)}")
            return False
