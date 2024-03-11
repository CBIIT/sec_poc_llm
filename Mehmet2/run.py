import sys
from pathlib import Path
from typing import Any

import click
import yaml

from Mehmet2 import logging
from Mehmet2.gpt_client import GPTClient, system_message
from Mehmet2.info_extractor import process_questions
from Mehmet2.settings import Settings

cwd = Path(__file__).parent
default_config = cwd / "config.yaml"
default_questions = cwd / "prompts.yaml"
default_env = cwd / ".env"
default_output = cwd / "results.csv"


@click.command
@click.option(
    "-c",
    "--config-file",
    default=default_config,
    help="Chat and search configuration file in YAML format.",
    show_default=True,
)
@click.option(
    "-q",
    "--questions-file",
    default=default_questions,
    help="Questions file in YAML format.",
    show_default=True,
)
@click.option(
    "-e",
    "--env-file",
    default=default_env,
    help="ENV file used to source OpenAI/Azure settings.",
    show_default=True,
)
@click.option(
    "--output-file",
    default=default_output,
    help="Save the results to a CSV file.",
    show_default=True,
)
@click.option(
    "-i",
    "--index-name",
    required=True,
    help="Unique name of the Trial/Protocol index to use for searching.",
)
@click.option(
    "--log-level",
    default="INFO",
    help="Set the level of the logger.",
    show_default=True,
)
@click.option(
    "--log-sink",
    help="Where to write the logs. Defaults to STDOUT.",
)
def run(
    config_file: str,
    questions_file: str,
    env_file: str,
    output_file: str,
    index_name: str,
    log_level: str,
    log_sink: Any,
):
    import chromadb
    import chromadb.utils.embedding_functions as embedding_functions

    with open(config_file) as fp:
        config = yaml.safe_load(fp)
    cliargs = {"search": {"indexName": index_name}}
    settings = Settings(env_file, config, cliargs)
    logging.configure(level=log_level, sink=log_sink or sys.stdout)

    with open((cwd / "trials" / index_name).with_suffix(".txt")) as fp:
        context = fp.read()

    context = [text.strip() for text in context.split("|")]

    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=settings.OPENAI_API_KEY,
        api_base=settings.OPENAI_API_BASE_URL,
        api_type="azure",
        deployment_id="embeddings",
        api_version=settings.OPENAI_API_VERSION,
        model_name="text-embedding-ada-002",
    )

    client = chromadb.Client()
    collection = client.create_collection(
        index_name,
        metadata={"hnsw:space": "l2"},
        embedding_function=openai_ef,
        get_or_create=True,
    )
    collection.add(documents=context, ids=[f"id{i}" for i in range(len(context))])

    chat = [system_message(settings.SYSTEM_MESSAGE)]
    process_questions(
        gpt=GPTClient(settings),
        vectorstore=collection,
        questions_file=questions_file,
        prompt2answer={"context": context},
        chat_history=chat,
        output_file=output_file,
    )


if __name__ == "__main__":
    run()
