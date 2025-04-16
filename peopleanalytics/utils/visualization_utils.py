"""
Visualization utilities for People Analytics.

This module provides functions for generating charts, graphs,
and visual reports from people analytics data.
"""

import base64
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure


def set_plot_style(
    style: str = "whitegrid", context: str = "notebook", palette: str = "deep"
):
    """
    Set the global plot style for visualizations.

    Args:
        style: Seaborn style
        context: Seaborn context
        palette: Color palette
    """
    sns.set_theme(style=style, context=context, palette=palette)
    plt.rcParams["figure.figsize"] = (10, 6)
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10


def create_radar_chart(
    categories: List[str],
    values: List[float],
    title: str = "Radar Chart",
    fill: bool = True,
    color: Optional[str] = None,
    max_value: Optional[float] = None,
    comparison_values: Optional[List[float]] = None,
    comparison_label: Optional[str] = None,
    fig_size: Tuple[int, int] = (10, 10),
) -> Figure:
    """
    Create a radar chart.

    Args:
        categories: List of category names
        values: List of values corresponding to categories
        title: Chart title
        fill: Whether to fill the radar chart
        color: Color of the main radar plot
        max_value: Maximum value for the radar chart (default: auto)
        comparison_values: Optional secondary dataset for comparison
        comparison_label: Label for the comparison dataset
        fig_size: Figure size (width, height) in inches

    Returns:
        Figure: Matplotlib figure
    """
    # Ensure we have the same number of categories and values
    if len(categories) != len(values):
        raise ValueError("Number of categories must match number of values")

    # Set up the radar chart
    num_vars = len(categories)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # Close the polygon by repeating the first value
    values = values.copy()
    values.append(values[0])
    angles.append(angles[0])
    categories.append(categories[0])

    if comparison_values is not None:
        if len(categories) - 1 != len(comparison_values):
            raise ValueError(
                "Number of categories must match number of comparison values"
            )
        comparison_values = comparison_values.copy()
        comparison_values.append(comparison_values[0])

    # Create figure and polar axis
    fig, ax = plt.subplots(figsize=fig_size, subplot_kw={"projection": "polar"})

    # Set the maximum value for the radar chart
    if max_value is None:
        if comparison_values:
            max_value = max(max(values), max(comparison_values)) * 1.1
        else:
            max_value = max(values) * 1.1

    # Plot the radar chart
    ax.plot(angles, values, "o-", linewidth=2, label="Individual")
    if fill:
        ax.fill(angles, values, alpha=0.25, color=color or "b")

    # Add comparison dataset if provided
    if comparison_values:
        ax.plot(
            angles,
            comparison_values,
            "o-",
            linewidth=2,
            label=comparison_label or "Comparison",
        )
        if fill:
            ax.fill(angles, comparison_values, alpha=0.1, color="r")

    # Set category labels
    ax.set_thetagrids(np.degrees(angles), categories)

    # Set y-axis limits and labels
    ax.set_ylim(0, max_value)
    ax.set_title(title, fontsize=15, pad=20)

    # Add legend if comparison data provided
    if comparison_values:
        ax.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))

    plt.tight_layout()

    return fig


def create_bar_chart(
    categories: List[str],
    values: List[float],
    title: str = "Bar Chart",
    xlabel: str = "Categories",
    ylabel: str = "Values",
    color: Optional[str] = None,
    horizontal: bool = False,
    comparison_values: Optional[List[float]] = None,
    comparison_label: Optional[str] = None,
    fig_size: Tuple[int, int] = (10, 6),
) -> Figure:
    """
    Create a bar chart.

    Args:
        categories: List of category names
        values: List of values corresponding to categories
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        color: Color of the bars
        horizontal: Whether to create a horizontal bar chart
        comparison_values: Optional secondary dataset for comparison
        comparison_label: Label for the comparison dataset
        fig_size: Figure size (width, height) in inches

    Returns:
        Figure: Matplotlib figure
    """
    # Create figure
    fig, ax = plt.subplots(figsize=fig_size)

    x = np.arange(len(categories))
    width = 0.35

    if horizontal:
        if comparison_values is not None:
            ax.barh(
                x - width / 2, values, width, label="Individual", color=color or "b"
            )
            ax.barh(
                x + width / 2,
                comparison_values,
                width,
                label=comparison_label or "Comparison",
                color="r",
            )
        else:
            ax.barh(x, values, color=color or "b")

        ax.set_yticks(x)
        ax.set_yticklabels(categories)
        ax.set_xlabel(ylabel)
        ax.set_ylabel(xlabel)
    else:
        if comparison_values is not None:
            ax.bar(x - width / 2, values, width, label="Individual", color=color or "b")
            ax.bar(
                x + width / 2,
                comparison_values,
                width,
                label=comparison_label or "Comparison",
                color="r",
            )
        else:
            ax.bar(x, values, color=color or "b")

        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

    ax.set_title(title)

    if comparison_values is not None:
        ax.legend()

    plt.tight_layout()

    return fig


