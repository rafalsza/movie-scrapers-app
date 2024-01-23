from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

# from sqlalchemy import create_engine
# from sqlalchemy.types import Integer, Text, Float


class ImdbScraperTop250Old:
    results = []
    # engine = create_engine('postgresql://postgres:')

    def __init__(self):
        self.results = []
        self.df = None

    def parse(self, headers):
        source = requests.get("https://www.imdb.com/chart/top/", headers=headers)
        soup = BeautifulSoup(source.text, "html.parser")
        movies = soup.select("li.ipc-metadata-list-summary-item")

        for movie in movies:
            name_element = movie.find("div", class_="ipc-title--title")
            rank = name_element.find("h3", class_="ipc-title__text").text.split(
                ". ", 1
            )[0]
            name_t = name_element.find("h3", class_="ipc-title__text").text.split(
                ". ", 1
            )[1]
            anchor_tag = name_element.find("a")
            href = anchor_tag.get("href")
            name = f'<a href="https://www.imdb.com{href}" target="_blank">{name_t}</a>'
            try:
                year = (
                    movie.find("div", class_="cli-title-metadata")
                    .find_all("span", class_="cli-title-metadata-item")[0]
                    .text
                )
            except AttributeError:
                year = 0
            rating_element = movie.find("span", class_="ipc-rating-star")
            rating_text = re.search(r"([\d.]+)", rating_element["aria-label"]).group(1)
            rating = float(rating_text) if rating_text else 0.0
            num_reviews_element = movie.find(
                "span", class_="ipc-rating-star--voteCount"
            )
            num_reviews = (
                re.search(r"\((.*?)\)", num_reviews_element.text).group(1)
                if num_reviews_element
                else 0
            )
            # # Convert M to millions and K to thousands
            # if "M" in num_reviews:
            #     num_reviews = num_reviews.replace("M", "")
            #     num_reviews = f"{float(num_reviews) * 1000000:.0f}"
            # elif "K" in num_reviews:
            #     num_reviews = num_reviews.replace("K", "")
            #     num_reviews = f"{float(num_reviews) * 1000:.0f}"

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
        self.df.to_csv("imdb_top250.csv", index=False)

    # def to_db(self):
    #     self.df.to_sql('imdb_top250', con=self.engine, if_exists='replace', index=False,
    #                    dtype={'rank': Integer, 'movie': Text, 'year': Integer, 'rating': Text, 'num_reviews': Text})
