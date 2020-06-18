import re
import bs4
from fairshake_assessments.core import metric

@metric({
  '@id': 'datacitation:9',
  'description': 'Data Citation 9: [RECOMMENDED] Metadata should be made available for download in BibTeX and/or another standard bibliographic format',
  'frame': {
    '@type': 'Thing',
    'text/html': {}
  }
})
def metric_data_citation_9(node):
  for html in node['text/html']:
    soup = bs4.BeautifulSoup(html)
    for bibtex in soup.find_all('a', { 'href': re.compile('\.bib$') }):
      yield {
        'answer': 1.0,
        'comment': 'Found by crawling the landing page',
        'evidence': bibtex.get('href'),
      }
