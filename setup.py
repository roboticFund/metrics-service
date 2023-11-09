from setuptools import setup, find_packages

from roboticFundMetrics import __version__

setup(
    name='roboticFundMetrics',
    version=__version__,

    url='https://github.com/roboticFund/metrics-service',
    author='Roboticfund pty ltd',
    author_email='support@roboticfund.com.au',

    packages=find_packages(),
)
