from pathlib import Path

import pandas as pd

from entity.config_entity import (
    ArtifactConfig,
    ValidationConfig
)
from exception.exception import DataValidationException
from logger.logger import get_logger


logger = get_logger(__name__)


class DataValidation:

    def __init__(
        self,
        artifact_config: ArtifactConfig,
        validation_config: ValidationConfig
    ):
        self.artifact_config = artifact_config
        self.validation_config = validation_config

    def initiate_data_validation(
        self,
        raw_file_path: Path
    ) -> bool:
        """
        Validates the raw e-commerce pricing dataset.

        Checks:
        - File existence
        - Required columns
        - Duplicate records
        - Null prices
        - Invalid prices
        - Minimum price constraint
        """

        try:
            logger.info(
                "========== DATA VALIDATION STARTED =========="
            )

            raw_file_path = Path(raw_file_path)

            # --------------------------------------------------
            # 1. Check raw file
            # --------------------------------------------------

            if not raw_file_path.exists():
                raise FileNotFoundError(
                    f"Raw dataset does not exist: {raw_file_path}"
                )

            logger.info(
                f"Validating file: {raw_file_path}"
            )

            # --------------------------------------------------
            # 2. Read dataset
            # --------------------------------------------------

            df = pd.read_csv(raw_file_path)

            logger.info(
                f"Dataset loaded successfully. "
                f"Rows: {len(df)}, Columns: {len(df.columns)}"
            )

            # --------------------------------------------------
            # 3. Validate required columns
            # --------------------------------------------------

            required_columns = set(
                self.validation_config.required_columns
            )

            actual_columns = set(df.columns)

            missing_columns = (
                required_columns - actual_columns
            )

            if missing_columns:
                raise ValueError(
                    "Missing required columns: "
                    f"{sorted(missing_columns)}"
                )

            logger.info(
                "Required column validation passed."
            )

            # --------------------------------------------------
            # 4. Validate duplicate records
            # --------------------------------------------------

            duplicate_count = int(
                df.duplicated().sum()
            )

            logger.info(
                f"Duplicate records found: {duplicate_count}"
            )

            if (
                duplicate_count > 0
                and not self.validation_config.allow_duplicates
            ):
                raise ValueError(
                    f"Dataset contains {duplicate_count} "
                    "duplicate records."
                )

            # --------------------------------------------------
            # 5. Convert price columns to numeric
            # --------------------------------------------------

            price_columns = [
                "prices.amountMin",
                "prices.amountMax"
            ]

            for column in price_columns:

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                )

            # --------------------------------------------------
            # 6. Validate null prices
            # --------------------------------------------------

            null_price_count = int(
                df[price_columns]
                .isnull()
                .any(axis=1)
                .sum()
            )

            logger.info(
                f"Records with null prices: "
                f"{null_price_count}"
            )

            if (
                null_price_count > 0
                and not self.validation_config.allow_null_prices
            ):
                raise ValueError(
                    f"Dataset contains {null_price_count} "
                    "records with null prices."
                )

            # --------------------------------------------------
            # 7. Validate negative prices
            # --------------------------------------------------

            minimum_price = (
                self.validation_config.minimum_price
            )

            invalid_price_mask = (
                (df["prices.amountMin"] < minimum_price)
                |
                (df["prices.amountMax"] < minimum_price)
            )

            invalid_price_count = int(
                invalid_price_mask.sum()
            )

            logger.info(
                f"Invalid price records: "
                f"{invalid_price_count}"
            )

            if invalid_price_count > 0:
                raise ValueError(
                    f"Found {invalid_price_count} records "
                    f"with prices below {minimum_price}."
                )

            # --------------------------------------------------
            # 8. Validate product IDs
            # --------------------------------------------------

            null_product_ids = int(
                df["id"].isnull().sum()
            )

            logger.info(
                f"Null product IDs: {null_product_ids}"
            )

            if null_product_ids > 0:
                raise ValueError(
                    f"Found {null_product_ids} records "
                    "with missing product IDs."
                )

            # --------------------------------------------------
            # 9. Create validation report
            # --------------------------------------------------

            report_directory = Path(
                self.artifact_config.reports_dir
            )

            report_directory.mkdir(
                parents=True,
                exist_ok=True
            )

            report_file = (
                report_directory
                / "validation_report.txt"
            )

            with open(
                report_file,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    "E-COMMERCE PRICE MONITOR "
                    "DATA VALIDATION REPORT\n"
                )

                file.write("=" * 60 + "\n\n")

                file.write(
                    f"File: {raw_file_path}\n"
                )

                file.write(
                    f"Rows: {len(df)}\n"
                )

                file.write(
                    f"Columns: {len(df.columns)}\n"
                )

                file.write(
                    f"Duplicates: {duplicate_count}\n"
                )

                file.write(
                    f"Null price records: "
                    f"{null_price_count}\n"
                )

                file.write(
                    f"Invalid price records: "
                    f"{invalid_price_count}\n"
                )

                file.write(
                    "\nValidation Status: PASSED\n"
                )

            logger.info(
                f"Validation report created: {report_file}"
            )

            logger.info(
                "========== DATA VALIDATION COMPLETED =========="
            )

            return True

        except Exception as error:

            logger.error(
                f"Data validation failed: {error}"
            )

            raise DataValidationException(
                str(error)
            )