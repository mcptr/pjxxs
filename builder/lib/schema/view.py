from lib.pg.view import View
from . table import SchemaTable


class SchemaView(View, SchemaTable):
	def __init__(self, *args, **kwargs):
		View.__init__(self, *args, **kwargs)
		SchemaTable.__init__(self, *args, **kwargs)
