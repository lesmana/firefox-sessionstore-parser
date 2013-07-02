#! /bin/sh

PATH="$PWD:$PATH"

./rununittests.sh

cd tests
./runacceptancetests.sh
