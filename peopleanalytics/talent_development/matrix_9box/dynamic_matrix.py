"""
Implementação da Matriz 9-Box Dinâmica para rastreamento de potencial e desempenho.
"""

from pathlib import Path

# Configure matplotlib to use non-interactive backend
import matplotlib

matplotlib.use("Agg")  # Set backend to Agg (non-interactive)

import datetime
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

from peopleanalytics.data_pipeline import DataPipeline
from peopleanalytics.talent_development.matrix_9box.trajectory import TrajectoryAnalyzer


@dataclass
class MatrixPosition:
    """Posição de um colaborador na matriz 9-box."""

    performance: float  # 0.0 a 10.0
    potential: float  # 0.0 a 10.0
    timestamp: datetime.datetime
    source_data: Dict[str, Any]  # Dados que geraram esta posição

    @property
    def quadrant(self) -> Tuple[int, int]:
        """Retorna o quadrante (x, y) na matriz 9-box (0-2, 0-2)."""
        x = min(2, max(0, int(self.performance / 3.4)))
        y = min(2, max(0, int(self.potential / 3.4)))
        return (x, y)

    @property
    def quadrant_name(self) -> str:
        """Retorna o nome do quadrante na matriz 9-box."""
        names = {
            (0, 0): "Baixo Desempenho / Baixo Potencial",
            (0, 1): "Baixo Desempenho / Médio Potencial",
            (0, 2): "Baixo Desempenho / Alto Potencial",
            (1, 0): "Médio Desempenho / Baixo Potencial",
            (1, 1): "Médio Desempenho / Médio Potencial",
            (1, 2): "Médio Desempenho / Alto Potencial",
            (2, 0): "Alto Desempenho / Baixo Potencial",
            (2, 1): "Alto Desempenho / Médio Potencial",
            (2, 2): "Alto Desempenho / Alto Potencial",
        }
        return names[self.quadrant]


