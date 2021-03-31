import json
import requests
import config


class Sumarizer:


	def __init__(self, articles):
		API_TOKEN = config.huggingface_token
		self.articles = articles
		self.API_URL = config.huggingface_API_URL
		self.headers = {"Authorization": f"Bearer {API_TOKEN}"}


	def getSummary(self):
		summaries = []
		for article in self.articles:
		    data = json.dumps(article['text'])
		    response = requests.request("POST", self.API_URL, headers = self.headers, data = data)
		    print('Sumarizer, response:')
		    print(json.loads(response.content.decode("utf-8")))
		    if not ('error' in json.loads(response.content.decode("utf-8"))):
		    	summaries.append({'url': article['url'], 'text': json.loads(response.content.decode("utf-8"))[0]['summary_text'].replace("<n>", " ")})
		return summaries    
