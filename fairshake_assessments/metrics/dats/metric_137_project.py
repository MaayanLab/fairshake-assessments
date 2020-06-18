from fairshake_assessments.core import metric
from fairshake_assessments.utils.jsonld_frame import jsonld_frame
from fairshake_assessments.utils.force_list import force_list


@metric({
  '@id': 137,
  'name': 'Project name',
  'description': 'Project name is available for querying',
  'principle': 'Findable',
})
def metric_137_project(doc):
  projects = set(
    storedIn['name']
    for node in jsonld_frame(doc, {
      '@type': 'Dataset',
      'storedIn': {
        '@type': 'DataRepository',
        'name': {}
      }
    })['@graph']
    if node['storedIn']
    for storedIn in force_list(node['storedIn'])
    if storedIn['name']
  )
  if projects:
    yield {
      'value': 1,
      'comment': 'Identified project(s): {}'.format(
        ', '.join(projects)
      ),
    }
  else:
    yield {
      'value': 0,
      'comment': 'Could not identify any projects',
    }
