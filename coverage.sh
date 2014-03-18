#! /bin/sh

export COVERAGE_FILE=coveragedatafile

clean() {
  rm -f $COVERAGE_FILE
}

trap clean EXIT

coverage run --branch runpythontests.py &&
  coverage report --show-missing --omit="testhelpers/*"
