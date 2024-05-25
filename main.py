from io import StringIO
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# URL for the Premier League stats
standings_url = "https://fbref.com/en/comps/9/Premier-League-Stats"

# Fetch the page
data = requests.get(standings_url)

# Check if the request was successful
if data.status_code == 200:
    print("Page fetched successfully")
else:
    print(f"Failed to fetch the page. Status code: {data.status_code}")

# Print a small part of the HTML to debug
print(data.text[:500])  # Print the first 500 characters of the HTML

# Parse the page using BeautifulSoup with the lxml parser
soup = BeautifulSoup(data.text, 'lxml')

# Find all tables
tables = soup.select('table')
print(f"Found {len(tables)} tables on the page")

# Find the standings table
standings_table = soup.select('table.stats_table')
if not standings_table:
    print("Standings table not found")
else:
    standings_table = standings_table[0]
    print("Standings table found")

# Continue with the rest of your script if the standings table is found
if standings_table:
    links = standings_table.find_all('a')
    links = [l.get("href") for l in links]
    links = [l for l in links if '/squads/' in l]

    team_urls = [f"https://fbref.com{l}" for l in links]
    team_url = team_urls[0]
    data = requests.get(team_url)
    html_content = StringIO(data.text)
    matches = pd.read_html(html_content, match="Scores & Fixtures")[0]

    soup = BeautifulSoup(data.text, 'lxml')
    links = soup.find_all('a')
    links = [l.get("href") for l in links]
    links = [l for l in links if l and 'all_comps/shooting/' in l]
    data = requests.get(f"https://fbref.com{links[0]}")
    html_content = StringIO(data.text)
    shooting = pd.read_html(html_content, match="Shooting")[0]
    shooting.columns = shooting.columns.droplevel(0)

    team_data = matches.merge(shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date")

    years = list(range(2024, 2020, -1))
    all_matches = []
    standings_url = "https://fbref.com/en/comps/9/Premier-League-Stats"

    for year in years:
        data = requests.get(standings_url)
        soup = BeautifulSoup(data.text, 'lxml')
        standings_table = soup.select('table.stats_table')[0]

        links = [l.get("href") for l in standings_table.find_all('a')]
        links = [l for l in links if '/squads/' in l]
        team_urls = [f"https://fbref.com{l}" for l in links]

        previous_season = soup.select("a.prev")[0].get("href")
        standings_url = f"https://fbref.com{previous_season}"

        for team_url in team_urls:
            team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")

            data = requests.get(team_url)
            html_content = StringIO(data.text)
            matches = pd.read_html(html_content, match="Scores & Fixtures")[0]

            soup = BeautifulSoup(data.text, 'lxml')
            links = [l.get("href") for l in soup.find_all('a')]
            links = [l for l in links if l and 'all_comps/shooting/' in l]
            data = requests.get(f"https://fbref.com{links[0]}")
            html_content = StringIO(data.text)
            shooting = pd.read_html(html_content, match="Shooting")[0]
            shooting.columns = shooting.columns.droplevel(0)

            try:
                team_data = matches.merge(shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date")
            except ValueError:
                continue

            team_data = team_data[team_data["Comp"] == "Premier League"]
            team_data["Season"] = year
            team_data["Team"] = team_name
            all_matches.append(team_data)
            time.sleep(1)

    match_df = pd.concat(all_matches, ignore_index=True)
    match_df.columns = [c.lower() for c in match_df.columns]
