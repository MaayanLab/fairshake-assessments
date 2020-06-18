import re
import bs4
from fairshake_assessments.core import metric

@metric({
  '@id': 'datacitation:11',
  'description': 'Data Citation 11: [OPTIONAL] HTTP link headers may be supported to advertise content negotation options',
  'frame': {
    '@type': 'Thing',
    'OPTIONS': {},
  }
})
def metric_data_citation_11(node):
  yield {
    'answer': 1.0,
    'comment': 'OPTIONS are available',
    'evidence': str(node['OPTIONS']),
  }
