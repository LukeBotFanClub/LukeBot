import glob
import os

import pytest
import discord.ext.test as dpytest

from luke_bot.discord_bot import get_luke_bot


@pytest.fixture
def bot(event_loop):
    bot_ = get_luke_bot()
    dpytest.configure(bot_)
    return bot_


def pytest_sessionfinish():
    # Clean up attachment files
    files = glob.glob('./dpytest_*.dat')
    for path in files:
        try:
            os.remove(path)
        except Exception as e:
            print(f"Error while deleting file {path}: {e}")
