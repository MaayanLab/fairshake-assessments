import os
import pathlib
import sys
import json
import click
import importlib

from fairshake_assessments.cli import cli
from fairshake_assessments.utils.scale_linear import scaleLinear

@cli.command()
@click.option('-i', '--input', type=click.File('r'), help='Assessments in jsonl format')
@click.option('-o', '--output', type=click.File('w'), help='Assessment summary in json format')
@click.option('-r', '--rubric', type=str, required=True, help='Rubric used for the assessments')
def summarize(input, output, rubric):
  try:
    rubric_id = int(rubric)
  except:
    rubric_path = pathlib.Path(rubric).resolve()
    sys.path.insert(0, str(rubric_path.parent))
    rubric_id = importlib.import_module(rubric_path.stem).rubric['@id']
  #
  summary = {}
  for assessment in map(json.loads, input):
    for answer in assessment['answers']:
      if answer['metric']['@id'] not in summary:
        summary[answer['metric']['@id']] = []
      summary[answer['metric']['@id']].append(answer['answer']['value'])
  #
  answers = []
  bins = ['bad', 'poor', 'okay', 'good', 'great']
  scale = scaleLinear((0, 1), bins)
  for metric_id, values in summary.items():
    # compute distribution statistics
    N = len(values)
    mu = sum(values)/N
    sigma = (sum((v - mu)**2 for v in values) / N)**(1/2)
    # compute a answer distribution according to the ordinal bins
    hist = { bin: 0 for bin in bins }
    for value in values: hist[scale(value)] += 1
    # add answer summary with supplement
    answers.append(dict(
      metric=metric_id,
      answer=mu,
      comment=f"sigma={sigma:0.2f} N={N}",
      supplement=dict(
        sigma=sigma,
        N=N,
        hist=hist,
      ),
    ))
  #
  assessment = dict(
    rubric=rubric_id,
    answers=answers,
  )
  json.dump(assessment, output)

if __name__ == '__main__':
  summarize()
