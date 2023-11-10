from setuptools import setup, find_packages, find_namespace_packages

from src.roboticFundMetrics import __version__

setup(
    name='roboticFundMetrics',
    version=__version__,

    url='https://github.com/roboticFund/metrics-service',
    author='Roboticfund pty ltd',
    author_email='support@roboticfund.com.au',
    # packages=['src.roboticFundMetrics', 'src.utils']
    packages=find_packages('src'),
    package_dir={'': 'src'}
)
