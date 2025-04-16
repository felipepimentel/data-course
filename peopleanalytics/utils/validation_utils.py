"""
Data validation utilities for People Analytics.

This module provides functions for validating data against schemas and business rules.
"""

from typing import Any, Dict, List, Tuple, Union

import jsonschema
import pandas as pd

from .logging_utils import get_module_logger

# Setup logger
logger = get_module_logger(__name__)


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """
    Validate data against a JSON schema.

    Args:
        data: The data to validate
        schema: The JSON schema to validate against

    Returns:
        List[str]: List of validation errors (empty if valid)
    """
    validator = jsonschema.Draft7Validator(schema)
    errors = []

    for error in validator.iter_errors(data):
        path = ".".join(str(p) for p in error.path) if error.path else "root"
        errors.append(f"Error at {path}: {error.message}")

    return errors


def validate_required_fields(
    data: Dict[str, Any], required_fields: List[str]
) -> List[str]:
    """
    Validate that the data contains all required fields.

    Args:
        data: The data to validate
        required_fields: List of required field names

    Returns:
        List[str]: List of missing fields (empty if all present)
    """
    missing_fields = []

    for field in required_fields:
        if field not in data:
            missing_fields.append(field)

    return missing_fields


def validate_data_types(data: Dict[str, Any], type_specs: Dict[str, type]) -> List[str]:
    """
    Validate that data fields have the correct types.

    Args:
        data: The data to validate
        type_specs: Dictionary mapping field names to expected types

    Returns:
        List[str]: List of type validation errors (empty if all valid)
    """
    type_errors = []

    for field, expected_type in type_specs.items():
        if field in data:
            value = data[field]
            # Handle special case of checking for None when type is Optional
            if (
                value is None
                and hasattr(expected_type, "__origin__")
                and expected_type.__origin__ is Union
            ):
                # This is an Optional type (Union with NoneType)
                continue

            # Regular type check
            if not isinstance(value, expected_type):
                type_errors.append(
                    f"Field '{field}' has type {type(value).__name__}, expected {expected_type.__name__}"
                )

    return type_errors


def validate_numeric_ranges(
    data: Dict[str, Any], range_specs: Dict[str, Tuple[float, float]]
) -> List[str]:
    """
    Validate that numeric fields are within specified ranges.

    Args:
        data: The data to validate
        range_specs: Dictionary mapping field names to (min, max) tuples

    Returns:
        List[str]: List of range validation errors (empty if all valid)
    """
    range_errors = []

    for field, (min_val, max_val) in range_specs.items():
        if field in data:
            value = data[field]
            if isinstance(value, (int, float)):
                if value < min_val or value > max_val:
                    range_errors.append(
                        f"Field '{field}' value {value} is outside the valid range [{min_val}, {max_val}]"
                    )
            else:
                range_errors.append(f"Field '{field}' is not numeric (value: {value})")

    return range_errors


def validate_enum_values(
    data: Dict[str, Any], enum_specs: Dict[str, List[Any]]
) -> List[str]:
    """
    Validate that enum fields have allowed values.

    Args:
        data: The data to validate
        enum_specs: Dictionary mapping field names to lists of allowed values

    Returns:
        List[str]: List of enum validation errors (empty if all valid)
    """
    enum_errors = []

    for field, allowed_values in enum_specs.items():
        if field in data:
            value = data[field]
            if value not in allowed_values:
                enum_errors.append(
                    f"Field '{field}' value '{value}' is not in allowed values: {allowed_values}"
                )

    return enum_errors


def validate_string_patterns(
    data: Dict[str, Any], pattern_specs: Dict[str, str]
) -> List[str]:
    """
    Validate that string fields match regex patterns.

    Args:
        data: The data to validate
        pattern_specs: Dictionary mapping field names to regex patterns

    Returns:
        List[str]: List of pattern validation errors (empty if all valid)
    """
    import re

    pattern_errors = []

    for field, pattern in pattern_specs.items():
        if field in data and isinstance(data[field], str):
            value = data[field]
            if not re.match(pattern, value):
                pattern_errors.append(
                    f"Field '{field}' value '{value}' does not match pattern '{pattern}'"
                )

    return pattern_errors


def validate_dependencies(
    data: Dict[str, Any], dependency_specs: Dict[str, List[str]]
) -> List[str]:
    """
    Validate field dependencies (if field A is present, field B must also be present).

    Args:
        data: The data to validate
        dependency_specs: Dictionary mapping fields to lists of dependent fields

    Returns:
        List[str]: List of dependency validation errors (empty if all valid)
    """
    dependency_errors = []

    for field, dependents in dependency_specs.items():
        if field in data and data[field] is not None:
            for dependent in dependents:
                if dependent not in data or data[dependent] is None:
                    dependency_errors.append(
                        f"Field '{dependent}' must be present when '{field}' is provided"
                    )

    return dependency_errors


def validate_data_consistency(
    data: Dict[str, Any], consistency_rules: List[callable]
) -> List[str]:
    """
    Validate data consistency using custom rule functions.

    Args:
        data: The data to validate
        consistency_rules: List of functions that check consistency
                           Each function should take the data dict and return a list of errors

    Returns:
        List[str]: List of consistency validation errors (empty if all valid)
    """
    consistency_errors = []

    for rule_func in consistency_rules:
        rule_errors = rule_func(data)
        consistency_errors.extend(rule_errors)

    return consistency_errors


def validate_dataframe(df: pd.DataFrame, schema: Dict[str, Any]) -> List[str]:
    """
    Validate a pandas DataFrame against a schema.

    Args:
        df: DataFrame to validate
        schema: Dictionary with validation rules
               {
                   "columns": ["col1", "col2"],  # Required columns
                   "types": {"col1": "int", "col2": "string"},  # Expected types
                   "non_null": ["col1"],  # Columns that should not have nulls
                   "unique": ["col1"]  # Columns with unique values
               }

    Returns:
        List[str]: List of validation errors (empty if valid)
    """
    errors = []

    # Check required columns
    if "columns" in schema:
        missing_cols = [col for col in schema["columns"] if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")

    # Check column types
    if "types" in schema:
        for col, expected_type in schema["types"].items():
            if col in df.columns:
                # Convert pandas dtype strings to more readable format
                actual_type = str(df[col].dtype)
                if expected_type.lower() not in actual_type.lower():
                    errors.append(
                        f"Column '{col}' has type {actual_type}, expected {expected_type}"
                    )

    # Check non-null columns
    if "non_null" in schema:
        for col in schema["non_null"]:
            if col in df.columns and df[col].isnull().any():
                null_count = df[col].isnull().sum()
                errors.append(
                    f"Column '{col}' has {null_count} null values but should not be null"
                )

    # Check unique columns
    if "unique" in schema:
        for col in schema["unique"]:
            if col in df.columns and not df[col].is_unique:
                duplicate_count = len(df) - df[col].nunique()
                errors.append(
                    f"Column '{col}' has {duplicate_count} duplicate values but should be unique"
                )

    return errors
