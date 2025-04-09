import argparse
import json
import random
from pathlib import Path

# Importar as constantes
from constants import (
    COMENTARIOS_GESTOR,
    COMENTARIOS_PARES,
    CONCEITOS,
    DIRECIONADORES_BY_YEAR,
    PERFORMANCE_CONCEPTS,
)

PEOPLE = [
    "João Silva",
    "Maria Oliveira",
    "Pedro Santos",
    "Ana Costa",
    "Carlos Pereira",
    "Lúcia Fernandes",
    "Roberto Almeida",
    "Patrícia Gomes",
]

# Colors for different concepts
COLORS = {
    "acima do grupo": "green",
    "alinhado em relação ao grupo": "blue",
    "abaixo do grupo": "red",
}


def normalize_frequencies(frequencies):
    """Normalize frequencies to ensure they sum to 100"""
    total = sum(frequencies)
    if total <= 0:
        return [0] * len(frequencies)
    return [int(round(freq / total * 100)) for freq in frequencies]


def generate_frequency_distribution(performance_level):
    """Generate frequency distribution based on performance level"""
    base_distribution = None

    if performance_level == "high":
        # High performers have more "observo sempre" and less "observo nunca"
        base_distribution = [
            random.randint(0, 5),  # n/a
            random.randint(0, 10),  # observo nunca
            random.randint(10, 30),  # observo raramente
            random.randint(30, 50),  # observo na maior parte das vezes
            random.randint(20, 40),  # observo sempre
            random.randint(0, 10),  # referencia
        ]
    elif performance_level == "medium":
        # Medium performers have balanced distribution
        base_distribution = [
            random.randint(0, 5),  # n/a
            random.randint(5, 15),  # observo nunca
            random.randint(20, 40),  # observo raramente
            random.randint(30, 50),  # observo na maior parte das vezes
            random.randint(10, 25),  # observo sempre
            random.randint(0, 5),  # referencia
        ]
    else:  # low
        # Low performers have more "observo nunca" and less "observo sempre"
        base_distribution = [
            random.randint(0, 5),  # n/a
            random.randint(10, 25),  # observo nunca
            random.randint(40, 60),  # observo raramente
            random.randint(20, 40),  # observo na maior parte das vezes
            random.randint(0, 15),  # observo sempre
            random.randint(0, 5),  # referencia
        ]

    return base_distribution


def generate_group_frequency():
    """Generate average group frequency"""
    return [
        random.randint(0, 5),  # n/a
        random.randint(5, 15),  # observo nunca
        random.randint(25, 45),  # observo raramente
        random.randint(30, 50),  # observo na maior parte das vezes
        random.randint(5, 15),  # observo sempre
        random.randint(0, 5),  # referencia
    ]


