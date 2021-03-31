import tweepy
from datetime import datetime
import config

class Twitter:


	def __init__(self):
		self.auth = tweepy.OAuthHandler(config.twitter_auth_1, config.twitter_auth_2)
		self.auth.set_access_token(config.twitter_token_1, config.twitter_token_2)
		self.api = tweepy.API(self.auth)


	def getTweets(self, user, number_of_tweets):
		tweets = self.api.user_timeline(
					screen_name = user, 
					count = number_of_tweets,
					include_rts = False,
					tweet_mode = 'extended'
				)
		return tweets


	def formatTweetsCTVMontreal(self, tweets):
		tweets_array = []
		for tweet in tweets:
			if len((tweet.entities)['urls']) > 0:
				url = (tweet.entities)['urls'][0]['url']
			tweets_array.append(url)
		return tweets_array


	def formatTweetsOwner(self, tweets):
		tweets_array = []
		for tweet in tweets:
			created_at = tweet.created_at.strftime("%d/%m/%Y %H:%M:%S")
			tweets_array.append({'created_at': created_at, 'full_text': tweet.full_text})
		return tweets_array


	def update_no_media(self, tweet):
		return self.api.update_status(status=tweet)


	def update_no_media_thread(self, tweet, last_twitted):
		return self.api.update_status(status=tweet, 
                                 in_reply_to_status_id=last_twitted.id, 
                                 auto_populate_reply_metadata=True)	
	