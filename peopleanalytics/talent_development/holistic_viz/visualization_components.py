"""
Componentes de Visualização para o Dashboard Holístico.

Este módulo fornece componentes de visualização especializados para
o dashboard holístico de desenvolvimento de talentos.
"""

from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_radar_chart(
    skills: Dict[str, float],
    title: str = "Radar de Competências",
    target_skills: Optional[Dict[str, float]] = None,
    skill_categories: Optional[Dict[str, str]] = None,
    filename: Optional[str] = None,
    color_scheme: Optional[Dict[str, str]] = None,
) -> go.Figure:
    """
    Cria um gráfico radar de competências interativo usando Plotly.

    Args:
        skills: Dicionário com nomes de habilidades e seus valores
        title: Título do gráfico
        target_skills: Dicionário com habilidades alvo para comparação (opcional)
        skill_categories: Dicionário mapeando habilidades para suas categorias (opcional)
        filename: Caminho para salvar o gráfico (opcional)
        color_scheme: Cores customizadas para o gráfico (opcional)

    Returns:
        Figura Plotly
    """
    if not skills:
        # Create an empty figure with a message if no skills data
        fig = go.Figure()
        fig.add_annotation(
            text="No skills data available",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=16),
        )
        fig.update_layout(title=title)
        return fig

    # Use only top 10 skills if there are more than 10
    if len(skills) > 10:
        skills = dict(sorted(skills.items(), key=lambda x: x[1], reverse=True)[:10])

    # Default color scheme
    default_colors = {
        "current": {"line": "rgb(53, 135, 212)", "fill": "rgba(53, 135, 212, 0.3)"},
        "target": {"line": "rgb(255, 102, 77)", "fill": "rgba(255, 102, 77, 0.2)"},
    }

    if color_scheme:
        # Update with custom colors if provided
        if "current" in color_scheme:
            default_colors["current"].update(color_scheme["current"])
        if "target" in color_scheme:
            default_colors["target"].update(color_scheme["target"])

    categories = list(skills.keys())
    values = list(skills.values())

    # Normalize values to 0-1 scale if above 1
    max_value = max(values + list(target_skills.values() if target_skills else []))
    if max_value > 1:
        normalized_values = [v / 5 if max_value >= 5 else v / max_value for v in values]
        if target_skills:
            target_values = [
                t / 5 if max_value >= 5 else t / max_value
                for t in [target_skills.get(c, 0) for c in categories]
            ]
    else:
        normalized_values = values
        if target_skills:
            target_values = [target_skills.get(c, 0) for c in categories]

    # Start figure
    fig = go.Figure()

    # Group categories if provided
    if skill_categories:
        category_groups = {}
        for skill, category in skill_categories.items():
            if skill in categories:
                if category not in category_groups:
                    category_groups[category] = []
                category_groups[category].append(categories.index(skill))

        # Add category annotations
        for category, indices in category_groups.items():
            if not indices:
                continue

            # For each category, add a colored segment
            mid_idx = len(indices) // 2
            if mid_idx < len(indices):
                mid_skill = categories[indices[mid_idx]]
                # Calculate angle for annotation (approximation)
                angle_deg = (360 * indices[mid_idx] / len(categories)) % 360
                fig.add_annotation(
                    text=category,
                    r=1.2,
                    theta=angle_deg,
                    font=dict(size=10, color="grey"),
                    showarrow=False,
                )

    # Add current skills trace
    fig.add_trace(
        go.Scatterpolar(
            r=normalized_values + [normalized_values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name="Current Skills",
            line_color=default_colors["current"]["line"],
            fillcolor=default_colors["current"]["fill"],
        )
    )

    # Add target skills if provided
    if target_skills:
        fig.add_trace(
            go.Scatterpolar(
                r=target_values + [target_values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                name="Target Skills",
                line_color=default_colors["target"]["line"],
                fillcolor=default_colors["target"]["fill"],
                line=dict(dash="dash"),
            )
        )

    # Update layout
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title=title,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # Save to file if filename provided
    if filename:
        fig.write_image(filename)
        fig.write_html(filename.replace(".png", ".html").replace(".jpg", ".html"))

    return fig


def create_3d_career_path(
    paths: List[Dict[str, Any]],
    dimensions: Tuple[str, str, str] = ("skill_level", "impact", "time"),
    title: str = "Trajetória de Carreira 3D",
) -> go.Figure:
    """
    Cria uma visualização 3D de caminhos de carreira usando Plotly.

    Args:
        paths: Lista de caminhos de carreira, cada um com pontos e scores
        dimensions: Dimensões a serem utilizadas nos eixos x, y, z
        title: Título do gráfico

    Returns:
        Figura Plotly
    """
    fig = go.Figure()

    colors = px.colors.qualitative.Plotly

    for i, path in enumerate(paths[:3]):  # Limitar a 3 caminhos para claridade
        x = [point.get(dimensions[0], 0) for point in path["points"]]
        y = [point.get(dimensions[1], 0) for point in path["points"]]
        z = [point.get(dimensions[2], 0) for point in path["points"]]

        # Adicionar trajetória
        fig.add_trace(
            go.Scatter3d(
                x=x,
                y=y,
                z=z,
                mode="lines+markers",
                marker=dict(size=5, color=colors[i % len(colors)]),
                line=dict(color=colors[i % len(colors)], width=3),
                name=f"Caminho {i + 1} (Score: {path.get('score', 0):.2f})",
            )
        )

        # Adicionar anotações para as posições
        for j, point in enumerate(path["points"]):
            if "title" in point:
                fig.add_trace(
                    go.Scatter3d(
                        x=[x[j]],
                        y=[y[j]],
                        z=[z[j]],
                        mode="markers+text",
                        marker=dict(size=8, color=colors[i % len(colors)]),
                        text=[point["title"]],
                        name=point["title"],
                        showlegend=False,
                    )
                )

    # Configurar layout
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title=dimensions[0].replace("_", " ").title(),
            yaxis_title=dimensions[1].replace("_", " ").title(),
            zaxis_title=dimensions[2].replace("_", " ").title(),
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        legend=dict(x=0, y=1),
    )

    return fig


def create_performance_vs_potential_matrix(
    people: List[Dict[str, Any]],
    highlight_person_id: Optional[str] = None,
    show_names: bool = True,
    title: str = "Matriz Desempenho vs. Potencial",
) -> go.Figure:
    """
    Cria uma matriz 9-box interativa de desempenho vs. potencial.

    Args:
        people: Lista de dicionários com dados das pessoas
        highlight_person_id: ID da pessoa a ser destacada (opcional)
        show_names: Se True, mostra os nomes das pessoas
        title: Título do gráfico

    Returns:
        Figura Plotly
    """
    fig = go.Figure()

    # Extrair dados
    names = [p.get("name", f"Pessoa {i}") for i, p in enumerate(people)]
    potentials = [p.get("potential_score", 0) for p in people]
    performances = [p.get("performance_score", 0) for p in people]
    person_ids = [p.get("person_id", f"id_{i}") for i, p in enumerate(people)]

    # Definir cores - destacar pessoa selecionada
    colors = ["royalblue"] * len(people)
    sizes = [30] * len(people)

    if highlight_person_id:
        for i, pid in enumerate(person_ids):
            if pid == highlight_person_id:
                colors[i] = "crimson"
                sizes[i] = 45

    # Criar scatter plot
    fig.add_trace(
        go.Scatter(
            x=potentials,
            y=performances,
            mode="markers+text" if show_names else "markers",
            marker=dict(
                color=colors, size=sizes, line=dict(width=2, color="DarkSlateGrey")
            ),
            text=names if show_names else None,
            textposition="top center",
            name="Colaboradores",
            hovertemplate="<b>%{text}</b><br>"
            + "Potencial: %{x:.2f}<br>"
            + "Desempenho: %{y:.2f}<br>",
        )
    )

    # Adicionar linhas divisórias
    for v in [0.33, 0.67]:
        fig.add_shape(
            type="line",
            line=dict(dash="dash", width=1, color="gray"),
            x0=v,
            y0=0,
            x1=v,
            y1=1,
        )
        fig.add_shape(
            type="line",
            line=dict(dash="dash", width=1, color="gray"),
            y0=v,
            x0=0,
            y1=v,
            x1=1,
        )

    # Adicionar rótulos dos quadrantes
    quadrant_labels = [
        ["Performer em Risco", "Performer Sólido", "Performer Forte"],
        ["Enigma", "Core", "Alta Performance"],
        ["Novo Enquadramento", "Futuro Promissor", "Estrela"],
    ]

    for i, x in enumerate([0.17, 0.5, 0.83]):
        for j, y in enumerate([0.17, 0.5, 0.83]):
            fig.add_annotation(
                x=x,
                y=y,
                text=quadrant_labels[2 - j][i],
                showarrow=False,
                font=dict(size=10, color="gray"),
            )

    # Configurar layout
    fig.update_layout(
        title=title,
        xaxis=dict(title="Potencial", range=[-0.05, 1.05], showgrid=False),
        yaxis=dict(title="Desempenho", range=[-0.05, 1.05], showgrid=False),
        shapes=[
            # Adicionar bordas ao gráfico
            dict(
                type="rect",
                xref="paper",
                yref="paper",
                x0=0,
                y0=0,
                x1=1,
                y1=1,
                line=dict(color="black", width=1),
            )
        ],
    )

    return fig


def create_influence_network_visualization(
    network: nx.Graph,
    central_node_id: str,
    edge_metrics: Dict[Tuple[str, str], float] = None,
    title: str = "Rede de Influência",
) -> go.Figure:
    """
    Cria uma visualização interativa de rede de influência.

    Args:
        network: Grafo NetworkX representando a rede
        central_node_id: ID do nó central
        edge_metrics: Dicionário opcional com pesos das arestas
        title: Título do gráfico

    Returns:
        Figura Plotly
    """
    # Calcular layout de forma determinística
    pos = nx.spring_layout(network, seed=42)

    # Calcular tamanhos dos nós baseados em centralidade
    degree_centrality = nx.degree_centrality(network)
    node_sizes = {node: 10 + 50 * degree_centrality[node] for node in network.nodes()}
    node_sizes[central_node_id] = (
        node_sizes.get(central_node_id, 0) * 1.5
    )  # Aumentar nó central

    # Preparar dados para edges (arestas)
    edge_x = []
    edge_y = []
    edge_weights = []

    for edge in network.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

        # Pegar peso se disponível
        weight = 1
        if edge_metrics and (edge[0], edge[1]) in edge_metrics:
            weight = edge_metrics[(edge[0], edge[1])]
        elif edge_metrics and (edge[1], edge[0]) in edge_metrics:
            weight = edge_metrics[(edge[1], edge[0])]
        elif network.has_edge(*edge) and "weight" in network[edge[0]][edge[1]]:
            weight = network[edge[0]][edge[1]]["weight"]

        edge_weights.append(weight)
        edge_weights.append(weight)
        edge_weights.append(None)

    # Criar linhas (arestas)
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1, color="#888"),
        hoverinfo="none",
        mode="lines",
    )

    # Preparar dados para nós
    node_x = []
    node_y = []
    node_colors = []
    node_text = []
    node_size = []

    for node in network.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        # Definir cor (destaque para nó central)
        color = "royalblue"
        if node == central_node_id:
            color = "crimson"
        node_colors.append(color)

        # Definir tamanho
        node_size.append(node_sizes[node])

        # Definir texto do hover
        node_text.append(f"{node}<br>Centralidade: {degree_centrality[node]:.2f}")

    # Criar nós
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        hoverinfo="text",
        text=node_text,
        marker=dict(
            showscale=False,
            color=node_colors,
            size=node_size,
            line=dict(width=2, color="DarkSlateGrey"),
        ),
    )

    # Criar figura
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=title,
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )

    return fig


