from pathlib import Path

import pandas as pd
import pytest

from components.data_transformation import DataTransformation
from exception.exception import DataTransformationException


def make_configs(tmp_path):
    """
    Create minimal configuration objects required by
    DataTransformation.
    """

    processed_dir = tmp_path / "processed"

    artifact_config = type(
        "ArtifactConfig",
        (),
        {
            "processed_dir": str(processed_dir)
        }
    )()

    return artifact_config


def create_raw_csv(tmp_path, rows):
    """
    Create a raw CSV containing the required source columns.
    """

    raw_file = tmp_path / "raw.csv"

    columns = [
        "id",
        "name",
        "brand",
        "categories",
        "prices.amountMin",
        "prices.amountMax",
        "prices.currency",
        "prices.dateSeen",
        "prices.merchant",
        "prices.condition",
    ]

    df = pd.DataFrame(rows, columns=columns)

    df.to_csv(
        raw_file,
        index=False
    )

    return raw_file


def test_transformation_creates_parquet_file(tmp_path):
    artifact_config = make_configs(tmp_path)

    raw_file = create_raw_csv(
        tmp_path,
        [
            [
                "product-1",
                "Test Product",
                "Test Brand",
                "Electronics",
                90,
                110,
                "usd",
                "2018-01-01T10:00:00Z",
                " TestMerchant ",
                " NEW ",
            ]
        ]
    )

    transformation = DataTransformation(
        artifact_config
    )

    result = transformation.initiate_data_transformation(
        raw_file
    )

    assert isinstance(result, Path)
    assert result.exists()
    assert result.is_file()
    assert result.suffix == ".parquet"

    assert result.name == (
        "ecommerce_price_processed.parquet"
    )


def test_transformation_removes_duplicates(tmp_path):
    artifact_config = make_configs(tmp_path)

    row = [
        "product-1",
        "Test Product",
        "Test Brand",
        "Electronics",
        90,
        110,
        "USD",
        "2018-01-01T10:00:00Z",
        "merchant",
        "new",
    ]

    raw_file = create_raw_csv(
        tmp_path,
        [row, row]
    )

    transformation = DataTransformation(
        artifact_config
    )

    result = transformation.initiate_data_transformation(
        raw_file
    )

    df = pd.read_parquet(result)

    assert len(df) == 1


def test_transformation_calculates_average_price(tmp_path):
    artifact_config = make_configs(tmp_path)

    raw_file = create_raw_csv(
        tmp_path,
        [
            [
                "product-1",
                "Test Product",
                "Brand",
                "Electronics",
                100,
                200,
                "USD",
                "2018-01-01T10:00:00Z",
                "merchant",
                "new",
            ]
        ]
    )

    transformation = DataTransformation(
        artifact_config
    )

    result = transformation.initiate_data_transformation(
        raw_file
    )

    df = pd.read_parquet(result)

    assert df.loc[0, "price"] == 150.0


def test_transformation_standardizes_text_fields(tmp_path):
    artifact_config = make_configs(tmp_path)

    raw_file = create_raw_csv(
        tmp_path,
        [
            [
                " product-1 ",
                " Test Product ",
                " Test Brand ",
                " Electronics ",
                100,
                200,
                " usd ",
                "2018-01-01T10:00:00Z",
                " BestBuy.COM ",
                " NEW ",
            ]
        ]
    )

    transformation = DataTransformation(
        artifact_config
    )

    result = transformation.initiate_data_transformation(
        raw_file
    )

    df = pd.read_parquet(result)

    row = df.iloc[0]

    assert row["product_id"] == "product-1"
    assert row["product_name"] == "Test Product"
    assert row["brand"] == "Test Brand"
    assert row["category"] == "Electronics"
    assert row["currency"] == "USD"
    assert row["merchant"] == "bestbuy.com"
    assert row["condition"] == "new"


