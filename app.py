from flask import Flask, render_template, url_for, request, redirect
from flask_apscheduler import APScheduler
import twitter
import scrapper
import sumarizer
import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
from pytz import timezone
import csv
import math
import time
import config

app = Flask(__name__)
scheduler = APScheduler()


cluster = MongoClient(config.mongo_key)
db = cluster[config.mongo_db]
collection = db[config.mongo_collection]
twitter_tags = collection.find({'_id': 'twitter_tags'})
twitter_tags = twitter_tags[0]['tags']


def findNews():
	user = '@CTVMontreal'
	number_of_tweets = 5
	chars_per_tweet = 260

	tweets = twitter.Twitter()
	last_tweets = tweets.getTweets(user, number_of_tweets)
	urls_from_tweets = tweets.formatTweetsCTVMontreal(last_tweets)
	print(urls_from_tweets)
	
	urls_to_summarize = []
	for url in urls_from_tweets:
		if collection.count_documents({'_id': url}) == 0:
			urls_to_summarize.append(url)
	print(urls_to_summarize)

	news_scrapper = scrapper.Scrapper(urls_to_summarize)
	articles = news_scrapper.getArticles()
	news_summarizer = sumarizer.Sumarizer(articles)
	articles_summarized = news_summarizer.getSummary()

	now = datetime.now()
	now_format = now.strftime("%d/%m/%Y %H:%M:%S")

	print('Server, articles summarized:')
	print(len(articles_summarized))
	for i in range(len(articles_summarized)):
		collection.insert_one({'_id': articles_summarized[i]['url'], 'text': articles_summarized[i]['text'], 'date_time': now_format})
		tag_count = 0
		for tag in twitter_tags:
			if tag in articles_summarized[i]['text'].lower():
				tag_count += 1
		print('Server, tags found:')
		print(tag_count)
		if tag_count > 0:
			time.sleep(5)
			text = (articles_summarized[i]['text'] + ' ' + user + ' ')
			total_tweets = math.ceil(len(text) / chars_per_tweet)
			tweet_consecutive = 1
			print('Server, twitter start---------------')
			while len(text) > 1:
				sub_string = text[0:chars_per_tweet]
				space_index = sub_string.rfind(' ')
				if tweet_consecutive == 1:
					last_tweeted = tweets.update_no_media(f'{tweet_consecutive}/{total_tweets}. {text[0:space_index]}')
				else:	
					last_tweeted = tweets.update_no_media_thread((f'{tweet_consecutive}/{total_tweets}. {text[0:space_index]}'), last_tweeted)
				print('Server, twitter string:')
				print(text[0:space_index])
				text = text[space_index:]
				tweet_consecutive += 1
			print('Server, twitter end---------------')
				

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
	print(now)
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
	scheduler.add_job(id = 'findNews', func = findNews, trigger = 'interval', seconds = 120)
	scheduler.start()
	app.run()
