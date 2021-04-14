from flask import Flask, render_template, request
import pickle
import numpy as np
import bs4 as bs
import re
from nltk.corpus import stopwords
import sqlite3 as sql

app = Flask(__name__)

model = pickle.load(open('IMDB_sentiment.pkl', 'rb'))


@app.route("/")
def home():
    return render_template('home.html')


@app.route('/result', methods=['POST'])
def predict():
    if request.method == 'POST':
        new_review = request.form['review']

        cleaned_review = review_cleaner(new_review)
        prediction = model.predict([cleaned_review])
        pred = ['negative', 'positive'][prediction[0]]

        try:
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO Results (Review,Sentiment) VALUES (?,?)",
                            (new_review, pred))
                con.commit()

        except:
            con.rollback()

        finally:
            return render_template("result.html", value=pred)
            con.close()


def review_cleaner(review):
    '''
    Clean and preprocess a review.

    1. Remove HTML tags
    2. Use regex to remove all special characters (only keep letters)
    3. Make strings to lower case and tokenize / word split reviews
    4. Remove English stopwords
    5. Rejoin to one string
    '''

    # 1. Remove HTML tags
    review = bs.BeautifulSoup(review).text

    # 2. Use regex to find emoticons
    emoticons = re.findall('(?::|;|=)(?:-)?(?:\)|\(|D|P)', review)

    # 3. Remove punctuation
    review = re.sub("[^a-zA-Z]", " ", review)

    # 4. Tokenize into words (all lower case)
    review = review.lower().split()

    # 5. Remove stopwords
    eng_stopwords = set(stopwords.words("english"))
    review = [w for w in review if not w in eng_stopwords]

    # 6. Join the review to one sentence
    review = ' '.join(review + emoticons)
    # add emoticons to the end

    return (review)


@app.route('/data')
def list_all():
    con = sql.connect("database.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select * from Results")

    rows = cur.fetchall()  # returns list of dictionaries
    return render_template("data.html", rows=rows)
    con.close()

if __name__ == "__main__":
    app.run(debug=True)