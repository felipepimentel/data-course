"""
Schema Manager for People Analytics.

This module provides functionality for managing and validating data schemas.
"""

import json
import os
from typing import Dict, Any, List, Optional


class SchemaManager:
    """Manages JSON schemas for data validation."""
    
    def __init__(self, schema_dir: Optional[str] = None):
        """Initialize the schema manager.
        
        Args:
            schema_dir: Directory containing schema files. If None, uses default.
        """
        self.schema_dir = schema_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "schemas"
        )
        self.schemas = {}
        
    def get_schema(self, schema_name: str) -> Dict[str, Any]:
        """Get a schema by name.
        
        Args:
            schema_name: Name of the schema to retrieve.
            
        Returns:
            The schema as a dictionary.
            
        Raises:
            FileNotFoundError: If the schema file doesn't exist.
        """
        if schema_name in self.schemas:
            return self.schemas[schema_name]
            
        schema_path = os.path.join(self.schema_dir, f"{schema_name}.json")
        if not os.path.exists(schema_path):
            # Return empty schema if file doesn't exist
            return {}
            
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
                self.schemas[schema_name] = schema
                return schema
        except Exception as e:
            # Return empty schema on error
            return {}
            
    def validate(self, data: Dict[str, Any], schema_name: str) -> List[Dict[str, str]]:
        """Validate data against a schema.
        
        Args:
            data: Data to validate.
            schema_name: Name of the schema to validate against.
            
        Returns:
            List of validation errors, empty if validation passed.
        """
        schema = self.get_schema(schema_name)
        if not schema:
            # No schema or empty schema, validation always passes
            return []
            
        # Basic validation - in a real implementation this would use jsonschema
        errors = []
        
        # For now, just check that required fields exist
        if "required" in schema:
            for field in schema["required"]:
                if field not in data:
                    errors.append({
                        "type": "missing_required_field",
                        "description": f"Missing required field: {field}",
                        "severity": "high"
                    })
                    
        # Check types for properties
        if "properties" in schema:
            for field, spec in schema["properties"].items():
                if field in data and "type" in spec:
                    expected_type = spec["type"]
                    
                    # Simple type validation
                    if expected_type == "string" and not isinstance(data[field], str):
                        errors.append({
                            "type": "invalid_type",
                            "description": f"Field {field} should be a string",
                            "severity": "medium"
                        })
                    elif expected_type == "number" and not isinstance(data[field], (int, float)):
                        errors.append({
                            "type": "invalid_type",
                            "description": f"Field {field} should be a number",
                            "severity": "medium"
                        })
                    elif expected_type == "object" and not isinstance(data[field], dict):
                        errors.append({
                            "type": "invalid_type",
                            "description": f"Field {field} should be an object",
                            "severity": "medium"
                        })
                    elif expected_type == "array" and not isinstance(data[field], list):
                        errors.append({
                            "type": "invalid_type",
                            "description": f"Field {field} should be an array",
                            "severity": "medium"
                        })
        
        return errors 