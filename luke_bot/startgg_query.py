import logging
from datetime import datetime, timedelta

from .graphql import api_query, is_null
from .settings import settings

logger = logging.getLogger(__name__)


# Player's Start GG Info
# Slug (changes with the tag)
# user/e4082a74 for luke
PLAYER_ID: int = int(settings.GG_PLAYER_ID)
PLAYER_NAME: str = settings.PLAYER_NAME
DEFAULT_GAME_ID: int = settings.DEFAULT_GAME_ID


def get_gamer_tag() -> str:
    """Fetches Player's current Start.GG Epic Gamer Tag."""
    query = """
    query Luke($id: ID){
    user(id: $id){
        id,
        slug,
        player{
            gamerTag
            }
        }
    }
    """
    response = api_query(query, id=PLAYER_ID)
    user = response["data"]["user"]
    if is_null(user):
        raise ValueError(f"No player found with ID {PLAYER_ID}")
    tag = user["player"]["gamerTag"]
    return tag


def get_last_result(num_results: int, gamertag: str):
    """Returns the last N results from Player's profile."""
    query = """
    query LastResult($id: ID){
    user(id: $id){
        events(query:{
          perPage: %d,
          page:1
        }) {
          nodes {
            tournament {
              name
              id
              shortSlug
            }
            id
            name
            numEntrants
            state
            standings(query:{
              perPage: %d,
              page:1
              filter:{
                search:{
                  searchString:"%s"
                }
                }
              }) {
              nodes {
                entrant {
                    id
                }
                placement
                isFinal
              }
            }
          }
        }
    }
    }
    """ % (num_results, num_results, gamertag)
    response = api_query(query, id=PLAYER_ID)
    try:
        nodes = response["data"]["user"]["events"]["nodes"]
    except TypeError as e:
        logger.warning(
            f"Failed to get result from response in `get_last_result`. {response = }."
            f" Error = {e} {e.args}"
        )
        nodes = None
    return nodes


def get_upcoming_tournaments(id_: int, gamertag: str, num_results: int):
    query = """
    query Upcoming($id: ID){
    user(id: $id){
        tournaments(query: {
            perPage: %d,
            page: 1,
            filter: {
                upcoming:true
            }
        }){
            nodes{
                name
                id
                shortSlug
                startAt
                state
                events(limit:3){
                  id
                  name
                  videogame {
                      id
                  }
                  entrants(query:{filter:{name:"%s"}}){
                    nodes{
                      id
                    }
                  }
                }
            }
        }
    }
    }
    """ % (num_results, gamertag)
    response = api_query(query, id=id_)
    return response["data"]["user"]["tournaments"]["nodes"][::-1]


def process_results(response):
    """Processes list of Finalised Tournament Objects into a readable
    Format."""
    results = ""
    for event in response:
        results += f"Tournament - `{event['tournament']['name']}`"
        slug = event["tournament"]["shortSlug"]
        if slug:
            results += (
                f" - [Start.GG](https://start.gg/{event['tournament']['shortSlug']})"
            )
        results += "\n"

        results += f"PROGRESS : `{event['state']}`\n"
        placing = event["standings"]["nodes"][0]["placement"]
        results += f"Placement : `{placing}` in `{event['numEntrants']}`\n\n"

    return results


