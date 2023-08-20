from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='LabAssist',
    version='0.1',  
    description='A package for automating titration analysis',
    author='ChronoVortex',
    author_email='your@email.com',
    install_requires=requirements,
    packages=find_packages(include=['app', 'app.*']),
)