import json

from ipywidgets import DOMWidget, Output, Widget, register, widget_serialization
from ipywidgets.widgets.trait_types import InstanceDict

from traitlets import Unicode, Int, List, Instance, Bool, validate, TraitError
from traitlets.utils.bunch import Bunch

from .options import *

from ._version import EXTENSION_VERSION

PUBLIC_GENOMES_FILE = os.path.join(os.path.dirname(__file__), 'public_genomes.json')
PUBLIC_GENOMES = Bunch({v['id']: v for v in json.load(open(PUBLIC_GENOMES_FILE, 'r')) } )


@register
class IgvBrowser(DOMWidget):
    """An IGV browser widget."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.on_msg(self._custom_message_handler)

    out = Output()

    _view_name = Unicode('IgvBrowser').tag(sync=True)
    _model_name = Unicode('IgvModel').tag(sync=True)
    _view_module = Unicode('jupyter-igv').tag(sync=True)
    _model_module = Unicode('jupyter-igv').tag(sync=True)
    _view_module_version = Unicode(EXTENSION_VERSION).tag(sync=True)
    _model_module_version = Unicode(EXTENSION_VERSION).tag(sync=True)

    # Widget-specific property.
    # Widget properties are defined as traitlets. Any property tagged with `sync=True`
    # is automatically synced to the frontend *any* time it changes in Python.
    # It is synced back to Python from the frontend *any* time the model is touched.
    genome = InstanceDict(ReferenceGenome).tag(sync=True, **widget_serialization)
    tracks = List(InstanceDict(Track)).tag(sync=True, **widget_serialization)
    doubleClickDelay = Int(default_value=500).tag(sync=True)
    flanking = Int(default_value=1000).tag(sync=True)
    genomeList = Unicode(allow_none=True).tag(sync=True, **widget_serialization)  # optional URL
    locus = (Unicode() | List(Unicode())).tag(sync=True, **widget_serialization)
    minimumBases = Int(default_value=40).tag(sync=True)
    queryParametersSupported = Bool(default=False).tag(sync=True)
    search = InstanceDict(SearchService, allow_none=True).tag(sync=True, **widget_serialization)
    showAllChromosomes = Bool(default_value=True).tag(sync=True)
    showAllChromosomeWidget = Bool(default_value=True).tag(sync=True)
    showNavigation = Bool(default_value=True).tag(sync=True)
    showSVGButton = Bool(default_value=False).tag(sync=True)
    showRuler = Bool(default_value=True).tag(sync=True)
    showCenterGuide = Bool(default_value=False).tag(sync=True)
    # trackDefaults = # missing documentation
    roi = List(InstanceDict(AnnotationTrack)).tag(sync=True, **widget_serialization) # regions of interest
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

