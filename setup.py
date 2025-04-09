#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="peopleanalytics",
    version="0.1.0",
    description="A tool for analyzing 360-degree evaluations and generating reports",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "rich>=10.0.0",
        "openpyxl>=3.0.0",
        "plotly>=5.0.0",
    ],
    entry_points={
        "console_scripts": [
            "peopleanalytics=peopleanalytics.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
) 