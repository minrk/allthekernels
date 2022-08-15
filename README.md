# All the Kernels!

A Jupyter kernel that multiplexes all the kernels you have installed.

## Installation

1. Download and extract the contents of this repository or clone it with <code>git clone https://github.com/minrk/allthekernels.git</code>
2. Install with:

```
python3 -m pip install allthekernels
```
Or to do a dev install from source:
```
python3 -m pip install -e .
# manually install kernelspec in your environment, e.g.:
# mkdir ~/mambaforge/envs/allthekernels/share/jupyter/kernels/atk
# cp atk/kernel.json ~/mambaforge/envs/allthekernels/share/jupyter/kernels/atk
```

## Usage

Specify which kernel a cell should use with `>kernelname`.
If no kernel is specified, IPython will be used.

![atk](img/allthekernels.png)

([All the things source](http://hyperboleandahalf.blogspot.no/2010/06/this-is-why-ill-never-be-adult.html))

## Making a release

Anyone with push access to this repo can make a release.
We use [tbump][] to publish releases.

tbump updates version numbers and publishes the `git tag` of the version.
[Our GitHub Actions](https://github.com/minrk/allthekernels/actions)
then build the releases and publish them to PyPI.

The steps involved:

1. install tbump: `pip install tbump`
2. tag and publish the release `tbump $NEW_VERSION`.

That's it!

[tbump]: https://github.com/your-tools/tbump
