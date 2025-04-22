import requests
import csv
import os
import json
import time
import sys
from langdetect import detect


# ----------------------
# GET REVIEWS
# ----------------------

def get_reviews(appid, num_reviews=100):
    """
    Gets as many reviews from an gameID as allowed by the API.
    """
    url = f'https://store.steampowered.com/appreviews/{appid}'
    params = {
        'json': 1,
        'filter': 'recent',
        'language': 'english',
        # max value is 365
        'day_range': 365,
        'review_type': 'all',
        'purchase_type': 'all',
        # Max review is 100
        'num_per_page': num_reviews,
        'playtime_forever': True
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data.get('success') == 1:
            return data.get('reviews', [])
        else:
            print(f"Failed to fetch reviews for AppID {appid}")
            return []
    except Exception as e:
        print(f"Error fetching reviews for {appid}: {e}")
        return []


# ----------------------
# WRITE REVIEWS TO CSV
# ----------------------

def isEnglish(text):
    try:
        lang = detect(text)
        return lang == 'en'
    except Exception as e:
        return False

def process_review(review_message, print_log=True):
    # Many messages aren't in english. This would be hard for a model
    if not isEnglish(review_message):
        if print_log:
            print(f'- Not English:\n')
            print(review_message.strip())
        return None
    # Remove new lines
    review_message = review_message.replace('\n', ' ').replace('\r', ' ')
    return review_message

def write_reviews_to_csv(appid, gamename, reviews, print_log=True):
    """
    Logs the reviews to the csv
    """
    filename = f"steamreviews.csv"
    # Check if the file already exists
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header if the file is new
        if not file_exists:
            writer.writerow(['AppID', 'GameName', 'ReviewID', 'Author', 'Review', 'Recommended',
                             'VotesUp', 'VotesFunny', 'PlaytimeTotal', 'PlaytimeReview', 'PlaytimeTwoWeeks',
                             'NumberofReviews', 'PostedDate'])
        for review in reviews:
            # Process/validate review
            review_text = process_review(review.get('review'), print_log)
            if review_text:
                writer.writerow([
                    appid,
                    gamename,
                    review.get('recommendationid'),
                    review.get('author', {}).get('steamid'),
                    review_text,
                    review.get('voted_up'),
                    review.get('votes_up'),
                    review.get('votes_funny'),
                    review.get('author').get('playtime_forever'),
                    review.get('author').get('playtime_at_review'),
                    review.get('author').get('playtime_last_two_weeks'),
                    review.get('author').get('num_reviews'),
                    review.get('timestamp_created')
                ])
    if print_log:
        print(f"- {appid}, {gamename}: {len(reviews)} reviews")
    return


# ----------------------
# GET APPIDS
# ----------------------

def get_game_ids(filename='gameIDs.json'):
    """
    This gets a list, of dictionaries

    [
        {'appid': ID, 'name': 'NAME'}, ...
    ]
    """
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data['applist']['apps']


def get_index():
    # Gets the next index to use from the file
    with open('next_ID.txt', 'r', encoding='utf-8') as file:
        index = int(file.read().strip())
    return index

def write_index(index):
    # Writes the next index to use to the file
    with open('next_ID.txt', 'w', encoding='utf-8') as file:
        file.write(str(index))
    return

# ----------------------
# TRACK REVIEWS
# ----------------------

def valid_name(name):
    """
    More can be done here. This is lazily just empty names and based 'test#' style names.
    There are some more test names with slightly more complex test names but I haven't looked to closely to see other patterns.
    This shouldn't impact performance too much as they just won't have reviews but does waste a query.
    """
    name = name.strip()
    return name != "" or (name[:4] == 'test' and len(name) == 5)

def track_reviews(game_info, print_log=True):
    """
    From the dictionaries returned by get_game_ids, this logs the reviews.
    """
    appid = game_info['appid']
    name = game_info['name']
    if valid_name(name):
        reviews = get_reviews(appid)
        write_reviews_to_csv(appid, name, reviews, print_log=print_log)
    elif print_log:
        print(f'- {appid}: "{name}" invalid name')
    return

def log_game(gameIDs=None):
    """
    This is the main funtion that gets the next unlogged gameID and logs it.
    It also lets you pass all the gameIDs along between calls if you are doing in batches.
    """
    if gameIDs is None:
        gameIDs = get_game_ids()
    
    index = get_index()
    
    if index < len(gameIDs):
        appid = gameIDs[index]
        track_reviews(appid)

    write_index(index + 1)
    return gameIDs

# ----------------------
# MAIN
# ----------------------

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python gatherSteamData.py <number_of_iterations>")
        sys.exit(1)

    try:
        x = int(sys.argv[1])
    except ValueError:
        print("Error: <number_of_iterations> must be an integer.")
        sys.exit(1)

    ids = None
    trial_len = len(str(x))
    for i in range(x):
        start_time = time.time()
        
        print(f'{i+1: >{trial_len}}/{x}', end=' ')
        ids = log_game(ids)
        
        elapsed_time = time.time() - start_time
        sleep_time = max(0, 1.5 - elapsed_time)
        time.sleep(sleep_time)