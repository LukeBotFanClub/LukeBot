# LukeBot

[![Build and Test](https://github.com/tolxe/LukeBot/actions/workflows/build-and-test.yml/badge.svg)](https://github.com/tolxe/LukeBot/actions/workflows/build-and-test.yml)

A Discord bot to poll the start.gg API for the results of a given player (originally Luke, but now configurable)
and post them to an given text channel.

Start the bot with `python3 -m luke_bot`
However, the recommended deployment method is using the Docker image at `ghcr.io/tolxe/lukebot`

The following environment variables need to be set for the bot to run:

- `GG_TOKEN`: The start.gg authentication token for polling the API
- `GG_PLAYER_ID`: The start.gg ID of the player to track the results of
- `PLAYER_NAME`: The name of the player to track the results of e.g. "Luke"
- `DISCORD_TOKEN`: The Discord bot authentication token to log in with
- `DISCORD_CHANNEL_ID`: The Discord channel ID to post the results update to
- `DEPLOYED_ENVIRONMENT`: Whether the bot is in 'dev', 'test' or 'prod' environment

The following environment variables additionally need to be set to run the tests:

- `DISCORD_TESTER_TOKEN`: The Discord bot authentication token for the test checker bot to log in with

The following environment variables can optionally be set:

- `BOT_POLLING_PERIOD`: The time in seconds between polls of the start.gg API. Defaults to 30.