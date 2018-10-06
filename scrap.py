import sys
from getter import simple_get
from bs4 import BeautifulSoup
import json
from beautyprint import printerr
import urllib
from hashlib import md5
from time import strftime, gmtime

def digest_article(html):
    try:
        infos = json.loads(html.find('script', type="application/ld+json").text)
    except:
        head = html.head
        infos.headline = head.find('meta', property="og:title")
    art = html.find(itemprop="articleBody")
    try:
        art.img.extract()
    except:
        pass
    try:
        art.script.extract()
    except:
        pass
    try:
        art.find_all('a', class_="conjug").extract()
    except:
        pass
    try:
        art.find_all('iframe').extract()
    except:
        pass
    for tag in art.find_all(True):
        if tag.name not in ['a'] or ("class" in tag.attrs and 'conjug' in tag.attrs["class"]):
            tag.attrs = {}
    
    infos['body'] = str(art)

    return infos

def scrap_article(url):
    print("scrap_article "+url)
    raw_html = simple_get(url)
    html = BeautifulSoup(raw_html, 'html.parser')  
    return digest_article(html)

def scrap_news(page=1):
    filename = "cache/monde"+strftime("%y%j%H%M", gmtime())+".html"
    try:
        f = open(filename,"r")
        raw_html = f.read()
    except IOError:
        raw_html = simple_get('https://www.lemonde.fr/actualite-en-continu/1.html')
        f = open(filename,"w+")
        f.write(raw_html)
    except:
        print ("Unexpected error:", sys.exc_info()[0])
        raise

    if len(raw_html) == 0:
        raise Exception("No Data")

    html = BeautifulSoup(raw_html, 'html.parser')
    fleuve = html.find_all('div', class_='fleuve')[0]

    data = []
    idx = 0
    for article in fleuve.find_all("article"):
        try:
            jsart = {}
            [s.extract() for s in article('span')]
            jsart['id'] = idx
            jsart['datetime'] = article.time.get('datetime')
            link = article.h3.a.get('href')
            if (link.startswith( '/' )):
                jsart['link'] = 'https://www.lemonde.fr'+link
            else:
                jsart['link'] = link
            jsart['title'] = article.h3.a.text.strip()
            jsart['summary'] = article.find_all('p', class_='txt3')[0].text
            
            hasher = md5()
            hasher.update(jsart['link'].encode())
            jsart['hlink'] = hasher.hexdigest()

            data.append(jsart)
            idx = idx + 1

        except AttributeError as e: # More than just a title
            print(e)
            for elements in article.h3.a:
                printerr (type(elements), elements)
    return data


if __name__ == "__main__":
    #scrap_article('https://www.lemonde.fr/europe/article/2018/09/29/moscou-diffuse-une-nouvelle-photo-du-cineaste-en-greve-de-la-faim-oleg-sentsov_5362172_3214.html')
    scrap_article('https://www.lemonde.fr/afrique/article/2018/10/05/comment-l-eswatini-a-mis-sous-controle-la-double-epidemie-sida-tuberculose_5365419_3212.html')