from pathlib import Path

import pandas as pd

from entity.config_entity import ArtifactConfig
from exception.exception import DataTransformationException
from logger.logger import get_logger


logger = get_logger(__name__)


class DataTransformation:

    def __init__(
        self,
        artifact_config: ArtifactConfig
    ):
        self.artifact_config = artifact_config

    def initiate_data_transformation(
        self,
        raw_file_path: Path
    ) -> Path:
        """
        Transforms the validated raw e-commerce pricing dataset.

        Transformation steps:
        1. Load raw CSV
        2. Remove exact duplicate records
        3. Select required business columns
        4. Clean text fields
        5. Convert prices to numeric
        6. Parse price observation dates
        7. Remove invalid records
        8. Create standardized columns
        9. Save processed data as Parquet

        Returns:
            Path: Path to processed Parquet file.
        """

        try:

            logger.info(
                "========== DATA TRANSFORMATION STARTED =========="
            )

            raw_file_path = Path(raw_file_path)

            # ==================================================
            # 1. Validate input file
            # ==================================================

            if not raw_file_path.exists():
                raise FileNotFoundError(
                    f"Raw dataset does not exist: {raw_file_path}"
                )

            logger.info(
                f"Loading raw dataset: {raw_file_path}"
            )

            # ==================================================
            # 2. Load dataset
            # ==================================================

            df = pd.read_csv(
                raw_file_path,
                low_memory=False
            )

            initial_row_count = len(df)

            logger.info(
                f"Raw dataset loaded successfully. "
                f"Rows: {initial_row_count}, "
                f"Columns: {len(df.columns)}"
            )

            # ==================================================
            # 3. Remove exact duplicate records
            # ==================================================

            duplicate_count = int(
                df.duplicated().sum()
            )

            if duplicate_count > 0:

                df = df.drop_duplicates().copy()

                logger.info(
                    f"Removed {duplicate_count} "
                    f"exact duplicate records."
                )

            else:

                logger.info(
                    "No duplicate records found."
                )

            # ==================================================
            # 4. Check required transformation columns
            # ==================================================

            required_columns = [
                "id",
                "name",
                "brand",
                "categories",
                "prices.amountMin",
                "prices.amountMax",
                "prices.currency",
                "prices.dateSeen",
                "prices.merchant",
                "prices.condition"
            ]

            missing_columns = [
                column
                for column in required_columns
                if column not in df.columns
            ]

            if missing_columns:

                raise ValueError(
                    "Required transformation columns are missing: "
                    f"{missing_columns}"
                )

            # ==================================================
            # 5. Select business columns
            # ==================================================

            df = df[
                required_columns
            ].copy()

            logger.info(
                f"Selected {len(required_columns)} "
                "business columns."
            )

            # ==================================================
            # 6. Rename columns
            # ==================================================

            df.rename(
                columns={
                    "id": "product_id",
                    "name": "product_name",
                    "brand": "brand",
                    "categories": "category",
                    "prices.amountMin": "price_min",
                    "prices.amountMax": "price_max",
                    "prices.currency": "currency",
                    "prices.dateSeen": "date_seen",
                    "prices.merchant": "merchant",
                    "prices.condition": "condition"
                },
                inplace=True
            )

            # ==================================================
            # 7. Clean text columns
            # ==================================================

            text_columns = [
                "product_id",
                "product_name",
                "brand",
                "category",
                "currency",
                "merchant",
                "condition"
            ]

            for column in text_columns:

                df[column] = (
                    df[column]
                    .astype("string")
                    .str.strip()
                )

            logger.info(
                "Text columns cleaned."
            )

            # ==================================================
            # 8. Convert prices to numeric
            # ==================================================

            df["price_min"] = pd.to_numeric(
                df["price_min"],
                errors="coerce"
            )

            df["price_max"] = pd.to_numeric(
                df["price_max"],
                errors="coerce"
            )

            # ==================================================
            # 9. Handle invalid price ranges
            # ==================================================

            invalid_price_mask = (
                df["price_min"].isna()
                |
                df["price_max"].isna()
                |
                (df["price_min"] < 0)
                |
                (df["price_max"] < 0)
                |
                (df["price_min"] > df["price_max"])
            )

            invalid_price_count = int(
                invalid_price_mask.sum()
            )

            if invalid_price_count > 0:

                logger.warning(
                    f"Removing {invalid_price_count} "
                    "records with invalid price values."
                )

                df = df.loc[
                    ~invalid_price_mask
                ].copy()

            # ==================================================
            # 10. Parse observation date
            # ==================================================

            df["date_seen"] = pd.to_datetime(
                df["date_seen"],
                errors="coerce",
                utc=True
            )

            invalid_date_count = int(
                df["date_seen"].isna().sum()
            )

            if invalid_date_count > 0:

                logger.warning(
                    f"Removing {invalid_date_count} "
                    "records with invalid observation dates."
                )

                df = df[
                    df["date_seen"].notna()
                ].copy()

            # ==================================================
            # 11. Standardize currency
            # ==================================================

            df["currency"] = (
                df["currency"]
                .str.upper()
            )

            # ==================================================
            # 12. Standardize merchant names
            # ==================================================

            df["merchant"] = (
                df["merchant"]
                .str.strip()
                .str.lower()
            )

            # ==================================================
            # 13. Standardize condition
            # ==================================================

            df["condition"] = (
                df["condition"]
                .str.strip()
                .str.lower()
            )

            # ==================================================
            # 14. Create average price
            # ==================================================

            df["price"] = (
                df["price_min"] + df["price_max"]
            ) / 2

            # ==================================================
            # 15. Create date dimensions
            # ==================================================

            df["observed_date"] = (
                df["date_seen"]
                .dt.date
            )

            df["observed_year"] = (
                df["date_seen"]
                .dt.year
            )

            df["observed_month"] = (
                df["date_seen"]
                .dt.month
            )

            # ==================================================
            # 16. Sort records
            # ==================================================

            df.sort_values(
                by=[
                    "product_id",
                    "merchant",
                    "date_seen"
                ],
                inplace=True
            )

            # ==================================================
            # 17. Reset index
            # ==================================================

            df.reset_index(
                drop=True,
                inplace=True
            )

            # ==================================================
            # 18. Create processed directory
            # ==================================================

            processed_directory = Path(
                self.artifact_config.processed_dir
            )

            processed_directory.mkdir(
                parents=True,
                exist_ok=True
            )

            # ==================================================
            # 19. Save processed dataset
            # ==================================================

            processed_file_path = (
                processed_directory
                / "ecommerce_price_processed.parquet"
            )

            df.to_parquet(
                processed_file_path,
                index=False
            )

            # ==================================================
            # 20. Transformation summary
            # ==================================================

            final_row_count = len(df)

            logger.info(
                f"Initial rows: {initial_row_count}"
            )

            logger.info(
                f"Final rows: {final_row_count}"
            )

            logger.info(
                f"Rows removed: "
                f"{initial_row_count - final_row_count}"
            )

            logger.info(
                f"Processed dataset saved to: "
                f"{processed_file_path}"
            )

            logger.info(
                "========== DATA TRANSFORMATION COMPLETED =========="
            )

            return processed_file_path

        except Exception as error:

            logger.error(
                f"Data transformation failed: {error}"
            )

            raise DataTransformationException(
                str(error)
            )