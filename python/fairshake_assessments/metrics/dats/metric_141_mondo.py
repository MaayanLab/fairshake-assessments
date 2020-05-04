import json
import pronto
from fairshake_assessments.core import metric
from fairshake_assessments.utils.jsonld_frame import jsonld_frame
from fairshake_assessments.utils.force_list import force_list
from fairshake_assessments.utils.IRI_to_NS import IRI_to_NS


MONDO = pronto.Ontology('http://purl.obolibrary.org/obo/mondo.obo')
MONDO_reversed = { node.name: node.id for node in MONDO }
MONDO_reversed_synonyms = { synonym: node.id for node in MONDO for synonym in node.synonyms }

@metric({
  '@id': 141,
  'name': 'Disease',
  'description': 'A disease is present with a valid MONDO identifier',
  'principle': 'Interoperable',
})
def metric_141_mondo(doc):
  diseases = list(map(json.loads,set(
    json.dumps({
      'value': isAbout['name'],
      'valueIRI': (isAbout['identifier'].get('identifierSource', '') + isAbout['identifier'].get('identifier', '')) if isAbout['identifier'] else ''
    })
    for node in jsonld_frame(doc, {
      '@type': 'Dataset',
      'isAbout': {
        '@type': 'Disease',
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
  if diseases:
    for disease in diseases:
      value_ns = IRI_to_NS(disease.get('valueIRI'))
      if disease.get('value') and disease.get('valueIRI') and pronto.Term(value_ns, disease['value']) in MONDO:
        yield {
          'value': 1,
          'comment': 'Ontological IRI for disease {} and term match what is found in MONDO.'.format(
            value_ns
          ),
        }
      elif disease.get('valueIRI') and disease['valueIRI'] in MONDO:
        yield {
          'value': 0.75,
          'comment': 'Ontological IRI for disease {} found in MONDO.'.format(
            value_ns
          ),
        }
      elif disease.get('value') and disease['value'] in MONDO_reversed:
        yield {
          'value': 0.75,
          'comment': 'Disease `{}` found in MONDO.'.format(
            disease['value']
          ),
        }
      elif disease.get('value') and disease['value'] in MONDO_reversed_synonyms:
        yield {
          'value': 0.5,
          'comment': 'Disease `{}` found in MONDO synonyms.'.format(
            disease['value']
          ),
        }
      else:
        yield {
          'value': 0.5,
          'comment': 'Disease `{}` found but not in MONDO.'.format(
            disease.get('value', '') + (('<' + value_ns + '>') if value_ns else '')
          ),
        }
  else:
    yield {
      'value': 0.0,
      'comment': 'Disease could not be identified',
    }
