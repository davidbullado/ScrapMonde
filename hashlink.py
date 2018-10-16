import hashlib

def hash_url(url):
    if (url.startswith( '/' )):
        url = 'https://www.lemonde.fr'+url
    m = hashlib.md5()
    m.update(url.encode())
    return m.hexdigest()