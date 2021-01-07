import os

from urllib.parse import urlparse

from spectate import mvc
from traitlets import (
    Float, Unicode, Int, Tuple, List, Instance, Bool, Dict, Enum,
    link, observe, default, validate, TraitError, Union, HasTraits, TraitType
)
from ipywidgets import Widget, register, widget_serialization
from ipywidgets.widgets.trait_types import Color, InstanceDict
from ipywidgets.widgets import widget

from .utils import widget_serialization_no_none
from ._version import EXTENSION_VERSION


# NB '.txt' considered annotation as it is used in the public genomes. But not as per the doc.
TRACK_FILE_TYPES = { \
        'annotation': [ '.txt', \
            '.bed', '.gff', '.gff3', '.gtf', '.genePred', '.genePredExt', \
            '.peaks', '.narrowPeak', '.broadPeak', '.bigBed', '.bedpe' \
            ],
        'wig': ['.wig', '.bigWig', '.bedGraph'],
        'alignment': ['.bam'],
        'variant': ['.vcf'],
        'seg': ['.seg'],
        'spliceJunctions': ['.bed'],
        'gwas': ['.gwas', '.bed'],
        'interaction': ['.bedpe'],
        }


class FieldColors(HasTraits):
    field = Unicode()
    palette = Dict(key_trait=Unicode, value_trait=Instance(Color))


class SortOption(HasTraits):
    chr = Unicode() # chromosone name
    position = Int() # genomic position
    option = Unicode() # 'BASE', 'STRAND', 'INSERT_SIZE', 'MATE_CHR', 'MQ', 'TAG'
    tag = Unicode () # doc not clear
    direction = Unicode("ASC") # 'ASC' for ascending, 'DESC' for descending


class SortOrder(HasTraits):
    chr = Unicode()  # chromosone name
    direction = Unicode("ASC") # 'ASC' for ascending, 'DESC' for descending
    start = Int()
    end = Int()


@register
class Track(Widget):
    """
    A class reflecting the common fields of a track as per igv documentation.
    https://github.com/igvteam/igv.js/wiki/Tracks-2.0

    If a Track type is not inferable a generic Track will be instantiated.
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
    _view_module_version = Unicode(EXTENSION_VERSION).tag(sync=True)
    # Version of the front-end module containing widget model
    _model_module_version = Unicode(EXTENSION_VERSION).tag(sync=True)


    def __new__(cls, **kwargs):
        if cls is Track:
            # we must infer the type to instantiate the right Track type
            trackType = kwargs.get('type', None)
            if trackType is None:
                # then type is inferred from the file extension
                url = kwargs.get('url')
                path = urlparse(url).path
                filename, filetype = os.path.splitext(path)
                if filetype == '.gz': # some files might be compressed
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
            elif trackType == 'variant':
                return super(Track, cls).__new__(VariantTrack)
            elif trackType == 'wig':
                return super(Track, cls).__new__(WigTrack)
            elif trackType == 'seg':
                return super(Track, cls).__new__(SegTrack)
            elif trackType == 'spliceJunctions':
                return super(Track, cls).__new__(SpliceJunctionsTrack)
            elif trackType == 'gwas':
                return super(Track, cls).__new__(GwassTrack)
            elif trackType == 'interation':
                return super(Track, cls).__new__(InteractionTrack)
            else:
                return super(Track, cls).__new__(cls)
        else:
            return super(Track, cls).__new__(cls)

    # These fields are common to all Track types
    sourceType = Unicode(default_value='file').tag(sync=True)  #
    format = Unicode().tag(sync=True) # missing documentation
    name = Unicode().tag(sync=True)
    url = Unicode().tag(sync=True)
    indexURL = Unicode().tag(sync=True)
    indexed = Bool(default_value=False).tag(sync=True)
    order = Int().tag(sync=True)
    color = Color().tag(sync=True).tag(sync=True)
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
    AnnotationTrack as described at:
    https://github.com/igvteam/igv.js/wiki/Annotation-Track
    """

    type = Unicode('annotation', read_only=True).tag(sync=True)
    displayMode = Unicode(default_value = 'COLLAPSED').tag(sync=True)
    expandedRowHeight = Int (default_value = 30).tag(sync=True)
    squishedRowHeight = Int (default_value = 15).tag(sync=True)
    nameField = Unicode(default_value = 'Name').tag(sync=True)
    maxRows = Int (default_value = 500).tag(sync=True)
    searchable = Bool(default_value=False).tag(sync=True)
    filterTypes = List(Unicode, default_value=['chromosone', 'gene']).tag(sync=True, **widget_serialization_no_none)
    color = Color("rgb(0,0,150)").tag(sync=True)
    altColor = Color("rgb(0,0,150)").tag(sync=True)
    colorBy = Instance(FieldColors, allow_none=True).tag(sync=True, **widget_serialization_no_none)
    roi = List(InstanceDict(Track)).tag(sync=True, **widget_serialization_no_none) # regions of interest


