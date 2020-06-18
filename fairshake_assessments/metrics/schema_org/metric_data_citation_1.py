from fairshake_assessments.core import metric

@metric({
  '@id': 'datacitation:1',
  'description': 'Data Citation 1: [REQUIRED] All datasets intended for citation must have a globally unique persistent identifier that can be expressed as an unambiguous URL',
  'frame': {
    '@type': 'Thing',
    '**': {
      '@type': 'Dataset',
      'identifier': {}
    }
  }
})
def metric_data_citation_1(node):
  for dataset in node['**'][{'@type': 'Dataset'}]:
    for identifier in dataset['identifier']:
      yield {
        'answer': 0.5,
        'comment': 'Found identifier--cannot assert unambiguity',
        'evidence': str(identifier),
      }
