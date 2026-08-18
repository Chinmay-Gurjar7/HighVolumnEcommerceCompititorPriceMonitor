import json
import os
from pathlib import Path
from typing import Any, Dict

import yaml


def read_yaml_file(file_path: str | Path) -> Dict[str, Any]:
    """
    Read a YAML configuration file and return its contents as a dictionary.

    Args:
        file_path: Path to the YAML file.

    Returns:
        Dictionary containing the YAML configuration.

    Raises:
        FileNotFoundError: If the YAML file does not exist.
        ValueError: If the YAML file is empty or invalid.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {file_path}"
        )

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = yaml.safe_load(file)

        if content is None:
            raise ValueError(
                f"Configuration file is empty: {file_path}"
            )

        return content

    except yaml.YAMLError as error:
        raise ValueError(
            f"Invalid YAML configuration: {file_path}"
        ) from error


def write_yaml_file(
    file_path: str | Path,
    data: Dict[str, Any]
) -> None:
    """
    Write a dictionary to a YAML file.
    """

    file_path = Path(file_path)

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(file_path, "w", encoding="utf-8") as file:
        yaml.safe_dump(
            data,
            file,
            default_flow_style=False,
            sort_keys=False
        )


def read_json_file(file_path: str | Path) -> Any:
    """
    Read a JSON file.

    Args:
        file_path: Path to JSON file.

    Returns:
        Parsed JSON data.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"JSON file not found: {file_path}"
        )

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json_file(
    file_path: str | Path,
    data: Any
) -> None:
    """
    Write data to a JSON file.
    """

    file_path = Path(file_path)

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def create_directories(*directories: str | Path) -> None:
    """
    Create multiple directories if they don't already exist.
    """

    for directory in directories:
        Path(directory).mkdir(
            parents=True,
            exist_ok=True
        )


def get_file_size(file_path: str | Path) -> float:
    """
    Return file size in MB.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    size_in_bytes = os.path.getsize(file_path)

    return round(
        size_in_bytes / (1024 * 1024),
        2
    )


def get_timestamp() -> str:
    """
    Return the current timestamp in a filesystem-friendly format.

    Example:
        20260818_143025
    """

    from datetime import datetime

    return datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )