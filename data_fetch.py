import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
import time

# Function to scrape match data for a given team URL
def scrape_team_data(team_url, year):
    team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
    
    data = requests.get(team_url)
    soup = BeautifulSoup(data.text, features="lxml")
    matches = pd.read_html(data.text, match="Scores & Fixtures")[0]
    
    links = soup.find_all("a")
    links = [l.get("href") for l in links]
    links = [l for l in links if l and "all_comps/shooting/" in l]
    
    if not links:
        return None
    
    data = requests.get(f"https://fbref.com{links[0]}")
    shooting = pd.read_html(io.StringIO(data.text), match="Shooting")[0]
    shooting.columns = shooting.columns.droplevel()

    try:
        team_data = matches.merge(shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date")
    except ValueError:
        return None
    
    team_data = team_data[team_data["Comp"] == "Premier League"]
    team_data["Season"] = year
    team_data["Team"] = team_name
    
    return team_data

# Function to scrape data for all teams in a given season
def scrape_season_data(year):
    standing_url = f"https://fbref.com/en/comps/9/Premier-League-Stats/{year}-Stats"
    data = requests.get(standing_url)
    soup = BeautifulSoup(data.text, features="lxml")
    standing_table = soup.select("table.stats_table")[0]

    links = standing_table.find_all("a")
    links = [l.get("href") for l in links]
    links = [l for l in links if '/squads/' in l]
    team_urls = [f"https://fbref.com{l}" for l in links]

    all_matches = []
    
    for team_url in team_urls:
        team_data = scrape_team_data(team_url, year)
        if team_data is not None:
            all_matches.append(team_data)
    
    return all_matches

# Main script to scrape data for multiple seasons
def main():
    years = list(range(2022, 2020, -1))  # Adjust the range accordingly
    
    all_season_matches = []

    for year in years:
        season_matches = scrape_season_data(year)
        all_season_matches.extend(season_matches)

    match_df = pd.concat(all_season_matches)
    match_df.columns = [c.lower() for c in match_df.columns]
    match_df.to_csv("matches.csv")

if __name__ == "__main__":
    main()
