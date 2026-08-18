def __init__(self, config_file_path: str = "config/config.yaml"):
    self.config_file_path = Path(config_file_path)

    # Load environment variables from .env
    load_dotenv()

    # Read YAML configuration
    self.config = read_yaml_file(
        self.config_file_path
    )

    # Resolve ${VARIABLE_NAME} placeholders
    self._resolve_environment_variables()