def create_skill_development_heatmap(
    skills_over_time: Dict[str, List[float]],
    time_labels: List[str],
    title: str = "Evolução de Competências",
) -> go.Figure:
    """
    Cria um heatmap da evolução de competências ao longo do tempo.

    Args:
        skills_over_time: Dicionário com nomes de skills e valores ao longo do tempo
        time_labels: Rótulos para os períodos de tempo
        title: Título do gráfico

    Returns:
        Figura Plotly
    """
    # Converter para matriz
    skills = list(skills_over_time.keys())
    values = list(skills_over_time.values())

    # Criar dataframe
    df = pd.DataFrame(values, columns=time_labels, index=skills)

    # Criar heatmap
    fig = px.imshow(
        df,
        labels=dict(x="Período", y="Competência", color="Nível"),
        x=time_labels,
        y=skills,
        color_continuous_scale="Viridis",
        aspect="auto",
    )

    fig.update_layout(title=title, xaxis_side="top", xaxis=dict(side="top"))

    # Adicionar anotações com valores
    for i, skill in enumerate(skills):
        for j, time in enumerate(time_labels):
            fig.add_annotation(
                x=j,
                y=i,
                text=f"{df.iloc[i, j]:.1f}",
                showarrow=False,
                font=dict(color="white" if df.iloc[i, j] > 0.5 else "black"),
            )

    return fig


