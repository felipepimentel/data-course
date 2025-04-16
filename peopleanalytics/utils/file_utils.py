"""
File utilities for People Analytics.

This module provides functions for file validation, processing,
and handling various file formats.
"""

import csv
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import pandas as pd
import yaml

from peopleanalytics.utils.logging_utils import get_module_logger

logger = get_module_logger(__name__)

# Common file extensions
JSON_EXTENSIONS = {".json"}
YAML_EXTENSIONS = {".yaml", ".yml"}
CSV_EXTENSIONS = {".csv"}
EXCEL_EXTENSIONS = {".xlsx", ".xls"}
TEXT_EXTENSIONS = {".txt", ".md"}

# Supported file formats
SUPPORTED_FORMATS = {
    "json": (".json",),
    "yaml": (".yaml", ".yml"),
    "csv": (".csv",),
    "excel": (".xlsx", ".xls"),
}

# All supported extensions
ALL_SUPPORTED_EXTENSIONS = set(
    ext for exts in SUPPORTED_FORMATS.values() for ext in exts
)


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        Path: Path object for the directory
    """
    if isinstance(path, str):
        path = Path(path)

    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_extension(file_path: Union[str, Path]) -> str:
    """
    Get the file extension (lowercase) from a path.

    Args:
        file_path: Path to the file

    Returns:
        str: Lowercase file extension with dot (e.g., '.json')
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    return file_path.suffix.lower()


def is_json_file(file_path: Union[str, Path]) -> bool:
    """Check if file is a JSON file based on extension."""
    return get_file_extension(file_path) in JSON_EXTENSIONS


def is_yaml_file(file_path: Union[str, Path]) -> bool:
    """Check if file is a YAML file based on extension."""
    return get_file_extension(file_path) in YAML_EXTENSIONS


def is_csv_file(file_path: Union[str, Path]) -> bool:
    """Check if file is a CSV file based on extension."""
    return get_file_extension(file_path) in CSV_EXTENSIONS


def is_excel_file(file_path: Union[str, Path]) -> bool:
    """Check if file is an Excel file based on extension."""
    return get_file_extension(file_path) in EXCEL_EXTENSIONS


def is_text_file(file_path: Union[str, Path]) -> bool:
    """Check if file is a text file based on extension."""
    return get_file_extension(file_path) in TEXT_EXTENSIONS


def read_file(file_path: Union[str, Path]) -> Any:
    """
    Read a file and return its contents based on file type.

    Args:
        file_path: Path to the file

    Returns:
        The file contents in appropriate format:
        - dict or list for JSON/YAML
        - list of rows for CSV
        - pandas DataFrame for Excel
        - string for text files

    Raises:
        ValueError: If file type is not supported
        IOError: If file cannot be read
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        if is_json_file(file_path):
            return read_json(file_path)
        elif is_yaml_file(file_path):
            return read_yaml(file_path)
        elif is_csv_file(file_path):
            return read_csv(file_path)
        elif is_excel_file(file_path):
            return read_excel(file_path)
        elif is_text_file(file_path):
            return read_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        raise


def read_json(file_path: Union[str, Path]) -> Union[Dict, List]:
    """
    Read a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dict or List: The parsed JSON data
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_yaml(file_path: Union[str, Path]) -> Union[Dict, List]:
    """
    Read a YAML file.

    Args:
        file_path: Path to the YAML file

    Returns:
        Dict or List: The parsed YAML data
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_csv(
    file_path: Union[str, Path], as_dict: bool = False
) -> Union[List[List], List[Dict]]:
    """
    Read a CSV file.

    Args:
        file_path: Path to the CSV file
        as_dict: If True, return list of dicts, otherwise list of lists

    Returns:
        List: The CSV data
    """
    with open(file_path, "r", encoding="utf-8", newline="") as f:
        if as_dict:
            reader = csv.DictReader(f)
            return list(reader)
        else:
            reader = csv.reader(f)
            return list(reader)


def read_excel(
    file_path: Union[str, Path], sheet_name: Optional[str] = None
) -> pd.DataFrame:
    """
    Read an Excel file.

    Args:
        file_path: Path to the Excel file
        sheet_name: Name of sheet to read (None for first sheet)

    Returns:
        pandas.DataFrame: The Excel data
    """
    return pd.read_excel(file_path, sheet_name=sheet_name)


def read_text(file_path: Union[str, Path]) -> str:
    """
    Read a text file.

    Args:
        file_path: Path to the text file

    Returns:
        str: The file contents
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_json(
    data: Union[Dict, List], file_path: Union[str, Path], indent: int = 2
) -> None:
    """
    Write data to a JSON file.

    Args:
        data: The data to write
        file_path: Path to the output file
        indent: JSON indentation level
    """
    ensure_directory(Path(file_path).parent)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def write_yaml(data: Union[Dict, List], file_path: Union[str, Path]) -> None:
    """
    Write data to a YAML file.

    Args:
        data: The data to write
        file_path: Path to the output file
    """
    ensure_directory(Path(file_path).parent)

    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)


