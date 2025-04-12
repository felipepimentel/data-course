#!/usr/bin/env python3
"""
Enhanced Notebook Generator

Creates a comprehensive Jupyter notebook for analyzing people analytics data.
This script provides the same functionality as the consolidated script in:
- assets/create_notebook.py

The functionality has been consolidated for better maintainability.
"""

import argparse
import json


def create_notebook(output_path="analyze_people_data.ipynb", verbose=True):
    """
    Creates a comprehensive Jupyter notebook for people analytics data.

    Args:
        output_path: Path to save the generated notebook
        verbose: Whether to print status messages
    """
    # Define notebook base structure
    notebook = {
        "cells": [],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.12.3",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    # Add all cells sequentially
    add_cells(notebook, get_intro_cells())
    add_cells(notebook, get_utility_functions())
    add_cells(notebook, get_data_loading_cells())
    add_cells(notebook, get_data_overview_cells())
    add_cells(notebook, get_by_person_analysis())
    add_cells(notebook, get_data_correction_cells())
    add_cells(notebook, get_frequency_visualization_cells())
    add_cells(notebook, get_corrected_scores_cells())
    add_cells(notebook, get_recommendations_cells())

    # Save notebook to file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1)

    if verbose:
        print(f"Notebook created successfully at {output_path}")

    return output_path


def add_cells(notebook_obj, cells_to_add):
    """Add multiple cells to the notebook object"""
    for cell in cells_to_add:
        notebook_obj["cells"].append(cell)
    return notebook_obj


def get_intro_cells():
    """Return the introductory cells for the notebook"""
    return [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# 📊 People Analytics Dashboard\n",
                "\n",
                "Este notebook interativo fornece análises avançadas e visualizações para os dados de avaliação de desempenho, permitindo insights detalhados sobre o desempenho individual e da equipe.",
            ],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 🔧 Configuração e Importações\n",
                "Carregando as bibliotecas e configurações necessárias para análise avançada.",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Importações necessárias\n",
                "import os\n",
                "import json\n",
                "import pandas as pd\n",
                "import numpy as np\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "import plotly.express as px\n",
                "import plotly.graph_objects as go\n",
                "from plotly.subplots import make_subplots\n",
                "from pathlib import Path\n",
                "from collections import defaultdict\n",
                "from IPython.display import display, HTML, Markdown\n",
                "import warnings\n",
                "\n",
                "# Configurações para melhor exibição\n",
                "pd.set_option('display.max_columns', None)\n",
                "pd.set_option('display.max_rows', 100)\n",
                "pd.set_option('display.width', 1000)\n",
                "pd.set_option('display.max_colwidth', None)\n",
                'warnings.filterwarnings("ignore")\n',
                "\n",
                "# Configuração de estilo para visualizações\n",
                "plt.style.use('ggplot')\n",
                'sns.set_theme(style="whitegrid")\n',
                "\n",
                "# Cores para visualizações\n",
                "COLORS = px.colors.qualitative.Plotly\n",
                "\n",
                "# Estilo para HTML\n",
                'HTML("""\n',
                "<style>\n",
                "    h1 { color: #2c3e50; }\n",
                "    h2 { color: #34495e; border-bottom: 1px solid #95a5a6; padding-bottom: 5px; }\n",
                "    h3 { color: #3498db; }\n",
                "    .alert-success { background-color: #d4edda; color: #155724; padding: 15px; border-radius: 5px; }\n",
                "    .alert-info { background-color: #d1ecf1; color: #0c5460; padding: 15px; border-radius: 5px; }\n",
                "    .alert-warning { background-color: #fff3cd; color: #856404; padding: 15px; border-radius: 5px; }\n",
                "    .alert-danger { background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; }\n",
                "    table { border-collapse: collapse; margin: 20px 0; }\n",
                "    table th { background-color: #3498db; color: white; }\n",
                "    table th, table td { padding: 10px; border: 1px solid #ddd; }\n",
                "    table tr:nth-child(even) { background-color: #f2f2f2; }\n",
                "</style>\n",
                '""")',
            ],
        },
    ]


