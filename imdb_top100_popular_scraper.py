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
            movies = soup.select("li.ipc-metadata-list-summary-item")

            for movie in movies:
                rank = movie.find("div", class_="meter-const-ranking").text.split()[0]
                name_element = movie.find("div", class_="ipc-title--title")
                # Check if there is an anchor tag inside the name_element
                anchor_tag = name_element.find("a")
                if anchor_tag:
                    href = anchor_tag.get("href")
                    name = f'<a href="https://www.imdb.com{href}" target="_blank">{name_element.text}</a>'
                else:
                    name = name_element.text
                try:
                    year = (
                        movie.find("div", class_="cli-title-metadata")
                        .find_all("span", class_="cli-title-metadata-item")[0]
                        .text
                    )
                except AttributeError:
                    year = 0

                rating_element = movie.find("span", class_="ipc-rating-star")
                rating_label = rating_element.get("aria-label", "")
                rating_text_match = re.search(r"([\d.]+)", rating_label)
                rating_text = rating_text_match.group(1) if rating_text_match else "0.0"
                rating = float(rating_text) if rating_text else 0.0

                num_reviews_element = movie.find(
                    "span", class_="ipc-rating-star--voteCount"
                )
                num_reviews = (
                    re.search(r"\((.*?)\)", num_reviews_element.text).group(1)
                    if num_reviews_element
                    else 0
                )

                results.append(
                    {
                        "rank": rank,
                        "movie": name,
                        "year": year,
                        "rating": rating,
                        "num_reviews": num_reviews,
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
