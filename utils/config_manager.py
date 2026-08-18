from pathlib import Path
from typing import Any
import os
import re

from dotenv import load_dotenv

from entity.config_entity import (
    ProjectConfig,
    DataSourceConfig,
    ArtifactConfig,
    DatabaseConfig,
    PipelineConfig,
    ValidationConfig,
    LoggingConfig,
)

from utils.common import read_yaml_file


class ConfigurationManager:
    """
    Loads YAML configuration and converts it into
    strongly typed configuration objects.
    """

    def __init__(
        self,
        config_file_path: str = "config/config.yaml"
    ):
        self.config_file_path = Path(config_file_path)

        # Project root directory
        self.project_root = Path.cwd()

        # Explicitly load .env from project root
        env_file = self.project_root / ".env"

        if env_file.exists():
            load_dotenv(
                dotenv_path=env_file,
                override=False
            )

        # Load YAML configuration
        self.config = read_yaml_file(
            self.config_file_path
        )

        # Resolve environment variables
        self._resolve_environment_variables()

    def _resolve_environment_variables(self) -> None:
        """
        Replace placeholders such as:

        ${POSTGRES_USER}

        with values from environment variables.
        """

        def resolve(value: Any) -> Any:

            if isinstance(value, dict):
                return {
                    key: resolve(item)
                    for key, item in value.items()
                }

            if isinstance(value, list):
                return [
                    resolve(item)
                    for item in value
                ]

            if isinstance(value, str):

                pattern = r"\$\{([^}]+)\}"

                def replace(match):
                    variable_name = match.group(1)

                    environment_value = os.getenv(
                        variable_name
                    )

                    if environment_value is None:
                        raise EnvironmentError(
                            f"Environment variable "
                            f"'{variable_name}' is not set."
                        )

                    return environment_value

                return re.sub(
                    pattern,
                    replace,
                    value
                )

            return value

        self.config = resolve(self.config)

    def get_project_config(self) -> ProjectConfig:

        config = self.config["project"]

        return ProjectConfig(
            name=config["name"],
            version=config["version"],
            environment=config["environment"],
        )

    def get_data_source_config(self) -> DataSourceConfig:

        config = self.config["data_source"]

        return DataSourceConfig(
            name=config["name"],
            type=config["type"],
            input_file=Path(
                config["input_file"]
            ),
        )

    def get_artifact_config(self) -> ArtifactConfig:

        config = self.config["artifacts"]

        return ArtifactConfig(
            root_dir=Path(
                config["root_dir"]
            ),
            raw_dir=Path(
                config["raw_dir"]
            ),
            processed_dir=Path(
                config["processed_dir"]
            ),
            failed_dir=Path(
                config["failed_dir"]
            ),
            reports_dir=Path(
                config["reports_dir"]
            ),
        )

    def get_database_config(self) -> DatabaseConfig:

        config = self.config["database"]

        return DatabaseConfig(
            host=config["host"],
            port=int(config["port"]),
            name=config["name"],
            username=config["username"],
            password=config["password"],
        )

    def get_pipeline_config(self) -> PipelineConfig:

        config = self.config["pipeline"]

        return PipelineConfig(
            batch_size=int(
                config["batch_size"]
            ),
            enable_validation=bool(
                config["enable_validation"]
            ),
            enable_logging=bool(
                config["enable_logging"]
            ),
        )

    def get_validation_config(self) -> ValidationConfig:

        config = self.config["validation"]

        return ValidationConfig(
            required_columns=config[
                "required_columns"
            ],
            allow_duplicates=bool(
                config["allow_duplicates"]
            ),
            allow_null_prices=bool(
                config["allow_null_prices"]
            ),
            minimum_price=float(
                config["minimum_price"]
            ),
        )

    def get_logging_config(self) -> LoggingConfig:

        config = self.config["logging"]

        return LoggingConfig(
            log_dir=Path(
                config["log_dir"]
            ),
            log_file=config["log_file"],
            level=config["level"],
        )