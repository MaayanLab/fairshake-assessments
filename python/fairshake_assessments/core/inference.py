from jsonlddb import JsonLDDatabase

def forward_chain_resolvers(resolvers, db, resolved):
  for resolver in resolvers.values():
    for node in db[resolver['frame']]:
      if not resolved.get(resolver['@id'], {}).get(node['@id'], False):
        db.update(list(resolver['func'](node)))
        if resolved.get(resolver['@id']) is None:
          resolved[resolver['@id']] = {}
        resolved[resolver['@id']][node['@id']] = True
  return db, resolved

def fully_resolve_jsonld(resolvers, jsonld):
  db = JsonLDDatabase()
  db.update(jsonld)
  # forward_chain until no new information can be resolved
  resolved = {}
  previous = None
  while str(resolved) != previous:
    previous = str(resolved)
    db, resolved = forward_chain_resolvers(resolvers, db, resolved)
  return db
