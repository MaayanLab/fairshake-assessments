from fairshake_assessments.core import metric

@metric({
  '@id': 'datacitation:3.2',
  'description': 'Data Citation 3.2: [REQUIRED] That landing page must contain metadata describing the dataset',
  'frame': {
    '@type': 'Thing',
    '**': {
      '@type': 'Dataset'
    }
  }
})
def metric_data_citation_3_2(node):
  yield {
    'answer': 1.0,
    'comment': 'Metadata describing the Dataset was found given the landing page',
    'evidence': str(node['**'][{ '@type': 'Dataset' }])
  }
