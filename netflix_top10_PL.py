from bs4 import BeautifulSoup
import requests
import re
import pandas as pd


# from sqlalchemy import create_engine
# from sqlalchemy.types import Integer, Text, Float
pd.options.display.max_columns = None

class NetflixTop10PL:
    # engine = create_engine('postgresql://')

    def parse(self):
        NETFLIX_URL = 'https://top10.netflix.com/poland'
        source = requests.get(NETFLIX_URL)
        soup = BeautifulSoup(source.text, "lxml")
        # movies = soup.find("tbody").find_all("tr")
        movies = soup.find_all("tr", attrs={"data-id": True})
        dates = soup.find("div", class_="px-3").get_text(strip=True)
        self.results = []

        for movie in movies:
            rank = movie.find("td", class_="pb-2").get_text(strip=True)
            # name = movie.find("td", class_="leading-tight").get_text(strip=True)
            weeks = movie.find("div", class_="w-12").span.text

            data_id = movie['data-id']
            url = f'https://www.netflix.com/pl/title/{data_id}'
            source1 = requests.get(url)
            soup1 = BeautifulSoup(source1.text, "lxml")
            movies2 = soup1.find("div", class_="details-container")

            for mov in movies2:
                name1 = mov.find("h1").get_text(strip=True)
                genre = mov.find("div", class_="title-info-metadata-wrapper").a.text
                year = mov.find("div", class_="title-info-metadata-wrapper").span.text

                self.results.append({'rank': rank,
                                     'movie': name1,
                                     'year': year,
                                     'genre': genre,
                                     'weeks in top10': weeks,
                                     })
            self.df = pd.DataFrame(self.results)
            self.dates = dates

    def download_csv(self):
        self.df.to_csv('filmweb_top100.csv', index=False)

    # def to_db(self):
    #     self.df.to_sql('filmweb_top100', con=self.engine, if_exists='replace', index=False,
    #                    dtype={'rank': Integer, 'movie': Text, 'year': Integer, 'rating': Text, 'num_reviews': Text})
