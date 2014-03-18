#! /bin/sh

SRCDIR="$PWD"
HELPERDIR="$PWD/testhelpers"

export PYTHONPATH="$SRCDIR:$HELPERDIR:$PYTHONPATH"

./runpythontests.py
