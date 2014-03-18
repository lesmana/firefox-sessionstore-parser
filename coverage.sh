#! /bin/sh

export COVERAGE_FILE=coveragedatafile

clean() {
  rm -f $COVERAGE_FILE
}

trap clean EXIT

coverage run --branch runpythontests.py || exit 1

coverage report --show-missing --omit="testhelpers/*"

if [ "$1" = "html" ]; then
  coverage html
  echo "coverage html done"
  echo "point browser to htmlcov/index.html"
fi
