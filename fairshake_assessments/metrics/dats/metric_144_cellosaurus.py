import json
import xml.etree.ElementTree
import urllib.request
from fairshake_assessments.core import metric
from fairshake_assessments.utils.jsonld_frame import jsonld_frame
from fairshake_assessments.utils.force_list import force_list
from fairshake_assessments.utils.IRI_to_NS import IRI_to_NS


# Cellosaurus does not distribute owl -- nonetheless we can parse the XML
#  and create the same structure as pronto
Cellosaurus_xml = xml.etree.ElementTree.parse(
  urllib.request.urlopen('ftp://ftp.expasy.org/databases/cellosaurus/cellosaurus.xml')
).getroot()
Cellosaurus = {
  accession.text.replace('_', ':'): {
    'id': accession.text.replace('_', ':'),
    'name': cell_line.find('name-list').find("name[@type='identifier']").text,
    'synonyms': set([
      synonym.text
      for synonym in cell_line.find('name-list').iterfind("name[@type='synonym']")
    ])
  }
  for cell_line in Cellosaurus_xml.find('cell-line-list').iterfind('cell-line')
  for accession in cell_line.find('accession-list').iterfind('accession')
}
Cellosaurus_reversed = { node['name']: node['id'] for node in Cellosaurus.values() }
Cellosaurus_reversed_synonyms = { synonym: node['id'] for node in Cellosaurus.values() for synonym in node['synonyms'] }

@metric({
  '@id': 144,
  'name': 'Cell Line',
  'description': 'A cell line is present with a valid Cellosaurus identifier',
  'principle': 'Interoperable',
})
def metric_144_cellosaurus(doc):
  cell_lines = list(map(json.loads,set(
    json.dumps({
      'value': isAbout['name'],
      'valueIRI': isAbout.get('identifier', {}).get('identifierSource', '') + isAbout.get('identifier', {}).get('identifier', '')
    })
    for node in jsonld_frame(doc, {
      '@type': 'Dataset',
      'isAbout': {
        '@type': 'BiologicalEntity',
        'name': {},
        'identifier': {
          'identifier': {},
          'identifierSource': { '@default': '' },
        }
      }
    })['@graph']
    if node['isAbout']
    for isAbout in force_list(node['isAbout'])
    if isAbout['name']
  )))
  if cell_lines:
    for cell_line in cell_lines:
      value_ns = IRI_to_NS(cell_line.get('valueIRI'))
      if cell_line.get('value') and cell_line.get('valueIRI') and Cellosaurus.get(value_ns, {}).get('name') == cell_line['value']:
        yield {
          'value': 1,
          'comment': 'Ontological IRI for cell line {} and term match what is found in Cellosaurus.'.format(
            value_ns
          ),
        }
      elif cell_line.get('valueIRI') and value_ns in Cellosaurus:
        yield {
          'value': 0.75,
          'comment': 'Ontological IRI for cell line {} found in Cellosaurus.'.format(
            value_ns
          ),
        }
      elif cell_line.get('value') and value_ns in Cellosaurus_reversed:
        yield {
          'value': 0.75,
          'comment': 'Cell line `{}` found in Cellosaurus.'.format(
            cell_line['value']
          ),
        }
      elif cell_line.get('value') and cell_line['value'] in Cellosaurus_reversed_synonyms:
        yield {
          'value': 0.5,
          'comment': 'Cell line `{}` found in Cellosaurus synonyms.'.format(
            cell_line['value']
          ),
        }
      else:
        yield {
          'value': 0.25,
          'comment': 'Cell line `{}` found but not in Cellosaurus.'.format(
            cell_line.get('value', '') + (('<' + value_ns + '>') if value_ns else '')
          ),
        }
  else:
    yield {
      'value': 0.0,
      'comment': 'Cell line could not be identified',
    }
