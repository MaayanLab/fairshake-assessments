import time
import requests
from selenium import webdriver
from fairshake_assessments.core import resolver

driver = None
def webdriver_singleton():
  global driver
  if driver is None:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)
  return driver

@resolver({
  '@id': 'resolver:2',
  'name': 'url html resolver',
  'frame': {
    '@type': 'Thing',
    'url': {},
  }
})
def resolver_http_html(node):
  for url in node['url']:
    try:
      d = webdriver_singleton()
      d.get(url)
      time.sleep(1)
      yield {
        '@id': node['@id'],
        'text/html': d.page_source
      }
    except:
      pass
