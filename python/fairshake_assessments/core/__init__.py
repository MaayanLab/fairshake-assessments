from .assess import *
from .fairshake import *

def metric(schema):
  assert '@id' in schema
  def wrapper(func):
    return dict({'@type': 'Metric'}, **schema, function=func)
  return wrapper
