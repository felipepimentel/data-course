"""
Exemplo de ETL usando Apache Airflow para processamento de arquivos JSON.

Este script define um DAG do Airflow que:
1. Escaneia um diretório em busca de novos arquivos JSON
2. Valida a estrutura de cada arquivo
3. Normaliza os dados para um formato padrão
4. Carrega os dados em um banco de dados (SQLite ou MongoDB)
5. Gera relatórios ou visualizações

Dependências:
- apache-airflow
- pandas
- sqlite3 ou pymongo

Para usar este DAG:
1. Instale o Apache Airflow: pip install apache-airflow
2. Copie este arquivo para a pasta de DAGs do Airflow (~/airflow/dags/)
3. Inicie o Airflow: airflow standalone
4. Acesse a interface web: http://localhost:8080
"""

# Importação simulada de bibliotecas do Airflow
# Na instalação real do Airflow, estas importações funcionariam
try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from airflow.operators.bash import BashOperator
    from airflow.sensors.filesystem import FileSensor
    from airflow.models import Variable
    from airflow.utils.dates import days_ago
    AIRFLOW_AVAILABLE = True
except ImportError:
    print("Airflow não está instalado. Este script apenas demonstra a estrutura do DAG.")
    # Classes simuladas para permitir a definição do DAG sem Airflow
    class DAG:
        def __init__(self, **kwargs):
            self.dag_id = kwargs.get('dag_id')
            self.default_args = kwargs.get('default_args')
            self.schedule_interval = kwargs.get('schedule_interval')
            self.catchup = kwargs.get('catchup', False)
    
    class BaseOperator:
        def __init__(self, **kwargs):
            self.task_id = kwargs.get('task_id')
            self.dag = kwargs.get('dag')
    
    class PythonOperator(BaseOperator):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.python_callable = kwargs.get('python_callable')
            self.op_kwargs = kwargs.get('op_kwargs', {})
    
    class BashOperator(BaseOperator):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.bash_command = kwargs.get('bash_command')
    
    class FileSensor(BaseOperator):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.filepath = kwargs.get('filepath')
            self.poke_interval = kwargs.get('poke_interval')
    
    class Variable:
        @staticmethod
        def get(key, default_var=None):
            return default_var
    
    def days_ago(n):
        from datetime import datetime, timedelta
        return datetime.now() - timedelta(days=n)
    
    AIRFLOW_AVAILABLE = False

# Outras importações
import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import pandas as pd

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PeopleAnalyticsETL")

# Funções ETL
def scan_for_new_files(**context):
    """Escanear diretório em busca de novos arquivos JSON"""
    data_dir = context['data_dir']
    pattern = context['file_pattern']
    
    logger.info(f"Escaneando diretório {data_dir} por arquivos {pattern}")
    
    # Encontrar todos os arquivos JSON
    json_files = list(Path(data_dir).glob(pattern))
    logger.info(f"Encontrados {len(json_files)} arquivos")
    
    # Filtrar apenas arquivos novos ou modificados
    processed_files = context.get('processed_files', [])
    new_files = []
    
    for json_file in json_files:
        file_path = str(json_file)
        file_stat = os.stat(file_path)
        last_modified = file_stat.st_mtime
        
        # Verificar se o arquivo é novo ou foi modificado
        is_new = True
        for processed in processed_files:
            if processed['path'] == file_path and processed['last_modified'] == last_modified:
                is_new = False
                break
        
        if is_new:
            new_files.append({
                'path': file_path,
                'last_modified': last_modified,
                'size': file_stat.st_size,
                'person': json_file.parts[-3] if len(json_file.parts) >= 3 else 'unknown',
                'year': json_file.parts[-2] if len(json_file.parts) >= 2 else 'unknown'
            })
    
    logger.info(f"Encontrados {len(new_files)} novos arquivos para processar")
    
    # Passar lista de novos arquivos para próximas tarefas
    context['ti'].xcom_push(key='new_files', value=new_files)
    return new_files

