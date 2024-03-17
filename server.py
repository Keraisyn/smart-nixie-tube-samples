from flask import Flask
import os
import requests
import datetime
import dotenv

dotenv.load_dotenv()

RIOT_API_KEY = os.environ["RIOT_API_KEY"]
USERNAME = os.environ["USERNAME"]
TAGLINE = os.environ["TAGLINE"]

app = Flask(__name__)


@app.route('/api/leaguelastplayed')
def league_last_played():
    # Generate puuid
    res = requests.get(
        "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}"
        .format(USERNAME, TAGLINE),
        headers={"X-Riot-Token": RIOT_API_KEY})

    if res.status_code != 200:
        return "Error fetching user"

    player_id = res.json()["puuid"]

    # Check if currently playing
    res = requests.get(
        "https://na1.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{}"
        .format(player_id),
        headers={"X-Riot-Token": RIOT_API_KEY})

    if res.status_code == 200:
        return {"number": 0}
    elif res.status_code != 404:
        return "Error fetching match data"

    # Not currently playing, get last match
    res = requests.get(
        "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{}/ids?start=0&count=1"
        .format(player_id),
        headers={"X-Riot-Token": RIOT_API_KEY})

    if len(res.json()) < 1:
        return "No matches found"

    match_id = res.json()[0]

    res = requests.get(
        "https://americas.api.riotgames.com/lol/match/v5/matches/{}".format(
            match_id),
        headers={"X-Riot-Token": RIOT_API_KEY})

    if res.status_code != 200:
        return "Error fetching match data"

    end_timestamp = res.json()["info"]["gameEndTimestamp"]

    end_time = datetime.datetime.fromtimestamp(end_timestamp / 1000)

    time_passed = datetime.datetime.now() - end_time

    return {"number": time_passed.seconds / 60}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
