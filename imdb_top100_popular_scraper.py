import json
import re
import pandas as pd
from bs4 import BeautifulSoup
import requests
import logging


class ImdbPopularMovies:

    @staticmethod
    def parse_imdb_page(url, headers):
        results = []
        try:
            source = requests.get(url, headers=headers)
            soup = BeautifulSoup(source.text, "html.parser")
            script_tag = soup.find(
                "script", id="__NEXT_DATA__", type="application/json"
            )
            json_data = json.loads(script_tag.string)
            movies = json_data["props"]["pageProps"]["pageData"]["chartTitles"]["edges"]

            for movie in movies:
                rank = movie["currentRank"]
                movie_node = movie["node"]
                title = movie_node["titleText"]["text"]
                movie_url = f"https://www.imdb.com/title/{movie_node['id']}/"
                name = f'<a href="{movie_url}" target="_blank">{title}</a>'
                year = movie_node["releaseYear"]["year"]
                genres = ", ".join(
                    [
                        genre["genre"]["text"]
                        for genre in movie_node["titleGenres"]["genres"]
                    ]
                )
                rating = movie_node["ratingsSummary"]["aggregateRating"]
                rating = rating if rating is not None else ""
                num_reviews = movie_node["ratingsSummary"]["voteCount"]

                results.append(
                    {
                        "rank": rank,
                        "movie": name,
                        "year": year,
                        "genres": genres,
                        "rating": rating,
                        "reviews": num_reviews,
                    }
                )
        except Exception as e:
            logging.error(f"Error parsing IMDb page: {e}")

        return results

    @staticmethod
    def download_csv(df, filename):
        try:
            df.to_csv(filename, index=False)
        except Exception as e:
            logging.error(f"Error saving CSV file '{filename}': {e}")

    @staticmethod
    def scrape_imdb_popular_movies(url, headers):
        results = ImdbPopularMovies.parse_imdb_page(url, headers)
        df = pd.DataFrame(results)
        return df
