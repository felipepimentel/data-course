"""
Constants for People Analytics.

This module provides constants used throughout the package.
"""

# Frequency labels for evaluation distributions
FREQUENCY_LABELS = ["n/a", "referencia", "sempre", "quase sempre", "poucas vezes", "raramente"]

# Weights for calculating weighted scores from frequencies
FREQUENCY_WEIGHTS = [0, 2.5, 4, 3, 2, 1]

# Chart colors for concepts
CONCEPT_CHART_COLORS = {
    "Excelente": "#27AE60",  # Green
    "Bom": "#2ECC71",        # Light Green
    "Regular": "#F1C40F",    # Yellow
    "Abaixo": "#E67E22",     # Orange
    "Insatisfatório": "#E74C3C",  # Red
    "default": "#7F8C8D"     # Gray
}

# Colors for visualization
CHART_COLORS = [
    "#3498db",  # Blue
    "#2ecc71",  # Green
    "#e74c3c",  # Red
    "#f1c40f",  # Yellow
    "#9b59b6",  # Purple
    "#1abc9c",  # Turquoise
    "#e67e22",  # Orange
    "#34495e",  # Dark Blue
    "#7f8c8d",  # Gray
    "#2c3e50"   # Darker Blue
]

# Default color schemes
COLOR_SCHEMES = {
    "default": {
        "concept_colors": {
            "Excelente": "#27AE60",
            "Muito Bom": "#2980B9",
            "Bom": "#F1C40F",
            "Regular": "#E67E22",
            "Insuficiente": "#E74C3C",
            "default": "#7F8C8D"
        },
        "chart_colors": [
            "#3498DB",  # Blue
            "#2ECC71",  # Green
            "#F1C40F",  # Yellow
            "#E67E22",  # Orange
            "#9B59B6",  # Purple
            "#1ABC9C",  # Turquoise
            "#34495E",  # Dark Blue
            "#E74C3C",  # Red
            "#95A5A6",  # Gray
            "#16A085",  # Dark Green
        ]
    },
    "corporate": {
        "concept_colors": {
            "Excelente": "#1F618D",
            "Muito Bom": "#2874A6",
            "Bom": "#5499C7",
            "Regular": "#7FB3D5",
            "Insuficiente": "#A9CCE3",
            "default": "#D4E6F1"
        },
        "chart_colors": [
            "#1F618D",  # Dark Blue
            "#2874A6",  # Medium Blue
            "#5499C7",  # Light Blue
            "#7FB3D5",  # Pale Blue
            "#154360",  # Very Dark Blue
            "#1A5276",  # Navy Blue
            "#2E86C1",  # Bright Blue
            "#3498DB",  # Standard Blue
            "#85C1E9",  # Sky Blue
            "#AED6F1",  # Baby Blue
        ]
    },
    "monochrome": {
        "concept_colors": {
            "Excelente": "#1C1C1C",
            "Muito Bom": "#383838",
            "Bom": "#585858",
            "Regular": "#787878",
            "Insuficiente": "#989898",
            "default": "#B8B8B8"
        },
        "chart_colors": [
            "#000000",  # Black
            "#1C1C1C",  # Almost Black
            "#383838",  # Dark Gray
            "#585858",  # Medium Dark Gray
            "#787878",  # Medium Gray
            "#989898",  # Light Medium Gray
            "#B8B8B8",  # Light Gray
            "#D8D8D8",  # Very Light Gray
            "#F0F0F0",  # Almost White
            "#FFFFFF",  # White
        ]
    }
}

# Radar chart style
RADAR_CHART_STYLE = {
    "primary_color": "#3498db",
    "secondary_color": "#7f8c8d",
    "primary_alpha": 0.3,
    "secondary_alpha": 0.1,
    "fontsize": 8,
    "tick_color": "#7f8c8d",
    "tick_size": 7
}

# Chart configuration
CHART_CONFIG = {
    "figsize": {
        "standard": (10, 6),
        "wide": (15, 8),
        "small": (8, 5),
        "square": (8, 8),
        "radar": (10, 8)
    },
    "fontsize": {
        "title": 14,
        "axis_label": 12,
        "tick_label": 10,
        "legend": 10,
        "annotation": 8
    },
    "linewidth": {
        "primary": 2,
        "secondary": 1.5,
        "grid": 0.5
    },
    "alpha": {
        "primary": 0.8,
        "secondary": 0.5,
        "grid": 0.3
    }
}

# Schema Configuration
SCHEMA_VALIDATION_LEVEL = "strict"  # Options: "none", "warn", "strict"

# Data Pipeline
DEFAULT_TRANSFORMERS = [
    "normalize_names",
    "standardize_dates",
    "validate_scores"
]

# File paths
DEFAULT_BACKUP_DIR = "backups"
DEFAULT_SCHEMA_FILE = "schema/evaluation_schema.json"

# CLI Configuration
MAX_TABLE_WIDTH = 120
MAX_DISPLAY_ROWS = 20
DEFAULT_OUTPUT_FORMAT = "table" 