import json
import pronto
from fairshake_assessments.core import metric
from fairshake_assessments.utils.jsonld_frame import jsonld_frame
from fairshake_assessments.utils.force_list import force_list
from fairshake_assessments.utils.IRI_to_NS import IRI_to_NS
from fairshake_assessments.utils.fetch_and_cache import fetch_and_cache


EDAM = pronto.Ontology(fetch_and_cache('http://edamontology.org/EDAM.owl', '.cache/EDAM.owl'))
EDAM_reversed = { node.name: node.id for node in map(EDAM.get, EDAM) if node }
EDAM_reversed_synonyms = { synonym: node.id for node in map(EDAM.get, EDAM) if node for synonym in node.synonyms }

@metric({
  '@id': 142,
  'name': 'File type',
  'description': 'A file type is present with a valid EDAM identifier',
  'principle': 'Interoperable',
})
def metric_142_edam(doc):
  filetypes = list(map(json.loads,set(
    json.dumps({
      'value': information['value'],
      'valueIRI': information['valueIRI'],
    })
    for node in jsonld_frame(doc, {
      '@type': 'Dataset',
      'types': {
        'information': {
          'value': { '@default': '' },
          'valueIRI': { '@default': '' }
        }
      }
    })['@graph']
    if node['types']
    for types in force_list(node['types'])
    if types['information']
    for information in force_list(types['information'])
    if information['value'] and information['valueIRI']
  )))
  if filetypes:
    for filetype in filetypes:
      value_ns = IRI_to_NS(filetype.get('valueIRI'))
      if filetype.get('value') and filetype.get('valueIRI') and pronto.Term(value_ns, filetype['value']) in EDAM:
        yield {
          'value': 1,
          'comment': 'Ontological IRI for file type {} and term match what is found in EDAM.'.format(
            value_ns
          ),
        }
      elif filetype.get('valueIRI') and value_ns in EDAM:
        yield {
          'value': 0.75,
          'comment': 'Ontological IRI for filetype {} found in EDAM.'.format(
            value_ns
          ),
        }
      elif filetype.get('value') and filetype['value'] in EDAM_reversed:
        yield {
          'value': 0.75,
          'comment': 'Filetype `{}` found in EDAM.'.format(
            filetype['value']
          ),
        }
      elif filetype.get('value') and filetype['value'] in EDAM_reversed_synonyms:
        yield {
          'value': 0.5,
          'comment': 'Filetype `{}` found in EDAM synonyms.'.format(
            filetype['value']
          ),
        }
      else:
        yield {
          'value': 0.25,
          'comment': 'Filetype `{}` found but not in EDAM.'.format(
            filetype.get('value', '') + (('<' + value_ns + '>') if value_ns else '')
          ),
        }
  else:
    yield {
      'value': 0.0,
      'comment': 'filetype could not be identified',
    }