def plot_metrics_comparison(
    ax: plt.Axes,
    person_metrics: Dict[str, float],
    team_metrics: Dict[str, float],
    metrics_labels: Dict[str, str] = None,
):
    """
    Plota uma comparação de métricas entre pessoa e equipe em um subplot matplotlib.

    Args:
        ax: Eixo matplotlib para plotar
        person_metrics: Métricas da pessoa
        team_metrics: Métricas da equipe
        metrics_labels: Rótulos para as métricas
    """
    if not metrics_labels:
        metrics_labels = {
            "performance": "Performance",
            "potential": "Potencial",
            "growth": "Crescimento",
            "influence": "Influência",
            "learning": "Aprendizado",
        }

    metrics = list(metrics_labels.keys())

    # Garantir que todas as métricas existam ou usar zero
    person_values = [person_metrics.get(m, 0) for m in metrics]
    team_values = [team_metrics.get(m, 0) for m in metrics]

    x = np.arange(len(metrics))
    width = 0.35

    ax.bar(x - width / 2, person_values, width, label="Pessoa", color="royalblue")
    ax.bar(x + width / 2, team_values, width, label="Equipe", color="lightcoral")

    ax.set_xticks(x)
    ax.set_xticklabels([metrics_labels[m] for m in metrics])
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.set_title("Comparação de Métricas")

    # Adicionar valores acima das barras
    for i, v in enumerate(person_values):
        ax.text(i - width / 2, v + 0.02, f"{v:.2f}", ha="center", fontsize=8)
    for i, v in enumerate(team_values):
        ax.text(i + width / 2, v + 0.02, f"{v:.2f}", ha="center", fontsize=8)


