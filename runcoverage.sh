#! /bin/sh

export COVERAGE_FILE=coveragedatafile

coverage run --branch runtests.py || exit 1

coverage report --show-missing

coverage html --directory=coveragehtmlreport
