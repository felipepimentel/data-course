#!/usr/bin/env python3
"""
Structure Adapter para o People Analytics.

Este módulo permite que o sistema funcione com estruturas de diretório invertidas:
- Estrutura esperada: <ano>/<pessoa>/resultado.json
- Estrutura atual: <pessoa>/<ano>/resultado.json

Fornece duas soluções:
1. Uma classe adaptadora que trabalha com a estrutura invertida
2. Uma função para converter a estrutura atual para a esperada
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Set, Any

from peopleanalytics.analyzer import EvaluationAnalyzer
from peopleanalytics.data_pipeline import DataPipeline


class InvertedStructureAnalyzer(EvaluationAnalyzer):
    """Versão adaptada do EvaluationAnalyzer que funciona com estrutura invertida."""
    
    def __init__(self, base_path: str):
        """Inicializa o analisador com estrutura invertida.
        
        Args:
            base_path: Caminho para a base de dados com estrutura <pessoa>/<ano>/
        """
        super().__init__(base_path)
        # Forçar nova carga para garantir compatibilidade
        self.evaluations_by_person = {}
        self.load_all_evaluations_inverted()
        
    def load_all_evaluations_inverted(self):
        """Carrega avaliações da estrutura invertida <pessoa>/<ano>/resultado.json"""
        if not self.base_path.exists():
            return
            
        # Primeiro nível são pessoas (não anos como na estrutura original)
        for person_dir in self.base_path.iterdir():
            if not person_dir.is_dir():
                continue

            person_name = person_dir.name

            # Segundo nível são anos (não pessoas como na estrutura original)
            for year_dir in person_dir.iterdir():
                if not year_dir.is_dir():
                    continue
                    
                year = year_dir.name
                
                # Procura por arquivos JSON neste diretório
                json_files = list(year_dir.glob("*.json"))
                if not json_files:
                    continue
                    
                # Processa todos os arquivos JSON encontrados
                for json_file in json_files:
                    try:
                        with open(json_file, "r", encoding="utf-8") as f:
                            try:
                                data = json.load(f)
                                # Inicializa os dados do ano se ainda não existirem
                                if person_name not in self.evaluations_by_person:
                                    self.evaluations_by_person[person_name] = {}
                                    
                                if year not in self.evaluations_by_person[person_name]:
                                    self.evaluations_by_person[person_name][year] = {
                                        "success": True,
                                        "data": data
                                    }
                            except json.JSONDecodeError as e:
                                # Mensagem de erro mais detalhada
                                relative_path = json_file.relative_to(self.base_path)
                                print(f"Erro ao decodificar JSON de {relative_path}: {str(e)}")
                                
                                # Inicializa com estrutura vazia mas válida
                                if person_name not in self.evaluations_by_person:
                                    self.evaluations_by_person[person_name] = {}
                                    
                                if year not in self.evaluations_by_person[person_name]:
                                    self.evaluations_by_person[person_name][year] = {
                                        "success": False, 
                                        "data": {}
                                    }
                    except Exception as e:
                        # Captura outros erros potenciais
                        relative_path = json_file.relative_to(self.base_path)
                        print(f"Erro ao ler arquivo {relative_path}: {str(e)}")
    
    def analyze_person(self, person: str, year: str) -> Dict[str, Any]:
        """Analisa os dados de uma pessoa em um ano específico.
        
        Args:
            person: Nome da pessoa
            year: Ano a analisar
            
        Returns:
            Dicionário com dados de análise
        """
        if person not in self.evaluations_by_person:
            return {"success": False, "error": f"Pessoa '{person}' não encontrada"}
            
        if year not in self.evaluations_by_person[person]:
            return {"success": False, "error": f"Ano '{year}' não encontrado para '{person}'"}
            
        evaluation = self.evaluations_by_person[person][year]
        if not evaluation["success"]:
            return {"success": False, "error": "Dados de avaliação inválidos"}
            
        # Retorna os dados com sucesso
        return {
            "success": True,
            "data": evaluation["data"]
        }


class InvertedStructurePipeline(DataPipeline):
    """Versão adaptada do DataPipeline que funciona com estrutura invertida."""
    
    def restructure_file_path(self, file_path: str, person: str, year: str) -> str:
        """Converte o caminho de arquivo para a estrutura esperada.
        
        Args:
            file_path: Caminho original do arquivo
            person: Nome da pessoa
            year: Ano da avaliação
            
        Returns:
            Caminho convertido para a estrutura <ano>/<pessoa>/
        """
        # Cria diretório se não existir
        target_dir = os.path.join(self.base_path, year, person)
        os.makedirs(target_dir, exist_ok=True)
        
        # Determina o nome do arquivo de destino
        filename = os.path.basename(file_path)
        target_path = os.path.join(target_dir, filename)
        
        return target_path
    
    def ingest_file_inverted(self, file_path: str, year: str = None, 
                           person: str = None, overwrite: bool = False) -> Dict[str, Any]:
        """Importa um arquivo com estrutura invertida.
        
        Args:
            file_path: Caminho para o arquivo a importar
            year: Sobrescreve o ano (opcional)
            person: Sobrescreve a pessoa (opcional)
            overwrite: Se deve sobrescrever dados existentes
            
        Returns:
            Dicionário com informações de status
        """
        try:
            # Extrai pessoa e ano do caminho do arquivo se não fornecidos
            if not person or not year:
                parts = os.path.normpath(file_path).split(os.sep)
                if len(parts) >= 3:
                    # Estrutura: <pessoa>/<ano>/resultado.json
                    potential_year = parts[-2]  # Penúltimo componente é o ano
                    potential_person = parts[-3]  # Antepenúltimo componente é a pessoa
                    
                    year = year or potential_year
                    person = person or potential_person
            
            # Chama a função de importação original mas com os argumentos invertidos
            return super().ingest_file(file_path, person=year, year=person, overwrite=overwrite)
            
        except Exception as e:
            return {
                'success': False,
                'file': file_path,
                'error': f'Erro inesperado: {str(e)}',
                'error_type': 'unexpected'
            }


def convert_structure(source_dir: str, target_dir: str, overwrite: bool = False) -> Dict[str, int]:
    """Converte a estrutura <pessoa>/<ano>/ para <ano>/<pessoa>/.
    
    Args:
        source_dir: Diretório de origem com estrutura <pessoa>/<ano>/
        target_dir: Diretório de destino para estrutura <ano>/<pessoa>/
        overwrite: Se deve sobrescrever arquivos existentes
        
    Returns:
        Dicionário com contagens de sucessos e falhas
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    if not source_path.exists():
        return {'success': 0, 'failed': 0, 'total': 0, 'error': 'Diretório de origem não existe'}
    
    # Cria o diretório de destino se não existir
    os.makedirs(target_path, exist_ok=True)
    
    success_count = 0
    failed_count = 0
    error_details = []
    
    # Primeiro nível: pessoas
    for person_dir in source_path.iterdir():
        if not person_dir.is_dir():
            continue
            
        person_name = person_dir.name
        
        # Segundo nível: anos
        for year_dir in person_dir.iterdir():
            if not year_dir.is_dir():
                continue
                
            year = year_dir.name
            
            # Diretório de destino com estrutura invertida
            dest_dir = target_path / year / person_name
            os.makedirs(dest_dir, exist_ok=True)
            
            # Copia todos os arquivos JSON
            for json_file in year_dir.glob("*.json"):
                dest_file = dest_dir / json_file.name
                
                try:
                    if not dest_file.exists() or overwrite:
                        shutil.copy2(json_file, dest_file)
                        success_count += 1
                    else:
                        failed_count += 1
                        error_details.append({
                            'file': str(json_file),
                            'error': 'Arquivo já existe e overwrite=False',
                            'error_type': 'exists'
                        })
                except Exception as e:
                    failed_count += 1
                    error_details.append({
                        'file': str(json_file),
                        'error': str(e),
                        'error_type': 'unexpected'
                    })
    
    return {
        'success': success_count,
        'failed': failed_count,
        'total': success_count + failed_count,
        'error_details': error_details
    }


