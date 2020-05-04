''' Here we define and codify the aspects of the FAIR assessment and mechanism by which
they will be evaluated.
'''

import fairshake_assessments.metrics.dats

rubric = {
  '@id': 36,
  'name': 'NIH CFDE Interoperability',
  'description': 'This rubric identifies aspects of the metadata models which promote interoperable dataset querying and filtering',
  'metrics': [
    fairshake_assessments.metrics.dats.metric_107_dats,
    fairshake_assessments.metrics.dats.metric_136_program,
    fairshake_assessments.metrics.dats.metric_137_project,
    fairshake_assessments.metrics.dats.metric_27_contact_pi,
    fairshake_assessments.metrics.dats.metric_138_institution,
    fairshake_assessments.metrics.dats.metric_110_access_protocol,
    fairshake_assessments.metrics.dats.metric_139_bao,
    fairshake_assessments.metrics.dats.metric_140_uberon,
    fairshake_assessments.metrics.dats.metric_141_mondo,
    fairshake_assessments.metrics.dats.metric_142_edam,
    fairshake_assessments.metrics.dats.metric_143_ncbitaxon,
    fairshake_assessments.metrics.dats.metric_144_cellosaurus,
    fairshake_assessments.metrics.dats.metric_116_data_usage_license,
    fairshake_assessments.metrics.dats.metric_104_doi,
    fairshake_assessments.metrics.dats.metric_108_resource_identifier,
    fairshake_assessments.metrics.dats.metric_145_landing_page,
  ],
}
