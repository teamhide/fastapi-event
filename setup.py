# encoding: utf-8
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fastapi-event",
    version="0.1.0",
    author="Hide",
    author_email="padocon@naver.com",
    description="Event dispatcher for FastAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/teamhide/fastapi-event",
    packages=setuptools.find_packages(),
    install_requires=[
        "fastapi",
        "pydantic",
    ],
    tests_require=['pytest'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)