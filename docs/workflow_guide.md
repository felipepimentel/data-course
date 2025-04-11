# Fluxo de Trabalho Manual

## Visão Geral

O Sistema de People Analytics suporta um fluxo de trabalho manual para atualização e processamento de dados de progressão de carreira. Este fluxo permite que você:

1. Gere templates estruturados para preenchimento manual
2. Preencha os dados em seu editor preferido
3. Sincronize os dados para processamento e geração de relatórios

## Passo a Passo

### 1. Gerar Template

```bash
python -m peopleanalytics generate-template --format json --output data/templates/colaborador.json
```

Este comando gera um template estruturado que pode ser preenchido manualmente. Opções para o formato incluem:
- `json`: Formato estruturado fácil de processar por sistemas (recomendado)
- `md`: Formato markdown para preenchimento em editores de texto simples
- `yaml`: Formato YAML para maior legibilidade

### 2. Preencher o Template

Abra o template gerado no seu editor preferido e preencha os dados de progressão de carreira. Certifique-se de:

- Seguir o formato especificado (datas no formato AAAA-MM-DD)
- Incluir todos os campos obrigatórios
- Salvar o arquivo na pasta `data/templates`

### 3. Sincronizar e Processar

```bash
python -m peopleanalytics sync --data-path data --output-path output
```

Este comando:
- Detecta automaticamente os templates preenchidos na pasta `data/templates`
- Processa os dados e calcula métricas relevantes
- Gera relatórios de progressão de carreira
- Move os templates processados para um arquivo

### 4. Atualizar Dados Existentes

Para atualizar dados existentes:

```bash
python -m peopleanalytics update-career --person "Nome do Colaborador" --format json
```

Este comando:
- Extrai os dados existentes do colaborador
- Gera um novo template preenchido com os dados atuais
- Permite que você faça as alterações necessárias
- Após edição, coloque o arquivo na pasta `data/templates` e execute o comando sync

## Dicas

- Mantenha templates consistentes para todos os colaboradores
- Atualize as informações regularmente (pelo menos a cada 3-6 meses)
- Considere usar editores JSON para garantir a estrutura correta dos dados
- Verifique os relatórios gerados na pasta `output` após sincronização

