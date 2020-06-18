def filter_none(obj):
  return {
    k: v
    for k, v in obj.items()
    if v is not None
  }
