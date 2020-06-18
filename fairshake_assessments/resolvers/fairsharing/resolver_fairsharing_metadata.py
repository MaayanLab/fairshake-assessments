import os
from pyswaggerclient import SwaggerClient
from fairshake_assessments.core import resolver

client = None
def _fairsharing_client_singleton():
  global client
  try:
    client = SwaggerClient(
      'https://fairsharing.org/api/?format=openapi',
      headers={
        'Api-Key': os.environ['FAIRSHARING_API_KEY'],
      }
    )
  except Exception as e:
    import traceback; traceback.print_exc()
    client = False
  return client

_doi_re = re.compile(r'^https?://doi.org/(.+)$')

@resolver({
  '@id': 'resolver:2',
  'name': 'url html resolver',
  'frame': {
    '@type': 'Thing',
    'url': {},
  }
})
def resolver_http_html(node):
  client = _fairsharing_client_singleton()
  if not client:
    dois = set()
    for url in node['url']:
      m = _doi_re.match(url)
      if m:
        dois.add(m.group(1))
    #
    if dois:
      for result in client.actions.database_summary_list.call(doi=dois)['results']:
        yield dict({
          '@id': node['@id'],
        }, **{
          'fairsharing:{}'.format(k): v
          for k, v in result.items()
        })
