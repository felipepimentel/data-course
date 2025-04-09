# Itaú Avaliação 360

Ferramenta para análise de avaliações de desempenho 360 graus, com geração de relatórios individuais e comparativos.

## Funcionalidades

O projeto possui as seguintes funcionalidades:

1. **Análise de Avaliações** (`analyze_evaluations.py`): Analisa dados de avaliação para extrair tendências, comportamentos e comparações com o grupo.

2. **Geração de Feedback** (`generate_feedback.py`): Cria relatórios detalhados de feedback para cada colaborador, incluindo:
   - Resumo executivo do desempenho
   - Análise ano a ano
   - Gráficos comparativos
   - Pontos fortes e oportunidades de desenvolvimento
   - Recomendações específicas
   - Plano de ação

3. **Geração de Planilha Comparativa** (`generate_comparative_spreadsheet.py`): Cria uma planilha Excel abrangente com:
   - Visão geral de todos os colaboradores e seus conceitos por ano
   - Análise de tendências mostrando a evolução de cada pessoa
   - Análise de gaps e recomendações específicas
   - Detalhes por ano de cada comportamento avaliado
   - Comentários e avaliações individuais
   - Gráficos embutidos e formatação condicional
   - Exportação para PowerPoint (experimental)

## Como Usar

### Requisitos

- Python 3.8+
- Bibliotecas: pandas, numpy, matplotlib, openpyxl, python-pptx (opcional)

Instale as dependências com:

```bash
pip install pandas numpy matplotlib openpyxl python-pptx
```

### Estrutura de Dados

Os dados de avaliação devem estar organizados na seguinte estrutura:

```
test_data/
  ├── [Nome do Colaborador]/
  │    ├── [Ano]/
  │    │    └── resultado.json
  │    ├── [Ano]/
  │    │    └── resultado.json
  │    └── ...
  ├── [Nome do Colaborador]/
  │    └── ...
  └── ...
```

### Gerando Relatórios de Feedback

Para gerar relatórios de feedback para todos os colaboradores:

```bash
python generate_feedback.py test_data --output-dir feedback_reports
```

Para gerar um relatório para um colaborador específico:

```bash
python generate_feedback.py test_data --person "Nome do Colaborador" --output-dir feedback_reports
```

### Gerando Planilha Comparativa

Para gerar uma planilha comparativa com dados de todos os colaboradores:

```bash
python generate_comparative_spreadsheet.py test_data --output avaliacao_comparativa.xlsx
```

Para gerar uma planilha e exportar para PowerPoint (funcionalidade experimental):

```bash
python generate_comparative_spreadsheet.py test_data --output avaliacao_comparativa.xlsx --export-pptx
```

## Conteúdo da Planilha Comparativa

A planilha comparativa gerada contém as seguintes abas:

1. **Visão Geral**: Resumo dos conceitos e pontuações de todos os colaboradores para cada ano.
   - Colunas: Pessoa, Conceito (por ano), Score (por ano), Score Grupo (por ano), Diferença (por ano), Ranking (por ano)
   - Formatação condicional para destacar conceitos e rankings
   - Gráficos de distribuição de conceitos

2. **Tendências**: Análise da evolução de cada colaborador ao longo do tempo.
   - Colunas: Pessoa, Primeiro/Último Ano, Conceitos, Variação no Score, Scores por Ano, Variação por Direcionador
   - Formatação condicional para destacar variações positivas e negativas
   - Gráficos de evolução temporal

3. **Análise de Gaps**: Identificação e análise dos principais gaps de cada colaborador.
   - Colunas: Pessoa, Conceito, Score Médio, Top 3 Gaps, Top 3 Forças
   - Recomendações específicas baseadas nos comportamentos com maior gap
   - Plano de ação sugerido com prazos

4. **Detalhes [Ano]**: Uma aba para cada ano com análise detalhada de cada comportamento.
   - Colunas: Pessoa, Conceito, Score para cada Comportamento, Comparação com Grupo, Avaliações Individuais
   - Formatação condicional para destacar scores acima/abaixo da média
   - Radar charts para top performers

5. **Comentários**: Todos os comentários e avaliações individuais.
   - Colunas: Pessoa, Ano, Direcionador, Comportamento, Avaliador, Conceito, Scores
   - Formatação para facilitar a leitura

## Análise Personalizada

Para análises específicas, você pode utilizar o script `analyze_evaluations.py`:

```bash
# Análise comparativa para um ano específico
python analyze_evaluations.py test_data --year 2024 --output 2024_comparison.png

# Análise histórica de um colaborador específico
python analyze_evaluations.py test_data --person "Nome do Colaborador" --output historico.png --details

# Listar critérios de avaliação por ano
python analyze_evaluations.py test_data --list-criteria
``` 