import sys
from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
from scrap import scrap_news, scrap_article

app = Flask(__name__)
CORS(app)
api = Api(app)

urlList = {}

class News(Resource):
    def get(self, page=1):
        newslist = scrap_news(page)
        for news in newslist:
            urlList[news['hlink']] = news['link']
            del news['link']
        return newslist

api.add_resource(News, '/news/<page>')

class Article(Resource):
    def get(self, hlink):
        try:
            url = urlList[hlink]
            return scrap_article(url)
        except KeyError:
            print(sys.exc_info()[0])
            return {'body': 'Please Reload'}

api.add_resource(Article, '/article/<hlink>')

class Home(Resource):
    def get(self, hlink=""):
        newslist = scrap_news(1)
        url = urlList[hlink]
        if url is None: 
            url = newslist[0]['link']
        for news in newslist:
            urlList[news['hlink']] = news['link']
            del news['link']
        return { "article": scrap_article(url), "newsList": newslist }

api.add_resource(Home, '/home/<hlink>')

#http://127.0.0.1:5002/news
if __name__ == '__main__':
     app.run(port='5001')