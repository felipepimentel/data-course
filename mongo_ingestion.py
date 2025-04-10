import json
import os
import logging
from pathlib import Path
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mongo_ingestion.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MongoDBIngestion")

class MongoDBJSONIngestion:
    """Classe para ingestão de JSONs em banco MongoDB"""
    
    def __init__(self, connection_string="mongodb://localhost:27017/", db_name="people_analytics"):
        """Inicializar com string de conexão e nome do banco de dados"""
        self.connection_string = connection_string
        self.db_name = db_name
        self.client = None
        self.db = None
        self._setup_connection()
        
    def _setup_connection(self):
        """Configurar conexão com o MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.db_name]
            # Verificar conexão
            self.client.admin.command('ping')
            logger.info(f"Conectado ao MongoDB: {self.connection_string}, DB: {self.db_name}")
            
            # Criar índices para performance
            self.db.evaluations.create_index("person")
            self.db.evaluations.create_index("year")
            self.db.evaluations.create_index("source_file", unique=True)
            self.db.evaluations.create_index([("data.direcionadores.comportamentos.comportamento", "text")])
            
        except Exception as e:
            logger.error(f"Erro ao conectar ao MongoDB: {str(e)}")
            raise
    
    def close_connection(self):
        """Fechar conexão com o MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Conexão com MongoDB fechada")
    
    def ingest_jsons(self, json_dir, pattern="**/*.json"):
        """Ingerir JSONs de um diretório para o MongoDB"""
        try:
            # Encontrar todos os arquivos JSON
            json_files = list(Path(json_dir).glob(pattern))
            logger.info(f"Encontrados {len(json_files)} arquivos JSON em {json_dir}")
            
            imported_count = 0
            skipped_count = 0
            error_count = 0
            
            for json_file in json_files:
                try:
                    # Verificar se arquivo já foi importado
                    if self.db.evaluations.find_one({"source_file": str(json_file)}):
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
                    
                    # Extrair metadados
                    metadata = self.extract_metadata(data)
                    
                    # Criar documento
                    document = {
                        "person": person,
                        "year": year,
                        "source_file": str(json_file),
                        "import_date": datetime.now(),
                        "raw_data": data,  # Armazenar JSON completo
                        "metadata": metadata
                    }
                    
                    # Adicionar análise de estrutura
                    document["structure_analysis"] = self.analyze_structure(data)
                    
                    # Inserir no MongoDB
                    result = self.db.evaluations.insert_one(document)
                    
                    # Processar comportamentos separadamente se existirem
                    if "data" in data and "direcionadores" in data["data"]:
                        self.process_behaviors(result.inserted_id, data, person, year)
                    
                    imported_count += 1
                    logger.debug(f"Importado com sucesso: {json_file}")
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"Erro ao processar {json_file}: {str(e)}")
            
            logger.info(f"Importação concluída: {imported_count} importados, {skipped_count} ignorados, {error_count} erros")
            return imported_count, skipped_count, error_count
            
        except Exception as e:
            logger.error(f"Erro na ingestão: {str(e)}")
            raise
    
    def extract_metadata(self, data):
        """Extrair metadados úteis do JSON para facilitar buscas"""
        metadata = {
            "concept": "Unknown",
            "avg_score": 0.0,
            "format_type": "unknown",
            "has_behaviors": False,
            "behavior_count": 0
        }
        
        try:
            # Detectar formato
            if "data" in data and isinstance(data["data"], dict):
                metadata["format_type"] = "standard"
                
                # Extrair conceito
                if "conceito_ciclo_filho_descricao" in data["data"]:
                    metadata["concept"] = data["data"]["conceito_ciclo_filho_descricao"]
                
                # Verificar comportamentos
                if "direcionadores" in data["data"] and isinstance(data["data"]["direcionadores"], list):
                    behavior_count = 0
                    scores = []
                    
                    for direcionador in data["data"]["direcionadores"]:
                        if "comportamentos" in direcionador and isinstance(direcionador["comportamentos"], list):
                            behavior_count += len(direcionador["comportamentos"])
                            
                            # Extrair scores
                            for comp in direcionador["comportamentos"]:
                                if "avaliacoes_grupo" in comp:
                                    for aval in comp["avaliacoes_grupo"]:
                                        if aval.get("avaliador") == "%todos" and "frequencia_colaborador" in aval:
                                            freq = aval["frequencia_colaborador"]
                                            if isinstance(freq, list) and len(freq) >= 5:
                                                # Cálculo de score
                                                weighted_sum = sum(f * i for i, f in enumerate(freq))
                                                total = sum(freq)
                                                if total > 0:
                                                    scores.append(weighted_sum / total)
                    
                    metadata["has_behaviors"] = behavior_count > 0
                    metadata["behavior_count"] = behavior_count
                    
                    # Calcular score médio
                    if scores:
                        metadata["avg_score"] = sum(scores) / len(scores)
            
            # Formato alternativo 1
            elif "evaluation" in data:
                metadata["format_type"] = "evaluation"
                if "concept" in data["evaluation"]:
                    metadata["concept"] = data["evaluation"]["concept"]
                if "scores" in data["evaluation"] and isinstance(data["evaluation"]["scores"], list):
                    metadata["avg_score"] = sum(data["evaluation"]["scores"]) / len(data["evaluation"]["scores"])
                if "behaviors" in data["evaluation"] and isinstance(data["evaluation"]["behaviors"], list):
                    metadata["has_behaviors"] = True
                    metadata["behavior_count"] = len(data["evaluation"]["behaviors"])
            
            # Formato alternativo 2
            elif "results" in data:
                metadata["format_type"] = "results"
                if "concept" in data["results"]:
                    metadata["concept"] = data["results"]["concept"]
                if "average_score" in data["results"]:
                    metadata["avg_score"] = data["results"]["average_score"]
                if "behaviors" in data["results"] and isinstance(data["results"]["behaviors"], list):
                    metadata["has_behaviors"] = True
                    metadata["behavior_count"] = len(data["results"]["behaviors"])
                    
        except Exception as e:
            logger.warning(f"Erro ao extrair metadados: {str(e)}")
        
        return metadata
    
    def analyze_structure(self, data):
        """Analisar estrutura do JSON para identificar problemas e características"""
        analysis = {
            "fields_count": 0,
            "has_nested_objects": False,
            "has_arrays": False,
            "max_nesting_level": 0,
            "potential_issues": []
        }
        
        try:
            # Função recursiva para analisar estrutura
            def analyze_obj(obj, level=0):
                nonlocal analysis
                
                if isinstance(obj, dict):
                    analysis["fields_count"] += len(obj)
                    analysis["max_nesting_level"] = max(analysis["max_nesting_level"], level)
                    analysis["has_nested_objects"] = True
                    
                    # Verificar campos vazios
                    empty_fields = [k for k, v in obj.items() if v is None or v == "" or v == [] or v == {}]
                    if empty_fields:
                        analysis["potential_issues"].append(f"Campos vazios encontrados: {', '.join(empty_fields)}")
                    
                    # Recursão
                    for k, v in obj.items():
                        if isinstance(v, (dict, list)):
                            analyze_obj(v, level + 1)
                
                elif isinstance(obj, list):
                    analysis["has_arrays"] = True
                    
                    # Verificar consistência de arrays
                    if len(obj) > 0:
                        first_type = type(obj[0])
                        if not all(isinstance(item, first_type) for item in obj):
                            analysis["potential_issues"].append("Array com tipos inconsistentes")
                    
                    # Recursão para itens da lista
                    for item in obj:
                        if isinstance(item, (dict, list)):
                            analyze_obj(item, level + 1)
            
            # Iniciar análise
            analyze_obj(data)
            
            # Verificações específicas para o formato conhecido
            if "data" in data and isinstance(data["data"], dict):
                if "direcionadores" not in data["data"]:
                    analysis["potential_issues"].append("Falta campo 'direcionadores'")
                elif not isinstance(data["data"]["direcionadores"], list):
                    analysis["potential_issues"].append("Campo 'direcionadores' não é uma lista")
                elif len(data["data"]["direcionadores"]) == 0:
                    analysis["potential_issues"].append("Lista 'direcionadores' está vazia")
                else:
                    # Verificar comportamentos
                    for i, direcionador in enumerate(data["data"]["direcionadores"]):
                        if "comportamentos" not in direcionador:
                            analysis["potential_issues"].append(f"Direcionador {i+1} não tem 'comportamentos'")
                        elif not isinstance(direcionador["comportamentos"], list):
                            analysis["potential_issues"].append(f"Campo 'comportamentos' em Direcionador {i+1} não é uma lista")
                        elif len(direcionador["comportamentos"]) == 0:
                            analysis["potential_issues"].append(f"Lista 'comportamentos' em Direcionador {i+1} está vazia")
            
        except Exception as e:
            logger.warning(f"Erro ao analisar estrutura: {str(e)}")
            analysis["potential_issues"].append(f"Erro na análise: {str(e)}")
        
        return analysis
    
    def process_behaviors(self, evaluation_id, data, person, year):
        """Processar e armazenar comportamentos separadamente para facilitar análises"""
        try:
            if "data" not in data or "direcionadores" not in data["data"]:
                return
            
            behaviors = []
            
            for direcionador in data["data"]["direcionadores"]:
                dir_name = direcionador.get("direcionador", "Desconhecido")
                
                if "comportamentos" not in direcionador:
                    continue
                    
                for comp in direcionador["comportamentos"]:
                    comp_name = comp.get("comportamento", "Desconhecido")
                    
                    if "avaliacoes_grupo" not in comp:
                        continue
                        
                    for aval in comp["avaliacoes_grupo"]:
                        avaliador = aval.get("avaliador", "Desconhecido")
                        freq_colab = aval.get("frequencia_colaborador", [])
                        freq_grupo = aval.get("frequencia_grupo", [])
                        
                        # Calcular scores
                        score_colab = self.calculate_weighted_score(freq_colab)
                        score_grupo = self.calculate_weighted_score(freq_grupo)
                        difference = score_colab - score_grupo
                        
                        behavior_doc = {
                            "evaluation_id": evaluation_id,
                            "person": person,
                            "year": year,
                            "direcionador": dir_name,
                            "comportamento": comp_name,
                            "avaliador": avaliador,
                            "score": score_colab,
                            "group_score": score_grupo,
                            "difference": difference,
                            "frequencias": {
                                "colaborador": freq_colab,
                                "grupo": freq_grupo
                            },
                            "import_date": datetime.now()
                        }
                        
                        # Inserir no MongoDB
                        self.db.behaviors.insert_one(behavior_doc)
                        behaviors.append(behavior_doc)
            
            # Atualizar documento principal com contagem
            if behaviors:
                self.db.evaluations.update_one(
                    {"_id": evaluation_id},
                    {"$set": {"behaviors_processed": len(behaviors)}}
                )
                
        except Exception as e:
            logger.warning(f"Erro ao processar comportamentos: {str(e)}")
    
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
    
    def query_data(self, collection, query=None, projection=None, limit=100):
        """Consultar dados no MongoDB"""
        try:
            if query is None:
                query = {}
                
            cursor = self.db[collection].find(query, projection).limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Erro ao consultar dados: {str(e)}")
            raise
    
    def aggregate(self, collection, pipeline):
        """Executar agregação no MongoDB"""
        try:
            return list(self.db[collection].aggregate(pipeline))
        except Exception as e:
            logger.error(f"Erro ao executar agregação: {str(e)}")
            raise
    
    def get_statistics(self):
        """Obter estatísticas sobre os dados importados"""
        try:
            stats = {
                "total_evaluations": self.db.evaluations.count_documents({}),
                "total_behaviors": self.db.behaviors.count_documents({}),
                "people_count": len(self.db.evaluations.distinct("person")),
                "years_count": len(self.db.evaluations.distinct("year")),
                "format_types": {}
            }
            
            # Contagem por formato
            format_counts = self.aggregate("evaluations", [
                {"$group": {"_id": "$metadata.format_type", "count": {"$sum": 1}}}
            ])
            
            for item in format_counts:
                stats["format_types"][item["_id"]] = item["count"]
            
            # Scores médios
            avg_pipeline = [
                {"$group": {"_id": None, "avg_score": {"$avg": "$metadata.avg_score"}}}
            ]
            avg_result = list(self.db.evaluations.aggregate(avg_pipeline))
            if avg_result:
                stats["average_score"] = avg_result[0]["avg_score"]
                
            return stats
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            raise

