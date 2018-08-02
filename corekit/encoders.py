from django.forms.models import model_to_dict
from django.db.models import Model
from django.db.models.fields.files import FieldFile
from datetime import datetime
from collections import OrderedDict
from enum import Enum
from decimal import Decimal
from rest_framework.utils import encoders
from io import IOBase
import json
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from yaml.representer import SafeRepresenter


Dumper.add_representer(
    OrderedDict, 
    lambda dumper, data:dumper.represent_dict(data.items())
)

Dumper.add_representer(
    str, SafeRepresenter.represent_str)

Loader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    lambda loader, node: OrderedDict(loader.construct_pairs(node))
)


IGNORES = (IOBase, )


class JSONEncoder(encoders.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, IGNORES):
            return None
        if isinstance(obj, Model):
            return model_to_dict(obj)
        try:
            return super(JSONEncoder, self).default(obj)
        except:
            pass

    @classmethod
    def to_json(cls, obj, *args, **kwargs):
        return json.dumps(obj, cls=cls, *args, **kwargs)

    @classmethod
    def from_json(cls, jsonstr,  *args, **kwargs):
        return json.loads(jsonstr, *args, **kwargs)

    @classmethod
    def to_yaml(cls, obj, *args, **kwargs):
        if not 'Dumper' in kwargs:
            kwargs['Dumper'] = Dumper
        if isinstance(obj, Model):
            obj = model_to_dict(obj)
        return yaml.dump(obj, *args, **kwargs)

to_json = JSONEncoder.to_json
from_json = JSONEncoder.from_json
to_yaml = JSONEncoder.to_yaml
