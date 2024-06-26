import os
import pandas as pd
import shutil
from flask import Flask, render_template, send_from_directory, request
from filmweb_scraper import FilmWebScraper
from imdb_top250_scraper import ImdbTop250Scraper
from imdb_top100_popular_scraper import ImdbPopularMovies
from netflix_top10_PL_scraper import NetflixTop10PL
from waitress import serve
import logging

app = Flask(__name__)
app.secret_key = "your_secret_key_here"
logging.basicConfig(level=logging.INFO)


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
        logging.info(f"Country code: {user_country}")
        if not user_country:
            logging.warning("Cf-Ipcountry header not found.")
            user_country = "US"  # Default to 'US' if header is not present
    except Exception as e:
        logging.error(f"Error retrieving country information: {e}")
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
    # Save the DataFrame to a CSV file
    filename = "imdb_top250.csv"
    ImdbTop250Scraper.download_csv(df, filename)
    # Render the imdb_top250.html template, passing the DataFrame as an HTML table and its columns and rows as lists
    return render_template(
        "imdb_top250.html",
        tables=[df.to_html(classes="data")],
        titles=df.columns.values,
        row_data=list(df.to_numpy().tolist()),
    )


# Define the download_i route for downloading the IMDB top 250 movies CSV file
@app.route("/download_imdb_top250")
def download_imdb_top250():
    # Send the imdb_top250.csv file as an attachment
    return send_from_directory("", "imdb_top250.csv", as_attachment=True)


# Define the results_imdb_popular route for IMDB top 100 popular movies
@app.route("/imdb_popular_movies", methods=["GET", "POST"])
def imdb_popular_movies():
    url = "https://www.imdb.com/chart/moviemeter/"
    headers = get_country_headers()
    df = ImdbPopularMovies.scrape_imdb_popular_movies(url, headers)
    # Remove duplicate rows based on the 'rank' column
    df = df.drop_duplicates(subset=["rank"])
    # Replace null values in the 'year' column with 0
    df["year"] = df["year"].fillna(0).astype(int)
    # Save the DataFrame to a CSV file
    filename = "imdb_top100_popular.csv"
    ImdbPopularMovies.download_csv(df, filename)
    # Render the imdb_popular_movies.html template, passing the DataFrame as an HTML table and its columns and rows
    # as lists
    return render_template(
        "imdb_popular_movies.html",
        tables=[df.to_html(classes="data")],
        titles=df.columns.values,
        row_data=list(df.to_numpy().tolist()),
    )


@app.route("/download_imdb_top100_popular")
def download_imdb_popular_top100():
    # Send the imdb_top100_popular.csv file as an attachment
    return send_from_directory("", "imdb_top100_popular.csv", as_attachment=True)


@app.route("/filmweb_top100", methods=["GET", "POST"])
def filmweb_top100():
    url = "https://www.filmweb.pl"
    headers = get_country_headers()
    df = FilmWebScraper.scrape_filmweb_top100(url, headers)
    df = df.drop_duplicates(subset=["rank"])
    filename = "filmweb_top100.csv"
    FilmWebScraper.download_csv(df, filename)

    return render_template(
        "filmweb_top100.html",
        tables=[df.to_html(classes="data")],
        titles=df.columns.values,
        row_data=list(df.to_numpy().tolist()),
    )


@app.route("/download_filmweb_top100")
def download_filmweb_top100():
    return send_from_directory("", "filmweb_top100.csv", as_attachment=True)


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
    # Save the DataFrame to a CSV file
    df.to_csv("netflix_top10_PL.csv", index=False)
    return render_template(
        "netflix_pl_top10.html",
        tables=[df.to_html(classes="data")],
        titles=df.columns.values,
        row_data=list(df.to_numpy().tolist()),
        dates=dates,
    )


@app.route("/download_netflix_pl_top10")
def download_netflix_pl_top10():
    return send_from_directory("", "netflix_top10_PL.csv", as_attachment=True)


# Run the app using the waitress WSGI server
if __name__ == "__main__":
    # app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
    serve(app, port="5000", threads=8)
