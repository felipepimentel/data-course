#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path
import pandas as pd
from peopleanalytics.data_pipeline import DataPipeline
from peopleanalytics.evaluation_analyzer import EvaluationAnalyzer
from peopleanalytics.visualization import Visualization

def validate_data_structure(data_path):
    """Verificar se a estrutura dos dados está correta"""
    try:
        has_valid_files = False
        path = Path(data_path)
        
        # Verificar se existem pessoas/anos/resultado.json
        for person_dir in path.iterdir():
            if not person_dir.is_dir():
                continue
                
            for year_dir in person_dir.iterdir():
                if not year_dir.is_dir():
                    continue
                    
                resultado_file = year_dir / "resultado.json"
                if resultado_file.exists():
                    has_valid_files = True
                    
                    # Verificar se o JSON está de acordo com o schema básico
                    try:
                        with open(resultado_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        # Verificações básicas da estrutura
                        if not isinstance(data, dict):
                            print(f"Erro: {resultado_file} não contém um objeto JSON válido")
                            continue
                            
                        if 'data' not in data:
                            print(f"Erro: {resultado_file} não contém o campo 'data'")
                            continue
                            
                        if 'direcionadores' not in data['data']:
                            print(f"Erro: {resultado_file} não contém o campo 'direcionadores'")
                            continue
                            
                        # Verificar se há comportamentos e avaliações
                        direcionadores = data['data']['direcionadores']
                        if not direcionadores:
                            print(f"Aviso: {resultado_file} não contém direcionadores")
                            continue
                            
                        for dir_idx, direcionador in enumerate(direcionadores):
                            if 'comportamentos' not in direcionador:
                                print(f"Erro: Direcionador {dir_idx} em {resultado_file} não contém comportamentos")
                                continue
                                
                            for comp_idx, comportamento in enumerate(direcionador['comportamentos']):
                                if 'avaliacoes_grupo' not in comportamento:
                                    print(f"Erro: Comportamento {comp_idx} em direcionador {dir_idx} em {resultado_file} não contém avaliacoes_grupo")
                                    continue
                                    
                                for aval_idx, avaliacao in enumerate(comportamento['avaliacoes_grupo']):
                                    if 'frequencia_colaborador' not in avaliacao or 'frequencia_grupo' not in avaliacao:
                                        print(f"Erro: Avaliação {aval_idx} em comportamento {comp_idx} em {resultado_file} não contém frequências")
                                        continue
                    except json.JSONDecodeError as e:
                        print(f"Erro ao decodificar JSON em {resultado_file}: {str(e)}")
                    except Exception as e:
                        print(f"Erro ao validar {resultado_file}: {str(e)}")
        
        return has_valid_files
    except Exception as e:
        print(f"Erro ao validar estrutura de dados: {str(e)}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Uso: python run_report.py /caminho/para/dados [ano]")
        return
    
    data_path = sys.argv[1]
    year = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"Verificando estrutura de dados em: {data_path}")
    if not validate_data_structure(data_path):
        print("Erro: Estrutura de dados inválida. Verifique se os arquivos seguem o padrão <pessoa>/<ano>/resultado.json")
        return
    
    # Criar diretório base
    base_dir = os.path.expanduser("~/.peopleanalytics")
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Importando dados de: {data_path}")
    pipeline = DataPipeline(base_dir)
    # Habilitar modo debug para mais informações
    pipeline.debug_mode = True
    
    try:
        # Tratar caso em que ingest_directory retorna None ou não tem formato esperado 
        result = pipeline.ingest_directory(data_path, pattern="*/*/resultado.json", overwrite=True)
        
        if result is None:
            # A função pode não retornar resultado, nesse caso consideramos sucesso
            print("Importação concluída (sem detalhes de resultado)")
        elif isinstance(result, dict) and not result.get('success', False):
            print(f"Erro na importação: {result.get('error', 'Erro desconhecido')}")
            if 'details' in result:
                for detail in result['details']:
                    if not detail.get('success', False):
                        print(f"  - {detail.get('file')}: {detail.get('error')}")
            return
        elif isinstance(result, dict):
            print(f"Importados com sucesso: {result.get('success_count', 0)} arquivos")
        else:
            print(f"Importação concluída com resultado: {result}")
    except Exception as e:
        print(f"Erro durante a importação: {str(e)}")
        # Continuar mesmo com erro, pode ter importado alguns arquivos
    
    print("Analisando dados...")
    analyzer = EvaluationAnalyzer(base_dir)
    visualizer = Visualization()
    
    # Listar pessoas e anos disponíveis
    all_people = analyzer.get_all_people()
    all_years = analyzer.get_all_years()
    
    print(f"\nPessoas encontradas ({len(all_people)}): {', '.join(all_people[:5])}...")
    print(f"Anos encontrados: {', '.join(all_years)}")
    
    # Se não especificou ano, usar o mais recente
    if not year and all_years:
        year = all_years[-1]
        print(f"Usando ano mais recente: {year}")
    
    # Gerar relatório comparativo para o ano
    if year and year in all_years:
        print(f"\nGerando relatório comparativo para {year}...")
        df = analyzer.compare_people_for_year(year)
        if not df.empty:
            # Salvar como CSV
            csv_path = os.path.join(output_dir, f"comparativo_{year}.csv")
            df.to_csv(csv_path, index=False)
            print(f"Relatório CSV salvo em: {csv_path}")
            
            # Gerar visualização
            png_path = os.path.join(output_dir, f"comparativo_{year}.png")
            try:
                analyzer.plot_comparative_report(df, year, png_path)
                print(f"Gráfico salvo em: {png_path}")
            except Exception as e:
                print(f"Erro ao gerar gráfico: {str(e)}")
            
            # Gerar HTML interativo
            if len(all_people) > 0:
                try:
                    html_path = os.path.join(output_dir, f"interativo_{year}.html")
                    data = {
                        'title': f'Relatório Comparativo {year}',
                        'year': year,
                        'people_data': df.to_dict('records')
                    }
                    visualizer.generate_interactive_html(data, html_path)
                    print(f"Relatório interativo salvo em: {html_path}")
                except Exception as e:
                    print(f"Erro ao gerar HTML interativo: {str(e)}")
        else:
            print(f"Nenhum dado encontrado para o ano {year}")
            
            # Tentar diagnosticar o problema
            print("\nDiagnosticando problema...")
            for person in all_people[:5]:  # Verificar apenas algumas pessoas para diagnóstico
                evaluation = analyzer.get_evaluations_for_person(person, year)
                if not evaluation:
                    print(f"  - {person}: Nenhum dado para o ano {year}")
                    continue
                    
                if not evaluation.get('success', False):
                    print(f"  - {person}: Dados com erro - {evaluation.get('error', 'Desconhecido')}")
                    continue
                    
                behavior_scores = analyzer.get_behavior_scores(person, year)
                if not behavior_scores:
                    print(f"  - {person}: Sem scores de comportamento. Verificar estrutura JSON.")
                    
                    # Diagnóstico detalhado
                    try:
                        with open(os.path.join(base_dir, person, year, "resultado.json"), 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if 'data' not in data:
                                print(f"      Problema: JSON não contém campo 'data'")
                            elif 'direcionadores' not in data['data']:
                                print(f"      Problema: JSON não contém campo 'direcionadores'")
                            elif not data['data']['direcionadores']:
                                print(f"      Problema: Lista de direcionadores está vazia")
                            else:
                                print(f"      Estrutura de direcionadores:")
                                for i, direcionador in enumerate(data['data']['direcionadores']):
                                    print(f"      - Direcionador {i+1}: {direcionador.get('direcionador', 'Sem nome')}")
                                    comportamentos = direcionador.get('comportamentos', [])
                                    if not comportamentos:
                                        print(f"        Sem comportamentos")
                                    else:
                                        for j, comportamento in enumerate(comportamentos):
                                            print(f"        Comportamento {j+1}: {comportamento.get('comportamento', 'Sem nome')}")
                                            avaliacoes = comportamento.get('avaliacoes_grupo', [])
                                            if not avaliacoes:
                                                print(f"          Sem avaliações")
                                            else:
                                                for k, avaliacao in enumerate(avaliacoes):
                                                    avaliador = avaliacao.get('avaliador', 'Desconhecido')
                                                    print(f"          Avaliador: {avaliador}")
                                                    freq_colaborador = avaliacao.get('frequencia_colaborador', [])
                                                    freq_grupo = avaliacao.get('frequencia_grupo', [])
                                                    print(f"          frequencia_colaborador: {freq_colaborador}")
                                                    print(f"          frequencia_grupo: {freq_grupo}")
                    except Exception as e:
                        print(f"      Erro ao analisar arquivo: {str(e)}")
                    
                    continue
                    
                print(f"  - {person}: Dados parecem válidos, mas não foram incluídos no relatório")

if __name__ == "__main__":
    main() 