from fairshake_assessments.core import metric
from fairshake_assessments.utils.valid_url import valid_url

@metric({
  '@id': 'datacitation:3.1',
  'description': 'Data Citation 3.1: [REQUIRED] The persistent identifier expressed as an URL must resolve to a landing page specific for that dataset',
  'frame': {
    '@type': 'Thing',
    'url': {},
    '**': {
      '@type': 'Dataset',
      'identifier': {}
    }
  }
})
def metric_data_citation_3_1(node):
  for dataset in node['**'][{'@type': 'Dataset'}]:
    for identifier in dataset['identifier']:
      if valid_url(identifier):
        if identifier in node['url']:
          # our identifier was the same url we started with!
          yield {
            'answer': 1,
            'comment': 'Found identifier corresponding to the url',
            'evidence': str(identifier),
          }
        elif any(node[{ '@id': node['@id'], 'relatesTo': { '@type': 'Thing', 'relatesTo': { '@id': dataset['@id'] } } }]):
          # our identifier was associated with another "thing" that relates to our original dataset!
          yield {
            'answer': 1,
            'comment': 'Found identifier corresponding to the url',
            'evidence': str(identifier),
          }
        elif any(node[{ '@id': node['@id'], 'relatesTo': { '@type': 'Thing' } }]):
          # our identifier was associated with another "thing"
          yield {
            'answer': 0.75,
            'comment': 'Found identifier corresponding to a url--cannot assert landing page specificity',
            'evidence': str(identifier),
          }
        else:
          # our identifier didn't get associated with another "thing" -- shouldn't happen
          pass
      else:
        yield {
          'answer': 0.25,
          'comment': 'Identifier found but does not correspond to a resolvable url',
          'evidence': str(identifier),
        }
