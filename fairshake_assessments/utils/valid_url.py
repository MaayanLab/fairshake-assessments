import urllib.parse

def valid_url(url):
  try:
    urllib.parse.urlparse(url)
    return True
  except:
    return False