def plot_recommendations_box(
    ax: plt.Axes, recommendations: List[str], title: str = "Recomendações"
):
    """
    Plota uma caixa de texto com recomendações em um subplot matplotlib.

    Args:
        ax: Eixo matplotlib para plotar
        recommendations: Lista de recomendações
        title: Título da caixa
    """
    ax.axis("off")
    ax.set_title(title)

    text = "\n\n".join([f"{i + 1}. {rec}" for i, rec in enumerate(recommendations)])

    ax.text(
        0.5,
        0.5,
        text,
        ha="center",
        va="center",
        wrap=True,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8),
    )


def create_interactive_dashboard(
    person_summary: Dict[str, Any], team_metrics: Dict[str, Any] = None
) -> go.Figure:
    """
    Cria um dashboard interativo completo usando Plotly.

    Args:
        person_summary: Dados completos da pessoa
        team_metrics: Métricas da equipe para comparação

    Returns:
        Figura Plotly com dashboard completo
    """
    # Criar dashboard com 6 visualizações
    fig = make_subplots(
        rows=2,
        cols=3,
        specs=[
            [{"type": "polar"}, {"type": "xy"}, {"type": "xy"}],
            [{"type": "xy"}, {"type": "scene"}, {"type": "xy"}],
        ],
        subplot_titles=(
            "Radar de Competências",
            "Desempenho vs. Potencial",
            "Rede de Influência",
            "Tendências de Performance",
            "Simulação de Carreira",
            "Recomendações",
        ),
    )

    # 1. Radar de Competências
    if person_summary.get("key_skills"):
        skills = person_summary["key_skills"]
        categories = list(skills.keys())
        values = list(skills.values())

        # Fechar o polígono
        categories = categories + [categories[0]]
        values = values + [values[0]]

        fig.add_trace(
            go.Scatterpolar(r=values, theta=categories, fill="toself", name="Skills"),
            row=1,
            col=1,
        )

        fig.update_polars(radialaxis=dict(visible=True, range=[0, 1]))

    # 2. Desempenho vs. Potencial
    if "performance_score" in person_summary and "potential_score" in person_summary:
        # Adicionar pessoa
        fig.add_trace(
            go.Scatter(
                x=[person_summary["potential_score"]],
                y=[person_summary["performance_score"]],
                mode="markers+text",
                marker=dict(color="crimson", size=15, symbol="circle"),
                text=[person_summary.get("name", "Pessoa")],
                textposition="top center",
                name="Pessoa",
            ),
            row=1,
            col=2,
        )

        # Adicionar linhas divisórias da matriz 9-box
        for v in [0.33, 0.67]:
            fig.add_shape(
                type="line",
                line=dict(dash="dash", width=1, color="gray"),
                x0=v,
                y0=0,
                x1=v,
                y1=1,
                row=1,
                col=2,
            )
            fig.add_shape(
                type="line",
                line=dict(dash="dash", width=1, color="gray"),
                y0=v,
                x0=0,
                y1=v,
                x1=1,
                row=1,
                col=2,
            )

    # 3. Tendências de Performance
    if "trends" in person_summary:
        trends = person_summary["trends"]
        for metric, values in trends.items():
            if len(values) > 1:  # Só plotar se tiver pelo menos 2 pontos
                x = list(range(len(values)))
                fig.add_trace(
                    go.Scatter(x=x, y=values, mode="lines+markers", name=metric),
                    row=2,
                    col=1,
                )

                # Adicionar previsão se disponível
                if metric in person_summary.get("predictions", {}):
                    pred = person_summary["predictions"][metric]
                    fig.add_trace(
                        go.Scatter(
                            x=[len(values)],
                            y=[pred["value"]],
                            mode="markers",
                            marker=dict(symbol="star", size=12),
                            name=f"{metric} (previsão)",
                        ),
                        row=2,
                        col=1,
                    )

    # 4. Recomendações
    if "top_recommendations" in person_summary:
        recommendations = person_summary["top_recommendations"]
        rec_text = "<br><br>".join(
            [f"<b>{i + 1}.</b> {rec}" for i, rec in enumerate(recommendations)]
        )

        fig.add_trace(
            go.Scatter(
                x=[0.5],
                y=[0.5],
                mode="text",
                text=[rec_text],
                textposition="middle center",
                hoverinfo="none",
            ),
            row=2,
            col=3,
        )

    # Configurar layout geral
    fig.update_layout(
        height=800,
        title_text=f"Dashboard Holístico de {person_summary.get('name', 'Colaborador')}",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
    )

    return fig


