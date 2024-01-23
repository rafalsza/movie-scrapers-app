import os
import shutil

from flask import Flask
from flask import render_template, request, session, redirect
from flask import send_from_directory
from filmweb_scraper import FilmWebScraper
from imdb_scraper_old import ImdbScraperTop250Old
from imdb_top100_popular_scraper import ImdbPopularMovies
from netflix_top10_PL_scraper import NetflixTop10PL
from waitress import serve
import pandas as pd

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

headers_PL = {
    "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
    "like Gecko)"
    "Chrome/91.0.4472.124 Safari/537.36",
}

headers_EN = {
    "Accept-Language": "en-US;q=0.8,en;q=0.7",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
    "like Gecko)"
    "Chrome/91.0.4472.124 Safari/537.36",
}


def remove_http_cache(directory_path):
    http_cache_path = os.path.join(directory_path, "http_cache")
    try:
        shutil.rmtree(http_cache_path)
        print(f"Removed http_cache folder in {directory_path}")
    except Exception as e:
        # Handle any errors that may occur during folder removal
        print(f"Error removing http_cache folder in {directory_path}: {e}")
        pass


# Function to get the selected language and headers
def get_language_and_headers():
    selected_language = session.get("language", "PL")
    headers = headers_PL if selected_language == "PL" else headers_EN
    return selected_language, headers


# Create a route to handle language selection
@app.route("/change_language", methods=["GET", "POST"])
def change_language():
    if request.method == "POST":
        language = request.form.get("language")
        session["language"] = language
        # remove_http_cache("http_cache/")
    else:
        language = request.args.get("language")
        if language:
            session["language"] = language
            # remove_http_cache("http_cache/")
    return redirect(request.referrer)  # Redirect back to the previous page


# Define the root route
@app.route("/", methods=["GET", "POST"])
def root():
    return render_template("home.html")


# Define the results_i route for IMDB top 250 movies
@app.route("/imdb_top250", methods=["GET", "POST"])
def imdb_top250():
    selected_language, headers = get_language_and_headers()
    # Create an instance of the IMDBSCRAPER class
    scraper = ImdbScraperTop250Old()
    # Parse the data from IMDB
    scraper.parse(headers)
    # Create a DataFrame from the scraper's results
    df = pd.DataFrame(scraper.results)
    # Remove duplicate rows based on the 'rank' column
    df = df.drop_duplicates(subset=["rank"])
    # Create an HTML table from the DataFrame
    table = df.to_html()
    # Save the DataFrame to a CSV file
    df.to_csv("imdb_top250.csv", index=False)
    # Render the imdb_top250.html template, passing the DataFrame as an HTML table and its columns and rows as lists
    return render_template(
        "imdb_top250.html",
        tables=[df.to_html(classes="data")],
        titles=df.columns.values,
        row_data=list(df.values.tolist()),
    )


# Define the download_i route for downloading the IMDB top 250 movies CSV file
@app.route("/download_imdb_top250")
def download_imdb_top250():
    # Send the imdb_top250.csv file as an attachment
    return send_from_directory("", "imdb_top250.csv", as_attachment=True)


# Define the results_imdb_popular route for IMDB top 100 popular movies
@app.route("/imdb_popular_movies", methods=["GET", "POST"])
def imdb_popular_movies():
    selected_language, headers = get_language_and_headers()
    scraper = ImdbPopularMovies()
    scraper.parse(headers)  # Call the parse method to populate the df attribute
    df = scraper.df
    # Remove duplicate rows based on the 'rank' column
    df = df.drop_duplicates(subset=["rank"])
    # Replace null values in the 'year' column with 0
    df.year.fillna(value=0, inplace=True)
    # Convert the 'year' column to integer data type
    df.year = df.year.astype(int)
    # Create an HTML table from the DataFrame
    table = df.to_html()
    # Save the DataFrame to a CSV file
    df.to_csv("imdb_top100_popular.csv", index=False)
    # Render the imdb_popular_movies.html template, passing the DataFrame as an HTML table and its columns and rows
    # as lists
    return render_template(
        "imdb_popular_movies.html",
        tables=[df.to_html(classes="data")],
        titles=df.columns.values,
        row_data=list(df.values.tolist()),
    )


# Define the download_i_p route for downloading the IMDB top 100 popular movies CSV file
@app.route("/download_imdb_top100_popular")
def download_imdb_popular_top100():
    # Send the imdb_top100_popular.csv file as an attachment
    return send_from_directory("", "imdb_top100_popular.csv", as_attachment=True)


# Define the results_f route for Filmweb top 100 movies
@app.route("/filmweb_top100", methods=["GET", "POST"])
def filmweb_top100():
    selected_language, headers = get_language_and_headers()
    scraper = FilmWebScraper()
    scraper.parse(headers)
    df = pd.DataFrame(scraper.results)
    df = df.drop_duplicates(subset=["rank"])
    df.to_csv("filmweb_top100.csv", index=False)
    # Render the filmweb_top100.html template, passing the DataFrame as an HTML table and its columns and rows as lists
    return render_template(
        "filmweb_top100.html",
        tables=[df.to_html(classes="data")],
        titles=df.columns.values,
        row_data=list(df.values.tolist()),
    )


# Define the download_f route for downloading the Filmweb top 100 movies CSV file
@app.route("/download_filmweb_top100")
def download_filmweb_top100():
    # Send the filmweb_top100.csv file as an attachment
    return send_from_directory("", "filmweb_top100.csv", as_attachment=True)


# Define the results_netflix_top10_pl route for Netflix top 10 movies in Poland
@app.route("/netflix_pl_top10", methods=["GET", "POST"])
def results_netflix_top10_pl():
    selected_language, headers = get_language_and_headers()
    scraper = NetflixTop10PL()
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
    # Render the netflix_pl_top10.html template, passing the dates and DataFrame as lists and the DataFrame
    # as an HTML table
    return render_template(
        "netflix_pl_top10.html",
        tables=[df.to_html(classes="data")],
        titles=df.columns.values,
        row_data=list(df.values.tolist()),
        dates=dates,
    )


# Define the download_n_t10_pl route for downloading the Netflix top 10 movies in Poland CSV file
@app.route("/download_netflix_pl_top10")
def download_netflix_pl_top10():
    return send_from_directory("", "netflix_top10_PL.csv", as_attachment=True)


# Run the app using the waitress WSGI server
if __name__ == "__main__":
    # app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
    serve(app, port="5000", threads=8)