@register
class AlignmentTrack(Track):
    """
    AlignmentTrack as described at:
    https://github.com/igvteam/igv.js/wiki/Alignment-Track
    """

    type = Unicode('alignment', read_only=True).tag(sync=True)
    viewAsPairs = Bool(default_value=False).tag(sync=True)
    pairsSupported = Bool(default_value=True).tag(sync=True)
    coverageColor = Color(default_value="rgb(150, 150, 150)").tag(sync=True, **widget_serialization) # default: rgb(150, 150, 150)
    color = Color(default_value="rgb(170, 170, 170)").tag(sync=True, **widget_serialization) # default: rgb(170, 170, 170)
    deletionColor = Color(default_value="black").tag(sync=True, **widget_serialization)
    skippedColor = Color(default_value="rgb(150, 170, 170)").tag(sync=True, **widget_serialization) # default: rgb(150, 170, 170)
    insertionColor = Color(default_value="rgb(138, 94, 161)").tag(sync=True, **widget_serialization) # default: rgb(138, 94, 161)
    negStrandColor = Color(default_value="rgba(150, 150, 230, 0.75)").tag(sync=True, **widget_serialization) # default: rgba(150, 150, 230, 0.75)
    posStrandColor = Color(default_value="rgba(230, 150, 150, 0.75)").tag(sync=True, **widget_serialization) # default: rgb(138, 94, 161)
    # pairConnectorColor = Instance(Color, default_value="alignmentColor") # default: doc not clear
    colorBy = Unicode("none").tag(sync=True) # "none", "strand", "firstOfPairStrand", or "tag"
    colorByTag = Unicode().tag(sync=True) # TODO - doc not clear
    bamColorTag = Unicode("YC").tag(sync=True) # TODO - doc not clear
    samplingWindowSize = Int(100).tag(sync=True)
    samplingDepth = Int(100).tag(sync=True)
    alignmentRowHeight = Int(14).tag(sync=True)
    readgroup = Unicode("RG").tag(sync=True)
    sortOption = Instance(SortOption, allow_none=True).tag(sync=True, **widget_serialization_no_none)
    showSoftClips = Bool(False).tag(sync=True)
    showMismatches = Bool(True).tag(sync=True)

    # Paired-end and mate-pair coloring options.
    pairOrientation  = Unicode(allow_none=True).tag(sync=True, **widget_serialization_no_none)  #  ff, fr, or rf
    minFragmentLength = Int(allow_none=True).tag(sync=True, **widget_serialization_no_none)
    maxFragmentLength = Int(allow_none=True).tag(sync=True, **widget_serialization_no_none)

    roi = List(InstanceDict(Track)).tag(sync=True, **widget_serialization_no_none) # regions of interest


@register
class VariantTrack(Track):
    """
    VariantTrack as described at:
    https://github.com/igvteam/igv.js/wiki/Variant-Track
    """

    type = Unicode('variant', read_only=True).tag(sync=True)
    displayMode = Unicode('EXPANDED').tag(sync=True)
    noCallColor = Color("rgb(250, 250, 250)").tag(sync=True)
    homvarColor = Color("rgb(17,248,254)").tag(sync=True)
    hetvarColor = Color("rgb(34,12,253)").tag(sync=True)
    homrefColor = Color("rgb(200, 200, 200)").tag(sync=True)
    squishedCallHeight = Int(1).tag(sync=True)
    expandedCallHeight = Int(10).tag(sync=True)

    roi = List(InstanceDict(Track)).tag(sync=True, **widget_serialization_no_none) # regions of interest


class Guideline(HasTraits):
    color = Color().tag(sync=True)
    dotted = Bool().tag(sync=True)
    y = Int().tag(sync=True)


@register
class WigTrack(Track):
    """
    WigTrack as described at:
    https://github.com/igvteam/igv.js/wiki/Wig-Track
    """

    type = Unicode('wig', read_only=True).tag(sync=True)
    autoscale = Bool(True).tag(sync=True)
    autoscaleGroup = Unicode(allow_none=True).tag(sync=True, **widget_serialization_no_none)
    min = Int(0).tag(sync=True)
    max = Int(allow_none=True).tag(sync=True, **widget_serialization_no_none)
    color = Color(default_value="rgb(150, 150, 150)").tag(sync=True)
    altColor = Color(allow_none=True).tag(sync=True, **widget_serialization_no_none)
    guideLines = List(trait=Instance(Guideline), allow_none=True).tag(sync=True, **widget_serialization_no_none)

    roi = List(InstanceDict(Track)).tag(sync=True, **widget_serialization_no_none) # regions of interest


