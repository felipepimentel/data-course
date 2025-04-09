class EvaluationAnalyzer:
    """Analyze evaluation data within a structured directory."""

    def __init__(self, base_path: str, use_cache: bool = True):
        """Initialize the evaluation analyzer.
        
        Args:
            base_path: Path to the directory containing evaluation data.
                Expected structure: <person>/<year>/resultado.json
            use_cache: Whether to cache results for faster lookups
        """
        self.base_path = base_path
        self.use_cache = use_cache
        self._cache = {}
        
        # Ensure the base directory exists
        os.makedirs(base_path, exist_ok=True)
        
        # Load schema manager for validation
        self.schema_manager = SchemaManager() 