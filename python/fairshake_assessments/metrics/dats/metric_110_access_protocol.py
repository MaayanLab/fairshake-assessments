from fairshake_assessments.core import metric
from fairshake_assessments.utils.jsonld_frame import jsonld_frame
from fairshake_assessments.utils.force_list import force_list


@metric({
  '@id': 110,
  'name': 'Access protocol',
  'description': 'The protocol for accessing the data is available and described with a URI',
  'principle': 'Accessible',
})
def metric_110_access_protocol(doc):
  access_protocols = set(
    access['accessURL']
    for node in jsonld_frame(doc, {
      '@type': 'DatasetDistribution',
      'access': {
        'accessURL': {},
      }
    })['@graph']
    if node['access']
    for access in force_list(node['access'])
    if access['accessURL']
  )
  if access_protocols:
    yield {
      'value': 1,
      'comment': 'Access protocol(s) found: {}'.format(', '.join(access_protocols))
    }
  else:
    yield {
      'value': 0,
      'comment': 'Could not identify any access protocols'
    }
