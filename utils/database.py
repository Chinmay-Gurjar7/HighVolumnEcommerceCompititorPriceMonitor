from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from entity.config_entity import DatabaseConfig
from exception.exception import DatabaseConnectionException
from logger.logger import get_logger


logger = get_logger(__name__)


class DatabaseManager:

    def __init__(
        self,
        database_config: DatabaseConfig
    ):
        self.database_config = database_config
        self.engine = None

    def get_connection_url(self) -> str:
        """
        Builds the PostgreSQL SQLAlchemy connection URL.
        """

        try:

            username = quote_plus(
                self.database_config.username
            )

            password = quote_plus(
                self.database_config.password
            )

            host = self.database_config.host
            port = self.database_config.port
            database = self.database_config.name

            connection_url = (
                f"postgresql+psycopg2://"
                f"{username}:{password}"
                f"@{host}:{port}/{database}"
            )

            return connection_url

        except Exception as error:

            logger.error(
                f"Failed to build database connection URL: "
                f"{error}"
            )

            raise DatabaseConnectionException(
                str(error)
            )

    def get_engine(self) -> Engine:
        """
        Creates and returns a SQLAlchemy engine.
        """

        try:

            if self.engine is not None:
                return self.engine

            connection_url = (
                self.get_connection_url()
            )

            logger.info(
                "Creating PostgreSQL SQLAlchemy engine..."
            )

            self.engine = create_engine(
                connection_url,
                pool_pre_ping=True,
                pool_recycle=1800,
                future=True
            )

            logger.info(
                "PostgreSQL SQLAlchemy engine created successfully."
            )

            return self.engine

        except Exception as error:

            logger.error(
                f"Failed to create PostgreSQL engine: "
                f"{error}"
            )

            raise DatabaseConnectionException(
                str(error)
            )

    def test_connection(self) -> bool:
        """
        Tests the PostgreSQL database connection.
        """

        try:

            engine = self.get_engine()

            with engine.connect() as connection:

                connection.execute(
                    text("SELECT 1")
                )

            logger.info(
                "PostgreSQL database connection successful."
            )

            return True

        except Exception as error:

            logger.error(
                f"PostgreSQL database connection failed: "
                f"{error}"
            )

            raise DatabaseConnectionException(
                str(error)
            )

    def dispose(self) -> None:
        """
        Closes the SQLAlchemy connection pool.
        """

        if self.engine is not None:

            self.engine.dispose()

            logger.info(
                "PostgreSQL connection pool disposed."
            )

            self.engine = None