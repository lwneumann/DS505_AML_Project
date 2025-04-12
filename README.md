# Ideas

## Pokemon generator
Generate pokemon cards using the [Dataset](https://www.kaggle.com/datasets/adampq/pokemon-tcg-all-cards-1999-2023/data)

For abilities and moves we could use a [word level model](https://www.youtube.com/watch?v=nzRIXaYAaqE) ([also see here](https://colab.research.google.com/drive/1-Nlo4B36oTB0ErIJropiPfrlQWk8qK6f?usp=sharing)). I think this would not work for the names though so either use charecter based models for both name and text or multiple different models. Perhaps just charecter based would be easier for the sake of not adding multiple different types. 

This is unsupervised - maybe we check if we are strictly required to focused on supervised learing.

## Speedrun prediction
Guess how long speedruns take based off game info

[Here is a dataset](https://www.kaggle.com/datasets/alexmerren1/speedrun-com-data). It is certainly large enough to use for a model. We would likely want to find a secondary dataset to merge or cross reference with this one to get elements of the game as features - genere, file size, popularity, etc.