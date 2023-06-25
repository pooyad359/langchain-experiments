from setuptools import setup, find_packages
from pathlib import Path

requirements = Path("requirements.txt").read_text().splitlines()
setup(
    name="paper_summary",
    version="0.1.0",
    description="A package for summarizing Arxive papers",
    author="Pooya Darvehei",
    author_email="pooya.darvehei@gmail.com",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
