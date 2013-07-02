#! /bin/sh

export PYTHONPATH=$PWD/tests/helper:$PWD:$PYTHONPATH

cd tests/unit
./rununittests.py
