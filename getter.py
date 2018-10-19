from requests import get, head
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import email.utils as eut
from datetime import datetime
import sys
from os import utime, path
from calendar import timegm
from time import mktime, struct_time, gmtime
from hashlink import hash_url, is_hash
from logger import log

def my_parsedate(text):
    my_dt = datetime(*eut.parsedate(text)[:6])
    ostime = my_dt.timetuple()
    inttime = mktime(ostime)
    
    return inttime

def load_from_cache(hashed_url):

    if not is_hash(hashed_url):
        raise ValueError("Not a valid hash")

    filename = "cache/"+hashed_url
    
    f = open(filename,"r")
    return f.read()

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    filename = "cache/"+hash_url(url)

    remote_mt = 0
    try:
        remote_mt = my_parsedate(head(url).headers["Last-Modified"])
        log.debug('HTTP Last-Modified: '+str(remote_mt))
    except KeyError:
        log.warning('No Last-Modified header for '+url)
        pass
    
    try:
        file_mt = path.getmtime(filename)
        log.debug('File last modified: '+str(file_mt))
        
        isCacheValid = False
        if remote_mt == 0:
            default_mt = timegm(gmtime()) - 15 * 60
            isCacheValid = default_mt <= file_mt
            log.warning('Default last modified: '+str(default_mt))
        elif remote_mt == file_mt:
            isCacheValid = True

        if isCacheValid:
            f = open(filename,"r")
            return f.read()
    except FileNotFoundError:
        log.debug('No candidate for '+filename)

    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                f = open(filename,"w+")
                f.write(resp.text)
                if remote_mt > 0:
                    utime(filename, (remote_mt,remote_mt))
                    log.debug('set last modified: '+str(remote_mt))
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