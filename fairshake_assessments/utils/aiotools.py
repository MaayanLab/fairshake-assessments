import random
import asyncio
import inspect
import functools
import logging

_backoff_scale = 0.001

# ```rust enum Maybe { Some(value), None };```
class _Maybe: pass
class _None(_Maybe):
  def __eq__(self, other):
    return isinstance(other, _None)
  def __lt__(self, other):
    return False
class _Some(_Maybe):
  def __init__(self, value):
    self.value = value
  def __lt__(self, other):
    if isinstance(other, _None):
      return True
    else:
      return self.value.__lt__(other.value)

# Async Function Helpers
def ensure_async(func, executor=None):
  if inspect.iscoroutinefunction(func):
    return func
  else:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
      loop = asyncio.get_running_loop()
      return await loop.run_in_executor(executor, functools.partial(func, *args, **kwargs))
    return wrapper


# Async Generator Tools

def async_maybe_next(it):
  try:
    return _Some(next(it))
  except StopIteration:
    return _None()

def ensure_async_generator(func, executor=None):
  if inspect.iscoroutinefunction(func):
    return func
  else:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
      loop = asyncio.get_running_loop()
      it = iter(func(*args, **kwargs))
      while not isinstance(result := await loop.run_in_executor(executor, async_maybe_next, it), _None):
        yield result.value
    return wrapper

async def async_collect(async_gen):
  L = []
  async for el in async_gen:
    L.append(el)
  return L

async def async_enumerate(async_gen, start=0):
  i = start
  async for el in async_gen:
    yield i, el
    i += 1

async def async_unenumerate(async_gen):
  ''' Order an unordered enumerated async iterator.
  a, b, ...
  => async_enumerate
  => (0, a), (1, b), ...
  => process with non-deterministic ordering
  => (1, b), (0, a), ...
  => async_unenumerate
  => a, b, ...
  '''
  Q = asyncio.PriorityQueue()
  async def mapper():
    async for i, el in async_gen:
      await Q.put(_Some((i, el)))
    await Q.put(_None())
  #
  asyncio.create_task(mapper())
  i = 0
  while not isinstance(value := await Q.get(), _None):
    _i, el = value.value
    if _i == i:
      yield el
      i += 1
    else:
      await asyncio.sleep(_backoff_scale * random.random())
      await Q.put(_Some((_i, el)))
    Q.task_done()
  Q.task_done()

def async_generator_split(async_gen, k=2):
  ''' Split an async generator into `k` async generators
  '''
  if k == 1: return [async_gen]
  #
  Q = asyncio.Queue(maxsize=k)
  #
  async def splitter():
    ''' Add elements from the primary generator to the queue '''
    async for task in async_gen:
      await Q.put(_Some(task))
    # trigger all k generators to close
    for _ in range(k):
      await Q.put(_None())
  #
  asyncio.create_task(splitter())
  #
  async def generator(i):
    ''' Add elements to the split generators from the queue '''
    while not isinstance(task := await Q.get(), _None):
      yield task.value
      Q.task_done()
    Q.task_done()
  #
  return [generator(i) for i in range(k)]

async def async_generator_merge(async_generators):
  ''' Join several independent generators into one
  '''
  if len(async_generators) == 1:
    async_generator, = async_generators
    async for el in async_generator:
      yield el
  elif len(async_generators) > 1:
    Q = asyncio.Queue(maxsize=len(async_generators))
    async def consumer(async_generator, i):
      async for el in async_generator:
        await Q.put(_Some(el))
      await Q.put(_None())
    # start consuming from all generators
    for i, async_generator in enumerate(async_generators):
      asyncio.create_task(consumer(async_generator, i))
    # until all generators are exhaused, we'll yield from the queue
    k = len(async_generators)
    while k > 0:
      el = await Q.get()
      if isinstance(el, _None):
        k -= 1
      else:
        yield el.value
      Q.task_done()

async def async_split_map_unordered(func, async_gen, k=2):
  ''' Map function to values of the async_generator with at most `k`
  concurrent operations at a time with non-deterministic result-set ordering
  '''
  async for el in async_generator_merge([
    (await func(el)
      async for el in gen)
    for gen in async_generator_split(async_gen, k=k)
  ]): yield el

async def async_split_map(func, async_gen, k=2):
  ''' Map functin to values of the async_generator with at most `k`
  concurrent operations at a time with results in order.
  '''
  async def _func(i_el):
    i, el = i_el
    return (i, await func(el))
  #
  async for el in async_unenumerate(
      async_split_map_unordered(_func, async_enumerate(async_gen), k=k)
  ): yield el
