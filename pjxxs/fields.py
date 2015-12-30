#!/usr/local/bin/python3 -tt

import sys
import json
import re
import datetime
from json import JSONEncoder

# This is really a serious mindfuck.


class Field(object):
	def __init__(self, ident, base_type, **kwargs):
		self._ident = ident
		self._base_type = base_type
		self._required = bool(kwargs.get("required", False))
		self._nullable = bool(kwargs.get("nullable", False))
		self._allowed_types = kwargs.get("allowed_types", [])
		self._allowed_values = kwargs.get("allowed_values", [])
		self._kwargs = kwargs
		if not isinstance(self._allowed_types, list):
			raise Exception(
				"Invalid 'allowed_types' passed to '%s'. Need list." % (
					self.__class__.__name__
				)
			)

		self._content = self._get_default()

	def get_ident(self):
		return self._ident

	def get_base_type(self):
		return self._base_type

	def get_type_id(self):
		return self.__class__.__name__

	def get_content(self):
		return self._content

	def get_properties(self):
		non_schema_types = filter(
			lambda k: not k.startswith("Schema:"),
			self.get_allowed_types()
		)

		prop = dict(
			field_type=self.get_type_id(),
			# base_type=self._base_type.__name__,
			required=self._required,
			nullable=self._nullable,
			allowed_types=list(
				map(
					lambda t: t.__name__ if not isinstance(t, str) else t,
					set(self.get_allowed_types())
				)
			),
			allowed_values=self._allowed_values,
		)

		prop.update(self._get_properties())
		kwargs_props = (self._get_kwargs_properties() or [])
		kw_dict = {}
		for kwprop in kwargs_props:
			kwv = self._kwargs.get(kwprop, None)
			if kwv:
				kw_dict[kwprop] = kwv
		prop.update(kw_dict)
		return prop

	def _get_properties(self):
		return dict()

	def _get_kwargs_properties(self):
		return []

	def _ensure_is_field(self, f):
		if not isinstance(f, Field):
			raise ValueError("Expected Field instance, got: ", f)

	def _get_default(self):
		return None if self._nullable else (
			self._kwargs.get(
				"default",
				self._base_type() if self._base_type else None
			)
		)

	def get_allowed_types(self):
		allowed_types = [self._base_type]
		allowed_types.extend(self._allowed_types)
		allowed_types = list(set(allowed_types))
		return allowed_types

	def _register_error(self, v, msg, errors=None):
		if errors is None:
			return
		if self._ident not in errors:
			errors[self._ident] = []
		msg = (msg or "Invalid data")
		# .rstrip(".") + ". Got: %r" % v
		errors[self._ident].append(msg)

	def validate(self, v, errors, **kwargs):
		result = []
		result.append(self.check_constraints(v, errors, **kwargs))

		# if this is None - any later iter would raise excpt
		if v is None and not self._nullable:
			self._register_error(v, "Must be set", errors)
			return False
		# if this is of wrong - any later processing might raise excpt
		if not self.validate_type(v, errors, **kwargs):
			return False

		result.append(self._validate(v, errors, **kwargs))
		result.append(self._check_allowed_value(v, errors, **kwargs))
		return len(list(filter(lambda b: not b, result))) == 0

	def _validate(self, v, errors, **kwargs):
		return True

	def validate_type(self, v, errors, **kwargs):
		if v is None and self._nullable:
			return True
		return self._validate_type(v, errors, **kwargs)

	def _validate_type(self, v, errors, **kwargs):
		allowed_types = self.get_allowed_types()
		ok = (len(allowed_types) == 0)
		for t in allowed_types:
			if isinstance(v, t):
				ok = True
				break
		if not ok:
			self._register_error(v, "Invalid type", errors)
			return False
		return True

	def check_constraints(self, v, errors, **kwargs):
		if (self._required and (v is None)) and not self._nullable:
			self._register_error(v, "Required", errors)
			return False
		return self._check_constraints(**kwargs)

	def _check_constraints(self):
		return True

	def _check_allowed_value(self, v, errors, **kwargs):
		if not self._allowed_values or not v:
			return True
		if v not in self._allowed_values:
			self._register_error(v, "Value not allowed", errors)
			return False
		return True

	def validate_type_allowed(self, v, errors, **kwargs):
		allowed_types = self.get_allowed_types()
		if not allowed_types:
			return True
		ok = True
		if isinstance(v, str) and str not in allowed_types:
			self._register_error(v, "String not allowed", errors)
			ok = False
		elif isinstance(v, int) and int not in allowed_types:
			self._register_error(v, "Integer not allowed", errors)
			ok = False
		elif isinstance(v, float) and float not in allowed_types:
			self._register_error(v, "Float not allowed", errors)
			ok = False
		elif isinstance(v, list) and list not in allowed_types:
			self._register_error(v, "List not allowed", errors)
			ok = False
		elif isinstance(v, dict):
			if "@id" in v:
				ns = "Schema:" + v["@id"]
				if ns not in allowed_types:
					self._register_error(v, "Type (%s) not allowed" % v["@id"], errors)
					ok = False
			elif dict not in allowed_types:
				self._register_error(v, "Object not allowed", errors)
				ok = False
		if isinstance(v, Schema):
			found = False
			for t in allowed_types:
				if isinstance(t, SchemaType) and t.ident == v.ident:
					found = True
					break
			if not found:
				self._register_error(
					v,
					"Schema '%s' not allowed" % v.ident,
					errors
				)
				ok = False
		return ok


