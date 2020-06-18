from fairshake_assessments.core import metric

@metric({
  '@id': 'datacitation:8',
  'description': 'Data Citation 8: [RECOMMENDED] Metadata should be made available via HTML meta tags to facilitate use by reference managers',
  'frame': {
    '@type': 'Thing',
    '**': {
      '@type': 'WebSite',
    }
  }
})
def metric_data_citation_8(node):
  yield {
    'answer': 1.0,
    'comment': 'Constructed from the landing page meta tags',
    'evidence': str(node['**'][{'@type': 'WebSite'}]),
  }
