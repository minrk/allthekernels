#!/usr/bin/env python
import os
import sys
import string

from setuptools import setup
from setuptools.command.bdist_egg import bdist_egg


class bdist_egg_disabled(bdist_egg):
    """Disabled version of bdist_egg

    Prevents setup.py install from performing setuptools' default easy_install,
    which it should never ever do.
    """
    def run(self):
        sys.exit("Aborting implicit building of eggs. Use `pip install .` to install from source.")


with open("README.md") as f:
    long_description = f.read()


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
    long_description_content_type="text/markdown",
    url="https://github.com/minrk/allthekernels",
    py_modules=['allthekernels'],
    data_files=[('share/jupyter/kernels/atk', ['atk/kernel.json'])],
    license="MIT",
    cmdclass={"bdist_egg": bdist_egg_disabled},
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        'ipykernel>=6.0',
        'jupyter-client>=5.0',
        'pyzmq>=15.2',
        'tornado>=5',
    ],
)


def kernelspec(executable):
    with open(os.path.join(here, 'atk', 'kernel.json.tpl')) as input_file:
        template = string.Template(input_file.read())
        text = template.safe_substitute({ 'python': executable })
    with open(os.path.join(here, 'atk', 'kernel.json'), 'w') as output_file:
        output_file.write(text)


# When building a wheel, the executable specified in the kernelspec is simply 'python'.
if any(a.startswith('bdist') for a in sys.argv):
    kernelspec(executable='python')

# When installing, the kernel executable path is set to `sys.executable`.
if any(a.startswith(("install", "develop")) for a in sys.argv):
    kernelspec(executable=sys.executable)


if __name__ == "__main__":
    setup(**setup_args)
