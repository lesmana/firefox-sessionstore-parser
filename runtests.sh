#! /bin/sh

PATH="$PWD:$PATH"

cd tests
./rununittests.sh
./runacceptancetests.sh
