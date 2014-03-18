#! /bin/sh

SRCDIR="$PWD"
HELPERDIR="$PWD/testhelpers"

export PYTHONPATH="pytests:$SRCDIR:$HELPERDIR:$PYTHONPATH"

./runpythontests.py
