import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ftpshutil-renegat0x0",
    version="0.0.1",
    author="Piotr Zielinski",
    author_email="rozbujnik@gmail.com",
    description="Ftplib Shutil like functionality",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rumca-js/ftplibshutil",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    test_suite="ftpshutil.tests.test_all",
)
