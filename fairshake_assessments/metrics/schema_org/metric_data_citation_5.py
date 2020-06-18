from fairshake_assessments.core import metric

@metric({
  '@id': 'datacitation:5',
  'description': 'Data Citation 5: [REQUIRED] The repository must provide documentation and support for data citation.',
  'frame': {
    '@type': 'Thing',
    '**': {
      '@type': 'DataRepository',
      'citation': {},
    }
  }
})
def metric_data_citation_5(node):
  yield {
    'answer': 1.0,
    'comment': 'Citation found in repository metadata',
    'evidence': str(node['**']['citation'])
  }