class Numeric(Field):
	def __init__(self, ident, base_type, **kwargs):
		self._range = kwargs.get("range", None)
		super().__init__(ident, base_type, **kwargs)

	def _validate(self, v, errors, **kwargs):
		if self._range and self._range[0] < v < self._range[1]:
			self._register_error(
				v,
				"Value out of range (%s ... %s)" % (
					self._range[0], self._range[1]
				),
				errors
			)
			return False
		return True


class Int(Numeric):
	def __init__(self, ident, **kwargs):
		kwargs["allowed_types"] = [int, float]
		super().__init__(ident, int, **kwargs)


class Double(Numeric):
	def __init__(self, ident, **kwargs):
		kwargs["allowed_types"] = [int, float]
		super().__init__(ident, float, **kwargs)


class Bool(Field):
	def __init__(self, ident, **kwargs):
		super().__init__(ident, bool, **kwargs)


class Time(Double):
	def __init__(self, ident, **kwargs):
		super().__init__(ident, **kwargs)


class Null(Field):
	def __init__(self, ident, **kwargs):
		kwargs["nullable"] = True
		kwargs["required"] = False
		super().__init__(ident, None, **kwargs)

	def _validate(self, v, errors, **kwargs):
		if v is not None:
			self._register_error(v, "Must be a null", errors)
			return False
		return True

	def _validate_type(self, v, errors, **kwargs):
		return True


class String(Field):
	def __init__(self, ident, **kwargs):
		super().__init__(ident, str, **kwargs)

	def _get_kwargs_properties(self):
		return ["format", "min_len", "max_len"]

	def _validate(self, v, errors, **kwargs):
		if not v:
			return True
		fmt = self._kwargs.get("format", None)
		if fmt and not re.match(fmt, v):
			self._register_error(v, "Invalid format", errors)
			return False
		minl = self._kwargs.get("min_len", None)
		maxl = self._kwargs.get("max_len", None)
		if minl:
			if len(v) < minl:
				self._register_error(v, "String value too short", errors)
				return False
		if maxl:
			if len(v) > maxl:
				self._register_error(v, "String value too long", errors)
				return False
		return True


class Date(String):
	def __init__(self, ident, **kwargs):
		if "format" not in kwargs:
			kwargs["format"] = "%d-%m-%Y"
		super().__init__(ident, **kwargs)

	def _validate(self, v, errors, **kwargs):
		if not super().validate(v, errors, kwargs):
			return False

		try:
			d = datetime.datetime.strptime(v, self._kwargs["format"])
		except ValueError as e:
			self._register_error(
				v,
				"Invalid date format, expected %s" % self._kwargs["format"],
				errors
			)
			return False
		return True


