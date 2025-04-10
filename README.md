# People Analytics

Sistema de análise de dados de pessoas usando DuckDB.

## Estrutura

```
.
├── data/                  # Diretório com dados de entrada
│   └── <pessoa>/         # Diretório por pessoa
│       └── <ano>/        # Diretório por ano
│           ├── resultado.json     # Avaliações
│           ├── perfil.json       # Dados do perfil
│           ├── frequencias.json  # Dados de frequência
│           └── pagamentos.json   # Dados de pagamentos
├── output/               # Diretório com resultados
│   ├── backups/         # Backups dos dados
│   ├── exports/         # Dados exportados
│   ├── logs/            # Logs de processamento
│   ├── plots/           # Gráficos gerados
│   ├── reports/         # Relatórios em Excel
│   └── summary/         # Resumos em HTML/JSON
└── peopleanalytics/     # Código fonte
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

### Importar e Analisar Dados

```bash
python -m peopleanalytics import --data_dir ./data --output_dir ./output
```

### Gerar Relatórios

```bash
python -m peopleanalytics report --year 2023
```

### Exportar Dados

```bash
python -m peopleanalytics export --all
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

## Licença

MIT