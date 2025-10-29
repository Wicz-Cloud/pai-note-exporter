"""Setup configuration for pai-note-exporter."""

from setuptools import find_packages, setup

setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
