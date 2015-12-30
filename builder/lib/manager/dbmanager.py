import os
import sys
import psycopg2
from distutils import dir_util

from . manager import Manager
from . import dbschema


class DBManager(Manager):
	def __init__(self, program_args, **kwargs):
		super().__init__(program_args, **kwargs)
		self._conn = None

	def _connection_params(self):
		return dict(
			host=self._args.host,
			port=self._args.port,
			database=self._args.dbname,
			user=self._args.user,
			password=self._args.password,
		)

	def connect(self):
		if not self._conn:
			params = self._connection_params()
			self._conn = psycopg2.connect(**params)

	def initdb(self):
		self.connect()
		schema_dir = self._mk_path(self._args.sql_schema_in)
		data_dir = self._mk_path(self._args.sql_data_in)
		print(schema_dir)
		c = self._conn.cursor()
		c.execute("BEGIN")
		if self._args.use_schema:
			self._execute_sql_from_dir(schema_dir, cursor=c)
		if self._args.use_data:
			self._execute_sql_from_dir(data_dir, cursor=c)
		c.execute("COMMIT")

	def generate_schema(self):
		self.p_info("Generating schema from database:", self._args.dbname)
		params = self._connection_params()
		dbschema.build(self._args, params, schema=True)

	def generate_code(self):
		self.p_info(
			"Generating code mappings from database schema:",
			self._args.dbname
		)
		params = self._connection_params()
		dbschema.build(self._args, params, code=True)

	def _execute_sql_from_dir(self, directory, cursor=None):
		sql_files = set()
		for root, dirs, files in os.walk(directory):
			for f in files:
				if f.endswith(".sql"):
					sql_files.add(os.path.join(root, f))
			c = (cursor or self._conn.cursor())
			for sqlf in sorted(sql_files):
				self.p_info(sqlf)
				with open(sqlf, "r") as fh:
					sql = fh.read()
					try:
						c.execute(sql)
						# self._conn.commit()
					except Exception as e:
						self._conn.rollback()
						if self.is_fatal:
							raise e
						else:
							self.p_info("Non-fatal ERROR", e)

	def populate(self, mod, use_all=False):
		self.connect()
		if use_all:
			for (root, dirs, files) in sorted(os.walk("data")):
				for f in sorted(files):
					if f.endswith(".py") and not f.startswith("_"):
						self._populate(os.path.join(root, f))
						# print(os.path.join(root, f))
		elif mod:
			self._populate(mod)
		else:
			raise Exception("No data module given")

	def _populate(self, mod):
		print("Populating data using:", mod)
		mod = mod.replace("/", ".")
		if mod.endswith(".py"):
			mod = mod[:-3]
		__import__(mod)
		sys.modules[mod].populate(self._conn)
