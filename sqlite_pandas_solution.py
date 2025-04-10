"""
Solução para análise de dados People Analytics usando SQLite e Pandas.

Esta implementação:
1. Importa dados de arquivos JSON
2. Armazena-os em um banco SQLite
3. Realiza análises usando Pandas
4. Gera visualizações com Matplotlib/Seaborn
5. Exporta resultados para a pasta 'output'

Uso:
    python sqlite_pandas_solution.py --data_dir ./data --output_dir ./output
"""

import os
import json
import argparse
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

# Configuração de estilo para plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("deep")

class SQLitePandasAnalyzer:
    """Analisador de dados usando SQLite e Pandas"""
    
    def __init__(self, data_dir: str = 'data', output_dir: str = 'output', 
                 db_path: str = 'people_analytics.db'):
        """
        Inicializa o analisador
        
        Args:
            data_dir: Diretório contendo os dados JSON
            output_dir: Diretório para salvar os resultados
            db_path: Caminho para o banco de dados SQLite
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.db_path = db_path
        
        # Criar diretório de saída
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Conectar ao banco de dados
        self.conn = sqlite3.connect(self.db_path)
        
        # Criar tabelas se não existirem
        self._create_tables()
    
    def _create_tables(self):
        """Cria as tabelas necessárias no banco de dados SQLite"""
        cursor = self.conn.cursor()
        
        # Tabela para pessoas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
        ''')
        
        # Tabela para avaliações
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER,
            year TEXT,
            file_path TEXT UNIQUE,
            concept TEXT,
            peer_group TEXT,
            avg_score REAL,
            import_date TEXT,
            FOREIGN KEY (person_id) REFERENCES people (id)
        )
        ''')
        
        # Tabela para direcionadores (categorias)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
        ''')
        
        # Tabela para comportamentos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS behaviors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
        ''')
        
        # Tabela para resultados dos comportamentos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS behavior_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluation_id INTEGER,
            driver_id INTEGER,
            behavior_id INTEGER,
            score REAL,
            group_score REAL,
            difference REAL,
            frequencies TEXT,
            group_frequencies TEXT,
            FOREIGN KEY (evaluation_id) REFERENCES evaluations (id),
            FOREIGN KEY (driver_id) REFERENCES drivers (id),
            FOREIGN KEY (behavior_id) REFERENCES behaviors (id)
        )
        ''')
        
        self.conn.commit()
    
    def scan_files(self) -> List[Dict]:
        """
        Escaneia o diretório de dados por arquivos JSON
        
        Returns:
            Lista de informações sobre os arquivos encontrados
        """
        file_pattern = "**/*/resultado.json"
        json_files = list(self.data_dir.glob(file_pattern))
        
        # Verificar arquivos já importados
        cursor = self.conn.cursor()
        cursor.execute("SELECT file_path FROM evaluations")
        existing_files = [row[0] for row in cursor.fetchall()]
        
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
        Importa dados dos arquivos JSON para o banco SQLite
        
        Returns:
            Número de arquivos importados
        """
        # Escanear arquivos
        new_files = self.scan_files()
        if not new_files:
            return 0
        
        cursor = self.conn.cursor()
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
                cursor.execute("INSERT OR IGNORE INTO people (name) VALUES (?)", (person_name,))
                cursor.execute("SELECT id FROM people WHERE name = ?", (person_name,))
                person_id = cursor.fetchone()[0]
                
                # Calcular score médio dos comportamentos
                total_score = 0
                count = 0
                
                behaviors_data = []
                if 'direcionadores' in data['data']:
                    for direcionador in data['data']['direcionadores']:
                        dir_name = direcionador.get('direcionador', 'Desconhecido')
                        
                        # Inserir/buscar direcionador
                        cursor.execute("INSERT OR IGNORE INTO drivers (name) VALUES (?)", (dir_name,))
                        cursor.execute("SELECT id FROM drivers WHERE name = ?", (dir_name,))
                        driver_id = cursor.fetchone()[0]
                        
                        if 'comportamentos' in direcionador:
                            for comp in direcionador['comportamentos']:
                                comp_name = comp.get('comportamento', 'Desconhecido')
                                
                                # Inserir/buscar comportamento
                                cursor.execute("INSERT OR IGNORE INTO behaviors (name) VALUES (?)", (comp_name,))
                                cursor.execute("SELECT id FROM behaviors WHERE name = ?", (comp_name,))
                                behavior_id = cursor.fetchone()[0]
                                
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
                                                'driver_id': driver_id,
                                                'behavior_id': behavior_id,
                                                'score': score_colab,
                                                'group_score': score_grupo,
                                                'difference': difference,
                                                'frequencies': json.dumps(freq_colab),
                                                'group_frequencies': json.dumps(freq_grupo)
                                            })
                
                # Calcular score médio
                avg_score = total_score / count if count > 0 else 0.0
                import_date = datetime.now().isoformat()
                
                # Inserir avaliação
                cursor.execute('''
                INSERT INTO evaluations 
                (person_id, year, file_path, concept, peer_group, avg_score, import_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (person_id, year, file_path, concept, peer_group, avg_score, import_date))
                
                evaluation_id = cursor.lastrowid
                
                # Inserir resultados dos comportamentos
                for behavior in behaviors_data:
                    cursor.execute('''
                    INSERT INTO behavior_results 
                    (evaluation_id, driver_id, behavior_id, score, group_score, difference, 
                     frequencies, group_frequencies)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        evaluation_id,
                        behavior['driver_id'],
                        behavior['behavior_id'],
                        behavior['score'],
                        behavior['group_score'],
                        behavior['difference'],
                        behavior['frequencies'],
                        behavior['group_frequencies']
                    ))
                
                self.conn.commit()
                imported_count += 1
                print(f"Importado: {file_path}")
                
            except Exception as e:
                print(f"Erro ao importar {file_info['path']}: {str(e)}")
                self.conn.rollback()
        
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
        query = """
        SELECT 
            p.name as person,
            e.year,
            e.concept,
            e.peer_group,
            e.avg_score,
            e.import_date
        FROM 
            evaluations e
        JOIN 
            people p ON e.person_id = p.id
        ORDER BY 
            e.year DESC, p.name
        """
        
        df = pd.read_sql_query(query, self.conn)
        
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
        query = """
        SELECT 
            d.name as driver,
            b.name as behavior,
            AVG(br.score) as avg_score,
            AVG(br.group_score) as avg_group_score,
            AVG(br.difference) as avg_difference,
            COUNT(*) as count
        FROM 
            behavior_results br
        JOIN 
            drivers d ON br.driver_id = d.id
        JOIN 
            behaviors b ON br.behavior_id = b.id
        GROUP BY 
            d.name, b.name
        ORDER BY 
            avg_difference DESC
        """
        
        df = pd.read_sql_query(query, self.conn)
        
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
        query = """
        SELECT 
            d.name as driver,
            AVG(br.score) as avg_score,
            AVG(br.group_score) as avg_group_score,
            AVG(br.difference) as avg_difference,
            COUNT(*) as count,
            COUNT(DISTINCT br.behavior_id) as num_behaviors
        FROM 
            behavior_results br
        JOIN 
            drivers d ON br.driver_id = d.id
        GROUP BY 
            d.name
        ORDER BY 
            avg_difference DESC
        """
        
        df = pd.read_sql_query(query, self.conn)
        
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
        query_person = """
        SELECT id FROM people WHERE name = ?
        """
        person_df = pd.read_sql_query(query_person, self.conn, params=(person_name,))
        
        if person_df.empty:
            print(f"Pessoa não encontrada: {person_name}")
            return {}
        
        person_id = person_df.iloc[0]['id']
        
        # Consulta para avaliações
        query_evals = """
        SELECT 
            e.year,
            e.concept,
            e.peer_group,
            e.avg_score,
            e.import_date
        FROM 
            evaluations e
        WHERE 
            e.person_id = ?
        ORDER BY 
            e.year
        """
        
        evals_df = pd.read_sql_query(query_evals, self.conn, params=(person_id,))
        
        # Consulta para comportamentos
        query_behaviors = """
        SELECT 
            e.year,
            d.name as driver,
            b.name as behavior,
            br.score,
            br.group_score,
            br.difference
        FROM 
            behavior_results br
        JOIN 
            evaluations e ON br.evaluation_id = e.id
        JOIN 
            drivers d ON br.driver_id = d.id
        JOIN 
            behaviors b ON br.behavior_id = b.id
        WHERE 
            e.person_id = ?
        ORDER BY 
            e.year, d.name, b.name
        """
        
        behaviors_df = pd.read_sql_query(query_behaviors, self.conn, params=(person_id,))
        
        # Salvar CSVs
        person_dir = self.output_dir / person_name
        person_dir.mkdir(exist_ok=True, parents=True)
        
        evals_file = person_dir / 'evaluations.csv'
        evals_df.to_csv(evals_file, index=False)
        
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
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM people")
        people = [row[0] for row in cursor.fetchall()]
        
        for person in people:
            self.analyze_person_detail(person)
        
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
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>People Analytics - Relatório Consolidado</title>
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
            <h1>People Analytics - Relatório Consolidado</h1>
            <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            
            <div class="section">
                <h2>Visão Geral</h2>
                {overview_df.to_html(index=False)}
                
                <div class="img-container">
                    <img src="person_evolution.png" alt="Evolução por Pessoa">
                    <p><em>Evolução do Score por Pessoa ao longo dos anos</em></p>
                </div>
            </div>
            
            <div class="section">
                <h2>Análise de Direcionadores</h2>
                {drivers_df.to_html(index=False)}
                
                <div class="img-container">
                    <img src="drivers_radar.png" alt="Radar de Direcionadores">
                    <p><em>Comparação de Direcionadores - Colaborador vs Peer Group</em></p>
                </div>
            </div>
            
            <div class="section">
                <h2>Análise de Comportamentos</h2>
                {behaviors_df.to_html(index=False)}
                
                <div class="img-container">
                    <img src="top_behaviors.png" alt="Top Comportamentos">
                    <p><em>Top 10 Comportamentos - Comparação Colaborador vs Peer Group</em></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        html_file = self.output_dir / 'report.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Relatório HTML consolidado salvo em: {html_file}")
    
    def close(self):
        """Fecha a conexão com o banco de dados"""
        if hasattr(self, 'conn'):
            self.conn.close()


def main():
    """Função principal do programa"""
    parser = argparse.ArgumentParser(description='Analisador People Analytics com SQLite e Pandas')
    parser.add_argument('--data_dir', default='data', help='Diretório contendo os dados JSON')
    parser.add_argument('--output_dir', default='output', help='Diretório para salvar os resultados')
    parser.add_argument('--db_path', default='people_analytics.db', help='Caminho para o banco de dados SQLite')
    
    args = parser.parse_args()
    
    try:
        analyzer = SQLitePandasAnalyzer(
            data_dir=args.data_dir,
            output_dir=args.output_dir,
            db_path=args.db_path
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