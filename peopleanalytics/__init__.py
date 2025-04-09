"""
People Analytics - Evaluation Analysis Tool
==========================================

A comprehensive tool for analyzing 360-degree evaluations,
generating reports, and visualizing performance data.
"""

__version__ = '1.0.0'

# Simplified imports for common components
from peopleanalytics.analyzer import EvaluationAnalyzer
from peopleanalytics.visualization import Visualization, ChartConfig
from peopleanalytics.data_pipeline import DataPipeline

# Version info
__all__ = [
    'EvaluationAnalyzer',
    'Visualization',
    'ChartConfig',
    'DataPipeline',
] 