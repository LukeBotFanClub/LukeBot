import logging
from datetime import datetime, timedelta

import startgg
from startgg import StartGGClient

from .settings import bot_settings

logger = logging.getLogger(__name__)


# Player's Start GG Info
# Slug (changes with the tag)
# user/e4082a74 for luke
PLAYER_ID: str = str(bot_settings.GG_PLAYER_ID)
PLAYER_NAME: str = bot_settings.PLAYER_NAME
DEFAULT_GAME_ID: str = str(bot_settings.DEFAULT_GAME_ID)
WINNER_EMOTE: str = ":crown:"
LOSER_EMOTE: str = ":regional_indicator_f:"


def get_client() -> StartGGClient:
    client = StartGGClient(
        url="https://api.start.gg/gql/alpha",
        headers={"Authorization": f"Bearer {bot_settings.GG_TOKEN.get_secret_value()}"},
    )
    return client


async def process_results(
    results_list: list[startgg.LastResultUserEventsNodes] | None,
) -> str:
    """Processes list of Finalised Tournament Objects into a readable
    Format."""
    if results_list is None:
        return ""
    results = ""
    for event in results_list:
        results += f"Tournament - `{event.tournament.name}`"
        slug = event.tournament.short_slug
        if slug:
            results += f" - [Start.GG](https://start.gg/{slug})"
        results += "\n"

        results += f"PROGRESS : `{event.state.value}`\n"
        standings = event.standings.nodes
        if standings:
            placing = event.standings.nodes[0].placement
            results += f"Placement : `{placing}` in `{event.num_entrants}`\n\n"

    return results


async def process_upcoming(
    results_list: list[startgg.UpcomingUserTournamentsNodes] | None,
    client: StartGGClient = None,
) -> str:
    if client is None:
        client = get_client()
    """Processes list of Upcoming Tournament Objects into a readable format."""
    if results_list is None:
        return ""
    results = ""
    for tournament in results_list:
        results += f"Tournament - `{tournament.name}`"
        slug = tournament.short_slug
        if slug:
            results += f" - [Start.GG](https://start.gg/{slug})"
        results += "\n"
        now = datetime.now(tz=tournament.start_at.tzinfo)
        tournament_starts_in = tournament.start_at - now
        days, hours, minutes = (
            tournament_starts_in.days,
            tournament_starts_in.seconds // 3600,
            tournament_starts_in.seconds // 60 % 60,
        )
        if tournament_starts_in < timedelta():
            results += (
                f"Started `{abs(days)}` days, `{hours}` hours, `{minutes}` minutes"
                " ago\n"
            )

            relevant_events = [
                event_
                for event_ in tournament.events
                if event_.videogame.id == DEFAULT_GAME_ID and event_.entrants.nodes
            ]
            if relevant_events:
                entrant_id = None
                # Filter for Smash Ultimate and 'Single' in event name
                for event in relevant_events:
                    if "single" in event.name.lower():
                        selected_event = event
                        break
                else:
                    # Fallback to the first event
                    selected_event = relevant_events[0]
                entrants = selected_event.entrants.nodes
                if entrants:
                    entrant_id = entrants[0].id
                event_id = selected_event.id

                in_progress_results = await client.in_progress_results(
                    event_id, entrant_id
                )
                set_scores = in_progress_results.event.sets.nodes[::-1]
                results += await process_set_results(set_scores, entrant_id)

        else:
            results += (
                f"Begins in `{days}` days, `{hours}` hours, `{minutes}` minutes\n"
            )
    return results


async def process_set_results(
    set_scores: list[startgg.InProgressResultsEventSetsNodes] | None,
    entrant_id: str | None,
) -> str:
    if not set_scores:
        return ""
    results = ""
    results += f"Set Score{'s' if len(set_scores) > 1 else ''} -\n"
    for set_result in set_scores:
        results += f"`{set_result.full_round_text}` -\n"
        if set_result.display_score:
            emoji = WINNER_EMOTE if entrant_id == set_result.winner_id else LOSER_EMOTE
            results += f"{set_result.display_score}{emoji:>17}\n"
        else:
            results += (
                f"{PLAYER_NAME} is waiting for their opponent in"
                f" {set_result.full_round_text}\n"
            )
    return results


async def get_last_bracket_run(client: StartGGClient = None) -> str:
    """Fetches the full bracket run from Luke's last tournament."""
    if client is None:
        client = get_client()
    gamertag_response = await client.gamer_tag(bot_settings.GG_PLAYER_ID)
    gamertag = gamertag_response.user.player.gamer_tag
    results = ""
    last_result_response = await client.last_result(
        bot_settings.GG_PLAYER_ID, 1, gamertag
    )
    last_result = last_result_response.user.events.nodes
    results += await process_results(last_result)

    event_id = last_result[0].id
    entrant_id = last_result[0].standings.nodes[0].entrant.id
    bracket_results_response = await client.in_progress_results(event_id, entrant_id)
    bracket_results = bracket_results_response.event.sets.nodes
    results += await process_set_results(bracket_results, entrant_id)
    return results


async def get_last_set(client: StartGGClient = None) -> str:
    """Fetches the full bracket run from Luke's last tournament."""
    if client is None:
        client = get_client()
    gamertag_response = await client.gamer_tag(bot_settings.GG_PLAYER_ID)
    gamertag = gamertag_response.user.player.gamer_tag
    results = ""
    last_result_response = await client.last_result(
        bot_settings.GG_PLAYER_ID, 1, gamertag
    )
    last_result = last_result_response.user.events.nodes
    event_id = last_result[0].id
    entrant_id = last_result[0].standings.nodes[0].entrant.id
    bracket_results_response = await client.in_progress_results(event_id, entrant_id)
    bracket_results = bracket_results_response.event.sets.nodes

    results += await process_set_results([bracket_results[-1]], entrant_id)
    return results


async def check_luke() -> str | None:
    client = get_client()
    gamertag_response = await client.gamer_tag(bot_settings.GG_PLAYER_ID)
    gamertag = gamertag_response.user.player.gamer_tag
    last_result_response = await client.last_result(
        bot_settings.GG_PLAYER_ID, 1, gamertag
    )
    last_result = last_result_response.user.events.nodes
    upcoming_response = await client.upcoming(bot_settings.GG_PLAYER_ID, 5, gamertag)
    upcoming = upcoming_response.user.tournaments.nodes[::-1]

    results = ""
    results += f"**Current {PLAYER_NAME} Tag** - `{gamertag}`\n"
    results += "Last Result:\n"
    results += await process_results(last_result)
    results += f"Upcoming `{len(upcoming)}` Tournaments - \n"
    results += await process_upcoming(upcoming, client)
    return results
