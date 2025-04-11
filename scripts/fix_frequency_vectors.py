#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path

def fix_frequency_vectors(data):
    """Corrige os vetores de frequência para ter 6 posições:
    [n/a, referencia, sempre, quase sempre, poucas vezes, raramente]
    """
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
                    avaliacao['frequencia_colaborador'] = [0, 0, 0, 0, 0, 0]
                elif not isinstance(avaliacao['frequencia_colaborador'], list):
                    avaliacao['frequencia_colaborador'] = [0, 0, 0, 0, 0, 0]
                else:
                    # Converter vetores de 5 posições para 6 posições
                    freq = avaliacao['frequencia_colaborador']
                    if len(freq) == 5:
                        # Adicionar n/a no início
                        avaliacao['frequencia_colaborador'] = [0] + freq
                    elif len(freq) < 6:
                        # Preencher para 6 posições
                        avaliacao['frequencia_colaborador'] = list(freq) + [0] * (6 - len(freq))
                
                # Corrigir frequencia_grupo
                if 'frequencia_grupo' not in avaliacao:
                    avaliacao['frequencia_grupo'] = [0, 0, 0, 0, 0, 0]
                elif not isinstance(avaliacao['frequencia_grupo'], list):
                    avaliacao['frequencia_grupo'] = [0, 0, 0, 0, 0, 0]
                else:
                    # Converter vetores de 5 posições para 6 posições
                    freq = avaliacao['frequencia_grupo']
                    if len(freq) == 5:
                        # Adicionar n/a no início
                        avaliacao['frequencia_grupo'] = [0] + freq
                    elif len(freq) < 6:
                        # Preencher para 6 posições
                        avaliacao['frequencia_grupo'] = list(freq) + [0] * (6 - len(freq))
    
    return data

def process_directory(base_dir):
    """Processa todos os arquivos JSON na estrutura recursivamente"""
    count = 0
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file == 'resultado.json':
                file_path = Path(root) / file
                
                try:
                    # Ler o arquivo
                    with open(file_path, 'r', encoding='utf-8') as f:
                        try:
                            data = json.load(f)
                        except json.JSONDecodeError:
                            print(f"Erro: {file_path} não é um JSON válido, pulando.")
                            continue
                    
                    # Aplicar correções
                    fixed_data = fix_frequency_vectors(data)
                    
                    # Salvar com backup
                    backup_path = file_path.with_suffix('.json.bak')
                    if not backup_path.exists():  # Apenas fazer backup se ainda não existir
                        os.rename(file_path, backup_path)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(fixed_data, f, indent=2, ensure_ascii=False)
                    
                    count += 1
                    print(f"Corrigido: {file_path}")
                    
                except Exception as e:
                    print(f"Erro ao processar {file_path}: {str(e)}")
    
    return count

def main():
    if len(sys.argv) < 2:
        print("Uso: python fix_frequency_vectors.py diretorio_base")
        return
    
    base_dir = sys.argv[1]
    print(f"Corrigindo vetores de frequência em: {base_dir}")
    
    count = process_directory(base_dir)
    print(f"\nTotal de arquivos corrigidos: {count}")

if __name__ == "__main__":
    main() 