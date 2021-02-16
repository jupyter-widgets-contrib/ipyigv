const widgets = require('@jupyter-widgets/base');
var _ = require('lodash');
var igv = require('./igv.js')

// Import the CSS
import '../css/widget.css'

import { MODULE_NAME, MODULE_VERSION } from './version'

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

    // returns a dictionary representing a track which igv.js can take in its configuration
    to_dict(include_empty = false) {
      let keys = Object.keys(this.attributes).filter(k => !k.startsWith("_"))
                  // removing empty values unless specified otherwise
                  .filter(k=> (include_empty || !([null, undefined, ""].includes(this.get(k)))));

      var dict = keys.reduce((result, key)=> ({...result, [key]:this.get(key)}), {});

      if (keys.includes('roi')) {
        dict['roi'] = dict['roi'].map(track => track.to_dict(include_empty));
      };
      console.log ("Finished generating dictionary from TrackModel", dict);
      return dict ;
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

    // returns a dictionary representing a genome which igv.js can take in its configuration
    to_dict(include_empty = false) {
      let keys = Object.keys(this.attributes).filter(k => !k.startsWith("_"))
                  // removing empty values unless specified otherwise
                  .filter(k=> (include_empty || !([null, undefined, ""].includes(this.get(k)))));

      var dict = keys.reduce((result, key)=> ({...result, [key]:this.get(key)}), {});

      // special treatment for tracks
      if (keys.includes('tracks')) {
        let tracks = dict['tracks'];
        dict['tracks'] = tracks.map(track=> track.to_dict(include_empty));
      };
      console.log ("Finished generating dictionary from ReferenceGenomeView", dict);
      return dict ;
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

    // returns a dictionary representing a genome which igv.js can take in its configuration
    to_dict(include_empty = false) {
      var keys = Object.keys(this.attributes).filter(k => !k.startsWith("_"))
                  // removing the layout attribute -- not related to igv
                  .filter(k=> (k!='layout'))
                  // removing empty values unless specified otherwise
                  .filter(k=> (include_empty || !([null, undefined, ""].includes(this.get(k)))));

      var dict = keys.reduce((result, key)=> ({...result, [key]:this.get(key)}), {});

      // special treatment for tracks
      if (keys.includes('tracks')) {
        let tracks = dict['tracks'];
        dict['tracks'] = tracks.map(track=> track.to_dict(include_empty));
      };

      // special treatment for regions of interest
      if (keys.includes('roi')) {
        let roi = dict['roi'];
        dict['roi'] = roi.map(roi=> roi.to_dict(include_empty));
      };


      // special treatment for genome
      if (keys.includes('genome')) {  // should always be the case
        let genome = dict['genome'];
        dict['genome'] = genome.to_dict(include_empty);
      };

      console.log ("Finished generating dictionary from IgvModel", dict);
      return dict ;
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

      var options = this.model.to_dict()
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
