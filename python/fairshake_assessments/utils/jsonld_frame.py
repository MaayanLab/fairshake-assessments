def jsonld_frame(doc, frame, default_ctx={ '@vocab': 'http://schema.org' }):
  from pyld import jsonld
  if '@context' in doc and '@context' in frame:
    result = jsonld.frame(doc, frame)
  elif '@context' in doc:
    result = jsonld.frame(
      doc,
      dict({ '@context': doc['@context'] }, **frame)
    )
  elif '@context' in frame:
    result = jsonld.frame(
      dict({ '@context': doc['@context'] }, **doc),
      frame
    )
  else:
    result = jsonld.frame(
      dict({ '@context': default_ctx }, **doc),
      dict({ '@context': default_ctx }, **frame)
    )
  #
  if '@graph' in result:
    return result
  else:
    return {'@context': result['@context'], '@graph': [result]}