def create_bar_chart(
    categories: List[str],
    values: List[float],
    title: str = "Gráfico de Barras",
    x_label: str = "Categorias",
    y_label: str = "Valores",
    color: str = "rgb(53, 135, 212)",
    compare_values: Optional[List[float]] = None,
    compare_label: Optional[str] = "Comparação",
    filename: Optional[str] = None,
) -> go.Figure:
    """
    Cria um gráfico de barras interativo usando Plotly.

    Args:
        categories: Lista de categorias para o eixo X
        values: Lista de valores para o eixo Y
        title: Título do gráfico
        x_label: Rótulo do eixo X
        y_label: Rótulo do eixo Y
        color: Cor das barras
        compare_values: Lista opcional de valores para comparação
        compare_label: Rótulo para os valores de comparação
        filename: Caminho para salvar o gráfico (opcional)

    Returns:
        Figura Plotly
    """
    fig = go.Figure()

    # Adicionar barras principais
    fig.add_trace(
        go.Bar(
            x=categories,
            y=values,
            name="Valores",
            marker_color=color,
        )
    )

    # Adicionar barras de comparação, se fornecidas
    if compare_values and len(compare_values) == len(categories):
        fig.add_trace(
            go.Bar(
                x=categories,
                y=compare_values,
                name=compare_label,
                marker_color="rgba(255, 102, 77, 0.7)",
            )
        )

    # Atualizar layout
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        barmode="group",
        xaxis=dict(tickangle=-45) if len(categories) > 5 else dict(),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # Salvar no arquivo, se o nome for fornecido
    if filename:
        fig.write_image(filename)
        fig.write_html(filename.replace(".png", ".html").replace(".jpg", ".html"))

    return fig