class ComplexField(Field):
	def __init__(self, ident, base_type, **kwargs):
		super().__init__(ident, base_type, **kwargs)

	def add_field(self, f):
		self._ensure_is_field(f)
		self._add_field(f)
		return self


class Array(ComplexField):
	def __init__(self, ident, **kwargs):
		self._allowed_element_types = kwargs.pop("allowed_types", [])
		super().__init__(ident, list, **kwargs)

	def append(self, *args):
		for f in list(args):
			self.add_field(f)
		return self

	def get_allowed_types(self):
		return self._allowed_element_types

	def _add_field(self, f):
		self._content.append(f)

	def _validate(self, values, errors, **kwargs):
		result = []
		for v in (values or []):
			if not self.validate_type_allowed(v, errors):
				result.append(False)
		return len(list(filter(lambda b: not b, result))) == 0

	def _validate_type(self, value, errors, **kwargs):
		allowed_types = self.get_allowed_types()
		if not allowed_types:
			return True
		result = []
		if isinstance(value, self._base_type):
			for v in value:
				found = False
				for t in allowed_types:
					if isinstance(t, str):
						if t.startswith("Schema:"):
							name = t[t.find(":") + 1:]
							module_name = name.replace("/", ".")
							__import__(module_name)
							schema = sys.modules[module_name].schema
							if schema.validate(v, errors):
								found = True
								break
					elif isinstance(v, t):
						found = True
						break
				result.append(found)
		else:
			result.append(False)
		ok = len(list(filter(lambda b: not b, result))) == 0
		if not ok:
			self._register_error(None, "Type not allowed", errors)
		return ok

	def _check_allowed_value(self, values, errors, **kwargs):
		if not self._allowed_values or not values:
			return True

		invalid = list(filter(lambda v: v not in self._allowed_values, values))
		if invalid:
			for v in invalid:
				self._register_error(v, "Value not allowed", errors)
			return False
		return True


class Enum(ComplexField):
	def __init__(self, ident, **kwargs):
		if "allowed_values" not in kwargs:
			raise Exception("Enum requires allowed_values")
		super().__init__(ident, str, **kwargs)

	def _add_field(self, f):
		raise Exception("Enum does not support adding fields")

	def _validate(self, v, errors, **kwargs):
		return True

	def _check_allowed_value(self, value, errors, **kwargs):
		if value not in self._allowed_values:
			self._register_error(
				value, "Value not allowed", errors
			)
			return False
		return True


class Object(ComplexField):
	def __init__(self, ident, **kwargs):
		kwargs["allowed_types"] = [dict]
		super().__init__(ident, dict, **kwargs)

	def _add_field(self, f):
		if not self._content:
			self._content = {}
		self._content[f._ident] = f

	def _validate(self, v, errors, **kwargs):
		keys_seen = kwargs.pop("keys_seen", [])
		result = []
		if v is None:
			if self._nullable:
				return True
			if self._required:
				return False
		if not self.validate_type_allowed(v, errors):
			# stop here, if it's not a dict we do not
			# want to iterate it below
			return False
		if self._content:
			for k in v:
				if k in self._content and isinstance(self._content[k], Field):
					keys_seen.append(k)
					result.append(self._content[k].validate(v[k], errors))
			# now check if we're missing any required fields
			for k in filter(lambda x: x not in keys_seen, self._content):
				result.append(self._content[k].validate(v.get(k, None), errors))
		return len(list(filter(lambda b: not b, result))) == 0


