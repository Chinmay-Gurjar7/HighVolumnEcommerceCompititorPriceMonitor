from logger.logger import get_logger
from utils.config_manager import ConfigurationManager
from components.data_ingestion import DataIngestion


logger = get_logger(__name__)


def run_data_ingestion():
    try:
        logger.info("Starting data ingestion pipeline")

        config_manager = ConfigurationManager()

        data_source_config = (
            config_manager.get_data_source_config()
        )

        artifact_config = (
            config_manager.get_artifact_config()
        )

        data_ingestion = DataIngestion(
            data_source_config=data_source_config,
            artifact_config=artifact_config
        )

        raw_file_path = (
            data_ingestion.initiate_data_ingestion()
        )

        logger.info(
            f"Data ingestion completed successfully: "
            f"{raw_file_path}"
        )

    except Exception as error:
        logger.exception(
            f"Data ingestion pipeline failed: {error}"
        )
        raise


if __name__ == "__main__":
    run_data_ingestion()