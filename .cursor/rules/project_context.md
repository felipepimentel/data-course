# Contexto do Projeto

## Descrição Geral

Este projeto é uma plataforma de People Analytics que processa dados de funcionários, feedback, avaliações e progressão de carreira. O sistema é projetado para importar dados estruturados, processá-los e gerar relatórios e visualizações.

## Estrutura do Projeto

```
people-analytics/
├── data/                   # Dados de entrada (IGNORADO pelo Git)
│   ├── career_progression/ # Dados de progressão de carreira
│   ├── templates/          # Templates para preenchimento manual
│   ├── team_development/   # Dados de desenvolvimento de equipes
│   └── manager_feedback/   # Feedback de gestores
├── docs/                   # Documentação
│   ├── QUICK_REFERENCE.md  # Guia rápido de referência
│   ├── workflow_guide.md   # Guia de fluxo de trabalho
│   ├── SEGURANCA.md        # Documentação de segurança
│   └── README_MODELO_NPS.md # Detalhes do modelo NPS
├── output/                 # Saída gerada (IGNORADO pelo Git)
│   ├── reports/            # Relatórios gerados
│   ├── people_analytics.duckdb # Banco de dados
│   └── visualizations/     # Gráficos e visualizações
├── peopleanalytics/        # Código-fonte principal
├── scripts/                # Scripts utilitários
├── tests/                  # Testes automatizados
└── README.md               # Documentação principal
```

## Fluxo de Trabalho

1. Gerar templates para entrada de dados
2. Preencher templates manualmente
3. Sincronizar dados para processamento
4. Gerar relatórios e visualizações

## Funcionalidades Principais

- Progressão de carreira e análise de habilidades
- Feedback 360° e avaliações
- Análise de desenvolvimento de equipes
- Modelo de pontuação NPS para classificação de desempenho
- Visualizações e relatórios personalizados

## Decisões Técnicas Importantes

1. **Proteção de dados sensíveis**: Regras estritas para evitar exposição (ver `security.md`)
2. **Estrutura de diretórios**: Separação clara entre código e dados
3. **Modelo NPS**: Sistema de pontuação avançado implementado para melhor avaliação
4. **Base de dados**: DuckDB para armazenamento local e processamento rápido
5. **Organização**: Fluxo de trabalho manual para processamento de dados estruturados

## Pendências e Prioridades

1. Manter proteções de segurança atualizadas
2. Organizar diretórios de acordo com a estrutura padronizada
3. Garantir que dados sensíveis permaneçam locais
4. Seguir o fluxo de trabalho documentado para atualizações

## Referências Importantes

- Documentação completa: `docs/`
- Regras de segurança: `.cursor/rules/security.md`
- Guia rápido: `docs/QUICK_REFERENCE.md`
- Fluxo de trabalho: `docs/workflow_guide.md` 