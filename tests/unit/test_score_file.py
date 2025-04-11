#!/usr/bin/env python3
"""
Script para testar o modelo de pontuação NPS diretamente em um arquivo de avaliação.
Uso: python test_score_file.py caminho/para/resultado.json

Este script extrai as frequências do arquivo JSON e calcula os scores usando o modelo NPS.
"""
import sys
import json
import os
from pathlib import Path
import pandas as pd
from typing import Dict, List, Any

# Importar funções do modelo de pontuação
from peopleanalytics.constants import (
    calculate_score, get_score_category,
    FREQUENCY_WEIGHTS, FREQUENCY_WEIGHTS_NPS
)

def process_evaluation(file_path: str) -> List[Dict[str, Any]]:
    """Extrai frequências do arquivo de avaliação e calcula scores NPS."""
    try:
        # Carregar o arquivo JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Verificar se os dados são válidos
        if not data.get("success", False) or "data" not in data:
            print("Dados inválidos ou incompletos")
            return []
        
        results = []
        
        # Processar dados aninhados (diferentes estruturas possíveis)
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
                    
                    # Calcular scores usando modelo tradicional
                    traditional_person = calculate_score(person_freq, use_nps_model=False)
                    traditional_group = calculate_score(group_freq, use_nps_model=False)
                    
                    # Calcular scores usando modelo NPS
                    nps_person = calculate_score(person_freq, use_nps_model=True)
                    nps_group = calculate_score(group_freq, use_nps_model=True)
                    
                    # Calcular scores normalizados (0-100)
                    norm_person = calculate_score(person_freq, use_nps_model=True, normalize=True)
                    norm_group = calculate_score(group_freq, use_nps_model=True, normalize=True)
                    
                    # Obter categorias qualitativas
                    person_category = get_score_category(nps_person)
                    person_category_norm = get_score_category(norm_person, normalized=True)
                    
                    # Adicionar ao resultado
                    results.append({
                        "direcionador": dir_name,
                        "comportamento": comp_name,
                        "avaliador": avaliador,
                        "frequencias_colaborador": person_freq,
                        "frequencias_grupo": group_freq,
                        "score_tradicional_pessoa": traditional_person,
                        "score_tradicional_grupo": traditional_group,
                        "score_nps_pessoa": nps_person,
                        "score_nps_grupo": nps_group,
                        "score_pessoa_norm": norm_person,
                        "score_grupo_norm": norm_group,
                        "categoria_pessoa": person_category,
                        "categoria_pessoa_norm": person_category_norm
                    })
                
                # Se não houver consolidado, verificar avaliacoes_grupo
                if not comportamento.get("consolidado", []):
                    for avaliacao in comportamento.get("avaliacoes_grupo", []):
                        avaliador = avaliacao.get("avaliador", "Desconhecido")
                        person_freq = avaliacao.get("frequencia_colaborador", [])
                        group_freq = avaliacao.get("frequencia_grupo", [])
                        
                        # Ignorar avaliações sem dados de frequência válidos
                        if not person_freq or not group_freq or len(person_freq) != 6 or len(group_freq) != 6:
                            continue
                        
                        # Calcular scores usando modelo tradicional
                        traditional_person = calculate_score(person_freq, use_nps_model=False)
                        traditional_group = calculate_score(group_freq, use_nps_model=False)
                        
                        # Calcular scores usando modelo NPS
                        nps_person = calculate_score(person_freq, use_nps_model=True)
                        nps_group = calculate_score(group_freq, use_nps_model=True)
                        
                        # Calcular scores normalizados (0-100)
                        norm_person = calculate_score(person_freq, use_nps_model=True, normalize=True)
                        norm_group = calculate_score(group_freq, use_nps_model=True, normalize=True)
                        
                        # Obter categorias qualitativas
                        person_category = get_score_category(nps_person)
                        person_category_norm = get_score_category(norm_person, normalized=True)
                        
                        # Adicionar ao resultado
                        results.append({
                            "direcionador": dir_name,
                            "comportamento": comp_name,
                            "avaliador": avaliador,
                            "frequencias_colaborador": person_freq,
                            "frequencias_grupo": group_freq,
                            "score_tradicional_pessoa": traditional_person,
                            "score_tradicional_grupo": traditional_group,
                            "score_nps_pessoa": nps_person,
                            "score_nps_grupo": nps_group,
                            "score_pessoa_norm": norm_person,
                            "score_grupo_norm": norm_group,
                            "categoria_pessoa": person_category,
                            "categoria_pessoa_norm": person_category_norm
                        })
        
        return results
    
    except Exception as e:
        print(f"Erro ao processar arquivo: {str(e)}")
        return []

