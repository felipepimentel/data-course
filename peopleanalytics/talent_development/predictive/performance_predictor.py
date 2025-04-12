"""
Modelo Preditivo de Alta Performance.

Utiliza algoritmos de aprendizado de máquina para prever o desempenho
futuro com base em padrões históricos e indicadores comportamentais.
"""
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass
from pathlib import Path
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import ElasticNet
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.impute import SimpleImputer

from peopleanalytics.data_pipeline import DataPipeline


@dataclass
class PerformanceMetric:
    """Representa uma métrica de desempenho de uma pessoa."""
    metric_id: str
    person_id: str
    metric_type: str  # 'avaliação', 'objetivo', 'kpi', etc.
    value: float  # Valor quantitativo
    timestamp: datetime.datetime
    target_value: Optional[float] = None  # Meta (se aplicável)
    context: Dict[str, Any] = None  # Metadados adicionais


@dataclass
class PredictionModel:
    """Modelo de previsão treinado."""
    model_id: str
    model_type: str  # 'rf', 'gbm', 'elastic', etc.
    target_metric: str  # Tipo de métrica prevista
    features: List[str]  # Lista de recursos usados
    creation_date: datetime.datetime
    performance: Dict[str, float]  # Métricas de performance
    parameters: Dict[str, Any]  # Parâmetros do modelo
    pipeline: Any  # Pipeline de ML


