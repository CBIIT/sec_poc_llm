import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import click
import yaml

from Mehmet2 import logging
from Mehmet2.gpt_client import GPTClient, system_message
from Mehmet2.info_extractor import process_questions
from Mehmet2.logging import logger
from Mehmet2.settings import Settings

cwd = Path(__file__).parent
timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
default_config = cwd / "config.yaml"
default_questions = cwd / "prompts.yaml"
default_env = cwd / ".env"
default_output = cwd / ("{trial_id}_%s.csv" % timestamp)


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
    # Maps to Input Datasets A. Protocol from the original PDF.
    index_name: str,
    log_level: str,
    log_sink: Any,
):
    """Entrypoint of the PROCESS-QUESTIONS algorithm.

    Arguments:
        config_file -- Contains the Chat hyperparams and AI Search config.
        questions_file -- Maps to Input Datasets B. Questions from the original PDF.
        env_file -- Contains the environment variables to authenticate to Azure OpenAI.
        output_file -- The file where the results will be saved.
        index_name -- Maps to Input Datasets A. Protocol from the original PDF.
        log_level -- Specifies how much should be logged during execution.
        log_sink -- The file stream where logs will be written.
    """
    start = datetime.now()
    with open(config_file) as fp:
        config = yaml.safe_load(fp)
    cliargs = {"search": {"indexName": index_name}}
    settings = Settings(env_file, config, cliargs)
    logging.configure(level=log_level, sink=log_sink or sys.stdout)

    output_file = output_file.format(trial_id=index_name)
    chat = [system_message(settings.SYSTEM_MESSAGE)]
    # Algorithms Line 4.
    process_questions(
        gpt=GPTClient(settings),
        questions_file=questions_file,
        chat_history=chat,
        output_file=output_file,
    )
    end = datetime.now()
    logger.info(f"Total time: {end - start}")


if __name__ == "__main__":
    run()
