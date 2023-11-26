import csv
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

file_directory = os.getenv("FILE_DIRECTORY")
os.chdir(file_directory)

base_url = requests.get('https://gg.deals/')
soup = BeautifulSoup(base_url.content, 'html.parser')

games_info = []
seen_games = set()

existing_rows = []

try:
    with open('free_games.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        existing_rows = list(reader)[-5:]  # Get the last 5 rows

except FileNotFoundError:
    pass

existing_titles = {row['Game'] for row in existing_rows}  # Set of game titles

max_existing_id = max(int(row['ID']) for row in existing_rows) if existing_rows else 0

game_containers = soup.find_all('div', {'class': 'mainpage-preset-item'})

for game in game_containers:
    launcher = game.find('div', {'class': 'tag-shop ellipsis tag'})
    game_title = game.find('a', {'data-title-auto-hide': True})
    price = game.find('span', {'class': 'price-inner numeric'})

    if launcher and game_title and price:
        launcher_name = launcher.find('span', {'class': 'value'}).text.strip()
        game_title = game_title['data-title-auto-hide'].strip()
        price_value = price.text.strip()

        game_key = (launcher_name, game_title, price_value)
        
        if (
            game_key not in seen_games
            and price_value.lower() == 'free'
            and game_title not in existing_titles
        ):
            seen_games.add(game_key)
            existing_titles.add(game_title)
            max_existing_id += 1
            games_info.append(
                {
                    'ID': max_existing_id,
                    'Launcher': launcher_name,
                    'Game': game_title,
                    'Date': datetime.now().strftime('%Y-%m-%d')
                }
            )

csv_file = f'{file_directory}free_games.csv'

with open(csv_file, mode='a+', newline='', encoding='utf-8') as file:
    fieldnames = ['ID', 'Date', 'Launcher', 'Game']
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    if file.tell() == 0:
        writer.writeheader()

    for game_info in games_info:
        writer.writerow(game_info)

print(f"{len(games_info)} rows with unique IDs have been appended to {csv_file}")
