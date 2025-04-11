#!/usr/bin/env python3
"""
Script para gerar um relatório de pontuação baseado no novo modelo NPS.
"""
import os
import sys
import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from peopleanalytics.constants import (
    FREQUENCY_LABELS, FREQUENCY_WEIGHTS_NPS, 
    calculate_score, get_score_category,
    CONCEPT_CHART_COLORS
)

# Definir pasta de saída padrão em uma constante
DEFAULT_OUTPUT_DIR = os.path.join(os.getcwd(), "output")

def load_evaluation_data(filepath: str) -> Dict[str, Any]:
    """Carrega os dados de avaliação de um arquivo JSON."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar arquivo {filepath}: {str(e)}")
        return {}

def process_evaluation(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Processa os dados de avaliação e calcula os scores NPS."""
    results = []
    
    # Verificar se os dados são válidos
    if not data.get("success", False) or "data" not in data:
        print("Dados inválidos ou incompletos")
        return results
    
    # Lidar com estrutura aninhada
    inner_data = data["data"]
    if "data" in inner_data and isinstance(inner_data["data"], dict):
        inner_data = inner_data["data"]
    
    # Processar direcionadores
    for direcionador in inner_data.get("direcionadores", []):
        dir_name = direcionador.get("direcionador", "Desconhecido")
        
        for comportamento in direcionador.get("comportamentos", []):
            comp_name = comportamento.get("comportamento", "Desconhecido")
            
            # Processar avaliações consolidadas
            for avaliacao in comportamento.get("consolidado", []):
                avaliador = avaliacao.get("avaliador", "Desconhecido")
                person_freq = avaliacao.get("frequencias_colaborador", [])
                group_freq = avaliacao.get("frequencias_grupo", [])
                
                # Ignorar avaliações sem dados de frequência válidos
                if not person_freq or not group_freq or len(person_freq) != 6 or len(group_freq) != 6:
                    continue
                
                # Calcular scores usando o novo modelo NPS
                person_score = calculate_score(person_freq, use_nps_model=True)
                group_score = calculate_score(group_freq, use_nps_model=True)
                
                # Calcular scores normalizados
                person_norm = calculate_score(person_freq, use_nps_model=True, normalize=True)
                group_norm = calculate_score(group_freq, use_nps_model=True, normalize=True)
                
                # Obter categorias qualitativas
                person_category = get_score_category(person_score)
                group_category = get_score_category(group_score)
                
                # Calcular diferença entre scores
                score_diff = person_score - group_score
                
                results.append({
                    "direcionador": dir_name,
                    "comportamento": comp_name,
                    "avaliador": avaliador,
                    "score_pessoa": person_score,
                    "score_grupo": group_score,
                    "categoria_pessoa": person_category,
                    "categoria_grupo": group_category,
                    "score_pessoa_norm": person_norm,
                    "score_grupo_norm": group_norm,
                    "diferenca": score_diff
                })
    
    return results

def ensure_output_dir(output_dir: str) -> str:
    """Garante que o diretório de saída exista e retorna o caminho absoluto.
    
    Args:
        output_dir: Caminho do diretório de saída
        
    Returns:
        Caminho absoluto do diretório de saída
    """
    # Converter para caminho absoluto se for relativo
    if not os.path.isabs(output_dir):
        output_dir = os.path.abspath(output_dir)
    
    # Garantir que o diretório exista
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Usando diretório de saída: {output_dir}")
    return output_dir

def generate_score_report(data_path: str, output_dir: Optional[str] = None) -> None:
    """Gera um relatório completo dos scores NPS a partir dos dados de avaliação."""
    # Definir diretório de saída
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    
    # Garantir que o diretório exista
    output_dir = ensure_output_dir(output_dir)
    
    # Carregar dados
    data = load_evaluation_data(data_path)
    if not data:
        print(f"Nenhum dado válido encontrado em {data_path}")
        return
    
    # Processar avaliações
    results = process_evaluation(data)
    if not results:
        print("Nenhum resultado encontrado para processar")
        return
    
    # Criar DataFrame
    df = pd.DataFrame(results)
    
    # Gerar relatório em CSV
    csv_path = os.path.join(output_dir, "nps_scores_report.csv")
    df.to_csv(csv_path, index=False)
    print(f"Relatório CSV gerado: {csv_path}")
    
    # Gerar gráficos
    plot_category_distribution(df, output_dir)
    plot_score_comparison(df, output_dir)
    
    # Mostrar estatísticas
    print("\nEstatísticas gerais:")
    print(f"Total de avaliações: {len(df)}")
    
    # Média de scores por categoria
    avg_by_category = df.groupby('categoria_pessoa')['score_pessoa'].mean().sort_values(ascending=False)
    print("\nScore médio por categoria:")
    for cat, score in avg_by_category.items():
        print(f"  {cat}: {score:.2f}")
    
    # Mostrar distribuição de categorias
    cat_counts = df['categoria_pessoa'].value_counts().sort_index()
    total = len(df)
    print("\nDistribuição de categorias:")
    for cat, count in cat_counts.items():
        percentage = (count / total) * 100
        print(f"  {cat}: {count} ({percentage:.1f}%)")
    
    # Gerar arquivo de resumo
    summary_path = os.path.join(output_dir, "nps_summary.txt")
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"Relatório de Pontuação NPS\n")
        f.write(f"=========================\n\n")
        f.write(f"Data de geração: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Arquivo de origem: {os.path.abspath(data_path)}\n\n")
        
        f.write(f"Total de avaliações: {len(df)}\n\n")
        
        f.write(f"Score médio por categoria:\n")
        for cat, score in avg_by_category.items():
            f.write(f"  {cat}: {score:.2f}\n")
        
        f.write(f"\nDistribuição de categorias:\n")
        for cat, count in cat_counts.items():
            percentage = (count / total) * 100
            f.write(f"  {cat}: {count} ({percentage:.1f}%)\n")
    
    print(f"Resumo salvo em: {summary_path}")

