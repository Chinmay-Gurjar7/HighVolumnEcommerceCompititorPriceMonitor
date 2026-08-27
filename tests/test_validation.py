from pathlib import Path

import pandas as pd
import pytest

from components.data_validation import DataValidation
from exception.exception import DataValidationException


REQUIRED_COLUMNS = [
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


def make_configs(
    tmp_path,
    allow_duplicates=False,
    allow_null_prices=False,
    minimum_price=0
):
    artifact_config = type(
        "ArtifactConfig",
        (),
        {
            "reports_dir": str(
                tmp_path / "reports"
            )
        }
    )()

    validation_config = type(
        "ValidationConfig",
        (),
        {
            "required_columns": REQUIRED_COLUMNS,
            "allow_duplicates": allow_duplicates,
            "allow_null_prices": allow_null_prices,
            "minimum_price": minimum_price,
        }
    )()

    return artifact_config, validation_config


def create_csv(tmp_path, rows):
    file_path = tmp_path / "raw.csv"

    df = pd.DataFrame(
        rows,
        columns=REQUIRED_COLUMNS
    )

    df.to_csv(
        file_path,
        index=False
    )

    return file_path


def valid_row():
    return [
        "product-1",
        "Test Product",
        "Test Brand",
        "Electronics",
        100,
        120,
        "USD",
        "2018-01-01T10:00:00Z",
        "merchant",
        "new",
    ]


def test_valid_dataset_passes_validation(tmp_path):
    artifact_config, validation_config = make_configs(
        tmp_path
    )

    raw_file = create_csv(
        tmp_path,
        [valid_row()]
    )

    validation = DataValidation(
        artifact_config,
        validation_config
    )

    result = validation.initiate_data_validation(
        raw_file
    )

    assert result is True


def test_validation_creates_report(tmp_path):
    artifact_config, validation_config = make_configs(
        tmp_path
    )

    raw_file = create_csv(
        tmp_path,
        [valid_row()]
    )

    validation = DataValidation(
        artifact_config,
        validation_config
    )

    validation.initiate_data_validation(
        raw_file
    )

    report = (
        tmp_path
        / "reports"
        / "validation_report.txt"
    )

    assert report.exists()

    content = report.read_text(
        encoding="utf-8"
    )

    assert (
        "E-COMMERCE PRICE MONITOR "
        "DATA VALIDATION REPORT"
    ) in content

    assert "Validation Status: PASSED" in content


def test_missing_file_fails_validation(tmp_path):
    artifact_config, validation_config = make_configs(
        tmp_path
    )

    validation = DataValidation(
        artifact_config,
        validation_config
    )

    missing_file = (
        tmp_path
        / "does_not_exist.csv"
    )

    with pytest.raises(
        DataValidationException
    ):
        validation.initiate_data_validation(
            missing_file
        )


def test_missing_required_column_fails_validation(tmp_path):
    artifact_config, validation_config = make_configs(
        tmp_path
    )

    raw_file = tmp_path / "raw.csv"

    data = {
        column: ["value"]
        for column in REQUIRED_COLUMNS
        if column != "id"
    }

    pd.DataFrame(data).to_csv(
        raw_file,
        index=False
    )

    validation = DataValidation(
        artifact_config,
        validation_config
    )

    with pytest.raises(
        DataValidationException
    ):
        validation.initiate_data_validation(
            raw_file
        )


def test_duplicates_fail_when_not_allowed(tmp_path):
    artifact_config, validation_config = make_configs(
        tmp_path,
        allow_duplicates=False
    )

    row = valid_row()

    raw_file = create_csv(
        tmp_path,
        [row, row]
    )

    validation = DataValidation(
        artifact_config,
        validation_config
    )

    with pytest.raises(
        DataValidationException
    ):
        validation.initiate_data_validation(
            raw_file
        )


def test_duplicates_are_allowed_when_configured(tmp_path):
    artifact_config, validation_config = make_configs(
        tmp_path,
        allow_duplicates=True
    )

    row = valid_row()

    raw_file = create_csv(
        tmp_path,
        [row, row]
    )

    validation = DataValidation(
        artifact_config,
        validation_config
    )

    result = validation.initiate_data_validation(
        raw_file
    )

    assert result is True


def test_null_prices_fail_when_not_allowed(tmp_path):
    artifact_config, validation_config = make_configs(
        tmp_path,
        allow_null_prices=False
    )

    row = valid_row()
    row[4] = None

    raw_file = create_csv(
        tmp_path,
        [row]
    )

    validation = DataValidation(
        artifact_config,
        validation_config
    )

    with pytest.raises(
        DataValidationException
    ):
        validation.initiate_data_validation(
            raw_file
        )


def test_null_prices_are_allowed_when_configured(tmp_path):
    artifact_config, validation_config = make_configs(
        tmp_path,
        allow_null_prices=True
    )

    row = valid_row()
    row[4] = None

    raw_file = create_csv(
        tmp_path,
        [row]
    )

    validation = DataValidation(
        artifact_config,
        validation_config
    )

    result = validation.initiate_data_validation(
        raw_file
    )

    assert result is True


def test_price_below_minimum_fails_validation(tmp_path):
    artifact_config, validation_config = make_configs(
        tmp_path,
        minimum_price=10
    )

    row = valid_row()
    row[4] = 5

    raw_file = create_csv(
        tmp_path,
        [row]
    )

    validation = DataValidation(
        artifact_config,
        validation_config
    )

    with pytest.raises(
        DataValidationException
    ):
        validation.initiate_data_validation(
            raw_file
        )


def test_price_above_minimum_passes_validation(tmp_path):
    artifact_config, validation_config = make_configs(
        tmp_path,
        minimum_price=10
    )

    raw_file = create_csv(
        tmp_path,
        [valid_row()]
    )

    validation = DataValidation(
        artifact_config,
        validation_config
    )

    result = validation.initiate_data_validation(
        raw_file
    )

    assert result is True


def test_missing_product_id_fails_validation(tmp_path):
    artifact_config, validation_config = make_configs(
        tmp_path
    )

    row = valid_row()
    row[0] = None

    raw_file = create_csv(
        tmp_path,
        [row]
    )

    validation = DataValidation(
        artifact_config,
        validation_config
    )

    with pytest.raises(
        DataValidationException
    ):
        validation.initiate_data_validation(
            raw_file
        )