from . table import Table


class View(Table):
	def __init__(self, conn, record, table_catalog):
		Table.__init__(self, conn, record, table_catalog)
		self._reltype = "View"
