import requests
from pyld import jsonld
from fairshake_assessments.core import resolver

@resolver({
  '@id': 'resolver:3',
  'name': 'url jsonld content-negotation resolver',
  'frame': {
    '@type': 'Thing',
    'OPTIONS': {},
    'url': {},
  }
})
def resolver_http_jsonld_content_negotation(node):
  if 'application/ld+json' in node['OPTIONS']['renders']:
    try:
      yield {
        '@id': node['@id'],
        'application/ld+json': jsonld.compact(
          requests.get(node['url'], headers={'Content-Type': 'application/ld+json'}).json(),
          { '@context': { '@vocab': 'http://schema.org' } }
        )
      }
    except:
      pass