@register
class SegTrack(Track):
    """
    SegTrack Track as described at:
    https://github.com/igvteam/igv.js/wiki/Seg-Track
    """

    type = Unicode('seg', read_only=True).tag(sync=True)
    isLog = Bool(allow_none=True).tag(sync=True, **widget_serialization_no_none)
    displayMode = Unicode("EXPANDED").tag(sync=True) #  "EXPANDED", "SQUISHED", or "FILL"
    sort = InstanceDict(SortOrder).tag(sync=True, **widget_serialization)

    roi = List(InstanceDict(Track)).tag(sync=True, **widget_serialization_no_none) # regions of interest


@register
class SpliceJunctionsTrack(Track):
    """
    SpliceJunctionsTrack as described at:
    https://github.com/igvteam/igv.js/wiki/SpliceJunctions
    """

    type = Unicode('spliceJunctions', read_only=True).tag(sync=True)
    # Display Options
    colorBy = Unicode('numUniqueReads').tag(sync=True) # "numUniqueReads", "numReads", "isAnnotatedJunction", "strand", "motif"
    colorByNumReadsThreshold = Int(5).tag(sync=True)
    thicknessBasedOn = Unicode('numUniqueReads').tag(sync=True) # "numUniqueReads", "numReads", "isAnnotatedJunction"
    bounceHeightBasedOn = Unicode('random').tag(sync=True) # "random", "distance", "thickness"
    labelUniqueReadCount = Bool(True).tag(sync=True)
    labelMultiMappedReadCount = Bool(True).tag(sync=True)
    labelTotalReadCount = Bool(False).tag(sync=True)
    labelMotif = Bool(False).tag(sync=True)
    labelAnnotatedJunction = Unicode(allow_none=True).tag(sync=True, **widget_serialization_no_none)

    # Filtering Options
    minUniquelyMappedReads = Int(0).tag(sync=True)
    minTotalReads = Int(0).tag(sync=True)
    maxFractionMultiMappedReads = Int(1).tag(sync=True)
    minSplicedAlignmentOverhang = Int(0).tag(sync=True)
    hideStrand = Unicode(allow_none=True).tag(sync=True, **widget_serialization_no_none) # None, "+" or "-"
    hideAnnotatedJunctions = Bool(False).tag(sync=True)
    hideUnannotatedJunctions = Bool(False).tag(sync=True)
    hideMotifs = List(Unicode).tag(sync=True, **widget_serialization)

    roi = List(InstanceDict(Track)).tag(sync=True, **widget_serialization_no_none) # regions of interest


@register
class GwasTrack (Track):
    """
    GwasTrack as described at:
    https://github.com/igvteam/igv.js/wiki/GWAS
    """

    type = Unicode('gwas', read_only=True).tag(sync=True)
    min = Int(0).tag(sync=True)
    max = Int(25).tag(sync=True)
    # format = Unicode().tag(sync=True) #  'bed' or 'gwas' - format is already in Track -> validation only
    posteriorProbability = Bool(False).tag(sync=True)
    dotSize = Int(3).tag(sync=True)
    columns = Dict(key_trait=Unicode, value_trait=Int, allow_none=True).tag(sync=True, **widget_serialization_no_none)

    roi = List(InstanceDict(Track)).tag(sync=True, **widget_serialization_no_none) # regions of interest


@register
class InteractionTrack (Track):
    """
    InteractionTrack as described at:
    https://github.com/igvteam/igv.js/wiki/Interaction
    """

    type = Unicode('interaction', read_only=True).tag(sync=True)
    arcOrientation = Bool(True).tag(sync=True)
    thickness = Int(2).tag(sync=True)

    roi = List(InstanceDict(Track)).tag(sync=True, **widget_serialization_no_none) # regions of interest


class Exon(HasTraits):
    start = Int()
    end = Int()
    cdStart = Int()
    cdEnd = Int()
    utr = Bool()


class TrackFeature(HasTraits):
    chr = Unicode()
    start = Int()
    end = Int()
    name = Unicode()
    score = Float()
    strand = Unicode()
    cdStart = Int()
    cdEnd = Int()
    color = Instance(Color)
    exons = List(trait=Instance(Exon))


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
    _view_module_version = Unicode(EXTENSION_VERSION).tag(sync=True)
    # Version of the front-end module containing widget model
    _model_module_version = Unicode(EXTENSION_VERSION).tag(sync=True)

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


@register
class SearchService(Widget):
    url = Unicode()
    resultsField = Unicode()
    coords = Int(default_value=1)
    chromosomeField = Unicode(default_value='chromosome')
    startField = Unicode(default_value='start')
    endField = Unicode(default_value='end', allow_none=True)
