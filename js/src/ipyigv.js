const widgets = require('@jupyter-widgets/base');
var _ = require('lodash');
var igv = require('./igv.js')

// Import the CSS
import '../css/widget.css'

import { MODULE_NAME, MODULE_VERSION } from './version'

// When serialiazing the entire widget state for embedding, only values that
// differ from the defaults will be specified.


export class TrackModel extends widgets.WidgetModel {
  defaults () {
      return _.extend(super.defaults(),  {
            _model_name : 'TrackModel',
            _view_name : 'TrackView',
            _model_module : MODULE_NAME,
            _view_module : MODULE_NAME,
            _model_module_version : MODULE_VERSION,
            _view_module_version : MODULE_VERSION,
        });
    };
  };


export class ReferenceGenomeModel extends widgets.WidgetModel {
  defaults () {
      return _.extend(super.defaults(),  {
        _model_name : 'ReferenceGenomeModel',
        _view_name : 'ReferenceGenomeView',
        _model_module : MODULE_NAME,
        _view_module : MODULE_NAME,
        _model_module_version : MODULE_VERSION,
        _view_module_version : MODULE_VERSION,
      });
    };
};

ReferenceGenomeModel.serializers = _.extend({
  tracks: { deserialize: widgets.unpack_models }
  },
  widgets.WidgetModel.serializers
)

export class IgvModel extends widgets.DOMWidgetModel {
    defaults () {
      return _.extend(super.defaults(),  {
          _model_name : 'IgvModel',
          _view_name : 'IgvBrowser',
          _model_module : MODULE_NAME,
          _view_module : MODULE_NAME,
          _model_module_version : MODULE_VERSION,
          _view_module_version : MODULE_VERSION,
      });
    };

    initialize(attributes, options) {
      super.initialize(attributes, options);
      this.on("msg:custom", this.custom_message_handler);
    };

    custom_message_handler(msg) {
      console.log('custom_message_handler in model', msg);
      if (msg.type === 'dump_json') {
        this.trigger('return_json');
      }
      else if (msg.type === 'search') {
        var symbol = msg.symbol
        this.trigger('search', symbol);
      }
    };
};

IgvModel.serializers = _.extend({
    genome: { deserialize: widgets.unpack_models },
    tracks: { deserialize: widgets.unpack_models },
    roi: { deserialize: widgets.unpack_models },
  },
  widgets.DOMWidgetModel.serializers
)

export class ReferenceGenomeView extends widgets.WidgetView {
  render () {
    super.render();
    console.log("rendering ReferenceGenomeView");
  }
}

export class TrackView extends widgets.WidgetView {
  render () {
    super.render();
    console.log("rendering TrackView");
  }
}


export class IgvBrowser extends widgets.DOMWidgetView {
    initialize(options) {
        super.initialize(options);
        this.tracks_initialized = true;
        this.browser = null;
        this.track_views = new widgets.ViewList(this.add_track_view, this.remove_track_view, this);
        console.log("configuring track_views");
        this.track_views.update(this.model.get('tracks'));
        this.tracks_initialized = true;
        console.log("Done configuring track_views");

        this.roi_views = new widgets.ViewList(this.add_roi_view, this.remove_roi_view, this);
        console.log("configuring roi_views");
        this.roi_views.update(this.model.get('roi'));
        console.log("Done configuring roi_views")
    }

    render() {
      super.render();

      this.igvDiv = document.createElement("div");
      var referenceGenome = this.model.get('genome');
      var tracks = this.model.get('tracks');
      var roi = this.model.get('roi');
      var doubleClickDelay = this.model.get('doubleClickDelay');
      var flanking = this.model.get('flanking');
      var genomeList = this.model.get('genomeList');
      var locus = this.model.get('locus');
      var minimumBases = this.model.get('minimumBases');
      var queryParametersSupported = this.model.get('queryParametersSupported');
      var search = this.model.get('search');
      var showAllChromosomes = this.model.get('showAllChromosomes');
      var showAllChromosomeWidget = this.model.get('showAllChromosomeWidget');
      var showNavigation = this.model.get('showNavigation');
      var showSVGButton = this.model.get('showSVGButton');
      var showRuler = this.model.get('showRuler');
      var showCenterGuide = this.model.get('showCenterGuide');
      var oauthToken = this.model.get('oauthToken');
      var apiKey = this.model.get('apiKey');
      var clientId = this.model.get('clientId');


      var options =  {
          reference: referenceGenome,
          tracks: tracks,
          roi: roi,
          doubleClickDelay: doubleClickDelay,
          flanking: flanking,
          genomeList: genomeList,
          locus: locus,
          minimumBases: minimumBases,
          queryParametersSupported: queryParametersSupported,
          showAllChromosomes:showAllChromosomes,
          showAllChromosomeWidget: showAllChromosomeWidget,
          showNavigation: showNavigation,
          showSVGButton: showSVGButton,
          showRuler: showRuler,
          showCenterGuide: showCenterGuide,
        };

        if (search) {
          options['search']=search
        }
        if (oauthToken) {
          options['oauthToken']=oauthToken
        }
        if (apiKey) {
          options['apiKey']=apiKey
        }
        if (clientId) {
          options['clientId']=clientId
        }

      console.log("rendering browser", options);
      this.browser = igv.createBrowser(this.igvDiv, options)
        .then((browser) => {
            console.log("Created IGV browser with options ", options);
            browser.on('trackremoved', this.track_removed);
            browser.on('trackdragend', this.track_dragged);

            browser.on('locuschange', this.locus_changed);
            browser.on('trackclick', this.track_clicked);
            return browser;
          });

      this.el.appendChild(this.igvDiv);


      this.listenTo(this.model, 'change:genome', this.update_genome);
      this.listenTo(this.model, 'change:tracks', this.update_tracks);
      this.listenTo(this.model, 'change:roi', this.update_roi);
      this.listenTo(this.model, "return_json", this._return_json);
      this.listenTo(this.model, "search", this._search);

    }

