# People Analytics

Sistema de análise de dados de pessoas usando DuckDB.

## Estrutura

```
.
├── <nome>/              # Diretório por pessoa
│   └── <ano>/          # Diretório por ano
│       └── resultado.json     # Arquivo de avaliações
├── output/             # Diretório com resultados
│   ├── backups/       # Backups dos dados
│   ├── exports/       # Dados exportados
│   ├── logs/          # Logs de processamento
│   ├── plots/         # Gráficos gerados
│   ├── reports/       # Relatórios em Excel
│   └── summary/       # Resumos em HTML/JSON
└── peopleanalytics/   # Código fonte
```

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

Todos os comandos aceitam os argumentos `--data-path` e `--output-path` para especificar os diretórios de entrada e saída. Por padrão:
- `--data-path`: Usa o diretório atual (`.`)
- `--output-path`: Usa o diretório `./output` dentro do diretório atual

### Validação de Dados

```bash
# Validar dados no diretório atual
python3 -m peopleanalytics validate

# Validar dados em um diretório específico
python3 -m peopleanalytics validate --data-path ./meus_dados --output-path ./resultados
```

### Importação de Dados

```bash
# Importar um arquivo específico
python3 -m peopleanalytics import ./pessoa/2023/resultado.json

# Importar um diretório específico
python3 -m peopleanalytics import ./pessoa/2023

# Importar recursivamente a partir do diretório atual
python3 -m peopleanalytics import . --recursive

# Importar recursivamente de um diretório específico
python3 -m peopleanalytics import ./meus_dados --recursive

# Importar com diretórios de entrada e saída personalizados
python3 -m peopleanalytics import . --recursive --data-path ./meus_dados --output-path ./resultados
```

### Exportação de Dados

```bash
# Exportar todos os dados
python3 -m peopleanalytics export --all

# Exportar dados de uma pessoa específica
python3 -m peopleanalytics export --person "Nome da Pessoa"

# Exportar dados de um ano específico
python3 -m peopleanalytics export --year 2023

# Exportar dados de um diretório específico
python3 -m peopleanalytics export --all --data-path ./meus_dados --output-path ./exportados
```

### Geração de Relatórios

```bash
# Gerar todos os relatórios para 2023
python3 -m peopleanalytics report all --year 2023

# Gerar relatório de frequência
python3 -m peopleanalytics report attendance --year 2023

# Gerar relatório de pagamentos
python3 -m peopleanalytics report payment --year 2023

# Gerar relatórios de um diretório específico
python3 -m peopleanalytics report all --year 2023 --data-path ./dados --output-path ./relatorios
```

### Geração de Resumos

```bash
# Gerar resumo em JSON
python3 -m peopleanalytics summary --format json

# Gerar resumo em HTML
python3 -m peopleanalytics summary --format html

# Gerar resumo em CSV
python3 -m peopleanalytics summary --format csv

# Gerar resumo de um diretório específico
python3 -m peopleanalytics summary --format json --data-path ./dados --output-path ./resumos
```

### Outros Comandos

```bash
# Listar pessoas ou anos
python3 -m peopleanalytics list people
python3 -m peopleanalytics list years

# Criar backup
python3 -m peopleanalytics backup

# Gerar gráficos
python3 -m peopleanalytics plot all

# Adicionar registro de frequência
python3 -m peopleanalytics add-attendance --person "Nome" --year 2023 --date 2023-01-01 --status presente

# Adicionar registro de pagamento
python3 -m peopleanalytics add-payment --person "Nome" --year 2023 --date 2023-01-15 --amount 1000 --type salary

# Atualizar perfil
python3 -m peopleanalytics update-profile --person "Nome" --year 2023

# Criar dados de exemplo
python3 -m peopleanalytics create-sample
```

## Formatos de Dados

### resultado.json

```json
{
  "data": {
    "nome": "Nome da Pessoa",
    "ano": 2023,
    "direcionadores": [
      {
        "nome": "Nome do Direcionador",
        "peso": 25,
        "comportamentos": [
          {
            "nome": "Nome do Comportamento",
            "peso": 25,
            "avaliacoes_grupo": [
              {
                "frequencia_colaborador": [1, 2, 3, 4, 5],
                "frequencia_grupo": [1, 2, 3, 4, 5],
                "peso": 20
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### perfil.json

```json
{
  "nome_completo": "Nome da Pessoa",
  "funcional": "12345",
  "funcional_gestor": "67890", 
  "nome_gestor": "Nome do Gestor",
  "cargo": "Analista",
  "codigo_cargo": "AN01",
  "nivel_cargo": "1",
  "nome_nivel_cargo": "Junior",
  "nome_departamento": "TI",
  "tipo_carreira": "Técnica",
  "codigo_comunidade": "COM01",
  "nome_comunidade": "Backend",
  "codigo_squad": "SQ01", 
  "nome_squad": "Squad 1",
  "codigo_papel": "DEV",
  "nome_papel": "Desenvolvedor",
  "tipo_gestao": false,
  "is_congelamento": false,
  "data_congelamento": null
}
```

### frequencias.json
```json
[
  {
    "data": "2023-01-01",
    "status": "presente",
    "justificativa": ""
  }
]
```

### pagamentos.json
```json
[
  {
    "data": "2023-01-15",
    "valor": 1000,
    "descricao": ""
  }
]
```

## Usage

### Commands

#### Import Data
```bash
# Import a single file
python3 -m peopleanalytics import ./pessoa/2023/resultado.json

# Import a directory
python3 -m peopleanalytics import ./pessoa/2023

# Import recursively from current directory
python3 -m peopleanalytics import . --recursive

# Import from specific directory
python3 -m peopleanalytics import ./meus_dados --recursive

# Import with custom paths
python3 -m peopleanalytics import . --recursive --data-path ./meus_dados --output-path ./resultados
```

#### Sync and Generate Reports
```bash
# Sync and generate reports for all data
python3 -m peopleanalytics sync

# Sync recursively from current directory
python3 -m peopleanalytics sync --recursive

# Sync from specific directory
python3 -m peopleanalytics sync --data-path ./meus_dados

# Sync with custom output path
python3 -m peopleanalytics sync --data-path ./meus_dados --output-path ./resultados
```

The sync command will:
1. Import all data from the specified directory
2. For each person/year directory:
   - Create an `analytics` subdirectory
   - Generate and save:
     - Excel report (`report.xlsx`)
     - HTML summary (`summary.html`)
     - Markdown summary (`summary.md`)
     - MermaidJS visualizations (`visualization.md`)
     - AI prompt for generating feedback (`ai_prompt.md`)
     - Stakeholder comparison report (`stakeholder_comparison.md`)

The MermaidJS visualizations include:
- Bar charts showing performance by competency area
- Pie charts showing assessment distribution
- Comparison charts between individual and group performance

The AI prompt file contains structured data about the employee's performance that can be used with AI tools like ChatGPT to generate comprehensive feedback reports automatically.

The stakeholder comparison report analyzes evaluations from different perspectives:
- Compares manager, peer/partner, and self-evaluations against peer group averages
- Provides a detailed breakdown by competency area and behavior
- Highlights the strongest and development areas
- Identifies gaps between different stakeholder perspectives
- Shows areas with the most significant differences in perception

#### Validate Data

```bash
# Validar dados no diretório atual
python3 -m peopleanalytics validate

# Validar dados em um diretório específico
python3 -m peopleanalytics validate --data-path ./meus_dados --output-path ./resultados
```

## Licença

MIT