def create_heatmap(
    data: List[List[float]],
    x_labels: List[str],
    y_labels: List[str],
    title: str = "Mapa de Calor",
    colorscale: str = "Viridis",
    filename: Optional[str] = None,
) -> go.Figure:
    """
    Cria um mapa de calor interativo usando Plotly.

    Args:
        data: Matriz de dados para o mapa de calor
        x_labels: Rótulos para o eixo X
        y_labels: Rótulos para o eixo Y
        title: Título do gráfico
        colorscale: Escala de cores (ex: 'Viridis', 'Reds', 'Blues')
        filename: Caminho para salvar o gráfico (opcional)

    Returns:
        Figura Plotly
    """
    fig = go.Figure(
        data=go.Heatmap(
            z=data,
            x=x_labels,
            y=y_labels,
            colorscale=colorscale,
            hoverongaps=False,
        )
    )

    fig.update_layout(
        title=title,
        xaxis=dict(tickangle=-45) if len(x_labels) > 5 else dict(),
    )

    # Salvar no arquivo, se o nome for fornecido
    if filename:
        fig.write_image(filename)
        fig.write_html(filename.replace(".png", ".html").replace(".jpg", ".html"))

    return fig


def create_line_chart(
    x_data: List[Any],
    y_data: List[float],
    title: str = "Gráfico de Linha",
    x_label: str = "Eixo X",
    y_label: str = "Eixo Y",
    color: str = "rgb(53, 135, 212)",
    compare_data: Optional[List[Tuple[List[Any], List[float], str]]] = None,
    markers: bool = True,
    filename: Optional[str] = None,
) -> go.Figure:
    """
    Cria um gráfico de linha interativo usando Plotly.

    Args:
        x_data: Dados para o eixo X
        y_data: Dados para o eixo Y
        title: Título do gráfico
        x_label: Rótulo do eixo X
        y_label: Rótulo do eixo Y
        color: Cor da linha principal
        compare_data: Dados adicionais para comparação [(x_data, y_data, label), ...]
        markers: Se deve mostrar marcadores nos pontos
        filename: Caminho para salvar o gráfico (opcional)

    Returns:
        Figura Plotly
    """
    fig = go.Figure()

    # Linha principal
    mode = "lines+markers" if markers else "lines"
    fig.add_trace(
        go.Scatter(
            x=x_data,
            y=y_data,
            mode=mode,
            name="Principal",
            line=dict(color=color, width=3),
        )
    )

    # Linhas de comparação
    if compare_data:
        colors = px.colors.qualitative.Plotly
        for i, (x_comp, y_comp, label) in enumerate(compare_data):
            fig.add_trace(
                go.Scatter(
                    x=x_comp,
                    y=y_comp,
                    mode=mode,
                    name=label,
                    line=dict(color=colors[i % len(colors)], width=2, dash="dash"),
                )
            )

    # Atualizar layout
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # Salvar no arquivo, se o nome for fornecido
    if filename:
        fig.write_image(filename)
        fig.write_html(filename.replace(".png", ".html").replace(".jpg", ".html"))

    return fig


