import os
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import text

from entity.config_entity import DatabaseConfig
from exception.exception import DataLoadingException
from logger.logger import get_logger
from utils.database import DatabaseManager


logger = get_logger(__name__)


class DataLoading:

    def __init__(
        self,
        database_config: DatabaseConfig
    ):
        self.database_config = database_config

    # ==========================================================
    # LOAD PROCESSED DATASET
    # ==========================================================

    def _load_processed_dataset(
        self,
        processed_file_path: str
    ) -> pd.DataFrame:

        try:

            logger.info(
                f"Loading processed dataset: "
                f"{processed_file_path}"
            )

            if not os.path.exists(
                processed_file_path
            ):
                raise FileNotFoundError(
                    f"Processed dataset does not exist: "
                    f"{processed_file_path}"
                )

            df = pd.read_parquet(
                processed_file_path
            )

            logger.info(
                f"Processed dataset loaded. "
                f"Rows: {len(df)}, "
                f"Columns: {len(df.columns)}"
            )

            return df

        except Exception as error:

            logger.error(
                f"Failed to load processed dataset: "
                f"{error}"
            )

            raise

    # ==========================================================
    # CREATE PIPELINE RUN
    # ==========================================================

    def _create_pipeline_run(
        self,
        connection
    ) -> int:

        query = text(
            """
            INSERT INTO pipeline_runs (
                started_at,
                status
            )
            VALUES (
                :started_at,
                :status
            )
            RETURNING run_id
            """
        )

        result = connection.execute(
            query,
            {
                "started_at": datetime.now(
                    timezone.utc
                ),
                "status": "RUNNING"
            }
        )

        run_id = result.scalar_one()

        logger.info(
            f"Pipeline run created. "
            f"Run ID: {run_id}"
        )

        return run_id

    # ==========================================================
    # UPDATE PIPELINE RUN
    # ==========================================================

    def _update_pipeline_run(
        self,
        connection,
        run_id: int,
        status: str,
        records_received: int = 0,
        records_validated: int = 0,
        records_transformed: int = 0,
        records_loaded: int = 0,
        error_message: str = None
    ) -> None:

        query = text(
            """
            UPDATE pipeline_runs
            SET
                completed_at = :completed_at,
                status = :status,
                records_received = :records_received,
                records_validated = :records_validated,
                records_transformed = :records_transformed,
                records_loaded = :records_loaded,
                error_message = :error_message
            WHERE run_id = :run_id
            """
        )

        connection.execute(
            query,
            {
                "completed_at": datetime.now(
                    timezone.utc
                ),
                "status": status,
                "records_received": records_received,
                "records_validated": records_validated,
                "records_transformed": records_transformed,
                "records_loaded": records_loaded,
                "error_message": error_message,
                "run_id": run_id
            }
        )

    # ==========================================================
    # LOAD PRODUCTS
    # ==========================================================

    def _load_products(
        self,
        connection,
        df: pd.DataFrame
    ) -> int:

        logger.info(
            "Preparing products for loading..."
        )

        product_columns = [
            "product_id",
            "product_name",
            "brand",
            "category"
        ]

        missing_columns = [
            column
            for column in product_columns
            if column not in df.columns
        ]

        if missing_columns:

            raise ValueError(
                "Missing product columns: "
                f"{missing_columns}"
            )

        products_df = (
            df[product_columns]
            .copy()
            .drop_duplicates(
                subset=["product_id"]
            )
        )

        products_df["product_id"] = (
            products_df["product_id"]
            .astype(str)
            .str.strip()
        )

        products_df["product_name"] = (
            products_df["product_name"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        products_df["brand"] = (
            products_df["brand"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        products_df["category"] = (
            products_df["category"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        products_df = products_df[
            products_df["product_id"] != ""
        ]

        logger.info(
            f"Unique products to load: "
            f"{len(products_df)}"
        )

        product_query = text(
            """
            INSERT INTO products (
                product_id,
                product_name,
                brand,
                category
            )
            VALUES (
                :product_id,
                :product_name,
                :brand,
                :category
            )
            ON CONFLICT (product_id)
            DO UPDATE SET
                product_name = EXCLUDED.product_name,
                brand = EXCLUDED.brand,
                category = EXCLUDED.category,
                updated_at = CURRENT_TIMESTAMP
            """
        )

        product_records = []

        for record in products_df.to_dict(
            orient="records"
        ):

            product_records.append(
                {
                    "product_id": record[
                        "product_id"
                    ],
                    "product_name": record[
                        "product_name"
                    ],
                    "brand": record[
                        "brand"
                    ],
                    "category": record[
                        "category"
                    ]
                }
            )

        if product_records:

            connection.execute(
                product_query,
                product_records
            )

        logger.info(
            f"Products loaded successfully: "
            f"{len(product_records)}"
        )

        return len(product_records)

    # ==========================================================
    # LOAD MERCHANTS
    # ==========================================================

    def _load_merchants(
        self,
        connection,
        df: pd.DataFrame
    ):

        logger.info(
            "Preparing merchants for loading..."
        )

        if "merchant" not in df.columns:

            raise ValueError(
                "Missing required column: merchant"
            )

        merchants_df = (
            df[["merchant"]]
            .copy()
        )

        merchants_df["merchant"] = (
            merchants_df["merchant"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        merchants_df = merchants_df[
            merchants_df["merchant"] != ""
        ]

        merchants_df = (
            merchants_df
            .drop_duplicates()
            .reset_index(drop=True)
        )

        logger.info(
            f"Unique merchants to load: "
            f"{len(merchants_df)}"
        )

        merchant_query = text(
            """
            INSERT INTO merchants (
                merchant_name
            )
            VALUES (
                :merchant_name
            )
            ON CONFLICT (merchant_name)
            DO NOTHING
            """
        )

        merchant_records = [
            {
                "merchant_name": merchant
            }
            for merchant in
            merchants_df["merchant"].tolist()
        ]

        if merchant_records:

            connection.execute(
                merchant_query,
                merchant_records
            )

        logger.info(
            "Merchants loaded successfully."
        )

        # ------------------------------------------------------
        # Fetch merchant IDs
        # ------------------------------------------------------

        lookup_query = text(
            """
            SELECT
                merchant_id,
                merchant_name
            FROM merchants
            """
        )

        result = connection.execute(
            lookup_query
        )

        merchant_lookup = {
            row.merchant_name.strip():
                row.merchant_id
            for row in result
        }

        return merchant_lookup

    # ==========================================================
    # PREPARE PRICE HISTORY
    # ==========================================================

    def _prepare_price_history(
        self,
        df: pd.DataFrame,
        merchant_lookup: dict
    ) -> pd.DataFrame:

        required_columns = [
            "product_id",
            "merchant",
            "price_min",
            "price_max",
            "price",
            "currency",
            "condition",
            "date_seen",
            "observed_date",
            "observed_year",
            "observed_month"
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:

            raise ValueError(
                "Missing price history columns: "
                f"{missing_columns}"
            )

        price_df = (
            df[required_columns]
            .copy()
        )

        # ------------------------------------------------------
        # Clean merchant
        # ------------------------------------------------------

        price_df["merchant"] = (
            price_df["merchant"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # ------------------------------------------------------
        # Map merchant → merchant_id
        # ------------------------------------------------------

        price_df["merchant_id"] = (
            price_df["merchant"]
            .map(merchant_lookup)
        )

        missing_merchants = int(
            price_df["merchant_id"]
            .isna()
            .sum()
        )

        if missing_merchants > 0:

            logger.warning(
                f"Removing {missing_merchants} "
                "records with unmapped merchants."
            )

            price_df = price_df[
                price_df["merchant_id"]
                .notna()
            ].copy()

        # ------------------------------------------------------
        # Parse observed timestamp
        # ------------------------------------------------------

        price_df["date_seen"] = (
            pd.to_datetime(
                price_df["date_seen"],
                errors="coerce",
                utc=True
            )
        )

        invalid_dates = int(
            price_df["date_seen"]
            .isna()
            .sum()
        )

        if invalid_dates > 0:

            logger.warning(
                f"Removing {invalid_dates} "
                "records with invalid "
                "observation timestamps."
            )

            price_df = price_df[
                price_df["date_seen"]
                .notna()
            ].copy()

        # ------------------------------------------------------
        # Create observed_at
        # ------------------------------------------------------

        price_df["observed_at"] = (
            price_df["date_seen"]
            .apply(
                lambda value:
                    value.to_pydatetime()
                    if pd.notna(value)
                    else None
            )
        )

        # ------------------------------------------------------
        # Clean currency
        # ------------------------------------------------------

        price_df["currency"] = (
            price_df["currency"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # PostgreSQL schema uses VARCHAR(10)
        invalid_currency = (
            price_df["currency"]
            .str.len()
            > 10
        )

        currency_count = int(
            invalid_currency.sum()
        )

        if currency_count > 0:

            logger.warning(
                f"Removing {currency_count} "
                "records with currency values "
                "longer than 10 characters."
            )

            price_df = price_df[
                ~invalid_currency
            ].copy()

        # ------------------------------------------------------
        # Clean condition
        # ------------------------------------------------------

        price_df["condition"] = (
            price_df["condition"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # PostgreSQL schema uses VARCHAR(100)
        condition_lengths = (
            price_df["condition"]
            .str.len()
        )

        long_conditions = (
            condition_lengths > 100
        )

        long_condition_count = int(
            long_conditions.sum()
        )

        if long_condition_count > 0:

            logger.warning(
                f"Removing {long_condition_count} "
                "records with condition values "
                "longer than 100 characters."
            )

            price_df = price_df[
                ~long_conditions
            ].copy()

        # ------------------------------------------------------
        # Numeric conversion
        # ------------------------------------------------------

        numeric_columns = [
            "price_min",
            "price_max",
            "price"
        ]

        for column in numeric_columns:

            price_df[column] = pd.to_numeric(
                price_df[column],
                errors="coerce"
            )

        invalid_prices = (
            price_df[
                numeric_columns
            ]
            .isna()
            .any(axis=1)
        )

        invalid_price_count = int(
            invalid_prices.sum()
        )

        if invalid_price_count > 0:

            logger.warning(
                f"Removing {invalid_price_count} "
                "records with invalid price values."
            )

            price_df = price_df[
                ~invalid_prices
            ].copy()

        # ------------------------------------------------------
        # Final required-field validation
        # ------------------------------------------------------

        required_db_columns = [
            "product_id",
            "merchant_id",
            "price_min",
            "price_max",
            "price",
            "observed_at"
        ]

        for column in required_db_columns:

            invalid_count = int(
                price_df[column]
                .isna()
                .sum()
            )

            if invalid_count > 0:

                raise ValueError(
                    f"{invalid_count} records "
                    f"contain invalid value "
                    f"for '{column}'."
                )

        # ------------------------------------------------------
        # Remove source-only columns
        # ------------------------------------------------------

        price_df.drop(
            columns=[
                "date_seen",
                "merchant"
            ],
            inplace=True
        )

        # ------------------------------------------------------
        # Convert merchant ID to integer
        # ------------------------------------------------------

        price_df["merchant_id"] = (
            price_df["merchant_id"]
            .astype(int)
        )

        logger.info(
            f"Price history records ready "
            f"for loading: {len(price_df)}"
        )

        return price_df

    # ==========================================================
    # LOAD PRICE HISTORY
    # ==========================================================

    def _load_price_history(
        self,
        connection,
        price_df: pd.DataFrame
    ) -> int:

        price_query = text(
            """
            INSERT INTO price_history (
                product_id,
                merchant_id,
                price_min,
                price_max,
                price,
                currency,
                condition,
                observed_at,
                observed_date,
                observed_year,
                observed_month
            )
            VALUES (
                :product_id,
                :merchant_id,
                :price_min,
                :price_max,
                :price,
                :currency,
                :condition,
                :observed_at,
                :observed_date,
                :observed_year,
                :observed_month
            )
            ON CONFLICT (
                product_id,
                merchant_id,
                observed_at,
                price,
                price_min,
                price_max,
                currency,
                condition
            )
            DO NOTHING
            RETURNING price_id
            """
        )

        price_records = (
            price_df
            .to_dict(
                orient="records"
            )
        )

        if not price_records:

            logger.warning(
                "No price history records "
                "available for loading."
            )

            return 0

        # ------------------------------------------------------
        # Final DB-boundary validation
        # ------------------------------------------------------

        for index, record in enumerate(
            price_records
        ):

            if not record.get(
                "product_id"
            ):
                raise ValueError(
                    f"Invalid product_id "
                    f"at record {index}."
                )

            if record.get(
                "merchant_id"
            ) is None: 
                raise ValueError(
                    f"Invalid merchant_id "
                    f"at record {index}."
                )

            if record.get(
                "observed_at"
            ) is None:
                raise ValueError(
                    f"Invalid observed_at "
                    f"at record {index}."
                )

            condition = record.get(
                "condition"
            )

            if condition is not None:

                if len(str(condition)) > 100:

                    raise ValueError(
                        f"Condition exceeds "
                        f"VARCHAR(100) at "
                        f"record {index}."
                    )

            currency = record.get(
                "currency"
            )

            if currency is not None:

                if len(str(currency)) > 10:

                    raise ValueError(
                        f"Currency exceeds "
                        f"VARCHAR(10) at "
                        f"record {index}."
                    )

        # ------------------------------------------------------
        # Idempotent bulk insert
        # ------------------------------------------------------

        records_received = len(price_records)

        records_inserted = 0
        records_skipped = 0

        for index, record in enumerate(price_records):

            result = connection.execute(
                price_query,
                record
            )

            inserted_id = result.scalar()

            if index < 3:
                logger.info(
                    f"INSERT TEST | rowcount={result.rowcount} | "
                    f"product_id={record.get('product_id')} | "
                    f"merchant_id={record.get('merchant_id')}"
                )

            if inserted_id is not None:
                records_inserted += 1
            else:
                records_skipped += 1

        logger.info(
            f"Price history received: "
            f"{records_received}"
        )

        logger.info(
            f"New price history records inserted: "
            f"{records_inserted}"
        )

        logger.info(
            f"Existing records skipped: "
            f"{records_skipped}"
        )

        return records_inserted

    # ==========================================================
    # MAIN DATA LOADING METHOD
    # ==========================================================

    def initiate_data_loading(
    self,
            processed_file_path: str
        ) -> int:

            engine = None
            run_id = None
            records_received = 0

            try:

                logger.info(
                    "========== DATA LOADING STARTED =========="
                )

                # ==================================================
                # 1. Load processed dataset
                # ==================================================

                df = self._load_processed_dataset(
                    processed_file_path
                )

                records_received = len(df)

                # ==================================================
                # 2. Create database engine
                # ==================================================

                database_manager = DatabaseManager(
                    self.database_config
                )

                engine = database_manager.get_engine()

                # ==================================================
                # 3. Start transaction
                # ==================================================

                with engine.begin() as connection:

                    # ----------------------------------------------
                    # Create pipeline run
                    # ----------------------------------------------

                    run_id = self._create_pipeline_run(
                        connection
                    )

                    # ----------------------------------------------
                    # Load products
                    # ----------------------------------------------

                    products_loaded = self._load_products(
                        connection,
                        df
                    )

                    # ----------------------------------------------
                    # Load merchants
                    # ----------------------------------------------

                    merchant_lookup = self._load_merchants(
                        connection,
                        df
                    )

                    # ----------------------------------------------
                    # Prepare price history
                    # ----------------------------------------------

                    price_df = self._prepare_price_history(
                        df,
                        merchant_lookup
                    )

                    # ----------------------------------------------
                    # Load price history
                    # ----------------------------------------------

                    price_history_loaded = (
                        self._load_price_history(
                            connection,
                            price_df
                        )
                    )

                    # ----------------------------------------------
                    # Update pipeline run
                    # ----------------------------------------------

                    self._update_pipeline_run(
                        connection=connection,
                        run_id=run_id,
                        status="SUCCESS",
                        records_received=records_received,
                        records_validated=records_received,
                        records_transformed=records_received,
                        records_loaded=price_history_loaded
                    )

                # ==================================================
                # 4. Pipeline completed
                # ==================================================

                logger.info(
                    f"Products loaded: {products_loaded}"
                )

                logger.info(
                    f"Price history records loaded: "
                    f"{price_history_loaded}"
                )

                logger.info(
                    "========== DATA LOADING COMPLETED =========="
                )

                return price_history_loaded

            except Exception as error:

                logger.exception(
                    f"Data loading failed: {error}"
                )

                # ==================================================
                # Update failed pipeline run
                # ==================================================

                if engine is not None and run_id is not None:

                    try:

                        with engine.begin() as connection:

                            self._update_pipeline_run(
                                connection=connection,
                                run_id=run_id,
                                status="FAILED",
                                records_received=records_received,
                                records_validated=0,
                                records_transformed=0,
                                records_loaded=0,
                                error_message=str(error)
                            )

                    except Exception as update_error:

                        logger.error(
                            "Failed to update pipeline run "
                            f"status: {update_error}"
                        )

                raise DataLoadingException(
                    str(error)
                )
            # --------------------------------------------------
            # Try to record failure
            # --------------------------------------------------

            try:

                with engine.begin() as connection:

                    if "run_id" in locals():

                        self._update_pipeline_run(
                            connection=connection,
                            run_id=run_id,
                            status="FAILED",
                            records_received=records_received,
                            records_validated=0,
                            records_transformed=0,
                            records_loaded=0,
                            error_message=str(error)
                        )

            except Exception as update_error:

                logger.error(
                    "Failed to update pipeline "
                    f"run status: {update_error}"
                )

            raise DataLoadingException(
                str(error)
            )