from bs4 import BeautifulSoup
import requests
import pandas as pd


class NetflixTop10PL:
    def __init__(self):
        self.dates = None
        self.df = None
        self.results = None

    def parse(self, headers):
        netflix_url = "https://www.netflix.com/tudum/top10/poland"
        try:
            source = requests.get(netflix_url, headers=headers)
            soup = BeautifulSoup(source.text, "lxml")
            movies = soup.find_all("tr", attrs={"data-id": True})
            dates = soup.find("div", class_="px-3").get_text(strip=True)
            self.results = []

            for movie in movies:
                rank = movie.find("td", class_="tbl-cell-rank").get_text(strip=True)
                title = movie.find("td", class_="tbl-cell-name").get_text(strip=True)
                weeks = movie.find("div", class_="w-10").span.get_text(strip=True)
                data_id = movie["data-id"]
                url = f"https://www.netflix.com/title/{data_id}"
                name = f'<a href="{url}" target="_blank">{title}</a>'

                self.results.append(
                    {
                        "rank": rank,
                        "movie": name,
                        "year": "N/A",
                        "genre": "N/A",
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
