import json
import os
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sqlite_ingestion.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SQLiteIngestion")

class SQLiteJSONIngestion:
    """Classe para ingestão de JSONs em banco SQLite"""
    
    def __init__(self, db_path="data.db"):
        """Inicializar com caminho para o banco de dados"""
        self.db_path = db_path
        self._setup_database()
        
    def _setup_database(self):
        """Configurar o banco de dados e suas tabelas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabela para dados extraídos
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person TEXT,
                year TEXT,
                source_file TEXT,
                concept TEXT,
                avg_score REAL,
                behaviors TEXT,
                import_date TEXT
            )
            ''')
            
            # Tabela para armazenar JSONs brutos
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS raw_json (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person TEXT,
                year TEXT,
                source_file TEXT,
                raw_data TEXT,
                import_date TEXT
            )
            ''')
            
            # Tabela para comportamentos individuais (normalização)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS behaviors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evaluation_id INTEGER,
                direcionador TEXT,
                comportamento TEXT,
                score REAL,
                group_score REAL,
                difference REAL,
                FOREIGN KEY (evaluation_id) REFERENCES evaluations (id)
            )
            ''')
            
            # Índices para performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_person ON evaluations (person)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_year ON evaluations (year)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_eval_id ON behaviors (evaluation_id)')
            
            conn.commit()
            conn.close()
            logger.info(f"Banco de dados configurado em {self.db_path}")
        except Exception as e:
            logger.error(f"Erro ao configurar banco de dados: {str(e)}")
            raise
    
    def ingest_jsons(self, json_dir, pattern="**/*.json"):
        """Ingerir JSONs de um diretório para o banco de dados"""
        try:
            # Encontrar todos os arquivos JSON
            json_files = list(Path(json_dir).glob(pattern))
            logger.info(f"Encontrados {len(json_files)} arquivos JSON em {json_dir}")
            
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.db_path)
            
            imported_count = 0
            skipped_count = 0
            error_count = 0
            
            for json_file in json_files:
                try:
                    # Verificar se arquivo já foi importado
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM raw_json WHERE source_file = ?", (str(json_file),))
                    if cursor.fetchone():
                        logger.debug(f"Arquivo já importado: {json_file}")
                        skipped_count += 1
                        continue
                    
                    # Extrair identificadores do caminho
                    try:
                        person = json_file.parts[-3]
                        year = json_file.parts[-2]
                    except IndexError:
                        # Tenta encontrar de outras formas
                        path_parts = str(json_file).split('/')
                        person = "unknown"
                        year = "unknown"
                        for part in path_parts:
                            if part.isdigit() and len(part) == 4:
                                year = part
                    
                    # Carregar JSON
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Extrair dados relevantes
                    extracted_data = self.extract_data_from_json(data)
                    
                    # Adicionar metadados
                    extracted_data['person'] = person
                    extracted_data['year'] = year
                    extracted_data['source_file'] = str(json_file)
                    extracted_data['import_date'] = datetime.now().isoformat()
                    
                    # Inserir dados extraídos
                    df = pd.DataFrame([extracted_data])
                    df.to_sql('evaluations', conn, if_exists='append', index=False)
                    
                    # Obter ID da avaliação inserida
                    cursor.execute("SELECT last_insert_rowid()")
                    evaluation_id = cursor.fetchone()[0]
                    
                    # Inserir comportamentos normalizados
                    self.insert_behaviors(conn, evaluation_id, data, person, year)
                    
                    # Salvar JSON original
                    pd.DataFrame([{
                        'person': person,
                        'year': year,
                        'source_file': str(json_file),
                        'raw_data': json.dumps(data),
                        'import_date': datetime.now().isoformat()
                    }]).to_sql('raw_json', conn, if_exists='append', index=False)
                    
                    imported_count += 1
                    logger.debug(f"Importado com sucesso: {json_file}")
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"Erro ao processar {json_file}: {str(e)}")
            
            conn.commit()
            conn.close()
            
            logger.info(f"Importação concluída: {imported_count} importados, {skipped_count} ignorados, {error_count} erros")
            return imported_count, skipped_count, error_count
            
        except Exception as e:
            logger.error(f"Erro na ingestão: {str(e)}")
            raise
    
    def extract_data_from_json(self, data):
        """Extrair dados relevantes de qualquer formato de JSON"""
        result = {
            'concept': 'Unknown',
            'avg_score': 0.0,
            'behaviors': '[]'
        }
        
        try:
            # Formato padrão
            if 'data' in data and isinstance(data['data'], dict):
                # Extrair conceito
                if 'conceito_ciclo_filho_descricao' in data['data']:
                    result['concept'] = data['data']['conceito_ciclo_filho_descricao']
                
                # Extrair comportamentos
                behaviors = []
                scores = []
                
                if 'direcionadores' in data['data']:
                    for direcionador in data['data']['direcionadores']:
                        if 'comportamentos' in direcionador:
                            for comp in direcionador['comportamentos']:
                                if 'comportamento' in comp:
                                    behaviors.append(comp['comportamento'])
                                    
                                    # Tentar extrair score
                                    if 'avaliacoes_grupo' in comp:
                                        for aval in comp['avaliacoes_grupo']:
                                            if 'frequencia_colaborador' in aval and isinstance(aval['frequencia_colaborador'], list):
                                                freq = aval['frequencia_colaborador']
                                                if len(freq) >= 5:
                                                    # Cálculo simplificado de score
                                                    weighted_sum = sum(f * i for i, f in enumerate(freq))
                                                    total = sum(freq)
                                                    if total > 0:
                                                        scores.append(weighted_sum / total)
                    
                    result['behaviors'] = json.dumps(behaviors)
                    
                    # Calcular score médio
                    if scores:
                        result['avg_score'] = sum(scores) / len(scores)
            
            # Se formato diferente, tentar outros esquemas conhecidos
            # Formato alternativo 1
            elif 'evaluation' in data and 'scores' in data['evaluation']:
                result['concept'] = data['evaluation'].get('concept', 'Unknown')
                if isinstance(data['evaluation']['scores'], list):
                    result['avg_score'] = sum(data['evaluation']['scores']) / len(data['evaluation']['scores'])
                    
            # Formato alternativo 2
            elif 'results' in data and isinstance(data['results'], dict):
                if 'concept' in data['results']:
                    result['concept'] = data['results']['concept']
                if 'average_score' in data['results']:
                    result['avg_score'] = data['results']['average_score']
                if 'behaviors' in data['results'] and isinstance(data['results']['behaviors'], list):
                    result['behaviors'] = json.dumps([b.get('name', '') for b in data['results']['behaviors']])
        
        except Exception as e:
            logger.warning(f"Erro ao extrair dados do JSON: {str(e)}")
        
        return result
    
    def insert_behaviors(self, conn, evaluation_id, data, person, year):
        """Inserir comportamentos normalizados"""
        try:
            if 'data' not in data or 'direcionadores' not in data['data']:
                return
            
            behaviors = []
            
            for direcionador in data['data']['direcionadores']:
                dir_name = direcionador.get('direcionador', 'Desconhecido')
                
                if 'comportamentos' not in direcionador:
                    continue
                    
                for comp in direcionador['comportamentos']:
                    comp_name = comp.get('comportamento', 'Desconhecido')
                    
                    if 'avaliacoes_grupo' not in comp:
                        continue
                        
                    for aval in comp['avaliacoes_grupo']:
                        if aval.get('avaliador') == '%todos':  # Considerar apenas avaliação geral
                            freq_colab = aval.get('frequencia_colaborador', [])
                            freq_grupo = aval.get('frequencia_grupo', [])
                            
                            # Calcular scores
                            score_colab = self.calculate_weighted_score(freq_colab)
                            score_grupo = self.calculate_weighted_score(freq_grupo)
                            difference = score_colab - score_grupo
                            
                            behaviors.append({
                                'evaluation_id': evaluation_id,
                                'direcionador': dir_name,
                                'comportamento': comp_name,
                                'score': score_colab,
                                'group_score': score_grupo,
                                'difference': difference
                            })
            
            if behaviors:
                pd.DataFrame(behaviors).to_sql('behaviors', conn, if_exists='append', index=False)
                
        except Exception as e:
            logger.warning(f"Erro ao inserir comportamentos: {str(e)}")
    
    def calculate_weighted_score(self, frequencies):
        """Calcular score ponderado a partir das frequências"""
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
    
    def query_data(self, query):
        """Executar consulta SQL no banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            result = pd.read_sql_query(query, conn)
            conn.close()
            return result
        except Exception as e:
            logger.error(f"Erro ao executar consulta: {str(e)}")
            raise

