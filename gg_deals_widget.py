import tkinter as tk
from datetime import datetime
from PIL import Image, ImageTk
import requests
import csv
import os
from dotenv import load_dotenv
from io import BytesIO

# Process image from URL
def fetch_image(image_url):
    try:
        response = requests.get(image_url)
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        img.thumbnail((100, 100), Image.LANCZOS)    # Resize image
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error fetching image from {image_url}: {e}")
        return None

# Read game data from a CSV file and filter out games based on end_date
def read_and_filter_games(csv_file):
    now = datetime.now()
    games = []
    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            end_date = datetime.fromisoformat(row['end_date'])
            if end_date > now:
                time_left = end_date - now
                days, seconds = time_left.days, time_left.seconds
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                image_url = row['image_url']
                games.append((row['game'], days, hours, minutes, image_url))
    return games

# Update widget display with the game data
def update_widget(root, csv_file, widgets):
    games = read_and_filter_games(csv_file)
    # Clear the previous widgets
    for widget in widgets:
        widget.destroy()
    widgets.clear()

    # Create new widgets for image, game, time left
    for i, (game, days, hours, minutes, image_url) in enumerate(games, start=1):
        if image_url:
            img = fetch_image(image_url)
            if img:
                img_label = tk.Label(root, image=img)
                img_label.image = img
                img_label.grid(row=i, column=0)
                widgets.append(img_label)

        game_label = tk.Label(root, text=f"{game}", anchor="w")
        game_label.grid(row=i, column=1, sticky="w")
        widgets.append(game_label)

        time_label = tk.Label(root, text=f"{days} days, {hours} hours, and {minutes} minutes", anchor="w")
        time_label.grid(row=i, column=2, sticky="w")
        widgets.append(time_label)

    # Schedule the next update
    root.after(60000, update_widget, root, csv_file, widgets)

# Create the main widget window, configure column size, create headers
def create_widget(csv_file):
    root = tk.Tk()
    root.title("Free Games")

    root.grid_columnconfigure(0, minsize=120)
    root.grid_columnconfigure(1, minsize=200)
    root.grid_columnconfigure(2, minsize=200)

    tk.Label(root, text="Image", font='Helvetica 10 bold').grid(row=0, column=0)
    tk.Label(root, text="Game", font='Helvetica 10 bold').grid(row=0, column=1)
    tk.Label(root, text="Time Left", font='Helvetica 10 bold').grid(row=0, column=2)

    # Store the widgets to update them later
    widgets = []
    update_widget(root, csv_file, widgets)
    root.mainloop()

# Main function to load environment variables and initiate widget creation
def main():
    load_dotenv()
    file_directory = os.getenv("FILE_DIRECTORY")

    csv_file = os.path.join(file_directory, 'free_games.csv')
    create_widget(csv_file)

if __name__ == "__main__":
    main()