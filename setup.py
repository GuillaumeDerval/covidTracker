
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='covidbelgium',
    version='0.0.1',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/pypa/sampleproject',
    author='UCLouvain/INGI - Céline Deknop, Guillaume Derval, Axel Legay, Pierre Schaus',
    author_email='guillaume.derval@uclouvain.be',
    packages=find_packages(where='src'),
    python_requires='>=3.4',
    install_requires=['Flask', 'Flask-Babel', "sqlalchemy", "flask-wtf"],
)