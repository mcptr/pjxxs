import psycopg2
import psycopg2.extras


class Column(object):
	def __init__(self, conn, record):
		self._conn = conn
		self._column = record

	def _get_enum_values(self):
		q = (
			"""
			SELECT e.enumlabel
			FROM pg_catalog.pg_enum e
			JOIN pg_catalog.pg_type t on e.enumtypid = t.oid
			LEFT JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
			WHERE (t.typrelid = 0 )
			AND ((t.typname = %(udt_name)s
			OR pg_catalog.format_type(t.oid, NULL) = %(udt_name)s))
			AND n.nspname = %(udt_schema)s
			ORDER BY e.enumsortorder
			"""
		)

		cur = self._conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
		#print(cur.mogrify(q, dict(column.__dict__)).expandtabs().decode())
		cur.execute(q, dict(self._column.__dict__))
		return list(map(lambda r: r[0], cur.fetchall()))
