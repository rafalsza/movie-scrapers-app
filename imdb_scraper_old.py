from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.types import Integer, Text, Float


class IMDBSCRAPER:
    results = []
    engine = create_engine('postgresql://postgres:postgres@18.197.53.140:5432/scrapers')

    def parse(self):
        source = requests.get("https://www.imdb.com/chart/top/")
        soup = BeautifulSoup(source.text, "html.parser")
        movies = soup.find("tbody", class_="lister-list").find_all("tr")

        for movie in movies:
            rank = movie.find("td", class_="titleColumn").get_text(strip=True).split('.')[0]
            name = movie.find("td", class_="titleColumn").a.text
            year = movie.find("td", class_="titleColumn").span.text.replace('(', '').replace(')', '')
            rating = movie.find("td", class_="ratingColumn imdbRating").get_text(strip=True)
            num_reviews = movie.find("td", class_="ratingColumn imdbRating").strong.attrs["title"]
            num_reviews = re.findall(r"\S+(?=\suser)", num_reviews)[0]

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
                       dtype={'rank': Integer, 'movie': Text, 'year': Integer, 'rating': Text, 'num_reviews': Text})
