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
            movies = [tr for tr in soup.find_all("tr") if tr.find("td", class_="title")]

            self.results = []

            for movie in movies:
                rank_tag = movie.find("span", class_="rank")
                rank = int(rank_tag.get_text(strip=True)) if rank_tag else "N/A"
                title_cell = movie.find("td", class_="title")
                title_button = title_cell.find("button") if title_cell else None
                title = (
                    title_button.get_text(strip=True) if title_button else "Brak tytułu"
                )
                weeks_tag = movie.find("td", {"data-uia": "top10-table-row-weeks"})
                weeks = weeks_tag.get_text(strip=True) if weeks_tag else "N/A"

                self.results.append(
                    {
                        "rank": rank,
                        "movie": title,
                        "year": "N/A",
                        "genre": "N/A",
                        "weeks in top10": weeks,
                    }
                )

            self.df = pd.DataFrame(self.results)

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
