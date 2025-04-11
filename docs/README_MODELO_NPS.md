# Modelo de Pontuação NPS para Avaliações de Pessoas

## Introdução

Este documento descreve o novo modelo de pontuação baseado em NPS (Net Promoter Score) implementado no sistema de avaliações de pessoas. Este modelo foi desenvolvido para proporcionar uma interpretação mais intuitiva e significativa das frequências de avaliação, permitindo identificar claramente desempenhos excelentes e problemas que precisam de atenção.

## Motivação

O modelo anterior de pontuação utilizava pesos [0, 2.5, 4, 3, 2, 1] para os 6 níveis de frequência:
- `n/a` - Não avaliado
- `referencia` - Referência
- `sempre` - Sempre/Acima do esperado
- `quase sempre` - Quase sempre/Dentro do esperado
- `poucas vezes` - Poucas vezes/Abaixo do esperado
- `raramente` - Raramente/Muito abaixo do esperado

No entanto, este modelo apresentava limitações:
- Não penalizava adequadamente desempenhos ruins
- Não destacava suficientemente os desempenhos excelentes
- Valores intermediários tinham pesos que não refletiam claramente a valência positiva ou negativa
- A escala resultante (entre 1 e 4) era pouco intuitiva para interpretação qualitativa

## Novo Modelo de Pontuação NPS

Inspirado pela metodologia do Net Promoter Score, desenvolvemos um modelo que:
- Utiliza uma escala com valores positivos e negativos para uma identificação clara de pontos fortes e fracos
- Amplifica os extremos para destacar desempenhos notáveis (tanto positivos quanto negativos)
- Fornece uma interpretação qualitativa padronizada dos scores
- Permite normalização para uma escala 0-100 para compatibilidade com outras métricas

### Pesos do Modelo NPS

Os novos pesos atribuídos são:
```
[0, 2, 10, 5, -5, -10]
```

Onde:
- `n/a` (0): Neutro, não contabilizado
- `referencia` (2): Levemente positivo
- `sempre` (10): Fortemente positivo
- `quase sempre` (5): Moderadamente positivo
- `poucas vezes` (-5): Moderadamente negativo
- `raramente` (-10): Fortemente negativo

### Escala de Interpretação

Os scores resultantes são mapeados para categorias qualitativas:

| Categoria      | Range (escala -10 a 10) | Range (escala 0-100) |
|----------------|-------------------------|----------------------|
| Excelente      | 7.5 a 10.0              | 87.5 a 100.0         |
| Bom            | 2.5 a 7.5               | 62.5 a 87.5          |
| Regular        | -2.5 a 2.5              | 37.5 a 62.5          |
| Abaixo         | -7.5 a -2.5             | 12.5 a 37.5          |
| Insatisfatório | -10.0 a -7.5            | 0.0 a 12.5           |

## Implementação

### Função de Pontuação Centralizada

Todo o cálculo de scores foi centralizado na função `calculate_score()` no módulo `constants.py`, garantindo consistência em todo o sistema.

```python
def calculate_score(frequencies: List[int], use_nps_model: bool = True, normalize: bool = False) -> float:
    """Calculate score from frequency distribution vectors using specified scoring model.
    
    Args:
        frequencies: Lista de inteiros representando a distribuição de frequência
            onde as posições significam: [n/a, referencia, sempre, quase sempre, poucas vezes, raramente]
        use_nps_model: Se deve usar o modelo NPS melhorado (True) ou os pesos tradicionais (False)
        normalize: Se deve normalizar o score para uma escala 0-100 (apenas para o modelo NPS)
            
    Returns:
        Um score baseado no modelo selecionado
    """
```

Esta função:
- Valida os vetores de entrada (devem ter exatamente 6 posições)
- Permite utilizar o modelo tradicional ou o novo modelo NPS
- Permite normalizar o resultado para uma escala 0-100
- Separa pesos positivos e negativos para um cálculo mais intuitivo

### Função de Categorização

A função `get_score_category()` permite obter uma categoria qualitativa a partir de um score numérico:

```python
def get_score_category(score: float, normalized: bool = False) -> str:
    """Retorna a categoria qualitativa correspondente a um score numérico.
    
    Args:
        score: O score numérico
        normalized: Se True, usa ranges para scores normalizados (0-100)
        
    Returns:
        Uma string representando a categoria do score
    """
```

## Ferramentas Complementares

### Script de Testes

O script `test_nps_score.py` permite verificar o comportamento do modelo em diferentes cenários e garantir a consistência da implementação entre os diferentes analisadores.

Para executar:
```
python test_nps_score.py
```

### Gerador de Relatórios

O script `generate_nps_score_report.py` permite gerar relatórios detalhados a partir dos dados de avaliação, incluindo:
- Arquivo CSV com todos os scores calculados
- Gráfico de distribuição por categorias
- Gráfico de comparação entre scores individuais e do grupo
- Estatísticas descritivas

Para executar:
```
python generate_nps_score_report.py <arquivo_json> [diretorio_saida]
```

## Exemplos de Resultados

### Vetores de Exemplo e Scores Resultantes

| Descrição                           | Score NPS | Categoria      | Score (0-100) | Categoria Norm. |
|-------------------------------------|-----------|----------------|---------------|-----------------|
| Vetor padrão (mais positivos)       | 6.75      | Bom            | 83.75         | Bom             |
| Muitos 'sempre'                     | 10.00     | Excelente      | 100.00        | Excelente       |
| Quase sempre dominante              | 5.00      | Bom            | 75.00         | Bom             |
| Distribuição uniforme               | 0.40      | Regular        | 52.00         | Regular         |
| Poucos vezes dominante              | -5.00     | Abaixo         | 25.00         | Abaixo          |
| Raramente dominante                 | -10.00    | Insatisfatório | 0.00          | Insatisfatório  |

## Integração com o Sistema Existente

O novo modelo foi integrado mantendo compatibilidade com o sistema existente:

1. As classes `EvaluationAnalyzer` em ambos os módulos `analyzer.py` e `evaluation_analyzer.py` foram modificadas para usar a função centralizada

2. Uma opção `use_nps_model` (padrão: False) foi adicionada para permitir a transição gradual

3. A documentação foi atualizada para refletir as novas funcionalidades

## Uso em Produção

Para utilizar o novo modelo de pontuação em produção:

1. Em código existente que usa `calculate_weighted_score()`, adicione o parâmetro `use_nps_model=True`:
   ```python
   score = analyzer.calculate_weighted_score(frequencies, use_nps_model=True)
   ```

2. Para obter a categoria qualitativa do score:
   ```python
   from peopleanalytics.constants import get_score_category
   categoria = get_score_category(score)
   ```

3. Para usar a escala normalizada (0-100):
   ```python
   score_normalizado = analyzer.calculate_weighted_score(frequencies, use_nps_model=True, normalize=True)
   categoria = get_score_category(score_normalizado, normalized=True)
   ```

## Considerações Futuras

Possíveis evoluções do modelo:
- Ajustes finos nos pesos com base em mais dados de produção
- Desenvolvimento de visualizações específicas para o modelo NPS
- Integração com sistemas de alerta para scores abaixo de limiares específicos
- Análise de tendências temporais dos scores NPS 