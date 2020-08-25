import os
from setuptools import setup, Extension

module = Extension('dijkstra', sources=['dijkstra_module.cpp'],
                   include_dirs=['.'], language='c++',extra_compile_args=['-std=c++11','-O3']) # , '-O3'

setup(name='dijkstra', ext_modules = [module])
