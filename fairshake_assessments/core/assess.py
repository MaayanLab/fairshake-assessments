def assess_one(rubric, doc):
  assessment = {
    '@type': 'Assessment',
    'target': doc,
    'rubric': rubric['@id'],
    'answers': []
  }
  if 'resolvers' in rubric:
    from fairshake_assessments.core.inference import fully_resolve_jsonld
    doc = fully_resolve_jsonld(rubric['resolvers'], doc)
  #
  for metric in rubric['metrics']:
    for answer in metric['function'](doc):
      assessment['answers'].append({
        'metric': metric['@id'],
        'answer': answer,
      })
  return assessment

def assess_many(rubric, doc_iterator, max_workers=10):
  for doc in doc_iterator:
    yield assess_one(rubric, doc)

def assess_many_async(rubric, doc_iterator, max_workers=10):
  import concurrent.futures
  with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    future_doc = {
      executor.submit(assess_one, rubric, doc): doc
      for doc in doc_iterator
    }
    for future in concurrent.futures.as_completed(future_doc):
      doc = future_doc[future]
      try:
        yield future.result()
      except Exception as e:
        yield e
