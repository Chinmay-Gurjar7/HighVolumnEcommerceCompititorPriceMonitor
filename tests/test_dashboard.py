import pandas as pd
import pytest

from dashboard.app import app


@pytest.fixture
def client():
    """
    Flask test client for dashboard route testing.
    """
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_analysis(monkeypatch):
    """
    Replaces the real DataAnalysis instance with a
    deterministic mock implementation.
    """

    class MockAnalysis:

        def get_competitor_price_summary(
            self,
            product_id=None
        ):
            data = [
                {
                    "product_id": "product-1",
                    "product_name": "Test Product",
                    "brand": "Test Brand",
                    "category": "Electronics",
                    "competitor_count": 3,
                    "lowest_price": 90.0,
                    "highest_price": 120.0,
                    "average_price": 105.0,
                    "price_spread": 30.0,
                }
            ]

            if product_id:
                data = [
                    row
                    for row in data
                    if row["product_id"] == product_id
                ]

            return pd.DataFrame(data)

        def get_latest_competitor_prices(
            self,
            product_id=None
        ):
            data = [
                {
                    "product_id": "product-1",
                    "product_name": "Test Product",
                    "brand": "Test Brand",
                    "category": "Electronics",
                    "merchant_id": 1001,
                    "merchant_name": "merchant-a",
                    "price": 90.0,
                    "price_min": 90.0,
                    "price_max": 90.0,
                    "currency": "USD",
                    "condition": "new",
                    "observed_at": pd.Timestamp(
                        "2026-01-01"
                    ),
                },
                {
                    "product_id": "product-1",
                    "product_name": "Test Product",
                    "brand": "Test Brand",
                    "category": "Electronics",
                    "merchant_id": 1002,
                    "merchant_name": "merchant-b",
                    "price": 120.0,
                    "price_min": 120.0,
                    "price_max": 120.0,
                    "currency": "USD",
                    "condition": "new",
                    "observed_at": pd.Timestamp(
                        "2026-01-01"
                    ),
                },
            ]

            if product_id:
                data = [
                    row
                    for row in data
                    if row["product_id"] == product_id
                ]

            return pd.DataFrame(data)

        def get_price_change_history(
            self,
            product_id=None
        ):
            data = [
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
                    "observed_at": pd.Timestamp(
                        "2026-01-02"
                    ),
                    "price_change": -10.0,
                    "price_change_percentage": -10.0,
                }
            ]

            if product_id:
                data = [
                    row
                    for row in data
                    if row["product_id"] == product_id
                ]

            return pd.DataFrame(data)

        def get_merchant_price_change_frequency(self):
            return pd.DataFrame(
                [
                    {
                        "merchant_id": 1001,
                        "merchant_name": "merchant-a",
                        "total_observations": 100,
                        "comparable_observations": 90,
                        "price_changes": 20,
                        "price_increases": 12,
                        "price_decreases": 8,
                        "price_change_rate": 22.22,
                    }
                ]
            )

        def get_largest_price_movements(self, limit=10):

            increases = pd.DataFrame(
                [
                    {
                        "product_id": "product-1",
                        "product_name": "Test Product",
                        "merchant_id": 1001,
                        "merchant_name": "merchant-a",
                        "price": 120.0,
                        "previous_price": 100.0,
                        "price_change": 20.0,
                        "price_change_percentage": 20.0,
                    }
                ]
            )

            decreases = pd.DataFrame(
                [
                    {
                        "product_id": "product-1",
                        "product_name": "Test Product",
                        "merchant_id": 1002,
                        "merchant_name": "merchant-b",
                        "price": 90.0,
                        "previous_price": 110.0,
                        "price_change": -20.0,
                        "price_change_percentage": -18.18,
                    }
                ]
            )

            return {
                "largest_increases": increases,
                "largest_decreases": decreases,
            }
    mock = MockAnalysis()

    monkeypatch.setitem(
        app.config,
        "DATA_ANALYSIS",
        mock
    )

    return mock


def test_dashboard_page_returns_200(
    client,
    mock_analysis
):
    response = client.get("/")

    assert response.status_code == 200


def test_dashboard_page_contains_expected_content(
    client,
    mock_analysis
):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Pricing Intelligence Dashboard" in response.data
    assert b"TOTAL PRODUCTS" in response.data
    assert b"MERCHANTS" in response.data


def test_products_page_returns_200(
    client,
    mock_analysis
):
    response = client.get("/products")

    assert response.status_code == 200
    assert b"Competitive Product Pricing" in response.data
    assert b"Test Product" in response.data


def test_product_detail_page_returns_200(
    client,
    mock_analysis
):
    response = client.get(
        "/product/product-1"
    )

    assert response.status_code == 200
    assert b"Test Product" in response.data
    assert b"merchant-a" in response.data


def test_product_detail_invalid_product_returns_404(
    client,
    mock_analysis
):
    response = client.get(
        "/product/does-not-exist"
    )

    assert response.status_code == 404


def test_price_history_page_returns_200(
    client,
    mock_analysis
):
    response = client.get("/price-history")

    assert response.status_code == 200
    assert b"Price History" in response.data


def test_api_products_returns_json(
    client,
    mock_analysis
):
    response = client.get("/api/products")

    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["product_id"] == "product-1"


def test_api_product_returns_expected_structure(
    client,
    mock_analysis
):
    response = client.get(
        "/api/product/product-1"
    )

    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()

    assert "summary" in data
    assert "competitors" in data
    assert "price_history" in data


def test_api_product_invalid_product_returns_404(
    client,
    mock_analysis
):
    response = client.get(
        "/api/product/does-not-exist"
    )

    assert response.status_code == 404


def test_api_merchant_frequency_returns_json(
    client,
    mock_analysis
):
    response = client.get(
        "/api/merchant-frequency"
    )

    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["merchant_name"] == "merchant-a"


def test_api_largest_movements_returns_expected_structure(
    client,
    mock_analysis
):
    response = client.get(
        "/api/largest-movements"
    )

    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()

    assert "largest_increases" in data
    assert "largest_decreases" in data

    assert len(data["largest_increases"]) == 1
    assert len(data["largest_decreases"]) == 1


def test_api_price_history_returns_list(
    client,
    mock_analysis
):
    response = client.get(
        "/api/price-history/product-1"
    )

    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["product_id"] == "product-1"