# Exemplo de uso
if __name__ == "__main__":
    try:
        # Verificar se MongoDB está rodando
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print("MongoDB está rodando!")
        
        # Diretório de testes
        test_dir = "teste"
        
        # Criar diretório se não existir
        os.makedirs(test_dir, exist_ok=True)
        
        # Instanciar a classe
        ingestion = MongoDBJSONIngestion()
        
        # Ingerir JSONs
        imported, skipped, errors = ingestion.ingest_jsons(test_dir, "*/*/resultado.json")
        
        print(f"\nResultados da importação MongoDB:")
        print(f"- Arquivos importados: {imported}")
        print(f"- Arquivos ignorados: {skipped}")
        print(f"- Erros: {errors}")
        
        # Estatísticas
        stats = ingestion.get_statistics()
        print("\nEstatísticas do MongoDB:")
        for key, value in stats.items():
            print(f"- {key}: {value}")
        
        # Exemplos de consultas
        print("\nConsulta de exemplo - últimas 3 avaliações:")
        results = ingestion.query_data("evaluations", 
                                      projection={"person": 1, "year": 1, "metadata.concept": 1, "metadata.avg_score": 1}, 
                                      limit=3)
        for doc in results:
            print(f"- {doc['person']} ({doc['year']}): {doc.get('metadata', {}).get('concept', 'N/A')} - Score: {doc.get('metadata', {}).get('avg_score', 0.0):.2f}")
        
        # Comportamentos com maior diferença
        print("\nComportamentos com maior diferença (colaborador vs grupo):")
        diff_behaviors = ingestion.aggregate("behaviors", [
            {"$match": {"avaliador": "%todos"}},
            {"$sort": {"difference": -1}},
            {"$limit": 5},
            {"$project": {"_id": 0, "person": 1, "year": 1, "comportamento": 1, "difference": 1}}
        ])
        
        for behavior in diff_behaviors:
            print(f"- {behavior['person']} ({behavior['year']}): {behavior['comportamento']} - Diferença: {behavior['difference']:.2f}")
        
        # Fechar conexão
        ingestion.close_connection()
        
    except Exception as e:
        print(f"Erro: {str(e)}")
        print("\nObs: Verifique se o MongoDB está instalado e em execução!")
        print("Para instalar o MongoDB: https://www.mongodb.com/try/download/community")
        print("Para iniciar o serviço: sudo systemctl start mongod") 