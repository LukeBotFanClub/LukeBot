import os

import requests
from datetime import datetime

token = os.getenv('API_TOKEN')
headers = {'authorization': f'Bearer {token} '}

# Luke's Start GG Info
# Slug (changes with the tag)
# user/e4082a74
ID = 1116942

endpoint = "https://api.start.gg/gql/alpha"


def get_gamer_tag() -> str:
    """Fetches Luke's current Start.GG Epic Gamer Tag"""
    query = '''
    query Luke($id: ID){
    user(id: $id){
        id,
        slug,
        player{
            gamerTag
            }
        }
    }
    '''

    raw_response = requests.post(endpoint, json={'query': query, 'variables': {'id': ID}}, headers=headers)
    tag = raw_response.json()['data']['user']['player']['gamerTag']
    return tag


def get_last_result(num_results: int, gamertag: str):
    """Returns the last N results from Luke's profile"""
    query = '''
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
            }
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
                placement
                isFinal
              }
            }
          }
        }
    }
    }
    ''' % (num_results, num_results, gamertag)
    raw_response = requests.post(endpoint, json={'query': query, 'variables': {'id': ID}}, headers=headers)
    response = raw_response.json()
    return response['data']['user']['events']['nodes']


def get_upcoming_tournaments():
    query = '''
    query Upcoming($id: ID){
    user(id: $id){
        tournaments(query: {
            perPage: 5,
            page: 1,
            filter: {
                upcoming:true
            }
        }){
            nodes{
                name
                id
                startAt
                state
            }
        }
    }
    }
    '''
    raw_response = requests.post(endpoint, json={'query': query, 'variables': {'id': ID}}, headers=headers)
    response = raw_response.json()
    return response['data']['user']['tournaments']['nodes'][::-1]


def process_results(response):
    """Processes list of Finalised Tournament Objects into a readable Format"""
    results = ""
    for event in response:
        results += f"Tournament - {event['tournament']['name']}\n"
        results += f"PROGRESS : {event['state']}\n"
        placing = event['standings']['nodes'][0]['placement']
        results += f"Placement : {placing} in {event['numEntrants']}\n"

    return results


def process_upcoming(response):
    """Processes list of Upcoming Tournament Objects into a readable format"""
    results = ""
    for event in response:
        results += f"Tournament - {event['name']}\n"
        ts = event['startAt']
        td = datetime.utcfromtimestamp(ts) - datetime.now()
        days, hours, minutes = td.days, td.seconds // 3600, td.seconds // 60 % 60
        results += f"Begins in {days} days, {hours} hours, {minutes} minutes\n"
    return results


def check_luke():
    results = ""
    gamertag = get_gamer_tag()
    last_result = get_last_result(1, gamertag)
    upcoming = get_upcoming_tournaments()
    results += f"Current Luke Tag - {gamertag}\n"
    results += "Last Result:\n"
    results += process_results(last_result)
    results += f"Upcoming {len(upcoming)} Tournaments - \n"
    results += process_upcoming(upcoming)
    return results


if __name__ == "__main__":
    print(check_luke())