def create_line_chart(
    x_values: List[Any],
    y_values: List[float],
    title: str = "Line Chart",
    xlabel: str = "X",
    ylabel: str = "Y",
    color: Optional[str] = None,
    marker: str = "o",
    comparison_x: Optional[List[Any]] = None,
    comparison_y: Optional[List[float]] = None,
    comparison_label: Optional[str] = None,
    add_trendline: bool = False,
    fig_size: Tuple[int, int] = (10, 6),
) -> Figure:
    """
    Create a line chart.

    Args:
        x_values: X-axis values
        y_values: Y-axis values
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        color: Line color
        marker: Point marker style
        comparison_x: Optional secondary X-axis dataset for comparison
        comparison_y: Optional secondary Y-axis dataset for comparison
        comparison_label: Label for the comparison dataset
        add_trendline: Whether to add a trend line
        fig_size: Figure size (width, height) in inches

    Returns:
        Figure: Matplotlib figure
    """
    # Create figure
    fig, ax = plt.subplots(figsize=fig_size)

    # Plot main line
    ax.plot(x_values, y_values, marker=marker, color=color or "b", label="Individual")

    # Add trend line if requested
    if add_trendline and len(x_values) > 1:
        # Convert x_values to numeric if they're not already
        if not isinstance(x_values[0], (int, float)):
            x_numeric = np.arange(len(x_values))
        else:
            x_numeric = np.array(x_values)

        y_numeric = np.array(y_values)
        z = np.polyfit(x_numeric, y_numeric, 1)
        p = np.poly1d(z)
        ax.plot(x_values, p(x_numeric), "r--", alpha=0.7, label="Trend")

    # Add comparison data if provided
    if comparison_x is not None and comparison_y is not None:
        ax.plot(
            comparison_x,
            comparison_y,
            marker=marker,
            color="r",
            label=comparison_label or "Comparison",
        )

        # Add trend line for comparison if requested
        if add_trendline and len(comparison_x) > 1:
            # Convert comparison_x to numeric if they're not already
            if not isinstance(comparison_x[0], (int, float)):
                x_numeric = np.arange(len(comparison_x))
            else:
                x_numeric = np.array(comparison_x)

            y_numeric = np.array(comparison_y)
            z = np.polyfit(x_numeric, y_numeric, 1)
            p = np.poly1d(z)
            ax.plot(
                comparison_x, p(x_numeric), "b--", alpha=0.7, label="Comparison Trend"
            )

    # Set labels and title
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    # Add legend if needed
    if add_trendline or (comparison_x is not None and comparison_y is not None):
        ax.legend()

    plt.tight_layout()

    return fig


def create_heatmap(
    data: Union[np.ndarray, pd.DataFrame],
    title: str = "Heatmap",
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    cmap: str = "YlGnBu",
    annot: bool = True,
    fmt: str = ".2f",
    linewidths: float = 0.5,
    fig_size: Tuple[int, int] = (10, 8),
) -> Figure:
    """
    Create a heatmap.

    Args:
        data: 2D data array or DataFrame
        title: Chart title
        xlabel: X-axis label (used if data is not a DataFrame)
        ylabel: Y-axis label (used if data is not a DataFrame)
        cmap: Colormap
        annot: Whether to annotate cells
        fmt: String formatting code for annotations
        linewidths: Width of lines separating cells
        fig_size: Figure size (width, height) in inches

    Returns:
        Figure: Matplotlib figure
    """
    # Create figure
    fig, ax = plt.subplots(figsize=fig_size)

    # Convert to DataFrame if needed
    if isinstance(data, np.ndarray):
        if data.ndim != 2:
            raise ValueError("Data must be 2-dimensional")

        # Create default indices and columns if not provided
        if xlabel is None:
            xlabel = "Variables X"
        if ylabel is None:
            ylabel = "Variables Y"

        # Create DataFrame with default indices and columns
        data = pd.DataFrame(
            data,
            index=[f"{ylabel} {i + 1}" for i in range(data.shape[0])],
            columns=[f"{xlabel} {i + 1}" for i in range(data.shape[1])],
        )

    # Create heatmap
    sns.heatmap(data, cmap=cmap, annot=annot, fmt=fmt, linewidths=linewidths, ax=ax)

    # Set title
    ax.set_title(title)

    plt.tight_layout()

    return fig


