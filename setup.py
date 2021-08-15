"packaging"
from os.path import dirname, join

from setuptools import setup

package_name = "pdfforms"
base_dir = dirname(__file__)


def read(filename):
    "read file contents"
    with open(join(base_dir, filename)) as f:
        return f.read()


def get_version(package_name, default="0.1"):
    "read package version from python file"
    with open(join(base_dir, package_name, "version.py")) as f:
        for line in f:
            parts = line.split()
            if parts[:2] == ["__version__", "="]:
                return parts[2].strip("'\"")
    return default


setup(
    name=package_name,
    version=get_version(package_name),
    description="Populate fillable pdf forms from csv data file",
    long_description=read("README.rst") + "\n\n" + read("CHANGELOG.rst"),
    author="Aryeh Leib Taurog",
    author_email="python@aryehleib.com",
    license="MIT",
    url="https://github.com/altaurog/pdfforms",
    packages=[package_name],
    entry_points={"console_scripts": ["pdfforms=pdfforms.cli:main"]},
    install_requires=["pyexcel"],
    extras_require={
        "csv": ["pyexcel-io"],
        "xlsx": ["pyexcel-xlsx"],
        "ods": ["pyexcel-ods"],
    },
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: End Users/Desktop",
        "Environment :: Console",
        "Topic :: Office/Business",
    ],
)
