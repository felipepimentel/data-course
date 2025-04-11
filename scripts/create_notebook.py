import json
import os

# Definir conteúdo do notebook
notebook = {
 'cells': [
  {
   'cell_type': 'markdown',
   'metadata': {},
   'source': ['# People Analytics - Análise Exploratória\n', '\n', 'Este notebook permite analisar os dados de avaliações, diagnosticar problemas e visualizar resultados.']
  },
  {
   'cell_type': 'code',
   'execution_count': None,
   'metadata': {},
   'outputs': [],
   'source': ['# Importações necessárias\n', 'import os\n', 'import json\n', 'import pandas as pd\n', 'import numpy as np\n', 'import matplotlib.pyplot as plt\n', 'import seaborn as sns\n', 'from pathlib import Path\n', 'from collections import defaultdict\n', 'from IPython.display import display, HTML\n', '\n', '# Configuração para exibição de dados\n', 'pd.set_option(\'display.max_columns\', None)\n', 'pd.set_option(\'display.max_rows\', 100)\n', 'pd.set_option(\'display.width\', 1000)\n', 'pd.set_option(\'display.max_colwidth\', None)\n', '\n', '# Configuração de estilo para visualizações\n', 'plt.style.use(\'ggplot\')\n', 'sns.set_theme(style=\"whitegrid\")']
  },
  {
   'cell_type': 'markdown',
   'metadata': {},
   'source': ['## Definição de funções úteis']
  },
  {
   'cell_type': 'code',
   'execution_count': None,
   'metadata': {},
   'outputs': [],
   'source': ['def load_json_file(file_path):\n', '    """Carrega um arquivo JSON com tratamento de erros"""\n', '    try:\n', '        with open(file_path, \'r\', encoding=\'utf-8\') as f:\n', '            return json.load(f), None\n', '    except json.JSONDecodeError as e:\n', '        return None, f"Erro ao decodificar JSON: {str(e)}"\n', '    except Exception as e:\n', '        return None, f"Erro ao ler arquivo: {str(e)}"\n', '\n', 'def scan_directory(directory_path, pattern="*/*/resultado.json"):\n', '    """Escaneia diretório procurando arquivos que seguem um padrão"""\n', '    path = Path(directory_path)\n', '    files = list(path.glob(pattern))\n', '    return files\n', '\n', 'def diagnose_json_file(file_path):\n', '    """Diagnostica problemas em um arquivo JSON de avaliação"""\n', '    data, error = load_json_file(file_path)\n', '    if error:\n', '        return {"file": str(file_path), "status": "error", "message": error}\n', '    \n', '    issues = []\n', '    \n', '    # Verificar estrutura básica\n', '    if \'data\' not in data:\n', '        issues.append("Campo \'data\' ausente")\n', '    elif \'direcionadores\' not in data[\'data\']:\n', '        issues.append("Campo \'direcionadores\' ausente")\n', '    elif not data[\'data\'][\'direcionadores\']:\n', '        issues.append("Lista de direcionadores vazia")\n', '    else:\n', '        # Verificar cada direcionador e comportamento\n', '        for i, direcionador in enumerate(data[\'data\'][\'direcionadores\']):\n', '            if \'comportamentos\' not in direcionador:\n', '                issues.append(f"Direcionador {i+1} não tem campo \'comportamentos\'")\n', '                continue\n', '                \n', '            for j, comportamento in enumerate(direcionador.get(\'comportamentos\', [])):\n', '                if \'avaliacoes_grupo\' not in comportamento:\n', '                    issues.append(f"Comportamento {j+1} em Direcionador {i+1} não tem campo \'avaliacoes_grupo\'")\n', '                    continue\n', '                    \n', '                for k, avaliacao in enumerate(comportamento.get(\'avaliacoes_grupo\', [])):\n', '                    if \'frequencia_colaborador\' not in avaliacao:\n', '                        issues.append(f"Avaliação {k+1} em Comportamento {j+1} não tem campo \'frequencia_colaborador\'")\n', '                    elif not isinstance(avaliacao.get(\'frequencia_colaborador\'), list):\n', '                        issues.append(f"Campo \'frequencia_colaborador\' não é uma lista em Avaliação {k+1}")\n', '                        \n', '                    if \'frequencia_grupo\' not in avaliacao:\n', '                        issues.append(f"Avaliação {k+1} em Comportamento {j+1} não tem campo \'frequencia_grupo\'")\n', '                    elif not isinstance(avaliacao.get(\'frequencia_grupo\'), list):\n', '                        issues.append(f"Campo \'frequencia_grupo\' não é uma lista em Avaliação {k+1}")\n', '    \n', '    return {\n', '        "file": str(file_path),\n', '        "status": "ok" if not issues else "issues",\n', '        "issues": issues,\n', '        "data": data\n', '    }']
  },
  {
   'cell_type': 'markdown',
   'metadata': {},
   'source': ['## Diretório dos Dados\n', '\n', 'Configure o caminho para o diretório de dados:']
  },
  {
   'cell_type': 'code',
   'execution_count': None,
   'metadata': {},
   'outputs': [],
   'source': ['# Configurar caminho para diretório de dados\n', 'DATA_DIR = "teste"  # Altere para o caminho dos seus dados reais\n', '\n', '# Encontrar arquivos no padrão <pessoa>/<ano>/resultado.json\n', 'files = scan_directory(DATA_DIR, "*/*/resultado.json")\n', 'print(f"Encontrados {len(files)} arquivos de resultados:")\n', 'for f in files:\n', '    print(f"  - {f}")']
  }
 ],
 'metadata': {
  'kernelspec': {
   'display_name': 'Python 3',
   'language': 'python',
   'name': 'python3'
  },
  'language_info': {
   'codemirror_mode': {
    'name': 'ipython',
    'version': 3
   },
   'file_extension': '.py',
   'mimetype': 'text/x-python',
   'name': 'python',
   'nbconvert_exporter': 'python',
   'pygments_lexer': 'ipython3',
   'version': '3.12.3'
  }
 },
 'nbformat': 4,
 'nbformat_minor': 4
}

# Salvar notebook
with open('analyze_people_data.ipynb', 'w') as f:
    json.dump(notebook, f, indent=1)

print('Notebook criado com sucesso!')
