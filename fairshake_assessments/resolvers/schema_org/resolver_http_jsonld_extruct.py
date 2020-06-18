import extruct
from fairshake_assessments.core import resolver

@resolver({
  '@id': 'resolver:4',
  'name': 'url jsonld extruct jsonld resolver',
  'frame': {
    '@type': 'Thing',
    'text/html': {},
  }
})
def resolver_http_jsonld_extruct(node):
  for html in node['text/html']:
    try:
      yield dict(
        extruct.extract(html, uniform=True),
        **{
          '@id': node['@id'],
        },
      )
    except Exception as e:
      print(e)
      pass
