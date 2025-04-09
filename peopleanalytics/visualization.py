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
    """Handles data visualization with various chart types"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize visualization module
        
        Args:
            output_dir: Directory to save visualizations
        """
        self.output_dir = Path(output_dir) if output_dir else None
        if self.output_dir and not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Custom color scheme
        self.custom_colors = COLOR_SCHEMES["default"]
    
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
    
    def generate_radar_chart(self, data: Dict[str, Any], title: str = "", output_path: Optional[str] = None) -> Optional[str]:
        """Generate a radar chart from data
        
        Args:
            data: Dictionary with chart data (categories and series)
            title: Chart title
            output_path: Path to save the generated chart
            
        Returns:
            Path to saved file or base64 string
        """
        # Extract categories and series from data
        categories = data.get("categories", [])
        series = data.get("series", {})
        
        if not categories or not series:
            logger.error("Missing categories or series data for radar chart")
            return None
            
        config = ChartConfig(title=title, figsize=(10, 8))
        
        # Use radar_chart method
        return self.radar_chart(
            data=series,
            categories=categories,
            config=config,
            filename=output_path
        )
    
    def generate_heatmap(self, 
                        data: pd.DataFrame, 
                        x_col: str, 
                        y_col: str, 
                        value_col: str,
                        title: str = "",
                        output_path: Optional[str] = None) -> Optional[str]:
        """Generate a heatmap from data
        
        Args:
            data: DataFrame with data
            x_col: Column to use for x-axis
            y_col: Column to use for y-axis
            value_col: Column to use for values
            title: Chart title
            output_path: Path to save the generated chart
            
        Returns:
            Path to saved file or base64 string
        """
        # Pivot the data to create a heatmap matrix
        try:
            pivot_data = data.pivot(index=y_col, columns=x_col, values=value_col)
            
            config = ChartConfig(
                title=title,
                figsize=(12, 10),
                rotate_xlabels=True
            )
            
            # Use heatmap method
            return self.heatmap(
                data=pivot_data,
                annot=True,
                cmap="viridis",
                config=config,
                filename=output_path
            )
        except Exception as e:
            logger.error(f"Error generating heatmap: {str(e)}")
            return None
    
    def generate_interactive_html(self, data: Dict[str, Any], output_path: str) -> str:
        """Generate an interactive HTML report
        
        Args:
            data: Report configuration and data
            output_path: Path to save the HTML report
            
        Returns:
            Path to saved file
        """
        # Build HTML content
        title = data.get("title", "Interactive Report")
        summary = data.get("summary", {})
        chart_type = data.get("chartType", "bar")
        labels = data.get("labels", [])
        datasets = data.get("datasets", [])
        table_data = data.get("tableData", [])
        
        # Format the HTML with Chart.js
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ margin-bottom: 30px; }}
                .chart-container {{ margin-bottom: 40px; height: 400px; }}
                .table-container {{ margin-top: 40px; overflow-x: auto; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ text-align: left; padding: 12px 15px; }}
                th {{ background-color: #f8f9fa; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .summary {{ margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }}
                h1, h2 {{ color: #2c3e50; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{title}</h1>
                    <p>Generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
        """
        
        # Add summary section if available
        if summary:
            html_content += '<div class="summary"><h2>Summary</h2><ul>'
            for key, value in summary.items():
                html_content += f'<li><strong>{key}:</strong> {value}</li>'
            html_content += '</ul></div>'
        
        # Add chart
        html_content += f"""
                <div class="chart-container">
                    <canvas id="mainChart"></canvas>
                </div>
                
                <script>
                    const ctx = document.getElementById('mainChart').getContext('2d');
                    new Chart(ctx, {{
                        type: '{chart_type}',
                        data: {{
                            labels: {json.dumps(labels)},
                            datasets: {json.dumps(datasets)}
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {{
                                title: {{
                                    display: true,
                                    text: 'Data Visualization'
                                }}
                            }}
                        }}
                    }});
                </script>
        """
        
        # Add table if data available
        if table_data:
            # Get column names from first row
            if table_data and isinstance(table_data[0], dict):
                columns = list(table_data[0].keys())
                
                html_content += f"""
                <div class="table-container">
                    <h2>Data Table</h2>
                    <table>
                        <thead>
                            <tr>
                """
                
                # Add table headers
                for col in columns:
                    html_content += f'<th>{col}</th>'
                
                html_content += """
                            </tr>
                        </thead>
                        <tbody>
                """
                
                # Add table rows
                for row in table_data:
                    html_content += '<tr>'
                    for col in columns:
                        html_content += f'<td>{row.get(col, "")}</td>'
                    html_content += '</tr>'
                
                html_content += """
                        </tbody>
                    </table>
                </div>
                """
        
        # Close HTML
        html_content += """
            </div>
        </body>
        </html>
        """
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write(html_content)
            
        return output_path 