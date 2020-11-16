import os
from urllib.parse import urlparse

from spectate import mvc

from traitlets import (
    Float, Unicode, Int, Tuple, List, Instance, Bool, Dict, Enum,
    link, observe, default, validate, TraitError, Union, HasTraits, TraitType
)

from ipywidgets import Widget, register
from ipywidgets.widgets.trait_types import Color, InstanceDict
from ipywidgets.widgets import widget

from .utils import widget_serialization_no_none



# NB '.txt' considered annotation as it is used in the public genomes. But not as per the doc.
TRACK_FILE_TYPES = { \
        'annotation': [ '.txt', \
            '.bed', '.gff', '.gff3', '.gtf', '.genePred', '.genePredExt', \
            '.peaks', '.narrowPeak', '.broadPeak', '.bigBed', '.bedpe' \
            ],
        'wig': ['.wig', '.bigWig', '.bedGraph'],
        'alignment': ['.bam'],
        'variant': ['.vcf'],
        'seg': ['.seg']
        }


class FieldColors(HasTraits):
    field = Unicode()
    palette = Dict(key_trait=Unicode, value_trait=Instance(Color))


@register
class Track(Widget):
    """
    A class reflecting the common fields of a track as per igv documentation.
    https://github.com/igvteam/igv.js/wiki/Tracks-2.0
    """

    # Name of the widget view class in front-end
    _view_name = Unicode('TrackView').tag(sync=True)
    # Name of the widget model class in front-end
    _model_name = Unicode('TrackModel').tag(sync=True)
    # Name of the front-end module containing widget view
    _view_module = Unicode('ipyigv').tag(sync=True)
    # Name of the front-end module containing widget model
    _model_module = Unicode('ipyigv').tag(sync=True)
    # Version of the front-end module containing widget view
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    # Version of the front-end module containing widget model
    _model_module_version = Unicode('^0.1.0').tag(sync=True)


    def __new__(cls, **kwargs):
        if cls is Track:
            # we must infer the type to instantiate the right Track type
            trackType = kwargs.get('type', None)
            if trackType is None:
                # then type is inferred from the file extension
                url = kwargs.get('url')
                path = urlparse(url).path
                filename, filetype = os.path.splitext(path)
                if filetype == '.gz':  # some files might be compressed
                    innerfilename, innerfiletype = os.path.splitext(filename)
                    filetype = innerfiletype
                for k, v in TRACK_FILE_TYPES.items():
                    if filetype in v:
                        trackType = k
                        break
            if trackType == 'annotation':
                return super(Track, cls).__new__(AnnotationTrack)
            elif trackType == 'alignment':
                return super(Track, cls).__new__(AlignmentTrack)
            else:
                print("WARNING: could not infer the type of track from the provided data. Instantiating a generic Track.")
                return super(Track, cls).__new__(cls)
        else:
            return super(Track, cls).__new__(cls)

    # These fields are common to all Track types
    sourceType = Unicode(default_value='file').tag(sync=True)  #
    format = Unicode().tag(sync=True)  # missing documentation
    name = Unicode().tag(sync=True)
    url = Unicode().tag(sync=True)
    indexURL = Unicode().tag(sync=True)
    indexed = Bool(default_value=False).tag(sync=True)
    order = Int().tag(sync=True)
    color = Unicode().tag(sync=True).tag(sync=True)
    height = Int(default_value=50).tag(sync=True)
    autoHeight = Bool(default_value=False).tag(sync=True)
    minHeight = Int(default_value=50).tag(sync=True)
    maxHeight = Int(default_value=500).tag(sync=True)
    # visibilityWindow = # missing documentation
    removable = Bool(default_value=True).tag(sync=True)
    headers = Dict().tag(sync=True)
    oauthToken = Unicode(allow_none = True).tag(sync=True)


