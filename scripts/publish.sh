#!/bin/bash

set -e
set -x

version=$(git describe --tags --abbrev=0)
poetry version "${version}"
poetry publish --build