def create_scatter_plot(
    x_values: List[float],
    y_values: List[float],
    title: str = "Scatter Plot",
    xlabel: str = "X",
    ylabel: str = "Y",
    color: Optional[str] = None,
    size: float = 50,
    alpha: float = 0.7,
    add_trendline: bool = True,
    categories: Optional[List[Any]] = None,
    fig_size: Tuple[int, int] = (10, 6),
) -> Figure:
    """
    Create a scatter plot.

    Args:
        x_values: X-axis values
        y_values: Y-axis values
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        color: Point color
        size: Point size
        alpha: Point transparency
        add_trendline: Whether to add a trend line
        categories: Optional list of categories for coloring points
        fig_size: Figure size (width, height) in inches

    Returns:
        Figure: Matplotlib figure
    """
    # Create figure
    fig, ax = plt.subplots(figsize=fig_size)

    # Create scatter plot
    if categories is not None:
        scatter = ax.scatter(
            x_values, y_values, c=categories, cmap="viridis", s=size, alpha=alpha
        )
        legend = ax.legend(
            *scatter.legend_elements(), loc="upper right", title="Categories"
        )
        ax.add_artist(legend)
    else:
        ax.scatter(x_values, y_values, color=color or "b", s=size, alpha=alpha)

    # Add trend line if requested
    if add_trendline and len(x_values) > 1:
        z = np.polyfit(x_values, y_values, 1)
        p = np.poly1d(z)
        x_line = np.linspace(min(x_values), max(x_values), 100)
        ax.plot(x_line, p(x_line), "r--", alpha=0.7)

    # Set labels and title
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    plt.tight_layout()

    return fig


def create_boxplot(
    data: Union[pd.DataFrame, Dict[str, List[float]], List[List[float]]],
    title: str = "Box Plot",
    xlabel: str = "Categories",
    ylabel: str = "Values",
    color: Optional[str] = None,
    vert: bool = True,
    notch: bool = False,
    fig_size: Tuple[int, int] = (10, 6),
) -> Figure:
    """
    Create a box plot.

    Args:
        data: Data for box plot (DataFrame, dict, or list of lists)
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        color: Box color
        vert: Whether to create a vertical box plot
        notch: Whether to create notched box plots
        fig_size: Figure size (width, height) in inches

    Returns:
        Figure: Matplotlib figure
    """
    # Create figure
    fig, ax = plt.subplots(figsize=fig_size)

    # Create box plot
    if isinstance(data, pd.DataFrame):
        # Use seaborn for DataFrames
        sns.boxplot(
            data=data,
            orient="v" if vert else "h",
            notch=notch,
            palette=[color] if color else None,
            ax=ax,
        )
    else:
        # Use matplotlib for lists and dicts
        ax.boxplot(
            data,
            vert=vert,
            notch=notch,
            patch_artist=True,
            boxprops=dict(facecolor=color or "skyblue"),
        )

    # Set labels and title
    if vert:
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    else:
        ax.set_xlabel(ylabel)
        ax.set_ylabel(xlabel)

    ax.set_title(title)

    plt.tight_layout()

    return fig


