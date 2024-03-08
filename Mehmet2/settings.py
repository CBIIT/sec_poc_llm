import os
from typing import Any

import dotenv


class Settings:
    _instance = None

    # Azure OpenAI on your own data is only supported by the 2023-08-01-preview API version
    OPENAI_API_BASE_URL = None
    OPENAI_API_KEY = None
    OPENAI_API_VERSION = None
    OPENAI_DEPLOYMENT_ID = None
    OPENAI_MODEL_TYPE = None

    # Azure AI Search setup
    AZURE_SEARCH_ENDPOINT = None
    AZURE_SEARCH_KEY = None

    # Blobs go here as a source indexing
    AZURE_STORAGE_URL = None
    AZURE_STORAGE_KEY = None

    CHAT_CONFIG = {}
    SYSTEM_MESSAGE = ""
    SEARCH_CONFIG = {}

    def __new__(cls, env_file: str, config: dict[str, Any], cliargs: dict[str, Any]):
        if cls._instance is None:
            assert dotenv.load_dotenv(env_file), f"No vars loaded from {env_file}"

            cls._instance = super(Settings, cls).__new__(cls)

            # Azure OpenAI on your own data is only supported by the 2023-08-01-preview API version
            cls._instance.OPENAI_API_BASE_URL = os.environ["OPENAI_API_BASE_URL"]
            cls._instance.OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
            cls._instance.OPENAI_API_VERSION = os.environ["OPENAI_API_VERSION"]
            cls._instance.OPENAI_DEPLOYMENT_ID = os.environ["OPENAI_API_DEPLOYMENT_ID"]
            cls._instance.OPENAI_MODEL_TYPE = os.environ["OPENAI_MODEL_TYPE"]

            # Azure AI Search setup
            cls._instance.AZURE_SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
            cls._instance.AZURE_SEARCH_KEY = os.environ["AZURE_SEARCH_KEY"]

            cls._instance.AZURE_STORAGE_URL = os.environ["AZURE_STORAGE_URL"]
            cls._instance.AZURE_STORAGE_KEY = os.environ["AZURE_STORAGE_KEY"]

            # Chat parameters
            cls._instance.CHAT_CONFIG = config["chat"]
            cls._instance.SYSTEM_MESSAGE = config.get("system_message", "")
            cls._instance.SEARCH_CONFIG = {
                "key": cls._instance.AZURE_SEARCH_KEY,
                "endpoint": cls._instance.AZURE_SEARCH_ENDPOINT,
                **config["search"],
                **cliargs["search"],
            }

        return cls._instance
