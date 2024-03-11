from datetime import timedelta
from timeit import default_timer as timer

import backoff
import openai
import tiktoken

from Mehmet2.logging import logger
from Mehmet2.response_parser import Response
from Mehmet2.settings import Settings


def system_message(content):
    return {"role": "system", "content": content}


def user_message(content):
    return {"role": "user", "content": content}


def assistant_message(content):
    return {"role": "assistant", "content": content}


class GPTClient:
    client: openai.AzureOpenAI
    settings: Settings

    def __init__(self, settings: Settings) -> None:
        """Initialize the AzureOpenAI client from Settings."""
        self.settings = settings
        self.client = openai.AzureOpenAI(
            base_url=f"{settings.OPENAI_API_BASE_URL.removesuffix('/')}/openai/deployments/{settings.OPENAI_DEPLOYMENT_ID}/extensions",
            api_key=settings.OPENAI_API_KEY,
            api_version=settings.OPENAI_API_VERSION,
        )

    @backoff.on_exception(backoff.expo, openai.RateLimitError)
    def send_messages(self, message_text: list[dict[str, str]]):
        start = timer()
        completion = self.client.chat.completions.create(
            model=self.settings.OPENAI_DEPLOYMENT_ID,
            messages=message_text,
            extra_body={
                "dataSources": [
                    {
                        "type": "AzureCognitiveSearch",
                        "parameters": self.settings.SEARCH_CONFIG,
                    }
                ]
            },
            **self.settings.CHAT_CONFIG,
        )
        end = timer()
        logger.info(f"GPT time: {timedelta(seconds=end - start)}")
        try:
            response = Response(completion.choices[0].message.content)
        except AssertionError:
            logger.warning(
                f"Failed to parse response {completion.choices[0].message.content}."
            )
            logger.warning("Setting to empty Response.")
            response = Response("")
        return response

    def count_message_tokens(self, message_text: list[dict[str, str]]):
        """See [Azure OpenAI Samples](https://github.com/Azure/openai-samples/blob/main/Basic_Samples/Chat/chatGPT_managing_conversation.ipynb)"""
        encoding = tiktoken.encoding_for_model(self.settings.OPENAI_MODEL_TYPE)
        num_tokens = 0
        for message in message_text:
            for value in message.values():
                num_tokens += len(encoding.encode(value))
        return num_tokens
