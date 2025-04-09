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