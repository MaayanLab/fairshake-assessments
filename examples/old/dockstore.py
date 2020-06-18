import os
import re
import sys
import json
import itertools
from pyswaggerclient import SwaggerClient
from objectpath import Tree

# Rubric we'll be evaluating (fairmetrics)
rubric = 25

# Project we'll be evaluating (dockstore)
project = 69

# Example metadata:
# {'aliases': [],
#  'author': 'Francesco Favero',
#  'checker_url': '',
#  'contains': [],
#  'description': '![](https://bytebucket.org/sequenza_tools/icons/raw/da034ccc8c1ab5f5f8e020402267bd3f2dd5d361/svg/sequenza_tools/sequenzaalpha_150.svg)\n\n![build_status](https://img.shields.io/docker/build/sequenza/sequenza.svg)\n![docker_pulls](https://img.shields.io/docker/pulls/sequenza/sequenza.svg)\n![docker_builds](https://img.shields.io/docker/automated/sequenza/sequenza.svg)\n\n**Sequenza workflow**\n\nAllele-specific SCNA analysis from tumor/normal sequencing with the sequenza docker container',
#  'has_checker': False,
#  'id': 'registry.hub.docker.com/sequenza/sequenza',
#  'meta_version': '2018-08-15 07:46:18.076',
#  'organization': 'sequenza',
#  'signed': False,
#  'toolclass': {'description': 'CommandLineTool',
#   'id': '0',
#   'name': 'CommandLineTool'},
#  'toolname': 'sequenza',
#  'url': 'https://dockstore.org/api/api/ga4gh/v2/tools/registry.hub.docker.com%2Fsequenza%2Fsequenza',
#  'verified': False,
#  'verified_source': '[]',
#  'versions': [{'containerfile': True,
#    'descriptor_type': ['CWL', 'WDL'],
#    'id': 'registry.hub.docker.com/sequenza/sequenza:2.2.0.9000',
#    'image': '',
#    'image_name': 'registry.hub.docker.com/sequenza/sequenza',
#    'meta_version': 'Thu Jan 01 00:00:00 UTC 1970',
#    'name': '2.2.0.9000',
#    'registry_url': 'registry.hub.docker.com',
#    'url': 'https://dockstore.org/api/api/ga4gh/v2/tools/registry.hub.docker.com%2Fsequenza%2Fsequenza/versions/2.2.0.9000',
#    'verified': False,
#    'verified_source': ''},
#   {'containerfile': True,
#    'descriptor_type': ['CWL', 'WDL'],
#    'id': 'registry.hub.docker.com/sequenza/sequenza:latest',
#    'image': '',
#    'image_name': 'registry.hub.docker.com/sequenza/sequenza',
#    'meta_version': 'Thu Jan 01 00:00:00 UTC 1970',
#    'name': 'latest',
#    'registry_url': 'registry.hub.docker.com',
#    'url': 'https://dockstore.org/api/api/ga4gh/v2/tools/registry.hub.docker.com%2Fsequenza%2Fsequenza/versions/latest',
#    'verified': False,
#    'verified_source': ''}

# Measurements:
metrics = [
  {
    'query': '$..id',
    'desc': 'globally unique identifier', 
    'metric': 104,
    'pattern': re.compile(r'.+'),
    'answer': 0.5,
  },
  {
    'query': '$..id',
    'desc': 'persistent identifier', 
    'metric': 105,
    'pattern': re.compile(r'.+'),
    'answer': 0.5,
  },
  {
    'desc': 'machine readable metadata', 
    'metric': 106,
    'answer': 1,
  },
  {
    'query': '$.author',
    'desc': 'standardized metadata',
    'metric': 107,
    'pattern': re.compile(r'.+'),
    'answer': 0.5,
  },
  {
    'query': '$..id',
    'desc': 'resource identifier',
    'metric': 108,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$..url',
    'desc': 'resource discovery',
    'metric': 109,
    'pattern': re.compile(r'.+'),
  },
  {
    'desc': 'open, free, standardized access protocol',
    'metric': 110,
    'answer': 1,
    'comment': 'docker',
  },
  {
    'desc': 'protocol to access restricted content',
    'metric': 111,
    'answer': None,
  },
  {
    'desc': 'persistence of resource and metadata',
    'metric': 112,
    'answer': 0.5,
  },
  {
    'query': '$..@context',
    'desc': 'formal language',
    'metric': 113,
  },
  {
    'query': '$..@context.@vocab',
    'desc': 'fair vocab',
    'metric': 114,
  },
  {
    'query': '$..versions',
    'desc': 'linked',
    'metric': 115,
    'pattern': re.compile(r'.+'),
  },
  {
    'desc': 'digital resource license',
    'metric': 116,
    'answer': 0,
  },
  {
    'query': '$..license',
    'desc': 'metadata license',
    'metric': 117,
  },
  {
    'desc': 'provenance scheme',
    'metric': 118,
    'answer': 0,
  },
  {
    'desc': 'certificate of compliance',
    'metric': 119,
    'answer': 0,
  }
]

