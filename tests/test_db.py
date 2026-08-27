from unittest.mock import MagicMock, patch

from utils.database import DatabaseManager


def test_get_connection_url():
    """
    Connection URL should contain the expected PostgreSQL
    driver and database configuration.
    """

    config = MagicMock()

    config.username = "test_user"
    config.password = "test_password"
    config.host = "localhost"
    config.port = 5432
    config.name = "test_database"

    manager = DatabaseManager(config)

    url = manager.get_connection_url()

    assert (
        url
        == "postgresql+psycopg2://"
        "test_user:test_password"
        "@localhost:5432/test_database"
    )


def test_get_connection_url_encodes_special_characters():
    """
    Username and password must be URL encoded so special
    characters do not break the PostgreSQL connection URL.
    """

    config = MagicMock()

    config.username = "test@example.com"
    config.password = "p@ss:word/123"
    config.host = "localhost"
    config.port = 5432
    config.name = "test_database"

    manager = DatabaseManager(config)

    url = manager.get_connection_url()

    assert "test%40example.com" in url
    assert "p%40ss%3Aword%2F123" in url


@patch("utils.database.create_engine")
def test_get_engine_creates_engine(mock_create_engine):
    """
    get_engine() should create a SQLAlchemy engine when
    one does not already exist.
    """

    config = MagicMock()

    config.username = "test_user"
    config.password = "test_password"
    config.host = "localhost"
    config.port = 5432
    config.name = "test_database"

    mock_engine = MagicMock()

    mock_create_engine.return_value = mock_engine

    manager = DatabaseManager(config)

    engine = manager.get_engine()

    assert engine is mock_engine
    mock_create_engine.assert_called_once()


@patch("utils.database.create_engine")
def test_get_engine_reuses_existing_engine(mock_create_engine):
    """
    get_engine() should reuse the existing engine instead of
    creating a new SQLAlchemy engine every time.
    """

    config = MagicMock()

    config.username = "test_user"
    config.password = "test_password"
    config.host = "localhost"
    config.port = 5432
    config.name = "test_database"

    mock_engine = MagicMock()

    mock_create_engine.return_value = mock_engine

    manager = DatabaseManager(config)

    first_engine = manager.get_engine()
    second_engine = manager.get_engine()

    assert first_engine is second_engine
    mock_create_engine.assert_called_once()