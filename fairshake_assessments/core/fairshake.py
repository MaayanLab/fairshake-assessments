import json
from pyswaggerclient import SwaggerClient

def get_fairshake_client(
  api_key=None,
  username=None,
  email=None,
  password=None,
):
  ''' Using either the api_key directly, or with fairshake
  user credentials, create an authenticated swagger client to fairshake.
  '''
  fairshake = SwaggerClient(
    'https://fairshake.cloud/swagger?format=openapi',
  )
  if not api_key:
    fairshake_auth = fairshake.actions.auth_login_create.call(data=dict({
      'username': username,
      'password': password,
    }, **({'email': email} if email else {})))
    api_key = fairshake_auth['key']
  # FAIRshake expects a Token in the Authorization request header for
  #  authenticated calls
  fairshake.update(
    headers={
      'Authorization': 'Token ' + api_key,
    }
  )
  return fairshake

def find_or_create_fairshake_digital_object(
  fairshake=None,
  url='',
  title='',
  description='',
  image='',
  type='any',
  tags='',
  projects=[],
  rubrics=[],
):
  ''' Register a digital object in FAIRshake
  '''
  try:
    existing = fairshake.actions.digital_object_list.call(
      url_strict=url,
    )['results']
  except:
    existing = []
  #
  if len(existing) > 1:
    objs = dict(enumerate(existing))
    print('Duplicate urls found:', *['\t[{}]: {}'.format(n, json.dumps(obj)) for n, obj in objs.items()], '', sep='\n')
    obj = None
    while obj is None:
      print('Select relevant object: ', end='')
      obj = objs.get(int(input().strip()))
  elif len(existing) == 1:
    obj = existing[0]
  elif len(existing) == 0:
    obj = fairshake.actions.digital_object_create.call(
      data=dict(
        url=url,
        title=title,
        description=description,
        image=image,
        type=type,
        tags=','.join(map(str, tags)) if type(tags) == list else str(tags),
        projects=[project['@id'] if type(project) == dict else project for project in projects],
        rubrics=[rubric['@id'] if type(rubric) == dict else rubric for rubric in rubrics],
      )
    )
  #
  return obj


def publish_fairshake_assessment(
  fairshake=None,
  target=None,
  rubric=None,
  project=None,
  answers=None,
  published=True,
  methodology='auto',
):
  ''' Publish an assessment in FAIRshake
  '''
  return fairshake.actions.assessment_create.call(
    data=dict(
      target=target['@id'] if type(target) == dict else target,
      rubric=rubric['@id'] if type(rubric) == dict else rubric,
      project=project['@id'] if type(project) == dict else project,
      answers=answers,
      published=published,
      methodology=methodology,
    )
  )


def fairshake_prompt_digital_object_new():
  import click
  click.echo('Register the digital object being assessed.')
  title = click.prompt('Title', type=str)
  description = click.prompt('Description', type=str)
  image = click.prompt('Image', type=str, default='')
  tags = click.prompt('Tags', type=str, default='')
  return dict(title=title, description=description, image=image, tags=tags)

def fairshake_prompt_digital_object_choose(values):
  import click
  if len(values) == 0: return None
  elif len(values) == 1: return values[0]
  else:
    choices = {
      chr(ord('a')+i): value
      for i, value in enumerate(values)
    }
    click.echo(yaml.dump(choices))
    choice = click.prompt('Digital object ([a], ..., [k], [n]ew, [1..] Digital Object ID)', type=str)
    if choice in choices:
      return choices[choice]
    elif choice == 'n':
      return fairshake_prompt_digital_object_new()
    else:
      return dict(id=int(choice))

def fairshake_prompt_digital_object(fairshake, rubric_id=None, project_id=None):
  import click
  url = click.prompt('Digital object URL (or ID)', type=str)
  #
  try: return dict(id=int(url))
  except: pass
  #
  try: existing = fairshake.actions.digital_object_list.call(url=url)['results']
  except: existing = []
  #
  if existing: digital_object = dict(url=url, **fairshake_prompt_digital_object_choose(existing))
  else: digital_object = dict(url=url, **fairshake_prompt_digital_object_new())
  #
  if 'id' not in digital_object:
    digital_object = fairshake.actions.digital_object_create.call(
      data=dict(
        digital_object,
        projects=digital_object.get('projects', []) if project_id is None else list(set(digital_object.get('projects', [])) | {project_id}),
        rubrics=digital_object.get('rubrics', []) if rubric_id is None else list(set(digital_object.get('rubrics', [])) | {rubric_id}),
      ),
    )
  #
  return digital_object
