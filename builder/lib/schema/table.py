from lib.pg.table import Table
from . column import SchemaColumn

from pjxxs import fields


class SchemaTable(Table):
	def __init__(self, *args, **kwargs):
		Table.__init__(self, *args, **kwargs)

	def _build(self, columns):
		schema_id = "%s/%s" % (
			self._record.table_schema, self._record.table_name
		)
		schema = fields.Schema(schema_id)
		for r in columns:
			column = SchemaColumn(self._conn, r)
			field = column.build()
			schema.add_field(field)
		return schema
