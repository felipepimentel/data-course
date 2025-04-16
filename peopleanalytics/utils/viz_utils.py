"""
Visualization utilities for People Analytics.

This module provides functions for creating visualizations, charts, and reports
from people analytics data.
"""

import base64
import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from peopleanalytics.utils.logging_utils import get_module_logger

logger = get_module_logger(__name__)

# Set default style for visualizations
plt.style.use("seaborn-v0_8-whitegrid")

# Default colors
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "danger": "#d62728",
    "warning": "#bcbd22",
    "info": "#17becf",
    "gray": "#7f7f7f",
    "purple": "#9467bd",
    "pink": "#e377c2",
    "brown": "#8c564b",
}

# Default figure size
DEFAULT_FIG_SIZE = (10, 6)


def set_visualization_style(style: str = "seaborn-v0_8-whitegrid") -> None:
    """
    Set the global visualization style.

    Args:
        style: The style name from matplotlib styles
    """
    plt.style.use(style)
    logger.info(f"Visualization style set to: {style}")


def figure_to_base64(fig: Figure, format: str = "png", dpi: int = 100) -> str:
    """
    Convert a matplotlib figure to a base64-encoded string.

    Args:
        fig: The matplotlib figure
        format: The image format (png, jpg, svg, etc.)
        dpi: Resolution in dots per inch

    Returns:
        str: Base64-encoded image string
    """
    buf = io.BytesIO()
    fig.savefig(buf, format=format, dpi=dpi, bbox_inches="tight")
    buf.seek(0)

    image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/{format};base64,{image_base64}"


