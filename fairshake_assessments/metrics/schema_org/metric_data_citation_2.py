from fairshake_assessments.core import metric

@metric({
  '@id': 'datacitation:2',
  'description': 'Data Citation 2: [REQUIRED] Persistent identifiers for datasets must support multiple levels of granularity, where appropriate',
  'frame': {
    '@type': 'Thing',
    '**': {
      '@type': 'Dataset',
      'identifier': {}
    }
  }
})
def metric_data_citation_2(node):
  for dataset in node['**'][{'@type': 'Dataset'}]:
    for identifier in dataset['identifier']:
      yield {
        'answer': 0.5,
        'comment': 'Found identifier--cannot assert levels of granularity',
        'evidence': str(identifier),
      }
