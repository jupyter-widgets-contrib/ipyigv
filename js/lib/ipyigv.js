var widgets = require('@jupyter-widgets/base');
var _ = require('lodash');
var igv = require('./igv.js')

// When serialiazing the entire widget state for embedding, only values that
// differ from the defaults will be specified.

var TrackModel = widgets.WidgetModel.extend({
    defaults: _.extend(widgets.WidgetModel.prototype.defaults(), {
        _model_name : 'TrackModel',
        _view_name : 'TrackView',
        _model_module : 'ipyigv',
        _view_module : 'ipyigv',
        _model_module_version : '0.1.0',
        _view_module_version : '0.1.0',
    })
  }, {
    serializers: _.extend({
        reference: { deserialize: widgets.unpack_models }
      }, widgets.WidgetModel.serializers)
});


var ReferenceGenomeModel = widgets.WidgetModel.extend({
    defaults: _.extend(widgets.WidgetModel.prototype.defaults(), {
        _model_name : 'ReferenceGenomeModel',
        _view_name : 'ReferenceGenomeView',
        _model_module : 'ipyigv',
        _view_module : 'ipyigv',
        _model_module_version : '0.1.0',
        _view_module_version : '0.1.0',
    })
  }, {
    serializers: _.extend({
        reference: { deserialize: widgets.unpack_models }
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
  update_tracks: function() {
    console.log('Updating tracks with '+ this.model.get('tracks'))
    //this.browser.loadGenome({"id": this.model.get('genome')})
  },

});

var TrackView = widgets.WidgetView.extend({
  render: function() {
    console.log("rendering TrackView")
  },
});


var IgvBrowser = widgets.DOMWidgetView.extend({
    // Defines how the widget gets rendered into the DOM
    render: function() {
      console.log("rendering browser")
      this.igvDiv = document.createElement("div");
      // console.log('model', this.model)
      reference = this.model.get('reference')
      console.log('reference:', reference)
      var options =  {reference: this.model.get('reference')} // { "genome": this.model.get('genome') };
      console.log("options:", options)
      igv.createBrowser(this.igvDiv, options)
        .then(function (browser) {
            console.log("Created IGV browser with options ", options);
          })

      this.el.appendChild(this.igvDiv)
      this.listenTo(this.model, 'change:reference', this.update_reference, this)
      //this.model.on('change:genome', this.update_genome, this)
    },

    update_reference: function() {
      console.log('Updating options["reference"] with '+ this.model.get('reference'))
      //this.browser.loadGenome({"id": this.model.get('genome')})
    },
});


module.exports = {
    IgvModel: IgvModel,
    IgvBrowser: IgvBrowser,
    ReferenceGenomeView: ReferenceGenomeView,
    ReferenceGenomeModel: ReferenceGenomeModel,
    TrackView: TrackView,
    TrackModel: TrackModel,
};
