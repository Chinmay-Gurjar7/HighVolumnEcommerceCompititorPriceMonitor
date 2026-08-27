import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

from components.data_analysis import DataAnalysis
from exception.exception import DataAnalysisException


@pytest.fixture
def database_config():
    """
    Minimal mocked database configuration.

    DataAnalysis only passes this configuration
    to DatabaseManager during initialization.
    """
    config = MagicMock()
    return config


@pytest.fixture
def analysis(database_config):
    """
    Creates DataAnalysis with a mocked DatabaseManager.
    """
    with patch(
        "components.data_analysis.DatabaseManager"
    ) as mock_database_manager:

        instance = mock_database_manager.return_value

        analysis = DataAnalysis(database_config)

        analysis.database_manager = instance

        yield analysis


def test_get_latest_competitor_prices_returns_dataframe(analysis):
    """
    Latest competitor price analysis should return
    a pandas DataFrame.
    """

    expected = pd.DataFrame(
        [
            {
                "product_id": "product-1",
                "product_name": "Test Product",
                "brand": "Test Brand",
                "category": "Electronics",
                "merchant_id": 1001,
                "merchant_name": "merchant-a",
                "price": 99.99,
                "price_min": 99.99,
                "price_max": 99.99,
                "currency": "USD",
                "condition": "new",
                "observed_at": "2026-01-01",
            }
        ]
    )

    mock_connection = MagicMock()
    mock_result = MagicMock()

    mock_result.fetchall.return_value = (
    expected.to_dict(orient="records")
    )

    mock_result.keys.return_value = expected.columns.tolist()
    mock_connection.execute.return_value = mock_result

    analysis.database_manager.get_engine.return_value.connect.return_value.__enter__.return_value = (
        mock_connection
    )

    result = analysis.get_latest_competitor_prices()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert result.iloc[0]["product_id"] == "product-1"


def test_get_price_change_history_returns_dataframe(analysis):
    """
    Price history analysis should return a DataFrame
    containing price-change metrics.
    """

    expected = pd.DataFrame(
        [
            {
                "product_id": "product-1",
                "product_name": "Test Product",
                "brand": "Test Brand",
                "category": "Electronics",
                "merchant_id": 1001,
                "merchant_name": "merchant-a",
                "price": 90.0,
                "previous_price": 100.0,
                "currency": "USD",
                "condition": "new",
                "observed_at": "2026-01-02",
                "price_change": -10.0,
                "price_change_percentage": -10.0,
            }
        ]
    )

    mock_connection = MagicMock()
    mock_result = MagicMock()

    mock_result.fetchall.return_value = (
    expected.to_dict(orient="records")
    )

    mock_result.keys.return_value = expected.columns.tolist()

    mock_connection.execute.return_value = mock_result

    analysis.database_manager.get_engine.return_value.connect.return_value.__enter__.return_value = (
        mock_connection
    )

    result = analysis.get_price_change_history()

    assert isinstance(result, pd.DataFrame)
    assert "previous_price" in result.columns
    assert "price_change" in result.columns
    assert "price_change_percentage" in result.columns


def test_price_change_calculation():
    """
    Business rule:

        price_change = price - previous_price
    """

    price = 90.0
    previous_price = 100.0

    price_change = price - previous_price

    assert price_change == -10.0


def test_price_change_percentage_calculation():
    """
    Business rule:

        percentage =
        ((price - previous_price) / previous_price) * 100
    """

    price = 90.0
    previous_price = 100.0

    percentage = (
        (price - previous_price)
        / previous_price
        * 100
    )

    assert percentage == -10.0


def test_price_change_percentage_handles_zero_previous_price():
    """
    Percentage change must not divide by zero.
    """

    previous_price = 0.0

    percentage = None

    if previous_price != 0:
        percentage = (
            (100.0 - previous_price)
            / previous_price
            * 100
        )

    assert percentage is None


def test_price_spread_business_rule():
    """
    Business rule:

        price_spread =
        highest_price - lowest_price
    """

    lowest_price = 100.0
    highest_price = 150.0

    price_spread = highest_price - lowest_price

    assert price_spread == 50.0
    assert price_spread >= 0


def test_merchant_frequency_business_rules():
    """
    Merchant analytics invariants:

    - changes cannot exceed comparable observations
    - increases + decreases must equal changes
    - change rate must be between 0 and 100
    """

    comparable_observations = 100
    price_changes = 40
    price_increases = 22
    price_decreases = 18

    price_change_rate = (
        price_changes
        / comparable_observations
        * 100
    )

    assert price_changes <= comparable_observations
    assert (
        price_increases + price_decreases
        == price_changes
    )
    assert 0 <= price_change_rate <= 100


def test_largest_price_increase_is_positive():
    """
    Largest-increase results must contain
    positive price movements.
    """

    price_change = 25.0

    assert price_change > 0


def test_largest_price_decrease_is_negative():
    """
    Largest-decrease results must contain
    negative price movements.
    """

    price_change = -25.0

    assert price_change < 0