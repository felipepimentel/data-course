#!/usr/bin/env python3
"""
Módulo de constantes para o sistema de avaliação 360 graus.
Este arquivo centraliza todas as constantes usadas em diferentes partes do sistema.
"""

# Tipos de frequência de observação e seus pesos
FREQUENCY_LABELS = [
    "n/a",
    "observo nunca",
    "observo raramente",
    "observo na maior parte das vezes",
    "observo sempre",
    "referencia",
]

FREQUENCY_WEIGHTS = [0, 1, 2, 3, 4, 5]

# Conceitos de avaliação individual
CONCEITOS = [
    "pratico raramente",
    "pratico às vezes",
    "pratico na maior parte das vezes",
    "pratico sempre",
]

# Conceitos de avaliação de desempenho (em relação ao grupo)
PERFORMANCE_CONCEPTS = [
    "abaixo do grupo",
    "alinhado em relação ao grupo",
    "acima do grupo",
]

# Cores para os diferentes conceitos
CONCEPT_COLORS = {
    "acima do grupo": "#92D050",  # Verde
    "alinhado em relação ao grupo": "#FFC000",  # Amarelo
    "conforme esperado": "#FFC000",  # Amarelo (alias)
    "abaixo do grupo": "#FF0000",  # Vermelho
    "n/a": "#CCCCCC",  # Cinza
}

# Comentários de gestores para uso em dados de teste
COMENTARIOS_GESTOR = [
    "Apresentou grande evolução neste ano, mas ainda precisa desenvolver habilidades de comunicação.",
    "Superou expectativas em entregas técnicas, porém pode melhorar em trabalho em equipe.",
    "Excelente em atendimento ao cliente e solução de problemas.",
    "Tem se destacado em liderança e inovação, continue assim.",
    "Bom trabalho com entregas consistentes, mas pode ser mais proativo.",
    "Grande potencial para crescer, foque em se comunicar melhor.",
    "Excelente desempenho técnico e comportamental neste ciclo.",
    "Alcançou todos os objetivos estabelecidos para o ano.",
]

# Comentários de pares para uso em dados de teste
COMENTARIOS_PARES = [
    "Sempre solícito quando precisamos de ajuda, ótimo colega.",
    "Profissional dedicado que busca sempre melhorar.",
    "Tem dificuldade em compartilhar conhecimento com a equipe.",
    "Contribui com ideias inovadoras e ajuda a todos.",
    "Muito técnico, mas às vezes falta empatia com a equipe.",
    "Excelente em conduzir projetos e envolver todos.",
    "Tem conhecimento técnico, mas pode melhorar a colaboração.",
    "Sempre disponível para auxiliar e compartilhar conhecimento.",
]

# Estrutura dos direcionadores e comportamentos por ano
DIRECIONADORES_BY_YEAR = {
    "2021": [
        {
            "name": "1. Inovação e Transformação",
            "comportamentos": [
                "você estimula a inovação no ambiente de trabalho",
                "você implementa soluções criativas para problemas complexos",
                "você adapta-se rapidamente às mudanças",
            ],
        },
        {
            "name": "2. Colaboração e Trabalho em Equipe",
            "comportamentos": [
                "você trabalha efetivamente em equipe",
                "você compartilha conhecimento com os colegas",
                "você contribui para um ambiente positivo",
            ],
        },
    ],
    "2022": [
        {
            "name": "1. A gente trabalha para o cliente",
            "comportamentos": [
                "você tem obstinação por encantar o cliente",
                "você adota soluções simples para nossos clientes",
                "você promove experiências diferenciadas",
            ],
        },
        {
            "name": "2. Performance que transforma",
            "comportamentos": [
                "você busca resultados sustentáveis",
                "você é eficiente e ágil nas entregas",
                "você tem foco na melhoria contínua",
            ],
        },
    ],
    "2023": [
        {
            "name": "1. A gente trabalha para o cliente",
            "comportamentos": [
                "você tem obstinação por encantar o cliente",
                "você promove experiências diferenciadas",
                "você se coloca no lugar do cliente",
            ],
        },
        {
            "name": "2. Performance que transforma",
            "comportamentos": [
                "você busca resultados sustentáveis",
                "você tem mentalidade de dono",
                "você é eficiente e ágil nas entregas",
            ],
        },
        {
            "name": "3. Liderança inspiradora",
            "comportamentos": [
                "você inspira pelo exemplo",
                "você desenvolve talentos e equipes",
                "você toma decisões com coragem",
            ],
        },
    ],
    "2024": [
        {
            "name": "1. A gente trabalha para o cliente",
            "comportamentos": [
                "você tem obstinação por encantar o cliente",
                "você promove experiências diferenciadas",
                "você se coloca no lugar do cliente",
            ],
        },
        {
            "name": "2. Performance que transforma",
            "comportamentos": [
                "você busca resultados sustentáveis",
                "você tem mentalidade de dono",
                "você é eficiente e ágil nas entregas",
            ],
        },
        {
            "name": "3. Liderança inspiradora",
            "comportamentos": [
                "você inspira pelo exemplo",
                "você desenvolve talentos e equipes",
                "você toma decisões com coragem",
            ],
        },
        {
            "name": "4. Inovação e Agilidade",
            "comportamentos": [
                "você inova e busca soluções disruptivas",
                "você prioriza o cliente nas decisões técnicas",
                "você aprende e se adapta rapidamente",
            ],
        },
    ],
}

