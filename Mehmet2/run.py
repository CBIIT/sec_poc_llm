from pathlib import Path

import click
import yaml

from Mehmet2.gpt_client import GPTClient, system_message
from Mehmet2.info_extractor import process_questions
from Mehmet2.settings import Settings

cwd = Path(__file__).parent
default_config = cwd / "config.yaml"
default_questions = cwd / "prompts.yaml"
default_env = cwd / ".env"


@click.command
@click.option(
    "-c",
    "--config-file",
    "config",
    default=default_config,
    help="Config file",
    show_default=True,
)
@click.option(
    "-q",
    "--questions-file",
    "questions",
    default=default_questions,
    help="Questions file (YAML format)",
    show_default=True,
)
@click.option(
    "-e",
    "--env-file",
    "env",
    default=default_env,
    help="ENV file used to source OpenAI/Azure settings",
    show_default=True,
)
@click.option(
    "-i",
    "--index-name",
    help="Unique name of the Trial/Protocol index to use for searching.",
)
def run(config: str, questions: str, env: str, index_name: str):
    with open(config) as fp:
        config = yaml.safe_load(fp)
    if index_name:
        config["search"]["indexName"] = index_name
    settings = Settings(env, config)

    chat = [system_message(settings.SYSTEM_MESSAGE)]
    results = []
    process_questions(
        gpt=GPTClient(settings),
        question_file=questions,
        chat_history=chat,
        results=results,
    )


if __name__ == "__main__":
    run()