def save_figure(
    fig: Figure,
    file_path: Union[str, Path],
    format: Optional[str] = None,
    dpi: int = 300,
) -> Path:
    """
    Save a matplotlib figure to a file.

    Args:
        fig: The matplotlib figure
        file_path: Path to save the figure
        format: Image format (inferred from file extension if None)
        dpi: Resolution in dots per inch

    Returns:
        Path: Path to the saved file
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    format = format or path.suffix.lstrip(".")
    fig.savefig(path, format=format, dpi=dpi, bbox_inches="tight")

    logger.debug(f"Figure saved to: {path}")
    return path


def create_radar_chart(
    categories: List[str],
    values: List[float],
    title: str = "",
    max_value: float = 5.0,
    colors: Optional[Dict[str, str]] = None,
    figsize: Tuple[int, int] = (8, 8),
) -> Figure:
    """
    Create a radar chart (spider plot) from categories and values.

    Args:
        categories: List of category names
        values: List of values (same length as categories)
        title: Chart title
        max_value: Maximum value for the chart scale
        colors: Dict with custom colors ('fill', 'line', 'marker')
        figsize: Figure size as (width, height)

    Returns:
        Figure: Matplotlib figure object
    """
    if len(categories) < 3:
        raise ValueError("Radar chart requires at least 3 categories")

    if len(categories) != len(values):
        raise ValueError("Categories and values must be the same length")

    # Default colors
    default_colors = {
        "fill": COLORS["primary"] + "40",  # with alpha
        "line": COLORS["primary"],
        "marker": COLORS["secondary"],
    }

    # Update with custom colors if provided
    if colors:
        default_colors.update(colors)

    # Repeat first value to close the loop
    values_closed = np.append(values, values[0])
    categories_closed = np.append(categories, categories[0])

    # Calculate angles for each category
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]  # Close the loop

    # Create figure
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))

    # Draw chart elements
    ax.fill(angles, values_closed, color=default_colors["fill"], alpha=0.25)
    ax.plot(angles, values_closed, color=default_colors["line"], linewidth=2)
    ax.scatter(angles, values_closed, color=default_colors["marker"], s=80)

    # Set category labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories_closed[:-1], fontsize=12)

    # Set y-axis limits
    ax.set_ylim(0, max_value)

    # Set title
    if title:
        ax.set_title(title, fontsize=14, pad=20)

    # Remove y-axis tick labels but keep grid
    ax.set_yticklabels([])

    # Customize grid
    ax.grid(True, linestyle="--", alpha=0.7)

    plt.tight_layout()
    return fig


def create_heatmap(
    data: Union[pd.DataFrame, np.ndarray],
    title: str = "",
    x_labels: Optional[List[str]] = None,
    y_labels: Optional[List[str]] = None,
    cmap: str = "YlGnBu",
    annot: bool = True,
    figsize: Optional[Tuple[int, int]] = None,
) -> Figure:
    """
    Create a heatmap from a DataFrame or array.

    Args:
        data: DataFrame or 2D array of values
        title: Chart title
        x_labels: Custom x-axis labels
        y_labels: Custom y-axis labels
        cmap: Colormap name
        annot: Whether to annotate cells with values
        figsize: Figure size as (width, height)

    Returns:
        Figure: Matplotlib figure object
    """
    # Convert arrays to DataFrame for easier handling
    if isinstance(data, np.ndarray):
        data = pd.DataFrame(
            data,
            index=y_labels or [f"Row {i + 1}" for i in range(data.shape[0])],
            columns=x_labels or [f"Col {i + 1}" for i in range(data.shape[1])],
        )

    # Set figure size based on data dimensions
    if figsize is None:
        width = max(8, data.shape[1] * 1.2)
        height = max(6, data.shape[0] * 0.8)
        figsize = (width, height)

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Create heatmap
    sns.heatmap(
        data,
        annot=annot,
        fmt=".2f" if data.dtypes.iloc[0] == "float64" else "g",
        cmap=cmap,
        ax=ax,
        linewidths=0.5,
    )

    # Set title
    if title:
        ax.set_title(title, fontsize=14, pad=20)

    # Rotate x labels if there are many columns
    if data.shape[1] > 6:
        plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    return fig


def create_bar_chart(
    data: Union[pd.Series, Dict[str, float], List[Tuple[str, float]]],
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    color: str = COLORS["primary"],
    horizontal: bool = False,
    sort_values: bool = False,
    figsize: Optional[Tuple[int, int]] = None,
) -> Figure:
    """
    Create a bar chart from various data formats.

    Args:
        data: Data for the bar chart (Series, Dict, or List of tuples)
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        color: Bar color
        horizontal: If True, create horizontal bar chart
        sort_values: If True, sort bars by value
        figsize: Figure size as (width, height)

    Returns:
        Figure: Matplotlib figure object
    """
    # Convert data to Series if needed
    if isinstance(data, dict):
        data = pd.Series(data)
    elif isinstance(data, list):
        if all(isinstance(item, tuple) and len(item) == 2 for item in data):
            data = pd.Series({item[0]: item[1] for item in data})
        else:
            raise ValueError("List must contain (label, value) tuples")

    # Sort if requested
    if sort_values:
        data = data.sort_values(ascending=horizontal)

    # Determine figure size based on number of bars
    if figsize is None:
        if horizontal:
            height = max(6, len(data) * 0.4)
            figsize = (10, height)
        else:
            width = max(8, len(data) * 0.6)
            figsize = (width, 6)

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Create bar chart
    if horizontal:
        data.plot(kind="barh", color=color, ax=ax)
    else:
        data.plot(kind="bar", color=color, ax=ax)

    # Set labels and title
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12)
    if title:
        ax.set_title(title, fontsize=14)

    # Customize grid
    ax.grid(axis="x" if horizontal else "y", linestyle="--", alpha=0.7)

    # Format axis labels
    if horizontal:
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
    else:
        plt.xticks(rotation=45, ha="right", fontsize=10)
        plt.yticks(fontsize=10)

    plt.tight_layout()
    return fig


def create_line_chart(
    data: Union[pd.DataFrame, Dict[str, List[float]]],
    x_values: Optional[List[Any]] = None,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    colors: Optional[List[str]] = None,
    markers: bool = True,
    figsize: Tuple[int, int] = DEFAULT_FIG_SIZE,
) -> Figure:
    """
    Create a line chart from DataFrame or dictionary.

    Args:
        data: DataFrame or Dict with series names as keys and values as lists
        x_values: X-axis values (if None, uses indexes/positions)
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        colors: List of colors for each line
        markers: Whether to show markers
        figsize: Figure size as (width, height)

    Returns:
        Figure: Matplotlib figure object
    """
    # Convert dictionary to DataFrame if needed
    if isinstance(data, dict):
        if x_values is not None:
            data = pd.DataFrame(data, index=x_values)
        else:
            data = pd.DataFrame(data)

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Get default colors if not provided
    if colors is None:
        colors = list(COLORS.values())[: len(data.columns)]
        # Cycle colors if needed
        if len(data.columns) > len(colors):
            colors = colors * (len(data.columns) // len(colors) + 1)

    # Plot each series
    marker = "o" if markers else None
    for i, column in enumerate(data.columns):
        ax.plot(
            data.index if x_values is None else x_values,
            data[column],
            label=column,
            color=colors[i % len(colors)],
            marker=marker,
            markersize=5,
        )

    # Set labels and title
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12)
    if title:
        ax.set_title(title, fontsize=14)

    # Add legend
    if len(data.columns) > 1:
        ax.legend(fontsize=10)

    # Add grid
    ax.grid(True, linestyle="--", alpha=0.7)

    # Format x ticks if there are many points
    if len(data) > 6:
        plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    return fig


def create_pie_chart(
    data: Union[pd.Series, Dict[str, float], List[Tuple[str, float]]],
    title: str = "",
    colors: Optional[List[str]] = None,
    explode: Optional[List[float]] = None,
    autopct: str = "%1.1f%%",
    figsize: Tuple[int, int] = (8, 8),
) -> Figure:
    """
    Create a pie chart from various data formats.

    Args:
        data: Data for the pie chart (Series, Dict, or List of tuples)
        title: Chart title
        colors: List of colors for pie slices
        explode: List of values to "explode" slices (offset from center)
        autopct: Format for showing percentages on slices
        figsize: Figure size as (width, height)

    Returns:
        Figure: Matplotlib figure object
    """
    # Convert data to Series if needed
    if isinstance(data, dict):
        data = pd.Series(data)
    elif isinstance(data, list):
        if all(isinstance(item, tuple) and len(item) == 2 for item in data):
            data = pd.Series({item[0]: item[1] for item in data})
        else:
            raise ValueError("List must contain (label, value) tuples")

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        data.values,
        labels=data.index,
        autopct=autopct,
        explode=explode,
        colors=colors,
        shadow=False,
        startangle=90,
        textprops={"fontsize": 10},
    )

    # Enhance text readability
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_weight("bold")
        autotext.set_color("white")

    # Set title
    if title:
        ax.set_title(title, fontsize=14, pad=20)

    # Equal aspect ratio ensures pie is drawn as a circle
    ax.axis("equal")

    plt.tight_layout()
    return fig


def create_correlation_matrix(
    data: pd.DataFrame,
    title: str = "Correlation Matrix",
    method: str = "pearson",
    figsize: Optional[Tuple[int, int]] = None,
) -> Figure:
    """
    Create a correlation matrix heatmap.

    Args:
        data: DataFrame of numerical variables
        title: Chart title
        method: Correlation method ('pearson', 'kendall', 'spearman')
        figsize: Figure size as (width, height)

    Returns:
        Figure: Matplotlib figure object
    """
    # Calculate correlation matrix
    corr_matrix = data.corr(method=method)

    # Set figure size based on data dimensions
    if figsize is None:
        size = max(8, len(corr_matrix) * 0.8)
        figsize = (size, size)

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Create heatmap
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    cmap = sns.diverging_palette(240, 10, as_cmap=True)

    sns.heatmap(
        corr_matrix,
        mask=mask,
        cmap=cmap,
        vmax=1,
        vmin=-1,
        center=0,
        square=True,
        linewidths=0.5,
        annot=True,
        fmt=".2f",
        ax=ax,
    )

    # Set title
    if title:
        ax.set_title(title, fontsize=14, pad=20)

    plt.tight_layout()
    return fig


def create_scatter_plot(
    x: Union[List[float], np.ndarray, pd.Series],
    y: Union[List[float], np.ndarray, pd.Series],
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    color: str = COLORS["primary"],
    size: int = 50,
    alpha: float = 0.7,
    add_trend: bool = True,
    labels: Optional[List[str]] = None,
    figsize: Tuple[int, int] = DEFAULT_FIG_SIZE,
) -> Figure:
    """
    Create a scatter plot with optional trend line.

    Args:
        x: X values
        y: Y values
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        color: Point color
        size: Point size
        alpha: Point transparency
        add_trend: Add trend line
        labels: Point labels (for tooltips)
        figsize: Figure size as (width, height)

    Returns:
        Figure: Matplotlib figure object
    """
    # Convert inputs to numpy arrays
    x_arr = np.array(x)
    y_arr = np.array(y)

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Create scatter plot
    scatter = ax.scatter(x_arr, y_arr, c=color, s=size, alpha=alpha)

    # Add trend line if requested
    if add_trend and len(x_arr) > 1:
        # Calculate trend line
        z = np.polyfit(x_arr, y_arr, 1)
        p = np.poly1d(z)

        # Add trend line to plot
        x_trend = np.linspace(min(x_arr), max(x_arr), 100)
        y_trend = p(x_trend)
        ax.plot(x_trend, y_trend, "--", color="gray")

        # Add correlation coefficient
        corr = np.corrcoef(x_arr, y_arr)[0, 1]
        equation = f"y = {z[0]:.2f}x + {z[1]:.2f}"
        ax.text(
            0.05,
            0.95,
            f"{equation}\nr = {corr:.2f}",
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.7),
        )

    # Set labels and title
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12)
    if title:
        ax.set_title(title, fontsize=14)

    # Add grid
    ax.grid(True, linestyle="--", alpha=0.7)

    # Add labels as annotations if provided
    if labels is not None:
        # Add interactive hover labels
        # Use only a subset of labels if there are many points
        if len(labels) > 30:
            annot_idx = np.linspace(0, len(labels) - 1, 30, dtype=int)
            for i in annot_idx:
                ax.annotate(
                    labels[i],
                    (x_arr[i], y_arr[i]),
                    xytext=(5, 5),
                    textcoords="offset points",
                    fontsize=8,
                    alpha=0.7,
                )
        else:
            for i, label in enumerate(labels):
                ax.annotate(
                    label,
                    (x_arr[i], y_arr[i]),
                    xytext=(5, 5),
                    textcoords="offset points",
                    fontsize=8,
                    alpha=0.7,
                )

    plt.tight_layout()
    return fig


def create_dashboard(
    charts: List[Dict[str, Any]],
    title: str = "Analytics Dashboard",
    output_path: Union[str, Path] = None,
    template: str = "default",
) -> str:
    """
    Create an HTML dashboard with multiple charts.

    Args:
        charts: List of chart configurations, each should have:
            - figure: Matplotlib figure
            - title: Chart title
            - description: Optional description
            - width: Optional width percentage
        title: Dashboard title
        output_path: Path to save the dashboard HTML
        template: Dashboard template to use

    Returns:
        str: HTML content of the dashboard
    """
    # Ensure each chart has required attributes
    for i, chart in enumerate(charts):
        if "figure" not in chart:
            raise ValueError(f"Chart {i} is missing 'figure' attribute")
        if "title" not in chart:
            chart["title"] = f"Chart {i + 1}"
        if "description" not in chart:
            chart["description"] = ""
        if "width" not in chart:
            chart["width"] = 100  # Full width by default

    # Convert charts to base64 images
    for chart in charts:
        chart["image"] = figure_to_base64(chart["figure"])

    # Create HTML content
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .dashboard-title {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .dashboard-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: center;
        }}
        .chart-container {{
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 15px;
            margin-bottom: 20px;
        }}
        .chart-title {{
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .chart-description {{
            font-size: 14px;
            color: #666;
            margin-bottom: 15px;
        }}
        .chart-image {{
            width: 100%;
            height: auto;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            font-size: 12px;
            color: #999;
        }}
    </style>
</head>
<body>
    <h1 class="dashboard-title">{title}</h1>
    
    <div class="dashboard-container">
"""

    # Add charts to HTML
    for chart in charts:
        width_style = f"width: {chart['width']}%;" if chart["width"] < 100 else ""
        html += f"""
        <div class="chart-container" style="{width_style}">
            <div class="chart-title">{chart["title"]}</div>
            <div class="chart-description">{chart["description"]}</div>
            <img class="chart-image" src="{chart["image"]}" alt="{chart["title"]}">
        </div>
"""

    # Add footer and close HTML
    html += f"""
    </div>
    
    <div class="footer">
        Generated on {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}
    </div>
</body>
</html>
"""

    # Save to file if path provided
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"Dashboard saved to: {path}")

    return html
