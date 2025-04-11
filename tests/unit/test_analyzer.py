#!/usr/bin/env python3
from peopleanalytics.analyzer import EvaluationAnalyzer
import sys

def main():
    if len(sys.argv) < 2:
        print("Uso: python test_analyzer.py /caminho/para/dados")
        return
        
    data_path = sys.argv[1]
    analyzer = EvaluationAnalyzer(data_path)
    
    # Listar pessoas e anos
    all_people = analyzer.get_all_people()
    all_years = analyzer.get_all_years()
    
    print(f"Pessoas encontradas ({len(all_people)}): {', '.join(all_people[:5])}...")
    print(f"Anos encontrados: {', '.join(all_years)}")
    
    # Testar obtenção de scores para cada pessoa
    for person in all_people:
        for year in analyzer.get_person_years(person):
            behavior_scores = analyzer.get_behavior_scores(person, year)
            
            if behavior_scores:
                print(f"{person} ({year}): Scores obtidos com sucesso")
                for dir_name, behaviors in behavior_scores.items():
                    print(f"  - {dir_name}: {len(behaviors)} comportamentos")
            else:
                print(f"{person} ({year}): Sem scores")

if __name__ == "__main__":
    main() 