import re
import bs4
from fairshake_assessments.core import metric

@metric({
  '@id': 'datacitation:10',
  'description': 'Data Citation 10: [OPTIONAL] Content negotation for schema.org/JSON-LD and other content types may be supported so that the persistent identifier expressed as URL resolves directly to machine-readable metadata',
  'frame': {
    '@type': 'Thing',
    'OPTIONS': {},
  }
})
def metric_data_citation_10(node):
  for options in node['OPTIONS']:
    if 'application/ld+json' in options['renders']:
      yield {
        'answer': 1.0,
        'comment': 'Content negotiation supports JSON-LD',
        'evidence': str(options),
      }
    elif 'application/json' in options['renders']:
      yield {
        'answer': 0.75,
        'comment': 'Content negotiation supports JSON but not JSON-LD',
        'evidence': str(options),
      }
    else:
      yield {
        'answer': 0.25,
        'comment': 'Content negotiation does not support JSON or JSONLD',
        'evidence': str(options),
      }
