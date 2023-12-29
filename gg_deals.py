import csv
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# Return the first URL that ends with '.jpg'
def extract_image_url(game_container):
    picture_tag = game_container.find('picture', class_='game-picture')
    if picture_tag:
        source_tag = picture_tag.find('source', {'srcset': True})
        if source_tag:
            srcset = source_tag['srcset'].split(',')
            for img_url in srcset:
                img_url = img_url.strip().split(' ')[0]
                if img_url.endswith('.jpg'):
                    return img_url
    return None

def main():
    load_dotenv()

    # Change the working directory specified by the .env file
    file_directory = os.getenv("FILE_DIRECTORY")
    os.chdir(file_directory)

    # Fetch the webpage content
    base_url = requests.get('https://gg.deals/deals/?maxPrice=0&minRating=3')
    soup = BeautifulSoup(base_url.content, 'html.parser')

    games_info = []
    seen_games = set()
    existing_rows = []
    max_game_id = 0

    # Read the last 5 rows of the existing CSV file, determine highest existing game_id
    try:
        with open('free_games.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            existing_rows = list(reader)[-5:]
            if existing_rows:
                max_game_id = max(int(row['game_id']) for row in existing_rows if 'game_id' in row and row['game_id'].isdigit())

    except FileNotFoundError:
        pass

    # Create set of existing game titles to avoid duplicates
    existing_titles = {row['game'] for row in existing_rows}

    game_containers = soup.find_all('div', {'class': 'd-flex flex-wrap relative list-items shadow-box-small-lighter'})

    # Iterate through each game container
    for game in game_containers:
        game_title_tag = game.find('a', class_='game-info-title title')
        launcher_tag = game.find('svg', class_=lambda x: x and 'svg-icon-drm-' in x)
        end_date_tag = game.find('time', class_='timesince')

        # Extract information if all tags are found
        if game_title_tag and launcher_tag and end_date_tag:
            game_title = game_title_tag.text.strip()

            launcher_class = launcher_tag.get('class', [])
            launcher_name = 'Unknown'
            for class_name in launcher_class:
                if 'svg-icon-drm-' in class_name:
                    launcher_name = class_name.split('-')[-1]
                    break
            
            # Convert end_date to ISO format
            end_date_raw = end_date_tag.get('datetime', '')
            end_date = end_date_raw.replace('T', ' ').split('+')[0]

            # Extract image URL
            image_url = extract_image_url(game)

            start_date = datetime.now().replace(microsecond=0, second=0, minute=0)

            # Add NEW game information to the list
            if game_title not in existing_titles:
                max_game_id += 1 
                seen_games.add(game_title)
                existing_titles.add(game_title)
                games_info.append(
                    {
                        'game_id': max_game_id,
                        'game': game_title,
                        'launcher': launcher_name.capitalize(),
                        'start_date': start_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'end_date': end_date,
                        'image_url': image_url
                    }
                )

    # Path to the CSV file
    csv_file = os.path.join(file_directory, 'free_games.csv')

    # Append and write the game information to CSV file
    with open(csv_file, mode='a+', newline='', encoding='utf-8') as file:
        fieldnames = ['game_id', 'game', 'launcher', 'start_date', 'end_date', 'image_url']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if file.tell() == 0:
            writer.writeheader()

        for game_info in games_info:
            writer.writerow(game_info)

    # Print the number of new rows added to the CSV file
    print(f"{len(games_info)} rows have been appended to {csv_file}")

if __name__ == "__main__":
    main()