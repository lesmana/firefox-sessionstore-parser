#! /bin/sh

SRCDIR="$PWD/.."
HELPERDIR="$PWD/../testhelpers"

export PATH="$SRCDIR:$HELPERDIR:$PATH"

cd shtests
shut -r
