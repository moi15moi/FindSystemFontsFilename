import os
import re
import setuptools


here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = [\'\"](.+)[\'\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name="FindSystemFontsFilename",
    url="https://github.com/moi15moi/FindSystemFontsFilename/",
    project_urls={
        "Source": "https://github.com/moi15moi/FindSystemFontsFilename/",
        "Tracker": "https://github.com/moi15moi/FindSystemFontsFilename/issues/",
    },
    author="moi15moi",
    author_email="moi15moismokerlolilol@gmail.com",
    description="Find the system fonts filename.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    version=find_version("find_system_fonts_filename", "__init__.py"),
    packages=["find_system_fonts_filename"],
    python_requires=">=3.8",
    install_requires=[
        "comtypes; platform_system=='Windows'",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
    license="MIT",
)
