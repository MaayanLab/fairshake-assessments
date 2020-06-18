from fairshake_assessments.core import metric

@metric({
  '@id': 'datacitation:7',
  'description': 'Data Citation 7: [RECOMMENDED] The machine-readable metadata should use schema.org markup in JSON-LD format',
  'frame': {
    '@type': 'Thing',
    '**': {
      '@context': {}
    }
  }
})
def metric_data_citation_7(node):
  yield {
    'answer': 1.0 if 'http://schema.org' in node['**']['@context'] else 0.0,
    'comment': 'Extracted from the landing page',
    'evidence': str(node['**']['@context']),
  }
