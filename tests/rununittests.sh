#! /bin/sh

export PYTHONPATH=$PWD/..:$PWD/helper:$PWD:$PYTHONPATH

cd unit
./rununittests.py
