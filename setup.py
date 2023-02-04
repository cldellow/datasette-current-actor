from setuptools import setup
import os

VERSION = "0.1"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-current-actor",
    description="Adds a current_actor() function to SQLite that show's the current actor's ID.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Colin Dellow",
    url="https://github.com/cldellow/datasette-current-actor",
    project_urls={
        "Issues": "https://github.com/cldellow/datasette-current-actor/issues",
        "CI": "https://github.com/cldellow/datasette-current-actor/actions",
        "Changelog": "https://github.com/cldellow/datasette-current-actor/releases",
    },
    license="Apache License, Version 2.0",
    classifiers=[
        "Framework :: Datasette",
        "License :: OSI Approved :: Apache Software License"
    ],
    version=VERSION,
    packages=["datasette_current_actor"],
    entry_points={"datasette": ["current_actor = datasette_current_actor"]},
    install_requires=["datasette"],
    extras_require={"test": ["pytest", "pytest-asyncio", "pytest-watch"]},
    python_requires=">=3.7",
)
