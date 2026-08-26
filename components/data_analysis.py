from typing import Optional

import pandas as pd
from sqlalchemy import text

from entity.config_entity import DatabaseConfig
from exception.exception import DataAnalysisException
from logger.logger import get_logger
from utils.database import DatabaseManager


logger = get_logger(__name__)


class DataAnalysis:
    """
    Performs analytical queries on the PostgreSQL
    e-commerce pricing database.
    """

    def __init__(
        self,
        database_config: DatabaseConfig
    ):
        self.database_config = database_config

        self.database_manager = DatabaseManager(
            database_config=database_config
        )

    def get_latest_competitor_prices(
        self,
        product_id: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Returns the latest known price for each
        product/merchant combination.

        If product_id is provided, analysis is
        restricted to that product.
        """

        try:

            logger.info(
                "Starting latest competitor price analysis..."
            )

            engine = (
                self.database_manager.get_engine()
            )

            query = text(
                """
                WITH ranked_prices AS (

                    SELECT
                        ph.product_id,
                        p.product_name,
                        p.brand,
                        p.category,
                        ph.merchant_id,
                        m.merchant_name,
                        ph.price,
                        ph.price_min,
                        ph.price_max,
                        ph.currency,
                        ph.condition,
                        ph.observed_at,

                        ROW_NUMBER() OVER (
                            PARTITION BY
                                ph.product_id,
                                ph.merchant_id
                            ORDER BY
                                ph.observed_at DESC
                        ) AS row_number

                    FROM price_history ph

                    INNER JOIN products p
                        ON ph.product_id = p.product_id

                    INNER JOIN merchants m
                        ON ph.merchant_id = m.merchant_id

                    WHERE
                        (
                            :product_id IS NULL
                            OR ph.product_id = :product_id
                        )
                )

                SELECT
                    product_id,
                    product_name,
                    brand,
                    category,
                    merchant_id,
                    merchant_name,
                    price,
                    price_min,
                    price_max,
                    currency,
                    condition,
                    observed_at

                FROM ranked_prices

                WHERE row_number = 1

                ORDER BY
                    product_id,
                    price;
                """
            )

            with engine.connect() as connection:

                result = connection.execute(
                    query,
                    {
                        "product_id": product_id
                    }
                )

                dataframe = pd.DataFrame(
                    result.fetchall(),
                    columns=result.keys()
                )

            logger.info(
                "Latest competitor price analysis "
                f"completed. Records: {len(dataframe)}"
            )

            return dataframe

        except Exception as error:

            logger.error(
                "Latest competitor price analysis failed: "
                f"{error}"
            )

            raise DataAnalysisException(
                str(error)
            )
            
    def get_competitor_price_summary(
        self,
        product_id: Optional[str] = None
    ) -> pd.DataFrame:
            """
            Returns competitor price statistics for each product.

            Metrics include:
            - Number of competitors
            - Minimum/latest competitor price
            - Maximum/latest competitor price
            - Average latest competitor price
            - Price spread
            """

            try:

                logger.info(
                    "Starting competitor price summary analysis..."
                )

                latest_prices = (
                    self.get_latest_competitor_prices(
                        product_id=product_id
                    )
                )

                if latest_prices.empty:

                    logger.warning(
                        "No competitor price data found "
                        "for the requested product."
                    )

                    return pd.DataFrame(
                        columns=[
                            "product_id",
                            "product_name",
                            "brand",
                            "category",
                            "competitor_count",
                            "lowest_price",
                            "highest_price",
                            "average_price",
                            "price_spread",
                        ]
                    )

                summary = (
                    latest_prices
                    .groupby(
                        [
                            "product_id",
                            "product_name",
                            "brand",
                            "category",
                        ],
                        dropna=False
                    )
                    .agg(
                        competitor_count=(
                            "merchant_id",
                            "nunique"
                        ),
                        lowest_price=(
                            "price",
                            "min"
                        ),
                        highest_price=(
                            "price",
                            "max"
                        ),
                        average_price=(
                            "price",
                            "mean"
                        ),
                    )
                    .reset_index()
                )

                summary["price_spread"] = (
                    summary["highest_price"]
                    - summary["lowest_price"]
                )

                summary["lowest_price"] = pd.to_numeric(
                    summary["lowest_price"],
                    errors="coerce"
                )

                summary["highest_price"] = pd.to_numeric(
                    summary["highest_price"],
                    errors="coerce"
                )

                summary["average_price"] = pd.to_numeric(
                    summary["average_price"],
                    errors="coerce"
                )

                summary["price_spread"] = pd.to_numeric(
                    summary["price_spread"],
                    errors="coerce"
                )

                summary["average_price"] = (
                    summary["average_price"].round(2)
                )

                summary["price_spread"] = (
                    summary["price_spread"].round(2)
                )

                summary = (
                    summary
                    .sort_values(
                        [
                            "price_spread",
                            "competitor_count",
                        ],
                        ascending=[False, False]
                    )
                    .reset_index(drop=True)
                    )

                logger.info(
                    "Competitor price summary analysis "
                    f"completed. Products analyzed: "
                    f"{len(summary)}"
                )

                return summary

            except Exception as error:

                logger.error(
                    "Competitor price summary analysis failed: "
                    f"{error}"
                )

                raise DataAnalysisException(
                    str(error)
                )
                
    def get_cheapest_and_most_expensive_merchants(
        self,
        product_id: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Returns the cheapest and most expensive merchant
        for each product based on the latest available
        competitor prices.
        """

        try:

            logger.info(
                "Starting merchant price ranking analysis..."
            )

            latest_prices = (
                self.get_latest_competitor_prices(
                    product_id=product_id
                )
            )

            if latest_prices.empty:

                logger.warning(
                    "No competitor price data found "
                    "for merchant ranking analysis."
                )

                return pd.DataFrame(
                    columns=[
                        "product_id",
                        "product_name",
                        "cheapest_merchant",
                        "cheapest_price",
                        "most_expensive_merchant",
                        "highest_price",
                    ]
                )

            cheapest = (
                latest_prices
                .sort_values(
                    ["product_id", "price"]
                )
                .groupby(
                    "product_id",
                    as_index=False
                )
                .first()
            )

            expensive = (
                latest_prices
                .sort_values(
                    ["product_id", "price"],
                    ascending=[True, False]
                )
                .groupby(
                    "product_id",
                    as_index=False
                )
                .first()
            )

            result = cheapest[
                [
                    "product_id",
                    "product_name",
                    "merchant_name",
                    "price",
                ]
            ].rename(
                columns={
                    "merchant_name": "cheapest_merchant",
                    "price": "cheapest_price",
                }
            )

            expensive = expensive[
                [
                    "product_id",
                    "merchant_name",
                    "price",
                ]
            ].rename(
                columns={
                    "merchant_name": "most_expensive_merchant",
                    "price": "highest_price",
                }
            )

            result = result.merge(
                expensive,
                on="product_id",
                how="left"
            )

            result["cheapest_price"] = pd.to_numeric(
                result["cheapest_price"],
                errors="coerce"
            )

            result["highest_price"] = pd.to_numeric(
                result["highest_price"],
                errors="coerce"
            )

            result["cheapest_price"] = (
                result["cheapest_price"].round(2)
            )

            result["highest_price"] = (
                result["highest_price"].round(2)
            )

            result = result.sort_values(
                "cheapest_price"
            ).reset_index(drop=True)

            logger.info(
                "Merchant price ranking analysis "
                f"completed. Products analyzed: "
                f"{len(result)}"
            )

            return result

        except Exception as error:

            logger.error(
                "Merchant price ranking analysis failed: "
                f"{error}"
            )

            raise DataAnalysisException(
                str(error)
            )
            
    def get_price_change_history(
        self,
        product_id: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Returns historical price observations with
        previous price, absolute price change, and
        percentage price change.
        """

        try:

            logger.info(
                "Starting price change history analysis..."
            )

            engine = (
                self.database_manager.get_engine()
            )

            query = text(
                """
                WITH distinct_observations AS (

                    SELECT DISTINCT ON (
                        ph.product_id,
                        ph.merchant_id,
                        ph.observed_at
                    )
                        ph.price_id,
                        ph.product_id,
                        p.product_name,
                        p.brand,
                        p.category,
                        ph.merchant_id,
                        m.merchant_name,
                        ph.price,
                        ph.currency,
                        ph.condition,
                        ph.observed_at

                    FROM price_history ph

                    INNER JOIN products p
                        ON ph.product_id = p.product_id

                    INNER JOIN merchants m
                        ON ph.merchant_id = m.merchant_id

                    WHERE
                        (
                            :product_id IS NULL
                            OR ph.product_id = :product_id
                        )

                    ORDER BY
                        ph.product_id,
                        ph.merchant_id,
                        ph.observed_at,
                        ph.price_id DESC
                ),

                price_history_ranked AS (

                    SELECT
                        product_id,
                        product_name,
                        brand,
                        category,
                        merchant_id,
                        merchant_name,
                        price,
                        currency,
                        condition,
                        observed_at,

                        LAG(price) OVER (
                            PARTITION BY
                                product_id,
                                merchant_id
                            ORDER BY
                                observed_at
                        ) AS previous_price

                    FROM distinct_observations
                )

                SELECT
                    product_id,
                    product_name,
                    brand,
                    category,
                    merchant_id,
                    merchant_name,
                    price,
                    previous_price,
                    currency,
                    condition,
                    observed_at,

                    CASE
                        WHEN previous_price IS NOT NULL
                        THEN price - previous_price
                        ELSE NULL
                    END AS price_change,

                    CASE
                        WHEN previous_price IS NOT NULL
                             AND previous_price <> 0
                        THEN
                            (
                                (price - previous_price)
                                / previous_price
                            ) * 100
                        ELSE NULL
                    END AS price_change_percentage

                FROM price_history_ranked

                ORDER BY
                    product_id,
                    merchant_id,
                    observed_at;
                """
            )

            with engine.connect() as connection:

                result = connection.execute(
                    query,
                    {
                        "product_id": product_id
                    }
                )

                dataframe = pd.DataFrame(
                    result.fetchall(),
                    columns=result.keys()
                )

            numeric_columns = [
                "price",
                "previous_price",
                "price_change",
                "price_change_percentage",
            ]

            for column in numeric_columns:

                dataframe[column] = pd.to_numeric(
                    dataframe[column],
                    errors="coerce"
                )

            dataframe["price_change"] = (
                dataframe["price_change"].round(2)
            )

            dataframe["price_change_percentage"] = (
                dataframe[
                    "price_change_percentage"
                ].round(2)
            )

            logger.info(
                "Price change history analysis "
                f"completed. Records: {len(dataframe)}"
            )

            return dataframe

        except Exception as error:

            logger.error(
                "Price change history analysis failed: "
                f"{error}"
            )

            raise DataAnalysisException(
                str(error)
            )
            
    def get_largest_price_movements(
        self,
        limit: int = 10,
        product_id: Optional[str] = None
    ) -> dict:
        """
        Returns products with the largest price increases
        and decreases based on historical price changes.
        """

        try:

            logger.info(
                "Starting largest price movement analysis..."
            )

            if limit <= 0:
                raise ValueError(
                    "limit must be greater than zero."
                )

            price_changes = (
                self.get_price_change_history(
                    product_id=product_id
                )
            )

            price_changes = price_changes.dropna(
                subset=[
                    "price_change",
                    "price_change_percentage",
                ]
            )
            
            price_changes = (
                price_changes
                .drop_duplicates(
                    subset=[
                        "product_id",
                        "merchant_id",
                        "observed_at",
                        "price",
                        "previous_price",
                    ]
                )
                .reset_index(drop=True)
            )

            if price_changes.empty:

                logger.warning(
                    "No price change records found."
                )

                return {
                    "largest_increases": pd.DataFrame(),
                    "largest_decreases": pd.DataFrame(),
                }

            largest_increases = (
                price_changes[
                    price_changes["price_change"] > 0
                ]
                .sort_values(
                    "price_change",
                    ascending=False
                )
                .head(limit)
                .reset_index(drop=True)
            )

            largest_decreases = (
                price_changes[
                    price_changes["price_change"] < 0
                ]
                .sort_values(
                    "price_change",
                    ascending=True
                )
                .head(limit)
                .reset_index(drop=True)
            )

            logger.info(
                "Largest price movement analysis completed. "
                f"Increases: {len(largest_increases)}, "
                f"Decreases: {len(largest_decreases)}"
            )

            return {
                "largest_increases": largest_increases,
                "largest_decreases": largest_decreases,
            }

        except Exception as error:

            logger.error(
                "Largest price movement analysis failed: "
                f"{error}"
            )

            raise DataAnalysisException(
                str(error)
            )
            
    def get_merchant_price_change_frequency(
        self
    ) -> pd.DataFrame:
        """
        Calculates price-change frequency by merchant.

        Metrics:
        - total_observations: all price observations
        - comparable_observations: observations with a previous price
        - price_changes: observations where price changed
        - price_increases: positive price changes
        - price_decreases: negative price changes
        - price_change_rate: price changes / comparable observations
        """

        try:

            logger.info(
                "Starting merchant price change frequency analysis..."
            )

            price_history = (
                self.get_price_change_history()
            )

            if price_history.empty:

                logger.warning(
                    "No historical price records available "
                    "for frequency analysis."
                )

                return pd.DataFrame()

            # --------------------------------------------------
            # TOTAL OBSERVATIONS
            # --------------------------------------------------

            total_observations = (
                price_history
                .groupby(
                    [
                        "merchant_id",
                        "merchant_name",
                    ],
                    as_index=False
                )
                .agg(
                    total_observations=(
                        "price",
                        "count"
                    )
                )
            )

            # --------------------------------------------------
            # COMPARABLE OBSERVATIONS
            # --------------------------------------------------

            comparable_history = (
                price_history
                .dropna(
                    subset=["previous_price"]
                )
                .copy()
            )

            if comparable_history.empty:

                logger.warning(
                    "No comparable price observations "
                    "available for frequency analysis."
                )

                total_observations[
                    "comparable_observations"
                ] = 0

                total_observations[
                    "price_changes"
                ] = 0

                total_observations[
                    "price_increases"
                ] = 0

                total_observations[
                    "price_decreases"
                ] = 0

                total_observations[
                    "price_change_rate"
                ] = 0.0

                return total_observations

            # --------------------------------------------------
            # PRICE CHANGE FLAGS
            # --------------------------------------------------

            comparable_history["is_price_change"] = (
                comparable_history["price_change"] != 0
            )

            comparable_history["is_price_increase"] = (
                comparable_history["price_change"] > 0
            )

            comparable_history["is_price_decrease"] = (
                comparable_history["price_change"] < 0
            )

            # --------------------------------------------------
            # AGGREGATE PRICE CHANGES
            # --------------------------------------------------

            change_summary = (
                comparable_history
                .groupby(
                    [
                        "merchant_id",
                        "merchant_name",
                    ],
                    as_index=False
                )
                .agg(
                    comparable_observations=(
                        "price",
                        "count"
                    ),
                    price_changes=(
                        "is_price_change",
                        "sum"
                    ),
                    price_increases=(
                        "is_price_increase",
                        "sum"
                    ),
                    price_decreases=(
                        "is_price_decrease",
                        "sum"
                    ),
                )
            )

            # --------------------------------------------------
            # COMBINE TOTAL + CHANGE METRICS
            # --------------------------------------------------

            summary = total_observations.merge(
                change_summary,
                on=[
                    "merchant_id",
                    "merchant_name",
                ],
                how="left"
            )

            numeric_columns = [
                "comparable_observations",
                "price_changes",
                "price_increases",
                "price_decreases",
            ]

            summary[numeric_columns] = (
                summary[numeric_columns]
                .fillna(0)
                .astype(int)
            )

            # --------------------------------------------------
            # PRICE CHANGE RATE
            # --------------------------------------------------

            summary["price_change_rate"] = (
                summary["price_changes"]
                .div(
                    summary["comparable_observations"]
                )
                .mul(100)
            )

            summary["price_change_rate"] = (
                summary["price_change_rate"]
                .fillna(0)
                .round(2)
            )

            # --------------------------------------------------
            # SORT
            # --------------------------------------------------

            summary = (
                summary
                .sort_values(
                    [
                        "price_changes",
                        "price_change_rate",
                    ],
                    ascending=[False, False]
                )
                .reset_index(drop=True)
            )

            logger.info(
                "Merchant price change frequency analysis "
                f"completed. Merchants analyzed: "
                f"{len(summary)}"
            )

            return summary

        except Exception as error:

            logger.error(
                "Merchant price change frequency analysis failed: "
                f"{error}"
            )

            raise DataAnalysisException(
                str(error)
            )