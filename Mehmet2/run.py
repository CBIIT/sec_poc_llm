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
    with open(config_file) as fp:
        config = yaml.safe_load(fp)
    cliargs = {"search": {"indexName": index_name}}
    settings = Settings(env_file, config, cliargs)
    logging.configure(level=log_level, sink=log_sink or sys.stdout)

    chat = [system_message(settings.SYSTEM_MESSAGE)]
    process_questions(
        gpt=GPTClient(settings),
        questions_file=questions_file,
        chat_history=chat,
        output_file=output_file,
    )


if __name__ == "__main__":
    run()
