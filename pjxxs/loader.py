import sys
import os
import json

from pjxxs import fields


__schema_map = dict()
__base_path = None


def set_base_path(path):
	global __base_path
	__base_path = path


def load_from_json(ident):
	global __base_path
	if __base_path is None:
		raise Exception("Base path not set")
	schema_name = ident.replace(".", "/")
	parts = schema_name.split("/")
	path = os.path.join(__base_path, *parts)
	path += ".json"
	data = None
	with open(path, "r") as fh:
		data = json.load(fh)
	schema = fields.Schema(
		data.get("@id", ident),
		data.get("@version", 1)
	)
	_build_schema(schema, data)
	return schema


def load(ident, **kwargs):
	schema_name = ident.replace("/", ".")
	schema = None
	try:
		__import__(schema_name)
		schema = sys.modules["schema." + schema_name].schema
	except ImportError as e:
		schema = load_from_json(schema_name)
	return schema


def _build_schema(root, data):
	keys = filter(lambda k: not k.startswith("@"), data)
	for k in keys:
		field = _build_field(k, data[k].get("@properties", {}))
		root.add_field(field)
		_build_schema(field, data[k])


def _build_field(k, props):
	field_type_map = {
		"Schema" : fields.SchemaType,
		"Object" : fields.Object,
		"Array" : fields.Array,
		"Int" : fields.Int,
		"Double" : fields.Double,
		"String" : fields.String,
		"Enum" : fields.Enum,
		"Bool" : fields.Bool,
		"Null" : fields.Null
	}

	dt_map = {
		"bool" : bool,
		"str" : str,
		"int" : int,
		"float" : float,
		"list" : list,
		"dict" : dict,
		"set" : set,
	}

	props["allowed_types"] = list(
		map(lambda t: dt_map[t], props["allowed_types"])
	)

	field = None
	if props["field_type"].startswith("Schema:"):
		cls = fields.SchemaType
		schema_id = props["field_type"].split(":")[1]
		field = fields.SchemaType(k, schema_id, **props)
	else:
		cls = field_type_map[props["field_type"]]
		field = cls(k, **props)
	return field