# Recomendações específicas para cada comportamento
BEHAVIOR_RECOMMENDATIONS = {
    "você tem obstinação por encantar o cliente": [
        "Acompanhar de perto a jornada do cliente para entender pontos de atrito",
        "Conversar diretamente com clientes para entender suas necessidades reais",
        "Fazer pesquisas periódicas de satisfação com seus clientes",
    ],
    "você promove experiências diferenciadas": [
        "Participar de workshops de design thinking centrado no cliente",
        "Implementar pesquisas de satisfação para suas entregas",
        'Perguntar-se regularmente: "Como o cliente se sente neste processo?"',
    ],
    "você se coloca no lugar do cliente": [
        "Criar mapas de empatia para seus principais clientes",
        "Participar de sessões de acompanhamento da jornada do cliente",
        "Realizar testes de usabilidade com clientes reais",
    ],
    "você busca resultados sustentáveis": [
        "Definir métricas claras para resultados sustentáveis",
        "Participar de projetos inovadores fora da zona de conforto",
        "Desenvolver métricas de longo prazo para seus projetos",
    ],
    "você tem mentalidade de dono": [
        "Criar plano de desenvolvimento específico para mentalidade de dono",
        "Estruturar análises de impacto para decisões importantes",
        "Assumir a responsabilidade por resultados além da sua área direta",
    ],
    "você é eficiente e ágil nas entregas": [
        "Aprimorar sua gestão de tempo e priorização",
        "Considerar metodologias ágeis e ferramentas de produtividade",
        "Documentar e otimizar processos recorrentes",
    ],
    "você inspira pelo exemplo": [
        "Buscar mentoria específica para desenvolver esta competência",
        "Criar plano de desenvolvimento pessoal com foco nesta área",
        "Solicitar feedback regular sobre seu comportamento como modelo",
    ],
    "você desenvolve talentos e equipes": [
        "Participar de treinamentos específicos neste tema",
        "Buscar feedback estruturado sobre este comportamento",
        "Dedicar tempo semanal para mentoria e desenvolvimento de colegas",
    ],
    "você toma decisões com coragem": [
        "Documentar decisões difíceis e seus resultados para aprendizado",
        "Criar um framework pessoal para tomada de decisões",
        "Buscar um mentor para apoiar em decisões críticas",
    ],
    "você inova e busca soluções disruptivas": [
        "Participar de comunidades de inovação dentro e fora da empresa",
        "Reservar tempo para experimentação e aprendizado",
        "Implementar um processo pessoal de geração e teste de ideias",
    ],
    "você prioriza o cliente nas decisões técnicas": [
        "Incluir representantes do cliente em decisões técnicas chave",
        "Criar critérios claros de priorização baseados no impacto para o cliente",
        "Validar com usuários reais antes de implementar soluções técnicas",
    ],
    "você aprende e se adapta rapidamente": [
        "Criar um plano estruturado de aprendizado contínuo",
        "Buscar feedback após cada projeto ou entrega significativa",
        "Documentar aprendizados e compartilhar com a equipe",
    ],
}

# Formato do plano de ação sugerido
ACTION_PLAN_TEMPLATE = """
**Plano de Ação Sugerido:**
• Curto prazo (3 meses): Foco no gap principal com feedback frequente
• Médio prazo (6 meses): Desenvolvimento dos gaps secundários
• Longo prazo (12 meses): Consolidação e mentoria para outros
"""

# Insights de carreira baseados no percentil de desempenho
CAREER_INSIGHTS = {
    "high": [
        "O desempenho destacado sugere potencial para:",
        "- Assumir projetos de maior visibilidade e impacto",
        "- Mentoria para colegas em desenvolvimento",
        "- Consideração para oportunidades de liderança",
    ],
    "medium": [
        "O desempenho sólido sugere foco em:",
        "- Identificar áreas específicas para se destacar ainda mais",
        "- Buscar projetos desafiadores para demonstrar potencial",
        "- Desenvolver habilidades de liderança situacional",
    ],
    "low": [
        "Para melhorar o posicionamento no grupo, recomenda-se:",
        "- Solicitar feedback específico e acionável",
        "- Desenvolver um plano estruturado para as principais oportunidades",
        "- Buscar mentoria com profissionais de alto desempenho",
    ],
}

#############################################
# Constantes para visualização e estilização
#############################################

# Cores para gráficos e visualizações
CHART_COLORS = {
    "primary": "#3498db",  # Azul principal
    "secondary": "#e74c3c",  # Vermelho secundário
    "neutral": "#95a5a6",  # Cinza neutro
    "highlight": "#f39c12",  # Laranja destaque
    "success": "#2ecc71",  # Verde sucesso
    "reference": "#34495e",  # Azul escuro referência
}

