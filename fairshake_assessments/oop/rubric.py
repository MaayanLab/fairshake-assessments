import os
import json
import click
import asyncio
import inspect
import functools
import logging
import aiofile

logger = logging.getLogger()

class _Join: pass

def _ensure_async(func, executor=None):
  if inspect.iscoroutinefunction(func):
    return func
  else:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
      loop = asyncio.get_running_loop()
      return await loop.run_in_executor(executor, functools.partial(func, *args, **kwargs))
    return wrapper

def _async_next(it):
  try:
    return next(it)
  except StopIteration:
    return _Join

def _ensure_async_generator(func, executor=None):
  if inspect.iscoroutinefunction(func):
    return func
  else:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
      loop = asyncio.get_running_loop()
      it = iter(func(*args, **kwargs))
      while (result := await loop.run_in_executor(executor, _async_next, it)) is not _Join:
        yield result
    return wrapper

class Rubric:
  def __init__(self, jsonld):
    self._jsonld = jsonld
    assert '@id' in jsonld, '@id is required'
    assert 'fairshake:metrics' not in self._jsonld, 'fairshake:metrics is reserved'
    self._jsonld['fairshake:metrics'] = {}
  #
  def __repr__(self) -> str:
    return repr(self._jsonld)
  #
  def add_metric(self, jsonld):
    ''' Add a metric to this rubric
    Usage:
    rubric = Rubric({ ... })

    @rubric.add_metric({ ... })
    def _(doc):
      # assess doc & yield result
      yield 1.0
    '''
    assert '@id' in jsonld, '@id is required'
    self._jsonld['fairshake:metrics'][jsonld['@id']] = jsonld
    def decorator(func):
      @functools.wraps(func)
      def wrapper(doc):
        return func(doc)
      jsonld['func'] = wrapper
      return wrapper
    return decorator
  #
  async def _answer(self, metric, input):
    answers = []
    async for answer in metric['func'](input):
      answers.append({
        'metric': metric['@id'],
        'answer': answer
      })
    return answers
  #
  async def _assess(self, input):
    return await asyncio.gather(*[
      self._answer(metric, input)
      for metric in self._jsonld['fairshake:metrics'].values()
    ])
  #
  async def _read_decode_enqueue(self, input_file, decoder, input_queue):
    async with aiofile.async_open(input_file, 'r') as reader:
      while serialized_input := await reader.readline():
        input = await decoder(serialized_input)
        await input_queue.put(input)
  #
  async def _dequeue_assess_enqueue(self, input_queue, output_queue):
    while (input := await input_queue.get()) is not _Join:
      output = await self._assess(input)
      await output_queue.put(output)
      input_queue.task_done()
    input_queue.task_done()
  #
  async def _dequeue_encode_write(self, output_queue, encoder, output_file):
    async with aiofile.async_open(output_file, 'w') as writer:
      while (output := await output_queue.get()) is not _Join:
        serialized_output = await encoder(output)
        await writer.write(serialized_output + os.linesep)
        output_queue.task_done()
    output_queue.task_done()
  #
  async def assess(self, input, output, jobs=10, decoder=json.loads, encoder=json.dumps, executor=None):
    ''' Read the documents in `input`, and write the assessment results to `output`.
    `jobs`: maximum number of concurrent assessments to perform
    `decoder`: decode lines of the document, default to json parsing
    `encoder`: encode assessment results, default to json serialization
    `executor`: executor to use for non-asyncio function calling, defaults to python default
    '''
    decoder = _ensure_async(decoder, executor=executor)
    encoder = _ensure_async(encoder, executor=executor)
    for metric in self._jsonld['fairshake:metrics'].values():
      metric['func'] = _ensure_async_generator(metric['func'], executor=executor)
    #
    input_queue = asyncio.Queue(maxsize=jobs)
    output_queue = asyncio.Queue(maxsize=jobs)
    reader = asyncio.create_task(self._read_decode_enqueue(input, decoder, input_queue))
    workers = [asyncio.create_task(self._dequeue_assess_enqueue(input_queue, output_queue))
               for _ in range(jobs)]
    writer = asyncio.create_task(self._dequeue_encode_write(output_queue, encoder, output))
    # wait for reader to complete
    await reader
    # join all the workers
    for _ in range(jobs):
      await input_queue.put(_Join)
    await asyncio.gather(*workers)
    # join the writer
    await output_queue.put(_Join)
    await writer
  #
  def cli(self):
    ''' Expose rubric as a command driven application for performing assessments.
    '''
    @click.command()
    @click.option('-i', '--input', type=click.Path(dir_okay=False, readable=True, allow_dash=True), default='-', help='Input stream in jsonl format')
    @click.option('-o', '--output', type=click.Path(dir_okay=False, writable=True, allow_dash=True), default='-', help='Output stream in jsonl format')
    @click.option('-j', '--jobs', type=int, default=10, help='Number of jobs to perform concurrently')
    def assess(input, output, jobs):
      input = '/dev/stdin' if input == '-' else input
      output = '/dev/stdout' if output == '-' else output
      asyncio.run(self.assess(input=input, output=output, jobs=jobs))
    #
    return assess()