def write_csv(
    data: Union[List[List], List[Dict]],
    file_path: Union[str, Path],
    fieldnames: Optional[List[str]] = None,
) -> None:
    """
    Write data to a CSV file.

    Args:
        data: The data to write (list of lists or list of dicts)
        file_path: Path to the output file
        fieldnames: Column names (required for list of dicts if first item is empty)
    """
    ensure_directory(Path(file_path).parent)

    with open(file_path, "w", encoding="utf-8", newline="") as f:
        if data and isinstance(data[0], dict):
            if not fieldnames and not data[0]:
                raise ValueError(
                    "fieldnames is required when data contains empty dictionaries"
                )

            writer = csv.DictWriter(f, fieldnames=fieldnames or list(data[0].keys()))
            writer.writeheader()
            writer.writerows(data)
        else:
            writer = csv.writer(f)
            writer.writerows(data)


def write_excel(data: Dict[str, pd.DataFrame], file_path: Union[str, Path]) -> None:
    """
    Write data to an Excel file with multiple sheets.

    Args:
        data: Dict mapping sheet names to DataFrames
        file_path: Path to the output file
    """
    ensure_directory(Path(file_path).parent)

    with pd.ExcelWriter(file_path) as writer:
        for sheet_name, df in data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)


def find_files(
    directory: Union[str, Path],
    pattern: str = "*",
    recursive: bool = False,
    file_types: Optional[Set[str]] = None,
) -> List[Path]:
    """
    Find files in a directory matching a pattern and/or file types.

    Args:
        directory: Directory to search
        pattern: Glob pattern to match
        recursive: Whether to search subdirectories
        file_types: Set of file extensions to include (e.g., {'.json', '.yaml'})

    Returns:
        List[Path]: List of matching file paths
    """
    if isinstance(directory, str):
        directory = Path(directory)

    if not directory.exists():
        logger.warning(f"Directory does not exist: {directory}")
        return []

    # Find files matching pattern
    if recursive:
        files = list(directory.glob(f"**/{pattern}"))
    else:
        files = list(directory.glob(pattern))

    # Filter by file type if specified
    if file_types:
        files = [f for f in files if f.is_file() and f.suffix.lower() in file_types]
    else:
        files = [f for f in files if f.is_file()]

    return sorted(files)


def create_timestamped_directory(base_dir: Union[str, Path], prefix: str = "") -> Path:
    """
    Create a directory with a timestamp in the name.

    Args:
        base_dir: Base directory
        prefix: Prefix for directory name

    Returns:
        Path: Path to the created directory
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_name = f"{prefix}_{timestamp}" if prefix else timestamp

    path = Path(base_dir) / dir_name
    path.mkdir(parents=True, exist_ok=True)

    return path


def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get information about a file.

    Args:
        file_path: Path to the file

    Returns:
        Dict: Information about the file
    """
    path = Path(file_path)
    stat = path.stat()

    return {
        "name": path.name,
        "path": str(path),
        "size": stat.st_size,
        "created": datetime.fromtimestamp(stat.st_ctime),
        "modified": datetime.fromtimestamp(stat.st_mtime),
        "extension": path.suffix,
        "is_directory": path.is_dir(),
    }


