#! /bin/sh

SRCDIR="$PWD/.."
HELPERDIR="$PWD/helper"

export PYTHONPATH="$SRCDIR:$HELPERDIR:$PYTHONPATH"

./rununittests.py
