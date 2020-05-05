import json
from fairshake_assessments.core import metric
from fairshake_assessments.utils.jsonld_frame import jsonld_frame
from fairshake_assessments.utils.force_list import force_list


@metric({
  '@id': 27,
  'name': 'PI Contact',
  'description': 'PI Contact is available for dataset',
  'principle': 'Reusable',
})
def metric_27_contact_pi(doc):
  people = list(map(json.loads, set(
    json.dumps({
      'fullName': creators['fullName'],
      'roles': creators.get('roles', []),
    })
    for node in jsonld_frame(doc, {
      '@type': 'Dataset',
      'creators': {
        '@type': 'Person',
        'fullName': {},
        'roles': {
          '@default': []
        },
      }
    })['@graph']
    if node['creators']
    for creators in force_list(node['creators'])
    if creators['fullName']
  )))
  PIs = [
    person
    for person in people
    if 'Principal Investigator' in person['roles']
  ]
  if PIs:
    yield {
      'value': 1,
      'comment': 'Found PI(s): {}'.format(
        ', '.join([person['fullName'] for person in PIs])
      ),
    }
  elif people:
    yield {
      'value': 0.5,
      'comment': 'Found {}, but cannot determine a PI'.format(
        [
          person['fullName'] + ('(' + ', '.join(person['roles']) + ')') if person['roles'] else '' 
          for person in people
        ]
      ),
    }
  else:
    yield {
      'value': 0,
      'comment': 'No PI or people could be identified'
    }
