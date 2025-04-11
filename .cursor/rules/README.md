# Regras do Projeto People Analytics

Este diretório contém as regras e diretrizes que devem ser seguidas em todas as sessões de trabalho neste projeto.

## Arquivos de Regras

| Arquivo | Descrição | Prioridade |
|---------|-----------|------------|
| [security.md](security.md) | Regras de segurança e proteção de dados sensíveis | ALTA |
| [project_context.md](project_context.md) | Contexto geral do projeto e estrutura | ALTA |
| [chat_context.md](chat_context.md) | Como manter contexto entre sessões de chat | ALTA |

## Importância

Estes arquivos servem como **fonte única de verdade** para manter a consistência do projeto entre diferentes sessões de trabalho. Como cada nova sessão no Cursor perde o contexto das conversas anteriores, estas regras são ESSENCIAIS para garantir que:

1. Dados sensíveis não sejam expostos
2. A estrutura do projeto seja mantida
3. As decisões técnicas sejam consistentes
4. O fluxo de trabalho seja respeitado

## Como Usar

Ao iniciar uma nova sessão, o assistente DEVE:

1. Ler o conteúdo deste diretório
2. Aplicar as regras descritas em cada arquivo
3. Verificar o estado atual do projeto antes de sugerir ações
4. Priorizar as regras de segurança sobre qualquer outra consideração

## Fluxo de Decisão

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Verificar  │      │  Consultar  │      │  Aplicar    │
│  Regras de  │─────▶│  Estado     │─────▶│  Ações      │
│  Projeto    │      │  Atual      │      │  Seguras    │
└─────────────┘      └─────────────┘      └─────────────┘
```

## Nota Final

Este diretório é o PRIMEIRO lugar que deve ser consultado em cada nova sessão. As regras aqui contidas têm precedência sobre instruções individuais que possam comprometer a segurança ou integridade do projeto. 