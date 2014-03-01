#! /bin/sh

SRCDIR="$PWD/.."
HELPERDIR="$PWD/helper"

export PYTHONPATH="$SRCDIR:$HELPERDIR:$PYTHONPATH"

cd unit
./rununittests.py
