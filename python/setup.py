from setuptools import setup, find_packages

setup(
  name='fairshake_assessments',
  version='0.1',
  url='https://github.com/maayanLab/fairshake-assessments/',
  author='Daniel J. B. Clarke',
  author_email='u8sand@gmail.com',
  long_description=open('../README.md', 'r').read(),
  license='Apache-2.0',
  install_requires=list(map(str.strip, open('requirements.txt', 'r').readlines())),
  packages=find_packages(),
)