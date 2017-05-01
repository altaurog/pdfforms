from os.path import join, dirname
from setuptools import setup

package_name = "pdfforms"
package_version = "1.0.0"
base_dir = dirname(__file__)

def read(filename):
    f = open(join(base_dir, filename))
    return f.read()

setup(
    name = package_name,
    version = package_version,
    description = "Populate fillable pdf forms from csv data file",
    long_description = read("README.rst") + '\n\n' + read("CHANGELOG.rst"),
    author = "Aryeh Leib Taurog",
    author_email = "python@aryehleib.com",
    license = 'MIT',
    url = "https://github.com/altaurog/pdfforms",
    packages = [package_name],
    entry_points = {'console_scripts': ['pdfforms=pdfforms.pdfforms:main']},
    classifiers = [
        "Programming Language :: Python :: 3.6",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: End Users/Desktop",
        "Environment :: Console",
        "Topic :: Office/Business",
    ],
)
