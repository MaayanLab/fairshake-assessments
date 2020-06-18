from jsonlddb import JsonLDDatabase

def forward_chain_resolvers(resolvers, db, resolved):
  for resolver in resolvers:
    for node in db[resolver['frame']]:
      if not resolved.get(resolver['@id'], {}).get(node['@id'], False):
        db.insert(list(resolver['function'](node)))
        if resolved.get(resolver['@id']) is None:
          resolved[resolver['@id']] = {}
        resolved[resolver['@id']][node['@id']] = True
  return db, resolved

def fully_resolve_jsonld(resolvers, jsonld):
  db = JsonLDDatabase()
  db.insert(jsonld)
  # forward_chain until no new information can be resolved
  resolved = {}
  previous = None
  while str(resolved) != previous:
    previous = str(resolved)
    db, resolved = forward_chain_resolvers(resolvers, db, resolved)
  return db
