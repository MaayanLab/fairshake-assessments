import requests
from fairshake_assessments.core import metric
from fairshake_assessments.utils.jsonld_frame import jsonld_frame

@metric({
  '@id': 108,
  'name': 'Resource identifier',
  'description': 'An identifier for the resource is present',
  'principle': 'Findable',
})
def metric_108_resource_identifier(doc):
  identifiers = set(
    node['identifier'].get('identifierSource', '') + node['identifier']['identifier']
    for node in jsonld_frame(doc, {
      '@type': 'Dataset',
      'identifier': {
        'identifier': {},
        'identifierSource': { '@default': '' },
      }
    })['@graph']
    if node['identifier'] and node['identifier']['identifier']
  )
  if identifiers:
    for identifier in identifiers:
      if '://' in identifier and requests.get(identifier).status_code < 400:
        yield {
          'value': 1,
          'comment': 'Resource identifier {} was identified and verified'.format(
            identifier
          )
        }
      else:
        yield {
          'value': 0.75,
          'comment': 'Resource identifier {} was identified but could not be verified'.format(
            identifier
          )
        }
  else:
    yield {
      'value': 0,
      'comment': 'No resource identifier was found',
    }
