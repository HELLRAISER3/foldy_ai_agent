from loguru import logger
import yaml
from pathlib import Path

from src.backend.entities import SYSTEM_PROMPT_PATH
def read_yaml(path_to_yaml: Path):
    """reads yaml file and returns

    Args:
        path_to_yaml (str): path like input

    Raises:
        ValueError: if yaml file is empty
        e: empty file

    Returns:
        ConfigBox: ConfigBox type
    """
    try:
        with open(path_to_yaml) as yaml_file:
            content = yaml.safe_load(yaml_file)
            logger.info(f"yaml file: {path_to_yaml} loaded successfully")
            return content
    except Exception as e:
        raise e

if __name__ == "__main__":
    print(read_yaml(SYSTEM_PROMPT_PATH))