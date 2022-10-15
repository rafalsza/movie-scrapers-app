import waitress
from flask import Flask
from flask import render_template
from flask import request
from flask import send_from_directory
from imdb_scraper import IMDBSCRAPER
from filmweb_scraper import FILMWEBSCRAPER
from imdb_scraper_2 import ImdbscraperPopular
from netflix_top10_PL import NetflixTop10PL
import pandas as pd

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def root():
    return render_template('home.html')


@app.route('/results_imdb', methods=['GET', 'POST'])
def results_i():
    scraper = IMDBSCRAPER()
    scraper.parse()
    df = pd.DataFrame(scraper.results)
    df = df.drop_duplicates(subset=['rank'])
    table = df.to_html()
    # scraper.to_db()
    df.to_csv('imdb_top250.csv', index=False)
    return render_template('results_imdb.html', tables=[df.to_html(classes='data')], titles=df.columns.values,
                           row_data=list(df.values.tolist()))


@app.route('/download_i')
def download_i():
    return send_from_directory('', 'imdb_top250.csv', as_attachment=True)


# IMDB top 100 popular
@app.route('/results_imdb_popular', methods=['GET', 'POST'])
def results_imdb_popular():
    scraper = ImdbscraperPopular()
    scraper.parse()
    df = pd.DataFrame(scraper.results)
    df = df.drop_duplicates(subset=['rank'])
    df.year.fillna(value=0, inplace=True)
    df.year = df.year.astype(int)
    table = df.to_html()
    # scraper.to_db()
    df.to_csv('imdb_top100_popular.csv', index=False)
    return render_template('results_imdb_popular.html', tables=[df.to_html(classes='data')], titles=df.columns.values,
                           row_data=list(df.values.tolist()))


@app.route('/download_i_p')
def download_i_p():
    return send_from_directory('', 'imdb_top100_popular.csv', as_attachment=True)


# FILMWEB
@app.route('/results_filmweb', methods=['GET', 'POST'])
def results_f():
    scraper = FILMWEBSCRAPER()
    scraper.parse()
    df = pd.DataFrame(scraper.results)
    df = df.drop_duplicates(subset=['rank'])
    # scraper.to_db()
    df.to_csv('filmweb_top100.csv', index=False)
    return render_template('results_filmweb.html', tables=[df.to_html(classes='data')], titles=df.columns.values,
                           row_data=list(df.values.tolist()))


@app.route('/download_f')
def download_f():
    return send_from_directory('', 'filmweb_top100.csv', as_attachment=True)


# NETFLIX TOP10 POLAND
@app.route('/results_netflix_top10_pl', methods=['GET', 'POST'])
def results_netflix_top10_pl():
    scraper = NetflixTop10PL()
    scraper.parse()
    dates = scraper.dates
    df = pd.DataFrame(scraper.results)
    df = df.drop_duplicates(subset=['rank'])
    # scraper.to_db()
    df.to_csv('netflix_top10_PL.csv', index=False)
    return render_template('results_netflix_top10_pl.html', tables=[df.to_html(classes='data')],
                           titles=df.columns.values,
                           row_data=list(df.values.tolist()), dates=dates)


@app.route('/download_n_top10_pl')
def download_netflix_top10_pl():
    return send_from_directory('', 'netflix_top10_PL.csv', as_attachment=True)


if __name__ == '__main__':
    #app.run(debug=True, threaded=True)
    waitress.serve(app, host='127.0.0.1', port='5000')
