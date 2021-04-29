# TA Toolkit

This pip package provides a utility to distribute grading load among TAs using
files downloaded from the UMD submit server. The pip package also includes
`mossum` as a dependency so Moss results are easier to analyze (specifically, 
it will install a personally modified version of `mossum`; you can change this
in `setup.py`).

## Why is this a pip package?

Before, this was a regular repository with the script in the root. This had the
consequence of creating a disaster zone of a repository, since student
submissions and other grading files were littered throughout the repository.
With a pip package, we can have one folder to develop the package and one
folder where everything else goes (read: a catastrophic mess).

## Prerequisites

You should have `pip` and `python3`. I'm not sure what version of Python is
needed, but given the scope of usage of this script, anybody who encounters
this will be using a sufficiently recent version of Python anyway. For what
it's worth, I'm using Python 3.8.

The `split_assgn` script itself has no dependencies other than stock Python.
All other dependencies are related to `mossum`.

If you're interested in using `mossum` you will also need to install
`graphviz`.

## Installation via pip (Recommended)

So you don't clutter your global pip, I would first create a virtual
environment. Then, to install, run

`pip install git+https://github.com/danzou56/tatoolkit@main`

and to update, run

`pip install -U --force-reinstall --no-deps git+https://github.com/danzou56/tatoolkit@main`

If you have the repository downloaded locally (perhaps because you're
performing modifications to my buggy code), to install, run

`pip install git+file:///absolute/path@branch`

and to update after committing modifications, run

`pip install -U --force-reinstall --no-deps git+file:///absolute/path@branch`

For example, I use

`pip install -U --force-reinstall --no-deps git+file:///home/dan/workspace/tatoolkit@main`

If a version change occurred, it is unecessary to include `--force-reinstall` and `--no-deps`

## Installation via Cloning

If you don't want to use pip, you can just clone the repository. You can then
directly run the `split_assgn` script in `bin`. Doing it this way won't install
any of the dependencies for `mossum`.

## Usage

Run

`split_assgn --help`

for usage.
