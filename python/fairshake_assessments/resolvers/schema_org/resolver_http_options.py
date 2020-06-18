import requests
from fairshake_assessments.core import resolver

@resolver({
  '@id': 'resolver:1',
  'name': 'url OPTIONS resolver',
  'frame': {
    '@type': 'Thing',
    'url': {},
  }
})
def resolver_http_options(node):
  for url in node['url']:
    try:
      yield {
        '@id': node['@id'],
        'OPTIONS': requests.options(url).json(),
      }
    except:
      pass