def plot_category_distribution(df: pd.DataFrame, output_dir: str) -> None:
    """Gera um gráfico de barras da distribuição de categorias."""
    plt.figure(figsize=(10, 6))
    
    # Contar frequência de cada categoria
    cat_counts = df['categoria_pessoa'].value_counts().sort_index()
    
    # Pegar cores correspondentes às categorias
    colors = [CONCEPT_CHART_COLORS.get(cat, CONCEPT_CHART_COLORS["default"]) for cat in cat_counts.index]
    
    # Criar gráfico de barras
    bars = plt.bar(cat_counts.index, cat_counts.values, color=colors)
    
    # Adicionar rótulos e título
    plt.title("Distribuição de Categorias de Score", fontsize=14)
    plt.xlabel("Categoria", fontsize=12)
    plt.ylabel("Quantidade", fontsize=12)
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Adicionar valores nas barras
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f'{height:.0f}', ha='center', va='bottom')
    
    # Salvar figura
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "category_distribution.png"))
    plt.close()
    print(f"Gráfico de distribuição de categorias gerado em {output_dir}/category_distribution.png")

def plot_score_comparison(df: pd.DataFrame, output_dir: str) -> None:
    """Gera um gráfico de comparação entre scores individuais e do grupo."""
    plt.figure(figsize=(12, 7))
    
    # Agrupar por direcionador e calcular médias
    avg_by_driver = df.groupby('direcionador').agg({
        'score_pessoa': 'mean',
        'score_grupo': 'mean'
    }).sort_values(by='score_pessoa', ascending=False)
    
    # Criar posições para as barras
    x = range(len(avg_by_driver))
    width = 0.35
    
    # Criar barras
    plt.bar([p - width/2 for p in x], avg_by_driver['score_pessoa'], width, 
            label='Score Individual', color='#3498db')
    plt.bar([p + width/2 for p in x], avg_by_driver['score_grupo'], width, 
            label='Score do Grupo', color='#2ecc71')
    
    # Adicionar linha zero
    plt.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    
    # Adicionar linhas de delimitação das categorias
    plt.axhline(y=7.5, color='green', linestyle='--', alpha=0.5, label='Limite Excelente')
    plt.axhline(y=2.5, color='#f1c40f', linestyle='--', alpha=0.5, label='Limite Bom')
    plt.axhline(y=-2.5, color='#e67e22', linestyle='--', alpha=0.5, label='Limite Regular')
    plt.axhline(y=-7.5, color='red', linestyle='--', alpha=0.5, label='Limite Abaixo')
    
    # Adicionar rótulos e título
    plt.title("Comparação de Scores por Direcionador", fontsize=14)
    plt.xlabel("Direcionador", fontsize=12)
    plt.ylabel("Score NPS", fontsize=12)
    plt.xticks(x, avg_by_driver.index, rotation=45, ha="right")
    plt.legend(loc='upper right')
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Ajustar limites do eixo Y
    plt.ylim(-10.5, 10.5)
    
    # Salvar figura
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "score_comparison.png"))
    plt.close()
    print(f"Gráfico de comparação de scores gerado em {output_dir}/score_comparison.png")

def main():
    # Verificar argumentos
    if len(sys.argv) < 2:
        print(f"Uso: {sys.argv[0]} <arquivo_json> [diretorio_saida]")
        sys.exit(1)
    
    # Obter caminho do arquivo
    data_path = sys.argv[1]
    
    # Obter diretório de saída (opcional)
    output_dir = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT_DIR
    
    # Gerar relatório
    generate_score_report(data_path, output_dir)

if __name__ == "__main__":
    main() 