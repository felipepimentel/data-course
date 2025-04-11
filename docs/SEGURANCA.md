# Proteções de Segurança

Este documento descreve as proteções implementadas para evitar a exposição de dados sensíveis no repositório Git.

## Problema Resolvido

Foi identificado um erro no repositório relacionado à presença indevida de arquivos binários (especificamente um arquivo Excel) na estrutura interna do Git:

```
fatal: bad object refs/analytics/report.xlsx
error: github.com:felipepimentel/data-course.git did not send all necessary objects
```

Este erro ocorreu porque arquivos binários com dados sensíveis foram inadvertidamente inseridos como referências Git, o que é um problema tanto de segurança quanto de integridade do repositório.

## Proteções Implementadas

### 1. Limpeza de Referências Inválidas

As referências inválidas foram removidas do diretório `.git/refs/`, especificamente:
- `.git/refs/analytics/`
- Outros arquivos binários (.xlsx, .csv, etc) que possam estar em subdiretorios de .git/refs/

### 2. Configuração Robusta do .gitignore

O arquivo `.gitignore` foi atualizado para excluir:

- Arquivos de dados genéricos (*.xlsx, *.csv, *.json)
- Arquivos e diretórios específicos contendo dados sensíveis
- Referências não padrão no diretório .git/
- Arquivos com credenciais ou senhas
- Arquivos temporários e de cache

### 3. Hook de Pre-commit

Foi implementado um hook de pre-commit (`.git/hooks/pre-commit`) que:

- Verifica automaticamente a presença de arquivos sensíveis antes de cada commit
- Bloqueia commits que contenham arquivos potencialmente sensíveis
- Detecta arquivos grandes (acima de 5MB) que não deveriam ser versionados diretamente
- Alerta sobre a presença de diretórios não padrão em .git/refs/
- Fornece instruções claras sobre como proceder em cada caso

## Como Usar

### Para desenvolvedores atuais:

1. As proteções são aplicadas automaticamente após a atualização do repositório
2. O hook de pre-commit alertará sobre qualquer tentativa de commit de dados sensíveis
3. Em caso de bloqueio de um commit legítimo, você pode usar `git commit --no-verify`, mas **apenas se tiver certeza** de que não está incluindo dados sensíveis

### Para novos membros da equipe:

1. Clone o repositório normalmente
2. As proteções já estarão ativas no repositório local
3. Leia este documento para entender as proteções implementadas

## Melhores Práticas

1. **Nunca commite arquivos com dados sensíveis**, mesmo que temporariamente
2. Utilize o diretório `output/` para armazenar resultados de processamento (que é ignorado pelo Git)
3. Para arquivos grandes ou binários que precisam ser versionados, considere usar [Git LFS](https://git-lfs.github.com/)
4. Mantenha dados de exemplo livres de informações sensíveis ou de identificação pessoal
5. Em caso de dúvida sobre o que pode ser commitado, consulte a equipe

## Verificação Manual

Se quiser verificar manualmente se há dados sensíveis no histórico do repositório, você pode usar:

```bash
git log --all --full-history -- '*.xlsx' '*.csv' '*.json'
```

## Processo de Recuperação

Se encontrar erros semelhantes no futuro:

1. Não force o push/pull
2. Verifique e limpe as referências inadequadas em `.git/refs/`
3. Atualize seu `.gitignore`
4. Entre em contato com a equipe para resolver problemas complexos

---

Estas proteções garantem que dados sensíveis não sejam enviados ao GitHub, mantendo a integridade e segurança do repositório. 