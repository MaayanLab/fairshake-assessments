import bs4
from fairshake_assessments.core import resolver
from fairshake_assessments.utils.filter_none import filter_none
from fairshake_assessments.utils.first_or import first_or

@resolver({
  '@id': 'resolver:6',
  'name': 'meta resolver',
  'frame': {
    '@type': 'Thing',
    'text/html': {},
  }
})
def resolver_http_html_meta(node):
  for html in node['text/html']:
    try:
      soup = bs4.BeautifulSoup(html)
      title = first_or(soup.select('title'), {}).get('text')
      description = first_or(soup.select('meta[name="description"]'), {}).get('content')
      keywords = first_or(soup.select('meta[name="keywords"]'), {}).get('content')
      image = first_or(soup.select('meta[itemprop="image"]'), {}).get('content')
      if image is None:
        image = first_or(soup.select('link[rel="shortcut icon"]'), {}).get('href')
      #
      yield {
        '@id': node['@id'],
        'website': filter_none({
          '@type': 'WebPage',
          'url': list(node['url']),
          'title': title,
          'description': description,
          'keywords': keywords,
          'image': image,
        })
      }
    except:
      pass
