"""  scraping.py
  (c) Jan. 2026 by MFH

  Part of "Script pour gestion CFE/CFT/LFR"

In this file we put data and functions for getting lists of links / math-id's etc 
from chess.com forum posts.

We use several types of forum pages:

A) "season" pages : they list the competitions of a given season.

B) "competition" pages : they contain the IDs of the matches of a competition
    They might be grouped by rounds and/or groups ("poules").

C) "annuaire" pages: they list the clubs that might participate

In particular:
- a page like https://www.chess.com/fr/announcements/view/cfe-cft-lfr-saison-2026
  lists all "championships" of a season, which consists of several divisions and/or rounds:
  (CFE | CFT | LFR) 2026 (D1 - D3, U1400, U1000)
  On such "season" pages we find links to the individual "division" pages, like:
  (a) https://www.chess.com/fr/clubs/forum/view/cfe2026-d1
  (b) https://www.chess.com/fr/announcements/view/cft2026-r1-4eme-edition-de-la-cft

- on (a), the championship is subdivided in Rounds and Groups, here 2 groups (A & B) of 4 teams
  which play against each other (of the same group) in 3 rounds.
  We want a results table by group, and a full / global one.
- on (b) we have no groups but 5 "rounds" which are 1/16th, 1/8th, 1/4, semi- and finals.
- on (c) ...

- On all of these pages, we have lines of the form
  Team1 - Team2 : Result (href = "https://www.chess.com/club/matches/team-nantes-1/1803600")

  The function "get_match_ids_from_forum(url)` extracts all these "...club/matches/..." links, 
  more precisely just the trailing component, the "match-id".

  We will store them in a session variable 
  st.session_state.matches = { season: { competition: [match_id's] } }
  
"""
import requests
import re

HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_matches(url: str, 
                pattern: str = r"matches/(?:[\w-]+/)?(\d+)"
               ):
    """
    Fetches a chess.com forum page and extracts all Match IDs found in links.
    The default pattern targets links of the form: 
    "https://www.chess.com/club/matches/{club-slug}/{id}", where "{club-slug}/" may be missing,
    and extracts only of the (numeric) {id}s.
    # The default regex ignores the domain prefix (chess.com/fr/ or chess.com/)
    # It matches 'matches/', optionally followed by 'any-slug/' followed by a number.
    # The (\d+) captures the numeric ID at the end.
    The function will return the list of all these (numeric) {id}s (or something else for other patterns).
    """    
    # 1. Fetch the page
    # We use a User-Agent to avoid being blocked by basic anti-bot filters
    try:
        response = requests.get(url, headers = HEADERS)
        response.raise_for_status() # Raise error if page doesn't load (404, 500)
        html_content = response.text
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching forum page: {e}")
        return ()

    # 2. Extract IDs using Regex
    
    # Find all matches in the HTML text
    # 3. Clean and Deduplicate
    # remove duplicates but keep the order
    return list(dict.fromkeys(re.findall(pattern, html_content)))

# --- Quick Test Block ---
if __name__ == "__main__":
    url = "https://www.chess.com/fr/clubs/forum/view/cfe2025-division-1"
    ids = get_match_ids_from_forum(url)
    print(f"Found {len(ids)} unique matches:")
    print(ids)

