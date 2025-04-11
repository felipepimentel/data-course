#!/usr/bin/env python3
"""
Script para testar o cálculo de scores com diferentes vetores de frequência.
"""
from peopleanalytics.analyzer import EvaluationAnalyzer
from peopleanalytics.evaluation_analyzer import EvaluationAnalyzer as EvaluationAnalyzer2

def test_weighted_score_calculation():
    """Testar os cálculos de score ponderado com diferentes vetores"""
    # Criar instâncias dos analisadores
    analyzer1 = EvaluationAnalyzer(".")
    analyzer2 = EvaluationAnalyzer2(".")
    
    # Definir os pesos esperados
    expected_weights = [0, 2.5, 4, 3, 2, 1]
    
    # Verificar se os pesos estão configurados corretamente
    print(f"Pesos analyzer1: {analyzer1.frequency_weights}")
    print(f"Pesos analyzer2: {analyzer2.frequency_weights}")
    
    # Casos de teste com diferentes vetores de frequência - sempre 6 posições
    test_cases = [
        # Vetor padrão de 6 posições
        ([0, 1, 2, 1, 0, 0], "Vetor padrão"),
        
        # Vetor com zeros
        ([0, 0, 0, 0, 0, 0], "Vetor só com zeros"),
        
        # Vetor com muitos sempre (peso 4)
        ([0, 0, 10, 0, 0, 0], "Muitos 'sempre'"),
        
        # Vetor com distribuição uniforme
        ([0, 1, 1, 1, 1, 1], "Distribuição uniforme"),
        
        # Concentração nas extremidades
        ([0, 5, 0, 0, 0, 5], "Extremos (referência e raramente)"),
        
        # Concentração no meio
        ([0, 0, 0, 10, 10, 0], "Meio (quase sempre e poucas vezes)"),
    ]
    
    print("\nCalculando scores para diferentes vetores de frequência:")
    
    for freq_vector, description in test_cases:
        print(f"\n{description}: {freq_vector}")
        
        # Calcular com o analyzer1 (analyzer.py)
        try:
            score1 = analyzer1.calculate_weighted_score(freq_vector)
            print(f"  Score analyzer1: {score1:.3f}")
        except Exception as e:
            print(f"  Erro analyzer1: {str(e)}")
            
        # Calcular com o analyzer2 (evaluation_analyzer.py)
        try:
            score2 = analyzer2.calculate_weighted_score(freq_vector)
            print(f"  Score analyzer2: {score2:.3f}")
        except Exception as e:
            print(f"  Erro analyzer2: {str(e)}")
        
        # Calcular manualmente para verificar
        try:
            # Cálculo manual
            weighted_sum = sum(f * w for f, w in zip(freq_vector, expected_weights))
            total_count = sum(freq_vector[1:])  # Excluir n/a (posição 0)
            
            manual_score = weighted_sum / total_count if total_count > 0 else 0
            print(f"  Score manual: {manual_score:.3f}")
            
            # Verificar se os resultados são consistentes
            if abs(score1 - manual_score) > 0.001 or abs(score2 - manual_score) > 0.001:
                print("  ❌ INCONSISTÊNCIA DETECTADA!")
            else:
                print("  ✅ Consistente com o cálculo manual")
        except Exception as e:
            print(f"  Erro cálculo manual: {str(e)}")

    # Verificar o comportamento para vetores inválidos
    print("\nTestando validação de vetores inválidos:")
    
    invalid_vectors = [
        # Vetor vazio
        ([], "Vetor vazio"),
        # Vetores pequenos
        ([1, 2, 3, 4, 5], "5 posições (faltando uma)"),
        ([1, 2, 3], "3 posições (muito curto)"),
        # Vetores grandes
        ([0, 1, 2, 3, 4, 5, 6], "7 posições (muito longo)"),
    ]
    
    for freq_vector, description in invalid_vectors:
        print(f"\n{description}: {freq_vector}")
        
        # Testar com analyzer1
        try:
            score1 = analyzer1.calculate_weighted_score(freq_vector)
            print(f"  ❌ Erro: analyzer1 aceitou um vetor inválido! Score: {score1:.3f}")
        except ValueError as e:
            print(f"  ✅ analyzer1 rejeitou corretamente: {str(e)}")
        except Exception as e:
            print(f"  ⚠️ analyzer1 lançou outro erro: {type(e).__name__}: {str(e)}")
            
        # Testar com analyzer2
        try:
            score2 = analyzer2.calculate_weighted_score(freq_vector)
            print(f"  ❌ Erro: analyzer2 aceitou um vetor inválido! Score: {score2:.3f}")
        except ValueError as e:
            print(f"  ✅ analyzer2 rejeitou corretamente: {str(e)}")
        except Exception as e:
            print(f"  ⚠️ analyzer2 lançou outro erro: {type(e).__name__}: {str(e)}")

    # Verificar o comportamento da função compare_with_group para diferentes pares de vetores
    test_case_pairs = [
        ([0, 1, 2, 1, 0, 0], [0, 0, 1, 2, 1, 0], "Pessoa com mais 'sempre' que o grupo"),
        ([0, 0, 1, 2, 1, 0], [0, 1, 2, 1, 0, 0], "Grupo com mais 'sempre' que a pessoa"),
        ([0, 0, 0, 0, 0, 0], [0, 1, 2, 1, 0, 0], "Pessoa com vetor zerado"),
        ([0, 1, 2, 1, 0, 0], [0, 0, 0, 0, 0, 0], "Grupo com vetor zerado"),
    ]
    
    print("\nTestando comparações de vetores:")
    
    for person_freq, group_freq, description in test_case_pairs:
        print(f"\n{description}:")
        print(f"  Pessoa: {person_freq}")
        print(f"  Grupo: {group_freq}")
        
        try:
            # Calcular com o analyzer1 (analyzer.py)
            comparison1 = analyzer1.compare_with_group(person_freq, group_freq)
            print(f"  Diferenças analyzer1: {comparison1}")
            
            # Calcular com o analyzer2 (evaluation_analyzer.py)
            comparison2 = analyzer2.compare_with_group(person_freq, group_freq)
            print(f"  Diferenças analyzer2: {comparison2}")
            
            # Verificar se os resultados são consistentes
            if str(comparison1) != str(comparison2):
                print("  ❌ INCONSISTÊNCIA DETECTADA!")
            else:
                print("  ✅ Resultados consistentes entre as implementações")
        except Exception as e:
            print(f"  Erro na comparação: {str(e)}")

if __name__ == "__main__":
    test_weighted_score_calculation() 