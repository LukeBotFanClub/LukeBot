import pytest
import discord.ext.test as dpytest

from luke_bot.discord_bot import same_update
from . import test_data as test


def test_same_update():
    assert same_update(test.update_a, test.update_b)
    assert not same_update(test.update_b, test.update_c)


@pytest.mark.asyncio
async def test_send_to_luke_updates(bot):
    assert True


@pytest.mark.asyncio
def test_about():
    await dpytest.message('!about')
    assert dpytest.get_message().content == "I report updates on Luke"
