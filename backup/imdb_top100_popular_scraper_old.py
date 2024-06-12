from imdb import Cinemagoer
import pandas as pd

# from sqlalchemy import create_engine
# from sqlalchemy.types import Integer, Text, Float


class ImdbScraperPopular:
    # engine = create_engine('postgresql://postgres:postgres@XX.XXX.XX.140:5432/scrapers')

    def parse(self):
        ia = Cinemagoer()
        self.results = []
        top100popular = ia.get_popular100_movies()
        for i in top100popular:
            rank = i.get("popular movies 100 rank")
            name = i.get("title")
            year = i.get("year")
            rating = i.get("rating")
            num_reviews = i.get("votes")

            self.results.append(
                {
                    "rank": rank,
                    "movie": name,
                    "year": year,
                    "rating": rating,
                    "num_reviews": num_reviews,
                }
            )
        self.df = pd.DataFrame(self.results)

    def download_csv(self):
        self.df.to_csv("imdb_top100_popular.csv", index=False)

    # def to_db(self):
    # self.df.to_sql('imdb_top100_popular', con=self.engine, if_exists='replace', index=False,
    # dtype={'rank': Integer, 'movie': Text, 'year': Integer, 'rating': Float, 'num_reviews': Integer})
