
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
First, make sure you have been added as a collaborator [here](https://pypi.org/manage/project/python-elemental/collaboration/).
Manually increase the version [here](https://github.com/cbsinteractive/elemental/blob/master/pyproject.toml#L3) and run

    poetry publish
