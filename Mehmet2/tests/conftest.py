import pytest

from Mehmet2 import logging


def pytest_addoption(parser):
    parser.addoption("--log-lvl", action="store", default="CRITICAL")


@pytest.fixture(scope="session", autouse=True)
def log_config(pytestconfig):
    logging.configure(level=pytestconfig.getoption("log_lvl"))
