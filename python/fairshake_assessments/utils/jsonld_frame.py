def jsonld_frame(doc, frame, default_ctx={ '@vocab': 'http://schema.org' }):
  from pyld import jsonld
  if '@context' in doc and '@context' in frame:
    return jsonld.frame(doc, frame)
  elif '@context' in doc:
    return jsonld.frame(
      doc,
      dict({ '@context': doc['@context'] }, **frame)
    )
  elif '@context' in frame:
    return jsonld.frame(
      dict({ '@context': doc['@context'] }, **doc),
      frame
    )
  else:
    return jsonld.frame(
      dict({ '@context': default_ctx }, **doc),
      dict({ '@context': default_ctx }, **frame)
    )