def create_evaluation(person, year, performance_trend):
    """Create a single evaluation JSON file"""
    # Determine performance level based on trend and year
    years = ["2021", "2022", "2023", "2024"]
    year_index = years.index(year)

    if performance_trend == "improving":
        # Performance improves over years
        if year_index == 0:
            performance_level = "low"
        elif year_index == 1:
            performance_level = "low" if random.random() < 0.7 else "medium"
        elif year_index == 2:
            performance_level = "medium" if random.random() < 0.7 else "high"
        else:
            performance_level = "high"
    elif performance_trend == "declining":
        # Performance declines over years
        if year_index == 0:
            performance_level = "high"
        elif year_index == 1:
            performance_level = "high" if random.random() < 0.7 else "medium"
        elif year_index == 2:
            performance_level = "medium" if random.random() < 0.7 else "low"
        else:
            performance_level = "low"
    elif performance_trend == "stable_high":
        performance_level = "high"
    elif performance_trend == "stable_medium":
        performance_level = "medium"
    else:  # stable_low
        performance_level = "low"

    # Assign overall concept based on performance
    if performance_level == "high":
        conceito = PERFORMANCE_CONCEPTS[2]  # "acima do grupo"
    elif performance_level == "medium":
        conceito = PERFORMANCE_CONCEPTS[1]  # "alinhado em relação ao grupo"
    else:
        conceito = PERFORMANCE_CONCEPTS[0]  # "abaixo do grupo"

    # Build direcionadores for this year
    direcionadores = []
    for direcionador in DIRECIONADORES_BY_YEAR[year]:
        comportamentos = []
        for comportamento in direcionador["comportamentos"]:
            # Generate frequencies for this behavior
            person_freq = generate_frequency_distribution(performance_level)
            group_freq = generate_group_frequency()

            # Normalize to ensure they sum to 100
            person_freq = normalize_frequencies(person_freq)
            group_freq = normalize_frequencies(group_freq)

            # Individual evaluations
            auto_conceito_index = min(
                3,
                max(
                    0,
                    {"high": 3, "medium": 2, "low": 1}[performance_level]
                    + random.randint(-1, 0),
                ),
            )
            gestor_conceito_index = min(
                3,
                max(
                    0,
                    {"high": 3, "medium": 2, "low": 1}[performance_level]
                    + random.randint(-1, 1),
                ),
            )

            comportamentos.append({
                "comportamento": comportamento,
                "pergunta_final": False,
                "avaliacoes_grupo": [
                    {
                        "avaliador": "%todos",
                        "frequencia_colaborador": person_freq,
                        "frequencia_grupo": group_freq,
                    },
                    {
                        "avaliador": "%pares e parceiros",
                        "frequencia_colaborador": normalize_frequencies([
                            f + random.randint(-5, 5) for f in person_freq
                        ]),
                        "frequencia_grupo": normalize_frequencies([
                            f + random.randint(-5, 5) for f in group_freq
                        ]),
                    },
                ],
                "avaliacoes_individuais": [
                    {
                        "avaliador": "autoavaliação",
                        "conceito": CONCEITOS[auto_conceito_index],
                        "cor": "MAGENTA",
                    },
                    {
                        "avaliador": "gestor",
                        "conceito": CONCEITOS[gestor_conceito_index],
                        "cor": "8628025",
                    },
                ],
            })

        direcionadores.append({
            "direcionador": direcionador["name"],
            "pergunta_final": False,
            "comportamentos": comportamentos,
        })

    # Generate comments based on performance
    gestor_comment = random.choice(COMENTARIOS_GESTOR)
    par_comment = random.choice(COMENTARIOS_PARES)

    comentarios = [
        {
            "codigo": 4,
            "texto": {"comentario": gestor_comment},
            "tipo": 0,
            "nome_fonte": "gestor",
        },
        {
            "codigo": 1,
            "texto": {"comentario": par_comment},
            "tipo": 1,
            "nome_fonte": "par/parceiro",
        },
    ]

    # Complete evaluation
    evaluation = {
        "success": True,
        "status_code": 200,
        "message": None,
        "data": {
            "conceito_ciclo_filho_descricao": conceito,
            "nome_peer_group": None,
            "direcionadores": direcionadores,
            "comentarios": comentarios,
        },
    }

    return evaluation


def create_test_data(output_path, years=None):
    if years is None:
        years = ["2021", "2022", "2023", "2024"]

    base_path = Path(output_path)

    # Assign performance trends to people
    performance_trends = {
        person: random.choice([
            "improving",
            "declining",
            "stable_high",
            "stable_medium",
            "stable_low",
        ])
        for person in PEOPLE
    }

    # Create directory structure
    for person in PEOPLE:
        person_dir = base_path / person
        person_dir.mkdir(parents=True, exist_ok=True)

        for year in years:
            year_dir = person_dir / year
            year_dir.mkdir(exist_ok=True)

            # Skip some years randomly to simulate incomplete data
            if (
                random.random() < 0.2 and year != years[-1]
            ):  # 20% chance to skip, but keep latest year
                continue

            evaluation = create_evaluation(person, year, performance_trends[person])

            # Save the JSON file
            with open(year_dir / "resultado.json", "w", encoding="utf-8") as f:
                json.dump(evaluation, f, indent=2, ensure_ascii=False)

    print(
        f"Generated test data for {len(PEOPLE)} people across {len(years)} years at {base_path}"
    )
    print("\nPeople and their performance trends:")
    for person, trend in performance_trends.items():
        print(f"- {person}: {trend.replace('_', ' ')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate test data for the 360 evaluation analyzer"
    )
    parser.add_argument(
        "output_path", help="Path where the test data will be generated"
    )
    parser.add_argument(
        "--years",
        nargs="+",
        help="Years to generate (default: 2021-2024)",
        default=["2021", "2022", "2023", "2024"],
    )

    args = parser.parse_args()
    create_test_data(args.output_path, args.years)
