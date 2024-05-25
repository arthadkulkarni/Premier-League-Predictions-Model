#import required libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import io

# html to bring data
standings_url = "https://fbref.com/en/comps/9/Premier-League-Stats"
# stores all teams
all_teams = []

data = requests.get(standings_url)
soup = BeautifulSoup(data.text, 'lxml')
standings_table = soup.select_one('table.stats_table')  # only need first index

links = standings_table.find_all('a')  # indentify links for all teams
links = [l.get("href") for l in links]
links = [l for l in links if '/squads/' in l]  # parsing through all links

team_urls = [f"https://fbref.com{l}" for l in links]  # formatting links

for team_url in team_urls:
    team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")  # find names of team
    data = requests.get(team_url)

    soup = BeautifulSoup(data.text, 'lxml')
    statistics_table = soup.find('table', class_="stats_table")  # find table

    html_content = io.StringIO(str(statistics_table))
    team_data = pd.read_html(html_content)[0]  # read table
    if isinstance(team_data.columns, pd.MultiIndex):
        team_data.columns = team_data.columns.droplevel(0)  # format stats
    team_data["Team"] = team_name
    all_teams.append(team_data)  # append data
    time.sleep(5)

match_df = pd.concat(all_teams)  # concat all stats
match_df.to_csv("stats.csv")  # import to csv
