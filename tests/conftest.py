import pytest
from loguru import logger

TEST_LOGGER_LEVEL = 'a'


@pytest.fixture(scope='function', autouse=True)
def logger_level_for_tests() -> str:
    """
    sets logger level for tests
    :return: logger level
    """
    if TEST_LOGGER_LEVEL == 'OFF':
        logger.remove()
    return TEST_LOGGER_LEVEL
