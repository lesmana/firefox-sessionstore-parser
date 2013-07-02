#! /bin/sh

SRCDIR="$PWD/.."
HELPERDIR="$PWD/helper"

export PYTHONPATH="$SRCDIR:$HELPERDIR:$PATH"

cd unit
./rununittests.py
