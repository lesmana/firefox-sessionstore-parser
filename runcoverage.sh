#! /bin/sh

export COVERAGE_FILE=coveragedatafile

coverage run --branch --omit="helpers/*,*/yaml/*" runtests_python.py || exit 1

coverage report --show-missing

coverage html --directory=coveragehtmlreport