class PerformancePredictor:
    """
    Modelo preditivo de alta performance.
    
    Analisa dados históricos para identificar padrões e prever
    tendências futuras de desempenho, permitindo intervenções
    proativas e planejamento de desenvolvimento personalizado.
    """
    
    def __init__(self, data_pipeline: Optional[DataPipeline] = None):
        """
        Inicializa o preditor de performance.
        
        Args:
            data_pipeline: Pipeline de dados opcional para carregar dados existentes
        """
        self.data_pipeline = data_pipeline
        self.performance_metrics = []  # Lista de métricas de desempenho
        self.prediction_models = {}  # model_id -> modelo
        self.feature_importance = {}  # model_id -> importância dos recursos
        self.person_predictions = {}  # person_id -> previsões
        
    def load_data(self) -> bool:
        """
        Carrega dados de métricas de desempenho e modelos.
        
        Returns:
            True se os dados foram carregados com sucesso, False caso contrário
        """
        if not self.data_pipeline:
            return False
            
        try:
            # Carregar métricas de desempenho
            metrics_data = self.data_pipeline.load_performance_metrics()
            
            # Converter para objetos PerformanceMetric
            self.performance_metrics = []
            for metric in metrics_data:
                performance_metric = PerformanceMetric(
                    metric_id=metric['id'],
                    person_id=metric['person_id'],
                    metric_type=metric.get('type', 'avaliação'),
                    value=float(metric.get('value', 0.0)),
                    timestamp=datetime.datetime.fromisoformat(
                        metric.get('timestamp', datetime.datetime.now().isoformat())
                    ),
                    target_value=float(metric.get('target', 0.0)) if 'target' in metric else None,
                    context=metric.get('context', {})
                )
                self.performance_metrics.append(performance_metric)
            
            # Carregar modelos salvos
            model_infos = self.data_pipeline.load_prediction_models_info()
            
            for model_info in model_infos:
                model_id = model_info['id']
                try:
                    # Carregar pipeline do modelo
                    model_path = self.data_pipeline.get_model_path(model_id)
                    pipeline = joblib.load(model_path)
                    
                    # Criar objeto de modelo
                    model = PredictionModel(
                        model_id=model_id,
                        model_type=model_info.get('type', 'unknown'),
                        target_metric=model_info.get('target_metric', ''),
                        features=model_info.get('features', []),
                        creation_date=datetime.datetime.fromisoformat(
                            model_info.get('creation_date', datetime.datetime.now().isoformat())
                        ),
                        performance=model_info.get('performance', {}),
                        parameters=model_info.get('parameters', {}),
                        pipeline=pipeline
                    )
                    
                    # Adicionar ao dicionário
                    self.prediction_models[model_id] = model
                    
                    # Carregar importância dos recursos
                    if 'feature_importance' in model_info:
                        self.feature_importance[model_id] = model_info['feature_importance']
                        
                except Exception as e:
                    print(f"Erro ao carregar modelo {model_id}: {str(e)}")
            
            return True
            
        except Exception as e:
            print(f"Erro ao carregar dados de desempenho: {str(e)}")
            return False
    
    def add_performance_metric(self, 
                             person_id: str,
                             metric_type: str,
                             value: float,
                             timestamp: Optional[datetime.datetime] = None,
                             target_value: Optional[float] = None,
                             context: Optional[Dict[str, Any]] = None) -> PerformanceMetric:
        """
        Adiciona uma nova métrica de desempenho.
        
        Args:
            person_id: ID da pessoa
            metric_type: Tipo de métrica
            value: Valor da métrica
            timestamp: Data/hora da medição
            target_value: Valor alvo/meta
            context: Contexto adicional
            
        Returns:
            Nova métrica de desempenho criada
        """
        # Criar ID único
        metric_id = f"pm_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{person_id}"
        
        # Criar métrica
        metric = PerformanceMetric(
            metric_id=metric_id,
            person_id=person_id,
            metric_type=metric_type,
            value=value,
            timestamp=timestamp or datetime.datetime.now(),
            target_value=target_value,
            context=context or {}
        )
        
        # Adicionar à lista
        self.performance_metrics.append(metric)
        
        # Salvar no pipeline se disponível
        if self.data_pipeline:
            metric_data = {
                'id': metric_id,
                'person_id': person_id,
                'type': metric_type,
                'value': value,
                'timestamp': metric.timestamp.isoformat(),
                'target': target_value,
                'context': context or {}
            }
            
            self.data_pipeline.save_performance_metric(metric_data)
        
        return metric
    
    def prepare_training_data(self, 
                           target_metric: str,
                           lookback_period: int = 6,
                           min_data_points: int = 3) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepara dados de treinamento para um modelo preditivo.
        
        Args:
            target_metric: Tipo de métrica a ser prevista
            lookback_period: Período de dados históricos (em meses)
            min_data_points: Número mínimo de pontos para incluir uma pessoa
            
        Returns:
            Features (X) e valores alvo (y) para treinamento
        """
        # Converter métricas para DataFrame
        metrics_data = []
        for metric in self.performance_metrics:
            metrics_data.append({
                'metric_id': metric.metric_id,
                'person_id': metric.person_id,
                'metric_type': metric.metric_type,
                'value': metric.value,
                'timestamp': metric.timestamp,
                'target_value': metric.target_value
            })
        
        df = pd.DataFrame(metrics_data)
        
        if df.empty:
            raise ValueError("Sem dados suficientes para treinamento")
        
        # Filtrar pela métrica alvo
        target_df = df[df['metric_type'] == target_metric].copy()
        
        if target_df.empty:
            raise ValueError(f"Sem dados para a métrica alvo '{target_metric}'")
        
        # Definir limite de tempo para lookback
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=30 * lookback_period)
        
        # Dados de todas as métricas para features
        features_df = df[df['timestamp'] >= cutoff_date].copy()
        
        # Obter lista de pessoas com dados suficientes
        person_counts = target_df.groupby('person_id').size()
        valid_persons = person_counts[person_counts >= min_data_points].index.tolist()
        
        if not valid_persons:
            raise ValueError(f"Nenhuma pessoa tem dados suficientes (mínimo {min_data_points} pontos)")
        
        # Filtrar apenas pessoas válidas
        features_df = features_df[features_df['person_id'].isin(valid_persons)]
        target_df = target_df[target_df['person_id'].isin(valid_persons)]
        
        # Preparar features: para cada pessoa, criar recursos baseados no histórico
        # de métricas, incluindo média, tendência, volatilidade, etc.
        feature_records = []
        target_values = []
        
        for person_id in valid_persons:
            # Obter última métrica alvo para esta pessoa
            person_targets = target_df[target_df['person_id'] == person_id].sort_values('timestamp')
            
            if person_targets.empty:
                continue
                
            last_target = person_targets.iloc[-1]
            
            # Excluir o último valor target dos dados de feature
            person_features = features_df[
                (features_df['person_id'] == person_id) & 
                (features_df['metric_id'] != last_target['metric_id'])
            ]
            
            if person_features.empty:
                continue
            
            # Agregar métricas por tipo
            person_metrics = {}
            
            for metric_type in person_features['metric_type'].unique():
                type_metrics = person_features[person_features['metric_type'] == metric_type]
                
                if len(type_metrics) > 0:
                    # Calcular estatísticas
                    values = type_metrics['value'].values
                    timestamps = type_metrics['timestamp'].values
                    
                    # Ordenar por timestamp
                    sorted_indices = np.argsort(timestamps)
                    values = values[sorted_indices]
                    
                    person_metrics[f"{metric_type}_mean"] = np.mean(values)
                    person_metrics[f"{metric_type}_recent"] = values[-1]
                    
                    if len(values) > 1:
                        person_metrics[f"{metric_type}_trend"] = (values[-1] - values[0]) / len(values)
                        person_metrics[f"{metric_type}_std"] = np.std(values)
                    else:
                        person_metrics[f"{metric_type}_trend"] = 0
                        person_metrics[f"{metric_type}_std"] = 0
                    
                    # Adicionar contagem
                    person_metrics[f"{metric_type}_count"] = len(values)
            
            # Adicionar dados da pessoa
            if person_metrics:
                person_metrics['person_id'] = person_id
                feature_records.append(person_metrics)
                target_values.append(last_target['value'])
        
        if not feature_records:
            raise ValueError("Não foi possível criar features para nenhuma pessoa")
            
        # Criar DataFrame de features e série de targets
        X = pd.DataFrame(feature_records)
        person_ids = X['person_id']
        X = X.drop(columns=['person_id'])
        y = pd.Series(target_values, index=X.index)
        
        return X, y, person_ids
    
    def train_model(self, 
                  target_metric: str,
                  model_type: str = 'gbm',
                  lookback_period: int = 6,
                  hyperparam_search: bool = False) -> str:
        """
        Treina um novo modelo preditivo.
        
        Args:
            target_metric: Tipo de métrica a ser prevista
            model_type: Tipo de modelo (rf=Random Forest, gbm=Gradient Boosting, elastic=Elastic Net)
            lookback_period: Período de dados históricos (em meses)
            hyperparam_search: Se deve realizar busca de hiperparâmetros
            
        Returns:
            ID do modelo treinado
        """
        # Preparar dados
        X, y, person_ids = self.prepare_training_data(target_metric, lookback_period)
        
        # Dividir em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Definir modelo base
        if model_type == 'rf':
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            params = {
                'regressor__n_estimators': [50, 100, 200],
                'regressor__max_depth': [None, 10, 20, 30]
            }
        elif model_type == 'elastic':
            model = ElasticNet(random_state=42)
            params = {
                'regressor__alpha': [0.1, 0.5, 1.0],
                'regressor__l1_ratio': [0.1, 0.5, 0.7, 0.9]
            }
        else:  # default: gbm
            model_type = 'gbm'
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            params = {
                'regressor__n_estimators': [50, 100, 200],
                'regressor__learning_rate': [0.01, 0.1, 0.2],
                'regressor__max_depth': [3, 5, 7]
            }
        
        # Criar pipeline com preprocessamento
        pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler()),
            ('regressor', model)
        ])
        
        # Treinar com ou sem busca de hiperparâmetros
        if hyperparam_search:
            grid = GridSearchCV(pipeline, params, cv=5, scoring='neg_mean_squared_error')
            grid.fit(X_train, y_train)
            best_pipeline = grid.best_estimator_
            best_params = grid.best_params_
        else:
            best_pipeline = pipeline
            best_pipeline.fit(X_train, y_train)
            best_params = {}
        
        # Avaliar no conjunto de teste
        y_pred = best_pipeline.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        # Extrair importância das features (caso seja árvore)
        feature_importance = {}
        if hasattr(best_pipeline.named_steps['regressor'], 'feature_importances_'):
            importances = best_pipeline.named_steps['regressor'].feature_importances_
            for i, feature in enumerate(X.columns):
                feature_importance[feature] = float(importances[i])
        
        # Criar ID do modelo
        model_id = f"model_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{target_metric}"
        
        # Criar objeto do modelo
        pred_model = PredictionModel(
            model_id=model_id,
            model_type=model_type,
            target_metric=target_metric,
            features=list(X.columns),
            creation_date=datetime.datetime.now(),
            performance={
                'rmse': float(rmse),
                'r2': float(r2)
            },
            parameters=best_params,
            pipeline=best_pipeline
        )
        
        # Adicionar ao dicionário
        self.prediction_models[model_id] = pred_model
        self.feature_importance[model_id] = feature_importance
        
        # Salvar no pipeline se disponível
        if self.data_pipeline:
            # Salvar informações do modelo
            model_info = {
                'id': model_id,
                'type': model_type,
                'target_metric': target_metric,
                'features': list(X.columns),
                'creation_date': pred_model.creation_date.isoformat(),
                'performance': {
                    'rmse': float(rmse),
                    'r2': float(r2)
                },
                'parameters': best_params,
                'feature_importance': feature_importance
            }
            
            self.data_pipeline.save_prediction_model_info(model_info)
            
            # Salvar pipeline do modelo usando joblib
            model_path = self.data_pipeline.save_model_pipeline(model_id, best_pipeline)
        
        return model_id
    
    def predict_performance(self, 
                         person_id: str, 
                         model_id: Optional[str] = None,
                         target_metric: Optional[str] = None) -> Dict[str, Any]:
        """
        Prevê o desempenho futuro de uma pessoa.
        
        Args:
            person_id: ID da pessoa
            model_id: ID do modelo a ser utilizado (ou None para usar o melhor)
            target_metric: Tipo de métrica a prever (necessário se model_id for None)
            
        Returns:
            Dicionário com a previsão e informações adicionais
        """
        # Verificar se temos um modelo válido
        if model_id is None:
            if target_metric is None:
                raise ValueError("Se model_id não for especificado, target_metric é obrigatório")
                
            # Encontrar o melhor modelo para esta métrica
            best_model = None
            best_r2 = -float('inf')
            
            for mid, model in self.prediction_models.items():
                if model.target_metric == target_metric:
                    r2 = model.performance.get('r2', -float('inf'))
                    if r2 > best_r2:
                        best_model = model
                        best_r2 = r2
            
            if best_model is None:
                raise ValueError(f"Nenhum modelo encontrado para a métrica '{target_metric}'")
                
            model_id = best_model.model_id
        
        # Obter o modelo
        if model_id not in self.prediction_models:
            raise ValueError(f"Modelo com ID '{model_id}' não encontrado")
            
        model = self.prediction_models[model_id]
        
        # Preparar dados da pessoa para previsão
        person_features = self._prepare_person_features(person_id, model.features)
        
        if not person_features:
            raise ValueError(f"Dados insuficientes para prever desempenho de {person_id}")
        
        # Fazer previsão
        X_pred = pd.DataFrame([person_features])
        prediction = float(model.pipeline.predict(X_pred)[0])
        
        # Calcular incerteza (simplificado)
        rmse = model.performance.get('rmse', 0)
        
        # Criar resultado
        result = {
            'person_id': person_id,
            'model_id': model_id,
            'target_metric': model.target_metric,
            'prediction': prediction,
            'uncertainty': rmse,
            'confidence_interval': [prediction - 1.96 * rmse, prediction + 1.96 * rmse],
            'timestamp': datetime.datetime.now()
        }
        
        # Armazenar previsão
        if person_id not in self.person_predictions:
            self.person_predictions[person_id] = []
        self.person_predictions[person_id].append(result)
        
        return result
    
    def _prepare_person_features(self, person_id: str, required_features: List[str]) -> Dict[str, float]:
        """
        Prepara as features para uma pessoa específica.
        
        Args:
            person_id: ID da pessoa
            required_features: Lista de features necessárias
            
        Returns:
            Dicionário com features extraídas
        """
        # Filtrar métricas da pessoa
        person_metrics = [m for m in self.performance_metrics if m.person_id == person_id]
        
        if not person_metrics:
            return {}
        
        # Agrupar por tipo de métrica
        metrics_by_type = {}
        for metric in person_metrics:
            if metric.metric_type not in metrics_by_type:
                metrics_by_type[metric.metric_type] = []
            metrics_by_type[metric.metric_type].append(metric)
        
        # Calcular features para cada tipo de métrica
        person_features = {}
        
        for metric_type, metrics in metrics_by_type.items():
            # Ordenar por timestamp
            sorted_metrics = sorted(metrics, key=lambda x: x.timestamp)
            values = [m.value for m in sorted_metrics]
            
            # Calcular estatísticas básicas
            if values:
                person_features[f"{metric_type}_mean"] = np.mean(values)
                person_features[f"{metric_type}_recent"] = values[-1]
                
                if len(values) > 1:
                    person_features[f"{metric_type}_trend"] = (values[-1] - values[0]) / len(values)
                    person_features[f"{metric_type}_std"] = np.std(values)
                else:
                    person_features[f"{metric_type}_trend"] = 0
                    person_features[f"{metric_type}_std"] = 0
                
                person_features[f"{metric_type}_count"] = len(values)
        
        # Verificar se temos todas as features necessárias
        missing_features = [f for f in required_features if f not in person_features]
        
        if missing_features:
            # Preencher com zeros como fallback
            for feature in missing_features:
                person_features[feature] = 0
        
        return person_features
    
    def analyze_feature_importance(self, model_id: str) -> Dict[str, float]:
        """
        Analisa a importância das features para um modelo.
        
        Args:
            model_id: ID do modelo a analisar
            
        Returns:
            Dicionário ordenado de features -> importância
        """
        if model_id not in self.feature_importance:
            raise ValueError(f"Importância de features não disponível para o modelo '{model_id}'")
            
        # Ordenar features por importância
        importances = self.feature_importance[model_id]
        sorted_importance = {
            k: v for k, v in sorted(
                importances.items(), 
                key=lambda item: item[1],
                reverse=True
            )
        }
        
        return sorted_importance
    
    def visualize_model_performance(self, 
                                 model_id: str,
                                 output_path: Optional[Path] = None) -> Path:
        """
        Visualiza a performance do modelo e importância das features.
        
        Args:
            model_id: ID do modelo a visualizar
            output_path: Caminho para salvar a visualização
            
        Returns:
            Caminho do arquivo salvo
        """
        if model_id not in self.prediction_models:
            raise ValueError(f"Modelo com ID '{model_id}' não encontrado")
            
        model = self.prediction_models[model_id]
        
        # Criar figura
        plt.figure(figsize=(12, 8))
        
        # 1. Gráfico de importância das features
        plt.subplot(2, 1, 1)
        
        if model_id in self.feature_importance:
            importances = self.feature_importance[model_id]
            sorted_importances = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:10]
            
            features = [item[0] for item in sorted_importances]
            values = [item[1] for item in sorted_importances]
            
            bars = plt.barh(features, values, color='skyblue')
            plt.xlabel('Importância')
            plt.title(f'Top 10 Features para Previsão de {model.target_metric}', fontsize=14)
            plt.grid(axis='x', linestyle='--', alpha=0.7)
            
            # Adicionar valores
            for bar in bars:
                width = bar.get_width()
                plt.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                        f'{width:.3f}', ha='left', va='center')
        else:
            plt.text(0.5, 0.5, 'Importância de features não disponível',
                    horizontalalignment='center', verticalalignment='center',
                    transform=plt.gca().transAxes)
        
        # 2. Métricas de performance
        plt.subplot(2, 1, 2)
        
        performance = model.performance
        metrics = list(performance.keys())
        values = [performance[m] for m in metrics]
        
        # Cores por métrica
        colors = ['green' if m == 'r2' else 'red' for m in metrics]
        
        bars = plt.bar(metrics, values, color=colors)
        plt.title('Métricas de Performance do Modelo', fontsize=14)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Adicionar valores
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, height + 0.01,
                    f'{height:.4f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Salvar figura
        if output_path is None:
            output_path = Path(f'output/modelo_performance_{model_id}.png')
            
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_prediction_report(self, 
                                person_id: str,
                                model_id: Optional[str] = None,
                                target_metric: Optional[str] = None,
                                output_path: Optional[Path] = None) -> Path:
        """
        Gera um relatório de previsão de desempenho.
        
        Args:
            person_id: ID da pessoa
            model_id: ID do modelo a ser utilizado (ou None para usar o melhor)
            target_metric: Tipo de métrica a prever (necessário se model_id for None)
            output_path: Caminho para salvar o relatório
            
        Returns:
            Caminho do relatório salvo
        """
        # Fazer previsão
        prediction = self.predict_performance(person_id, model_id, target_metric)
        model_id = prediction['model_id']
        model = self.prediction_models[model_id]
        
        # Obter histórico da métrica
        metric_type = model.target_metric
        person_metrics = [m for m in self.performance_metrics 
                        if m.person_id == person_id and m.metric_type == metric_type]
        
        # Ordenar por timestamp
        person_metrics = sorted(person_metrics, key=lambda x: x.timestamp)
        
        # Criar caminho de saída
        if output_path is None:
            output_path = Path(f'output/relatorio_previsao_{person_id}_{metric_type}.txt')
            
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Gerar relatório
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"RELATÓRIO DE PREVISÃO DE DESEMPENHO\n")
            f.write(f"{'='*50}\n\n")
            
            f.write(f"Pessoa: {person_id}\n")
            f.write(f"Métrica: {metric_type}\n")
            f.write(f"Data: {datetime.datetime.now().strftime('%d/%m/%Y')}\n\n")
            
            f.write(f"PREVISÃO\n")
            f.write(f"{'-'*50}\n")
            f.write(f"Valor previsto: {prediction['prediction']:.2f}\n")
            f.write(f"Intervalo de confiança: [{prediction['confidence_interval'][0]:.2f}, {prediction['confidence_interval'][1]:.2f}]\n")
            f.write(f"Incerteza (RMSE): {prediction['uncertainty']:.4f}\n\n")
            
            # Adicionar histórico da métrica
            if person_metrics:
                f.write(f"HISTÓRICO DE DESEMPENHO\n")
                f.write(f"{'-'*50}\n")
                
                for i, metric in enumerate(person_metrics[-5:], 1):  # últimos 5
                    f.write(f"{i}. {metric.timestamp.strftime('%d/%m/%Y')}: {metric.value:.2f}")
                    if metric.target_value is not None:
                        f.write(f" (meta: {metric.target_value:.2f})")
                    f.write("\n")
                f.write("\n")
            
            # Adicionar fatores importantes
            if model_id in self.feature_importance:
                f.write(f"FATORES DE INFLUÊNCIA\n")
                f.write(f"{'-'*50}\n")
                
                importances = self.feature_importance[model_id]
                sorted_imp = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:5]
                
                for i, (feature, importance) in enumerate(sorted_imp, 1):
                    # Transformar nome da feature para algo mais legível
                    parts = feature.split('_')
                    if len(parts) >= 2:
                        metric = parts[0]
                        aspect = '_'.join(parts[1:])
                        readable = f"{metric} ({aspect})"
                    else:
                        readable = feature
                        
                    f.write(f"{i}. {readable}: {importance:.4f}\n")
                f.write("\n")
            
            f.write(f"RECOMENDAÇÕES\n")
            f.write(f"{'-'*50}\n")
            
            # Gerar recomendações baseadas na previsão e histórico
            if not person_metrics:
                f.write("Dados históricos insuficientes para gerar recomendações personalizadas.\n")
            else:
                current_value = person_metrics[-1].value if person_metrics else 0
                prediction_value = prediction['prediction']
                
                # Verificar tendência
                if prediction_value > current_value * 1.1:
                    trend = "positiva"
                elif prediction_value < current_value * 0.9:
                    trend = "negativa"
                else:
                    trend = "estável"
                
                # Recomendações baseadas na tendência
                if trend == "positiva":
                    f.write("1. Continuar com as práticas atuais que estão levando a uma tendência positiva\n")
                    f.write("2. Documentar ações bem-sucedidas para compartilhar boas práticas\n")
                    f.write("3. Considerar mentorar outras pessoas para difundir conhecimentos\n")
                elif trend == "negativa":
                    f.write("1. Identificar fatores específicos contribuindo para a tendência negativa\n")
                    f.write("2. Buscar feedback adicional de líderes e pares\n")
                    f.write("3. Desenvolver plano de ação focado nos indicadores de maior impacto\n")
                else:
                    f.write("1. Identificar áreas específicas para desenvolvimento e potencial crescimento\n")
                    f.write("2. Explorar novos desafios para evitar estagnação\n")
                    f.write("3. Manter consistência enquanto busca oportunidades de melhoria incremental\n")
            
            # Adicionar visualização
            if output_path.suffix == '.txt':
                viz_path = output_path.with_suffix('.png')
                self.visualize_model_performance(model_id, viz_path)
                f.write(f"\nVisualização do modelo salva em: {viz_path}\n")
        
        return output_path 