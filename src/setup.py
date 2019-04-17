import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="Bibchecker",
    version="0.0.1",
    author="Dabiao",
    author_email="zhaang.dabiao11@gmai.com",
    description="A small package for bibtex file consistency check.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/messcode/bibchecker",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)