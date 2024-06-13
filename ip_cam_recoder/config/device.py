import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def check_for_environment(environment: str = "") -> None:
    # Set environment to be able to get the correct .env file.
    logger.debug("Environment: " + environment)
    path_to_dotenv = ""
    if len(environment) > 0:
        path_to_dotenv = f".env.{environment}"
        logger.debug("Program has a specific .env file with name: %s.", path_to_dotenv)
    else:
        path_to_dotenv = ".env"
        logger.debug("No specific .env file. Path set to default (.env).")
    load_dotenv(dotenv_path=path_to_dotenv)
    logger.info("Environment was initiated with file: %s.", path_to_dotenv)


def get_device(name_prefix: str) -> str:
    device = ""
    try:
        device = os.getenv(name_prefix)
    except:
        raise Exception("No device in environment with name: " + name_prefix)
    logger.info("Device name: %s exists in the environment.", name_prefix)
    return device
