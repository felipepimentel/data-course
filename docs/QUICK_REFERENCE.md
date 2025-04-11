# Guia Rápido: Fluxo de Trabalho Manual para People Analytics

## Comandos Disponíveis

### Geração de Templates

```bash
# Gerar template de carreira (formato JSON)
python -m peopleanalytics generate-template --format json --output colaborador.json

# Gerar template em formato markdown para edição em texto
python -m peopleanalytics generate-template --format md --output colaborador.md

# Gerar template com nome específico no diretório de templates
python -m peopleanalytics generate-template --format json --output data/templates/colaborador_novo.json
```

### Atualização de Dados Existentes

```bash
# Extrair dados existentes para atualização
python -m peopleanalytics update-career --person "Nome do Colaborador" --format json

# Extrair em formato markdown
python -m peopleanalytics update-career --person "Nome do Colaborador" --format md

# Especificar caminho de saída
python -m peopleanalytics update-career --person "Nome do Colaborador" --format json --output atualizar_colaborador.json
```

### Sincronização e Processamento

```bash
# Sincronizar todos os templates no diretório data/templates
python -m peopleanalytics sync --data-path data --output-path output
```

### Documentação

```bash
# Gerar documentação completa
python -m peopleanalytics docs --topic all --output documentacao_completa.md

# Gerar guia do fluxo de trabalho
python -m peopleanalytics docs --topic workflow --output guia_workflow.md

# Gerar documentação sobre progressão de carreira
python -m peopleanalytics docs --topic career --output docs_carreira.md

# Gerar documentação sobre templates
python -m peopleanalytics docs --topic templates --output docs_templates.md
```

### Análise de Equipe

```bash
# Gerar análise de desenvolvimento de equipe
python -m peopleanalytics team-development --data-path data --output-path output
```

## Fluxo de Trabalho Típico

1. Gerar template para colaborador:
   ```bash
   python -m peopleanalytics generate-template --format json --output data/templates/colaborador.json
   ```

2. Preencher o template com dados de progressão de carreira

3. Sincronizar para processar os dados:
   ```bash
   python -m peopleanalytics sync --data-path data --output-path output
   ```

4. Verificar relatórios gerados na pasta output

5. Para atualizar posteriormente:
   ```bash
   python -m peopleanalytics update-career --person "Nome do Colaborador" --format json
   ```

6. Editar o arquivo gerado e colocá-lo novamente em `data/templates`

7. Sincronizar novamente para processar as atualizações

## Dicas

- Os arquivos JSON devem ser válidos para processamento correto
- Mantenha as datas no formato AAAA-MM-DD
- Avalie habilidades e impacto em escala de 1-5
- Utilize os tipos de eventos padronizados
- Confira a documentação completa com `python -m peopleanalytics docs --topic all` 