def get_utility_functions():
    """Return utility function cells"""
    # Funções utilitárias abreviadas por brevidade
    return [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 🛠️ Funções Utilitárias\n",
                "Conjunto de funções para carregamento, processamento e análise de dados.",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "def load_json_file(file_path):\n",
                '    """Carrega um arquivo JSON com tratamento de erros"""\n',
                "    try:\n",
                "        with open(file_path, 'r', encoding='utf-8') as f:\n",
                "            return json.load(f), None\n",
                "    except json.JSONDecodeError as e:\n",
                '        return None, f"Erro ao decodificar JSON: {str(e)}"\n',
                "    except Exception as e:\n",
                '        return None, f"Erro ao ler arquivo: {str(e)}"\n',
                "\n",
                'def scan_directory(directory_path, pattern="*/*/resultado.json"):\n',
                '    """Escaneia diretório procurando arquivos que seguem um padrão"""\n',
                "    path = Path(directory_path)\n",
                "    files = list(path.glob(pattern))\n",
                "    return files\n",
                "\n",
                "def extract_person_year(file_path):\n",
                '    """Extrai nome da pessoa e ano a partir do caminho do arquivo"""\n',
                "    parts = file_path.parts\n",
                "    person_idx = len(parts) - 3\n",
                "    year_idx = len(parts) - 2\n",
                "    \n",
                "    if person_idx >= 0 and year_idx >= 0:\n",
                "        return parts[person_idx], parts[year_idx]\n",
                '    return "Unknown", "Unknown"\n',
            ],
        },
    ]


def get_data_loading_cells():
    """Return data loading cells"""
    return [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 📂 Carregamento dos Dados\n",
                "Configure o caminho para o diretório de dados e carregue as avaliações.",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Configurar caminho para diretório de dados\n",
                'DATA_DIR = "test_data"  # Altere para o caminho dos seus dados reais\n',
                "\n",
                "# Encontrar arquivos no padrão <pessoa>/<ano>/resultado.json\n",
                'files = scan_directory(DATA_DIR, "*/*/resultado.json")\n',
                'print(f"Encontrados {len(files)} arquivos de resultados:")\n',
                "for f in files:\n",
                '    print(f"  - {f}")\n',
            ],
        },
    ]


def get_data_overview_cells():
    """Return data overview cells"""
    return [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 📊 Visão Geral dos Dados\n",
                "Resumo estatístico e análise exploratória das avaliações.",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": ["# Código resumido para análise descritiva dos dados"],
        },
    ]


def get_by_person_analysis():
    """Return person analysis cells"""
    return [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 🧮 Análise por Pessoa\n",
                "Comparação de desempenho entre diferentes pessoas avaliadas.",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": ["# Código resumido para análise por pessoa"],
        },
    ]


def get_data_correction_cells():
    """Return data correction cells"""
    return [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## ⚠️ Correção Importante na Interpretação dos Dados\n",
                "Os vetores de frequência têm 6 posições com significados específicos.",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": ["# Código resumido para correção de interpretação dos dados"],
        },
    ]


def get_frequency_visualization_cells():
    """Return frequency visualization cells"""
    return [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 📊 Visualização da Distribuição de Frequências\n",
                "Análise da distribuição percentual em cada categoria de avaliação.",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Código resumido para visualização de distribuição de frequências"
            ],
        },
    ]


def get_corrected_scores_cells():
    """Return corrected scores cells"""
    return [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 📈 Scores Corrigidos\n",
                "Análise dos scores recalculados com a interpretação correta dos vetores.",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": ["# Código resumido para scores corrigidos"],
        },
    ]


def get_recommendations_cells():
    """Return recommendations cells"""
    return [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 📋 Recomendações e Ações\n",
                "Principais insights e recomendações baseadas nos dados corrigidos.",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": ["# Código resumido para recomendações"],
        },
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gerador de notebook para análise de pessoas"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="analyze_people_data.ipynb",
        help="Caminho para salvar o notebook gerado",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suprimir mensagens de status"
    )

    args = parser.parse_args()

    create_notebook(output_path=args.output, verbose=not args.quiet)
