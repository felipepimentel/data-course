# People Analytics Pro

Uma plataforma abrangente para análise e gestão de desenvolvimento de pessoas, focada em dados estruturados para tomada de decisão baseada em evidências. Avaliações, feedback, progressão de carreira e análise de equipes em um único sistema.

![Licença](https://img.shields.io/badge/licença-Apache%202.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7%2B-brightgreen.svg)

## 🌟 Recursos Principais

- **Progressão de Carreira**: Rastreamento completo da trajetória profissional de cada colaborador
- **Análise 360°**: Coleta e processamento de feedback multidirecional
- **Avaliações do Gestor**: Templates especializados por nível de senioridade
- **Modelo de Pontuação NPS**: Sistema avançado para classificação de desempenho
- **Análise de Equipes**: Otimização de composição e desenvolvimento de times
- **PDI Automatizado**: Planos de desenvolvimento personalizados baseados em dados
- **Fluxo de Trabalho Manual**: Suporte para preenchimento manual de templates
- **Visualizações Avançadas**: Dashboards, gráficos e linhas do tempo interativas

## 🔧 Instalação

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/people-analytics.git
cd people-analytics

# Criar ambiente virtual (opcional, mas recomendado)
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Instalar o pacote em modo desenvolvimento
pip install -e .
```

## 🚀 Início Rápido

### Fluxo de Trabalho Manual

```bash
# Gerar template para preenchimento manual
python -m peopleanalytics generate-template --format json --output data/templates/colaborador.json

# Preencher o template com dados e colocá-lo em data/templates/

# Sincronizar para processar os dados
python -m peopleanalytics sync --data-path data --output-path output

# Verificar relatórios gerados na pasta output/
```

### Comandos de Carreira

```bash
# Adicionar evento de carreira
python -m peopleanalytics career add-event joao --date 2023-05-15 --type promotion --details "Promoção por mérito" --previous-position "Desenvolvedor Jr" --new-position "Desenvolvedor Pleno" --impact 4

# Adicionar habilidade
python -m peopleanalytics career add-skill maria --name "technical.python" --level 4

# Gerar análise de desenvolvimento de equipe
python -m peopleanalytics team-development --data-path data --output-path output
```

## 📊 Modelo de Pontuação NPS

O sistema agora utiliza um modelo de pontuação inspirado no Net Promoter Score para avaliações:

- **Escala com valência**: Valores positivos e negativos (-10 a +10)
- **Amplificação de extremos**: Destaca desempenhos notáveis (+10) e problemas críticos (-10)
- **Categorização qualitativa**: Excelente, Bom, Regular, Abaixo, Insatisfatório
- **Normalização opcional**: Conversão para escala 0-100

Pesos do modelo NPS:
```
[0, 2, 10, 5, -5, -10]
```

Onde:
- `n/a` (0): Neutro
- `referencia` (2): Levemente positivo
- `sempre` (10): Fortemente positivo
- `quase sempre` (5): Moderadamente positivo
- `poucas vezes` (-5): Moderadamente negativo
- `raramente` (-10): Fortemente negativo

Detalhes completos disponíveis em `docs/README_MODELO_NPS.md`.

## 📁 Estrutura do Projeto

```
people-analytics/
├── data/                   # Dados de entrada
│   ├── career_progression/ # Dados de progressão de carreira
│   ├── templates/          # Templates para preenchimento manual
│   ├── team_development/   # Dados de desenvolvimento de equipes
│   └── manager_feedback/   # Feedback de gestores
├── docs/                   # Documentação
│   ├── QUICK_REFERENCE.md  # Guia rápido de referência
│   ├── workflow_guide.md   # Guia detalhado de fluxo de trabalho
│   └── README_MODELO_NPS.md # Detalhes do modelo de pontuação NPS
├── output/                 # Relatórios e visualizações geradas
│   ├── reports/            # Relatórios de avaliação
│   ├── people_analytics.duckdb # Banco de dados DuckDB
│   ├── radar_charts/       # Gráficos de radar de habilidades
│   ├── mermaid/            # Diagramas em formato Mermaid
│   └── action_plans/       # Planos de ação gerados
├── peopleanalytics/        # Código-fonte do pacote
├── scripts/                # Scripts utilitários
├── tests/                  # Testes automatizados
├── notebooks/              # Jupyter notebooks para análises
├── tools/                  # Ferramentas auxiliares
├── assets/                 # Recursos estáticos
├── requirements.txt        # Dependências Python
├── setup.py                # Configuração do pacote
├── README.md               # Este arquivo
└── LICENSE                 # Licença Apache 2.0
```

## 📄 Estrutura de Dados de Carreira

Os dados de progressão de carreira seguem esta estrutura JSON:

```json
{
  "nome": "Nome do Colaborador",
  "eventos_carreira": [
    {
      "data": "2023-05-15",
      "tipo_evento": "promotion",
      "detalhes": "Promoção por mérito",
      "cargo_anterior": "Desenvolvedor Jr",
      "cargo_novo": "Desenvolvedor Pleno",
      "impacto": 4
    }
  ],
  "matriz_habilidades": {
    "technical.python": 4,
    "technical.javascript": 3,
    "soft.comunicacao": 5
  },
  "metas_carreira": [
    {
      "title": "Liderar projeto estratégico",
      "target_date": "2024-06-30",
      "details": "Coordenar equipe de 5 pessoas em projeto de alta visibilidade",
      "progress": 20,
      "status": "in_progress"
    }
  ],
  "certificacoes": [
    {
      "name": "AWS Solutions Architect",
      "issuer": "Amazon Web Services",
      "date_obtained": "2023-07-20"
    }
  ],
  "mentoria": [
    {
      "mentor_name": "João Silva",
      "start_date": "2023-01-15",
      "focus_areas": ["Liderança Técnica", "Arquitetura de Software"],
      "active": true
    }
  ],
  "high_performer_index": {
    "technical_excellence": 4.2,
    "learning_velocity": 3.8,
    "leadership": 3.5,
    "execution": 4.0,
    "overall": 3.9
  }
}
```

## 📊 Visualizações Geradas

- **Linha do tempo de carreira**: Representação visual da trajetória profissional
- **Radar de habilidades**: Visualização por categorias técnicas e comportamentais
- **Métricas de crescimento**: Gráficos de gauge mostrando evolução
- **Heatmaps de time**: Identificação de pontos fortes e gaps na equipe
- **Gráficos de benchmark**: Comparação entre membros e equipes
- **Dashboards interativos**: Visões consolidadas em HTML e JSON

## 🔍 Métricas Calculadas

- **High Performer Index**: Combinação ponderada de excelência técnica, velocidade de aprendizado, liderança e execução
- **Learning Velocity**: Taxa de aquisição de novas habilidades ao longo do tempo
- **Promotion Velocity**: Tempo médio entre promoções
- **Skill Growth Rate**: Taxa de melhoria em habilidades específicas
- **Team Compatibility Score**: Medida de complementaridade de habilidades em uma equipe

## 🛠️ Comandos Disponíveis

### Fluxo de Trabalho Manual

```
generate-template   Gerar template para preenchimento manual
update-career       Extrair dados existentes para atualização
sync                Sincronizar e processar todos os dados
docs                Gerar documentação específica
```

### Análise de Pessoas e Equipes

```
career              Gerenciar dados de progressão de carreira
team-development    Gerar análise de desenvolvimento de equipe
validate            Validar integridade dos dados
list                Listar dados disponíveis no sistema
```

Um guia completo com exemplos está disponível em `docs/QUICK_REFERENCE.md`.

## ⚙️ Configuração Avançada

O sistema pode ser configurado através de arquivo `.env` ou variáveis de ambiente:

```
PA_DATA_PATH=./data            # Caminho para diretório de dados
PA_OUTPUT_PATH=./output        # Caminho para saída de relatórios
PA_USE_NPS_MODEL=true          # Usar modelo NPS para pontuação
PA_DEFAULT_TEMPLATE=json       # Formato padrão para templates
PA_LOG_LEVEL=INFO              # Nível de log (DEBUG, INFO, WARNING, ERROR)
```

## 📄 Licença

Este projeto está licenciado sob os termos da Licença Apache 2.0. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, consulte o arquivo CONTRIBUTING.md para guidelines sobre como contribuir.

---

Documentação completa disponível em `docs/`. Para dúvidas ou suporte, abra uma issue no repositório.