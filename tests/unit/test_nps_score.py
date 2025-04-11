#!/usr/bin/env python3
"""
Script para testar o novo modelo de pontuação baseado em NPS.
"""
from peopleanalytics.constants import (
    calculate_score, get_score_category,
    FREQUENCY_WEIGHTS, FREQUENCY_WEIGHTS_NPS,
    SCORE_RANGES, NORMALIZED_SCORE_RANGES
)
from peopleanalytics.analyzer import EvaluationAnalyzer
from peopleanalytics.evaluation_analyzer import EvaluationAnalyzer as EvaluationAnalyzer2

def test_nps_scoring_model():
    """Testar o novo modelo de pontuação baseado em NPS em comparação com o modelo tradicional"""
    # Criar instâncias dos analisadores
    analyzer1 = EvaluationAnalyzer(".")
    analyzer2 = EvaluationAnalyzer2(".")
    
    # Imprimir os pesos para ambos os modelos
    print(f"Pesos tradicionais: {FREQUENCY_WEIGHTS}")
    print(f"Pesos NPS atualizados: {FREQUENCY_WEIGHTS_NPS}")
    print("\n")
    
    # Mostrar as faixas de categorização
    print("Categorias de score (modelo NPS):")
    for categoria, (min_val, max_val) in SCORE_RANGES.items():
        print(f"  {categoria}: {min_val} a {max_val}")
    
    print("\nCategorias de score normalizado (0-100):")
    for categoria, (min_val, max_val) in NORMALIZED_SCORE_RANGES.items():
        print(f"  {categoria}: {min_val} a {max_val}")
    print("\n")
    
    # Casos de teste com diferentes vetores de frequência - sempre 6 posições
    test_cases = [
        # Vetor padrão de 6 posições
        ([0, 1, 2, 1, 0, 0], "Vetor padrão (mais positivos)"),
        
        # Vetor com zeros
        ([0, 0, 0, 0, 0, 0], "Vetor só com zeros"),
        
        # Vetor com muitos sempre (peso 10 no NPS)
        ([0, 0, 10, 0, 0, 0], "Muitos 'sempre'"),
        
        # Vetor com distribuição uniforme
        ([0, 1, 1, 1, 1, 1], "Distribuição uniforme"),
        
        # Concentração nas extremidades positivas e negativas
        ([0, 0, 5, 0, 0, 5], "Extremos (sempre e raramente)"),
        
        # Concentração no meio
        ([0, 0, 0, 10, 10, 0], "Meio (quase sempre e poucas vezes)"),
        
        # Concentração no meio negativo
        ([0, 0, 0, 0, 10, 0], "Poucos vezes dominante"),
        
        # Concentração no meio positivo
        ([0, 0, 0, 10, 0, 0], "Quase sempre dominante"),
        
        # Concentração em raramente (extremo negativo)
        ([0, 0, 0, 0, 0, 10], "Raramente dominante"),
        
        # Forte preferência por referência
        ([0, 10, 0, 0, 0, 0], "Referência dominante"),
        
        # Casos mistos com diferentes distribuições
        ([0, 3, 5, 2, 1, 0], "Maioria positiva com algumas referências"),
        ([0, 3, 1, 1, 5, 1], "Maioria negativa com algumas referências"),
    ]
    
    print("Comparando modelos de pontuação:\n")
    print(f"{'Descrição':<35} | {'NPS':<8} | {'Categoria':<14} | {'NPS (0-100)':<10} | {'Cat. Norm.':<14}")
    print(f"{'-'*35} | {'-'*8} | {'-'*14} | {'-'*10} | {'-'*14}")
    
    for freq_vector, description in test_cases:
        # Calcular usando o modelo NPS
        nps_score = calculate_score(freq_vector, use_nps_model=True)
        categoria = get_score_category(nps_score)
        
        # Calcular usando o modelo NPS normalizado
        nps_normalized = calculate_score(freq_vector, use_nps_model=True, normalize=True)
        categoria_norm = get_score_category(nps_normalized, normalized=True)
        
        # Formatar para exibição
        print(f"{description:<35} | {nps_score:8.2f} | {categoria:<14} | {nps_normalized:10.2f} | {categoria_norm:<14}")
    
    # Verificar consistência entre as classes de análise
    print("\nVerificando consistência entre as implementações:")
    
    # Testar vários casos com ambas as classes
    test_vectors = [
        ([0, 1, 5, 3, 2, 1], "Caso típico misto"),
        ([0, 8, 1, 1, 1, 1], "Alto em referências"),
        ([0, 0, 0, 0, 0, 10], "Extremo negativo"),
        ([0, 0, 10, 0, 0, 0], "Extremo positivo")
    ]
    
    for test_vector, description in test_vectors:
        print(f"\nVetor teste: {test_vector} - {description}")
        
        # Calcular scores diretos
        dir_nps = calculate_score(test_vector, use_nps_model=True)
        categoria = get_score_category(dir_nps)
        
        dir_norm = calculate_score(test_vector, use_nps_model=True, normalize=True)
        categoria_norm = get_score_category(dir_norm, normalized=True)
        
        # Exibir resultados
        print(f"Score NPS: {dir_nps:.2f} - Categoria: {categoria}")
        print(f"Score Normalizado (0-100): {dir_norm:.2f} - Categoria: {categoria_norm}")
        
        # Verificar se os analyzers produzem os mesmos resultados
        a1_nps = analyzer1.calculate_weighted_score(test_vector, use_nps_model=True)
        a2_nps = analyzer2.calculate_weighted_score(test_vector, use_nps_model=True)
        
        if a1_nps == dir_nps and a2_nps == dir_nps:
            print(f"✅ Todos os cálculos são consistentes para este vetor")
        else:
            print(f"❌ Inconsistência detectada!")
            print(f"analyzer1 (NPS): {a1_nps:.2f}, esperado: {dir_nps:.2f}")
            print(f"analyzer2 (NPS): {a2_nps:.2f}, esperado: {dir_nps:.2f}")

if __name__ == "__main__":
    test_nps_scoring_model() 