def test_transformation_expands_multiple_dates(tmp_path):
    artifact_config = make_configs(tmp_path)

    raw_file = create_raw_csv(
        tmp_path,
        [
            [
                "product-1",
                "Test Product",
                "Brand",
                "Electronics",
                100,
                200,
                "USD",
                (
                    "2018-01-01T10:00:00Z,"
                    "2018-01-02T10:00:00Z"
                ),
                "merchant",
                "new",
            ]
        ]
    )

    transformation = DataTransformation(
        artifact_config
    )

    result = transformation.initiate_data_transformation(
        raw_file
    )

    df = pd.read_parquet(result)

    assert len(df) == 2

    assert (
        df["observed_date"]
        .nunique()
        == 2
    )


def test_transformation_creates_date_dimensions(tmp_path):
    artifact_config = make_configs(tmp_path)

    raw_file = create_raw_csv(
        tmp_path,
        [
            [
                "product-1",
                "Test Product",
                "Brand",
                "Electronics",
                100,
                200,
                "USD",
                "2018-05-23T10:00:00Z",
                "merchant",
                "new",
            ]
        ]
    )

    transformation = DataTransformation(
        artifact_config
    )

    result = transformation.initiate_data_transformation(
        raw_file
    )

    df = pd.read_parquet(result)

    row = df.iloc[0]

    assert row["observed_year"] == 2018
    assert row["observed_month"] == 5
    assert str(row["observed_date"]) == "2018-05-23"


def test_transformation_removes_invalid_prices(tmp_path):
    artifact_config = make_configs(tmp_path)

    raw_file = create_raw_csv(
        tmp_path,
        [
            [
                "valid",
                "Valid Product",
                "Brand",
                "Electronics",
                100,
                200,
                "USD",
                "2018-01-01T10:00:00Z",
                "merchant",
                "new",
            ],
            [
                "negative",
                "Negative Product",
                "Brand",
                "Electronics",
                -10,
                100,
                "USD",
                "2018-01-01T10:00:00Z",
                "merchant",
                "new",
            ],
            [
                "reversed",
                "Reversed Product",
                "Brand",
                "Electronics",
                300,
                100,
                "USD",
                "2018-01-01T10:00:00Z",
                "merchant",
                "new",
            ],
        ]
    )

    transformation = DataTransformation(
        artifact_config
    )

    result = transformation.initiate_data_transformation(
        raw_file
    )

    df = pd.read_parquet(result)

    assert len(df) == 1
    assert df.iloc[0]["product_id"] == "valid"


def test_transformation_removes_invalid_dates(tmp_path):
    artifact_config = make_configs(tmp_path)

    raw_file = create_raw_csv(
        tmp_path,
        [
            [
                "valid",
                "Valid Product",
                "Brand",
                "Electronics",
                100,
                200,
                "USD",
                "2018-01-01T10:00:00Z",
                "merchant",
                "new",
            ],
            [
                "invalid",
                "Invalid Product",
                "Brand",
                "Electronics",
                100,
                200,
                "USD",
                "not-a-date",
                "merchant",
                "new",
            ],
        ]
    )

    transformation = DataTransformation(
        artifact_config
    )

    result = transformation.initiate_data_transformation(
        raw_file
    )

    df = pd.read_parquet(result)

    assert len(df) == 1
    assert df.iloc[0]["product_id"] == "valid"


def test_transformation_requires_business_columns(tmp_path):
    artifact_config = make_configs(tmp_path)

    raw_file = tmp_path / "invalid.csv"

    pd.DataFrame(
        {
            "id": ["product-1"],
            "name": ["Test Product"],
        }
    ).to_csv(
        raw_file,
        index=False
    )

    transformation = DataTransformation(
        artifact_config
    )

    with pytest.raises(
        DataTransformationException
    ):
        transformation.initiate_data_transformation(
            raw_file
        )


def test_transformation_fails_for_missing_file(tmp_path):
    artifact_config = make_configs(tmp_path)

    transformation = DataTransformation(
        artifact_config
    )

    missing_file = tmp_path / "missing.csv"

    with pytest.raises(
        DataTransformationException
    ):
        transformation.initiate_data_transformation(
            missing_file
        )