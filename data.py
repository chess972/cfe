""" data.py - the data managing part of the CFE/CFT/LFR managing app
    (c) 2025-2026 by MFH

There are two parts:
    I. Functions to get data (club, match, player) from the chess.com API
        http://chess.com/news/view/published-data-api/
    II. Functions to get information from chess.com forum pages specific to given competitions
    
Provides:
- get_club_data(club_id or sub-endpoint, force_refresh=False): get general club data
- get_club_matches(club_id, force_refresh=False): get recent matches of a given club
- get_match
- get_player_data
- 

internal/"private" functions:
fetch_data(endpoint, version):
get_version(key, increment=False): get 'version' argument for key (= 'club_data', ...)
"""
import streamlit as st
import requests
from collections import defaultdict

API_URL = "https://api.chess.com/pub"
HEADERS = {'User-Agent': 'ChessCom-LFR-Project'}

@st.cache_data(ttl=3600) # Auto-refresh every hour

def fetch_data(endpoint: str, version: int = 0) -> dict:
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

#helper function
def get_version(key, increment = False):
    """Possible keys are: 'club', 'player', 'match'."""
    if 'refresh' not in st.session_state:
        st.session_state.refresh = defaultdict(int)
    if increment: st.session_state.refresh[key] += 1
    return st.session_state.refresh[key]

def get_club_data(club_id, force_refresh = False) -> dict:
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
    return fetch_data("club/" + club_id, 
                      get_version('club', increment = force_refresh))

'''
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
'''

def get_club_matches(club_id, force_refresh = False):
    """
Fetch, store and return the dict of daily and club matches for chess.com/club/{club_url_id}.

The result is a dict with three lists of matches, grouped by status:
{"finished": [...], "in_progress": [...], "registered": [...]}. Each match is a dict
MATCH = { '@id': (URL of team match API endpoint), 'name': (name of the match),
    'opponent': (URL of club profile API endpoint),
    'start_time': (unix timestamp), 'time_class': 'daily' (or ...?),
    (and only for finished matches:) 'result': "win" or "lose" or "draw" }

The result is stored in club_info[club_url_id]['matches']. If that dict
already exists and is nonempty, it is returned instead of fetching through the API.
    """
    return get_club_data(club_id + "/matches", force_refresh)


################# matches ################

"""All team matches-based URLs use the match "ID" to specify which match you want data for.
https://api.chess.com/pub/match/{ID}

The ID is the same as found in the URL for the team match web page on www.chess.com.
For example, the ID of "WORLD LEAGUE Round 5: Romania vs USA Southwest" is 12803.
"""

def get_match_data(match_id: str, force_refresh = False) -> dict:
  """
Fetch data for a specific match ("rencontre entre deux clubs") using its ID, 
which may be given with or without the API prefix, i.e., 
'https://api.chess.com/pub/match/1530241' or just '1530241'.

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
  if '/' in match_id: match_id = match_id.split('/')[-1] # get the trailing component = match number
  return fetch_data("match/" + match_id, get_version('match', force_refresh))


########### now PLAYER related data ##############

#@title `get_player_matches(player, status)`: renvoit une liste de *rencontres* pour `player`
# example: https://api.chess.com/pub/player/mf972/matches  =>  5 kB of data
# so if we have say 100 players it's only 500 K of data

STATUS = ('finished', 'in_progress', 'registered', '')

def get_player_matches(username, status = ('in_progress', 'registered'),
                       as_dict = False, # by default, return only list of match_id's
                       debug = 0) -> list:
    """For a given player, return the list of club match_id's he did/does/will participate in.

`status` can be a tuple/list/set/string with items among {'finished', 'in_progress', 'registered'},
possibly abbreviated or separated by comma and/or space, cf. helper function `normalize_status()`

