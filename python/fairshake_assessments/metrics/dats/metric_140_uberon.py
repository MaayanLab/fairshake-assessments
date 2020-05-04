import json
import pronto
from fairshake_assessments.core import metric
from fairshake_assessments.utils.jsonld_frame import jsonld_frame
from fairshake_assessments.utils.force_list import force_list
from fairshake_assessments.utils.IRI_to_NS import IRI_to_NS


UBERON = pronto.Ontology('http://purl.obolibrary.org/obo/uberon/uberon.owl')
UBERON_reversed = { node.name: node.id for node in UBERON }
UBERON_reversed_synonyms = { synonym: node.id for node in UBERON for synonym in node.synonyms }

@metric({
  '@id': 140,
  'name': 'Anatomical Part',
  'description': 'An anatomical part is present with a valid UBERON identifier',
  'principle': 'Interoperable',
})
def _(doc):
  anatomical_parts = list(map(json.loads,set(
    json.dumps({
      'value': isAbout['name'],
      'valueIRI': isAbout.get('identifier', {}).get('identifierSource', '') + isAbout.get('identifier', {}).get('identifier', '')
    })
    for node in jsonld_frame(doc, {
      '@type': 'Dataset',
      'isAbout': {
        '@type': 'AnatomicalPart',
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
  if anatomical_parts:
    for anatomical_part in anatomical_parts:
      value_ns = IRI_to_NS(anatomical_part.get('valueIRI'))
      if anatomical_part.get('value') and anatomical_part.get('valueIRI') and pronto.Term(value_ns, anatomical_part['value']) in UBERON:
        yield {
          'value': 1,
          'comment': 'Ontological IRI for anatomical part {} and term match what is found in UBERON.'.format(
            value_ns
          ),
        }
      elif anatomical_part.get('valueIRI') and value_ns in UBERON:
        yield {
          'value': 0.75,
          'comment': 'Ontological IRI for anatomical part {} found in UBERON.'.format(
            value_ns
          ),
        }
      elif anatomical_part.get('value') and anatomical_part['value'] in UBERON_reversed:
        yield {
          'value': 0.75,
          'comment': 'Anatomical part `{}` found in UBERON.'.format(
            anatomical_part['value']
          ),
        }
      elif anatomical_part.get('value') and anatomical_part['value'] in UBERON_reversed_synonyms:
        yield {
          'value': 0.5,
          'comment': 'Anatomical part `{}` found in UBERON synonyms.'.format(
            anatomical_part['value']
          ),
        }
      else:
        yield {
          'value': 0.25,
          'comment': 'Anatomical part `{}` found but not in UBERON.'.format(
            anatomical_part.get('value', '') + (('<' + value_ns + '>') if value_ns else '')
          ),
        }
  else:
    yield {
      'value': 0.0,
      'comment': 'Anatomical part could not be identified',
    }
