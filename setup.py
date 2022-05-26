from setuptools import setup, find_packages
from setuptools.dist import Distribution as _Distribution
from subyo import __name__, __version__


class Distribution(_Distribution):
    def is_pure(self): return True


setup(
    name=__name__,
    version=__version__,
    author='cacko',
    author_email='cacko@cacko.net',
    distclass=Distribution,
    url='http://pypi.cacko.net/simple/subyo/',
    description='whatever',
    install_requires=[
        "transformers >= 4.18.0",
        "click >= 8.1.2",
        "torch >= 1.11.0",
        "pydub >= 0.25.1",
        "datasets >= 2.0.0",
        "numpy >= 1.22.3",
        "moviepy >= 1.0.3",
        "stringcase >= 1.2.0",
        "torchaudio >= 0.11.0",
        "sentencepiece >= 0.1.96"
    ],
    setup_requires=['wheel'],
    python_requires=">=3.10",
    packages=find_packages(include=['subyo', 'subyo.*']),
    entry_points="""
        [console_scripts]
        subyo=subyo.cli:cli
    """,
)