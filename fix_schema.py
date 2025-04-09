#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path

def fix_frequencies(data):
    """Corrigir problemas com frequências: garantir que são arrays de inteiros"""
    if 'data' not in data or 'direcionadores' not in data['data']:
        return data
        
    for direcionador in data['data']['direcionadores']:
        if 'comportamentos' not in direcionador:
            continue
            
        for comportamento in direcionador['comportamentos']:
            if 'avaliacoes_grupo' not in comportamento:
                continue
                
            for avaliacao in comportamento['avaliacoes_grupo']:
                # Corrigir frequencia_colaborador
                if 'frequencia_colaborador' not in avaliacao:
                    avaliacao['frequencia_colaborador'] = [0, 0, 0, 0, 0]
                elif not isinstance(avaliacao['frequencia_colaborador'], list):
                    avaliacao['frequencia_colaborador'] = [0, 0, 0, 0, 0]
                else:
                    # Garantir que são inteiros
                    avaliacao['frequencia_colaborador'] = [
                        int(freq) if isinstance(freq, (int, float, str)) else 0
                        for freq in avaliacao['frequencia_colaborador']
                    ]
                    
                    # Garantir tamanho correto (5 elementos)
                    if len(avaliacao['frequencia_colaborador']) < 5:
                        avaliacao['frequencia_colaborador'].extend([0] * (5 - len(avaliacao['frequencia_colaborador'])))
                
                # Corrigir frequencia_grupo
                if 'frequencia_grupo' not in avaliacao:
                    avaliacao['frequencia_grupo'] = [0, 0, 0, 0, 0]
                elif not isinstance(avaliacao['frequencia_grupo'], list):
                    avaliacao['frequencia_grupo'] = [0, 0, 0, 0, 0]
                else:
                    # Garantir que são inteiros
                    avaliacao['frequencia_grupo'] = [
                        int(freq) if isinstance(freq, (int, float, str)) else 0
                        for freq in avaliacao['frequencia_grupo']
                    ]
                    
                    # Garantir tamanho correto (5 elementos)
                    if len(avaliacao['frequencia_grupo']) < 5:
                        avaliacao['frequencia_grupo'].extend([0] * (5 - len(avaliacao['frequencia_grupo'])))
    
    return data

def fix_json_files(data_path):
    """Corrigir todos os arquivos JSON na estrutura <pessoa>/<ano>/resultado.json"""
    try:
        path = Path(data_path)
        fixed_count = 0
        
        for person_dir in path.iterdir():
            if not person_dir.is_dir():
                continue
                
            for year_dir in person_dir.iterdir():
                if not year_dir.is_dir():
                    continue
                    
                resultado_file = year_dir / "resultado.json"
                if resultado_file.exists():
                    try:
                        # Ler o arquivo
                        with open(resultado_file, 'r', encoding='utf-8') as f:
                            try:
                                data = json.load(f)
                            except json.JSONDecodeError:
                                print(f"Erro: {resultado_file} não é um JSON válido, não é possível corrigir")
                                continue
                        
                        # Aplicar correções
                        fixed_data = fix_frequencies(data)
                        
                        # Salvar com backup
                        backup_file = resultado_file.with_suffix('.json.bak')
                        os.rename(resultado_file, backup_file)
                        
                        with open(resultado_file, 'w', encoding='utf-8') as f:
                            json.dump(fixed_data, f, indent=2, ensure_ascii=False)
                            
                        fixed_count += 1
                        print(f"Corrigido: {resultado_file}")
                        
                    except Exception as e:
                        print(f"Erro ao processar {resultado_file}: {str(e)}")
        
        return fixed_count
    except Exception as e:
        print(f"Erro ao corrigir arquivos: {str(e)}")
        return 0

def main():
    if len(sys.argv) < 2:
        print("Uso: python fix_schema.py /caminho/para/dados")
        return
    
    data_path = sys.argv[1]
    print(f"Corrigindo arquivos JSON em: {data_path}")
    
    fixed_count = fix_json_files(data_path)
    print(f"\nTotal de arquivos corrigidos: {fixed_count}")
    print("\nAgora execute o run_report.py para analisar os dados corrigidos.")

if __name__ == "__main__":
    main() 