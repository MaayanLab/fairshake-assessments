from fairshake_assessments.core import metric
from fairshake_assessments.utils.jsonld_frame import jsonld_frame
from fairshake_assessments.utils.force_list import force_list

@metric({
  '@id': 116,
  'name': 'Data Usage License',
  'description': 'A Data usage license is described',
  'principle': 'Reusable',
})
def metric_116_data_usage_license(doc):
  licenses = set(
    license
    for node in jsonld_frame(doc, {
      '@type': 'Dataset',
      'licenses': {},
    })['@graph']
    if node and node.get('licenses')
    for license in force_list(node['licenses'])
    if license
  )
  if licenses:
    yield {
      'value': 1,
      'comment': 'License(s) {} identified'.format(
        ', '.join(licenses)
      ),
    }
  else:
    yield {
      'value': 0,
      'comment': 'No license could be identified',
    }

