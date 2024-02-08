from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import logging


class ImdbScraperTop250Old:

    @staticmethod
    def parse_imdb_page(url, headers):
        results = []
        try:
            source = requests.get(url, headers=headers)
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
                name = (
                    f'<a href="https://www.imdb.com{href}" target="_blank">{name_t}</a>'
                )
                try:
                    year = (
                        movie.find("div", class_="cli-title-metadata")
                        .find_all("span", class_="cli-title-metadata-item")[0]
                        .text
                    )
                except AttributeError:
                    year = 0
                rating_element = movie.find("span", class_="ipc-rating-star")
                rating_text = re.search(
                    r"([\d.]+)", rating_element["aria-label"]
                ).group(1)
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
    def scrape_imdb_top250(url, headers):
        results = ImdbScraperTop250Old.parse_imdb_page(url, headers)
        df = pd.DataFrame(results)
        return df
