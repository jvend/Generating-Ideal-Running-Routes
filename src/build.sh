#!/bin/bash
if [ -d "./build" ]
then
    echo "Dir exists"
    rm -rf build
    rm dijkstra.so
fi
python setup.py build
cp build/lib.macosx-10.9-x86_64-3.7/dijkstra.cpython-37m-darwin.so ./dijkstra.so
