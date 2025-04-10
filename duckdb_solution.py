"""
Solução para análise de dados People Analytics usando DuckDB.

DuckDB é um banco de dados analítico embutido que não requer instalação 
de um servidor separado, similar ao SQLite mas otimizado para análises.

Esta implementação:
1. Importa dados de arquivos JSON
2. Armazena-os em um banco DuckDB
3. Realiza análises usando DuckDB
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
    raise ImportError("DuckDB é necessário para esta solução")

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
        self.performance_metrics = {}
        
        # Criar diretório de saída
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Conectar ao banco de dados
        start_time = time.time()
        self.conn = duckdb.connect(self.db_path)
        print(f"Usando DuckDB - banco de dados: {self.db_path}")
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
        
        # Tabela de pessoas
        cursor.execute('''
        CREATE SEQUENCE IF NOT EXISTS people_id_seq;
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER DEFAULT nextval('people_id_seq') PRIMARY KEY,
            name VARCHAR UNIQUE
        )
        ''')
        
        # Tabela de perfis
        cursor.execute('''
        CREATE SEQUENCE IF NOT EXISTS profiles_id_seq;
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER DEFAULT nextval('profiles_id_seq') PRIMARY KEY,
            person_id INTEGER,
            year INTEGER,
            nome_completo VARCHAR,
            funcional VARCHAR,
            funcional_gestor VARCHAR,
            nome_gestor VARCHAR,
            cargo VARCHAR,
            codigo_cargo VARCHAR,
            nivel_cargo VARCHAR,
            nome_nivel_cargo VARCHAR,
            nome_departamento VARCHAR,
            tipo_carreira VARCHAR,
            codigo_comunidade VARCHAR,
            nome_comunidade VARCHAR,
            codigo_squad VARCHAR,
            nome_squad VARCHAR,
            codigo_papel VARCHAR,
            nome_papel VARCHAR,
            tipo_gestao BOOLEAN,
            is_congelamento BOOLEAN,
            data_congelamento DATE,
            FOREIGN KEY (person_id) REFERENCES people (id)
        )
        ''')
        
        # Tabela de frequências
        cursor.execute('''
        CREATE SEQUENCE IF NOT EXISTS attendance_id_seq;
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER DEFAULT nextval('attendance_id_seq') PRIMARY KEY,
            person_id INTEGER,
            year INTEGER,
            date DATE,
            present BOOLEAN,
            notes VARCHAR,
            FOREIGN KEY (person_id) REFERENCES people (id)
        )
        ''')
        
        # Tabela de pagamentos
        cursor.execute('''
        CREATE SEQUENCE IF NOT EXISTS payments_id_seq;
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER DEFAULT nextval('payments_id_seq') PRIMARY KEY,
            person_id INTEGER,
            year INTEGER,
            date DATE,
            amount DOUBLE,
            reference VARCHAR,
            FOREIGN KEY (person_id) REFERENCES people (id)
        )
        ''')
        
        # Tabela de arquivos importados
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_imports (
            file_path VARCHAR PRIMARY KEY,
            import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        self.conn.commit()
    
    def _create_indexes(self):
        """Cria índices para melhorar a performance das consultas"""
        cursor = self.conn.cursor()
        
        try:
            # Índices para profiles
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_profiles_person_id ON profiles(person_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_profiles_year ON profiles(year)")
            
            # Índices para attendance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_person_id ON attendance(person_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_year ON attendance(year)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date)")
            
            # Índices para payments
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_person_id ON payments(person_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_year ON payments(year)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(date)")
            
            self.conn.commit()
            
        except Exception as e:
            print(f"Aviso: Não foi possível criar índices: {str(e)}")
    
    def _is_empty_file(self, file_path: Path) -> bool:
        """
        Verifica se um arquivo está vazio ou contém apenas JSON vazio
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            True se o arquivo estiver vazio ou contiver apenas JSON vazio
        """
        if not file_path.exists() or not file_path.is_file():
            return True
            
        # Verificar tamanho do arquivo
        if file_path.stat().st_size == 0:
            return True
            
        # Verificar conteúdo JSON
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content or content == '{}' or content == '[]':
                    return True
                    
                # Tentar carregar o JSON para verificar estrutura
                data = json.loads(content)
                if not data:
                    return True
                    
                return False
        except:
            return True

    def _is_empty_directory(self, directory: Path) -> bool:
        """
        Verifica se um diretório está vazio ou contém apenas arquivos vazios
        
        Args:
            directory: Caminho do diretório
            
        Returns:
            True se o diretório estiver vazio ou contiver apenas arquivos vazios
        """
        if not directory.exists() or not directory.is_dir():
            return True
            
        # Verificar se diretório está vazio
        if not any(directory.iterdir()):
            return True
            
        # Verificar se todos os arquivos estão vazios
        for item in directory.iterdir():
            if item.is_file():
                if not self._is_empty_file(item):
                    return False
            elif item.is_dir():
                if not self._is_empty_directory(item):
                    return False
                    
        return True

    def scan_files(self) -> List[Dict]:
        """
        Escaneia o diretório de dados por arquivos JSON
        
        Returns:
            Lista de informações sobre os arquivos encontrados
        """
        # Padrões de arquivo a procurar
        patterns = [
            "**/*/resultado.json",  # Formato legado
            "**/*/data.json",       # Novo formato
            "**/*/perfil.json",     # Arquivo de perfil
            "**/*/frequencias.json", # Arquivo de frequências
            "**/*/pagamentos.json"   # Arquivo de pagamentos
        ]
        
        json_files = []
        for pattern in patterns:
            json_files.extend(list(self.data_dir.glob(pattern)))
        
        # Verificar arquivos já importados
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT file_path FROM file_imports")
        existing_files = [row[0] for row in cursor.fetchall()]
        
        # Filtrar apenas novos arquivos não vazios
        new_files = []
        for json_file in json_files:
            file_path = str(json_file.absolute())
            
            # Pular arquivos já importados
            if file_path in existing_files:
                continue
                
            # Pular arquivos vazios
            if self._is_empty_file(json_file):
                print(f"Pulando arquivo vazio: {json_file}")
                continue
                
            # Extrair informações do caminho
            parts = json_file.parts
            person = parts[-3] if len(parts) >= 3 else "unknown"
            year = parts[-2] if len(parts) >= 2 else "unknown"
            file_type = json_file.stem
            
            new_files.append({
                'person': person,
                'year': year,
                'type': file_type,
                'path': file_path
            })
        
        print(f"Encontrados {len(new_files)} novos arquivos válidos para importar")
        return new_files
    
    def import_data(self, batch_size: int = 10) -> int:
        """
        Importa dados dos arquivos JSON para o banco
        
        Args:
            batch_size: Tamanho do lote para importação em massa
            
        Returns:
            Número de arquivos importados
        """
        # Escanear arquivos
        new_files = self.scan_files()
        if not new_files:
            return 0
        
        cursor = self.conn.cursor()
        imported_count = 0
        skipped_count = 0
        
        # Usar tqdm para mostrar barra de progresso
        with tqdm.tqdm(total=len(new_files), desc="Importando arquivos") as pbar:
            for file_info in new_files:
                try:
                    # Verificar se o arquivo ainda é válido
                    if self._is_empty_file(Path(file_info['path'])):
                        print(f"Arquivo se tornou inválido durante importação: {file_info['path']}")
                        skipped_count += 1
                        pbar.update(1)
                        continue
                    
                    # Iniciar transação para este arquivo
                    self.conn.execute("BEGIN TRANSACTION")
                    
                    # Carregar dados do arquivo
                    with open(file_info['path'], 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Extrair dados básicos
                    person_name = file_info['person']
                    year = int(file_info['year'])
                    file_path = file_info['path']
                    file_type = file_info['type']
                    
                    # Inserir pessoa se não existir
                    cursor.execute("""
                    INSERT INTO people (name)
                    SELECT ? WHERE NOT EXISTS (SELECT 1 FROM people WHERE name = ?)
                    """, (person_name, person_name))
                    
                    # Obter ID da pessoa
                    cursor.execute("SELECT id FROM people WHERE name = ?", (person_name,))
                    person_id = cursor.fetchone()[0]
                    
                    # Processar dados baseado no tipo de arquivo
                    if file_type == 'resultado':
                        # Formato legado
                        if 'frequencias' in data:
                            for freq in data['frequencias']:
                                cursor.execute("""
                                INSERT INTO attendance (person_id, year, date, present, notes)
                                VALUES (?, ?, ?, ?, ?)
                                """, (
                                    person_id,
                                    year,
                                    freq['data'],
                                    freq['status'] == 'presente',
                                    freq.get('justificativa', '')
                                ))
                        
                        if 'pagamentos' in data:
                            for pag in data['pagamentos']:
                                cursor.execute("""
                                INSERT INTO payments (person_id, year, date, amount, reference)
                                VALUES (?, ?, ?, ?, ?)
                                """, (
                                    person_id,
                                    year,
                                    pag['data'],
                                    pag['valor'],
                                    pag.get('descricao', '')
                                ))
                                
                    elif file_type == 'frequencias':
                        # Novo formato - frequências
                        for freq in data:
                            cursor.execute("""
                            INSERT INTO attendance (person_id, year, date, present, notes)
                            VALUES (?, ?, ?, ?, ?)
                            """, (
                                person_id,
                                year,
                                freq['data'],
                                freq['status'] == 'presente',
                                freq.get('justificativa', '')
                            ))
                            
                    elif file_type == 'pagamentos':
                        # Novo formato - pagamentos
                        for pag in data:
                            cursor.execute("""
                            INSERT INTO payments (person_id, year, date, amount, reference)
                            VALUES (?, ?, ?, ?, ?)
                            """, (
                                person_id,
                                year,
                                pag['data'],
                                pag['valor'],
                                pag.get('descricao', '')
                            ))
                            
                    elif file_type == 'perfil':
                        # Perfil
                        cursor.execute("""
                        INSERT INTO profiles (
                            person_id, year, nome_completo, funcional, funcional_gestor,
                            nome_gestor, cargo, codigo_cargo, nivel_cargo, nome_nivel_cargo,
                            nome_departamento, tipo_carreira, codigo_comunidade, nome_comunidade,
                            codigo_squad, nome_squad, codigo_papel, nome_papel,
                            tipo_gestao, is_congelamento, data_congelamento
                        ) VALUES (
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                        )
                        """, (
                            person_id,
                            year,
                            data.get('nome_completo', ''),
                            data.get('funcional', ''),
                            data.get('funcional_gestor'),
                            data.get('nome_gestor'),
                            data.get('cargo', ''),
                            data.get('codigo_cargo', ''),
                            data.get('nivel_cargo', ''),
                            data.get('nome_nivel_cargo', ''),
                            data.get('nome_departamento', ''),
                            data.get('tipo_carreira'),
                            data.get('codigo_comunidade'),
                            data.get('nome_comunidade'),
                            data.get('codigo_squad'),
                            data.get('nome_squad'),
                            data.get('codigo_papel'),
                            data.get('nome_papel'),
                            bool(data.get('tipo_gestao', False)),
                            bool(data.get('is_congelamento', False)),
                            data.get('data_congelamento')
                        ))
                    
                    # Registrar arquivo importado
                    cursor.execute("""
                    INSERT INTO file_imports (file_path, import_date)
                    VALUES (?, CURRENT_TIMESTAMP)
                    """, (file_path,))
                    
                    # Commit da transação
                    self.conn.commit()
                    imported_count += 1
                    
                except Exception as e:
                    print(f"Erro ao importar {file_info['path']}: {str(e)}")
                    self.conn.execute("ROLLBACK")
                    skipped_count += 1
                
                finally:
                    pbar.update(1)
        
        print(f"Importação concluída: {imported_count} arquivos importados, {skipped_count} pulados")
        return imported_count

    def analyze_attendance(self, year: Optional[int] = None) -> pd.DataFrame:
        """
        Analisa dados de frequência
        
        Args:
            year: Ano específico para análise (opcional)
            
        Returns:
            DataFrame com análise de frequência
        """
        query = """
        WITH attendance_stats AS (
            SELECT 
                p.name,
                a.year,
                COUNT(*) as total_days,
                SUM(CASE WHEN a.present THEN 1 ELSE 0 END) as present_days,
                CAST(SUM(CASE WHEN a.present THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) as attendance_rate
            FROM people p
            JOIN attendance a ON p.id = a.person_id
            WHERE 1=1
        """
        
        if year is not None:
            query += f" AND a.year = {year}"
            
        query += """
            GROUP BY p.name, a.year
        )
        SELECT 
            name,
            year,
            total_days,
            present_days,
            ROUND(attendance_rate * 100, 2) as attendance_rate
        FROM attendance_stats
        ORDER BY name, year
        """
        
        return self.conn.execute(query).df()

    def analyze_payments(self, year: Optional[int] = None) -> pd.DataFrame:
        """
        Analisa dados de pagamentos
        
        Args:
            year: Ano específico para análise (opcional)
            
        Returns:
            DataFrame com análise de pagamentos
        """
        query = """
        WITH payment_stats AS (
            SELECT 
                p.name,
                pay.year,
                COUNT(*) as total_payments,
                SUM(pay.amount) as total_amount,
                AVG(pay.amount) as avg_amount,
                MIN(pay.amount) as min_amount,
                MAX(pay.amount) as max_amount
            FROM people p
            JOIN payments pay ON p.id = pay.person_id
            WHERE 1=1
        """
        
        if year is not None:
            query += f" AND pay.year = {year}"
            
        query += """
            GROUP BY p.name, pay.year
        )
        SELECT 
            name,
            year,
            total_payments,
            ROUND(total_amount, 2) as total_amount,
            ROUND(avg_amount, 2) as avg_amount,
            ROUND(min_amount, 2) as min_amount,
            ROUND(max_amount, 2) as max_amount
        FROM payment_stats
        ORDER BY name, year
        """
        
        return self.conn.execute(query).df()

    def generate_summary(self, output_format: str = 'html') -> str:
        """
        Gera um resumo dos dados
        
        Args:
            output_format: Formato de saída ('html' ou 'json')
            
        Returns:
            Caminho do arquivo gerado
        """
        # Obter dados de frequência e pagamentos
        attendance_data = self.analyze_attendance()
        payment_data = self.analyze_payments()
        
        # Criar diretório de saída
        summary_dir = self.output_dir / 'summary'
        summary_dir.mkdir(exist_ok=True)
        
        # Gerar nome do arquivo com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format == 'html':
            # Criar HTML
            style = """
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                    margin-bottom: 20px;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #f2f2f2;
                }
                tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                h2 {
                    color: #333;
                }
            """
            
            html_content = f"""
            <html>
            <head>
                <title>People Analytics - Resumo</title>
                <style>
                {style}
                </style>
            </head>
            <body>
                <h1>People Analytics - Resumo</h1>
                
                <h2>Frequência</h2>
                {attendance_data.to_html(index=False)}
                
                <h2>Pagamentos</h2>
                {payment_data.to_html(index=False)}
            </body>
            </html>
            """
            
            # Salvar HTML
            output_file = summary_dir / f"summary_{timestamp}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
        else:  # JSON
            # Criar dicionário com dados
            summary_data = {
                'attendance': attendance_data.to_dict(orient='records'),
                'payments': payment_data.to_dict(orient='records')
            }
            
            # Salvar JSON
            output_file = summary_dir / f"summary_{timestamp}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2)
        
        return str(output_file)

    def plot_attendance(self, year: Optional[int] = None) -> str:
        """
        Gera gráfico de frequência
        
        Args:
            year: Ano específico para análise (opcional)
            
        Returns:
            Caminho do arquivo gerado
        """
        # Obter dados
        data = self.analyze_attendance(year)
        
        # Criar plot
        plt.figure(figsize=(12, 6))
        
        # Barplot de taxa de frequência
        sns.barplot(data=data, x='name', y='attendance_rate')
        
        # Customizar
        plt.title('Taxa de Frequência por Pessoa')
        plt.xlabel('Pessoa')
        plt.ylabel('Taxa de Frequência (%)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Salvar
        plots_dir = self.output_dir / 'plots'
        plots_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = plots_dir / f"attendance_plot_{timestamp}.png"
        
        plt.savefig(output_file)
        plt.close()
        
        return str(output_file)

    def plot_payments(self, year: Optional[int] = None) -> str:
        """
        Gera gráfico de pagamentos
        
        Args:
            year: Ano específico para análise (opcional)
            
        Returns:
            Caminho do arquivo gerado
        """
        # Obter dados
        data = self.analyze_payments(year)
        
        # Criar plot
        plt.figure(figsize=(12, 6))
        
        # Barplot de média de pagamentos
        sns.barplot(data=data, x='name', y='avg_amount')
        
        # Customizar
        plt.title('Média de Pagamentos por Pessoa')
        plt.xlabel('Pessoa')
        plt.ylabel('Valor Médio (R$)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Salvar
        plots_dir = self.output_dir / 'plots'
        plots_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = plots_dir / f"payment_plot_{timestamp}.png"
        
        plt.savefig(output_file)
        plt.close()
        
        return str(output_file)

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Análise de dados People Analytics')
    parser.add_argument('--data_dir', default='data', help='Diretório com dados')
    parser.add_argument('--output_dir', default='output', help='Diretório para saída')
    parser.add_argument('--year', type=int, help='Ano específico para análise')
    args = parser.parse_args()
    
    # Criar analisador
    analyzer = DuckDBAnalyzer(args.data_dir, args.output_dir)
    
    # Importar dados
    print("\nImportando dados...")
    analyzer.import_data()
    
    # Gerar análises
    print("\nGerando análises...")
    analyzer.analyze_attendance(args.year)
    analyzer.analyze_payments(args.year)
    
    # Gerar visualizações
    print("\nGerando visualizações...")
    analyzer.plot_attendance(args.year)
    analyzer.plot_payments(args.year)
    
    # Gerar resumo
    print("\nGerando resumo...")
    summary_file = analyzer.generate_summary()
    print(f"Resumo salvo em: {summary_file}")

if __name__ == '__main__':
    main() 