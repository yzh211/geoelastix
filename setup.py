"""Setup script for GeoElastix."""

from setuptools import setup, find_packages
import os

# Read version from __version__.py
version = {}
with open(os.path.join("geoelastix", "__version__.py")) as f:
    exec(f.read(), version)

# Read README for long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="geoelastix",
    version=version["__version__"],
    author=version["__author__"],
    description="Geospatial image registration for landslide monitoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yzh211/geoelastix",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20",
        "scipy>=1.7",
        "matplotlib>=3.5",
        "pyyaml>=6.0",
        "reportlab>=3.6",
        "pillow>=9.0",
    ],
    entry_points={
        "console_scripts": [
            "geoelastix=geoelastix.cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "geoelastix": ["../parameters/*.txt"],
    },
    zip_safe=False,
)
