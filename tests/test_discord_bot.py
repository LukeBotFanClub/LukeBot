import os

import pytest
import discord

from luke_bot.discord_bot import same_update
from . import test_data as test


def test_same_update():
    assert same_update(test.update_a, test.update_b)
    assert not same_update(test.update_b, test.update_c)


@pytest.mark.asyncio
async def test_send_to_luke_updates():
    # this test should somehow check that the bot sends appropriate messages into the correct channel
    # and that it correctly knows when to post a new update or skip repeats
    # should probably mock the smashgg interface though for consistent tests
    # maybe just have a list of dummy responses that feed into it with known expected results
    tester = discord.Client()
    await tester.login(os.getenv("DISCORD_TESTER_TOKEN"))
    channel = tester.get_channel(int(os.getenv("DISCORD_CHANNEL_ID")))
    assert channel.name == "luke-updates"
