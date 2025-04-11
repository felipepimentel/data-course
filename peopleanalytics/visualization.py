"""
Visualization module for creating various types of charts and reports.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
from typing import Dict, List, Tuple, Optional, Union, Any
import io
import base64
from pathlib import Path
import logging
import json
from dataclasses import dataclass
import os

# Import constants from peopleanalytics module
from peopleanalytics.constants import COLOR_SCHEMES, RADAR_CHART_STYLE, CHART_CONFIG

# Configure logging
logger = logging.getLogger("visualization")

@dataclass
class ChartConfig:
    """Configuration for chart generation"""
    title: str = ""
    xlabel: str = ""
    ylabel: str = ""
    figsize: Tuple[int, int] = (10, 6)
    palette: str = "viridis"
    style: str = "whitegrid"
    context: str = "talk"
    font_scale: float = 1.0
    legend_title: Optional[str] = None
    grid: bool = True
    rotate_xlabels: bool = False
    rotate_ylabels: bool = False
    format_func: Optional[callable] = None
    
class Visualization:
    """Class for generating visualizations from evaluation data."""
    
    def __init__(self):
        """Initialize the visualization component."""
        pass
        
    def generate_interactive_html(self, data: Dict[str, Any], output_path: str) -> bool:
        """Generate an interactive HTML report.
        
        Args:
            data: Dictionary with data to visualize
            output_path: Path to save the HTML file
            
        Returns:
            Boolean indicating success
        """
        try:
            # Create a simple HTML template
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{data.get('title', 'People Analytics Report')}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    h1, h2 {{ color: #2c3e50; }}
                    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                    th, td {{ text-align: left; padding: 12px; }}
                    th {{ background-color: #3498db; color: white; }}
                    tr:nth-child(even) {{ background-color: #f2f2f2; }}
                    .positive {{ color: green; }}
                    .negative {{ color: red; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>{data.get('title', 'People Analytics Report')}</h1>
            """
            
            # Add summary information if available
            if 'summary' in data:
                html_content += """
                    <h2>Summary</h2>
                    <table>
                        <tr><th>Metric</th><th>Value</th></tr>
                """
                
                for key, value in data['summary'].items():
                    if isinstance(value, list):
                        value_str = ", ".join(str(v) for v in value)
                    else:
                        value_str = str(value)
                    
                    html_content += f"""
                        <tr><td>{key.replace('_', ' ').title()}</td><td>{value_str}</td></tr>
                    """
                
                html_content += """
                    </table>
                """
            
            # Add people data if available
            if 'people_data' in data:
                html_content += """
                    <h2>People Data</h2>
                    <table>
                        <tr>
                            <th>Person</th>
                            <th>Concept</th>
                            <th>Score</th>
                            <th>Group Avg</th>
                            <th>Difference</th>
                        </tr>
                """
                
                for person_data in data['people_data']:
                    person = person_data.get('Person', 'Unknown')
                    concept = person_data.get('Overall Concept', 'Unknown')
                    score = person_data.get('Average Score', 0)
                    group_avg = person_data.get('Group Average', 0)
                    diff = person_data.get('Difference', 0)
                    
                    # Format difference with color
                    diff_class = 'positive' if diff >= 0 else 'negative'
                    diff_sign = '+' if diff > 0 else ''
                    
                    html_content += f"""
                        <tr>
                            <td>{person}</td>
                            <td>{concept}</td>
                            <td>{score:.2f}</td>
                            <td>{group_avg:.2f}</td>
                            <td class="{diff_class}">{diff_sign}{diff:.2f}</td>
                        </tr>
                    """
                
                html_content += """
                    </table>
                """
            
            # Add filtered data if available
            if 'filtered_data' in data:
                html_content += """
                    <h2>Filtered Results</h2>
                    <table>
                        <tr>
                            <th>Person</th>
                            <th>Year</th>
                            <th>Behavior</th>
                            <th>Score</th>
                        </tr>
                """
                
                for item in data['filtered_data']:
                    person = item.get('Person', 'Unknown')
                    year = item.get('Year', 'Unknown')
                    behavior = item.get('Comportamento', item.get('Behavior', 'Unknown'))
                    score = item.get('Score', 0)
                    
                    html_content += f"""
                        <tr>
                            <td>{person}</td>
                            <td>{year}</td>
                            <td>{behavior}</td>
                            <td>{score:.2f}</td>
                        </tr>
                    """
                
                html_content += """
                    </table>
                """
            
            # Close the HTML
            html_content += """
                </div>
            </body>
            </html>
            """
            
            # Write the HTML file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            return True
        except Exception as e:
            print(f"Error generating HTML report: {str(e)}")
            return False
    
    def generate_radar_chart(self, data: Dict[str, Any], output_path: str) -> bool:
        """
        Placeholder for generating a radar chart.
        In a real implementation, this would use matplotlib or plotly.
        """
        try:
            # Just create a simple HTML page with a message
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Radar Chart Placeholder</title>
            </head>
            <body>
                <h1>Radar Chart Placeholder</h1>
                <p>In a full implementation, this would be a radar chart visualization.</p>
            </body>
            </html>
            """
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            return True
        except Exception as e:
            print(f"Error generating radar chart: {str(e)}")
            return False
    
    def generate_heatmap(self, data: Dict[str, Any], output_path: str) -> bool:
        """
        Placeholder for generating a heatmap.
        In a real implementation, this would use matplotlib or seaborn.
        """
        try:
            # Just create a simple HTML page with a message
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Heatmap Placeholder</title>
            </head>
            <body>
                <h1>Heatmap Placeholder</h1>
                <p>In a full implementation, this would be a heatmap visualization.</p>
            </body>
            </html>
            """
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            return True
        except Exception as e:
            print(f"Error generating heatmap: {str(e)}")
            return False

    def setup_plot(self, config: ChartConfig) -> Tuple[plt.Figure, plt.Axes]:
        """Set up plot with configuration
        
        Args:
            config: Chart configuration
            
        Returns:
            Tuple of figure and axes
        """
        # Set Seaborn style
        sns.set_style(config.style)
        sns.set_context(config.context, font_scale=config.font_scale)
        
        # Create figure and axes
        fig, ax = plt.subplots(figsize=config.figsize)
        
        # Set title and labels
        if config.title:
            ax.set_title(config.title)
        if config.xlabel:
            ax.set_xlabel(config.xlabel)
        if config.ylabel:
            ax.set_ylabel(config.ylabel)
            
        # Set grid
        ax.grid(config.grid)
        
        return fig, ax
    
    def finalize_plot(self, fig: plt.Figure, ax: plt.Axes, config: ChartConfig) -> plt.Figure:
        """Apply final touches to plot
        
        Args:
            fig: Matplotlib figure
            ax: Matplotlib axes
            config: Chart configuration
            
        Returns:
            Finalized figure
        """
        # Rotate labels if needed
        if config.rotate_xlabels:
            plt.xticks(rotation=45, ha='right')
        if config.rotate_ylabels:
            plt.yticks(rotation=45, ha='right')
        
        # Adjust layout
        fig.tight_layout()
        
        return fig
    
    def save_or_show(self, fig: plt.Figure, filename: Optional[str] = None) -> Optional[str]:
        """Save figure to file or return as base64 string
        
        Args:
            fig: Matplotlib figure
            filename: Filename to save (without extension)
            
        Returns:
            Base64 encoded image if no filename provided
        """
        if filename:
            # Check if this is a complete file path
            if filename.endswith('.png'):
                filepath = filename
            elif self.output_dir:
                filepath = self.output_dir / f"{filename}.png"
            else:
                filepath = f"{filename}.png"
                
            # Ensure directory exists
            if isinstance(filepath, str):
                filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Save figure
            fig.savefig(filepath, bbox_inches='tight', dpi=150)
            plt.close(fig)
            return str(filepath)
        else:
            # Convert figure to base64 string
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)
            return img_str
    
    def bar_chart(self, 
                 data: pd.DataFrame, 
                 x: str, 
                 y: str, 
                 hue: Optional[str] = None,
                 config: Optional[ChartConfig] = None,
                 filename: Optional[str] = None) -> Optional[str]:
        """Create a bar chart
        
        Args:
            data: DataFrame with data
            x: Column for x-axis
            y: Column for y-axis
            hue: Column for grouping
            config: Chart configuration
            filename: Filename to save (without extension)
            
        Returns:
            Path to saved file or base64 string
        """
        if config is None:
            config = ChartConfig()
            
        # Set up plot
        fig, ax = self.setup_plot(config)
        
        # Create bar chart
        sns.barplot(data=data, x=x, y=y, hue=hue, palette=config.palette, ax=ax)
        
        # Set legend title if provided
        if hue and config.legend_title:
            ax.legend(title=config.legend_title)
            
        # Finalize plot
        fig = self.finalize_plot(fig, ax, config)
        
        # Save or return
        return self.save_or_show(fig, filename)
    
    def line_chart(self, 
                  data: pd.DataFrame, 
                  x: str, 
                  y: str, 
                  hue: Optional[str] = None,
                  config: Optional[ChartConfig] = None,
                  filename: Optional[str] = None) -> Optional[str]:
        """Create a line chart
        
        Args:
            data: DataFrame with data
            x: Column for x-axis
            y: Column for y-axis
            hue: Column for grouping
            config: Chart configuration
            filename: Filename to save (without extension)
            
        Returns:
            Path to saved file or base64 string
        """
        if config is None:
            config = ChartConfig()
            
        # Set up plot
        fig, ax = self.setup_plot(config)
        
        # Create line chart
        sns.lineplot(data=data, x=x, y=y, hue=hue, palette=config.palette, ax=ax)
        
        # Set legend title if provided
        if hue and config.legend_title:
            ax.legend(title=config.legend_title)
            
        # Finalize plot
        fig = self.finalize_plot(fig, ax, config)
        
        # Save or return
        return self.save_or_show(fig, filename)
    
    def scatter_plot(self, 
                    data: pd.DataFrame, 
                    x: str, 
                    y: str, 
                    hue: Optional[str] = None,
                    size: Optional[str] = None,
                    config: Optional[ChartConfig] = None,
                    filename: Optional[str] = None) -> Optional[str]:
        """Create a scatter plot
        
        Args:
            data: DataFrame with data
            x: Column for x-axis
            y: Column for y-axis
            hue: Column for color
            size: Column for point size
            config: Chart configuration
            filename: Filename to save (without extension)
            
        Returns:
            Path to saved file or base64 string
        """
        if config is None:
            config = ChartConfig()
            
        # Set up plot
        fig, ax = self.setup_plot(config)
        
        # Create scatter plot
        sns.scatterplot(data=data, x=x, y=y, hue=hue, size=size, palette=config.palette, ax=ax)
        
        # Set legend title if provided
        if (hue or size) and config.legend_title:
            ax.legend(title=config.legend_title)
            
        # Finalize plot
        fig = self.finalize_plot(fig, ax, config)
        
        # Save or return
        return self.save_or_show(fig, filename)
    
    def heatmap(self, 
               data: pd.DataFrame, 
               annot: bool = True,
               cmap: str = "viridis",
               config: Optional[ChartConfig] = None,
               filename: Optional[str] = None) -> Optional[str]:
        """Create a heatmap
        
        Args:
            data: DataFrame with data
            annot: Whether to annotate cells
            cmap: Colormap
            config: Chart configuration
            filename: Filename to save (without extension)
            
        Returns:
            Path to saved file or base64 string
        """
        if config is None:
            config = ChartConfig()
            
        # Set up plot
        fig, ax = self.setup_plot(config)
        
        # Create heatmap
        sns.heatmap(data, annot=annot, cmap=cmap, ax=ax)
            
        # Finalize plot
        fig = self.finalize_plot(fig, ax, config)
        
        # Save or return
        return self.save_or_show(fig, filename)
    
    def radar_chart(self, 
                   data: Dict[str, List[float]], 
                   categories: List[str],
                   config: Optional[ChartConfig] = None,
                   filename: Optional[str] = None) -> Optional[str]:
        """Create a radar chart
        
        Args:
            data: Dictionary with series names as keys and values as list of values
            categories: List of category names
            config: Chart configuration
            filename: Filename to save (without extension)
            
        Returns:
            Path to saved file or base64 string
        """
        if config is None:
            config = ChartConfig()
            
        # Set up plot
        fig = plt.figure(figsize=config.figsize)
        ax = fig.add_subplot(111, polar=True)
        
        # Set color cycle based on palette
        color_cycle = plt.cm.get_cmap(config.palette, len(data) + 1)
        
        # Number of categories
        N = len(categories)
        
        # Compute angle for each category
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Close the loop
        
        # Initialize plot
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        
        # Draw category labels
        plt.xticks(angles[:-1], categories)
        
        # Set y limits
        ax.set_ylim(0, 10)
        
        # Plot data
        for i, (name, values) in enumerate(data.items()):
            values += values[:1]  # Close the loop
            color = color_cycle(i)
            ax.plot(angles, values, linewidth=1, linestyle='solid', label=name, color=color)
            ax.fill(angles, values, alpha=0.1, color=color)
            
        # Add legend
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        
        # Add title
        if config.title:
            plt.title(config.title, size=11, color='gray', y=1.1)
        
        # Save or return
        return self.save_or_show(fig, filename)
    
    def distribution_plot(self, 
                         data: pd.Series, 
                         kde: bool = True,
                         config: Optional[ChartConfig] = None,
                         filename: Optional[str] = None) -> Optional[str]:
        """Create a distribution plot
        
        Args:
            data: Series with data
            kde: Whether to include KDE
            config: Chart configuration
            filename: Filename to save (without extension)
            
        Returns:
            Path to saved file or base64 string
        """
        if config is None:
            config = ChartConfig()
            
        # Set up plot
        fig, ax = self.setup_plot(config)
        
        # Create distribution plot
        sns.histplot(data, kde=kde, ax=ax)
            
        # Finalize plot
        fig = self.finalize_plot(fig, ax, config)
        
        # Save or return
        return self.save_or_show(fig, filename)
    
    def box_plot(self, 
                data: pd.DataFrame, 
                x: str, 
                y: str, 
                hue: Optional[str] = None,
                config: Optional[ChartConfig] = None,
                filename: Optional[str] = None) -> Optional[str]:
        """Create a box plot
        
        Args:
            data: DataFrame with data
            x: Column for x-axis
            y: Column for y-axis
            hue: Column for grouping
            config: Chart configuration
            filename: Filename to save (without extension)
            
        Returns:
            Path to saved file or base64 string
        """
        if config is None:
            config = ChartConfig()
            
        # Set up plot
        fig, ax = self.setup_plot(config)
        
        # Create box plot
        sns.boxplot(data=data, x=x, y=y, hue=hue, palette=config.palette, ax=ax)
        
        # Set legend title if provided
        if hue and config.legend_title:
            ax.legend(title=config.legend_title)
            
        # Finalize plot
        fig = self.finalize_plot(fig, ax, config)
        
        # Save or return
        return self.save_or_show(fig, filename)
    
    def pie_chart(self, 
                 data: pd.Series, 
                 config: Optional[ChartConfig] = None,
                 filename: Optional[str] = None) -> Optional[str]:
        """Create a pie chart
        
        Args:
            data: Series with data
            config: Chart configuration
            filename: Filename to save (without extension)
            
        Returns:
            Path to saved file or base64 string
        """
        if config is None:
            config = ChartConfig()
            
        # Set up plot
        fig, ax = plt.subplots(figsize=config.figsize)
        
        # Create pie chart
        data.plot.pie(ax=ax, autopct='%1.1f%%', startangle=90, 
                     colors=sns.color_palette(config.palette, len(data)))
        
        # Set title
        if config.title:
            ax.set_title(config.title)
            
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.set_aspect('equal')
        
        # Remove y-label
        ax.set_ylabel('')
        
        # Save or return
        return self.save_or_show(fig, filename)
    
    def multi_chart_grid(self, 
                        charts: List[Dict[str, Any]], 
                        rows: int, 
                        cols: int,
                        suptitle: Optional[str] = None,
                        figsize: Tuple[int, int] = (16, 10),
                        filename: Optional[str] = None) -> Optional[str]:
        """Create a grid of multiple charts
        
        Args:
            charts: List of chart configurations
            rows: Number of rows
            cols: Number of columns
            suptitle: Super title for the grid
            figsize: Figure size
            filename: Filename to save (without extension)
            
        Returns:
            Path to saved file or base64 string
        """
        # Create figure
        fig = plt.figure(figsize=figsize)
        
        # Add suptitle if provided
        if suptitle:
            fig.suptitle(suptitle, fontsize=14)
            
        # Create charts
        for i, chart_config in enumerate(charts):
            if i >= rows * cols:
                logger.warning(f"Too many charts provided. Only showing {rows * cols}.")
                break
                
            # Get chart type and data
            chart_type = chart_config.get("type", "bar")
            data = chart_config.get("data")
            title = chart_config.get("title", "")
            
            # Create subplot
            ax = fig.add_subplot(rows, cols, i+1)
            
            # Set title
            if title:
                ax.set_title(title)
                
            # Create chart based on type
            if chart_type == "bar":
                if isinstance(data, pd.DataFrame):
                    data.plot(kind="bar", ax=ax)
                elif isinstance(data, dict):
                    ax.bar(data.keys(), data.values())
            elif chart_type == "line":
                if isinstance(data, pd.DataFrame):
                    data.plot(kind="line", ax=ax)
                elif isinstance(data, dict):
                    ax.plot(list(data.keys()), list(data.values()))
            elif chart_type == "pie":
                if isinstance(data, pd.Series):
                    data.plot.pie(ax=ax, autopct='%1.1f%%')
                elif isinstance(data, dict):
                    ax.pie(list(data.values()), labels=list(data.keys()), autopct='%1.1f%%')
            elif chart_type == "scatter":
                if isinstance(data, pd.DataFrame):
                    ax.scatter(data[chart_config.get("x", data.columns[0])], 
                              data[chart_config.get("y", data.columns[1])])
            
            # Customize axis labels
            if "xlabel" in chart_config:
                ax.set_xlabel(chart_config["xlabel"])
            if "ylabel" in chart_config:
                ax.set_ylabel(chart_config["ylabel"])
                
        # Adjust layout
        plt.tight_layout()
        if suptitle:
            plt.subplots_adjust(top=0.9)
            
        # Save or return
        return self.save_or_show(fig, filename)
    
    def load_config_from_file(self, config_file: str) -> Dict[str, Any]:
        """Load chart configuration from file
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            Dictionary with configuration
        """
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return None

    def create_career_progression_charts(self, person_name: str, career_data: Dict[str, Any], output_path: Path) -> None:
        """Create visualizations for career progression data.
        
        Args:
            person_name: The name of the person
            career_data: Dictionary containing career progression data
            output_path: Path to save the visualizations to
        """
        try:
            # Create career progression directory if it doesn't exist
            charts_dir = output_path / "career_charts"
            charts_dir.mkdir(exist_ok=True)
            
            # Extract data
            events = career_data.get("eventos_carreira", [])
            skills = career_data.get("matriz_habilidades", {})
            metrics = career_data.get("metricas", {})
            
            # Only create visualizations if we have data
            if events:
                self._create_career_timeline(person_name, events, charts_dir)
                
            if skills:
                self._create_skills_radar(person_name, skills, charts_dir)
                
            if metrics:
                self._create_growth_metrics_chart(person_name, metrics, charts_dir)
                
            # Create a comprehensive growth dashboard if we have all components
            if events and skills and metrics:
                self._create_career_dashboard(person_name, career_data, charts_dir)
                
        except Exception as e:
            self.logger.error(f"Error creating career charts for {person_name}: {e}")

    def _create_career_timeline(self, person_name: str, events: List[Dict[str, Any]], output_path: Path) -> None:
        """Create a career timeline visualization.
        
        Args:
            person_name: The name of the person
            events: List of career events
            output_path: Path to save the visualization to
        """
        try:
            # Sort events by date
            sorted_events = sorted(events, key=lambda x: x.get("data", ""))
            
            # Create timeline as HTML/JavaScript using Chart.js
            html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Linha do Tempo de Carreira - {person_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/moment"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-moment"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        h1 {{ color: #333; text-align: center; }}
        .chart-container {{ height: 600px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Linha do Tempo de Carreira - {person_name}</h1>
        <div class="chart-container">
            <canvas id="timeline"></canvas>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('timeline').getContext('2d');
        
        // Dados dos eventos
        const events = [
"""
            
            # Add each event as a data point
            for event in sorted_events:
                date = event.get("data", "")
                event_type = event.get("tipo_evento", "")
                details = event.get("detalhes", "").replace("'", "\\'")  # Escape single quotes
                
                # Determine color and label based on event type
                color = ""
                if event_type == "promotion":
                    color = "#4CAF50"  # Green
                    label = "Promoção"
                elif event_type == "lateral_move":
                    color = "#2196F3"  # Blue
                    label = "Movimentação Lateral"
                elif event_type == "role_change":
                    color = "#9C27B0"  # Purple
                    label = "Mudança de Função"
                elif event_type == "skill_acquisition":
                    color = "#FF9800"  # Orange
                    label = "Nova Habilidade"
                elif event_type == "certification":
                    color = "#F44336"  # Red
                    label = "Certificação"
                else:
                    color = "#607D8B"  # Gray
                    label = event_type.capitalize()
                
                new_position = event.get("cargo_novo", "")
                if new_position and (event_type in ["promotion", "lateral_move", "role_change"]):
                    details = f"{new_position}: {details}"
                
                html_content += f"            {{x: '{date}', y: '{label}', details: '{details}', color: '{color}'}},\n"
            
            html_content += """        ];
            
            // Configurar o gráfico
            new Chart(ctx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        data: events,
                        backgroundColor: events.map(e => e.color),
                        pointRadius: 10,
                        pointHoverRadius: 12
                    }]
                },
                options: {
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'month',
                                displayFormats: {
                                    month: 'MMM YYYY'
                                }
                            },
                            title: {
                                display: true,
                                text: 'Data'
                            }
                        },
                        y: {
                            type: 'category',
                            labels: ['Certificação', 'Nova Habilidade', 'Mudança de Função', 'Movimentação Lateral', 'Promoção'],
                            title: {
                                display: true,
                                text: 'Tipo de Evento'
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.raw.details;
                                }
                            }
                        },
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Linha do Tempo de Carreira'
                        }
                    },
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        </script>
    </body>
