#!/usr/bin/env python
import glob
import os
import sys

from distutils.core import setup

long_description = """
Multiplexing kernel for Jupyter

Use all your kernels in a single notebook.
Specify which kernel each should run by starting the cell with

>kernel-name
"""

version_ns = {}
with open('allthekernels.py') as f:
    for line in f:
        if line.startswith('__version__'):
            exec(line, version_ns)

here = os.path.dirname(__file__)

setup_args = dict(
    name='allthekernels',
    version=version_ns['__version__'],
    author="Min RK",
    author_email="benjaminrk@gmail.com",
    description="Multiplexing kernel for Jupyter",
    long_description=long_description,
    url="https://github.com/minrk/allthekernels",
    py_modules=['allthekernels'],
    data_files=[('share/jupyter/kernels/atk', glob.glob('atk/*'))],
    license="MIT",
    cmdclass={},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        'ipykernel>=4.3',
        'jupyter-client>=5.0',
        'pyzmq>=15.2',
        'tornado>=4',
    ],
)

if 'bdist_wheel' in sys.argv:
    from wheel.bdist_wheel import bdist_wheel
    setup_args['cmdclass']['bdist_wheel'] = bdist_wheel

if __name__ == '__main__':
    setup(**setup_args)
