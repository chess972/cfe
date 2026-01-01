""" data.py - the data managing part of the CFE/CFT/LFR managing app
    (c) 2025-2026 by MFH
"""
import streamlit as st
import requests
from collections import defaultdict

API_URL = "https://api.chess.com/pub"
HEADERS = {'User-Agent': 'ChessCom-LFR-Project'}

@st.cache_data(ttl=3600) # Auto-refresh every hour
def fetch_data(endpoint, version=0):
    """
Fetch data from the chess.com API, cf. http://chess.com/news/view/published-data-api/.
`endpoint` will be appended to the global `API_URL` + '/'.
Includes the global HEADERS (in particular: a User-Agent) in the request.
`version` is a 'dummy' variable; changing it forces a re-fetch.
    """
    try:
      response = requests.get(f"{API_URL}/{endpoint}", headers=HEADERS)
      response.raise_for_status() # Important: catch 404s/500s
      return response.json()
    except Exception as e:
      # Using st.warning instead of st.error is often softer for the UI
      st.warning(f"Erreur lors de `get(API/{endpoint})`: {e}")
    return {} # Return empty dict so the rest of the app doesn't crash

def get_version(key, increment=False):
    if 'refresh' not in st.session_state:
        st.session_state.refresh = defaultdict(int)
    if increment: st.session_state.refresh[key] += 1
    return st.session_state.refresh[key]
  
def get_club_data(club_id, refresh=False) -> dict:
  """
  Fetch data for a specific club using its "URL ID", which is the same as the
  base name of the club's URL, e.g., 'martinique' for www.chess.com/club/martinique.
  An "extended" `club_id` can be provided, e.g., 'martinique/matches',
  to get more specific data relate to that club: for the possible enpoints,
  see chess.com/news/view/published-data-api#pubapi-endpoint-club-profile
  If `refresh` is Truthy, it increments the version counter for 'club_data',
    forcing a fresh API call.

  Returns: a dict with data depending on the (possibly extended) `club_id`.
    For a plain club_id, it returns the basic club data:
      {'name':..., 'club_id': API_URL/.../id, 'url': CC_URL/.../id, 'members_count':...,
       'created', 'last_activity', 'country', 'average_rating', 'icon', 'join_request',
       'visibility', 'description', 'rules', 'timezone', 'admin', "description"}

  If the club_id has a "sub-directory" appended, e.g., '{club_id}/members' or
  '{club_id}/matches', then the corresponding, more specific data is returned
  instead: see the dedicated functions below.
  """
  return fetch_data("club/" + club_id, get_version('club_data', refresh))

def get_club_members(club_url_id): # Pas vraiment utile
  """
  Fetch the list of members for chess.com/club/{club_url_id}.
  Returns a dictionary with three items: "weekly", "monthly" and "all_time",
  each of which is a list of dicts: {"username": (username:str), "joined": (timestamp:int)}.

  Members are grouped by club-activity frequency, the club-activity being one of:
  * Viewing the club homepage, the club's news index or a specific news article
      (but not the notification message received that the news was published),
  * Viewing the club's forums or a specific forum thread,
  * Changing their club settings, including modifying their membership; for admins,
      this includes inviting or authorizing new members;
  * Viewing the club's tournament, team match, or votechess lists;
  * Viewing club membership lists or running a related search, or viewing the leaderboards for the club
  NB: Playing a club game is not counted as a club-activity!
  """
  return fetch_club_data(club_url_id + "/members")

def fetch_club_matches(club_url_id):
  """
Fetch, store and return the dict of daily and club matches for chess.com/club/{club_url_id}.

The result is a dict with three lists of matches, grouped by status:
{"finished": [...], "in_progress": [...], "registered": [...]}. Each match is a dict
MATCH = { '@id': (URL of team match API endpoint), 'name': (name of the match),
    'opponent': (URL of club profile API endpoint),
    'start_time': (unix timestamp), 'time_class': 'daily' (or ...?),
    (and only for finished matches) 'result': "win" or "lose" or "draw" }

The result is stored in clubs_info_dict[club_url_id]['matches']. If that dict
already exists and is nonempty, it is returned instead of fetching through the API.
  """
  global clubs_info_dict
  if not(club_info := clubs_info_dict.get(club_url_id)):
      clubs_info_dict[club_url_id] = club_info = fetch_club_data(club_url_id)
  if not(matches := club_info.get('matches')):
      club_info['matches'] = matches = fetch_club_data(club_url_id + "/matches")
  return matches

# team matches
"""All team matches-based URLs use the match "ID" to specify which match you want data for.
https://api.chess.com/pub/match/{ID}

The ID is the same as found in the URL for the team match web page on www.chess.com.
For example, the ID WORLD LEAGUE Round 5: Romania vs USA Southwest is 12803.
"""

def fetch_match_data(match_id: str) -> dict:
  """
Fetch data for a specific match using its ID, which may be given with or without
the API prefix, i.e., 'https://api.chess.com/pub/match/1530241' or just '1530241'.

Returns:
    A `dict` containing match data, with keys: '@id': (with API prefix), 'url':...,
      'name':..., 'status': "finished", 'start_time', 'end_time': (unix timestamp),
      'settings': {'rules': "chess", 'time_class': "daily", 'time_control': "1/259200"},
      'boards': (number),  'teams': {'team1': TEAM, 'team2': TEAM}, ...
    TEAM = { "@id": "{API}/club/martinique", "name": "Martinique", "url": CHESSCOM/club/martinique,
      "score": 5, "result": "lose", "players": [PLAYER, ... ], "fair_play_removals": [username,...]}
    PLAYER = { "username": "durvalo", "stats": "{API}/player/durvalo/stats", "status": "basic",
          "played_as_white": "checkmated", "played_as_black": "win", "board": "{API}/match/1713457/5"}
  """
  global all_full_matches_data
  if '/'in match_id: match_id = match_id.split('/')[-1]
  if not(match_data := all_full_matches_data.get(match_id)):
      match_data = fetch_data("match/" + match_id)
      all_full_matches_data[match_id] = match_data
  return match_data

