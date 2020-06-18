import json
import pronto
from fairshake_assessments.core import metric
from fairshake_assessments.utils.jsonld_frame import jsonld_frame
from fairshake_assessments.utils.force_list import force_list
from fairshake_assessments.utils.IRI_to_NS import IRI_to_NS
from fairshake_assessments.utils.fetch_and_cache import fetch_and_cache


BAO = pronto.Ontology(fetch_and_cache('http://www.bioassayontology.org/bao/bao_complete.owl', '.cache/bao_complete.owl'))
BAO_reversed = { node.name: node.id for node in map(BAO.get, BAO) if node }
BAO_reversed_synonyms = { synonym: node.id for node in map(BAO.get, BAO) if node for synonym in node.synonyms }

@metric({
  '@id': 139,
  'name': 'BioAssay',
  'description': 'Assay is present and a proper BioAssay term resolvable in the latest BAO release.',
  'principle': 'Interoperable',
})
def metric_139_bao(doc):
  assays = list(map(json.loads,set(
    json.dumps({
      'value': method if type(method) == str else method['value'],
      'valueIRI': '' if type(method) == str else method['valueIRI'],
    })
    for node in jsonld_frame(doc, {
      '@type': 'Dataset',
      'types': {
        'method': {
          'value': { '@default': '' },
          'valueIRI': { '@default': '' }
        }
      }
    })['@graph']
    if node['types']
    for types in force_list(node['types'])
    if types['method']
    for method in force_list(types['method'])
    if type(method) == str or (type(method) == dict and method['value'] or method['valueIRI'])
  )))
  if assays:
    for assay in assays:
      value_ns = IRI_to_NS(assay.get('valueIRI'))
      if assay.get('value') and assay.get('valueIRI') and pronto.Term(value_ns, assay.get('value')) in BAO:
        yield {
          'value': 1,
          'comment': 'Ontological IRI for Assay {} and term match what is found in BAO.'.format(
            assay['valueIRI']
          ),
        }
      elif value_ns and assay['valueIRI'] in BAO:
        yield {
          'value': 0.75,
          'comment': 'Ontological IRI for Assay {} found in BAO.'.format(
            assay['valueIRI']
          ),
        }
      elif assay.get('value') and assay['value'] in BAO_reversed:
        yield {
          'value': 0.75,
          'comment': 'Assay {} found in BAO.'.format(
            assay['value']
          ),
        }
      elif assay.get('value') and assay['value'] in BAO_reversed_synonyms:
        yield {
          'value': 0.5,
          'comment': 'Assay `{}` found in BAO synonyms.'.format(
            assay['value']
          ),
        }
      else:
        yield {
          'value': 0.25,
          'comment': 'Assay {} found but not in BAO.'.format(
            assay.get('value', '') + (('<' + value_ns + '>') if value_ns else '')
          ),
        }
  else:
    yield {
      'value': 0.0,
      'comment': 'Assay could not be identified',
    }
