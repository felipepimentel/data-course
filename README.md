# People Analytics

Sistema de análise de dados de pessoas usando DuckDB.

## Estrutura

```
.
├── assets/             # Recursos estáticos
│   └── schemas/       # Esquemas JSON
├── data/               # Dados de entrada
│   └── rawdata.json   # Dados brutos
├── notebooks/          # Jupyter notebooks
│   ├── analyze_people_data.ipynb
│   ├── analyze_people_data_enhanced.ipynb
│   └── analyze_people_data_enhanced_complete.ipynb
├── output/             # Diretório com resultados
│   ├── action_plans/  # Planos de ação
│   ├── ai_prompts/    # Prompts para IA
│   ├── benchmark_reports/ # Relatórios de benchmark
│   ├── heat_maps/     # Mapas de calor
│   ├── logs/          # Logs de processamento
│   ├── mermaid/       # Diagramas Mermaid
│   ├── radar_charts/  # Gráficos de radar
│   ├── reports/       # Relatórios em Excel
│   ├── stakeholder_analysis/ # Análises de stakeholders
│   ├── summaries/     # Resumos naturais
│   ├── summary/       # Resumos em HTML/JSON
│   └── team_reports/  # Relatórios de equipe
├── peopleanalytics/    # Código fonte principal (pacote Python)
│   ├── templates/     # Templates HTML
│   └── *.py           # Módulos Python
├── scripts/            # Scripts de utilidade
├── tests/              # Testes
│   ├── data/          # Dados para testes
│   └── unit/          # Testes unitários
└── requirements.txt    # Dependências do projeto
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
     - Time series analysis (`time_series.md`)
     - Radar chart visualization (`radar_chart.html`)
     - Team aggregation report (`team_report.md`)
     - Benchmark report (`benchmark_report.md`)
     - Heat map visualization (`heat_map.md`)
     - Natural language summary (`narrative_summary.md`)
     - Development action plan (`action_plan.md`)

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

The time series analysis tracks performance trends over time:
- Shows performance evolution across multiple evaluation cycles
- Highlights improvement and decline areas
- Provides year-over-year comparisons with visual charts
- Identifies long-term patterns in specific competency areas

The radar chart visualization offers a multi-dimensional view:
- Interactive graphical representation of all competencies
- Compares individual scores against peer group averages
- Shows multiple stakeholder perspectives in a single view
- Clearly identifies strong and weak areas at a glance

The team aggregation report offers organizational insights:
- Aggregates performance data across departments or teams
- Identifies collective strengths and development opportunities
- Compares performance between different organizational units
- Provides recommendations for team-wide training and development

The benchmark report compares performance against standards:
- Evaluates readiness for promotion to the next level
- Shows gaps between current performance and expectations
- Compares against both current level and next level benchmarks
- Provides specific development focus areas for career advancement

The heat map visualization offers a color-coded analysis:
- Provides an easy-to-scan overview of all competency areas
- Uses color coding to quickly identify strengths and weaknesses
- Shows all stakeholder perspectives in a consolidated view
- Offers a comprehensive view of performance at different granularity levels

The natural language summary provides a narrative overview:
- Translates data points into readable paragraphs
- Highlights key findings in conversational language
- Provides context and nuance to numerical ratings
- Offers an accessible summary for quick understanding

The development action plan provides structured next steps:
- Targets specific improvement areas based on evaluation results
- Includes suggested activities and resources for development
- Provides templates for tracking progress and accountability
- Focuses on leveraging strengths while addressing weaknesses

#### Validate Data

```bash
# Validar dados no diretório atual
python3 -m peopleanalytics validate

# Validar dados em um diretório específico
python3 -m peopleanalytics validate --data-path ./meus_dados --output-path ./resultados
```

## Licença

MIT