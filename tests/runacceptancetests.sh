#! /bin/sh

SRCDIR="$PWD/.."
HELPERDIR="$PWD/helper"

export PATH="$SRCDIR:$HELPERDIR:$PATH"

cd acceptance
shut -r