</html>
"""
            
            # Save the HTML file
            timeline_file = output_path / f"{person_name}_career_timeline.html"
            with open(timeline_file, 'w') as f:
                f.write(html_content)
                
            # Also create a Mermaid version for Markdown
            mermaid_content = self._create_mermaid_timeline(person_name, sorted_events)
            mermaid_file = output_path / f"{person_name}_career_timeline.md"
            with open(mermaid_file, 'w') as f:
                f.write(mermaid_content)
                
        except Exception as e:
            self.logger.error(f"Error creating career timeline for {person_name}: {e}")

    def _create_mermaid_timeline(self, person_name: str, events: List[Dict[str, Any]]) -> str:
        """Create a Mermaid timeline for career events.
        
        Args:
            person_name: The name of the person
            events: List of career events sorted by date
            
        Returns:
            str: Mermaid timeline content
        """
        # Create Mermaid timeline
        mermaid = f"""# Linha do Tempo de Carreira: {person_name}

```mermaid
timeline
    title Trajetória de Carreira de {person_name}
"""
        
        # Group events by year
        years = {}
        for event in events:
            date_str = event.get("data", "")
            if date_str:
                year = date_str.split("-")[0]
                if year not in years:
                    years[year] = []
                years[year].append(event)
        
        # Add events to timeline by year
        for year in sorted(years.keys()):
            mermaid += f"    section {year}\n"
            
            for event in years[year]:
                date = event.get("data", "").replace("-", "/")
                event_type = event.get("tipo_evento", "")
                details = event.get("detalhes", "")
                
                # Format event text based on type
                if event_type == "promotion":
                    cargo_novo = event.get("cargo_novo", "")
                    event_text = f"{date}: Promoção para {cargo_novo}"
                elif event_type == "lateral_move":
                    cargo_novo = event.get("cargo_novo", "")
                    event_text = f"{date}: Movimento lateral para {cargo_novo}"
                elif event_type == "role_change":
                    cargo_novo = event.get("cargo_novo", "")
                    event_text = f"{date}: Mudança de função para {cargo_novo}"
                elif event_type == "skill_acquisition":
                    event_text = f"{date}: Nova habilidade: {details}"
                elif event_type == "certification":
                    event_text = f"{date}: Certificação: {details}"
                else:
                    event_text = f"{date}: {event_type} - {details}"
                
                mermaid += f"        {event_text}\n"
        
        mermaid += "```\n"
        
        return mermaid

    def _create_skills_radar(self, person_name: str, skills: Dict[str, int], output_path: Path) -> None:
        """Create a radar chart for skills.
        
        Args:
            person_name: The name of the person
            skills: Dictionary mapping skill names to proficiency levels
            output_path: Path to save the visualization to
        """
        try:
            # Group skills by category (if using dot notation like "technical.python")
            categorized_skills = {}
            
            for skill_name, level in skills.items():
                if "." in skill_name:
                    category, name = skill_name.split(".", 1)
                else:
                    category = "Habilidades Técnicas"
                    name = skill_name
                
                if category not in categorized_skills:
                    categorized_skills[category] = []
                    
                categorized_skills[category].append({
                    "name": name,
                    "level": level
                })
            
            # Create the HTML/JavaScript radar chart
            html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Matriz de Habilidades - {person_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        h1, h2 {{ color: #333; text-align: center; }}
        .chart-container {{ height: 400px; margin-bottom: 40px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Matriz de Habilidades - {person_name}</h1>
"""
            
            # Add a radar chart for each category
            chart_id = 1
            for category, skill_list in categorized_skills.items():
                html_content += f"""
            <h2>{category}</h2>
            <div class="chart-container">
                <canvas id="radar{chart_id}"></canvas>
            </div>
            
            <script>
                const ctx{chart_id} = document.getElementById('radar{chart_id}').getContext('2d');
                
                new Chart(ctx{chart_id}, {{
                    type: 'radar',
                    data: {{
                        labels: [{', '.join([f"'{skill['name']}'" for skill in skill_list])}],
                        datasets: [{{
                            label: 'Nível de Proficiência',
                            data: [{', '.join([str(skill['level']) for skill in skill_list])}],
                            fill: true,
                            backgroundColor: 'rgba(54, 162, 235, 0.2)',
                            borderColor: 'rgb(54, 162, 235)',
                            pointBackgroundColor: 'rgb(54, 162, 235)',
                            pointBorderColor: '#fff',
                            pointHoverBackgroundColor: '#fff',
                            pointHoverBorderColor: 'rgb(54, 162, 235)'
                        }}]
                    }},
                    options: {{
                        scales: {{
                            r: {{
                                angleLines: {{
                                    display: true
                                }},
                                suggestedMin: 0,
                                suggestedMax: 5
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                display: true
                            }},
                            title: {{
                                display: true,
                                text: '{category}'
                            }}
                        }},
                        responsive: true,
                        maintainAspectRatio: false
                    }}
                }});
            </script>
"""
                chart_id += 1
            
            html_content += """
        </div>
    </div>
</body>
</html>
"""
            
            # Save the HTML file
            skills_file = output_path / f"{person_name}_skills_radar.html"
            with open(skills_file, 'w') as f:
                f.write(html_content)
                
        except Exception as e:
            self.logger.error(f"Error creating skills radar for {person_name}: {e}")

    def _create_growth_metrics_chart(self, person_name: str, metrics: Dict[str, Any], output_path: Path) -> None:
        """Create a chart visualizing growth metrics.
        
        Args:
            person_name: The name of the person
            metrics: Dictionary of career metrics
            output_path: Path to save the visualization to
        """
        try:
            # Extract growth score and other key metrics
            growth_score = metrics.get("growth_score", 0)
            promotion_velocity = metrics.get("media_anos_entre_promocoes", 0)
            skill_avg = metrics.get("media_habilidades", 0)
            cert_count = metrics.get("total_certificacoes", 0)
            goal_completion = metrics.get("taxa_conclusao_metas", 0)
            
            # Create HTML/JavaScript gauge chart for growth score
            html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Métricas de Crescimento - {person_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-gauge"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        h1, h2 {{ color: #333; text-align: center; }}
        .chart-container {{ height: 300px; margin-bottom: 30px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 30px; }}
        .metric-card {{ background-color: #f5f5f5; border-radius: 8px; padding: 15px; }}
        .metric-title {{ font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #2196F3; }}
        .metric-description {{ font-size: 0.9em; color: #666; margin-top: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Métricas de Crescimento Profissional - {person_name}</h1>
        
        <div class="chart-container">
            <canvas id="growthScore"></canvas>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">Velocidade de Promoção</div>
                <div class="metric-value">{promotion_velocity:.1f} anos</div>
                <div class="metric-description">Tempo médio entre promoções</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Nível Médio de Habilidades</div>
                <div class="metric-value">{skill_avg:.1f}/5</div>
                <div class="metric-description">Proficiência média em todas as habilidades</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Total de Certificações</div>
                <div class="metric-value">{cert_count}</div>
                <div class="metric-description">Número de certificações obtidas</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">Taxa de Conclusão de Metas</div>
                <div class="metric-value">{goal_completion:.1f}%</div>
                <div class="metric-description">Percentual de metas de carreira concluídas</div>
            </div>
        </div>
        
        <script>
            const ctx = document.getElementById('growthScore').getContext('2d');
            
            // Define gauge chart options
            const gaugeChartOptions = {{
                responsive: true,
                maintainAspectRatio: false,
                title: {{
                    display: true,
                    text: 'Score de Crescimento Profissional'
                }},
                layout: {{
                    padding: 20
                }},
                needle: {{
                    radiusPercentage: 2,
                    widthPercentage: 3.2,
                    lengthPercentage: 80,
                    color: 'rgba(0, 0, 0, 1)'
                }},
                valueLabel: {{
                    formatter: value => {{
                        return Math.round(value);
                    }}
                }}
            }};
            
            // Create gauge chart
            new Chart(ctx, {{
                type: 'gauge',
                data: {{
                    datasets: [{{
                        value: {growth_score},
                        data: [20, 40, 60, 80, 100],
                        backgroundColor: ['#f44336', '#ff9800', '#ffeb3b', '#8bc34a', '#4caf50'],
                        borderWidth: 0
                    }}]
                }},
                options: gaugeChartOptions
            }});
        </script>
    </div>
</body>
</html>
"""
            
            # Save the HTML file
            metrics_file = output_path / f"{person_name}_growth_metrics.html"
            with open(metrics_file, 'w') as f:
                f.write(html_content)
                
        except Exception as e:
            self.logger.error(f"Error creating growth metrics chart for {person_name}: {e}")

    def _create_career_dashboard(self, person_name: str, career_data: Dict[str, Any], output_path: Path) -> None:
        """Create a comprehensive career dashboard.
        
        Args:
            person_name: The name of the person
            career_data: Dictionary containing all career progression data
            output_path: Path to save the visualization to
        """
        try:
            # Extract all needed data
            events = career_data.get("eventos_carreira", [])
            skills = career_data.get("matriz_habilidades", {})
            goals = career_data.get("metas_carreira", [])
            certifications = career_data.get("certificacoes", [])
            metrics = career_data.get("metricas", {})
            
            # Sort events by date
            sorted_events = sorted(events, key=lambda x: x.get("data", ""))
            
            # Group skills by category
            categorized_skills = {}
            for skill_name, level in skills.items():
                if "." in skill_name:
                    category, name = skill_name.split(".", 1)
                else:
                    category = "Habilidades Técnicas"
                    name = skill_name
                
                if category not in categorized_skills:
                    categorized_skills[category] = []
                    
                categorized_skills[category].append({
                    "name": name,
                    "level": level
                })
            
            # Extract metrics
            growth_score = metrics.get("growth_score", 0)
            promotion_velocity = metrics.get("media_anos_entre_promocoes", 0)
            skill_avg = metrics.get("media_habilidades", 0)
            cert_count = metrics.get("total_certificacoes", 0)
            goal_completion = metrics.get("taxa_conclusao_metas", 0)
            
            # Create HTML dashboard
            html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Carreira - {person_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/moment"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-moment"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        header {{ background-color: #2196F3; color: white; padding: 20px; text-align: center; margin-bottom: 20px; }}
        h1, h2, h3 {{ margin: 0; }}
        .dashboard-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }}
        .dashboard-item {{ background-color: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .dashboard-item.full-width {{ grid-column: span 2; }}
        .chart-container {{ height: 300px; margin-top: 15px; }}
        .metrics-container {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }}
        .metric-card {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
        .metric-value {{ font-size: 1.8em; font-weight: bold; color: #2196F3; }}
        .metric-title {{ font-size: 0.9em; color: #666; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        .progress-bar {{ height: 8px; background-color: #e0e0e0; border-radius: 4px; margin-top: 5px; }}
        .progress-fill {{ height: 100%; background-color: #4CAF50; border-radius: 4px; }}
    </style>
</head>
<body>
    <header>
        <h1>Dashboard de Carreira</h1>
        <h2>{person_name}</h2>
    </header>
    
    <div class="container">
        <div class="dashboard-grid">
            <!-- Métricas principais -->
            <div class="dashboard-item">
                <h3>Métricas de Crescimento</h3>
                <div class="metrics-container">
                    <div class="metric-card">
                        <div class="metric-value">{growth_score:.1f}/100</div>
                        <div class="metric-title">Score de Crescimento</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{promotion_velocity:.1f} anos</div>
                        <div class="metric-title">Tempo entre Promoções</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{skill_avg:.1f}/5</div>
                        <div class="metric-title">Nível Médio de Habilidades</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{cert_count}</div>
                        <div class="metric-title">Certificações</div>
                    </div>
                </div>
            </div>
            
            <!-- Distribuição de habilidades -->
            <div class="dashboard-item">
                <h3>Distribuição de Habilidades</h3>
                <div class="chart-container">
                    <canvas id="skillsDistribution"></canvas>
                </div>
            </div>
            
            <!-- Linha do tempo -->
            <div class="dashboard-item full-width">
                <h3>Linha do Tempo de Carreira</h3>
                <div class="chart-container">
                    <canvas id="timeline"></canvas>
                </div>
            </div>
            
            <!-- Metas de carreira -->
            <div class="dashboard-item">
                <h3>Metas de Carreira</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Meta</th>
                            <th>Progresso</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            
            # Add goals to the table
            if goals:
                for goal in sorted(goals, key=lambda x: x.get("target_date", "")):
                    title = goal.get("title", "")
                    progress = goal.get("progress", 0)
                    status_en = goal.get("status", "")
                    status = {
                        "not_started": "Não Iniciado",
                        "in_progress": "Em Andamento",
                        "completed": "Concluído",
                        "delayed": "Atrasado"
                    }.get(status_en, status_en)
                    
                    # Determine status color
                    status_color = {
                        "not_started": "#9e9e9e",  # Gray
                        "in_progress": "#2196F3",  # Blue
                        "completed": "#4CAF50",    # Green
                        "delayed": "#F44336"       # Red
                    }.get(status_en, "#9e9e9e")
                    
                    html_content += f"""
                            <tr>
                                <td>{title}</td>
                                <td>
                                    <div>{progress}%</div>
                                    <div class="progress-bar">
                                        <div class="progress-fill" style="width: {progress}%"></div>
                                    </div>
                                </td>
                                <td style="color: {status_color}">{status}</td>
                            </tr>"""
            else:
                html_content += """
                            <tr>
                                <td colspan="3">Nenhuma meta de carreira registrada</td>
                            </tr>"""
            
            html_content += """
                    </tbody>
                </table>
            </div>
            
            <!-- Certificações -->
            <div class="dashboard-item">
                <h3>Certificações</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Certificação</th>
                            <th>Emissor</th>
                            <th>Data</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            
            # Add certifications to the table
            if certifications:
                for cert in sorted(certifications, key=lambda x: x.get("date_obtained", ""), reverse=True):
                    name = cert.get("name", "")
                    issuer = cert.get("issuer", "")
                    date = cert.get("date_obtained", "").replace("-", "/")
                    
                    html_content += f"""
                            <tr>
                                <td>{name}</td>
                                <td>{issuer}</td>
                                <td>{date}</td>
                            </tr>"""
            else:
                html_content += """
                            <tr>
                                <td colspan="3">Nenhuma certificação registrada</td>
                            </tr>"""
            
            # Add chart initialization scripts
            html_content += """
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script>
        // Dados para os gráficos
"""
            
            # Add timeline data
            html_content += """
        const events = [
"""
            for event in sorted_events:
                date = event.get("data", "")
                event_type = event.get("tipo_evento", "")
                details = event.get("detalhes", "").replace("'", "\\'")  # Escape single quotes
                
                # Determine color and label based on event type
                color = ""
                if event_type == "promotion":
                    color = "#4CAF50"  # Green
                    label = "Promoção"
                elif event_type == "lateral_move":
                    color = "#2196F3"  # Blue
                    label = "Movimentação Lateral"
                elif event_type == "role_change":
                    color = "#9C27B0"  # Purple
                    label = "Mudança de Função"
                elif event_type == "skill_acquisition":
                    color = "#FF9800"  # Orange
                    label = "Nova Habilidade"
                elif event_type == "certification":
                    color = "#F44336"  # Red
                    label = "Certificação"
                else:
                    color = "#607D8B"  # Gray
                    label = event_type.capitalize()
                
                new_position = event.get("cargo_novo", "")
                if new_position and (event_type in ["promotion", "lateral_move", "role_change"]):
                    details = f"{new_position}: {details}"
                
                html_content += f"            {{x: '{date}', y: '{label}', details: '{details}', color: '{color}'}},\n"
            
            html_content += "        ];\n"
            
            # Add skills distribution data
            html_content += """
        const skillDistribution = {
"""
            skill_distribution = metrics.get("distribuicao_habilidades", {})
            for level in range(1, 6):
                count = skill_distribution.get(f"nivel_{level}", 0)
                html_content += f"            {level}: {count},\n"
            
            html_content += "        };\n"
            
            # Initialize charts
            html_content += """
        // Timeline chart
        const timelineCtx = document.getElementById('timeline').getContext('2d');
        new Chart(timelineCtx, {
            type: 'scatter',
            data: {
                datasets: [{
                    data: events,
                    backgroundColor: events.map(e => e.color),
                    pointRadius: 10,
                    pointHoverRadius: 12
                }]
            },
            options: {
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'month',
                            displayFormats: {
                                month: 'MMM YYYY'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Data'
                        }
                    },
                    y: {
                        type: 'category',
                        labels: ['Certificação', 'Nova Habilidade', 'Mudança de Função', 'Movimentação Lateral', 'Promoção'],
                        title: {
                            display: true,
                            text: 'Tipo de Evento'
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.raw.details;
                            }
                        }
                    },
                    legend: {
                        display: false
                    }
                },
                responsive: true,
                maintainAspectRatio: false
            }
        });
        
        // Skills distribution chart
        const skillsCtx = document.getElementById('skillsDistribution').getContext('2d');
        new Chart(skillsCtx, {
            type: 'bar',
            data: {
                labels: ['Nível 1', 'Nível 2', 'Nível 3', 'Nível 4', 'Nível 5'],
                datasets: [{
                    label: 'Número de Habilidades',
                    data: [
                        skillDistribution[1] || 0,
                        skillDistribution[2] || 0,
                        skillDistribution[3] || 0,
                        skillDistribution[4] || 0,
                        skillDistribution[5] || 0
                    ],
                    backgroundColor: [
                        '#f44336',
                        '#ff9800',
                        '#ffeb3b',
                        '#8bc34a',
                        '#4caf50'
                    ]
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Número de Habilidades'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Nível de Proficiência'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                },
                responsive: true,
                maintainAspectRatio: false
            }
        });
    </script>
</body>
</html>
"""
            
            # Save the HTML file
            dashboard_file = output_path / f"{person_name}_career_dashboard.html"
            with open(dashboard_file, 'w') as f:
                f.write(html_content)
                
        except Exception as e:
            self.logger.error(f"Error creating career dashboard for {person_name}: {e}") 