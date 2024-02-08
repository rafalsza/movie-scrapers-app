from bs4 import BeautifulSoup
import requests
import pandas as pd
import logging


class FilmWebScraper:
    results = []

    @staticmethod
    def parse_filmweb_page(url, headers):
        results = []
        try:
            for page_number in range(5):
                source = requests.get(
                    url + f"/ajax/ranking/film/{page_number}", headers=headers
                )
                soup = BeautifulSoup(source.text, "lxml")
                movies = soup.find_all("div", class_="rankingType")

                for movie in movies:
                    rank = movie.find("span", class_="rankingType__position").get_text(
                        strip=True
                    )
                    name_element = movie.find("div", class_="rankingType__titleWrapper")
                    title = name_element.a.text
                    href = name_element.find("a")["href"]
                    if href:
                        name = f'<a href="{url}{href}" target="_blank">{title}</a>'
                    else:
                        name = title

                    year = movie.find("span", class_="rankingType__year").get_text(
                        strip=True
                    )
                    genre_elements = movie.find(
                        "div", class_="rankingType__genres"
                    ).find_all("a")
                    genres = ", ".join(
                        [genre.get_text(strip=True) for genre in genre_elements]
                    )
                    rating = movie.find(
                        "span", class_="rankingType__rate--value"
                    ).get_text(strip=True)
                    num_reviews = movie.find(
                        "span", class_="rankingType__rate--count"
                    ).span.text

                    results.append(
                        {
                            "rank": rank,
                            "movie": name,
                            "year": year,
                            "genre": genres,
                            "rating": rating,
                            "num_reviews": num_reviews,
                        }
                    )
        except Exception as e:
            logging.error(f"Error parsing Filmweb page: {e}")

        return results

    @staticmethod
    def download_csv(df, filename):
        try:
            df.to_csv(filename, index=False)
        except Exception as e:
            logging.error(f"Error saving CSV file '{filename}': {e}")

    @staticmethod
    def scrape_filmweb_top100(url, headers):
        results = FilmWebScraper.parse_filmweb_page(url, headers)
        df = pd.DataFrame(results)
        return df
