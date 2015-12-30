import psycopg2
import psycopg2.extras


class Table(object):
	def __init__(self, conn, record, table_catalog, **kwargs):
		self._conn = conn
		self._record = record
		self._table_catalog = table_catalog
		self._kwargs = kwargs
		self._reltype = "table"

	def build(self):
		q = (
			"""
			select column_name,column_default, data_type,
			udt_catalog, udt_schema, udt_name,
			is_nullable, is_updatable, character_maximum_length
			from information_schema.columns
			where table_name = %s
			and table_schema = %s
			and table_catalog = %s
			and table_schema != 'information_schema'
			and table_schema not like 'pg_%%'
			order by column_name asc
			"""
		)

		cur = self._conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
		params = (
			self._record.table_name, self._record.table_schema, self._table_catalog
		)
		cur.execute(q, params)
		return self._build(cur.fetchall())
