"""
Data processing utilities for People Analytics.

This module provides functions for loading, parsing, and manipulating
data in various formats used in People Analytics workflows.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
import yaml

logger = logging.getLogger(__name__)


def read_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Read a JSON file and return its contents as a dictionary.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dict: Contents of the JSON file

    Raises:
        ValueError: If the file cannot be parsed as JSON
    """
    try:
        file_path = Path(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"File {file_path} is not valid JSON: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error reading file {file_path}: {str(e)}")


def write_json_file(
    data: Dict[str, Any],
    file_path: Union[str, Path],
    indent: int = 2,
    ensure_dir: bool = True,
) -> None:
    """
    Write a dictionary to a JSON file.

    Args:
        data: Dictionary to write
        file_path: Path to write the JSON file
        indent: Indentation level for the JSON file
        ensure_dir: Create the parent directory if it doesn't exist

    Raises:
        ValueError: If the data cannot be serialized as JSON
    """
    try:
        file_path = Path(file_path)

        if ensure_dir:
            file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    except Exception as e:
        raise ValueError(f"Error writing JSON to {file_path}: {str(e)}")


def read_yaml_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Read a YAML file and return its contents as a dictionary.

    Args:
        file_path: Path to the YAML file

    Returns:
        Dict: Contents of the YAML file

    Raises:
        ValueError: If the file cannot be parsed as YAML
    """
    try:
        file_path = Path(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"File {file_path} is not valid YAML: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error reading file {file_path}: {str(e)}")


def write_yaml_file(
    data: Dict[str, Any],
    file_path: Union[str, Path],
    ensure_dir: bool = True,
) -> None:
    """
    Write a dictionary to a YAML file.

    Args:
        data: Dictionary to write
        file_path: Path to write the YAML file
        ensure_dir: Create the parent directory if it doesn't exist

    Raises:
        ValueError: If the data cannot be serialized as YAML
    """
    try:
        file_path = Path(file_path)

        if ensure_dir:
            file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        raise ValueError(f"Error writing YAML to {file_path}: {str(e)}")


def read_csv_file(
    file_path: Union[str, Path],
    encoding: str = "utf-8",
    sep: str = ",",
    **kwargs,
) -> pd.DataFrame:
    """
    Read a CSV file and return its contents as a DataFrame.

    Args:
        file_path: Path to the CSV file
        encoding: File encoding
        sep: Delimiter to use
        **kwargs: Additional arguments to pass to pandas.read_csv

    Returns:
        DataFrame: Contents of the CSV file

    Raises:
        ValueError: If the file cannot be parsed as CSV
    """
    try:
        return pd.read_csv(file_path, encoding=encoding, sep=sep, **kwargs)
    except Exception as e:
        raise ValueError(f"Error reading CSV file {file_path}: {str(e)}")


def write_csv_file(
    df: pd.DataFrame,
    file_path: Union[str, Path],
    encoding: str = "utf-8",
    sep: str = ",",
    index: bool = False,
    ensure_dir: bool = True,
    **kwargs,
) -> None:
    """
    Write a DataFrame to a CSV file.

    Args:
        df: DataFrame to write
        file_path: Path to write the CSV file
        encoding: File encoding
        sep: Delimiter to use
        index: Whether to write row names (index)
        ensure_dir: Create the parent directory if it doesn't exist
        **kwargs: Additional arguments to pass to DataFrame.to_csv

    Raises:
        ValueError: If the DataFrame cannot be written to CSV
    """
    try:
        file_path = Path(file_path)

        if ensure_dir:
            file_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_csv(file_path, encoding=encoding, sep=sep, index=index, **kwargs)
    except Exception as e:
        raise ValueError(f"Error writing CSV to {file_path}: {str(e)}")


def read_excel_file(
    file_path: Union[str, Path],
    sheet_name: Optional[Union[str, int, List[str], List[int]]] = 0,
    **kwargs,
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Read an Excel file and return its contents as a DataFrame or dict of DataFrames.

    Args:
        file_path: Path to the Excel file
        sheet_name: Sheets to read (name, index, or list of names/indices)
        **kwargs: Additional arguments to pass to pandas.read_excel

    Returns:
        DataFrame or Dict[str, DataFrame]: Contents of the Excel file

    Raises:
        ValueError: If the file cannot be parsed as Excel
    """
    try:
        return pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
    except Exception as e:
        raise ValueError(f"Error reading Excel file {file_path}: {str(e)}")


