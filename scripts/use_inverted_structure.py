#!/usr/bin/env python3
"""
Exemplo de uso da estrutura invertida com o adaptador.

Este script demonstra como usar o adaptador para analisar dados na estrutura invertida:
<pessoa>/<ano>/resultado.json
"""

from structure_adapter import InvertedStructureAnalyzer, InvertedStructurePipeline
import matplotlib.pyplot as plt
import pandas as pd
import os

# Diretório com dados na estrutura <pessoa>/<ano>/resultado.json
DATA_DIR = "data"

# Criação do analisador adaptado para estrutura invertida
analyzer = InvertedStructureAnalyzer(DATA_DIR)
pipeline = InvertedStructurePipeline(DATA_DIR)

def list_people_and_years():
    """Lista todas as pessoas e anos disponíveis."""
    print("\n=== Pessoas e Anos Disponíveis ===")
    
    people = analyzer.get_all_people()
    years = analyzer.get_all_years()
    
    print(f"Pessoas ({len(people)}): {', '.join(people)}")
    print(f"Anos ({len(years)}): {', '.join(years)}")
    
    # Mostra detalhes para cada pessoa
    for person in people:
        person_years = analyzer.get_people_for_year(person)
        print(f"- {person}: {', '.join(sorted(person_years))}")
    
def analyze_person(person_name):
    """Analisa uma pessoa específica em todos os anos disponíveis."""
    print(f"\n=== Análise de {person_name} ===")
    
    try:
        # Lista anos disponíveis para esta pessoa
        years = analyzer.get_people_for_year(person_name)
        print(f"Anos disponíveis: {', '.join(sorted(years))}")
        
        if not years:
            print("Nenhum dado disponível para esta pessoa.")
            return
        
        # Busca conceitos por ano
        conceitos = analyzer.get_conceito_by_year(person_name)
        print("Conceitos por ano:")
        for year, conceito in conceitos.items():
            print(f"- {year}: {conceito}")
        
        # Tenta analisar os dados da pessoa
        for year in sorted(years):
            print(f"\nAnálise para {year}:")
            data = analyzer.analyze_person(person_name, year)
            
            if not data or not data.get('success', False):
                print(f"  Sem dados válidos para {year}")
                continue
                
            # Mostra algumas informações básicas
            concept = data.get('data', {}).get('conceito_ciclo_filho_descricao', 'N/A')
            print(f"  Conceito: {concept}")
            
            # Se houver comportamentos, mostra alguns
            behaviors = data.get('data', {}).get('comportamentos', [])
            if behaviors:
                print(f"  Comportamentos: {len(behaviors)}")
                for i, behavior in enumerate(behaviors[:3], 1):
                    print(f"    {i}. {behavior.get('nome', 'N/A')}")
                if len(behaviors) > 3:
                    print(f"    ...e mais {len(behaviors) - 3} comportamentos")
    
    except Exception as e:
        print(f"Erro na análise: {e}")

