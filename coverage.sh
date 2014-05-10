#! /bin/sh

export COVERAGE_FILE=coveragedatafile

coverage run --branch --omit="helpers/*,*/yaml/*" runpythontests.py || exit 1

coverage report --show-missing

coverage html --directory=coveragehtmlreport
