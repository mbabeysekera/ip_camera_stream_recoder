import os
from dotenv import load_dotenv


def check_for_environment(environment=""):
    # Set environment to be able to get the correct .env file.
    path_to_dotenv = ""
    if len(environment) > 0:
        path_to_dotenv = f".env.{environment}"
    else:
        path_to_dotenv = ".env"
    load_dotenv(dotenv_path=path_to_dotenv)


def get_device(name_prefix):
    return os.getenv(name_prefix)
