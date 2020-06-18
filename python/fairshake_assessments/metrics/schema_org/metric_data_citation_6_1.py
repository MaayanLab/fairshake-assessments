from fairshake_assessments.core import metric

@metric({
  '@id': 'datacitation:6.1',
  'description': 'Data Citation 6.1: [RECOMMENDED] The landing page should include metadata required for citation.',
  'frame': {
    '@type': 'Thing',
    'text/html': {},
    '**': {
      '@type': 'Dataset',
      'citation': {},
    }
  }
})
def metric_data_citation_6_1(node):
  yield {
    'answer': 1.0,
    'comment': 'Citation found in dataset metadata',
    'evidence': str(node['**']['citation']),
  }