def create_network_graph(
    network: nx.Graph,
    title: str = "Grafo de Rede",
    central_node: Optional[str] = None,
    node_colors: Optional[Dict[str, str]] = None,
    node_sizes: Optional[Dict[str, float]] = None,
    filename: Optional[str] = None,
) -> go.Figure:
    """
    Cria uma visualização de rede interativa usando Plotly.

    Args:
        network: Grafo networkx
        title: Título do gráfico
        central_node: ID do nó central (opcional)
        node_colors: Dicionário de cores para os nós (opcional)
        node_sizes: Dicionário de tamanhos para os nós (opcional)
        filename: Caminho para salvar o gráfico (opcional)

    Returns:
        Figura Plotly
    """
    # Posição dos nós - layout spring
    pos = nx.spring_layout(network, seed=42)

    # Extrair posições
    x_pos = [pos[node][0] for node in network.nodes()]
    y_pos = [pos[node][1] for node in network.nodes()]

    # Cores e tamanhos padrão
    default_color = "rgb(53, 135, 212)"
    default_size = 15
    central_color = "rgb(255, 102, 77)"
    central_size = 25

    # Preparar cores e tamanhos dos nós
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []

    for node in network.nodes():
        node_x.append(pos[node][0])
        node_y.append(pos[node][1])
        node_text.append(str(node))

        # Definir cor do nó
        if node_colors and node in node_colors:
            node_color.append(node_colors[node])
        elif central_node and node == central_node:
            node_color.append(central_color)
        else:
            node_color.append(default_color)

        # Definir tamanho do nó
        if node_sizes and node in node_sizes:
            node_size.append(node_sizes[node])
        elif central_node and node == central_node:
            node_size.append(central_size)
        else:
            node_size.append(default_size)

    # Preparar arestas
    edge_x = []
    edge_y = []
    edge_width = []

    for edge in network.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

        # Espessura da aresta baseada no peso, se disponível
        weight = edge[2].get("weight", 1.0)
        edge_width.append(weight)

    # Média das espessuras das arestas para normalização
    if edge_width:
        avg_width = sum(edge_width) / len(edge_width)
        edge_width = [w / avg_width * 2 for w in edge_width]

    # Criar figura
    fig = go.Figure()

    # Adicionar arestas
    fig.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=1, color="rgba(150, 150, 150, 0.5)"),
            hoverinfo="none",
            mode="lines",
            showlegend=False,
        )
    )

    # Adicionar nós
    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers",
            hoverinfo="text",
            text=node_text,
            marker=dict(
                color=node_color,
                size=node_size,
                line=dict(width=1, color="rgba(50, 50, 50, 0.2)"),
            ),
            showlegend=False,
        )
    )

    # Atualizar layout
    fig.update_layout(
        title=title,
        showlegend=False,
        hovermode="closest",
        margin=dict(b=0, l=0, r=0, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )

    # Salvar no arquivo, se o nome for fornecido
    if filename:
        fig.write_image(filename)
        fig.write_html(filename.replace(".png", ".html").replace(".jpg", ".html"))

    return fig


def create_sankey_diagram(
    source_indices: List[int],
    target_indices: List[int],
    values: List[float],
    node_labels: List[str],
    title: str = "Diagrama de Sankey",
    colorscale: str = "Viridis",
    filename: Optional[str] = None,
) -> go.Figure:
    """
    Cria um diagrama de Sankey interativo usando Plotly.

    Args:
        source_indices: Índices dos nós de origem
        target_indices: Índices dos nós de destino
        values: Valores dos fluxos
        node_labels: Rótulos para os nós
        title: Título do gráfico
        colorscale: Escala de cores (ex: 'Viridis', 'Blues')
        filename: Caminho para salvar o gráfico (opcional)

    Returns:
        Figura Plotly
    """
    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=node_labels,
                    color="rgba(53, 135, 212, 0.8)",
                ),
                link=dict(
                    source=source_indices,
                    target=target_indices,
                    value=values,
                    color="rgba(150, 150, 150, 0.5)",
                ),
            )
        ]
    )

    fig.update_layout(title=title, font=dict(size=12))

    # Salvar no arquivo, se o nome for fornecido
    if filename:
        fig.write_image(filename)
        fig.write_html(filename.replace(".png", ".html").replace(".jpg", ".html"))

    return fig


def create_scatter_chart(
    x_data: List[float],
    y_data: List[float],
    title: str = "Gráfico de Dispersão",
    x_label: str = "Eixo X",
    y_label: str = "Eixo Y",
    color: str = "rgb(53, 135, 212)",
    hover_text: Optional[List[str]] = None,
    size: Optional[List[float]] = None,
    filename: Optional[str] = None,
) -> go.Figure:
    """
    Cria um gráfico de dispersão interativo usando Plotly.

    Args:
        x_data: Dados para o eixo X
        y_data: Dados para o eixo Y
        title: Título do gráfico
        x_label: Rótulo do eixo X
        y_label: Rótulo do eixo Y
        color: Cor dos pontos
        hover_text: Textos para mostrar ao passar o mouse sobre os pontos
        size: Tamanhos dos pontos
        filename: Caminho para salvar o gráfico (opcional)

    Returns:
        Figura Plotly
    """
    fig = go.Figure()

    # Configurar marcador
    marker = dict(color=color)
    if size:
        marker["size"] = size

    # Adicionar trace
    fig.add_trace(
        go.Scatter(
            x=x_data,
            y=y_data,
            mode="markers",
            marker=marker,
            hovertext=hover_text,
            hoverinfo="text" if hover_text else "x+y",
        )
    )

    # Atualizar layout
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
    )

    # Salvar no arquivo, se o nome for fornecido
    if filename:
        fig.write_image(filename)
        fig.write_html(filename.replace(".png", ".html").replace(".jpg", ".html"))

    return fig
