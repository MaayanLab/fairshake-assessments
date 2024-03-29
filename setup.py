from setuptools import setup, find_packages

requirements = list(map(str.strip, open('requirements.txt', 'r').readlines()))

setup(
  name='fairshake_assessments',
  version='0.0.2',
  url='https://github.com/maayanLab/fairshake-assessments/',
  author='Daniel J. B. Clarke',
  author_email='u8sand@gmail.com',
  long_description=open('README.md', 'r').read(),
  license='Apache-2.0',
  packages=find_packages(exclude=('example',)),
  install_requires=[requirement for requirement in requirements if '://' not in requirement],
  dependency_links=[requirement for requirement in requirements if '://' in requirement],
  entry_points={
    'console_scripts': ['fairshake-assessments=fairshake_assessments.cli.__main__:cli'],
  }
)
