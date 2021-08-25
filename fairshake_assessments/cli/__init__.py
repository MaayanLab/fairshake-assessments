import click

@click.group()
def cli(): pass

import fairshake_assessments.cli.summarize
import fairshake_assessments.cli.publish

if __name__ == '__main__':
  cli()
