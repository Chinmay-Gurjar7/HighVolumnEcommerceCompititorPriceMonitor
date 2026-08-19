import shutil
from datetime import datetime
from pathlib import Path

from entity.config_entity import DataSourceConfig, ArtifactConfig
from exception.exception import DataIngestionException
from logger.logger import get_logger


logger = get_logger(__name__)


class DataIngestion:

    def __init__(
        self,
        data_source_config: DataSourceConfig,
        artifact_config: ArtifactConfig
    ):
        self.data_source_config = data_source_config
        self.artifact_config = artifact_config

    def initiate_data_ingestion(self) -> Path:
        """
        Copies the source dataset into the raw artifact directory.

        The original source file is never modified.
        A timestamped copy is created in artifacts/raw/.
        """

        try:
            logger.info("========== DATA INGESTION STARTED ==========")

            source_file = Path(
                self.data_source_config.input_file
            )

            raw_directory = Path(
                self.artifact_config.raw_dir
            )

            logger.info(
                f"Source dataset: {source_file}"
            )

            logger.info(
                f"Raw artifact directory: {raw_directory}"
            )

            # --------------------------------------------------
            # 1. Check source file
            # --------------------------------------------------

            if not source_file.exists():
                raise FileNotFoundError(
                    f"Source dataset does not exist: {source_file}"
                )

            if not source_file.is_file():
                raise FileNotFoundError(
                    f"Source path is not a file: {source_file}"
                )

            # --------------------------------------------------
            # 2. Create raw directory
            # --------------------------------------------------

            raw_directory.mkdir(
                parents=True,
                exist_ok=True
            )

            # --------------------------------------------------
            # 3. Generate timestamp
            # --------------------------------------------------

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            raw_file_name = (
                f"{source_file.stem}_"
                f"{timestamp}"
                f"{source_file.suffix}"
            )

            raw_file_path = raw_directory / raw_file_name

            # --------------------------------------------------
            # 4. Copy source dataset
            # --------------------------------------------------

            shutil.copy2(
                source_file,
                raw_file_path
            )

            logger.info(
                f"Raw dataset successfully created: "
                f"{raw_file_path}"
            )

            logger.info(
                "========== DATA INGESTION COMPLETED =========="
            )

            return raw_file_path

        except Exception as error:

            logger.error(
                f"Data ingestion failed: {error}"
            )

            raise DataIngestionException(
                str(error)
            )