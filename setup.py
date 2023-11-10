from setuptools import setup, find_packages, find_namespace_packages

from src.roboticFundMetrics import __version__

setup(
    name='roboticFundMetrics',
    version=__version__,

    url='https://github.com/roboticFund/metrics-service',
    author='Roboticfund pty ltd',
    author_email='support@roboticfund.com.au',
    packages=find_packages('python'),
    package_dir={'src': 'python'},
    # packages=find_namespace_packages(),
)
