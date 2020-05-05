
def assess_one(rubric, doc):
  assessment = {
    '@type': 'Assessment',
    'target': doc,
    'rubric': rubric['@id'],
    'answers': []
  }
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
