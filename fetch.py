import argparse
import json
import matplotlib.pyplot as plt
import requests

class Game:
    def __init__(self, id, name=str(), play_time=0):
        self.id=id
        self.name=name
        self.play_time=play_time
    
    def __repr__(self):
        return f"""* App id: {self.id}
* Name: {self.name}
* Total playtime (seconds): {self.play_time}
        """

def fetch_year_in_review(steam_id: str, year: int):
    # https://api.steampowered.com/ISaleFeatureService/GetUserYearInReview/v1/?key={STEAM_KEY}&steamid={STEAM_ID}&year={YEAR}
    params={
        'key': api_key,
        'steamid': steam_id,
        'year': year
    }
    response=requests.get(
        url='https://api.steampowered.com/ISaleFeatureService/GetUserYearInReview/v1/',
        params=params
    )
    return json.loads(response.content)

def fetch_app_names(app_ids: list[int]):
    # https://api.steampowered.com/ICommunityService/GetApps/v1/?key={STEAM_KEY}&appids[0]={APP_ID}
    params={
        'key': api_key
    }
    for index,app_id in enumerate(app_ids):
        params[f'appids[{index}]'] = app_id
    response=requests.get(
        url='https://api.steampowered.com/ICommunityService/GetApps/v1/',
        params=params
    )
    data=json.loads(response.content)
    app_list=data['response']['apps']
    return { app['appid']:app['name'] for app in app_list }

def plot(game_data: list[Game], total_playtime: int, year):
    names = [game.name for game in game_data]
    names.insert(0, 'Total')
    playtime = [game.play_time / 3600 for game in game_data]
    playtime.insert(0, total_playtime / 3600)

    bars = plt.barh(names, playtime)

    for bar in bars:
        width = bar.get_width()
        plt.text(
            width,
            bar.get_y() + bar.get_height() / 2,
            f'{width:.2f}',
            va='center'
        )

    plt.title(f'Playtime by games ({year})')
    plt.xlabel('Playtime (hours)')
    plt.ylabel('Games')
    plt.tight_layout()
    plt.show()

def get_args():
    # Create the parser
    parser = argparse.ArgumentParser()

    # Add required arguments
    parser.add_argument('--api-key', required=True, help="steam api key, can be found here: https://steamcommunity.com/dev/apikey")
    parser.add_argument('--steam-id', required=True, help="user's steam id")
    parser.add_argument('--year', help="steam review's year e.g 2024")

    # Parse the arguments
    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args=get_args()
    
    api_key=args.api_key
    year=args.year or 2024
    year_in_review_response=fetch_year_in_review(args.steam_id, year)
    if not year_in_review_response['response']:
        print(f'Steam review not found for {args.steam_id} in {year}')
        exit(-1)
    playtime_stats=year_in_review_response['response']['stats']['playtime_stats']
    total_playtime=playtime_stats['total_stats']['total_playtime_seconds']
    
    game_data=[]
    for game in playtime_stats['games']:
        game_data.append(
            Game(
                id=game['appid'],
                play_time=game['stats']['total_playtime_seconds']
            )
        )

    game_names=fetch_app_names([game.id for game in game_data])
    for game in game_data:
        game.name=game_names[game.id]
    
    plot(game_data, total_playtime, year)