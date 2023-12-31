# websc_free_games

The goal of this project is to receive notifications when a paid game becomes free. 
It also generates structured data about name of game, launcher, and the start/end dates of the free game period.
To ensure that you won't miss out on free deals, it need to be run daily. Set up a daily execution schedule using a server or any automotion method.

## Files

- `gg_deals.py`: main file, set up a schedule to automatically update games
- `gg_deals_widget.py`: "widget" for desktop (should be run after main file has been run and a CSV file was created)
- `requirements.txt`: required libraries
- `.env`: directory for CSV file

## How to use

1. Follow installation guide

2. Setup `gg_deals.py` through a scheduler such as crontab

3. After `free_games.csv` file has been created run `gg_deals_widget.py`

## Installation

1. Clone this repository:

```
git clone https://github.com/Jarosz96/websc_free_games.git
```

2. Navigate to the project directory:

```
cd websc_free_games
```

3. Install the required packages:

```
pip install -r requirements.txt
```

4. Modify the `.env` file to specify the directory containing the images you want to rename. Save and exit.

5. Run the code:

```
python gg_deals.py
```

## Future Plans

- Recieve notification on different devices when new line is created
- Create phone app with widget

## Known Issues

- Not taking timezones into consideration (widget 'Time Left' and CSV file)