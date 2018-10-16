import hashlib
import re
from logger import log

urlList = {}

def hash_url(url):
    if (url.startswith( '/' )):
        url = 'https://www.lemonde.fr'+url
    m = hashlib.md5()
    m.update(url.encode())
    hash = m.hexdigest()
    urlList[hash] = url
    return hash

def reverse_hash(hash):
    if not is_hash(hash):
        raise ValueError("Hash must be 32 chars")
    if hash in urlList:
        return urlList[hash]
    raise KeyError

def is_hash(hash):
    matchMD5 = re.match( r'[a-z0-9]{32}', hash, re.I)
    if not matchMD5:
        log.warning("This is not an hash: "+hash)
        return False
    else:
        return True