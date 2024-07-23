import os
import pandas as pd
import shutil
from flask import Flask, render_template, send_from_directory, request
from filmweb_scraper import FilmWebScraper
from imdb_top250_scraper import ImdbTop250Scraper
from imdb_top100_popular_scraper import ImdbPopularMovies
from netflix_top10_PL_scraper import NetflixTop10PL
from waitress import serve
from loguru import logger

app = Flask(__name__)


def remove_http_cache(directory_path):
    http_cache_path = os.path.join(directory_path, "http_cache")
    try:
        shutil.rmtree(http_cache_path)
        print(f"Removed http_cache folder in {directory_path}")
    except Exception as e:
        # Handle any errors that may occur during folder removal
        print(f"Error removing http_cache folder in {directory_path}: {e}")


def get_country_headers():
    try:
        user_country = request.headers.get("Cf-Ipcountry")
        logger.info(f"Country code: {user_country}")
        if not user_country:
            logger.warning("Cf-Ipcountry header not found.")
            user_country = "US"  # Default to 'US' if header is not present
    except Exception as e:
        logger.error(f"Error retrieving country information: {e}")
        user_country = "US"  # Default to 'US' in case of an error

    headers = {
        "Accept-Language": f"{user_country.lower()}-{user_country};q=0.9,en-US;q=0.8,en;q=0.7",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
        "like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    return headers


# Define the root route
@app.route("/", methods=["GET", "POST"])
def root():
    return render_template("home.html")


@app.route("/imdb_top250", methods=["GET", "POST"])
def imdb_top250():
    url = "https://www.imdb.com/chart/top/"
    headers = get_country_headers()
    df = ImdbTop250Scraper.scrape_imdb_top250(url, headers)
    # Remove duplicate rows based on the 'rank' column
    df = df.drop_duplicates(subset=["rank"])
    # Render the imdb_top250.html template, passing the DataFrame as an HTML table and its columns and rows as lists
    return render_template(
        "imdb_top250.html",
        tables=[df.to_html(classes="data")],
        titles=df.columns.values,
        row_data=list(df.to_numpy().tolist()),
    )


@app.route("/imdb_popular_movies", methods=["GET", "POST"])
def imdb_popular_movies():
    url = "https://www.imdb.com/chart/moviemeter/"
    headers = get_country_headers()
    df = ImdbPopularMovies.scrape_imdb_popular_movies(url, headers)
    # Remove duplicate rows based on the 'rank' column
    df = df.drop_duplicates(subset=["rank"])
    # Replace null values in the 'year' column with 0
    df["year"] = df["year"].fillna(0).astype(int)
    return render_template(
        "imdb_popular_movies.html",
        tables=[df.to_html(classes="data")],
        titles=df.columns.values,
        row_data=list(df.to_numpy().tolist()),
    )


@app.route("/filmweb_top100", methods=["GET", "POST"])
def filmweb_top100():
    url = "https://www.filmweb.pl"
    headers = get_country_headers()
    df = FilmWebScraper.scrape_filmweb_top100(url, headers)
    df = df.drop_duplicates(subset=["rank"])

    return render_template(
        "filmweb_top100.html",
        tables=[df.to_html(classes="data")],
        titles=df.columns.values,
        row_data=list(df.to_numpy().tolist()),
    )


@app.route("/netflix_pl_top10", methods=["GET", "POST"])
def results_netflix_top10_pl():
    scraper = NetflixTop10PL()
    headers = get_country_headers()
    scraper.parse(headers)
    # Get the dates of the top 10 rankings from the scraper
    dates = scraper.dates
    # Create a DataFrame from the scraper's results
    df = pd.DataFrame(scraper.results)
    # Remove duplicate rows based on the 'rank' column
    df = df.drop_duplicates(subset=["rank"])
    # scraper.to_db()
    return render_template(
        "netflix_pl_top10.html",
        tables=[df.to_html(classes="data")],
        titles=df.columns.values,
        row_data=list(df.to_numpy().tolist()),
        dates=dates,
    )


# Run the app using the waitress WSGI server
if __name__ == "__main__":
    # app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
    serve(app, port="5000", threads=8)
