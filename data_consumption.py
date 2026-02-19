import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
HEADERS = {
    'Ocp-Apim-Subscription-Key': API_KEY
}


def fetch_tournament_data(tournament_id):
    url = f"https://api.sportsdata.io/golf/v2/json/PlayerTournamentRoundScoresFinal/{tournament_id}?key={API_KEY}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        df.to_json(f'data/raw/tournament_{tournament_id}_round_scores.json', orient='records', indent=4)
        print(f"Data for tournament {tournament_id} saved successfully.")
    else:
        print(f"Failed to fetch data for tournament {tournament_id}. Status code: {response.status_code}")

def creating_master_dataframe(tournament_ids):
    master_df = pd.DataFrame()
    for tournament_id in tournament_ids:
        file_path = f'data/raw/tournament_{tournament_id}_round_scores.json'
        if os.path.exists(file_path):
            df = pd.read_json(file_path)
            master_df = pd.concat([master_df, df], ignore_index=True)
        else:
            print(f"File for tournament {tournament_id} not found.")
    master_df = master_df.explode("PlayerRoundScore")
    master_df = pd.concat([master_df.drop(['PlayerRoundScore'], axis=1), master_df['PlayerRoundScore'].apply(pd.Series)], axis=1)
    master_df["Day"] = pd.to_datetime(master_df["Day"])
    time_series = master_df.groupby("Day")["Score"].mean()
    time_series.index = pd.to_datetime(time_series.index)
    time_series = time_series.reset_index()
    time_series = time_series.drop(columns=["Day"], axis=1)

    time_series.to_csv('data/processed/average_scores_time_series_frequency.csv', index=True)
    print("Master dataframe created and saved successfully.")

if __name__ == "__main__":
    TOURNAMENT_IDS = [n for n in range(300, 350)]
    for tournament_id in TOURNAMENT_IDS:
        fetch_tournament_data(tournament_id)
    creating_master_dataframe(TOURNAMENT_IDS)