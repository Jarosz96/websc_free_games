import tkinter as tk
from datetime import datetime
from PIL import Image, ImageTk
import requests
import csv
import os
from dotenv import load_dotenv
from io import BytesIO
from plyer import notification

# Track notification status and previously seen games
notifications_enabled = False
seen_games = set()

# Function to send notifications
def send_notification(title, message):
    if notifications_enabled:
        notification.notify(
            title=title,
            message=message,
            app_name="Game Tracker",
            timeout=30
        )

# Process image from URL
def fetch_image(image_url):
    try:
        response = requests.get(image_url)
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        img.thumbnail((100, 100), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error fetching image from {image_url}: {e}")
        return None

# Read CSV file and filter out games based on end_date
def read_and_filter_games(csv_file):
    now = datetime.now()
    games = []
    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            game = row['game']
            end_date = datetime.fromisoformat(row['end_date'])
            if end_date > now:
                time_left = end_date - now
                days, seconds = time_left.days, time_left.seconds
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                image_url = row['image_url']
                games.append((game, days, hours, minutes, image_url))
                if game not in seen_games:
                    send_notification("NEW GAME", f"{game} is now available!")
                    seen_games.add(game)
    return games

# Toggle notifications
def toggle_notifications():
    global notifications_enabled
    notifications_enabled = not notifications_enabled
    if notifications_enabled:
        notification_status.set("🔔 ON  ")
    else:
        notification_status.set("🔕 OFF")

# Update widget with game data
def update_widget(root, csv_file, widgets):
    games = read_and_filter_games(csv_file)
    # Clear previous widgets
    for widget in widgets:
        widget.destroy()
    widgets.clear()

    # Create/update widgets rows
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

    # Check for approaching deadlines and send notifications
    for game, days, hours, minutes, _ in games:
        if days == 0 and hours in [1, 2, 3] and minutes == 0:
            send_notification("Don't Miss Out: Free Gaming Ending", f"{game} ends in {hours} hours!")

    # Schedule next update
    root.after(60000, update_widget, root, csv_file, widgets)

# Create widget, configure column, create headers
def create_widget(csv_file):
    root = tk.Tk()
    root.title("Free Games")

    root.grid_columnconfigure(0, minsize=120)
    root.grid_columnconfigure(1, minsize=200)
    root.grid_columnconfigure(2, minsize=200)

    tk.Label(root, text="Image", font='Helvetica 10 bold').grid(row=0, column=0)
    tk.Label(root, text="Game", font='Helvetica 10 bold').grid(row=0, column=1)
    tk.Label(root, text="Time Left", font='Helvetica 10 bold').grid(row=0, column=2)

    # Add a toggle button for notifications
    global notification_status
    notification_status = tk.StringVar(value="🔕 OFF")
    notification_toggle = tk.Button(root, textvariable=notification_status, command=toggle_notifications, font='Helvetica 11 bold')
    notification_toggle.grid(row=0, column=3)

    # Store widgets to update them later
    widgets = []
    update_widget(root, csv_file, widgets)
    root.mainloop()

def main():
    load_dotenv()
    file_directory = os.getenv("FILE_DIRECTORY")

    csv_file = os.path.join(file_directory, 'free_games.csv')
    create_widget(csv_file)

if __name__ == "__main__":
    main()
