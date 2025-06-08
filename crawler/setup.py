from setuptools import find_packages, setup

setup(
    name="crawler",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "scrapy",
        "behave",
        "requests",
        "lxml",
        "cssselect",
    ],
)
