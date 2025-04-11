# Regras para Manutenção de Contexto entre Sessões

## Princípio Fundamental

Cada nova sessão de chat no Cursor perde o contexto completo das conversas anteriores. Para manter a consistência do projeto, estas regras DEVEM ser seguidas em cada nova interação.

## Procedimento para Início de Sessão

1. **Verificar arquivos de contexto**:
   - Sempre consultar `.cursor/rules/` no início de cada nova sessão
   - Priorizar `security.md` e `project_context.md` para entender o escopo e restrições

2. **Explorar a estrutura atual**:
   - Executar `ls -la` para verificar a estrutura atual do projeto
   - Confirmar que a estrutura de diretórios está conforme esperado
   - Verificar que arquivos sensíveis estão nos diretórios corretos

3. **Validar estado do Git**:
   - Executar `git status` para verificar se há referências problemáticas
   - Confirmar que o pre-commit hook está ativo (`.git/hooks/pre-commit`)

## Regras para Manutenção de Contexto

1. **Não inferir contexto anterior sem verificação**:
   - Sempre verificar diretamente o estado atual dos arquivos relevantes
   - Não presumir que o estado anterior foi mantido
   - Buscar confirmação antes de realizar ações destrutivas

2. **Consultar documentação existente**:
   - Verificar `README.md` para visão geral
   - Consultar `docs/SEGURANCA.md` para questões de segurança
   - Ler `docs/workflow_guide.md` para entender o fluxo de trabalho

3. **Priorizar segurança**:
   - NUNCA sugerir ações que possam expor dados sensíveis
   - Seguir à risca as regras em `.cursor/rules/security.md`
   - Em caso de dúvida, optar pela abordagem mais conservadora

## Como Responder a Comandos Comuns

1. **Quando solicitado para organizar arquivos**:
   - Verificar regras de estrutura do projeto
   - Mover arquivos sensíveis para `/data/` ou `/output/`
   - Nunca sugerir versionamento de dados reais

2. **Quando solicitado para resolver problemas Git**:
   - Verificar referências Git problemáticas
   - Aplicar proteções conforme docs/SEGURANCA.md
   - Nunca forçar operações que possam causar exposição de dados

3. **Quando solicitado novos recursos**:
   - Garantir que implementações sigam o fluxo de trabalho estabelecido
   - Manter separação clara entre código (versionado) e dados (local)
   - Documentar adequadamente novas funcionalidades

## Notas Especiais

- As regras de segurança têm prioridade sobre qualquer outra consideração
- Os diretórios `/data/` e `/output/` NÃO são versionados e devem conter todos os dados
- O fluxo de trabalho manual deve ser preservado para manter a simplicidade
- Qualquer modificação na estrutura de diretórios deve seguir o padrão existente

---

Estas regras DEVEM ser consultadas ao início de cada nova sessão para garantir continuidade e coerência no desenvolvimento do projeto. 