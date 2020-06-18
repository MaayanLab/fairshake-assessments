def first_or(l, o):
  try:
    return next(iter(l))
  except:
    return o