@register
class AnnotationTrack(Track):
    """
    Annotation Track as described at:
    https://github.com/igvteam/igv.js/wiki/Annotation-Track
    """

    # Name of the widget view class in front-end
    _view_name = Unicode('TrackView').tag(sync=True)
    # Name of the widget model class in front-end
    _model_name = Unicode('TrackModel').tag(sync=True)
    # Name of the front-end module containing widget view
    _view_module = Unicode('ipyigv').tag(sync=True)
    # Name of the front-end module containing widget model
    _model_module = Unicode('ipyigv').tag(sync=True)
    # Version of the front-end module containing widget view
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    # Version of the front-end module containing widget model
    _model_module_version = Unicode('^0.1.0').tag(sync=True)


    displayMode = Unicode(default_value = 'COLLAPSED')
    expandedRowHeight = Int (default_value = 30)
    squishedRowHeight = Int (default_value = 15)
    nameField = Unicode(default_value = 'Name')
    maxRows = Int (default_value = 500)
    searchable = Bool(default_value=False)
    filterTypes = List(Unicode, default_value=['chromosone', 'gene'])
    color = Instance(Color)
    altColor = Instance(Color, allow_none=True)
    type = Unicode('annotation', read_only=True)
    colorBy = Instance(FieldColors)


@register
class AlignmentTrack(Track):
    viewAsPairs = Bool(default_value=False)
    pairsSupported = Bool(default_value=True)
    coverageColor = Instance(Color)  # default should be red=150, green=150, blue=150
    color = Instance(Color)


# class Exon(HasTraits):
#     start = Int()
#     end = Int()
#     cdStart = Int()
#     cdEnd = Int()
#     utr = Bool()
#
# class TrackFeature(Widget):
#     chr = Unicode()
#     start = Int()
#     end = Int()
#     name = Unicode()
#     score = Float()
#     strand = Unicode()
#     cdStart = Int()
#     cdEnd = Int()
#     color = Instance(Color)
#     exons = List(trait=Exon)

@register
class ReferenceGenome(Widget):
    """
    A class reflecting a reference genome as per IGV documentation.
    https://github.com/igvteam/igv.js/wiki/Reference-Genome
    """

    # Name of the widget view class in front-end
    _view_name = Unicode('ReferenceGenomeView').tag(sync=True)
    # Name of the widget model class in front-end
    _model_name = Unicode('ReferenceGenomeModel').tag(sync=True)
    # Name of the front-end module containing widget view
    _view_module = Unicode('ipyigv').tag(sync=True)
    # Name of the front-end module containing widget model
    _model_module = Unicode('ipyigv').tag(sync=True)
    # Version of the front-end module containing widget view
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    # Version of the front-end module containing widget model
    _model_module_version = Unicode('^0.1.0').tag(sync=True)


    id = Unicode(allow_none=True).tag(sync=True)
    name = Unicode(allow_none=True).tag(sync=True)
    fastaURL = Unicode().tag(sync=True)
    indexURL = Unicode(allow_none=True).tag(sync=True)
    cytobandURL = Unicode(allow_none=True).tag(sync=True)
    aliasURL = Unicode(allow_none=True).tag(sync=True)
    indexed = Bool(default_value=False).tag(sync=True)
    tracks = List(InstanceDict(Track)).tag(sync=True, **widget_serialization_no_none)
    chromosomeOrder = Unicode(allow_none=True).tag(sync=True)
    headers = Dict().tag(sync=True)
    wholeGenomeView = Bool(default_value=True).tag(sync=True)


# class SearchService(Widget):
#     url = Unicode()
#     resultsField = Unicode()
#     coords = Int(default_value=1)
#     chromosomeField = Unicode(default_value='chromosone')
#     startField = Unicode(default_value='start')
#     endField = Unicode(default_value='end', allow_none=True)

# class options(Widget):
#     """
#     A class reflecting the options to be passed at igv browser creation.
#     https://github.com/igvteam/igv.js/wiki/Browser-Creation
#     """
#     reference = Instance(ReferenceGenome)
#     doubleClickDelay = Int(default_value=500)
#     flanking = Int(default_value=1000)
#     genomeList = Unicode(allow_none=True)  # optional URL
#     locus = Unicode() | List(Unicode())
#     minimumBases = Int(default_value=40)
#     queryParametersSupported = Bool(default=False)
#     search = Instance(SearchService, allow_none=True)
#     showAllChromosomes = Bool(default_value=True)
#     showAllChromosomeWidget = Bool(default_value=True)
#     showNavigation = Bool(default_value=True)
#     showSVGButton = Bool(default_value=False)
#     showRuler = Bool(default_value=True)
#     showCenterGuide = Bool(default_value=False)
#     # trackDefaults = # missing documentation
#     tracks = List(Track)
#     regionsOfInterest = List(Track)
#     oauthToken = Unicode(allow_none = True)
#     apiKey = Unicode(allow_none = True)
#     clientId = Unicode(allow_none = True)
