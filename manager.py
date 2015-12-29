import os
import json

from . import types


__schemas = dict()
__base_path = None


def from_data(root, data):
	for k in filter(lambda x: not x.startswith("@"), sorted(data)):
		if isinstance(data[k], dict):
			field = None
			props = data[k]["@properties"]
			field_type = props["field_type"]
			if field_type.startswith("Schema:"):
				s = load(field_type.split(":")[1])
				field = from_data(root, s.data())
				pass
			else:
				fld_ctor = _field_from_string(field_type)
				if "allowed_types" in props:
					props["allowed_types"] = list(map(
						lambda x: _type_from_string(x),
						props["allowed_types"]
					))
				field = fld_ctor(k, **props)
			if isinstance(field, types.Object):
				for sub_k in filter(lambda x: not x.startswith("@"), data[k]):
					if not isinstance(data[k][sub_k], types.Schema):
						from_data(field, data[k][sub_k])
			root.add_field(field)


def _field_from_string(fld):
	fldmap = {
		"Object" : types.Object,
		"Array" : types.Array,
		"String" : types.String,
		"Int" : types.Int,
		"Bool" : types.Bool,
		"Enum" : types.Enum,
		"Numeric" : types.Numeric,
		"Double" : types.Double,
		"Time" : types.Time,
		"Null" : types.Null,
		"SchemaType" : types.SchemaType
	}
	return fldmap[fld]


def _type_from_string(tp):
	if tp.startswith("Schema:"):
		tp = load(tp.split(":")[1])
		return tp
	tpmap = {
		"str" : str,
		"int" : int,
		"float" : float,
		"bool" : bool,
		"list" : list,
		"dict" : dict,
	}
	return tpmap[tp]


class JSONSchema(object):
	__path = None
	__ident = None
	__data = {}
	__initialized = False
	__gen = None

	def __init__(self, path):
		self.__path = path
		self._schema_inst = types.Schema(self.ident())
		self.reload()

	def ident(self):
		return self.__ident

	def schema_data(self):
		return self.__data.copy()

	def data(self):
		return self._schema_inst.data()

	def path(self):
		return self.__path

	def reload(self):
		with open(self.__path, "r") as fh:
			self.__data = json.load(fh)
		if not self.__initialized:
			self.__ident = self.__data["@id"]
		elif self.__ident != self.__data["@id"]:
			raise Exception("Schema id changed: %s" % self.__path)
		from_data(self._schema_inst, self.schema_data())

	def validate(self, data):
		errors = {}
		self._schema_inst.validate(data, errors)
		return errors


def initialize(base_path):
	global __base_path
	__base_path = base_path
	for (root, dirs, files) in os.walk(base_path):
		for f in files:
			if f.endswith(".json"):
				full_path = os.path.join(root, f)
				schema = JSONSchema(full_path)
				if schema.ident() in __schemas and (
						full_path != __schemas[schema.ident()].path()):
					msg = "Duplicate schema: %s" % full_path
					msg += "\nDuplicates: %s" % (__schemas[schema.ident()].path())
					raise Exception(msg)
				__schemas[schema.ident()] = schema


def load(ident):
	if ident and ident not in __schemas:
		schema_file = os.path.join(__base_path, ident)
		schema_file += ".json"
		if os.path.isfile(schema_file):
			schema = JSONSchema(schema_file)
			__schemas[schema.ident()] = schema
	return __schemas.get(ident, None)