class SchemaType(Object):
	def __init__(self, ident, schema_name, **kwargs):
		version = kwargs.pop("version", None)
		module_name = schema_name.replace("/", ".")
		__import__(module_name)
		self.schema = sys.modules[module_name].schema
		super().__init__(ident, **kwargs)

	def _get_default(self):
		return None if self._nullable else self.schema._raw_data()

	def _validate(self, v, errors, **kwargs):
		restricted_keys = filter(lambda k: k.startswith("@"), v)
		if len(list(restricted_keys)):
			msg = "Cannot overwrite restricted keys in schema '%s'" % (
				self.get_ident()
			)
			self._register_error(None, msg, errors)
			return False

		keys_seen = kwargs.pop("keys_seen", [])
		result = []
		if v is None:
			if self._nullable:
				return True
			if self._required:
				return False
		if not isinstance(v, self._base_type):
			msg = "Invalid type, expected schema '%s' at key '%s'" % (
				self.schema.get_ident(), self.get_ident()
			)
			self._register_error(None, msg, errors)
			return False
		if self._content:
			keys = list(filter(
				lambda k: not k.startswith("@"), self._content
			))
			if len(keys):
				content = self._content
				for k in keys:
					result.append(content[k].validate(
						v.get(k, None), errors, **kwargs)
					)
		return len(list(filter(lambda b: not b, result))) == 0

	def get_type_id(self):
		return "Schema:" + self.schema.get_ident()


class Schema(object):
	def __init__(self, ident, version=0):
		self._ident = ident
		self.version = version
		self.root = {
			"@id" : self._ident,
			"@version" : self.version,
		}
		self._content = {}
		self._errors = {}

	def _ensure_is_field(self, f):
		if not isinstance(f, Field):
			raise ValueError(f)

	def get_ident(self):
		return self._ident

	def get_errors(self, **kwargs):
		as_json = kwargs.get("as_json", False)
		if as_json:
			return json.dumps(self._errors)
		return self._errors

	def add_field(self, f):
		self._ensure_is_field(f)
		self._content[f._ident] = f

	def set_content(self, f):
		self._ensure_is_field(f)
		self._content = f

	def get_content(self):
		return self._content

	def data(self):
		d = self._raw_data()

		def recurse(root, dest):
			for k in root:
				if not k.startswith("@"):
					if isinstance(root[k], Object):
						dest[k] = root[k].get_content()
						if root[k].get_content():
							recurse(root[k].get_content(), dest[k])
					else:
						dest[k] = root[k].get_content()

		result = {}
		recurse(self._raw_data(), result)
		return result

	def _raw_data(self):
		data = {}
		data.update(self.root)
		if isinstance(self._content, Field):
			data.update(self._content.get_content())
		else:
			data.update(self._content)
		return data

	def _build_json(self, root, result):
		obj = None
		if isinstance(root, dict):
			obj = root
		elif isinstance(root, Object):
			obj = root.get_content()

		if obj:
			data_keys = list(
				filter(lambda k: not k.startswith("@"), obj.keys())
			)
			for k in (data_keys or []):
				result[k] = {
					"@properties" : obj[k].get_properties()
				}
				self._build_json(obj[k], result[k])

	def to_json(self, **kwargs):
		result = {}
		result.update(self.root)
		self._build_json(self._raw_data(), result)
		return json.dumps(
			result,
			sort_keys=kwargs.pop("sort_keys", False),
			indent=kwargs.pop("indent", False),
			cls=FieldEncoder
		)

	def validate(self, data, errors=None):
		ref = self._errors if errors is None else errors
		ref[self._ident] = {}
		ref = ref[self._ident]

		if data is None:
			return True
		result = []
		for k in sorted(self._content):
			if isinstance(data, dict):
				if not self._content[k].validate(data.get(k, None), ref):
					result.append(False)
			elif not self._content[k].validate(data, ref):
					result.append(False)
		return len(list(filter(lambda b: not b, result))) == 0

	def _validate_object(self, data, root):
		result = True
		if not data and root._required:
			return False
		for k in root:
			if not root[k].validate(data):
				result = False
		return result

	def _validate_array_UNUSED(self, data, root):
		if not data and root._required:
			return False
		for el in data:
			if isinstance(el, Schema):
				if not el.validate(el):
					return False


class FieldEncoder(JSONEncoder):
	def default(self, o):
		return o.get_content()
