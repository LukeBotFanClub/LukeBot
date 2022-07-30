import pytest
# import discord.ext.test as dpytest

from luke_bot.discord_bot import same_update


def test_same_update():
    update_a = (
        "Current Luke Tag - Luukifi\n"
        "Last Result:\n"
        "Tournament - The Great Kent Offensive #5\n"
        "PROGRESS : COMPLETED\n"
        "Placement : 4 in 12\n"
        "Upcoming 2 Tournaments - \n"
        "Tournament - Mega Mayhem\n"
        "Begins in 22 days, 12 hours, 49 minutes\n"
        "Tournament - Tea Party 2: Mayoral Madness\n"
        "Begins in 50 days, 12 hours, 49 minutes\n"
    )
    update_b = (
        "Current Luke Tag - Luukifi\n"
        "Last Result:\n"
        "Tournament - The Great Kent Offensive #5\n"
        "PROGRESS : COMPLETED\n"
        "Placement : 4 in 12\n"
        "Upcoming 2 Tournaments - \n"
        "Tournament - Mega Mayhem\n"
        "Begins in 22 days, 12 hours, 48 minutes\n"
        "Tournament - Tea Party 2: Mayoral Madness\n"
        "Begins in 50 days, 12 hours, 48 minutes\n"
    )
    assert same_update(update_a, update_b)

    update_c = (
        "Current Luke Tag - Luukifi\n"
        "Last Result:\n"
        "Tournament - The Great Kent Offensive #6\n"
        "PROGRESS : COMPLETED\n"
        "Placement : 5 in 12\n"
        "Upcoming 3 Tournaments - \n"
        "Tournament - Mega Mayhem\n"
        "Begins in 22 days, 12 hours, 48 minutes\n"
        "Tournament - Tea Party 2: Mayoral Madness\n"
        "Begins in 50 days, 12 hours, 48 minutes\n"
    )

    assert not same_update(update_b, update_c)


@pytest.mark.asyncio
async def test_send_to_luke_updates(bot):
    # await dpytest.message("testing")
    assert True
