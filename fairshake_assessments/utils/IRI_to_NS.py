def IRI_to_NS(iri):
  ''' Try to convert an IRI to a namespace (NS:IDENTIFIER)
  Essentially we assume the last part of a URI (separated by # or /) contains
   the namespace and identifier with some delineation (i.e. _ or -) 
  '''
  import re
  if iri and type(iri) == str:
    return re.sub(r'[_-]', ':', re.split(r'[#/]', iri[::-1])[0][::-1])
