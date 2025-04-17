## Steam Review Sentiment

# Dataset
Tenatively we will gather data locally to be fed back into the model.

# Notes about [Steam API](https://steamcommunity.com/dev)
- 200 requests in five minutes or one request every 1.5 seconds.

- [List of games and IDs](http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key=STEAMKEY&format=json).
  - We need to ignore games with names "" since they don't have a page so won't have reviews. There are also lots of games with test in their name that are also not worth checking such as 
    - "Pieterw test app76 ( 216938 )"
    - "test[n]" (there are several test games like that)

- [User reviews documentation](https://partner.steamgames.com/doc/store/getreviews)