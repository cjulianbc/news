from flask import Flask, render_template, url_for, request, redirect
from flask_apscheduler import APScheduler
import twitter
import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
from pytz import timezone
import csv
import time
import config


app = Flask(__name__)


cluster = MongoClient(config.mongo_key)
db = cluster[config.mongo_db]
collection = db[config.mongo_collection]
twitter_tags = collection.find({'_id': 'twitter_tags'})
twitter_tags = twitter_tags[0]['tags']
				

def writeToCSV(data):
	with open('contact_me.csv', mode = 'a') as db:
		email = data['email']
		subject = data['subject']	
		message = data['message']
		csv_writer = csv.writer(db, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
		csv_writer.writerow([email, subject, message])


@app.route('/')
def home():
	return index()


@app.route('/index.html')
def index():
	time_zone = timezone('US/Eastern')
	now = datetime.now(time_zone)
	an_hour_ago = now - timedelta(hours = 2)
	now_format = now.strftime("%d/%m/%Y %H:%M:%S")
	an_hour_ago_format = an_hour_ago.strftime("%d/%m/%Y %H:%M:%S")
	results = list(collection.find({'date_time' : {'$gt' : an_hour_ago_format,'$lt' : now_format}}))
	return render_template('index.html', company = '@CTVMontreal', sumaries = results)


@app.route('/twitterbot.html')
def twitterbot():
	tweets = twitter.Twitter()
	last_tweets = tweets.getTweets('@cjulianbc', 6)
	tweets_with_format = tweets.formatTweetsOwner(last_tweets)
	return render_template('twitterbot.html', user = '@cjulianbc', tweets = tweets_with_format, tags = twitter_tags)


@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
	if request.method == 'POST':
		data = request.form.to_dict()
		writeToCSV(data)
		return redirect('./thankyou.html')
	else:
		return redirect('./error.html')


@app.route('/<string:page>')
def html_page(page):
	return render_template(page)

if __name__ == '__main__':
	app.run(port = 5001)
