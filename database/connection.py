from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL

from utils.config_manager import ConfigurationManager


def create_database_engine() -> Engine:
    """
    Create and return a SQLAlchemy engine for PostgreSQL.

    Database credentials are loaded through:
        .env
          ↓
        config.yaml
          ↓
        ConfigurationManager
          ↓
        SQLAlchemy Engine
    """

    config_manager = ConfigurationManager()

    db_config = config_manager.get_database_config()

    database_url = URL.create(
        drivername="postgresql+psycopg2",
        username=db_config.username,
        password=db_config.password,
        host=db_config.host,
        port=db_config.port,
        database=db_config.name,
    )

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
    )

    return engine


def test_database_connection() -> bool:
    """
    Test the PostgreSQL database connection.

    Returns:
        True if connection succeeds.

    Raises:
        Exception if connection fails.
    """

    engine = create_database_engine()

    try:
        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT version();")
            )

            postgres_version = result.scalar()

            print("Database connection successful.")
            print(f"PostgreSQL version: {postgres_version}")

            return True

    finally:
        engine.dispose()


if __name__ == "__main__":
    test_database_connection()