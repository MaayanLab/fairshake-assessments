import json
import uuid

U = uuid.UUID('00000000-0000-0000-0000-000000000000')

def with_id(doc):
  id = str(uuid.uuid5(U, json.dumps(doc)))
  return dict(doc, id=id)