def validate_json_files(**context):
    """Validar estrutura dos arquivos JSON"""
    new_files = context['ti'].xcom_pull(key='new_files', task_ids='scan_for_new_files')
    
    if not new_files:
        logger.info("Nenhum arquivo novo para validar")
        return []
    
    valid_files = []
    invalid_files = []
    
    for file_info in new_files:
        file_path = file_info['path']
        try:
            # Carregar JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validação básica
            is_valid = True
            issues = []
            
            # Verificar estrutura básica
            if 'data' not in data:
                issues.append("Campo 'data' ausente")
                is_valid = False
            elif 'direcionadores' not in data['data']:
                issues.append("Campo 'direcionadores' ausente")
                is_valid = False
            elif not isinstance(data['data']['direcionadores'], list):
                issues.append("Campo 'direcionadores' não é uma lista")
                is_valid = False
            
            # Adicionar resultado da validação
            file_info['valid'] = is_valid
            file_info['issues'] = issues
            
            if is_valid:
                valid_files.append(file_info)
            else:
                invalid_files.append(file_info)
                logger.warning(f"Arquivo inválido: {file_path}. Problemas: {issues}")
        
        except Exception as e:
            logger.error(f"Erro ao validar {file_path}: {str(e)}")
            file_info['valid'] = False
            file_info['issues'] = [str(e)]
            invalid_files.append(file_info)
    
    # Salvar resultados
    context['ti'].xcom_push(key='valid_files', value=valid_files)
    context['ti'].xcom_push(key='invalid_files', value=invalid_files)
    
    logger.info(f"Validação concluída: {len(valid_files)} válidos, {len(invalid_files)} inválidos")
    return valid_files

def transform_data(**context):
    """Transformar dados para formato padrão"""
    valid_files = context['ti'].xcom_pull(key='valid_files', task_ids='validate_json_files')
    
    if not valid_files:
        logger.info("Nenhum arquivo válido para transformar")
        return []
    
    transformed_files = []
    
    for file_info in valid_files:
        file_path = file_info['path']
        try:
            # Carregar JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extrair dados relevantes
            transformed_data = {
                'person': file_info['person'],
                'year': file_info['year'],
                'source_file': file_path,
                'import_date': datetime.now().isoformat(),
                'concept': data.get('data', {}).get('conceito_ciclo_filho_descricao', 'Unknown'),
                'peer_group': data.get('data', {}).get('nome_peer_group', 'Unknown'),
                'behaviors': []
            }
            
            # Processar comportamentos
            total_score = 0
            count = 0
            
            if 'data' in data and 'direcionadores' in data['data']:
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
                                        score_colab = calculate_weighted_score(freq_colab)
                                        score_grupo = calculate_weighted_score(freq_grupo)
                                        difference = score_colab - score_grupo
                                        
                                        # Adicionar ao total
                                        total_score += score_colab
                                        count += 1
                                        
                                        transformed_data['behaviors'].append({
                                            'direcionador': dir_name,
                                            'comportamento': comp_name,
                                            'score': score_colab,
                                            'group_score': score_grupo,
                                            'difference': difference,
                                            'frequencia_colaborador': freq_colab,
                                            'frequencia_grupo': freq_grupo
                                        })
            
            # Calcular score médio
            transformed_data['avg_score'] = total_score / count if count > 0 else 0.0
            
            # Adicionar dados transformados
            file_info['transformed_data'] = transformed_data
            transformed_files.append(file_info)
            logger.info(f"Arquivo transformado: {file_path}")
            
        except Exception as e:
            logger.error(f"Erro ao transformar {file_path}: {str(e)}")
            file_info['transformed'] = False
            file_info['transform_error'] = str(e)
    
    # Salvar resultados
    context['ti'].xcom_push(key='transformed_files', value=transformed_files)
    
    logger.info(f"Transformação concluída: {len(transformed_files)} arquivos")
    return transformed_files

