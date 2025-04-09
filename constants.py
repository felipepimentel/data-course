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
