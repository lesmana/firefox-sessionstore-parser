#! /bin/sh

SRCDIR="$PWD"
HELPERDIR="$PWD/helpers"

export PATH="$SRCDIR:$HELPERDIR:$PATH"

cd tests_shell
shut -r