    update_genome () {
      var genome = this.model.get('genome');
      console.log('Updating browser reference with ', genome);
      this.browser.then((b) => {
        b.loadGenome(genome);
      });
    }

    update_tracks () {
      console.log("update_tracks")
      if (this.tracks_initialized) {
        var tracks = this.model.get('tracks');
        console.log('Updating tracks_views with ', tracks);
        this.track_views.update(tracks);
      }
      else {
        console.log ("Tracks not yet initialized - skipping");
      }
    }

    add_track_view (child_model) {
      return this.create_child_view(child_model, {}).then(view => {
          console.log('add_track_view with child :', child_model);
          if (this.tracks_initialized) {
              return this.browser.then((browser) => {
                  return browser.loadTrack(child_model.attributes).then((newTrack) => {
                      console.log("new track loaded in browser: " , newTrack);
                      view.igvTrack = newTrack
                      return view;
                  });
            });
          } else {
              console.log("track_view not yet initialized, skipping");
              return view;
          }
      });
    }

    remove_track_view (child_view) {
      console.log('removing Track from genome', child_view.igvTrack);

      if (!this.tracks_initialized) {
        console.log("track_view not yet initialized, skipping");
        return;
      }
      var child = child_view
      this.browser.then(b => {
          //b.removeTrackByName(child_view.model.get("name"));
          if (child.igvTrack){
            b.removeTrack(child.igvTrack);
          }
          else {
            b.removeTrackByName(child.model.get("name"));
          }
      });
    }

    update_roi () {
      console.log("update_roi")
      var roi = this.model.get('roi');
      console.log('Updating roi_views with ', roi);
      // the browser lets us only add ROI (one or several), or delete all ROI. (no unitary delete)
      if (roi == []) {
        console.log('removing Regions of Interest');
        this.browser.then(b => { b.clearROIs(); });
      }
      else {
        this.roi_views.update(roi);
      }
    }

    add_roi_view (child_model) {
      return this.create_child_view(child_model, {}).then(view => {
          console.log('add_roi_view with child view :', view);
              return this.browser.then((browser) => {
                  return browser.loadROI(view.model.attributes).then((newROI) => {
                      console.log("new roi loaded in browser: " , newROI);
                      return view;
                  });
            });
      });
    }

    remove_all_roi_view (child_view) {
      console.log('Oops - removing one Region of Interest not supported - Ignoring');
    }

    track_removed (tracks) {
      console.log('track removed', tracks);
    }

    track_dragged (arg) {
      console.log('track dragged', arg);
    }

    locus_changed (referenceFrame, label) {
      console.log('locus changed', referenceFrame, label);
    }

    track_clicked (track, popoverData) {
      console.log('track clicked', track, popoverData);
    }

    _return_json(event) {
      console.log('view._return_json', event);
      this.browser.then((browser)=> {
        var json = browser.toJSON()
        this.send({ event: 'return_json', json:json});

      });
    }

    _search(symbol) {
      console.log('view._search', symbol);
      var symbol = symbol
      this.browser.then((browser) => {
        browser.search(symbol);
      });
    }


}

// module.exports = {
//     IgvModel: IgvModel,
//     IgvBrowser: IgvBrowser,
//     ReferenceGenomeView: ReferenceGenomeView,
//     ReferenceGenomeModel: ReferenceGenomeModel,
//     TrackView: TrackView,
//     TrackModel: TrackModel,
// };