def create_pie_chart(
    categories: List[str],
    values: List[float],
    title: str = "Pie Chart",
    colors: Optional[List[str]] = None,
    explode: Optional[List[float]] = None,
    shadow: bool = False,
    autopct: str = "%1.1f%%",
    fig_size: Tuple[int, int] = (10, 8),
) -> Figure:
    """
    Create a pie chart.

    Args:
        categories: List of category names
        values: List of values corresponding to categories
        title: Chart title
        colors: List of colors for pie slices
        explode: List of explode values for pie slices
        shadow: Whether to add a shadow
        autopct: Format string for percentage labels
        fig_size: Figure size (width, height) in inches

    Returns:
        Figure: Matplotlib figure
    """
    # Create figure
    fig, ax = plt.subplots(figsize=fig_size)

    # Create pie chart
    ax.pie(
        values,
        labels=categories,
        colors=colors,
        explode=explode,
        shadow=shadow,
        autopct=autopct,
        startangle=90,
    )

    # Equal aspect ratio ensures that pie is drawn as a circle
    ax.axis("equal")

    # Set title
    ax.set_title(title)

    plt.tight_layout()

    return fig


def save_figure(
    figure: Figure,
    file_path: Union[str, Path],
    dpi: int = 300,
    format: Optional[str] = None,
    transparent: bool = False,
    create_parent_dirs: bool = True,
) -> Path:
    """
    Save a matplotlib figure to a file.

    Args:
        figure: Matplotlib figure to save
        file_path: Path to save the figure
        dpi: Resolution in dots per inch
        format: File format (png, pdf, svg, etc.)
        transparent: Whether to use a transparent background
        create_parent_dirs: Whether to create parent directories

    Returns:
        Path: Path to the saved figure
    """
    path = Path(file_path)

    # Create parent directories if needed
    if create_parent_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)

    # Save figure
    figure.savefig(
        path, dpi=dpi, format=format, transparent=transparent, bbox_inches="tight"
    )

    plt.close(figure)

    return path


def figure_to_base64(figure: Figure, format: str = "png", dpi: int = 100) -> str:
    """
    Convert a matplotlib figure to a base64-encoded string.

    Args:
        figure: Matplotlib figure
        format: Image format (png, jpg, svg, etc.)
        dpi: Resolution in dots per inch

    Returns:
        str: Base64-encoded image string
    """
    buf = BytesIO()
    figure.savefig(buf, format=format, dpi=dpi, bbox_inches="tight")
    buf.seek(0)

    # Convert to base64 string
    img_str = base64.b64encode(buf.read()).decode("utf-8")

    # Close the figure to free memory
    plt.close(figure)

    return img_str


def create_subplot_grid(
    num_plots: int,
    fig_size: Tuple[int, int] = (12, 8),
) -> Tuple[plt.Figure, List[plt.Axes]]:
    """
    Create a grid of subplots.

    Args:
        num_plots: Number of plots
        fig_size: Figure size (width, height) in inches

    Returns:
        Tuple[plt.Figure, List[plt.Axes]]: Figure and list of axes
    """
    # Calculate grid dimensions
    cols = min(3, num_plots)
    rows = (num_plots + cols - 1) // cols

    # Create figure and axes
    fig, axes = plt.subplots(rows, cols, figsize=fig_size)

    # Convert axes to a flat list
    if rows == 1 and cols == 1:
        axes = [axes]
    elif rows == 1 or cols == 1:
        axes = list(axes)
    else:
        axes = axes.flatten()

    # Hide unused subplots
    for i in range(num_plots, len(axes)):
        axes[i].set_visible(False)

    plt.tight_layout()

    return fig, axes


def create_correlation_matrix(
    data: pd.DataFrame,
    title: str = "Correlation Matrix",
    cmap: str = "coolwarm",
    annot: bool = True,
    fig_size: Tuple[int, int] = (10, 8),
) -> Figure:
    """
    Create a correlation matrix heatmap.

    Args:
        data: DataFrame containing the data
        title: Chart title
        cmap: Colormap
        annot: Whether to annotate cells
        fig_size: Figure size (width, height) in inches

    Returns:
        Figure: Matplotlib figure
    """
    # Calculate correlation matrix
    corr_matrix = data.corr()

    # Create figure
    fig, ax = plt.subplots(figsize=fig_size)

    # Create heatmap
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(
        corr_matrix,
        mask=mask,
        cmap=cmap,
        annot=annot,
        fmt=".2f",
        linewidths=0.5,
        ax=ax,
        vmin=-1,
        vmax=1,
        center=0,
        square=True,
        cbar_kws={"shrink": 0.8},
    )

    # Set title
    ax.set_title(title)

    plt.tight_layout()

    return fig
