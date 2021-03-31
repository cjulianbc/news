import requests
from bs4 import BeautifulSoup


class Scrapper:


	def __init__(self, urls):
		self.urls = urls


	def getArticles(self):
		articles = []
		for url in self.urls:
			html_document = requests.get(url)
			soup = BeautifulSoup(html_document.text, 'html.parser')
			paragraphs = soup.select('div.articleBody > p')
			
			article = ''
			if len(paragraphs) != 0:
				for paragraph in paragraphs:
					article = article + paragraph.get_text() + ' '
				articles.append({'url': url, 'text': article})
		return(articles)