class DynamicMatrix9Box:
    """
    Matriz 9-Box Dinâmica que rastreia a evolução temporal do posicionamento
    de colaboradores na matriz de potencial e desempenho.

    Funcionalidades:
    - Rastreamento temporal: Posicionamento nos últimos 4-8 trimestres
    - Vetores de movimento: Direção e velocidade de evolução
    - Gatilhos de aceleração: Identificar eventos que causaram saltos de performance
    - Projeção futura: IA prevendo posicionamento futuro baseado em intervenções
    """

    def __init__(self, data_pipeline: Optional[DataPipeline] = None):
        """
        Inicializa a matriz 9-box dinâmica.

        Args:
            data_pipeline: Pipeline de dados opcional para carregar dados existentes
        """
        self.historical_data = {}  # person_id -> List[MatrixPosition]
        self.trajectory_analyzer = TrajectoryAnalyzer()
        self.data_pipeline = data_pipeline

    def load_data(self, person_id: str) -> List[MatrixPosition]:
        """
        Carrega dados históricos de posicionamento na matriz para uma pessoa.

        Args:
            person_id: ID da pessoa

        Returns:
            Lista de posições históricas na matriz 9-box
        """
        if self.data_pipeline is None:
            return []

        # Carrega dados de avaliação de desempenho
        performance_data = self.data_pipeline.load_performance_evaluations(person_id)

        # Carrega dados de potencial
        potential_data = self.data_pipeline.load_potential_assessments(person_id)

        # Combina os dados por período
        positions = []
        for period, perf_value in performance_data.items():
            if period in potential_data:
                pot_value = potential_data[period]
                timestamp = datetime.datetime.strptime(period, "%Y-Q%m")

                # Normaliza valores para escala 0-10
                normalized_perf = perf_value * 10 / 5  # Assumindo escala original 0-5
                normalized_pot = pot_value * 10 / 5  # Assumindo escala original 0-5

                position = MatrixPosition(
                    performance=normalized_perf,
                    potential=normalized_pot,
                    timestamp=timestamp,
                    source_data={
                        "performance": perf_value,
                        "potential": pot_value,
                        "period": period,
                    },
                )
                positions.append(position)

        # Ordena por data
        positions.sort(key=lambda p: p.timestamp)

        # Armazena no cache
        self.historical_data[person_id] = positions

        return positions

    def add_position(
        self,
        person_id: str,
        performance: float,
        potential: float,
        timestamp: datetime.datetime,
        source_data: Dict[str, Any] = None,
    ) -> MatrixPosition:
        """
        Adiciona uma nova posição na matriz 9-box para uma pessoa.

        Args:
            person_id: ID da pessoa
            performance: Valor de desempenho (0-10)
            potential: Valor de potencial (0-10)
            timestamp: Data/hora da avaliação
            source_data: Dados de origem que geraram esta avaliação

        Returns:
            Nova posição criada na matriz
        """
        if person_id not in self.historical_data:
            self.historical_data[person_id] = []

        position = MatrixPosition(
            performance=performance,
            potential=potential,
            timestamp=timestamp,
            source_data=source_data or {},
        )

        self.historical_data[person_id].append(position)
        # Ordena por data
        self.historical_data[person_id].sort(key=lambda p: p.timestamp)

        return position

    def analyze_trajectory(
        self, person_id: str, timespan_quarters: int = 8
    ) -> Dict[str, Any]:
        """
        Analisa a trajetória de uma pessoa na matriz 9-box.

        Args:
            person_id: ID da pessoa
            timespan_quarters: Número de trimestres para análise (padrão: 8)

        Returns:
            Análise completa da trajetória, contendo:
            - positions: Posições históricas
            - movement_vector: Vetor de movimento (direção e velocidade)
            - acceleration_triggers: Eventos que causaram aceleração
            - future_projection: Projeção para próximos trimestres
        """
        # Certifica que temos dados para a pessoa
        if person_id not in self.historical_data:
            self.load_data(person_id)

        if person_id not in self.historical_data:
            return {
                "positions": [],
                "movement_vector": None,
                "acceleration_triggers": [],
                "future_projection": None,
            }

        # Filtra para o período solicitado
        cutoff_date = datetime.datetime.now() - datetime.timedelta(
            days=timespan_quarters * 90
        )
        positions = [
            p for p in self.historical_data[person_id] if p.timestamp >= cutoff_date
        ]

        # Se não tivermos posições suficientes, retorna dados limitados
        if len(positions) < 2:
            return {
                "positions": positions,
                "movement_vector": None,
                "acceleration_triggers": [],
                "future_projection": None,
            }

        # Calcula o vetor de movimento
        movement_vector = self.trajectory_analyzer.calculate_movement_vector(positions)

        # Identifica gatilhos de aceleração
        acceleration_triggers = self.trajectory_analyzer.identify_acceleration_triggers(
            positions, person_id, self.data_pipeline
        )

        # Gera projeção futura
        future_projection = self.trajectory_analyzer.generate_future_projection(
            positions, movement_vector, acceleration_triggers
        )

        return {
            "positions": positions,
            "movement_vector": movement_vector,
            "acceleration_triggers": acceleration_triggers,
            "future_projection": future_projection,
        }

    def visualize_matrix(
        self,
        person_id: str,
        output_path: Optional[Path] = None,
        show_trajectories: bool = True,
        show_future: bool = True,
        timespan_quarters: int = 8,
    ) -> Path:
        """
        Gera visualização da matriz 9-box para uma pessoa, incluindo sua trajetória.

        Args:
            person_id: ID da pessoa
            output_path: Caminho para salvar a visualização (opcional)
            show_trajectories: Se deve mostrar a trajetória histórica
            show_future: Se deve mostrar a projeção futura
            timespan_quarters: Número de trimestres para análise

        Returns:
            Caminho para a visualização gerada
        """
        # Obter análise de trajetória
        analysis = self.analyze_trajectory(person_id, timespan_quarters)

        # Configurar o plot
        fig, ax = plt.subplots(figsize=(12, 10))

        # Desenhar a grade da matriz 9-box
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_xticks([0, 3.33, 6.67, 10])
        ax.set_yticks([0, 3.33, 6.67, 10])
        ax.set_xticklabels(["0", "Baixo", "Médio", "Alto"])
        ax.set_yticklabels(["0", "Baixo", "Médio", "Alto"])
        ax.set_xlabel("Desempenho", fontsize=14)
        ax.set_ylabel("Potencial", fontsize=14)
        ax.set_title(f"Matriz 9-Box Dinâmica: {person_id}", fontsize=16)

        # Adicionar linhas de grade para os quadrantes
        ax.grid(True, linestyle="--", alpha=0.7)
        ax.axvline(x=3.33, color="black", linestyle="-", alpha=0.5)
        ax.axvline(x=6.67, color="black", linestyle="-", alpha=0.5)
        ax.axhline(y=3.33, color="black", linestyle="-", alpha=0.5)
        ax.axhline(y=6.67, color="black", linestyle="-", alpha=0.5)

        # Criar um colormap para os quadrantes
        colors = [
            [0.7, 0.7, 0.7],  # Baixo/Baixo - Cinza
            [1.0, 0.8, 0.2],  # Médio/Baixo - Amarelo acinzentado
            [1.0, 0.6, 0.4],  # Alto/Baixo - Laranja
            [0.6, 0.8, 1.0],  # Baixo/Médio - Azul claro
            [0.8, 0.8, 0.8],  # Médio/Médio - Cinza médio
            [0.6, 1.0, 0.6],  # Alto/Médio - Verde claro
            [0.4, 0.6, 1.0],  # Baixo/Alto - Azul médio
            [0.4, 0.9, 0.4],  # Médio/Alto - Verde médio
            [0.2, 1.0, 0.2],  # Alto/Alto - Verde forte
        ]

        # Desenhar os quadrantes coloridos
        for i in range(3):
            for j in range(3):
                rect = plt.Rectangle(
                    (i * 3.33, j * 3.33),
                    3.33,
                    3.33,
                    facecolor=colors[i + j * 3],
                    alpha=0.3,
                )
                ax.add_patch(rect)

                # Adicionar rótulos nos quadrantes
                labels = [
                    "Problema de\nDesempenho",
                    "Enigma",
                    "Estrela em\nAscensão",
                    "Profissional\nSólido",
                    "Profissional\nChave",
                    "Futuro\nTalento",
                    "Especialista\nTécnico",
                    "Alta\nPerformance",
                    "Estrela\nOrganizacional",
                ]
                ax.text(
                    i * 3.33 + 1.67,
                    j * 3.33 + 1.67,
                    labels[i + j * 3],
                    ha="center",
                    va="center",
                    fontsize=10,
                )

        # Plotar a trajetória histórica
        positions = analysis["positions"]
        if show_trajectories and len(positions) > 0:
            perf_values = [p.performance for p in positions]
            pot_values = [p.potential for p in positions]
            timestamps = [p.timestamp for p in positions]

            # Plotar pontos com tamanho variando por recência
            sizes = np.linspace(30, 100, len(positions))
            colors = plt.cm.viridis(np.linspace(0, 1, len(positions)))

            for i, (perf, pot, ts, sz, clr) in enumerate(
                zip(perf_values, pot_values, timestamps, sizes, colors)
            ):
                ax.scatter(perf, pot, s=sz, color=clr, alpha=0.7, edgecolor="black")
                ax.text(perf + 0.2, pot + 0.2, ts.strftime("%Y-Q%m"), fontsize=8)

                # Conectar pontos com linhas
                if i > 0:
                    ax.plot(
                        [perf_values[i - 1], perf],
                        [pot_values[i - 1], pot],
                        "k-",
                        alpha=0.5,
                    )

            # Adicionar legenda de tempo
            sm = plt.cm.ScalarMappable(
                cmap=plt.cm.viridis, norm=plt.Normalize(0, len(positions) - 1)
            )
            cbar = plt.colorbar(sm, ax=ax)
            cbar.set_ticks([0, len(positions) - 1])
            cbar.set_ticklabels(
                [timestamps[0].strftime("%Y-Q%m"), timestamps[-1].strftime("%Y-Q%m")]
            )
            cbar.set_label("Período")

        # Plotar projeção futura
        if show_future and analysis["future_projection"]:
            future_proj = analysis["future_projection"]
            future_perf = [p.performance for p in future_proj.projected_positions]
            future_pot = [p.potential for p in future_proj.projected_positions]

            # Usar linha tracejada para projeção futura
            ax.plot(future_perf, future_pot, "r--", alpha=0.7)
            ax.scatter(
                future_perf, future_pot, s=30, color="red", alpha=0.5, marker="x"
            )

            # Adicionar área sombreada para indicar incerteza na projeção
            confidence = 0.2  # Margem de erro
            for i, (perf, pot) in enumerate(zip(future_perf, future_pot)):
                confidence_factor = (i + 1) * confidence  # Aumenta com o tempo
                circle = plt.Circle(
                    (perf, pot), confidence_factor, color="red", fill=True, alpha=0.1
                )
                ax.add_patch(circle)

        # Adicionar anotações para gatilhos de aceleração
        for trigger in analysis.get("acceleration_triggers", []):
            timestamp = trigger.timestamp
            event_type = trigger.event_type

            # Encontrar a posição correspondente a este gatilho
            matching_positions = [p for p in positions if p.timestamp == timestamp]
            if matching_positions:
                pos = matching_positions[0]
                ax.annotate(
                    f"{event_type}",
                    xy=(pos.performance, pos.potential),
                    xytext=(pos.performance + 1, pos.potential + 1),
                    arrowprops=dict(facecolor="green", shrink=0.05, width=1.5),
                    fontsize=9,
                    color="green",
                )

        # Configurações finais do plot
        plt.tight_layout()

        # Salvar ou mostrar a figura
        if output_path:
            plt.savefig(output_path)
            return output_path
        else:
            # Gerar um nome padrão na pasta output
            output_dir = Path("output") / "matrix_9box"
            output_dir.mkdir(parents=True, exist_ok=True)

            output_file = (
                output_dir
                / f"{person_id}_matrix_9box_{datetime.datetime.now().strftime('%Y%m%d')}.png"
            )
            plt.savefig(output_file)
            plt.close()
            return output_file

    def generate_report(
        self,
        person_id: str,
        output_path: Optional[Path] = None,
        timespan_quarters: int = 8,
    ) -> Tuple[Path, Path]:
        """
        Gera um relatório completo da matriz 9-box para uma pessoa, incluindo
        visualização e análise textual.

        Args:
            person_id: ID da pessoa
            output_path: Diretório para salvar o relatório (opcional)
            timespan_quarters: Número de trimestres para análise

        Returns:
            Tuple contendo caminhos para o relatório e a visualização
        """
        # Obter análise de trajetória
        analysis = self.analyze_trajectory(person_id, timespan_quarters)

        # Gerar visualização
        if output_path:
            viz_path = output_path / f"{person_id}_matrix_9box.png"
        else:
            output_dir = Path("output") / "matrix_9box"
            output_dir.mkdir(parents=True, exist_ok=True)
            viz_path = (
                output_dir
                / f"{person_id}_matrix_9box_{datetime.datetime.now().strftime('%Y%m%d')}.png"
            )

        self.visualize_matrix(person_id, viz_path, timespan_quarters=timespan_quarters)

        # Gerar relatório textual
        positions = analysis["positions"]
        movement_vector = analysis["movement_vector"]
        acceleration_triggers = analysis["acceleration_triggers"]
        future_projection = analysis["future_projection"]

        # Preparar arquivo de relatório
        if output_path:
            report_path = output_path / f"{person_id}_matrix_9box_report.md"
        else:
            report_path = (
                Path("output")
                / "matrix_9box"
                / f"{person_id}_matrix_9box_report_{datetime.datetime.now().strftime('%Y%m%d')}.md"
            )

        with open(report_path, "w") as f:
            f.write(f"# Relatório de Matriz 9-Box: {person_id}\n\n")
            f.write(
                f"Data de geração: {datetime.datetime.now().strftime('%d/%m/%Y')}\n\n"
            )

            f.write("## Posicionamento Atual\n\n")
            if positions:
                current = positions[-1]
                f.write(f"**Quadrante Atual:** {current.quadrant_name}\n")
                f.write(f"**Desempenho:** {current.performance:.2f}/10\n")
                f.write(f"**Potencial:** {current.potential:.2f}/10\n")
                f.write(
                    f"**Data da última avaliação:** {current.timestamp.strftime('%d/%m/%Y')}\n\n"
                )
            else:
                f.write("Não há dados de posicionamento disponíveis.\n\n")

            f.write("## Trajetória\n\n")
            if movement_vector:
                f.write(
                    f"**Direção do movimento:** {movement_vector.direction_degrees:.1f}° "
                )

                # Interpretar a direção
                if 45 <= movement_vector.direction_degrees <= 135:
                    f.write("(crescimento de potencial prioritário)\n")
                elif 225 <= movement_vector.direction_degrees <= 315:
                    f.write("(redução de potencial preocupante)\n")
                elif 135 < movement_vector.direction_degrees < 225:
                    f.write("(redução de desempenho preocupante)\n")
                else:
                    f.write("(crescimento de desempenho prioritário)\n")

                f.write(
                    f"**Velocidade de evolução:** {movement_vector.velocity:.2f} pontos/trimestre\n"
                )

                # Interpretar a velocidade
                if movement_vector.velocity > 1.0:
                    f.write("Evolução acelerada - acima do esperado.\n")
                elif movement_vector.velocity > 0.5:
                    f.write("Evolução satisfatória - dentro do esperado.\n")
                elif movement_vector.velocity > 0:
                    f.write("Evolução lenta - abaixo do esperado.\n")
                else:
                    f.write("Estagnação ou retrocesso - atenção necessária.\n")

                f.write("\n")
            else:
                f.write("Dados insuficientes para análise de trajetória.\n\n")

            f.write("## Gatilhos de Aceleração\n\n")
            if acceleration_triggers:
                for i, trigger in enumerate(acceleration_triggers, 1):
                    f.write(f"### Gatilho {i}: {trigger.event_type}\n")
                    f.write(f"**Data:** {trigger.timestamp.strftime('%d/%m/%Y')}\n")
                    f.write(f"**Descrição:** {trigger.description}\n")
                    f.write(f"**Impacto:** {trigger.impact_description}\n\n")
            else:
                f.write(
                    "Nenhum gatilho de aceleração identificado no período analisado.\n\n"
                )

            f.write("## Projeção Futura\n\n")
            if future_projection:
                f.write(
                    f"**Quadrante projetado (em 1 ano):** {future_projection.projected_positions[-1].quadrant_name}\n"
                )
                f.write(
                    f"**Desempenho projetado:** {future_projection.projected_positions[-1].performance:.2f}/10\n"
                )
                f.write(
                    f"**Potencial projetado:** {future_projection.projected_positions[-1].potential:.2f}/10\n"
                )
                f.write(
                    f"**Confiança da projeção:** {future_projection.confidence_level * 100:.0f}%\n\n"
                )

                f.write("### Intervenções Recomendadas\n\n")
                for i, intervention in enumerate(
                    future_projection.recommended_interventions, 1
                ):
                    f.write(f"{i}. **{intervention['title']}**\n")
                    f.write(f"   {intervention['description']}\n")
                    f.write(
                        f"   Impacto estimado: {intervention['estimated_impact']}\n\n"
                    )
            else:
                f.write("Dados insuficientes para projeção futura.\n\n")

            f.write("## Visualização\n\n")
            f.write(f"![Matriz 9-Box]({viz_path.name})\n\n")

            f.write("## Notas e Recomendações\n\n")
            if positions:
                current = positions[-1]
                quads = {
                    (
                        0,
                        0,
                    ): "Considerar programa de recuperação de desempenho ou reavaliação de fit no cargo atual.",
                    (
                        0,
                        1,
                    ): "Investigar barreiras ao desempenho. Considerar realocação ou mudança de responsabilidades.",
                    (
                        0,
                        2,
                    ): "Potencial não realizado. Avaliar se está na função correta ou precisa de melhor direcionamento.",
                    (
                        1,
                        0,
                    ): "Bom executor, mas com limitações de crescimento. Foco em especialização técnica.",
                    (
                        1,
                        1,
                    ): "Profissional sólido. Manter engajado com desafios incrementais.",
                    (
                        1,
                        2,
                    ): "Alto potencial em desenvolvimento. Oferecer desafios crescentes e mentoria estruturada.",
                    (
                        2,
                        0,
                    ): "Excelente no papel atual, mas com teto atingido. Valorizar contribuição especializada.",
                    (
                        2,
                        1,
                    ): "Forte performer com potencial de crescimento. Expandir escopo e responsabilidades.",
                    (
                        2,
                        2,
                    ): "Talento excepcional. Desenvolvimento acelerado, exposição estratégica e plano de sucessão.",
                }

                q = current.quadrant
                f.write(f"{quads.get(q, 'Análise personalizada necessária.')}\n\n")

                # Adicionar recomendações baseadas na trajetória
                if movement_vector:
                    if movement_vector.velocity < 0:
                        f.write(
                            "**Alerta:** A trajetória atual mostra retrocesso. Recomenda-se intervenção imediata e análise aprofundada das causas.\n\n"
                        )
                    elif movement_vector.velocity < 0.3:
                        f.write(
                            "**Atenção:** A velocidade de evolução está abaixo do esperado. Revisar desafios e suporte oferecidos.\n\n"
                        )
            else:
                f.write("Dados insuficientes para recomendações específicas.\n")

        return report_path, viz_path
