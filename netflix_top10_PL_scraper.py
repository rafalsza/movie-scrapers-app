from bs4 import BeautifulSoup
import requests
import pandas as pd

# import requests_cache

# Initialize the requests-cache session
# requests_cache.install_cache(
#     "http_cache/4/netflix_top10_cache", expire_after=3600
# )  # Cache expires after 1 hour


def scrape_movie_details(url, headers):
    source = requests.get(url, headers=headers)
    soup = BeautifulSoup(source.text, "lxml")

    name1 = soup.find("h1").get_text(strip=True)
    metadata = soup.find("div", class_="title-info-metadata-wrapper")
    genre = metadata.a.text
    year = metadata.span.text

    return {
        "movie": name1,
        "year": year,
        "genre": genre,
    }


class NetflixTop10PL:
    def __init__(self):
        self.dates = None
        self.df = None
        self.results = None

    def parse(self, headers):
        netflix_url = "https://top10.netflix.com/poland"
        source = requests.get(netflix_url, headers=headers)
        soup = BeautifulSoup(source.text, "lxml")
        movies = soup.find_all("tr", attrs={"data-id": True})
        dates = soup.find("div", class_="px-3").get_text(strip=True)
        self.results = []

        for movie in movies:
            rank = movie.find("td", class_="tbl-cell-rank").get_text(strip=True)
            title = movie.find("td", class_="tbl-cell-name").get_text(strip=True)
            weeks = movie.find("div", class_="w-10").span.text

            data_id = movie["data-id"]
            url = f"https://www.netflix.com/pl/title/{data_id}"
            if url:
                name = f'<a href="{url}" target="_blank">{title}</a>'
            else:
                name = title

            # movie_details = scrape_movie_details(url, headers)

            # self.results.append(
            #     {
            #         "rank": rank,
            #         "movie": movie_details["movie"],
            #         "year": movie_details["year"],
            #         "genre": movie_details["genre"],
            #         "weeks in top10": weeks,
            #     }
            # )

            self.results.append(
                {
                    "rank": rank,
                    "movie": name,
                    "year": "null",
                    "genre": "null",
                    "weeks in top10": weeks,
                }
            )

        self.df = pd.DataFrame(self.results)
        self.dates = dates

    def download_csv(self):
        self.df.to_csv("filmweb_top100.csv", index=False)

    # def to_db(self):
    #     self.df.to_sql('filmweb_top100', con=self.engine, if_exists='replace', index=False,
    #                    dtype={'rank': Integer, 'movie': Text, 'year': Integer, 'rating': Text, 'num_reviews': Text})
