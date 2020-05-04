import requests
from fairshake_assessments.core import metric
from fairshake_assessments.utils.jsonld_frame import jsonld_frame

@metric({
  '@id': 104,
  'name': 'DOI identifiers',
  'description': 'Globally unique, persistent, and valid DOI identifiers are present for the dataset',
  'principle': 'Findable',
})
def metric_104_doi(doc):
  dois = set(
    node['identifier']
    for node in jsonld_frame(doc, {
      '@type': ['Identifier', 'relatedIdentifier', 'alternateIdentifiers'],
      'description': ['doi', 'DOI'],
      'identifier': {}
    })['@graph']
    if node['identifier'] and node['description']
  )
  if dois:
    for doi in dois:
      try:
        urllib.request.urlopen(doi if doi.startswith('http') else 'https://doi.org/{}'.format(doi))
        yield {
          'value': 1,
          'comment': 'DOI {} was identified and verified'.format(
            doi
          )
        }
      except urllib.error.HTTPError:
        yield {
          'value': 0.25,
          'comment': 'DOI {} was identified but could not be verified'.format(
            doi
          )
        }
  else:
    yield {
      'value': 0,
      'comment': 'No DOIs could be identified',
    }