def create_symlinks(source_dir: str, target_dir: str) -> Dict[str, int]:
    """Cria links simbólicos invertendo a estrutura sem duplicar dados.
    
    Args:
        source_dir: Diretório de origem com estrutura <pessoa>/<ano>/
        target_dir: Diretório de destino para estrutura <ano>/<pessoa>/
        
    Returns:
        Dicionário com contagens de sucessos e falhas
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    if not source_path.exists():
        return {'success': 0, 'failed': 0, 'total': 0, 'error': 'Diretório de origem não existe'}
    
    # Cria o diretório de destino se não existir
    os.makedirs(target_path, exist_ok=True)
    
    success_count = 0
    failed_count = 0
    error_details = []
    
    # Primeiro nível: pessoas
    for person_dir in source_path.iterdir():
        if not person_dir.is_dir():
            continue
            
        person_name = person_dir.name
        
        # Segundo nível: anos
        for year_dir in person_dir.iterdir():
            if not year_dir.is_dir():
                continue
                
            year = year_dir.name
            
            # Diretório de destino com estrutura invertida
            dest_dir = target_path / year / person_name
            os.makedirs(dest_dir, exist_ok=True)
            
            # Cria links simbólicos para todos os arquivos JSON
            for json_file in year_dir.glob("*.json"):
                dest_file = dest_dir / json_file.name
                
                try:
                    if not dest_file.exists():
                        # Cria um link simbólico para o arquivo original
                        os.symlink(json_file.absolute(), dest_file)
                        success_count += 1
                    else:
                        # Já existe, não precisa fazer nada
                        success_count += 1
                except Exception as e:
                    failed_count += 1
                    error_details.append({
                        'file': str(json_file),
                        'error': str(e),
                        'error_type': 'unexpected'
                    })
    
    return {
        'success': success_count,
        'failed': failed_count,
        'total': success_count + failed_count,
        'error_details': error_details
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Adaptador de estrutura para People Analytics")
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")
    
    # Comando para converter estrutura
    convert_parser = subparsers.add_parser("convert", help="Converte estrutura de diretórios")
    convert_parser.add_argument("--source", required=True, help="Diretório de origem")
    convert_parser.add_argument("--target", required=True, help="Diretório de destino")
    convert_parser.add_argument("--overwrite", action="store_true", help="Sobrescrever arquivos existentes")
    
    # Comando para criar links simbólicos
    symlink_parser = subparsers.add_parser("symlink", help="Cria links simbólicos em vez de copiar")
    symlink_parser.add_argument("--source", required=True, help="Diretório de origem")
    symlink_parser.add_argument("--target", required=True, help="Diretório de destino")
    
    # Comando para testar a adaptação
    test_parser = subparsers.add_parser("test", help="Testa o adaptador")
    test_parser.add_argument("--dir", required=True, help="Diretório a testar")
    
    args = parser.parse_args()
    
    if args.command == "convert":
        print(f"Convertendo estrutura de {args.source} para {args.target}...")
        result = convert_structure(args.source, args.target, args.overwrite)
        print(f"Conversão completa: {result['success']} sucessos, {result['failed']} falhas")
        
    elif args.command == "symlink":
        print(f"Criando links simbólicos de {args.source} para {args.target}...")
        result = create_symlinks(args.source, args.target)
        print(f"Links criados: {result['success']} sucessos, {result['failed']} falhas")
        
    elif args.command == "test":
        print(f"Testando adaptador com diretório {args.dir}...")
        
        # Testa o analisador adaptado
        analyzer = InvertedStructureAnalyzer(args.dir)
        people = analyzer.get_all_people()
        years = analyzer.get_all_years()
        
        print(f"Pessoas encontradas: {', '.join(people)}")
        print(f"Anos encontrados: {', '.join(years)}")
        
        # Testa algumas funções do analisador
        if people and years:
            person = people[0]
            year = years[0]
            print(f"Testando análise para {person} no ano {year}...")
            
            try:
                concept = analyzer.get_conceito_by_year(person)
                print(f"Conceito por ano: {concept}")
            except Exception as e:
                print(f"Erro ao buscar conceito: {e}")
    else:
        parser.print_help() 