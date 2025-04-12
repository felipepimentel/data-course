"""
Componentes de Visualização para o Dashboard Holístico.

Este módulo fornece componentes de visualização especializados para
o dashboard holístico de desenvolvimento de talentos.
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
from matplotlib.figure import Figure


def create_radar_chart(skills: Dict[str, float], 
                       title: str = "Radar de Competências") -> go.Figure:
    """
    Cria um gráfico radar de competências interativo usando Plotly.
    
    Args:
        skills: Dicionário com nomes de habilidades e seus valores
        title: Título do gráfico
        
    Returns:
        Figura Plotly
    """
    categories = list(skills.keys())
    values = list(skills.values())
    
    # Adicionar o primeiro valor novamente para fechar o círculo
    categories = categories + [categories[0]]
    values = values + [values[0]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Skills',
        line_color='royalblue',
        fillcolor='rgba(65, 105, 225, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        title=title,
        showlegend=False
    )
    
    return fig


def create_3d_career_path(paths: List[Dict[str, Any]], 
                         dimensions: Tuple[str, str, str] = ('skill_level', 'impact', 'time'),
                         title: str = "Trajetória de Carreira 3D") -> go.Figure:
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
        x = [point.get(dimensions[0], 0) for point in path['points']]
        y = [point.get(dimensions[1], 0) for point in path['points']]
        z = [point.get(dimensions[2], 0) for point in path['points']]
        
        # Adicionar trajetória
        fig.add_trace(go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode='lines+markers',
            marker=dict(size=5, color=colors[i % len(colors)]),
            line=dict(color=colors[i % len(colors)], width=3),
            name=f"Caminho {i+1} (Score: {path.get('score', 0):.2f})"
        ))
        
        # Adicionar anotações para as posições
        for j, point in enumerate(path['points']):
            if 'title' in point:
                fig.add_trace(go.Scatter3d(
                    x=[x[j]],
                    y=[y[j]],
                    z=[z[j]],
                    mode='markers+text',
                    marker=dict(size=8, color=colors[i % len(colors)]),
                    text=[point['title']],
                    name=point['title'],
                    showlegend=False
                ))
    
    # Configurar layout
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title=dimensions[0].replace('_', ' ').title(),
            yaxis_title=dimensions[1].replace('_', ' ').title(),
            zaxis_title=dimensions[2].replace('_', ' ').title(),
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        legend=dict(x=0, y=1)
    )
    
    return fig


def create_performance_vs_potential_matrix(people: List[Dict[str, Any]],
                                          highlight_person_id: Optional[str] = None,
                                          show_names: bool = True,
                                          title: str = "Matriz Desempenho vs. Potencial") -> go.Figure:
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
    names = [p.get('name', f"Pessoa {i}") for i, p in enumerate(people)]
    potentials = [p.get('potential_score', 0) for p in people]
    performances = [p.get('performance_score', 0) for p in people]
    person_ids = [p.get('person_id', f"id_{i}") for i, p in enumerate(people)]
    
    # Definir cores - destacar pessoa selecionada
    colors = ['royalblue'] * len(people)
    sizes = [30] * len(people)
    
    if highlight_person_id:
        for i, pid in enumerate(person_ids):
            if pid == highlight_person_id:
                colors[i] = 'crimson'
                sizes[i] = 45
    
    # Criar scatter plot
    fig.add_trace(go.Scatter(
        x=potentials,
        y=performances,
        mode='markers+text' if show_names else 'markers',
        marker=dict(
            color=colors,
            size=sizes,
            line=dict(width=2, color='DarkSlateGrey')
        ),
        text=names if show_names else None,
        textposition="top center",
        name='Colaboradores',
        hovertemplate=
        '<b>%{text}</b><br>' +
        'Potencial: %{x:.2f}<br>' +
        'Desempenho: %{y:.2f}<br>'
    ))
    
    # Adicionar linhas divisórias
    for v in [0.33, 0.67]:
        fig.add_shape(
            type="line", line=dict(dash="dash", width=1, color="gray"),
            x0=v, y0=0, x1=v, y1=1
        )
        fig.add_shape(
            type="line", line=dict(dash="dash", width=1, color="gray"),
            y0=v, x0=0, y1=v, x1=1
        )
    
    # Adicionar rótulos dos quadrantes
    quadrant_labels = [
        ['Performer em Risco', 'Performer Sólido', 'Performer Forte'],
        ['Enigma', 'Core', 'Alta Performance'],
        ['Novo Enquadramento', 'Futuro Promissor', 'Estrela']
    ]
    
    for i, x in enumerate([0.17, 0.5, 0.83]):
        for j, y in enumerate([0.17, 0.5, 0.83]):
            fig.add_annotation(
                x=x, y=y,
                text=quadrant_labels[2-j][i],
                showarrow=False,
                font=dict(size=10, color="gray")
            )
    
    # Configurar layout
    fig.update_layout(
        title=title,
        xaxis=dict(
            title="Potencial",
            range=[-0.05, 1.05],
            showgrid=False
        ),
        yaxis=dict(
            title="Desempenho",
            range=[-0.05, 1.05],
            showgrid=False
        ),
        shapes=[
            # Adicionar bordas ao gráfico
            dict(type="rect", xref="paper", yref="paper",
                 x0=0, y0=0, x1=1, y1=1,
                 line=dict(color="black", width=1))
        ]
    )
    
    return fig


def create_influence_network_visualization(network: nx.Graph,
                                         central_node_id: str,
                                         edge_metrics: Dict[Tuple[str, str], float] = None,
                                         title: str = "Rede de Influência") -> go.Figure:
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
    node_sizes[central_node_id] = node_sizes.get(central_node_id, 0) * 1.5  # Aumentar nó central
    
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
        elif network.has_edge(*edge) and 'weight' in network[edge[0]][edge[1]]:
            weight = network[edge[0]][edge[1]]['weight']
            
        edge_weights.append(weight)
        edge_weights.append(weight)
        edge_weights.append(None)
    
    # Criar linhas (arestas)
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines'
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
        color = 'royalblue'
        if node == central_node_id:
            color = 'crimson'
        node_colors.append(color)
        
        # Definir tamanho
        node_size.append(node_sizes[node])
        
        # Definir texto do hover
        node_text.append(f"{node}<br>Centralidade: {degree_centrality[node]:.2f}")
    
    # Criar nós
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            showscale=False,
            color=node_colors,
            size=node_size,
            line=dict(width=2, color='DarkSlateGrey')
        )
    )
    
    # Criar figura
    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                     title=title,
                     showlegend=False,
                     hovermode='closest',
                     margin=dict(b=20, l=5, r=5, t=40),
                     xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                     yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                 ))
    
    return fig


def create_skill_development_heatmap(skills_over_time: Dict[str, List[float]],
                                   time_labels: List[str],
                                   title: str = "Evolução de Competências") -> go.Figure:
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
    fig = px.imshow(df,
                 labels=dict(x="Período", y="Competência", color="Nível"),
                 x=time_labels,
                 y=skills,
                 color_continuous_scale='Viridis',
                 aspect="auto")
    
    fig.update_layout(
        title=title,
        xaxis_side="top",
        xaxis=dict(side="top")
    )
    
    # Adicionar anotações com valores
    for i, skill in enumerate(skills):
        for j, time in enumerate(time_labels):
            fig.add_annotation(
                x=j,
                y=i,
                text=f"{df.iloc[i, j]:.1f}",
                showarrow=False,
                font=dict(color="white" if df.iloc[i, j] > 0.5 else "black")
            )
    
    return fig


def plot_metrics_comparison(ax: plt.Axes, 
                          person_metrics: Dict[str, float],
                          team_metrics: Dict[str, float],
                          metrics_labels: Dict[str, str] = None):
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
            'performance': 'Performance',
            'potential': 'Potencial',
            'growth': 'Crescimento',
            'influence': 'Influência',
            'learning': 'Aprendizado'
        }
    
    metrics = list(metrics_labels.keys())
    
    # Garantir que todas as métricas existam ou usar zero
    person_values = [person_metrics.get(m, 0) for m in metrics]
    team_values = [team_metrics.get(m, 0) for m in metrics]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    ax.bar(x - width/2, person_values, width, label='Pessoa', color='royalblue')
    ax.bar(x + width/2, team_values, width, label='Equipe', color='lightcoral')
    
    ax.set_xticks(x)
    ax.set_xticklabels([metrics_labels[m] for m in metrics])
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.set_title("Comparação de Métricas")
    
    # Adicionar valores acima das barras
    for i, v in enumerate(person_values):
        ax.text(i - width/2, v + 0.02, f"{v:.2f}", ha='center', fontsize=8)
    for i, v in enumerate(team_values):
        ax.text(i + width/2, v + 0.02, f"{v:.2f}", ha='center', fontsize=8)


def plot_recommendations_box(ax: plt.Axes, recommendations: List[str], title: str = "Recomendações"):
    """
    Plota uma caixa de texto com recomendações em um subplot matplotlib.
    
    Args:
        ax: Eixo matplotlib para plotar
        recommendations: Lista de recomendações
        title: Título da caixa
    """
    ax.axis('off')
    ax.set_title(title)
    
    text = "\n\n".join([f"{i+1}. {rec}" for i, rec in enumerate(recommendations)])
    
    ax.text(0.5, 0.5, text, ha='center', va='center', wrap=True,
          bbox=dict(boxstyle="round,pad=0.5", facecolor='lightyellow', alpha=0.8))


def create_interactive_dashboard(person_summary: Dict[str, Any], 
                               team_metrics: Dict[str, Any] = None) -> go.Figure:
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
        rows=2, cols=3,
        specs=[
            [{"type": "polar"}, {"type": "xy"}, {"type": "xy"}],
            [{"type": "xy"}, {"type": "scene"}, {"type": "xy"}]
        ],
        subplot_titles=(
            "Radar de Competências", 
            "Desempenho vs. Potencial", 
            "Rede de Influência",
            "Tendências de Performance",
            "Simulação de Carreira", 
            "Recomendações"
        )
    )
    
    # 1. Radar de Competências
    if person_summary.get('key_skills'):
        skills = person_summary['key_skills']
        categories = list(skills.keys())
        values = list(skills.values())
        
        # Fechar o polígono
        categories = categories + [categories[0]]
        values = values + [values[0]]
        
        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Skills'
            ),
            row=1, col=1
        )
        
        fig.update_polars(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        )
    
    # 2. Desempenho vs. Potencial
    if 'performance_score' in person_summary and 'potential_score' in person_summary:
        # Adicionar pessoa
        fig.add_trace(
            go.Scatter(
                x=[person_summary['potential_score']],
                y=[person_summary['performance_score']],
                mode='markers+text',
                marker=dict(
                    color='crimson',
                    size=15,
                    symbol='circle'
                ),
                text=[person_summary.get('name', 'Pessoa')],
                textposition="top center",
                name='Pessoa'
            ),
            row=1, col=2
        )
        
        # Adicionar linhas divisórias da matriz 9-box
        for v in [0.33, 0.67]:
            fig.add_shape(
                type="line", line=dict(dash="dash", width=1, color="gray"),
                x0=v, y0=0, x1=v, y1=1,
                row=1, col=2
            )
            fig.add_shape(
                type="line", line=dict(dash="dash", width=1, color="gray"),
                y0=v, x0=0, y1=v, x1=1,
                row=1, col=2
            )
    
    # 3. Tendências de Performance
    if 'trends' in person_summary:
        trends = person_summary['trends']
        for metric, values in trends.items():
            if len(values) > 1:  # Só plotar se tiver pelo menos 2 pontos
                x = list(range(len(values)))
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=values,
                        mode='lines+markers',
                        name=metric
                    ),
                    row=2, col=1
                )
                
                # Adicionar previsão se disponível
                if metric in person_summary.get('predictions', {}):
                    pred = person_summary['predictions'][metric]
                    fig.add_trace(
                        go.Scatter(
                            x=[len(values)],
                            y=[pred['value']],
                            mode='markers',
                            marker=dict(symbol='star', size=12),
                            name=f"{metric} (previsão)"
                        ),
                        row=2, col=1
                    )
    
    # 4. Recomendações
    if 'top_recommendations' in person_summary:
        recommendations = person_summary['top_recommendations']
        rec_text = "<br><br>".join([f"<b>{i+1}.</b> {rec}" for i, rec in enumerate(recommendations)])
        
        fig.add_trace(
            go.Scatter(
                x=[0.5],
                y=[0.5],
                mode='text',
                text=[rec_text],
                textposition='middle center',
                hoverinfo='none'
            ),
            row=2, col=3
        )
    
    # Configurar layout geral
    fig.update_layout(
        height=800,
        title_text=f"Dashboard Holístico de {person_summary.get('name', 'Colaborador')}",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig 