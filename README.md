ipyigv
===============================

A Jupyter wrapper for the igv.js library

Installation
------------

To install use pip:

    $ pip install ipyigv
    $ jupyter nbextension enable --py --sys-prefix ipyigv

To install for jupyterlab

    $ jupyter labextension install ipyigv

For a development installation (requires npm),

    $ git clone https://github.com//ipyigv.git
    $ cd ipyigv
    $ pip install -e .
    $ jupyter nbextension install --py --symlink --sys-prefix ipyigv
    $ jupyter nbextension enable --py --sys-prefix ipyigv
    $ jupyter labextension install js

When actively developing your extension, build Jupyter Lab with the command:

    $ jupyter lab --watch

This takes a minute or so to get started, but then automatically rebuilds JupyterLab when your javascript changes.

Note on first `jupyter lab --watch`, you may need to touch a file to get Jupyter Lab to open.

