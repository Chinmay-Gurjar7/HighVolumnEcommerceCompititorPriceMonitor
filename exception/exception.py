import sys
from typing import Optional


def get_error_message(
    error: Exception,
    error_detail: Optional[object] = None
) -> str:
    """
    Create a detailed error message containing:

    - Exception type
    - File where the error occurred
    - Line number
    - Original error message
    """

    if error_detail is None:
        error_detail = sys

    _, _, exc_tb = sys.exc_info()

    if exc_tb is not None:
        file_name = exc_tb.tb_frame.f_code.co_filename
        line_number = exc_tb.tb_lineno
    else:
        file_name = "Unknown"
        line_number = "Unknown"

    error_message = (
        f"Error occurred in file "
        f"[{file_name}] "
        f"at line [{line_number}]: "
        f"{str(error)}"
    )

    return error_message


class EcommercePriceMonitorException(Exception):
    """
    Base exception for the entire project.
    """

    def __init__(
        self,
        error_message: str,
        error_detail: Optional[object] = None
    ):
        super().__init__(error_message)

        self.error_message = get_error_message(
            Exception(error_message),
            error_detail
        )

    def __str__(self) -> str:
        return self.error_message


class DataIngestionException(
    EcommercePriceMonitorException
):
    """Raised when data ingestion fails."""
    pass


class DataValidationException(
    EcommercePriceMonitorException
):
    """Raised when data validation fails."""
    pass


class DataTransformationException(
    EcommercePriceMonitorException
):
    """Raised when data transformation fails."""
    pass


class DataLoadingException(
    EcommercePriceMonitorException
):
    """Raised when loading data into PostgreSQL fails."""
    pass


class DatabaseConnectionException(
    EcommercePriceMonitorException
):
    """Raised when database connection fails."""
    pass


class ConfigurationException(
    EcommercePriceMonitorException
):
    """Raised when configuration loading fails."""
    pass


class PipelineException(
    EcommercePriceMonitorException
):
    """Raised when the pipeline fails."""
    

class DataAnalysisException(Exception):
    """
    Exception raised when data analysis fails.
    """

    def __init__(self, message: str):
        super().__init__(message)