# Exemplo de uso
if __name__ == "__main__":
    # Diretório de testes
    test_dir = "teste"
    
    # Criar diretório se não existir
    os.makedirs(test_dir, exist_ok=True)
    
    # Instanciar a classe
    ingestion = SQLiteJSONIngestion("people_analytics.db")
    
    # Ingerir JSONs
    imported, skipped, errors = ingestion.ingest_jsons(test_dir, "*/*/resultado.json")
    
    print(f"\nResultados da importação:")
    print(f"- Arquivos importados: {imported}")
    print(f"- Arquivos ignorados: {skipped}")
    print(f"- Erros: {errors}")
    
    # Exemplo de consulta
    print("\nConsulta de exemplo - pessoas por ano:")
    result = ingestion.query_data("SELECT year, COUNT(DISTINCT person) as total_pessoas FROM evaluations GROUP BY year")
    print(result)
    
    print("\nConsulta de exemplo - scores médios:")
    result = ingestion.query_data("SELECT person, year, avg_score FROM evaluations ORDER BY avg_score DESC")
    print(result)
    
    print("\nConsulta de exemplo - comportamentos mais frequentes:")
    result = ingestion.query_data("""
    SELECT comportamento, COUNT(*) as frequencia, AVG(score) as score_medio 
    FROM behaviors 
    GROUP BY comportamento 
    ORDER BY frequencia DESC 
    LIMIT 10
    """)
    print(result) 