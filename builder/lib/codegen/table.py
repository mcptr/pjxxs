from lib.environ import renderer
from lib.pg.table import Table
from . column import CodegenColumn

import time


class CodegenTable(Table):
	def __init__(self, *args, **kwargs):
		Table.__init__(self, *args, **kwargs)

	def _build(self, columns):
		table_hxx = renderer.get_template("codegen/table_hxx.tpl")
		table_cxx = renderer.get_template("codegen/table_cxx.tpl")
		params = dict(
			reltype=self._reltype,
			generation_time=time.asctime(),
			table_catalog=self._table_catalog,
			table=self._record,
			columns=self._prepare_columns(columns),
			class_name=self._mk_clas_name()
		)
		return dict(
			header=table_hxx.render(data=params),
			unit=table_cxx.render(data=params),
		)

	def _prepare_columns(self, columns):
		out = []
		for col in columns:
			c = CodegenColumn(self._conn, col)
			schema = c.build()
			prop = schema.get_properties()
			o = dict(
				schema=prop,
				record=col,
				cpp_type=self._translate_type(prop)
			)
			out.append(o)
		return out

	def _translate_type(self, prop):
		ftype = prop["field_type"].lower()
		if ftype in ["bool", "boolean"]:
			return "int"
		if ftype in ["int"]:
			return "int"
		if ftype in ["double", "float", "numeric"]:
			return "double"
		if ftype in ["str", "string", "enum"]:
			return "std::string"
		if ftype in ["time"]:
			return "std::tm"
		if ftype in ["array"]:
			# print(self._translate_array_type(prop["allowed_types"][0]))
			#return self._translate_array_type(prop["allowed_types"][0])
			return "std::string"

	def _translate_array_type(self, tp):
		tp_map = {
			"str": "std::string",
			"int": "long",
			"float": "double",
		}
		return "db::types::Array<%s>" % tp_map[tp]

	def _mk_clas_name(self):
		parts = self._record.table_name.lower().split("_")
		return "".join([p.capitalize() for p in parts])
