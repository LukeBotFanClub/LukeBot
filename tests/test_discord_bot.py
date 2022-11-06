import logging
import os
from datetime import datetime, timedelta, timezone

import requests

from luke_bot.discord_bot import same_update
from . import test_data as test

logger = logging.getLogger(__name__)

CHANNEL_ID: int = int(os.environ["DISCORD_CHANNEL_ID"])
TOKEN: str = os.environ["DISCORD_TESTER_TOKEN"]


def request(method: str, path: str, params: dict = None, data: dict = None, json=None) -> requests.Response:
    params = params or {}
    data = data or {}
    base_url = "https://discord.com/api/v10"
    r = requests.request(
        method=method,
        url=f'{base_url}{path}',
        headers={'Authorization': f'Bot {TOKEN}'},
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


def test_luke_bot():
    # THIS TEST ASSUMES THAT THE MAIN LUKEBOT HAS JUST STARTED UP IN THE TEST SERVER WITHIN THE LAST 5 MINUTES
    channel = request('GET', f'/channels/{CHANNEL_ID}').json()
    assert channel['name'] == "luke-updates"

    messages = request('GET', f'/channels/{CHANNEL_ID}/messages', params=dict(limit=1)).json()
    latest_message = messages[0]
    assert latest_message['author']['username'] == 'TestLukeBot'
    timestamp = datetime.fromisoformat(latest_message['timestamp'])
    assert datetime.now(timezone.utc) - timestamp < timedelta(minutes=5)

    all_messages = request('GET', f'/channels/{CHANNEL_ID}/messages', params=dict(limit=100)).json()

    # DELETE ALL MESSAGES IN CHANNEL TO MAKE SURE IT'S EMPTY FOR FUTURE TESTS
    message_ids = [message['id'] for message in all_messages]
    if len(message_ids) > 1:
        request('POST', f'/channels/{CHANNEL_ID}/messages/bulk-delete', json=dict(messages=message_ids))
    elif len(message_ids) == 1:
        request('DELETE', f'/channels/{CHANNEL_ID}/messages/{message_ids[0]}')
