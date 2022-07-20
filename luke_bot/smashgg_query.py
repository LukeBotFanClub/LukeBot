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


def get_gamer_tag():
    # Fetches Luke's current Start.GG Epic Gamer Tag
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


def last_result(num_results):
    #  Returns the last N results from Luke's profile
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
    ''' % (num_results, num_results, GAMERTAG)
    raw_response = requests.post(endpoint, json={'query': query, 'variables': {'id': ID}}, headers=headers)
    response = raw_response.json()
    return response['data']['user']['events']['nodes']


def upcoming_tournaments():
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
    for event in response:
        print("Tournament - ", event['tournament']['name'])
        print("PROGRESS : ", event['state'])
        print(
            "Placement : %d in %d " % (event['standings']['nodes'][0]['placement'],
                                       event['numEntrants'])
        )


def process_upcoming(response):
    # Processes list of Upcoming Tournament Objects into
    # a readable format
    for event in response:
        print("Tournament - ", event['name'])
        ts = event['startAt']
        td = datetime.utcfromtimestamp(ts) - datetime.now()
        days, hours, minutes = td.days, td.seconds // 3600, td.seconds // 60 % 60
        print("Begins in %d days, %d hours, %d minutes" % (days, hours, minutes))


if __name__ == "__main__":
    GAMERTAG = get_gamer_tag()
    LAST_RESULT = last_result(1)
    UPCOMING = upcoming_tournaments()
    print("Current Luke Tag - ", GAMERTAG)
    print("Last Result:")
    process_results(LAST_RESULT)
    print(f"Upcoming {len(UPCOMING)} Tournaments - ")
    process_upcoming(UPCOMING)
