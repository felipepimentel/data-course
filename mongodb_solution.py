"""
Solução para análise de dados People Analytics usando MongoDB e Pandas.

Esta implementação:
1. Importa dados de arquivos JSON
2. Armazena-os em uma base MongoDB
3. Realiza análises usando PyMongo e Pandas
4. Gera visualizações com Matplotlib/Seaborn
5. Exporta resultados para a pasta 'output'

Uso:
    python mongodb_solution.py --data_dir ./data --output_dir ./output --db_name people_analytics
"""

import os
import json
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

try:
    import pymongo
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("AVISO: PyMongo não está instalado. Use: pip install pymongo")

# Configuração de estilo para plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("deep")

class MongoDBAnalyzer:
    """Analisador de dados usando MongoDB e Pandas"""
    
    def __init__(self, data_dir: str = 'data', output_dir: str = 'output', 
                 db_name: str = 'people_analytics', host: str = 'localhost', 
                 port: int = 27017):
        """
        Inicializa o analisador
        
        Args:
            data_dir: Diretório contendo os dados JSON
            output_dir: Diretório para salvar os resultados
            db_name: Nome do banco de dados MongoDB
            host: Host do MongoDB
            port: Porta do MongoDB
        """
        if not MONGODB_AVAILABLE:
            raise ImportError("PyMongo não está instalado. Use: pip install pymongo")
        
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        
        # Criar diretório de saída
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Conectar ao MongoDB
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]
        
        # Coleções
        self.people_coll = self.db['people']
        self.evaluations_coll = self.db['evaluations']
        self.behaviors_coll = self.db['behaviors']
        
        # Criar índices
        self._create_indexes()
    
    def _create_indexes(self):
        """Cria índices necessários no MongoDB"""
        # Índice único para pessoas
        self.people_coll.create_index([("name", pymongo.ASCENDING)], unique=True)
        
        # Índice composto para avaliações
        self.evaluations_coll.create_index([
            ("person_id", pymongo.ASCENDING),
            ("year", pymongo.ASCENDING)
        ])
        
        # Índice para caminho do arquivo (único)
        self.evaluations_coll.create_index([("file_path", pymongo.ASCENDING)], unique=True)
        
        # Índice para comportamentos
        self.behaviors_coll.create_index([
            ("evaluation_id", pymongo.ASCENDING),
            ("driver", pymongo.ASCENDING),
            ("behavior", pymongo.ASCENDING)
        ])
    
    def scan_files(self) -> List[Dict]:
        """
        Escaneia o diretório de dados por arquivos JSON
        
        Returns:
            Lista de informações sobre os arquivos encontrados
        """
        file_pattern = "**/*/resultado.json"
        json_files = list(self.data_dir.glob(file_pattern))
        
        # Verificar arquivos já importados
        existing_files = set()
        for doc in self.evaluations_coll.find({}, {"file_path": 1}):
            existing_files.add(doc.get("file_path", ""))
        
        # Filtrar apenas novos arquivos
        new_files = []
        for json_file in json_files:
            file_path = str(json_file.absolute())
            
            if file_path not in existing_files:
                # Extrair informações do caminho
                parts = json_file.parts
                person = parts[-3] if len(parts) >= 3 else "unknown"
                year = parts[-2] if len(parts) >= 2 else "unknown"
                
                new_files.append({
                    'person': person,
                    'year': year,
                    'path': file_path
                })
        
        print(f"Encontrados {len(new_files)} novos arquivos para importar")
        return new_files
    
    def import_data(self) -> int:
        """
        Importa dados dos arquivos JSON para o MongoDB
        
        Returns:
            Número de arquivos importados
        """
        # Escanear arquivos
        new_files = self.scan_files()
        if not new_files:
            return 0
        
        imported_count = 0
        
        for file_info in new_files:
            try:
                # Carregar dados do arquivo
                with open(file_info['path'], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'data' not in data:
                    print(f"Arquivo inválido (sem 'data'): {file_info['path']}")
                    continue
                
                # Extrair dados básicos
                person_name = file_info['person']
                year = file_info['year']
                file_path = file_info['path']
                concept = data['data'].get('conceito_ciclo_filho_descricao', 'Unknown')
                peer_group = data['data'].get('nome_peer_group', 'Unknown')
                
                # Inserir/buscar pessoa
                person_doc = self.people_coll.find_one({"name": person_name})
                if not person_doc:
                    person_id = self.people_coll.insert_one({"name": person_name}).inserted_id
                else:
                    person_id = person_doc["_id"]
                
                # Calcular score médio dos comportamentos
                behaviors_data = []
                total_score = 0
                count = 0
                
                if 'direcionadores' in data['data']:
                    for direcionador in data['data']['direcionadores']:
                        dir_name = direcionador.get('direcionador', 'Desconhecido')
                        
                        if 'comportamentos' in direcionador:
                            for comp in direcionador['comportamentos']:
                                comp_name = comp.get('comportamento', 'Desconhecido')
                                
                                if 'avaliacoes_grupo' in comp:
                                    for aval in comp['avaliacoes_grupo']:
                                        avaliador = aval.get('avaliador', 'Desconhecido')
                                        
                                        if avaliador == '%todos':  # Considerar apenas avaliação geral
                                            freq_colab = aval.get('frequencia_colaborador', [])
                                            freq_grupo = aval.get('frequencia_grupo', [])
                                            
                                            # Calcular scores
                                            score_colab = self._calculate_weighted_score(freq_colab)
                                            score_grupo = self._calculate_weighted_score(freq_grupo)
                                            difference = score_colab - score_grupo
                                            
                                            # Adicionar ao total
                                            total_score += score_colab
                                            count += 1
                                            
                                            behaviors_data.append({
                                                "driver": dir_name,
                                                "behavior": comp_name,
                                                "score": score_colab,
                                                "group_score": score_grupo,
                                                "difference": difference,
                                                "frequencies": freq_colab,
                                                "group_frequencies": freq_grupo
                                            })
                
                # Calcular score médio
                avg_score = total_score / count if count > 0 else 0.0
                
                # Inserir avaliação
                evaluation = {
                    "person_id": person_id,
                    "year": year,
                    "file_path": file_path,
                    "concept": concept,
                    "peer_group": peer_group,
                    "avg_score": avg_score,
                    "import_date": datetime.now(),
                    "data": data  # Armazenar dados completos para referência
                }
                
                evaluation_id = self.evaluations_coll.insert_one(evaluation).inserted_id
                
                # Inserir comportamentos
                for behavior in behaviors_data:
                    behavior_doc = {
                        "evaluation_id": evaluation_id,
                        "driver": behavior["driver"],
                        "behavior": behavior["behavior"],
                        "score": behavior["score"],
                        "group_score": behavior["group_score"],
                        "difference": behavior["difference"],
                        "frequencies": behavior["frequencies"],
                        "group_frequencies": behavior["group_frequencies"]
                    }
                    self.behaviors_coll.insert_one(behavior_doc)
                
                imported_count += 1
                print(f"Importado: {file_path}")
                
            except Exception as e:
                print(f"Erro ao importar {file_info['path']}: {str(e)}")
        
        print(f"Importação concluída: {imported_count} arquivos")
        return imported_count
    
    def _calculate_weighted_score(self, frequencies: List[int]) -> float:
        """
        Calcula score ponderado a partir das frequências
        
        Args:
            frequencies: Lista de frequências [nunca, quase nunca, às vezes, frequentemente, sempre]
            
        Returns:
            Score ponderado (0-4)
        """
        if not frequencies or not isinstance(frequencies, list):
            return 0.0
        
        # Garantir tamanho correto
        weights = [0, 1, 2, 3, 4]  # Pesos para as frequências
        
        if len(frequencies) < len(weights):
            frequencies = list(frequencies) + [0] * (len(weights) - len(frequencies))
        elif len(frequencies) > len(weights):
            frequencies = frequencies[:len(weights)]
            
        # Calcular soma ponderada
        weighted_sum = sum(freq * weight for freq, weight in zip(frequencies, weights))
        total = sum(frequencies)
        
        return weighted_sum / total if total > 0 else 0.0
    
    def analyze_overview(self) -> pd.DataFrame:
        """
        Analisa visão geral das avaliações
        
        Returns:
            DataFrame com visão geral
        """
        # Consulta usando agregação do MongoDB
        pipeline = [
            {
                "$lookup": {
                    "from": "people",
                    "localField": "person_id",
                    "foreignField": "_id",
                    "as": "person"
                }
            },
            {
                "$unwind": "$person"
            },
            {
                "$project": {
                    "_id": 0,
                    "person": "$person.name",
                    "year": 1,
                    "concept": 1,
                    "peer_group": 1,
                    "avg_score": 1,
                    "import_date": 1
                }
            },
            {
                "$sort": {
                    "year": -1,
                    "person": 1
                }
            }
        ]
        
        result = list(self.evaluations_coll.aggregate(pipeline))
        df = pd.DataFrame(result)
        
        if df.empty:
            print("Nenhum dado encontrado para análise de visão geral")
            return df
        
        # Salvar CSV
        output_file = self.output_dir / 'overview_report.csv'
        df.to_csv(output_file, index=False)
        print(f"Relatório de visão geral salvo em: {output_file}")
        
        # Gerar gráfico de evolução por pessoa
        if not df.empty and len(df) > 1:
            plt.figure(figsize=(12, 8))
            pivot_df = df.pivot(index='year', columns='person', values='avg_score')
            ax = pivot_df.plot(kind='line', marker='o')
            
            plt.title('Evolução do Score por Pessoa', fontsize=16)
            plt.xlabel('Ano', fontsize=12)
            plt.ylabel('Score Médio', fontsize=12)
            plt.grid(True)
            plt.legend(title='Pessoa')
            
            # Salvar gráfico
            graph_file = self.output_dir / 'person_evolution.png'
            plt.savefig(graph_file, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Gráfico de evolução salvo em: {graph_file}")
        
        return df
    
    def analyze_behaviors(self) -> pd.DataFrame:
        """
        Analisa comportamentos
        
        Returns:
            DataFrame com análise de comportamentos
        """
        # Consulta usando agregação do MongoDB
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "driver": "$driver",
                        "behavior": "$behavior"
                    },
                    "avg_score": {"$avg": "$score"},
                    "avg_group_score": {"$avg": "$group_score"},
                    "avg_difference": {"$avg": "$difference"},
                    "count": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "driver": "$_id.driver",
                    "behavior": "$_id.behavior",
                    "avg_score": 1,
                    "avg_group_score": 1,
                    "avg_difference": 1,
                    "count": 1
                }
            },
            {
                "$sort": {"avg_difference": -1}
            }
        ]
        
        result = list(self.behaviors_coll.aggregate(pipeline))
        df = pd.DataFrame(result)
        
        if df.empty:
            print("Nenhum dado encontrado para análise de comportamentos")
            return df
        
        # Salvar CSV
        output_file = self.output_dir / 'behaviors_report.csv'
        df.to_csv(output_file, index=False)
        print(f"Relatório de comportamentos salvo em: {output_file}")
        
        # Gerar gráfico de barras dos top comportamentos por diferença
        if not df.empty:
            plt.figure(figsize=(14, 10))
            
            # Top 10 comportamentos por diferença
            top_df = df.nlargest(10, 'avg_difference')
            
            # Criar barras agrupadas
            x = np.arange(len(top_df))
            width = 0.35
            
            fig, ax = plt.subplots(figsize=(14, 10))
            rects1 = ax.bar(x - width/2, top_df['avg_score'], width, label='Colaborador')
            rects2 = ax.bar(x + width/2, top_df['avg_group_score'], width, label='Peer Group')
            
            ax.set_title('Top 10 Comportamentos - Comparação', fontsize=16)
            ax.set_xlabel('Comportamento', fontsize=12)
            ax.set_ylabel('Score Médio', fontsize=12)
            ax.set_xticks(x)
            ax.set_xticklabels([f"{d} - {b[:20]}..." for d, b in zip(top_df['driver'], top_df['behavior'])], 
                               rotation=45, ha='right')
            ax.legend()
            ax.grid(axis='y')
            
            # Adicionar rótulos
            def add_labels(rects):
                for rect in rects:
                    height = rect.get_height()
                    ax.annotate(f'{height:.2f}',
                                xy=(rect.get_x() + rect.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom')
            
            add_labels(rects1)
            add_labels(rects2)
            
            fig.tight_layout()
            
            # Salvar gráfico
            graph_file = self.output_dir / 'top_behaviors.png'
            plt.savefig(graph_file, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Gráfico de top comportamentos salvo em: {graph_file}")
        
        return df
    
    def analyze_drivers(self) -> pd.DataFrame:
        """
        Analisa direcionadores (categorias)
        
        Returns:
            DataFrame com análise de direcionadores
        """
        # Consulta usando agregação do MongoDB
        pipeline = [
            {
                "$group": {
                    "_id": "$driver",
                    "avg_score": {"$avg": "$score"},
                    "avg_group_score": {"$avg": "$group_score"},
                    "avg_difference": {"$avg": "$difference"},
                    "count": {"$sum": 1},
                    "behaviors": {"$addToSet": "$behavior"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "driver": "$_id",
                    "avg_score": 1,
                    "avg_group_score": 1,
                    "avg_difference": 1,
                    "count": 1,
                    "num_behaviors": {"$size": "$behaviors"}
                }
            },
            {
                "$sort": {"avg_difference": -1}
            }
        ]
        
        result = list(self.behaviors_coll.aggregate(pipeline))
        df = pd.DataFrame(result)
        
        if df.empty:
            print("Nenhum dado encontrado para análise de direcionadores")
            return df
        
        # Salvar CSV
        output_file = self.output_dir / 'drivers_report.csv'
        df.to_csv(output_file, index=False)
        print(f"Relatório de direcionadores salvo em: {output_file}")
        
        # Gerar gráfico de radar
        if not df.empty:
            # Preparar dados para gráfico radar
            categories = df['driver']
            N = len(categories)
            
            # Ângulos para cada categoria
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]  # Fechar o círculo
            
            # Valores para colaborador e grupo
            values_collab = df['avg_score'].tolist()
            values_collab += values_collab[:1]  # Fechar o círculo
            
            values_group = df['avg_group_score'].tolist()
            values_group += values_group[:1]  # Fechar o círculo
            
            # Criar figura
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
            
            # Adicionar linhas do gráfico
            ax.plot(angles, values_collab, 'o-', linewidth=2, label='Colaborador')
            ax.plot(angles, values_group, 'o-', linewidth=2, label='Peer Group')
            ax.fill(angles, values_collab, alpha=0.25)
            ax.fill(angles, values_group, alpha=0.25)
            
            # Configurar rótulos
            ax.set_thetagrids(np.degrees(angles[:-1]), categories)
            ax.set_ylim(0, 4)
            ax.set_title('Comparação de Direcionadores', fontsize=16)
            ax.grid(True)
            ax.legend(loc='upper right')
            
            # Salvar gráfico
            graph_file = self.output_dir / 'drivers_radar.png'
            plt.savefig(graph_file, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Gráfico de radar dos direcionadores salvo em: {graph_file}")
        
        return df
    
    def analyze_person_detail(self, person_name: str) -> Dict[str, pd.DataFrame]:
        """
        Analisa detalhes de uma pessoa específica
        
        Args:
            person_name: Nome da pessoa para análise
            
        Returns:
            Dicionário com DataFrames de detalhes
        """
        # Verificar se a pessoa existe
        person_doc = self.people_coll.find_one({"name": person_name})
        
        if not person_doc:
            print(f"Pessoa não encontrada: {person_name}")
            return {}
        
        person_id = person_doc["_id"]
        
        # Consulta para avaliações
        evals_pipeline = [
            {
                "$match": {"person_id": person_id}
            },
            {
                "$project": {
                    "_id": 1,
                    "year": 1,
                    "concept": 1,
                    "peer_group": 1,
                    "avg_score": 1,
                    "import_date": 1
                }
            },
            {
                "$sort": {"year": 1}
            }
        ]
        
        evals_result = list(self.evaluations_coll.aggregate(evals_pipeline))
        evals_df = pd.DataFrame(evals_result)
        
        if evals_df.empty:
            print(f"Nenhuma avaliação encontrada para: {person_name}")
            return {}
        
        # Mapear evaluation_id para year para uso posterior
        eval_years = {str(row["_id"]): row["year"] for _, row in evals_df.iterrows()}
        
        # Consulta para comportamentos
        behaviors_pipeline = [
            {
                "$lookup": {
                    "from": "evaluations",
                    "localField": "evaluation_id",
                    "foreignField": "_id",
                    "as": "evaluation"
                }
            },
            {
                "$unwind": "$evaluation"
            },
            {
                "$match": {"evaluation.person_id": person_id}
            },
            {
                "$project": {
                    "_id": 0,
                    "evaluation_id": 1,
                    "year": "$evaluation.year",
                    "driver": 1,
                    "behavior": 1,
                    "score": 1,
                    "group_score": 1,
                    "difference": 1
                }
            },
            {
                "$sort": {"year": 1, "driver": 1, "behavior": 1}
            }
        ]
        
        behaviors_result = list(self.behaviors_coll.aggregate(behaviors_pipeline))
        behaviors_df = pd.DataFrame(behaviors_result)
        
        # Salvar CSVs
        person_dir = self.output_dir / person_name
        person_dir.mkdir(exist_ok=True, parents=True)
        
        # Remover colunas de ID para a versão CSV
        evals_csv_df = evals_df.drop(columns=["_id"]) if "_id" in evals_df.columns else evals_df
        
        evals_file = person_dir / 'evaluations.csv'
        evals_csv_df.to_csv(evals_file, index=False)
        
        behaviors_file = person_dir / 'behaviors.csv'
        behaviors_df.to_csv(behaviors_file, index=False)
        
        print(f"Relatórios para {person_name} salvos em: {person_dir}")
        
        # Gerar gráficos
        if not evals_df.empty:
            # Gráfico de evolução do score
            plt.figure(figsize=(10, 6))
            plt.plot(evals_df['year'], evals_df['avg_score'], 'o-', linewidth=2)
            plt.title(f'Evolução do Score - {person_name}', fontsize=16)
            plt.xlabel('Ano', fontsize=12)
            plt.ylabel('Score Médio', fontsize=12)
            plt.grid(True)
            plt.ylim(0, 4)
            
            evolution_file = person_dir / 'score_evolution.png'
            plt.savefig(evolution_file, dpi=300, bbox_inches='tight')
            plt.close()
        
        if not behaviors_df.empty and len(behaviors_df['year'].unique()) > 1:
            # Pivot para direcionadores por ano
            pivot_df = behaviors_df.pivot_table(
                index='driver', 
                columns='year', 
                values='score', 
                aggfunc='mean'
            )
            
            # Gráfico de calor
            plt.figure(figsize=(12, 8))
            sns.heatmap(pivot_df, annot=True, cmap='YlGnBu', fmt='.2f', linewidths=.5)
            plt.title(f'Evolução por Direcionador - {person_name}', fontsize=16)
            plt.tight_layout()
            
            heatmap_file = person_dir / 'drivers_heatmap.png'
            plt.savefig(heatmap_file, dpi=300, bbox_inches='tight')
            plt.close()
        
        return {
            'evaluations': evals_df,
            'behaviors': behaviors_df
        }
    
    def generate_full_report(self) -> None:
        """Gera um relatório completo com todos os tipos de análises"""
        print("\n--- Gerando relatório completo ---")
        
        # Visão geral
        overview_df = self.analyze_overview()
        
        # Comportamentos
        behaviors_df = self.analyze_behaviors()
        
        # Direcionadores
        drivers_df = self.analyze_drivers()
        
        # Para cada pessoa, gerar relatório individual
        for person_doc in self.people_coll.find({}, {"name": 1}):
            person_name = person_doc["name"]
            self.analyze_person_detail(person_name)
        
        # Gerar relatório consolidado em HTML
        self._generate_html_report(overview_df, behaviors_df, drivers_df)
        
        print("Relatório completo gerado com sucesso!")
    
    def _generate_html_report(self, overview_df: pd.DataFrame, 
                             behaviors_df: pd.DataFrame,
                             drivers_df: pd.DataFrame) -> None:
        """
        Gera um relatório HTML consolidado
        
        Args:
            overview_df: DataFrame de visão geral
            behaviors_df: DataFrame de comportamentos
            drivers_df: DataFrame de direcionadores
        """
        # Verificar se temos dados
        if overview_df.empty and behaviors_df.empty and drivers_df.empty:
            print("Sem dados suficientes para gerar relatório HTML")
            return
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>People Analytics - Relatório Consolidado (MongoDB)</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .section {{ margin-bottom: 30px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .img-container {{ text-align: center; margin: 20px 0; }}
                img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>People Analytics - Relatório Consolidado (MongoDB)</h1>
            <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        """
        
        # Adicionar seções se houver dados
        if not overview_df.empty:
            # Remover coluna _id para exibição se existir
            overview_html_df = overview_df.drop(columns=["_id"]) if "_id" in overview_df.columns else overview_df
            
            html_content += f"""    
            <div class="section">
                <h2>Visão Geral</h2>
                {overview_html_df.to_html(index=False)}
                
                <div class="img-container">
                    <img src="person_evolution.png" alt="Evolução por Pessoa">
                    <p><em>Evolução do Score por Pessoa ao longo dos anos</em></p>
                </div>
            </div>
            """
        
        if not drivers_df.empty:
            html_content += f"""
            <div class="section">
                <h2>Análise de Direcionadores</h2>
                {drivers_df.to_html(index=False)}
                
                <div class="img-container">
                    <img src="drivers_radar.png" alt="Radar de Direcionadores">
                    <p><em>Comparação de Direcionadores - Colaborador vs Peer Group</em></p>
                </div>
            </div>
            """
        
        if not behaviors_df.empty:
            html_content += f"""
            <div class="section">
                <h2>Análise de Comportamentos</h2>
                {behaviors_df.to_html(index=False)}
                
                <div class="img-container">
                    <img src="top_behaviors.png" alt="Top Comportamentos">
                    <p><em>Top 10 Comportamentos - Comparação Colaborador vs Peer Group</em></p>
                </div>
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        html_file = self.output_dir / 'report.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Relatório HTML consolidado salvo em: {html_file}")
    
    def close(self):
        """Fecha a conexão com o MongoDB"""
        if hasattr(self, 'client'):
            self.client.close()


def main():
    """Função principal do programa"""
    parser = argparse.ArgumentParser(description='Analisador People Analytics com MongoDB e Pandas')
    parser.add_argument('--data_dir', default='data', help='Diretório contendo os dados JSON')
    parser.add_argument('--output_dir', default='output', help='Diretório para salvar os resultados')
    parser.add_argument('--db_name', default='people_analytics', help='Nome do banco de dados MongoDB')
    parser.add_argument('--host', default='localhost', help='Host do MongoDB')
    parser.add_argument('--port', type=int, default=27017, help='Porta do MongoDB')
    
    args = parser.parse_args()
    
    if not MONGODB_AVAILABLE:
        print("MongoDB não disponível. Instale com: pip install pymongo")
        return
    
    try:
        analyzer = MongoDBAnalyzer(
            data_dir=args.data_dir,
            output_dir=args.output_dir,
            db_name=args.db_name,
            host=args.host,
            port=args.port
        )
        
        # Importar dados
        analyzer.import_data()
        
        # Gerar relatório completo
        analyzer.generate_full_report()
        
    except Exception as e:
        print(f"Erro durante a execução: {str(e)}")
    finally:
        if 'analyzer' in locals():
            analyzer.close()


if __name__ == "__main__":
    main() 