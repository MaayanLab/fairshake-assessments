import sys, pprint
from fairshake_assessments.core import assess_one
from fairshake_assessments.rubrics.rubric_data_citation import rubric_data_citation
from fairshake_assessments.utils.valid_url import valid_url

if len(sys.argv) != 2 or not valid_url(sys.argv[1]):
  print('Usage: {} [URL]'.format(sys.argv[0]))
  print('Example:')
  print('{} https://fairshake.cloud'.format(sys.argv[0]))
else:
  pprint.pprint(assess_one(rubric_data_citation, { '@type': 'Thing', 'url': sys.argv[1] }))
