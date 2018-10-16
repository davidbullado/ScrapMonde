import sys
from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
from scrap import scrap_news, scrap_article, get_article_from_disk

from hashlink import hash_url, reverse_hash

from logger import log

app = Flask(__name__)
CORS(app)
api = Api(app)

class News(Resource):
    def get(self, page=1):
        newslist = scrap_news(page)
        return newslist

api.add_resource(News, '/news/<page>')

class Article(Resource):
    def get(self, hlink):
        url = ""
        try:
            log.debug("Try to resolve "+hlink)
            url = reverse_hash(hlink)
            log.debug("OK")
        except KeyError:
            log.info("Key not found")
            pass

        if url != "":
            log.info("Scrap URL "+url)
            return scrap_article(url)
        else:
            log.info("Try to load from disk.")
            return get_article_from_disk(hlink)

api.add_resource(Article, '/article/<hlink>')

class Home(Resource):
    def get(self, link=""):
        newslist = scrap_news(1)
        if (link != ""):
            url = link
        else:
            url = newslist[0]['link']

        return { "article": scrap_article(url), "newsList": newslist }

api.add_resource(Home, '/','/home/<hlink>')

#http://127.0.0.1:5002/news
if __name__ == '__main__':
     app.run(port='5001')