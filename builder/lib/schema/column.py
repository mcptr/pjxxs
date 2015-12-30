from lib.pg.column import Column
from pjxxs import fields


class SchemaColumn(Column):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._type_map = {
			"character" : fields.String,
			"character varying" : fields.String,
			"text" : fields.String,
			"json" : fields.String,
			"jsonb" : fields.String,
			"boolean" : fields.Bool,
			"integer" : fields.Int,
			"bigint" : fields.Int,
			"double precision" : fields.Double,
			"numeric" : fields.Double,
			"timestamp without time zone" : fields.Time,
			"timestamp with time zone" : fields.Time,
			"date" : fields.Time,
			"array" : fields.Array,
		}

		self._udt_type_map = {
			"_int4" : int,
			"_int8" : int,
			"_varchar" : str,
			"_numeric" : float,
		}

	def _map_constraints(self):
		params = dict(
			nullable=(self._column.is_nullable == "YES"),
		)
		if self._column.character_maximum_length:
			params["max_len"] = self._column.character_maximum_length
		return params

	def _is_expression(self, value):
		if value.startswith("nextval(") or value == "now()":
			return True
		return False

	def build(self):
		params = dict()
		default = self._column.column_default
		if default and not self._is_expression(default):
			params["default"] = default

		params.update(self._map_constraints())

		result = None
		col_type = self._column.data_type.lower()
		if col_type not in self._type_map:
			if col_type == "user-defined":
				result = self._map_user_define_type(params)
			else:
				raise Exception("Unknown type:", self._column.data_type, self._column)
		else:
			cls = self._type_map[col_type]
			if col_type == "array":
				params["allowed_types"] = params.get("allowed_types", [])
				params["allowed_types"].append(
					self._udt_type_map[self._column.udt_name]
				)
			result = cls(self._column.column_name, **params)
		return result

	def _map_user_define_type(self, params):
		# 2DO: check typrelid, and create another mapping.
		# FIXME: handling anything as enum for now
		params["allowed_values"] = self._get_enum_values()
		return fields.Enum(self._column.column_name, **params)
