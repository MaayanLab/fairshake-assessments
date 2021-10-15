import os
import pathlib
import sys
import json
import click
import importlib

from fairshake_assessments.cli import cli

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
  for metric_id, values in summary.items():
    N = len(values)
    mu = sum(values)/N
    sigma = (sum((v - mu)**2 for v in values) / N)**(1/2)
    answers.append(dict(
      metric=metric_id,
      answer=mu,
      comment=f"sigma={sigma:0.2f} N={N}",
    ))
  #
  assessment = dict(
    rubric=rubric_id,
    answers=answers,
  )
  json.dump(assessment, output)

if __name__ == '__main__':
  summarize()
