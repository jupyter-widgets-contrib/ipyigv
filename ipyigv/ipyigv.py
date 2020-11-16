import json
import ipywidgets as widgets

from ipywidgets.widgets.trait_types import InstanceDict

from traitlets import (
    Float, Unicode, Int, Tuple, List, Instance, Bool, Dict, Enum,
    link, observe, default, validate, TraitError, Union, HasTraits
)

from traitlets.utils.bunch import Bunch

from .options import ReferenceGenome, Track

from .utils import widget_serialization_no_none

# See js/lib/example.js for the frontend counterpart to this file.

PUBLIC_GENOMES_FILE = 'public_genomes.json'
PUBLIC_GENOMES = Bunch({v['id']: v for v in json.load(open(PUBLIC_GENOMES_FILE, 'r')) } )


@widgets.register
class IgvBrowser(widgets.DOMWidget):
    """An IGV browser widget."""

    # Name of the widget view class in front-end
    _view_name = Unicode('IgvBrowser').tag(sync=True)
    # Name of the widget model class in front-end
    _model_name = Unicode('IgvModel').tag(sync=True)
    # Name of the front-end module containing widget view
    _view_module = Unicode('ipyigv').tag(sync=True)
    # Name of the front-end module containing widget model
    _model_module = Unicode('ipyigv').tag(sync=True)
    # Version of the front-end module containing widget view
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    # Version of the front-end module containing widget model
    _model_module_version = Unicode('^0.1.0').tag(sync=True)

    # Widget specific property.
    # Widget properties are defined as traitlets. Any property tagged with `sync=True`
    # is automatically synced to the frontend *any* time it changes in Python.
    # It is synced back to Python from the frontend *any* time the model is touched.
    genome = InstanceDict(ReferenceGenome).tag(sync=True, **widget_serialization_no_none)
    tracks = List(InstanceDict(Track)).tag(sync=True, **widget_serialization_no_none)

    def add_track(self, track):
        # List subscript does not work for enpty List, so handling this case manually.
        if len(self.tracks) == 0:
            self.tracks = [track]
        else:
            self.tracks = self.tracks[:] + [track]

    def remove_track(self, track):
        self.tracks = [t for t in self.tracks if t != track]
