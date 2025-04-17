import requests
import csv
import os

# ----------------------
# CONFIGURATION
# ----------------------

# This should be pulled more intellegently from the gameIDs.json depending on progress and pass queries to work
# through the listed games. For now I'm just leaving this here but we'll need fix this when we start gathering.
APPIDS = {
    2495100: 'Hello Kitty Island Adventure'
}

# Steam Web API Key
STEAM_API_KEY = "wewilladdsteamkeyinasecuremannerhere:)"

# ----------------------
# GET REVIEWS
# ----------------------

def get_reviews(appid, num_reviews=100):
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

def write_reviews_to_csv(appid, reviews, print_log=True):
    filename = f"steamreviews.csv"
    # Check if the file already exists
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header only if the file is new
        if not file_exists:
            writer.writerow(['AppID', 'ReviewID', 'Author', 'Review', 'Recommended', 'VotesUp', 'VotesFunny', 'PostedDate'])
        for review in reviews:
            writer.writerow([
                appid,
                review.get('recommendationid'),
                review.get('author', {}).get('steamid'),
                review.get('review'),
                review.get('voted_up'),
                review.get('votes_up'),
                review.get('votes_funny'),
                review.get('timestamp_created')
            ])
    if print_log:
        print(f"-{appid}: {len(reviews)} reviews")
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

def track_reviews(appid_map, print_log=True):
    for appid, name in appid_map.items():
        if valid_name(name):
            reviews = get_reviews(appid)
            write_reviews_to_csv(appid, reviews, print_log=print_log)
    return

# ----------------------
# MAIN
# ----------------------

if __name__ == '__main__':
    track_reviews(APPIDS)