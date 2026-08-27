from pathlib import Path

import pytest

from components.data_ingestion import DataIngestion
from exception.exception import DataIngestionException


def test_data_ingestion_creates_timestamped_copy(tmp_path):
    source_file = tmp_path / "source.csv"
    source_file.write_text(
        "product_id,price\n"
        "product-1,99.99\n",
        encoding="utf-8"
    )

    raw_dir = tmp_path / "artifacts" / "raw"

    data_source_config = type(
        "DataSourceConfig",
        (),
        {
            "input_file": str(source_file)
        }
    )()

    artifact_config = type(
        "ArtifactConfig",
        (),
        {
            "raw_dir": str(raw_dir)
        }
    )()

    ingestion = DataIngestion(
        data_source_config,
        artifact_config
    )

    result = ingestion.initiate_data_ingestion()

    assert isinstance(result, Path)
    assert result.exists()
    assert result.is_file()
    assert result.parent == raw_dir
    assert result.suffix == ".csv"
    assert source_file.exists()


def test_data_ingestion_preserves_source_file(tmp_path):
    source_file = tmp_path / "source.csv"

    original_content = (
        "product_id,price\n"
        "product-1,99.99\n"
    )

    source_file.write_text(
        original_content,
        encoding="utf-8"
    )

    raw_dir = tmp_path / "raw"

    data_source_config = type(
        "DataSourceConfig",
        (),
        {
            "input_file": str(source_file)
        }
    )()

    artifact_config = type(
        "ArtifactConfig",
        (),
        {
            "raw_dir": str(raw_dir)
        }
    )()

    ingestion = DataIngestion(
        data_source_config,
        artifact_config
    )

    result = ingestion.initiate_data_ingestion()

    assert source_file.read_text(
        encoding="utf-8"
    ) == original_content

    assert result.read_text(
        encoding="utf-8"
    ) == original_content


def test_data_ingestion_creates_raw_directory(tmp_path):
    source_file = tmp_path / "products.csv"

    source_file.write_text(
        "product_id,price\n"
        "product-1,50\n",
        encoding="utf-8"
    )

    raw_dir = tmp_path / "nested" / "artifacts" / "raw"

    data_source_config = type(
        "DataSourceConfig",
        (),
        {
            "input_file": str(source_file)
        }
    )()

    artifact_config = type(
        "ArtifactConfig",
        (),
        {
            "raw_dir": str(raw_dir)
        }
    )()

    ingestion = DataIngestion(
        data_source_config,
        artifact_config
    )

    result = ingestion.initiate_data_ingestion()

    assert raw_dir.exists()
    assert raw_dir.is_dir()
    assert result.exists()


def test_data_ingestion_fails_for_missing_source(tmp_path):
    source_file = tmp_path / "does_not_exist.csv"
    raw_dir = tmp_path / "raw"

    data_source_config = type(
        "DataSourceConfig",
        (),
        {
            "input_file": str(source_file)
        }
    )()

    artifact_config = type(
        "ArtifactConfig",
        (),
        {
            "raw_dir": str(raw_dir)
        }
    )()

    ingestion = DataIngestion(
        data_source_config,
        artifact_config
    )

    with pytest.raises(DataIngestionException):
        ingestion.initiate_data_ingestion()


def test_data_ingestion_fails_when_source_is_directory(tmp_path):
    source_directory = tmp_path / "source"
    source_directory.mkdir()

    raw_dir = tmp_path / "raw"

    data_source_config = type(
        "DataSourceConfig",
        (),
        {
            "input_file": str(source_directory)
        }
    )()

    artifact_config = type(
        "ArtifactConfig",
        (),
        {
            "raw_dir": str(raw_dir)
        }
    )()

    ingestion = DataIngestion(
        data_source_config,
        artifact_config
    )

    with pytest.raises(DataIngestionException):
        ingestion.initiate_data_ingestion()