def process_upcoming(response):
    """Processes list of Upcoming Tournament Objects into a readable format."""
    results = ""
    for event in response:
        results += f"Tournament - `{event['name']}`"
        slug = event["shortSlug"]
        if slug:
            results += f" - [Start.GG](https://start.gg/{event['shortSlug']})"
        results += "\n"
        event_start = datetime.utcfromtimestamp(event["startAt"])
        event_starts_in = event_start - datetime.utcnow()
        days, hours, minutes = (
            event_starts_in.days,
            event_starts_in.seconds // 3600,
            event_starts_in.seconds // 60 % 60,
        )
        if event_starts_in < timedelta():
            results += (
                f"Started `{abs(days)}` days, `{hours}` hours, `{minutes}` minutes"
                " ago\n"
            )
            event_id = event["id"]
            entrant_id = -1
            # Filter for Smash Ultimate and 'Single' in event name
            for events in event["events"]:
                if (
                        "single" in events["name"].lower()
                        and events["videogame"]["id"] == DEFAULT_GAME_ID
                        and events["entrants"]["nodes"]
                ):
                    entrant_id = events["entrants"]["nodes"][0]["id"]
                    event_id = events["id"]
                    break
            # If still empty, take any Smash Ultimate event
            if entrant_id == -1:
                for events in event["events"]:
                    if (
                        events["videogame"]["id"] == DEFAULT_GAME_ID
                        and events["entrants"]["nodes"]
                    ):
                        entrant_id = events["entrants"]["nodes"][0]["id"]
                        event_id = events["id"]
                        break

            set_scores = ongoing_results(event_id, entrant_id)
            results += process_set_results(set_scores, entrant_id)

        else:
            results += (
                f"Begins in `{days}` days, `{hours}` hours, `{minutes}` minutes\n"
            )
    return results


def process_set_results(set_scores: list, entrant_id: int):
    results = ""
    results += f"Set Score{'s' if len(set_scores) > 1 else ''} -\n"
    for set_result in set_scores:
        results += f"`{set_result['fullRoundText']}` -\n"
        if set_result["displayScore"]:
            emoji = (
                ":crown:"
                if entrant_id == set_result["winnerId"]
                else ":regional_indicator_f:"
            )
            results += f"{set_result['displayScore']}                 {emoji}\n"
        else:
            results += (
                f"{PLAYER_NAME} is waiting for their opponent in"
                f" {set_result['fullRoundText']}\n"
            )
    return results


def ongoing_results(event_id: int, entrant_id: int):
    query = """
    query InProgressResults($event_id: ID, $entrant_id: ID){
    event(id: $event_id){
        tournament{
            name
        }
        name
        sets(filters:{entrantIds:[$entrant_id]}){
            nodes{
                fullRoundText
                displayScore
                wPlacement
                lPlacement
                winnerId
                round
            }
        }
        }
    }
    """
    response = api_query(query, event_id=event_id, entrant_id=entrant_id)
    event = response["data"]["event"]
    if not is_null(event):
        current_results = event["sets"]["nodes"][::-1]
    else:
        current_results = []
    return current_results


STARTGG_ISSUE_MSG = (
    "There was an issue fetching data from start.gg, please try again later"
)


def get_last_bracket_run() -> str:
    """Fetches the full bracket run from Luke's last tournament."""
    gamertag = get_gamer_tag()
    results = ""
    last_result = get_last_result(1, gamertag)
    if is_null(last_result):
        return STARTGG_ISSUE_MSG

    results += process_results(last_result)

    event_id = last_result[0]["id"]
    entrant_id = last_result[0]["standings"]["nodes"][0]["entrant"]["id"]
    bracket_results = ongoing_results(event_id, entrant_id)

    results += process_set_results(bracket_results, entrant_id)
    return results


def get_last_set() -> str:
    """Fetches the full bracket run from Luke's last tournament."""
    gamertag = get_gamer_tag()
    results = ""
    last_result = get_last_result(1, gamertag)
    if is_null(last_result):
        return STARTGG_ISSUE_MSG

    event_id = last_result[0]["id"]
    entrant_id = last_result[0]["standings"]["nodes"][0]["entrant"]["id"]
    bracket_results = ongoing_results(event_id, entrant_id)

    results += process_set_results([bracket_results[-1]], entrant_id)
    return results


def check_luke() -> str | None:
    results = ""
    gamertag = get_gamer_tag()
    last_result = get_last_result(1, gamertag)
    if is_null(last_result):
        return None
    upcoming = get_upcoming_tournaments(PLAYER_ID, gamertag, 5)
    results += f"**Current {PLAYER_NAME} Tag** - `{gamertag}`\n"
    results += "Last Result:\n"
    results += process_results(last_result)
    results += f"Upcoming `{len(upcoming)}` Tournaments - \n"
    results += process_upcoming(upcoming)
    return results