# Mapeamento de cores para conceitos em gráficos
CONCEPT_CHART_COLORS = {
    "acima do grupo": "green",
    "alinhado em relação ao grupo": "blue",
    "abaixo do grupo": "red",
    "default": "gray",
}

# Configurações para geração de gráficos
CHART_CONFIG = {
    # Tamanhos de figuras para diferentes tipos de gráficos
    "figsize": {
        "historical": (12, 8),
        "category": (10, 6),
        "radar": (8, 8),
        "comparative": (14, 8),
        "historical_detailed": (14, 14),
    },
    # Espessuras de linha para diferentes elementos
    "linewidth": {
        "primary": 2.5,
        "secondary": 2.0,
        "reference": 1.5,
    },
    # Tamanhos de marcadores para diferentes elementos
    "markersize": {
        "primary": 10,
        "secondary": 8,
        "highlight": 12,
    },
    # Tamanhos de texto para diferentes elementos
    "fontsize": {
        "title": 16,
        "axis_label": 12,
        "legend": 12,
        "annotation": 11,
        "tick": 10,
    },
    # Valores alfa para transparência
    "alpha": {
        "grid": 0.7,
        "fill": 0.25,
        "reference_line": 0.3,
        "annotation_box": 0.8,
    },
    # Valores de referência usados em gráficos
    "reference": {
        "average_score": 2.5,
    },
}

# Estilos para formatação de gráficos do radar
RADAR_CHART_STYLE = {
    "primary_color": "#3498db",
    "secondary_color": "#e74c3c",
    "primary_alpha": 0.25,
    "secondary_alpha": 0.1,
    "fontsize": 12,
    "tick_color": "grey",
    "tick_size": 8,
}

# Mapeamento de cores para diferenças de categoria em visualizações de timeline
TIMELINE_COLOR_MAP = {
    "acima do grupo": "rgb(0,128,0)",
    "alinhado em relação ao grupo": "rgb(0,0,255)",
    "abaixo do grupo": "rgb(255,0,0)",
    "default": "rgb(128,128,128)",
}

# Configurações para caixas de anotação em gráficos
ANNOTATION_BOX_STYLE = {
    "boxstyle": "round,pad=0.3",
    "fc": "white",
    "ec": "gray",
    "alpha": 0.8,
}

# Descritores de desempenho baseados na diferença com a média do grupo
PERFORMANCE_DESCRIPTORS = {
    "very_high": {
        "threshold": 0.5,
        "description": "significativamente acima da média do grupo",
    },
    "high": {
        "threshold": 0.2,
        "description": "acima da média do grupo",
    },
    "average": {
        "threshold": -0.2,
        "description": "alinhado com a média do grupo",
    },
    "low": {
        "threshold": -0.5,
        "description": "abaixo da média do grupo",
    },
    "very_low": {
        "threshold": float("-inf"),
        "description": "significativamente abaixo da média do grupo",
    },
}

# Descritores de tendência baseados na diferença entre o primeiro e o último ano
TREND_DESCRIPTORS = {
    "significant_up": {
        "threshold": 0.3,
        "description": "ascendente significativa",
    },
    "up": {
        "threshold": 0.1,
        "description": "ascendente",
    },
    "stable": {
        "threshold": -0.1,
        "description": "estável",
    },
    "down": {
        "threshold": -0.3,
        "description": "descendente",
    },
    "significant_down": {
        "threshold": float("-inf"),
        "description": "descendente significativa",
    },
}

#############################################
# Constantes para planilhas e exportações
#############################################

# Cores para escalas de cores em planilhas Excel
EXCEL_COLORS = {
    # Cores para pontuações
    "low_score": "FF6961",  # Vermelho para pontuações baixas
    "mid_score": "FFFF99",  # Amarelo para pontuações médias
    "high_score": "77DD77",  # Verde para pontuações altas
    # Cores para diferenças
    "negative": "FF0000",  # Vermelho para diferenças negativas
    "neutral": "FFFF00",  # Amarelo para valor zero
    "positive": "00FF00",  # Verde para diferenças positivas
    # Cores para rankings e formatação
    "top_rank": "92D050",  # Verde para top 3 no ranking
    "alt_row": "F2F2F2",  # Cinza claro para linhas alternadas
    "header": "366092",  # Azul escuro para cabeçalhos
}

# Configurações para formatação de cabeçalhos em planilhas
EXCEL_HEADER_STYLE = {
    "font": {
        "bold": True,
        "color": "FFFFFF",  # Branco
        "size": 11,
    },
    "alignment": {
        "horizontal": "center",
        "vertical": "center",
        "wrap_text": True,
    },
}

# Configurações para regras de formatação condicional
EXCEL_CONDITIONAL_FORMAT = {
    # Configuração para escala de cores de pontuações (1-5)
    "score_scale": {
        "start_value": 1,
        "mid_value": 3,
        "end_value": 5,
    },
    # Configuração para largura padrão de colunas
    "default_column_width": 20,
}
