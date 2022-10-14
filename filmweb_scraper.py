from bs4 import BeautifulSoup
import requests
import re
import pandas as pd


# from sqlalchemy import create_engine
# from sqlalchemy.types import Integer, Text, Float


class FILMWEBSCRAPER:
    results = []

    # engine = create_engine('postgresql://postgres:postgres@18.197.53.140:5432/scrapers')

    def parse(self):
        for page_number in range(5):
            FILMWEB_URL = 'https://www.filmweb.pl'
            source = requests.get(FILMWEB_URL + f'/ajax/ranking/film/{page_number}')
            soup = BeautifulSoup(source.text, "lxml")
            movies = soup.find_all("div", class_="rankingType")

            for movie in movies:
                rank = movie.find("span", class_="rankingType__position").get_text(strip=True)
                name = movie.find("div", class_="rankingType__titleWrapper").a.text
                year = movie.find("span", class_="rankingType__year").get_text(strip=True)
                genre = movie.find("div", class_="rankingType__genres").get_text(strip=True).replace('gatunek', '')
                rating = movie.find("span", class_="rankingType__rate--value").get_text(strip=True)
                num_reviews = movie.find("span", class_="rankingType__rate--count").span.text

                self.results.append({'rank': rank,
                                     'movie': name,
                                     'year': year,
                                     'genre': genre,
                                     'rating': rating,
                                     'num_reviews': num_reviews})
                self.df = pd.DataFrame(self.results)

    def download_csv(self):
        self.df.to_csv('filmweb_top100.csv', index=False)

    # def to_db(self):
    #     self.df.to_sql('filmweb_top100', con=self.engine, if_exists='replace', index=False,
    #                    dtype={'rank': Integer, 'movie': Text, 'year': Integer, 'rating': Text, 'num_reviews': Text})