# 
database = {
  "CFE/CFT/LFR - Saison 2026": {
    'url': "https://www.chess.com/fr/announcements/view/cfe-cft-lfr-saison-2026",
    'comment': """lists the pages where information specific to a given "championships"/divisions can be found""",
    'scrape': { 'start': '<div class="post-view-content">', # or: "annuaire"
                'pattern': 'https://www.chess.com/(?:fr/)?clubs/forum/view/(lfr|cfe|cft)2026[^"]+',
                'end': '-----', # or: '<div\w+ id="social-share"'
              },
    'annuaire': "https://www.chess.com/fr/announcements/view/annuaire-des-equipes-locales",
    'competitions': {
        "Championnat de France par Equipes (CFE) 1ère division": 
          'https://www.chess.com/fr/clubs/forum/view/cfe2026-d1',
        "Championnat de France par Equipes (CFE) 2ème division": 
          'https://www.chess.com/fr/clubs/forum/view/cfe2026-d2',
        "Championnat de France par Equipes (CFE) 3ème division": 
          'https://www.chess.com/fr/clubs/forum/view/cfe2026-d3',
             
        "Coupe de France des Territoires (CFT)":
             "https://www.chess.com/fr/announcements/view/cft2026-r1-4eme-edition-de-la-cft",
        "Coupe de France des Territoires (CFT)":
             "https://www.chess.com/fr/announcements/view/cft2026-r2",
             
        "Ligue Française des Régions (LFR) 1ère division": 
            "https://www.chess.com/fr/clubs/forum/view/lfr2026-l1",
        
        "Ligue Française des Régions (LFR) 2ème division": 
            "https://www.chess.com/fr/clubs/forum/view/lfr2026-l2",
        "Ligue Française des Régions (LFR) 3ème division": 
             "https://www.chess.com/fr/clubs/forum/view/lfr2026-l3",
        "Ligue Française des Régions (LFR) en 960" : 
             "https://www.chess.com/fr/clubs/forum/view/lfr2026-960",
    
        "Championnat de France par Equipes en moins de 1400 (CFE)": 
             "https://www.chess.com/fr/clubs/forum/view/cfe2026-u1400",
        "Ligue Française des Régions en moins de 1400 (LFR)": 
             "https://www.chess.com/fr/clubs/forum/view/lfr2026-u1400",
        "Ligue Française des Régions en moins de 1000 (LFR)":
             "https://www.chess.com/fr/clubs/forum/view/lfr2026-u1000",
        }, # end links
  }, # end saison 2026
  "CFE - saison 2025": { # CFE - Démarrage de la saison 2025 - Ronde 1
     'url': "https://www.chess.com/fr/announcements/view/cfe2-demarrage-de-la-saison-2025-ronde-1",
     'comment': """Liste des divisions, et aussi des rencontres de Ronde 1.\n"""
       """Il y a trois divisions, où chaque division est composée de 8 équipes.
       Démarrage au 15/01/2025 pour toutes les parties de cette ronde.
       Cut_off des rencontres le 15 juin 2025.""",
     'competitions': {
        "Division 1": "https://www.chess.com/fr/clubs/forum/view/cfe2025-division-1",
        "Division 2": "https://www.chess.com/fr/clubs/forum/view/cfe2025-division-2",
        "Division 3": "https://www.chess.com/fr/clubs/forum/view/cfe-division-3",
        "CFE 2025 U1400": "https://www.chess.com/fr/clubs/forum/view/cfe2025-u1400",
     }, # le dernier lien vient de la page
    #  "https://www.chess.com/fr/announcements/view/demarrage-du-cfe2025-en-moins-de-1400",
    'comment-U1400': """Ce championnat sera composé de 8 ou 9 équipes au sein d'une poule unique: 
Démarrage au 20/01/2025 pour toutes les parties de cette ronde ("1ère journée").
Poule unique avec 3 joueurs minimum par rencontre. J1: démarrage le 20 janvier 2025.
Cut-Off de la saison au 31/12/2025.
Titre de la rencontre : CFE 2025 U1400 R1 - équipe 1 vs équipe 2
Bordeaux - Toulouse ; Grenoble - Strasbourg ; Isbergues - Rennes ; Montpellier - Paris neuf trois
""",
      },# end CFE 2025
  "Saison 2024": {
    'competitions': {
      "CFE 2024": "https://www.chess.com/fr/clubs/forum/view/cfe-2024",
    },
    'comment-cfe': """Contient la liste des clubs et les rencontres (avec url .../match-id) pour les 11 rondes.
Dans les posts/réponses ultérieurs, certains match_id se répètent.
Lien vers le classement : https://www.chess.com/fr/announcements/view/cfe-classement-2024""",
  } # end saison 2024  
} # end database


""" Each of the above pages has more information. 
From 2026 the individual pages have a quite regular structure:
For example, https://www.chess.com/fr/clubs/forum/view/cfe2026-d1 :
  CFE2026 D1
  (...general information...)
-----
  [List of participating clubs: note how ":" is sometimes missing]
Bordeaux https://www.chess.com/club/bordeaux 
Boulogne https://www.chess.com/club/cercle-boulonnais-des-echecs
Dieppe: https://www.chess.com/club/lechiquier-dieppois
Lyon: https://www.chess.com/club/lyon-echecs
Metz https://www.chess.com/club/metz-the-chess-tt-team
Rennes  https://www.chess.com/club/rennes
Tahiti: https://www.chess.com/club/federation-tahitienne-des-echecs
Toulouse https://www.chess.com/club/team-toulouse-equipa-tolosa

Titre de la rencontre - CFE2026 D1: equipe1 vs equipe2

  [List of rounds with groups & matches]
Ronde 1: démarrage le 25/11/2025 (lancement des défis le 11/11/2025)
CFE2026 D1 Groupe A
Toulouse - Dieppe Résultat href="https://www.chess.com/club/matches/1869975" 
Rennes - Tahiti Résultat href="https://www.chess.com/club/matches/federation-tahitienne-des-echecs/1870061"

CFE2026 D1 Groupe B
Boulogne - Bordeaux Résultat
Metz - Lyon Résultat

Ronde 2: démarrage le 10/12/2025
...etc...
"""
