from distutils.core import setup

setup(
    name='pywp',
    version='1.0.0',
    author='Eric Stein',
    author_email='toba@des.truct.org',
    packages=['pywp'],
    url='https://github.com/eastein/pywp',
    license='LICENSE',
    description='Library for accessing NOAA / National Weather Service DWML forecasts',
    long_description=open('README.txt').read(),
    install_requires=[
        'requests',
        'pytz',
        'python-dateutil'
    ]
)
