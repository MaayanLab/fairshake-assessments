import yaml
import json
import click
from fairshake_assessments.cli import cli
from fairshake_assessments.core.fairshake import get_fairshake_client

def prompt_object_info():
  click.echo('Register the digital object being assessed.')
  title = click.prompt('Title', type=str)
  description = click.prompt('Description', type=str)
  image = click.prompt('Image', type=str, default='')
  tags = click.prompt('Tags', type=str, default='')
  return dict(title=title, description=description, image=image, tags=tags)

def choose(values):
  if len(values) == 0: return None
  elif len(values) == 1: return values[0]
  else:
    choices = {
      i: value
      for i, value in enumerate(values, start=1)
    }
    click.echo(yaml.dump(choices))
    choices = {str(k): (lambda: v) for k, v in choices.items()}
    choices['create'] = prompt_object_info
    choice = click.prompt('Selection', type=click.Choice(choices.keys()))
    return choices[choice]()

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
  '--url',
  type=str,
  help='Digital object URL being assessed',
  prompt=True,
)
@click.option(
  '--project-id',
  type=int, default=None,
  help='FAIRshake project id',
)
def publish(input, api_key, url, project_id):
  assessment = json.load(input)
  rubric_id = assessment['rubric']
  answers = assessment['answers']
  fairshake = get_fairshake_client(api_key=api_key)
  try:
    existing = fairshake.actions.digital_object_list.call(
      url=url,
    )['results']
  except:
    existing = []
  #
  if existing:
    digital_object = choose(existing)
  else:
    digital_object = dict(**prompt_object_info(), url=url)
  #
  if 'id' not in digital_object:
    digital_object = fairshake.actions.digital_object_create.call(
      data=dict(
        digital_object,
        projects=[] if project_id is None else [project_id],
        rubrics=[] if rubric_id is None else [rubric_id],
      ),
    )
  else:
    click.echo('Using:', yaml.dump(digital_object))
  #
  fairshake.actions.assessment_create.call(
    target=digital_object['id'],
    rubric=rubric_id,
    project=project_id,
    answers=answers,
    published=True,
    methodology='auto',
  )

if __name__ == '__main__':
  publish()
