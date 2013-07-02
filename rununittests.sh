#! /bin/sh

export PYTHONPATH=$PWD:$PYTHONPATH

cd tests/unit
./rununittests.py
