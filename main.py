from logger.logger import get_logger
from utils.config_manager import ConfigurationManager

from components.data_ingestion import DataIngestion
from components.data_validation import DataValidation
from components.data_transformation import DataTransformation
from components.data_loading import DataLoading


logger = get_logger(__name__)


def run_pipeline():
    try:
        logger.info("========== PIPELINE STARTED ==========")

        # ==================================================
        # 1. LOAD CONFIGURATION
        # ==================================================

        config_manager = ConfigurationManager()

        data_source_config = (
            config_manager.get_data_source_config()
        )

        artifact_config = (
            config_manager.get_artifact_config()
        )

        validation_config = (
            config_manager.get_validation_config()
        )

        database_config = (
            config_manager.get_database_config()
        )

        # ==================================================
        # 2. DATA INGESTION
        # ==================================================

        logger.info("Starting data ingestion...")

        data_ingestion = DataIngestion(
            data_source_config=data_source_config,
            artifact_config=artifact_config
        )

        raw_file_path = (
            data_ingestion.initiate_data_ingestion()
        )

        logger.info(
            f"Data ingestion completed: "
            f"{raw_file_path}"
        )

        # ==================================================
        # 3. DATA VALIDATION
        # ==================================================

        logger.info("Starting data validation...")

        data_validation = DataValidation(
            artifact_config=artifact_config,
            validation_config=validation_config
        )

        validation_status = (
            data_validation.initiate_data_validation(
                raw_file_path=raw_file_path
            )
        )

        if not validation_status:
            raise ValueError(
                "Data validation failed."
            )

        logger.info(
            "Data validation completed successfully."
        )

        # ==================================================
        # 4. DATA TRANSFORMATION
        # ==================================================

        logger.info("Starting data transformation...")

        data_transformation = DataTransformation(
            artifact_config=artifact_config
        )

        processed_file_path = (
            data_transformation
            .initiate_data_transformation(
                raw_file_path=raw_file_path
            )
        )

        logger.info(
            f"Data transformation completed: "
            f"{processed_file_path}"
        )

        # ==================================================
        # 5. DATA LOADING
        # ==================================================

        logger.info("Starting data loading...")

        data_loading = DataLoading(
            database_config=database_config
        )

        records_loaded = (
            data_loading.initiate_data_loading(
                processed_file_path=processed_file_path
            )
        )

        logger.info(
            f"Data loading completed successfully. "
            f"Records loaded: {records_loaded}"
        )

        # ==================================================
        # 6. PIPELINE COMPLETED
        # ==================================================

        logger.info(
            "========== PIPELINE COMPLETED SUCCESSFULLY =========="
        )

    except Exception as error:

        logger.exception(
            f"Pipeline execution failed: {error}"
        )

        raise


if __name__ == "__main__":
    run_pipeline()