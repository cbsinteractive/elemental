
# Elemental

[![continuous integration status](https://github.com/cbsinteractive/elemental/workflows/CI/badge.svg)](https://github.com/cbsinteractive/elemental/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/cbsinteractive/elemental/branch/master/graph/badge.svg?token=qFdUKsI2tD)](https://codecov.io/gh/cbsinteractive/elemental)


Python Client for Elemental On-Premises Appliances

## Run Tests

Before running tests locally, install `tox` and `poetry`.

    pipx install tox
    pipx install poetry

Run tests using

    make test

To run lint, use

    make lint

## Release Updated Version
Use the Github UI to [create a new release](https://github.com/cbsinteractive/elemental/releases/new), the tag needs
to follow the semver format `0.0.0`. After the new release is created, a Github workflow will build and publish the
new python package to PyPI automatically.
