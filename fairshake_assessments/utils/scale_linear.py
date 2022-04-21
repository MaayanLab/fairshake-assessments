def scaleLinear(domain, range):
  ''' Like d3's scaleLinear
  domain: (0, 1)
  range: (0, 10)
  range: ['poor', 'okay', 'good', 'great']
  '''
  assert type(domain) == tuple and len(domain) == 2
  if type(range) == tuple and len(domain) == 2:
    def scale(value):
      assert value >= domain[0] and value <= domain[1]
      return (value - domain[0]) * (range[1] - range[0]) + range[0]
    return scale
  elif type(range) == list:
    indexScale = scaleLinear(domain, (0, len(range)))
    def scale(value):
      assert value >= domain[0] and value <= domain[1]
      return range[min(int(indexScale(value)), len(range)-1)]
    return scale
  else:
    raise NotImplementedError
