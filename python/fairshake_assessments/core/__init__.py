def metric(schema):
  assert '@id' in schema
  assert 'name' in schema
  def wrapper(func):
    return dict({'@type': 'Metric'}, **schema, call=func)
  setattr(wrapper, '__name__', schema.get('name', '@id'))
  return wrapper