def write_excel_file(
    df_dict: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
    file_path: Union[str, Path],
    sheet_name: str = "Sheet1",
    index: bool = False,
    ensure_dir: bool = True,
    **kwargs,
) -> None:
    """
    Write a DataFrame or dict of DataFrames to an Excel file.

    Args:
        df_dict: DataFrame or dict of DataFrames to write
        file_path: Path to write the Excel file
        sheet_name: Sheet name (used if df_dict is a DataFrame)
        index: Whether to write row names (index)
        ensure_dir: Create the parent directory if it doesn't exist
        **kwargs: Additional arguments to pass to DataFrame.to_excel

    Raises:
        ValueError: If the DataFrame cannot be written to Excel
    """
    try:
        file_path = Path(file_path)

        if ensure_dir:
            file_path.parent.mkdir(parents=True, exist_ok=True)

        # Handle both DataFrame and dict of DataFrames
        if isinstance(df_dict, pd.DataFrame):
            df_dict = {sheet_name: df_dict}

        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            for sheet, df in df_dict.items():
                df.to_excel(writer, sheet_name=sheet, index=index, **kwargs)
    except Exception as e:
        raise ValueError(f"Error writing Excel to {file_path}: {str(e)}")


def convert_json_to_df(
    data: Union[Dict[str, Any], List[Dict[str, Any]]],
    normalize: bool = False,
    record_path: Optional[Union[str, List[str]]] = None,
    **kwargs,
) -> pd.DataFrame:
    """
    Convert JSON data to a DataFrame.

    Args:
        data: JSON data (dict or list of dicts)
        normalize: Whether to normalize semi-structured JSON data
        record_path: Path to records in nested JSON data
        **kwargs: Additional arguments to pass to pd.json_normalize

    Returns:
        DataFrame: DataFrame representation of the JSON data

    Raises:
        ValueError: If the JSON data cannot be converted to a DataFrame
    """
    try:
        if normalize:
            if isinstance(data, dict) and record_path is not None:
                return pd.json_normalize(data, record_path=record_path, **kwargs)
            else:
                return pd.json_normalize(data, **kwargs)

        if isinstance(data, dict):
            return pd.DataFrame.from_dict(data, **kwargs)
        else:
            return pd.DataFrame(data)
    except Exception as e:
        raise ValueError(f"Error converting JSON to DataFrame: {str(e)}")


