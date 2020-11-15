const widgets = require('@jupyter-widgets/base');
var _ = require('lodash');
var igv = require('./igv.js')

// When serialiazing the entire widget state for embedding, only values that
// differ from the defaults will be specified.


// NOT WORKING -- Promise
class TrackModel extends widgets.WidgetModel {
  defaults () {
      console.log("Defaults", super.defaults())
      var dico = JSON.parse(JSON.stringify(super.defaults()))
      return _.extend(...dico,  {
            _model_name : 'TrackModel',
            _view_name : 'TrackView',
            _model_module : 'ipyigv',
            _view_module : 'ipyigv',
            _model_module_version : '0.1.0',
            _view_module_version : '0.1.0',
          }
      );
    };
  };

// var TrackModel = widgets.WidgetModel.extend({
//     defaults: _.extend(widgets.WidgetModel.prototype.defaults(), {
//         _model_name : 'TrackModel',
//         _view_name : 'TrackView',
//         _model_module : 'ipyigv',
//         _view_module : 'ipyigv',
//         _model_module_version : '0.1.0',
//         _view_module_version : '0.1.0',
//     })
//   });


var ReferenceGenomeModel = widgets.WidgetModel.extend({
    defaults: _.extend(widgets.WidgetModel.prototype.defaults(), {
        _model_name : 'ReferenceGenomeModel',
        _view_name : 'ReferenceGenomeView',
        _model_module : 'ipyigv',
        _view_module : 'ipyigv',
        _model_module_version : '0.1.0',
        _view_module_version : '0.1.0',
    }),
  }, {
    serializers: _.extend({
        tracks: { deserialize: widgets.unpack_models }
      }, widgets.WidgetModel.serializers)
});


var IgvModel = widgets.DOMWidgetModel.extend({
    defaults: _.extend(widgets.DOMWidgetModel.prototype.defaults(), {
        _model_name : 'IgvModel',
        _view_name : 'IgvBrowser',
        _model_module : 'ipyigv',
        _view_module : 'ipyigv',
        _model_module_version : '0.1.0',
        _view_module_version : '0.1.0',
    })
  }, {
    serializers: _.extend({
        reference: { deserialize: widgets.unpack_models }
      }, widgets.DOMWidgetModel.serializers)
});

var ReferenceGenomeView = widgets.WidgetView.extend({
  render: function() {
    console.log("rendering ReferenceGenomeView")
    // this.listenTo(this.model, 'change:tracks', this.update_tracks, this)
  },

});

var TrackView = widgets.WidgetView.extend({
  render: function() {
    console.log("rendering TrackView")
  },
});


var IgvBrowser = widgets.DOMWidgetView.extend({
    // Defines how the widget gets rendered into the DOM

    tracks_initialized: false,
    browser: null,

    render: function() {
      var that = this
      console.log("rendering browser")
      this.igvDiv = document.createElement("div");
      // console.log('model', this.model)
      reference = this.model.get('reference')
      var options =  {reference: this.model.get('reference')} // { "genome": this.model.get('genome') };
      this.browser = igv.createBrowser(this.igvDiv, options)
        .then(browser => {
            console.log("Created IGV browser with options ", options);
            browser.on('trackremoved', that.track_removed);
            browser.on('trackdragend', that.track_dragged);

            browser.on('locuschange', that.locus_changed);
            browser.on('trackclick', that.track_clicked);
            return browser;
          });

      this.el.appendChild(this.igvDiv)

      console.log("configuring track_views")
      this.track_views = new widgets.ViewList(this.add_track_view, this.remove_track_view, this)
      this.track_views.update(reference.get('tracks'))
      this.tracks_initialized = true
      console.log("Done configuring track_views")

      // IMPORTANT: do this after this.track_views.update(...), or this.update_tracks gets called
      this.listenTo(this.model, 'change:reference', this.update_reference, this)
      this.listenTo(this.model.get('reference'), 'change:tracks', this.update_tracks, this.reference)
      //this.model.on('change:genome', this.update_genome, this)
    },

    update_reference: function() {
      reference = this.model.get('reference')
      console.log('Updating browser reference with ', reference)
      this.browser.then((b) => {
        b.loadGenome(reference)
      });
    },

    update_tracks: function() {
      if (this.tracks_initialized) {
        tracks = this.model.get('reference').get('tracks')
        console.log('Updating tracks_views with ', tracks)
        this.track_views.update(tracks)
      }
      else {
        console.log ("tracks not yet initialized - skipping")
      }
      //this.browser.loadGenome({"id": this.model.get('genome')})
    },

    add_track_view: function(child_model) {
      var that = this;
      return this.create_child_view(child_model, {}).then(view => {
          console.log('add_track_view with child :', child_model)
          if (!this.tracks_initialized) {
              return that.browser.then((browser) => {
                  return browser.loadTrack(child_model.attributes).then((newTrack) => {
                      console.log("new track loaded in browser: " , newTrack);
                      return view;
                  });
            });
          } else {
              console.log("track_view not yet initialized, skipping");
              return view;
          }
      });
    },

    remove_track_view: function(child_view) {
      console.log('removing Track from genome', child_view);
      var that = this;
      if (!this.tracks_initialized) {
        console.log("track_view not yet initialized, skipping");
        return;
      }
      that.browser.then(b => {
          b.removeTrackByName(child_view.model.get("name"));
      });
    },

    track_removed: function(tracks) {
      console.log('track removed', tracks)
    },

    track_dragged: function(arg) {
      console.log('track dragged', arg)
    },

    locus_changed: function(referenceFrame, label) {
      console.log('locus changed', referenceFrame, label)
    },

    track_clicked: function (track, popoverData) {
      console.log('track clicked', track, popoverData)
    }
});


module.exports = {
    IgvModel: IgvModel,
    IgvBrowser: IgvBrowser,
    ReferenceGenomeView: ReferenceGenomeView,
    ReferenceGenomeModel: ReferenceGenomeModel,
    TrackView: TrackView,
    TrackModel: TrackModel,
};
