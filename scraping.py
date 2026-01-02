"""  scraping.py
  (c) Jan. 2026 by MFH

  Part of "Script pour gestion CFE/CFT/LFR"

In this file we put data and functions for getting lists of links / math-id's etc 
from chess.com forum posts.
"""
import requests
import re

def get_match_ids_from_forum(forum_url):
    """
    Fetches a Chess.com forum page and extracts all Match IDs found in links.
    Target link format: https://www.chess.com/club/matches/{club-slug}/{id}
    """
    
    # 1. Fetch the page
    # We use a User-Agent to avoid being blocked by basic anti-bot filters
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(forum_url, headers=headers)
        response.raise_for_status() # Raise error if page doesn't load (404, 500)
        html_content = response.text
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching forum page: {e}")
        return ()

    # 2. Extract IDs using Regex
    # We look for the pattern: .../matches/some-club-name/123456
    # The (\d+) captures the numeric ID at the end.
    
    # This regex is flexible: 
    # It ignores the domain prefix (chess.com/fr/ or chess.com/)
    # It matches 'matches/' followed by 'any-slug/' followed by 'numbers'
    pattern = r"matches/(?:[\w-]+/)?(\d+)"
    
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
  2026: { 'name': "CFE/CFT/LFR - Saison 2026",
    'url': "https://www.chess.com/fr/announcements/view/cfe-cft-lfr-saison-2026",
    'comment': "lists the pages where information specific to a given competition can be found",
    'scrape': { 'start': '<div class="post-view-content">', # or: "annuaire"
                'pattern': 'https://www.chess.com/fr/clubs/forum/view/(lfr|cfe|cft)2026[^"]+',
                'end': '-----', # or: '<div\w+ id="social-share"'
              },
    'annuaire': "https://www.chess.com/fr/announcements/view/annuaire-des-equipes-locales",
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
  },# end saison 2026
} # end database
""" Each of the above pages has more information. 
From 2026 the individual pages have a quite regular structure:
For example, https://www.chess.com/fr/clubs/forum/view/cfe2026-d1 :
  CFE2026 D1
  (...general information...)
-----
  [List of participating clubs]
Bordeaux https://www.chess.com/club/bordeaux 
Boulogne https://www.chess.com/club/cercle-boulonnais-des-echecs
Dieppe: https://www.chess.com/club/lechiquier-dieppois
Lyon: https://www.chess.com/club/lyon-echecs
Metz https://www.chess.com/club/metz-the-chess-tt-team
Rennes  https://www.chess.com/club/rennes
Tahiti: https://www.chess.com/club/federation-tahitienne-des-echecs
Toulouse https://www.chess.com/club/team-toulouse-equipa-tolosa

Titre de la rencontre - CFE2026 D1: equipe1 vs equipe2

[list of rounds with groups & matches]
Ronde 1: démarrage le 25/11/2025 (lancement des défis le 11/11/2025)
CFE2026 D1 Groupe A
Toulouse - Dieppe Résultat href="https://www.chess.com/club/matches/1869975" 
Rennes - Tahiti Résultat href="https://www.chess.com/club/matches/federation-tahitienne-des-echecs/1870061"

CFE2026 D1 Groupe B
Boulogne - Bordeaux Résultat
Metz - Lyon Résultat

Ronde 2: démarrage le 10/12/2025
...etc...
# The following function will extract the links from the above page 
"""
