from fairshake_assessments.core import metric

@metric({
  '@id': 'datacitation:6.2',
  'description': 'Data Citation 6.2: [RECOMMENDED] Ideally also metadata facilitating discovery, in human-readable and machine-readable format.',
  'frame': {
    '@type': 'Thing',
    'url': {}
  }
})
def metric_data_citation_6_2(node):
  answer, comment = {
    (True, True, True): (1, 'human-readable & machine-readable (json & jsonld)'),
    (True, True, False): (0.75, 'human-readable & machine-readable (json)'),
    (True, False, True): (1, 'human-readable & machine-readable (jsonld)'),
    (True, False, False): (0.25, 'human-readable, not machine-readable'),
    (False, True, True): (0.5, 'machine-readable, not human-readable (json & jsonld)'),
    (False, True, False): (0.25, 'machine-readable, not human-readable (json)'),
    (False, False, True): (0.5, 'machine-readable, not human-readable (jsonld)'),
    (False, False, False): (0, 'neither human-readable nor machine-readable'),
  }.get(
    (any(node['text/html']), any(node['application/json']), any(node['application/ld+json']))
  )
  yield {
    'answer': answer,
    'comment': comment,
    'evidence': None,
  }
