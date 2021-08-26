import yaml
import json
import click
from fairshake_assessments.cli import cli
from fairshake_assessments.core.fairshake import get_fairshake_client, fairshake_prompt_digital_object

@cli.command()
@click.option(
  '-i', '--input',
  type=click.File('r'),
  help='Summarized assessment to upload to FAIRshake',
)
@click.option(
  '--api-key', envvar='FAIRSHAKE_API_KEY',
  type=str,
  help='FAIRshake API Key',
  prompt='Please provide your fairshake API key (obtainable from https://fairshake.cloud/accounts/api_access/)',
)
@click.option(
  '--target-id',
  type=int,
  help='Digital object ID being assessed',
)
@click.option(
  '--project-id',
  type=int, default=None,
  help='FAIRshake project id',
)
def publish(input, api_key, target_id, project_id):
  assessment = json.load(input)
  rubric_id = assessment['rubric']
  answers = assessment['answers']
  fairshake = get_fairshake_client(api_key=api_key)
  if not target_id: digital_object = fairshake_prompt_digital_object()
  #
  click.echo('Using')
  click.echo(yaml.dump(digital_object))
  #
  assessment = dict(
    target=digital_object['id'],
    rubric=rubric_id,
    project=project_id,
    answers=answers,
    published=True,
    methodology='auto',
  )
  click.echo(yaml.dump(assessment))
  click.echo(fairshake.actions.assessment_create.call(
    data=assessment
  ))

if __name__ == '__main__':
  publish()
