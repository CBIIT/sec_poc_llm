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
            azure_endpoint="https://cameron-openai-instance.openai.azure.com/",
            api_key=settings.OPENAI_API_KEY,
            api_version="2024-02-15-preview",
        )

    @backoff.on_exception(backoff.expo, openai.RateLimitError)
    def send_messages(self, message_text: list[dict[str, str]]):
        completion = self.client.chat.completions.create(
            model=self.settings.OPENAI_DEPLOYMENT_ID,
            messages=message_text,
            **self.settings.CHAT_CONFIG,
        )
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
