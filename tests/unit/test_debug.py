#!/usr/bin/env python3
from peopleanalytics.analyzer import EvaluationAnalyzer
import sys
import json
import os

def main():
    if len(sys.argv) < 2:
        print("Uso: python test_debug.py /caminho/para/dados")
        return
        
    data_path = sys.argv[1]
    print(f"Analisando dados de: {data_path}")
    analyzer = EvaluationAnalyzer(data_path)
    
    # Listar pessoas e anos
    all_people = analyzer.get_all_people()
    all_years = analyzer.get_all_years()
    
    print(f"Pessoas encontradas ({len(all_people)}): {', '.join(all_people[:5])}...")
    print(f"Anos encontrados: {', '.join(all_years)}")
    
    # Examinar dados brutos para uma pessoa
    person = all_people[0] if all_people else None
    if not person:
        print("Nenhuma pessoa encontrada")
        return
        
    print(f"\nExaminando dados para: {person}")
    
    for year in analyzer.get_person_years(person):
        print(f"\nDados para o ano: {year}")
        
        # Obter dados brutos
        raw_data = analyzer.get_evaluations_for_person(person, year)
        print(f"Dados carregados com sucesso: {raw_data.get('success', False)}")
        
        # Mostrar as chaves principais do objeto
        if isinstance(raw_data, dict):
            print(f"Chaves no objeto raw_data: {list(raw_data.keys())}")
            if "data" in raw_data:
                if isinstance(raw_data["data"], dict):
                    print(f"Chaves em raw_data['data']: {list(raw_data['data'].keys())}")
                else:
                    print(f"raw_data['data'] não é um dicionário: {type(raw_data['data'])}")
            
                # Verificar estrutura
                if "direcionadores" in raw_data["data"]:
                    print(f"Número de direcionadores: {len(raw_data['data']['direcionadores'])}")
                    
                    # Examinar o primeiro direcionador
                    direcionador = raw_data["data"]["direcionadores"][0]
                    print(f"Direcionador: {direcionador.get('direcionador', 'N/A')}")
                    
                    if "comportamentos" in direcionador:
                        print(f"Número de comportamentos: {len(direcionador['comportamentos'])}")
                        
                        # Examinar o primeiro comportamento
                        comportamento = direcionador["comportamentos"][0]
                        print(f"Comportamento: {comportamento.get('comportamento', 'N/A')}")
                        
                        # Verificar avaliacoes_grupo
                        if "avaliacoes_grupo" in comportamento:
                            print(f"Número de avaliações_grupo: {len(comportamento['avaliacoes_grupo'])}")
                            if comportamento['avaliacoes_grupo']:
                                avaliacao = comportamento['avaliacoes_grupo'][0]
                                print(f"Avaliador: {avaliacao.get('avaliador', 'N/A')}")
                                print(f"frequencia_colaborador: {avaliacao.get('frequencia_colaborador', [])}")
                                print(f"frequencia_grupo: {avaliacao.get('frequencia_grupo', [])}")
                        else:
                            print("Sem avaliacoes_grupo")
                        
                        # Verificar consolidado
                        if "consolidado" in comportamento:
                            print(f"Número de consolidado: {len(comportamento['consolidado'])}")
                            if comportamento['consolidado']:
                                consolidado = comportamento['consolidado'][0]
                                print(f"Avaliador (consolidado): {consolidado.get('avaliador', 'N/A')}")
                                print(f"frequencias_colaborador: {consolidado.get('frequencias_colaborador', [])}")
                                print(f"frequencias_grupo: {consolidado.get('frequencias_grupo', [])}")
                        else:
                            print("Sem consolidado")
                else:
                    print("Chave 'direcionadores' não encontrada em raw_data['data']")
        else:
            print(f"raw_data não é um dicionário: {type(raw_data)}")
            
        # Tentar carregar o arquivo JSON diretamente
        try:
            json_path = os.path.join(data_path, person, year, "resultado.json")
            print(f"\nTentando ler diretamente o arquivo: {json_path}")
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    direct_data = json.load(f)
                print(f"Arquivo carregado com sucesso")
                print(f"Chaves principais: {list(direct_data.keys())}")
                if "data" in direct_data:
                    print(f"Chaves em data: {list(direct_data['data'].keys())}")
                    if "direcionadores" in direct_data["data"]:
                        print(f"Número de direcionadores: {len(direct_data['data']['direcionadores'])}")
            else:
                print(f"Arquivo não encontrado: {json_path}")
        except Exception as e:
            print(f"Erro ao carregar arquivo diretamente: {str(e)}")
        
        # Tentar extrair scores
        behavior_scores = analyzer.get_behavior_scores(person, year)
        if behavior_scores:
            print("\nScores obtidos com sucesso")
            for dir_name, behaviors in behavior_scores.items():
                print(f"  - {dir_name}: {len(behaviors)} comportamentos")
                
                for comp_name, details in behaviors.items():
                    print(f"    - {comp_name}")
                    
                    for avaliador, scores in details["scores"].items():
                        print(f"      - Avaliador: {avaliador}")
                        print(f"        Score colab: {scores.get('score_colaborador', 'N/A')}")
                        print(f"        Score grupo: {scores.get('score_grupo', 'N/A')}")
        else:
            print("\nSem scores")
            
            # Examinar valores relevantes
            print(f"\nLabels de frequência: {analyzer.frequency_labels}")
            print(f"Pesos de frequência: {analyzer.frequency_weights}")

if __name__ == "__main__":
    main() 