def flatten_dict(
    d: Dict[str, Any],
    parent_key: str = "",
    sep: str = "_",
) -> Dict[str, Any]:
    """
    Flatten a nested dictionary.

    Args:
        d: Dictionary to flatten
        parent_key: Parent key for nested keys
        sep: Separator to use between keys

    Returns:
        Dict: Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def extract_values_from_dict(
    d: Dict[str, Any],
    keys: List[str],
    default_value: Any = None,
) -> Dict[str, Any]:
    """
    Extract values for specified keys from a dictionary.

    Args:
        d: Dictionary to extract values from
        keys: Keys to extract
        default_value: Default value to use if key is not found

    Returns:
        Dict: Dictionary with extracted keys and values
    """
    return {k: d.get(k, default_value) for k in keys}


def merge_dicts(
    dicts: List[Dict[str, Any]],
    overwrite: bool = True,
) -> Dict[str, Any]:
    """
    Merge multiple dictionaries.

    Args:
        dicts: List of dictionaries to merge
        overwrite: Whether to overwrite values in case of key conflicts

    Returns:
        Dict: Merged dictionary
    """
    if not dicts:
        return {}

    result = dicts[0].copy()

    for d in dicts[1:]:
        if overwrite:
            result.update(d)
        else:
            for k, v in d.items():
                if k not in result:
                    result[k] = v

    return result


def load_data_from_file(
    file_path: Union[str, Path],
    file_format: Optional[str] = None,
    **kwargs,
) -> Union[Dict[str, Any], pd.DataFrame]:
    """
    Load data from a file based on its format.

    Args:
        file_path: Path to the file
        file_format: Format of the file (json, yaml, csv, excel)
                     If None, format is inferred from the file extension
        **kwargs: Additional arguments to pass to the reader function

    Returns:
        Dict or DataFrame: Contents of the file

    Raises:
        ValueError: If the file format is not supported or cannot be inferred
    """
    file_path = Path(file_path)

    if not file_format:
        suffix = file_path.suffix.lower()
        if suffix == ".json":
            file_format = "json"
        elif suffix in [".yaml", ".yml"]:
            file_format = "yaml"
        elif suffix == ".csv":
            file_format = "csv"
        elif suffix in [".xlsx", ".xls"]:
            file_format = "excel"
        else:
            raise ValueError(f"Could not infer file format from extension: {suffix}")

    file_format = file_format.lower()

    if file_format == "json":
        return read_json_file(file_path)
    elif file_format in ["yaml", "yml"]:
        return read_yaml_file(file_path)
    elif file_format == "csv":
        return read_csv_file(file_path, **kwargs)
    elif file_format in ["excel", "xlsx", "xls"]:
        return read_excel_file(file_path, **kwargs)
    else:
        raise ValueError(f"Unsupported file format: {file_format}")


def save_data_to_file(
    data: Union[Dict[str, Any], pd.DataFrame],
    file_path: Union[str, Path],
    file_format: Optional[str] = None,
    ensure_dir: bool = True,
    **kwargs,
) -> None:
    """
    Save data to a file based on its format.

    Args:
        data: Data to save (dict or DataFrame)
        file_path: Path to save the file
        file_format: Format of the file (json, yaml, csv, excel)
                     If None, format is inferred from the file extension
        ensure_dir: Create the parent directory if it doesn't exist
        **kwargs: Additional arguments to pass to the writer function

    Raises:
        ValueError: If the file format is not supported or cannot be inferred
    """
    file_path = Path(file_path)

    if not file_format:
        suffix = file_path.suffix.lower()
        if suffix == ".json":
            file_format = "json"
        elif suffix in [".yaml", ".yml"]:
            file_format = "yaml"
        elif suffix == ".csv":
            file_format = "csv"
        elif suffix in [".xlsx", ".xls"]:
            file_format = "excel"
        else:
            raise ValueError(f"Could not infer file format from extension: {suffix}")

    file_format = file_format.lower()

    if ensure_dir:
        file_path.parent.mkdir(parents=True, exist_ok=True)

    if file_format == "json":
        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient="records")
        write_json_file(data, file_path, ensure_dir=False, **kwargs)
    elif file_format in ["yaml", "yml"]:
        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient="records")
        write_yaml_file(data, file_path, ensure_dir=False, **kwargs)
    elif file_format == "csv":
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)
        write_csv_file(data, file_path, ensure_dir=False, **kwargs)
    elif file_format in ["excel", "xlsx", "xls"]:
        if not isinstance(data, pd.DataFrame) and not isinstance(data, dict):
            data = pd.DataFrame(data)
        write_excel_file(data, file_path, ensure_dir=False, **kwargs)
    else:
        raise ValueError(f"Unsupported file format: {file_format}")


def combine_data_frames(
    dfs: List[pd.DataFrame],
    how: str = "outer",
    on: Optional[Union[str, List[str]]] = None,
    **kwargs,
) -> pd.DataFrame:
    """
    Combine multiple DataFrames.

    Args:
        dfs: List of DataFrames to combine
        how: How to join the DataFrames ('outer', 'inner', 'left', 'right')
        on: Column(s) to join on
        **kwargs: Additional arguments to pass to DataFrame.merge

    Returns:
        DataFrame: Combined DataFrame

    Raises:
        ValueError: If the DataFrames cannot be combined
    """
    if not dfs:
        return pd.DataFrame()

    if len(dfs) == 1:
        return dfs[0].copy()

    result = dfs[0].copy()

    for df in dfs[1:]:
        if on is not None:
            result = result.merge(df, how=how, on=on, **kwargs)
        else:
            result = result.merge(df, how=how, **kwargs)

    return result


def group_and_aggregate(
    df: pd.DataFrame,
    group_by: Union[str, List[str]],
    agg_dict: Dict[str, Union[str, List[str]]],
) -> pd.DataFrame:
    """
    Group a DataFrame and apply aggregation functions.

    Args:
        df: DataFrame to group
        group_by: Column(s) to group by
        agg_dict: Dictionary mapping columns to aggregation functions

    Returns:
        DataFrame: Grouped and aggregated DataFrame

    Example:
        >>> group_and_aggregate(df, 'department', {'salary': ['mean', 'median'], 'age': 'mean'})
    """
    return df.groupby(group_by).agg(agg_dict).reset_index()


def pivot_data(
    df: pd.DataFrame,
    index: Union[str, List[str]],
    columns: str,
    values: Union[str, List[str]],
    aggfunc: str = "mean",
    fill_value: Optional[Any] = None,
) -> pd.DataFrame:
    """
    Pivot a DataFrame.

    Args:
        df: DataFrame to pivot
        index: Column(s) to use as index
        columns: Column to use as columns
        values: Column(s) to use as values
        aggfunc: Aggregation function to use
        fill_value: Value to use for missing values

    Returns:
        DataFrame: Pivoted DataFrame
    """
    return pd.pivot_table(
        df,
        index=index,
        columns=columns,
        values=values,
        aggfunc=aggfunc,
        fill_value=fill_value,
    ).reset_index()


def calculate_statistics(
    data: Union[List[float], np.ndarray, pd.Series],
) -> Dict[str, float]:
    """
    Calculate basic statistics for a data series.

    Args:
        data: Data to calculate statistics for

    Returns:
        Dict: Dictionary of statistics
    """
    if isinstance(data, pd.Series):
        data = data.dropna().values

    if len(data) == 0:
        return {
            "count": 0,
            "mean": np.nan,
            "median": np.nan,
            "min": np.nan,
            "max": np.nan,
            "std": np.nan,
            "q1": np.nan,
            "q3": np.nan,
        }

    return {
        "count": len(data),
        "mean": float(np.mean(data)),
        "median": float(np.median(data)),
        "min": float(np.min(data)),
        "max": float(np.max(data)),
        "std": float(np.std(data)),
        "q1": float(np.percentile(data, 25)),
        "q3": float(np.percentile(data, 75)),
    }


def detect_outliers(
    data: Union[List[float], np.ndarray, pd.Series],
    method: str = "iqr",
    threshold: float = 1.5,
) -> Union[List[bool], np.ndarray]:
    """
    Detect outliers in a data series.

    Args:
        data: Data to detect outliers in
        method: Method to use ('iqr' or 'zscore')
        threshold: Threshold for outlier detection

    Returns:
        List[bool] or np.ndarray: Boolean mask of outliers
    """
    if isinstance(data, pd.Series):
        data = data.dropna().values
    else:
        data = np.array(data)

    if len(data) == 0:
        return np.array([], dtype=bool)

    if method == "iqr":
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        return (data < lower_bound) | (data > upper_bound)

    elif method == "zscore":
        z_scores = (data - np.mean(data)) / np.std(data)
        return np.abs(z_scores) > threshold

    else:
        raise ValueError(f"Unsupported outlier detection method: {method}")


def normalize_data(
    data: Union[List[float], np.ndarray, pd.Series, pd.DataFrame],
    method: str = "minmax",
    columns: Optional[List[str]] = None,
) -> Union[np.ndarray, pd.DataFrame]:
    """
    Normalize data.

    Args:
        data: Data to normalize
        method: Method to use ('minmax', 'zscore', or 'robust')
        columns: Columns to normalize (if data is a DataFrame)

    Returns:
        np.ndarray or pd.DataFrame: Normalized data
    """
    if isinstance(data, pd.DataFrame):
        if columns is None:
            columns = data.select_dtypes(include=np.number).columns

        result = data.copy()

        for col in columns:
            if col in result.columns:
                result[col] = normalize_data(result[col], method=method)

        return result

    if isinstance(data, pd.Series):
        data = data.dropna().values
    else:
        data = np.array(data)

    if len(data) == 0:
        return data

    if method == "minmax":
        min_val = np.min(data)
        max_val = np.max(data)

        if min_val == max_val:
            return np.zeros_like(data)

        return (data - min_val) / (max_val - min_val)

    elif method == "zscore":
        mean_val = np.mean(data)
        std_val = np.std(data)

        if std_val == 0:
            return np.zeros_like(data)

        return (data - mean_val) / std_val

    elif method == "robust":
        median_val = np.median(data)
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1

        if iqr == 0:
            return np.zeros_like(data)

        return (data - median_val) / iqr

    else:
        raise ValueError(f"Unsupported normalization method: {method}")


def fill_missing_values(
    df: pd.DataFrame,
    method: str = "mean",
    columns: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Fill missing values in a DataFrame.

    Args:
        df: DataFrame with missing values
        method: Method to use ('mean', 'median', 'mode', 'ffill', 'bfill', or a constant value)
        columns: Columns to fill (default: all numeric columns)

    Returns:
        DataFrame: DataFrame with filled values
    """
    result = df.copy()

    if columns is None:
        columns = result.select_dtypes(include=np.number).columns

    for col in columns:
        if col not in result.columns:
            continue

        if result[col].isna().sum() == 0:
            continue

        if method == "mean":
            result[col] = result[col].fillna(result[col].mean())
        elif method == "median":
            result[col] = result[col].fillna(result[col].median())
        elif method == "mode":
            result[col] = result[col].fillna(result[col].mode()[0])
        elif method == "ffill":
            result[col] = result[col].ffill()
        elif method == "bfill":
            result[col] = result[col].bfill()
        else:
            # Assume method is a constant value
            result[col] = result[col].fillna(method)

    return result
