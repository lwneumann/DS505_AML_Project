import requests
import csv
import os
import json


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
        'num_per_page': num_reviews
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

def isEnglish(s):
    """
    Since most english messages can be written in ascii this sort of detects english.
    It doesn't do anything to stop the other languages that also use ascii though.
    Also drops reviews with emojis that are otherwise in english.
    """
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def process_review(review_message):
    valid_message = True
    # Many messages aren't in english. This would be hard for a model to deal with so we shouldn't deal with them.
    if not isEnglish(review_message):
        print(review_message)
        return "", False
    # Remove new lines
    review_message.get('review').replace('\n', ' ')
    return review_message, valid_message

def write_reviews_to_csv(appid, reviews, print_log=True):
    """
    Logs the reviews to the csv
    """
    filename = f"steamreviews.csv"
    # Check if the file already exists
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header only if the file is new
        if not file_exists:
            writer.writerow(['AppID', 'ReviewID', 'Author', 'Review', 'Recommended', 'VotesUp', 'VotesFunny', 'PostedDate'])
        for review in reviews:
            # Process/validate review
            review_message, valid_message = process_review(review.get('review'))
            if valid_message:
                writer.writerow([
                    appid,
                    review.get('recommendationid'),
                    review.get('author', {}).get('steamid'),
                    review_message,
                    review.get('voted_up'),
                    review.get('votes_up'),
                    review.get('votes_funny'),
                    review.get('timestamp_created')
                ])
    if print_log:
        print(f"-{appid}: {len(reviews)} reviews")
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
        write_reviews_to_csv(appid, reviews, print_log=print_log)
    elif print_log:
        print(f'-{appid}: "{name}" invalid name')
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
    ids = None
    for i in range(40):
        ids = log_game(ids)
