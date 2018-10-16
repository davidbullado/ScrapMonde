import sys
from getter import simple_get
from bs4 import BeautifulSoup
import json
from logger import log
import urllib
from time import strftime, gmtime
import dateparser
from hashlink import hash_url
from functools import reduce
from getter import load_from_cache

def digest_article(html):
    jsondata = html.find('script', type="application/ld+json")
    infos = {}

    try:
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
                try:
                    art.find("div", class_="wp-caption").extract()
                except:
                    pass

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

        for tag in art.find_all('p'):
            if tag.contents == '':
                tag.extract()

        # Remove conjug tags
        for tag in art.find_all('a', class_='lien_interne conjug'):
            tag.replaceWithChildren()

        for tag in art.find_all('a'):
            if 'href' not in tag.attrs:
                tag.replaceWithChildren()
            else:
                # internal link
                if tag.attrs['href'].startswith('/'):
                    tag.attrs['href'] = "/#/article/" + hash_url(tag.attrs['href'])
                else:
                    # external link, add targer=_blank
                    tag.attrs['target'] = "_blank"
                    tag.attrs['rel'] = "nofollow noreferrer noopener"
        
        for tag in art.find_all(True):
            if tag.name == "img":
                continue
            """
            if tag.name == "a" and ("class" in tag.attrs and "conjug" in tag.attrs["class"]):
                tag.name = "span"
                tag.attrs = {}
            else:
                tag.attrs = {}
            """
    except Exception as e:
        log.error("Not able to parse the article")

    # Save article html
    infos["body"] = str(art)
    return infos

def get_article_from_disk(hlink):
    raw_html = ""
    try:
        raw_html = load_from_cache(hlink)
    except:
        log.warning("No article found on disk !")
        return {'body': 'Please Reload'}
    html = BeautifulSoup(raw_html, 'html.parser')
    return digest_article(html)

def scrap_article(url):
    raw_html = simple_get(url)

    html = BeautifulSoup(raw_html, 'html.parser')
    return digest_article(html)

def is_link_excluded(link):
    exclusionList = ['ligue-1','football','athletisme','cyclisme', 'live']
    for tag in exclusionList:
        if '/'+tag+'/' in link:
            log.debug('Exclude link '+link)
            return True
    else:
        return False

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

    data = []
    idx = 0
    for article in fleuve.find_all("article"):
        link = article.h3.a.get('href')
        if link is None:
            log.error("Unable to retreive the link for: "+str(article))
            continue
        try:
            if is_link_excluded(link):
                continue
            jsart = {}
            jsart['id'] = idx
            if (link.startswith( '/' )):
                jsart['link'] = 'https://www.lemonde.fr'+link
            else:
                jsart['link'] = link
            jsart['hlink'] = hash_url(link)
            jsart['title'] = article.h3.a.text.strip()
            jsart['datetime'] = article.time.get('datetime')
            # remove img
            [s.extract() for s in article('span')]
            jsart['summary'] = article.find_all('p', class_='txt3')[0].text
            data.append(jsart)
            idx = idx + 1

        except AttributeError as e: # More than just a title
            log.error(e)

    return data
