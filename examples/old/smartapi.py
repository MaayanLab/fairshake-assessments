import os
import re
import json
import itertools
from pyswaggerclient import SwaggerClient
from pyswaggerclient.fetch import read_spec
from objectpath import Tree
from merging import prompt_merge_attr, prompt_select_dups

# Rubric we'll be evaluating (smartapi)
rubric = 28

# Project we'll be evaluating (smartapi)
project = 53

# Metrics we'll be evaluating
# query: objectpath query
# desc: Description of the metric
# metric: The id of the metric we're evaluating
# pattern: valid content of query result
metrics = [
  {
    'query': '$..info.x-accessRestriction.name',
    'desc': 'access restriction', 
    'metric': 92,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$..tags.name',
    'desc': 'tags', 
    'metric': 123,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$..info.version',
    'desc': 'Has version information', 
    'metric': 26,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$..contact.email',
    'desc': 'Has contact',
    'metric': 27,
    'pattern': re.compile(r'.+@.+'),
  },
  {
    'query': '$..info.license.name',
    'desc': 'License',
    'metric': 117,
    'pattern': re.compile(r'.+'),
  },

  {
    'query': '$..info.termsOfService',
    'desc': 'Usage Protocol/TOS',
    'metric':122,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$..info.title',
    'desc': 'Has a title',
    'metric': 60,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$..info.description',
    'desc': 'Has a description',
    'metric': 63,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$..contact.name',
    'desc': 'Metadata specifies the creators',
    'metric': 61,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$..paths..parameters.description',
    'ratio': [ # ratio of those with descriptions
      ['map(values, map(values, map(values, $..paths[type(@) is "object"])[type(@) is "object"]).parameters)[@.description is not None]'],
      'map(values, map(values, map(values, $..paths[type(@) is "object"])[type(@) is "object"]).parameters)',
      'all'
    ],
    'desc': 'All parameters have descriptions',
    'metric': 124,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$..paths.*.description',
    'ratio': [ # ratio of those with descriptions
      ['map(values, map(values, $..paths[type(@) is "object"])[type(@) is "object"])[@.description is not None]'],
      'map(values, map(values, $..paths[type(@) is "object"])[type(@) is "object"])',
      'all'
    ],
    'desc': 'All paths have descriptions',
    'metric': 125,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': 'map(values, $..paths..responses.*).*[@.description is not  None].description',
    'ratio': [ # ratio of those with descriptions
      ['map(values, map(values, map(values, $..paths[type(@) is "object"])[type(@) is "object"]).responses)[@.description is not None]'],
      'map(values, map(values, map(values, $..paths[type(@) is "object"])[type(@) is "object"]).responses)',
      'all'
    ], 
    'desc': 'All responses have descriptions',
    'metric': 126,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$..paths..operationId',
    'ratio': [['$..paths..operationId'],'$..paths..operationId','unique'], # ratio of unique ids
    'desc': 'All paths have unique operation Ids',
    'metric': 127,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$.."x-externalResources"[@."x-url"]',
    'ratio': [['$.."x-externalResources"[@."x-type" is not None]','$.."x-externalResources"[@."x-description" is not None]'],'$.."x-externalResources"[@."x-url" is not None]','all'],
    'desc': 'x-url (smartAPI fields all described w/ x-type and x-description)',
    'metric': 128,
    'pattern': re.compile(r'.+'),
  },
  {
    'metric': 89,
    'answer': 1.0,
    'desc': 'Machine readable metadata exists'
  },
  {
    'metric': 24,
    'answer': 1.0,
    'desc': 'Data is in an established data repository'
  },
  {
    'metric': 25,
    'answer': 1.0,
    'desc': 'Data can be downloaded for free from the repository'
  }
]

def smartapi_obj_to_fairshake_obj(smartapi_obj):
  ''' Convert a smartapi object entry into a FAIRshake
  object entry, mapping the field names in the smartapi
  object to those in FAIRshake.
  '''
  return {
    "title": smartapi_obj['info']['title'],
    "description": smartapi_obj['info'].get('description', ''),
    "tags": ','.join([t['name'] for t in smartapi_obj.get('tags', '')]),
    "url": '\n'.join(
      map(''.join,
        itertools.product(
          smartapi_obj['schemes'],
          ['://'],
          [smartapi_obj['host']],
          list(set(['', smartapi_obj['basePath']])),
        )
      )
    ),
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

def smartapi_get_all(smartapi, **kwargs):
  '''
  Yield paginated query operation using `from` syntax.
    query(from=0) == {
      [...] first 10
    }
    query(from=10) == {
      [...] second 10
    }
    ...
  '''
  n_results = 0
  while True:
    resp = smartapi.actions.query_get.call(**kwargs, **{'from': n_results})
    for hit in resp['hits']:
      n_results += 1
      yield hit
    if n_results >= resp['total']:
      break
    else:
      resp = smartapi.actions.query_get.call(**kwargs)

def get_smartapi_client():
  ''' Create a swagger client for smartapi.
  '''
  smartapi = SwaggerClient('https://smart-api.info/api/metadata/27a5b60716c3a401f2c021a5b718c5b1?format=yaml')
  return smartapi

def assess_smartapi_obj(smartapi_obj):
  ''' Given a smartapi object from the API, assess it for its fairness
  '''
  root = Tree(smartapi_obj)
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
          results = '; '.join([e.strip() for e in matches]).strip()
          try:
            ratio = get_ratio(
              root,
              metric['ratio'][0],
              metric['ratio'][1],
              metric['ratio'][2],
            )
          except Exception as e:
            print(e)
            pass
    
      if ratio == None:
        answers[metric['desc']] = {
          'metric': metric.get('metric',''),
          'answer': 1.0 if len(results)>0 and metric['pattern'].match(results) else 0.0,
          'comment': str(results),
        }
      else:
        answers[metric['desc']] = {
          'answer': ratio,
          'metric': metric.get('metric',''),
          'comment': metric['desc'],
        }

  return answers

def assess_all_smartapi_objects(smartapi=None, fairshake=None):
  ''' Gather all smartapi objects using `read_spec` to ensure they all
  follow the same smartapi format. Register them in FAIRshake and then
  assess them.
  '''
  for smartapi_obj in map(read_spec, itertools.chain(
    smartapi_get_all(smartapi, q='openapi:3'),
    smartapi_get_all(smartapi, q='swagger:2'),
  )):
    fairshake_obj = smartapi_obj_to_fairshake_obj(smartapi_obj)
    fairshake_assessment = assess_smartapi_obj(smartapi_obj)
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

for result in assess_all_smartapi_objects(smartapi=get_smartapi_client()):
  print(json.dumps(result))
