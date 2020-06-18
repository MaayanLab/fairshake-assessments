from fairshake_assessments.core import metric

@metric({
  '@id': 'datacitation:4',
  'description': 'Data Citation 4: [REQUIRED] The persistent identifier must be embedded in the landing page in machine-readable format',
  'frame': {
    '@type': 'Thing',
    '**': {
      '@type': 'Dataset',
      'identifier': {}
    }
  }
})
def metric_data_citation_4(node):
  for identifier in node['identifier']:
    yield {
      'answer': 0.75,
      'comment': 'Identifier found in Dataset metadata -- a persistence determination could not be automated',
      'evidence': str(identifier),
    }
