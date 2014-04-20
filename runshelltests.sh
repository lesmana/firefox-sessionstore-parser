#! /bin/sh

SRCDIR="$PWD"
HELPERDIR="$PWD/testhelpers"

export PATH="$SRCDIR:$HELPERDIR:$PATH"

cd tests_shell
shut -r
