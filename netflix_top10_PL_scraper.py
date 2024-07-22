from bs4 import BeautifulSoup
import requests
import pandas as pd

import requests_cache

# Initialize the requests-cache session
requests_cache.install_cache(
    "http_cache/4/netflix_top10_cache", expire_after=3600
)  # Cache expires after 1 hour


def scrape_movie_details(url, headers):
    try:
        source = requests.get(url, headers=headers)
        soup = BeautifulSoup(source.text, "lxml")

        name1 = soup.find("h1").get_text(strip=True)
        metadata = soup.find("div", class_="title-info-metadata-wrapper")
        genre = metadata.find("a").get_text(strip=True) if metadata else "N/A"
        year = metadata.find("span").get_text(strip=True) if metadata else "N/A"

        return {
            "movie": name1,
            "year": year,
            "genre": genre,
        }
    except Exception as e:
        print(f"Error scraping movie details: {e}")
        return {
            "movie": "N/A",
            "year": "N/A",
            "genre": "N/A",
        }


class NetflixTop10PL:
    def __init__(self):
        self.dates = None
        self.df = None
        self.results = None

    def parse(self, headers):
        netflix_url = "https://top10.netflix.com/poland"
        try:
            source = requests.get(netflix_url, headers=headers)
            soup = BeautifulSoup(source.text, "lxml")
            movies = soup.find_all("tr", attrs={"data-id": True})
            dates = soup.find("div", class_="px-3").get_text(strip=True)
            self.results = []

            for movie in movies:
                rank = movie.find("td", class_="tbl-cell-rank").get_text(strip=True)
                weeks = movie.find("div", class_="w-10").span.get_text(strip=True)

                data_id = movie["data-id"]
                url = f"https://www.netflix.com/pl/title/{data_id}"

                movie_details = scrape_movie_details(url, headers)
                name = f'<a href="{url}" target="_blank">{movie_details["movie"]}</a>'

                self.results.append(
                    {
                        "rank": rank,
                        "movie": name,
                        "year": movie_details["year"],
                        "genre": movie_details["genre"],
                        "weeks in top10": weeks,
                    }
                )

            self.df = pd.DataFrame(self.results)
            self.dates = dates

        except Exception as e:
            print(f"Error parsing Netflix page: {e}")

    def download_csv(self):
        try:
            self.df.to_csv("netflix_top10_pl.csv", index=False)
        except Exception as e:
            print(f"Error saving CSV file: {e}")

    # def to_db(self):
    #     self.df.to_sql('filmweb_top100', con=self.engine, if_exists='replace', index=False,
    #                    dtype={'rank': Integer, 'movie': Text, 'year': Integer, 'rating': Text, 'num_reviews': Text})
