# Regras de Segurança e Proteção de Dados

## Contexto

Este projeto contém dados sensíveis que NÃO devem ser expostos no GitHub. O repositório foi previamente afetado por um erro de referência Git (`refs/analytics/report.xlsx`) que expôs dados indevidamente. Proteções foram implementadas e DEVEM ser mantidas.

## Regras Estritamente Obrigatórias

1. **NUNCA commitar arquivos sensíveis**:
   - Dados pessoais ou identificáveis
   - Arquivos de senha ou credenciais
   - Planilhas, CSVs ou JSONs com dados reais
   - Arquivos binários (xlsx, docx, pdf, etc.)
   - Arquivos grandes (>5MB)

2. **Respeitar a estrutura de diretórios**:
   - `/data/` - Para armazenamento de dados (ignorado pelo Git)
   - `/output/` - Para resultados de processamento (ignorado pelo Git)
   - `/docs/` - Para documentação
   - Banco de dados DuckDB deve estar SEMPRE em `/output/`, NUNCA na raiz

3. **Manter proteções Git**:
   - Pre-commit hook (`.git/hooks/pre-commit`)
   - Regras .gitignore atualizadas
   - Nunca usar `--force` em operações Git sem análise prévia

4. **Sanitizar exemplos**:
   - Todo dado de exemplo deve ser fictício
   - Templates não devem conter informações reais
   - Nunca usar nomes, identificadores ou dados reais

## Arquivos Ignorados

O sistema foi configurado para ignorar automaticamente:
- Arquivos .xlsx, .csv, .json
- Conteúdo dos diretórios /data/ e /output/
- Referências Git não-padrão
- Arquivos com nomes suspeitos (credential, secret, etc.)

## Processo de Desenvolvimento

1. **Desenvolvimento local**:
   - Trabalhar com dados em `/data/` e `/output/`
   - Usar templates para entrada manual de dados
   - Executar sincronização apenas localmente

2. **Versionamento seguro**:
   - Versionar apenas código e estrutura
   - Usar Git apenas para arquivos não-sensíveis
   - Manter dados reais fora do repositório

3. **Recuperação de erro**:
   - Se ocorrer "bad object", verificar `.git/refs/`
   - Não forçar push/pull em caso de erro
   - Consultar `docs/SEGURANCA.md` para procedimentos detalhados

## Notas Adicionais

1. O arquivo `.git/hooks/pre-commit` verifica automaticamente arquivos sensíveis
2. As configurações de .gitignore foram atualizadas para proteção adicional
3. Dados reais devem ser processados apenas localmente
4. Qualquer adição de novos tipos de dados deve considerar estas restrições

---

Estas regras DEVEM ser seguidas em TODAS as conversações, independentemente do contexto. A proteção de dados sensíveis é PRIORITÁRIA em todas as ações neste projeto. 