def backup_file(
    file_path: Union[str, Path], backup_dir: Optional[Union[str, Path]] = None
) -> Path:
    """
    Create a backup of a file.

    Args:
        file_path: Path to the file to backup
        backup_dir: Directory for backups (uses file's directory if None)

    Returns:
        Path: Path to the backup file
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # Use file's directory if backup_dir not specified
    if backup_dir is None:
        backup_dir = path.parent / "backups"
    else:
        backup_dir = Path(backup_dir)

    # Create backup directory
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Create backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{path.stem}_{timestamp}{path.suffix}"

    # Copy file
    import shutil

    shutil.copy2(path, backup_path)

    logger.info(f"Created backup: {backup_path}")
    return backup_path


def get_file_format(file_path: Union[str, Path]) -> Optional[str]:
    """
    Determine the format of a file based on its extension.

    Args:
        file_path: Path to the file

    Returns:
        str: Format name or None if not recognized
    """
    path = Path(file_path)
    extension = path.suffix.lower()

    for format_name, extensions in SUPPORTED_FORMATS.items():
        if extension in extensions:
            return format_name

    return None


def filter_files_by_format(
    files: List[Union[str, Path]], formats: Union[str, List[str]] = "all"
) -> List[Path]:
    """
    Filter a list of files by format.

    Args:
        files: List of file paths
        formats: Format names to include or "all" for all formats

    Returns:
        List[Path]: Filtered list of file paths
    """
    if formats == "all":
        valid_extensions = ALL_SUPPORTED_EXTENSIONS
    else:
        if isinstance(formats, str):
            formats = [formats]

        valid_extensions = set()
        for fmt in formats:
            if fmt in SUPPORTED_FORMATS:
                valid_extensions.update(SUPPORTED_FORMATS[fmt])

    filtered_files = []
    for file in files:
        path = Path(file)
        if path.suffix.lower() in valid_extensions:
            filtered_files.append(path)

    return filtered_files


def is_valid_json_file(file_path: Union[str, Path]) -> bool:
    """
    Check if a file is a valid JSON file.

    Args:
        file_path: Path to the file

    Returns:
        bool: True if valid JSON, False otherwise
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            json.load(f)
        return True
    except Exception:
        return False


def is_valid_yaml_file(file_path: Union[str, Path]) -> bool:
    """
    Check if a file is a valid YAML file.

    Args:
        file_path: Path to the file

    Returns:
        bool: True if valid YAML, False otherwise
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            yaml.safe_load(f)
        return True
    except Exception:
        return False


def is_valid_csv_file(file_path: Union[str, Path]) -> bool:
    """
    Check if a file is a valid CSV file.

    Args:
        file_path: Path to the file

    Returns:
        bool: True if valid CSV, False otherwise
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            csv_reader = csv.reader(f)
            # Read at least one row to confirm it's valid
            next(csv_reader)
        return True
    except Exception:
        return False


def is_valid_excel_file(file_path: Union[str, Path]) -> bool:
    """
    Check if a file is a valid Excel file.

    Args:
        file_path: Path to the file

    Returns:
        bool: True if valid Excel, False otherwise
    """
    try:
        pd.read_excel(file_path, sheet_name=None, nrows=1)
        return True
    except Exception:
        return False


def validate_file(file_path: Union[str, Path]) -> Tuple[bool, str, Optional[str]]:
    """
    Validate a file and determine its format.

    Args:
        file_path: Path to the file

    Returns:
        Tuple[bool, str, Optional[str]]: (is_valid, message, format)
    """
    path = Path(file_path)

    if not path.exists():
        return False, f"File not found: {path}", None

    if not path.is_file():
        return False, f"Not a file: {path}", None

    format_name = get_file_format(path)
    if not format_name:
        return False, f"Unsupported file format: {path.suffix}", None

    # Check file validity based on format
    is_valid = False
    if format_name == "json":
        is_valid = is_valid_json_file(path)
    elif format_name == "yaml":
        is_valid = is_valid_yaml_file(path)
    elif format_name == "csv":
        is_valid = is_valid_csv_file(path)
    elif format_name == "excel":
        is_valid = is_valid_excel_file(path)

    message = (
        f"Valid {format_name.upper()} file"
        if is_valid
        else f"Invalid {format_name.upper()} file"
    )
    return is_valid, message, format_name


