import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import logging

# Load configuration
with open('config.json') as config_file:
    config = json.load(config_file)

# Configure logging
logging.basicConfig(level=logging.INFO, filename='app.log', 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define headers for HTTP requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def fetch_webpage(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        logging.error(f"Error fetching the webpage: {e}")
        return None

def parse_html(content):
    return BeautifulSoup(content, 'html.parser')
    
def extract_game_data(soup, selectors):
    table = soup.select(selectors["table_section"])
    if not table:
        logging.error("No elements found with the selector: table_section")
        return []

    table = table[0]
    header = table.select(selectors["headline"])
    if not header:
        logging.error("No elements found with the selector: headline")
        return []

    logging.info('Parsing games from %s', header[0].text)

    data = []
    date = None
    game_id = 0
    
    for game in table.select('div.margin-date'):
        date_ = game.select(selectors["date"])
        if date_:
            date = date_[0].text

        for game_table in game.select(selectors["game_table"]):
            data_header = game_table.select(selectors["header"])
            if not data_header:
                logging.warning("Header missing in game table")
                continue

            time = data_header[0].text
            data_headers = [dh.text for dh in data_header[1:]]
            
            data_game = {
                'date': date,
                'time': time,
                'game': game_id,
            }
            game_id += 1

            teams = game_table.select(selectors["teams"])
            if len(teams) != 2:
                logging.warning("Expected 2 teams, got %d", len(teams))
                continue

            for team, flag in zip(teams, ('Away Team', 'Home Team')):
                data_game_ = data_game.copy()
                team_data = team.select('td')
                if len(team_data) - 1 != len(data_headers):
                    logging.warning("Mismatch between team data and headers")
                    continue
                
                team_el = team_data[0].select('a')[-1]
                data_game_['team'] = team_el['href'].split('/')[-2].upper()
                data_game_['flag'] = flag
                data_game_['ml'] = ''.join([td.text for td in team_data[1:]])
                
                data.append(data_game_)

    return data

def format_dataframe(data):
    df = pd.DataFrame(data)
    df.sort_values(by='game', inplace=True)
    return df

def output_to_csv(df, filename="lines.csv"):
    df_pivot = df.pivot(index='game', columns='flag', values=['team', 'ml']).reset_index(drop=True)
    df_pivot.columns = ['Away Team', 'Money Line Home', 'Home Team', 'Money Line Away']
    df_pivot.to_csv(filename, columns=['Away Team', 'Money Line Away', 'Home Team', 'Money Line Home'], index=False)
    logging.info('Data written to %s', filename)

def main():
    content = fetch_webpage(config['url'])
    if content:
        soup = parse_html(content)
        game_data = extract_game_data(soup, config['selectors'])
        df = format_dataframe(game_data)
        output_to_csv(df)

if __name__ == "__main__":
    main()