# Steam Review Sentiment

## Dataset
Tenatively we will gather data locally to be fed back into the model.

## Notes about [Steam API](https://steamcommunity.com/dev)
- 200 requests in five minutes or one request every 1.5 seconds.

- [List of games and IDs](http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key=STEAMKEY&format=json).
  - We need to ignore games with names "" since they don't have a page so won't have reviews. There are also lots of games with test in their name that are also not worth checking such as
    - "Pieterw test app76 ( 216938 )"
    - "test[n]" (there are several test games like that)

- [User reviews documentation](https://partner.steamgames.com/doc/store/getreviews)

## Project setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-folder>
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Launch Jupyter Notebook:
```bash
jupyter notebook
```

## Data Scraper Usage

The ```gameIDs.json``` has many games and their IDs. ```gatherSteamData.py``` takes the list of all games and from the index in ```next_ID.txt```. Each time it collects the reviews from the game it updates the next index to ```next_ID.txt```. This each time ```gatherSteamData.py``` it will append only new data to ```steamreviews.csv```.

```python gatherSteamData.py x``` gathers the next *x* game reviews. (make sure you are in ```.\Dataset```)
