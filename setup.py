from __future__ import print_function
from setuptools import setup, find_packages
import os
from os.path import join as pjoin
from distutils import log

from jupyter_packaging import (
    create_cmdclass,
    install_npm,
    ensure_targets,
    combine_commands,
    get_version,
)

#
here = os.path.dirname(os.path.abspath(__file__))

log.set_verbosity(log.DEBUG)
log.info('setup.py entered')
log.info('$PATH=%s' % os.environ['PATH'])

name = 'ipyigv'
LONG_DESCRIPTION = 'A Jupyter wrapper for the igv.js library'

# Get ipyigv version
version = get_version(pjoin(name, '_version.py'))

js_dir = pjoin(here, 'js')

# Representative files that should exist after a successful build
jstargets = [
    pjoin(js_dir, 'dist', 'index.js'),
]

data_files_spec = [
    ('share/jupyter/nbextensions/jupyter-ipyigv', 'ipyigv/nbextension', '*.*'),
    ('share/jupyter/labextensions/jupyter-ipyigv', 'ipyigv/labextension', '**'),
    ('etc/jupyter/nbconfig/notebook.d', '.', 'jupyter-ipyigv.json'),
]

cmdclass = create_cmdclass('jsdeps', data_files_spec=data_files_spec)
cmdclass['jsdeps'] = combine_commands(
    install_npm(js_dir, build_cmd='build'),
    ensure_targets(jstargets),
)

setup_args = dict(
    name=name,
    version=version,
    description='A Jupyter wrapper for the igv.js library',
    long_description=LONG_DESCRIPTION,
    include_package_data=True,
    install_requires=[
        'ipywidgets>=7.6.0,<8',
        'spectate'
    ],
    extras_require={
        "test": ["pytest>4.6"]
    },
    packages=find_packages(),
    zip_safe=False,
    cmdclass=cmdclass,
    author='Project Jupyter',
    author_email='jeandavid.harrouet@hopsys.com',
    url='https://github.com/QuantStack/ipyigv',
    keywords=[
        'ipython',
        'jupyter',
        'widgets',
    ],
    package_data={'ipyigv': ['public_genomes.json']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Multimedia :: Graphics',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)

setup(**setup_args)