def compare_two_people(person1, person2, year):
    """Compara duas pessoas em um ano específico."""
    print(f"\n=== Comparação entre {person1} e {person2} ({year}) ===")
    
    try:
        # Analisa cada pessoa
        data1 = analyzer.analyze_person(person1, year)
        data2 = analyzer.analyze_person(person2, year)
        
        if not data1 or not data1.get('success', False):
            print(f"{person1}: Sem dados válidos para {year}")
            return
            
        if not data2 or not data2.get('success', False):
            print(f"{person2}: Sem dados válidos para {year}")
            return
        
        # Mostra conceitos
        concept1 = data1.get('data', {}).get('conceito_ciclo_filho_descricao', 'N/A')
        concept2 = data2.get('data', {}).get('conceito_ciclo_filho_descricao', 'N/A')
        
        print(f"{person1} - Conceito: {concept1}")
        print(f"{person2} - Conceito: {concept2}")
        
        # Compara comportamentos (se houver)
        behaviors1 = data1.get('data', {}).get('comportamentos', [])
        behaviors2 = data2.get('data', {}).get('comportamentos', [])
        
        if behaviors1 and behaviors2:
            print("\nComparação de comportamentos:")
            
            # Cria um dicionário para comportamentos da pessoa 1
            behavior_dict1 = {b.get('nome', ''): b.get('score', 0) for b in behaviors1 if 'nome' in b}
            behavior_dict2 = {b.get('nome', ''): b.get('score', 0) for b in behaviors2 if 'nome' in b}
            
            # Encontra comportamentos comuns
            common_behaviors = set(behavior_dict1.keys()) & set(behavior_dict2.keys())
            
            if common_behaviors:
                print(f"Comportamentos comuns: {len(common_behaviors)}")
                
                comparison_data = []
                for behavior in common_behaviors:
                    comparison_data.append({
                        'Comportamento': behavior,
                        person1: behavior_dict1.get(behavior, 0),
                        person2: behavior_dict2.get(behavior, 0),
                        'Diferença': behavior_dict1.get(behavior, 0) - behavior_dict2.get(behavior, 0)
                    })
                
                # Cria um DataFrame
                df = pd.DataFrame(comparison_data)
                # Ordena pela diferença absoluta
                df['Abs_Diff'] = df['Diferença'].abs()
                df = df.sort_values('Abs_Diff', ascending=False).drop('Abs_Diff', axis=1)
                
                # Mostra top 5 diferenças
                print("\nTop 5 maiores diferenças:")
                print(df.head(5).to_string(index=False))
            else:
                print("Não há comportamentos comuns para comparação.")
    
    except Exception as e:
        print(f"Erro na comparação: {e}")

def visualize_person_years(person_name):
    """Visualiza a evolução de uma pessoa ao longo dos anos."""
    print(f"\n=== Visualização da evolução de {person_name} ===")
    
    try:
        # Lista anos disponíveis para esta pessoa
        years = sorted(analyzer.get_people_for_year(person_name))
        
        if len(years) < 2:
            print("Não há dados suficientes para visualizar evolução (necessário pelo menos 2 anos).")
            return
        
        # Coleta dados para cada ano
        year_data = []
        for year in years:
            data = analyzer.analyze_person(person_name, year)
            if data and data.get('success', False):
                behaviors = data.get('data', {}).get('comportamentos', [])
                
                # Calcula score médio dos comportamentos
                if behaviors:
                    scores = [b.get('score', 0) for b in behaviors if 'score' in b]
                    avg_score = sum(scores) / len(scores) if scores else 0
                    year_data.append({'Ano': year, 'Score Médio': avg_score})
        
        if not year_data:
            print("Nenhum dado de comportamento disponível para visualização.")
            return
            
        # Cria um DataFrame
        df = pd.DataFrame(year_data)
        print(df.to_string(index=False))
        
        # Plotagem simples
        plt.figure(figsize=(10, 6))
        plt.plot(df['Ano'], df['Score Médio'], marker='o', linestyle='-', linewidth=2)
        plt.title(f'Evolução de {person_name} ao longo dos anos')
        plt.xlabel('Ano')
        plt.ylabel('Score Médio')
        plt.grid(True)
        
        # Salva o gráfico
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(os.path.join(output_dir, f"{person_name.replace(' ', '_')}_evolucao.png"))
        print(f"Gráfico salvo em output/{person_name.replace(' ', '_')}_evolucao.png")
        
    except Exception as e:
        print(f"Erro na visualização: {e}")

if __name__ == "__main__":
    # Executa as funções de exemplo
    list_people_and_years()
    
    # Analisa uma pessoa específica
    analyze_person("João Silva")
    
    # Compara duas pessoas
    compare_two_people("João Silva", "Maria Oliveira", "2022")
    
    # Visualiza evolução ao longo dos anos
    visualize_person_years("João Silva") 