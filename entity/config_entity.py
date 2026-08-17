from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class ProjectConfig:
    name: str
    version: str
    environment: str


@dataclass(frozen=True)
class DataSourceConfig:
    name: str
    type: str
    input_file: Path


@dataclass(frozen=True)
class ArtifactConfig:
    root_dir: Path
    raw_dir: Path
    processed_dir: Path
    failed_dir: Path
    reports_dir: Path


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    name: str
    username: str
    password: str


@dataclass(frozen=True)
class PipelineConfig:
    batch_size: int
    enable_validation: bool
    enable_logging: bool


@dataclass(frozen=True)
class ValidationConfig:
    required_columns: List[str]
    allow_duplicates: bool
    allow_null_prices: bool
    minimum_price: float


@dataclass(frozen=True)
class LoggingConfig:
    log_dir: Path
    log_file: str
    level: str