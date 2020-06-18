import json
from fairshake_assessments.core import metric
from fairshake_assessments.utils.jsonld_frame import jsonld_frame
from fairshake_assessments.utils.force_list import force_list


@metric({
  '@id': 138,
  'name': 'Responsible institution',
  'description': 'The institution that created this dataset is available',
  'principle': 'Findable',
})
def metric_138_institution(doc):
  institutions = set(
    creators['name']
    for node in jsonld_frame(doc, {
      '@type': 'Dataset',
      'creators': {
        '@type': 'Organization',
        'name': {},
      }
    })['@graph']
    if node['creators']
    for creators in force_list(node['creators'])
    if creators['name']
  )
  affiliated_institutions = list(map(json.loads,set(
    json.dumps({
      'person': creators['fullName'],
      'organization': affiliations['name']
    })
    for node in jsonld_frame(doc, {
      '@type': 'Dataset',
      'creators': {
        '@type': 'Person',
        'fullName': {},
        'affiliations': {
          '@type': 'Organization',
          'name': {}
        }
      }
    })['@graph']
    if node['creators']
    for creators in force_list(node['creators'])
    if creators['fullName'] and creators['affiliations']
    for affiliations in force_list(creators['affiliations'])
    if affiliations['name']
  )))
  if institutions:
    yield {
      'value': 1,
      'comment': 'Found institution(s): {}'.format(
        ', '.join(institutions),
      ),
    }
  elif affiliated_institutions:
    yield {
      'value': 0.75,
      'comment': 'Found affiliated institution(s): {}'.format(
        ', '.join('{} <{}>'.format(person['person'], person['organization']) for person in affiliated_institutions),
      ),
    }
  else:
    yield {
      'value': 0,
      'comment': 'No institution was identified',
    }
