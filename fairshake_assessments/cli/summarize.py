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
        summary[answer['metric']['@id']] = {'mu': 0., 'sigma': 0., 'N': 0}
      summary[answer['metric']['@id']]['mu'] += answer['answer']['value']
      summary[answer['metric']['@id']]['sigma'] += answer['answer']['value']**2
      summary[answer['metric']['@id']]['N'] += 1
  #
  answers = []
  for metric_id, metric in summary.items():
    metric['mu'] = metric['mu']/metric['N']
    metric['sigma'] = metric['sigma']**(1/2)
    answers.append(dict(
      metric=metric_id,
      answer=metric['mu'],
      comment=f"sigma={metric['sigma']:0.2f} N={metric['N']}",
    ))
  #
  assessment = dict(
    rubric=rubric_id,
    answers=answers,
  )
  json.dump(assessment, output)

if __name__ == '__main__':
  summarize()