The returned dict (formerly stored in `joueurs[username]`) will contain an entry for each of status, 
with a list of "match infos", of the form:
"in_progress": [ { "name": "CFE2025 Phases Finales R2 - Antilles Françaises vs Nantes",
                   "url": "https://www.chess.com/club/matches/1815536",
                   "@id": "https://api.chess.com/pub/match/1815536",
                   "club": "https://api.chess.com/pub/club/team-french-antilles",
                   "results": { # only if either game is already finished
                     "played_as_black": "resigned",
                     "played_as_white": "win"
                   },
                   "board": "https://api.chess.com/pub/match/1815536/1"
                }, ... ]

If `joueurs[username]` already exists and has these items (all s in status),
we assume those lists are complete and up to date.

Related global data:
  * `joueurs[compèt = pattern]` : { club_id : {recontres...}}
  * `matches[compèt] = { match_@id: {'name':..., 'start_time': 1752469383,
        '@id': match_@id='https://api.chess.com/pub/match/1803610',
        'result': 'lose'/'win', 'teams': {'la-tour-infernale', 'team-ajaccio'}}}`.
    """
    if not username: 
        raise ValueError("Username must be given!")
        
    if not all(x in STATUS for x in status):
        status = normalize_status(status)

    if not 'joueurs' in st.session_state:
        st.session_state.joueurs = {}
    if not 'joueurs' in globals():
        globals()['joueurs'] = st.session_state.joueurs                       
    if not username in joueurs:
        joueurs[username] = {}
    if not all(s in joueurs[username] for s in status):
        if debug: print(end = f"Fetching data for player '{username}'... ")
        try: player_matches = fetch_data(f'player/{username}/matches')
        except:
            st.warning(f"ERROR: can't get data for {player = }. Do they exist?)")
# TODO: WORK IN PROGRESS HERE
        if player_matches:
          if debug: print("success:", ' + '.join(f'{len(m)} {s}' for s,m
                                                 in player_matches.items()))
          if debug > 1: print(player_matches)
          joueurs[username] |= player_matches
        else: display(f"Couldn't find {username}'s matches :-( !")
    # we assume the lists are now complete.
    # make the simplified list of match id's
    return [ m if as_dict or not( ((id := m.get('@id')) or
              (id := m.get('url'))) and (id := id.split('/')[-1]) ) else id
        for s in status for m in joueurs[username][s] ]

# helper function:
def normalize_status(status: str|list|set|tuple) -> tuple:
    """
Normalize status: convert several possible abbreviations to the standard form,
which is a tuple or list of strings among ('finished', 'in_progress', 'registered').
These three terms can be abbreviated by any initial segment ('f', 'reg', ...) and also
'p' is allowed for "in progress" and 'u' = 'upcoming' for 'registered'.
However, "fi" is ambiguous: "f"(inished)" + "i(n_progress)" or just "fi(nished)"?
If it's the only argument, "fi" =  (finished, in_progress) ; 
if part of more (e.g. "fi reg") => finished (+ registered)
"""
    if isinstance(status, str):
       # we got a string. 2 possibilities: just initials, or
       # full words or initials separated by comma and/or spaces.
       if not status.isalpha(): # not only letters => some space or "," separators
          # first check whether we must split (even if single-letter abbreviations
          # are used, e.g. separated by commas and/or whitespace)
          separators = ''.join(c for c in status if not c.isalpha())
          status = [s for s in status.split(separators) if s]
       elif len(status) < len(STATUS): # single letter abbrevs, e.g. 'fi' = finished, in_progress
          status = tuple(status)
       else: status = (status,)
    if not all(s in STATUS for s in status): # e.g., if abbreviations are used
        old = set(status) # discard duplicates
        status = tuple(ns for s in old  # discard unknown
                  if (ns := next(ss for ss in standard if ss.startswith(s)))
                  or (ns := next(ss for ss in standard if s in ss))
                  or s.startswith('u') and (ns := 'registered')) # "upcoming"
        if len(status) < len(old): print(f"Warning: some in {old} were ignored.")
        elif len(status) > 3 : # there must be duplicates -- should not happen
            print(f"Warning: duplicates in {status = } -- should not happen! {old =}")
            status = tuple(s for s in set(status) if standard[:3])
    return status
