# People Analytics Pro

Uma plataforma abrangente para análise e gestão de desenvolvimento de pessoas, com foco em avaliações 360°, progresso de carreira e visualizações analíticas.

## Estrutura do Pacote

O pacote foi refatorado para simplificar o uso e melhorar a integração entre componentes:

```
peopleanalytics/
├── cli.py            # ÚNICO ponto de entrada via CLI
├── sync.py           # Motor principal de sincronização e processamento
├── evaluation_analyzer.py  # Análise de avaliações 360°
├── reports_generator.py    # Geração de relatórios e visualizações
├── data_processor.py       # Processamento e validação de dados
├── manager_feedback.py     # Análise de feedback de gestores
├── constants.py            # Constantes e configurações
├── data_model.py           # Modelos de dados
├── domain/                 # Modelos de domínio
│   ├── evaluation.py       # Modelos de avaliação
│   ├── score.py            # Sistema de pontuação
│   └── skill_base.py       # Base de habilidades
└── talent_development/     # Módulos avançados de desenvolvimento
    ├── matrix_9box/        # Matriz 9-Box dinâmica
    ├── career_sim/         # Simulação de carreira
    ├── influence_network/  # Análise de redes de influência
    ├── predictive/         # Modelos preditivos de performance
    ├── feedback_cycle/     # Ciclo integrado de feedback
    └── holistic_viz/       # Visualizações holísticas
```

## Uso do CLI

O CLI (`cli.py`) é o **ÚNICO** ponto de entrada do sistema, com foco no comando `sync` que incorpora todas as funcionalidades necessárias:

```bash
# Uso básico
python -m peopleanalytics sync --data-dir=data --output-dir=output

# Com funcionalidades avançadas de desenvolvimento de talentos
python -m peopleanalytics sync --data-dir=data --output-dir=output --enable-9box --enable-career-sim --enable-network
```

### Opções do comando sync

- `--data-dir=PATH`: Diretório contendo os dados (padrão: "data")
- `--output-dir=PATH`: Diretório para saída dos relatórios (padrão: "output")
- `--enable-9box`: Habilitar geração da matriz 9-box
- `--enable-career-sim`: Habilitar simulação de carreira
- `--enable-network`: Habilitar análise de rede de influência

## Pipeline de Processamento

1. Carregamento e validação de dados
2. Análise de avaliações 360°
3. Geração de relatórios comparativos
4. Análise de tendências e evolução temporal
5. Visualizações avançadas (gráficos, heatmaps, rede)
6. Relatórios HTML interativos
7. Dashboard abrangente de métricas

## Análise de Avaliações 360°

O sistema processa arquivos de avaliação 360° com a seguinte estrutura:

```
data/
├── pessoa1/
│   └── 2023/
│       └── resultado.json
├── pessoa2/
│   └── 2023/
│       └── resultado.json
...
```

Para cada pessoa/ano, são gerados:
- Análise comparativa com o grupo
- Heatmap de direcionadores/comportamentos
- Gráfico de radar de competências
- Relatório de evolução histórica

## Integração com Desenvolvimento de Talentos

Através dos módulos de talent_development, o sistema pode:

1. **Matriz 9-Box Dinâmica**: Posicionamento na matriz de desempenho x potencial
2. **Simulação de Carreira**: Projeção de crescimento baseada em dados históricos
3. **Rede de Influência**: Mapeamento de relações e impacto organizacional
4. **Análise Preditiva**: Modelos de previsão de performance futura
5. **Dashboard Holístico**: Visão consolidada de métricas de desenvolvimento

## Extensão

O sistema foi projetado para ser facilmente estendido. Para adicionar novos módulos:

1. Crie sua classe no diretório apropriado
2. Adicione a importação em `__init__.py`
3. Integre com o CLI no arquivo `cli.py` mantendo-o como único ponto de entrada

## Documentação

A documentação completa está disponível em:
- Docstrings para cada função e classe
- Este README para visão geral
- Arquivos README.md específicos em cada subdiretório 