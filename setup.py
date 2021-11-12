import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyDAQHAT",
    version="0.0.1",
    author='Nick Sadovnikov',
    author_email='nysadov@gmail.com',
    url='https://github.com/uwasystemhealth/PyDAQHAT',
    description=("Python module to communicate with a MCC 172 DAQ HAT."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)