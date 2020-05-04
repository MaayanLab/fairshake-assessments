from fairshake_assessments.core import metric
from fairshake_assessments.utils.jsonld_frame import jsonld_frame
from fairshake_assessments.utils.force_list import force_list


@metric({
  '@id': 136,
  'name': 'Program name',
  'description': 'Program name is available for querying',
  'principle': 'Findable',
})
def metric_136_program(doc):
  programs = set(
    node['program']['name']
    for node in jsonld_frame(doc, {
      '@type': 'Dataset',
      'program': {
        'name': {}
      }
    })['@graph']
    if node['program']
    for program in force_list(node['program'])
    if program['name']
  )
  if programs:
    yield {
      'value': 1,
      'comment': 'Identified program(s): {}'.format(
        ', '.join(programs)
      )
    }
  else:
    yield {
      'value': 0,
      'comment': 'Could not identify any programs',
    }
