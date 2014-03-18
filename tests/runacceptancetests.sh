#! /bin/sh

SRCDIR="$PWD/.."
HELPERDIR="$PWD/../testhelpers"

export PATH="$SRCDIR:$HELPERDIR:$PATH"

cd acceptance
shut -r
