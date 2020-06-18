'''
Grab and utilize FAIR Maturity Indicator tests registered here:
https://fairsharing.github.io/FAIR-Evaluator-FrontEnd/#!/metrics
'''

import re
import json
import urllib.request
from functools import wraps
from pyswaggerclient import SwaggerClient
from fairshake_assessments.core import metric

metrics = json.load(urllib.request.urlopen('https://fair-evaluator.semanticscience.org/FAIR_Evaluator/metrics.json'))

def metric_id_to_name(id):
  return re.match('^https://w3id.org/(.+)', id).group(1).replace('/', '_')

for fair_metric in metrics:
  fair_metric_client = SwaggerClient(fair_metric['smarturl'])
  for action in dir(fair_metric_client.actions):
    if action.startswith('_'):
      continue
    func = getattr(fair_metric_client.actions, action).call
    wrap_func = wraps(func)(lambda content: func(content=dict(subject=content)))
    globals()[metric_id_to_name(fair_metric['@id'])] = metric(fair_metric)(wrap_func)
