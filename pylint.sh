#! /bin/sh

pylint \
  --rcfile=/dev/null \
  --persistent=n \
  --disable=locally-disabled \
  --disable=missing-docstring \
  --disable=no-self-use \
  --disable=duplicate-code \
  --disable=too-few-public-methods \
  --disable=too-many-public-methods \
  --disable=star-args \
  --output-format=colorized \
  --reports=n \
  --indent-string='  ' \
  sessionstoreparser.py \
  tests_python
