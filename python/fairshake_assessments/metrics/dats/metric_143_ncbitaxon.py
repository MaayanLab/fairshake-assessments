import json
import pronto
from fairshake_assessments.core import metric
from fairshake_assessments.utils.jsonld_frame import jsonld_frame
from fairshake_assessments.utils.force_list import force_list
from fairshake_assessments.utils.IRI_to_NS import IRI_to_NS


NCBITaxon = pronto.Ontology('http://purl.obolibrary.org/obo/ncbitaxon.owl')
NCBITaxon_reversed = { node.name: node.id for node in NCBITaxon }
NCBITaxon_reversed_synonyms = { synonym: node.id for node in NCBITaxon for synonym in node.synonyms }

@metric({
  '@id': 143,
  'name': 'Taxonomy',
  'description': 'A taxonomy is present with a valid NCBITaxon identifier',
  'principle': 'Interoperable',
})
def metric_143_ncbitaxon(doc):
  taxonomies = list(map(json.loads,set(
    json.dumps({
      'value': isAbout['name'],
      'valueIRI': isAbout.get('identifier', {}).get('identifierSource', '') + isAbout.get('identifier', {}).get('identifier', '')
    })
    for node in jsonld_frame(doc, {
      '@type': 'Dataset',
      'isAbout': {
        '@type': 'TaxonomicInformation',
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
  if taxonomies:
    for taxonomy in taxonomies:
      value_ns = IRI_to_NS(taxonomy.get('valueIRI'))
      if taxonomy.get('value') and taxonomy.get('valueIRI') and pronto.Term(value_ns, taxonomy['value']) in NCBITaxon:
        yield {
          'value': 1,
          'comment': 'Ontological IRI for taxonomy {} and term match what is found in NCBITaxon.'.format(
            value_ns
          ),
        }
      elif taxonomy.get('valueIRI') and value_ns in NCBITaxon:
        yield {
          'value': 0.75,
          'comment': 'Ontological IRI for taxonomy {} found in NCBITaxon.'.format(
            value_ns
          ),
        }
      elif taxonomy.get('value') and taxonomy['value'] in NCBITaxon_reversed:
        yield {
          'value': 0.75,
          'comment': 'Taxonomy `{}` found in NCBITaxon.'.format(
            taxonomy['value']
          ),
        }
      elif taxonomy.get('value') and taxonomy['value'] in NCBITaxon_reversed_synonyms:
        yield {
          'value': 0.5,
          'comment': 'Taxonomy `{}` found in NCBITaxon synonyms.'.format(
            taxonomy['value']
          ),
        }
      else:
        yield {
          'value': 0.25,
          'comment': 'Taxonomy `{}` found but not in NCBITaxon.'.format(
            taxonomy.get('value', '') + (('<' + value_ns + '>') if value_ns else '')
          ),
        }
  else:
    yield {
      'value': 0.0,
      'comment': 'Taxonomy could not be identified',
    }
