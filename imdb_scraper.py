from imdb import Cinemagoer
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.types import Integer, Text, Float


class IMDBSCRAPER:
    results = []

    engine = create_engine('postgresql://postgres:postgres@18.197.53.140:5432/scrapers')

    def parse(self):
        ia = Cinemagoer()
        top250 = ia.get_top250_movies()
        for i in top250:
            rank = i.get('top 250 rank')
            name = i.get('title')
            year = i.get('year')
            rating = i.get('rating')
            num_reviews = i.get('votes')

            self.results.append({'rank': rank,
                                 'movie': name,
                                 'year': year,
                                 'rating': rating,
                                 'num_reviews': num_reviews})
            self.df = pd.DataFrame(self.results)

    def download_csv(self):
        self.df.to_csv('imdb_top250.csv', index=False)

    def to_db(self):
        self.df.to_sql('imdb_top250', con=self.engine, if_exists='replace', index=False,
                       dtype={'rank': Integer, 'movie': Text, 'year': Integer, 'rating': Float, 'num_reviews': Integer})