def dockstore_obj_to_fairshake_obj(dockstore_obj):
  ''' Convert a dockstore object entry into a FAIRshake
  object entry, mapping the field names in the dockstore
  object to those in FAIRshake.
  '''
  return {
    "title": dockstore_obj['toolname'],
    "description": dockstore_obj['description'].rstrip('\n'),
    "tags": ','.join([t['name'] for t in dockstore_obj.get('tags', '')]),
    "url": dockstore_obj['url'],
    "projects": [project],
    "rubrics": [rubric],
  }

def get_ratio(ROOT, sample, n, u):
  '''
  function gets ratio of present parameters
  '''
  r = None
  if len(list(ROOT.execute(n))) != 0:
    total = 0
    for s in sample:
      res = list(ROOT.execute(s))
      if u == 'unique':
        res = list(set(res))
      total = total + len(res)
    total = total/len(sample)    
    r = (total)/len(list(ROOT.execute(n)))
  return(r)

def dockstore_get_all(dockstore, **kwargs):
  '''
  Get all dockstore tools
  '''
  return dockstore.actions.toolsGet.call(**kwargs)

def get_dockstore_client():
  ''' Create a swagger client for dockstore.
  '''
  dockstore = SwaggerClient('https://dockstore.org/swagger.json')
  return dockstore

def assess_dockstore_obj(dockstore_obj):
  ''' Given a dockstore object from the API, assess it for its fairness
  '''
  root = Tree(dockstore_obj)
  print('Performing assessment...')

  answers = {}
  for metric in metrics:
    if metric.get('query') is None:
      answers[metric['desc']] = {
        'metric': metric.get('metric', ''),
        'answer': metric.get('answer', 1.0),
        'comment': metric['desc'],
      }
    else:
      matches = root.execute(metric['query'])
      results = []
      ratio = None
      if matches != None:
          matches = list(itertools.chain(matches))
          results = '; '.join([str(e).strip() for e in matches]).strip()
          try:
            ratio = get_ratio(
              root,
              metric['ratio'][0],
              metric['ratio'][1],
              metric['ratio'][2],
            )
          except:
            pass
    
      if ratio == None:
        answers[metric['desc']] = {
          'metric': metric.get('metric',''),
          'answer': 1.0 if len(results)>0 and metric['pattern'].match(results) else 0.0,
          'comment': str(results),
        }
      else:
        answers[metric['desc']] = {
          'metric': metric.get('metric',''),
          'comment': metric['desc'],
        }
        answers[metric['desc']]['answer'] = ratio

  return answers

def assess_all_dockstore_objects(dockstore=None, fairshake=None):
  ''' Gather all dockstore objects using `read_spec` to ensure they all
  follow the same dockstore format then assess them.
  '''
  for dockstore_obj in dockstore_get_all(dockstore):
    fairshake_obj = dockstore_obj_to_fairshake_obj(dockstore_obj)
    fairshake_assessment = assess_dockstore_obj(dockstore_obj)
    yield dict(
      answers=[
        answer
        for answer in fairshake_assessment.values()
        if answer.get('answer') is not None
      ],
      project=project,
      rubric=rubric,
      target=fairshake_obj,
    )

for result in assess_all_dockstore_objects(dockstore=get_dockstore_client()):
  print(json.dumps(result))
