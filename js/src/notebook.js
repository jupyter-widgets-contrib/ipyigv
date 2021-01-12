// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

// Some static assets may be required by the custom widget javascript. The base
// url for the notebook is not known at build time and is therefore computed
// dynamically.
__webpack_public_path__ = document.querySelector('body').getAttribute('data-base-url') + 'nbextensions/jupyter-ipyigv/';

module.exports = require('./index.js');
