#!/usr/bin/env python3
import os
import json
from pathlib import Path

def create_sample_data(output_dir):
    """Criar dados de exemplo para Pessoa1 e Pessoa2 com formato correto dos vetores de frequência"""
    # Criar estrutura de diretórios
    pessoa1_dir = Path(output_dir) / "Pessoa1" / "2023"
    pessoa2_dir = Path(output_dir) / "Pessoa2" / "2023"
    
    pessoa1_dir.mkdir(parents=True, exist_ok=True)
    pessoa2_dir.mkdir(parents=True, exist_ok=True)
    
    # Dados de exemplo para Pessoa1
    pessoa1_data = {
        "success": True,
        "status_code": 200,
        "data": {
            "conceito_ciclo_filho_descricao": "Exceeds Expectations",
            "direcionadores": [
                {
                    "direcionador": "Liderança",
                    "pergunta_final": "Quão bem a pessoa lidera?",
                    "comportamentos": [
                        {
                            "comportamento": "Comunicação Efetiva",
                            "pergunta_final": "Quão bem a pessoa se comunica?",
                            "avaliacoes_grupo": [
                                {
                                    "avaliador": "%todos",
                                    "frequencia_colaborador": [0, 1, 2, 1, 0, 0],
                                    "frequencia_grupo": [0, 0, 1, 2, 1, 0]
                                }
                            ],
                            "consolidado": [
                                {
                                    "avaliador": "%todos",
                                    "frequencias_colaborador": [0, 1, 2, 1, 0, 0],
                                    "frequencias_grupo": [0, 0, 1, 2, 1, 0]
                                }
                            ]
                        },
                        {
                            "comportamento": "Tomada de Decisão",
                            "pergunta_final": "Quão bem a pessoa toma decisões?",
                            "avaliacoes_grupo": [
                                {
                                    "avaliador": "%todos",
                                    "frequencia_colaborador": [0, 1, 2, 1, 0, 0],
                                    "frequencia_grupo": [0, 0, 1, 2, 1, 0]
                                }
                            ],
                            "consolidado": [
                                {
                                    "avaliador": "%todos",
                                    "frequencias_colaborador": [0, 1, 2, 1, 0, 0],
                                    "frequencias_grupo": [0, 0, 1, 2, 1, 0]
                                }
                            ]
                        }
                    ]
                },
                {
                    "direcionador": "Inovação",
                    "pergunta_final": "Quão inovadora é a pessoa?",
                    "comportamentos": [
                        {
                            "comportamento": "Criatividade",
                            "pergunta_final": "Quão criativa é a pessoa?",
                            "avaliacoes_grupo": [
                                {
                                    "avaliador": "%todos",
                                    "frequencia_colaborador": [0, 0, 3, 1, 0, 0],
                                    "frequencia_grupo": [0, 1, 1, 1, 1, 0]
                                }
                            ],
                            "consolidado": [
                                {
                                    "avaliador": "%todos",
                                    "frequencias_colaborador": [0, 0, 3, 1, 0, 0],
                                    "frequencias_grupo": [0, 1, 1, 1, 1, 0]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }
    
    # Dados de exemplo para Pessoa2
    pessoa2_data = {
        "success": True,
        "status_code": 200,
        "data": {
            "conceito_ciclo_filho_descricao": "Meets Expectations",
            "direcionadores": [
                {
                    "direcionador": "Liderança",
                    "pergunta_final": "Quão bem a pessoa lidera?",
                    "comportamentos": [
                        {
                            "comportamento": "Comunicação Efetiva",
                            "pergunta_final": "Quão bem a pessoa se comunica?",
                            "avaliacoes_grupo": [
                                {
                                    "avaliador": "%todos",
                                    "frequencia_colaborador": [0, 1, 1, 1, 1, 0],
                                    "frequencia_grupo": [0, 0, 2, 1, 1, 0]
                                }
                            ],
                            "consolidado": [
                                {
                                    "avaliador": "%todos",
                                    "frequencias_colaborador": [0, 1, 1, 1, 1, 0],
                                    "frequencias_grupo": [0, 0, 2, 1, 1, 0]
                                }
                            ]
                        },
                        {
                            "comportamento": "Tomada de Decisão",
                            "pergunta_final": "Quão bem a pessoa toma decisões?",
                            "avaliacoes_grupo": [
                                {
                                    "avaliador": "%todos",
                                    "frequencia_colaborador": [0, 0, 1, 2, 1, 0],
                                    "frequencia_grupo": [0, 1, 1, 1, 1, 0]
                                }
                            ],
                            "consolidado": [
                                {
                                    "avaliador": "%todos",
                                    "frequencias_colaborador": [0, 0, 1, 2, 1, 0],
                                    "frequencias_grupo": [0, 1, 1, 1, 1, 0]
                                }
                            ]
                        }
                    ]
                },
                {
                    "direcionador": "Inovação",
                    "pergunta_final": "Quão inovadora é a pessoa?",
                    "comportamentos": [
                        {
                            "comportamento": "Criatividade",
                            "pergunta_final": "Quão criativa é a pessoa?",
                            "avaliacoes_grupo": [
                                {
                                    "avaliador": "%todos",
                                    "frequencia_colaborador": [0, 0, 1, 1, 2, 0],
                                    "frequencia_grupo": [0, 0, 2, 1, 1, 0]
                                }
                            ],
                            "consolidado": [
                                {
                                    "avaliador": "%todos",
                                    "frequencias_colaborador": [0, 0, 1, 1, 2, 0],
                                    "frequencias_grupo": [0, 0, 2, 1, 1, 0]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }
    
    # Perfil para Pessoa1
    pessoa1_perfil = {
        "cargo": "Gerente de Projetos",
        "nivel_cargo": "Senior"
    }
    
    # Perfil para Pessoa2
    pessoa2_perfil = {
        "cargo": "Analista de Sistemas",
        "nivel_cargo": "Junior"
    }
    
    # Salvar arquivos
    with open(pessoa1_dir / "resultado.json", 'w', encoding='utf-8') as f:
        json.dump(pessoa1_data, f, ensure_ascii=False, indent=2)
        
    with open(pessoa1_dir / "perfil.json", 'w', encoding='utf-8') as f:
        json.dump(pessoa1_perfil, f, ensure_ascii=False, indent=2)
        
    with open(pessoa2_dir / "resultado.json", 'w', encoding='utf-8') as f:
        json.dump(pessoa2_data, f, ensure_ascii=False, indent=2)
        
    with open(pessoa2_dir / "perfil.json", 'w', encoding='utf-8') as f:
        json.dump(pessoa2_perfil, f, ensure_ascii=False, indent=2)
    
    print(f"Dados gerados em {pessoa1_dir} e {pessoa2_dir}")

if __name__ == "__main__":
    create_sample_data("test_data") 