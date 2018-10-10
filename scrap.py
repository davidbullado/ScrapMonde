import sys
from getter import simple_get
from bs4 import BeautifulSoup
import json
from beautyprint import printerr
import urllib
from hashlib import md5
from time import strftime, gmtime
import dateparser

from functools import reduce

def digest_article(html):
    jsondata = html.find('script', type="application/ld+json")
    infos = {}

    if jsondata is not None:
        infos = json.loads(jsondata.text)
        infos["articleType"] = "article"
    else:
        infos["articleType"] = "?"
        head = html.head
        body = html.body
        infos["headline"] = head.find('meta', property="og:title").get("content")
        infos["description"] = head.find('meta', property="og:description").get("content")
        infos["image"] = {}
        infos["image"]["url"] = head.find('meta', property="og:image").get("content")
        dateinfo = body.find('span', class_="entry-date")
        infos['dateCreated'] = dateparser.parse(dateinfo.text + " " + dateinfo.parent.get('title'), languages=['fr']).isoformat()
        
    art = html.find(itemprop="articleBody")
    
    # if blog
    if art is None:
        art = html.find(class_="entry-content")
        if art is not None:
            infos["articleType"] = "blog"
            art.find("div", class_="wp-caption").extract()

    # if grand format
    if art is None:
        art = html.find(class_="article__content")
        if art is not None:
            infos["picture"] = str(html.picture)
            infos["articleType"] = "grandformat"
    if art is None:
        art = html.find("section", itemscope="")
        if art is not None:
            infos["articleType"] = "reportage"
            art = art.find("div",class_="description")
    if art is None:
        art = html.find("div",class_="global-live")
        if art is not None:
            infos["articleType"] = "live"
    if art is None:
        raise Exception ("Article not found.")

    # Remove extra tags
    extractTags = [ art.find_all('script'),  art.find_all('iframe'), art.find_all('figure')]
    for tagstoremove in extractTags:
        if tagstoremove is not None:
            for tag in tagstoremove:
                tag.extract()

    # Remove conjug tags
    for tag in art.find_all(True):
        if tag.name == "img":
            continue
        if tag.name not in ['a'] or ("class" in tag.attrs and 'conjug' in tag.attrs["class"]):
            tag.attrs = {}
    
    # Save article html
    infos["body"] = str(art)
    return infos

def scrap_article(url):
    print("scrap_article "+url)
    raw_html = simple_get(url)
    html = BeautifulSoup(raw_html, 'html.parser')  
    return digest_article(html)

def scrap_news(page=1):
    #filename = "cache/monde"+strftime("%y%j%H%M", gmtime())+"_"+str(page)+".html"
    filename = "cache/monde"+strftime("%y%j%H", gmtime())+"_"+str(page)+".html"
    try:
        f = open(filename,"r")
        raw_html = f.read()
    except IOError:
        raw_html = simple_get('https://www.lemonde.fr/actualite-en-continu/'+str(page)+'.html')
        f = open(filename,"w+")
        f.write(raw_html)
    except:
        print ("Unexpected error:", sys.exc_info()[0])
        raise

    if len(raw_html) == 0:
        raise Exception("No Data")

    html = BeautifulSoup(raw_html, 'html.parser')
    fleuve = html.find_all('div', class_='fleuve')[0]

    # ie exclude some categories
    exclusionList = ['ligue-1','football','athletisme','cyclisme']

    data = []
    idx = 0
    for article in fleuve.find_all("article"):
        try:
            link = article.h3.a.get('href')
            # if link in exclusionList, concat the current category in the result
            resexclude = reduce(lambda x,y: x+y if link.startswith('/'+y+'/') else x, exclusionList, "")
            if len(resexclude) > 0:
                continue
            jsart = {}
            [s.extract() for s in article('span')]
            jsart['id'] = idx
            jsart['datetime'] = article.time.get('datetime')
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
    print(scrap_news(1))
    #scrap_article('https://www.lemonde.fr/europe/article/2018/09/29/moscou-diffuse-une-nouvelle-photo-du-cineaste-en-greve-de-la-faim-oleg-sentsov_5362172_3214.html')
    #scrap_article('https://www.lemonde.fr/afrique/article/2018/10/05/comment-l-eswatini-a-mis-sous-controle-la-double-epidemie-sida-tuberculose_5365419_3212.html')