import json
import ipywidgets as widgets

from ipywidgets.widgets.trait_types import InstanceDict

from traitlets import (
    Float, Unicode, Int, Tuple, List, Instance, Bool, Dict, Enum,
    link, observe, default, validate, TraitError, Union, HasTraits
)

from traitlets.utils.bunch import Bunch

from .options import *

from .utils import widget_serialization_no_none
from ._version import EXTENSION_VERSION

PUBLIC_GENOMES_FILE = os.path.join(os.path.dirname(__file__), 'public_genomes.json')
PUBLIC_GENOMES = Bunch({v['id']: v for v in json.load(open(PUBLIC_GENOMES_FILE, 'r')) } )


@widgets.register
class IgvBrowser(widgets.DOMWidget):
    """An IGV browser widget."""


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.on_msg(self._custom_message_handler)

    out = widgets.Output()

    # Name of the widget view class in front-end
    _view_name = Unicode('IgvBrowser').tag(sync=True)
    # Name of the widget model class in front-end
    _model_name = Unicode('IgvModel').tag(sync=True)
    # Name of the front-end module containing widget view
    _view_module = Unicode('ipyigv').tag(sync=True)
    # Name of the front-end module containing widget model
    _model_module = Unicode('ipyigv').tag(sync=True)
    # Version of the front-end module containing widget view
    _view_module_version = Unicode(EXTENSION_VERSION).tag(sync=True)
    # Version of the front-end module containing widget model
    _model_module_version = Unicode(EXTENSION_VERSION).tag(sync=True)

    # Widget specific property.
    # Widget properties are defined as traitlets. Any property tagged with `sync=True`
    # is automatically synced to the frontend *any* time it changes in Python.
    # It is synced back to Python from the frontend *any* time the model is touched.
    genome = InstanceDict(ReferenceGenome).tag(sync=True, **widget_serialization_no_none)
    tracks = List(InstanceDict(Track)).tag(sync=True, **widget_serialization_no_none)
    doubleClickDelay = Int(default_value=500).tag(sync=True)
    flanking = Int(default_value=1000).tag(sync=True)
    genomeList = Unicode(allow_none=True).tag(sync=True, **widget_serialization_no_none)  # optional URL
    locus = (Unicode() | List(Unicode())).tag(sync=True, **widget_serialization_no_none)
    minimumBases = Int(default_value=40).tag(sync=True)
    queryParametersSupported = Bool(default=False).tag(sync=True)
    search = InstanceDict(SearchService, allow_none=True).tag(sync=True, **widget_serialization_no_none)
    showAllChromosomes = Bool(default_value=True).tag(sync=True)
    showAllChromosomeWidget = Bool(default_value=True).tag(sync=True)
    showNavigation = Bool(default_value=True).tag(sync=True)
    showSVGButton = Bool(default_value=False).tag(sync=True)
    showRuler = Bool(default_value=True).tag(sync=True)
    showCenterGuide = Bool(default_value=False).tag(sync=True)
    # trackDefaults = # missing documentation
    roi = List(InstanceDict(AnnotationTrack)).tag(sync=True, **widget_serialization_no_none) # regions of interest
    oauthToken = Unicode(allow_none = True).tag(sync=True)
    apiKey = Unicode(allow_none = True).tag(sync=True)
    clientId = Unicode(allow_none = True).tag(sync=True)

    def add_track(self, track):
        # List subscript does not work for empty List, so handling this case manually.
        if len(self.tracks) == 0:
            self.tracks = [track]
        else:
            self.tracks = self.tracks[:] + [track]

    def remove_track(self, track):
        self.tracks = [t for t in self.tracks if t != track]

    def add_roi(self, roi):
        # List subscript does not work for empty List, so handling this case manually.
        if len(self.roi) == 0:
            self.roi = [roi]
        else:
            self.roi = self.roi[:] + [roi]

    def remove_all_roi(self):
        self.roi = []

    def search(self, symbol):
        self.send({"type": "search", "symbol": symbol})
        print("Search completed. Check the widget instance for results.")

    def dump_json(self):
        print("Dumping browser configuration to browser.out")
        self.send({"type": "dump_json"})

    @out.capture()
    def _custom_message_handler(self, _, content, buffers):
        if content.get('event', '') == 'return_json':
            self._return_json_handler(content)

    @out.capture()
    def _return_json_handler(self, content):
        print (content['json'])


    # @validate('roi')
    # def _valid_roi(self, roi):
    #     if isinstance(roi, AnnotationTrack)):
    #         return roi
    #     else:
    #         print("validating roi: type %s", type(roi))
    #         raise TraitError("Regions of Interest must be of type AnnotationTrack")
