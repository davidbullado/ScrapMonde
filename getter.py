from requests import get, head
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import email.utils as eut
from datetime import datetime
import sys
import hashlib
from os import utime, path
from time import mktime, struct_time

hasher = hashlib.md5()
with open('scrap.py', 'rb') as scrap_src:
    buf = scrap_src.read()
    hasher.update(buf)
    hashsources = hasher.digest()

def my_parsedate(text):
    my_dt = datetime(*eut.parsedate(text)[:6])
    ostime = my_dt.timetuple()
    inttime = mktime(ostime)
    
    return inttime

def my_filename(url):
    m = hashlib.md5()
    m.update(url.encode())
    m.update(hashsources)
    return m.hexdigest()

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    filename = "cache/"+my_filename(url)

    if path.isfile(filename):
        content_mt = my_parsedate(head(url).headers["Last-Modified"])
        if (content_mt == path.getmtime(filename)):
            f = open(filename,"r")
            return f.read()

    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                lastmodified = my_parsedate(resp.headers["Last-Modified"])
                f = open(filename,"w+")
                f.write(resp.text)
                utime(filename, (lastmodified,lastmodified))
                return resp.text
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)