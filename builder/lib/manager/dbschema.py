import os
import psycopg2
import psycopg2.extras

from lib.schema.table import SchemaTable
from lib.schema.view import SchemaView
from lib.codegen.table import CodegenTable
from lib.codegen.view import CodegenView

from lib.manager.manager import Manager

json_params = dict(
	sort_keys=True,
	indent=4
)


def build(args, conn_params, **kwargs):
	builder = Builder(args, conn_params, **kwargs)
	builder.build_table_mappings()
	builder.build_view_mappings()


class Builder(Manager):
	def __init__(self, args, conn_params, **kwargs):
		super().__init__({}, **kwargs)
		self._args = args
		self._table_catalog = conn_params.get("database")
		self._conn = psycopg2.connect(**conn_params)

	def _save_schema(self, schema):
		schema_out_dir = self._mk_path(self._args.schema_out)
		fname_parts = schema.get_ident().split("/")
		fname = os.path.join(schema_out_dir, *fname_parts)
		fname += ".json"
		dname = os.path.dirname(fname)
		if not os.path.isdir(dname):
			os.makedirs(dname)
		if self._args.verbose:
			print("Saving:", fname)
		with open(fname, "w+") as fh:
			fh.write(schema.to_json(**json_params))

	def _save_code_mapping(self, table, mapping):
		cxx_out_dir = self._mk_path(self._args.cxx_out)
		directory = os.path.join(cxx_out_dir, table.table_schema)
		try:
			os.makedirs(directory)
		except OSError as e:
			pass

		header_path = os.path.join(directory, table.table_name) + ".hxx"
		unit_path = os.path.join(directory, table.table_name) + ".cxx"
		if self._args.verbose:
			print("Saving:", header_path)
		with open(header_path, "w") as fh:
			fh.write(mapping["header"] + "\n")
		if self._args.verbose:
			print("Saving:", unit_path)
		with open(unit_path, "w") as fh:
			fh.write(mapping["unit"] + "\n")

	def build_table_mappings(self):
		table_type = "BASE TABLE"
		q = (
			"""
			select table_schema, table_name
			from information_schema.tables inst
			where table_catalog = %s
			and table_schema != 'information_schema'
			and table_schema not like 'pg_%%'
			and table_type = %s
			"""
		)

		cur = self._conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
		cur.execute(q, (self._table_catalog, table_type))
		for r in cur.fetchall():
			if self._args.gen_schema:
				t = SchemaTable(self._conn, r, self._table_catalog)
				schema = t.build()
				self._save_schema(schema)
			if self._args.gen_code:
				t = CodegenTable(self._conn, r, self._table_catalog)
				mapping = t.build()
				self._save_code_mapping(r, mapping)

	def build_view_mappings(self):
		table_type = "VIEW"
		q = (
			"""
			select table_schema, table_name
			from information_schema.tables inst
			where table_catalog = %s
			and table_schema != 'information_schema'
			and table_schema not like 'pg_%%'
			and table_type = %s
			"""
		)

		cur = self._conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
		cur.execute(q, (self._table_catalog, table_type))
		for r in cur.fetchall():
			if self._args.gen_schema:
				v = SchemaView(self._conn, r, self._table_catalog)
				schema = v.build()
				self._save_schema(schema)
			if self._args.gen_code:
				t = CodegenView(self._conn, r, self._table_catalog)
				mapping = t.build()
				self._save_code_mapping(r, mapping)
