# People Analytics

Uma plataforma abrangente para análise e gestão de desenvolvimento de pessoas, focada em dados estruturados para tomada de decisão baseada em evidências.

![Python](https://img.shields.io/badge/python-3.7%2B-brightgreen.svg)
![Licença](https://img.shields.io/badge/licença-Apache%202.0-blue.svg)

## 🚀 Início Rápido

### Usando o Makefile

```bash
# Instalar o UV (opcional, recomendado para instalação mais rápida)
make install-uv

# Instalar dependências
make install

# Gerar dados de exemplo
make sample

# Iniciar o dashboard
make dashboard

# Executar sincronização de dados
make sync

# Ou executar todos os passos em sequência
make all
```

### Instalação Manual

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt  
pip install -e .

# Gerar dados de exemplo
python -m scripts.dashboard.populate_sample_data

# Iniciar o dashboard
python -m scripts.run_dashboard
```

## 📊 Funcionalidades Principais

- **Progressão de Carreira**: Rastreamento completo da trajetória profissional
- **Análise 360°**: Coleta e processamento de feedback multidirecional
- **Avaliações do Gestor**: Templates por nível de senioridade
- **Modelo de Pontuação NPS**: Sistema avançado para classificação de desempenho
- **Análise de Equipes**: Otimização de composição e desenvolvimento de times
- **PDI Automatizado**: Planos de desenvolvimento personalizados baseados em dados
- **Dashboard Interativo**: Interface web para gestão de equipes
- **Visualizações Avançadas**: Dashboards, gráficos e linhas do tempo interativas

## ⚙️ Uso do CLI

### Comando Sync

O comando `sync` é a principal ferramenta para processamento de dados, gerando relatórios, visualizações e análises.

```bash
# Formato básico
python sync_app.py --data-dir DATA_DIR --output-dir OUTPUT_DIR [opções]

# Exemplo com diretórios padrão
python sync_app.py
```

#### Opções disponíveis:

| Opção | Descrição |
|-------|-----------|
| `--data-dir DIR` | Diretório de dados de entrada (padrão: `data`) |
| `--output-dir DIR` | Diretório para resultados (padrão: `output`) |
| `--pessoa NOME` | Filtrar por pessoa específica |
| `--ano ANO` | Filtrar por ano específico |
| `--formats FORMATOS` | Formatos a processar (lista separada por vírgulas) |
| `--force` | Forçar reprocessamento de arquivos |
| `--ignore-errors` | Ignorar erros e continuar processamento |

#### Desativar funcionalidades:

| Opção | Descrição |
|-------|-----------|
| `--no-viz` | Pular geração de visualizações |
| `--no-zip` | Não comprimir diretório após processamento |
| `--no-dashboard` | Pular geração de dashboard |
| `--no-excel` | Pular exportação para Excel |
| `--no-markdown` | Pular geração de relatórios markdown |

#### Opções de desempenho:

| Opção | Descrição |
|-------|-----------|
| `--no-parallel` | Usar processamento sequencial em vez de paralelo |
| `--workers N` | Número de workers para processamento paralelo (0 = auto) |
| `--batch-size N` | Tamanho do lote para processamento paralelo (0 = todos) |
| `--quiet` | Mostrar informações mínimas durante processamento |
| `--verbose` | Mostrar informações detalhadas durante processamento |

### Exemplos de Uso

```bash
# Filtrar por pessoa e ano
python sync_app.py --data-dir data --output-dir output --pessoa "João Silva" --ano 2023

# Desabilitar recursos específicos
python sync_app.py --no-viz --no-excel --no-markdown

# Processamento sequencial com tratamento de erros
python sync_app.py --no-parallel --ignore-errors --force
```

## 📁 Estrutura do Projeto

```
people-analytics/
├── data/                   # Dados de entrada
│   ├── career_progression/ # Dados de progressão de carreira
│   ├── templates/          # Templates para preenchimento manual
│   ├── team_development/   # Dados de desenvolvimento de equipes
│   └── manager_feedback/   # Feedback de gestores
├── docs/                   # Documentação
├── output/                 # Relatórios e visualizações geradas
├── peopleanalytics/        # Código-fonte do pacote
│   ├── cli_commands/       # Comandos CLI
│   ├── domain/             # Modelos de domínio
│   └── utils/              # Utilitários
├── scripts/                # Scripts utilitários
├── tests/                  # Testes automatizados
├── notebooks/              # Jupyter notebooks para análises
├── requirements.txt        # Dependências Python
├── setup.py                # Configuração do pacote
├── Makefile                # Automações do projeto
└── sync_app.py             # Script standalone para sincronização
```

## 📄 Estrutura de Dados

Os dados de progressão de carreira seguem estrutura JSON:

```json
{
  "nome": "Nome do Colaborador",
  "eventos_carreira": [
    {
      "data": "2023-01-15",
      "tipo": "promoção",
      "cargo": "Senior Engineer",
      "detalhes": "Promovido após conclusão do projeto X"
    }
  ],
  "competencias": {
    "Python": 4.5,
    "Liderança": 3.8
  }
}
```

## 💡 Modelo de Pontuação NPS

O sistema utiliza um modelo de pontuação inspirado no Net Promoter Score:

- **Escala com valência**: Valores positivos e negativos (-10 a +10)
- **Amplificação de extremos**: Destaca desempenhos notáveis (+10) e problemas críticos (-10)
- **Categorização qualitativa**: Excelente, Bom, Regular, Abaixo, Insatisfatório
- **Normalização opcional**: Conversão para escala 0-100

## 📜 Licença

Este projeto está licenciado sob os termos da licença Apache 2.0 - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, consulte o arquivo [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes sobre o processo de envio de pull requests.