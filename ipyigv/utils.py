from ipywidgets import Widget, widget_serialization

def is_json_valid(v):
    if v is None:
        return False
    elif isinstance(v, str):
        return (v != "")
    else:
        return True


def _widget_to_json_no_none(x, obj):
    if isinstance(x, dict):
        return {k: _widget_to_json_no_none(v, obj) for k, v in x.items() if v not in (None, "")}
    elif isinstance(x, (list, tuple)):
        return [_widget_to_json_no_none(v, obj) for v in x if v not in (None, "")]
    elif isinstance(x, Widget):
        return "IPY_MODEL_" + x.model_id
    else:
        return x

widget_serialization_no_none = {
    'to_json': _widget_to_json_no_none,
    'from_json': widget_serialization['from_json']
}
