import logging
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

import dotenv
import requests

dotenv.load_dotenv()

from luke_bot.discord_bot import same_update  # noqa: E402

from . import test_data as test  # noqa: E402

logger = logging.getLogger(__name__)

CHANNEL_ID: int = int(os.environ["DISCORD_CHANNEL_ID"])
TOKEN: str = os.environ["DISCORD_TESTER_TOKEN"]
TEST_BOT_NAME = "TestLukeBot"
TEST_BOT_ID = 1002654448826454097


def request(
    method: str,
    path: str,
    params: dict | None = None,
    data: dict | None = None,
    json: dict | None = None,
) -> requests.Response:
    params = params or {}
    data = data or {}
    base_url = "https://discord.com/api/v10"
    r = requests.request(
        method=method,
        url=f"{base_url}{path}",
        headers={"Authorization": f"Bot {TOKEN}"},
        params=params,
        data=data,
        json=json,
    )
    message = f"{method} {path}"
    try:
        d = r.json()
    except requests.exceptions.JSONDecodeError:
        d = r
    logger.info(f"{message} {d}")
    return r


def test_same_update():
    assert same_update(test.update_a, test.update_b)
    assert not same_update(test.update_b, test.update_c)


def get_latest_message(expecting_message: bool = True) -> Optional[dict]:
    messages = request(
        "GET", f"/channels/{CHANNEL_ID}/messages", params=dict(limit=1)
    ).json()
    if expecting_message:
        assert len(messages) == 1
        latest_message = messages[0]
        return latest_message
    else:
        return None


def test_channel():
    channel = request("GET", f"/channels/{CHANNEL_ID}").json()
    assert channel["name"] == "luke-updates"


def test_standard_update():
    # THIS TEST ASSUMES THAT THE MAIN LUKEBOT HAS JUST STARTED UP IN THE TEST SERVER WITHIN THE LAST 5 MINUTES
    # also relies on other tests not happening first
    latest_message = get_latest_message()
    if latest_message is not None:
        assert latest_message["author"]["username"] == TEST_BOT_NAME
        timestamp = datetime.fromisoformat(latest_message["timestamp"])
        assert datetime.now(timezone.utc) - timestamp < timedelta(minutes=5)


def test_help_command():
    help_message_json = dict(
        content=f"<@{TEST_BOT_ID}> help",
    )
    request("POST", f"/channels/{CHANNEL_ID}/messages", json=help_message_json)
    time.sleep(0.5)
    latest_message = get_latest_message()
    if latest_message is not None:
        assert latest_message["author"]["username"] == TEST_BOT_NAME


def test_clean_up():
    # DELETE ALL MESSAGES IN CHANNEL TO MAKE SURE IT'S EMPTY FOR FUTURE TESTS
    #  a bit cheeky in that i'm assuming this runs after the other tests since i define it last
    # this works but i should probably work out how to do it with a pytest fixture
    all_messages = request(
        "GET", f"/channels/{CHANNEL_ID}/messages", params=dict(limit=100)
    ).json()
    message_ids = [message["id"] for message in all_messages]
    if len(message_ids) > 1:
        request(
            "POST",
            f"/channels/{CHANNEL_ID}/messages/bulk-delete",
            json=dict(messages=message_ids),
        )
    elif len(message_ids) == 1:
        request("DELETE", f"/channels/{CHANNEL_ID}/messages/{message_ids[0]}")
