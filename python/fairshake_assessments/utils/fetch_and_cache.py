import os
import urllib.request

def fetch_and_cache(url, file):
  if not os.path.exists(file):
    os.makedirs(os.path.dirname(file), exist_ok=True)
    urllib.request.urlretrieve(url, file)
  return file
