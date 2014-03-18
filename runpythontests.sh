#! /bin/sh

SRCDIR="$PWD"
HELPERDIR="$PWD/testhelpers"

export PYTHONPATH="$SRCDIR:$HELPERDIR:$PYTHONPATH"

cd pytests
./runpythontests.py
