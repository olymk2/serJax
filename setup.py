from setuptools import setup, find_packages


with open('README.org') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

requirements = [
    'flask',
    'flask-restful',
    'requests',
    'zeroconf',
    'pyserial'
]


setup(
    name='serjax',
    version='0.2.1',
    description='Turns your serial port into an API',
    long_description=readme,
    author='Oliver Marks',
    author_email='oly@digitaloctave.com',
    url='https://github.com/olymk2/serJax',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=requirements,
    setup_requires=['pytest-runner'],
    tests_require=['pytest-cov', 'pytest', 'mock']
)