def load_data_from_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load data from a file based on its format.

    Args:
        file_path: Path to the file

    Returns:
        Dict: Data from the file

    Raises:
        ValueError: If file is invalid or unsupported
    """
    is_valid, message, format_name = validate_file(file_path)

    if not is_valid:
        raise ValueError(message)

    path = Path(file_path)

    if format_name == "json":
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    elif format_name == "yaml":
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    elif format_name == "csv":
        df = pd.read_csv(path, encoding="utf-8")
        return df.to_dict(orient="records")

    elif format_name == "excel":
        df = pd.read_excel(path)
        return df.to_dict(orient="records")

    raise ValueError(f"Unsupported format: {format_name}")


def save_data_to_file(
    data: Any,
    file_path: Union[str, Path],
    format_name: Optional[str] = None,
    create_parent_dirs: bool = True,
) -> None:
    """
    Save data to a file in the specified format.

    Args:
        data: Data to save
        file_path: Path to save the file
        format_name: Format to save as (if None, determined from extension)
        create_parent_dirs: Whether to create parent directories

    Raises:
        ValueError: If format is unsupported
    """
    path = Path(file_path)

    # Determine format from file extension if not specified
    if format_name is None:
        format_name = get_file_format(path)
        if format_name is None:
            raise ValueError(f"Unsupported file extension: {path.suffix}")

    # Create parent directories if needed
    if create_parent_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)

    if format_name == "json":
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    elif format_name == "yaml":
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False, allow_unicode=True)

    elif format_name == "csv":
        df = pd.DataFrame(data)
        df.to_csv(path, index=False, encoding="utf-8")

    elif format_name == "excel":
        df = pd.DataFrame(data)
        df.to_excel(path, index=False)

    else:
        raise ValueError(f"Unsupported format: {format_name}")


def list_files_recursive(
    directory: Union[str, Path],
    pattern: Optional[str] = None,
    exclude_dirs: Optional[List[str]] = None,
) -> List[Path]:
    """
    List all files in a directory and its subdirectories.

    Args:
        directory: Directory to search
        pattern: Glob pattern to match files
        exclude_dirs: List of directory names to exclude

    Returns:
        List[Path]: List of file paths
    """
    directory = Path(directory)
    exclude_dirs = set(exclude_dirs) if exclude_dirs else set()

    all_files = []

    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            file_path = Path(root) / file

            # Skip hidden files
            if file.startswith("."):
                continue

            # Apply pattern filter if specified
            if pattern and not file_path.match(pattern):
                continue

            all_files.append(file_path)

    return all_files


def create_directory_structure(
    base_dir: Union[str, Path],
    structure: Dict[str, Any],
) -> None:
    """
    Create a directory structure from a dictionary.

    Args:
        base_dir: Base directory
        structure: Dictionary defining the structure

    Example:
        create_directory_structure('/path/to/base', {
            'dir1': {},
            'dir2': {
                'subdir1': {},
                'subdir2': {},
            }
        })
    """
    base_path = Path(base_dir)

    def _create_structure(path, struct):
        path.mkdir(parents=True, exist_ok=True)

        for name, content in struct.items():
            child_path = path / name

            if isinstance(content, dict):
                _create_structure(child_path, content)
            elif content is None:
                # Empty file
                child_path.touch()
            else:
                # File with content
                with open(child_path, "w", encoding="utf-8") as f:
                    if isinstance(content, (dict, list)):
                        json.dump(content, f, ensure_ascii=False, indent=2)
                    else:
                        f.write(str(content))

    _create_structure(base_path, structure)


def compress_directory(
    source_dir: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    format: str = "zip",
) -> Path:
    """
    Compress a directory.

    Args:
        source_dir: Directory to compress
        output_path: Path to save the compressed file (if None, uses source_dir name)
        format: Compression format ('zip', 'tar', 'gztar', 'bztar', or 'xztar')

    Returns:
        Path: Path to the compressed file
    """
    source_dir = Path(source_dir)

    if not source_dir.exists():
        raise FileNotFoundError(f"Directory not found: {source_dir}")

    if not source_dir.is_dir():
        raise ValueError(f"Not a directory: {source_dir}")

    if output_path is None:
        output_path = source_dir.with_suffix(f".{format}")
    else:
        output_path = Path(output_path)

    # Create parent directories if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Compress directory
    base_name = str(output_path.with_suffix(""))
    root_dir = str(source_dir.parent)
    base_dir = source_dir.name

    output_filename = shutil.make_archive(base_name, format, root_dir, base_dir)

    return Path(output_filename)


def get_file_size(
    file_path: Union[str, Path], human_readable: bool = False
) -> Union[int, str]:
    """
    Get the size of a file.

    Args:
        file_path: Path to the file
        human_readable: Whether to return human-readable size

    Returns:
        Union[int, str]: File size in bytes or human-readable format
    """
    path = Path(file_path)
    size_bytes = path.stat().st_size

    if human_readable:
        # Convert to human-readable format
        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        size = float(size_bytes)

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        return f"{size:.2f} {units[unit_index]}"

    return size_bytes


def get_file_modification_time(
    file_path: Union[str, Path], as_datetime: bool = False
) -> Union[float, datetime]:
    """
    Get the modification time of a file.

    Args:
        file_path: Path to the file
        as_datetime: Whether to return as datetime object

    Returns:
        Union[float, datetime]: Modification time
    """
    path = Path(file_path)
    mtime = path.stat().st_mtime

    if as_datetime:
        return datetime.fromtimestamp(mtime)

    return mtime


def ensure_dir_exists(directory: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory: Directory path

    Returns:
        Path: Path to the directory
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path