def print_results(results):
    """Imprime os resultados formatados."""
    if not results:
        print("Nenhum resultado para exibir.")
        return
    
    print("\n============= RESULTADOS DE PONTUAÇÃO =============\n")
    print("Comparação entre modelo tradicional e modelo NPS:\n")
    
    # Criar DataFrame para facilitar a visualização
    df = pd.DataFrame(results)
    
    # Calcular médias para cada comportamento
    comp_avg = df.groupby(["direcionador", "comportamento"]).agg({
        "score_tradicional_pessoa": "mean",
        "score_tradicional_grupo": "mean",
        "score_nps_pessoa": "mean",
        "score_nps_grupo": "mean",
        "score_pessoa_norm": "mean",
        "score_grupo_norm": "mean"
    }).reset_index()
    
    # Imprimir resultados por comportamento
    for _, row in comp_avg.iterrows():
        print(f"Direcionador: {row['direcionador']}")
        print(f"Comportamento: {row['comportamento']}")
        print(f"  Score Tradicional: Pessoa={row['score_tradicional_pessoa']:.2f}, Grupo={row['score_tradicional_grupo']:.2f}")
        print(f"  Score NPS (-10 a 10): Pessoa={row['score_nps_pessoa']:.2f}, Grupo={row['score_nps_grupo']:.2f}")
        print(f"  Score NPS (0 a 100): Pessoa={row['score_pessoa_norm']:.2f}, Grupo={row['score_grupo_norm']:.2f}")
        print()
    
    # Calcular médias globais
    total_avg = df.agg({
        "score_tradicional_pessoa": "mean",
        "score_tradicional_grupo": "mean",
        "score_nps_pessoa": "mean",
        "score_nps_grupo": "mean",
        "score_pessoa_norm": "mean",
        "score_grupo_norm": "mean"
    })
    
    print("============= MÉDIAS GLOBAIS =============")
    print(f"Score Tradicional: Pessoa={total_avg['score_tradicional_pessoa']:.2f}, Grupo={total_avg['score_tradicional_grupo']:.2f}")
    print(f"Score NPS (-10 a 10): Pessoa={total_avg['score_nps_pessoa']:.2f}, Grupo={total_avg['score_nps_grupo']:.2f}")
    print(f"Score NPS (0 a 100): Pessoa={total_avg['score_pessoa_norm']:.2f}, Grupo={total_avg['score_grupo_norm']:.2f}")
    
    # Contagem por categoria
    cat_counts = df['categoria_pessoa'].value_counts().sort_index()
    total = len(df)
    
    print("\n============= DISTRIBUIÇÃO DE CATEGORIAS =============")
    for cat, count in cat_counts.items():
        percentage = (count / total) * 100
        print(f"{cat}: {count} ({percentage:.1f}%)")

def main():
    """Função principal."""
    if len(sys.argv) < 2:
        print("Uso: python test_score_file.py caminho/para/resultado.json")
        return
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Erro: Arquivo {file_path} não encontrado")
        return
    
    print(f"Processando arquivo: {file_path}")
    results = process_evaluation(file_path)
    print_results(results)

if __name__ == "__main__":
    main() 