def load_to_database(**context):
    """Carregar dados transformados no banco de dados"""
    transformed_files = context['ti'].xcom_pull(key='transformed_files', task_ids='transform_data')
    db_type = context.get('db_type', 'sqlite')
    db_path = context.get('db_path', 'people_analytics.db')
    
    if not transformed_files:
        logger.info("Nenhum arquivo transformado para carregar no banco de dados")
        return []
    
    if db_type == 'sqlite':
        # Carregar para SQLite
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Criar tabelas se não existirem
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person TEXT,
                year TEXT,
                source_file TEXT UNIQUE,
                concept TEXT,
                peer_group TEXT,
                avg_score REAL,
                import_date TEXT
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS behaviors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evaluation_id INTEGER,
                direcionador TEXT,
                comportamento TEXT,
                score REAL,
                group_score REAL,
                difference REAL,
                frequencia_colaborador TEXT,
                frequencia_grupo TEXT,
                FOREIGN KEY (evaluation_id) REFERENCES evaluations (id)
            )
            ''')
            
            # Inserir dados
            for file_info in transformed_files:
                data = file_info['transformed_data']
                
                # Inserir avaliação
                cursor.execute('''
                INSERT OR REPLACE INTO evaluations 
                (person, year, source_file, concept, peer_group, avg_score, import_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['person'],
                    data['year'],
                    data['source_file'],
                    data['concept'],
                    data['peer_group'],
                    data['avg_score'],
                    data['import_date']
                ))
                
                # Obter ID da avaliação
                evaluation_id = cursor.lastrowid
                
                # Inserir comportamentos
                for behavior in data['behaviors']:
                    cursor.execute('''
                    INSERT INTO behaviors 
                    (evaluation_id, direcionador, comportamento, score, group_score, difference, 
                     frequencia_colaborador, frequencia_grupo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        evaluation_id,
                        behavior['direcionador'],
                        behavior['comportamento'],
                        behavior['score'],
                        behavior['group_score'],
                        behavior['difference'],
                        json.dumps(behavior['frequencia_colaborador']),
                        json.dumps(behavior['frequencia_grupo'])
                    ))
            
            conn.commit()
            conn.close()
            logger.info(f"Dados carregados com sucesso no SQLite: {db_path}")
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados no SQLite: {str(e)}")
            raise
    
    elif db_type == 'mongodb':
        try:
            # Verificar se pymongo está disponível
            try:
                from pymongo import MongoClient
                mongo_available = True
            except ImportError:
                logger.error("PyMongo não está instalado. Não é possível carregar no MongoDB.")
                mongo_available = False
                return []
            
            if mongo_available:
                # Carregar para MongoDB
                client = MongoClient('mongodb://localhost:27017/')
                db = client['people_analytics']
                
                for file_info in transformed_files:
                    data = file_info['transformed_data']
                    
                    # Criar documento para avaliação
                    evaluation_doc = {
                        'person': data['person'],
                        'year': data['year'],
                        'source_file': data['source_file'],
                        'concept': data['concept'],
                        'peer_group': data['peer_group'],
                        'avg_score': data['avg_score'],
                        'import_date': data['import_date'],
                        'behaviors': data['behaviors']
                    }
                    
                    # Inserir no MongoDB
                    db.evaluations.replace_one(
                        {'source_file': data['source_file']},
                        evaluation_doc,
                        upsert=True
                    )
                
                logger.info(f"Dados carregados com sucesso no MongoDB: people_analytics")
        
        except Exception as e:
            logger.error(f"Erro ao carregar dados no MongoDB: {str(e)}")
            raise
    
    return transformed_files

def generate_reports(**context):
    """Gerar relatórios e visualizações"""
    db_type = context.get('db_type', 'sqlite')
    db_path = context.get('db_path', 'people_analytics.db')
    output_dir = context.get('output_dir', 'output')
    
    # Criar diretório de saída
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        if db_type == 'sqlite':
            # Conectar ao SQLite
            conn = sqlite3.connect(db_path)
            
            # Consulta para relatório comparativo
            comparative_df = pd.read_sql_query('''
            SELECT person, year, avg_score, concept
            FROM evaluations
            ORDER BY year DESC, avg_score DESC
            ''', conn)
            
            # Salvar CSV
            comparative_csv = os.path.join(output_dir, 'comparative_report.csv')
            comparative_df.to_csv(comparative_csv, index=False)
            logger.info(f"Relatório comparativo gerado: {comparative_csv}")
            
            # Consulta para comportamentos
            behaviors_df = pd.read_sql_query('''
            SELECT b.direcionador, b.comportamento, AVG(b.score) as avg_score,
                   AVG(b.group_score) as avg_group_score, AVG(b.difference) as avg_difference,
                   COUNT(*) as count
            FROM behaviors b
            GROUP BY b.direcionador, b.comportamento
            ORDER BY avg_difference DESC
            ''', conn)
            
            # Salvar CSV
            behaviors_csv = os.path.join(output_dir, 'behaviors_report.csv')
            behaviors_df.to_csv(behaviors_csv, index=False)
            logger.info(f"Relatório de comportamentos gerado: {behaviors_csv}")
            
            conn.close()
            
        elif db_type == 'mongodb':
            try:
                from pymongo import MongoClient
                mongo_available = True
            except ImportError:
                logger.error("PyMongo não está instalado. Não é possível gerar relatórios do MongoDB.")
                mongo_available = False
                return
            
            if mongo_available:
                # Conectar ao MongoDB
                client = MongoClient('mongodb://localhost:27017/')
                db = client['people_analytics']
                
                # Consulta para relatório comparativo
                comparative_data = list(db.evaluations.find(
                    {},
                    {'_id': 0, 'person': 1, 'year': 1, 'avg_score': 1, 'concept': 1}
                ).sort([('year', -1), ('avg_score', -1)]))
                
                comparative_df = pd.DataFrame(comparative_data)
                
                # Salvar CSV
                comparative_csv = os.path.join(output_dir, 'comparative_report.csv')
                comparative_df.to_csv(comparative_csv, index=False)
                logger.info(f"Relatório comparativo gerado: {comparative_csv}")
                
                # Consulta para comportamentos
                pipeline = [
                    {'$unwind': '$behaviors'},
                    {'$group': {
                        '_id': {
                            'direcionador': '$behaviors.direcionador',
                            'comportamento': '$behaviors.comportamento'
                        },
                        'avg_score': {'$avg': '$behaviors.score'},
                        'avg_group_score': {'$avg': '$behaviors.group_score'},
                        'avg_difference': {'$avg': '$behaviors.difference'},
                        'count': {'$sum': 1}
                    }},
                    {'$sort': {'avg_difference': -1}}
                ]
                
                behaviors_data = list(db.evaluations.aggregate(pipeline))
                
                # Transformar para DataFrame
                behaviors_rows = []
                for item in behaviors_data:
                    behaviors_rows.append({
                        'direcionador': item['_id']['direcionador'],
                        'comportamento': item['_id']['comportamento'],
                        'avg_score': item['avg_score'],
                        'avg_group_score': item['avg_group_score'],
                        'avg_difference': item['avg_difference'],
                        'count': item['count']
                    })
                
                behaviors_df = pd.DataFrame(behaviors_rows)
                
                # Salvar CSV
                behaviors_csv = os.path.join(output_dir, 'behaviors_report.csv')
                behaviors_df.to_csv(behaviors_csv, index=False)
                logger.info(f"Relatório de comportamentos gerado: {behaviors_csv}")
        
        # Gerar arquivo de sumário
        summary_file = os.path.join(output_dir, 'summary.txt')
        with open(summary_file, 'w') as f:
            f.write(f"Relatórios gerados em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Número de avaliações: {len(comparative_df)}\n")
            f.write(f"Anos disponíveis: {', '.join(sorted(comparative_df['year'].unique()))}\n")
            f.write(f"Pessoas avaliadas: {len(comparative_df['person'].unique())}\n")
            if 'avg_score' in comparative_df.columns:
                f.write(f"Score médio geral: {comparative_df['avg_score'].mean():.2f}\n")
            
        logger.info(f"Sumário gerado: {summary_file}")
        
        # Retornar arquivos gerados
        return [comparative_csv, behaviors_csv, summary_file]
    
    except Exception as e:
        logger.error(f"Erro ao gerar relatórios: {str(e)}")
        raise

def calculate_weighted_score(frequencies):
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

# Definir argumentos padrão do DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['your_email@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': days_ago(1)
}

# Definir DAG
dag = DAG(
    dag_id='people_analytics_etl',
    default_args=default_args,
    description='ETL para dados People Analytics',
    schedule_interval=timedelta(days=1),
    catchup=False
)

# Definir tarefas
if AIRFLOW_AVAILABLE:
    # Tarefa para verificar se o diretório de dados existe
    check_data_dir = FileSensor(
        task_id='check_data_dir',
        filepath="{{ var.value.data_dir }}",
        poke_interval=300,  # 5 minutos
        dag=dag
    )
    
    # Tarefa para escanear diretório
    scan_files = PythonOperator(
        task_id='scan_for_new_files',
        python_callable=scan_for_new_files,
        op_kwargs={
            'data_dir': "{{ var.value.data_dir or 'data' }}",
            'file_pattern': "{{ var.value.file_pattern or '*/*/resultado.json' }}",
            'processed_files': []
        },
        dag=dag
    )
    
    # Tarefa para validar arquivos
    validate_files = PythonOperator(
        task_id='validate_json_files',
        python_callable=validate_json_files,
        dag=dag
    )
    
    # Tarefa para transformar dados
    transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
        dag=dag
    )
    
    # Tarefa para carregar dados no banco
    load_db = PythonOperator(
        task_id='load_to_database',
        python_callable=load_to_database,
        op_kwargs={
            'db_type': "{{ var.value.db_type or 'sqlite' }}",
            'db_path': "{{ var.value.db_path or 'people_analytics.db' }}"
        },
        dag=dag
    )
    
    # Tarefa para gerar relatórios
    generate = PythonOperator(
        task_id='generate_reports',
        python_callable=generate_reports,
        op_kwargs={
            'db_type': "{{ var.value.db_type or 'sqlite' }}",
            'db_path': "{{ var.value.db_path or 'people_analytics.db' }}",
            'output_dir': "{{ var.value.output_dir or 'output' }}"
        },
        dag=dag
    )
    
    # Notificação de conclusão
    notify = BashOperator(
        task_id='notify_completion',
        bash_command='echo "ETL concluído com sucesso em $(date)"',
        dag=dag
    )
    
    # Definir dependências
    check_data_dir >> scan_files >> validate_files >> transform >> load_db >> generate >> notify

# Executar localmente (para teste sem Airflow)
if __name__ == "__main__":
    # Configurações para teste local
    context = {
        'data_dir': 'teste',
        'file_pattern': '*/*/resultado.json',
        'db_type': 'sqlite',
        'db_path': 'people_analytics_etl.db',
        'output_dir': 'output',
        'ti': type('', (), {
            'xcom_push': lambda self, key, value: print(f"XCOM Push: {key} -> {len(value)} items"),
            'xcom_pull': lambda self, key, task_ids: []
        })()
    }
    
    # Simular execução do pipeline
    print("\n--- Iniciando teste local do ETL ---")
    print("1. Escaneando diretório...")
    
    # Criar diretório de teste se não existir
    os.makedirs(context['data_dir'], exist_ok=True)
    
    # Executar tarefas
    new_files = scan_for_new_files(**context)
    context['ti'].xcom_pull = lambda key, task_ids: new_files
    
    print("2. Validando arquivos...")
    valid_files = validate_json_files(**context)
    context['ti'].xcom_pull = lambda key, task_ids: valid_files if task_ids == 'validate_json_files' else new_files
    
    print("3. Transformando dados...")
    transformed_files = transform_data(**context)
    context['ti'].xcom_pull = lambda key, task_ids: transformed_files if task_ids == 'transform_data' else valid_files
    
    print("4. Carregando no banco de dados...")
    try:
        loaded_files = load_to_database(**context)
        print(f"   Carregados {len(loaded_files)} arquivos no banco")
    except Exception as e:
        print(f"   Erro ao carregar no banco: {str(e)}")
    
    print("5. Gerando relatórios...")
    try:
        reports = generate_reports(**context)
        print(f"   Relatórios gerados: {reports}")
    except Exception as e:
        print(f"   Erro ao gerar relatórios: {str(e)}")
    
    print("\n--- ETL local concluído ---")
    print("Para executar com Airflow, instale-o e copie este arquivo para a pasta de DAGs.") 