"""
Solução para análise de dados People Analytics usando DuckDB.

DuckDB é um banco de dados analítico embutido que não requer instalação 
de um servidor separado, similar ao SQLite mas otimizado para análises.

Esta implementação:
1. Importa dados de arquivos JSON
2. Armazena-os em um banco DuckDB
3. Realiza análises usando DuckDB e Pandas
4. Gera visualizações com Matplotlib/Seaborn
5. Exporta resultados para a pasta 'output'

Uso:
    python duckdb_solution.py --data_dir ./data --output_dir ./output
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
import time
from typing import Dict, List, Any, Tuple, Optional
import tqdm  # Add progress bar support

try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False
    print("AVISO: DuckDB não está instalado. Use: pip install duckdb")
    print("Usando SQLite como fallback...")
    import sqlite3

try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
    print("AVISO: openpyxl não está instalado. Use: pip install openpyxl")
    print("Exportação para Excel não estará disponível.")

# Configuração de estilo para plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("deep")

class DuckDBAnalyzer:
    """Analisador de dados usando DuckDB"""
    
    def __init__(self, data_dir: str = 'data', output_dir: str = 'output', 
                 db_path: str = 'people_analytics.duckdb'):
        """
        Inicializa o analisador
        
        Args:
            data_dir: Diretório contendo os dados JSON
            output_dir: Diretório para salvar os resultados
            db_path: Caminho para o banco de dados DuckDB
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.db_path = db_path
        self.using_sqlite = False
        self.performance_metrics = {}
        
        # Criar diretório de saída
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Conectar ao banco de dados (DuckDB ou SQLite como fallback)
        start_time = time.time()
        if DUCKDB_AVAILABLE:
            self.conn = duckdb.connect(self.db_path)
            print(f"Usando DuckDB - banco de dados: {self.db_path}")
        else:
            self.conn = sqlite3.connect(self.db_path.replace('.duckdb', '.db'))
            self.using_sqlite = True
            print(f"Usando SQLite (fallback) - banco de dados: {self.db_path.replace('.duckdb', '.db')}")
        self.performance_metrics['db_connect_time'] = time.time() - start_time
        
        # Criar tabelas se não existirem
        start_time = time.time()
        self._create_tables()
        self.performance_metrics['create_tables_time'] = time.time() - start_time
        
        # Criar índices para melhorar performance
        start_time = time.time()
        self._create_indexes()
        self.performance_metrics['create_indexes_time'] = time.time() - start_time
    
    def _create_tables(self):
        """Cria as tabelas necessárias no banco de dados"""
        cursor = self.conn.cursor()
        
        if self.using_sqlite:
            # Tabelas para SQLite
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
            ''')
            
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
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS behaviors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
            ''')
            
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
        else:
            # Tabelas para DuckDB (pequenas diferenças na sintaxe)
            cursor.execute('''
            CREATE SEQUENCE IF NOT EXISTS people_id_seq;
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER DEFAULT nextval('people_id_seq') PRIMARY KEY,
                name VARCHAR UNIQUE
            )
            ''')
            
            cursor.execute('''
            CREATE SEQUENCE IF NOT EXISTS evaluations_id_seq;
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER DEFAULT nextval('evaluations_id_seq') PRIMARY KEY,
                person_id INTEGER,
                year VARCHAR,
                file_path VARCHAR UNIQUE,
                concept VARCHAR,
                peer_group VARCHAR,
                avg_score DOUBLE,
                import_date VARCHAR,
                FOREIGN KEY (person_id) REFERENCES people (id)
            )
            ''')
            
            cursor.execute('''
            CREATE SEQUENCE IF NOT EXISTS drivers_id_seq;
            CREATE TABLE IF NOT EXISTS drivers (
                id INTEGER DEFAULT nextval('drivers_id_seq') PRIMARY KEY,
                name VARCHAR UNIQUE
            )
            ''')
            
            cursor.execute('''
            CREATE SEQUENCE IF NOT EXISTS behaviors_id_seq;
            CREATE TABLE IF NOT EXISTS behaviors (
                id INTEGER DEFAULT nextval('behaviors_id_seq') PRIMARY KEY,
                name VARCHAR UNIQUE
            )
            ''')
            
            cursor.execute('''
            CREATE SEQUENCE IF NOT EXISTS behavior_results_id_seq;
            CREATE TABLE IF NOT EXISTS behavior_results (
                id INTEGER DEFAULT nextval('behavior_results_id_seq') PRIMARY KEY,
                evaluation_id INTEGER,
                driver_id INTEGER,
                behavior_id INTEGER,
                score DOUBLE,
                group_score DOUBLE,
                difference DOUBLE,
                frequencies VARCHAR,
                group_frequencies VARCHAR,
                FOREIGN KEY (evaluation_id) REFERENCES evaluations (id),
                FOREIGN KEY (driver_id) REFERENCES drivers (id),
                FOREIGN KEY (behavior_id) REFERENCES behaviors (id)
            )
            ''')
        
        self.conn.commit()
    
    def _create_indexes(self):
        """Cria índices para melhorar a performance das consultas"""
        cursor = self.conn.cursor()
        
        # Criar índices para as chaves estrangeiras e campos frequentemente consultados
        try:
            # Índice para evaluations.person_id (muito usado em consultas por pessoa)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_evaluations_person_id ON evaluations(person_id)")
            
            # Índice para evaluations.year (usado para consultas de evolução por ano)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_evaluations_year ON evaluations(year)")
            
            # Índices para behavior_results (usados em várias consultas de análise)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_behavior_results_eval ON behavior_results(evaluation_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_behavior_results_driver ON behavior_results(driver_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_behavior_results_behavior ON behavior_results(behavior_id)")
            
            self.conn.commit()
            
        except Exception as e:
            # Algumas versões ou implementações podem não suportar índices
            print(f"Aviso: Não foi possível criar índices: {str(e)}")
    
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
    
    def import_data(self, batch_size: int = 10) -> int:
        """
        Importa dados dos arquivos JSON para o banco
        
        Args:
            batch_size: Tamanho do lote para importação em massa (para grandes volumes)
            
        Returns:
            Número de arquivos importados
        """
        # Escanear arquivos
        new_files = self.scan_files()
        if not new_files:
            return 0
        
        cursor = self.conn.cursor()
        imported_count = 0
        
        # Usar tqdm para mostrar barra de progresso
        with tqdm.tqdm(total=len(new_files), desc="Importando arquivos") as pbar:
            for file_info in new_files:
                try:
                    # Iniciar transação para este arquivo
                    self.conn.execute("BEGIN TRANSACTION")
                    
                    # Carregar dados do arquivo
                    with open(file_info['path'], 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if 'data' not in data:
                        print(f"Arquivo inválido (sem 'data'): {file_info['path']}")
                        self.conn.execute("ROLLBACK")
                        pbar.update(1)  # Atualizar barra mesmo em caso de erro
                        continue
                    
                    # Extrair dados básicos
                    person_name = file_info['person']
                    year = file_info['year']
                    file_path = file_info['path']
                    concept = data['data'].get('conceito_ciclo_filho_descricao', 'Unknown')
                    peer_group = data['data'].get('nome_peer_group', 'Unknown')
                    
                    # Inserir pessoa
                    if self.using_sqlite:
                        cursor.execute("INSERT OR IGNORE INTO people (name) VALUES (?)", (person_name,))
                        cursor.execute("SELECT id FROM people WHERE name = ?", (person_name,))
                        person_id = cursor.fetchone()[0]
                    else:
                        # Para DuckDB, primeiro verificar se já existe
                        cursor.execute("SELECT id FROM people WHERE name = ?", (person_name,))
                        result = cursor.fetchone()
                        if not result:
                            cursor.execute("INSERT INTO people (name) VALUES (?) RETURNING id", (person_name,))
                            person_id = cursor.fetchone()[0]
                        else:
                            person_id = result[0]
                    
                    # Calcular score médio dos comportamentos
                    total_score = 0
                    count = 0
                    
                    behaviors_data = []
                    if 'direcionadores' in data['data']:
                        for direcionador in data['data']['direcionadores']:
                            dir_name = direcionador.get('direcionador', 'Desconhecido')
                            
                            # Inserir/buscar direcionador
                            if self.using_sqlite:
                                cursor.execute("INSERT OR IGNORE INTO drivers (name) VALUES (?)", (dir_name,))
                                cursor.execute("SELECT id FROM drivers WHERE name = ?", (dir_name,))
                                driver_id = cursor.fetchone()[0]
                            else:
                                # Para DuckDB, primeiro verificar se já existe
                                cursor.execute("SELECT id FROM drivers WHERE name = ?", (dir_name,))
                                result = cursor.fetchone()
                                if not result:
                                    cursor.execute("INSERT INTO drivers (name) VALUES (?) RETURNING id", (dir_name,))
                                    driver_id = cursor.fetchone()[0]
                                else:
                                    driver_id = result[0]
                            
                            if 'comportamentos' in direcionador:
                                for comp in direcionador['comportamentos']:
                                    comp_name = comp.get('comportamento', 'Desconhecido')
                                    
                                    # Inserir/buscar comportamento
                                    if self.using_sqlite:
                                        cursor.execute("INSERT OR IGNORE INTO behaviors (name) VALUES (?)", (comp_name,))
                                        cursor.execute("SELECT id FROM behaviors WHERE name = ?", (comp_name,))
                                        behavior_id = cursor.fetchone()[0]
                                    else:
                                        # Para DuckDB, primeiro verificar se já existe
                                        cursor.execute("SELECT id FROM behaviors WHERE name = ?", (comp_name,))
                                        result = cursor.fetchone()
                                        if not result:
                                            cursor.execute("INSERT INTO behaviors (name) VALUES (?) RETURNING id", (comp_name,))
                                            behavior_id = cursor.fetchone()[0]
                                        else:
                                            behavior_id = result[0]
                                    
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
                    
                    # Verificar se avaliação já existe
                    cursor.execute("SELECT id FROM evaluations WHERE file_path = ?", (file_path,))
                    eval_result = cursor.fetchone()
                    
                    if eval_result:
                        # Atualizar avaliação existente
                        cursor.execute('''
                        UPDATE evaluations SET
                        person_id = ?,
                        year = ?,
                        concept = ?,
                        peer_group = ?,
                        avg_score = ?,
                        import_date = ?
                        WHERE file_path = ?
                        ''', (person_id, year, concept, peer_group, avg_score, import_date, file_path))
                        evaluation_id = eval_result[0]
                    else:
                        # Inserir nova avaliação
                        if self.using_sqlite:
                            cursor.execute('''
                            INSERT INTO evaluations
                            (person_id, year, file_path, concept, peer_group, avg_score, import_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (person_id, year, file_path, concept, peer_group, avg_score, import_date))
                            
                            # Obter ID da avaliação inserida
                            cursor.execute("SELECT id FROM evaluations WHERE file_path = ?", (file_path,))
                            evaluation_id = cursor.fetchone()[0]
                        else:
                            # Para DuckDB, usar RETURNING para obter o ID
                            cursor.execute('''
                            INSERT INTO evaluations
                            (person_id, year, file_path, concept, peer_group, avg_score, import_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            RETURNING id
                            ''', (person_id, year, file_path, concept, peer_group, avg_score, import_date))
                            
                            evaluation_id = cursor.fetchone()[0]
                    
                    # Excluir comportamentos antigos se existirem
                    cursor.execute("DELETE FROM behavior_results WHERE evaluation_id = ?", (evaluation_id,))
                    
                    # Preparar inserção em lote para os comportamentos
                    batch_values = []
                    batch_params = []
                    
                    for behavior in behaviors_data:
                        batch_params.extend([
                            evaluation_id,
                            behavior['driver_id'],
                            behavior['behavior_id'],
                            behavior['score'],
                            behavior['group_score'],
                            behavior['difference'],
                            behavior['frequencies'],
                            behavior['group_frequencies']
                        ])
                        batch_values.append("(?, ?, ?, ?, ?, ?, ?, ?)")
                    
                    # Inserir resultados dos comportamentos em lote, se houver dados
                    if batch_values:
                        batch_sql = f'''
                        INSERT INTO behavior_results
                        (evaluation_id, driver_id, behavior_id, score, group_score, difference,
                         frequencies, group_frequencies)
                        VALUES {", ".join(batch_values)}
                        '''
                        cursor.execute(batch_sql, batch_params)
                    
                    # Commit da transação
                    self.conn.execute("COMMIT")
                    imported_count += 1
                    pbar.update(1)  # Atualizar barra de progresso
                    
                except Exception as e:
                    print(f"Erro ao importar {file_info['path']}: {str(e)}")
                    # Rollback em caso de erro
                    try:
                        self.conn.execute("ROLLBACK")
                    except Exception as rollback_error:
                        # Ignorar erro se não houver transação ativa
                        print(f"Erro ao fazer rollback: {str(rollback_error)}")
                    pbar.update(1)  # Atualizar barra mesmo em caso de erro
        
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
        
        if not self.using_sqlite and DUCKDB_AVAILABLE:
            # Usar a função read_sql do DuckDB
            df = self.conn.execute(query).fetchdf()
        else:
            # Usar pandas padrão para SQLite
            df = pd.read_sql_query(query, self.conn)
        
        if df.empty:
            print("Sem dados para gerar relatório de visão geral")
            return df
        
        # Salvar CSV
        output_file = self.output_dir / 'overview_report.csv'
        df.to_csv(output_file, index=False)
        print(f"Relatório de visão geral salvo em: {output_file}")
        
        # Salvar Excel se disponível
        if EXCEL_AVAILABLE:
            excel_file = self.output_dir / 'overview_report.xlsx'
            df.to_excel(excel_file, index=False, sheet_name='Visão Geral')
            print(f"Relatório Excel de visão geral salvo em: {excel_file}")
        
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
        
        if not self.using_sqlite and DUCKDB_AVAILABLE:
            # Usar a função read_sql do DuckDB
            df = self.conn.execute(query).fetchdf()
        else:
            # Usar pandas padrão para SQLite
            df = pd.read_sql_query(query, self.conn)
        
        if df.empty:
            print("Sem dados para gerar relatório de comportamentos")
            return df
        
        # Salvar CSV
        output_file = self.output_dir / 'behaviors_report.csv'
        df.to_csv(output_file, index=False)
        print(f"Relatório de comportamentos salvo em: {output_file}")
        
        # Salvar Excel se disponível
        if EXCEL_AVAILABLE:
            excel_file = self.output_dir / 'behaviors_report.xlsx'
            df.to_excel(excel_file, index=False, sheet_name='Comportamentos')
            print(f"Relatório Excel de comportamentos salvo em: {excel_file}")
        
        # Gerar gráfico de barras dos top comportamentos por diferença
        if not df.empty:
            plt.figure(figsize=(14, 10))
            
            # Top 10 comportamentos por diferença (ou menos se não houver 10)
            top_count = min(10, len(df))
            top_df = df.nlargest(top_count, 'avg_difference')
            
            # Criar barras agrupadas
            x = np.arange(len(top_df))
            width = 0.35
            
            fig, ax = plt.subplots(figsize=(14, 10))
            rects1 = ax.bar(x - width/2, top_df['avg_score'], width, label='Colaborador')
            rects2 = ax.bar(x + width/2, top_df['avg_group_score'], width, label='Peer Group')
            
            ax.set_title(f'Top {top_count} Comportamentos - Comparação', fontsize=16)
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
        
        if not self.using_sqlite and DUCKDB_AVAILABLE:
            # Usar a função read_sql do DuckDB
            df = self.conn.execute(query).fetchdf()
        else:
            # Usar pandas padrão para SQLite
            df = pd.read_sql_query(query, self.conn)
        
        if df.empty:
            print("Sem dados para gerar relatório de direcionadores")
            return df
        
        # Salvar CSV
        output_file = self.output_dir / 'drivers_report.csv'
        df.to_csv(output_file, index=False)
        print(f"Relatório de direcionadores salvo em: {output_file}")
        
        # Salvar Excel se disponível
        if EXCEL_AVAILABLE:
            excel_file = self.output_dir / 'drivers_report.xlsx'
            df.to_excel(excel_file, index=False, sheet_name='Direcionadores')
            print(f"Relatório Excel de direcionadores salvo em: {excel_file}")
        
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
        cursor = self.conn.cursor()
        cursor.execute(query_person, (person_name,))
        person_row = cursor.fetchone()
        
        if not person_row:
            print(f"Pessoa não encontrada: {person_name}")
            return {}
        
        person_id = person_row[0]
        
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
        
        if not self.using_sqlite and DUCKDB_AVAILABLE:
            # Usar função do DuckDB passando parâmetros
            evals_df = self.conn.execute(query_evals, [person_id]).fetchdf()
        else:
            # Usar pandas padrão para SQLite
            evals_df = pd.read_sql_query(query_evals, self.conn, params=(person_id,))
        
        if evals_df.empty:
            print(f"Nenhuma avaliação encontrada para: {person_name}")
            return {}
        
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
        
        if not self.using_sqlite and DUCKDB_AVAILABLE:
            # Usar função do DuckDB passando parâmetros
            behaviors_df = self.conn.execute(query_behaviors, [person_id]).fetchdf()
        else:
            # Usar pandas padrão para SQLite
            behaviors_df = pd.read_sql_query(query_behaviors, self.conn, params=(person_id,))
        
        # Salvar CSVs
        person_dir = self.output_dir / person_name
        person_dir.mkdir(exist_ok=True, parents=True)
        
        evals_file = person_dir / 'evaluations.csv'
        evals_df.to_csv(evals_file, index=False)
        
        behaviors_file = person_dir / 'behaviors.csv'
        behaviors_df.to_csv(behaviors_file, index=False)
        
        # Salvar Excel se disponível
        if EXCEL_AVAILABLE:
            excel_file = person_dir / f'{person_name}_report.xlsx'
            with pd.ExcelWriter(excel_file) as writer:
                evals_df.to_excel(writer, index=False, sheet_name='Avaliações')
                behaviors_df.to_excel(writer, index=False, sheet_name='Comportamentos')
            print(f"Relatório Excel para {person_name} salvo em: {excel_file}")
        
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
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas sobre o banco de dados
        
        Returns:
            Dicionário com estatísticas do banco
        """
        stats = {}
        cursor = self.conn.cursor()
        
        # Contar registros em cada tabela
        tables = ['people', 'evaluations', 'drivers', 'behaviors', 'behavior_results']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[f"{table}_count"] = cursor.fetchone()[0]
        
        # Adicionar métricas de performance
        stats.update(self.performance_metrics)
        
        # Adicionar informações do banco
        if not self.using_sqlite and DUCKDB_AVAILABLE:
            # Obter tamanho do arquivo
            if os.path.exists(self.db_path):
                stats['db_file_size'] = os.path.getsize(self.db_path)
                stats['db_size_mb'] = round(stats['db_file_size'] / (1024 * 1024), 2)
        
        return stats
    
    def print_stats(self):
        """Imprime estatísticas sobre o banco de dados e métricas de performance"""
        stats = self.get_database_stats()
        
        print("\n--- Estatísticas do Banco de Dados ---")
        print(f"Pessoas: {stats.get('people_count', 0)}")
        print(f"Avaliações: {stats.get('evaluations_count', 0)}")
        print(f"Direcionadores: {stats.get('drivers_count', 0)}")
        print(f"Comportamentos: {stats.get('behaviors_count', 0)}")
        print(f"Resultados: {stats.get('behavior_results_count', 0)}")
        
        if 'db_size_mb' in stats:
            print(f"Tamanho do DB: {stats['db_size_mb']} MB")
        
        print("\n--- Métricas de Performance ---")
        for key, value in stats.items():
            if key.endswith('_time'):
                print(f"{key.replace('_time', '').replace('_', ' ').title()}: {value:.4f} segundos")
        print("-----------------------------------")
    
    def generate_stats_report(self, include_in_html: bool = True):
        """
        Gera um relatório com estatísticas do banco e métricas de performance
        
        Args:
            include_in_html: Se True, inclui as estatísticas no relatório HTML principal
        """
        stats = self.get_database_stats()
        
        # Criar DataFrame com estatísticas de contagem
        counts_data = {
            'Tabela': ['Pessoas', 'Avaliações', 'Direcionadores', 'Comportamentos', 'Resultados'],
            'Registros': [
                stats.get('people_count', 0),
                stats.get('evaluations_count', 0),
                stats.get('drivers_count', 0),
                stats.get('behaviors_count', 0),
                stats.get('behavior_results_count', 0)
            ]
        }
        counts_df = pd.DataFrame(counts_data)
        
        # Criar DataFrame com métricas de performance
        perf_data = {
            'Operação': [],
            'Tempo (s)': []
        }
        
        for key, value in stats.items():
            if key.endswith('_time'):
                perf_data['Operação'].append(key.replace('_time', '').replace('_', ' ').title())
                perf_data['Tempo (s)'].append(round(value, 4))
        
        perf_df = pd.DataFrame(perf_data)
        
        # Salvar CSVs
        counts_file = self.output_dir / 'database_counts.csv'
        counts_df.to_csv(counts_file, index=False)
        
        perf_file = self.output_dir / 'performance_metrics.csv'
        perf_df.to_csv(perf_file, index=False)
        
        # Salvar Excel
        if EXCEL_AVAILABLE:
            stats_file = self.output_dir / 'database_stats.xlsx'
            with pd.ExcelWriter(stats_file) as writer:
                counts_df.to_excel(writer, sheet_name='Contagens', index=False)
                perf_df.to_excel(writer, sheet_name='Performance', index=False)
                
                # Adicionar metadados
                meta_df = pd.DataFrame({
                    'Propriedade': ['Data', 'Versão DB', 'Tamanho DB (MB)'],
                    'Valor': [
                        datetime.now().strftime('%d/%m/%Y %H:%M'),
                        'DuckDB' if DUCKDB_AVAILABLE else 'SQLite',
                        stats.get('db_size_mb', 'N/A')
                    ]
                })
                meta_df.to_excel(writer, sheet_name='Metadados', index=False)
            
            print(f"Relatório de estatísticas salvo em: {stats_file}")
        
        # Criar visualizações
        # Gráfico de barras para contagens
        plt.figure(figsize=(10, 6))
        ax = sns.barplot(x='Tabela', y='Registros', data=counts_df)
        plt.title('Contagem de Registros por Tabela', fontsize=16)
        plt.xlabel('Tabela', fontsize=12)
        plt.ylabel('Número de Registros', fontsize=12)
        plt.xticks(rotation=45)
        
        # Adicionar rótulos
        for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', 
                       (p.get_x() + p.get_width() / 2., p.get_height()),
                       ha = 'center', va = 'bottom')
        
        plt.tight_layout()
        counts_graph = self.output_dir / 'database_counts.png'
        plt.savefig(counts_graph, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Gráfico de barras horizontais para performance
        if perf_df.shape[0] > 0:
            plt.figure(figsize=(10, 6))
            ax = sns.barplot(x='Tempo (s)', y='Operação', data=perf_df)
            plt.title('Tempo de Execução por Operação', fontsize=16)
            plt.xlabel('Tempo (segundos)', fontsize=12)
            plt.ylabel('Operação', fontsize=12)
            
            # Adicionar rótulos
            for p in ax.patches:
                width = p.get_width()
                plt.text(width + 0.02, p.get_y() + p.get_height()/2, 
                        f'{width:.4f}s', ha='left', va='center')
            
            plt.tight_layout()
            perf_graph = self.output_dir / 'performance_metrics.png'
            plt.savefig(perf_graph, dpi=300, bbox_inches='tight')
            plt.close()
        
        return {
            'counts_df': counts_df,
            'perf_df': perf_df,
            'stats': stats
        }
    
    def generate_full_report(self, report_types: List[str] = None) -> None:
        """
        Gera um relatório completo com todos os tipos de análises
        
        Args:
            report_types: Lista de tipos de relatório a gerar ('overview', 'behaviors', 'drivers', 'people', 'stats').
                         Se None, gera todos os relatórios.
        """
        print("\n--- Gerando relatório completo ---")
        
        # Iniciar timer para medir tempo total
        start_report_time = time.time()
        
        # Se não especificado, gerar todos os relatórios
        if report_types is None:
            report_types = ['overview', 'behaviors', 'drivers', 'people', 'stats']
        
        # Converter para minúsculas para comparação
        report_types = [rt.lower() for rt in report_types]
        
        # DataFrames para o relatório HTML
        overview_df = pd.DataFrame()
        behaviors_df = pd.DataFrame()
        drivers_df = pd.DataFrame()
        stats_data = {}
        
        # Visão geral
        if 'overview' in report_types:
            start_time = time.time()
            overview_df = self.analyze_overview()
            self.performance_metrics['overview_analysis_time'] = time.time() - start_time
        
        # Comportamentos
        if 'behaviors' in report_types:
            start_time = time.time()
            behaviors_df = self.analyze_behaviors()
            self.performance_metrics['behaviors_analysis_time'] = time.time() - start_time
        
        # Direcionadores
        if 'drivers' in report_types:
            start_time = time.time()
            drivers_df = self.analyze_drivers()
            self.performance_metrics['drivers_analysis_time'] = time.time() - start_time
        
        # Para cada pessoa, gerar relatório individual
        if 'people' in report_types:
            start_time = time.time()
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM people")
            people = [row[0] for row in cursor.fetchall()]
            
            for person in people:
                self.analyze_person_detail(person)
            self.performance_metrics['people_analysis_time'] = time.time() - start_time
        
        # Estatísticas do banco de dados
        if 'stats' in report_types:
            start_time = time.time()
            stats_data = self.generate_stats_report()
            self.performance_metrics['stats_generation_time'] = time.time() - start_time
        
        # Gerar relatório consolidado em HTML
        if set(report_types) & {'overview', 'behaviors', 'drivers', 'stats'}:  # Se pelo menos um desses tipos foi solicitado
            self._generate_html_report(overview_df, behaviors_df, drivers_df, stats_data)
        
        # Gerar relatório consolidado em Excel se disponível
        if EXCEL_AVAILABLE and set(report_types) & {'overview', 'behaviors', 'drivers', 'stats'}:
            self._generate_excel_report(overview_df, behaviors_df, drivers_df, stats_data)
        
        # Registrar tempo total de geração de relatório
        self.performance_metrics['total_report_time'] = time.time() - start_report_time
        
        # Imprimir estatísticas
        self.print_stats()
        
        print("Relatório completo gerado com sucesso!")
    
    def _generate_html_report(self, overview_df: pd.DataFrame, 
                             behaviors_df: pd.DataFrame,
                             drivers_df: pd.DataFrame,
                             stats_data: Dict = None) -> None:
        """
        Gera um relatório HTML consolidado
        
        Args:
            overview_df: DataFrame de visão geral
            behaviors_df: DataFrame de comportamentos
            drivers_df: DataFrame de direcionadores
            stats_data: Dados de estatísticas do banco (opcional)
        """
        # Verificar se temos dados
        if overview_df.empty and behaviors_df.empty and drivers_df.empty and not stats_data:
            print("Sem dados suficientes para gerar relatório HTML")
            return
            
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>People Analytics - Relatório Consolidado</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; background-color: #f9f9f9; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                h1 {{ border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #3498db; color: white; font-weight: bold; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                tr:hover {{ background-color: #e5e5e5; }}
                .section {{ margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 8px; 
                           background-color: white; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
                .img-container {{ text-align: center; margin: 25px 0; }}
                img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 3px 10px rgba(0,0,0,0.1); }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; }}
                .header h1 {{ border-bottom: none; color: white; margin: 0; }}
                .header p {{ color: #ecf0f1; margin: 10px 0 0 0; }}
                .footer {{ text-align: center; margin-top: 30px; padding: 15px; border-top: 1px solid #ddd; color: #7f8c8d; }}
                .nav {{ background-color: #34495e; padding: 10px; margin-bottom: 20px; border-radius: 5px; }}
                .nav a {{ color: white; text-decoration: none; padding: 8px 15px; display: inline-block; border-radius: 3px; }}
                .nav a:hover {{ background-color: #2c3e50; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>People Analytics - Relatório Consolidado</h1>
                <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            </div>
            
            <div class="nav">
                <a href="#overview">Visão Geral</a>
                <a href="#drivers">Direcionadores</a>
                <a href="#behaviors">Comportamentos</a>
                <a href="#stats">Estatísticas</a>
            </div>
        """
        
        # Adicionar seções se houver dados
        if not overview_df.empty:
            html_content += f"""    
            <div id="overview" class="section">
                <h2>Visão Geral</h2>
                {overview_df.to_html(index=False, classes="table table-striped")}
                
                <div class="img-container">
                    <img src="person_evolution.png" alt="Evolução por Pessoa">
                    <p><em>Evolução do Score por Pessoa ao longo dos anos</em></p>
                </div>
            </div>
            """
        
        if not drivers_df.empty:
            html_content += f"""
            <div id="drivers" class="section">
                <h2>Análise de Direcionadores</h2>
                {drivers_df.to_html(index=False, classes="table table-striped")}
                
                <div class="img-container">
                    <img src="drivers_radar.png" alt="Radar de Direcionadores">
                    <p><em>Comparação de Direcionadores - Colaborador vs Peer Group</em></p>
                </div>
            </div>
            """
        
        if not behaviors_df.empty:
            html_content += f"""
            <div id="behaviors" class="section">
                <h2>Análise de Comportamentos</h2>
                {behaviors_df.to_html(index=False, classes="table table-striped")}
                
                <div class="img-container">
                    <img src="top_behaviors.png" alt="Top Comportamentos">
                    <p><em>Top Comportamentos - Comparação Colaborador vs Peer Group</em></p>
                </div>
            </div>
            """
        
        # Adicionar seção de estatísticas se disponível
        if stats_data and 'counts_df' in stats_data:
            counts_df = stats_data['counts_df']
            perf_df = stats_data.get('perf_df', pd.DataFrame())
            
            html_content += f"""
            <div id="stats" class="section">
                <h2>Estatísticas do Banco de Dados</h2>
                
                <h3>Contagem de Registros</h3>
                {counts_df.to_html(index=False, classes="table table-striped")}
                
                <div class="img-container">
                    <img src="database_counts.png" alt="Contagem de Registros">
                    <p><em>Distribuição de registros por tabela</em></p>
                </div>
            """
            
            if not perf_df.empty:
                html_content += f"""
                <h3>Métricas de Performance</h3>
                {perf_df.to_html(index=False, classes="table table-striped")}
                
                <div class="img-container">
                    <img src="performance_metrics.png" alt="Métricas de Performance">
                    <p><em>Tempo de execução por operação</em></p>
                </div>
                """
            
            html_content += "</div>"
        
        html_content += """
            <div class="footer">
                <p>© People Analytics - Gerado por DuckDB Analytics</p>
            </div>
        </body>
        </html>
        """
        
        html_file = self.output_dir / 'report.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Relatório HTML consolidado salvo em: {html_file}")
    
    def _generate_excel_report(self, overview_df: pd.DataFrame, 
                              behaviors_df: pd.DataFrame,
                              drivers_df: pd.DataFrame,
                              stats_data: Dict = None) -> None:
        """
        Gera um relatório Excel consolidado
        
        Args:
            overview_df: DataFrame de visão geral
            behaviors_df: DataFrame de comportamentos
            drivers_df: DataFrame de direcionadores
            stats_data: Dados de estatísticas do banco (opcional)
        """
        if not EXCEL_AVAILABLE:
            print("Exportação para Excel não disponível (falta o pacote openpyxl)")
            return
            
        # Verificar se temos dados
        if overview_df.empty and behaviors_df.empty and drivers_df.empty and not stats_data:
            print("Sem dados suficientes para gerar relatório Excel")
            return
        
        excel_file = self.output_dir / 'consolidated_report.xlsx'
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            if not overview_df.empty:
                overview_df.to_excel(writer, sheet_name='Visão Geral', index=False)
                
            if not behaviors_df.empty:
                behaviors_df.to_excel(writer, sheet_name='Comportamentos', index=False)
                
            if not drivers_df.empty:
                drivers_df.to_excel(writer, sheet_name='Direcionadores', index=False)
            
            # Adicionar estatísticas se disponíveis
            if stats_data and 'counts_df' in stats_data:
                stats_data['counts_df'].to_excel(writer, sheet_name='Contagens DB', index=False)
                
                if 'perf_df' in stats_data and not stats_data['perf_df'].empty:
                    stats_data['perf_df'].to_excel(writer, sheet_name='Performance', index=False)
            
            # Adicionar uma aba com informações sobre o relatório
            info_df = pd.DataFrame({
                'Informação': ['Data de Geração', 'Versão', 'Análise', 'Tempo Total (s)'],
                'Valor': [datetime.now().strftime('%d/%m/%Y %H:%M'), 
                         '1.0.0', 
                         'People Analytics com DuckDB',
                         round(self.performance_metrics.get('total_report_time', 0), 4)]
            })
            info_df.to_excel(writer, sheet_name='Informações', index=False)
        
        print(f"Relatório Excel consolidado salvo em: {excel_file}")
    
    def close(self):
        """Fecha a conexão com o banco de dados"""
        if hasattr(self, 'conn'):
            self.conn.close()


def main():
    """Função principal do programa"""
    parser = argparse.ArgumentParser(description='Analisador People Analytics com DuckDB')
    parser.add_argument('--data_dir', default='data', help='Diretório contendo os dados JSON')
    parser.add_argument('--output_dir', default='output', help='Diretório para salvar os resultados')
    parser.add_argument('--db_path', default='people_analytics.duckdb', help='Caminho para o banco de dados DuckDB')
    parser.add_argument('--report_types', nargs='+', default=None, 
                       choices=['overview', 'behaviors', 'drivers', 'people', 'stats', 'all'],
                       help='Tipos de relatório a gerar (overview, behaviors, drivers, people, stats ou all)')
    parser.add_argument('--only_import', action='store_true', help='Apenas importa os dados, sem gerar relatórios')
    parser.add_argument('--batch_size', type=int, default=10, help='Tamanho do lote para importação em massa')
    parser.add_argument('--only_stats', action='store_true', help='Apenas gera estatísticas do banco, sem relatórios analíticos')
    
    args = parser.parse_args()
    
    try:
        start_time = time.time()
        
        analyzer = DuckDBAnalyzer(
            data_dir=args.data_dir,
            output_dir=args.output_dir,
            db_path=args.db_path
        )
        
        # Registrar tempo de inicialização
        analyzer.performance_metrics['init_time'] = time.time() - start_time
        
        # Importar dados
        import_start = time.time()
        imported_count = analyzer.import_data(batch_size=args.batch_size)
        analyzer.performance_metrics['import_time'] = time.time() - import_start
        
        # Se flag only_stats, apenas gerar estatísticas
        if args.only_stats:
            analyzer.generate_stats_report()
            analyzer.print_stats()
            return
            
        # Se flag only_import, terminar após a importação
        if args.only_import:
            print("Importação concluída. Relatórios não gerados (--only_import)")
            return
        
        # Determinar os tipos de relatório a gerar
        report_types = None  # Default: todos
        if args.report_types:
            if 'all' in args.report_types:
                report_types = None  # Manter como None para gerar todos
            else:
                report_types = args.report_types
        
        # Gerar relatório completo
        analyzer.generate_full_report(report_types=report_types)
        
    except Exception as e:
        print(f"Erro durante a execução: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if 'analyzer' in locals():
            total_time = time.time() - start_time
            print(f"\nTempo total de execução: {total_time:.2f} segundos")
            analyzer.close()


if __name__ == "__main__":
    main() 